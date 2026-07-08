# Prompt 46 - Account Management

## User Prompt

```text
You are implementing Platform V1 Account Operations.

Implement Phase D only.

Password Reset

Do NOT implement Phase E or Phase F.

==================================================
Before Coding
==================================================

Read:

- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md
- AGENTS.md

Review:

accounts/
players/
analytics/
drafts/

Pay particular attention to:

accounts/services/account_operations_service.py
accounts/services/password_service.py
accounts/services/provisioning_service.py
accounts/services/profile_service.py
accounts/services/auth_redirect_service.py
accounts/views.py
accounts/forms.py
accounts/templates/

==================================================
Goal
==================================================

Allow staff to reset passwords for existing accounts.

This is an operational password reset.

NOT an email reset workflow.

NOT a self-service password recovery flow.

==================================================
Architecture
==================================================

accounts owns:

- password reset
- temporary password generation
- must_change_password
- password services

Views remain thin.

Business logic belongs in services.

==================================================
Service Ownership
==================================================

Expand:

accounts/services/account_operations_service.py

Implement ONLY:

reset_account_password(...)

This becomes the only public orchestration entry point.

It should internally call password_service.

Views must never manipulate User passwords directly.

==================================================
Behavior
==================================================

Staff may reset passwords.

Support two cases.

Player account

Reuse existing birthdate temporary password rules.

Temporary password:

YYYYMMDD

using existing password_service.

Non-player account

Generate secure random temporary password.

Reuse the existing random password implementation.

Do NOT duplicate password generation.

==================================================
Password Reset Rules
==================================================

Reset should:

set new password

mark must_change_password=True

leave account active/inactive unchanged

leave role unchanged

leave links unchanged

leave provenance unchanged

leave import metadata unchanged

==================================================
Security
==================================================

Password is displayed ONLY once.

Immediately after successful reset.

Never:

store plaintext

serialize plaintext

log plaintext

place in metadata

place in import summaries

place in messages

After refresh,

password disappears.

==================================================
UI
==================================================

Add:

Reset Password

button

to:

/accounts/users/<id>/

Confirmation page is acceptable.

After reset:

Display one-time password.

==================================================
Permissions
==================================================

Staff:

may reset passwords.

Regular users:

may not.

==================================================
Forms
==================================================

Create only what is necessary.

Simple confirmation form is sufficient.

No JavaScript.

==================================================
Views
==================================================

Add:

/accounts/users/<id>/password/

Thin view.

==================================================
Templates
==================================================

Create:

user_password_reset.html

Reuse existing layout.

==================================================
Validation
==================================================

Reject:

missing account

invalid user

permission violations

==================================================
Do NOT Implement
==================================================

NO email

NO invitation

NO password recovery email

NO activation

NO deactivation

NO username editing

NO role editing

NO link editing

NO merge

NO audit logging

NO bulk reset

NO coach import

NO portals

==================================================
Engineering Recommendations
==================================================

1.

Reuse exactly one implementation of:

birthdate password generation

and

random password generation.

No duplication.

2.

password_service should remain the only owner of password generation.

3.

account_operations_service should orchestrate.

Views should call only account_operations_service.

4.

Create a reusable dataclass:

PasswordResetResult

containing:

- user
- username
- temporary_password

Hide temporary_password from repr.

5.

Continue the one-time password display pattern introduced in Phase B.

6.

Do not expose password through Django messages.

Messages should simply say:

"Password reset successfully."

7.

Keep must_change_password behavior identical to import provisioning.

==================================================
Testing
==================================================

Add tests for:

service

player password reset

non-player password reset

must_change_password

inactive account reset

view

permission

one-time password visibility

password not visible after refresh

regressions

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

Verify:

Phase D only

No Phase E

No Phase F

No email

No invitation

No activation logic

No link mutations

No role mutations

No duplicated password generation

Views remain thin

No migrations unless absolutely necessary

==================================================
Final Report
==================================================

Report:

implementation summary

files created

files modified

services expanded

views/templates/forms added

tests added

test results

implementation decisions

deviations

technical debt

self-review

confirmation that only Phase D was implemented.
```

## Implementation Commit Diff

