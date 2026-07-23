Review the Django project at:

`/Users/eugenelin/dev/vmba0`

Create a complete, reusable production QA package for testing the VCB Platform’s account provisioning, imports, assignments, and evaluation workflows.

## Goal

Generate:

1. A detailed end-to-end test script in Markdown.
2. A valid CSV for importing test players.
3. A valid CSV for importing test coaches.
4. A concise README explaining exactly how to use the files.
5. A cleanup checklist for safely deactivating or archiving test data afterward.

The testing should require minimal manual setup, while deliberately leaving a few players and coaches to be created manually so that both import and manual-creation workflows are tested.

Do not change application code unless a small, clearly necessary correction is required to make the QA fixtures valid. The primary deliverables are documentation and CSV test data.

---

# 1. Inspect the Existing Import Workflows

Before generating any CSV files, inspect the actual implementation and determine:

- the current player-import route
- the current coach-import or account-provisioning route
- the accepted CSV headers
- required fields
- optional fields
- accepted date formats
- accepted role values
- season and team matching behavior
- account activation behavior
- username generation behavior
- temporary-password behavior
- duplicate-detection and idempotency rules
- whether coach imports and player imports use separate schemas
- whether season and team values must already exist
- whether accounts are provisioned automatically during import
- whether imported accounts start active or inactive

Relevant areas may include:

- `players/services/import_service.py`
- account provisioning services
- coach import services
- Analytics import views and forms
- import templates
- import tests
- CSV fixtures already present in the repository
- model definitions for seasons, teams, users, roles, and player links

Do not invent CSV columns. Generate files that match the project’s actual supported import format.

If the project does not currently support direct coach CSV import, document the real supported workflow and create the closest valid fixture possible, such as an account-import CSV or a manual coach-creation worksheet. Do not falsely claim that unsupported imports exist.

---

# 2. Create the QA Directory

Create a directory such as:

`docs/qa/platform_e2e/`

Place the generated files there.

Suggested deliverables:

```text
docs/qa/platform_e2e/
├── README.md
├── platform_e2e_test_script.md
├── test_players_import.csv
├── test_coaches_import.csv
├── manual_test_records.md
└── cleanup_checklist.md
```

Adjust filenames only if the repository has an established documentation convention.

---

# 3. Test Data Design

Use an isolated QA environment within production.

Recommended test season:

`TEST - Platform QA 2026`

Recommended teams:

- `TEST - Alpha`
- `TEST - Beta`

The test script should instruct the administrator to create these manually if they do not already exist.

Do not associate test records with real teams or seasons.

Use clearly artificial names and no real personal data.

## Imported players

Generate a player CSV containing four imported test players:

1. Player QA One
2. Player QA Two
3. Player QA Three
4. Player QA Four

Assign:

- Player QA One and Player QA Two to `TEST - Alpha`
- Player QA Three and Player QA Four to `TEST - Beta`

Use artificial birthdates appropriate for the import format.

Use controlled or placeholder email aliases that are clearly intended to be replaced before use, for example:

- `REPLACE_WITH_YOUR_EMAIL+qa-player1@example.com`
- `REPLACE_WITH_YOUR_EMAIL+qa-player2@example.com`

If the import rejects `example.com`, instead document that the administrator must replace the placeholder domain before importing.

Do not use real third-party email addresses.

## Imported coaches

Generate a coach CSV containing two imported test coaches:

1. Coach QA One
2. Coach QA Two

Assign:

- Coach QA One to `TEST - Alpha`
- Coach QA Two to `TEST - Beta`

Use placeholder email aliases that the administrator must replace with addresses they control.

Ensure the role values and assignment columns exactly match the supported import schema.

## Manually created records

Leave the following records out of the CSV files so they can be created manually:

### Manual coach

- Coach QA Manual
- assigned to `TEST - Alpha`

### Manual players

- Player QA Manual One
- assigned to `TEST - Alpha`

- Player QA Manual Two
- assigned to `TEST - Beta`

The manual-record document should list every field the administrator must enter and the expected role, season, team, activation, and account-link settings.

This creates a total QA set of:

- 3 coaches
- 6 players
- 2 teams
- 1 isolated test season

This is enough to test imported records, manually created records, same-team evaluations, cross-team evaluations, self-evaluations, and peer evaluations.

---

# 4. Generate the End-to-End Test Script

Create:

`platform_e2e_test_script.md`

The script should be detailed, sequential, and usable by a non-developer administrator.

Include checkboxes or Pass / Fail fields.

Cover the following workflows.

## A. Initial setup

- confirm the production commit being tested
- confirm a recent database backup exists
- create or verify the isolated QA season
- create or verify both QA teams
- replace placeholder email addresses in both CSV files
- confirm no real users are assigned to the QA season

## B. Player import

- import the four test players
- verify preview behavior
- verify season and team assignment
- verify account provisioning
- verify usernames
- verify role assignment
- verify active or inactive state
- verify player-user links
- verify import result counts
- repeat the import to test idempotency
- confirm no duplicate players, accounts, or links are created

## C. Coach import

- import the two test coaches using the actual supported workflow
- verify user creation
- verify Coach role
- verify team and season assignment
- verify account activation
- verify coaches are not staff or superusers unless intentionally configured
- repeat the import where supported to test duplicate handling

## D. Manual creation

Manually create:

- Coach QA Manual
- Player QA Manual One
- Player QA Manual Two

Verify the manual workflow creates the same expected relationships and permissions as imported records.

## E. Administrator navigation and permissions

Verify the administrator can access:

- Operations Home
- User Accounts
- Seasons
- Imports
- Evaluations
- Review Evaluations
- Profile
- Password
- Logout

Verify:

