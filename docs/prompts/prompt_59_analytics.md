# Prompt 59 - Analytics

## User Prompt

```text
Implement Evaluation Access V1 Phase 4 only:

Player “My Evaluations.”

Do NOT implement Phase 5 or Phase 6.

Do NOT implement coach evaluation review/filtering.

Do NOT change coach import.

Do NOT change player evaluation submission except where needed for integration/navigation.

Goal:
Players can privately view submitted evaluations about themselves only, with evaluator names hidden and evaluator role/category shown.

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
- analytics/services/evaluation_access_service.py
- analytics/services/observation_service.py
- analytics/views.py
- analytics/urls.py
- analytics/templates/
- analytics/tests.py
- accounts/services/link_service.py
- accounts/templates/accounts/profile.html
- accounts/views.py

==================================================
Scope
==================================================

Implement Phase 4 only.

This phase adds private player-facing result views.

Players can view submitted evaluations about their linked self player record.

This is NOT coach review.

This is NOT all-evaluation review.

This is NOT staff analytics review.

==================================================
Required Behavior
==================================================

1. My Evaluations list

Add route:

/analytics/my/evaluations/

Route name:

analytics:my-evaluations

Authenticated users with active self player links can access.

The page should show submitted evaluations about the player(s) linked to the current user with `UserPlayerLink(relationship="self")`.

If the user has no active self-linked player, show a clear empty/denied message.

Do not use name/email matching.

Only active self links count.

2. My Evaluations player-specific list

Add route if useful:

/analytics/my/evaluations/players/<int:player_id>/

Route name:

analytics:my-evaluations-player

Access allowed only if current user has active self link to that player.

3. My Evaluation detail

Add route:

/analytics/my/evaluations/<int:observation_id>/

Route name:

analytics:my-evaluation-detail

Access allowed only if:

- observation is submitted
- observation.player is linked to current user by active self link

Players must not access:

- another player’s evaluations
- draft observations
- reopened observations
- staff-only review screens
- evaluator email/username

4. Evaluator visibility

For player-facing My Evaluations:

Show:
- evaluator role/category
- submitted date
- evaluation cycle
- questions/responses/notes
- target player name

Do NOT show:
- evaluator name
- evaluator username
- evaluator email
- staff-only metadata
- draft/reopened observations

5. Multiple self links

If a user has multiple active self links, list all linked players or provide a player selector.

Do not assume exactly one.

6. Navigation

Add profile navigation for eligible players:

- “My Evaluations”

Only show if user has at least one active self player link.

Do not show to coaches unless they also have a self player link.

Do not show to parents unless they have a self link, which normally they should not.

7. Permission helpers

Add/update Analytics permission helpers:

- can_view_my_evaluations(user, player=None)
- can_view_my_evaluation_detail(user, observation)

Use account/link services for self-link checks.

Permission logic belongs in services, not templates.

8. Read model service

Create or expand:

analytics/services/evaluation_access_service.py

or create:

analytics/services/my_evaluation_service.py

Responsibilities:
- get_self_linked_players(user)
- get_my_evaluations(user, player=None)
- get_my_evaluation_detail(user, observation_id)

Return read models/dataclasses where useful.

==================================================
Service Ownership
==================================================

analytics owns:
- My Evaluations queries/read models
- evaluation detail visibility rules
- display-safe evaluator labels

accounts owns:
- user-player self links

players owns:
- player identity

Views remain thin.

==================================================
Templates
==================================================

Add templates:

- analytics/my_evaluations.html
- analytics/my_evaluation_detail.html

Keep server-rendered.

No JavaScript.

==================================================
Privacy Rules
==================================================

Critical:

- Player cannot view another player’s evaluations by changing URL.
- Player cannot view evaluator names.
- Player cannot view evaluator email/username.
- Player cannot view draft/reopened evaluations as final results.
- Player cannot access coach review.
- Player cannot access staff review unless Django staff.

==================================================
Do NOT Implement
==================================================

Do NOT implement:
- coach evaluation review/filtering
- coach review detail
- staff review changes
- coach import changes
- evaluation submission changes beyond navigation integration
- coach-to-player links
- parent portal
- full player portal
- audit logging
- invitations
- email
- APIs
- JavaScript
- charts
- exports
- new models/migrations unless absolutely necessary

==================================================
Testing
==================================================

Add/update tests for:

Permissions:
- anonymous cannot access My Evaluations
- player with self link can access My Evaluations
- player without self link sees empty/denied state
- player can view submitted evaluations about self
- player cannot view submitted evaluations about another player
- player cannot view draft/reopened evaluations about self
- parent cannot access unless self-linked
- coach cannot access unless self-linked
- staff behavior remains unchanged

Privacy:
- evaluator name hidden
- evaluator username/email hidden
- evaluator role/category shown
- submitted date/cycle shown
- question responses shown
- notes shown if part of submitted evaluation

Multiple self links:
- user with multiple active self links can see each linked player’s submitted evaluations
- player-specific route enforces ownership

Navigation:
- self-linked player sees My Evaluations link on profile
- coach without self link does not see My Evaluations
- parent without self link does not see My Evaluations

Regression:
- evaluation submission still works
- submitted “View My Submission” still works for evaluator
- existing staff review still works
- existing coach assessment routes still work
- Account Operations tests still pass
- Coach import tests still pass

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

Mark Phase 4 implemented only if complete.

Update:
- docs/USER_MANUAL.md

Document only current behavior:
- players can view submitted evaluations about themselves
- evaluator names are hidden from players
- evaluator role/category is shown
- draft/reopened evaluations are not shown as final feedback
- coaches still do not have all-evaluation review until Phase 5

Do not document Phase 5 as available.

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
- privacy decisions
- test results
- documentation updates
- implementation decisions
- deviations
- technical debt
- confirmation that only Phase 4 was implemented
- confirmation that Phase 5+ were NOT implemented
```

