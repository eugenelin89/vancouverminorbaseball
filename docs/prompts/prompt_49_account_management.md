# Prompt 49 - Account Management

## User Prompt

```text
You are performing Platform V1 Account Operations Phase F.

This is NOT a feature implementation phase.

This is the production hardening and freeze review.

Assume Phases A-E are complete.

Your objective is to determine whether Platform V1 Account Operations is truly production-ready, fix only production-quality issues, then freeze it.

==================================================
Before Doing Anything
==================================================

Read completely:

- AGENTS.md
- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md

Review the entire accounts subsystem.

Pay particular attention to:

accounts/models.py
accounts/views.py
accounts/forms.py
accounts/urls.py
accounts/templates/

accounts/services/

accounts/tests.py

Also inspect interactions with:

players/
analytics/
drafts/
pdp/

Understand the architecture before changing anything.

==================================================
Phase F Philosophy
==================================================

This is a freeze review.

DO NOT add features simply because they are nice ideas.

Only fix problems that would prevent declaring Platform V1 Account Operations production-ready.

Every change should reduce technical debt.

Every change must make the architecture cleaner.

==================================================
Review Categories
==================================================

Perform a complete review of:

1.
Architecture

2.
Service boundaries

3.
Dependency direction

4.
Business rule ownership

5.
Security

6.
Permissions

7.
Authentication

8.
Authorization

9.
Data integrity

10.
Import provenance

11.
Temporary password handling

12.
Username handling

13.
Role handling

14.
Link management

15.
Bulk operations

16.
Error handling

17.
View thinness

18.
Code duplication

19.
Dead code

20.
Naming consistency

21.
Transaction boundaries

22.
Database query efficiency

23.
N+1 queries

24.
Validation placement

25.
Template consistency

26.
URL consistency

27.
Test coverage

28.
Documentation consistency

==================================================
Allowed Changes
==================================================

Allowed:

small architecture cleanup

small security improvements

bug fixes

duplicate code removal

service extraction

better validation placement

better transaction boundaries

test improvements

documentation corrections

performance improvements

consistency improvements

edge-case fixes

==================================================
Not Allowed
==================================================

Do NOT implement:

audit logging

coach import

parent import

account merge

duplicate account resolution

email verification

email invitations

self-service password reset

portal dashboards

REST APIs

JavaScript

new models unless absolutely required

new workflows

new features

new implementation phases

==================================================
Architecture Review Expectations
==================================================

Verify:

views remain orchestration only

services own business rules

players owns player identity

accounts owns authentication

analytics never owns accounts

drafts remain isolated

PDP remains isolated

No subsystem leaks responsibility.

==================================================
Security Review
==================================================

Verify:

temporary passwords

password exposure

must_change_password

inactive users

role escalation

staff permissions

superuser protections

CSRF

POST-only mutations

authorization

==================================================
Performance Review
==================================================

Inspect:

select_related()

prefetch_related()

duplicate queries

count() abuse

repeated lookups

transaction scope

==================================================
Consistency Review
==================================================

Verify consistent:

templates

forms

URLs

service naming

dataclasses

exceptions

messages

button layout

confirmation pages

==================================================
Testing Review
==================================================

Look for:

missing regressions

edge cases

permission gaps

negative tests

error handling

404 behavior

validation behavior

bulk operation failures

==================================================
Documentation Review
==================================================

Ensure:

ARCHITECTURE.md

V1_SUMMARY.md

engineering docs

all reflect the final implementation.

Do not rewrite documentation.

Only correct inconsistencies.

==================================================
Freeze Criteria
==================================================

Only declare frozen if ALL are true:

architecture is consistent

service ownership is clean

security acceptable

permissions acceptable

no known architecture debt

no significant duplication

tests comprehensive

documentation current

working tree clean

==================================================
Implementation Rules
==================================================

If you find no significant issue:

DO NOT manufacture refactoring.

Leave good code alone.

If you find issues:

Fix only what is necessary.

Do not expand scope.

==================================================
Verification
==================================================

Run:

python manage.py check

python manage.py makemigrations accounts --check

python manage.py test accounts

python manage.py test analytics

python manage.py test players

python manage.py test drafts

python manage.py test pdp

python manage.py test

git diff --check

==================================================
Final Report
==================================================

Produce:

1.
Executive assessment

Release readiness score (/10)

2.
Architecture findings

3.
Security findings

4.
Performance findings

5.
Documentation findings

6.
Issues fixed

7.
Files modified

8.
Tests executed

9.
Remaining deferred work

10.
Explicit freeze recommendation

If no blocking issues remain, state:

Platform V1 Account Operations is COMPLETE and FROZEN.

Otherwise state exactly what blocks the freeze.

Do not begin any future version work.
```