- Imports points to `/analytics/imports/`
- no visible link points to `/pdp/`
- no visible page displays `PDP`
- no important link returns 404
- no unexpected 403 appears

## F. Coach evaluation workflow

Test all three coaches.

At minimum:

- Coach QA One evaluates Player QA One
- Coach QA Two evaluates Player QA Three
- Coach QA Manual evaluates Player QA Manual One

For each:

1. start an evaluation
2. answer several questions
3. save as draft
4. leave the page
5. reopen the draft
6. verify answers persisted
7. modify one answer
8. submit
9. verify submitted status
10. verify evaluator identity and role
11. verify season, team, and player relationships

Test whether coaches can see:

- same-team players
- players from the other QA team
- real players

Compare actual behavior to the intended evaluator policy.

## G. Player self-evaluations

Test at least:

- Player QA One self-evaluates
- Player QA Manual One self-evaluates

Verify:

- the subject is automatically or correctly set to the logged-in player
- the evaluator relationship is Self
- the player cannot select another player for a self-evaluation
- draft, reopen, edit, and submit all work
- the evaluation appears in My Evaluations
- another player cannot edit it

## H. Player peer evaluations

Test at least:

- Player QA One evaluates Player QA Two
- Player QA Two evaluates Player QA One
- Player QA Manual One evaluates Player QA Manual Two
- one cross-team peer evaluation, if intended by policy

Verify:

- the evaluator relationship is Peer
- self-selection is blocked for a peer evaluation
- the correct subject player is recorded
- draft, reopen, edit, and submit all work
- evaluator identity is protected or shown according to product policy
- players cannot edit peer evaluations submitted by someone else
- unrelated real players are not exposed unnecessarily

## I. Review workflow

As administrator or authorized reviewer, verify all submitted evaluations appear.

For each evaluation, verify:

- evaluator name
- evaluator account
- evaluator role
- relationship type
- subject player
- team
- season
- evaluation cycle
- submission timestamp
- status
- answers and scores

Reopen one coach evaluation, one self-evaluation, and one peer evaluation.

Log in as the original evaluator and verify:

- prior answers remain
- the evaluation becomes editable
- it can be resubmitted
- no duplicate record is created

## J. Permission testing

As a coach, directly attempt:

- `/analytics/imports/`
- account operations
- season administration
- Django Admin

As a player, directly attempt:

- `/analytics/imports/`
- review pages
- account operations
- season administration
- another player’s private evaluation URL

As an anonymous user, directly attempt:

- `/analytics/`
- `/analytics/imports/`
- evaluation pages
- profile pages

Record whether each result is:

- allowed
- redirected to login
- 403
- 404
- unexpectedly exposed

Navigation hiding is not sufficient; direct URL access must also be tested.

## K. Account activation and password workflow

Test one imported coach, one imported player, and one manually created player.

Verify:

- expected initial active/inactive status
- administrator activation
- temporary password login
- forced password change, if supported
- password update
- logout and login with the new password
- old temporary password no longer works
- password pages use current Accounts routes and branding

## L. Analytics and timeline

Verify the test evaluations appear correctly in:

- player profile
- player timeline
- player comparison
- command-center metrics where applicable

Confirm coach, self, and peer evaluations are labelled distinctly and not incorrectly combined.

## M. Mobile testing

Test at approximately 390-pixel width:

- login
- navigation
- import page
- evaluation list
- evaluation form
- draft and submit buttons
- review page
- profile
- timeline

## N. Cleanup

After testing:

- record defects and screenshots
- deactivate all QA accounts
- archive or deactivate the QA season
- ensure it is not the default season
- hide it from normal selectors where supported
- do not delete linked records until cascade behavior is understood
- retain the QA environment for repeat smoke tests if appropriate

---

# 5. Create README.md

The README should provide a very short operational sequence:

1. Create the QA season and teams.
2. Replace email placeholders in the CSV files.
3. Import players.
4. Import coaches or follow the documented supported coach workflow.
5. Create the manual coach and two manual players.
6. Activate accounts as needed.
7. Follow the end-to-end test script.
8. Archive or deactivate the QA records afterward.

Clearly state which records are imported and which are intentionally manual.

Include the exact current UI paths discovered from the code.

Do not document nonexistent routes.

---

# 6. Create manual_test_records.md

Provide a compact table listing the three manually created records and all fields needed.

Include:

- first name
- last name
- username
- controlled email placeholder
- role
- season
- team
- active status
- staff status
- superuser status
- player relationship, where applicable
- expected password workflow

Also include a short verification checklist after each manual record is created.

---

# 7. Create cleanup_checklist.md

Include:

- deactivate test accounts
- archive or deactivate QA season
- verify it is not default
- remove QA teams from active selectors
- ensure no real users are linked to QA records
- preserve records needed for audit or regression testing
- delete only after backup and cascade review
- verify reports no longer include QA data, or document how QA data is filtered

---

# 8. CSV Quality Requirements

For each CSV:

- use UTF-8
- include a header row
- use only columns actually accepted by the current code
- use valid date formats
- use valid role values
- use exact season and team names expected by matching logic
- include no formulas
- include no real personal data
- include no unsupported fields
- quote values where necessary
- ensure the files parse using Python’s standard `csv` module
- ensure row counts match the intended fixtures

Add a lightweight automated validation script or test only if useful and consistent with the repository.

At minimum, validate:

```bash
python - <<'PY'
import csv
from pathlib import Path

for filename in (
    "docs/qa/platform_e2e/test_players_import.csv",
    "docs/qa/platform_e2e/test_coaches_import.csv",
):
    path = Path(filename)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    print(filename, len(rows), rows[0].keys() if rows else "NO ROWS")
PY
```

---

# 9. Validation

