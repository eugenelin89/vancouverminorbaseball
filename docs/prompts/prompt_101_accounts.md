# Prompt 101 - Accounts

## User Prompt

```text
You are implementing a targeted fix to player account provisioning during CSV import.

Implement only the email-handling and provisioning behavior described below.

Do not redesign the broader import system.
Do not implement parent-account creation.
Do not implement a new authentication system.
Do not add unrelated features.

==================================================
Before Coding
==================================================

Read:

- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/account_management_v1.md
- AGENTS.md

Review:

- players/
- accounts/
- analytics/

Pay particular attention to:

- player CSV import services
- player account provisioning services
- username generation
- password generation
- UserPlayerLink creation
- import result models/read models
- import summary storage
- row-level import errors and warnings
- any current handling of `account_email` or equivalent fields

==================================================
Problem
==================================================

The current import workflow treats an imported email as part of provisioning a player self-account.

This causes two issues:

1. Players without an account email do not receive accounts when “Provision player accounts” is selected.

2. Sibling rows sharing the same parent or family email may create provisioning conflicts because the same email is treated as belonging uniquely to each player account.

In youth registrations, a registration or contact email often belongs to a parent, guardian, or family rather than the player.

The platform must not assume that a generic registration email is the player’s login email.

==================================================
Goal
==================================================

Allow player account provisioning to succeed even when:

- `player_login_email` is blank
- the supplied `player_login_email` is already used by another account

Username uniqueness remains the primary account-creation constraint.

Email assignment must not block creation of an otherwise valid player self-account.

==================================================
Terminology
==================================================

Use the concept:

    player_login_email

This means an email explicitly intended to belong to the player’s own login account.

Do not treat a generic registration, contact, parent, guardian, or family email as `player_login_email` unless staff explicitly maps or confirms it as such.

==================================================
Provisioning Rules
==================================================

Implement the following rules.

1. Blank player login email

If `player_login_email` is blank:

- still create the player account
- generate the username using the existing username policy
- generate the temporary password using the existing birthdate-based password policy
- leave the Django user email field blank
- create the normal player self-link
- preserve all existing activation and first-login password-change behavior

2. Unique player login email

If `player_login_email` is provided and is not already assigned to another account:

- create or reuse the player account according to existing provisioning rules
- assign the email to that user’s email field

3. Duplicate player login email

If `player_login_email` is already assigned to another account:

- do not block player account creation
- do not assign the duplicate email to the new player account
- create the player account with a blank email
- continue creating the normal player self-link
- record a non-blocking warning for staff review

4. Username conflicts

Username uniqueness remains the real account-creation constraint.

Continue using the existing username-generation and collision-resolution policy.

A duplicate email by itself must not be treated as a provisioning failure.

5. Existing linked accounts

Preserve all current idempotency and existing-account reuse rules.

Do not create duplicate player self-accounts or duplicate self-links.

==================================================
Import Mapping Rules
==================================================

Do not automatically map a generic CSV column such as:

- Email
- Contact Email
- Parent Email
- Guardian Email
- Family Email
- Registration Email

to `player_login_email`.

Only map an imported value to `player_login_email` when staff explicitly selects or confirms that the field belongs to the player.

For current CSV workflows, the safe default should be:

- map player identity and roster fields
- leave `player_login_email` blank unless staff is confident it belongs to the player
- provision the player account using username plus birthdate-derived temporary password
- handle parent/contact emails later as a separate account-linking problem

Do not implement the later parent/contact account-linking workflow in this phase.

==================================================
Warnings and Auditability
==================================================

When a duplicate `player_login_email` cannot be assigned, create a non-blocking warning.

The warning must:

- be visible in the immediate import result
- be included in the import summary
- be attached to the relevant imported row’s stored warnings/errors
- remain available for later staff review
- identify the player row clearly
- identify the email value that was not assigned
- explain that the player account was still created with a blank email

Suggested message:

    Player account was created, but the login email "<email>" was already assigned to another account and was not added.

Treat this as a warning, not an error.

It must not increase the failed-provisioning count if the account and player link were otherwise created successfully.

If the existing import result structure has no separate warning collection, extend it minimally and consistently rather than misclassifying the condition as a hard error.

Hide sensitive values such as temporary passwords from stored summaries and repr output.

==================================================
Service Architecture
==================================================

Keep business logic in the existing provisioning and import services.

Do not duplicate provisioning logic in views.

The account provisioning service should decide whether the email may be assigned.

The import service should:

- pass the explicit `player_login_email`
- receive the provisioning result
- surface and persist any non-blocking warnings
- continue processing remaining rows

Prefer a typed result/read model that can distinguish:

- account created
- account reused
- account linked
- email assigned
- email omitted
- warnings

Use existing public service methods wherever possible.

==================================================
UI
==================================================

Update the current import preview/result UI only as needed.

The UI should make clear that:

- player login email is optional
- blank login email does not prevent account creation
- duplicate login email produces a warning but does not prevent account creation
- registration/contact email should only be mapped as player login email when staff is confident it belongs to the player

Do not add JavaScript unless the existing workflow already requires it.

Keep the implementation server-rendered.

==================================================
Do Not Implement
==================================================

NO parent-account creation

NO guardian-account creation

NO family-account linking

NO email invitations

NO email verification

NO password-reset changes

NO authentication-provider integration

NO social login

NO broad import redesign

NO unrelated account-management changes

NO APIs

==================================================
Testing
==================================================

Add tests for at least:

1. Provision account with blank `player_login_email`
   - account is created
   - email is blank
   - username is generated
   - temporary password policy is preserved
   - player self-link is created

2. Provision account with unique `player_login_email`
   - account is created
   - email is assigned

3. Provision two sibling players with the same `player_login_email`
   - first account may receive the email
   - second account is still created
   - second account email is blank
   - both players have distinct usernames
   - both player self-links are created
   - second row has a non-blocking warning
   - import does not report the second provisioning as failed

4. Duplicate email warning persistence
   - warning appears in immediate result
   - warning appears in import summary
   - warning is stored against the relevant row
   - warning remains retrievable later

5. Blank email does not block bulk provisioning

6. Username conflict behavior remains unchanged

7. Existing account reuse remains idempotent

8. Generic contact email is not automatically treated as player login email

9. Temporary passwords are not stored in import summaries, row errors, logs, or repr output

Run:

- python manage.py check
- python manage.py makemigrations accounts players analytics --check
- python manage.py test accounts
- python manage.py test players
- python manage.py test analytics
- python manage.py test drafts
- python manage.py test pdp
- python manage.py test
- git diff --check

==================================================
Self Review
==================================================

Verify:

- player accounts are created when login email is blank
- duplicate login email does not block account creation
- duplicate email is not assigned to multiple player accounts
- username uniqueness remains the primary constraint
- generic contact email is not assumed to belong to the player
- warnings are visible immediately
- warnings are persisted in summary and row-level records
- warnings are non-blocking
- temporary passwords are not persisted or exposed
- existing idempotency rules remain intact
- no parent-account workflow was implemented
- no unrelated features were added

==================================================
Final Report
==================================================

Report:

- implementation summary
- files created
- files modified
- services expanded
- models or migrations added, if any
- import result changes
- warning persistence changes
- tests added
- full test results
- implementation decisions
- technical debt
- self-review
- confirmation that only this provisioning fix was implemented
```

