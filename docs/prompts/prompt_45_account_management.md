# Prompt 45 - Account Management

## User Prompt

```text
You are reviewing the completed implementation of Platform V1 Account Operations Phase C.

This is a REVIEW/FIX pass only.

Do NOT implement any Phase D, E, or F work.

==================================================
Goal
==================================================

Review the existing Phase C implementation for:

- architecture
- correctness
- edge cases
- security
- permissions
- service boundaries
- regression risk

Fix only genuine issues.

Do NOT add features.

==================================================
Read
==================================================

Read:

- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md
- AGENTS.md

Review the existing implementation in:

accounts/
players/
analytics/

Pay particular attention to:

accounts/services/account_operations_service.py
accounts/services/link_service.py
accounts/services/profile_service.py
accounts/services/username_service.py
accounts/services/permissions.py
accounts/views.py
accounts/forms.py
accounts/templates/

==================================================
Review Checklist
==================================================

Verify that:

Views remain thin.

Business logic lives in services.

No duplicated username normalization exists.

No duplicated link logic exists.

No duplicated permission logic exists.

All ValidationErrors are converted into user-friendly errors.

Transactions are correctly applied.

Service ownership remains correct.

No architecture violations were introduced.

==================================================
Specifically Review
==================================================

1.

Account activation/deactivation.

Verify no unintended side effects.

Confirm profile, links, provenance, and history remain untouched.

2.

Username updates.

Verify username normalization occurs in exactly one place.

Ensure updates correctly allow the existing username while rejecting duplicates.

3.

Role updates.

Verify:

- only superusers may assign Admin
- AccountProfile.role never mutates User.is_staff
- AccountProfile.role never mutates User.is_superuser

4.

Link management.

Verify:

- duplicate active links cannot occur
- inactive links reactivate correctly
- historical links are preserved
- no duplicate link logic exists outside link_service

5.

Primary self links.

Verify:

exactly one active primary SELF link per user

exactly one active primary SELF link per player

Only SELF may be primary.

Verify race-condition safety.

6.

Permissions.

Ensure regular users cannot access operational pages.

Ensure staff restrictions remain correct.

==================================================
Look For Edge Cases
==================================================

Examples:

attempting to deactivate yourself

attempting to deactivate the last superuser

editing account with unchanged username

editing email to existing email

reactivating conflicting links

setting inactive link as primary

double submission

invalid IDs

missing objects

invalid POST actions

==================================================
Do NOT Add
==================================================

No password reset

No invitations

No email

No bulk operations

No merge

No duplicate resolution

No audit logging

No imports

No player editing

No player creation

No JavaScript

No API endpoints

No UI redesign

==================================================
Testing
==================================================

Add regression tests only if they expose a genuine issue.

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
Self Review
==================================================

Confirm:

Review fixes only.

No new features.

No Phase D work.

Architecture remains clean.

Views remain orchestration only.

No service duplication.

No provenance regression.

No migration added.

project_flat_file.txt updated only if necessary.

==================================================
Final Report
==================================================

Report:

- issues found
- fixes applied
- files modified
- additional regression tests added
- test results
- architectural observations
- remaining technical debt
- confirmation that this was a review/fix pass only
```

## Implementation Commit Diff

