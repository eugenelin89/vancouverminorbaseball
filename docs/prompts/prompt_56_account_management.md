# Prompt 56 - Account Management

## User Prompt

```text
Implement Evaluation Access V1 Phase 2 only:

Evaluation Permission and Role Snapshot Updates.

Do NOT implement Phase 3, 4, 5, or 6.

Do NOT implement player evaluation submission pages yet.

Do NOT implement player “My Evaluations.”

Do NOT implement coach evaluation review.

Do NOT implement coach import changes.

Goal:
Prepare Analytics evaluation permissions and evaluator role snapshot behavior so coaches, players, staff, and guest evaluators can submit evaluations with correct role attribution.

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
- analytics/models.py
- analytics/services/permissions.py
- analytics/services/coach_assessment_service.py
- analytics/services/observation_service.py
- analytics/views.py
- analytics/forms.py
- analytics/tests.py
- accounts/services/profile_service.py
- accounts/services/link_service.py
- accounts/services/role_service.py
- accounts/services/permissions.py

==================================================
Scope
==================================================

Implement Phase 2 only.

This phase should update service-layer permissions and evaluator role resolution.

It should not add major new UI surfaces.

It should preserve existing coach assessment UI behavior while making underlying permission/role logic correct for future player evaluation access.

==================================================
Required Behavior
==================================================

1. Evaluation submission permissions

Create or update Analytics permission helpers:

- can_submit_evaluation(user, target_player=None)
- can_evaluate_player(user, target_player)
- can_view_own_evaluation_draft(user, observation)
- can_edit_own_evaluation_draft(user, observation)

Rules:

- Anonymous users cannot submit.
- Authenticated coaches can submit.
- Authenticated players can submit.
- Authenticated staff/admin users can submit.
- Authenticated guest evaluators can submit.
- Parents should not submit unless explicitly allowed by existing behavior. For Evaluation Access V1, do not grant parent submission unless the current system already does.
- Self-evaluation is blocked.
- Self-evaluation means user has an active `UserPlayerLink(relationship="self")` to the target player.
- Existing staff review permissions must not regress.

2. Evaluator role resolution

Add or update a service helper such as:

- evaluator_role_for_user(user)

Behavior:

- use `AccountProfile.role` when available
- map account roles to Analytics `EvaluatorRole`
- coach -> coach
- player -> player
- staff -> staff, if Analytics role exists
- admin -> staff or admin depending on existing Analytics roles; prefer staff if no admin role exists
- guest_evaluator -> guest_evaluator, if role exists; otherwise create/use a safe existing equivalent only if already supported
- parent should not become evaluator unless explicitly allowed

If Analytics lacks required `EvaluatorRole` seed data, use existing role creation/helper patterns rather than hardcoding FK IDs.

3. Role snapshot correctness

Update Analytics observation/coach-assessment creation so evaluator role snapshots come from the actual submitting user's account role, not a hardcoded coach default.

Every created evaluation/observation should store:

- evaluator User
- evaluator_role FK
- evaluator_role_key
- evaluator_role_name

Existing coach submissions should still snapshot as coach.

Player submissions in future Phase 3 should snapshot as player.

Guest evaluator submissions should snapshot as guest evaluator if supported.

4. Existing coach assessment workflow compatibility

Existing staff/coach assessment pages and tests should continue to work.

If current view names still say “coach assessment,” do not rename them in Phase 2.

Do not change templates except small wording if necessary for tests.

5. Self-evaluation blocking service

Add a service-level check.

Do not rely on views only.

This should use `accounts.services.link_service` or a clear account/link helper.

Do not duplicate link lookup logic in views.

6. Permissions remain separate from Account Operations

Do not grant Account Operations access to coaches/players/guest evaluators.

`AccountProfile.role = coach` may allow evaluation submission but must not grant Django staff access.

==================================================
Service Ownership
==================================================

analytics owns:

- evaluation permission helpers
- evaluator role resolution for observations
- observation creation behavior
- role snapshot behavior

accounts owns:

- account roles
- user-player links
- account permissions

players owns:

- canonical player identity

Views remain thin.

==================================================
Do NOT Implement
==================================================

Do NOT implement:
- player-facing evaluation list/form routes
- player “My Evaluations”
- coach evaluation review
- coach import changes
- coach-to-player links
- Coach model
- account merge
- audit logging
- invitations
- emails
- APIs
- JavaScript
- charts
- exports
- new observation types unless absolutely required

==================================================
Testing
==================================================

Add/update tests for:

Permissions:
- anonymous cannot submit
- coach can submit
- player can submit
- staff can submit
- guest evaluator can submit
- parent cannot submit unless existing behavior says otherwise
- self-evaluation is blocked
- user without active self link to target can evaluate target
- inactive self link does not block evaluation unless link_service says otherwise
- AccountProfile.role=coach does not grant Account Operations access

Role snapshots:
- coach submission snapshots coach
- player submission snapshots player
- staff submission snapshots staff
- admin submission snapshots staff/admin according to implemented mapping
- guest evaluator submission snapshots guest evaluator if supported
- role snapshot does not default all users to coach

Regression:
- existing coach assessment creation still works
- existing staff review still works
- existing Analytics command center still works
- existing Account Operations tests still pass
- coach import tests still pass
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
- docs/evaluations/implementation/engineering/evaluation_access_v1.md

Mark Phase 2 implemented only if complete.

Update:
- docs/USER_MANUAL.md

only if the current user-facing behavior changed.

Do not over-document future Phase 3/4/5 features.

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
- services changed
- tests added/updated
- role mapping decisions
- test results
- documentation updates
- implementation decisions
- deviations
- technical debt
- confirmation that only Phase 2 was implemented
- confirmation that Phase 3+ were NOT implemented
```

