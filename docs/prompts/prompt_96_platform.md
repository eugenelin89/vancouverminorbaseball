Review the Django project at:

`/Users/eugenelin/dev/vmba0`

Improve the existing Platform E2E QA package located at:

`docs/qa/platform_e2e/`

Existing files:

```text
docs/qa/platform_e2e/
├── README.md
├── platform_e2e_test_script.md
├── test_players_import.csv
├── test_coaches_import.csv
├── manual_test_records.md
└── cleanup_checklist.md
```

Existing implementation commit:

```text
d85aea5 Add platform end-to-end QA package
```

The existing package is already comprehensive and grounded in the actual application. Preserve its current structure, terminology, supported routes, schemas, and documented behavior.

Do not rewrite the QA package from scratch. Extend and refine it.

## Goal

Improve the existing QA package by adding:

1. Cross-workflow tests between imported and manually created records.
2. Username and email collision tests.
3. Inactive-account lifecycle tests.
4. Evaluation-cycle isolation tests.
5. Duplicate-evaluation and resubmission tests.
6. Browser refresh, back-button, and repeat-submit tests.
7. Archive/deactivation behavior tests.
8. More complete command-center and reporting verification.
9. A concise production smoke-test checklist.
10. Clear separation between required release-blocking tests and optional extended regression tests.

Do not create production records or run imports.

Do not change application code unless inspection reveals that the existing documentation makes a materially incorrect claim. If application behavior and documentation differ, update the documentation to reflect the current implementation and report the discrepancy.

---

# 1. Inspect Existing QA Files and Current Application Behavior

Read all files under:

`docs/qa/platform_e2e/`

Inspect the current application code and tests relevant to:

- player imports
- coach imports
- username generation and collision handling
- email reuse and conflict handling
- account activation
- temporary passwords
- forced password changes
- evaluation creation
- evaluator relationship classification
- evaluation cycles
- duplicate evaluation rules
- draft and submission behavior
- observation reopening
- season and team activation
- player roster memberships
- coach assignments
- Analytics Command Center metrics
- player timeline
- player comparison
- reporting filters
- QA or inactive season filtering

Relevant code may include:

- `accounts/services/username_service.py`
- account provisioning services
- coach import services
- player import services
- evaluation and observation services
- evaluation permission helpers
- season services
- Analytics metrics and reporting services
- related views, forms, templates, and tests

Do not assume a behavior merely because it would be desirable.

Document the actual behavior currently supported.

Where a recommended test depends on an undefined business rule, mark it clearly as:

```text
Policy decision required
```

and explain the alternatives.

---

# 2. Preserve Existing QA Fixture Design

Retain the existing isolated QA structure:

```text
Season: TEST - Platform QA 2026

Teams:
- TEST - Alpha
- TEST - Beta
```

Retain the existing QA records:

## Imported coaches

- Coach QA One
- Coach QA Two

## Imported players

- Player QA One
- Player QA Two
- Player QA Three
- Player QA Four

## Manual records

- Coach QA Manual
- Player QA Manual One
- Player QA Manual Two

Do not add large numbers of permanent fixture records.

Use the existing records for most of the new tests.

Where collision testing requires an extra CSV row or temporary record, place it in a separate clearly named negative-test fixture rather than modifying the normal happy-path fixtures.

---

# 3. Add Cross-Workflow Tests

Extend `platform_e2e_test_script.md` with a section titled:

```markdown
## Cross-Workflow Consistency Tests
```

Add tests covering:

- imported coach evaluates an imported player
- imported coach evaluates a manually created player
- manually created coach evaluates an imported player
- manually created coach evaluates a manually created player
- imported player peer-evaluates an imported player
- imported player peer-evaluates a manually created player
- manually created player peer-evaluates an imported player
- manually created player peer-evaluates a manually created player

Recommended examples:

- Coach QA One evaluates Player QA Manual One
- Coach QA Manual evaluates Player QA Two
- Player QA One evaluates Player QA Manual One
- Player QA Manual One evaluates Player QA Two

For each combination, verify:

- the evaluator account is recognized correctly
- the evaluator role snapshot is correct
- Self versus Peer versus Coach is classified correctly
- the subject player is correct
- season, team, division, and evaluation-cycle snapshots are correct
- draft, reopen, and submit work identically
- imported and manually created accounts have equivalent practical permissions
- no differences arise from the provisioning method

Add a compact matrix showing which combinations were tested.

---

# 4. Add Username-Collision Testing

Determine the actual username-collision behavior from the code.

Add a section titled:

```markdown
## Username Collision Tests
```

Test scenarios such as:

1. A generated username already exists.
2. The existing username belongs to the same intended account.
3. The existing username belongs to a different account.
4. Two imported rows would generate the same base username.
5. A manually requested username conflicts with an existing account.

Verify whether the application:

- reuses the account
- generates a suffix
- blocks the row
- marks the row for review
- reports a conflict
- risks assigning the wrong person

Do not state that suffixing occurs unless the implementation supports it.

If practical, create a separate fixture:

```text
test_account_collisions.csv
```

Only create this file if there is a supported UI workflow through which it can safely be tested.

Otherwise, document the exact manual steps.

Collision records must:

- use artificial identities
- use controlled email placeholders
- be clearly marked as negative-test data
- not be part of the standard happy-path import

---

# 5. Add Email Reuse and Conflict Testing

Add a section titled:

```markdown
## Email Reuse and Conflict Tests
```

Cover:

### Coach email scenarios

- same coach, same email, repeated import
- different coach identity using an existing coach email
- coach import using an email belonging to a Player account
- coach import using an email belonging to Staff or another non-Coach role
- email differing only by letter case
- leading or trailing whitespace around an email

### Player account-provisioning scenarios

- repeated import with the same player and same email
- same player with a changed email
- different player using an existing Player account email
- player import using an email already owned by a Coach account
- email differing only by case
- whitespace normalization

For each scenario, verify:

- account reuse behavior
- conflict behavior
- preview status
- whether commit is blocked
- whether a user-player link is created
- whether an existing role is changed
- whether an unintended duplicate account appears
- whether the result clearly explains the outcome

Do not include real email addresses in committed fixtures.

---

# 6. Add Account Activation Lifecycle Testing

Extend the account section with a complete inactive-account lifecycle.

Test at least:

- one imported coach with `is_active=false`
- one deactivated player account
- one manually created inactive account, if supported

Verify:

1. The inactive account is created or retained.
2. The inactive user cannot sign in.
3. The account does not gain access merely by knowing the correct password.
4. Staff can activate it through the supported Account Operations workflow.
5. The activated user can sign in.
6. Forced password change still behaves correctly.
7. The user can log out and sign in with the new password.
8. The original temporary password no longer works.
9. Deactivating the account again blocks login.
10. Historical evaluations remain attributed to the deactivated account.

