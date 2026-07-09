from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import AccountRole, UserPlayerRelationship
from accounts.services.link_service import deactivate_link, link_user_to_player
from accounts.services.profile_service import set_account_role
from analytics.models import (
    OBSERVATION_STATUS_DRAFT,
    OBSERVATION_STATUS_REOPENED,
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    EvaluationCycle,
    EvaluatorRole,
    Observation,
    ObservationQuestion,
    ObservationQuestionSet,
    ObservationResponse,
    ObservationSource,
    ObservationType,
)
from analytics.assessment_forms import CoachAssessmentForm
from analytics.services.observation_service import (
    create_coach_assessment_observation,
    create_observation,
    default_coach_assessment_question_set,
    get_observation_detail,
    save_observation_responses,
    submit_observation,
    validate_required_responses,
)
from analytics.services.comparison_service import (
    get_player_comparison,
    get_player_score_summary,
)
from analytics.services.metrics_service import (
    completion_metrics,
    draft_matching_metrics,
    import_metrics,
    observation_metrics,
    recent_submitted_observations,
)
from analytics.services.player_service import (
    DRAFT_STATUS_AVAILABLE,
    DRAFT_STATUS_DRAFTED,
    DRAFT_STATUS_NO_CONTEXT,
    EVALUATION_HAS_ANY,
    EVALUATION_HAS_SUBMITTED,
    EVALUATION_NO_SUBMITTED,
    EVALUATION_NOT_STARTED,
    active_player_ids,
    parse_player_search_filters,
    search_players,
)
from analytics.services.permissions import (
    can_evaluate_player,
    can_submit_evaluation,
    can_view_own_evaluation_draft,
    evaluator_role_for_user,
)
from analytics.services.reporting_service import get_command_center_context
from analytics.services.draft_service import get_draft_context_for_draft_player, get_draft_contexts_for_draft
from analytics.services.question_service import (
    COACH_ASSESSMENT_RUBRIC,
    DEFAULT_COACH_ASSESSMENT_QUESTIONS,
    DEFAULT_EVALUATOR_ROLES,
    DEFAULT_OBSERVATION_SOURCES,
    ROLE_ADMIN,
    ROLE_COACH,
    ROLE_GUEST_EVALUATOR,
    ROLE_PLAYER,
    ROLE_STAFF,
    SOURCE_COACH,
    ensure_default_coach_assessment_setup,
    get_active_questions,
    get_question_set_for_cycle,
)
from analytics.services.timeline_service import get_player_timeline
from drafts.models import Draft, DraftAction, DraftActionType, DraftPlayer, DraftTeam
from players.models import Player, PlayerImportBatch, PlayerImportStatus, PlayerSourceRow, PlayerTag
from players.services.import_service import SOURCE_MEMBER_LIST
from players.services.tag_service import assign_tag


User = get_user_model()


class AnalyticsImportViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.user = User.objects.create_user(username="user", password="testpass")

    def upload(self):
        return SimpleUploadedFile(
            "member list for 13u house.csv",
            b"First,Last,Gender,Team\nEugene,Lin,M,Expos\n",
            content_type="text/csv",
        )

    def test_import_views_require_staff(self):
        response = self.client.get(reverse("analytics:import-list"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse("analytics:import-list"))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_open_import_list(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:import-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player Imports")

    def test_upload_redirects_to_preview(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("analytics:import-new"),
            {"source": SOURCE_MEMBER_LIST, "csv_file": self.upload()},
        )

        self.assertEqual(response.status_code, 302)
        batch = PlayerImportBatch.objects.get()
        self.assertEqual(response["Location"], reverse("analytics:import-preview", kwargs={"pk": batch.pk}))

    def test_upload_can_enable_account_provisioning_options(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB,Email\nEugene,Lin,2012-05-01,eugene@example.com\n",
                    content_type="text/csv",
                ),
                "provision_player_accounts": "on",
            },
        )

        batch = PlayerImportBatch.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(batch.mapping_config["_provision_player_accounts"])
        self.assertTrue(batch.mapping_config["_activate_player_accounts"])

    def test_preview_can_map_account_email_and_preserves_provisioning_options(self):
        self.client.force_login(self.staff)
        batch = PlayerImportBatch.objects.create(
            source=SOURCE_MEMBER_LIST,
            original_filename="member.csv",
            uploaded_by=self.staff,
            mapping_config={"_provision_player_accounts": True, "_activate_player_accounts": False},
            preview_snapshot={
                "parsed_csv": {
                    "file_name": "member.csv",
                    "headers": ["First", "Last", "DOB", "Email"],
                    "normalized_headers": {"first": "First", "last": "Last", "dob": "DOB", "email": "Email"},
                    "rows": [
                        {
                            "row_number": 2,
                            "original_row": {"First": "Eugene", "Last": "Lin", "DOB": "2012-05-01", "Email": "eugene@example.com"},
                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "DOB": "2012-05-01", "Email": "eugene@example.com"},
                        }
                    ],
                }
            },
        )

        response = self.client.post(
            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
            {"first_name": "First", "last_name": "Last", "birthdate": "DOB", "account_email": "Email"},
        )

        batch.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(batch.mapping_config["_provision_player_accounts"])
        self.assertEqual(batch.mapping_config["account_email"], "Email")
        self.assertTrue(batch.preview_snapshot["preview"]["account_provisioning"]["enabled"])
        self.assertTrue(batch.preview_snapshot["preview"]["account_provisioning"]["activate_users"])

    def test_preview_refresh_and_confirm_import(self):
        self.client.force_login(self.staff)
        batch = PlayerImportBatch.objects.create(
            source=SOURCE_MEMBER_LIST,
            original_filename="member.csv",
            uploaded_by=self.staff,
            preview_snapshot={
                "parsed_csv": {
                    "file_name": "member.csv",
                    "headers": ["First", "Last", "Team"],
                    "normalized_headers": {"first": "First", "last": "Last", "team": "Team"},
                    "rows": [
                        {
                            "row_number": 2,
                            "original_row": {"First": "Eugene", "Last": "Lin", "Team": "Expos"},
                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "Team": "Expos"},
                        }
                    ],
                }
            },
        )

        preview_response = self.client.post(
            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
            {"first_name": "First", "last_name": "Last", "team_name": "Team"},
        )
        self.assertEqual(preview_response.status_code, 302)

        confirm_response = self.client.post(reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True)

        self.assertEqual(confirm_response.status_code, 200)
        self.assertTrue(Player.objects.filter(first_name="Eugene", last_name="Lin").exists())
        self.assertContains(confirm_response, "Import Result")

    def test_import_detail_shows_safe_account_provisioning_summary(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB\nEugene,Lin,2012-05-01\n",
                    content_type="text/csv",
                ),
                "provision_player_accounts": "on",
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.post(reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account provisioning")
        self.assertContains(response, "Users Created")
        self.assertNotContains(response, "20120501")

    def test_conflict_page_displays_review_rows(self):
        self.client.force_login(self.staff)
        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", team_name="Old")
        upload_response = self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB,Team\nEugene,Lin,2012-05-01,New\n",
                    content_type="text/csv",
                ),
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.get(reverse("analytics:import-conflicts", kwargs={"pk": batch.pk}))

        self.assertEqual(upload_response.status_code, 302)
        self.assertContains(response, "Row 2")
        self.assertContains(response, "team_name")

    def test_preview_routes_review_rows_through_conflict_review(self):
        self.client.force_login(self.staff)
        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", team_name="Old")
        self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,DOB,Team\nEugene,Lin,2012-05-01,New\n",
                    content_type="text/csv",
                ),
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.get(reverse("analytics:import-preview", kwargs={"pk": batch.pk}))

        self.assertContains(response, "Review Rows")
        self.assertNotContains(response, "Confirm Import")

    def test_conflict_page_can_commit_ambiguous_row_to_selected_candidate(self):
        self.client.force_login(self.staff)
        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        selected = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        self.client.post(
            reverse("analytics:import-new"),
            {
                "source": SOURCE_MEMBER_LIST,
                "csv_file": SimpleUploadedFile(
                    "member.csv",
                    b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n",
                    content_type="text/csv",
                ),
            },
        )
        batch = PlayerImportBatch.objects.get()

        response = self.client.post(
            reverse("analytics:import-confirm", kwargs={"pk": batch.pk}),
            {"row_2_action": "use_candidate", "row_2_candidate": str(selected.id)},
            follow=True,
        )

        selected.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(selected.team_name, "Expos")
        self.assertEqual(PlayerSourceRow.objects.get().player, selected)


