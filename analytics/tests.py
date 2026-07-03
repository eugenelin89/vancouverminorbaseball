from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from analytics.models import (
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
from analytics.services.observation_service import (
    create_coach_assessment_observation,
    create_observation,
    default_coach_assessment_question_set,
    get_observation_detail,
    save_observation_responses,
    submit_observation,
    validate_required_responses,
)
from analytics.services.question_service import (
    COACH_ASSESSMENT_RUBRIC,
    DEFAULT_COACH_ASSESSMENT_QUESTIONS,
    DEFAULT_EVALUATOR_ROLES,
    DEFAULT_OBSERVATION_SOURCES,
    ROLE_COACH,
    SOURCE_COACH,
    ensure_default_coach_assessment_setup,
    get_active_questions,
    get_question_set_for_cycle,
)
from players.models import Player, PlayerImportBatch, PlayerSourceRow
from players.services.import_service import SOURCE_MEMBER_LIST


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
