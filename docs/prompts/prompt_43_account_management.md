# Prompt 43: Account Management

## User Prompt

```text
You are performing Platform V1 Account Operations Phase B review fixes only.

Do NOT implement Phase C.

Do NOT implement new features.

Do NOT implement link management, activation/deactivation, username editing, password reset, bulk operations, coach import, merge flows, audit logging, email invitations, or portals.

Only address correctness, security, maintainability, and review issues found in Phase B.

==================================================
Before Coding
==================================================

Read:

- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md
- AGENTS.md

Review current Phase B implementation:

- accounts/forms.py
- accounts/services/account_operations_service.py
- accounts/services/password_service.py
- accounts/services/provisioning_service.py
- accounts/services/username_service.py
- accounts/views.py
- accounts/templates/accounts/account_create.html
- accounts/templates/accounts/player_account_create.html
- accounts/tests.py

==================================================
Required Review Fixes
==================================================

1. Confirm temporary password exposure is one-time only

Temporary passwords may appear only in the immediate successful POST response.

They must not appear in:

- Django messages
- database fields
- metadata
- logs
- import summaries
- serialized dataclasses beyond the immediate in-memory result object
- redirected pages
- refreshed GET pages

Add or strengthen tests proving:

- successful creation POST displays the temporary password
- following/opening the account detail page does not display the temporary password
- refreshing or opening the create page with GET does not display the temporary password
- Django messages do not contain the temporary password

==================================================
2. Explicitly document player-account birthdate password behavior in code/tests

For player account creation, the temporary password is birthdate-based.

This is acceptable for Platform V1 because it reuses the existing player provisioning rule.

However:

- keep it isolated to player account creation/provisioning
- keep random passwords for account-only creation
- ensure password-change is required
- do not store plaintext birthdate password anywhere
- do not expose it except immediate successful POST response

Add test coverage if missing.

==================================================
3. Username normalization decision

Review `validate_available_username()`.

Make username handling consistent with generated usernames.

Decision:

- Explicit usernames should be normalized to lowercase using casefold()
- Leading/trailing whitespace should be trimmed
- Allowed characters remain letters, numbers, dots, underscores, hyphens
- Duplicate checks remain case-insensitive

Update implementation and tests accordingly.

Example:

Input:

Coach.One

Stored username:

coach.one

==================================================
4. Import provenance preservation

Verify manual account creation and manual player account creation never mark:

- AccountProfile.created_from_import=True
- UserPlayerLink.created_from_import=True
- import_batch

unless an import batch is actually involved.

Add or strengthen tests proving:

- account-only creation has no import provenance
- manual player account creation has no import provenance
- import provisioning still preserves import provenance

==================================================
5. Service boundary cleanup

Ensure:

- views call only `account_operations_service`
- account_operations_service orchestrates
- provisioning_service still owns player-account provisioning mechanics
- username_service owns username normalization/validation
- password_service owns password generation/setting
- forms do not duplicate business rules beyond basic field validation

Do not change external behavior.

==================================================
6. Error handling cleanup

Review ValidationError handling in create views.

Ensure user-facing errors are clear and safe.

Do not leak sensitive information.

Do not expose temporary passwords after failure.

==================================================
7. Tests

Add or strengthen tests for:

- explicit username input is normalized lowercase
- duplicate username check remains case-insensitive
- temporary password appears only in immediate success response
- temporary password does not appear on account detail
- temporary password does not appear on GET create page
- manual account creation does not set import provenance
- manual player account creation does not set import provenance
- import provisioning still sets import provenance when import_batch exists
- account-only random temporary password remains random and hashed
- player-account birthdate password remains hashed and must-change-password

==================================================
Do NOT Change
==================================================

Do NOT implement:

- Phase C
- link management UI
- activation/deactivation workflows
- username edit workflow
- password reset workflow
- bulk operations
- coach import
- account merge
- duplicate account resolution
- audit logging
- emails/invitations
- portals
- new models/migrations unless absolutely unavoidable

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
Self Review
==================================================

Verify:

- Phase B only
- no Phase C work
- one-time temporary password exposure only
- explicit usernames normalized lowercase
- no plaintext password persistence
- manual creation provenance remains manual
- import provenance remains import-only
- views remain thin
- no duplicated provisioning logic
- no architecture violations
- project_flat_file.txt updated

==================================================
Final Report
==================================================

Report:

- files modified
- review fixes applied
- tests added/updated
- test results
- implementation decisions
- remaining technical debt
- self-review findings
- confirmation that Phase C was NOT started
```