## App / Subsystem

Account Management

## Work Commit

`ab8210d Freeze account operations Phase F`

## Work Commit Diff

```diff
commit ab8210d676c020d775c408b25709f6dceadb5d91
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 8 11:48:11 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 8 11:48:11 2026 -0700

    Freeze account operations Phase F
---
 accounts/services/account_operations_service.py    | 27 +++++++-
 accounts/tests.py                                  | 81 +++++++++++++++++++++-
 docs/ARCHITECTURE.md                               |  6 +-
 docs/account_management/V1_SUMMARY.md              | 14 ++--
 .../engineering/platform_v1_account_operations.md  | 10 +--
 5 files changed, 118 insertions(+), 20 deletions(-)

diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
index f7cbb90..bbd5aca 100644
--- a/accounts/services/account_operations_service.py
+++ b/accounts/services/account_operations_service.py
@@ -25,6 +25,7 @@ from accounts.services.password_service import (
     set_random_temporary_password,
     set_temporary_password,
 )
+from accounts.services.permissions import can_manage_accounts, can_manage_privileged_accounts
 from accounts.services.profile_service import get_or_create_account_profile, set_account_role
 from accounts.services.provisioning_service import STATUS_CREATED, provision_player_account
 from accounts.services.role_service import role_label
@@ -151,15 +152,26 @@ class BulkOperationResult:
 
 
 def _validate_actor_can_create_role(actor, role: str) -> None:
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can manage accounts.")
     if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
         raise ValidationError("Only superusers can create admin accounts.")
 
 
 def _validate_actor_can_assign_role(actor, role: str) -> None:
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can manage accounts.")
     if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
         raise ValidationError("Only superusers can assign admin role.")
 
 
+def _validate_actor_can_manage_target(actor, user: User) -> None:
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can manage accounts.")
+    if (user.is_staff or user.is_superuser) and not can_manage_privileged_accounts(actor):
+        raise ValidationError("Only superusers can manage staff or superuser accounts.")
+
+
 def _validate_account_deactivation_allowed(actor, user: User) -> None:
     if actor and getattr(actor, "id", None) == user.id:
         raise ValidationError("You cannot deactivate your own account.")
@@ -365,12 +377,13 @@ def update_account(
     """Update lifecycle and profile fields for an existing account."""
     _validate_actor_can_assign_role(actor, role)
     user = _get_user_for_update(user_id)
+    if user.is_active and not bool(is_active):
+        _validate_account_deactivation_allowed(actor, user)
+    _validate_actor_can_manage_target(actor, user)
     user.username = validate_available_username_for_user(user, username)
     user.first_name = str(first_name or "").strip()
     user.last_name = str(last_name or "").strip()
     user.email = _validate_email_available_for_user(user, email)
-    if user.is_active and not bool(is_active):
-        _validate_account_deactivation_allowed(actor, user)
     user.is_active = bool(is_active)
     user.save(update_fields=["username", "first_name", "last_name", "email", "is_active"])
     set_account_role(user, role, actor=actor)
@@ -382,6 +395,7 @@ def update_account(
 def activate_account(*, actor, user_id: int) -> UpdatedAccountResult:
     """Activate an existing account without changing profile or link history."""
     user = _get_user_for_update(user_id)
+    _validate_actor_can_manage_target(actor, user)
     if not user.is_active:
         user.is_active = True
         user.save(update_fields=["is_active"])
@@ -394,6 +408,7 @@ def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
     user = _get_user_for_update(user_id)
     if user.is_active:
         _validate_account_deactivation_allowed(actor, user)
+        _validate_actor_can_manage_target(actor, user)
         user.is_active = False
         user.save(update_fields=["is_active"])
     return _updated_account_result(user)
@@ -410,6 +425,7 @@ def create_user_player_link(
 ) -> UpdatedLinkResult:
     """Create an active user/player link through the account operations workflow."""
     user = _get_user_for_update(user_id)
+    _validate_actor_can_manage_target(actor, user)
     validate_no_active_relationship_conflict(user, player, relationship)
     link = link_user_to_player(user, player, relationship=relationship, is_primary=is_primary)
     return _updated_link_result(link)
@@ -419,6 +435,7 @@ def create_user_player_link(
 def deactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
     """Deactivate a user/player link without deleting its history."""
     user = _get_user_for_update(user_id)
+    _validate_actor_can_manage_target(actor, user)
     link = _get_link_for_user(user, link_id)
     return _updated_link_result(deactivate_link(link, actor=actor))
 
@@ -427,6 +444,7 @@ def deactivate_user_player_link(*, actor, user_id: int, link_id: int) -> Updated
 def reactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
     """Reactivate an existing inactive user/player link when constraints allow it."""
     user = _get_user_for_update(user_id)
+    _validate_actor_can_manage_target(actor, user)
     link = _get_link_for_user(user, link_id)
     return _updated_link_result(activate_link(link, actor=actor))
 
@@ -435,6 +453,7 @@ def reactivate_user_player_link(*, actor, user_id: int, link_id: int) -> Updated
 def set_primary_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
     """Set an existing self link as the active primary player link."""
     user = _get_user_for_update(user_id)
+    _validate_actor_can_manage_target(actor, user)
     link = _get_link_for_user(user, link_id)
     return _updated_link_result(set_primary_self_link(link, actor=actor))
 
@@ -443,6 +462,7 @@ def set_primary_user_player_link(*, actor, user_id: int, link_id: int) -> Update
 def reset_account_password(*, actor, user_id: int) -> PasswordResetResult:
     """Reset an existing account password and require password change on next login."""
     user = _get_user_for_update(user_id)
+    _validate_actor_can_manage_target(actor, user)
     player = _player_for_password_reset(user)
     if player:
         temporary_password = generate_birthdate_password(player)
@@ -458,6 +478,7 @@ def reset_account_password(*, actor, user_id: int) -> PasswordResetResult:
 def set_account_password_change_required(*, actor, user_id: int, required: bool) -> UpdatedAccountResult:
     """Set the password-change requirement for an existing account."""
     user = _get_user_for_update(user_id)
+    _validate_actor_can_manage_target(actor, user)
     mark_password_change_required(user, bool(required))
     user.refresh_from_db()
     return _updated_account_result(user)
@@ -494,6 +515,8 @@ def _validation_message(exc: ValidationError) -> str:
 
 def bulk_account_operation(*, actor, action: str, user_ids) -> BulkOperationResult:
     """Apply a safe account operation to selected users and collect per-account failures."""
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can manage accounts.")
     if action not in BULK_ACCOUNT_ACTIONS:
         raise ValidationError("Unsupported bulk action.")
 
diff --git a/accounts/tests.py b/accounts/tests.py
index 0904486..bba2ce8 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -497,6 +497,53 @@ class AccountOperationsServiceTests(TestCase):
         self.assertFalse(self.coach.is_staff)
         self.assertFalse(self.coach.is_superuser)
 
+    def test_account_operation_services_require_staff_actor(self):
+        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
+            create_account_only(actor=self.coach, username="not.allowed", role=AccountRole.COACH)
+        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
+            create_player_account(actor=self.coach, player=self.player)
+        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
+            update_account(
+                actor=self.coach,
+                user_id=self.player_user.id,
+                username="alex.player",
+                role=AccountRole.PLAYER,
+            )
+        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
+            reset_account_password(actor=self.coach, user_id=self.player_user.id)
+        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
+            bulk_account_operation(actor=self.coach, action="activate", user_ids=[self.player_user.id])
+
+    def test_staff_cannot_mutate_staff_or_superuser_accounts(self):
+        other_staff = User.objects.create_user(username="other.staff", password="testpass", is_staff=True)
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+        superuser_actor = User.objects.create_superuser(username="ops.admin2", password="testpass")
+
+        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
+            update_account(
+                actor=self.staff,
+                user_id=other_staff.id,
+                username="other.staff",
+                role=AccountRole.STAFF,
+            )
+        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
+            activate_account(actor=self.staff, user_id=other_staff.id)
+        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
+            deactivate_account(actor=self.staff, user_id=superuser.id)
+        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
+            reset_account_password(actor=self.staff, user_id=superuser.id)
+        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
+            create_user_player_link(
+                actor=self.staff,
+                user_id=other_staff.id,
+                player=self.player,
+                relationship=UserPlayerRelationship.STAFF,
+            )
+
+        result = reset_account_password(actor=superuser_actor, user_id=other_staff.id)
+        other_staff.refresh_from_db()
+        self.assertTrue(other_staff.check_password(result.temporary_password))
+
     def test_activate_and_deactivate_account_preserve_profile_and_links(self):
         deactivate_result = deactivate_account(actor=self.staff, user_id=self.player_user.id)
         self.player_user.refresh_from_db()
@@ -543,11 +590,12 @@ class AccountOperationsServiceTests(TestCase):
         superuser.refresh_from_db()
         self.assertTrue(superuser.is_active)
 
-    def test_deactivate_account_allows_superuser_when_another_active_superuser_exists(self):
+    def test_deactivate_account_allows_superuser_actor_when_another_active_superuser_exists(self):
         superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+        actor = User.objects.create_superuser(username="ops.actor", password="testpass")
         User.objects.create_superuser(username="ops.admin2", password="testpass")
 
-        result = deactivate_account(actor=self.staff, user_id=superuser.id)
+        result = deactivate_account(actor=actor, user_id=superuser.id)
 
         self.assertFalse(result.is_active)
 
@@ -1787,6 +1835,22 @@ class AccountOperationsViewTests(TestCase):
         self.coach.refresh_from_db()
         self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
 
+    def test_staff_user_edit_rejects_staff_or_superuser_target(self):
+        other_staff = User.objects.create_user(username="other.staff", password="testpass", is_staff=True)
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": other_staff.id}),
+            {
+                "username": "other.staff",
+                "role": AccountRole.STAFF,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Only superusers can manage staff or superuser accounts")
+
     def test_user_links_requires_staff(self):
         self.client.force_login(self.regular)
 
@@ -1952,6 +2016,19 @@ class AccountOperationsViewTests(TestCase):
 
         self.assertEqual(response.status_code, 404)
 
+    def test_staff_password_reset_rejects_staff_or_superuser_target(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-password-reset", kwargs={"user_id": self.superuser.id}),
+            {"confirm": "on"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Only superusers can manage staff or superuser accounts")
+        self.superuser.refresh_from_db()
+        self.assertTrue(self.superuser.check_password("testpass"))
+
     def test_profile_page_links_staff_to_account_operations(self):
         self.client.force_login(self.staff)
 
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index ed01946..359bfb4 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -156,7 +156,7 @@ What it must not own:
 
 Current status:
 
-Core V1 is complete. Platform V1 Account Operations is implemented through Phase E and is awaiting Phase F production hardening/freeze review.
+V1 complete and frozen, including Platform V1 Account Operations Phase F production hardening/freeze review.
 
 Documentation:
 
@@ -271,7 +271,7 @@ Dependency guidance:
 | --- | --- | --- |
 | Players | V1 | Complete |
 | Analytics | V1 | Complete |
-| Account Management | V1 | Core complete; Account Operations Phase F pending |
+| Account Management | V1 | Complete / Frozen |
 | Drafts | Active | Active development |
 | PDP | Legacy | Transitionary |
 | LeagueHub | Planned | Planned |
@@ -285,7 +285,7 @@ The platform currently has:
 - production-ready player import and matching workflow
 - production-ready Analytics V1 workflow
 - production-ready Account Management V1 foundation
-- staff-facing Account Operations implemented through Phase E
+- production-ready staff-facing Account Operations
 - account provisioning from player imports
 - forced password-change account flow
 - staff-only Analytics command center and reporting tables
diff --git a/docs/account_management/V1_SUMMARY.md b/docs/account_management/V1_SUMMARY.md
index 12bb58e..d45e225 100644
--- a/docs/account_management/V1_SUMMARY.md
+++ b/docs/account_management/V1_SUMMARY.md
@@ -211,7 +211,7 @@ Authentication behavior:
 
 ## Platform V1 Account Operations
 
-Platform V1 Account Operations extends Account Management V1 with staff-facing production operations. These workflows are implemented through Phase E and are ready for Phase F production hardening/freeze review.
+Platform V1 Account Operations extends Account Management V1 with staff-facing production operations. These workflows are implemented through Phase F and are frozen for Platform V1.
 
 Implemented sequence:
 
@@ -220,7 +220,7 @@ Implemented sequence:
 - Phase C - Account Lifecycle and Link Management.
 - Phase D - Operational Password Reset.
 - Phase E - Bulk Operations.
-- Phase F - Production Hardening / Freeze. This is pending and is not a feature phase.
+- Phase F - Production Hardening / Freeze. This was a freeze review, not a feature phase.
 
 Implemented routes:
 
@@ -282,7 +282,6 @@ Provenance rules:
 
 Deferred from Platform V1 Account Operations:
 
-- Phase F production hardening/freeze review;
 - audit logging;
 - account merge;
 - duplicate account resolution;
@@ -597,7 +596,7 @@ Coverage includes:
 - PDP coexistence
 - ownership-boundary regressions
 
-Every core V1 phase concluded with implementation review and regression testing. Platform V1 Account Operations has also been implemented through Phase E and is awaiting Phase F production hardening/freeze review.
+Every core V1 phase concluded with implementation review and regression testing. Platform V1 Account Operations has also completed Phase F production hardening/freeze review.
 
 ## Lessons Learned
 
@@ -627,12 +626,11 @@ Account Management V1
 Status:
 
 ```text
