# Prompt 57 - Analytics

## User Prompt

```text
Implement Evaluation Access V1 Phase 3 only:

Player Evaluation Submission.

Do NOT implement Phase 4, 5, or 6.

Do NOT implement player “My Evaluations.”

Do NOT implement coach evaluation review/filtering.

Do NOT change coach import.

Goal:
Authenticated player users can evaluate other active players using the existing Analytics observation / coach-assessment workflow, with correct player role snapshot and self-evaluation blocked.

Read:
- docs/ARCHITECTURE.md
- docs/USER_MANUAL.md
- docs/evaluations/implementation/engineering/evaluation_access_v1.md
- docs/analytics/architecture/
- docs/analytics/implementation/
- docs/account_management/V1_SUMMARY.md
- AGENTS.md

Review:
- analytics/
- accounts/
- players/

Pay particular attention to:
- analytics/services/permissions.py
- analytics/services/observation_service.py
- analytics/services/coach_assessment_service.py
- analytics/views.py
- analytics/forms.py
- analytics/urls.py
- analytics/templates/
- analytics/tests.py
- accounts/services/link_service.py
- accounts/services/profile_service.py

==================================================
Scope
==================================================

Implement Phase 3 only.

This phase should add player-accessible evaluation submission flow.

It should reuse existing dynamic coach-assessment observation/question-set infrastructure.

Do not rename the underlying observation type.

It is acceptable for internal model names to remain `coach_assessment`, but user-facing copy should use “evaluation” where appropriate for players.

==================================================
Required Behavior
==================================================

1. Player-accessible evaluation entry point

Add a player-accessible evaluation list/search page.

Recommended route:

/analytics/evaluations/

Recommended route name:

analytics:evaluation-list

This page should be available to authenticated users who can submit evaluations:

- coaches
- players
- staff/admin
- guest evaluators

It should not be available to anonymous users.

Parents should not be allowed unless they have a separate evaluator role.

The page should allow evaluators to find/select an active player to evaluate.

Reuse existing player search/query service where practical.

2. Player evaluation form

Add or expose a route for evaluating an active player.

Recommended route:

/analytics/evaluations/players/<int:player_id>/

Recommended route name:

analytics:evaluation-player

Behavior:

- if evaluator already has a draft/reopened evaluation for that player/current cycle, open it
- if evaluator already submitted for that player/current cycle, redirect/show detail
- otherwise create draft observation
- use existing dynamic question form
- save draft and submit behavior should reuse existing observation response services

3. Self-evaluation blocked

Self-evaluation must be blocked at service and view level.

Rule:

- if evaluator has an active `UserPlayerLink(relationship="self")` to target player, they cannot evaluate that player

Return a clear user-facing error or PermissionDenied.

Do not rely only on UI filtering.

4. Role snapshot

Player-submitted evaluations must snapshot evaluator role as `player`.

Coach-submitted evaluations must snapshot as `coach`.

Guest evaluator and staff snapshots from Phase 2 must continue to work.

Do not reintroduce default-everyone-to-coach behavior.

5. Existing coach assessment workflow compatibility

Do not break existing routes:

- analytics:assessment-list
- analytics:assessment-new
- analytics:assessment-detail
- analytics:assessment-edit
- analytics:assessment-review-list
- analytics:assessment-review-detail

Existing coach/staff assessment workflows should still pass tests.

6. Duplicate protection

Continue to enforce one assessment per evaluator/player/cycle.

Behavior should match existing coach-assessment duplicate rules:

- draft can be resumed
- submitted cannot be duplicated

7. Navigation

Add a simple navigation link where appropriate, such as:

- Account profile page for authenticated evaluators
- Analytics command center if staff
- Existing Analytics navigation if present

Do not overbuild portals.

8. Copy

Use user-facing copy like:

- “Evaluations”
- “Evaluate Player”
- “My draft evaluations”

Do not require end users to understand “coach assessment.”

==================================================
Service Ownership
==================================================

analytics owns:

- evaluation list/search
- evaluation submission flow
- permission checks
- observation creation
- response save/submit

accounts owns:

- account roles
- user-player links

players owns:

- player identity/search helpers

Views remain thin.

Business logic stays in services.

==================================================
Suggested Services
==================================================

Create or expand:

analytics/services/evaluation_access_service.py

Possible responsibilities:

- get_evaluation_target_list(user, filters)
- get_or_create_evaluation_for_player(user, player, cycle)
- get_existing_evaluation_for_player(user, player, cycle)
- build evaluation form context/read model if useful

Reuse:

- analytics.services.permissions.can_evaluate_player
- analytics.services.observation_service.create_coach_assessment_observation
- analytics.services.observation_service.save_observation_responses
- analytics.services.observation_service.submit_observation
- analytics.services.player_service
- accounts.services.link_service

Do not duplicate observation creation or response saving logic.

==================================================
Templates
==================================================

Add templates only as needed.

Recommended:

- analytics/evaluation_list.html
- analytics/evaluation_form.html

Reusing existing assessment form template is okay if clean.

Keep server-rendered.

No JavaScript.

==================================================
Permissions
==================================================

- anonymous: no access
- player: can evaluate other active players
- player: cannot evaluate self
- coach: can evaluate active players
- staff/admin: can evaluate active players
- guest evaluator: can evaluate active players
- parent: no access unless role behavior already allows

==================================================
Do NOT Implement
==================================================

Do NOT implement:

- My Evaluations result page
- coach review/filtering
- coach import changes
- coach-to-player links
- Coach model
- account operations changes
- audit logging
- invitations
- email
- APIs
- JavaScript
- charts
- exports
- new observation types
- new models/migrations unless absolutely necessary

==================================================
Testing
==================================================

Add/update tests for:

Permissions:
- anonymous cannot access evaluation list
- player can access evaluation list
- coach can access evaluation list
- guest evaluator can access evaluation list
- parent cannot access evaluation list
- player cannot evaluate self
- player can evaluate another active player
- evaluator cannot evaluate inactive player

Workflow:
- player can open evaluation form for another player
- player role snapshot is stored as player
- coach role snapshot remains coach
- guest evaluator role snapshot remains guest_evaluator
- draft can be resumed
- submitted evaluation cannot be duplicated
- save draft works
- submit works
- missing required responses are blocked
- user-facing copy says evaluation/evaluate player where appropriate

Regression:
- existing coach assessment list/new/edit/detail still works
- staff review still works
- Analytics command center still works
- Account Operations tests still pass
- Coach import tests still pass
- Player import provisioning tests still pass

==================================================
Verification
==================================================

Run:
- python manage.py check
- python manage.py makemigrations analytics --check
- python manage.py makemigrations accounts --check
- python manage.py test analytics
- python manage.py test accounts
- python manage.py test players
- python manage.py test drafts
- python manage.py test pdp
- python manage.py test
- git diff --check

==================================================
Documentation
==================================================

Update:
- docs/evaluations/implementation/engineering/evaluation_access_v1.md

Mark Phase 3 implemented only if complete.

Update:
- docs/USER_MANUAL.md

Document only current behavior:

- players/coaches/staff/guest evaluators can submit evaluations
- players cannot evaluate themselves
- parent accounts do not submit evaluations unless given another evaluator role
- this is evaluation submission only, not My Evaluations or coach review

Do not document Phase 4/5 features as available.

==================================================
Prompt Archive
==================================================

Create the next prompt record in docs/prompts/ according to AGENTS.md.

Commit implementation first.

Then commit prompt archive separately.

Push both commits.

==================================================
Final Report
==================================================

Report:
- implementation summary
- files created
- files modified
- routes added
- services added/changed
- templates added
- tests added/updated
- test results
- documentation updates
- implementation decisions
- deviations
- technical debt
- confirmation that only Phase 3 was implemented
- confirmation that Phase 4+ were NOT implemented
```