## App / Subsystem

account_management

## Work Commit

`2e1cd9a`

## Work Commit Diff

```diff
diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
index 4b38248..6fca77c 100644
--- a/accounts/services/account_operations_service.py
+++ b/accounts/services/account_operations_service.py
@@ -1,6 +1,6 @@
 from __future__ import annotations

-from dataclasses import dataclass
+from dataclasses import dataclass, field

 from django.contrib.auth import get_user_model
 from django.core.exceptions import ValidationError
@@ -84,7 +84,7 @@ class AccountDetailContext:
 class CreatedAccountResult:
     user: User
     username: str
-    temporary_password: str
+    temporary_password: str = field(repr=False)
     role: str
     role_label: str
     player: Player | None = None
diff --git a/accounts/services/password_service.py b/accounts/services/password_service.py
index 38b03ba..501437c 100644
--- a/accounts/services/password_service.py
+++ b/accounts/services/password_service.py
@@ -8,7 +8,7 @@ from accounts.services.profile_service import get_or_create_account_profile


 def generate_birthdate_password(player) -> str:
-    """Return the temporary birthdate password for a player."""
+    """Return the temporary birthdate password for player-account provisioning only."""
     birthdate = getattr(player, "birthdate", None)
     if not birthdate:
         raise ValidationError("Player birthdate is required for account provisioning.")
diff --git a/accounts/services/username_service.py b/accounts/services/username_service.py
index 9d1792b..e17615c 100644
--- a/accounts/services/username_service.py
+++ b/accounts/services/username_service.py
@@ -40,10 +40,10 @@ def username_for_player(player) -> str:

 def validate_available_username(username: str) -> str:
     """Validate an explicitly supplied username and return the normalized value."""
-    cleaned = str(username or "").strip()
+    cleaned = str(username or "").strip().casefold()
     if not cleaned:
         raise ValidationError("Username is required.")
-    if USERNAME_ALLOWED_PATTERN.search(cleaned.casefold()):
+    if USERNAME_ALLOWED_PATTERN.search(cleaned):
         raise ValidationError("Username may contain only letters, numbers, dots, underscores, and hyphens.")
     if User.objects.filter(username__iexact=cleaned).exists():
         raise ValidationError("Username is already in use.")
diff --git a/accounts/tests.py b/accounts/tests.py
index 7cf9c73..24f97df 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -1,4 +1,5 @@
 from django.contrib import admin
+from django.contrib.messages import get_messages
 from django.contrib.auth import get_user_model
 from django.conf import settings
 from django.core.exceptions import ValidationError
@@ -306,7 +307,7 @@ class AccountOperationsServiceTests(TestCase):
     def test_create_account_only_creates_user_profile_and_temporary_password(self):
         result = create_account_only(
             actor=self.staff,
-            username="new.coach",
+            username="New.Coach",
             first_name="New",
             last_name="Coach",
             email="New.Coach@example.com",
@@ -322,10 +323,12 @@ class AccountOperationsServiceTests(TestCase):
         self.assertEqual(result.role_label, "Coach")
         self.assertTrue(result.temporary_password)
         self.assertTrue(user.check_password(result.temporary_password))
+        self.assertNotIn(result.temporary_password, repr(result))
         self.assertEqual(user.email, "new.coach@example.com")
         self.assertEqual(profile.role, AccountRole.COACH)
         self.assertTrue(profile.must_change_password)
         self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
         self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())

     def test_create_account_only_can_create_inactive_account(self):
@@ -383,11 +386,14 @@ class AccountOperationsServiceTests(TestCase):
         self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
         self.assertTrue(link.is_primary)
         self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
+        self.assertFalse(link.created_from_import)
+        self.assertIsNone(link.import_batch)

     def test_create_player_account_accepts_optional_username_and_inactive_flag(self):
         player = Player.objects.create(first_name="Casey", last_name="Player", birthdate="2014-07-03")

-        result = create_player_account(actor=self.staff, player=player, username="custom.player", is_active=False)
+        result = create_player_account(actor=self.staff, player=player, username="Custom.Player", is_active=False)

         self.assertEqual(result.username, "custom.player")
         self.assertFalse(User.objects.get(username="custom.player").is_active)
@@ -740,6 +746,7 @@ class AccountUsernameServiceTests(TestCase):
         User.objects.create_user(username="coach.one")

         self.assertEqual(validate_available_username("new.user"), "new.user")
+        self.assertEqual(validate_available_username("  Coach.Two  "), "coach.two")
         with self.assertRaises(ValidationError):
             validate_available_username("coach.ONE")
         with self.assertRaises(ValidationError):
@@ -1273,10 +1280,18 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Account Created")
         self.assertContains(response, "Temporary password")
+        temporary_password = response.context["created_account"].temporary_password
+        self.assertIn(temporary_password, response.content.decode())
+        self.assertNotIn(temporary_password, " ".join(str(message) for message in get_messages(response.wsgi_request)))
         self.assertTrue(user.account_profile.must_change_password)
         self.assertEqual(user.account_profile.role, AccountRole.GUEST_EVALUATOR)
         self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())

+        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
+        self.assertNotContains(detail_response, temporary_password)
+        get_response = self.client.get(reverse("accounts:account-create"))
+        self.assertNotContains(get_response, temporary_password)
+
     def test_staff_cannot_create_admin_account(self):
         self.client.force_login(self.staff)

@@ -1291,6 +1306,7 @@ class AccountOperationsViewTests(TestCase):

         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Only superusers can create admin accounts")
+        self.assertNotContains(response, "Temporary password")
         self.assertFalse(User.objects.filter(username="admin.try").exists())

     def test_player_account_create_requires_staff(self):
@@ -1318,10 +1334,16 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Player Account Created")
         self.assertContains(response, "20130602")
+        self.assertNotIn("20130602", " ".join(str(message) for message in get_messages(response.wsgi_request)))
         self.assertTrue(user.check_password("20130602"))
         self.assertTrue(user.account_profile.must_change_password)
         self.assertEqual(UserPlayerLink.objects.get(user=user).player, player)

+        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
+        self.assertNotContains(detail_response, "20130602")
+        get_response = self.client.get(reverse("accounts:player-account-create"))
+        self.assertNotContains(get_response, "20130602")
+
     def test_player_account_create_rejects_duplicate_player_account(self):
         player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
         create_player_account(actor=self.staff, player=player)
diff --git a/project_flat_file.txt b/project_flat_file.txt
index 2e01522..2a4aba8 100644
--- a/project_flat_file.txt
+++ b/project_flat_file.txt
@@ -65,6 +65,7 @@ When a user prompt causes any file to be created, modified, moved, or deleted:
 - Generate the diff for that commit against its previous commit.
 - Paste that diff into the prompt record.
 - Commit the prompt record and regenerated `project_flat_file.txt` separately.
+- Push the resulting commits to the remote repository before finishing the workflow.
 - Do not include unrelated user changes in either commit.
 - If a task cannot be committed safely because the worktree contains unrelated staged changes or an instruction explicitly forbids committing, explain the blocker.

@@ -804,7 +805,7 @@ CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 from __future__ import annotations

-from dataclasses import dataclass
+from dataclasses import dataclass, field

 from django.contrib.auth import get_user_model
 from django.core.exceptions import ValidationError
@@ -888,7 +889,7 @@ class AccountDetailContext:
 class CreatedAccountResult:
     user: User
     username: str
-    temporary_password: str
+    temporary_password: str = field(repr=False)
     role: str
     role_label: str
     player: Player | None = None
@@ -1577,7 +1578,7 @@ from accounts.services.profile_service import get_or_create_account_profile


 def generate_birthdate_password(player) -> str:
-    """Return the temporary birthdate password for a player."""
+    """Return the temporary birthdate password for player-account provisioning only."""
     birthdate = getattr(player, "birthdate", None)
     if not birthdate:
         raise ValidationError("Player birthdate is required for account provisioning.")
@@ -2124,10 +2125,10 @@ def username_for_player(player) -> str:

 def validate_available_username(username: str) -> str:
     """Validate an explicitly supplied username and return the normalized value."""
-    cleaned = str(username or "").strip()
+    cleaned = str(username or "").strip().casefold()
     if not cleaned:
         raise ValidationError("Username is required.")
-    if USERNAME_ALLOWED_PATTERN.search(cleaned.casefold()):
+    if USERNAME_ALLOWED_PATTERN.search(cleaned):
         raise ValidationError("Username may contain only letters, numbers, dots, underscores, and hyphens.")
     if User.objects.filter(username__iexact=cleaned).exists():
         raise ValidationError("Username is already in use.")
@@ -2677,6 +2678,7 @@ FILE: /Users/eugenelin/dev/vmba0/accounts/tests.py
 CONTENT-TYPE: text/plain; charset=utf-8
 ----------------------------------------------------------------------------------------------------
 from django.contrib import admin
+from django.contrib.messages import get_messages
 from django.contrib.auth import get_user_model
 from django.conf import settings
 from django.core.exceptions import ValidationError
@@ -2984,7 +2986,7 @@ class AccountOperationsServiceTests(TestCase):
     def test_create_account_only_creates_user_profile_and_temporary_password(self):
         result = create_account_only(
             actor=self.staff,
-            username="new.coach",
+            username="New.Coach",
             first_name="New",
             last_name="Coach",
             email="New.Coach@example.com",
@@ -3000,10 +3002,12 @@ class AccountOperationsServiceTests(TestCase):
         self.assertEqual(result.role_label, "Coach")
         self.assertTrue(result.temporary_password)
         self.assertTrue(user.check_password(result.temporary_password))
+        self.assertNotIn(result.temporary_password, repr(result))
         self.assertEqual(user.email, "new.coach@example.com")
         self.assertEqual(profile.role, AccountRole.COACH)
         self.assertTrue(profile.must_change_password)
         self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
         self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())

     def test_create_account_only_can_create_inactive_account(self):
@@ -3061,11 +3065,14 @@ class AccountOperationsServiceTests(TestCase):
         self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
         self.assertTrue(link.is_primary)
         self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
+        self.assertFalse(link.created_from_import)
+        self.assertIsNone(link.import_batch)

     def test_create_player_account_accepts_optional_username_and_inactive_flag(self):
         player = Player.objects.create(first_name="Casey", last_name="Player", birthdate="2014-07-03")

-        result = create_player_account(actor=self.staff, player=player, username="custom.player", is_active=False)
+        result = create_player_account(actor=self.staff, player=player, username="Custom.Player", is_active=False)

         self.assertEqual(result.username, "custom.player")
         self.assertFalse(User.objects.get(username="custom.player").is_active)
@@ -3418,6 +3425,7 @@ class AccountUsernameServiceTests(TestCase):
         User.objects.create_user(username="coach.one")

         self.assertEqual(validate_available_username("new.user"), "new.user")
+        self.assertEqual(validate_available_username("  Coach.Two  "), "coach.two")
         with self.assertRaises(ValidationError):
             validate_available_username("coach.ONE")
         with self.assertRaises(ValidationError):
@@ -3951,10 +3959,18 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Account Created")
         self.assertContains(response, "Temporary password")
+        temporary_password = response.context["created_account"].temporary_password
+        self.assertIn(temporary_password, response.content.decode())
+        self.assertNotIn(temporary_password, " ".join(str(message) for message in get_messages(response.wsgi_request)))
         self.assertTrue(user.account_profile.must_change_password)
         self.assertEqual(user.account_profile.role, AccountRole.GUEST_EVALUATOR)
         self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())

+        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
+        self.assertNotContains(detail_response, temporary_password)
+        get_response = self.client.get(reverse("accounts:account-create"))
+        self.assertNotContains(get_response, temporary_password)
+
     def test_staff_cannot_create_admin_account(self):
         self.client.force_login(self.staff)

@@ -3969,6 +3985,7 @@ class AccountOperationsViewTests(TestCase):

         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Only superusers can create admin accounts")
+        self.assertNotContains(response, "Temporary password")
         self.assertFalse(User.objects.filter(username="admin.try").exists())

     def test_player_account_create_requires_staff(self):
@@ -3996,10 +4013,16 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(response.status_code, 200)
         self.assertContains(response, "Player Account Created")
         self.assertContains(response, "20130602")
+        self.assertNotIn("20130602", " ".join(str(message) for message in get_messages(response.wsgi_request)))
         self.assertTrue(user.check_password("20130602"))
         self.assertTrue(user.account_profile.must_change_password)
         self.assertEqual(UserPlayerLink.objects.get(user=user).player, player)

+        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
+        self.assertNotContains(detail_response, "20130602")
+        get_response = self.client.get(reverse("accounts:player-account-create"))
+        self.assertNotContains(get_response, "20130602")
+
     def test_player_account_create_rejects_duplicate_player_account(self):
         player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
         create_player_account(actor=self.staff, player=player)
```