If the coach import CSV supports `is_active`, consider creating:

```text
test_coaches_inactive_import.csv
```

containing one clearly named inactive QA coach.

Only add this fixture if it improves the test without unnecessarily increasing permanent QA data.

---

# 7. Add Evaluation-Cycle Isolation Tests

Inspect how evaluation cycles are selected, filtered, and assigned.

Add a section titled:

```markdown
## Evaluation Cycle Isolation Tests
```

Use two QA evaluation cycles where supported, for example:

- `TEST - Cycle A`
- `TEST - Cycle B`

Do not invent UI routes or fields.

Test:

- the same coach evaluating the same player once in each cycle
- the same player completing a self-evaluation once in each cycle
- the same player evaluating the same peer once in each cycle
- review filters separating Cycle A and Cycle B
- timelines showing the correct cycle
- comparison and summary metrics using the intended cycle
- drafts from one cycle not appearing as drafts in another
- reopening an evaluation preserving its original cycle
- inactive or closed cycles preventing new submissions if that is intended behavior

Explicitly identify the uniqueness rule found in the implementation.

Examples:

```text
One evaluator + one player + one evaluation type + one cycle
```

or whatever the actual rule is.

If the application currently permits multiple evaluations where the expected policy is unclear, mark:

```text
Policy decision required
```

---

# 8. Add Duplicate-Evaluation Tests

Add a section titled:

```markdown
## Duplicate Evaluation and Repeat Submission Tests
```

Test:

- starting the same evaluation twice in separate browser tabs
- double-clicking Submit
- refreshing immediately after submission
- using the browser back button after submission and submitting again
- reopening a submitted evaluation and resubmitting
- attempting to create another evaluation for the same evaluator, player, type, and cycle
- submitting an old draft after a newer draft or submission exists
- two requests arriving close together, where practical to test

Verify:

- whether duplicates are blocked
- whether the existing draft is reused
- whether duplicate observations are created
- whether the user receives a useful message
- whether answers are overwritten unexpectedly
- whether review counts increase incorrectly

Record the actual intended uniqueness behavior.

Do not assume that only one evaluation is permitted unless the code or product rules establish that.

---

# 9. Add Browser Navigation and State Tests

Add a section titled:

```markdown
## Browser State and Navigation Tests
```

For coach, self, and peer evaluations, test:

### Refresh

1. Begin an evaluation.
2. Enter answers.
3. Save as draft.
4. Refresh the page.
5. Confirm answers remain.
6. Submit.
7. Refresh the success page.
8. Confirm no duplicate submission is created.

### Back and Forward

1. Begin an evaluation.
2. Save a draft.
3. Navigate back.
4. Navigate forward.
5. Confirm state remains valid.
6. Submit once.
7. Use Back.
8. Attempt to submit again.
9. Verify no duplicate is created.

### Multiple tabs

1. Open the same draft in two tabs.
2. Modify both copies differently.
3. Save one.
4. Save or submit the other.
5. Record whether stale data overwrites newer data.
6. Verify whether the user receives a conflict warning.

If stale-update protection is not implemented, document the risk rather than claiming a pass.

---

# 10. Add Archive and Deactivation Behavior Tests

Add a section titled:

```markdown
## Archive and Deactivation Behavior Tests
```

Do not delete records while performing the normal test.

Test the effects of deactivating or archiving, where supported:

### Season

- mark `TEST - Platform QA 2026` inactive
- verify whether it disappears from active selectors
- verify whether historical evaluations remain viewable
- verify whether timelines still load
- verify whether player comparison still works
- verify whether review filters can still access historical data
- verify whether new evaluations can still be started

### Team

- deactivate or end `TEST - Alpha`, if supported
- verify roster and coach assignment history remains intact
- verify historical evaluation snapshots still display
- verify inactive teams do not appear in active assignment workflows

### Player account

- deactivate Player QA One’s account
- verify login is blocked
- verify player record and history still exist
- verify coach and peer evaluations of the player remain visible to authorized reviewers
- verify the player does not appear in new-evaluation selectors if that is the intended behavior

### Coach account

- deactivate Coach QA One
- verify login is blocked
- verify historical coach evaluations remain attributed correctly
- verify the coach no longer appears as an active evaluator or assignment option if intended

### Membership and assignment

- end a player roster membership
- end a coach assignment
- verify historical snapshots remain correct
- verify active permissions update appropriately

Document actual behavior and any policy ambiguity.

---

# 11. Expand Analytics and Reporting Verification

Extend the existing Analytics and Timeline section.

Test the following Command Center and reporting outputs where currently implemented:

- total player counts
- active player counts
- active coach or evaluator counts
- observation or evaluation counts
- draft counts
- submitted counts
- completion percentages
- average scores
- recent observations
- import summaries
- season summaries
- team summaries
- evaluator-role breakdowns
- evaluation-type breakdowns
- variance rows or score differences
- player comparison
- player timeline

For each relevant metric:

1. Record the value before creating QA evaluations.
2. Submit a known number of QA evaluations.
3. Refresh the dashboard.
4. Confirm the metric changes by the expected amount.
5. Filter to the QA season if supported.
6. Confirm QA records do not unexpectedly pollute real-season reporting.
7. Deactivate or archive the QA season.
8. Confirm reports treat archived QA data according to the intended policy.

Pay special attention to:

- coach evaluations
- self-evaluations
- peer evaluations

Verify they are:

- counted correctly
- labelled distinctly
- not accidentally combined
- not double-counted after reopen and resubmit
- associated with the correct cycle and season

Where a report intentionally aggregates evaluation types, document that behavior.

---

# 12. Add a Production Smoke Test

Create a new file:

`docs/qa/platform_e2e/production_smoke_test.md`

This should be a concise checklist intended to take roughly one short testing session after deployment.

Do not duplicate the entire E2E test.

Include:

## Setup

- confirm deployed commit
- confirm database backup
- confirm QA season is active for testing
- activate only the required QA accounts

## Admin workflow

- sign in as administrator
- open Operations Home
- confirm Imports, User Accounts, Seasons, Evaluations, and Review links work
- import or re-import the standard player CSV
- verify no duplicates
- import or re-import the standard coach CSV
- verify no duplicates
- create or verify one manual account

## Coach workflow

- sign in as an imported coach
- create, save, reopen, and submit one coach evaluation
- sign in as the manual coach
- submit one evaluation of an imported player

## Player workflow

- sign in as an imported player
- submit one self-evaluation
- submit one peer evaluation of a manual player
- sign in as a manual player
- submit one self-evaluation or peer evaluation of an imported player

