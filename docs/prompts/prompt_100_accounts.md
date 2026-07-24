# Prompt 100 - Accounts

## User Prompt

```text
Implement shared default-password provisioning for imported coach accounts in the Django project at:

`/Users/eugenelin/dev/vmba0`

## Goal

Change the coach import workflow so that newly created coach user accounts all receive the same administrator-configured default password instead of a randomly generated password.

Every newly provisioned coach account must still be required to change its password after the first successful login.

Do not hard-code the actual default password in source code, migrations, tests, fixtures, logs, import summaries, or documentation.

The password must come from an environment variable or an equivalent secure Django setting.

## Existing architecture

Review the existing implementation before changing anything, especially:

* the `accounts` app;
* `AccountProfile`;
* the profile field that requires a password change;
* existing account-provisioning services;
* coach import services and forms;
* player import provisioning;
* password-generation utilities;
* username-generation services;
* email-matching and account-reuse logic;
* import result/read-model classes;
* existing account and coach-import tests;
* deployment environment-variable conventions.

Preserve the current service-oriented architecture. Keep views and forms thin.

Do not duplicate account-provisioning logic inside the coach importer if an existing provisioning service can be extended cleanly.

## Required behaviour

### 1. Shared coach password setting

Add a production setting sourced from an environment variable, using a clear name such as:

```python
COACH_IMPORT_DEFAULT_PASSWORD
```

The repository must not contain the real password.

Do not provide an insecure production default.

If the setting is absent or blank when coach account provisioning is requested, fail safely with a clear, administrator-facing validation error.

The failure must happen before partially provisioning a batch of coach accounts.

Normal application startup should not necessarily fail merely because the setting is absent if coach provisioning is not being used.

### 2. Newly created coach users

When a coach import creates a new Django user:

* use the existing username-generation rules;
* call Django’s `set_password()` with the configured shared password;
* never assign the raw string directly to `user.password`;
* assign the correct coach role/profile;
* set the existing password-change-required flag to `True`;
* preserve the current activation policy;
* create or maintain the appropriate link between the user and coach record, if such a relationship currently exists;
* preserve import-origin and import-batch metadata currently recorded by the provisioning workflow.

All newly created coach users in the same or later imports should receive the configured default password until an administrator changes the environment setting.

### 3. Existing and reused users

Do not reset the password of an existing user merely because the coach appears in an import.

For users that are matched, reused, already linked, or otherwise already exist:

* preserve their current password;
* preserve their current password-change status unless an existing business rule explicitly requires a change;
* do not silently reactivate them;
* do not overwrite unrelated account profile data.

Idempotently re-importing the same coach must not reset that user’s password.

### 4. First-login password change

Confirm that the existing forced-password-change workflow applies to imported coach users.

A newly imported coach user must not be able to use the rest of the authenticated application indefinitely with the shared password.

After initial authentication, the user should be redirected to the existing password-change page or otherwise restricted according to the project’s established first-login workflow.

After a successful password change:

* clear the password-change-required flag;
* allow normal application access;
* ensure the old shared password no longer authenticates that user.

Avoid building a second password-change system specifically for coaches.

### 5. Import user interface

Update the coach import interface and administrator-facing instructions so they accurately describe the behaviour.

The interface may say something like:

> Newly created coach accounts use the configured default coach password and must change it at first login.

Do not display the actual password in:

* the import form;
* preview screens;
* success messages;
* import summaries;
* logs;
* exception text;
* downloadable result files;
* HTML source;
* documentation committed to Git.

If administrators need to communicate the password to coaches, that should remain an operational process outside the import result page.

### 6. Import atomicity and validation

Inspect whether the coach import already uses `transaction.atomic()`.

Where practical, validate the configured default password before creating any accounts.

A missing or invalid setting should not result in a partially provisioned batch.

Preserve the existing behaviour for rows that do not request account provisioning.

### 7. Password validation

Use Django’s configured password validators where appropriate.

Decide whether the shared default password should be validated:

* when the import begins;
* through a dedicated provisioning-service validation function; or
* both.

Return a useful administrator-facing error if the configured password does not satisfy project password requirements.

Do not include the password itself in the error.

Be mindful that Django password validators relying on user attributes may require a representative unsaved user or validation at provisioning time.

Prefer a clean, testable implementation over embedding validation in a view.

### 8. Security safeguards

Ensure that:

* the raw password is never logged;
* the raw password is never returned in provisioning read models;
* the raw password is never serialized;
* the raw password is never stored in import-batch metadata;
* only Django’s password hash is stored in the database;
* tests do not use or reveal the real production password;
* test settings override the configuration with a clearly fake test-only value.

Search the codebase for any current behaviour that returns generated temporary passwords from the coach import workflow. Remove or adjust that behaviour for coaches so no raw password is exposed.

Do not change player-import password behaviour unless shared code must be refactored to support separate password policies cleanly.

## Suggested design

Prefer a password-policy abstraction or a clearly scoped provisioning function rather than coach-specific branching scattered across the importer.

For example, an account-provisioning service could accept a password strategy or explicit raw password internally:

```python
provision_user(
    ...,
    initial_password=coach_default_password,
    require_password_change=True,
)
```

However, raw passwords must remain internal to the provisioning call and must not appear in the returned result object.

Alternatively, introduce a coach-specific service such as:

```python
get_coach_import_default_password()
validate_coach_import_default_password()
provision_imported_coach_account(...)
```

Use whichever approach best matches the existing code structure.

Avoid overengineering. Do not introduce a new model just to store the shared password.

## Environment configuration

Update the project’s environment-variable example or deployment documentation with the variable name only, for example:

```text
COACH_IMPORT_DEFAULT_PASSWORD=<set securely in production>
```

Do not commit an actual usable password.

Document that production administrators must:

1. set the environment variable;
2. restart the application service;
3. communicate the temporary password securely to the coaches;
4. rotate the shared default password when appropriate.

Do not place the password in a systemd unit committed to the repository.

Follow the project’s existing `/etc/vancouverminorbaseball.env` deployment convention if that is still current.

## Tests

Add or update tests covering at least the following.

### Configuration

1. Coach provisioning succeeds when a valid test default password is configured.
2. Coach provisioning fails clearly when the setting is missing.
3. Coach provisioning fails clearly when the setting is blank.
4. An invalid configured password is rejected if Django password validation is enforced.
5. Error output does not contain the raw password.

Use `override_settings()` or the project’s established settings-testing pattern.

### New user creation

6. Two newly imported coaches receive the same configured initial password.
7. Both users authenticate successfully with that password before changing it.
8. Their database password values are hashed and are not equal to the raw password.
9. Both profiles are marked as requiring a password change.
10. The correct coach role and import metadata are assigned.

### Existing users and idempotency

11. Re-importing an already provisioned coach does not reset the password.
12. Reusing an existing user does not replace that user’s password.
13. Reusing an existing user does not incorrectly set or clear the password-change-required flag.
14. Re-importing the same data does not create duplicate users or duplicate active links.

A strong password-reset test should:

* provision the coach;
* change the user’s password to a distinct value;
* re-import the coach;
* assert that the distinct password still works;
* assert that the shared default password no longer works.

### First-login enforcement

15. A new coach account is redirected or restricted by the existing forced-password-change workflow.
16. Completing the password change clears the required-change flag.
17. After changing the password, the user can reach the normal coach application pages.
18. After changing the password, the shared default password no longer authenticates that user.

### Import behaviour

19. A missing password setting does not partially create accounts in a multi-row provisioning import.
20. Coach import without account provisioning continues to work when the setting is absent.
21. Import summaries do not contain the shared password.
22. Logs and returned provisioning objects do not expose the shared password.

## Backward compatibility

Preserve existing behaviour for:

* coaches imported without user provisioning;
* existing coach records;
* account matching and reuse;
* username collision handling;
* email normalization;
* coach roles and permissions;
* import summaries and batch records;
* player account provisioning;
* non-coach account workflows.

Do not reset passwords for coaches who were imported before this change.

No data migration should be necessary unless the existing schema or profile defaults require one. Explain clearly if a migration is generated and why.

## Documentation and QA

Update relevant documentation and QA traceability.

Add a QA case for shared coach default-password provisioning and first-login enforcement, using the project’s existing QA ID convention.

Document:

* the environment-variable name;
* the provisioning behaviour;
* the no-password-disclosure requirement;
* idempotent re-import behaviour;
* the first-login password-change requirement;
* deployment steps for setting or rotating the password.

Do not document the actual password.

## Validation commands

Run the project’s standard checks, including at least:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test accounts
```