## Resulting Commit

```text
9376f58 Implement evaluation permission role snapshots
```

## Commit Diff

```diff
commit 9376f5820da18df7807bc31dd357b5cfaf653366
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 8 19:06:51 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 8 19:06:51 2026 -0700

    Implement evaluation permission role snapshots
---
 accounts/tests.py                                  |   8 ++
 analytics/services/observation_service.py          |   8 +-
 analytics/services/permissions.py                  |  62 ++++++++++-
 analytics/services/question_service.py             |   4 +
 analytics/tests.py                                 | 114 +++++++++++++++++++++
 analytics/views.py                                 |  10 +-
 docs/USER_MANUAL.md                                |   8 +-
 .../engineering/evaluation_access_v1.md            |   6 +-
 8 files changed, 210 insertions(+), 10 deletions(-)

diff --git a/accounts/tests.py b/accounts/tests.py
index 56472c3..c6b1b6f 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -179,6 +179,14 @@ class AccountPermissionTests(TestCase):
         self.assertTrue(can_view_account_detail(self.staff, self.user))
         self.assertTrue(can_access_account_operations(self.superuser))
 
+    def test_coach_role_does_not_grant_account_operations_access(self):
+        self.profile.role = AccountRole.COACH
+        self.profile.save(update_fields=["role", "updated_at"])
+
+        self.assertFalse(self.user.is_staff)
+        self.assertFalse(self.user.is_superuser)
+        self.assertFalse(can_access_account_operations(self.user))
+
     def test_privileged_account_management_is_superuser_only(self):
         self.assertFalse(can_manage_privileged_accounts(self.user))
         self.assertFalse(can_manage_privileged_accounts(self.staff))
diff --git a/analytics/services/observation_service.py b/analytics/services/observation_service.py
index 9479b04..3b2dbd6 100644
--- a/analytics/services/observation_service.py
+++ b/analytics/services/observation_service.py
@@ -24,13 +24,13 @@ from analytics.models import (
     ObservationType,
 )
 from analytics.services.question_service import (
-    ROLE_COACH,
     SOURCE_COACH,
     get_active_questions,
     get_coach_assessment_type,
     get_default_coach_assessment_question_set,
     get_question_set_for_cycle,
 )
+from analytics.services.permissions import can_evaluate_player, evaluator_role_for_user
 from players.models import Player
 
 
@@ -129,6 +129,10 @@ def create_observation(
 ) -> Observation:
     """Create an observation with role snapshot and duplicate validation."""
     _validate_question_set_for_type(question_set, observation_type)
+    if evaluator is not None:
+        if not can_evaluate_player(evaluator, player):
+            raise ValidationError("This evaluator cannot evaluate this player.")
+        evaluator_role = evaluator_role or evaluator_role_for_user(evaluator)
     _validate_unique_coach_assessment(
         player=player,
         evaluation_cycle=evaluation_cycle,
@@ -179,7 +183,7 @@ def create_coach_assessment_observation(
     observation_type = get_coach_assessment_type()
     question_set = question_set or get_question_set_for_cycle(evaluation_cycle, observation_type)
     source = source or ObservationSource.objects.get(key=SOURCE_COACH)
-    evaluator_role = evaluator_role or EvaluatorRole.objects.get(key=ROLE_COACH)
+    evaluator_role = evaluator_role or evaluator_role_for_user(evaluator)
     observation = create_observation(
         player=player,
         evaluation_cycle=evaluation_cycle,
diff --git a/analytics/services/permissions.py b/analytics/services/permissions.py
index 3a87749..ea54acb 100644
--- a/analytics/services/permissions.py
+++ b/analytics/services/permissions.py
@@ -1,8 +1,56 @@
-from analytics.models import OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED, OBSERVATION_STATUS_SUBMITTED
+from django.core.exceptions import ValidationError
+
+from accounts.models import AccountRole
+from accounts.services.link_service import is_player_self
+from accounts.services.role_service import role_for_user, role_label
+from analytics.models import OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED, OBSERVATION_STATUS_SUBMITTED, EvaluatorRole
+
+
+ACCOUNT_ROLE_TO_EVALUATOR_ROLE = {
+    AccountRole.COACH: "coach",
+    AccountRole.PLAYER: "player",
+    AccountRole.STAFF: "staff",
+    AccountRole.ADMIN: "admin",
+    AccountRole.GUEST_EVALUATOR: "guest_evaluator",
+}
+
+EVALUATION_SUBMITTER_ROLES = set(ACCOUNT_ROLE_TO_EVALUATOR_ROLE)
 
 
 def can_submit_coach_assessment(user) -> bool:
-    return bool(user and user.is_authenticated)
+    return can_submit_evaluation(user)
+
+
+def can_submit_evaluation(user, target_player=None) -> bool:
+    if not user or not user.is_authenticated:
+        return False
+    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
+        return not (target_player is not None and is_player_self(user, target_player))
+
+    account_role = role_for_user(user)
+    if account_role not in EVALUATION_SUBMITTER_ROLES:
+        return False
+    if target_player is not None and is_player_self(user, target_player):
+        return False
+    return True
+
+
+def can_evaluate_player(user, target_player) -> bool:
+    return bool(target_player and can_submit_evaluation(user, target_player=target_player))
+
+
+def evaluator_role_for_user(user) -> EvaluatorRole:
+    if not user or not user.is_authenticated:
+        raise ValidationError("An authenticated evaluator is required.")
+    account_role = role_for_user(user)
+    evaluator_role_key = ACCOUNT_ROLE_TO_EVALUATOR_ROLE.get(account_role)
+    if not evaluator_role_key:
+        raise ValidationError("This account role cannot submit evaluations.")
+    evaluator_role, _ = EvaluatorRole.objects.get_or_create(
+        key=evaluator_role_key,
+        defaults={"name": role_label(account_role), "is_active": True},
+    )
+    return evaluator_role
 
 
 def can_review_observations(user) -> bool:
@@ -16,6 +64,16 @@ def can_view_observation(user, observation) -> bool:
 
 
 def can_edit_observation(user, observation) -> bool:
+    return can_edit_own_evaluation_draft(user, observation)
+
+
+def can_view_own_evaluation_draft(user, observation) -> bool:
+    if not user or not user.is_authenticated or observation.evaluator_id != user.id:
+        return False
+    return observation.status in {OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED}
+
+
+def can_edit_own_evaluation_draft(user, observation) -> bool:
     if not user or not user.is_authenticated or observation.evaluator_id != user.id:
         return False
     return observation.status in {OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED}
diff --git a/analytics/services/question_service.py b/analytics/services/question_service.py
index 6a69838..431013b 100644
--- a/analytics/services/question_service.py
+++ b/analytics/services/question_service.py
@@ -29,8 +29,10 @@ ROLE_COACH = "coach"
 ROLE_ASSISTANT_COACH = "assistant_coach"
 ROLE_HEAD_COACH = "head_coach"
 ROLE_COORDINATOR = "coordinator"
+ROLE_PLAYER = "player"
 ROLE_STAFF = "staff"
 ROLE_ADMIN = "admin"
+ROLE_GUEST_EVALUATOR = "guest_evaluator"
 
 COACH_ASSESSMENT_RUBRIC = {
     "scale": "1-5",
@@ -56,8 +58,10 @@ DEFAULT_EVALUATOR_ROLES = [
     (ROLE_ASSISTANT_COACH, "Assistant Coach"),
     (ROLE_HEAD_COACH, "Head Coach"),
     (ROLE_COORDINATOR, "Coordinator"),
+    (ROLE_PLAYER, "Player"),
     (ROLE_STAFF, "Staff"),
     (ROLE_ADMIN, "Admin"),
+    (ROLE_GUEST_EVALUATOR, "Guest Evaluator"),
 ]
 
 DEFAULT_COACH_ASSESSMENT_QUESTIONS = [
diff --git a/analytics/tests.py b/analytics/tests.py
index 8644d34..ec98839 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -11,6 +11,9 @@ from django.test import TestCase
 from django.urls import reverse
 from django.utils import timezone
 
+from accounts.models import AccountRole, UserPlayerRelationship
+from accounts.services.link_service import deactivate_link, link_user_to_player
+from accounts.services.profile_service import set_account_role
 from analytics.models import (
     OBSERVATION_STATUS_DRAFT,
     OBSERVATION_STATUS_REOPENED,
@@ -60,6 +63,12 @@ from analytics.services.player_service import (
     parse_player_search_filters,
     search_players,
 )
+from analytics.services.permissions import (
+    can_evaluate_player,
+    can_submit_evaluation,
+    can_view_own_evaluation_draft,
+    evaluator_role_for_user,
+)
 from analytics.services.reporting_service import get_command_center_context
 from analytics.services.draft_service import get_draft_context_for_draft_player, get_draft_contexts_for_draft
 from analytics.services.question_service import (
@@ -67,7 +76,11 @@ from analytics.services.question_service import (
     DEFAULT_COACH_ASSESSMENT_QUESTIONS,
     DEFAULT_EVALUATOR_ROLES,
     DEFAULT_OBSERVATION_SOURCES,
+    ROLE_ADMIN,
     ROLE_COACH,
+    ROLE_GUEST_EVALUATOR,
+    ROLE_PLAYER,
+    ROLE_STAFF,
     SOURCE_COACH,
     ensure_default_coach_assessment_setup,
     get_active_questions,
@@ -431,6 +444,107 @@ class AnalyticsObservationFoundationTests(TestCase):
         self.assertEqual(observation.evaluator_role_name, "Coach")
         self.assertEqual(observation.observation_type_key, OBSERVATION_TYPE_COACH_ASSESSMENT)
 
+    def test_evaluation_submission_permissions_by_role(self):
+        anonymous = None
+        coach = User.objects.create_user(username="rolecoach", password="testpass")
+        player_user = User.objects.create_user(username="roleplayer", password="testpass")
+        staff_user = User.objects.create_user(username="rolestaff", password="testpass", is_staff=True)
+        guest = User.objects.create_user(username="roleguest", password="testpass")
+        parent = User.objects.create_user(username="roleparent", password="testpass")
+        set_account_role(coach, AccountRole.COACH)
+        set_account_role(player_user, AccountRole.PLAYER)
+        set_account_role(staff_user, AccountRole.STAFF)
+        set_account_role(guest, AccountRole.GUEST_EVALUATOR)
+        set_account_role(parent, AccountRole.PARENT)
+
+        self.assertFalse(can_submit_evaluation(anonymous))
+        self.assertTrue(can_submit_evaluation(coach))
+        self.assertTrue(can_submit_evaluation(player_user))
+        self.assertTrue(can_submit_evaluation(staff_user))
+        self.assertTrue(can_submit_evaluation(guest))
+        self.assertFalse(can_submit_evaluation(parent))
+
+    def test_self_evaluation_is_blocked_by_active_self_link_only(self):
+        player_user = User.objects.create_user(username="selflinked", password="testpass")
+        set_account_role(player_user, AccountRole.PLAYER)
+        link = link_user_to_player(player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
+
+        self.assertFalse(can_evaluate_player(player_user, self.player))
+        self.assertTrue(can_evaluate_player(player_user, self.other_player))
+        with self.assertRaises(ValidationError):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=player_user,
+            )
+
+        deactivate_link(link)
+        self.assertTrue(can_evaluate_player(player_user, self.player))
+
+    def test_parent_role_cannot_create_observation(self):
+        parent = User.objects.create_user(username="parent", password="testpass")
+        set_account_role(parent, AccountRole.PARENT)
+
+        with self.assertRaises(ValidationError):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=parent,
+            )
+
+    def test_evaluator_role_for_user_maps_account_roles(self):
+        expectations = [
+            (AccountRole.COACH, ROLE_COACH),
+            (AccountRole.PLAYER, ROLE_PLAYER),
+            (AccountRole.STAFF, ROLE_STAFF),
+            (AccountRole.ADMIN, ROLE_ADMIN),
+            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
+        ]
+        for account_role, evaluator_role_key in expectations:
+            with self.subTest(account_role=account_role):
+                user = User.objects.create_user(username=f"{account_role}-user", password="testpass")
+                set_account_role(user, account_role)
+
+                evaluator_role = evaluator_role_for_user(user)
+
+                self.assertEqual(evaluator_role.key, evaluator_role_key)
+
+    def test_coach_assessment_snapshots_actual_account_role_by_default(self):
+        role_expectations = [
+            (AccountRole.COACH, ROLE_COACH),
+            (AccountRole.PLAYER, ROLE_PLAYER),
+            (AccountRole.STAFF, ROLE_STAFF),
+            (AccountRole.ADMIN, ROLE_ADMIN),
+            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
+        ]
+        for index, (account_role, evaluator_role_key) in enumerate(role_expectations, start=1):
+            with self.subTest(account_role=account_role):
+                evaluator = User.objects.create_user(username=f"snapshot-{account_role}", password="testpass")
+                set_account_role(evaluator, account_role)
+                player = Player.objects.create(first_name=f"Snapshot{index}", last_name="Target", division="13U")
+
+                result = create_coach_assessment_observation(
+                    player=player,
+                    evaluation_cycle=self.cycle,
+                    evaluator=evaluator,
+                )
+
+                self.assertEqual(result.observation.evaluator_role_key, evaluator_role_key)
+                self.assertEqual(result.observation.evaluator_role, EvaluatorRole.objects.get(key=evaluator_role_key))
+
+    def test_draft_view_helpers_are_limited_to_own_drafts(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        self.assertTrue(can_view_own_evaluation_draft(self.evaluator, observation))
+        self.assertFalse(can_view_own_evaluation_draft(self.other_evaluator, observation))
+
+        observation.status = OBSERVATION_STATUS_SUBMITTED
+        observation.save(update_fields=["status", "updated_at"])
+        self.assertFalse(can_view_own_evaluation_draft(self.evaluator, observation))
+
     def test_submitted_observation_sets_submitted_at(self):
         result = create_coach_assessment_observation(
             player=self.player,
diff --git a/analytics/views.py b/analytics/views.py
index 72f3d12..89653c3 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -30,7 +30,13 @@ from analytics.services.player_service import (
 )
 from analytics.services.draft_service import get_draft_contexts_for_player
 from analytics.services.observation_service import get_observation_detail, save_observation_responses, submit_observation
-from analytics.services.permissions import can_edit_observation, can_reopen_observation, can_submit_coach_assessment, can_view_observation
+from analytics.services.permissions import (
+    can_edit_observation,
+    can_evaluate_player,
+    can_reopen_observation,
+    can_submit_coach_assessment,
+    can_view_observation,
+)
 from analytics.services.metrics_service import normalize_cycle_id
 from analytics.services.reporting_service import get_command_center_context
 from analytics.services.timeline_service import get_player_timeline
@@ -296,6 +302,8 @@ class CoachAssessmentEditView(LoginRequiredMixin, TemplateView):
                 messages.error(request, "No active coach assessment cycle is available.")
                 return redirect("analytics:assessment-list")
             player = get_object_or_404(Player, pk=kwargs["player_id"], is_active=True)
+            if not can_evaluate_player(request.user, player):
+                raise PermissionDenied("You cannot evaluate this player.")
             existing = get_existing_coach_assessment(player, cycle, request.user)
             if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
                 return redirect("analytics:assessment-detail", observation_id=existing.pk)
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 66aeed3..d2b8478 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -48,7 +48,7 @@ The platform account role is separate from Django staff access. For example, `Ac
 
 ### Coaches And Evaluators
 
