# Prompt 102 - Accounts

## User Prompt

```text
You are implementing a small follow-up cleanup to the recently completed player account provisioning fix.

Implement only the two issues described below.

Do not redesign the import system.
Do not change the provisioning policy.
Do not add parent-account functionality.
Do not add unrelated features.

==================================================
Before Coding
==================================================

Read:

- docs/ARCHITECTURE.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/account_management_v1.md
- docs/prompts/prompt_101_accounts.md
- AGENTS.md

Review:

- accounts/services/provisioning_service.py
- players/services/imports/commit.py
- players/services/imports/result_models.py
- analytics/templates/analytics/import_detail.html
- analytics/templates/analytics/import_preview.html
- accounts/tests/test_account_services.py
- players/tests/test_import_workflow.py

The existing behavior from Prompt 101 must remain intact:

- blank player login email does not block provisioning
- duplicate player login email does not block provisioning
- duplicate email is omitted from the new account
- username remains the actual account-creation constraint
- warnings remain non-blocking
- generic contact email is not automatically treated as player login email

==================================================
Issue 1: Warning Text Is Sometimes Inaccurate
==================================================

The current duplicate-email warning always says:

    Player account was created...

That wording is inaccurate when the player already had an existing linked account and the system merely left that account unchanged.

Update the warning generation so it accurately reflects the provisioning outcome.

Required behavior:

1. Newly created account

Use wording similar to:

    Player account was created, but the login email "<email>" was already assigned to another account and was not added. The new account has a blank email.

2. Existing linked account

Use wording similar to:

    The login email "<email>" was already assigned to another account and was not added to the existing player account. The existing account was left unchanged.

The exact wording may vary slightly, but it must never claim an account was created when no account was created.

Keep warning generation centralized in the provisioning service.

A helper may accept context such as:

- account_created=True/False
- result status
- existing account vs new account

Do not duplicate warning text across multiple branches.

==================================================
Issue 2: Do Not Persist Warnings as Row Errors
==================================================

The current import commit logic stores warnings inside:

    PlayerImportBatch.row_errors

This conflates non-blocking warnings with actual import errors.

Change the persistence behavior so:

- `row_errors` contains only actual errors
- warnings remain persisted in `import_summary`
- provisioning warnings remain available under the existing account provisioning summary
- warnings remain available in the overall import summary
- the import detail UI continues to display warnings
- no migration is required unless absolutely unavoidable

Preferred behavior:

    locked_batch.row_errors = result.errors

Warnings should remain available through:

    import_summary["warnings"]

and/or:

    import_summary["account_provisioning"]["warnings"]

Do not classify successful provisioning warnings as errors.

==================================================
Backward Compatibility
==================================================

Preserve the current serialized import summary structure wherever practical.

At minimum, retain:

- top-level `warnings`
- `account_provisioning["warnings"]`

Do not remove fields currently used by templates or tests without updating all consumers.

Existing imports with older summaries should continue rendering safely when warning keys are absent.

Use defensive template access where needed.

==================================================
Testing
==================================================

Add or update tests for:

1. New account duplicate-email warning
   - account is created
   - email is blank
   - warning says the account was created
   - warning does not describe it as an existing account

2. Existing linked account duplicate-email warning
   - existing account remains linked
   - existing account email is unchanged
   - warning does not say the account was created
   - warning clearly says the existing account was left unchanged

3. Warning persistence
   - warning appears in immediate provisioning result
   - warning appears in `import_summary["warnings"]`
   - warning appears in `import_summary["account_provisioning"]["warnings"]`

4. Row errors remain clean
   - duplicate-email warning is not stored in `row_errors`
   - actual import errors still remain in `row_errors`

5. Import detail page still displays persisted warnings

6. Existing blank-email provisioning tests continue to pass

7. Existing sibling shared-email provisioning tests continue to pass

8. No temporary password appears in:
   - warnings
   - import summary
   - row errors
   - repr output

==================================================
Do Not Implement
==================================================

NO model redesign

NO parent accounts

NO guardian accounts

NO family linking

NO new warning model

NO new database field unless absolutely necessary

NO email invitations

NO authentication changes

NO broad import refactor

NO APIs

NO JavaScript

NO unrelated cleanup

==================================================
Run
==================================================

Run:

- DJANGO_SECRET_KEY=test python manage.py check
- DJANGO_SECRET_KEY=test python manage.py makemigrations accounts players analytics --check
- DJANGO_SECRET_KEY=test python manage.py test accounts
- DJANGO_SECRET_KEY=test python manage.py test players
- DJANGO_SECRET_KEY=test python manage.py test analytics
- DJANGO_SECRET_KEY=test python manage.py test drafts
- DJANGO_SECRET_KEY=test python manage.py test pdp
- DJANGO_SECRET_KEY=test python manage.py test
- git diff --check

==================================================
Self Review
==================================================

Verify:

- warning text matches whether the account was created or already existed
- no warning incorrectly claims account creation
- `row_errors` contains only actual errors
- warnings remain persisted in import summaries
- warnings remain visible in the UI
- provisioning behavior from Prompt 101 is unchanged
- no migration was added unless absolutely necessary
- no unrelated work was included

==================================================
Final Report
==================================================

Report:

- implementation summary
- files modified
- warning wording changes
- warning persistence changes
- tests added or updated
- full test results
- migrations added, if any
- implementation decisions
- technical debt
- self-review
- confirmation that only this follow-up cleanup was implemented
```