-CORE V1 COMPLETE
-PLATFORM V1 ACCOUNT OPERATIONS PHASES A-E COMPLETE
-PHASE F PRODUCTION HARDENING / FREEZE PENDING
+COMPLETE
+FROZEN
 ```
 
-Account Management V1 core account infrastructure is complete. Platform V1 Account Operations is implemented through Phase E and should receive a Phase F production hardening/freeze review before being declared frozen.
+Account Management V1 core account infrastructure is complete. Platform V1 Account Operations is implemented through Phase F and is frozen for Platform V1.
 
 V1 should remain stable. Future work should be added through a new version or explicit implementation phase.
 
diff --git a/docs/account_management/implementation/engineering/platform_v1_account_operations.md b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
index 2872dda..498162f 100644
--- a/docs/account_management/implementation/engineering/platform_v1_account_operations.md
+++ b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
@@ -643,7 +643,7 @@ Review areas:
 - documentation finalization;
 - freeze declaration.
 
-Status: pending.
+Status: complete. Platform V1 Account Operations is frozen.
 
 ### Explicitly Deferred: Bulk Coach Import
 
@@ -664,7 +664,7 @@ That future plan should define CSV format, matching rules, duplicate detection,
 - Username changes could create collisions or make staff unable to find accounts.
 - Imported player accounts may be active immediately, so staff need clear visibility into which accounts still require password changes.
 - Bulk operations could cause large accidental access changes if not carefully confirmed and permission-guarded.
-- Phase F could expose production-readiness defects that require targeted cleanup before freeze.
+- Future account-operation changes after freeze should use a new version or explicit approved implementation phase.
 - Without audit logging, staff may have limited historical visibility into who performed account changes. Audit logging is out of scope for this plan unless separately approved.
 
 ## 11. Open Questions
@@ -678,15 +678,15 @@ That future plan should define CSV format, matching rules, duplicate detection,
 - Should changing `User.is_staff` be included in this operational UI, or remain in Django admin for Platform V1?
 - Should account merge and duplicate account resolution be planned as a later Platform V1 operations extension or deferred to a future platform version?
 - Should account-operation changes eventually produce audit records? This plan treats audit logging as out of scope, but production operations may require it later.
-- What exact checklist should define the Phase F freeze declaration?
+- What future version should introduce audit logging, if production operations require it?
 
 ## Definition Of Done
 
-This roadmap is ready for Phase F freeze review when:
+This roadmap is complete when:
 
 - Phases A-E are implemented and tested;
 - permission rules are confirmed;
 - password reset behavior is confirmed;
 - role/staff/superuser boundaries are confirmed;
 - documentation reflects the implemented state;
-- Phase F can proceed without introducing new feature scope.
+- Phase F production hardening/freeze review is complete.
```