-Any authenticated user can submit a coach assessment for any player they know.
+Authenticated coaches, players, staff, and guest evaluators can submit assessments for players they know.
 
 The system records:
 
@@ -359,12 +359,14 @@ Submitted assessments become part of the player's Analytics record.
 
 ## Who Can Evaluate A Player
 
-Any authenticated user can evaluate any player if they know the player.
+Authenticated coaches, players, staff, and guest evaluators can evaluate any player if they know the player.
 
 The player does not need to be on the evaluator's own team.
 
 This is intentional. It allows coaches, coordinators, staff, and other approved evaluators to contribute observations when they have useful knowledge of a player.
 
+Players cannot evaluate themselves in Evaluation Access V1. Parent accounts do not submit evaluations unless staff gives the user a separate evaluator role.
+
 ## Staff Review Of Assessments
 
 Staff can review submitted observations:
@@ -507,7 +509,7 @@ Yes. Multiple evaluators can submit assessments for the same player.
 
 ### Can I evaluate a player who is not on my team?
 
-Yes, if you are authenticated and know the player well enough to provide a useful evaluation.
+Yes, if your account has an evaluator role and you know the player well enough to provide a useful evaluation. Players cannot evaluate themselves.
 
 ### Is my role recorded when I submit an evaluation?
 
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index 6145e20..6a67350 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -416,8 +416,8 @@ Role snapshot should come from Account Management role metadata:
 - `AccountProfile.role = coach` maps to `EvaluatorRole.coach`;
 - `AccountProfile.role = player` maps to `EvaluatorRole.player`;
 - `AccountProfile.role = staff` maps to `EvaluatorRole.staff`;
-- `AccountProfile.role = admin` should snapshot as `staff` or `admin` only if Analytics defines that evaluator role;
-- `AccountProfile.role = guest_evaluator` maps to `EvaluatorRole.guest_evaluator` if added.
+- `AccountProfile.role = admin` maps to `EvaluatorRole.admin`;
+- `AccountProfile.role = guest_evaluator` maps to `EvaluatorRole.guest_evaluator`.
 
 Recommended implementation:
 
@@ -951,6 +951,8 @@ Deliverables:
 - self-evaluation rule enforced based on Phase 0 decision;
 - regression tests proving existing coach assessment behavior still works.
 
+Status: implemented.
+
 ### Phase 3: Player Evaluation Submission
 
 Purpose:
```