Run appropriate validation, including:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
git diff --check
```

If documentation or fixture tests exist, run them.

Do not run production imports automatically.

Do not create production database records.

Do not commit real email addresses, real passwords, or personal information.

---

# 10. Deliverable Summary

At completion, report:

1. Files created.
2. Actual player CSV schema discovered.
3. Actual coach-import workflow and schema discovered.
4. Which records are imported.
5. Which records must be created manually.
6. Any placeholder values the administrator must replace.
7. Validation commands and results.
8. Any limitations or unsupported workflows found.
9. Any assumptions that must be confirmed before using the fixtures.

Commit the completed QA package to the current branch with a clear commit message, but do not push unless explicitly instructed.

==================================================
Implementation Commit Diff
==================================================

```diff
commit d85aea5b18129c709cccefa34cda4fde05837986
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 23 14:14:27 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 23 14:14:27 2026 -0700

    Add platform end-to-end QA package
---
 docs/qa/platform_e2e/README.md                   |  77 +++
 docs/qa/platform_e2e/cleanup_checklist.md        |  80 ++++
 docs/qa/platform_e2e/manual_test_records.md      | 106 +++++
 docs/qa/platform_e2e/platform_e2e_test_script.md | 565 +++++++++++++++++++++++
 docs/qa/platform_e2e/test_coaches_import.csv     |   3 +
 docs/qa/platform_e2e/test_players_import.csv     |   5 +
 6 files changed, 836 insertions(+)