Also run the coach-import test module or app-specific suite identified during code inspection.

Then run the full test suite:

```bash
python manage.py test
```

Finally run:

```bash
git diff --check
```

Report:

* files changed;
* design decisions;
* whether a migration was needed;
* test counts and results;
* the exact environment-variable name;
* any deployment steps required;
* any unrelated working-tree files left untouched.

## Git discipline

Inspect `git status` before making changes.

Do not include unrelated files, especially any local QA CSVs, production data, uploaded media, virtual environments, SQLite databases, or backups.

Create focused commits with clear messages, such as:

```text
Use shared default password for imported coaches
```

If prompt archiving is part of the project’s established workflow, archive this prompt in a separate commit.

Do not push unless explicitly instructed.

## Acceptance criteria

The work is complete when:

* all newly created coach users receive the configured shared default password;
* the password is securely hashed through `set_password()`;
* new coach profiles require a password change;
* existing or reused users do not have passwords reset;
* idempotent imports do not reset passwords;
* the shared password is never exposed by the import system;
* missing configuration fails safely before partial provisioning;
* the existing first-login password-change workflow is enforced;
* player and unrelated account provisioning behaviour remains unchanged;
* relevant targeted and full tests pass.
```

## Implementation Commit

```text
0519119dd3e258b1c3fcff11339caac53e083aa0
```

## Commit Diff

```diff
diff --git a/README.md b/README.md
index 8231ec0..bc39c0b 100644
--- a/README.md
+++ b/README.md
@@ -158,6 +158,7 @@ Key environment variables:
 
 - `DJANGO_SECRET_KEY` is required.
 - `DJANGO_DEBUG` defaults to false.
+- `COACH_IMPORT_DEFAULT_PASSWORD` is required before creating new coach accounts through coach import.
 - `DJANGO_ALLOWED_HOSTS` defaults to `localhost,127.0.0.1`.
 - `DJANGO_STATIC_ROOT` defaults to `BASE_DIR / "staticfiles"`.
 - `DJANGO_MEDIA_ROOT` defaults to `BASE_DIR / "media"`.
diff --git a/accounts/services/coach_import/commit.py b/accounts/services/coach_import/commit.py
index 9890c65..3b2fcbb 100644
--- a/accounts/services/coach_import/commit.py
+++ b/accounts/services/coach_import/commit.py
@@ -31,7 +31,10 @@ from accounts.services.coach_import.result_models import (
     CoachImportRowPreview,
 )
 from accounts.services.email_service import find_existing_email_user