## Implementation Commit Diff

```diff
commit 1f6bc2050897627b220d1193a3daa87525b30573
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Sat Jul 25 11:58:38 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Sat Jul 25 11:58:38 2026 -0700

    Allow player import accounts without unique email

diff --git a/accounts/services/provisioning_service.py b/accounts/services/provisioning_service.py
index f899f50..2a6e5c0 100644
--- a/accounts/services/provisioning_service.py
+++ b/accounts/services/provisioning_service.py
@@ -10,12 +10,17 @@ from django.db import transaction
 from accounts.models import AccountRole, UserPlayerLink, UserPlayerRelationship
 from accounts.services.email_service import find_existing_email_user, normalize_email
 from accounts.services.link_service import activate_link, link_user_to_player
-from accounts.services.password_service import mark_password_change_required, set_temporary_password
+from accounts.services.password_service import (
+    mark_password_change_required,
+    set_temporary_password,
+)
 from accounts.services.profile_service import get_or_create_account_profile
-from accounts.services.username_service import validate_available_username, username_for_player
+from accounts.services.username_service import (
+    username_for_player,
+    validate_available_username,
+)
 from players.models import Player, PlayerImportBatch
 
-
 User = get_user_model()
 
 STATUS_CREATED = "created"
@@ -40,6 +45,9 @@ class ProvisioningResult:
     username: str = ""
     user_id: int | None = None
     messages: list[str] = field(default_factory=list)
+    warnings: list[str] = field(default_factory=list)
+    email_assigned: bool = False
+    email_omitted: bool = False
 
     def to_dict(self) -> dict[str, Any]:
         return asdict(self)
@@ -55,6 +63,7 @@ class ProvisioningSummary:
     skipped: int = 0
     conflicts: int = 0
     messages: list[str] = field(default_factory=list)
+    warnings: list[str] = field(default_factory=list)
     results: list[ProvisioningResult] = field(default_factory=list)
 
     def add_result(self, result: ProvisioningResult) -> None:
@@ -70,6 +79,7 @@ class ProvisioningSummary:
         elif result.status == STATUS_CONFLICT:
             self.conflicts += 1
         self.messages.extend(result.messages)
+        self.warnings.extend(result.warnings)
 
     def to_dict(self) -> dict[str, Any]:
         return {
@@ -81,6 +91,7 @@ class ProvisioningSummary:
             "skipped": self.skipped,
             "conflicts": self.conflicts,
             "messages": list(self.messages),
+            "warnings": list(self.warnings),
         }
 
 
@@ -113,14 +124,18 @@ def _find_safe_email_user(player: Player, email: str):
         return None, None
     link = (
         UserPlayerLink.objects.select_related("user", "player")
-        .filter(user=email_user, player=player, relationship=UserPlayerRelationship.SELF)
+        .filter(
+            user=email_user, player=player, relationship=UserPlayerRelationship.SELF
+        )
         .order_by("-is_active", "-is_primary", "id")
         .first()
     )
     return email_user, link
 
 
-def _apply_import_profile_state(user, import_batch, *, set_player_role: bool, created_from_import: bool):
+def _apply_import_profile_state(
+    user, import_batch, *, set_player_role: bool, created_from_import: bool
+):
     profile = get_or_create_account_profile(user)
     update_fields = []
     if set_player_role and profile.role not in {AccountRole.ADMIN, AccountRole.STAFF}:
@@ -150,18 +165,17 @@ def _ensure_active_self_link(link, import_batch):
     return activate_link(link)
 
 
-def _safe_linked_user_result(player, link, import_batch, email: str, row_number: int | None) -> ProvisioningResult:
+def _safe_linked_user_result(
+    player, link, import_batch, email: str, row_number: int | None
+) -> ProvisioningResult:
     normalized_email = normalize_email(email)
     existing_email_user = find_existing_email_user(normalized_email)
+    warnings = []
+    email_assigned = False
+    email_omitted = False
     if existing_email_user and existing_email_user.id != link.user_id:
-        return ProvisioningResult(
-            player_id=player.id,
-            row_number=row_number,
-            status=STATUS_CONFLICT,
-            username=link.user.username,
-            user_id=link.user_id,
-            messages=[_row_message(row_number, "Email belongs to a different existing user; account not provisioned.")],
-        )
+        warnings.append(_duplicate_email_warning(row_number, normalized_email))
+        email_omitted = True
     try:
         link = _ensure_active_self_link(link, import_batch)
     except ValidationError as exc:
@@ -173,17 +187,32 @@ def _safe_linked_user_result(player, link, import_batch, email: str, row_number:
             user_id=link.user_id,
             messages=[_row_message(row_number, "; ".join(exc.messages))],
         )
-    if normalized_email and not link.user.email:
+    if normalized_email and not link.user.email and not email_omitted:
         link.user.email = normalized_email
         link.user.save(update_fields=["email"])
-    _apply_import_profile_state(link.user, import_batch, set_player_role=False, created_from_import=False)
+        email_assigned = True
+    _apply_import_profile_state(
+        link.user, import_batch, set_player_role=False, created_from_import=False
+    )
     return ProvisioningResult(
         player_id=player.id,
         row_number=row_number,
         status=STATUS_ALREADY_LINKED,
         username=link.user.username,
         user_id=link.user_id,
-        messages=[_row_message(row_number, "Player already has a linked user account.")],
+        messages=[
+            _row_message(row_number, "Player already has a linked user account.")
+        ],
+        warnings=warnings,
+        email_assigned=email_assigned,
+        email_omitted=email_omitted,
+    )
+
+
+def _duplicate_email_warning(row_number: int | None, email: str) -> str:
+    return _row_message(
+        row_number,
+        f'Player account was created, but the login email "{email}" was already assigned to another account and was not added.',
     )
 
 
@@ -204,7 +233,9 @@ def provision_player_account(
 
     existing_link = _find_existing_self_link(player)
     if existing_link:
-        return _safe_linked_user_result(player, existing_link, import_batch, normalized_email, row_number)
+        return _safe_linked_user_result(
+            player, existing_link, import_batch, normalized_email, row_number
+        )
 
     email_user, same_player_link = _find_safe_email_user(player, normalized_email)
     if email_user:
@@ -220,34 +251,44 @@ def provision_player_account(
                     user_id=email_user.id,
                     messages=[_row_message(row_number, "; ".join(exc.messages))],
                 )
-            _apply_import_profile_state(email_user, import_batch, set_player_role=False, created_from_import=False)
+            _apply_import_profile_state(
+                email_user,
+                import_batch,
+                set_player_role=False,
+                created_from_import=False,
+            )
             return ProvisioningResult(
                 player_id=player.id,
                 row_number=row_number,
                 status=STATUS_LINKED_EXISTING,
                 username=email_user.username,
                 user_id=email_user.id,
-                messages=[_row_message(row_number, "Existing linked email user reused.")],
+                messages=[
+                    _row_message(row_number, "Existing linked email user reused.")
+                ],
+                email_assigned=bool(normalized_email),
             )
-        return ProvisioningResult(
-            player_id=player.id,
-            row_number=row_number,
-            status=STATUS_CONFLICT,
-            username=email_user.username,
-            user_id=email_user.id,
-            messages=[_row_message(row_number, "Email belongs to an unrelated existing user; account not provisioned.")],
-        )
+        email_warning = _duplicate_email_warning(row_number, normalized_email)
+        normalized_email = ""
+    else:
+        email_warning = ""
 
     if not player.birthdate:
         return ProvisioningResult(
             player_id=player.id,
             row_number=row_number,
             status=STATUS_SKIPPED,
-            messages=[_row_message(row_number, "Missing birthdate; account not provisioned.")],
+            messages=[
+                _row_message(row_number, "Missing birthdate; account not provisioned.")
+            ],
         )
 
     try:
-        username = validate_available_username(username) if username else username_for_player(player)
+        username = (
+            validate_available_username(username)
+            if username
+            else username_for_player(player)
+        )
     except ValidationError as exc:
         return ProvisioningResult(
             player_id=player.id,
@@ -256,10 +297,17 @@ def provision_player_account(
             messages=[_row_message(row_number, "; ".join(exc.messages))],
         )
 
-    user = User.objects.create(username=username, email=normalized_email, is_active=activate_user)
+    user = User.objects.create(
+        username=username, email=normalized_email, is_active=activate_user
+    )
     set_temporary_password(user, player)
     created_from_import = bool(import_batch)
-    profile = _apply_import_profile_state(user, import_batch, set_player_role=True, created_from_import=created_from_import)
+    profile = _apply_import_profile_state(
+        user,
+        import_batch,
+        set_player_role=True,
+        created_from_import=created_from_import,
+    )
     if not profile.must_change_password:
         mark_password_change_required(user, True)
     link_user_to_player(
@@ -277,6 +325,9 @@ def provision_player_account(
         username=user.username,
         user_id=user.id,
         messages=[_row_message(row_number, "Player account provisioned.")],
+        warnings=[email_warning] if email_warning else [],
+        email_assigned=bool(normalized_email),
+        email_omitted=bool(email_warning),
     )
 
 
@@ -297,7 +348,9 @@ def provision_accounts_for_import(
     """Provision accounts for committed player import rows."""
     _validate_import_batch(import_batch)
     options = options or ProvisioningOptions()
-    summary = ProvisioningSummary(enabled=options.enabled, activate_users=options.activate_users)
+    summary = ProvisioningSummary(
+        enabled=options.enabled, activate_users=options.activate_users
+    )
     if not options.enabled:
         return summary
 
diff --git a/accounts/tests/test_account_services.py b/accounts/tests/test_account_services.py
index a6aea56..288ae10 100644
--- a/accounts/tests/test_account_services.py
+++ b/accounts/tests/test_account_services.py
@@ -192,6 +192,26 @@ class AccountProvisioningServiceTests(TestCase):
         self.assertTrue(link.created_from_import)
         self.assertEqual(link.import_batch, self.import_batch)
 
+    def test_provision_player_account_allows_blank_login_email(self):
+        result = provision_player_account(
+            self.player,
+            import_batch=self.import_batch,
+            actor=self.staff,
+            row_number=2,
+        )
+
+        user = User.objects.get(username="jose.garcia")
+        self.assertEqual(result.status, STATUS_CREATED)
+        self.assertEqual(user.email, "")
+        self.assertFalse(result.email_assigned)
+        self.assertFalse(result.email_omitted)
+        self.assertTrue(user.check_password("20120501"))
+        self.assertTrue(
+            UserPlayerLink.objects.filter(
+                user=user, player=self.player, relationship=UserPlayerRelationship.SELF
+            ).exists()
+        )
+
     def test_provision_player_account_can_activate_user_when_explicit(self):
         result = provision_player_account(
             self.player, import_batch=self.import_batch, activate_user=True
@@ -316,15 +336,29 @@ class AccountProvisioningServiceTests(TestCase):
             1,
         )
 
-    def test_provision_player_account_conflicts_on_unrelated_email(self):
+    def test_provision_player_account_omits_duplicate_email_without_blocking_account(
+        self,
+    ):
         User.objects.create_user(username="other", email="player@example.com")
 
         result = provision_player_account(
-            self.player, import_batch=self.import_batch, email="PLAYER@example.com"
+            self.player,
+            import_batch=self.import_batch,
+            email="PLAYER@example.com",
+            row_number=2,
         )
 
-        self.assertEqual(result.status, STATUS_CONFLICT)
-        self.assertFalse(UserPlayerLink.objects.filter(player=self.player).exists())
+        user = User.objects.get(username="jose.garcia")
+        self.assertEqual(result.status, STATUS_CREATED)
+        self.assertEqual(result.user_id, user.id)
+        self.assertEqual(user.email, "")
+        self.assertFalse(result.email_assigned)
+        self.assertTrue(result.email_omitted)
+        self.assertIn("login email", result.warnings[0])
+        self.assertIn("player@example.com", result.warnings[0])
+        self.assertTrue(
+            UserPlayerLink.objects.filter(player=self.player, user=user).exists()
+        )
 
     def test_provision_player_account_does_not_downgrade_existing_staff_link(self):
         staff_profile = get_or_create_account_profile(self.staff)
@@ -362,9 +396,38 @@ class AccountProvisioningServiceTests(TestCase):
         self.assertIsInstance(summary, ProvisioningSummary)
         self.assertEqual(serialized["users_created"], 1)
         self.assertEqual(serialized["already_linked"], 0)
+        self.assertEqual(serialized["warnings"], [])
         self.assertNotIn("20120501", str(serialized))
         self.assertNotIn("password", str(serialized).casefold())
 
+    def test_provisioning_summary_records_duplicate_email_warning_without_conflict(
+        self,
+    ):
+        User.objects.create_user(username="other", email="family@example.com")
+
+        summary = provision_accounts_for_import(
+            self.import_batch,
+            [
+                {
+                    "player": self.player,
+                    "row_number": 2,
+                    "original_row": {"Email": "family@example.com"},
+                }
+            ],
+            actor=self.staff,
+            options=ProvisioningOptions(
+                enabled=True, activate_users=True, email_column="Email"
+            ),
+        )
+
+        serialized = summary.to_dict()
+        user = User.objects.get(username="jose.garcia")
+        self.assertEqual(summary.users_created, 1)
+        self.assertEqual(summary.conflicts, 0)
+        self.assertEqual(user.email, "")
+        self.assertEqual(len(serialized["warnings"]), 1)
+        self.assertIn("family@example.com", serialized["warnings"][0])
+
 
 class AccountRegressionTests(TestCase):
     def test_phase_two_creates_user_player_link_but_no_provisioning_models(self):
diff --git a/analytics/forms.py b/analytics/forms.py
index ea7f7e0..c78e4d2 100644
--- a/analytics/forms.py
+++ b/analytics/forms.py
@@ -6,14 +6,21 @@ from seasons.services.season_service import get_current_season
 
 
 class PlayerImportUploadForm(forms.Form):
-    season = forms.ModelChoiceField(queryset=Season.objects.none(), help_text="Choose the season for this roster import.")
-    csv_file = forms.FileField(help_text="Upload a player member-list or roster-detail CSV.")
+    season = forms.ModelChoiceField(
+        queryset=Season.objects.none(),
+        help_text="Choose the season for this roster import.",
+    )
+    csv_file = forms.FileField(
+        help_text="Upload a player member-list or roster-detail CSV."
+    )
     source = forms.ChoiceField(choices=SOURCE_CHOICES)
     provision_player_accounts = forms.BooleanField(required=False, initial=False)
 
     def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
-        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by("-is_current", "-starts_on", "name")
+        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by(
+            "-is_current", "-starts_on", "name"
+        )
         current = get_current_season()
         if current and current.is_active:
             self.fields["season"].initial = current
@@ -44,7 +51,15 @@ class PlayerImportMappingForm(forms.Form):
     registrant_id = forms.ChoiceField(required=False)
     team_id = forms.ChoiceField(required=False)
     source_player_id = forms.ChoiceField(required=False)
-    account_email = forms.ChoiceField(required=False)
+    account_email = forms.ChoiceField(
+        required=False,
+        label="Player login email",
+        help_text=(
+            "Optional. Map only when the email belongs to the player's own login "
+            "account. Leave blank for registration, parent, guardian, or family "
+            "contact emails."
+        ),
+    )
     roster_status = forms.ChoiceField(required=False)
     jersey_number = forms.ChoiceField(required=False)
     membership_start_date = forms.ChoiceField(required=False)
@@ -61,8 +76,12 @@ class PlayerImportMappingForm(forms.Form):
 
     def clean(self):
         cleaned_data = super().clean()
-        if not cleaned_data.get("full_name") and not (cleaned_data.get("first_name") and cleaned_data.get("last_name")):
-            raise forms.ValidationError("Map either full name or both first and last name.")
+        if not cleaned_data.get("full_name") and not (
+            cleaned_data.get("first_name") and cleaned_data.get("last_name")
+        ):
+            raise forms.ValidationError(
+                "Map either full name or both first and last name."
+            )
         return cleaned_data
 
     def mapping_config(self):
@@ -77,8 +96,12 @@ def parse_conflict_resolutions(post_data):
             resolutions.setdefault(row_number, {"fields": {}})["action"] = value
         elif key.startswith("row_") and key.endswith("_candidate"):
             row_number = key.removeprefix("row_").removesuffix("_candidate")
-            resolutions.setdefault(row_number, {"action": "commit", "fields": {}})["candidate_id"] = value
+            resolutions.setdefault(row_number, {"action": "commit", "fields": {}})[
+                "candidate_id"
+            ] = value
         elif key.startswith("row_") and "_field_" in key:
             row_part, field_name = key.removeprefix("row_").split("_field_", 1)
-            resolutions.setdefault(row_part, {"action": "commit", "fields": {}})["fields"][field_name] = value
+            resolutions.setdefault(row_part, {"action": "commit", "fields": {}})[
+                "fields"
+            ][field_name] = value
     return resolutions
diff --git a/analytics/templates/analytics/import_detail.html b/analytics/templates/analytics/import_detail.html
index 18973c0..26cf458 100644
--- a/analytics/templates/analytics/import_detail.html
+++ b/analytics/templates/analytics/import_detail.html
@@ -41,6 +41,14 @@
                 {% endfor %}
             </ul>
         {% endif %}
+        {% if import_batch.import_summary.account_provisioning.warnings %}
+            <h4>Warnings</h4>
+            <ul>
+                {% for warning in import_batch.import_summary.account_provisioning.warnings %}
+                    <li>{{ warning }}</li>
+                {% endfor %}
+            </ul>
+        {% endif %}
     {% endif %}
     <a class="button button--ghost" href="{% url 'analytics:import-list' %}">Back to Imports</a>
 </article>
diff --git a/analytics/templates/analytics/import_preview.html b/analytics/templates/analytics/import_preview.html
index 84c7ce5..1ca09ed 100644
--- a/analytics/templates/analytics/import_preview.html
+++ b/analytics/templates/analytics/import_preview.html
@@ -19,7 +19,9 @@
     {% if preview.account_provisioning.enabled %}
         <p>
             Account provisioning enabled; new accounts will be activated immediately and must change password on first login.
-            {% if preview.account_provisioning.email_column %}Email column: {{ preview.account_provisioning.email_column }}.{% endif %}
+            Player login email is optional. Leave it blank unless the mapped email belongs to the player's own login account.
+            Duplicate login emails create accounts with blank email and a staff warning.
+            {% if preview.account_provisioning.email_column %}Player login email column: {{ preview.account_provisioning.email_column }}.{% endif %}
         </p>
     {% endif %}
     {% if preview.summary %}
diff --git a/players/services/imports/commit.py b/players/services/imports/commit.py
index 07a6823..a7b444c 100644
--- a/players/services/imports/commit.py
+++ b/players/services/imports/commit.py
@@ -366,6 +366,7 @@ def commit_import_batch(
             ),
         )
         result.account_provisioning = provisioning_summary.to_dict()
+        result.warnings.extend(provisioning_summary.warnings)
 
     locked_batch.status = PlayerImportStatus.COMMITTED
     locked_batch.rows_created = result.created
@@ -373,7 +374,7 @@ def commit_import_batch(
     locked_batch.rows_skipped = result.skipped
     locked_batch.rows_conflicted = result.conflicts
     locked_batch.import_summary = asdict(result)
-    locked_batch.row_errors = result.errors
+    locked_batch.row_errors = [*result.errors, *result.warnings]
     locked_batch.committed_at = timezone.now()
     locked_batch.save(
         update_fields=[
diff --git a/players/services/imports/result_models.py b/players/services/imports/result_models.py
index 31e72a9..6ef1797 100644
--- a/players/services/imports/result_models.py
+++ b/players/services/imports/result_models.py
@@ -74,4 +74,5 @@ class ImportCommitResult:
     memberships_created: int = 0
     memberships_updated: int = 0
     errors: list[str] = field(default_factory=list)
+    warnings: list[str] = field(default_factory=list)
     account_provisioning: dict[str, Any] = field(default_factory=dict)
diff --git a/players/tests/test_import_workflow.py b/players/tests/test_import_workflow.py
index 89513dc..5f652ea 100644
--- a/players/tests/test_import_workflow.py
+++ b/players/tests/test_import_workflow.py
@@ -604,7 +604,7 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertFalse(User.objects.filter(username="eugene.lin").exists())
         self.assertEqual(batch.import_summary["account_provisioning"]["skipped"], 1)
 
-    def test_commit_with_provisioning_reports_duplicate_unrelated_email_conflict(self):
+    def test_commit_with_provisioning_omits_duplicate_email_but_creates_account(self):
         User.objects.create_user(username="existing", email="eugene@example.com")
         batch = create_import_batch(
             file_obj=self.upload(
@@ -625,5 +625,66 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertTrue(
             Player.objects.filter(first_name="Eugene", last_name="Lin").exists()
         )
-        self.assertFalse(User.objects.filter(username="eugene.lin").exists())
-        self.assertEqual(batch.import_summary["account_provisioning"]["conflicts"], 1)
+        user = User.objects.get(username="eugene.lin")
+        self.assertEqual(user.email, "")
+        self.assertTrue(
+            UserPlayerLink.objects.filter(
+                user=user,
+                player__first_name="Eugene",
+                player__last_name="Lin",
+                relationship="self",
+            ).exists()
+        )
+        account_summary = batch.import_summary["account_provisioning"]
+        self.assertEqual(account_summary["users_created"], 1)
+        self.assertEqual(account_summary["conflicts"], 0)
+        self.assertEqual(len(account_summary["warnings"]), 1)
+        self.assertIn("eugene@example.com", account_summary["warnings"][0])
+        self.assertIn(account_summary["warnings"][0], batch.row_errors)
+
+    def test_commit_with_provisioning_allows_sibling_rows_sharing_login_email(self):
+        batch = create_import_batch(
+            file_obj=self.upload(
+                body=(
+                    b"First,Last,DOB,Email,Division,Team\n"
+                    b"Boaz,Singerman,2013-03-31,family@example.com,13U,Dodgers\n"
+                    b"Shael,Singerman,2013-03-31,family@example.com,13U,Dodgers\n"
+                )
+            ),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            provision_player_accounts=True,
+            season=self.season,
+        )
+        mapping = dict(batch.mapping_config)
+        mapping["account_email"] = "Email"
+        build_import_preview(import_batch=batch, mapping_config=mapping)
+
+        commit_import_batch(import_batch=batch, actor=self.staff)
+
+        batch.refresh_from_db()
+        boaz = User.objects.get(username="boaz.singerman")
+        shael = User.objects.get(username="shael.singerman")
+        self.assertEqual(boaz.email, "family@example.com")
+        self.assertEqual(shael.email, "")
+        self.assertEqual(UserPlayerLink.objects.filter(user=boaz).count(), 1)
+        self.assertEqual(UserPlayerLink.objects.filter(user=shael).count(), 1)
+        account_summary = batch.import_summary["account_provisioning"]
+        self.assertEqual(account_summary["users_created"], 2)
+        self.assertEqual(account_summary["conflicts"], 0)
+        self.assertEqual(len(account_summary["warnings"]), 1)
+        self.assertIn("family@example.com", account_summary["warnings"][0])
+        self.assertNotIn("20130331", str(batch.import_summary))
+
+    def test_generic_email_header_is_not_auto_mapped_as_player_login_email(self):
+        batch = create_import_batch(
+            file_obj=self.upload(
+                body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"
+            ),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            provision_player_accounts=True,
+            season=self.season,
+        )
+
+        self.assertNotIn("account_email", batch.mapping_config)
```
