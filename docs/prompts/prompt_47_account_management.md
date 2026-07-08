# Prompt 47 - Account Management

## User Prompt

```text
You are implementing Platform V1 Account Operations.

Implement Phase E only.

Bulk Operations

Do NOT implement Phase F.

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
accounts/services/account_query_service.py
accounts/services/password_service.py
accounts/services/link_service.py
accounts/views.py
accounts/forms.py
accounts/templates/

==================================================
Goal
==================================================

Allow staff to perform common operations on multiple accounts safely.

This is an operational convenience feature.

It must reuse the existing single-account services.

Do not duplicate business logic.

==================================================
Architecture
==================================================

Views remain orchestration only.

Bulk operations must simply iterate through existing
account_operations_service methods.

Example:

bulk activate

↓

update_account(...)

bulk password reset

↓

reset_account_password(...)

Never duplicate lower-level logic.

==================================================
Operations
==================================================

Implement:

Bulk Activate

Bulk Deactivate

Bulk Require Password Change

Bulk Clear Password Change

Do NOT implement bulk password reset.

Password reset intentionally remains an explicit,
per-user operation.

==================================================
UI
==================================================

User list gains:

checkbox per row

select all

bulk action dropdown

Apply button

Server-rendered only.

No JavaScript required.

==================================================
Bulk Actions
==================================================

Support:

Activate

Deactivate

Require Password Change

Clear Password Change

==================================================
Safety Rules
==================================================

Reuse all existing validation.

Specifically:

cannot deactivate yourself

cannot deactivate last active superuser

role restrictions remain unchanged

inactive accounts stay inactive unless activating

must_change_password handled through existing service

==================================================
Service Ownership
==================================================

Expand:

accounts/services/account_operations_service.py

Implement:

bulk_update_accounts(...)

or

bulk_account_operation(...)

Return:

BulkOperationResult

containing:

processed count

success count

failure count

per-account errors

Hide verbose internals from repr.

==================================================
Permissions
==================================================

Staff:

may perform bulk operations.

Superuser restrictions continue to apply.

==================================================
Views
==================================================

Add:

POST bulk operation endpoint

Reuse existing user list.

==================================================
Templates
==================================================

Modify only:

user_list.html

Keep layout consistent.

==================================================
Validation
==================================================

Reject:

unknown bulk action

empty selection

missing users

permission violations

Continue processing remaining users when practical.

Collect failures instead of aborting the whole batch.

==================================================
Engineering Recommendations
==================================================

1.

Bulk operations must reuse existing public service methods.

Never bypass business rules.

2.

Keep account_operations_service the orchestration boundary.

3.

Create:

BulkOperationResult

with:

processed

successful

failed

errors

4.

Errors should identify usernames rather than internal ids.

5.

Continue processing after failures.

Return a complete summary.

6.

Views should only display summary results.

==================================================
Do NOT Implement
==================================================

NO audit logging

NO imports

NO merge

NO email

NO invitations

NO bulk password reset

NO bulk username change

NO bulk role change

NO JavaScript

NO APIs

==================================================
Testing
==================================================

Add tests for:

bulk activate

bulk deactivate

bulk require password change

bulk clear password change

mixed success/failure

empty selection

unknown action

cannot deactivate self

cannot deactivate last superuser

view

permissions

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

Phase E only

No Phase F

No duplicated logic

Bulk operations reuse existing services

Views remain thin

No migrations unless absolutely necessary

Working tree clean

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

technical debt

self-review

confirmation that only Phase E was implemented.
```

## Implementation Commit Diff