-from accounts.services.password_service import set_random_temporary_password
+from accounts.services.password_service import (
+    set_coach_import_default_password,
+    validate_coach_import_default_password,
+)
 from accounts.services.permissions import can_manage_accounts
 from accounts.services.profile_service import (
     get_or_create_account_profile,
@@ -47,6 +50,22 @@ def validate_actor(actor) -> None:
         raise ValidationError("Only staff users can import coaches.")
 
 
+def validate_ready_row_passwords(preview_rows: list[CoachImportRowPreview]) -> None:
+    """Validate shared coach-import password before creating any new users."""
+    users = [
+        User(
+            username=row.final_username,
+            first_name=row.first_name,
+            last_name=row.last_name,
+            email=row.email,
+        )
+        for row in preview_rows
+        if row.status == STATUS_READY
+    ]
+    if users:
+        validate_coach_import_default_password(users=users)
+
+
 @transaction.atomic
 def reuse_existing_coach(
     row: CoachImportRowPreview, season: Season
@@ -98,7 +117,7 @@ def create_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResul
         email=row.email,
         is_active=row.is_active,
     )
-    temporary_password = set_random_temporary_password(user)
+    set_coach_import_default_password(user)
     profile = set_account_role(user, AccountRole.COACH)
     profile.must_change_password = True
     profile.metadata = {**profile_metadata(profile), **metadata_for_row(row)}
@@ -111,16 +130,16 @@ def create_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResul
         username=user.username,
         user_id=user.id,
         is_active=user.is_active,
-        temporary_password=temporary_password,
         season_name=season.name,
         team=row.team,
         division=row.division,
         assignment_role_label=row.assignment_role_label,
         assignment_status=assignment_action,
-        password_behavior="Temporary password generated",
+        password_behavior="Configured default password; change required",
         messages=[
             status_message,
-            "temporary password generated",
+            "configured default password assigned",
+            "password change required",
             "season team created" if team_created else "season team reused",
             f"assignment {assignment_action}",
         ],
@@ -130,9 +149,10 @@ def create_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResul
 def commit_coach_import(
     actor, csv_text: str, season: Season | None = None
 ) -> CoachImportResult:
-    """Create or reuse coach accounts from CSV text and return one-time passwords."""
+    """Create or reuse coach accounts from CSV text without exposing passwords."""
     validate_actor(actor)
     preview = preview_coach_import(csv_text, season=season)
+    validate_ready_row_passwords(preview.rows)
     result_rows = []
 
     for error in preview.row_errors:
diff --git a/accounts/services/coach_import/preview.py b/accounts/services/coach_import/preview.py
index 95e204a..8e39dfb 100644
--- a/accounts/services/coach_import/preview.py
+++ b/accounts/services/coach_import/preview.py
@@ -249,7 +249,7 @@ def preview_row(
         assignment_label="Create Assignment",
         account_action="create",
         account_label="Create Coach Account",
-        password_behavior="Temporary password will be generated",
+        password_behavior="Configured default password; change required",
         status=STATUS_READY,
         messages=messages,
     )
diff --git a/accounts/services/coach_import/result_models.py b/accounts/services/coach_import/result_models.py
index b3ec7c4..6877fd3 100644
--- a/accounts/services/coach_import/result_models.py
+++ b/accounts/services/coach_import/result_models.py
@@ -116,7 +116,6 @@ class CoachImportResultRow:
     username: str = ""
     user_id: int | None = None
     is_active: bool = False
-    temporary_password: str = field(default="", repr=False)
     season_name: str = ""
     team: str = ""
     division: str = ""
diff --git a/accounts/services/password_service.py b/accounts/services/password_service.py
index 501437c..5dd0865 100644
--- a/accounts/services/password_service.py
+++ b/accounts/services/password_service.py
@@ -1,11 +1,15 @@
-from datetime import date
 import secrets
+from datetime import date
 
+from django.conf import settings
+from django.contrib.auth.password_validation import validate_password
 from django.core.exceptions import ValidationError
 from django.db import transaction
 
 from accounts.services.profile_service import get_or_create_account_profile
 
+COACH_IMPORT_DEFAULT_PASSWORD_SETTING = "COACH_IMPORT_DEFAULT_PASSWORD"
+
 
 def generate_birthdate_password(player) -> str:
     """Return the temporary birthdate password for player-account provisioning only."""
@@ -29,7 +33,9 @@ def set_temporary_password(user, player) -> None:
 def generate_random_temporary_password(length: int = 18) -> str:
     """Return a secure random temporary password for non-player accounts."""
     if length < 12:
-        raise ValidationError("Temporary password length must be at least 12 characters.")
+        raise ValidationError(
+            "Temporary password length must be at least 12 characters."
+        )
     return secrets.token_urlsafe(length)[:length]
 
 
@@ -41,6 +47,33 @@ def set_random_temporary_password(user, length: int = 18) -> str:
     return password
 
 
+def get_coach_import_default_password() -> str:
+    """Return the configured shared coach-import password or fail safely."""
+    password = getattr(settings, COACH_IMPORT_DEFAULT_PASSWORD_SETTING, "")
+    password = "" if password is None else str(password).strip()
+    if not password:
+        raise ValidationError(
+            f"{COACH_IMPORT_DEFAULT_PASSWORD_SETTING} must be configured before creating coach accounts."
+        )
+    return password
+
+
+def validate_coach_import_default_password(users=None) -> str:
+    """Validate the configured coach-import password without exposing it."""
+    password = get_coach_import_default_password()
+    validation_users = list(users or [None])
+    for user in validation_users:
+        validate_password(password, user=user)
+    return password
+
+
+def set_coach_import_default_password(user) -> None:
+    """Set a hashed shared default password for a newly imported coach account."""
+    password = validate_coach_import_default_password(users=[user])
+    user.set_password(password)
+    user.save(update_fields=["password"])
+
+
 @transaction.atomic
 def mark_password_change_required(user, value=True):
     """Set the account profile password-change requirement."""
diff --git a/accounts/templates/accounts/coach_import_preview.html b/accounts/templates/accounts/coach_import_preview.html
index 1483b81..2100c8f 100644
--- a/accounts/templates/accounts/coach_import_preview.html
+++ b/accounts/templates/accounts/coach_import_preview.html
@@ -81,7 +81,7 @@
     <article class="pdp-card">
         <h2>Confirm</h2>
         <p>Only rows marked ready or reuse will be processed. Reused coach accounts keep their existing passwords unchanged.</p>
-        <p>Temporary passwords are generated and shown once only for newly created coach accounts.</p>
+        <p>Newly created coach accounts use the configured default coach password and must change it at first login. The password is not displayed by the import workflow.</p>
         <form method="post" action="{% url 'accounts:coach-import-confirm' %}" class="pdp-form">
             {% csrf_token %}
             <label>
diff --git a/accounts/templates/accounts/coach_import_result.html b/accounts/templates/accounts/coach_import_result.html
index 823da42..65d8c31 100644
--- a/accounts/templates/accounts/coach_import_result.html
+++ b/accounts/templates/accounts/coach_import_result.html
@@ -1,7 +1,7 @@
 {% extends "pdp/base.html" %}
 
 {% block pdp_title %}Coach Import Result{% endblock %}
-{% block pdp_subtitle %}Copy temporary passwords now. They will not be shown again.{% endblock %}
+{% block pdp_subtitle %}New coach accounts use the configured default password and must change it at first login.{% endblock %}
 
 {% block pdp_content %}
 <section class="pdp-grid pdp-grid--single">
@@ -39,7 +39,6 @@
                         <th>Assignment</th>
                         <th>Password</th>
                         <th>Active</th>
-                        <th>Temporary password</th>
                         <th>Messages</th>
                     </tr>
                 </thead>
@@ -60,7 +59,6 @@
                             <td>{{ row.assignment_status|default:"-" }}</td>
                             <td>{{ row.password_behavior|default:"-" }}</td>
                             <td>{% if row.user_id %}{{ row.is_active|yesno:"Yes,No" }}{% else %}-{% endif %}</td>
-                            <td><strong>{{ row.temporary_password|default:"-" }}</strong></td>
                             <td>
                                 {% for message in row.messages %}
                                     <div>{{ message }}</div>
@@ -70,7 +68,7 @@
                             </td>
                         </tr>
                     {% empty %}
-                        <tr><td colspan="10">No rows processed.</td></tr>
+                        <tr><td colspan="9">No rows processed.</td></tr>
                     {% endfor %}
                 </tbody>
             </table>
diff --git a/accounts/tests/test_account_operations.py b/accounts/tests/test_account_operations.py
index 4cf714d..0ae9c3c 100644
--- a/accounts/tests/test_account_operations.py
+++ b/accounts/tests/test_account_operations.py
@@ -1,3 +1,5 @@
+from django.test import override_settings
+
 from accounts.tests.helpers import (
     AccountListFilters,
     AccountRole,
@@ -35,6 +37,8 @@ from accounts.tests.helpers import (
     update_account,
 )
 
+COACH_IMPORT_TEST_PASSWORD = "CoachImportDefault123!"
+
 
 class AccountOperationsServiceTests(TestCase):
     def setUp(self):
@@ -785,6 +789,7 @@ class AccountOperationsServiceTests(TestCase):
         self.assertTrue(superuser.is_active)
 
 
+@override_settings(COACH_IMPORT_DEFAULT_PASSWORD=COACH_IMPORT_TEST_PASSWORD)
 class AccountOperationsViewTests(TestCase):
     def setUp(self):
         self.staff = User.objects.create_user(
@@ -1515,12 +1520,12 @@ class AccountOperationsViewTests(TestCase):
         )
         self.assertEqual(confirm_response.status_code, 200)
         self.assertContains(confirm_response, "Coach Import Result")
-        self.assertContains(confirm_response, "Temporary password")
+        self.assertContains(confirm_response, "configured default password")
+        self.assertNotContains(confirm_response, COACH_IMPORT_TEST_PASSWORD)
         user = User.objects.get(username="new.coach")
-        temporary_password = (
-            confirm_response.context["result"].rows[0].temporary_password
-        )
-        self.assertTrue(user.check_password(temporary_password))
+        result_row = confirm_response.context["result"].rows[0]
+        self.assertFalse(hasattr(result_row, "temporary_password"))
+        self.assertTrue(user.check_password(COACH_IMPORT_TEST_PASSWORD))
         self.assertTrue(user.is_active)
         self.assertEqual(user.account_profile.role, AccountRole.COACH)
         self.assertTrue(user.account_profile.must_change_password)
@@ -1539,9 +1544,9 @@ class AccountOperationsViewTests(TestCase):
         detail_response = self.client.get(
             reverse("accounts:user-detail", kwargs={"user_id": user.id})
         )
-        self.assertNotContains(detail_response, temporary_password)
+        self.assertNotContains(detail_response, COACH_IMPORT_TEST_PASSWORD)
         list_response = self.client.get(reverse("accounts:coach-import-list"))
-        self.assertNotContains(list_response, temporary_password)
+        self.assertNotContains(list_response, COACH_IMPORT_TEST_PASSWORD)
         preview_again = self.client.get(reverse("accounts:coach-import-preview"))
         self.assertEqual(preview_again.status_code, 302)
         confirm_again = self.client.get(reverse("accounts:coach-import-confirm"))
@@ -1601,9 +1606,8 @@ class AccountOperationsViewTests(TestCase):
         result = response.context["result"]
         self.assertEqual(result.existing_coaches_reused, 1)
         self.assertEqual(result.conflicts, 1)
-        temporary_password = result.rows[0].temporary_password
         existing_coach.refresh_from_db()
-        self.assertFalse(temporary_password)
+        self.assertFalse(hasattr(result.rows[0], "temporary_password"))
         self.assertFalse(existing_coach.account_profile.must_change_password)
         self.assertEqual(existing_coach.account_profile.role, AccountRole.COACH)
         self.assertEqual(
diff --git a/accounts/tests/test_account_services.py b/accounts/tests/test_account_services.py
index 1b2e04f..a6aea56 100644
--- a/accounts/tests/test_account_services.py
+++ b/accounts/tests/test_account_services.py
@@ -1,3 +1,9 @@
+from django.test import override_settings
+
+from accounts.services.password_service import (
+    set_coach_import_default_password,
+    validate_coach_import_default_password,
+)
 from accounts.tests.helpers import (
     STATUS_ALREADY_LINKED,
     STATUS_CONFLICT,
@@ -121,6 +127,29 @@ class AccountPasswordServiceTests(TestCase):
         self.assertGreaterEqual(len(password), 12)
         self.assertNotEqual(password, generate_random_temporary_password())
 
+    @override_settings(COACH_IMPORT_DEFAULT_PASSWORD="CoachImportDefault123!")
+    def test_set_coach_import_default_password_hashes_configured_password(self):
+        user = User.objects.create_user(
+            username="coach.import",
+            first_name="Coach",
+            last_name="Import",
+            email="coach@example.com",
+        )
+
+        set_coach_import_default_password(user)
+        user.refresh_from_db()
+
+        self.assertNotEqual(user.password, "CoachImportDefault123!")
+        self.assertTrue(user.check_password("CoachImportDefault123!"))
+
+    @override_settings(COACH_IMPORT_DEFAULT_PASSWORD="")
+    def test_coach_import_default_password_requires_setting(self):
+        with self.assertRaisesMessage(
+            ValidationError,
+            "COACH_IMPORT_DEFAULT_PASSWORD must be configured",
+        ):
+            validate_coach_import_default_password()
+
 
 class AccountProvisioningServiceTests(TestCase):
     def setUp(self):
diff --git a/accounts/tests/test_coach_import.py b/accounts/tests/test_coach_import.py
index ed4a6f3..60ec34f 100644
--- a/accounts/tests/test_coach_import.py
+++ b/accounts/tests/test_coach_import.py
@@ -1,3 +1,5 @@
+from django.test import override_settings
+
 from accounts.tests.helpers import (
     RESULT_CONFLICT,
     RESULT_CREATED,
@@ -15,11 +17,15 @@ from accounts.tests.helpers import (
     commit_coach_import,
     create_season,
     preview_coach_import,
+    reverse,
     set_account_role,
     username_for_person,
 )
 
+COACH_IMPORT_TEST_PASSWORD = "CoachImportDefault123!"
+
 
+@override_settings(COACH_IMPORT_DEFAULT_PASSWORD=COACH_IMPORT_TEST_PASSWORD)
 class CoachImportServiceTests(TestCase):
     def setUp(self):
         self.staff = User.objects.create_user(
@@ -36,16 +42,20 @@ class CoachImportServiceTests(TestCase):
             + "\n".join(rows)
         )
 
-    def test_valid_csv_creates_active_coach_with_one_time_password(self):
+    def test_valid_csv_creates_active_coach_with_default_password(self):
         result = commit_coach_import(
             self.staff,
             self.csv_text(
-                ["Casey,Coach,casey@example.com,,Reds,13U,true,Lead coach,C001"]
+                [
+                    "Casey,Coach,casey@example.com,,Reds,13U,true,Lead coach,C001",
+                    "Sam,Coach,sam@example.com,,Reds,13U,true,Assistant coach,C002",
+                ]
             ),
             season=self.season,
         )
 
         user = User.objects.get(email="casey@example.com")
+        second_user = User.objects.get(email="sam@example.com")
         profile = user.account_profile
         result_row = result.rows[0]
         self.assertEqual(result_row.status, RESULT_CREATED)
@@ -57,15 +67,19 @@ class CoachImportServiceTests(TestCase):
         self.assertTrue(profile.must_change_password)
         self.assertEqual(profile.metadata["team"], "Reds")
         self.assertEqual(profile.metadata["division"], "13U")
-        self.assertTrue(result_row.temporary_password)
-        self.assertTrue(user.check_password(result_row.temporary_password))
-        self.assertNotIn(result_row.temporary_password, repr(result_row))
+        self.assertFalse(hasattr(result_row, "temporary_password"))
+        self.assertTrue(user.check_password(COACH_IMPORT_TEST_PASSWORD))
+        self.assertTrue(second_user.check_password(COACH_IMPORT_TEST_PASSWORD))
+        self.assertNotEqual(user.password, COACH_IMPORT_TEST_PASSWORD)
+        self.assertNotEqual(second_user.password, COACH_IMPORT_TEST_PASSWORD)
+        self.assertNotIn(COACH_IMPORT_TEST_PASSWORD, repr(result_row))
+        self.assertNotIn(COACH_IMPORT_TEST_PASSWORD, str(result))
         self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
         self.assertEqual(Player.objects.count(), 0)
-        self.assertEqual(result.users_created, 1)
-        self.assertEqual(result.active_accounts, 1)
+        self.assertEqual(result.users_created, 2)
+        self.assertEqual(result.active_accounts, 2)
         self.assertEqual(result.inactive_accounts, 0)
-        self.assertEqual(result.password_change_required, 1)
+        self.assertEqual(result.password_change_required, 2)
         assignment = CoachSeasonAssignment.objects.select_related("season_team").get(
             user=user
         )
@@ -76,7 +90,110 @@ class CoachImportServiceTests(TestCase):
         )
         self.assertTrue(assignment.is_primary)
         self.assertEqual(result.season_teams_created, 1)
-        self.assertEqual(result.assignments_created, 1)
+        self.assertEqual(result.assignments_created, 2)
+
+    @override_settings(COACH_IMPORT_DEFAULT_PASSWORD="")
+    def test_missing_default_password_blocks_new_coaches_before_partial_creation(self):
+        with self.assertRaisesMessage(
+            ValidationError,
+            "COACH_IMPORT_DEFAULT_PASSWORD must be configured",
+        ):
+            commit_coach_import(
+                self.staff,
+                self.csv_text(
+                    [
+                        "Casey,Coach,casey@example.com,,Reds,13U,true,,",
+                        "Sam,Coach,sam@example.com,,Reds,13U,true,,",
+                    ]
+                ),
+                season=self.season,
+            )
+
+        self.assertFalse(
+            User.objects.filter(
+                email__in=["casey@example.com", "sam@example.com"]
+            ).exists()
+        )
+        self.assertFalse(CoachSeasonAssignment.objects.exists())
+
+    @override_settings(COACH_IMPORT_DEFAULT_PASSWORD="   ")
+    def test_blank_default_password_blocks_new_coaches(self):
+        with self.assertRaisesMessage(
+            ValidationError,
+            "COACH_IMPORT_DEFAULT_PASSWORD must be configured",
+        ):
+            commit_coach_import(
+                self.staff,
+                self.csv_text(["Blank,Coach,blank@example.com,,Reds,13U,true,,"]),
+                season=self.season,
+            )
+
+        self.assertFalse(User.objects.filter(email="blank@example.com").exists())
+
+    @override_settings(COACH_IMPORT_DEFAULT_PASSWORD="12345678")
+    def test_invalid_default_password_is_rejected_without_exposing_password(self):
+        with self.assertRaises(ValidationError) as context:
+            commit_coach_import(
+                self.staff,
+                self.csv_text(["Weak,Coach,weak@example.com,,Reds,13U,true,,"]),
+                season=self.season,
+            )
+
+        self.assertNotIn("12345678", str(context.exception))
+        self.assertFalse(User.objects.filter(email="weak@example.com").exists())
+
+    @override_settings(COACH_IMPORT_DEFAULT_PASSWORD="")
+    def test_reuse_only_import_does_not_require_default_password(self):
+        existing = User.objects.create_user(
+            username="existing.coach",
+            email="coach@example.com",
+            password="oldpass",
+        )
+        set_account_role(existing, AccountRole.COACH)
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Existing,Coach,coach@example.com,,Reds,13U,true,,"]),
+            season=self.season,
+        )
+
+        existing.refresh_from_db()
+        self.assertEqual(result.rows[0].status, RESULT_REUSED)
+        self.assertTrue(existing.check_password("oldpass"))
+
+    def test_imported_coach_must_change_shared_default_password_after_login(self):
+        commit_coach_import(
+            self.staff,
+            self.csv_text(["Login,Coach,login@example.com,,Reds,13U,true,,"]),
+            season=self.season,
+        )
+        user = User.objects.get(email="login@example.com")
+
+        self.assertTrue(
+            self.client.login(
+                username=user.username,
+                password=COACH_IMPORT_TEST_PASSWORD,
+            )
+        )
+        profile_response = self.client.get(reverse("accounts:profile"))
+        self.assertEqual(profile_response.status_code, 302)
+        self.assertEqual(profile_response["Location"], "/accounts/password/")
+
+        change_response = self.client.post(
+            reverse("accounts:password-change"),
+            {
+                "old_password": COACH_IMPORT_TEST_PASSWORD,
+                "new_password1": "DistinctCoachPassword123!",
+                "new_password2": "DistinctCoachPassword123!",
+            },
+        )
+
+        user.refresh_from_db()
+        user.account_profile.refresh_from_db()
+        self.assertEqual(change_response.status_code, 302)
+        self.assertFalse(user.account_profile.must_change_password)
+        self.assertTrue(user.check_password("DistinctCoachPassword123!"))
+        self.assertFalse(user.check_password(COACH_IMPORT_TEST_PASSWORD))
 
     def test_coach_import_requires_active_season(self):
         inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
@@ -206,7 +323,7 @@ class CoachImportServiceTests(TestCase):
             User.objects.filter(email__iexact="coach@example.com").count(), 1
         )
         self.assertFalse(existing.account_profile.must_change_password)
-        self.assertFalse(result.rows[0].temporary_password)
+        self.assertFalse(hasattr(result.rows[0], "temporary_password"))
         self.assertEqual(existing.password, original_password_hash)
         self.assertEqual(existing.account_profile.role, AccountRole.COACH)
         self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)
@@ -236,7 +353,7 @@ class CoachImportServiceTests(TestCase):
         self.assertEqual(result.rows[0].status, RESULT_REUSED)
         self.assertFalse(existing.is_active)
         self.assertEqual(existing.password, original_password_hash)
-        self.assertFalse(result.rows[0].temporary_password)
+        self.assertFalse(hasattr(result.rows[0], "temporary_password"))
         self.assertFalse(profile.must_change_password)
         self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)
 