## Implementation Commit Diff

```diff
commit 0d7f967808f42bc965b5feebd06847e4e9777480
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Sat Jul 25 12:09:48 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Sat Jul 25 12:09:48 2026 -0700

    Clean up player provisioning warnings

diff --git a/accounts/services/provisioning_service.py b/accounts/services/provisioning_service.py
index 2a6e5c0..28735de 100644
--- a/accounts/services/provisioning_service.py
+++ b/accounts/services/provisioning_service.py
@@ -174,7 +174,11 @@ def _safe_linked_user_result(
     email_assigned = False
     email_omitted = False
     if existing_email_user and existing_email_user.id != link.user_id:
-        warnings.append(_duplicate_email_warning(row_number, normalized_email))
+        warnings.append(
+            _duplicate_email_warning(
+                row_number, normalized_email, account_created=False
+            )
+        )
         email_omitted = True
     try:
         link = _ensure_active_self_link(link, import_batch)
@@ -209,10 +213,24 @@ def _safe_linked_user_result(
     )
 
 
-def _duplicate_email_warning(row_number: int | None, email: str) -> str:
+def _duplicate_email_warning(
+    row_number: int | None, email: str, *, account_created: bool
+) -> str:
+    if account_created:
+        message = (
+            f'Player account was created, but the login email "{email}" was '
+            "already assigned to another account and was not added. The new "
+            "account has a blank email."
+        )
+    else:
+        message = (
+            f'The login email "{email}" was already assigned to another account '
+            "and was not added to the existing player account. The existing "
+            "account was left unchanged."
+        )
     return _row_message(
         row_number,
-        f'Player account was created, but the login email "{email}" was already assigned to another account and was not added.',
+        message,
     )
 
 
@@ -268,7 +286,9 @@ def provision_player_account(
                 ],
                 email_assigned=bool(normalized_email),
             )
-        email_warning = _duplicate_email_warning(row_number, normalized_email)
+        email_warning = _duplicate_email_warning(
+            row_number, normalized_email, account_created=True
+        )
         normalized_email = ""
     else:
         email_warning = ""
diff --git a/accounts/tests/test_account_services.py b/accounts/tests/test_account_services.py
index 288ae10..7db4c56 100644
--- a/accounts/tests/test_account_services.py
+++ b/accounts/tests/test_account_services.py
@@ -356,10 +356,48 @@ class AccountProvisioningServiceTests(TestCase):
         self.assertTrue(result.email_omitted)
         self.assertIn("login email", result.warnings[0])
         self.assertIn("player@example.com", result.warnings[0])
+        self.assertIn("Player account was created", result.warnings[0])
+        self.assertIn("new account has a blank email", result.warnings[0])
+        self.assertNotIn("existing player account", result.warnings[0])
         self.assertTrue(
             UserPlayerLink.objects.filter(player=self.player, user=user).exists()
         )
 
+    def test_provision_player_account_existing_link_warning_does_not_claim_creation(
+        self,
+    ):
+        linked_user = User.objects.create_user(
+            username="linked.player", email="linked@example.com"
+        )
+        other_user = User.objects.create_user(
+            username="other", email="family@example.com"
+        )
+        link_user_to_player(
+            linked_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+
+        result = provision_player_account(
+            self.player,
+            import_batch=self.import_batch,
+            email=other_user.email,
+            row_number=2,
+        )
+
+        linked_user.refresh_from_db()
+        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
+        self.assertEqual(result.user_id, linked_user.id)
+        self.assertEqual(linked_user.email, "linked@example.com")
+        self.assertFalse(result.email_assigned)
+        self.assertTrue(result.email_omitted)
+        self.assertEqual(len(result.warnings), 1)
+        self.assertIn("family@example.com", result.warnings[0])
+        self.assertIn("existing player account", result.warnings[0])
+        self.assertIn("left unchanged", result.warnings[0])
+        self.assertNotIn("Player account was created", result.warnings[0])
+
     def test_provision_player_account_does_not_downgrade_existing_staff_link(self):
         staff_profile = get_or_create_account_profile(self.staff)
         staff_profile.role = AccountRole.STAFF
@@ -427,6 +465,8 @@ class AccountProvisioningServiceTests(TestCase):
         self.assertEqual(user.email, "")
         self.assertEqual(len(serialized["warnings"]), 1)
         self.assertIn("family@example.com", serialized["warnings"][0])
+        self.assertIn("Player account was created", serialized["warnings"][0])
+        self.assertNotIn("20120501", str(serialized))
 
 
 class AccountRegressionTests(TestCase):
diff --git a/analytics/templates/analytics/import_detail.html b/analytics/templates/analytics/import_detail.html
index 26cf458..54db794 100644
--- a/analytics/templates/analytics/import_detail.html
+++ b/analytics/templates/analytics/import_detail.html
@@ -25,6 +25,14 @@
             {% endfor %}
         </ul>
     {% endif %}
+    {% if import_batch.import_summary.warnings %}
+        <h3>Warnings</h3>
+        <ul>
+            {% for warning in import_batch.import_summary.warnings %}
+                <li>{{ warning }}</li>
+            {% endfor %}
+        </ul>
+    {% endif %}
     {% if import_batch.import_summary.account_provisioning.enabled %}
         <h3>Account provisioning</h3>
         <div class="pdp-stat-grid">
diff --git a/analytics/tests/test_import_views.py b/analytics/tests/test_import_views.py
index 9382cee..523cbf4 100644
--- a/analytics/tests/test_import_views.py
+++ b/analytics/tests/test_import_views.py
@@ -241,6 +241,44 @@ class AnalyticsImportViewTests(TestCase):
         self.assertContains(response, "Users Created")
         self.assertNotContains(response, "20120501")
 
+    def test_import_detail_displays_persisted_provisioning_warnings(self):
+        self.client.force_login(self.staff)
+        warning = (
+            'Row 2: Player account was created, but the login email "family@example.com" '
+            "was already assigned to another account and was not added. The new account "
+            "has a blank email."
+        )
+        batch = PlayerImportBatch.objects.create(
+            source=SOURCE_MEMBER_LIST,
+            original_filename="member.csv",
+            uploaded_by=self.staff,
+            season=self.season,
+            status="committed",
+            import_summary={
+                "warnings": [warning],
+                "account_provisioning": {
+                    "enabled": True,
+                    "users_created": 1,
+                    "users_linked": 0,
+                    "already_linked": 0,
+                    "skipped": 0,
+                    "conflicts": 0,
+                    "messages": [],
+                    "warnings": [warning],
+                },
+            },
+            row_errors=[],
+        )
+
+        response = self.client.get(
+            reverse("analytics:import-detail", kwargs={"pk": batch.pk})
+        )
+
+        self.assertContains(response, "Warnings")
+        self.assertContains(response, "family@example.com")
+        self.assertContains(response, "new account has a blank email")
+        self.assertNotContains(response, "Issues")
+
     def test_conflict_page_displays_review_rows(self):
         self.client.force_login(self.staff)
         Player.objects.create(
diff --git a/players/services/imports/commit.py b/players/services/imports/commit.py
index a7b444c..f1be03c 100644
--- a/players/services/imports/commit.py
+++ b/players/services/imports/commit.py
@@ -374,7 +374,7 @@ def commit_import_batch(
     locked_batch.rows_skipped = result.skipped
     locked_batch.rows_conflicted = result.conflicts
     locked_batch.import_summary = asdict(result)
-    locked_batch.row_errors = [*result.errors, *result.warnings]
+    locked_batch.row_errors = result.errors
     locked_batch.committed_at = timezone.now()
     locked_batch.save(
         update_fields=[
diff --git a/players/tests/test_import_workflow.py b/players/tests/test_import_workflow.py
index 5f652ea..75dfc11 100644
--- a/players/tests/test_import_workflow.py
+++ b/players/tests/test_import_workflow.py
@@ -640,7 +640,10 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(account_summary["conflicts"], 0)
         self.assertEqual(len(account_summary["warnings"]), 1)
         self.assertIn("eugene@example.com", account_summary["warnings"][0])
-        self.assertIn(account_summary["warnings"][0], batch.row_errors)
+        self.assertEqual(batch.import_summary["warnings"], account_summary["warnings"])
+        self.assertEqual(batch.row_errors, [])
+        self.assertNotIn("20120501", str(batch.import_summary))
+        self.assertNotIn("20120501", str(batch.row_errors))
 
     def test_commit_with_provisioning_allows_sibling_rows_sharing_login_email(self):
         batch = create_import_batch(
@@ -674,7 +677,10 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(account_summary["conflicts"], 0)
         self.assertEqual(len(account_summary["warnings"]), 1)
         self.assertIn("family@example.com", account_summary["warnings"][0])
+        self.assertEqual(batch.import_summary["warnings"], account_summary["warnings"])
+        self.assertEqual(batch.row_errors, [])
         self.assertNotIn("20130331", str(batch.import_summary))
+        self.assertNotIn("20130331", str(batch.row_errors))
 
     def test_generic_email_header_is_not_auto_mapped_as_player_login_email(self):
         batch = create_import_batch(
```