```diff
diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
index e9361e5..6090b8c 100644
--- a/accounts/services/account_operations_service.py
+++ b/accounts/services/account_operations_service.py
@@ -17,6 +17,7 @@ from accounts.services.link_service import (
     deactivate_link,
     link_user_to_player,
     set_primary_self_link,
+    validate_no_active_relationship_conflict,
 )
 from accounts.services.password_service import (
     generate_birthdate_password,
@@ -125,6 +126,15 @@ def _validate_actor_can_assign_role(actor, role: str) -> None:
         raise ValidationError("Only superusers can assign admin role.")
 
 
+def _validate_account_deactivation_allowed(actor, user: User) -> None:
+    if actor and getattr(actor, "id", None) == user.id:
+        raise ValidationError("You cannot deactivate your own account.")
+    if user.is_superuser and user.is_active:
+        other_active_superusers = User.objects.filter(is_superuser=True, is_active=True).exclude(pk=user.pk).exists()
+        if not other_active_superusers:
+            raise ValidationError("You cannot deactivate the last active superuser account.")
+
+
 def _validate_email_available(email: str) -> str:
     normalized = normalize_email(email)
     if normalized and find_existing_email_user(normalized):
@@ -315,6 +325,8 @@ def update_account(
     user.first_name = str(first_name or "").strip()
     user.last_name = str(last_name or "").strip()
     user.email = _validate_email_available_for_user(user, email)
+    if user.is_active and not bool(is_active):
+        _validate_account_deactivation_allowed(actor, user)
     user.is_active = bool(is_active)
     user.save(update_fields=["username", "first_name", "last_name", "email", "is_active"])
     set_account_role(user, role, actor=actor)
@@ -337,6 +349,7 @@ def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
     """Deactivate an existing account without deleting account data or links."""
     user = _get_user_for_update(user_id)
     if user.is_active:
+        _validate_account_deactivation_allowed(actor, user)
         user.is_active = False
         user.save(update_fields=["is_active"])
     return _updated_account_result(user)
@@ -353,8 +366,7 @@ def create_user_player_link(
 ) -> UpdatedLinkResult:
     """Create an active user/player link through the account operations workflow."""
     user = _get_user_for_update(user_id)
-    if UserPlayerLink.objects.filter(user=user, player=player, relationship=relationship, is_active=True).exists():
-        raise ValidationError("An active link already exists for this user, player, and relationship.")
+    validate_no_active_relationship_conflict(user, player, relationship)
     link = link_user_to_player(user, player, relationship=relationship, is_primary=is_primary)
     return _updated_link_result(link)
 
diff --git a/accounts/services/link_service.py b/accounts/services/link_service.py
index a03f13f..a2f6c19 100644
--- a/accounts/services/link_service.py
+++ b/accounts/services/link_service.py
@@ -59,19 +59,27 @@ def _validate_primary_self_conflicts(user, player, exclude_link_id=None) -> None
         raise ValidationError("This player already has an active primary self user link.")
 
 
-def _validate_active_relationship_conflict(link) -> None:
+def validate_no_active_relationship_conflict(user, player, relationship: str, exclude_link_id=None) -> None:
+    """Validate that no active link exists for this user, player, and relationship."""
+    _validate_user(user)
+    _validate_player(player)
+    relationship = _validate_relationship(relationship)
     conflicts = UserPlayerLink.objects.filter(
-        user=link.user,
-        player=link.player,
-        relationship=link.relationship,
+        user=user,
+        player=player,
+        relationship=relationship,
         is_active=True,
     )
-    if link.pk:
-        conflicts = conflicts.exclude(pk=link.pk)
+    if exclude_link_id:
+        conflicts = conflicts.exclude(pk=exclude_link_id)
     if conflicts.exists():
         raise ValidationError("An active link already exists for this user, player, and relationship.")
 
 
+def _validate_active_relationship_conflict(link) -> None:
+    validate_no_active_relationship_conflict(link.user, link.player, link.relationship, exclude_link_id=link.pk)
+
+
 @transaction.atomic
 def link_user_to_player(
     user,
diff --git a/accounts/tests.py b/accounts/tests.py
index ee63b08..6a3aaf4 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -512,6 +512,43 @@ class AccountOperationsServiceTests(TestCase):
         self.assertTrue(self.player_user.is_active)
         self.assertTrue(UserPlayerLink.objects.get(pk=link.pk).is_active)
 
+    def test_deactivate_account_rejects_self_deactivation(self):
+        with self.assertRaises(ValidationError):
+            deactivate_account(actor=self.staff, user_id=self.staff.id)
+
+        self.staff.refresh_from_db()
+        self.assertTrue(self.staff.is_active)
+
+    def test_update_account_rejects_self_deactivation(self):
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.staff.id,
+                username="staff",
+                role=AccountRole.STAFF,
+                is_active=False,
+            )
+
+        self.staff.refresh_from_db()
+        self.assertTrue(self.staff.is_active)
+
+    def test_deactivate_account_rejects_last_active_superuser(self):
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+
+        with self.assertRaises(ValidationError):
+            deactivate_account(actor=self.staff, user_id=superuser.id)
+
+        superuser.refresh_from_db()
+        self.assertTrue(superuser.is_active)
+
+    def test_deactivate_account_allows_superuser_when_another_active_superuser_exists(self):
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+        User.objects.create_superuser(username="ops.admin2", password="testpass")
+
+        result = deactivate_account(actor=self.staff, user_id=superuser.id)
+
+        self.assertFalse(result.is_active)
+
     def test_account_operations_manage_player_links_through_services(self):
         link_result = create_user_player_link(
             actor=self.staff,
@@ -1414,6 +1451,13 @@ class AccountOperationsViewTests(TestCase):
 
         self.assertEqual(response.status_code, 403)
 
+    def test_user_detail_missing_account_returns_404(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": 999999}))
+
+        self.assertEqual(response.status_code, 404)
+
     def test_user_detail_renders_profile_and_linked_players(self):
         self.client.force_login(self.staff)
 
@@ -1566,6 +1610,28 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "An active link already exists")
 
+    def test_links_page_handles_invalid_link_id_as_form_error(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "deactivate", "link_id": "999999"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player link not found")
+
+    def test_links_page_handles_unknown_action_as_form_error(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "unsupported", "link_id": "1"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Unsupported link action")
+
     def test_profile_page_links_staff_to_account_operations(self):
         self.client.force_login(self.staff)
 
diff --git a/accounts/views.py b/accounts/views.py
index ae34d9d..8e9ace4 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -2,7 +2,8 @@ from django.contrib import messages
 from django.contrib.auth import update_session_auth_hash
 from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
 from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
-from django.core.exceptions import PermissionDenied, ValidationError
+from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
+from django.http import Http404
 from django.shortcuts import redirect
 from django.views.generic import FormView, TemplateView
 
@@ -42,6 +43,13 @@ class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixi
         return can_view_account_operations_dashboard(self.request.user)
 
 
+def _account_detail_or_404(user_id):
+    try:
+        return get_account_detail(user_id)
+    except ObjectDoesNotExist as exc:
+        raise Http404("Account not found.") from exc
+
+
 class AccountLoginView(LoginView):
     template_name = "accounts/login.html"
 
@@ -131,7 +139,7 @@ class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
     template_name = "accounts/user_detail.html"
 
     def dispatch(self, request, *args, **kwargs):
-        self.account_detail = get_account_detail(kwargs["user_id"])
+        self.account_detail = _account_detail_or_404(kwargs["user_id"])
         if not can_view_account_detail(request.user, self.account_detail.user):
             raise PermissionDenied
         return super().dispatch(request, *args, **kwargs)
@@ -149,7 +157,7 @@ class AccountUserEditView(AccountOperationsStaffRequiredMixin, FormView):
     form_class = AccountEditForm
 
     def dispatch(self, request, *args, **kwargs):
-        self.account_detail = get_account_detail(kwargs["user_id"])
+        self.account_detail = _account_detail_or_404(kwargs["user_id"])
         if not can_view_account_detail(request.user, self.account_detail.user):
             raise PermissionDenied
         return super().dispatch(request, *args, **kwargs)
@@ -195,7 +203,7 @@ class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
     form_class = UserPlayerLinkForm
 
     def dispatch(self, request, *args, **kwargs):
-        self.account_detail = get_account_detail(kwargs["user_id"])
+        self.account_detail = _account_detail_or_404(kwargs["user_id"])
         if not can_view_account_detail(request.user, self.account_detail.user):
             raise PermissionDenied
         return super().dispatch(request, *args, **kwargs)
@@ -231,7 +239,8 @@ class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
         if action == "create":
             return super().post(request, *args, **kwargs)
 
-        form = self.form_class()
+        form = self.form_class(request.POST)
+        form.is_valid()
         try:
             link_id = int(request.POST.get("link_id", ""))
             if action == "deactivate":
@@ -245,6 +254,9 @@ class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
                 messages.success(request, "Primary self link updated.")
             else:
                 raise ValidationError("Unsupported link action.")
+        except ObjectDoesNotExist:
+            form.add_error(None, "Player link not found.")
+            return self.form_invalid(form)
         except (TypeError, ValueError, ValidationError) as exc:
             form.add_error(None, exc)
             return self.form_invalid(form)
diff --git a/project_flat_file.txt b/project_flat_file.txt
index 9015269..b033482 100644
--- a/project_flat_file.txt
+++ b/project_flat_file.txt
@@ -842,6 +842,7 @@ from accounts.services.link_service import (
     deactivate_link,
     link_user_to_player,
     set_primary_self_link,
+    validate_no_active_relationship_conflict,
 )
 from accounts.services.password_service import (
     generate_birthdate_password,
@@ -950,6 +951,15 @@ def _validate_actor_can_assign_role(actor, role: str) -> None:
         raise ValidationError("Only superusers can assign admin role.")
 
 
+def _validate_account_deactivation_allowed(actor, user: User) -> None:
+    if actor and getattr(actor, "id", None) == user.id:
+        raise ValidationError("You cannot deactivate your own account.")
+    if user.is_superuser and user.is_active:
+        other_active_superusers = User.objects.filter(is_superuser=True, is_active=True).exclude(pk=user.pk).exists()
+        if not other_active_superusers:
+            raise ValidationError("You cannot deactivate the last active superuser account.")
+
+
 def _validate_email_available(email: str) -> str:
     normalized = normalize_email(email)
     if normalized and find_existing_email_user(normalized):
@@ -1140,6 +1150,8 @@ def update_account(
     user.first_name = str(first_name or "").strip()
     user.last_name = str(last_name or "").strip()
     user.email = _validate_email_available_for_user(user, email)
+    if user.is_active and not bool(is_active):
+        _validate_account_deactivation_allowed(actor, user)
     user.is_active = bool(is_active)
     user.save(update_fields=["username", "first_name", "last_name", "email", "is_active"])
     set_account_role(user, role, actor=actor)
@@ -1162,6 +1174,7 @@ def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
     """Deactivate an existing account without deleting account data or links."""
     user = _get_user_for_update(user_id)
     if user.is_active:
+        _validate_account_deactivation_allowed(actor, user)
         user.is_active = False
         user.save(update_fields=["is_active"])
     return _updated_account_result(user)
@@ -1178,8 +1191,7 @@ def create_user_player_link(
 ) -> UpdatedLinkResult:
     """Create an active user/player link through the account operations workflow."""
     user = _get_user_for_update(user_id)
-    if UserPlayerLink.objects.filter(user=user, player=player, relationship=relationship, is_active=True).exists():
-        raise ValidationError("An active link already exists for this user, player, and relationship.")
+    validate_no_active_relationship_conflict(user, player, relationship)
     link = link_user_to_player(user, player, relationship=relationship, is_primary=is_primary)
     return _updated_link_result(link)
 
@@ -1554,19 +1566,27 @@ def _validate_primary_self_conflicts(user, player, exclude_link_id=None) -> None
         raise ValidationError("This player already has an active primary self user link.")
 
 
-def _validate_active_relationship_conflict(link) -> None:
+def validate_no_active_relationship_conflict(user, player, relationship: str, exclude_link_id=None) -> None:
+    """Validate that no active link exists for this user, player, and relationship."""
+    _validate_user(user)
+    _validate_player(player)
+    relationship = _validate_relationship(relationship)
     conflicts = UserPlayerLink.objects.filter(
-        user=link.user,
-        player=link.player,
-        relationship=link.relationship,
+        user=user,
+        player=player,
+        relationship=relationship,
         is_active=True,
     )
-    if link.pk:
-        conflicts = conflicts.exclude(pk=link.pk)
+    if exclude_link_id:
+        conflicts = conflicts.exclude(pk=exclude_link_id)
     if conflicts.exists():
         raise ValidationError("An active link already exists for this user, player, and relationship.")
 
 
+def _validate_active_relationship_conflict(link) -> None:
+    validate_no_active_relationship_conflict(link.user, link.player, link.relationship, exclude_link_id=link.pk)
+
+
 @transaction.atomic
 def link_user_to_player(
     user,
@@ -3568,6 +3588,43 @@ class AccountOperationsServiceTests(TestCase):
         self.assertTrue(self.player_user.is_active)
         self.assertTrue(UserPlayerLink.objects.get(pk=link.pk).is_active)
 
+    def test_deactivate_account_rejects_self_deactivation(self):
+        with self.assertRaises(ValidationError):
+            deactivate_account(actor=self.staff, user_id=self.staff.id)
+
+        self.staff.refresh_from_db()
+        self.assertTrue(self.staff.is_active)
+
+    def test_update_account_rejects_self_deactivation(self):
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.staff.id,
+                username="staff",
+                role=AccountRole.STAFF,
+                is_active=False,
+            )
+
+        self.staff.refresh_from_db()
+        self.assertTrue(self.staff.is_active)
+
+    def test_deactivate_account_rejects_last_active_superuser(self):
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+
+        with self.assertRaises(ValidationError):
+            deactivate_account(actor=self.staff, user_id=superuser.id)
+
+        superuser.refresh_from_db()
+        self.assertTrue(superuser.is_active)
+
+    def test_deactivate_account_allows_superuser_when_another_active_superuser_exists(self):
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+        User.objects.create_superuser(username="ops.admin2", password="testpass")
+
+        result = deactivate_account(actor=self.staff, user_id=superuser.id)
+
+        self.assertFalse(result.is_active)
+
     def test_account_operations_manage_player_links_through_services(self):
         link_result = create_user_player_link(
             actor=self.staff,
@@ -4470,6 +4527,13 @@ class AccountOperationsViewTests(TestCase):
 
         self.assertEqual(response.status_code, 403)
 
+    def test_user_detail_missing_account_returns_404(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": 999999}))
+
+        self.assertEqual(response.status_code, 404)
+
     def test_user_detail_renders_profile_and_linked_players(self):
         self.client.force_login(self.staff)
 
@@ -4622,6 +4686,28 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "An active link already exists")
 
+    def test_links_page_handles_invalid_link_id_as_form_error(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "deactivate", "link_id": "999999"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player link not found")
+
+    def test_links_page_handles_unknown_action_as_form_error(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "unsupported", "link_id": "1"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Unsupported link action")
+
     def test_profile_page_links_staff_to_account_operations(self):
         self.client.force_login(self.staff)
 
@@ -4903,7 +4989,8 @@ from django.contrib import messages
 from django.contrib.auth import update_session_auth_hash
 from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
 from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
-from django.core.exceptions import PermissionDenied, ValidationError
+from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
+from django.http import Http404
 from django.shortcuts import redirect
 from django.views.generic import FormView, TemplateView
 
@@ -4943,6 +5030,13 @@ class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixi
         return can_view_account_operations_dashboard(self.request.user)
 
 
+def _account_detail_or_404(user_id):
+    try:
+        return get_account_detail(user_id)
+    except ObjectDoesNotExist as exc:
+        raise Http404("Account not found.") from exc
+
+
 class AccountLoginView(LoginView):
     template_name = "accounts/login.html"
 
@@ -5032,7 +5126,7 @@ class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
     template_name = "accounts/user_detail.html"
 
     def dispatch(self, request, *args, **kwargs):
-        self.account_detail = get_account_detail(kwargs["user_id"])
+        self.account_detail = _account_detail_or_404(kwargs["user_id"])
         if not can_view_account_detail(request.user, self.account_detail.user):
             raise PermissionDenied
         return super().dispatch(request, *args, **kwargs)
@@ -5050,7 +5144,7 @@ class AccountUserEditView(AccountOperationsStaffRequiredMixin, FormView):
     form_class = AccountEditForm
 
     def dispatch(self, request, *args, **kwargs):
-        self.account_detail = get_account_detail(kwargs["user_id"])
+        self.account_detail = _account_detail_or_404(kwargs["user_id"])
         if not can_view_account_detail(request.user, self.account_detail.user):
             raise PermissionDenied
         return super().dispatch(request, *args, **kwargs)
@@ -5096,7 +5190,7 @@ class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
     form_class = UserPlayerLinkForm
 
     def dispatch(self, request, *args, **kwargs):
-        self.account_detail = get_account_detail(kwargs["user_id"])
+        self.account_detail = _account_detail_or_404(kwargs["user_id"])
         if not can_view_account_detail(request.user, self.account_detail.user):
             raise PermissionDenied
         return super().dispatch(request, *args, **kwargs)
@@ -5132,7 +5226,8 @@ class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
         if action == "create":
             return super().post(request, *args, **kwargs)
 
-        form = self.form_class()
+        form = self.form_class(request.POST)
+        form.is_valid()
         try:
             link_id = int(request.POST.get("link_id", ""))
             if action == "deactivate":
@@ -5146,6 +5241,9 @@ class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
                 messages.success(request, "Primary self link updated.")
             else:
                 raise ValidationError("Unsupported link action.")
+        except ObjectDoesNotExist:
+            form.add_error(None, "Player link not found.")
+            return self.form_invalid(form)
         except (TypeError, ValueError, ValidationError) as exc:
             form.add_error(None, exc)
             return self.form_invalid(form)
```
