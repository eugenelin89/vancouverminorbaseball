# Prompt 51 - Platform

## User Prompt

```text
Perform a documentation consistency cleanup only.

Do NOT change application code.

Do NOT modify Python files.

Do NOT modify models, services, forms, views, URLs, templates, middleware, tests, or migrations.

Goal:
Make the project documentation consistent with the current frozen state:

- Account Management V1 is complete and frozen.
- Platform V1 Account Operations is complete and frozen.
- Account Operations A-F have been implemented.
- `project_flat_file.txt` is now an on-request artifact only.

Read:

- AGENTS.md
- README.md
- docs/ARCHITECTURE.md
- docs/USER_MANUAL.md
- docs/account_management/V1_SUMMARY.md
- docs/account_management/implementation/engineering/platform_v1_account_operations.md

Required updates:

1. Update `docs/USER_MANUAL.md`

Remove or revise stale future-facing language that says staff account-management screens are future work.

Document current Account Operations capabilities, including:

- staff Account Operations dashboard
- account search/list/detail
- manual account creation
- player account creation from existing players
- account activation/deactivation
- username/email/role editing
- user-player link management
- operational password reset
- bulk account operations
- forced password-change behavior
- temporary password shown once

Clarify permission model:

- staff-only Account Operations pages require Django `User.is_staff` or `User.is_superuser`
- `AccountProfile.role = staff` does not grant access by itself
- platform roles are metadata unless backed by Django staff/superuser flags

Keep the user manual user-facing and operational. Do not turn it into an architecture document.

2. Update `README.md`

Fix the outdated Project Snapshot Policy.

It currently says `project_flat_file.txt` should be updated whenever a file changes.

Update it to match `AGENTS.md`:

- do not regenerate/update `project_flat_file.txt` during normal work
- treat it as an on-request artifact only
- prompt archives should store prompt text and commit diffs, not full repository snapshots
- if a snapshot is requested, exclude dependency/generated/cache directories and represent binary files by metadata/description only

3. Lightly verify architecture docs

Check `docs/ARCHITECTURE.md`, `docs/account_management/V1_SUMMARY.md`, and `platform_v1_account_operations.md`.

Only update them if they contain obvious stale statements contradicting the frozen Account Operations state.

Do not rewrite them.

4. Prompt archive

Create the next prompt record in `docs/prompts/` according to `AGENTS.md`.

Use the correct next prompt number.

Because this is documentation-only, commit documentation changes first, then commit the prompt record separately.

Verification:

Run:

git diff --check

No Django tests are required unless application code is accidentally changed.

Final report:

Report:

- files modified
- stale documentation corrected
- user manual updates made
- README policy correction made
- whether architecture docs needed changes
- confirmation that no application code was changed
- confirmation that Account Management V1 and Account Operations remain frozen
- git diff --check result
- commits created
- push result
```

## App / Subsystem

platform

## Work Commit

```text
ecbb96fb6df60aa2c14887a74203c905502c3187 Align documentation with frozen account operations
```

## Commit Diff

```diff
commit ecbb96fb6df60aa2c14887a74203c905502c3187
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 8 12:15:11 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 8 12:15:11 2026 -0700

    Align documentation with frozen account operations
---
 README.md                                          |   4 +-
 docs/USER_MANUAL.md                                | 115 ++++++++++++++++++++-
 .../engineering/platform_v1_account_operations.md  |   4 +-
 3 files changed, 116 insertions(+), 7 deletions(-)

diff --git a/README.md b/README.md
index 6817d26..b622ef0 100644
--- a/README.md
+++ b/README.md
@@ -79,7 +79,9 @@ Because the site is mostly static, productivity comes from editing `content.py`
 
 ## Project Snapshot Policy
 
-When a file is created or changed in this repository, update `project_flat_file.txt` before finishing the task. The snapshot should include all project text files with their full absolute paths and clear separators. Binary files should be represented by metadata and a short description rather than embedding their full contents.
+Do not regenerate or update `project_flat_file.txt` during normal work. Treat it as an on-request artifact only.
+
+Prompt archive records should store the user prompt and commit diffs, not full repository snapshots. If a full-project snapshot is explicitly requested, exclude dependency, generated, and cache directories such as `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, and `build`. Binary files should be represented by metadata and a short description rather than embedding their full contents.
 
 ---
 
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 6dfa3ad..1ba6a58 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -32,16 +32,19 @@ The current platform supports:
 - draft context from submitted assessments
 - draft room workflows
 - account login and password change
+- staff Account Operations for managing user accounts
 
-Some future features are not available yet, including full player portals, parent portals, coach portals, email invitations, password reset emails, and staff account-management screens.
+Some future features are not available yet, including full player portals, parent portals, coach portals, email invitations, and password reset emails.
 
 ## User Types
 
 ### Administrators And Staff
 