## Resulting Commit

```text
77b5d5e Implement player my evaluations
```

## Commit Diff

```diff
commit 77b5d5e97b468a1dc8e7da4cab0d7efede2fa521
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Fri Jul 10 10:47:26 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Fri Jul 10 10:47:26 2026 -0700

    Implement player my evaluations
---
 accounts/services/link_service.py                  |  12 ++
 accounts/templates/accounts/profile.html           |   3 +
 accounts/tests.py                                  |  24 +++
 accounts/views.py                                  |   3 +-
 analytics/services/evaluation_access_service.py    | 104 +++++++++++-
 analytics/services/permissions.py                  |  16 +-
 .../templates/analytics/my_evaluation_detail.html  |  36 ++++
 analytics/templates/analytics/my_evaluations.html  |  50 ++++++
 analytics/tests.py                                 | 181 +++++++++++++++++++++
 analytics/urls.py                                  |   6 +
 analytics/views.py                                 |  60 +++++++
 docs/USER_MANUAL.md                                |  14 +-
 .../engineering/evaluation_access_v1.md            |   2 +
 13 files changed, 506 insertions(+), 5 deletions(-)

diff --git a/accounts/services/link_service.py b/accounts/services/link_service.py
index a2f6c19..b22d8ab 100644
--- a/accounts/services/link_service.py
+++ b/accounts/services/link_service.py
@@ -223,6 +223,18 @@ def get_players_for_user(user, active_only=True):
     return Player.objects.filter(**filters).distinct()
 
 
+def get_self_linked_players(user, active_only=True):
+    """Return players actively self-linked to a user."""
+    _validate_user(user)
+    filters = {
+        "user_links__user": user,
+        "user_links__relationship": UserPlayerRelationship.SELF,
+    }
+    if active_only:
+        filters["user_links__is_active"] = True
+    return Player.objects.filter(**filters).distinct().order_by("last_name", "first_name", "id")
+
+
 def get_users_for_player(player, active_only=True):
     """Return users linked to a player."""
     _validate_player(player)
diff --git a/accounts/templates/accounts/profile.html b/accounts/templates/accounts/profile.html
index bf71969..7574bf1 100644
--- a/accounts/templates/accounts/profile.html
+++ b/accounts/templates/accounts/profile.html
@@ -28,6 +28,9 @@
         {% if can_submit_evaluations %}
             <p><a class="button button--primary" href="{% url 'analytics:evaluation-list' %}">Submit Evaluation</a></p>
         {% endif %}
+        {% if can_view_my_evaluations %}
+            <p><a class="button button--ghost" href="{% url 'analytics:my-evaluations' %}">My Evaluations</a></p>
+        {% endif %}
         {% if request.user.is_staff or request.user.is_superuser %}
             <p><a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Account Operations</a></p>
         {% endif %}
diff --git a/accounts/tests.py b/accounts/tests.py
index c826b08..21a0a54 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -1610,6 +1610,30 @@ class AccountAuthViewTests(TestCase):
                     self.assertNotContains(response, "Submit Evaluation")
                 self.client.logout()
 
+    def test_profile_my_evaluations_link_requires_self_link(self):
+        player = Player.objects.create(first_name="Linked", last_name="Player")
+        player_user = User.objects.create_user(username="linked-player", password="testpass")
+        coach = User.objects.create_user(username="unlinked-coach", password="testpass")
+        parent = User.objects.create_user(username="unlinked-parent", password="testpass")
+        set_account_role(player_user, AccountRole.PLAYER)
+        set_account_role(coach, AccountRole.COACH)
+        set_account_role(parent, AccountRole.PARENT)
+        link_user_to_player(player_user, player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+
+        self.client.force_login(player_user)
+        response = self.client.get(reverse("accounts:profile"))
+        self.assertTrue(response.context["can_view_my_evaluations"])
+        self.assertContains(response, reverse("analytics:my-evaluations"))
+        self.assertContains(response, "My Evaluations")
+
+        for user in [coach, parent]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                response = self.client.get(reverse("accounts:profile"))
+                self.assertFalse(response.context["can_view_my_evaluations"])
+                self.assertNotContains(response, reverse("analytics:my-evaluations"))
+                self.client.logout()
+
 
 class CoachImportServiceTests(TestCase):
     def setUp(self):
diff --git a/accounts/views.py b/accounts/views.py
index 1f6f8c1..c24b3ee 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -48,7 +48,7 @@ from accounts.services.permissions import (
 )
 from accounts.services.profile_service import get_account_role
 from accounts.services.role_service import role_label
-from analytics.services.permissions import can_submit_evaluation
+from analytics.services.permissions import can_submit_evaluation, can_view_my_evaluations
 
 
 class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
@@ -102,6 +102,7 @@ class AccountProfileView(LoginRequiredMixin, TemplateView):
                 "account_role": role,
                 "account_role_label": role_label(role),
                 "can_submit_evaluations": can_submit_evaluation(self.request.user),
+                "can_view_my_evaluations": can_view_my_evaluations(self.request.user),
                 "linked_players": get_players_for_user(self.request.user),
             }
         )
diff --git a/analytics/services/evaluation_access_service.py b/analytics/services/evaluation_access_service.py
index 6d54ac8..8e37de0 100644
--- a/analytics/services/evaluation_access_service.py
+++ b/analytics/services/evaluation_access_service.py
@@ -5,7 +5,13 @@ from dataclasses import dataclass
 from django.core.exceptions import PermissionDenied
 from django.db import transaction
 
-from analytics.models import OBSERVATION_STATUS_SUBMITTED, EvaluationCycle, Observation
+from accounts.services.link_service import get_self_linked_players
+from analytics.models import (
+    OBSERVATION_STATUS_SUBMITTED,
+    OBSERVATION_TYPE_COACH_ASSESSMENT,
+    EvaluationCycle,
+    Observation,
+)
 from analytics.services.coach_assessment_service import (
     assessment_status_for_players,
     get_active_coach_assessment_cycle,
@@ -13,7 +19,12 @@ from analytics.services.coach_assessment_service import (
     get_or_create_draft_coach_assessment,
     list_players_for_assessment,
 )
-from analytics.services.permissions import can_evaluate_player, can_submit_evaluation
+from analytics.services.permissions import (
+    can_evaluate_player,
+    can_submit_evaluation,
+    can_view_my_evaluation_detail,
+    can_view_my_evaluations,
+)
 from players.models import Player
 
 
@@ -34,6 +45,33 @@ class EvaluationTargetList:
     team: str = ""
 
 
+@dataclass(frozen=True)
+class MyEvaluationSummary:
+    observation: Observation
+    player: Player
+    evaluator_role_name: str
+    submitted_at: object
+    cycle_name: str
+
+
+@dataclass(frozen=True)
+class MyEvaluationQuestionResponse:
+    question_prompt: str
+    category: str
+    numeric_value: object = None
+    text_value: str = ""
+
+
+@dataclass(frozen=True)
+class MyEvaluationDetail:
+    observation: Observation
+    player: Player
+    evaluator_role_name: str
+    submitted_at: object
+    cycle_name: str
+    responses: list[MyEvaluationQuestionResponse]
+
+
 def get_evaluation_target_list(user, params) -> EvaluationTargetList:
     """Return active player evaluation targets for an authenticated evaluator."""
     if not can_submit_evaluation(user):
@@ -87,3 +125,65 @@ def get_or_create_evaluation_for_player(user, player: Player, cycle: EvaluationC
 def active_evaluation_cycle() -> EvaluationCycle | None:
     """Return the active evaluation cycle for player-facing evaluation submission."""
     return get_active_coach_assessment_cycle()
+
+
+def self_linked_players_for_user(user) -> list[Player]:
+    """Return active self-linked players for My Evaluations."""
+    return list(get_self_linked_players(user).filter(is_active=True))
+
+
+def get_my_evaluations(user, player: Player | None = None) -> tuple[list[Player], list[MyEvaluationSummary]]:
+    """Return submitted evaluations about the current user's self-linked player records."""
+    if player is not None and not can_view_my_evaluations(user, player=player):
+        raise PermissionDenied("You cannot view evaluations for this player.")
+    players = [player] if player is not None else self_linked_players_for_user(user)
+    if not players:
+        return [], []
+    observations = (
+        Observation.objects.select_related("player", "evaluation_cycle", "evaluator_role")
+        .filter(
+            player__in=players,
+            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
+            status=OBSERVATION_STATUS_SUBMITTED,
+        )
+        .order_by("-submitted_at", "-created_at", "-id")
+    )
+    summaries = [
+        MyEvaluationSummary(
+            observation=observation,
+            player=observation.player,
+            evaluator_role_name=observation.evaluator_role_name or "Evaluator",
+            submitted_at=observation.submitted_at,
+            cycle_name=observation.evaluation_cycle.name,
+        )
+        for observation in observations
+    ]
+    return players, summaries
+
+
+def get_my_evaluation_detail(user, observation_id: int) -> MyEvaluationDetail:
+    """Return a player-safe submitted evaluation detail view."""
+    observation = (
+        Observation.objects.select_related("player", "evaluation_cycle", "evaluator_role")
+        .prefetch_related("responses__question")
+        .get(pk=observation_id)
+    )
+    if not can_view_my_evaluation_detail(user, observation):
+        raise PermissionDenied("You cannot view this evaluation.")
+    responses = [
+        MyEvaluationQuestionResponse(
+            question_prompt=response.question.prompt,
+            category=response.question.category or "Questions",
+            numeric_value=response.numeric_value,
+            text_value=response.text_value,
+        )
+        for response in observation.responses.all()
+    ]
+    return MyEvaluationDetail(
+        observation=observation,
+        player=observation.player,
+        evaluator_role_name=observation.evaluator_role_name or "Evaluator",
+        submitted_at=observation.submitted_at,
+        cycle_name=observation.evaluation_cycle.name,
+        responses=responses,
+    )
diff --git a/analytics/services/permissions.py b/analytics/services/permissions.py
index ea54acb..7dab101 100644
--- a/analytics/services/permissions.py
+++ b/analytics/services/permissions.py
@@ -1,7 +1,7 @@
 from django.core.exceptions import ValidationError
 
 from accounts.models import AccountRole
-from accounts.services.link_service import is_player_self
+from accounts.services.link_service import get_self_linked_players, is_player_self
 from accounts.services.role_service import role_for_user, role_label
 from analytics.models import OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED, OBSERVATION_STATUS_SUBMITTED, EvaluatorRole
 
@@ -63,6 +63,20 @@ def can_view_observation(user, observation) -> bool:
     return bool(user and user.is_authenticated and observation.evaluator_id == user.id)
 
 
+def can_view_my_evaluations(user, player=None) -> bool:
+    if not user or not user.is_authenticated:
+        return False
+    if player is not None:
+        return is_player_self(user, player)
+    return get_self_linked_players(user).exists()
+
+
+def can_view_my_evaluation_detail(user, observation) -> bool:
+    if not observation or observation.status != OBSERVATION_STATUS_SUBMITTED:
+        return False
+    return can_view_my_evaluations(user, player=observation.player)
+
+
 def can_edit_observation(user, observation) -> bool:
     return can_edit_own_evaluation_draft(user, observation)
 
diff --git a/analytics/templates/analytics/my_evaluation_detail.html b/analytics/templates/analytics/my_evaluation_detail.html
new file mode 100644
index 0000000..abf1909
--- /dev/null
+++ b/analytics/templates/analytics/my_evaluation_detail.html
@@ -0,0 +1,36 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}{{ detail.player.display_name }}{% endblock %}
+{% block analytics_subtitle %}{{ detail.cycle_name }} · Submitted evaluation{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>Evaluation</h2>
+    <dl class="pdp-definition-list">
+        <dt>Player</dt>
+        <dd>{{ detail.player.display_name }}</dd>
+        <dt>Evaluator Role</dt>
+        <dd>{{ detail.evaluator_role_name }}</dd>
+        <dt>Submitted</dt>
+        <dd>{{ detail.submitted_at|date:"M j, Y" }}</dd>
+    </dl>
+    {% for response in detail.responses %}
+        <section class="pdp-list__item pdp-list__item--stack">
+            <h3>{{ response.category }}</h3>
+            <div>
+                <strong>{{ response.question_prompt }}</strong>
+                {% if response.numeric_value %}
+                    <span>{{ response.numeric_value|floatformat:0 }}</span>
+                {% elif response.text_value %}
+                    <p>{{ response.text_value }}</p>
+                {% else %}
+                    <span>Not answered</span>
+                {% endif %}
+            </div>
+        </section>
+    {% empty %}
+        <p>No responses are available.</p>
+    {% endfor %}
+    <a class="button button--ghost" href="{% url 'analytics:my-evaluations' %}">Back</a>
+</article>
+{% endblock %}
diff --git a/analytics/templates/analytics/my_evaluations.html b/analytics/templates/analytics/my_evaluations.html
new file mode 100644
index 0000000..14f6673
--- /dev/null
+++ b/analytics/templates/analytics/my_evaluations.html
@@ -0,0 +1,50 @@
+{% extends "analytics/base.html" %}
+
+{% block analytics_title %}My Evaluations{% endblock %}
+{% block analytics_subtitle %}Submitted evaluations about your linked player record.{% endblock %}
+
+{% block analytics_content %}
+<article class="pdp-card">
+    <h2>{% if selected_player %}{{ selected_player.display_name }}{% else %}My Evaluations{% endif %}</h2>
+    {% if not has_self_link %}
+        <p>No player record is linked to your account.</p>
+    {% else %}
+        {% if players|length > 1 and not selected_player %}
+            <section class="pdp-list__item pdp-list__item--stack">
+                <h3>Linked players</h3>
+                <ul>
+                    {% for player in players %}
+                        <li><a href="{% url 'analytics:my-evaluations-player' player_id=player.id %}">{{ player.display_name }}</a></li>
+                    {% endfor %}
+                </ul>
+            </section>
+        {% endif %}
+        <div class="table-wrap">
+            <table class="pdp-table">
+                <thead>
+                    <tr>
+                        <th>Player</th>
+                        <th>Cycle</th>
+                        <th>Evaluator Role</th>
+                        <th>Submitted</th>
+                        <th>Action</th>
+                    </tr>
+                </thead>
+                <tbody>
+                    {% for item in evaluations %}
+                        <tr>
+                            <td>{{ item.player.display_name }}</td>
+                            <td>{{ item.cycle_name }}</td>
+                            <td>{{ item.evaluator_role_name }}</td>
+                            <td>{{ item.submitted_at|date:"M j, Y" }}</td>
+                            <td><a class="button button--ghost" href="{% url 'analytics:my-evaluation-detail' observation_id=item.observation.id %}">View Evaluation</a></td>
+                        </tr>
+                    {% empty %}
+                        <tr><td colspan="5">No submitted evaluations are available yet.</td></tr>
+                    {% endfor %}
+                </tbody>
+            </table>
+        </div>
+    {% endif %}
+</article>
+{% endblock %}
diff --git a/analytics/tests.py b/analytics/tests.py
index 53c1430..15d6e06 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -1966,3 +1966,184 @@ class EvaluationAccessSubmissionViewTests(TestCase):
                 self.assertEqual(response.status_code, 200)
                 self.assertEqual(observation.evaluator_role_key, expected_role)
                 self.client.logout()
+
+
+class MyEvaluationsViewTests(TestCase):
+    def setUp(self):
+        self.player_user = User.objects.create_user(
+            username="linked-player-user",
+            password="testpass",
+            first_name="Linked",
+            last_name="User",
+            email="linked@example.com",
+        )
+        self.other_player_user = User.objects.create_user(username="other-linked-player", password="testpass")
+        self.coach = User.objects.create_user(
+            username="coach-private-name",
+            password="testpass",
+            first_name="Coach",
+            last_name="Private",
+            email="coach-private@example.com",
+        )
+        self.guest = User.objects.create_user(username="guest-evaluator-private", password="testpass")
+        self.parent = User.objects.create_user(username="parent-no-self", password="testpass")
+        self.staff = User.objects.create_user(username="staff-review", password="testpass", is_staff=True)
+        set_account_role(self.player_user, AccountRole.PLAYER)
+        set_account_role(self.other_player_user, AccountRole.PLAYER)
+        set_account_role(self.coach, AccountRole.COACH)
+        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
+        set_account_role(self.parent, AccountRole.PARENT)
+        set_account_role(self.staff, AccountRole.STAFF)
+        self.player = Player.objects.create(first_name="Linked", last_name="Player", division="13U")
+        self.second_player = Player.objects.create(first_name="Second", last_name="Player", division="15U")
+        self.other_player = Player.objects.create(first_name="Other", last_name="Player", division="13U")
+        link_user_to_player(self.player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+        link_user_to_player(self.other_player_user, self.other_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+        )
+
+    def service_response_payload(self, value=4, note="Good teammate."):
+        payload = {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
+        payload[text_question] = note
+        return payload
+
+    def submitted_observation(self, player=None, evaluator=None, value=4, note="Good teammate."):
+        result = create_coach_assessment_observation(
+            player=player or self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=evaluator or self.coach,
+            responses=self.service_response_payload(value=value, note=note),
+        )
+        return submit_observation(result.observation, actor=evaluator or self.coach)
+
+    def test_my_evaluations_requires_login_and_handles_no_self_link(self):
+        self.assertEqual(self.client.get(reverse("analytics:my-evaluations")).status_code, 302)
+
+        self.client.force_login(self.parent)
+        response = self.client.get(reverse("analytics:my-evaluations"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "No player record is linked to your account.")
+
+    def test_player_can_view_submitted_evaluations_about_self(self):
+        observation = self.submitted_observation(note="Shows leadership.")
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:my-evaluations"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, self.cycle.name)
+        self.assertContains(response, "Coach")
+        self.assertContains(response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+
+    def test_my_evaluation_detail_hides_evaluator_identity_and_shows_feedback(self):
+        observation = self.submitted_observation(value=5, note="Strong instincts.")
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, "Evaluator Role")
+        self.assertContains(response, "Coach")
+        self.assertContains(response, self.cycle.name)
+        self.assertContains(response, "Strong instincts.")
+        self.assertContains(response, "5")
+        self.assertNotContains(response, self.coach.username)
+        self.assertNotContains(response, self.coach.email)
+        self.assertNotContains(response, self.coach.get_full_name())
+
+    def test_player_cannot_view_another_players_evaluation_by_url(self):
+        observation = self.submitted_observation(player=self.other_player, evaluator=self.coach)
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_draft_and_reopened_observations_are_not_player_results(self):
+        draft = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.service_response_payload(),
+        ).observation
+        reopened = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.guest,
+            responses=self.service_response_payload(),
+        ).observation
+        reopened.status = OBSERVATION_STATUS_REOPENED
+        reopened.save(update_fields=["status", "updated_at"])
+        self.client.force_login(self.player_user)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        draft_detail = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": draft.id}))
+        reopened_detail = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": reopened.id}))
+
+        self.assertNotContains(list_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": draft.id}))
+        self.assertNotContains(list_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": reopened.id}))
+        self.assertEqual(draft_detail.status_code, 403)
+        self.assertEqual(reopened_detail.status_code, 403)
+
+    def test_multiple_self_links_are_listed_and_player_specific_route_enforces_ownership(self):
+        link_user_to_player(
+            self.player_user,
+            self.second_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+        first_observation = self.submitted_observation(player=self.player, evaluator=self.coach)
+        second_observation = self.submitted_observation(player=self.second_player, evaluator=self.guest)
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:my-evaluations"))
+        player_response = self.client.get(reverse("analytics:my-evaluations-player", kwargs={"player_id": self.second_player.id}))
+        forbidden_response = self.client.get(reverse("analytics:my-evaluations-player", kwargs={"player_id": self.other_player.id}))
+
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, self.second_player.display_name)
+        self.assertContains(response, reverse("analytics:my-evaluations-player", kwargs={"player_id": self.player.id}))
+        self.assertContains(response, reverse("analytics:my-evaluations-player", kwargs={"player_id": self.second_player.id}))
+        self.assertContains(response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": first_observation.id}))
+        self.assertContains(player_response, self.second_player.display_name)
+        self.assertContains(player_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": second_observation.id}))
+        self.assertNotContains(player_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": first_observation.id}))
+        self.assertEqual(forbidden_response.status_code, 403)
+
+    def test_coach_without_self_link_cannot_view_player_result_detail(self):
+        observation = self.submitted_observation()
+        self.client.force_login(self.coach)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+
+        self.assertContains(list_response, "No player record is linked to your account.")
+        self.assertEqual(detail_response.status_code, 403)
+
+    def test_staff_review_and_submission_routes_still_work(self):
+        observation = self.submitted_observation()
+        self.client.force_login(self.staff)
+
+        self.assertEqual(self.client.get(reverse("analytics:observation-review-list")).status_code, 200)
+        self.assertEqual(
+            self.client.get(reverse("analytics:observation-review-detail", kwargs={"observation_id": observation.id})).status_code,
+            200,
+        )
+
+        self.client.force_login(self.player_user)
+        self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 200)
diff --git a/analytics/urls.py b/analytics/urls.py
index 7992f3b..3d080a2 100644
--- a/analytics/urls.py
+++ b/analytics/urls.py
@@ -7,6 +7,9 @@ from analytics.views import (
     CoachAssessmentListView,
     EvaluationListView,
     EvaluationPlayerView,
+    MyEvaluationDetailView,
+    MyEvaluationsPlayerView,
+    MyEvaluationsView,
     PlayerComparisonView,
     PlayerProfileView,
     PlayerImportConfirmView,
@@ -30,6 +33,9 @@ urlpatterns = [
     path("players/<int:player_id>/", PlayerProfileView.as_view(), name="player-profile"),
     path("evaluations/", EvaluationListView.as_view(), name="evaluation-list"),
     path("evaluations/players/<int:player_id>/", EvaluationPlayerView.as_view(), name="evaluation-player"),
+    path("my/evaluations/", MyEvaluationsView.as_view(), name="my-evaluations"),
+    path("my/evaluations/players/<int:player_id>/", MyEvaluationsPlayerView.as_view(), name="my-evaluations-player"),
+    path("my/evaluations/<int:observation_id>/", MyEvaluationDetailView.as_view(), name="my-evaluation-detail"),
     path("assessments/", CoachAssessmentListView.as_view(), name="assessment-list"),
     path("assessments/players/<int:player_id>/", CoachAssessmentEditView.as_view(), name="assessment-player"),
     path("assessments/<int:observation_id>/", CoachAssessmentDetailView.as_view(), name="assessment-detail"),
diff --git a/analytics/views.py b/analytics/views.py
index 1cf237c..14d49c2 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -2,6 +2,7 @@ from django.contrib import messages
 from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
 from django.core.exceptions import PermissionDenied, ValidationError
 from django.db.models import Q
+from django.http import Http404
 from django.shortcuts import get_object_or_404, redirect
 from django.urls import reverse
 from django.views.generic import FormView, ListView, TemplateView, View
@@ -32,6 +33,8 @@ from analytics.services.draft_service import get_draft_contexts_for_player
 from analytics.services.evaluation_access_service import (
     active_evaluation_cycle,
     get_evaluation_target_list,
+    get_my_evaluation_detail,
+    get_my_evaluations,
     get_or_create_evaluation_for_player,
 )
 from analytics.services.observation_service import get_observation_detail, save_observation_responses, submit_observation
@@ -41,6 +44,7 @@ from analytics.services.permissions import (
     can_reopen_observation,
     can_submit_coach_assessment,
     can_submit_evaluation,
+    can_view_my_evaluations,
     can_view_observation,
 )
 from analytics.services.metrics_service import normalize_cycle_id
@@ -341,6 +345,62 @@ class EvaluationPlayerView(EvaluationSubmitterRequiredMixin, TemplateView):
         return self.render_to_response(self.get_context_data(form=form))
 
 
+class MyEvaluationsView(LoginRequiredMixin, TemplateView):
+    template_name = "analytics/my_evaluations.html"
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        players, evaluations = get_my_evaluations(self.request.user)
+        context.update(
+            {
+                "players": players,
+                "evaluations": evaluations,
+                "has_self_link": bool(players),
+                "selected_player": None,
+            }
+        )
+        return context
+
+
+class MyEvaluationsPlayerView(LoginRequiredMixin, TemplateView):
+    template_name = "analytics/my_evaluations.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        self.player = get_object_or_404(Player, pk=kwargs["player_id"])
+        if not can_view_my_evaluations(request.user, player=self.player):
+            raise PermissionDenied("You cannot view evaluations for this player.")
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        players, evaluations = get_my_evaluations(self.request.user, player=self.player)
+        context.update(
+            {
+                "players": players,
+                "evaluations": evaluations,
+                "has_self_link": bool(players),
+                "selected_player": self.player,
+            }
+        )
+        return context
+
+
+class MyEvaluationDetailView(LoginRequiredMixin, TemplateView):
+    template_name = "analytics/my_evaluation_detail.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        try:
+            self.detail = get_my_evaluation_detail(request.user, kwargs["observation_id"])
+        except Observation.DoesNotExist as exc:
+            raise Http404("Evaluation not found.") from exc
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["detail"] = self.detail
+        return context
+
+
 class CoachAssessmentListView(LoginRequiredMixin, TemplateView):
     template_name = "analytics/assessment_list.html"
 
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 471194d..3dcfc87 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -364,7 +364,19 @@ When submitting an assessment:
 Submitted assessments become part of the player's Analytics record.
 
 Players, coaches, staff, and guest evaluators use the evaluation pages to submit evaluations. Staff-only review pages and player result pages are separate workflows.
-After submitting, an evaluator can view their own submission. Player-facing pages that show all evaluations about a player are not available yet.
+After submitting, an evaluator can view their own submission.
+
+## Player My Evaluations
+
+Players with a linked self player record can view submitted evaluations about themselves:
+
+```text
+/analytics/my/evaluations/
+```
+
+Player-facing evaluation results show evaluator role/category, submitted date, cycle, ratings, and notes. Evaluator names, usernames, and email addresses are hidden from players.
+
+Draft and reopened evaluations are not shown as final feedback. Coaches still do not have an all-evaluation review page until the coach review phase.
 
 ## Who Can Evaluate A Player
 
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index 1454276..16c8914 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -987,6 +987,8 @@ Deliverables:
 - no access to other players' private results;
 - tests.
 
+Status: implemented.
+
 ### Phase 5: Coach Review And Filtering
 
 Purpose:
```