@@ -251,6 +368,8 @@ class CoachImportServiceTests(TestCase):
             season=self.season,
         )
         user = User.objects.get(email="return@example.com")
+        user.set_password("DistinctCoachPassword123!")
+        user.save(update_fields=["password"])
         original_password_hash = user.password
 
         second = commit_coach_import(
@@ -271,7 +390,9 @@ class CoachImportServiceTests(TestCase):
         self.assertEqual(CoachSeasonAssignment.objects.filter(user=user).count(), 1)
         self.assertEqual(assignment.starts_on.isoformat(), "2026-04-01")
         self.assertEqual(user.password, original_password_hash)
-        self.assertFalse(second.rows[0].temporary_password)
+        self.assertTrue(user.check_password("DistinctCoachPassword123!"))
+        self.assertFalse(hasattr(second.rows[0], "temporary_password"))
+        self.assertFalse(user.check_password(COACH_IMPORT_TEST_PASSWORD))
 
     def test_new_season_creates_new_assignment_and_distinct_team(self):
         commit_coach_import(
@@ -408,7 +529,7 @@ class CoachImportServiceTests(TestCase):
         self.assertEqual(profile.metadata["division"], "13U")
         self.assertEqual(profile.metadata["notes"], "Keep this")
         self.assertEqual(profile.metadata["custom"], "value")
-        self.assertFalse(result.rows[0].temporary_password)
+        self.assertFalse(hasattr(result.rows[0], "temporary_password"))
         self.assertFalse(profile.created_from_import)
         self.assertIsNone(profile.import_batch)
 
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index a69ab6c..1068665 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -245,7 +245,7 @@ The password-change page is:
 /accounts/password/
 ```
 
-Temporary passwords are shown only once when staff creates, imports, or resets an account. If the temporary password is lost, staff must reset it.
+Temporary passwords are shown only once when staff manually creates or resets an account. Imported player accounts use the documented player-import password rule. Imported coach accounts use the administrator-configured default coach password, which is not displayed in the import workflow.
 
 ### Account Profile
 
diff --git a/docs/deployment/README.md b/docs/deployment/README.md
index 8a5cf9d..fc544c3 100644
--- a/docs/deployment/README.md
+++ b/docs/deployment/README.md
@@ -61,6 +61,7 @@ Future production deployments should:
 - avoid production-only edits to tracked files;
 - keep secrets out of Git;
 - use environment variables for deployment-specific settings;
+- configure `COACH_IMPORT_DEFAULT_PASSWORD` before creating new imported coach accounts;
 - back up the database before migrations;
 - archive media before major upgrades;
 - verify migrations before applying them;
diff --git a/docs/deployment/RUNBOOK.md b/docs/deployment/RUNBOOK.md
index 5de9cc1..9c73eba 100644
--- a/docs/deployment/RUNBOOK.md
+++ b/docs/deployment/RUNBOOK.md
@@ -61,6 +61,7 @@ DJANGO_DEBUG
 DJANGO_ALLOWED_HOSTS
 DJANGO_STATIC_ROOT
 DJANGO_MEDIA_ROOT
+COACH_IMPORT_DEFAULT_PASSWORD
 ```
 
 Verify systemd configuration:
@@ -74,6 +75,13 @@ Verify that production uses `EnvironmentFile=/etc/vancouverminorbaseball.env`.
 
 Do not commit `/etc/vancouverminorbaseball.env`.
 
+`COACH_IMPORT_DEFAULT_PASSWORD` must be set before staff create new coach
+accounts through coach import. Set it securely in
+`/etc/vancouverminorbaseball.env`, restart the application service after changing
+it, communicate it to coaches through an approved operational channel, and
+rotate it when appropriate. Do not paste the value into Git, logs, screenshots,
+or shared documentation.
+
 ## Deployment
 
 Activate the production virtual environment if needed, then verify dependencies:
diff --git a/docs/qa/platform_e2e/CHANGELOG.md b/docs/qa/platform_e2e/CHANGELOG.md
index 35832a4..32af477 100644
--- a/docs/qa/platform_e2e/CHANGELOG.md
+++ b/docs/qa/platform_e2e/CHANGELOG.md
@@ -12,6 +12,7 @@
 - Change-impact guidance for selecting QA scope.
 - Lightweight maintenance conventions for future traceability changes.
 - Optional evaluation question traceability and regression coverage.
+- Coach import default-password provisioning traceability and QA guidance.
 
 ## Previous Milestones
 
diff --git a/docs/qa/platform_e2e/README.md b/docs/qa/platform_e2e/README.md
index 6161951..01be655 100644
--- a/docs/qa/platform_e2e/README.md
+++ b/docs/qa/platform_e2e/README.md
@@ -205,7 +205,7 @@ Each future feature should receive:
 - Coach import belongs to Account Operations and creates or reuses coach accounts.
 - Player imports can optionally provision player accounts when staff select the account-provisioning option and map the `account_email` column.
 - Player account temporary passwords are based on the imported birthdate in `YYYYMMDD` format and are not displayed in the import result.
-- Coach account temporary passwords are secure random passwords shown only once on the coach import result page.
+- Coach account initial passwords use the configured coach import default password and are not displayed by the coach import workflow.
 - Imported coach accounts are active by default unless the CSV sets `is_active` to a false value.
 - Imported coaches do not receive Django staff or superuser access.
 - Coach import creates or updates season teams and coach assignments.
diff --git a/docs/qa/platform_e2e/feature_traceability.md b/docs/qa/platform_e2e/feature_traceability.md
index 204139d..def4eb4 100644
--- a/docs/qa/platform_e2e/feature_traceability.md
+++ b/docs/qa/platform_e2e/feature_traceability.md
@@ -62,6 +62,7 @@ Current prefixes:
 | `ACC-005` | Account activation lifecycle | Critical | Partial | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Account Activation And Password Workflow |
 | `ACC-006` | Temporary password and forced password change | Critical | Yes | Yes | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Account Activation And Password Workflow |
 | `ACC-007` | Manual account creation | High | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Manual Creation |
+| `ACC-008` | Coach import default-password provisioning | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Coach Import / Account Activation And Password Workflow |
 | `ASN-001` | Player roster membership | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Player Import / Manual Creation |
 | `ASN-002` | Coach season assignment | Critical | Yes | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Coach Import / Manual Creation |
 | `ASN-003` | Historical assignment preservation | High | No | No | Yes | Yes | Semi-automatable | `platform_e2e_test_script.md` - Archive and Deactivation Behavior Tests |
diff --git a/docs/qa/platform_e2e/negative_test_fixtures.md b/docs/qa/platform_e2e/negative_test_fixtures.md
index d91913c..f7e4d34 100644
--- a/docs/qa/platform_e2e/negative_test_fixtures.md
+++ b/docs/qa/platform_e2e/negative_test_fixtures.md
@@ -10,7 +10,7 @@ Purpose:
 
 - Verify that coach import supports inactive accounts.
 - Verify inactive imported accounts cannot sign in until staff activates them.
-- Verify activation does not change role, staff status, superuser status, assignment history, or temporary-password behavior.
+- Verify activation does not change role, staff status, superuser status, assignment history, or initial-password behavior.
 
 Prerequisites:
 
@@ -23,7 +23,7 @@ Expected outcome:
 - One coach account is created with role Coach.
 - `User.is_active` is false.
 - The coach season assignment is created as inactive.
-- A temporary password is shown once on the result page.
+- The account uses the configured coach import default password, which is not shown on the result page.
 - The inactive coach cannot sign in until activated through Account Operations.
 - After activation, the coach must change password before normal platform use.
 
@@ -56,7 +56,7 @@ Expected outcome:
 Cleanup:
 
 - Deactivate any new collision-test coach accounts.
-- Remove temporary passwords from notes.
+- Remove any operational password notes from shared test records.
 - Confirm no `players.Player` records or `UserPlayerLink` rows were created by the coach collision fixture.
 
 ## Player Account-Provisioning Collision Tests
diff --git a/docs/qa/platform_e2e/platform_e2e_test_script.md b/docs/qa/platform_e2e/platform_e2e_test_script.md
index 0ece02a..3e18012 100644
--- a/docs/qa/platform_e2e/platform_e2e_test_script.md
+++ b/docs/qa/platform_e2e/platform_e2e_test_script.md
@@ -30,6 +30,7 @@ These tests must pass before a production release is accepted:
 - [ ] evaluation review (`REV-001`, `REV-003`)
 - [ ] direct URL permissions (`SEC-001` to `SEC-004`)
 - [ ] forced password change (`ACC-006`)
+- [ ] coach import default-password provisioning (`ACC-008`)
 - [ ] no duplicate submissions after refresh or repeat submit (`EVL-005`)
 - [ ] basic Analytics Command Center integrity (`ANA-001`)
 
@@ -65,7 +66,7 @@ Critical and High tests should be prioritized when release time is limited. Medi
 | --- | --- | --- |
 | Import data creation and idempotency | `IMP-001` to `IMP-003` | Critical |
 | Import preview and conflict reporting | `IMP-004` | High |
-| Account provisioning, activation, and passwords | `ACC-001`, `ACC-002`, `ACC-005`, `ACC-006` | Critical |
+| Account provisioning, activation, and passwords | `ACC-001`, `ACC-002`, `ACC-005`, `ACC-006`, `ACC-008` | Critical |
 | Username and email handling | `ACC-003`, `ACC-004` | High |
 | Manual account creation | `ACC-007` | High |
 | Active assignments and memberships | `ASN-001`, `ASN-002` | Critical |
@@ -140,7 +141,7 @@ Coach import:
 - Boolean values accepted for `is_active`: blank, `1`, `true`, `yes`, `y`, `active`, `0`, `false`, `no`, `n`, `inactive`.
 - Imported coach accounts are active by default unless `is_active` is false.
 - Imported coach accounts must change password on first login.
-- New coach temporary passwords are random and shown once on the result page.
+- New coach accounts use the configured default coach import password. The password is not displayed on preview, result, summaries, logs, or account detail pages.
 - Existing coach accounts are reused by email and keep their existing password.
 - Existing non-coach accounts with the same email are conflicts.
 - Coach import creates or reuses season teams and creates or updates coach season assignments.
@@ -272,9 +273,9 @@ Steps:
 - [ ] Confirm team and division are recognized.
 - [ ] Confirm assignment roles are Head Coach and Assistant Coach.
 - [ ] Confirm account action is Create Coach Account or Reuse Coach Account.
-- [ ] Confirm password behavior says temporary password will be generated only for new accounts.
+- [ ] Confirm password behavior says the configured default password will be used only for new accounts and that password change is required.
 - [ ] Confirm Import.
-- [ ] Copy temporary passwords from the result page immediately if new coach accounts were created.
+- [ ] Confirm no raw coach password is shown on the result page.
 
 Expected result:
 
@@ -670,19 +671,19 @@ For each:
 
 - [ ] Confirm expected initial active/inactive status.
 - [ ] If inactive, activate through Account Operations.
-- [ ] Sign in with temporary password.
+- [ ] Sign in with the expected initial password.
 - [ ] Confirm forced password change happens before normal platform pages.
 - [ ] Change password.
 - [ ] Confirm redirect to the correct landing page.
 - [ ] Log out.
 - [ ] Confirm login succeeds with the new password.
-- [ ] Confirm the old temporary password no longer works.
+- [ ] Confirm the old initial password no longer works.
 - [ ] Confirm password pages use Accounts routes and current platform branding.
 
 Password expectations:
 
 - Imported player temporary password: birthdate as `YYYYMMDD`.
-- Imported coach temporary password: random one-time value shown only on import result page.
+- Imported coach initial password: configured default coach import password, not shown by the application.
 - Manually created account temporary password: one-time value shown only on creation result page.
 
 Pass / Fail:
@@ -948,12 +949,12 @@ Steps:
 - [ ] Import the inactive coach fixture.
 - [ ] Confirm the inactive coach user is created or retained.
 - [ ] Confirm the inactive coach cannot sign in.
-- [ ] Confirm knowing the correct temporary password does not grant access while inactive.
+- [ ] Confirm knowing the correct initial password does not grant access while inactive.
 - [ ] Confirm staff can activate the account from Account Operations.
 - [ ] Confirm the activated user can sign in.
 - [ ] Confirm forced password change still applies.
 - [ ] Confirm the user can log out and sign in with the new password.
-- [ ] Confirm the original temporary password no longer works.
+- [ ] Confirm the original initial password no longer works.
 - [ ] Deactivate the account again.
 - [ ] Confirm login is blocked again.
 - [ ] Submit or locate a historical evaluation by the account before deactivation where practical.
diff --git a/vancouverminor/settings.py b/vancouverminor/settings.py
index 2eaa7a7..ffbb762 100644
--- a/vancouverminor/settings.py
+++ b/vancouverminor/settings.py
@@ -45,6 +45,10 @@ DEBUG = env_bool("DJANGO_DEBUG", default=False)
 
 ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
 
+COACH_IMPORT_DEFAULT_PASSWORD = os.environ.get(
+    "COACH_IMPORT_DEFAULT_PASSWORD", ""
+).strip()
+
 
 # Application definition
```