## Review workflow

- sign back in as administrator
- confirm all smoke-test evaluations appear
- reopen one evaluation
- resubmit it
- confirm no duplicate
- confirm player timeline
- confirm player comparison
- confirm key Command Center metrics

## Security workflow

- verify coach receives 403 from Imports
- verify player receives 403 from Review
- verify anonymous user is redirected to login

## Cleanup

- deactivate QA accounts not needed
- archive or deactivate the QA season when appropriate
- record Pass or Fail
- record critical defects

Use checkboxes and provide fields for:

```text
Tester:
Date:
Environment:
Commit:
Overall result:
Critical defects:
Non-critical defects:
```

---

# 13. Separate Required and Extended Tests

At the top of `platform_e2e_test_script.md`, add a test classification section.

Use three levels:

## Release-blocking

Examples:

- imports
- account provisioning
- coach evaluation
- self-evaluation
- peer evaluation
- review
- direct URL permissions
- password change
- no duplicate submissions
- basic dashboard integrity

## Standard regression

Examples:

- imported/manual cross-workflows
- cycle isolation
- inactive-account lifecycle
- archive behavior
- reporting filters
- mobile layout

## Extended edge cases

Examples:

- collision handling
- multi-tab stale edits
- browser back/forward
- case and whitespace normalization
- conflicting cross-role emails

Do not remove any existing test merely because it is classified as extended.

---

# 14. Update README.md

Update the README to include:

- `production_smoke_test.md`
- any new negative-test fixture files
- the distinction between happy-path fixtures and collision fixtures
- instructions not to import collision fixtures during normal smoke testing
- test-level definitions
- the recommended sequence:

```text
Production smoke test
→ release-blocking E2E tests
→ standard regression
→ extended edge cases
```

Keep the README concise.

Preserve the existing actual UI paths unless code inspection shows they have changed.

---

# 15. Update Cleanup Checklist

Extend `cleanup_checklist.md` to include:

- deactivate collision-test accounts
- confirm inactive-account fixtures are not left enabled
- close or archive additional QA evaluation cycles
- check that dashboard metrics are no longer filtered incorrectly
- verify QA season is not current/default
- verify QA records are not visible in real operational selectors
- preserve evidence for defects
- remove temporary passwords from notes
- document any intentionally retained QA evaluations

---

# 16. Fixture Rules

Do not modify the standard happy-path CSVs unless a correction is required.

If adding negative-test fixtures, use clear names such as:

```text
test_coaches_inactive_import.csv
test_account_collision_cases.csv
```

Each negative fixture must include a Markdown explanation of:

- its purpose
- prerequisites
- expected outcome
- cleanup steps
- why it must not be used in normal production imports

Use only actual accepted CSV fields.

Do not include:

- real personal information
- real passwords
- uncontrolled email addresses
- formulas
- unsupported columns

Use placeholder emails that must be replaced by the tester.

---

# 17. Validation

Run:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
git diff --check
```

Validate every CSV using Python’s standard `csv` module.

Check:

- expected row counts
- no duplicate headers
- no empty required values
- valid date formats
- accepted role values
- accepted boolean values
- no formulas
- no accidental real email addresses

If repository tests directly cover any behavior described by the documentation, run the relevant focused tests.

Do not run production imports.

Do not modify the production database.

---

# 18. Review for Unsupported Claims

Before completion, review every new assertion in the QA documentation.

For each assertion, ensure it is supported by one of:

- application code
- existing tests
- actual route configuration
- existing documented product policy

Where behavior is not established, use wording such as:

```text
Verify the current behavior and compare it with the intended policy.
```

or:

```text
Policy decision required.
```

Do not turn recommendations into false descriptions of current functionality.

---

# 19. Completion Report

At completion, report:

1. Files modified.
2. Files added.
3. New test sections added.
4. New fixtures added, if any.
5. Actual username-collision behavior discovered.
6. Actual email-conflict behavior discovered.
7. Actual duplicate-evaluation rule discovered.
8. Actual evaluation-cycle uniqueness behavior discovered.
9. Archive and deactivation behavior discovered.
10. Reporting metrics verified through code or tests.
11. Policy decisions still required.
12. Validation commands and results.
13. Relevant test commands and results.
14. Any inaccuracies corrected in the original QA package.

Commit the improvements to the current branch with a clear commit message, for example:

```text
Expand platform end-to-end QA coverage
```

Do not push unless explicitly instructed.

==================================================
Implementation Commit Diff
==================================================

```diff
commit fd8afb812e20e6527de4264af53968ebd6763b7a
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 23 14:37:58 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 23 14:37:58 2026 -0700

    Expand platform end-to-end QA coverage
---
 docs/qa/platform_e2e/README.md                     |  26 +-
 docs/qa/platform_e2e/cleanup_checklist.md          |  22 +
 docs/qa/platform_e2e/negative_test_fixtures.md     |  80 ++++
 docs/qa/platform_e2e/platform_e2e_test_script.md   | 505 +++++++++++++++++++++
 docs/qa/platform_e2e/production_smoke_test.md      |  79 ++++
 .../test_coach_account_collision_cases.csv         |   7 +
 .../platform_e2e/test_coaches_inactive_import.csv  |   2 +
 7 files changed, 720 insertions(+), 1 deletion(-)

diff --git a/docs/qa/platform_e2e/README.md b/docs/qa/platform_e2e/README.md
index 726fdf8..e5a7ae4 100644
--- a/docs/qa/platform_e2e/README.md
+++ b/docs/qa/platform_e2e/README.md
@@ -18,6 +18,10 @@ Recommended QA teams:
 - `platform_e2e_test_script.md`: step-by-step production QA script.
 - `test_players_import.csv`: four imported player records.
 - `test_coaches_import.csv`: two imported coach records.
+- `test_coaches_inactive_import.csv`: optional inactive-coach lifecycle fixture.
+- `test_coach_account_collision_cases.csv`: optional negative-test fixture for coach account collision behavior.
+- `negative_test_fixtures.md`: purpose, prerequisites, expected outcomes, and cleanup for optional negative fixtures.
+- `production_smoke_test.md`: concise post-deployment smoke-test checklist.
 - `manual_test_records.md`: records intentionally left for manual creation.
 - `cleanup_checklist.md`: safe cleanup checklist after testing.

@@ -46,13 +50,30 @@ Recommended QA teams:
 1. Confirm a recent database backup exists.
 2. Create or verify the QA season `TEST - Platform QA 2026`.
 3. Create or verify the QA teams `TEST - Alpha` and `TEST - Beta`.