class AnalyticsObservationFoundationTests(TestCase):
    def setUp(self):
        self.evaluator = User.objects.create_user(username="coach", password="testpass")
        self.other_evaluator = User.objects.create_user(username="othercoach", password="testpass")
        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U")
        self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="13U")
        self.setup_result = ensure_default_coach_assessment_setup()
        self.role = EvaluatorRole.objects.get(key=ROLE_COACH)
        self.source = ObservationSource.objects.get(key=SOURCE_COACH)
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
        )

    def required_response_payload(self):
        return {
            question: 4
            for question in self.setup_result.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5,
                is_required=True,
                is_active=True,
            )
        }

    def test_default_setup_creates_coach_assessment_configuration(self):
        self.assertTrue(ObservationType.objects.filter(key=OBSERVATION_TYPE_COACH_ASSESSMENT).exists())
        self.assertEqual(ObservationSource.objects.count(), len(DEFAULT_OBSERVATION_SOURCES))
        self.assertEqual(EvaluatorRole.objects.count(), len(DEFAULT_EVALUATOR_ROLES))
        self.assertEqual(self.setup_result.question_set.rubric, COACH_ASSESSMENT_RUBRIC)
        self.assertEqual(self.setup_result.question_set.questions.count(), len(DEFAULT_COACH_ASSESSMENT_QUESTIONS))
        self.assertEqual(
            self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_TEXT).count(),
            1,
        )
        self.assertEqual(
            self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).count(),
            len(DEFAULT_COACH_ASSESSMENT_QUESTIONS) - 1,
        )

    def test_default_setup_is_idempotent(self):
        first_question_count = ObservationQuestion.objects.count()

        second_result = ensure_default_coach_assessment_setup()

        self.assertEqual(ObservationQuestion.objects.count(), first_question_count)
        self.assertEqual(second_result.questions_created, 0)

    def test_default_setup_does_not_overwrite_existing_questions(self):
        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
        question.prompt = "Edited prompt"
        question.display_order = 99
        question.is_required = False
        question.save()

        ensure_default_coach_assessment_setup()

        question.refresh_from_db()
        self.assertEqual(question.prompt, "Edited prompt")
        self.assertEqual(question.display_order, 99)
        self.assertFalse(question.is_required)

    def test_cycle_slug_generation_creates_unique_slugs(self):
        second_cycle = EvaluationCycle.objects.create(name=self.cycle.name, cycle_type="Coach Assessment")

        self.assertEqual(self.cycle.slug, "2026-13u-coach-assessment")
        self.assertEqual(second_cycle.slug, "2026-13u-coach-assessment-2")

    def test_question_set_version_is_unique_per_observation_type(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ObservationQuestionSet.objects.create(
                    observation_type=self.setup_result.observation_type,
                    name="Duplicate",
                    version=1,
                )

    def test_question_key_is_unique_per_question_set(self):
        first_question = self.setup_result.question_set.questions.first()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ObservationQuestion.objects.create(
                    question_set=self.setup_result.question_set,
                    key=first_question.key,
                    prompt="Duplicate",
                    response_type=RESPONSE_TYPE_RATING_1_5,
                )

    def test_get_active_questions_and_cycle_question_set(self):
        questions = list(get_active_questions(self.setup_result.question_set))

        self.assertEqual(questions[0].display_order, 1)
        self.assertEqual(get_question_set_for_cycle(self.cycle), self.setup_result.question_set)
        fallback_cycle = EvaluationCycle.objects.create(name="Fallback Cycle", cycle_type="Coach Assessment")
        self.assertEqual(get_question_set_for_cycle(fallback_cycle), self.setup_result.question_set)

    def test_cycle_rejects_non_coach_assessment_question_set(self):
        other_type = ObservationType.objects.create(key="tryout", name="Tryout")
        other_question_set = ObservationQuestionSet.objects.create(observation_type=other_type, name="Tryout", version=1)

        with self.assertRaises(ValidationError):
            EvaluationCycle.objects.create(
                name="Invalid Cycle",
                cycle_type="Coach Assessment",
                coach_assessment_question_set=other_question_set,
            )

    def test_create_coach_assessment_references_players_player_and_snapshots_role(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
            evaluator_role=self.role,
            source=self.source,
        )

        observation = result.observation
        self.assertEqual(observation.player, self.player)
        self.assertEqual(observation.evaluator_role_key, ROLE_COACH)
        self.assertEqual(observation.evaluator_role_name, "Coach")
        self.assertEqual(observation.observation_type_key, OBSERVATION_TYPE_COACH_ASSESSMENT)

    def test_evaluation_submission_permissions_by_role(self):
        anonymous = None
        coach = User.objects.create_user(username="rolecoach", password="testpass")
        player_user = User.objects.create_user(username="roleplayer", password="testpass")
        staff_user = User.objects.create_user(username="rolestaff", password="testpass", is_staff=True)
        guest = User.objects.create_user(username="roleguest", password="testpass")
        parent = User.objects.create_user(username="roleparent", password="testpass")
        set_account_role(coach, AccountRole.COACH)
        set_account_role(player_user, AccountRole.PLAYER)
        set_account_role(staff_user, AccountRole.STAFF)
        set_account_role(guest, AccountRole.GUEST_EVALUATOR)
        set_account_role(parent, AccountRole.PARENT)

        self.assertFalse(can_submit_evaluation(anonymous))
        self.assertTrue(can_submit_evaluation(coach))
        self.assertTrue(can_submit_evaluation(player_user))
        self.assertTrue(can_submit_evaluation(staff_user))
        self.assertTrue(can_submit_evaluation(guest))
        self.assertFalse(can_submit_evaluation(parent))

    def test_self_evaluation_is_blocked_by_active_self_link_only(self):
        player_user = User.objects.create_user(username="selflinked", password="testpass")
        set_account_role(player_user, AccountRole.PLAYER)
        link = link_user_to_player(player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)

        self.assertFalse(can_evaluate_player(player_user, self.player))
        self.assertTrue(can_evaluate_player(player_user, self.other_player))
        with self.assertRaises(ValidationError):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=player_user,
            )

        deactivate_link(link)
        self.assertTrue(can_evaluate_player(player_user, self.player))

    def test_parent_role_cannot_create_observation(self):
        parent = User.objects.create_user(username="parent", password="testpass")
        set_account_role(parent, AccountRole.PARENT)

        with self.assertRaises(ValidationError):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=parent,
            )

    def test_evaluator_role_for_user_maps_account_roles(self):
        expectations = [
            (AccountRole.COACH, ROLE_COACH),
            (AccountRole.PLAYER, ROLE_PLAYER),
            (AccountRole.STAFF, ROLE_STAFF),
            (AccountRole.ADMIN, ROLE_ADMIN),
            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
        ]
        for account_role, evaluator_role_key in expectations:
            with self.subTest(account_role=account_role):
                user = User.objects.create_user(username=f"{account_role}-user", password="testpass")
                set_account_role(user, account_role)

                evaluator_role = evaluator_role_for_user(user)

                self.assertEqual(evaluator_role.key, evaluator_role_key)

    def test_coach_assessment_snapshots_actual_account_role_by_default(self):
        role_expectations = [
            (AccountRole.COACH, ROLE_COACH),
            (AccountRole.PLAYER, ROLE_PLAYER),
            (AccountRole.STAFF, ROLE_STAFF),
            (AccountRole.ADMIN, ROLE_ADMIN),
            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
        ]
        for index, (account_role, evaluator_role_key) in enumerate(role_expectations, start=1):
            with self.subTest(account_role=account_role):
                evaluator = User.objects.create_user(username=f"snapshot-{account_role}", password="testpass")
                set_account_role(evaluator, account_role)
                player = Player.objects.create(first_name=f"Snapshot{index}", last_name="Target", division="13U")

                result = create_coach_assessment_observation(
                    player=player,
                    evaluation_cycle=self.cycle,
                    evaluator=evaluator,
                )

                self.assertEqual(result.observation.evaluator_role_key, evaluator_role_key)
                self.assertEqual(result.observation.evaluator_role, EvaluatorRole.objects.get(key=evaluator_role_key))

    def test_draft_view_helpers_are_limited_to_own_drafts(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        self.assertTrue(can_view_own_evaluation_draft(self.evaluator, observation))
        self.assertFalse(can_view_own_evaluation_draft(self.other_evaluator, observation))

        observation.status = OBSERVATION_STATUS_SUBMITTED
        observation.save(update_fields=["status", "updated_at"])
        self.assertFalse(can_view_own_evaluation_draft(self.evaluator, observation))

    def test_submitted_observation_sets_submitted_at(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
            responses=self.required_response_payload(),
        )
        submitted = submit_observation(result.observation)

        self.assertIsNotNone(submitted.submitted_at)

    def test_coach_assessment_requires_evaluator(self):
        with self.assertRaises(ValidationError):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=None,
            )

    def test_create_observation_rejects_mismatched_question_set_type(self):
        other_type = ObservationType.objects.create(key="tryout", name="Tryout")
        other_question_set = ObservationQuestionSet.objects.create(observation_type=other_type, name="Tryout", version=1)

        with self.assertRaises(ValidationError):
            create_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                observation_type=self.setup_result.observation_type,
                question_set=other_question_set,
                source=self.source,
                evaluator=self.evaluator,
                evaluator_role=self.role,
            )

    def test_save_numeric_text_and_payload_responses(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        rating_question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)

        created, updated = save_observation_responses(
            observation,
            [
                {"question": rating_question, "value": 4, "payload": {"source": "test"}},
                {"question": text_question.key, "value": "Good teammate."},
            ],
        )

        rating_response = ObservationResponse.objects.get(observation=observation, question=rating_question)
        text_response = ObservationResponse.objects.get(observation=observation, question=text_question)
        self.assertEqual(created, 2)
        self.assertEqual(updated, 0)
        self.assertEqual(rating_response.numeric_value, Decimal("4.00"))
        self.assertEqual(rating_response.payload, {"source": "test"})
        self.assertEqual(text_response.text_value, "Good teammate.")

    def test_save_response_updates_existing_response(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()

        save_observation_responses(observation, {question: 3})
        created, updated = save_observation_responses(observation, {question: 5})

        response = ObservationResponse.objects.get(observation=observation, question=question)
        self.assertEqual(created, 0)
        self.assertEqual(updated, 1)
        self.assertEqual(response.numeric_value, Decimal("5.00"))

    def test_invalid_rating_is_rejected(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()

        with self.assertRaises(ValidationError):
            save_observation_responses(observation, {question: 6})

    def test_decimal_and_non_finite_ratings_are_rejected(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()

        for value in ["3.5", "NaN", "Infinity"]:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    save_observation_responses(observation, {question: value})

    def test_question_from_different_question_set_is_rejected(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        other_question_set = ObservationQuestionSet.objects.create(
            observation_type=self.setup_result.observation_type,
            name="Other",
            version=2,
        )
        other_question = ObservationQuestion.objects.create(
            question_set=other_question_set,
            key="other_question",
            prompt="Other question",
            response_type=RESPONSE_TYPE_RATING_1_5,
        )

        with self.assertRaises(ValidationError):
            save_observation_responses(observation, {other_question: 3})

    def test_duplicate_coach_assessment_is_prevented_for_same_evaluator_player_cycle(self):
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        )

        with self.assertRaises(ValidationError):
            create_coach_assessment_observation(
                player=self.player,
                evaluation_cycle=self.cycle,
                evaluator=self.evaluator,
            )

    def test_multiple_evaluators_can_assess_same_player_cycle(self):
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        )
        second = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_evaluator,
        )

        self.assertEqual(second.observation.player, self.player)
        self.assertEqual(Observation.objects.filter(player=self.player, evaluation_cycle=self.cycle).count(), 2)

    def test_same_evaluator_can_assess_different_players_and_cycles(self):
        other_cycle = EvaluationCycle.objects.create(name="2026 15U Coach Assessment", cycle_type="Coach Assessment")

        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        )
        create_coach_assessment_observation(
            player=self.other_player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        )
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=other_cycle,
            evaluator=self.evaluator,
        )

        self.assertEqual(Observation.objects.filter(evaluator=self.evaluator).count(), 3)

    def test_submit_observation_and_detail_loader(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation
        save_observation_responses(observation, self.required_response_payload())

        submitted = submit_observation(observation, actor=self.evaluator)
        detail = get_observation_detail(submitted.id)

        self.assertEqual(submitted.status, OBSERVATION_STATUS_SUBMITTED)
        self.assertIsNotNone(submitted.submitted_at)
        self.assertEqual(detail.player, self.player)

    def test_submit_observation_requires_required_responses(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.evaluator,
        ).observation

        with self.assertRaises(ValidationError):
            validate_required_responses(observation)
        with self.assertRaises(ValidationError):
            submit_observation(observation, actor=self.evaluator)

    def test_default_question_set_wrapper(self):
        self.assertEqual(default_coach_assessment_question_set(), self.setup_result.question_set)

    def test_phase_three_models_registered_in_admin(self):
        for model in [
            EvaluationCycle,
            ObservationType,
            ObservationSource,
            EvaluatorRole,
            ObservationQuestionSet,
            ObservationQuestion,
            Observation,
            ObservationResponse,
        ]:
            self.assertIn(model, admin.site._registry)


class AnalyticsDraftContextServiceTests(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
        self.third_coach = User.objects.create_user(username="thirdcoach", password="testpass")
        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
        )
        self.draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
        self.team = DraftTeam.objects.create(draft=self.draft, name="Expos Navy", display_order=1)
        DraftTeam.objects.create(draft=self.draft, name="Expos Gold", display_order=2)
        self.draft_player = DraftPlayer.objects.create(
            draft=self.draft,
            first_name="Eugene",
            last_name="Lin",
            full_name="Eugene Lin",
            extra_data={"Birth Year": "2012"},
        )

    def submitted_observation(self, evaluator, rating=4):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=evaluator,
            responses={
                question: rating
                for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
            },
        )
        return submit_observation(result.observation, actor=evaluator)

    def test_draft_context_retrieves_submitted_observation_and_selection(self):
        expected_round_question = ObservationQuestion.objects.create(
            question_set=self.setup_result.question_set,
            key="expected_draft_round",
            prompt="Expected draft round",
            response_type=RESPONSE_TYPE_TEXT,
            metadata={"draft_context_field": "expected_draft_round"},
            display_order=100,
        )
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={
                **{
                    question: 4
                    for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
                },
                expected_round_question: "2",
            },
        ).observation
        submit_observation(observation, actor=self.coach)
        DraftAction.objects.create(
            draft=self.draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=self.draft_player,
            to_team=self.team,
            pick_number=3,
        )

        context = get_draft_context_for_draft_player(self.draft_player)

        self.assertTrue(context.is_matched)
        self.assertEqual(context.matched_player, self.player)
        self.assertEqual(context.pick_number, 3)
        self.assertEqual(context.selected_round, 2)
        self.assertEqual(context.selected_team, self.team)
        self.assertEqual(context.submitted_observation_count, 1)
        self.assertEqual(context.latest_observation.expected_draft_round, "2")
        self.assertEqual(context.average_rating, Decimal("4"))

    def test_draft_context_is_empty_when_no_submitted_observations_exist(self):
        context = get_draft_context_for_draft_player(self.draft_player)

        self.assertTrue(context.is_matched)
        self.assertEqual(context.submitted_observation_count, 0)
        self.assertIsNone(context.average_rating)

    def test_draft_context_excludes_draft_and_reopened_observations(self):
        self.submitted_observation(self.coach, rating=5)
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            status=OBSERVATION_STATUS_DRAFT,
            responses={
                question: 1
                for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
            },
        )
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.third_coach,
            status=OBSERVATION_STATUS_REOPENED,
            responses={
                question: 1
                for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
            },
        )

        context = get_draft_context_for_draft_player(self.draft_player)

        self.assertEqual(context.submitted_observation_count, 1)
        self.assertEqual(context.latest_observation.evaluator_name, self.coach.username)

    def test_multiple_submitted_observations_are_ordered_newest_first(self):
        older = self.submitted_observation(self.coach, rating=3)
        newer = self.submitted_observation(self.other_coach, rating=5)
        Observation.objects.filter(pk=older.pk).update(submitted_at=timezone.now() - timedelta(days=2))
        Observation.objects.filter(pk=newer.pk).update(submitted_at=timezone.now() - timedelta(hours=1))

        context = get_draft_context_for_draft_player(self.draft_player)

        self.assertEqual(context.submitted_observation_count, 2)
        self.assertEqual([summary.evaluator_name for summary in context.observations], [self.other_coach.username, self.coach.username])
        self.assertEqual(context.average_rating, Decimal("4"))

    def test_draft_context_reports_unmatched_player(self):
        unmatched = DraftPlayer.objects.create(
            draft=self.draft,
            first_name="No",
            last_name="Match",
            full_name="No Match",
        )

        context = get_draft_context_for_draft_player(unmatched)

        self.assertFalse(context.is_matched)
        self.assertEqual(context.submitted_observation_count, 0)

    def test_ambiguous_player_match_does_not_select_observations(self):
        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")

        context = get_draft_contexts_for_draft(self.draft)[self.draft_player.id]

        self.assertFalse(context.is_matched)
        self.assertEqual(context.match_status, "ambiguous")
        self.assertEqual(context.submitted_observation_count, 0)


class PlayerExperienceServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
        self.player = Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birth_year=2012,
            division="13U",
            team_name="Expos",
        )
        self.other_player = Player.objects.create(
            first_name="Alex",
            last_name="Chen",
            birth_year=2011,
            division="15U",
            team_name="Mounties",
        )
        self.no_context_player = Player.objects.create(first_name="No", last_name="Context", division="13U")
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
        )
        self.draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
        self.team = DraftTeam.objects.create(draft=self.draft, name="Expos Navy", display_order=1)
        DraftTeam.objects.create(draft=self.draft, name="Expos Gold", display_order=2)
        self.draft_player = DraftPlayer.objects.create(
            draft=self.draft,
            first_name="Eugene",
            last_name="Lin",
            full_name="Eugene Lin",
            extra_data={"Birth Year": "2012"},
        )

    def rating_payload(self, value=4):
        return {
            question: value
            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
        }

    def submit_assessment(self, evaluator=None, player=None, value=4):
        result = create_coach_assessment_observation(
            player=player or self.player,
            evaluation_cycle=self.cycle,
            evaluator=evaluator or self.coach,
            responses=self.rating_payload(value),
        )
        return submit_observation(result.observation, actor=evaluator or self.coach)

    def test_timeline_includes_submitted_assessment_import_and_draft_context(self):
        observation = self.submit_assessment()
        PlayerSourceRow.objects.create(
            player=self.player,
            source="vcb_member_list_csv",
            source_filename="members.csv",
            row_number=2,
            original_row={"private": "do not render"},
        )
        DraftAction.objects.create(
            draft=self.draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=self.draft_player,
            to_team=self.team,
            pick_number=1,
        )

        timeline = get_player_timeline(self.player)

        self.assertEqual(timeline.coach_assessment_count, 1)
        self.assertEqual(timeline.import_count, 1)
        self.assertEqual(timeline.draft_context_count, 1)
        self.assertEqual({item.kind for item in timeline.items}, {"coach_assessment", "import", "draft_context"})
        self.assertTrue(any(str(observation.id) in item.url for item in timeline.items if item.url))

    def test_timeline_excludes_draft_and_reopened_observations(self):
        submitted = self.submit_assessment(evaluator=self.coach, value=5)
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            status=OBSERVATION_STATUS_DRAFT,
            responses=self.rating_payload(1),
        )
        third_coach = User.objects.create_user(username="thirdcoach", password="testpass")
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=third_coach,
            status=OBSERVATION_STATUS_REOPENED,
            responses=self.rating_payload(1),
        )

        timeline = get_player_timeline(self.player)

        self.assertEqual(timeline.coach_assessment_count, 1)
        self.assertEqual(timeline.items[0].metadata.get("evaluator"), submitted.evaluator.username)

    def test_timeline_handles_no_entries(self):
        timeline = get_player_timeline(self.other_player)

        self.assertEqual(timeline.items, [])
        self.assertEqual(timeline.coach_assessment_count, 0)

    def test_comparison_computes_scores_notes_tags_and_draft_context(self):
        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={**self.rating_payload(4), text_question: "Strong arm."},
        ).observation
        submit_observation(observation, actor=self.coach)
        assign_tag(self.player, "Strong Prospect")
        DraftAction.objects.create(
            draft=self.draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=self.draft_player,
            to_team=self.team,
            pick_number=1,
        )

        summary = get_player_score_summary(self.player)
        comparison = get_player_comparison([self.other_player, self.player])

        self.assertEqual(summary.average_rating, Decimal("4"))
        self.assertEqual(summary.evaluator_count, 1)
        self.assertIn("Strong arm.", summary.notes)
        self.assertEqual([tag.name for tag in summary.tags], ["Strong Prospect"])
        self.assertEqual(len(summary.draft_contexts), 1)
        self.assertEqual([player.id for player in comparison.players], [self.other_player.id, self.player.id])
        self.assertIn("Throw", comparison.category_names)

    def test_search_filters_by_name_team_division_birth_year_tag_source_and_evaluation(self):
        assign_tag(self.player, "Future AAA")
        PlayerSourceRow.objects.create(player=self.player, source="vcb_member_list_csv", source_filename="members.csv")
        self.submit_assessment()

        expectations = [
            ({"q": "Eug"}, [self.player]),
            ({"team": "Expos"}, [self.player]),
            ({"division": "13U"}, [self.no_context_player, self.player]),
            ({"birth_year": "2012"}, [self.player]),
            ({"tag": "future-aaa"}, [self.player]),
            ({"source": "vcb_member_list_csv"}, [self.player]),
            ({"evaluation": EVALUATION_HAS_SUBMITTED}, [self.player]),
            ({"evaluation": EVALUATION_NO_SUBMITTED}, [self.other_player, self.no_context_player]),
            ({"evaluation": EVALUATION_HAS_ANY}, [self.player]),
            ({"evaluation": EVALUATION_NOT_STARTED}, [self.other_player, self.no_context_player]),
        ]
        for params, expected_players in expectations:
            with self.subTest(params=params):
                result = search_players(parse_player_search_filters(params))
                self.assertEqual([player.id for player in result.players], [player.id for player in expected_players])

    def test_search_filters_by_draft_status_and_ignores_invalid_birth_year(self):
        available_player = Player.objects.create(first_name="Ava", last_name="Lopez", birth_year=2012, division="13U")
        DraftPlayer.objects.create(
            draft=self.draft,
            first_name="Ava",
            last_name="Lopez",
            full_name="Ava Lopez",
            extra_data={"Birth Year": "2012"},
        )
        DraftAction.objects.create(
            draft=self.draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=self.draft_player,
            to_team=self.team,
            pick_number=1,
        )

        drafted = search_players(parse_player_search_filters({"draft_status": DRAFT_STATUS_DRAFTED}))
        available = search_players(parse_player_search_filters({"draft_status": DRAFT_STATUS_AVAILABLE}))
        no_context = search_players(parse_player_search_filters({"draft_status": DRAFT_STATUS_NO_CONTEXT}))
        invalid = search_players(parse_player_search_filters({"birth_year": "not-a-year"}))

        self.assertIn(self.player, drafted.players)
        self.assertIn(available_player, available.players)
        self.assertIn(self.no_context_player, no_context.players)
        self.assertIn(self.player, invalid.players)


class PlayerExperienceViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.player = Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birth_year=2012,
            division="13U",
            team_name="Expos",
            bats="R",
            throws="R",
            primary_positions="SS",
        )
        self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="15U", team_name="Mounties")
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
        )

    def rating_payload(self, value=4):
        return {
            question: value
            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
        }

    def test_player_experience_views_require_staff(self):
        profile_url = reverse("analytics:player-profile", kwargs={"player_id": self.player.id})
        for url in [reverse("analytics:player-search"), profile_url, reverse("analytics:player-compare")]:
            with self.subTest(url=url):
                self.client.logout()
                self.assertEqual(self.client.get(url).status_code, 302)
                self.client.force_login(self.coach)
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_player_search_view_renders_filters_and_results(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:player-search"), {"q": "Eugene"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Player Search")
        self.assertContains(response, self.player.display_name)
        self.assertNotContains(response, self.other_player.display_name)

    def test_player_profile_renders_phase_six_context_without_raw_import_json(self):
        assign_tag(self.player, "Strong Prospect")
        PlayerSourceRow.objects.create(
            player=self.player,
            source="vcb_member_list_csv",
            source_filename="members.csv",
            row_number=2,
            original_row={"private": "secret value"},
        )
        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={**self.rating_payload(4), text_question: "Good teammate."},
        ).observation
        submit_observation(observation, actor=self.coach)
        draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
        team = DraftTeam.objects.create(draft=draft, name="Expos Navy", display_order=1)
        DraftTeam.objects.create(draft=draft, name="Expos Gold", display_order=2)
        draft_player = DraftPlayer.objects.create(
            draft=draft,
            first_name="Eugene",
            last_name="Lin",
            full_name="Eugene Lin",
            extra_data={"Birth Year": "2012"},
        )
        DraftAction.objects.create(
            draft=draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=draft_player,
            to_team=team,
            pick_number=1,
        )
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:player-profile", kwargs={"player_id": self.player.id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Strong Prospect")
        self.assertContains(response, "vcb_member_list_csv")
        self.assertContains(response, "Good teammate.")
        self.assertContains(response, "Draft Context")
        self.assertContains(response, "Timeline")
        self.assertNotContains(response, "secret value")

    def test_player_profile_empty_states(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:player-profile", kwargs={"player_id": self.other_player.id}))

        self.assertContains(response, "No tags assigned.")
        self.assertContains(response, "No imported source rows.")
        self.assertContains(response, "No draft context found.")
        self.assertContains(response, "No submitted coach assessments yet.")
        self.assertContains(response, "No timeline entries yet.")

    def test_player_compare_handles_empty_selected_and_selected_players(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.rating_payload(4),
        ).observation
        submit_observation(observation, actor=self.coach)
        self.client.force_login(self.staff)

        empty_response = self.client.get(reverse("analytics:player-compare"))
        selected_response = self.client.get(reverse("analytics:player-compare"), {"players": [str(self.player.id), str(self.other_player.id)]})

        self.assertContains(empty_response, "Select players to compare.")
        self.assertContains(selected_response, self.player.display_name)
        self.assertContains(selected_response, "4.0")
        self.assertContains(selected_response, "No submitted assessments")

    def test_player_compare_caps_selected_players(self):
        extra_players = [
            Player.objects.create(first_name=f"Player{i}", last_name="Test", division="13U")
            for i in range(10)
        ]
        ids = [str(player.id) for player in extra_players]
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:player-compare"), {"players": ids})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["selected_players"]), 6)

    def test_phase_six_regression_existing_pages_render(self):
        self.client.force_login(self.staff)

        self.assertEqual(self.client.get(reverse("analytics:assessment-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:observation-review-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:import-list")).status_code, 200)


class AnalyticsCommandCenterServiceTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
        self.player = Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birth_year=2012,
            division="13U",
            team_name="Expos",
        )
        self.other_player = Player.objects.create(
            first_name="Alex",
            last_name="Chen",
            birth_year=2011,
            division="15U",
            team_name="Mounties",
        )
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
        )

    def rating_payload(self, value=4):
        return {
            question: value
            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
        }

    def submit_assessment(self, evaluator=None, player=None, value=4):
        result = create_coach_assessment_observation(
            player=player or self.player,
            evaluation_cycle=self.cycle,
            evaluator=evaluator or self.coach,
            responses=self.rating_payload(value),
        )
        return submit_observation(result.observation, actor=evaluator or self.coach)

    def test_player_population_helpers_live_in_player_service(self):
        self.assertIn(self.player.id, active_player_ids(division="13U"))
        self.assertNotIn(self.other_player.id, active_player_ids(division="13U"))

        result = search_players(parse_player_search_filters({"q": "Eugene"}))

        self.assertEqual(result.players, [self.player])

    def test_completion_and_observation_metrics_respect_cycle_and_filters(self):
        self.submit_assessment(value=5)
        create_coach_assessment_observation(
            player=self.other_player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            status=OBSERVATION_STATUS_DRAFT,
            responses=self.rating_payload(2),
        )

        completion = completion_metrics(cycle=self.cycle, division="13U")
        observations = observation_metrics(cycle=self.cycle, division="13U")

        self.assertEqual(completion.total_active_players, 1)
        self.assertEqual(completion.players_with_submitted_assessment, 1)
        self.assertEqual(completion.players_without_submitted_assessment, 0)
        self.assertEqual(completion.completion_rate, Decimal("100"))
        self.assertEqual(observations.submitted_count, 1)
        self.assertEqual(observations.draft_count, 0)
        self.assertEqual(observations.by_category_average[0].average, Decimal("5"))

    def test_metrics_exclude_draft_and_reopened_from_submitted_rating_summaries(self):
        self.submit_assessment(evaluator=self.coach, value=5)
        create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            status=OBSERVATION_STATUS_REOPENED,
            responses=self.rating_payload(1),
        )

        observations = observation_metrics(cycle=self.cycle)

        averages = {row.label: row.average for row in observations.by_category_average}
        self.assertTrue(averages)
        self.assertEqual(set(averages.values()), {Decimal("5")})

    def test_coach_to_coach_spread_requires_two_evaluators(self):
        self.submit_assessment(evaluator=self.coach, value=2)
        self.submit_assessment(evaluator=self.other_coach, value=5)

        observations = observation_metrics(cycle=self.cycle)

        self.assertTrue(observations.variance_rows)
        self.assertEqual(observations.variance_rows[0].player, self.player)
        self.assertEqual(observations.variance_rows[0].spread, Decimal("3"))

    def test_import_summary_counts_statuses_and_rows(self):
        PlayerImportBatch.objects.create(
            source="member_list",
            original_filename="members.csv",
            status=PlayerImportStatus.NEEDS_REVIEW,
            rows_created=1,
            rows_updated=2,
            rows_skipped=3,
            rows_conflicted=4,
        )
        PlayerImportBatch.objects.create(
            source="member_list",
            original_filename="committed.csv",
            status=PlayerImportStatus.COMMITTED,
        )

        summary = import_metrics()

        self.assertEqual(summary.total_batches, 2)
        self.assertEqual(summary.needs_review_count, 1)
        self.assertEqual(summary.committed_count, 1)
        self.assertEqual(summary.rows_created, 1)
        self.assertEqual(summary.rows_conflicted, 4)
        self.assertEqual(len(summary.recent_batches), 2)

    def test_draft_matching_summary_uses_draft_context_and_detects_mismatch(self):
        expected_round_question = ObservationQuestion.objects.create(
            question_set=self.setup_result.question_set,
            key="expected_draft_round",
            prompt="Expected draft round",
            response_type=RESPONSE_TYPE_TEXT,
            metadata={"draft_context_field": "expected_draft_round"},
            display_order=100,
        )
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={**self.rating_payload(4), expected_round_question: "1"},
        ).observation
        submit_observation(observation, actor=self.coach)
        draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
        team = DraftTeam.objects.create(draft=draft, name="Expos Navy", display_order=1)
        DraftTeam.objects.create(draft=draft, name="Expos Gold", display_order=2)
        draft_player = DraftPlayer.objects.create(
            draft=draft,
            first_name="Eugene",
            last_name="Lin",
            full_name="Eugene Lin",
            extra_data={"Birth Year": "2012"},
        )
        DraftPlayer.objects.create(draft=draft, first_name="No", last_name="Match", full_name="No Match")
        DraftAction.objects.create(
            draft=draft,
            action_type=DraftActionType.PLAYER_DRAFTED,
            player=draft_player,
            to_team=team,
            pick_number=3,
        )

        summary = draft_matching_metrics(division="13U")

        self.assertEqual(summary.matched_player_count, 1)
        self.assertEqual(summary.drafted_player_count, 1)
        self.assertEqual(summary.no_context_player_count, 0)
        self.assertEqual(summary.unmatched_draft_player_count, 1)
        self.assertEqual(summary.expected_round_mismatch_count, 1)
        self.assertEqual(summary.mismatches[0].player, self.player)

    def test_recent_observations_are_ordered_and_limited(self):
        older = self.submit_assessment(evaluator=self.coach, value=3)
        newer = self.submit_assessment(evaluator=self.other_coach, value=4)
        Observation.objects.filter(pk=older.pk).update(submitted_at=timezone.now() - timedelta(days=1))
        Observation.objects.filter(pk=newer.pk).update(submitted_at=timezone.now())

        observations = recent_submitted_observations(cycle=self.cycle, limit=1)

        self.assertEqual(observations, [Observation.objects.get(pk=newer.pk)])

    def test_reporting_context_is_grouped_and_template_ready(self):
        self.submit_assessment()

        context = get_command_center_context(cycle_id=self.cycle.id, division="13U")

        self.assertTrue(context.summary_cards)
        self.assertEqual(context.completion_summary.active_cycle, self.cycle)
        self.assertTrue(context.observation_summary.by_category_average)
        self.assertIsNotNone(context.import_summary)
        self.assertIsNotNone(context.draft_summary)
        self.assertTrue(context.recent_observations)
        self.assertTrue(context.navigation_links)
        self.assertFalse(hasattr(context, "total_active_players"))


class AnalyticsCommandCenterViewTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U", team_name="Expos")
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
        )

    def rating_payload(self, value=4):
        return {
            question: value
            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
        }

    def test_command_center_requires_staff(self):
        url = reverse("analytics:command-center")
        self.assertEqual(self.client.get(url).status_code, 302)

        self.client.force_login(self.coach)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_staff_can_render_command_center_links_and_empty_states(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:command-center"), {"cycle": "not-a-number"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analytics Command Center")
        self.assertContains(response, reverse("analytics:import-list"))
        self.assertContains(response, reverse("analytics:player-search"))
        self.assertContains(response, reverse("analytics:player-compare"))
        self.assertContains(response, reverse("analytics:assessment-list"))
        self.assertContains(response, reverse("analytics:observation-review-list"))
        self.assertContains(response, "No player imports yet.")
        self.assertContains(response, "No submitted observations yet.")

    def test_command_center_renders_populated_summaries_and_filters(self):
        observation = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses=self.rating_payload(4),
        ).observation
        submit_observation(observation, actor=self.coach)
        PlayerImportBatch.objects.create(source="member_list", original_filename="members.csv", status=PlayerImportStatus.COMMITTED)
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:command-center"), {"division": "13U", "team": "Expos"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Submitted assessments")
        self.assertContains(response, "Completion rate")
        self.assertContains(response, "Average Score By Category")
        self.assertContains(response, "members.csv")
        self.assertContains(response, self.player.display_name)
        self.assertEqual(response.context["filters"]["division"], "13U")
        self.assertEqual(response.context["filters"]["team"], "Expos")

    def test_phase_seven_regression_existing_pages_render(self):
        self.client.force_login(self.staff)

        self.assertEqual(self.client.get(reverse("analytics:player-search")).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:player-profile", kwargs={"player_id": self.player.id})).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:player-compare")).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:import-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:assessment-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("analytics:observation-review-list")).status_code, 200)