```diff
diff --git a/accounts/forms.py b/accounts/forms.py
index 5fa11a7..3568389 100644
--- a/accounts/forms.py
+++ b/accounts/forms.py
@@ -1,6 +1,12 @@
 from django import forms
 
 from accounts.models import AccountRole, UserPlayerRelationship
+from accounts.services.account_operations_service import (
+    BULK_ACTION_ACTIVATE,
+    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
+    BULK_ACTION_DEACTIVATE,
+    BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
+)
 from players.models import Player
 
 
@@ -12,6 +18,13 @@ ACCOUNT_ONLY_ROLE_CHOICES = (
     (AccountRole.ADMIN, "Admin"),
 )
 
+BULK_ACTION_CHOICES = (
+    (BULK_ACTION_ACTIVATE, "Activate"),
+    (BULK_ACTION_DEACTIVATE, "Deactivate"),
+    (BULK_ACTION_REQUIRE_PASSWORD_CHANGE, "Require password change"),
+    (BULK_ACTION_CLEAR_PASSWORD_CHANGE, "Clear password change"),
+)
+
 
 class AccountOnlyCreateForm(forms.Form):
     username = forms.CharField(max_length=150)
@@ -55,3 +68,21 @@ class UserPlayerLinkForm(forms.Form):
 
 class PasswordResetConfirmForm(forms.Form):
     confirm = forms.BooleanField(required=True, label="I understand this temporary password will be shown once.")
+
+
+class BulkAccountOperationForm(forms.Form):
+    action = forms.ChoiceField(choices=BULK_ACTION_CHOICES)
+    user_ids = forms.MultipleChoiceField(required=False)
+    visible_user_ids = forms.MultipleChoiceField(required=False)
+    select_all = forms.BooleanField(required=False, label="Select all accounts shown")
+
+    def __init__(self, *args, visible_user_ids=None, **kwargs):
+        super().__init__(*args, **kwargs)
+        choices = [(str(user_id), str(user_id)) for user_id in visible_user_ids or []]
+        self.fields["user_ids"].choices = choices
+        self.fields["visible_user_ids"].choices = choices
+
+    def selected_user_ids(self):
+        if self.cleaned_data.get("select_all"):
+            return self.cleaned_data.get("visible_user_ids", [])
+        return self.cleaned_data.get("user_ids", [])
diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
index fdfd539..f7cbb90 100644
--- a/accounts/services/account_operations_service.py
+++ b/accounts/services/account_operations_service.py
@@ -124,6 +124,32 @@ class PasswordResetResult:
     temporary_password: str = field(repr=False)
 
 
+BULK_ACTION_ACTIVATE = "activate"
+BULK_ACTION_DEACTIVATE = "deactivate"
+BULK_ACTION_REQUIRE_PASSWORD_CHANGE = "require_password_change"
+BULK_ACTION_CLEAR_PASSWORD_CHANGE = "clear_password_change"
+BULK_ACCOUNT_ACTIONS = {
+    BULK_ACTION_ACTIVATE,
+    BULK_ACTION_DEACTIVATE,
+    BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
+    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
+}
+
+
+@dataclass(frozen=True)
+class BulkOperationError:
+    username: str
+    message: str
+
+
+@dataclass(frozen=True)
+class BulkOperationResult:
+    processed: int
+    successful: int
+    failed: int
+    errors: list[BulkOperationError] = field(default_factory=list, repr=False)
+
+
 def _validate_actor_can_create_role(actor, role: str) -> None:
     if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
         raise ValidationError("Only superusers can create admin accounts.")
@@ -428,6 +454,84 @@ def reset_account_password(*, actor, user_id: int) -> PasswordResetResult:
     return PasswordResetResult(user=user, username=user.username, temporary_password=temporary_password)
 
 
+@transaction.atomic
+def set_account_password_change_required(*, actor, user_id: int, required: bool) -> UpdatedAccountResult:
+    """Set the password-change requirement for an existing account."""
+    user = _get_user_for_update(user_id)
+    mark_password_change_required(user, bool(required))
+    user.refresh_from_db()
+    return _updated_account_result(user)
+
+
+def _clean_bulk_user_ids(user_ids):
+    clean_ids = []
+    seen = set()
+    for raw_user_id in user_ids or []:
+        raw_value = str(raw_user_id or "").strip()
+        if not raw_value or raw_value in seen:
+            continue
+        seen.add(raw_value)
+        try:
+            clean_ids.append(int(raw_value))
+        except (TypeError, ValueError):
+            clean_ids.append(raw_value)
+    return clean_ids
+
+
+def _bulk_error_username(user_id) -> str:
+    if isinstance(user_id, int):
+        username = User.objects.filter(pk=user_id).values_list("username", flat=True).first()
+        if username:
+            return username
+    return "Unknown account"
+
+
+def _validation_message(exc: ValidationError) -> str:
+    if hasattr(exc, "messages"):
+        return "; ".join(exc.messages)
+    return str(exc)
+
+
+def bulk_account_operation(*, actor, action: str, user_ids) -> BulkOperationResult:
+    """Apply a safe account operation to selected users and collect per-account failures."""
+    if action not in BULK_ACCOUNT_ACTIONS:
+        raise ValidationError("Unsupported bulk action.")
+
+    clean_user_ids = _clean_bulk_user_ids(user_ids)
+    if not clean_user_ids:
+        raise ValidationError("Select at least one account.")
+
+    successful = 0
+    errors = []
+    for user_id in clean_user_ids:
+        username = _bulk_error_username(user_id)
+        if not isinstance(user_id, int):
+            errors.append(BulkOperationError(username=username, message="Account not found."))
+            continue
+        try:
+            if action == BULK_ACTION_ACTIVATE:
+                activate_account(actor=actor, user_id=user_id)
+            elif action == BULK_ACTION_DEACTIVATE:
+                deactivate_account(actor=actor, user_id=user_id)
+            elif action == BULK_ACTION_REQUIRE_PASSWORD_CHANGE:
+                set_account_password_change_required(actor=actor, user_id=user_id, required=True)
+            elif action == BULK_ACTION_CLEAR_PASSWORD_CHANGE:
+                set_account_password_change_required(actor=actor, user_id=user_id, required=False)
+        except User.DoesNotExist:
+            errors.append(BulkOperationError(username=username, message="Account not found."))
+        except ValidationError as exc:
+            errors.append(BulkOperationError(username=username, message=_validation_message(exc)))
+        else:
+            successful += 1
+
+    return BulkOperationResult(
+        processed=len(clean_user_ids),
+        successful=successful,
+        failed=len(errors),
+        errors=errors,
+    )
+
+
 @transaction.atomic
 def create_account_only(
     *,
diff --git a/accounts/templates/accounts/user_list.html b/accounts/templates/accounts/user_list.html
index e78f575..bb3c9e7 100644
--- a/accounts/templates/accounts/user_list.html
+++ b/accounts/templates/accounts/user_list.html
@@ -77,10 +77,49 @@
     <article class="pdp-card">
         <h2>Results</h2>
         <p>{{ total_count }} account{{ total_count|pluralize }} found.</p>
+        <form method="post" action="{{ current_path }}" class="pdp-form">
+            {% csrf_token %}
+            {{ bulk_form.non_field_errors }}
+            <div class="pdp-actions">
+                <label>
+                    {{ bulk_form.select_all }}
+                    {{ bulk_form.select_all.label }}
+                </label>
+                <label>
+                    Bulk action
+                    {{ bulk_form.action }}
+                    {{ bulk_form.action.errors }}
+                </label>
+                <button class="button button--primary" type="submit">Apply</button>
+            </div>
+            {% if bulk_result %}
+                <section>
+                    <h3>Bulk Operation Result</h3>
+                    <p>{{ bulk_result.successful }} succeeded, {{ bulk_result.failed }} failed, {{ bulk_result.processed }} processed.</p>
+                    {% if bulk_result.errors %}
+                        <div class="table-wrap">
+                            <table class="pdp-table">
+                                <thead>
+                                    <tr><th>Account</th><th>Error</th></tr>
+                                </thead>
+                                <tbody>
+                                    {% for error in bulk_result.errors %}
+                                        <tr>
+                                            <td>{{ error.username }}</td>
+                                            <td>{{ error.message }}</td>
+                                        </tr>
+                                    {% endfor %}
+                                </tbody>
+                            </table>
+                        </div>
+                    {% endif %}
+                </section>
+            {% endif %}
         <div class="table-wrap">
             <table class="pdp-table">
                 <thead>
                     <tr>
+                        <th>Select</th>
                         <th>Username</th>
                         <th>Name</th>
                         <th>Email</th>
@@ -97,6 +136,10 @@
                 <tbody>
                     {% for row in rows %}
                         <tr>
+                            <td>
+                                <input type="hidden" name="visible_user_ids" value="{{ row.user.id }}">
+                                <input type="checkbox" name="user_ids" value="{{ row.user.id }}">
+                            </td>
                             <td>{{ row.user.username }}</td>
                             <td>{{ row.user.get_full_name|default:"-" }}</td>
                             <td>{{ row.user.email|default:"-" }}</td>
@@ -122,11 +165,12 @@
                             <td><a class="button button--ghost" href="{{ row.detail_url }}">Open</a></td>
                         </tr>
                     {% empty %}
-                        <tr><td colspan="11">No accounts match these filters.</td></tr>
+                        <tr><td colspan="12">No accounts match these filters.</td></tr>
                     {% endfor %}
                 </tbody>
             </table>
         </div>
+        </form>
     </article>
 </section>
 {% endblock %}
diff --git a/accounts/tests.py b/accounts/tests.py
index ac95e07..0904486 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -11,6 +11,7 @@ from django.contrib.auth import SESSION_KEY
 from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
 from accounts.services.account_operations_service import (
     activate_account,
+    bulk_account_operation,
     create_account_only,
     create_player_account,
     create_user_player_link,
@@ -664,6 +665,93 @@ class AccountOperationsServiceTests(TestCase):
         with self.assertRaises(ValidationError):
             reset_account_password(actor=self.staff, user_id=user.id)
 
+    def test_bulk_account_operation_activates_accounts(self):
+        result = bulk_account_operation(actor=self.staff, action="activate", user_ids=[self.inactive_user.id])
+
+        self.inactive_user.refresh_from_db()
+        self.assertEqual(result.processed, 1)
+        self.assertEqual(result.successful, 1)
+        self.assertEqual(result.failed, 0)
+        self.assertTrue(self.inactive_user.is_active)
+
+    def test_bulk_account_operation_deactivates_accounts(self):
+        result = bulk_account_operation(actor=self.staff, action="deactivate", user_ids=[self.coach.id])
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.processed, 1)
+        self.assertEqual(result.successful, 1)
+        self.assertFalse(self.coach.is_active)
+
+    def test_bulk_account_operation_sets_password_change_requirement(self):
+        mark_password_change_required(self.coach, False)
+
+        result = bulk_account_operation(
+            actor=self.staff,
+            action="require_password_change",
+            user_ids=[self.coach.id],
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.successful, 1)
+        self.assertTrue(self.coach.account_profile.must_change_password)
+
+    def test_bulk_account_operation_clears_password_change_requirement(self):
+        mark_password_change_required(self.player_user, True)
+
+        result = bulk_account_operation(
+            actor=self.staff,
+            action="clear_password_change",
+            user_ids=[self.player_user.id],
+        )
+
+        self.player_user.refresh_from_db()
+        self.assertEqual(result.successful, 1)
+        self.assertFalse(self.player_user.account_profile.must_change_password)
+
+    def test_bulk_account_operation_continues_after_failure(self):
+        result = bulk_account_operation(
+            actor=self.staff,
+            action="deactivate",
+            user_ids=[self.staff.id, self.coach.id],
+        )
+
+        self.staff.refresh_from_db()
+        self.coach.refresh_from_db()
+        self.assertEqual(result.processed, 2)
+        self.assertEqual(result.successful, 1)
+        self.assertEqual(result.failed, 1)
+        self.assertEqual(result.errors[0].username, "staff")
+        self.assertIn("cannot deactivate your own account", result.errors[0].message)
+        self.assertTrue(self.staff.is_active)
+        self.assertFalse(self.coach.is_active)
+
+    def test_bulk_account_operation_rejects_empty_selection_and_unknown_action(self):
+        with self.assertRaises(ValidationError):
+            bulk_account_operation(actor=self.staff, action="activate", user_ids=[])
+        with self.assertRaises(ValidationError):
+            bulk_account_operation(actor=self.staff, action="unsupported", user_ids=[self.coach.id])
+
+    def test_bulk_account_operation_reports_missing_users(self):
+        result = bulk_account_operation(actor=self.staff, action="activate", user_ids=[999999])
+
+        self.assertEqual(result.processed, 1)
+        self.assertEqual(result.successful, 0)
+        self.assertEqual(result.failed, 1)
+        self.assertEqual(result.errors[0].username, "Unknown account")
+        self.assertEqual(result.errors[0].message, "Account not found.")
+
+    def test_bulk_account_operation_rejects_last_superuser_deactivation(self):
+        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
+
+        result = bulk_account_operation(actor=self.staff, action="deactivate", user_ids=[superuser.id])
+
+        superuser.refresh_from_db()
+        self.assertEqual(result.successful, 0)
+        self.assertEqual(result.failed, 1)
+        self.assertEqual(result.errors[0].username, "ops.admin")
+        self.assertIn("last active superuser", result.errors[0].message)
+        self.assertTrue(superuser.is_active)
+
 
 class UserPlayerLinkModelTests(TestCase):
     def setUp(self):
@@ -1499,6 +1587,117 @@ class AccountOperationsViewTests(TestCase):
         self.assertContains(response, "coach.one")
         self.assertContains(response, "Coach")
         self.assertNotContains(response, "regular")
+        self.assertContains(response, "Bulk action")
+        self.assertContains(response, "Select all accounts shown")
+
+    def test_user_list_bulk_post_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {"action": "activate", "user_ids": [self.coach.id], "visible_user_ids": [self.coach.id]},
+        )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_bulk_activate_from_user_list(self):
+        self.coach.is_active = False
+        self.coach.save(update_fields=["is_active"])
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {"action": "activate", "user_ids": [self.coach.id], "visible_user_ids": [self.coach.id]},
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "1 succeeded, 0 failed")
+        self.assertTrue(self.coach.is_active)
+
+    def test_staff_can_bulk_require_and_clear_password_change_from_user_list(self):
+        mark_password_change_required(self.coach, False)
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "require_password_change",
+                "user_ids": [self.coach.id],
+                "visible_user_ids": [self.coach.id],
+            },
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertTrue(self.coach.account_profile.must_change_password)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "clear_password_change",
+                "user_ids": [self.coach.id],
+                "visible_user_ids": [self.coach.id],
+            },
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertFalse(self.coach.account_profile.must_change_password)
+
+    def test_staff_bulk_deactivate_reports_self_failure_and_successes(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "deactivate",
+                "user_ids": [self.staff.id, self.coach.id],
+                "visible_user_ids": [self.staff.id, self.coach.id],
+            },
+        )
+
+        self.staff.refresh_from_db()
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "1 succeeded, 1 failed")
+        self.assertContains(response, "staff")
+        self.assertContains(response, "cannot deactivate your own account")
+        self.assertTrue(self.staff.is_active)
+        self.assertFalse(self.coach.is_active)
+
+    def test_staff_bulk_action_rejects_empty_selection_and_unknown_action(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {"action": "activate", "visible_user_ids": [self.coach.id]},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Select at least one account")
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {"action": "unsupported", "user_ids": [self.coach.id], "visible_user_ids": [self.coach.id]},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Select a valid choice")
+
+    def test_staff_bulk_select_all_uses_visible_user_ids(self):
+        self.coach.is_active = False
+        self.coach.save(update_fields=["is_active"])
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {"action": "activate", "select_all": "on", "visible_user_ids": [self.coach.id]},
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertTrue(self.coach.is_active)
 
     def test_user_detail_requires_staff(self):
         self.client.force_login(self.regular)
diff --git a/accounts/views.py b/accounts/views.py
index 887a2b2..8b4a483 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -10,11 +10,13 @@ from django.views.generic import FormView, TemplateView
 from accounts.forms import (
     AccountEditForm,
     AccountOnlyCreateForm,
+    BulkAccountOperationForm,
     PasswordResetConfirmForm,
     PlayerAccountCreateForm,
     UserPlayerLinkForm,
 )
 from accounts.services.account_operations_service import (
+    bulk_account_operation,
     create_account_only,
     create_player_account,
     create_user_player_link,
@@ -130,9 +132,14 @@ class AccountUserListView(AccountOperationsStaffRequiredMixin, TemplateView):
         context = super().get_context_data(**kwargs)
         filters = parse_account_list_filters(self.request.GET)
         account_list = get_account_list(filters)
+        visible_user_ids = [row.user.id for row in account_list.rows]
+        bulk_form = kwargs.get("bulk_form") or BulkAccountOperationForm(visible_user_ids=visible_user_ids)
         context.update(
             {
                 "account_list": account_list,
+                "bulk_form": bulk_form,
+                "bulk_result": kwargs.get("bulk_result"),
+                "current_path": self.request.get_full_path(),
                 "filters": account_list.filters,
                 "rows": account_list.rows,
                 "role_choices": account_list.role_choices,
@@ -141,6 +148,29 @@ class AccountUserListView(AccountOperationsStaffRequiredMixin, TemplateView):
         )
         return context
 
+    def post(self, request, *args, **kwargs):
+        if not can_view_account_list(request.user):
+            raise PermissionDenied
+        visible_user_ids = request.POST.getlist("visible_user_ids")
+        form = BulkAccountOperationForm(request.POST, visible_user_ids=visible_user_ids)
+        bulk_result = None
+        if form.is_valid():
+            try:
+                bulk_result = bulk_account_operation(
+                    actor=request.user,
+                    action=form.cleaned_data["action"],
+                    user_ids=form.selected_user_ids(),
+                )
+            except ValidationError as exc:
+                form.add_error(None, exc)
+            else:
+                messages.success(
+                    request,
+                    f"Bulk operation complete: {bulk_result.successful} succeeded, {bulk_result.failed} failed.",
+                )
+                form = BulkAccountOperationForm(visible_user_ids=visible_user_ids)
+        return self.render_to_response(self.get_context_data(bulk_form=form, bulk_result=bulk_result))
+
 
 class AccountUserDetailView(AccountOperationsStaffRequiredMixin, TemplateView):
     template_name = "accounts/user_detail.html"
```