-4. Replace every `REPLACE_WITH_YOUR_EMAIL+...@example.com` placeholder in both CSV files with controlled test inbox aliases before importing.
+4. Replace every `REPLACE_WITH_YOUR_EMAIL+...@example.com` placeholder in the CSV files with controlled test inbox aliases before importing.
 5. Import `test_players_import.csv` from `/analytics/imports/new/`.
 6. Import `test_coaches_import.csv` from `/accounts/imports/coaches/new/`.
 7. Manually create the records listed in `manual_test_records.md`.
 8. Follow `platform_e2e_test_script.md`.
 9. After testing, follow `cleanup_checklist.md`.

+## Test Levels
+
+Use the package in this order:
+
+```text
+Production smoke test
+-> release-blocking E2E tests
+-> standard regression
+-> extended edge cases
+```
+
+- **Release-blocking**: imports, account provisioning, coach evaluation, self-evaluation, peer evaluation, review, direct URL permissions, password change, duplicate-submission protection, and basic dashboard integrity.
+- **Standard regression**: imported/manual cross-workflows, cycle isolation, inactive-account lifecycle, archive behavior, reporting filters, and mobile layout.
+- **Extended edge cases**: collision handling, multi-tab stale edits, browser back/forward behavior, case and whitespace normalization, and conflicting cross-role emails.
+
+Do not import optional negative fixtures during a normal production smoke test. Use them only when deliberately testing collision or inactive-account behavior.
+
 ## Important Import Notes

 - Player import and coach import use different CSV schemas.
@@ -65,6 +86,9 @@ Recommended QA teams:
 - Imported coaches do not receive Django staff or superuser access.
 - Coach import creates or updates season teams and coach assignments.
 - Player import creates or updates season teams and player roster memberships.
+- Generated usernames use `firstname.lastname` and suffix with `2`, `3`, and so on when the generated base already exists.
+- Explicit usernames are normalized and rejected when already used by a different account.
+- Emails are normalized by trimming whitespace and comparing case-insensitively.

 ## Placeholder Email Rule

diff --git a/docs/qa/platform_e2e/cleanup_checklist.md b/docs/qa/platform_e2e/cleanup_checklist.md
index 5d9b34e..2f8082b 100644
--- a/docs/qa/platform_e2e/cleanup_checklist.md
+++ b/docs/qa/platform_e2e/cleanup_checklist.md
@@ -5,7 +5,9 @@ Use this checklist after the end-to-end QA run. Prefer deactivation and archival
 ## Before Cleanup

 - [ ] Defects, screenshots, and test notes have been recorded.
+- [ ] Evidence needed for open defects has been preserved.
 - [ ] Temporary passwords copied during testing are destroyed or removed from notes.
+- [ ] Temporary passwords have been removed from tickets, shared documents, chat logs, and screenshots unless the artifact is access-controlled and required for a defect.
 - [ ] The QA season is not required for immediate retesting.
 - [ ] A recent database backup exists.

@@ -28,6 +30,8 @@ Deactivate these test accounts:
 - [ ] `player.qa.four`
 - [ ] `player.qa.manual.one`
 - [ ] `player.qa.manual.two`
+- [ ] `coach.qa.inactive`
+- [ ] any accounts created from `test_coach_account_collision_cases.csv`

 Verify:

@@ -35,6 +39,7 @@ Verify:
 - [ ] No QA account is a superuser.
 - [ ] QA accounts requiring password change are either deactivated or documented for retest.
 - [ ] Temporary passwords are not stored in shared notes, tickets, screenshots, or chat logs.
+- [ ] Inactive-account lifecycle fixtures are not left enabled unless intentionally retained for repeat testing.

 ## User-Player Links

@@ -58,7 +63,10 @@ Clean up:
 - [ ] Mark `TEST - Platform QA 2026` inactive if the QA run is complete.
 - [ ] Mark `TEST - Alpha` inactive if supported by the current workflow.
 - [ ] Mark `TEST - Beta` inactive if supported by the current workflow.
+- [ ] Close, deactivate, or archive `TEST - Cycle A` if it was created.
+- [ ] Close, deactivate, or archive `TEST - Cycle B` if it was created.
 - [ ] Confirm QA teams no longer appear in normal active selectors, or document why they remain visible.
+- [ ] Confirm QA records are not visible in real operational selectors unless the selector intentionally includes inactive or historical data.

 ## Roster Memberships And Coach Assignments

@@ -69,12 +77,26 @@ Clean up:
 ## Analytics Data

 - [ ] Verify reports and review pages no longer include QA data in normal operating filters, or document the QA season filter users should apply.
+- [ ] Verify dashboard metrics are not filtered incorrectly after QA season deactivation.
+- [ ] Verify command-center counts are understood if QA data remains in all-time aggregates.
 - [ ] Preserve submitted QA evaluations if they are useful for regression testing.
+- [ ] Document any intentionally retained QA evaluations, including season, cycle, and players involved.
 - [ ] Delete evaluations only after backup and cascade review.

+## Negative-Test Fixtures
+
+- [ ] Deactivate collision-test accounts.
+- [ ] Confirm inactive-coach fixture accounts remain inactive after testing.
+- [ ] Confirm collision-test imports did not create real player records.
+- [ ] Confirm collision-test imports did not create user-player links.
+- [ ] Remove temporary passwords from notes.
+- [ ] Keep negative-test result notes separate from normal smoke-test sign-off.
+
 ## Final Cleanup Review

 - [ ] No real users are assigned to the QA season.
 - [ ] No real players are linked to QA accounts.
 - [ ] QA records are clearly identifiable by `QA` or `TEST -`.
+- [ ] QA season is not current/default.
+- [ ] QA records are not visible in normal real-season operational selectors unless intentionally retained.
 - [ ] The cleanup outcome is recorded in the QA run notes.
