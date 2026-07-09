# Prompt 58 - Analytics

## User Prompt

```text
Perform Evaluation Access V1 Phase 3 Player Evaluation Submission review fixes only.

Do NOT implement Phase 4, 5, or 6.

Do NOT implement player “My Evaluations.”

Do NOT implement coach evaluation review/filtering.

Do NOT change coach import.

Goal:
Review the completed Phase 3 player evaluation submission workflow for privacy, permission consistency, UX clarity, and service-boundary correctness.

Read:
- docs/ARCHITECTURE.md
- docs/USER_MANUAL.md
- docs/evaluations/implementation/engineering/evaluation_access_v1.md
- docs/analytics/architecture/
- docs/analytics/implementation/
- docs/account_management/V1_SUMMARY.md
- AGENTS.md

Review:
- analytics/services/evaluation_access_service.py
- analytics/services/permissions.py
- analytics/services/observation_service.py
- analytics/views.py
- analytics/urls.py
- analytics/templates/analytics/evaluation_list.html
- analytics/templates/analytics/evaluation_form.html
- accounts/templates/accounts/profile.html
- analytics/tests.py
- accounts/tests.py

==================================================
Required Review Areas
==================================================

1. Submitted evaluation detail privacy

Phase 3 redirects submitted evaluations to the existing `analytics:assessment-detail`.

Verify that this does not allow players, coaches, or guest evaluators to view evaluations they should not see.

Rules for Phase 3:

- evaluator can view their own draft/reopened/submitted evaluation detail
- staff can view any evaluation detail through existing staff permissions
- players cannot view other users’ evaluations just by changing URL
- coaches/guest evaluators cannot view other users’ evaluations just by changing URL
- player-facing “evaluations about me” is NOT implemented yet

If existing `can_view_observation()` is too broad or too narrow, fix it in the permission service.

Add regression tests.

--------------------------------------------------

2. Submitted evaluation View link

Review the `View` link on `/analytics/evaluations/`.

It is acceptable only if it links to the evaluator’s own submitted evaluation and permission checks are safe.

If there is any risk of implying “My Evaluations,” adjust copy to:

- “View My Submission”

or similar.

Do NOT implement Phase 4 result viewing.

--------------------------------------------------

3. Account profile navigation permission consistency

The profile template currently links to Submit Evaluation based on role copy/role string.

Change it so the template only receives a service-derived boolean from the view context, such as:

- can_submit_evaluations

This boolean should come from `analytics.services.permissions.can_submit_evaluation(user)`.

Do not duplicate role checks in templates.

Add/update tests proving:

- coach sees Submit Evaluation
- player sees Submit Evaluation
- guest evaluator sees Submit Evaluation
- parent does not
- role/staff logic remains consistent

--------------------------------------------------

4. EvaluationPlayerView state safety

Review `EvaluationPlayerView`.

Do not use class-level mutable or request-specific state for `observation`.

Ensure observation/cycle/player are instance attributes only and are set safely per request.

This is mostly cleanup/hardening.

--------------------------------------------------

5. Cycle handling

Review cycle handling in evaluation list and form.

If a user selects a cycle on the list, continue preserving cycle where applicable.

If only the active/current cycle is supported in Phase 3, make the UI and service behavior clear and avoid unused cycle controls.

Do not implement historical-cycle workflows.

--------------------------------------------------

6. Permission/service boundaries

Ensure:

- views call services
- permission logic remains in `analytics.services.permissions`
- evaluation workflow orchestration remains in `evaluation_access_service`
- no account role logic is duplicated in templates or views
- no player identity logic is duplicated outside player services/query helpers unless already existing

--------------------------------------------------

7. User-facing wording

Ensure Phase 3 copy clearly describes:

- submitting evaluations
- drafts/submissions created by the current evaluator
- not player-facing results about themselves

Avoid wording that implies players can already view all evaluations about themselves.

Do not document Phase 4 or Phase 5 as available.

==================================================
Do NOT Implement
==================================================

Do NOT implement:

- My Evaluations
- coach evaluation review/filtering
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
- models/migrations

==================================================
Testing
==================================================

Add/update tests for:

Privacy:
- evaluator can view their own submitted evaluation detail
- player cannot view another evaluator’s submitted evaluation detail
- coach cannot view another evaluator’s submitted evaluation detail unless staff
- guest evaluator cannot view another evaluator’s submitted evaluation detail
- staff can view submitted evaluation detail

Profile navigation:
- coach sees Submit Evaluation
- player sees Submit Evaluation
- guest evaluator sees Submit Evaluation
- parent does not see Submit Evaluation

Evaluation list:
- submitted row copy says “View My Submission” or otherwise clearly means evaluator’s own submission
- no copy implies My Evaluations/result viewing

Cycle:
- no broken links or lost required parameters
- if current cycle only, no misleading cycle selector

Regression:
- existing coach assessment routes still work
- staff review still works
- Account Operations tests still pass
- Coach import tests still pass
- player import provisioning tests still pass

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
- docs/USER_MANUAL.md
only if wording needs clarification.

Update:
- docs/evaluations/implementation/engineering/evaluation_access_v1.md
only if Phase 3 review status needs clarification.

Do not mark Phase 4 or Phase 5 implemented.

==================================================
Prompt Archive
==================================================

Create the next prompt record in docs/prompts/ according to AGENTS.md.

Commit review fixes first.

Then commit prompt archive separately.

Push both commits.

==================================================
Final Report
==================================================

Report:
- issues found
- fixes applied
- files modified
- tests added/updated
- documentation changes
- test results
- implementation decisions
- remaining technical debt
- confirmation that this was Phase 3 review-fix only
- confirmation that Phase 4+ were NOT implemented
```

