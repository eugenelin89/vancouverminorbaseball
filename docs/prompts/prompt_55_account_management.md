# Prompt 55 - Account Management

## User Prompt

```text
Perform Evaluation Access V1 Phase 1 Coach Import review fixes only.

Do NOT implement Phase 2, 3, 4, 5, or 6.

Do NOT change Analytics evaluation permissions.

Do NOT implement evaluation submission, My Evaluations, coach review, portals, audit logging, invitations, email verification, APIs, JavaScript, coach-to-player links, Coach model, or persistent coach import batch model.

Goal:
Review the completed Coach Import implementation for correctness, security, one-time password safety, UX clarity, and documentation consistency.

Read:
- docs/ARCHITECTURE.md
- docs/USER_MANUAL.md
- docs/evaluations/implementation/engineering/evaluation_access_v1.md
- docs/account_management/V1_SUMMARY.md
- AGENTS.md

Review:
- accounts/services/coach_import_service.py
- accounts/forms.py
- accounts/views.py
- accounts/urls.py
- accounts/templates/accounts/coach_import_*.html
- accounts/templates/accounts/operations_dashboard.html
- accounts/tests.py

==================================================
Required Review Areas
==================================================

1. Session safety

Verify:
- CSV text may be stored temporarily in session between upload/preview/confirm.
- Temporary passwords are never stored in session.
- Temporary passwords are only created during confirm.
- Temporary passwords are only present in the immediate result response.
- After confirm, session CSV is removed.
- Refreshing/opening import pages later does not redisplay temporary passwords.

Add or strengthen tests if needed.

--------------------------------------------------

2. Existing coach reuse behavior

Existing coach email reuse currently resets that coach's password.

Confirm this behavior is intentional and safe.

Make the UI/documentation explicit:
- Rows marked "reuse" will reuse the existing coach account.
- Confirming the import will reset the existing coach's temporary password.
- The coach must change password on next login.

Add or strengthen tests proving:
- reused coach gets a new temporary password
- reused coach must_change_password=True
- reused coach remains coach
- plaintext temporary password is shown only in the immediate result response

--------------------------------------------------

3. Metadata preservation

Review how `team`, `division`, `notes`, and `source_id` are merged into `AccountProfile.metadata`.

Ensure:
- blank CSV fields do not wipe existing metadata
- metadata remains a dict
- manual/import provenance fields are not changed incorrectly
- no plaintext passwords are stored in metadata

Add tests if needed.

--------------------------------------------------

4. Result row state

Review the result summary logic.

If counts depend on string messages like "active" or "inactive", replace that with an explicit boolean field on the result row, such as:

- is_active: bool

Then update summary counts and tests.

Do not change user-facing behavior except improving correctness/clarity.

--------------------------------------------------

5. Username and email handling

Verify:
- explicit usernames use `username_service`
- generated usernames use `username_for_person`
- duplicate generated usernames within the same CSV cannot collide
- duplicate explicit usernames within the same CSV are caught
- duplicate emails within the same CSV are caught
- email normalization is consistent

Add tests if missing.

--------------------------------------------------

6. Permissions

Verify:
- only Django staff/superusers can access coach import pages
- service layer enforces staff actor
- `AccountProfile.role = staff` alone does not grant access
- importing coaches never grants Django `is_staff` or `is_superuser`

Add tests if needed.

--------------------------------------------------

7. User manual update

Update `docs/USER_MANUAL.md` to include coach import as an available Account Operations workflow.

Keep it user-facing and operational.

Mention:
- required CSV columns
- optional CSV columns
- preview/confirm workflow
- existing coach reuse behavior
- one-time temporary password display
- no player records or player links are created by coach import

--------------------------------------------------

8. Engineering plan status

Update `docs/evaluations/implementation/engineering/evaluation_access_v1.md` only if needed.

Phase 1 should be marked implemented only if the review fixes confirm it is acceptable.

Do not rewrite the plan.

==================================================
Do NOT Implement
==================================================

Do NOT implement:
- Analytics permission changes
- player evaluation submission
- player My Evaluations
- coach evaluation review
- coach-to-player links
- Coach model
- persistent coach import batch model
- audit logging
- invitations
- emails
- APIs
- JavaScript

==================================================
Verification
==================================================

Run:
- python manage.py check
- python manage.py makemigrations accounts --check
- python manage.py test accounts
- python manage.py test analytics
- python manage.py test players
- python manage.py test drafts
- python manage.py test pdp
- python manage.py test
- git diff --check

==================================================
Prompt Archive / Commit
==================================================

Create the next prompt record in docs/prompts/ according to AGENTS.md.

Commit implementation/documentation review fixes first.

Commit the prompt archive separately.

Push both commits.

==================================================
Final Report
==================================================

Report:
- issues found
- fixes applied
- files modified
- tests added/updated
- documentation updated
- test results
- implementation decisions
- remaining technical debt
- confirmation that this was Phase 1 review-fix only
- confirmation that Phase 2+ were NOT implemented
```