diff --git a/docs/qa/platform_e2e/negative_test_fixtures.md b/docs/qa/platform_e2e/negative_test_fixtures.md
new file mode 100644
index 0000000..d91913c
--- /dev/null
+++ b/docs/qa/platform_e2e/negative_test_fixtures.md
@@ -0,0 +1,80 @@
+# Negative Test Fixtures
+
+These fixtures are optional. Do not use them during the normal production smoke test or happy-path release validation.
+
+Replace all placeholder email addresses with controlled test inbox aliases before importing.
+
+## `test_coaches_inactive_import.csv`
+
+Purpose:
+
+- Verify that coach import supports inactive accounts.
+- Verify inactive imported accounts cannot sign in until staff activates them.
+- Verify activation does not change role, staff status, superuser status, assignment history, or temporary-password behavior.
+
+Prerequisites:
+
+- QA season `TEST - Platform QA 2026` exists and is active.
+- QA team `TEST - Alpha` exists or may be created by import.
+- The placeholder email has been replaced with a controlled test inbox alias.
+
+Expected outcome:
+
+- One coach account is created with role Coach.
+- `User.is_active` is false.
+- The coach season assignment is created as inactive.
+- A temporary password is shown once on the result page.
+- The inactive coach cannot sign in until activated through Account Operations.
+- After activation, the coach must change password before normal platform use.
+
+Cleanup:
+
+- Deactivate `coach.qa.inactive` after the lifecycle test.
+- End or deactivate the inactive coach assignment if it is not needed for future regression testing.
+
+## `test_coach_account_collision_cases.csv`
+
+Purpose:
+
+- Exercise coach import username and email collision behavior without modifying the happy-path coach fixture.
+- Verify preview and result messages are clear enough for staff.
+
+Prerequisites:
+
+- Run the standard player and coach imports first.
+- The standard imports should have created or reused `coach.qa.one` and the Player QA One account.
+- Replace every placeholder email address with controlled test inbox aliases using the same aliases used for the standard fixture where the row intentionally references an existing account.
+
+Expected outcome:
+
+- Row using Coach QA One's existing coach email should reuse the existing coach account and keep its password unchanged.
+- Row using Player QA One's email should conflict because the email belongs to a non-coach account.
+- Two rows that generate the same `collision.coach` username should leave one row ready and mark the other as a username conflict in preview.
+- Explicit username `coach.qa.one` should conflict because that username already exists.
+- The whitespace email row should trim and normalize the email before account creation.
+
+Cleanup:
+
+- Deactivate any new collision-test coach accounts.
+- Remove temporary passwords from notes.
+- Confirm no `players.Player` records or `UserPlayerLink` rows were created by the coach collision fixture.
+
+## Player Account-Provisioning Collision Tests
+
+No separate mixed-schema CSV is included because player account-provisioning collision tests are safest through the existing player import workflow:
+
+- Use a working copy of `test_players_import.csv`.
+- Change one player row's `account_email` to match an existing unrelated player account email.
+- Change another player row's `account_email` to match an existing coach account email.
+- Re-import through `/analytics/imports/new/` with account provisioning enabled.
+
+Expected outcome:
+
+- Same player with the same email should reuse or already-link safely.
+- Different player using an existing player email should conflict and should not create a self link.
+- Player import using an email owned by a coach account should conflict and should not change the coach role.
+- Case-only email differences and surrounding whitespace should normalize to the same existing email.
+
+Policy decision required:
+
+- Decide whether QA should maintain permanent collision-test player records or only use disposable working copies during extended regression.
diff --git a/docs/qa/platform_e2e/platform_e2e_test_script.md b/docs/qa/platform_e2e/platform_e2e_test_script.md
index ec044c4..468896e 100644
--- a/docs/qa/platform_e2e/platform_e2e_test_script.md
+++ b/docs/qa/platform_e2e/platform_e2e_test_script.md
@@ -4,6 +4,58 @@ Use this script to test account provisioning, player imports, coach imports, sea

 Do not use real personal data. Replace all placeholder email addresses before importing.

+## Test Classification
+
+Run tests in this order:
+
+```text
+Production smoke test
+-> release-blocking E2E tests
+-> standard regression
+-> extended edge cases
+```
+
+### Release-Blocking
+
+These tests must pass before a production release is accepted:
+
+- [ ] player import
+- [ ] player account provisioning
+- [ ] coach import
+- [ ] manual account creation
+- [ ] coach evaluation submission
+- [ ] player self-evaluation submission
+- [ ] player peer-evaluation submission
+- [ ] evaluation review
+- [ ] direct URL permissions
+- [ ] forced password change
+- [ ] no duplicate submissions after refresh or repeat submit
+- [ ] basic Analytics Command Center integrity
+
+### Standard Regression
+
+These tests should run for a planned release or when related code changes:
+
+- [ ] imported/manual cross-workflow consistency
+- [ ] evaluation-cycle isolation
+- [ ] inactive-account lifecycle
+- [ ] archive and deactivation behavior
+- [ ] reporting filters
+- [ ] player timeline
+- [ ] player comparison
+- [ ] mobile layout
+
+### Extended Edge Cases
+
+These tests are useful before major pilots, after import/account changes, or when investigating defects:
+
+- [ ] username collision handling
+- [ ] email reuse and cross-role conflict handling
+- [ ] browser back/forward behavior
+- [ ] multi-tab stale edits
+- [ ] case and whitespace normalization
+- [ ] conflicting cross-role emails
+
 ## QA Fixture Summary

 QA season:
@@ -563,3 +615,456 @@ Pass / Fail:
 Result:
 Notes:
 ```
+
+## Cross-Workflow Consistency Tests
+
+Level: Standard regression.
+
+Use these tests to verify that imported and manually created accounts behave the same in evaluation workflows.
+
+| Combination | Example | Tested | Result |
+| --- | --- | --- | --- |
+| Imported coach evaluates imported player | Coach QA One evaluates Player QA One | [ ] |  |
+| Imported coach evaluates manual player | Coach QA One evaluates Player QA Manual One | [ ] |  |
+| Manual coach evaluates imported player | Coach QA Manual evaluates Player QA Two | [ ] |  |
+| Manual coach evaluates manual player | Coach QA Manual evaluates Player QA Manual One | [ ] |  |
+| Imported player evaluates imported player | Player QA One evaluates Player QA Two | [ ] |  |
+| Imported player evaluates manual player | Player QA One evaluates Player QA Manual One | [ ] |  |
+| Manual player evaluates imported player | Player QA Manual One evaluates Player QA Two | [ ] |  |
+| Manual player evaluates manual player | Player QA Manual One evaluates Player QA Manual Two | [ ] |  |
+
+For each combination:
+
+- [ ] Start an evaluation.
+- [ ] Save as draft.
+- [ ] Leave the page.
+- [ ] Reopen the draft.
+- [ ] Submit.
+- [ ] If reopened by staff, resubmit as the original evaluator.
+- [ ] Confirm evaluator account is recognized correctly.
+- [ ] Confirm evaluator role snapshot is correct.
+- [ ] Confirm Self, Peer, or Coach classification is correct.
+- [ ] Confirm subject player is correct.
+- [ ] Confirm season snapshot is `TEST - Platform QA 2026`.
+- [ ] Confirm team and division snapshots match the target player's QA roster membership.
+- [ ] Confirm evaluation-cycle snapshot is correct.
+- [ ] Confirm imported and manual accounts have equivalent practical permissions.
+- [ ] Confirm no behavior difference is caused only by provisioning method.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## Username Collision Tests
+
+Level: Extended edge cases.
+
+Actual behavior discovered from code:
+
+- Generated usernames use `firstname.lastname`.
+- When a generated username already exists in the database, the username service adds suffixes such as `firstname.lastname2`.
+- Explicit usernames are normalized to lowercase and trimmed.
+- Explicit usernames with letters, numbers, dots, underscores, and hyphens are allowed.
+- Explicit usernames that already exist are rejected.
+- Coach import detects two ready rows that would use the same final username in the same CSV and marks the later row as a conflict.
+- Manual account creation rejects duplicate usernames.
+- Manual player-account creation rejects duplicate usernames and refuses to create a second self account for the same player.
+
+Use optional fixture:
+
+```text
+test_coach_account_collision_cases.csv
+```
+
+Do not use this fixture in a normal smoke test.
+
+Scenarios:
+
+- [ ] Generated username already exists before import.
+- [ ] Existing username belongs to the same intended account and email matches an existing coach.
+- [ ] Existing username belongs to a different account.
+- [ ] Two imported coach rows generate the same base username.
+- [ ] Manually requested username conflicts with an existing account.
+
+Verify:
+
+- [ ] Generated username collision suffixes correctly when the existing username is already in the database.
+- [ ] Existing coach email is reused safely and password remains unchanged.
+- [ ] Explicit duplicate username is reported as a conflict.
+- [ ] Two new rows that would generate the same final username do not both create accounts.
+- [ ] Conflict rows do not create accounts, assignments, player records, or user-player links.
+- [ ] Staff can understand the preview/result message.
+
+Policy decision required:
+
+- Decide whether duplicate generated names in the same coach CSV should suffix automatically instead of marking the later row as a conflict.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## Email Reuse and Conflict Tests
+
+Level: Extended edge cases.
+
+Actual behavior discovered from code:
+
+- Emails are normalized by trimming whitespace and comparing case-insensitively.
+- Coach import reuses an existing Coach account by email and keeps that account's password unchanged.
+- Coach import does not activate an existing inactive Coach account and does not reset its password.
+- Coach import conflicts when the email belongs to a non-Coach account.
+- Player account provisioning reuses an existing self-linked user for the same player.
+- Player account provisioning conflicts when the imported email belongs to an unrelated existing user.
+- Player account provisioning does not change an existing coach role into a player role.
+
+Coach email scenarios:
+
+- [ ] Same coach, same email, repeated import.
+- [ ] Different coach identity using an existing coach email.
+- [ ] Coach import using an email belonging to a Player account.
+- [ ] Coach import using an email belonging to Staff or another non-Coach role.
+- [ ] Email differing only by letter case.
+- [ ] Leading or trailing whitespace around an email.
+
+Player account-provisioning scenarios:
+
+- [ ] Repeated import with same player and same email.
+- [ ] Same player with a changed email.
+- [ ] Different player using an existing Player account email.
+- [ ] Player import using an email already owned by a Coach account.
+- [ ] Email differing only by case.
+- [ ] Whitespace normalization.
+
+For each scenario, verify:
+
+- [ ] account reuse behavior
+- [ ] conflict behavior
+- [ ] preview status
+- [ ] whether commit is blocked or row is skipped/conflicted
+- [ ] whether a user-player link is created
+- [ ] whether an existing role changes
+- [ ] whether an unintended duplicate account appears
+- [ ] whether the result clearly explains the outcome
+
+Policy decision required:
+
+- Decide whether an existing coach email reused with a different first/last name should require staff review before assignment changes are committed.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## Inactive-Account Lifecycle Tests
+
+Level: Standard regression.
+
+Use optional fixture:
+
+```text
+test_coaches_inactive_import.csv
+```
+
+Also test one deactivated player account and one manually created inactive account where practical.
+
+Steps:
+
+- [ ] Import the inactive coach fixture.
+- [ ] Confirm the inactive coach user is created or retained.
+- [ ] Confirm the inactive coach cannot sign in.
+- [ ] Confirm knowing the correct temporary password does not grant access while inactive.
+- [ ] Confirm staff can activate the account from Account Operations.
+- [ ] Confirm the activated user can sign in.
+- [ ] Confirm forced password change still applies.
+- [ ] Confirm the user can log out and sign in with the new password.
+- [ ] Confirm the original temporary password no longer works.
+- [ ] Deactivate the account again.
+- [ ] Confirm login is blocked again.
+- [ ] Submit or locate a historical evaluation by the account before deactivation where practical.
+- [ ] Confirm historical evaluations remain attributed to the deactivated account.
+
+Actual behavior discovered from code:
+
+- New inactive coach import rows create inactive Django users.
+- Existing inactive coach accounts reused by coach import are not activated and do not get a new password.
+- Operational password reset preserves inactive account state.
+- Account deactivation preserves profile, user-player links, provenance, and historical attribution.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## Evaluation Cycle Isolation Tests
+
+Level: Standard regression.
+
+Use two QA evaluation cycles where supported:
+
+- `TEST - Cycle A`
+- `TEST - Cycle B`
+
+Create or verify both cycles through the supported staff/admin workflow available in the environment. Do not invent a route if cycle management is admin-only in the deployed build.
+
+Actual uniqueness rule discovered from code:
+
+```text
+One evaluator + one player + one observation type + one evaluation perspective + one evaluation cycle.
+Self evaluations are stricter: one self evaluation per player per cycle.
+```
+
+Tests:
+
+- [ ] Same coach evaluates the same player once in Cycle A.
+- [ ] Same coach evaluates the same player once in Cycle B.
+- [ ] Same player completes a self-evaluation once in Cycle A.
+- [ ] Same player completes a self-evaluation once in Cycle B.
+- [ ] Same player evaluates the same peer once in Cycle A.
+- [ ] Same player evaluates the same peer once in Cycle B.
+- [ ] Review filters separate Cycle A and Cycle B.
+- [ ] Timeline entries show the correct cycle.
+- [ ] Player comparison includes only submitted evaluations according to current comparison behavior.
+- [ ] Command Center cycle filter changes completion/submitted counts for the selected cycle.
+- [ ] Drafts from one cycle do not appear as drafts in another.
+- [ ] Reopening an evaluation preserves its original cycle.
+- [ ] Inactive cycles do not become the default active cycle.
+
+Policy decision required:
+
+- Confirm whether inactive or closed cycles should prevent new submissions through the UI or whether staff/admin lifecycle controls are sufficient.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## Duplicate Evaluation and Repeat Submission Tests
+
+Level: Release-blocking for basic duplicate protection; extended for multi-tab concurrency.
+
+Actual behavior discovered from code:
+
+- Starting the same evaluator/player/perspective/cycle evaluation reuses the existing draft or redirects to the submitted detail.
+- Service-level duplicate creation is blocked for the same evaluator, player, observation type, perspective, and cycle.
+- Self-evaluation duplicate creation is blocked per player and cycle.
+- Submission revalidates uniqueness before saving.
+- Reopened evaluations reuse the same observation record.
+
+Tests:
+
+- [ ] Start the same evaluation twice in separate browser tabs.
+- [ ] Double-click Submit.
+- [ ] Refresh immediately after submission.
+- [ ] Use browser Back after submission and submit again.
+- [ ] Reopen a submitted evaluation and resubmit it.
+- [ ] Attempt to create another evaluation for the same evaluator, player, type, perspective, and cycle.
+- [ ] Submit an old draft after a newer draft or submission exists.
+- [ ] Try two requests close together where practical.
+
+Verify:
+
+- [ ] duplicates are blocked or existing drafts are reused
+- [ ] duplicate observations are not created
+- [ ] the user receives a useful message or redirect
+- [ ] answers are not overwritten unexpectedly during ordinary single-tab use
+- [ ] review counts do not increase incorrectly
+
+Risk to document:
+
+- Multi-tab stale-update conflict warnings are not currently a documented feature. If one tab overwrites another tab's saved draft, record it as a known UX risk unless product policy requires optimistic locking.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## Browser State and Navigation Tests
+
+Level: Extended edge cases.
+
+Run for coach, self, and peer evaluations.
+
+### Refresh
+
+- [ ] Begin an evaluation.
+- [ ] Enter answers.
+- [ ] Save as draft.
+- [ ] Refresh the page.
+- [ ] Confirm answers remain.
+- [ ] Submit.
+- [ ] Refresh the success/detail page.
+- [ ] Confirm no duplicate submission is created.
+
+### Back and Forward
+
+- [ ] Begin an evaluation.
+- [ ] Save a draft.
+- [ ] Navigate back.
+- [ ] Navigate forward.
+- [ ] Confirm state remains valid.
+- [ ] Submit once.
+- [ ] Use Back.
+- [ ] Attempt to submit again.
+- [ ] Verify no duplicate is created.
+
+### Multiple Tabs
+
+- [ ] Open the same draft in two tabs.
+- [ ] Modify both copies differently.
+- [ ] Save one.
+- [ ] Save or submit the other.
+- [ ] Record whether stale data overwrites newer data.
+- [ ] Verify whether the user receives a conflict warning.
+
+Risk to document:
+
+- Stale-update protection is not currently documented as implemented. Treat multi-tab overwrite behavior as an observation unless the product requires a blocking fix.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## Archive and Deactivation Behavior Tests
+
+Level: Standard regression.
+
+Do not delete records during the normal test run.
+
+### Season
+
+- [ ] Mark `TEST - Platform QA 2026` inactive.
+- [ ] Verify it disappears from active import selectors.
+- [ ] Verify historical evaluations remain viewable to authorized users.
+- [ ] Verify timelines still load.
+- [ ] Verify player comparison still works.
+- [ ] Verify review filters can still access historical data if the inactive season remains selectable.
+- [ ] Verify whether new evaluations can still be started for a cycle tied to the inactive season.
+
+### Team
+
+- [ ] Deactivate `TEST - Alpha`.
+- [ ] Verify roster and coach assignment history remains intact.
+- [ ] Verify historical evaluation snapshots still display.
+- [ ] Verify inactive teams do not appear in active assignment workflows.
+
+### Player Account
+
+- [ ] Deactivate Player QA One's user account.
+- [ ] Verify login is blocked.
+- [ ] Verify the player record and history still exist.
+- [ ] Verify coach and peer evaluations of the player remain visible to authorized reviewers.
+- [ ] Verify whether the player appears in new-evaluation selectors.
+
+### Coach Account
+
+- [ ] Deactivate Coach QA One.
+- [ ] Verify login is blocked.
+- [ ] Verify historical coach evaluations remain attributed correctly.
+- [ ] Verify whether the coach appears as an active evaluator or assignment option.
+
+### Membership and Assignment
+
+- [ ] End a player roster membership.
+- [ ] End a coach assignment.
+- [ ] Verify historical snapshots remain correct.
+- [ ] Verify active permissions update appropriately.
+
+Policy decision required:
+
+- Current selectors primarily filter active players, active seasons, active memberships, active teams, and coach-role accounts. Confirm the desired policy for inactive-season historical review filters and inactive player visibility in staff reports.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## Expanded Analytics Command Center and Reporting Verification
+
+Level: Release-blocking for basic dashboard integrity; standard regression for detailed counts.
+
+Current implemented outputs include:
+
+- summary cards
+- active player count
+- submitted assessment count
+- completion rate
+- imports needing review
+- drafted/matched summary
+- recent observations
+- coach completion details
+- observation status counts
+- evaluator-role breakdown
+- average score by category
+- average score by role
+- coach-to-coach spread rows
+- import status and row summaries
+- draft matching summary
+- players without draft context
+- player profile timeline
+- player comparison
+- evaluation review filters
+
+Test process:
+
+1. Record values before creating QA evaluations.
+2. Submit a known number of coach, self, and peer evaluations.
+3. Refresh `/analytics/`.
+4. Confirm submitted counts change by the expected amount.
+5. Filter by cycle, division, and team where supported.
+6. Confirm QA records do not unexpectedly pollute real-season reporting, or document the filter required to isolate them.
+7. Reopen and resubmit one evaluation.
+8. Confirm counts do not double-count the reopened/resubmitted record.
+9. Deactivate or archive the QA season.
+10. Confirm reports treat archived QA data according to current behavior.
+
+For each metric, verify:
+
+- [ ] value before QA activity
+- [ ] expected delta
+- [ ] value after QA activity
+- [ ] cycle filter behavior
+- [ ] team/division filter behavior
+- [ ] behavior after reopen/resubmit
+- [ ] behavior after QA season deactivation
+
+Pay special attention to:
+
+- [ ] coach evaluations
+- [ ] self-evaluations
+- [ ] peer evaluations
+- [ ] evaluator-role labels
+- [ ] evaluation-type labels
+- [ ] score averages
+- [ ] variance rows
+- [ ] timeline labels
+- [ ] comparison summaries
+
+Policy decision required:
+
+- Command Center labels still use "coach assessment" language in some places because the underlying observation type is `coach_assessment`. Confirm whether broader user-facing labels should change in a future UI polish pass.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
diff --git a/docs/qa/platform_e2e/production_smoke_test.md b/docs/qa/platform_e2e/production_smoke_test.md
new file mode 100644
index 0000000..d68de95
--- /dev/null
+++ b/docs/qa/platform_e2e/production_smoke_test.md
@@ -0,0 +1,79 @@
+# Production Smoke Test
+
+Use this checklist after deployment. It is intentionally shorter than the full E2E script and should fit into one short testing session.
+
+Do not use optional negative fixtures during the smoke test.
+
+## Run Information
+
+```text
+Tester:
+Date:
+Environment:
+Commit:
+Overall result:
+Critical defects:
+Non-critical defects:
+```
+
+## Setup
+
+- [ ] Confirm the deployed commit.
+- [ ] Confirm a recent database backup exists.
+- [ ] Confirm QA season `TEST - Platform QA 2026` is active for testing.
+- [ ] Confirm `TEST - Alpha` and `TEST - Beta` exist.
+- [ ] Replace CSV placeholder emails with controlled test aliases.
+- [ ] Activate only the QA accounts required for this smoke test.
+
+## Admin Workflow
+
+- [ ] Sign in as an administrator or Django staff user.
+- [ ] Open Operations Home `/analytics/`.
+- [ ] Confirm Imports, User Accounts, Seasons, Evaluations, and Review links work.
+- [ ] Import or re-import `test_players_import.csv`.
+- [ ] Verify no duplicate players, player accounts, self links, or active roster memberships are created.
+- [ ] Import or re-import `test_coaches_import.csv`.
+- [ ] Verify no duplicate coach accounts or active coach assignments are created.
+- [ ] Create or verify one manual account from `manual_test_records.md`.
+
+## Coach Workflow
+
+- [ ] Sign in as imported coach `coach.qa.one`.
+- [ ] Create, save, reopen, and submit one coach evaluation.
+- [ ] Sign in as manual coach `coach.qa.manual`.
+- [ ] Submit one evaluation of an imported player.
+
+## Player Workflow
+
+- [ ] Sign in as imported player `player.qa.one`.
+- [ ] Submit one self-evaluation.
+- [ ] Submit one peer evaluation of a manual player.
+- [ ] Sign in as manual player `player.qa.manual.one`.
+- [ ] Submit one self-evaluation or one peer evaluation of an imported player.
+
+## Review Workflow
+
+- [ ] Sign back in as administrator or Django staff.
+- [ ] Confirm all smoke-test evaluations appear in `/analytics/evaluation-review/`.
+- [ ] Reopen one evaluation from `/analytics/observations/review/`.
+- [ ] Resubmit it as the original evaluator.
+- [ ] Confirm no duplicate evaluation is created.
+- [ ] Confirm the player timeline includes the submitted evaluations.
+- [ ] Confirm player comparison includes submitted evaluation scores.
+- [ ] Confirm key Command Center metrics changed by the expected amount.
+
+## Security Workflow
+
+- [ ] Coach receives 403 from `/analytics/imports/`.
+- [ ] Coach receives 403 from `/accounts/`.
+- [ ] Player receives 403 from `/analytics/evaluation-review/`.
+- [ ] Player receives 403 from `/accounts/`.
+- [ ] Anonymous user is redirected to login from `/analytics/`.
+
+## Cleanup
+
+- [ ] Deactivate QA accounts not needed for continued testing.
+- [ ] Archive or deactivate the QA season when appropriate.
+- [ ] Remove temporary passwords from notes.
+- [ ] Preserve screenshots and notes for any defects.
+- [ ] Record final Pass or Fail above.
diff --git a/docs/qa/platform_e2e/test_coach_account_collision_cases.csv b/docs/qa/platform_e2e/test_coach_account_collision_cases.csv
new file mode 100644
index 0000000..542aa84
--- /dev/null
+++ b/docs/qa/platform_e2e/test_coach_account_collision_cases.csv
@@ -0,0 +1,7 @@
+first_name,last_name,email,username,team,division,is_active,notes,source_id,season,assignment_role,assignment_start_date,assignment_end_date,assignment_source_id
+Coach,QA One,REPLACE_WITH_YOUR_EMAIL+qa-coach1@example.com,,TEST - Alpha,13U House,true,Expected reuse of existing imported coach email,qa-coach-collision-reuse,TEST - Platform QA 2026,assistant_coach,2026-07-01,,qa-assignment-collision-reuse
+Coach,QA PlayerEmail,REPLACE_WITH_YOUR_EMAIL+qa-player1@example.com,,TEST - Alpha,13U House,true,Expected conflict because email belongs to a player account,qa-coach-collision-player-email,TEST - Platform QA 2026,assistant_coach,2026-07-01,,qa-assignment-collision-player-email
+Collision,Coach,REPLACE_WITH_YOUR_EMAIL+qa-coach-collision1@example.com,,TEST - Alpha,13U House,true,Generated username collision row one,qa-coach-collision-generated-001,TEST - Platform QA 2026,assistant_coach,2026-07-01,,qa-assignment-collision-generated-001
+Collision,Coach,REPLACE_WITH_YOUR_EMAIL+qa-coach-collision2@example.com,,TEST - Beta,13U House,true,Generated username collision row two should conflict in preview,qa-coach-collision-generated-002,TEST - Platform QA 2026,assistant_coach,2026-07-01,,qa-assignment-collision-generated-002
+Explicit,Username,REPLACE_WITH_YOUR_EMAIL+qa-coach-explicit-conflict@example.com,coach.qa.one,TEST - Alpha,13U House,true,Expected conflict because explicit username already exists,qa-coach-collision-explicit-001,TEST - Platform QA 2026,assistant_coach,2026-07-01,,qa-assignment-collision-explicit-001
+Whitespace,Email, REPLACE_WITH_YOUR_EMAIL+qa-coach-whitespace@example.com ,,TEST - Beta,13U House,true,Expected email trim and normalize,qa-coach-collision-whitespace-001,TEST - Platform QA 2026,assistant_coach,2026-07-01,,qa-assignment-collision-whitespace-001
diff --git a/docs/qa/platform_e2e/test_coaches_inactive_import.csv b/docs/qa/platform_e2e/test_coaches_inactive_import.csv
new file mode 100644
index 0000000..8c0fd8b
--- /dev/null
+++ b/docs/qa/platform_e2e/test_coaches_inactive_import.csv
@@ -0,0 +1,2 @@
+first_name,last_name,email,username,team,division,is_active,notes,source_id,season,assignment_role,assignment_start_date,assignment_end_date,assignment_source_id
+Coach,QA Inactive,REPLACE_WITH_YOUR_EMAIL+qa-coach-inactive@example.com,coach.qa.inactive,TEST - Alpha,13U House,false,QA inactive coach lifecycle test,qa-coach-inactive-001,TEST - Platform QA 2026,evaluator,2026-07-01,,qa-assignment-coach-inactive-001

```