class CoachAssessmentWorkflowTests(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(username="coach", password="testpass")
        self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U", team_name="Expos")
        self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="13U", team_name="Expos")
        self.setup_result = ensure_default_coach_assessment_setup()
        self.cycle = EvaluationCycle.objects.create(
            name="2026 13U Coach Assessment",
            cycle_type="Coach Assessment",
            coach_assessment_question_set=self.setup_result.question_set,
        )

    def response_payload(self, include_required=True):
        data = {}
        for question in self.setup_result.question_set.questions.filter(is_active=True):
            field_name = f"question_{question.id}"
            if question.response_type == RESPONSE_TYPE_RATING_1_5 and include_required:
                data[field_name] = "4"
            elif question.response_type == RESPONSE_TYPE_TEXT:
                data[field_name] = "Good teammate."
        return data

    def test_dynamic_form_uses_configured_questions(self):
        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
        question.prompt = "Edited dynamic question"
        question.save()

        form = CoachAssessmentForm(question_set=self.setup_result.question_set)

        self.assertIn(f"question_{question.id}", form.fields)
        self.assertEqual(form.fields[f"question_{question.id}"].label, "Edited dynamic question")

    def test_assessment_list_requires_login_and_lists_players(self):
        response = self.client.get(reverse("analytics:assessment-list"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.coach)
        response = self.client.get(reverse("analytics:assessment-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)
        self.assertContains(response, "Not started")

    def test_invalid_cycle_parameter_does_not_crash_assessment_list(self):
        self.client.force_login(self.coach)

        response = self.client.get(reverse("analytics:assessment-list"), {"cycle": "not-a-number"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)

    def test_coach_can_open_dynamic_assessment_form_for_any_active_player(self):
        prompt = self.setup_result.question_set.questions.first().prompt
        self.client.force_login(self.coach)

        response = self.client.get(reverse("analytics:assessment-player", kwargs={"player_id": self.other_player.id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.other_player.display_name)
        self.assertContains(response, prompt)

    def test_invalid_cycle_parameter_does_not_crash_assessment_form(self):
        self.client.force_login(self.coach)

        response = self.client.get(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}), {"cycle": "bad"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)

    def test_assessment_edit_uses_submit_permission_helper(self):
        self.client.force_login(self.coach)

        with patch("analytics.views.can_submit_coach_assessment", return_value=False):
            response = self.client.get(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}))

        self.assertEqual(response.status_code, 403)

    def test_coach_can_save_partial_draft(self):
        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
        self.client.force_login(self.coach)

        response = self.client.post(
            reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}),
            {"action": "save_draft", f"question_{question.id}": "3"},
        )

        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
        self.assertEqual(observation.responses.get(question=question).numeric_value, Decimal("3.00"))

    def test_submit_missing_required_responses_is_rejected(self):
        self.client.force_login(self.coach)

        response = self.client.post(
            reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}),
            {"action": "submit"},
        )

        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
        self.assertContains(response, "This field is required")

    def test_coach_can_submit_complete_assessment(self):
        self.client.force_login(self.coach)
        data = {"action": "submit"}
        data.update(self.response_payload())

        response = self.client.post(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}), data)

        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
        self.assertIsNotNone(observation.submitted_at)
        self.assertEqual(observation.responses.count(), len(self.response_payload()))

    def test_submitted_assessment_redirects_instead_of_creating_duplicate(self):
        self.client.force_login(self.coach)
        data = {"action": "submit"}
        data.update(self.response_payload())
        self.client.post(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}), data)
        observation = Observation.objects.get(player=self.player, evaluator=self.coach)

        response = self.client.get(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
        self.assertEqual(Observation.objects.filter(player=self.player, evaluator=self.coach).count(), 1)

    def test_multiple_evaluators_can_submit_for_same_player(self):
        for user in [self.coach, self.other_coach]:
            self.client.force_login(user)
            data = {"action": "submit"}
            data.update(self.response_payload())
            self.client.post(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}), data)

        self.assertEqual(Observation.objects.filter(player=self.player, status=OBSERVATION_STATUS_SUBMITTED).count(), 2)

    def test_coach_cannot_view_or_edit_other_evaluator_observation(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.other_coach,
            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
        )
        submit_observation(result.observation)
        self.client.force_login(self.coach)

        detail_response = self.client.get(reverse("analytics:assessment-detail", kwargs={"observation_id": result.observation.id}))
        edit_response = self.client.get(reverse("analytics:assessment-edit", kwargs={"observation_id": result.observation.id}))

        self.assertEqual(detail_response.status_code, 403)
        self.assertEqual(edit_response.status_code, 403)

    def test_coach_detail_context_controls_edit_and_back_link(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
        )
        self.client.force_login(self.coach)

        response = self.client.get(reverse("analytics:assessment-detail", kwargs={"observation_id": result.observation.id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("analytics:assessment-edit", kwargs={"observation_id": result.observation.id}))
        self.assertContains(response, f'href="{reverse("analytics:assessment-list")}"')

    def test_staff_review_requires_staff_and_displays_observation(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
        )
        submit_observation(result.observation)

        self.client.force_login(self.coach)
        self.assertEqual(self.client.get(reverse("analytics:observation-review-list")).status_code, 403)

        self.client.force_login(self.staff)
        list_response = self.client.get(reverse("analytics:observation-review-list"))
        detail_response = self.client.get(reverse("analytics:observation-review-detail", kwargs={"observation_id": result.observation.id}))

        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, self.player.display_name)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, result.observation.evaluator.username)

    def test_staff_review_search_uses_single_q_filter(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
        )
        submit_observation(result.observation)
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:observation-review-list"), {"q": self.coach.username})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.display_name)

    def test_invalid_cycle_parameter_does_not_crash_staff_review_list(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:observation-review-list"), {"cycle": "bad"})

        self.assertEqual(response.status_code, 200)

    def test_staff_review_detail_back_link_returns_to_review_list(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
        )
        submit_observation(result.observation)
        self.client.force_login(self.staff)

        response = self.client.get(reverse("analytics:observation-review-detail", kwargs={"observation_id": result.observation.id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="{reverse("analytics:observation-review-list")}"')

    def test_staff_can_reopen_submitted_observation(self):
        result = create_coach_assessment_observation(
            player=self.player,
            evaluation_cycle=self.cycle,
            evaluator=self.coach,
            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
        )
        submit_observation(result.observation)
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("analytics:observation-review-detail", kwargs={"observation_id": result.observation.id}),
            {"action": "reopen"},
        )

        result.observation.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(result.observation.status, OBSERVATION_STATUS_REOPENED)