## Resulting Commit

```text
2f5420c Apply coach import review fixes
```

## Commit Diff

```diff
commit 2f5420cb7b947245393529666f359a3b716ca5a3
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 8 18:47:00 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 8 18:47:00 2026 -0700

    Apply coach import review fixes
---
 accounts/services/coach_import_service.py          | 15 ++++--
 .../templates/accounts/coach_import_preview.html   |  3 +-
 .../templates/accounts/coach_import_result.html    |  4 +-
 accounts/tests.py                                  | 57 ++++++++++++++++++++++
 docs/USER_MANUAL.md                                | 37 ++++++++++++++
 .../engineering/evaluation_access_v1.md            |  4 +-
 6 files changed, 113 insertions(+), 7 deletions(-)

diff --git a/accounts/services/coach_import_service.py b/accounts/services/coach_import_service.py
index bc536ed..a5ba666 100644
--- a/accounts/services/coach_import_service.py
+++ b/accounts/services/coach_import_service.py
@@ -97,6 +97,7 @@ class CoachImportResultRow:
     status: str
     username: str = ""
     user_id: int | None = None
+    is_active: bool = False
     temporary_password: str = field(default="", repr=False)
     messages: list[str] = field(default_factory=list)
 
@@ -131,11 +132,11 @@ class CoachImportResult:
 
     @property
     def active_accounts(self) -> int:
-        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and "inactive" not in row.messages)
+        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and row.is_active)
 
     @property
     def inactive_accounts(self) -> int:
-        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and "inactive" in row.messages)
+        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and not row.is_active)
 
     @property
     def password_change_required(self) -> int:
@@ -354,11 +355,15 @@ def _metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
     }
 
 
+def _profile_metadata(profile) -> dict:
+    return profile.metadata if isinstance(profile.metadata, dict) else {}
+
+
 @transaction.atomic
 def _reuse_existing_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
     user = User.objects.select_for_update().select_related("account_profile").get(pk=row.existing_user_id)
     profile = set_account_role(user, AccountRole.COACH)
-    metadata = {**profile.metadata, **_metadata_for_row(row)}
+    metadata = {**_profile_metadata(profile), **_metadata_for_row(row)}
     profile.metadata = metadata
     profile.must_change_password = True
     profile.save(update_fields=["metadata", "must_change_password", "updated_at"])
@@ -374,6 +379,7 @@ def _reuse_existing_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
         status=RESULT_REUSED,
         username=user.username,
         user_id=user.id,
+        is_active=user.is_active,
         temporary_password=temporary_password,
         messages=[status_message],
     )
@@ -391,7 +397,7 @@ def _create_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
     temporary_password = set_random_temporary_password(user)
     profile = set_account_role(user, AccountRole.COACH)
     profile.must_change_password = True
-    profile.metadata = {**profile.metadata, **_metadata_for_row(row)}
+    profile.metadata = {**_profile_metadata(profile), **_metadata_for_row(row)}
     profile.save(update_fields=["must_change_password", "metadata", "updated_at"])
     status_message = "inactive" if not user.is_active else "active"
     return CoachImportResultRow(
@@ -399,6 +405,7 @@ def _create_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
         status=RESULT_CREATED,
         username=user.username,
         user_id=user.id,
+        is_active=user.is_active,
         temporary_password=temporary_password,
         messages=[status_message],
     )
diff --git a/accounts/templates/accounts/coach_import_preview.html b/accounts/templates/accounts/coach_import_preview.html
index c908df5..eb0121b 100644
--- a/accounts/templates/accounts/coach_import_preview.html
+++ b/accounts/templates/accounts/coach_import_preview.html
@@ -65,7 +65,8 @@
 
     <article class="pdp-card">
         <h2>Confirm</h2>
-        <p>Only rows marked ready or reuse will be processed. Temporary passwords are shown once on the result page.</p>
+        <p>Only rows marked ready or reuse will be processed. Rows marked reuse will use the existing coach account and reset that coach's temporary password. The coach must change the password on next login.</p>
+        <p>Temporary passwords are shown once on the result page.</p>
         <form method="post" action="{% url 'accounts:coach-import-confirm' %}" class="pdp-form">
             {% csrf_token %}
             <label>
diff --git a/accounts/templates/accounts/coach_import_result.html b/accounts/templates/accounts/coach_import_result.html
index db9e86d..cef292e 100644
--- a/accounts/templates/accounts/coach_import_result.html
+++ b/accounts/templates/accounts/coach_import_result.html
@@ -29,6 +29,7 @@
                         <th>Row</th>
                         <th>Status</th>
                         <th>Username</th>
+                        <th>Active</th>
                         <th>Temporary password</th>
                         <th>Messages</th>
                     </tr>
@@ -45,6 +46,7 @@
                                     {{ row.username|default:"-" }}
                                 {% endif %}
                             </td>
+                            <td>{% if row.user_id %}{{ row.is_active|yesno:"Yes,No" }}{% else %}-{% endif %}</td>
                             <td><strong>{{ row.temporary_password|default:"-" }}</strong></td>
                             <td>
                                 {% for message in row.messages %}
@@ -55,7 +57,7 @@
                             </td>
                         </tr>
                     {% empty %}
-                        <tr><td colspan="5">No rows processed.</td></tr>
+                        <tr><td colspan="6">No rows processed.</td></tr>
                     {% endfor %}
                 </tbody>
             </table>
diff --git a/accounts/tests.py b/accounts/tests.py
index 96eec66..56472c3 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -1622,6 +1622,7 @@ class CoachImportServiceTests(TestCase):
 
         user = User.objects.get(username="inactive.coach")
         self.assertFalse(user.is_active)
+        self.assertFalse(result.rows[0].is_active)
         self.assertEqual(result.inactive_accounts, 1)
 
     def test_explicit_username_is_normalized_and_validated(self):
@@ -1647,6 +1648,7 @@ class CoachImportServiceTests(TestCase):
     def test_duplicate_email_with_existing_coach_reuses_account(self):
         existing = User.objects.create_user(username="existing.coach", email="coach@example.com", password="oldpass")
         set_account_role(existing, AccountRole.COACH)
+        original_password_hash = existing.password
 
         result = commit_coach_import(
             self.staff,
@@ -1659,6 +1661,8 @@ class CoachImportServiceTests(TestCase):
         self.assertEqual(User.objects.filter(email__iexact="coach@example.com").count(), 1)
         self.assertTrue(existing.account_profile.must_change_password)
         self.assertTrue(existing.check_password(result.rows[0].temporary_password))
+        self.assertNotEqual(existing.password, original_password_hash)
+        self.assertEqual(existing.account_profile.role, AccountRole.COACH)
 
     def test_duplicate_email_with_non_coach_conflicts(self):
         existing = User.objects.create_user(username="player.user", email="shared@example.com")
@@ -1684,6 +1688,44 @@ class CoachImportServiceTests(TestCase):
         self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
         self.assertFalse(User.objects.filter(email="taken@example.com").exists())
 
+    def test_duplicate_email_and_username_within_same_csv_conflict(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(
+                [
+                    "First,Coach,first@example.com,same.username,,,,,",
+                    "Second,Coach,first@example.com,other.username,,,,,",
+                    "Third,Coach,third@example.com,same.username,,,,,",
+                ]
+            ),
+        )
+
+        self.assertEqual(result.users_created, 1)
+        self.assertEqual(result.conflicts, 2)
+        self.assertTrue(User.objects.filter(email="first@example.com").exists())
+        self.assertFalse(User.objects.filter(email="third@example.com").exists())
+
+    def test_blank_csv_fields_do_not_wipe_existing_metadata(self):
+        existing = User.objects.create_user(username="metadata.coach", email="metadata@example.com")
+        profile = set_account_role(existing, AccountRole.COACH)
+        profile.metadata = {"team": "Reds", "division": "13U", "notes": "Keep this", "custom": "value"}
+        profile.save(update_fields=["metadata", "updated_at"])
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Metadata,Coach,metadata@example.com,,,,,,"]),
+        )
+
+        profile.refresh_from_db()
+        self.assertEqual(result.rows[0].status, RESULT_REUSED)
+        self.assertEqual(profile.metadata["team"], "Reds")
+        self.assertEqual(profile.metadata["division"], "13U")
+        self.assertEqual(profile.metadata["notes"], "Keep this")
+        self.assertEqual(profile.metadata["custom"], "value")
+        self.assertNotIn(result.rows[0].temporary_password, str(profile.metadata))
+        self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
+
     def test_missing_required_fields_produce_row_errors(self):
         preview = preview_coach_import("first_name,last_name,email\nMissing,Email,\n")
         result = commit_coach_import(self.staff, "first_name,last_name,email\nMissing,Email,\n")
@@ -2336,11 +2378,18 @@ class AccountOperationsViewTests(TestCase):
         self.assertTrue(user.is_active)
         self.assertEqual(user.account_profile.role, AccountRole.COACH)
         self.assertTrue(user.account_profile.must_change_password)
+        self.assertFalse(user.is_staff)
+        self.assertFalse(user.is_superuser)
         self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
         self.assertEqual(Player.objects.count(), 1)
+        self.assertNotIn("coach_import_csv", self.client.session)
 
         detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
         self.assertNotContains(detail_response, temporary_password)
+        list_response = self.client.get(reverse("accounts:coach-import-list"))
+        self.assertNotContains(list_response, temporary_password)
+        preview_again = self.client.get(reverse("accounts:coach-import-preview"))
+        self.assertEqual(preview_again.status_code, 302)
         confirm_again = self.client.get(reverse("accounts:coach-import-confirm"))
         self.assertEqual(confirm_again.status_code, 302)
 
@@ -2367,9 +2416,17 @@ class AccountOperationsViewTests(TestCase):
         result = response.context["result"]
         self.assertEqual(result.existing_coaches_reused, 1)
         self.assertEqual(result.conflicts, 1)
+        temporary_password = result.rows[0].temporary_password
+        existing_coach.refresh_from_db()
+        self.assertTrue(existing_coach.check_password(temporary_password))
+        self.assertTrue(existing_coach.account_profile.must_change_password)
+        self.assertEqual(existing_coach.account_profile.role, AccountRole.COACH)
         self.assertEqual(User.objects.filter(email__iexact="existing@example.com").count(), 1)
         self.assertEqual(User.objects.filter(email__iexact="player@example.com").count(), 1)
 
+        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": existing_coach.id}))
+        self.assertNotContains(detail_response, temporary_password)
+
 
 class AccountPasswordMiddlewareTests(TestCase):
     def setUp(self):
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 1ba6a58..66aeed3 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -130,6 +130,7 @@ Staff Account Operations includes:
 - account search, list, and detail pages
 - account-only creation for coaches, parents, guest evaluators, staff-role metadata users, and other non-player accounts
 - player account creation from an existing player record
+- coach account import from CSV
 - account activation and deactivation
 - username, email, and platform role editing
 - user-player link management
@@ -158,6 +159,42 @@ Use this only when the player already exists in the player database.
 
 Temporary passwords are shown once immediately after account creation. They are not shown again on the account detail page.
 
+### Importing Coach Accounts
+
+Staff can import coach accounts from:
+
+```text
+/accounts/imports/coaches/
+```
+
+Coach import uses a preview and confirm workflow:
+
+1. Upload a coach CSV file.
+2. Review the preview for rows to create, existing coach accounts to reuse, conflicts, and row errors.
+3. Confirm the import.
+4. Copy temporary passwords from the result page immediately.
+
+Required CSV columns:
+
+- first_name
+- last_name
+- email
+
+Optional CSV columns:
+
+- username
+- team
+- division
+- is_active
+- notes
+- source_id
+
+If an imported row uses the email address of an existing coach account, the system reuses that coach account. Confirming the import resets that coach's temporary password, and the coach must change the password on next login.
+
+Temporary passwords are shown only once on the immediate result page. They are not stored on the account detail page or in account metadata.
+
+Coach import creates or reuses coach login accounts only. It does not create player records and does not create coach-to-player links.
+
 ### Editing Accounts
 
 Staff can open an account detail page from the account list:
diff --git a/docs/evaluations/implementation/engineering/evaluation_access_v1.md b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
index e67efd4..6145e20 100644
--- a/docs/evaluations/implementation/engineering/evaluation_access_v1.md
+++ b/docs/evaluations/implementation/engineering/evaluation_access_v1.md
@@ -927,7 +927,7 @@ Purpose:
 Deliverables:
 
 - `accounts.services.coach_import_service`;
-- staff-only coach import upload/preview/confirm/detail workflow;
+- staff-only coach import upload/preview/confirm/result workflow without a persistent import batch model;
 - account creation with `AccountProfile.role = coach`;
 - username/email duplicate handling;
 - random temporary password generation;
@@ -935,6 +935,8 @@ Deliverables:
 - import summary without plaintext password persistence;
 - tests.
 
+Status: implemented.
+
 ### Phase 2: Evaluation Permission And Role Snapshot Updates
 
 Purpose:
```
