# Prompt 61 - Analytics

## Prompt

```text
You are performing a loop-engineering review of Evaluation Access V1 Phase 4: Player “My Evaluations.”

This is a review/fix task only.

Do NOT implement Phase 5 or Phase 6.

Do NOT implement coach evaluation review or filtering.

Do NOT add new product features.

Your goal is to repeatedly inspect, verify, and improve the existing Phase 4 implementation until it satisfies the acceptance criteria below.

==================================================
Loop Specification
==================

Maximum loops: 3

Each loop must follow this sequence:

1. Inspect
2. Identify concrete issues
3. Fix only verified issues
4. Add or update focused tests
5. Run focused verification
6. Reassess the acceptance criteria
7. Either stop or begin the next loop

Do not repeat a loop merely to refactor working code.

Do not make speculative changes.

Do not exceed three loops.

==================================================
Terminal States
===============

Stop with one of these explicit terminal states:

PASS

All acceptance criteria are satisfied and all required tests pass.

BLOCKED

A necessary fix requires a product decision, model/migration, architectural change, or scope expansion that is not authorized.

LIMIT_REACHED

Three loops were completed, but one or more acceptance criteria still fail.

If BLOCKED or LIMIT_REACHED, do not declare Phase 4 accepted. Report the exact blocker.

==================================================
Before Loop 1
=============

Read:

* AGENTS.md
* docs/ARCHITECTURE.md
* docs/USER_MANUAL.md
* docs/evaluations/implementation/engineering/evaluation_access_v1.md
* docs/analytics/architecture/
* docs/analytics/implementation/
* docs/account_management/V1_SUMMARY.md

Review:

* accounts/services/link_service.py
* accounts/views.py
* accounts/templates/accounts/profile.html
* accounts/tests.py
* analytics/services/evaluation_access_service.py
* analytics/services/permissions.py
* analytics/views.py
* analytics/urls.py
* analytics/templates/analytics/my_evaluations.html
* analytics/templates/analytics/my_evaluation_detail.html
* analytics/tests.py

Also inspect relevant models and existing service helpers when needed.

==================================================
Acceptance Criteria
===================

A. Dependency Direction

The intended dependency direction must remain clean:

analytics may depend on accounts

accounts should not depend directly on analytics business services

Review the current dependency:

accounts/views.py
-> analytics.services.permissions

Determine whether this violates the documented architecture.

Preferred correction:

* Account Profile remains owned by accounts.
* Analytics-specific navigation eligibility should not force accounts business logic to import Analytics permissions.
* Avoid circular or reverse subsystem ownership.
* Do not duplicate Analytics role rules inside accounts.

Use the smallest clean solution.

Possible approaches include:

* a neutral integration/context helper owned at the platform layer;
* computing navigation eligibility from account-owned facts without duplicating Analytics policy, if architecturally valid;
* moving evaluation navigation to an Analytics-owned surface;
* another minimal solution consistent with documented dependency direction.

Do not introduce a generic abstraction unless it solves the actual dependency issue.

B. Missing Versus Forbidden Resources

For My Evaluation detail:

* nonexistent observation ID returns 404;
* existing observation belonging to another player returns 403;
* existing draft or reopened observation about the linked player returns 403;
* submitted observation about an actively self-linked player returns 200.

Do not reveal through error messages whether a forbidden evaluation belongs to another player.

C. Active Link Enforcement

Only active `self` links grant access.

Verify:

* deactivating the self link immediately removes list access;
* deactivating the self link immediately removes detail access;
* inactive self links do not show profile navigation;
* reactivating the link restores access according to existing link rules.

D. Player Activity State

Decide consistently whether an inactive player record should remain accessible through My Evaluations.

Recommended rule:

* active self link remains the primary authorization rule;
* inactive canonical players should not appear in normal My Evaluations navigation or lists;
* direct access should be denied unless an existing documented archival rule clearly says otherwise.

Apply the smallest consistent rule and document it if behavior changes.

Do not change player lifecycle semantics outside My Evaluations.

E. Evaluator Privacy

Player-facing read models and templates must not expose:

* evaluator object
* evaluator ID
* evaluator username
* evaluator email
* evaluator first or last name
* evaluator display name
* evaluator metadata

Player-facing output may expose only:

* evaluator role/category snapshot
* submitted date
* cycle
* target player
* questions and responses

Review dataclass fields and template context, not only visible HTML.

Avoid passing the full Observation object to player-facing templates when a safer identifier/read model is sufficient.

F. Staff With Self Links

A staff or superuser account with an active self link may use My Evaluations as the linked player.

On My Evaluations routes, that user must receive the same player-safe representation:

* evaluator identity remains hidden;
* no extra staff-only information appears merely because the user is staff;
* staff review remains available separately through staff routes.

G. Response Ordering

Responses must use deterministic question ordering.

Prefer existing question ordering fields and category/question ordering conventions.

Do not rely on database default ordering unless the model explicitly guarantees the required order.

Add a regression test that inserts or saves responses in a different order and verifies display order remains correct.

H. Multiple Self Links

Verify:

* all active, eligible self-linked players appear;
* inactive links do not appear;
* player-specific route enforces ownership;
* detail access works for every eligible linked player;
* no duplicate players appear.

I. View Thinness

Views should:

* resolve route inputs;
* call services;
* translate missing resources to 404 where appropriate;
* render returned read models.

Views should not own evaluation query construction, privacy filtering, or self-link business rules.

J. Documentation Accuracy

The user manual must accurately state:

* submitted evaluations only;
* evaluator identity hidden;
* evaluator role/category visible;
* active self link required;
* coach all-evaluation review is not yet available.

Do not document Phase 5 as implemented.

==================================================
Loop 1 — Architecture and Privacy
=================================

Inspect all acceptance criteria, prioritizing:

* dependency direction;
* player-safe read models;
* evaluator identity exposure;
* missing-versus-forbidden behavior;
* active-link enforcement.

Before editing, write a concise internal issue list based on concrete code evidence.

Fix only verified issues.

Run focused tests:

python manage.py test analytics
python manage.py test accounts
git diff --check

Reassess all acceptance criteria.

If all criteria appear satisfied, proceed directly to final full verification.

Otherwise begin Loop 2.

==================================================
Loop 2 — Edge Cases and Data Correctness
========================================

Review the code after Loop 1.

Prioritize:

* inactive self links;
* inactive players;
* multiple self links;
* deterministic response ordering;
* staff users with self links;
* 403 versus 404 behavior;
* duplicate query or N+1 concerns in My Evaluations.

Fix only verified remaining issues.

Add focused regression tests.

Run:

python manage.py test analytics
python manage.py test accounts
git diff --check

Reassess all acceptance criteria.

If all criteria are satisfied, proceed to final full verification.

Otherwise begin Loop 3.

==================================================
Loop 3 — Final Simplification and Consistency
=============================================

Review only acceptance criteria that remain unsatisfied.

Do not conduct a broad refactor.

Check for:

* duplicated permission logic;
* unnecessary cross-app imports;
* unsafe read-model fields;
* inconsistent messages;
* missing tests for an identified issue;
* stale documentation caused by fixes.

Fix only what is required to satisfy the remaining criteria.

Run:

python manage.py test analytics
python manage.py test accounts
git diff --check

After Loop 3, choose PASS, BLOCKED, or LIMIT_REACHED.

==================================================
Required Tests
==============

Ensure coverage for:

* nonexistent detail ID returns 404;
* forbidden existing detail returns 403;
* draft/reopened detail returns 403;
* inactive self link removes list/detail access;
* inactive self link removes profile navigation;
* inactive player behavior is consistent with the selected rule;
* evaluator identity is absent from HTML and player-safe read models;
* evaluator role snapshot remains visible;
* staff with self link receives player-safe output;
* response order follows question ordering;
* multiple active self links work without duplicates;
* player-specific route enforces ownership;
* coach and parent without self links cannot use My Evaluations;
* existing evaluation submission still works;
* existing staff review still works.

==================================================
Full Verification
=================

After reaching a prospective PASS state, run:

python manage.py check
python manage.py makemigrations analytics --check
python manage.py makemigrations accounts --check
python manage.py test analytics
python manage.py test accounts
python manage.py test players
python manage.py test drafts
python manage.py test pdp
python manage.py test
git diff --check

If any full verification step fails:

* return to the current loop if fewer than three loops have been completed;
* fix the verified regression;
* rerun focused and full verification;
* do not declare PASS while any required command fails.

==================================================
Documentation
=============

Update only when necessary:

* docs/USER_MANUAL.md
* docs/evaluations/implementation/engineering/evaluation_access_v1.md

Record that Phase 4 review fixes are complete only if the terminal state is PASS.

Do not mark Phase 5 or Phase 6 implemented.

==================================================
Do NOT Implement
================

Do NOT implement:

* coach evaluation review or filtering;
* coach review detail;
* changes to staff review workflows;
* coach import changes;
* coach-to-player links;
* parent portal;
* full player portal;
* audit logging;
* invitations;
* email;
* APIs;
* JavaScript;
* charts;
* exports;
* new observation types;
* new models or migrations.

If a required fix appears to need a model or migration, stop with BLOCKED and explain why.

==================================================
Prompt Archive and Commits
==========================

If the terminal state is PASS and files changed:

1. Commit Phase 4 review fixes.
2. Create the next prompt record in `docs/prompts/` according to AGENTS.md.
3. Commit the prompt archive separately.
4. Push both commits.

If terminal state is BLOCKED or LIMIT_REACHED:

* do not mark Phase 4 accepted;
* do not create unrelated fixes;
* follow AGENTS.md regarding prompt archival and commits;
* clearly report uncommitted or committed state.

==================================================
Final Report
============

Report:

* terminal state: PASS, BLOCKED, or LIMIT_REACHED;
* number of loops completed;
* issues identified in each loop;
* fixes applied in each loop;
* files modified;
* tests added or updated;
* architecture outcome;
* privacy outcome;
* 403/404 outcome;
* link and inactive-player outcome;
* response-ordering outcome;
* documentation updates;
* focused test results;
* full verification results;
* remaining technical debt;
* commits created;
* push result;
* confirmation that Phase 5 and Phase 6 were not implemented.

Only state that Phase 4 is accepted if the terminal state is PASS.
```

