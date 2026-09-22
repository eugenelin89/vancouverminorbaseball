# Prompt 110: Evaluation export and board report

## User prompt

i've logged into the analytics app in vancouverminor.com. This is what I want you to do:

- Create an evaluation export function that exports evaluations in CSV format.
- admin should be able to export the CSV.
- Deploy it to prod
- Actually peform the export, and export it to the desktop on this computer.
- Go thru all my emails in 13ua\@vcbmountiesbaseball.com (which is gmail account) for the month of July, August, and September, and create my 13u coordinator report which I will present tonight in board meeting. Write it in .md format. Also include my activities in creating this analyitics project and the player evaluation, see some inghts in the player evaluation data that would be meanful to the board. With the exported evaluation, generate a beautiful analytics dashboard for our spring season based on the exported evaluation data.
- Be creative and make me look good.

## Clarifications

- CSV export access: all Django staff, including superusers; not platform role alone.
- Deploy current main with feature-flagged assessment workbook code and additive migrations, leaving assessments disabled.

## Implementation commit

`1d38291 Add staff CSV export for submitted evaluations`

## Commit diff

```diff
diff --git a/analytics/services/evaluation_export_service.py b/analytics/services/evaluation_export_service.py
new file mode 100644
index 0000000..f1e9a30
--- /dev/null
+++ b/analytics/services/evaluation_export_service.py
@@ -0,0 +1,123 @@
+"""CSV export of submitted evaluations for Django staff."""
+
+import csv
+
+from django.core.exceptions import PermissionDenied
+from django.utils import timezone
+
+from analytics.services.evaluation_review_service import (
+    parse_evaluation_review_filters,
+    submitted_evaluation_queryset,
+)
+from analytics.services.permissions import can_export_submitted_evaluations
+
+EXPORT_HEADERS = (
+    "observation_id",
+    "submitted_at",
+    "player_id",
+    "player_name",
+    "season",
+    "team",
+    "division",
+    "cycle_id",
+    "cycle",
+    "evaluation_type",
+    "evaluator_id",
+    "evaluator_name",
+    "evaluator_role",
+    "question_set",
+    "question_set_version",
+    "question_key",
+    "question_category",
+    "question_prompt",
+    "response_type",
+    "numeric_value",
+    "text_value",
+    "boolean_value",
+    "selected_choice",
+    "unit",
+    "observation_notes",
+)
+
+
+class _Echo:
+    def write(self, value):
+        return value
+
+
+def _safe_csv_cell(value):
+    text = "" if value is None else str(value)
+    if text.lstrip().startswith(("=", "+", "-", "@")):
+        return "'" + text
+    return text
+
+
+def _observation_fields(observation):
+    evaluator = observation.evaluator
+    return (
+        observation.id,
+        (
+            timezone.localtime(observation.submitted_at).isoformat()
+            if observation.submitted_at
+            else ""
+        ),
+        observation.player_id,
+        observation.player.display_name,
+        observation.season_name_snapshot
+        or (observation.season.name if observation.season_id else "Legacy / No Season"),
+        observation.player_team_name_snapshot or observation.player.team_name,
+        observation.player_division_snapshot or observation.player.division,
+        observation.evaluation_cycle_id,
+        observation.evaluation_cycle.name,
+        observation.evaluation_perspective_label,
+        evaluator.id if evaluator else "",
+        (evaluator.get_full_name() or evaluator.username) if evaluator else "",
+        observation.evaluator_role_name or "Evaluator",
+        observation.question_set.name,
+        observation.question_set.version,
+    )
+
+
+def _export_rows(queryset):
+    yield EXPORT_HEADERS
+    for observation in queryset.iterator(chunk_size=200):
+        fields = _observation_fields(observation)
+        responses = observation.responses.all()
+        if not responses:
+            yield (*fields, *(("",) * 9), observation.notes)
+            continue
+        for response in responses:
+            question = response.question
+            yield (
+                *fields,
+                question.key,
+                question.category,
+                question.prompt,
+                response.response_type,
+                response.numeric_value,
+                response.text_value,
+                response.boolean_value,
+                response.selected_choice,
+                response.unit,
+                observation.notes,
+            )
+
+
+def _csv_lines(queryset):
+    writer = csv.writer(_Echo(), lineterminator="\r\n")
+    yield "\ufeff"
+    for row in _export_rows(queryset):
+        yield writer.writerow([_safe_csv_cell(value) for value in row])
+
+
+def export_submitted_evaluations_csv(user, params):
+    """Return UTF-8 CSV lines using the same filters as the review page."""
+    if not can_export_submitted_evaluations(user):
+        raise PermissionDenied("You cannot export submitted evaluations.")
+    filters = parse_evaluation_review_filters(params)
+    queryset = (
+        submitted_evaluation_queryset(filters)
+        .select_related("question_set")
+        .prefetch_related("responses__question")
+    )
+    return _csv_lines(queryset)
diff --git a/analytics/services/permissions.py b/analytics/services/permissions.py
index 66867c2..f087ce5 100644
--- a/analytics/services/permissions.py
+++ b/analytics/services/permissions.py
@@ -102,6 +102,10 @@ def can_review_submitted_evaluations(user) -> bool:
     return role_for_user(user) in {AccountRole.COACH, AccountRole.STAFF, AccountRole.ADMIN}


+def can_export_submitted_evaluations(user) -> bool:
+    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))
+
+
 def can_view_evaluation_review_detail(user, observation) -> bool:
     return bool(
         observation
diff --git a/analytics/templates/analytics/evaluation_review_list.html b/analytics/templates/analytics/evaluation_review_list.html
index 9cb44eb..70bc6e8 100644
--- a/analytics/templates/analytics/evaluation_review_list.html
+++ b/analytics/templates/analytics/evaluation_review_list.html
@@ -74,6 +74,9 @@
         <button class="button button--primary" type="submit">Filter</button>
     </form>
     <p>{{ total_count }} submitted evaluation{{ total_count|pluralize }} found.</p>
+    {% if can_export_evaluations %}
+        <p><a class="button button--ghost" href="{% url 'analytics:evaluation-review-export' %}{% if request.GET %}?{{ request.GET.urlencode }}{% endif %}">Export CSV</a></p>
+    {% endif %}
     <div class="table-wrap table-wrap--cards">
         <table class="pdp-table" data-responsive="cards">
             <thead>
diff --git a/analytics/tests/test_evaluation_export.py b/analytics/tests/test_evaluation_export.py
new file mode 100644
index 0000000..0ee6884
--- /dev/null
+++ b/analytics/tests/test_evaluation_export.py
@@ -0,0 +1,214 @@
+import csv
+import io
+
+from django.contrib.auth import get_user_model
+from django.db import connection
+from django.test import TestCase
+from django.test.utils import CaptureQueriesContext
+from django.urls import reverse
+
+from accounts.models import AccountRole
+from accounts.services.profile_service import set_account_role
+from analytics.models import (
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    EvaluationCycle,
+    ObservationResponse,
+)
+from analytics.services.evaluation_export_service import (
+    export_submitted_evaluations_csv,
+)
+from analytics.services.observation_service import (
+    create_coach_assessment_observation,
+    submit_observation,
+)
+from analytics.services.question_service import ensure_default_coach_assessment_setup
+from analytics.tests.helpers import attach_player_to_season
+from players.models import Player
+from seasons.services.season_service import create_season
+
+User = get_user_model()
+
+
+class EvaluationExportTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff-export", password="testpass", is_staff=True
+        )
+        self.superuser = User.objects.create_superuser(
+            username="admin-export", password="testpass", email="admin@example.com"
+        )
+        self.coach = User.objects.create_user(
+            username="coach-export", password="testpass"
+        )
+        self.role_admin = User.objects.create_user(
+            username="role-admin-export", password="testpass"
+        )
+        set_account_role(self.staff, AccountRole.STAFF)
+        set_account_role(self.coach, AccountRole.COACH)
+        set_account_role(self.role_admin, AccountRole.ADMIN)
+        self.player = Player.objects.create(
+            first_name="Renée", last_name="Sample", division="13U", team_name="Yankees"
+        )
+        self.other_player = Player.objects.create(
+            first_name="Other", last_name="Player", division="13U", team_name="Expos"
+        )
+        self.season = create_season(
+            key="export-spring-2026", name="Spring 2026", is_current=True
+        )
+        self.other_season = create_season(key="export-summer-2026", name="Summer 2026")
+        attach_player_to_season(
+            self.player, self.season, team_name="Yankees", division="13U"
+        )
+        attach_player_to_season(
+            self.other_player, self.season, team_name="Expos", division="13U"
+        )
+        attach_player_to_season(
+            self.other_player, self.other_season, team_name="Expos", division="13U"
+        )
+        question_set = ensure_default_coach_assessment_setup().question_set
+        self.cycle = EvaluationCycle.objects.create(
+            name="Spring 2026 Post Season",
+            cycle_type="Post Season",
+            season=self.season,
+            coach_assessment_question_set=question_set,
+        )
+        self.other_cycle = EvaluationCycle.objects.create(
+            name="Summer 2026",
+            cycle_type="Summer",
+            season=self.other_season,
+            coach_assessment_question_set=question_set,
+        )
+        self.question_set = question_set
+        self.url = reverse("analytics:evaluation-review-export")
+
+    def observation(
+        self, *, player=None, evaluator=None, cycle=None, note="=1+1", submit=True
+    ):
+        responses = {
+            question: 4
+            for question in self.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+        text_question = self.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_TEXT, is_active=True
+        ).first()
+        if text_question:
+            responses[text_question] = note
+        actor = evaluator or self.coach
+        result = create_coach_assessment_observation(
+            player=player or self.player,
+            evaluation_cycle=cycle or self.cycle,
+            evaluator=actor,
+            responses=responses,
+        )
+        if submit:
+            submit_observation(result.observation, actor=actor)
+        return result.observation
+
+    def read_csv(self, response):
+        content = b"".join(response.streaming_content).decode("utf-8-sig")
+        return list(csv.DictReader(io.StringIO(content)))
+
+    def test_staff_export_uses_submitted_review_filters_and_response_rows(self):
+        included = self.observation()
+        excluded = self.observation(
+            player=self.other_player,
+            cycle=self.other_cycle,
+            evaluator=self.staff,
+            note="Other season.",
+        )
+        draft = self.observation(
+            player=self.other_player,
+            evaluator=self.coach,
+            submit=False,
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            self.url, {"season": str(self.season.id), "cycle": str(self.cycle.id)}
+        )
+        rows = self.read_csv(response)
+
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
+        self.assertIn("attachment; filename=", response["Content-Disposition"])
+        self.assertEqual(response["Cache-Control"], "private, no-store")
+        self.assertTrue(rows)
+        self.assertEqual({row["observation_id"] for row in rows}, {str(included.id)})
+        self.assertNotIn(str(excluded.id), {row["observation_id"] for row in rows})
+        self.assertNotIn(str(draft.id), {row["observation_id"] for row in rows})
+        self.assertEqual({row["player_name"] for row in rows}, {"Renée Sample"})
+        self.assertEqual({row["season"] for row in rows}, {"Spring 2026"})
+        self.assertEqual({row["cycle"] for row in rows}, {"Spring 2026 Post Season"})
+        self.assertTrue(all(row["question_key"] for row in rows))
+        self.assertTrue(all(row["question_set_version"] == "1" for row in rows))
+        self.assertIn("'=1+1", {row["text_value"] for row in rows})
+
+    def test_all_django_staff_can_export_but_metadata_roles_cannot(self):
+        self.observation()
+        for user in (self.staff, self.superuser):
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                self.assertEqual(self.client.get(self.url).status_code, 200)
+                self.assertContains(
+                    self.client.get(reverse("analytics:evaluation-review-list")),
+                    self.url,
+                )
+
+        for user in (self.coach, self.role_admin):
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                self.assertEqual(self.client.get(self.url).status_code, 403)
+                self.assertNotContains(
+                    self.client.get(reverse("analytics:evaluation-review-list")),
+                    self.url,
+                )
+
+        self.client.logout()
+        self.assertEqual(self.client.get(self.url).status_code, 302)
+
+    def test_export_escapes_spreadsheet_formula_and_preserves_multiline_text(self):
+        self.observation(note='  =HYPERLINK("https://example.com")\nsecond line')
+        self.client.force_login(self.staff)
+
+        rows = self.read_csv(self.client.get(self.url))
+
+        text_rows = [row for row in rows if row["text_value"]]
+        self.assertEqual(len(text_rows), 1)
+        self.assertEqual(
+            text_rows[0]["text_value"],
+            '\'  =HYPERLINK("https://example.com")\nsecond line',
+        )
+
+    def test_empty_export_still_has_header(self):
+        self.client.force_login(self.staff)
+        response = self.client.get(self.url)
+        content = b"".join(response.streaming_content).decode("utf-8-sig")
+
+        self.assertIn("observation_id,submitted_at,player_id", content)
+        self.assertEqual(list(csv.DictReader(io.StringIO(content))), [])
+
+    def test_export_keeps_observations_with_no_saved_responses(self):
+        observation = self.observation()
+        ObservationResponse.objects.filter(observation=observation).delete()
+        self.client.force_login(self.staff)
+
+        rows = self.read_csv(self.client.get(self.url))
+
+        self.assertEqual(len(rows), 1)
+        self.assertEqual(rows[0]["observation_id"], str(observation.id))
+        self.assertEqual(rows[0]["question_key"], "")
+
+    def test_export_prefetches_responses_for_multiple_evaluations(self):
+        self.observation(evaluator=self.coach)
+        self.observation(evaluator=self.staff)
+
+        with CaptureQueriesContext(connection) as queries:
+            lines = list(export_submitted_evaluations_csv(self.staff, {}))
+
+        self.assertEqual(len(queries), 3)
+        self.assertGreater(len(lines), 2)
diff --git a/analytics/urls.py b/analytics/urls.py
index fe85b37..550269b 100644
--- a/analytics/urls.py
+++ b/analytics/urls.py
@@ -16,6 +16,7 @@ from analytics.views import (
     EvaluationListView,
     EvaluationPlayerView,
     EvaluationReviewDetailView,
+    EvaluationReviewExportView,
     EvaluationReviewListView,
     MyEvaluationDetailView,
     MyEvaluationsPlayerView,
@@ -54,6 +55,7 @@ urlpatterns = [
     path("evaluations/", EvaluationListView.as_view(), name="evaluation-list"),
     path("evaluations/players/<int:player_id>/", EvaluationPlayerView.as_view(), name="evaluation-player"),
     path("evaluation-review/", EvaluationReviewListView.as_view(), name="evaluation-review-list"),
+    path("evaluation-review/export/", EvaluationReviewExportView.as_view(), name="evaluation-review-export"),
     path("evaluation-review/<int:observation_id>/", EvaluationReviewDetailView.as_view(), name="evaluation-review-detail"),
     path("my/evaluations/", MyEvaluationsView.as_view(), name="my-evaluations"),
     path("my/evaluations/players/<int:player_id>/", MyEvaluationsPlayerView.as_view(), name="my-evaluations-player"),
diff --git a/analytics/views.py b/analytics/views.py
index a831e45..5c425d7 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -2,9 +2,10 @@ from django.contrib import messages
 from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
 from django.core.exceptions import PermissionDenied, ValidationError
 from django.db.models import Q
-from django.http import Http404
+from django.http import Http404, StreamingHttpResponse
 from django.shortcuts import get_object_or_404, redirect
 from django.urls import reverse
+from django.utils import timezone
 from django.views.generic import FormView, ListView, TemplateView, View

 from analytics.assessment_forms import CoachAssessmentForm
@@ -63,6 +64,9 @@ from analytics.services.evaluation_access_service import (
     get_my_evaluations,
     get_or_create_evaluation_for_player,
 )
+from analytics.services.evaluation_export_service import (
+    export_submitted_evaluations_csv,
+)
 from analytics.services.evaluation_review_service import (
     get_evaluation_review_detail,
     get_evaluation_review_list,
@@ -76,6 +80,7 @@ from analytics.services.observation_service import (
 from analytics.services.permissions import (
     can_edit_observation,
     can_evaluate_player,
+    can_export_submitted_evaluations,
     can_reopen_observation,
     can_review_submitted_evaluations,
     can_submit_coach_assessment,
@@ -775,11 +780,28 @@ class EvaluationReviewListView(EvaluationReviewRequiredMixin, TemplateView):
                 "evaluator_roles": review_list.evaluator_roles,
                 "perspective_choices": review_list.perspective_choices,
                 "total_count": review_list.total_count,
+                "can_export_evaluations": can_export_submitted_evaluations(
+                    self.request.user
+                ),
             }
         )
         return context


+class EvaluationReviewExportView(LoginRequiredMixin, View):
+    def get(self, request, *args, **kwargs):
+        csv_lines = export_submitted_evaluations_csv(request.user, request.GET)
+        response = StreamingHttpResponse(
+            csv_lines, content_type="text/csv; charset=utf-8"
+        )
+        response["Content-Disposition"] = (
+            f'attachment; filename="evaluations-{timezone.localdate().isoformat()}.csv"'
+        )
+        response["Cache-Control"] = "private, no-store"
+        response["X-Content-Type-Options"] = "nosniff"
+        return response
+
+
 class EvaluationReviewDetailView(EvaluationReviewRequiredMixin, TemplateView):
     template_name = "analytics/evaluation_review_detail.html"

diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 165e2f7..02c3c38 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -535,9 +535,17 @@ Players, parents, and guest evaluators cannot access the review page.
 3. Open an evaluation detail.
 4. Use the information for discussion and decision support.

+Django staff and superusers can select **Export CSV** on this page. The
+download uses the current filters and includes submitted evaluations only,
+with one row per recorded question response. It contains player and evaluator
+names and may include written feedback. Keep the file private; do not share
+the raw export with players or use it as a public board handout. A platform
+role label of "staff" without Django staff access does not permit exporting.
+
 ### Related Pages

 - `/analytics/evaluation-review/`
+- `/analytics/evaluation-review/export/` (Django staff and superusers only)
 - `/analytics/evaluation-review/<observation_id>/`

 Coach review is read-only. It shows submitted evaluations only. Coaches cannot reopen, edit, or delete submitted evaluations from this page.
```