diff --git a/docs/qa/platform_e2e/README.md b/docs/qa/platform_e2e/README.md
new file mode 100644
index 0000000..726fdf8
--- /dev/null
+++ b/docs/qa/platform_e2e/README.md
@@ -0,0 +1,77 @@
+# Platform End-To-End QA Package
+
+This package contains reusable QA material for testing VCB Platform account provisioning, imports, season/team assignments, and evaluation workflows.
+
+Use these files in an isolated QA season only:
+
+```text
+TEST - Platform QA 2026
+```
+
+Recommended QA teams:
+
+- `TEST - Alpha`
+- `TEST - Beta`
+
+## Files
+
+- `platform_e2e_test_script.md`: step-by-step production QA script.
+- `test_players_import.csv`: four imported player records.
+- `test_coaches_import.csv`: two imported coach records.
+- `manual_test_records.md`: records intentionally left for manual creation.
+- `cleanup_checklist.md`: safe cleanup checklist after testing.
+
+## Current UI Paths
+
+- Sign in: `/accounts/login/`
+- Analytics Command Center: `/analytics/`
+- Player import: `/analytics/imports/`
+- New player import: `/analytics/imports/new/`
+- Coach import: `/accounts/imports/coaches/`
+- New coach import: `/accounts/imports/coaches/new/`
+- Account Operations: `/accounts/`
+- Account list/search: `/accounts/users/`
+- Manual account creation: `/accounts/create/`
+- Manual player-account creation: `/accounts/create/player/`
+- Season Operations: `/seasons/`
+- Season teams: `/seasons/teams/`
+- Player roster memberships: `/seasons/memberships/`
+- Coach assignments: `/seasons/coach-assignments/`
+- Evaluation submission: `/analytics/evaluations/`
+- Player "My Evaluations": `/analytics/my/evaluations/`
+- Coach/staff evaluation review: `/analytics/evaluation-review/`
+
+## Short Operating Sequence
+
+1. Confirm a recent database backup exists.
+2. Create or verify the QA season `TEST - Platform QA 2026`.
+3. Create or verify the QA teams `TEST - Alpha` and `TEST - Beta`.
+4. Replace every `REPLACE_WITH_YOUR_EMAIL+...@example.com` placeholder in both CSV files with controlled test inbox aliases before importing.
+5. Import `test_players_import.csv` from `/analytics/imports/new/`.
+6. Import `test_coaches_import.csv` from `/accounts/imports/coaches/new/`.
+7. Manually create the records listed in `manual_test_records.md`.
+8. Follow `platform_e2e_test_script.md`.
+9. After testing, follow `cleanup_checklist.md`.
+
+## Important Import Notes
+
+- Player import and coach import use different CSV schemas.
+- Player import belongs to Analytics UI but uses `players` import services.
+- Coach import belongs to Account Operations and creates or reuses coach accounts.
+- Player imports can optionally provision player accounts when staff select the account-provisioning option and map the `account_email` column.
+- Player account temporary passwords are based on the imported birthdate in `YYYYMMDD` format and are not displayed in the import result.
+- Coach account temporary passwords are secure random passwords shown only once on the coach import result page.
+- Imported coach accounts are active by default unless the CSV sets `is_active` to a false value.
+- Imported coaches do not receive Django staff or superuser access.
+- Coach import creates or updates season teams and coach assignments.
+- Player import creates or updates season teams and player roster memberships.
+
+## Placeholder Email Rule
+
+The committed CSV files intentionally use `example.com` placeholders. Before using them in a real QA environment, replace them with aliases controlled by the tester, such as:
+
+```text
+your.name+qa-player1@your-domain.example
+```
+
+Do not import real personal data for this QA package.
diff --git a/docs/qa/platform_e2e/cleanup_checklist.md b/docs/qa/platform_e2e/cleanup_checklist.md
new file mode 100644
index 0000000..5d9b34e
--- /dev/null
+++ b/docs/qa/platform_e2e/cleanup_checklist.md
@@ -0,0 +1,80 @@
+# Platform E2E QA Cleanup Checklist
+
+Use this checklist after the end-to-end QA run. Prefer deactivation and archival over deletion unless a backup and cascade review have been completed.
+
+## Before Cleanup
+
+- [ ] Defects, screenshots, and test notes have been recorded.
+- [ ] Temporary passwords copied during testing are destroyed or removed from notes.
+- [ ] The QA season is not required for immediate retesting.
+- [ ] A recent database backup exists.
+
+## Accounts
+
+Search Account Operations at:
+
+```text
+/accounts/users/
+```
+
+Deactivate these test accounts:
+
+- [ ] `coach.qa.one`
+- [ ] `coach.qa.two`
+- [ ] `coach.qa.manual`
+- [ ] `player.qa.one`
+- [ ] `player.qa.two`
+- [ ] `player.qa.three`
+- [ ] `player.qa.four`
+- [ ] `player.qa.manual.one`
+- [ ] `player.qa.manual.two`
+
+Verify:
+
+- [ ] No QA account has Django staff access unless intentionally granted for testing.
+- [ ] No QA account is a superuser.
+- [ ] QA accounts requiring password change are either deactivated or documented for retest.
+- [ ] Temporary passwords are not stored in shared notes, tickets, screenshots, or chat logs.
+
+## User-Player Links
+
+For each QA player account:
+
+- [ ] Confirm self links are attached only to QA player records.
+- [ ] Confirm no real player is linked to a QA user.
+- [ ] Do not delete links unless cascade behavior has been reviewed.
+
+## Season And Teams
+
+Use Season Operations:
+
+```text
+/seasons/
+```
+
+Clean up:
+
+- [ ] Confirm `TEST - Platform QA 2026` is not the current/default season.
+- [ ] Mark `TEST - Platform QA 2026` inactive if the QA run is complete.
+- [ ] Mark `TEST - Alpha` inactive if supported by the current workflow.
+- [ ] Mark `TEST - Beta` inactive if supported by the current workflow.
+- [ ] Confirm QA teams no longer appear in normal active selectors, or document why they remain visible.
+
+## Roster Memberships And Coach Assignments
+
+- [ ] End or deactivate QA player roster memberships if repeat smoke testing is not planned.
+- [ ] End or deactivate QA coach assignments if repeat smoke testing is not planned.
+- [ ] Preserve historical records where they are needed to verify evaluation snapshots.
+
+## Analytics Data
+
+- [ ] Verify reports and review pages no longer include QA data in normal operating filters, or document the QA season filter users should apply.
+- [ ] Preserve submitted QA evaluations if they are useful for regression testing.
+- [ ] Delete evaluations only after backup and cascade review.
+
+## Final Cleanup Review
+
+- [ ] No real users are assigned to the QA season.
+- [ ] No real players are linked to QA accounts.
+- [ ] QA records are clearly identifiable by `QA` or `TEST -`.
+- [ ] The cleanup outcome is recorded in the QA run notes.
diff --git a/docs/qa/platform_e2e/manual_test_records.md b/docs/qa/platform_e2e/manual_test_records.md
new file mode 100644
index 0000000..b44a719
--- /dev/null
+++ b/docs/qa/platform_e2e/manual_test_records.md
@@ -0,0 +1,106 @@
+# Manual QA Test Records
+
+These records are intentionally excluded from the CSV files so administrators can test manual creation workflows alongside import workflows.
+
+Use artificial data only. Replace every placeholder email address with a controlled test inbox alias before creating accounts.
+
+## Manual Records
+
+| Record | First name | Last name | Username | Email placeholder | Role | Season | Team | Division | Active | Staff | Superuser | Player relationship | Expected password workflow |
+| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
+| Manual coach | Coach | QA Manual | `coach.qa.manual` | `REPLACE_WITH_YOUR_EMAIL+qa-coach-manual@example.com` | Coach | `TEST - Platform QA 2026` | `TEST - Alpha` | `13U House` | Yes | No | No | None | Temporary password shown once; must change password on first login. |
+| Manual player one | Player | QA Manual One | `player.qa.manual.one` | `REPLACE_WITH_YOUR_EMAIL+qa-player-manual1@example.com` | Player | `TEST - Platform QA 2026` | `TEST - Alpha` | `13U House` | Yes | No | No | Self, primary | Temporary password shown once for manual account creation; must change password on first login. |
+| Manual player two | Player | QA Manual Two | `player.qa.manual.two` | `REPLACE_WITH_YOUR_EMAIL+qa-player-manual2@example.com` | Player | `TEST - Platform QA 2026` | `TEST - Beta` | `13U House` | Yes | No | No | Self, primary | Temporary password shown once for manual account creation; must change password on first login. |
+
+## Manual Coach Creation
+
+Use Account Operations:
+
+```text
+/accounts/create/
+```
+
+Create:
+
+- username: `coach.qa.manual`
+- first name: `Coach`
+- last name: `QA Manual`
+- email: controlled replacement for `REPLACE_WITH_YOUR_EMAIL+qa-coach-manual@example.com`
+- role: `Coach`
+- active: checked
+
+Then create a coach assignment:
+
+```text
+/seasons/coach-assignments/new/
+```
+
+Use:
+
+- coach account: `coach.qa.manual`
+- season team: `TEST - Platform QA 2026 / 13U House TEST - Alpha`
+- assignment role: `Assistant Coach`
+- primary: checked if this is the coach's only active assignment in the season
+- active: checked
+- start date: `2026-07-01`
+- source: `manual_qa`
+- source identifier: `qa-assignment-coach-manual`
+
+Verification:
+
+- [ ] User exists.
+- [ ] Account role is Coach.
+- [ ] User is active.
+- [ ] User is not Django staff.
+- [ ] User is not a superuser.
+- [ ] Coach assignment exists for `TEST - Alpha`.
+- [ ] Password change is required before normal platform use.
+
+## Manual Player Creation
+
+For each manual player, create the canonical player first if it does not already exist. Use the player management route available through season membership creation or Django admin if required by the current environment.
+
+Then create a player account:
+
+```text
+/accounts/create/player/
+```
+
+Use:
+
+- player: the matching manual QA player
+- username: table value above
+- email: controlled replacement from the table
+- role: `Player`
+- active: checked
+
+Then create a player roster membership:
+
+```text
+/seasons/memberships/new/
+```
+
+Use:
+
+- player: matching manual QA player
+- season team: matching QA team
+- status: `Active`
+- primary: checked
+- active: checked
+- start date: `2026-07-01`
+- source: `manual_qa`
+- source identifier:
+  - `qa-membership-player-manual-001` for Player QA Manual One
+  - `qa-membership-player-manual-002` for Player QA Manual Two
+
+Verification for each manual player:
+
+- [ ] Player exists once.
+- [ ] User exists once.
+- [ ] Account role is Player.
+- [ ] User is active.
+- [ ] User is not Django staff.
+- [ ] User is not a superuser.
+- [ ] A primary active self link exists between user and player.
+- [ ] A primary active roster membership exists for the correct QA team.
+- [ ] Password change is required before normal platform use.
diff --git a/docs/qa/platform_e2e/platform_e2e_test_script.md b/docs/qa/platform_e2e/platform_e2e_test_script.md
new file mode 100644
index 0000000..ec044c4
--- /dev/null
+++ b/docs/qa/platform_e2e/platform_e2e_test_script.md
@@ -0,0 +1,565 @@
+# VCB Platform End-To-End QA Test Script
+
+Use this script to test account provisioning, player imports, coach imports, season assignments, and evaluation workflows in an isolated QA season.
+
+Do not use real personal data. Replace all placeholder email addresses before importing.
+
+## QA Fixture Summary
+
+QA season:
+
+```text
+TEST - Platform QA 2026
+```
+
+QA teams:
+
+- `TEST - Alpha`
+- `TEST - Beta`
+
+Imported players:
+
+- Player QA One, `TEST - Alpha`
+- Player QA Two, `TEST - Alpha`
+- Player QA Three, `TEST - Beta`
+- Player QA Four, `TEST - Beta`
+
+Imported coaches:
+
+- Coach QA One, `TEST - Alpha`
+- Coach QA Two, `TEST - Beta`
+
+Manual records:
+
+- Coach QA Manual, `TEST - Alpha`
+- Player QA Manual One, `TEST - Alpha`
+- Player QA Manual Two, `TEST - Beta`
+
+## Current Supported Import Behavior
+
+Player import:
+
+- Route: `/analytics/imports/new/`
+- Required mapping: either `full_name` or both `first_name` and `last_name`.
+- Season is selected on the upload form.
+- Team and division are required before commit because roster membership must be created.
+- Birthdate formats accepted: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`.
+- Roster status values accepted: blank, `active`, `inactive`, `transferred`, `transfer`, `guest`, `removed`, `remove`.
+- Player account provisioning is optional on upload.
+- If player account provisioning is enabled, map `account_email` to the CSV email column in the preview form.
+- Player account temporary password is the player's birthdate as `YYYYMMDD`; it is not shown in the import result.
+- Imported player accounts are active when provisioning is enabled.
+- Imported player accounts must change password on first login.
+- Re-importing the same source identifiers should update/reuse records instead of creating duplicates.
+
+Coach import:
+
+- Route: `/accounts/imports/coaches/new/`
+- Required CSV columns: `first_name`, `last_name`, `email`.
+- Current implementation also requires `team` and `division` for each valid row because coach assignments are created during import.
+- Optional CSV columns: `username`, `team`, `division`, `is_active`, `notes`, `source_id`, `season`, `assignment_role`, `assignment_start_date`, `assignment_end_date`, `assignment_source_id`.
+- Assignment role values accepted: blank, `assistant`, `assistant coach`, `assistant_coach`, `head`, `head coach`, `head_coach`, `manager`, `coordinator`, `evaluator`.
+- Date formats accepted: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`.
+- Boolean values accepted for `is_active`: blank, `1`, `true`, `yes`, `y`, `active`, `0`, `false`, `no`, `n`, `inactive`.
+- Imported coach accounts are active by default unless `is_active` is false.
+- Imported coach accounts must change password on first login.
+- New coach temporary passwords are random and shown once on the result page.
+- Existing coach accounts are reused by email and keep their existing password.
+- Existing non-coach accounts with the same email are conflicts.
+- Coach import creates or reuses season teams and creates or updates coach season assignments.
+- Coach import does not create `players.Player` records and does not create `UserPlayerLink` rows.
+
+## A. Initial Setup
+
+Tester:
+
+```text
+Name:
+Date:
+Environment:
+Production commit:
+```
+
+Checklist:
+
+- [ ] Confirm the exact production commit being tested.
+- [ ] Confirm a recent database backup exists.
+- [ ] Sign in as a Django staff or superuser account at `/accounts/login/`.
+- [ ] Open `/seasons/`.
+- [ ] Create or verify season `TEST - Platform QA 2026`.
+- [ ] Recommended season key: `test-platform-qa-2026`.
+- [ ] Recommended start date: `2026-07-01`.
+- [ ] Recommended end date: leave blank or use the planned QA end date.
+- [ ] Confirm the QA season is active.
+- [ ] Confirm the QA season is current only if this QA run intentionally tests current-season defaults.
+- [ ] Create or verify season team `TEST - Alpha` in division `13U House`.
+- [ ] Create or verify season team `TEST - Beta` in division `13U House`.
+- [ ] Confirm no real users are assigned to the QA season.
+- [ ] Replace placeholder emails in `test_players_import.csv`.
+- [ ] Replace placeholder emails in `test_coaches_import.csv`.
+- [ ] Save a working copy of each CSV outside the repository if using real controlled email aliases.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## B. Player Import
+
+Path:
+
+```text
+/analytics/imports/new/
+```
+
+Steps:
+
+- [ ] Open Analytics Command Center `/analytics/`.
+- [ ] Click Imports and confirm it opens `/analytics/imports/`.
+- [ ] Click New Import.
+- [ ] Select season `TEST - Platform QA 2026`.
+- [ ] Upload `test_players_import.csv`.
+- [ ] Select source `Manual staff CSV` unless another source is intentionally tested.
+- [ ] Check `Provision player accounts`.
+- [ ] Click Preview Import.
+- [ ] On preview, confirm mapped columns include first name, last name, birthdate, division, team name, roster status, roster source ID, source identifiers, and `account_email`.
+- [ ] If `account_email` is not automatically mapped, map it manually to the `account_email` CSV column.
+- [ ] Confirm each row previews as create or update, not error.
+- [ ] Confirm teams are shown as create or reuse.
+- [ ] Confirm memberships are shown as create or update.
+- [ ] Resolve any review rows, or explicitly skip only rows that are intentionally invalid.
+- [ ] Confirm Import.
+
+Expected result:
+
+- [ ] Four player rows are processed.
+- [ ] Four canonical players exist or are reused safely.
+- [ ] Four active player roster memberships exist in `TEST - Platform QA 2026`.
+- [ ] Player QA One and Player QA Two are on `TEST - Alpha`.
+- [ ] Player QA Three and Player QA Four are on `TEST - Beta`.
+- [ ] Four player user accounts are created or linked when account provisioning is enabled.
+- [ ] Player account usernames follow generated or existing username rules.
+- [ ] Player accounts are active.
+- [ ] Player accounts have role Player.
+- [ ] Player accounts must change password.
+- [ ] Each player user has one active primary self link.
+- [ ] Import result account provisioning summary matches the rows processed.
+
+Idempotency test:
+
+- [ ] Repeat the same player import.
+- [ ] Confirm no duplicate players are created.
+- [ ] Confirm no duplicate user accounts are created.
+- [ ] Confirm no duplicate active self links are created.
+- [ ] Confirm no duplicate active primary roster memberships are created.
+- [ ] Record whether rows were updated, already linked, or skipped as expected.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## C. Coach Import
+
+Path:
+
+```text
+/accounts/imports/coaches/new/
+```
+
+Steps:
+
+- [ ] Open Account Operations `/accounts/`.
+- [ ] Open Coach Imports `/accounts/imports/coaches/`.
+- [ ] Click New Coach Import.
+- [ ] Select season `TEST - Platform QA 2026`.
+- [ ] Upload `test_coaches_import.csv`.
+- [ ] Click Preview Import.
+- [ ] Confirm both rows are ready or reuse.
+- [ ] Confirm team and division are recognized.
+- [ ] Confirm assignment roles are Head Coach and Assistant Coach.
+- [ ] Confirm account action is Create Coach Account or Reuse Coach Account.
+- [ ] Confirm password behavior says temporary password will be generated only for new accounts.
+- [ ] Confirm Import.
+- [ ] Copy temporary passwords from the result page immediately if new coach accounts were created.
+
+Expected result:
+
+- [ ] Two coach rows are processed.
+- [ ] Coach QA One and Coach QA Two users exist.
+- [ ] Account role is Coach for both.
+- [ ] Both users are active unless the CSV says otherwise.
+- [ ] Both users are not Django staff.
+- [ ] Both users are not superusers.
+- [ ] Both users must change password if newly created.
+- [ ] Coach QA One has an assignment to `TEST - Alpha`.
+- [ ] Coach QA Two has an assignment to `TEST - Beta`.
+- [ ] No `players.Player` records were created for coaches.
+- [ ] No `UserPlayerLink` rows were created for coaches.
+
+Idempotency test:
+
+- [ ] Repeat the same coach import if safe for the environment.
+- [ ] Confirm existing coach accounts are reused by email.
+- [ ] Confirm reused coach accounts keep existing passwords unchanged.
+- [ ] Confirm no duplicate active coach assignments are created.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## D. Manual Creation
+
+Use `manual_test_records.md`.
+
+Steps:
+
+- [ ] Manually create Coach QA Manual.
+- [ ] Manually create Player QA Manual One.
+- [ ] Manually create Player QA Manual Two.
+- [ ] Create or verify Coach QA Manual assignment to `TEST - Alpha`.
+- [ ] Create or verify Player QA Manual One membership on `TEST - Alpha`.
+- [ ] Create or verify Player QA Manual Two membership on `TEST - Beta`.
+
+Expected result:
+
+- [ ] Manual coach has role Coach, active account, no Django staff, no superuser.
+- [ ] Manual players have role Player, active accounts, no Django staff, no superuser.
+- [ ] Manual players each have exactly one active primary self link.
+- [ ] Manual records have the same practical permissions as imported records.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## E. Administrator Navigation And Permissions
+
+As a staff or superuser account, verify visible navigation:
+
+- [ ] Operations Home opens `/analytics/`.
+- [ ] User Accounts opens `/accounts/`.
+- [ ] Seasons opens `/seasons/`.
+- [ ] Imports opens `/analytics/imports/`.
+- [ ] Evaluations opens `/analytics/evaluations/`.
+- [ ] Review Evaluations opens `/analytics/evaluation-review/`.
+- [ ] Profile opens `/accounts/profile/`.
+- [ ] Password opens `/accounts/password/`.
+- [ ] Log out works.
+
+Verify:
+
+- [ ] No visible link points to `/pdp/`.
+- [ ] No visible page displays `PDP`.
+- [ ] No important link returns 404.
+- [ ] No unexpected 403 appears for staff-only workflows.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## F. Coach Evaluation Workflow
+
+Test all three coaches.
+
+Minimum submissions:
+
+- Coach QA One evaluates Player QA One.
+- Coach QA Two evaluates Player QA Three.
+- Coach QA Manual evaluates Player QA Manual One.
+
+For each coach:
+
+- [ ] Sign in at `/accounts/login/`.
+- [ ] Change temporary password if prompted.
+- [ ] Open `/analytics/evaluations/`.
+- [ ] Search or filter for the target player.
+- [ ] Start an evaluation.
+- [ ] Answer several questions.
+- [ ] Save as draft.
+- [ ] Leave the page.
+- [ ] Reopen the draft.
+- [ ] Verify answers persisted.
+- [ ] Modify one answer.
+- [ ] Submit.
+- [ ] Verify submitted status.
+- [ ] Verify evaluator identity is the coach user.
+- [ ] Verify evaluator role snapshot is Coach.
+- [ ] Verify evaluation type is Coach Evaluation.
+- [ ] Verify season is `TEST - Platform QA 2026`.
+- [ ] Verify player team/division snapshot is correct.
+- [ ] Verify coach assignment snapshot is correct when available.
+
+Access behavior:
+
+- [ ] Coach can see same-team players.
+- [ ] Coach can see other QA-team players if current broad evaluator policy allows it.
+- [ ] Coach can see real players if they are active in the selected evaluation cycle; record whether this is acceptable for the pilot.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## G. Player Self-Evaluations
+
+Minimum submissions:
+
+- Player QA One self-evaluates.
+- Player QA Manual One self-evaluates.
+
+For each player:
+
+- [ ] Sign in at `/accounts/login/`.
+- [ ] Change temporary password if prompted.
+- [ ] Open `/analytics/evaluations/`.
+- [ ] Select the player's own record.
+- [ ] Confirm the form displays Self Evaluation.
+- [ ] Save as draft.
+- [ ] Leave the page.
+- [ ] Reopen the draft.
+- [ ] Verify answers persisted.
+- [ ] Modify one answer.
+- [ ] Submit.
+- [ ] Verify the evaluation appears in `/analytics/my/evaluations/`.
+- [ ] Confirm another player cannot edit it.
+
+Current behavior to verify:
+
+- [ ] The subject is the selected active player.
+- [ ] Self Evaluation is server-derived when the logged-in user has an active self link to the target player.
+- [ ] Player self-evaluation is allowed.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## H. Player Peer Evaluations
+
+Minimum submissions:
+
+- Player QA One evaluates Player QA Two.
+- Player QA Two evaluates Player QA One.
+- Player QA Manual One evaluates Player QA Manual Two.
+- One cross-team peer evaluation, such as Player QA One evaluating Player QA Three.
+
+For each:
+
+- [ ] Sign in as the evaluating player.
+- [ ] Open `/analytics/evaluations/`.
+- [ ] Search or filter for the target player.
+- [ ] Start an evaluation.
+- [ ] Confirm the form displays Peer Evaluation.
+- [ ] Save as draft.
+- [ ] Reopen the draft.
+- [ ] Submit.
+- [ ] Verify the correct subject player is recorded.
+- [ ] Verify evaluator role snapshot is Player.
+- [ ] Verify evaluation type is Peer Evaluation.
+- [ ] Confirm self-selection is labeled Self Evaluation, not Peer Evaluation.
+- [ ] Confirm players cannot edit peer evaluations submitted by someone else.
+- [ ] Confirm evaluator names are hidden in player-facing My Evaluations.
+- [ ] Confirm coaches/staff can see evaluator names in review pages.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## I. Review Workflow
+
+As an administrator, staff user, or coach reviewer:
+
+- [ ] Open `/analytics/evaluation-review/`.
+- [ ] Confirm all submitted QA evaluations appear.
+- [ ] Filter by player.
+- [ ] Filter by evaluator.
+- [ ] Filter by evaluator role.
+- [ ] Filter by evaluation type.
+- [ ] Filter by team.
+- [ ] Filter by division.
+- [ ] Filter by season.
+- [ ] Filter by evaluation cycle.
+- [ ] Filter by submitted date range.
+
+For each sampled evaluation, verify:
+
+- [ ] evaluator name
+- [ ] evaluator account
+- [ ] evaluator role
+- [ ] evaluation type
+- [ ] subject player
+- [ ] team
+- [ ] season
+- [ ] evaluation cycle
+- [ ] submission timestamp
+- [ ] status
+- [ ] answers and scores
+
+Reopen test:
+
+- [ ] Reopen one coach evaluation from staff observation review at `/analytics/observations/review/`.
+- [ ] Reopen one self-evaluation from staff observation review.
+- [ ] Reopen one peer evaluation from staff observation review.
+- [ ] Log in as the original evaluator.
+- [ ] Verify prior answers remain.
+- [ ] Verify the evaluation is editable.
+- [ ] Resubmit.
+- [ ] Confirm no duplicate observation was created.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## J. Permission Testing
+
+Direct URL access must be tested. Navigation hiding is not enough.
+
+As a coach, directly attempt:
+
+- [ ] `/analytics/imports/` - expected 403.
+- [ ] `/accounts/` - expected 403.
+- [ ] `/seasons/` - expected 403.
+- [ ] `/admin/` - expected denied unless Django staff access was intentionally granted.
+
+As a player, directly attempt:
+
+- [ ] `/analytics/imports/` - expected 403.
+- [ ] `/analytics/evaluation-review/` - expected 403.
+- [ ] `/accounts/` - expected 403.
+- [ ] `/seasons/` - expected 403.
+- [ ] Another player's private `/analytics/my/evaluations/<id>/` URL - expected 403 or not found.
+
+As an anonymous visitor, directly attempt:
+
+- [ ] `/analytics/` - expected redirect to login.
+- [ ] `/analytics/imports/` - expected redirect to login.
+- [ ] `/analytics/evaluations/` - expected redirect to login.
+- [ ] `/accounts/profile/` - expected redirect to login.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## K. Account Activation And Password Workflow
+
+Test:
+
+- one imported coach
+- one imported player
+- one manually created player
+
+For each:
+
+- [ ] Confirm expected initial active/inactive status.
+- [ ] If inactive, activate through Account Operations.
+- [ ] Sign in with temporary password.
+- [ ] Confirm forced password change happens before normal platform pages.
+- [ ] Change password.
+- [ ] Confirm redirect to the correct landing page.
+- [ ] Log out.
+- [ ] Confirm login succeeds with the new password.
+- [ ] Confirm the old temporary password no longer works.
+- [ ] Confirm password pages use Accounts routes and current platform branding.
+
+Password expectations:
+
+- Imported player temporary password: birthdate as `YYYYMMDD`.
+- Imported coach temporary password: random one-time value shown only on import result page.
+- Manually created account temporary password: one-time value shown only on creation result page.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## L. Analytics And Timeline
+
+As staff:
+
+- [ ] Open `/analytics/players/`.
+- [ ] Search for each QA player.
+- [ ] Open each player profile.
+- [ ] Confirm submitted evaluations appear.
+- [ ] Confirm timeline includes submitted evaluations.
+- [ ] Open `/analytics/players/compare/`.
+- [ ] Compare QA players.
+- [ ] Confirm coach, self, and peer evaluations are labelled distinctly.
+- [ ] Confirm command-center metrics update where applicable.
+- [ ] Confirm QA season/team context displays correctly.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## M. Mobile Testing
+
+At approximately 390-pixel width, test:
+
+- [ ] login
+- [ ] navigation
+- [ ] player import page
+- [ ] coach import page
+- [ ] evaluation list
+- [ ] evaluation form
+- [ ] draft and submit buttons
+- [ ] evaluation review page
+- [ ] account profile
+- [ ] player profile
+- [ ] player timeline
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## N. Cleanup
+
+Use `cleanup_checklist.md`.
+
+- [ ] Record defects and screenshots.
+- [ ] Deactivate all QA accounts.
+- [ ] Archive or deactivate the QA season.
+- [ ] Ensure the QA season is not current/default.
+- [ ] Hide QA teams from normal selectors where supported.
+- [ ] Do not delete linked records until cascade behavior is understood.
+- [ ] Retain the QA environment for repeat smoke tests if appropriate.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
diff --git a/docs/qa/platform_e2e/test_coaches_import.csv b/docs/qa/platform_e2e/test_coaches_import.csv
new file mode 100644
index 0000000..c1c9dd1
--- /dev/null
+++ b/docs/qa/platform_e2e/test_coaches_import.csv
@@ -0,0 +1,3 @@
+first_name,last_name,email,username,team,division,is_active,notes,source_id,season,assignment_role,assignment_start_date,assignment_end_date,assignment_source_id
+Coach,QA One,REPLACE_WITH_YOUR_EMAIL+qa-coach1@example.com,coach.qa.one,TEST - Alpha,13U House,true,QA imported coach for Alpha,qa-coach-001,TEST - Platform QA 2026,head_coach,2026-07-01,,qa-assignment-coach-001
+Coach,QA Two,REPLACE_WITH_YOUR_EMAIL+qa-coach2@example.com,coach.qa.two,TEST - Beta,13U House,true,QA imported coach for Beta,qa-coach-002,TEST - Platform QA 2026,assistant_coach,2026-07-01,,qa-assignment-coach-002
diff --git a/docs/qa/platform_e2e/test_players_import.csv b/docs/qa/platform_e2e/test_players_import.csv
new file mode 100644
index 0000000..5dd7935
--- /dev/null
+++ b/docs/qa/platform_e2e/test_players_import.csv
@@ -0,0 +1,5 @@
+first_name,last_name,preferred_name,birthdate,birth_year,gender,division,team_name,roster_status,jersey_number,membership_start_date,membership_end_date,roster_source_id,primary_positions,bats,throws,school,graduation_year,registration_id,registrant_id,team_id,source_player_id,account_email
+Player,QA One,,2013-04-01,2013,,13U House,TEST - Alpha,active,11,2026-07-01,,qa-roster-player-001,Pitcher / Infield,R,R,QA Middle School,2031,qa-reg-001,qa-member-001,qa-team-alpha,qa-player-001,REPLACE_WITH_YOUR_EMAIL+qa-player1@example.com
+Player,QA Two,,2013-05-02,2013,,13U House,TEST - Alpha,active,12,2026-07-01,,qa-roster-player-002,Catcher / Infield,R,R,QA Middle School,2031,qa-reg-002,qa-member-002,qa-team-alpha,qa-player-002,REPLACE_WITH_YOUR_EMAIL+qa-player2@example.com
+Player,QA Three,,2013-06-03,2013,,13U House,TEST - Beta,active,21,2026-07-01,,qa-roster-player-003,Outfield,L,L,QA Middle School,2031,qa-reg-003,qa-member-003,qa-team-beta,qa-player-003,REPLACE_WITH_YOUR_EMAIL+qa-player3@example.com
+Player,QA Four,,2013-07-04,2013,,13U House,TEST - Beta,active,22,2026-07-01,,qa-roster-player-004,Infield,R,R,QA Middle School,2031,qa-reg-004,qa-member-004,qa-team-beta,qa-player-004,REPLACE_WITH_YOUR_EMAIL+qa-player4@example.com

```