```diff
diff --git a/accounts/forms.py b/accounts/forms.py
index 8cd49fc..5fa11a7 100644
--- a/accounts/forms.py
+++ b/accounts/forms.py
@@ -51,3 +51,7 @@ class UserPlayerLinkForm(forms.Form):
     def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
+
+
+class PasswordResetConfirmForm(forms.Form):
+    confirm = forms.BooleanField(required=True, label="I understand this temporary password will be shown once.")
diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
index 6090b8c..fdfd539 100644
--- a/accounts/services/account_operations_service.py
+++ b/accounts/services/account_operations_service.py
@@ -8,7 +8,7 @@ from django.db import transaction
 from django.urls import reverse
 from django.utils import timezone
 
-from accounts.models import AccountRole, UserPlayerLink
+from accounts.models import AccountRole, UserPlayerLink, UserPlayerRelationship
 from accounts.services import account_query_service
 from accounts.services.account_query_service import AccountListFilters
 from accounts.services.email_service import find_existing_email_user, normalize_email
@@ -23,6 +23,7 @@ from accounts.services.password_service import (
     generate_birthdate_password,
     mark_password_change_required,
     set_random_temporary_password,
+    set_temporary_password,
 )
 from accounts.services.profile_service import get_or_create_account_profile, set_account_role
 from accounts.services.provisioning_service import STATUS_CREATED, provision_player_account
@@ -116,6 +117,13 @@ class UpdatedLinkResult:
     is_active: bool
 
 
+@dataclass(frozen=True)
+class PasswordResetResult:
+    user: User
+    username: str
+    temporary_password: str = field(repr=False)
+
+
 def _validate_actor_can_create_role(actor, role: str) -> None:
     if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
         raise ValidationError("Only superusers can create admin accounts.")
@@ -221,6 +229,16 @@ def _get_link_for_user(user: User, link_id: int) -> UserPlayerLink:
     return UserPlayerLink.objects.select_for_update().select_related("user", "player").get(pk=link_id, user=user)
 
 
+def _player_for_password_reset(user: User) -> Player | None:
+    link = (
+        UserPlayerLink.objects.select_related("player")
+        .filter(user=user, relationship=UserPlayerRelationship.SELF, is_active=True)
+        .order_by("-is_primary", "id")
+        .first()
+    )
+    return link.player if link else None
+
+
 def get_account_operations_dashboard() -> AccountOperationsDashboard:
     """Return the read-only Account Operations dashboard context."""
     users = User.objects.select_related("account_profile")
@@ -395,6 +413,21 @@ def set_primary_user_player_link(*, actor, user_id: int, link_id: int) -> Update
     return _updated_link_result(set_primary_self_link(link, actor=actor))
 
 
+@transaction.atomic
+def reset_account_password(*, actor, user_id: int) -> PasswordResetResult:
+    """Reset an existing account password and require password change on next login."""
+    user = _get_user_for_update(user_id)
+    player = _player_for_password_reset(user)
+    if player:
+        temporary_password = generate_birthdate_password(player)
+        set_temporary_password(user, player)
+    else:
+        temporary_password = set_random_temporary_password(user)
+    mark_password_change_required(user, True)
+    user.refresh_from_db()
+    return PasswordResetResult(user=user, username=user.username, temporary_password=temporary_password)
+
+
 @transaction.atomic
 def create_account_only(
     *,
diff --git a/accounts/templates/accounts/user_detail.html b/accounts/templates/accounts/user_detail.html
index 2eeebc1..ee24f27 100644
--- a/accounts/templates/accounts/user_detail.html
+++ b/accounts/templates/accounts/user_detail.html
@@ -52,6 +52,7 @@
         <div class="pdp-actions">
             <a class="button button--primary" href="{% url 'accounts:user-edit' target_user.id %}">Edit Account</a>
             <a class="button button--ghost" href="{% url 'accounts:user-links' target_user.id %}">Manage Links</a>
+            <a class="button button--ghost" href="{% url 'accounts:user-password-reset' target_user.id %}">Reset Password</a>
             <a class="button button--ghost" href="{% url 'accounts:user-list' %}">Back to users</a>
         </div>
     </article>
diff --git a/accounts/templates/accounts/user_password_reset.html b/accounts/templates/accounts/user_password_reset.html
new file mode 100644
index 0000000..0b18dc8
--- /dev/null
+++ b/accounts/templates/accounts/user_password_reset.html
@@ -0,0 +1,42 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}Reset Password{% endblock %}
+{% block pdp_subtitle %}Set a temporary password and require a password change at next login.{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    {% if password_reset_result %}
+        <article class="pdp-card">
+            <h2>Password Reset Complete</h2>
+            <p>The temporary password is shown once. It will not be available after leaving or refreshing this page.</p>
+            <dl class="pdp-definition-list">
+                <dt>Username</dt>
+                <dd>{{ password_reset_result.username }}</dd>
+                <dt>Temporary password</dt>
+                <dd><strong>{{ password_reset_result.temporary_password }}</strong></dd>
+            </dl>
+            <div class="pdp-actions">
+                <a class="button button--primary" href="{% url 'accounts:user-detail' target_user.id %}">Back to account</a>
+            </div>
+        </article>
+    {% else %}
+        <article class="pdp-card">
+            <h2>{{ target_user.get_full_name|default:target_user.username }}</h2>
+            <p>Resetting this password will require the user to change it at next login.</p>
+            <form method="post" class="pdp-form">
+                {% csrf_token %}
+                {{ form.non_field_errors }}
+                <label>
+                    {{ form.confirm }}
+                    {{ form.confirm.label }}
+                    {{ form.confirm.errors }}
+                </label>
+                <div class="pdp-actions">
+                    <button class="button button--primary" type="submit">Reset Password</button>
+                    <a class="button button--ghost" href="{% url 'accounts:user-detail' target_user.id %}">Cancel</a>
+                </div>
+            </form>
+        </article>
+    {% endif %}
+</section>
+{% endblock %}
diff --git a/accounts/tests.py b/accounts/tests.py
index 6a3aaf4..ac95e07 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -20,6 +20,7 @@ from accounts.services.account_operations_service import (
     get_account_list,
     get_account_operations_dashboard,
     reactivate_user_player_link,
+    reset_account_password,
     set_primary_user_player_link,
     update_account,
 )
@@ -608,6 +609,61 @@ class AccountOperationsServiceTests(TestCase):
         with self.assertRaises(ValidationError):
             set_primary_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link.id)
 
+    def test_reset_account_password_uses_birthdate_for_player_account(self):
+        self.player_user.account_profile.must_change_password = False
+        self.player_user.account_profile.save(update_fields=["must_change_password", "updated_at"])
+        original_link_count = UserPlayerLink.objects.filter(user=self.player_user).count()
+
+        result = reset_account_password(actor=self.staff, user_id=self.player_user.id)
+
+        self.player_user.refresh_from_db()
+        self.assertEqual(result.user, self.player_user)
+        self.assertEqual(result.username, "alex.player")
+        self.assertEqual(result.temporary_password, "20120501")
+        self.assertTrue(self.player_user.check_password("20120501"))
+        self.assertTrue(self.player_user.account_profile.must_change_password)
+        self.assertTrue(self.player_user.is_active)
+        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
+        self.assertTrue(self.player_user.account_profile.created_from_import)
+        self.assertEqual(self.player_user.account_profile.import_batch, self.import_batch)
+        self.assertEqual(UserPlayerLink.objects.filter(user=self.player_user).count(), original_link_count)
+        self.assertNotIn(result.temporary_password, repr(result))
+
+    def test_reset_account_password_uses_random_password_for_non_player_account(self):
+        self.coach.account_profile.must_change_password = False
+        self.coach.account_profile.save(update_fields=["must_change_password", "updated_at"])
+
+        result = reset_account_password(actor=self.staff, user_id=self.coach.id)
+
+        self.coach.refresh_from_db()
+        self.assertTrue(result.temporary_password)
+        self.assertNotEqual(result.temporary_password, "20120501")
+        self.assertTrue(self.coach.check_password(result.temporary_password))
+        self.assertTrue(self.coach.account_profile.must_change_password)
+        self.assertTrue(self.coach.is_active)
+        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
+        self.assertFalse(UserPlayerLink.objects.filter(user=self.coach, relationship=UserPlayerRelationship.SELF).exists())
+        self.assertNotIn(result.temporary_password, repr(result))
+
+    def test_reset_account_password_preserves_inactive_account_state(self):
+        self.assertFalse(self.inactive_user.is_active)
+
+        result = reset_account_password(actor=self.staff, user_id=self.inactive_user.id)
+
+        self.inactive_user.refresh_from_db()
+        self.assertFalse(self.inactive_user.is_active)
+        self.assertTrue(self.inactive_user.check_password(result.temporary_password))
+        self.assertTrue(self.inactive_user.account_profile.must_change_password)
+
+    def test_reset_account_password_rejects_player_account_missing_birthdate(self):
+        player = Player.objects.create(first_name="No", last_name="Birthdate")
+        user = User.objects.create_user(username="no.birthdate", password="testpass")
+        set_account_role(user, AccountRole.PLAYER)
+        link_user_to_player(user, player)
+
+        with self.assertRaises(ValidationError):
+            reset_account_password(actor=self.staff, user_id=user.id)
+
 
 class UserPlayerLinkModelTests(TestCase):
     def setUp(self):
@@ -1470,6 +1526,7 @@ class AccountOperationsViewTests(TestCase):
         self.assertContains(response, "Alex Player")
         self.assertContains(response, reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))
         self.assertContains(response, reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))
+        self.assertContains(response, reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}))
 
     def test_user_edit_requires_staff(self):
         self.client.force_login(self.regular)
@@ -1632,6 +1689,70 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Unsupported link action")
 
+    def test_password_reset_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_reset_non_player_password_and_see_password_once(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}),
+            {"confirm": "on"},
+        )
+
+        self.coach.refresh_from_db()
+        temporary_password = response.context["password_reset_result"].temporary_password
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Password Reset Complete")
+        self.assertContains(response, temporary_password)
+        self.assertTrue(self.coach.check_password(temporary_password))
+        self.assertTrue(self.coach.account_profile.must_change_password)
+        self.assertNotIn(temporary_password, " ".join(str(message) for message in get_messages(response.wsgi_request)))
+
+        refresh_response = self.client.get(reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}))
+        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
+        self.assertNotContains(refresh_response, temporary_password)
+        self.assertNotContains(detail_response, temporary_password)
+
+    def test_staff_can_reset_player_password_with_birthdate_password(self):
+        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
+        user = User.objects.create_user(username="blake.player", password="testpass")
+        set_account_role(user, AccountRole.PLAYER)
+        link_user_to_player(user, player)
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-password-reset", kwargs={"user_id": user.id}),
+            {"confirm": "on"},
+        )
+
+        user.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "20130602")
+        self.assertTrue(user.check_password("20130602"))
+        self.assertTrue(user.account_profile.must_change_password)
+
+    def test_password_reset_does_not_run_without_confirmation(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}), {})
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "This field is required")
+        self.coach.refresh_from_db()
+        self.assertTrue(self.coach.check_password("testpass"))
+
+    def test_password_reset_missing_account_returns_404(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:user-password-reset", kwargs={"user_id": 999999}))
+
+        self.assertEqual(response.status_code, 404)
+
     def test_profile_page_links_staff_to_account_operations(self):
         self.client.force_login(self.staff)
 
diff --git a/accounts/urls.py b/accounts/urls.py
index b618b47..f4fad92 100644
--- a/accounts/urls.py
+++ b/accounts/urls.py
@@ -11,6 +11,7 @@ from accounts.views import (
     AccountUserEditView,
     AccountUserLinksView,
     AccountUserListView,
+    AccountUserPasswordResetView,
     PlayerAccountCreateView,
 )
 
@@ -29,4 +30,5 @@ urlpatterns = [
     path("users/<int:user_id>/", AccountUserDetailView.as_view(), name="user-detail"),
     path("users/<int:user_id>/edit/", AccountUserEditView.as_view(), name="user-edit"),
     path("users/<int:user_id>/links/", AccountUserLinksView.as_view(), name="user-links"),
+    path("users/<int:user_id>/password/", AccountUserPasswordResetView.as_view(), name="user-password-reset"),
 ]
diff --git a/accounts/views.py b/accounts/views.py
index 8e9ace4..887a2b2 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -7,7 +7,13 @@ from django.http import Http404
 from django.shortcuts import redirect
 from django.views.generic import FormView, TemplateView
 
-from accounts.forms import AccountEditForm, AccountOnlyCreateForm, PlayerAccountCreateForm, UserPlayerLinkForm
+from accounts.forms import (
+    AccountEditForm,
+    AccountOnlyCreateForm,
+    PasswordResetConfirmForm,
+    PlayerAccountCreateForm,
+    UserPlayerLinkForm,
+)
 from accounts.services.account_operations_service import (
     create_account_only,
     create_player_account,
@@ -17,6 +23,7 @@ from accounts.services.account_operations_service import (
     get_account_list,
     get_account_operations_dashboard,
     reactivate_user_player_link,
+    reset_account_password,
     set_primary_user_player_link,
     update_account,
 )
@@ -263,6 +270,34 @@ class AccountUserLinksView(AccountOperationsStaffRequiredMixin, FormView):
         return redirect("accounts:user-links", user_id=self.account_detail.user.id)
 
 
+class AccountUserPasswordResetView(AccountOperationsStaffRequiredMixin, FormView):
+    template_name = "accounts/user_password_reset.html"
+    form_class = PasswordResetConfirmForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.account_detail = _account_detail_or_404(kwargs["user_id"])
+        if not can_view_account_detail(request.user, self.account_detail.user):
+            raise PermissionDenied
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["account_detail"] = self.account_detail
+        context["target_user"] = self.account_detail.user
+        return context
+
+    def form_valid(self, form):
+        try:
+            result = reset_account_password(actor=self.request.user, user_id=self.account_detail.user.id)
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Password reset successfully.")
+        return self.render_to_response(
+            self.get_context_data(form=self.form_class(), password_reset_result=result)
+        )
+
+
 class AccountOnlyCreateView(AccountOperationsStaffRequiredMixin, FormView):
     template_name = "accounts/account_create.html"
     form_class = AccountOnlyCreateForm
```