-Administrators and staff can access staff-only areas such as Analytics, imports, player search, review pages, reporting summaries, and draft workflows.
+Administrators and staff can access staff-only areas such as Analytics, imports, player search, review pages, reporting summaries, draft workflows, and Account Operations.
 
-Staff/admin access is controlled by the system account. If you cannot access a staff page, ask a site administrator to check your account permissions.
+Staff/admin access is controlled by Django account permissions. Staff-only Account Operations pages require `User.is_staff` or `User.is_superuser`.
+
+The platform account role is separate from Django staff access. For example, `AccountProfile.role = staff` is metadata and does not grant staff-only page access by itself. If you cannot access a staff page, ask a site administrator to check your Django staff or superuser permissions.
 
 ### Coaches And Evaluators
 
@@ -112,6 +115,111 @@ It shows basic account information such as:
 
 This page is intentionally simple. It is not a player portal.
 
+## Account Operations
+
+Staff can manage platform user accounts from Account Operations:
+
+```text
+/accounts/
+```
+
+The Account Operations dashboard gives staff a production view of account status, including account totals, active and inactive accounts, imported accounts, accounts requiring password changes, players without accounts, and users without player links.
+
+Staff Account Operations includes:
+
+- account search, list, and detail pages
+- account-only creation for coaches, parents, guest evaluators, staff-role metadata users, and other non-player accounts
+- player account creation from an existing player record
+- account activation and deactivation
+- username, email, and platform role editing
+- user-player link management
+- operational password reset
+- bulk account operations for low-risk actions
+
+Account Operations does not create new player identity records. Player accounts are created by finding an existing player, creating a login account, and linking the user to that player.
+
+### Creating Accounts
+
+Staff can create account-only users from:
+
+```text
+/accounts/create/
+```
+
+Use this for coaches, parents, guest evaluators, staff-role metadata users, or other users who do not need a new player identity.
+
+Staff can create a player login account from an existing player record at:
+
+```text
+/accounts/create/player/
+```
+
+Use this only when the player already exists in the player database.
+
+Temporary passwords are shown once immediately after account creation. They are not shown again on the account detail page.
+
+### Editing Accounts
+
+Staff can open an account detail page from the account list:
+
+```text
+/accounts/users/
+```
+
+From account detail, staff can edit:
+
+- username
+- email
+- platform role
+- active/inactive status
+
+Changing `AccountProfile.role` does not change Django `User.is_staff` or `User.is_superuser`. Platform roles help describe account purpose; Django staff/superuser flags control operational access.
+
+### User-Player Links
+
+Staff can manage user-player links from an account detail page.
+
+Supported link relationships include:
+
+- self
+- parent
+- guardian
+- coach
+- staff
+
+A parent or guardian account may be linked to multiple players. A player may also be linked to multiple parents or guardians.
+
+Normal unlinking deactivates the link instead of deleting it, so staff can preserve history and reactivate links when needed.
+
+### Password Reset And Forced Password Change
+
+Staff can perform operational password resets from an account detail page.
+
+When a password is reset:
+
+- a temporary password is shown once
+- the user is required to change the password at next login
+- the temporary password is not stored in account summaries, import data, or account detail pages
+
+Users who must change their password are sent to:
+
+```text
+/accounts/password/
+```
+
+They cannot use normal platform pages until the password change is complete.
+
+### Bulk Account Operations
+
+Staff can perform selected low-risk bulk actions from the account list, such as:
+
+- activate selected accounts
+- deactivate selected accounts
+- require selected users to change passwords
+- clear password-change requirement for selected users
+
+Bulk operations are intended for routine account maintenance. Staff should review selected accounts carefully before applying a bulk action.
+
 ## Analytics Command Center
 
 The Analytics Command Center is the staff starting point:
@@ -347,7 +455,6 @@ The following are not part of the current version:
 - public self-registration
 - email invitations
 - password reset emails
-- staff account-management UI
 - audit dashboard
 - video analysis
 - AI-generated summaries
diff --git a/docs/account_management/implementation/engineering/platform_v1_account_operations.md b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
index 498162f..a1ee442 100644
--- a/docs/account_management/implementation/engineering/platform_v1_account_operations.md
+++ b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
@@ -2,9 +2,9 @@
 
 ## 1. Objectives
 
-Players V1, Analytics V1, Account Management V1, and the platform architecture documentation are complete and frozen. The remaining gap is operational: staff can authenticate users, provision accounts from imports, link users to players, and force password changes, but they do not yet have production-ready screens for day-to-day account management.
+Players V1, Analytics V1, Account Management V1, Platform V1 Account Operations, and the platform architecture documentation are complete and frozen. This document records the operational account-management plan that was used to complete the staff-facing production workflows for managing accounts, links, passwords, and bulk account actions.
 
-This plan defines the remaining account-management work required to make Platform V1 production-ready. It extends Platform V1 operations without introducing a new architecture version.
+This plan defines the account-management work that made Platform V1 production-ready. It extended Platform V1 operations without introducing a new architecture version.
 
 The objectives are:
```