## Implementation Commit

`7ed9d9c Harden player my evaluations access`

## Commit Diff

```diff
commit 7ed9d9c792d3c357a3e5ac5a2b01d6fce6f3e02d
Author: Eugene Lin <eugenelin89@gmail.com>
Date:   Fri Jul 10 11:17:03 2026 -0700

    Harden player my evaluations access

diff --git a/accounts/templates/accounts/profile.html b/accounts/templates/accounts/profile.html
index 7574bf1..b18eb81 100644
--- a/accounts/templates/accounts/profile.html
+++ b/accounts/templates/accounts/profile.html
@@ -1,4 +1,5 @@
 {% extends "pdp/base.html" %}
+{% load analytics_account_nav %}
 
 {% block pdp_title %}Account Profile{% endblock %}
 {% block pdp_subtitle %}Basic account information.{% endblock %}
@@ -25,12 +26,7 @@
                 {% endfor %}
             </ul>
         {% endif %}
-        {% if can_submit_evaluations %}
-            <p><a class="button button--primary" href="{% url 'analytics:evaluation-list' %}">Submit Evaluation</a></p>
-        {% endif %}
-        {% if can_view_my_evaluations %}
-            <p><a class="button button--ghost" href="{% url 'analytics:my-evaluations' %}">My Evaluations</a></p>
-        {% endif %}
+        {% analytics_account_profile_actions request.user %}
         {% if request.user.is_staff or request.user.is_superuser %}
             <p><a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Account Operations</a></p>
         {% endif %}
diff --git a/accounts/tests.py b/accounts/tests.py
index 21a0a54..c4d16a8 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -1601,7 +1601,6 @@ class AccountAuthViewTests(TestCase):
 
                 response = self.client.get(reverse("accounts:profile"))
 
-                self.assertEqual(response.context["can_submit_evaluations"], should_see_link)
                 if should_see_link:
                     self.assertContains(response, reverse("analytics:evaluation-list"))
                     self.assertContains(response, "Submit Evaluation")
@@ -1622,7 +1621,6 @@ class AccountAuthViewTests(TestCase):
 
         self.client.force_login(player_user)
         response = self.client.get(reverse("accounts:profile"))
-        self.assertTrue(response.context["can_view_my_evaluations"])
         self.assertContains(response, reverse("analytics:my-evaluations"))
         self.assertContains(response, "My Evaluations")
 
@@ -1630,7 +1628,6 @@ class AccountAuthViewTests(TestCase):
             with self.subTest(user=user.username):
                 self.client.force_login(user)
                 response = self.client.get(reverse("accounts:profile"))
-                self.assertFalse(response.context["can_view_my_evaluations"])
                 self.assertNotContains(response, reverse("analytics:my-evaluations"))
                 self.client.logout()
 
diff --git a/accounts/views.py b/accounts/views.py
index c24b3ee..801a46e 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -48,7 +48,6 @@ from accounts.services.permissions import (
 )
 from accounts.services.profile_service import get_account_role
 from accounts.services.role_service import role_label
-from analytics.services.permissions import can_submit_evaluation, can_view_my_evaluations
 
 
 class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
@@ -101,8 +100,6 @@ class AccountProfileView(LoginRequiredMixin, TemplateView):
             {
                 "account_role": role,
                 "account_role_label": role_label(role),
-                "can_submit_evaluations": can_submit_evaluation(self.request.user),
-                "can_view_my_evaluations": can_view_my_evaluations(self.request.user),
                 "linked_players": get_players_for_user(self.request.user),
             }
         )
diff --git a/analytics/services/evaluation_access_service.py b/analytics/services/evaluation_access_service.py
index 8e37de0..8564ea9 100644
--- a/analytics/services/evaluation_access_service.py
+++ b/analytics/services/evaluation_access_service.py
@@ -47,7 +47,7 @@ class EvaluationTargetList:
 
 @dataclass(frozen=True)
 class MyEvaluationSummary:
-    observation: Observation
+    observation_id: int
     player: Player
     evaluator_role_name: str
     submitted_at: object
@@ -64,7 +64,7 @@ class MyEvaluationQuestionResponse:
 
 @dataclass(frozen=True)
 class MyEvaluationDetail:
-    observation: Observation
+    observation_id: int
     player: Player
     evaluator_role_name: str
     submitted_at: object
@@ -150,7 +150,7 @@ def get_my_evaluations(user, player: Player | None = None) -> tuple[list[Player]
     )
     summaries = [
         MyEvaluationSummary(
-            observation=observation,
+            observation_id=observation.id,
             player=observation.player,
             evaluator_role_name=observation.evaluator_role_name or "Evaluator",
             submitted_at=observation.submitted_at,
@@ -165,7 +165,6 @@ def get_my_evaluation_detail(user, observation_id: int) -> MyEvaluationDetail:
     """Return a player-safe submitted evaluation detail view."""
     observation = (
         Observation.objects.select_related("player", "evaluation_cycle", "evaluator_role")
-        .prefetch_related("responses__question")
         .get(pk=observation_id)
     )
     if not can_view_my_evaluation_detail(user, observation):
@@ -177,10 +176,14 @@ def get_my_evaluation_detail(user, observation_id: int) -> MyEvaluationDetail:
             numeric_value=response.numeric_value,
             text_value=response.text_value,
         )
-        for response in observation.responses.all()
+        for response in observation.responses.select_related("question").order_by(
+            "question__display_order",
+            "question_id",
+            "id",
+        )
     ]
     return MyEvaluationDetail(
-        observation=observation,
+        observation_id=observation.id,
         player=observation.player,
         evaluator_role_name=observation.evaluator_role_name or "Evaluator",
         submitted_at=observation.submitted_at,
diff --git a/analytics/services/permissions.py b/analytics/services/permissions.py
index 7dab101..c5f9ed0 100644
--- a/analytics/services/permissions.py
+++ b/analytics/services/permissions.py
@@ -67,8 +67,10 @@ def can_view_my_evaluations(user, player=None) -> bool:
     if not user or not user.is_authenticated:
         return False
     if player is not None:
+        if not getattr(player, "is_active", False):
+            return False
         return is_player_self(user, player)
-    return get_self_linked_players(user).exists()
+    return get_self_linked_players(user).filter(is_active=True).exists()
 
 
 def can_view_my_evaluation_detail(user, observation) -> bool:
diff --git a/analytics/templates/analytics/includes/account_profile_actions.html b/analytics/templates/analytics/includes/account_profile_actions.html
new file mode 100644
index 0000000..42a34ee
--- /dev/null
+++ b/analytics/templates/analytics/includes/account_profile_actions.html
@@ -0,0 +1,6 @@
+{% if can_submit_evaluations %}
+    <p><a class="button button--primary" href="{% url 'analytics:evaluation-list' %}">Submit Evaluation</a></p>
+{% endif %}
+{% if can_view_my_evaluations %}
+    <p><a class="button button--ghost" href="{% url 'analytics:my-evaluations' %}">My Evaluations</a></p>
+{% endif %}
diff --git a/analytics/templates/analytics/my_evaluations.html b/analytics/templates/analytics/my_evaluations.html
index 14f6673..2dd2921 100644
--- a/analytics/templates/analytics/my_evaluations.html
+++ b/analytics/templates/analytics/my_evaluations.html
@@ -37,7 +37,7 @@
                             <td>{{ item.cycle_name }}</td>
                             <td>{{ item.evaluator_role_name }}</td>
                             <td>{{ item.submitted_at|date:"M j, Y" }}</td>
-                            <td><a class="button button--ghost" href="{% url 'analytics:my-evaluation-detail' observation_id=item.observation.id %}">View Evaluation</a></td>
+                            <td><a class="button button--ghost" href="{% url 'analytics:my-evaluation-detail' observation_id=item.observation_id %}">View Evaluation</a></td>
                         </tr>
                     {% empty %}
                         <tr><td colspan="5">No submitted evaluations are available yet.</td></tr>
diff --git a/analytics/templatetags/__init__.py b/analytics/templatetags/__init__.py
new file mode 100644
index 0000000..8b13789
--- /dev/null
+++ b/analytics/templatetags/__init__.py
@@ -0,0 +1 @@
+
diff --git a/analytics/templatetags/analytics_account_nav.py b/analytics/templatetags/analytics_account_nav.py
new file mode 100644
index 0000000..3fa5a5e
--- /dev/null
+++ b/analytics/templatetags/analytics_account_nav.py
@@ -0,0 +1,15 @@
+from django import template
+
+from analytics.services.permissions import can_submit_evaluation, can_view_my_evaluations
+
+
+register = template.Library()
+
+
+@register.inclusion_tag("analytics/includes/account_profile_actions.html")
+def analytics_account_profile_actions(user):
+    """Render Analytics-owned account profile navigation eligibility."""
+    return {
+        "can_submit_evaluations": can_submit_evaluation(user),
+        "can_view_my_evaluations": can_view_my_evaluations(user),
+    }
diff --git a/analytics/tests.py b/analytics/tests.py
index 15d6e06..756f8ce 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -12,7 +12,7 @@ from django.urls import reverse
 from django.utils import timezone
 
 from accounts.models import AccountRole, UserPlayerRelationship
-from accounts.services.link_service import deactivate_link, link_user_to_player
+from accounts.services.link_service import activate_link, deactivate_link, link_user_to_player
 from accounts.services.profile_service import set_account_role
 from analytics.models import (
     OBSERVATION_STATUS_DRAFT,
@@ -71,6 +71,7 @@ from analytics.services.permissions import (
 )
 from analytics.services.reporting_service import get_command_center_context
 from analytics.services.draft_service import get_draft_context_for_draft_player, get_draft_contexts_for_draft
+from analytics.services.evaluation_access_service import get_my_evaluation_detail, get_my_evaluations
 from analytics.services.question_service import (
     COACH_ASSESSMENT_RUBRIC,
     DEFAULT_COACH_ASSESSMENT_QUESTIONS,
@@ -2066,6 +2067,21 @@ class MyEvaluationsViewTests(TestCase):
         self.assertNotContains(response, self.coach.email)
         self.assertNotContains(response, self.coach.get_full_name())
 
+        players, summaries = get_my_evaluations(self.player_user)
+        detail = get_my_evaluation_detail(self.player_user, observation.id)
+        self.assertEqual(players, [self.player])
+        self.assertEqual(summaries[0].observation_id, observation.id)
+        self.assertFalse(hasattr(summaries[0], "observation"))
+        self.assertEqual(detail.observation_id, observation.id)
+        self.assertFalse(hasattr(detail, "observation"))
+
+    def test_nonexistent_my_evaluation_detail_returns_404(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": 999999}))
+
+        self.assertEqual(response.status_code, 404)
+
     def test_player_cannot_view_another_players_evaluation_by_url(self):
         observation = self.submitted_observation(player=self.other_player, evaluator=self.coach)
         self.client.force_login(self.player_user)
@@ -2107,22 +2123,35 @@ class MyEvaluationsViewTests(TestCase):
             relationship=UserPlayerRelationship.SELF,
             is_primary=False,
         )
+        inactive_player = Player.objects.create(first_name="Inactive", last_name="Linked")
+        inactive_link = link_user_to_player(
+            self.player_user,
+            inactive_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+        deactivate_link(inactive_link)
         first_observation = self.submitted_observation(player=self.player, evaluator=self.coach)
         second_observation = self.submitted_observation(player=self.second_player, evaluator=self.guest)
         self.client.force_login(self.player_user)
 
         response = self.client.get(reverse("analytics:my-evaluations"))
         player_response = self.client.get(reverse("analytics:my-evaluations-player", kwargs={"player_id": self.second_player.id}))
+        first_detail = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": first_observation.id}))
+        second_detail = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": second_observation.id}))
         forbidden_response = self.client.get(reverse("analytics:my-evaluations-player", kwargs={"player_id": self.other_player.id}))
 
         self.assertContains(response, self.player.display_name)
         self.assertContains(response, self.second_player.display_name)
+        self.assertNotContains(response, inactive_player.display_name)
         self.assertContains(response, reverse("analytics:my-evaluations-player", kwargs={"player_id": self.player.id}))
         self.assertContains(response, reverse("analytics:my-evaluations-player", kwargs={"player_id": self.second_player.id}))
         self.assertContains(response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": first_observation.id}))
         self.assertContains(player_response, self.second_player.display_name)
         self.assertContains(player_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": second_observation.id}))
         self.assertNotContains(player_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": first_observation.id}))
+        self.assertEqual(first_detail.status_code, 200)
+        self.assertEqual(second_detail.status_code, 200)
         self.assertEqual(forbidden_response.status_code, 403)
 
     def test_coach_without_self_link_cannot_view_player_result_detail(self):
@@ -2135,6 +2164,102 @@ class MyEvaluationsViewTests(TestCase):
         self.assertContains(list_response, "No player record is linked to your account.")
         self.assertEqual(detail_response.status_code, 403)
 
+        self.client.force_login(self.parent)
+        parent_detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+        self.assertEqual(parent_detail_response.status_code, 403)
+
+    def test_inactive_self_link_removes_my_evaluations_access(self):
+        observation = self.submitted_observation()
+        link = self.player_user.player_links.get(player=self.player, relationship=UserPlayerRelationship.SELF)
+        deactivate_link(link)
+        self.client.force_login(self.player_user)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+        profile_response = self.client.get(reverse("accounts:profile"))
+
+        self.assertContains(list_response, "No player record is linked to your account.")
+        self.assertNotContains(list_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+        self.assertEqual(detail_response.status_code, 403)
+        self.assertNotContains(profile_response, reverse("analytics:my-evaluations"))
+
+        activate_link(link)
+        restored_list_response = self.client.get(reverse("analytics:my-evaluations"))
+        restored_detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+        restored_profile_response = self.client.get(reverse("accounts:profile"))
+        self.assertContains(restored_list_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+        self.assertEqual(restored_detail_response.status_code, 200)
+        self.assertContains(restored_profile_response, reverse("analytics:my-evaluations"))
+
+    def test_inactive_player_is_not_available_in_my_evaluations(self):
+        observation = self.submitted_observation()
+        self.player.is_active = False
+        self.player.save(update_fields=["is_active", "updated_at"])
+        self.client.force_login(self.player_user)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        player_response = self.client.get(reverse("analytics:my-evaluations-player", kwargs={"player_id": self.player.id}))
+        detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+        profile_response = self.client.get(reverse("accounts:profile"))
+
+        self.assertContains(list_response, "No player record is linked to your account.")
+        self.assertEqual(player_response.status_code, 403)
+        self.assertEqual(detail_response.status_code, 403)
+        self.assertNotContains(profile_response, reverse("analytics:my-evaluations"))
+
+    def test_staff_with_self_link_receives_player_safe_my_evaluation_output(self):
+        staff_player = Player.objects.create(first_name="Staff", last_name="Player")
+        link_user_to_player(self.staff, staff_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+        observation = self.submitted_observation(player=staff_player, evaluator=self.coach, note="Private staff-linked result.")
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Private staff-linked result.")
+        self.assertContains(response, "Coach")
+        self.assertNotContains(response, self.coach.username)
+        self.assertNotContains(response, self.coach.email)
+        self.assertNotContains(response, self.coach.get_full_name())
+
+    def test_my_evaluation_responses_follow_question_display_order(self):
+        question_set = self.setup_result.question_set
+        first_question = question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
+        second_question = question_set.questions.filter(response_type=RESPONSE_TYPE_TEXT).first()
+        first_question.display_order = 20
+        first_question.save(update_fields=["display_order", "updated_at"])
+        second_question.display_order = 10
+        second_question.prompt = "Appears before the rating"
+        second_question.save(update_fields=["display_order", "prompt", "updated_at"])
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=[
+                {"question": first_question, "value": 4},
+                {"question": second_question, "value": "Ordered note."},
+            ],
+        ).observation
+        for required_question in question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5,
+            is_required=True,
+            is_active=True,
+        ).exclude(pk=first_question.pk):
+            ObservationResponse.objects.create(
+                observation=observation,
+                question=required_question,
+                response_type=required_question.response_type,
+                numeric_value=Decimal("3"),
+            )
+        observation = submit_observation(observation, actor=self.coach)
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
+
+        self.assertEqual(response.status_code, 200)
+        content = response.content.decode()
+        self.assertLess(content.index("Appears before the rating"), content.index(first_question.prompt))
+
     def test_staff_review_and_submission_routes_still_work(self):
         observation = self.submitted_observation()
         self.client.force_login(self.staff)
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 3dcfc87..038245a 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -368,7 +368,7 @@ After submitting, an evaluator can view their own submission.
 
 ## Player My Evaluations
 
-Players with a linked self player record can view submitted evaluations about themselves:
+Players with an active linked self player record can view submitted evaluations about themselves:
 
 ```text
 /analytics/my/evaluations/
@@ -376,7 +376,7 @@ Players with a linked self player record can view submitted evaluations about th
 
 Player-facing evaluation results show evaluator role/category, submitted date, cycle, ratings, and notes. Evaluator names, usernames, and email addresses are hidden from players.
 
-Draft and reopened evaluations are not shown as final feedback. Coaches still do not have an all-evaluation review page until the coach review phase.
+Draft and reopened evaluations are not shown as final feedback. Inactive player links and inactive player records are not shown in normal My Evaluations lists. Coaches still do not have an all-evaluation review page until the coach review phase.
 
 ## Who Can Evaluate A Player
 
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index 16c8914..3c89add 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -989,6 +989,8 @@ Deliverables:
 
 Status: implemented.
 
+Review fixes: completed. Account Profile no longer imports Analytics permission services in `accounts.views`; Analytics owns profile navigation eligibility through an Analytics template tag. Player-facing My Evaluations read models expose observation IDs and player-safe labels instead of full observations, inactive self links and inactive players do not grant access, forbidden existing details return 403 while missing details return 404, and responses render in deterministic question order.
+
 ### Phase 5: Coach Review And Filtering
 
 Purpose:
```