## Resulting Commit

```text
f0ca4bd Implement player evaluation submission
```

## Commit Diff

```diff
commit f0ca4bd68bb247ef1bc481ae97b5ac564a61c295
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 9 09:52:10 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 9 09:53:39 2026 -0700

    Implement player evaluation submission
---
 accounts/templates/accounts/profile.html           |   3 +
 analytics/services/evaluation_access_service.py    |  90 +++++++++++++
 analytics/templates/analytics/evaluation_form.html |  32 +++++
 analytics/templates/analytics/evaluation_list.html |  66 +++++++++
 analytics/tests.py                                 | 150 +++++++++++++++++++++
 analytics/urls.py                                  |   4 +
 analytics/views.py                                 |  93 +++++++++++++
 docs/USER_MANUAL.md                                |  10 +-
 .../engineering/evaluation_access_v1.md            |   2 +
 9 files changed, 449 insertions(+), 1 deletion(-)

diff --git a/accounts/templates/accounts/profile.html b/accounts/templates/accounts/profile.html
index b81b7c9..ab797b5 100644
--- a/accounts/templates/accounts/profile.html
+++ b/accounts/templates/accounts/profile.html
@@ -25,6 +25,9 @@
                 {% endfor %}
             </ul>
         {% endif %}
+        {% if account_role != "parent" %}
+            <p><a class="button button--primary" href="{% url 'analytics:evaluation-list' %}">Submit Evaluation</a></p>
+        {% endif %}
         {% if request.user.is_staff or request.user.is_superuser %}
             <p><a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Account Operations</a></p>
         {% endif %}
diff --git a/analytics/services/evaluation_access_service.py b/analytics/services/evaluation_access_service.py
new file mode 100644
index 0000000..b718441
--- /dev/null
+++ b/analytics/services/evaluation_access_service.py
@@ -0,0 +1,90 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from django.core.exceptions import PermissionDenied
+from django.db import transaction
+
+from analytics.models import OBSERVATION_STATUS_SUBMITTED, EvaluationCycle, Observation
+from analytics.services.coach_assessment_service import (
+    assessment_status_for_players,
+    get_active_coach_assessment_cycle,
+    get_existing_coach_assessment,
+    get_or_create_draft_coach_assessment,
+    list_players_for_assessment,
+)
+from analytics.services.metrics_service import normalize_cycle_id
+from analytics.services.permissions import can_evaluate_player, can_submit_evaluation
+from players.models import Player
+
+
+@dataclass(frozen=True)
+class EvaluationTargetStatus:
+    player: Player
+    observation: Observation | None
+    status: str
+    can_evaluate: bool
+
+
+@dataclass(frozen=True)
+class EvaluationTargetList:
+    cycle: EvaluationCycle | None
+    player_statuses: list[EvaluationTargetStatus]
+    query: str = ""
+    division: str = ""
+    team: str = ""
+
+
+def get_evaluation_target_list(user, params) -> EvaluationTargetList:
+    """Return active player evaluation targets for an authenticated evaluator."""
+    if not can_submit_evaluation(user):
+        raise PermissionDenied("You cannot submit evaluations.")
+
+    cycle = get_active_coach_assessment_cycle(normalize_cycle_id(params.get("cycle")))
+    query = (params.get("q") or "").strip()
+    division = (params.get("division") or "").strip()
+    team = (params.get("team") or "").strip()
+    if not cycle:
+        return EvaluationTargetList(cycle=None, player_statuses=[], query=query, division=division, team=team)
+
+    players = list(list_players_for_assessment(query=query, division=division, team=team))
+    statuses_by_player_id = {
+        item.player.id: item for item in assessment_status_for_players(players, cycle, user)
+    }
+    player_statuses = [
+        EvaluationTargetStatus(
+            player=player,
+            observation=statuses_by_player_id[player.id].observation,
+            status=statuses_by_player_id[player.id].status,
+            can_evaluate=can_evaluate_player(user, player),
+        )
+        for player in players
+    ]
+    return EvaluationTargetList(
+        cycle=cycle,
+        player_statuses=player_statuses,
+        query=query,
+        division=division,
+        team=team,
+    )
+
+
+def get_existing_evaluation_for_player(user, player: Player, cycle: EvaluationCycle) -> Observation | None:
+    """Return the evaluator's existing coach-assessment observation for a target player and cycle."""
+    return get_existing_coach_assessment(player, cycle, user)
+
+
+@transaction.atomic
+def get_or_create_evaluation_for_player(user, player: Player, cycle: EvaluationCycle) -> Observation:
+    """Return or create the evaluator's draft evaluation for a target player."""
+    if not can_evaluate_player(user, player):
+        raise PermissionDenied("You cannot evaluate this player.")
+    existing = get_existing_evaluation_for_player(user, player, cycle)
+    if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
+        return existing
+    return get_or_create_draft_coach_assessment(player, cycle, user)
+
+
+def active_evaluation_cycle(cycle_id: str | int | None = None) -> EvaluationCycle | None:
+    """Return the active evaluation cycle for player-facing evaluation submission."""
+    return get_active_coach_assessment_cycle(normalize_cycle_id(cycle_id))
diff --git a/analytics/templates/analytics/evaluation_form.html b/analytics/templates/analytics/evaluation_form.html
new file mode 100644
index 0000000..46ca022
--- /dev/null
+++ b/analytics/templates/analytics/evaluation_form.html
@@ -0,0 +1,32 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Evaluate {{ player.display_name }}{% endblock %}
+{% block analytics_subtitle %}{{ cycle.name }} · {{ observation.get_status_display }}{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card pdp-card--form">
+    <h2>Evaluation</h2>
+    {% if question_set.rubric.labels %}
+        <p>
+            {% for value, label in question_set.rubric.labels.items %}
+                <strong>{{ value }}</strong> {{ label }}{% if not forloop.last %} · {% endif %}
+            {% endfor %}
+        </p>
+    {% endif %}
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.non_field_errors }}
+        {% for group in question_groups %}
+            <section class="pdp-list__item pdp-list__item--stack">
+                <h3>{{ group.category }}</h3>
+                {% for item in group.questions %}
+                    {% include "analytics/_assessment_question.html" with question=item.question field=item.field %}
+                {% endfor %}
+            </section>
+        {% endfor %}
+        <button class="button button--ghost" type="submit" name="action" value="save_draft">Save Draft</button>
+        <button class="button button--primary" type="submit" name="action" value="submit">Submit Evaluation</button>
+        <a class="button button--ghost" href="{% url 'analytics:evaluation-list' %}">Back</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/evaluation_list.html b/analytics/templates/analytics/evaluation_list.html
new file mode 100644
index 0000000..469db7a
--- /dev/null
+++ b/analytics/templates/analytics/evaluation_list.html
@@ -0,0 +1,66 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}Evaluations{% endblock %}
+{% block analytics_subtitle %}Find an active player and submit an evaluation.{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Evaluate Player</h2>
+    {% if not cycle %}
+        <p>No active evaluation cycle is available.</p>
+    {% else %}
+        <form method="get" class="pdp-form">
+            <label>
+                Search
+                <input type="search" name="q" value="{{ query }}">
+            </label>
+            <label>
+                Division
+                <input type="text" name="division" value="{{ division }}">
+            </label>
+            <label>
+                Team
+                <input type="text" name="team" value="{{ team }}">
+            </label>
+            <button class="button button--primary" type="submit">Filter</button>
+        </form>
+        <p>{{ cycle.name }}</p>
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Player</th>
+                        <th>Division</th>
+                        <th>Team</th>
+                        <th>My draft evaluations</th>
+                        <th>Action</th>
+                    </tr>
+                </thead>
+                <tbody>
+                    {% for item in player_statuses %}
+                        <tr>
+                            <td>{{ item.player.display_name }}</td>
+                            <td>{{ item.player.division }}</td>
+                            <td>{{ item.player.team_name }}</td>
+                            <td>{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
+                            <td>
+                                {% if not item.can_evaluate %}
+                                    <span class="pdp-badge pdp-badge--muted">Self-evaluation blocked</span>
+                                {% elif item.observation and item.status == "submitted" %}
+                                    <a class="button button--ghost" href="{% url 'analytics:assessment-detail' observation_id=item.observation.id %}">View</a>
+                                {% elif item.observation %}
+                                    <a class="button button--primary" href="{% url 'analytics:evaluation-player' player_id=item.player.id %}">Continue</a>
+                                {% else %}
+                                    <a class="button button--primary" href="{% url 'analytics:evaluation-player' player_id=item.player.id %}">Evaluate Player</a>
+                                {% endif %}
+                            </td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="5">No active players found.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    {% endif %}
+</article>
+{% endblock %}
diff --git a/analytics/tests.py b/analytics/tests.py
index ec98839..1659724 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -1743,3 +1743,153 @@ class CoachAssessmentWorkflowTests(TestCase):
         result.observation.refresh_from_db()
         self.assertEqual(response.status_code, 302)
         self.assertEqual(result.observation.status, OBSERVATION_STATUS_REOPENED)
+
+
+class EvaluationAccessSubmissionViewTests(TestCase):
+    def setUp(self):
+        self.coach = User.objects.create_user(username="coach-evaluator", password="testpass")
+        self.player_user = User.objects.create_user(username="player-evaluator", password="testpass")
+        self.guest = User.objects.create_user(username="guest-evaluator", password="testpass")
+        self.parent = User.objects.create_user(username="parent-user", password="testpass")
+        self.staff = User.objects.create_user(username="staff-evaluator", password="testpass", is_staff=True)
+        set_account_role(self.coach, AccountRole.COACH)
+        set_account_role(self.player_user, AccountRole.PLAYER)
+        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
+        set_account_role(self.parent, AccountRole.PARENT)
+        set_account_role(self.staff, AccountRole.STAFF)
+        self.self_player = Player.objects.create(first_name="Self", last_name="Player", division="13U", team_name="Expos")
+        self.target_player = Player.objects.create(first_name="Target", last_name="Player", division="13U", team_name="Expos")
+        self.inactive_player = Player.objects.create(first_name="Inactive", last_name="Player", division="13U", is_active=False)
+        link_user_to_player(self.player_user, self.self_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+        )
+
+    def response_payload(self, include_required=True):
+        data = {}
+        for question in self.setup_result.question_set.questions.filter(is_active=True):
+            field_name = f"question_{question.id}"
+            if question.response_type == RESPONSE_TYPE_RATING_1_5 and include_required:
+                data[field_name] = "4"
+            elif question.response_type == RESPONSE_TYPE_TEXT:
+                data[field_name] = "Good teammate."
+        return data
+
+    def test_evaluation_list_permissions(self):
+        self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 302)
+        for user in [self.player_user, self.coach, self.guest, self.staff]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                response = self.client.get(reverse("analytics:evaluation-list"))
+                self.assertEqual(response.status_code, 200)
+                self.assertContains(response, "Evaluations")
+                self.client.logout()
+
+        self.client.force_login(self.parent)
+        self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 403)
+
+    def test_evaluation_list_blocks_self_and_uses_evaluation_copy(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:evaluation-list"), {"q": "Player"})
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Evaluate Player")
+        self.assertContains(response, "My draft evaluations")
+        self.assertContains(response, "Self-evaluation blocked")
+        self.assertContains(response, reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
+
+    def test_player_can_open_evaluation_form_for_another_player(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
+
+        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, f"Evaluate {self.target_player.display_name}")
+        self.assertContains(response, "Submit Evaluation")
+        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
+        self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
+
+    def test_player_cannot_evaluate_self_or_inactive_player(self):
+        self.client.force_login(self.player_user)
+
+        self.assertEqual(
+            self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id})).status_code,
+            403,
+        )
+        self.assertEqual(
+            self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.inactive_player.id})).status_code,
+            404,
+        )
+
+    def test_player_can_save_draft_and_resume(self):
+        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
+        self.client.force_login(self.player_user)
+
+        response = self.client.post(
+            reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}),
+            {"action": "save_draft", f"question_{question.id}": "3"},
+        )
+        second_response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
+
+        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
+        self.assertEqual(second_response.status_code, 200)
+        self.assertEqual(Observation.objects.filter(player=self.target_player, evaluator=self.player_user).count(), 1)
+        self.assertEqual(observation.responses.get(question=question).numeric_value, Decimal("3.00"))
+
+    def test_player_can_submit_complete_evaluation(self):
+        self.client.force_login(self.player_user)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+
+        response = self.client.post(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}), data)
+
+        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
+        self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
+
+    def test_missing_required_responses_are_blocked(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.post(
+            reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}),
+            {"action": "submit"},
+        )
+
+        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
+        self.assertContains(response, "This field is required")
+
+    def test_submitted_evaluation_cannot_be_duplicated(self):
+        self.client.force_login(self.player_user)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+        self.client.post(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}), data)
+        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
+
+        response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
+        self.assertEqual(Observation.objects.filter(player=self.target_player, evaluator=self.player_user).count(), 1)
+
+    def test_coach_and_guest_role_snapshots_continue_to_work(self):
+        for user, expected_role in [(self.coach, ROLE_COACH), (self.guest, ROLE_GUEST_EVALUATOR)]:
+            with self.subTest(user=user.username):
+                target = Player.objects.create(first_name=user.username, last_name="Target", division="13U")
+                self.client.force_login(user)
+                response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": target.id}))
+
+                observation = Observation.objects.get(player=target, evaluator=user)
+                self.assertEqual(response.status_code, 200)
+                self.assertEqual(observation.evaluator_role_key, expected_role)
+                self.client.logout()
diff --git a/analytics/urls.py b/analytics/urls.py
index 6764052..7992f3b 100644
--- a/analytics/urls.py
+++ b/analytics/urls.py
@@ -5,6 +5,8 @@ from analytics.views import (
     CoachAssessmentDetailView,
     CoachAssessmentEditView,
     CoachAssessmentListView,
+    EvaluationListView,
+    EvaluationPlayerView,
     PlayerComparisonView,
     PlayerProfileView,
     PlayerImportConfirmView,
@@ -26,6 +28,8 @@ urlpatterns = [
     path("players/", PlayerSearchView.as_view(), name="player-search"),
     path("players/compare/", PlayerComparisonView.as_view(), name="player-compare"),
     path("players/<int:player_id>/", PlayerProfileView.as_view(), name="player-profile"),
+    path("evaluations/", EvaluationListView.as_view(), name="evaluation-list"),
+    path("evaluations/players/<int:player_id>/", EvaluationPlayerView.as_view(), name="evaluation-player"),
     path("assessments/", CoachAssessmentListView.as_view(), name="assessment-list"),
     path("assessments/players/<int:player_id>/", CoachAssessmentEditView.as_view(), name="assessment-player"),
     path("assessments/<int:observation_id>/", CoachAssessmentDetailView.as_view(), name="assessment-detail"),
diff --git a/analytics/views.py b/analytics/views.py
index 89653c3..2a2e88f 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -29,12 +29,18 @@ from analytics.services.player_service import (
     staff_player_queryset,
 )
 from analytics.services.draft_service import get_draft_contexts_for_player
+from analytics.services.evaluation_access_service import (
+    active_evaluation_cycle,
+    get_evaluation_target_list,
+    get_or_create_evaluation_for_player,
+)
 from analytics.services.observation_service import get_observation_detail, save_observation_responses, submit_observation
 from analytics.services.permissions import (
     can_edit_observation,
     can_evaluate_player,
     can_reopen_observation,
     can_submit_coach_assessment,
+    can_submit_evaluation,
     can_view_observation,
 )
 from analytics.services.metrics_service import normalize_cycle_id
@@ -252,6 +258,93 @@ class PlayerComparisonView(AnalyticsStaffRequiredMixin, TemplateView):
         return context
 
 
+class EvaluationSubmitterRequiredMixin(LoginRequiredMixin):
+    def dispatch(self, request, *args, **kwargs):
+        if request.user.is_authenticated and not can_submit_evaluation(request.user):
+            raise PermissionDenied("You cannot submit evaluations.")
+        return super().dispatch(request, *args, **kwargs)
+
+
+class EvaluationListView(EvaluationSubmitterRequiredMixin, TemplateView):
+    template_name = "analytics/evaluation_list.html"
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        target_list = get_evaluation_target_list(self.request.user, self.request.GET)
+        context.update(
+            {
+                "target_list": target_list,
+                "cycle": target_list.cycle,
+                "player_statuses": target_list.player_statuses,
+                "query": target_list.query,
+                "division": target_list.division,
+                "team": target_list.team,
+                "cycles": EvaluationCycle.objects.filter(
+                    is_active=True,
+                    coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT,
+                ),
+            }
+        )
+        return context
+
+
+class EvaluationPlayerView(EvaluationSubmitterRequiredMixin, TemplateView):
+    template_name = "analytics/evaluation_form.html"
+    observation = None
+
+    def dispatch(self, request, *args, **kwargs):
+        cycle = active_evaluation_cycle(request.GET.get("cycle"))
+        if not cycle:
+            messages.error(request, "No active evaluation cycle is available.")
+            return redirect("analytics:evaluation-list")
+        player = get_object_or_404(Player, pk=kwargs["player_id"], is_active=True)
+        if not can_evaluate_player(request.user, player):
+            raise PermissionDenied("You cannot evaluate this player.")
+        self.observation = get_or_create_evaluation_for_player(request.user, player, cycle)
+        if self.observation.status == OBSERVATION_STATUS_SUBMITTED:
+            return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_form(self, data=None, require_required=False):
+        return CoachAssessmentForm(
+            data=data,
+            question_set=self.observation.question_set,
+            observation=self.observation,
+            require_required=require_required,
+        )
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        form = kwargs.get("form") or self.get_form()
+        context.update(
+            {
+                "observation": self.observation,
+                "player": self.observation.player,
+                "cycle": self.observation.evaluation_cycle,
+                "question_set": self.observation.question_set,
+                "form": form,
+                "question_groups": form.question_groups(),
+            }
+        )
+        return context
+
+    def post(self, request, *args, **kwargs):
+        action = request.POST.get("action", "save_draft")
+        form = self.get_form(data=request.POST, require_required=action == "submit")
+        if form.is_valid():
+            try:
+                save_observation_responses(self.observation, form.response_payload())
+                if action == "submit":
+                    submit_observation(self.observation, actor=request.user)
+                    messages.success(request, "Evaluation submitted.")
+                    return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
+                messages.success(request, "Evaluation draft saved.")
+                return redirect("analytics:evaluation-player", player_id=self.observation.player_id)
+            except ValidationError as exc:
+                form.add_error(None, exc)
+        return self.render_to_response(self.get_context_data(form=form))
+
+
 class CoachAssessmentListView(LoginRequiredMixin, TemplateView):
     template_name = "analytics/assessment_list.html"
 
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index d2b8478..b0e7b2f 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -341,6 +341,12 @@ Assessment pages are available under:
 /analytics/assessments/
 ```
 
+Evaluation submission pages are available under:
+
+```text
+/analytics/evaluations/
+```
+
 The assessment form uses the active question set for the current assessment cycle. Questions are not hard-coded into the page, so they can evolve over time.
 
 Assessments may include:
@@ -350,13 +356,15 @@ Assessments may include:
 
 When submitting an assessment:
 
-- choose or open the player assessment
+- choose or open the player evaluation
 - enter ratings and notes
 - save a draft if more work is needed
 - submit when finished
 
 Submitted assessments become part of the player's Analytics record.
 
+Players, coaches, staff, and guest evaluators use the evaluation pages to submit evaluations. Staff-only review pages and player result pages are separate workflows.
+
 ## Who Can Evaluate A Player
 
 Authenticated coaches, players, staff, and guest evaluators can evaluate any player if they know the player.
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index 6a67350..ea78195 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -968,6 +968,8 @@ Deliverables:
 - self-evaluation handling;
 - permission tests.
 
+Status: implemented.
+
 ### Phase 4: Player "My Evaluations"
 
 Purpose:
```
