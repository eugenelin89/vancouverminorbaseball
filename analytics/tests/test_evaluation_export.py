import csv
import io

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from accounts.models import AccountRole
from accounts.services.profile_service import set_account_role
from analytics.models import (
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    EvaluationCycle,
    ObservationResponse,
)
from analytics.services.evaluation_export_service import (
    export_submitted_evaluations_csv,
)
from analytics.services.observation_service import (
    create_coach_assessment_observation,
    submit_observation,
)
from analytics.services.question_service import ensure_default_coach_assessment_setup
from analytics.tests.helpers import attach_player_to_season
from players.models import Player
from seasons.services.season_service import create_season

User = get_user_model()


class EvaluationExportTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff-export", password="testpass", is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            username="admin-export", password="testpass", email="admin@example.com"
        )
        self.coach = User.objects.create_user(
            username="coach-export", password="testpass"
        )
        self.role_admin = User.objects.create_user(
            username="role-admin-export", password="testpass"
        )
        set_account_role(self.staff, AccountRole.STAFF)
        set_account_role(self.coach, AccountRole.COACH)
        set_account_role(self.role_admin, AccountRole.ADMIN)
        self.player = Player.objects.create(
            first_name="Renée", last_name="Sample", division="13U", team_name="Yankees"
        )
        self.other_player = Player.objects.create(
            first_name="Other", last_name="Player", division="13U", team_name="Expos"
        )
        self.season = create_season(
            key="export-spring-2026", name="Spring 2026", is_current=True
        )
        self.other_season = create_season(key="export-summer-2026", name="Summer 2026")
        attach_player_to_season(
            self.player, self.season, team_name="Yankees", division="13U"
        )
        attach_player_to_season(
            self.other_player, self.season, team_name="Expos", division="13U"
        )
        attach_player_to_season(
            self.other_player, self.other_season, team_name="Expos", division="13U"
        )
        question_set = ensure_default_coach_assessment_setup().question_set
        self.cycle = EvaluationCycle.objects.create(
            name="Spring 2026 Post Season",
            cycle_type="Post Season",
            season=self.season,
            coach_assessment_question_set=question_set,
        )
        self.other_cycle = EvaluationCycle.objects.create(
            name="Summer 2026",
            cycle_type="Summer",
            season=self.other_season,
            coach_assessment_question_set=question_set,
        )
        self.question_set = question_set
        self.url = reverse("analytics:evaluation-review-export")

    def observation(
        self, *, player=None, evaluator=None, cycle=None, note="=1+1", submit=True
    ):
        responses = {
            question: 4
            for question in self.question_set.questions.filter(
                response_type=RESPONSE_TYPE_RATING_1_5,
                is_required=True,
                is_active=True,
            )
        }
        text_question = self.question_set.questions.filter(
            response_type=RESPONSE_TYPE_TEXT, is_active=True
        ).first()
        if text_question:
            responses[text_question] = note
        actor = evaluator or self.coach
        result = create_coach_assessment_observation(
            player=player or self.player,
            evaluation_cycle=cycle or self.cycle,
            evaluator=actor,
            responses=responses,
        )
        if submit:
            submit_observation(result.observation, actor=actor)
        return result.observation

    def read_csv(self, response):
        content = b"".join(response.streaming_content).decode("utf-8-sig")
        return list(csv.DictReader(io.StringIO(content)))

    def test_staff_export_uses_submitted_review_filters_and_response_rows(self):
        included = self.observation()
        excluded = self.observation(
            player=self.other_player,
            cycle=self.other_cycle,
            evaluator=self.staff,
            note="Other season.",
        )
        draft = self.observation(
            player=self.other_player,
            evaluator=self.coach,
            submit=False,
        )
        self.client.force_login(self.staff)

        response = self.client.get(
            self.url, {"season": str(self.season.id), "cycle": str(self.cycle.id)}
        )
        rows = self.read_csv(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertTrue(rows)
        self.assertEqual({row["observation_id"] for row in rows}, {str(included.id)})
        self.assertNotIn(str(excluded.id), {row["observation_id"] for row in rows})
        self.assertNotIn(str(draft.id), {row["observation_id"] for row in rows})
        self.assertEqual({row["player_name"] for row in rows}, {"Renée Sample"})
        self.assertEqual({row["season"] for row in rows}, {"Spring 2026"})
        self.assertEqual({row["cycle"] for row in rows}, {"Spring 2026 Post Season"})
        self.assertTrue(all(row["question_key"] for row in rows))
        self.assertTrue(all(row["question_set_version"] == "1" for row in rows))
        self.assertIn("'=1+1", {row["text_value"] for row in rows})

    def test_all_django_staff_can_export_but_metadata_roles_cannot(self):
        self.observation()
        for user in (self.staff, self.superuser):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                self.assertEqual(self.client.get(self.url).status_code, 200)
                self.assertContains(
                    self.client.get(reverse("analytics:evaluation-review-list")),
                    self.url,
                )

        for user in (self.coach, self.role_admin):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                self.assertEqual(self.client.get(self.url).status_code, 403)
                self.assertNotContains(
                    self.client.get(reverse("analytics:evaluation-review-list")),
                    self.url,
                )

        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_export_escapes_spreadsheet_formula_and_preserves_multiline_text(self):
        self.observation(note='  =HYPERLINK("https://example.com")\nsecond line')
        self.client.force_login(self.staff)

        rows = self.read_csv(self.client.get(self.url))

        text_rows = [row for row in rows if row["text_value"]]
        self.assertEqual(len(text_rows), 1)
        self.assertEqual(
            text_rows[0]["text_value"],
            '\'  =HYPERLINK("https://example.com")\nsecond line',
        )

    def test_empty_export_still_has_header(self):
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        content = b"".join(response.streaming_content).decode("utf-8-sig")

        self.assertIn("observation_id,submitted_at,player_id", content)
        self.assertEqual(list(csv.DictReader(io.StringIO(content))), [])

    def test_export_keeps_observations_with_no_saved_responses(self):
        observation = self.observation()
        ObservationResponse.objects.filter(observation=observation).delete()
        self.client.force_login(self.staff)

        rows = self.read_csv(self.client.get(self.url))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["observation_id"], str(observation.id))
        self.assertEqual(rows[0]["question_key"], "")

    def test_export_prefetches_responses_for_multiple_evaluations(self):
        self.observation(evaluator=self.coach)
        self.observation(evaluator=self.staff)

        with CaptureQueriesContext(connection) as queries:
            lines = list(export_submitted_evaluations_csv(self.staff, {}))

        self.assertEqual(len(queries), 3)
        self.assertGreater(len(lines), 2)