## Resulting Commit

```text
7beec3b Apply player evaluation submission review fixes
```

## Commit Diff

```diff
commit 7beec3b51c9af440ed29dfd4724a6904b97dc46a
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 9 10:12:48 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 9 10:12:48 2026 -0700

    Apply player evaluation submission review fixes
---
 accounts/templates/accounts/profile.html           |  2 +-
 accounts/tests.py                                  | 24 +++++++
 accounts/views.py                                  |  2 +
 analytics/services/evaluation_access_service.py    |  7 +-
 analytics/templates/analytics/evaluation_list.html |  4 +-
 analytics/tests.py                                 | 75 +++++++++++++++++++++-
 analytics/views.py                                 |  8 +--
 docs/USER_MANUAL.md                                |  1 +
 .../engineering/evaluation_access_v1.md            |  2 +
 9 files changed, 111 insertions(+), 14 deletions(-)

diff --git a/accounts/templates/accounts/profile.html b/accounts/templates/accounts/profile.html
index ab797b5..bf71969 100644
--- a/accounts/templates/accounts/profile.html
+++ b/accounts/templates/accounts/profile.html
@@ -25,7 +25,7 @@
                 {% endfor %}
             </ul>
         {% endif %}
-        {% if account_role != "parent" %}
+        {% if can_submit_evaluations %}
             <p><a class="button button--primary" href="{% url 'analytics:evaluation-list' %}">Submit Evaluation</a></p>
         {% endif %}
         {% if request.user.is_staff or request.user.is_superuser %}
diff --git a/accounts/tests.py b/accounts/tests.py
index c6b1b6f..c826b08 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -1586,6 +1586,30 @@ class AccountAuthViewTests(TestCase):
         self.assertContains(response, "Account Profile")
         self.assertContains(response, "Guest Evaluator")
 
+    def test_profile_submit_evaluation_link_uses_service_permissions(self):
+        cases = [
+            (AccountRole.COACH, True),
+            (AccountRole.PLAYER, True),
+            (AccountRole.GUEST_EVALUATOR, True),
+            (AccountRole.PARENT, False),
+        ]
+        for role, should_see_link in cases:
+            with self.subTest(role=role):
+                user = User.objects.create_user(username=f"profile-{role}", password="testpass")
+                set_account_role(user, role)
+                self.client.force_login(user)
+
+                response = self.client.get(reverse("accounts:profile"))
+
+                self.assertEqual(response.context["can_submit_evaluations"], should_see_link)
+                if should_see_link:
+                    self.assertContains(response, reverse("analytics:evaluation-list"))
+                    self.assertContains(response, "Submit Evaluation")
+                else:
+                    self.assertNotContains(response, reverse("analytics:evaluation-list"))
+                    self.assertNotContains(response, "Submit Evaluation")
+                self.client.logout()
+
 
 class CoachImportServiceTests(TestCase):
     def setUp(self):
diff --git a/accounts/views.py b/accounts/views.py
index 801a46e..1f6f8c1 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -48,6 +48,7 @@ from accounts.services.permissions import (
 )
 from accounts.services.profile_service import get_account_role
 from accounts.services.role_service import role_label
+from analytics.services.permissions import can_submit_evaluation
 
 
 class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
@@ -100,6 +101,7 @@ class AccountProfileView(LoginRequiredMixin, TemplateView):
             {
                 "account_role": role,
                 "account_role_label": role_label(role),
+                "can_submit_evaluations": can_submit_evaluation(self.request.user),
                 "linked_players": get_players_for_user(self.request.user),
             }
         )
diff --git a/analytics/services/evaluation_access_service.py b/analytics/services/evaluation_access_service.py
index b718441..6d54ac8 100644
--- a/analytics/services/evaluation_access_service.py
+++ b/analytics/services/evaluation_access_service.py
@@ -13,7 +13,6 @@ from analytics.services.coach_assessment_service import (
     get_or_create_draft_coach_assessment,
     list_players_for_assessment,
 )
-from analytics.services.metrics_service import normalize_cycle_id
 from analytics.services.permissions import can_evaluate_player, can_submit_evaluation
 from players.models import Player
 
@@ -40,7 +39,7 @@ def get_evaluation_target_list(user, params) -> EvaluationTargetList:
     if not can_submit_evaluation(user):
         raise PermissionDenied("You cannot submit evaluations.")
 
-    cycle = get_active_coach_assessment_cycle(normalize_cycle_id(params.get("cycle")))
+    cycle = get_active_coach_assessment_cycle()
     query = (params.get("q") or "").strip()
     division = (params.get("division") or "").strip()
     team = (params.get("team") or "").strip()
@@ -85,6 +84,6 @@ def get_or_create_evaluation_for_player(user, player: Player, cycle: EvaluationC
     return get_or_create_draft_coach_assessment(player, cycle, user)
 
 
-def active_evaluation_cycle(cycle_id: str | int | None = None) -> EvaluationCycle | None:
+def active_evaluation_cycle() -> EvaluationCycle | None:
     """Return the active evaluation cycle for player-facing evaluation submission."""
-    return get_active_coach_assessment_cycle(normalize_cycle_id(cycle_id))
+    return get_active_coach_assessment_cycle()
diff --git a/analytics/templates/analytics/evaluation_list.html b/analytics/templates/analytics/evaluation_list.html
index 469db7a..75af0b9 100644
--- a/analytics/templates/analytics/evaluation_list.html
+++ b/analytics/templates/analytics/evaluation_list.html
@@ -32,7 +32,7 @@
                         <th>Player</th>
                         <th>Division</th>
                         <th>Team</th>
-                        <th>My draft evaluations</th>
+                        <th>My submission</th>
                         <th>Action</th>
                     </tr>
                 </thead>
@@ -47,7 +47,7 @@
                                 {% if not item.can_evaluate %}
                                     <span class="pdp-badge pdp-badge--muted">Self-evaluation blocked</span>
                                 {% elif item.observation and item.status == "submitted" %}
-                                    <a class="button button--ghost" href="{% url 'analytics:assessment-detail' observation_id=item.observation.id %}">View</a>
+                                    <a class="button button--ghost" href="{% url 'analytics:assessment-detail' observation_id=item.observation.id %}">View My Submission</a>
                                 {% elif item.observation %}
                                     <a class="button button--primary" href="{% url 'analytics:evaluation-player' player_id=item.player.id %}">Continue</a>
                                 {% else %}
diff --git a/analytics/tests.py b/analytics/tests.py
index 1659724..53c1430 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -1778,6 +1778,16 @@ class EvaluationAccessSubmissionViewTests(TestCase):
                 data[field_name] = "Good teammate."
         return data
 
+    def service_response_payload(self):
+        return {
+            question: 4
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+
     def test_evaluation_list_permissions(self):
         self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 302)
         for user in [self.player_user, self.coach, self.guest, self.staff]:
@@ -1798,7 +1808,7 @@ class EvaluationAccessSubmissionViewTests(TestCase):
 
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Evaluate Player")
-        self.assertContains(response, "My draft evaluations")
+        self.assertContains(response, "My submission")
         self.assertContains(response, "Self-evaluation blocked")
         self.assertContains(response, reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
 
@@ -1856,6 +1866,43 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
         self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
 
+    def test_submitted_evaluation_detail_is_private_to_evaluator_and_staff(self):
+        result = create_coach_assessment_observation(
+            player=self.target_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.player_user,
+            responses=self.service_response_payload(),
+        )
+        observation = submit_observation(result.observation, actor=self.player_user)
+        detail_url = reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id})
+
+        self.client.force_login(self.player_user)
+        self.assertEqual(self.client.get(detail_url).status_code, 200)
+
+        for user in [self.coach, self.guest]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                self.assertEqual(self.client.get(detail_url).status_code, 403)
+
+        self.client.force_login(self.staff)
+        self.assertEqual(self.client.get(detail_url).status_code, 200)
+
+    def test_player_cannot_view_another_evaluators_submitted_detail(self):
+        other_player_user = User.objects.create_user(username="other-player-evaluator", password="testpass")
+        set_account_role(other_player_user, AccountRole.PLAYER)
+        result = create_coach_assessment_observation(
+            player=self.target_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.service_response_payload(),
+        )
+        observation = submit_observation(result.observation, actor=self.coach)
+
+        self.client.force_login(other_player_user)
+        response = self.client.get(reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
+
+        self.assertEqual(response.status_code, 403)
+
     def test_missing_required_responses_are_blocked(self):
         self.client.force_login(self.player_user)
 
@@ -1882,6 +1929,32 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
         self.assertEqual(Observation.objects.filter(player=self.target_player, evaluator=self.player_user).count(), 1)
 
+    def test_evaluation_list_submitted_copy_is_own_submission(self):
+        result = create_coach_assessment_observation(
+            player=self.target_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.player_user,
+            responses=self.service_response_payload(),
+        )
+        submit_observation(result.observation, actor=self.player_user)
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:evaluation-list"), {"q": "Target"})
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "View My Submission")
+        self.assertNotContains(response, ">View<")
+        self.assertNotContains(response, "evaluations about me")
+
+    def test_evaluation_list_uses_current_cycle_without_cycle_selector(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:evaluation-list"), {"cycle": "999"})
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.cycle.name)
+        self.assertNotContains(response, 'name="cycle"')
+
     def test_coach_and_guest_role_snapshots_continue_to_work(self):
         for user, expected_role in [(self.coach, ROLE_COACH), (self.guest, ROLE_GUEST_EVALUATOR)]:
             with self.subTest(user=user.username):
diff --git a/analytics/views.py b/analytics/views.py
index 2a2e88f..1cf237c 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -279,10 +279,6 @@ class EvaluationListView(EvaluationSubmitterRequiredMixin, TemplateView):
                 "query": target_list.query,
                 "division": target_list.division,
                 "team": target_list.team,
-                "cycles": EvaluationCycle.objects.filter(
-                    is_active=True,
-                    coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT,
-                ),
             }
         )
         return context
@@ -290,10 +286,10 @@ class EvaluationListView(EvaluationSubmitterRequiredMixin, TemplateView):
 
 class EvaluationPlayerView(EvaluationSubmitterRequiredMixin, TemplateView):
     template_name = "analytics/evaluation_form.html"
-    observation = None
 
     def dispatch(self, request, *args, **kwargs):
-        cycle = active_evaluation_cycle(request.GET.get("cycle"))
+        self.observation = None
+        cycle = active_evaluation_cycle()
         if not cycle:
             messages.error(request, "No active evaluation cycle is available.")
             return redirect("analytics:evaluation-list")
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index b0e7b2f..471194d 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -364,6 +364,7 @@ When submitting an assessment:
 Submitted assessments become part of the player's Analytics record.
 
 Players, coaches, staff, and guest evaluators use the evaluation pages to submit evaluations. Staff-only review pages and player result pages are separate workflows.
+After submitting, an evaluator can view their own submission. Player-facing pages that show all evaluations about a player are not available yet.
 
 ## Who Can Evaluate A Player
 
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index ea78195..1454276 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -970,6 +970,8 @@ Deliverables:
 
 Status: implemented.
 
+Review fixes: completed. Submitted evaluation detail remains limited to the evaluator and staff; the evaluation list labels submitted links as "View My Submission"; profile navigation uses service-derived evaluation permission context.
+
 ### Phase 4: Player "My Evaluations"
 
 Purpose:
```
