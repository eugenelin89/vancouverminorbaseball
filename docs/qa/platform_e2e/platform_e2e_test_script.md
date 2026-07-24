# VCB Platform End-To-End QA Test Script

Use this script to test account provisioning, player imports, coach imports, season assignments, and evaluation workflows in an isolated QA season.

Do not use real personal data. Replace all placeholder email addresses before importing.

## Test Classification

Run tests in this order:

```text
Production smoke test
-> release-blocking E2E tests
-> standard regression
-> extended edge cases
```

### Release-Blocking

These tests must pass before a production release is accepted:

- [ ] player import (`IMP-001`, `IMP-003`)
- [ ] player account provisioning (`ACC-001`)
- [ ] coach import (`IMP-002`, `IMP-003`)
- [ ] manual account creation (`ACC-007`)
- [ ] coach evaluation submission (`EVL-001`)
- [ ] player self-evaluation submission (`EVL-002`)
- [ ] player peer-evaluation submission (`EVL-003`)
- [ ] optional evaluation question handling (`EVL-008`)
- [ ] evaluation review (`REV-001`, `REV-003`)
- [ ] direct URL permissions (`SEC-001` to `SEC-004`)
- [ ] forced password change (`ACC-006`)
- [ ] no duplicate submissions after refresh or repeat submit (`EVL-005`)
- [ ] basic Analytics Command Center integrity (`ANA-001`)

### Standard Regression

These tests should run for a planned release or when related code changes:

- [ ] imported/manual cross-workflow consistency
- [ ] evaluation-cycle isolation
- [ ] inactive-account lifecycle
- [ ] archive and deactivation behavior
- [ ] reporting filters
- [ ] player timeline
- [ ] player comparison
- [ ] mobile layout

### Extended Edge Cases

These tests are useful before major pilots, after import/account changes, or when investigating defects:

- [ ] username collision handling
- [ ] email reuse and cross-role conflict handling
- [ ] browser back/forward behavior
- [ ] multi-tab stale edits
- [ ] case and whitespace normalization
- [ ] conflicting cross-role emails

## Risk Priority

Critical and High tests should be prioritized when release time is limited. Medium and Low tests should not be permanently skipped; they may be deferred based on release scope. Release-blocking classification and risk classification are related but not identical.

| Area | Requirement IDs | Risk |
| --- | --- | --- |
| Import data creation and idempotency | `IMP-001` to `IMP-003` | Critical |
| Import preview and conflict reporting | `IMP-004` | High |
| Account provisioning, activation, and passwords | `ACC-001`, `ACC-002`, `ACC-005`, `ACC-006` | Critical |
| Username and email handling | `ACC-003`, `ACC-004` | High |
| Manual account creation | `ACC-007` | High |
| Active assignments and memberships | `ASN-001`, `ASN-002` | Critical |
| Historical assignment preservation | `ASN-003` | High |
| Core evaluation workflows | `EVL-001` to `EVL-006` | Critical |
| Imported/manual workflow consistency | `EVL-007` | High |
| Optional evaluation questions | `EVL-008` | High |
| Review and attribution | `REV-001` to `REV-003` | High |
| Permissions | `SEC-001` to `SEC-004` | Critical |
| Command Center and reporting | `ANA-001` to `ANA-005` | High |
| Navigation and mobile | `NAV-001`, `NAV-002` | Medium |
| Browser refresh and back-button behavior | `NAV-003` | Medium |
| Multi-tab stale edits | `NAV-004` | Medium |
| QA retention and cleanup | `OPS-002`, `OPS-003` | Medium |

## QA Fixture Summary

QA season:

```text
TEST - Platform QA 2026
```

QA teams:

- `TEST - Alpha`
- `TEST - Beta`

Imported players:

- Player QA One, `TEST - Alpha`
- Player QA Two, `TEST - Alpha`
- Player QA Three, `TEST - Beta`
- Player QA Four, `TEST - Beta`

Imported coaches:

- Coach QA One, `TEST - Alpha`
- Coach QA Two, `TEST - Beta`

Manual records:

- Coach QA Manual, `TEST - Alpha`
- Player QA Manual One, `TEST - Alpha`
- Player QA Manual Two, `TEST - Beta`

## Current Supported Import Behavior

Player import:

- Route: `/analytics/imports/new/`
- Required mapping: either `full_name` or both `first_name` and `last_name`.
- Season is selected on the upload form.
- Team and division are required before commit because roster membership must be created.
- Birthdate formats accepted: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`.
- Roster status values accepted: blank, `active`, `inactive`, `transferred`, `transfer`, `guest`, `removed`, `remove`.
- Player account provisioning is optional on upload.
- If player account provisioning is enabled, map `account_email` to the CSV email column in the preview form.
- Player account temporary password is the player's birthdate as `YYYYMMDD`; it is not shown in the import result.
- Imported player accounts are active when provisioning is enabled.
- Imported player accounts must change password on first login.
- Re-importing the same source identifiers should update/reuse records instead of creating duplicates.

Coach import:

- Route: `/accounts/imports/coaches/new/`
- Required CSV columns: `first_name`, `last_name`, `email`.
- Current implementation also requires `team` and `division` for each valid row because coach assignments are created during import.
- Optional CSV columns: `username`, `team`, `division`, `is_active`, `notes`, `source_id`, `season`, `assignment_role`, `assignment_start_date`, `assignment_end_date`, `assignment_source_id`.
- Assignment role values accepted: blank, `assistant`, `assistant coach`, `assistant_coach`, `head`, `head coach`, `head_coach`, `manager`, `coordinator`, `evaluator`.
- Date formats accepted: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`.
- Boolean values accepted for `is_active`: blank, `1`, `true`, `yes`, `y`, `active`, `0`, `false`, `no`, `n`, `inactive`.
- Imported coach accounts are active by default unless `is_active` is false.
- Imported coach accounts must change password on first login.
- New coach temporary passwords are random and shown once on the result page.
- Existing coach accounts are reused by email and keep their existing password.
- Existing non-coach accounts with the same email are conflicts.
- Coach import creates or reuses season teams and creates or updates coach season assignments.
- Coach import does not create `players.Player` records and does not create `UserPlayerLink` rows.

## A. Initial Setup

Requirements covered: `OPS-001`, `OPS-002`, `NAV-001`

Automation readiness: Manual

Tester:

```text
Name:
Date:
Environment:
Production commit:
```

Checklist:

- [ ] Confirm the exact production commit being tested.
- [ ] Confirm a recent database backup exists.
- [ ] Sign in as a Django staff or superuser account at `/accounts/login/`.
- [ ] Open `/seasons/`.
- [ ] Create or verify season `TEST - Platform QA 2026`.
- [ ] Recommended season key: `test-platform-qa-2026`.
- [ ] Recommended start date: `2026-07-01`.
- [ ] Recommended end date: leave blank or use the planned QA end date.
- [ ] Confirm the QA season is active.
- [ ] Confirm the QA season is current only if this QA run intentionally tests current-season defaults.
- [ ] Create or verify season team `TEST - Alpha` in division `13U House`.
- [ ] Create or verify season team `TEST - Beta` in division `13U House`.
- [ ] Confirm no real users are assigned to the QA season.
- [ ] Replace placeholder emails in `test_players_import.csv`.
- [ ] Replace placeholder emails in `test_coaches_import.csv`.
- [ ] Save a working copy of each CSV outside the repository if using real controlled email aliases.

Pass / Fail:

```text
Result:
Notes:
```

## B. Player Import

Requirements covered: `IMP-001`, `IMP-003`, `IMP-004`, `ACC-001`, `ACC-003`, `ACC-004`, `ACC-005`, `ACC-006`, `ASN-001`

Automation readiness: Semi-automatable

Path:

```text
/analytics/imports/new/
```

Steps:

- [ ] Open Analytics Command Center `/analytics/`.
- [ ] Click Imports and confirm it opens `/analytics/imports/`.
- [ ] Click New Import.
- [ ] Select season `TEST - Platform QA 2026`.
- [ ] Upload `test_players_import.csv`.
- [ ] Select source `Manual staff CSV` unless another source is intentionally tested.
- [ ] Check `Provision player accounts`.
- [ ] Click Preview Import.
- [ ] On preview, confirm mapped columns include first name, last name, birthdate, division, team name, roster status, roster source ID, source identifiers, and `account_email`.
- [ ] If `account_email` is not automatically mapped, map it manually to the `account_email` CSV column.
- [ ] Confirm each row previews as create or update, not error.
- [ ] Confirm teams are shown as create or reuse.
- [ ] Confirm memberships are shown as create or update.
- [ ] Resolve any review rows, or explicitly skip only rows that are intentionally invalid.
- [ ] Confirm Import.

Expected result:

- [ ] Four player rows are processed.
- [ ] Four canonical players exist or are reused safely.
- [ ] Four active player roster memberships exist in `TEST - Platform QA 2026`.
- [ ] Player QA One and Player QA Two are on `TEST - Alpha`.
- [ ] Player QA Three and Player QA Four are on `TEST - Beta`.
- [ ] Four player user accounts are created or linked when account provisioning is enabled.
- [ ] Player account usernames follow generated or existing username rules.
- [ ] Player accounts are active.
- [ ] Player accounts have role Player.
- [ ] Player accounts must change password.
- [ ] Each player user has one active primary self link.
- [ ] Import result account provisioning summary matches the rows processed.

Idempotency test:

- [ ] Repeat the same player import.
- [ ] Confirm no duplicate players are created.
- [ ] Confirm no duplicate user accounts are created.
- [ ] Confirm no duplicate active self links are created.
- [ ] Confirm no duplicate active primary roster memberships are created.
- [ ] Record whether rows were updated, already linked, or skipped as expected.

Pass / Fail:

```text
Result:
Notes:
```

## C. Coach Import

Requirements covered: `IMP-002`, `IMP-003`, `IMP-004`, `ACC-002`, `ACC-003`, `ACC-004`, `ACC-005`, `ACC-006`, `ASN-002`

Automation readiness: Semi-automatable

Path:

```text
/accounts/imports/coaches/new/
```

Steps:

- [ ] Open Account Operations `/accounts/`.
- [ ] Open Coach Imports `/accounts/imports/coaches/`.
- [ ] Click New Coach Import.
- [ ] Select season `TEST - Platform QA 2026`.
- [ ] Upload `test_coaches_import.csv`.
- [ ] Click Preview Import.
- [ ] Confirm both rows are ready or reuse.
- [ ] Confirm team and division are recognized.
- [ ] Confirm assignment roles are Head Coach and Assistant Coach.
- [ ] Confirm account action is Create Coach Account or Reuse Coach Account.
- [ ] Confirm password behavior says temporary password will be generated only for new accounts.
- [ ] Confirm Import.
- [ ] Copy temporary passwords from the result page immediately if new coach accounts were created.

Expected result:

- [ ] Two coach rows are processed.
- [ ] Coach QA One and Coach QA Two users exist.
- [ ] Account role is Coach for both.
- [ ] Both users are active unless the CSV says otherwise.
- [ ] Both users are not Django staff.
- [ ] Both users are not superusers.
- [ ] Both users must change password if newly created.
- [ ] Coach QA One has an assignment to `TEST - Alpha`.
- [ ] Coach QA Two has an assignment to `TEST - Beta`.
- [ ] No `players.Player` records were created for coaches.
- [ ] No `UserPlayerLink` rows were created for coaches.

Idempotency test:

- [ ] Repeat the same coach import if safe for the environment.
- [ ] Confirm existing coach accounts are reused by email.
- [ ] Confirm reused coach accounts keep existing passwords unchanged.
- [ ] Confirm no duplicate active coach assignments are created.

Pass / Fail:

```text
Result:
Notes:
```

## D. Manual Creation

Requirements covered: `ACC-007`, `ACC-005`, `ACC-006`, `ASN-001`, `ASN-002`

Automation readiness: Semi-automatable

Use `manual_test_records.md`.

Steps:

- [ ] Manually create Coach QA Manual.
- [ ] Manually create Player QA Manual One.
- [ ] Manually create Player QA Manual Two.
- [ ] Create or verify Coach QA Manual assignment to `TEST - Alpha`.
- [ ] Create or verify Player QA Manual One membership on `TEST - Alpha`.
- [ ] Create or verify Player QA Manual Two membership on `TEST - Beta`.

Expected result:

- [ ] Manual coach has role Coach, active account, no Django staff, no superuser.
- [ ] Manual players have role Player, active accounts, no Django staff, no superuser.
- [ ] Manual players each have exactly one active primary self link.
- [ ] Manual records have the same practical permissions as imported records.

Pass / Fail:

```text
Result:
Notes:
```

## E. Administrator Navigation And Permissions

Requirements covered: `NAV-001`, `SEC-001`, `SEC-002`

Automation readiness: Semi-automatable

As a staff or superuser account, verify visible navigation:

- [ ] Operations Home opens `/analytics/`.
- [ ] User Accounts opens `/accounts/`.
- [ ] Seasons opens `/seasons/`.
- [ ] Imports opens `/analytics/imports/`.
- [ ] Evaluations opens `/analytics/evaluations/`.
- [ ] Review Evaluations opens `/analytics/evaluation-review/`.
- [ ] Profile opens `/accounts/profile/`.
- [ ] Password opens `/accounts/password/`.
- [ ] Log out works.

Verify:

- [ ] No visible link points to `/pdp/`.
- [ ] No visible page displays `PDP`.
- [ ] No important link returns 404.
- [ ] No unexpected 403 appears for staff-only workflows.

Pass / Fail:

```text
Result:
Notes:
```

## F. Coach Evaluation Workflow

Requirements covered: `EVL-001`, `EVL-004`, `REV-003`, `SEC-003`

Automation readiness: Semi-automatable

Test all three coaches.

Minimum submissions:

- Coach QA One evaluates Player QA One.
- Coach QA Two evaluates Player QA Three.
- Coach QA Manual evaluates Player QA Manual One.

For each coach:

- [ ] Sign in at `/accounts/login/`.
- [ ] Change temporary password if prompted.
- [ ] Open `/analytics/evaluations/`.
- [ ] Search or filter for the target player.
- [ ] Start an evaluation.
- [ ] Answer several questions.
- [ ] Save as draft.
- [ ] Leave the page.
- [ ] Reopen the draft.
- [ ] Verify answers persisted.
- [ ] Modify one answer.
- [ ] Submit.
- [ ] Verify submitted status.
- [ ] Verify evaluator identity is the coach user.
- [ ] Verify evaluator role snapshot is Coach.
- [ ] Verify evaluation type is Coach Evaluation.
- [ ] Verify season is `TEST - Platform QA 2026`.
- [ ] Verify player team/division snapshot is correct.
- [ ] Verify coach assignment snapshot is correct when available.

Access behavior:

- [ ] Coach can see same-team players.
- [ ] Coach can see other QA-team players if current broad evaluator policy allows it.
- [ ] Coach can see real players if they are active in the selected evaluation cycle; record whether this is acceptable for the pilot.

Pass / Fail:

```text
Result:
Notes:
```

## G. Player Self-Evaluations

Requirements covered: `EVL-002`, `EVL-004`, `SEC-003`

Automation readiness: Semi-automatable

Minimum submissions:

- Player QA One self-evaluates.
- Player QA Manual One self-evaluates.

For each player:

- [ ] Sign in at `/accounts/login/`.
- [ ] Change temporary password if prompted.
- [ ] Open `/analytics/evaluations/`.
- [ ] Select the player's own record.
- [ ] Confirm the form displays Self Evaluation.
- [ ] Save as draft.
- [ ] Leave the page.
- [ ] Reopen the draft.
- [ ] Verify answers persisted.
- [ ] Modify one answer.
- [ ] Submit.
- [ ] Verify the evaluation appears in `/analytics/my/evaluations/`.
- [ ] Confirm another player cannot edit it.

Current behavior to verify:

- [ ] The subject is the selected active player.
- [ ] Self Evaluation is server-derived when the logged-in user has an active self link to the target player.
- [ ] Player self-evaluation is allowed.

Pass / Fail:

```text
Result:
Notes:
```

## H. Player Peer Evaluations

Requirements covered: `EVL-003`, `EVL-004`, `SEC-003`, `REV-003`

Automation readiness: Semi-automatable

Minimum submissions:

- Player QA One evaluates Player QA Two.
- Player QA Two evaluates Player QA One.
- Player QA Manual One evaluates Player QA Manual Two.
- One cross-team peer evaluation, such as Player QA One evaluating Player QA Three.

For each:

- [ ] Sign in as the evaluating player.
- [ ] Open `/analytics/evaluations/`.
- [ ] Search or filter for the target player.
- [ ] Start an evaluation.
- [ ] Confirm the form displays Peer Evaluation.
- [ ] Save as draft.
- [ ] Reopen the draft.
- [ ] Submit.
- [ ] Verify the correct subject player is recorded.
- [ ] Verify evaluator role snapshot is Player.
- [ ] Verify evaluation type is Peer Evaluation.
- [ ] Confirm self-selection is labeled Self Evaluation, not Peer Evaluation.
- [ ] Confirm players cannot edit peer evaluations submitted by someone else.
- [ ] Confirm evaluator names are hidden in player-facing My Evaluations.
- [ ] Confirm coaches/staff can see evaluator names in review pages.

Pass / Fail:

```text
Result:
Notes:
```

## I. Optional Evaluation Question Tests

Requirements covered: `EVL-008`, `EVL-001`, `EVL-002`, `EVL-003`, `REV-001`, `ANA-002`

Automation readiness: Fully automatable

Setup:

- [ ] In Django admin, open the active coach assessment question set.
- [ ] Mark one rating question optional.
- [ ] Leave at least one other rating question required.
- [ ] Confirm the freeform notes question may also be optional if configured that way.

Required-question behavior:

- [ ] As a coach, open a new evaluation form.
- [ ] Leave a required rating blank.
- [ ] Fill any optional questions or leave them blank.
- [ ] Click Submit.
- [ ] Confirm the page blocks submission and shows a required-field error.
- [ ] Confirm the evaluation remains draft.
- [ ] Confirm entered answers remain visible after the validation error.

Optional-question behavior:

- [ ] As a coach, fill all required questions and leave the optional rating blank.
- [ ] Click Submit.
- [ ] Confirm submission succeeds.
- [ ] Open the evaluation detail page.
- [ ] Confirm the optional question is shown as `Optional`.
- [ ] Confirm the optional unanswered question displays `Not answered`.
- [ ] Confirm it is not displayed or counted as a `0`.

Draft behavior:

- [ ] Start another evaluation.
- [ ] Answer only the optional question.
- [ ] Save as draft.
- [ ] Reopen the draft and clear the optional answer.
- [ ] Save again.
- [ ] Confirm the optional blank value is not retained as a zero or stale answer.
- [ ] Complete only required questions and submit successfully.

Player-submission behavior:

- [ ] Repeat the optional blank submit path as a player self-evaluation.
- [ ] Repeat the optional blank submit path as a player peer evaluation.
- [ ] Confirm both submit successfully when required questions are complete.

Review and analytics behavior:

- [ ] Open player-facing `/analytics/my/evaluations/` detail for the submitted result.
- [ ] Confirm evaluator names remain hidden.
- [ ] Confirm the unanswered optional question is visible as `Not answered`.
- [ ] Open coach/staff review detail.
- [ ] Confirm the unanswered optional question is visible as `Not answered`.
- [ ] Open Analytics Command Center and comparison views.
- [ ] Confirm averages exclude blank optional answers.
- [ ] Confirm completion metrics treat the submitted evaluation as complete because required questions were answered.

Cleanup:

- [ ] Restore the optional question setting to the desired production configuration.

Pass / Fail:

```text
Result:
Notes:
```

## J. Review Workflow

Requirements covered: `REV-001`, `REV-002`, `REV-003`, `ANA-005`, `EVL-005`

Automation readiness: Semi-automatable

As an administrator, staff user, or coach reviewer:

- [ ] Open `/analytics/evaluation-review/`.
- [ ] Confirm all submitted QA evaluations appear.
- [ ] Filter by player.
- [ ] Filter by evaluator.
- [ ] Filter by evaluator role.
- [ ] Filter by evaluation type.
- [ ] Filter by team.
- [ ] Filter by division.
- [ ] Filter by season.
- [ ] Filter by evaluation cycle.
- [ ] Filter by submitted date range.

For each sampled evaluation, verify:

- [ ] evaluator name
- [ ] evaluator account
- [ ] evaluator role
- [ ] evaluation type
- [ ] subject player
- [ ] team
- [ ] season
- [ ] evaluation cycle
- [ ] submission timestamp
- [ ] status
- [ ] answers and scores

Reopen test:

- [ ] Reopen one coach evaluation from staff observation review at `/analytics/observations/review/`.
- [ ] Reopen one self-evaluation from staff observation review.
- [ ] Reopen one peer evaluation from staff observation review.
- [ ] Log in as the original evaluator.
- [ ] Verify prior answers remain.
- [ ] Verify the evaluation is editable.
- [ ] Resubmit.
- [ ] Confirm no duplicate observation was created.

Pass / Fail:

```text
Result:
Notes:
```

## J. Permission Testing

Requirements covered: `SEC-001`, `SEC-002`, `SEC-003`, `SEC-004`

Automation readiness: Fully automatable

Direct URL access must be tested. Navigation hiding is not enough.

As a coach, directly attempt:

- [ ] `/analytics/imports/` - expected 403.
- [ ] `/accounts/` - expected 403.
- [ ] `/seasons/` - expected 403.
- [ ] `/admin/` - expected denied unless Django staff access was intentionally granted.

As a player, directly attempt:

- [ ] `/analytics/imports/` - expected 403.
- [ ] `/analytics/evaluation-review/` - expected 403.
- [ ] `/accounts/` - expected 403.
- [ ] `/seasons/` - expected 403.
- [ ] Another player's private `/analytics/my/evaluations/<id>/` URL - expected 403 or not found.

As an anonymous visitor, directly attempt:

- [ ] `/analytics/` - expected redirect to login.
- [ ] `/analytics/imports/` - expected redirect to login.
- [ ] `/analytics/evaluations/` - expected redirect to login.
- [ ] `/accounts/profile/` - expected redirect to login.

Pass / Fail:

```text
Result:
Notes:
```

## K. Account Activation And Password Workflow

Requirements covered: `ACC-005`, `ACC-006`, `SEC-004`

Automation readiness: Semi-automatable

Test:

- one imported coach
- one imported player
- one manually created player

For each:

- [ ] Confirm expected initial active/inactive status.
- [ ] If inactive, activate through Account Operations.
- [ ] Sign in with temporary password.
- [ ] Confirm forced password change happens before normal platform pages.
- [ ] Change password.
- [ ] Confirm redirect to the correct landing page.
- [ ] Log out.
- [ ] Confirm login succeeds with the new password.
- [ ] Confirm the old temporary password no longer works.
- [ ] Confirm password pages use Accounts routes and current platform branding.

Password expectations:

- Imported player temporary password: birthdate as `YYYYMMDD`.
- Imported coach temporary password: random one-time value shown only on import result page.
- Manually created account temporary password: one-time value shown only on creation result page.

Pass / Fail:

```text
Result:
Notes:
```

## L. Analytics And Timeline

Requirements covered: `ANA-001`, `ANA-002`, `ANA-003`, `ANA-004`, `ANA-005`

Automation readiness: Semi-automatable

As staff:

- [ ] Open `/analytics/players/`.
- [ ] Search for each QA player.
- [ ] Open each player profile.
- [ ] Confirm submitted evaluations appear.
- [ ] Confirm timeline includes submitted evaluations.
- [ ] Open `/analytics/players/compare/`.
- [ ] Compare QA players.
- [ ] Confirm coach, self, and peer evaluations are labelled distinctly.
- [ ] Confirm command-center metrics update where applicable.
- [ ] Confirm QA season/team context displays correctly.

Pass / Fail:

```text
Result:
Notes:
```

## M. Mobile Testing

Requirements covered: `NAV-002`

Automation readiness: Manual

At approximately 390-pixel width, test:

- [ ] login
- [ ] navigation
- [ ] player import page
- [ ] coach import page
- [ ] evaluation list
- [ ] evaluation form
- [ ] draft and submit buttons
- [ ] evaluation review page
- [ ] account profile
- [ ] player profile
- [ ] player timeline

Pass / Fail:

```text
Result:
Notes:
```

## N. Cleanup

Requirements covered: `OPS-003`

Automation readiness: Manual

Use `cleanup_checklist.md`.

- [ ] Record defects and screenshots.
- [ ] Deactivate all QA accounts.
- [ ] Archive or deactivate the QA season.
- [ ] Ensure the QA season is not current/default.
- [ ] Hide QA teams from normal selectors where supported.
- [ ] Do not delete linked records until cascade behavior is understood.
- [ ] Retain the QA environment for repeat smoke tests if appropriate.

Pass / Fail:

```text
Result:
Notes:
```

## Cross-Workflow Consistency Tests

Level: Standard regression.

Requirements covered: `EVL-007`, `REV-003`

Automation readiness: Semi-automatable

Use these tests to verify that imported and manually created accounts behave the same in evaluation workflows.

| Combination | Example | Tested | Result |
| --- | --- | --- | --- |
| Imported coach evaluates imported player | Coach QA One evaluates Player QA One | [ ] |  |
| Imported coach evaluates manual player | Coach QA One evaluates Player QA Manual One | [ ] |  |
| Manual coach evaluates imported player | Coach QA Manual evaluates Player QA Two | [ ] |  |
| Manual coach evaluates manual player | Coach QA Manual evaluates Player QA Manual One | [ ] |  |
| Imported player evaluates imported player | Player QA One evaluates Player QA Two | [ ] |  |
| Imported player evaluates manual player | Player QA One evaluates Player QA Manual One | [ ] |  |
| Manual player evaluates imported player | Player QA Manual One evaluates Player QA Two | [ ] |  |
| Manual player evaluates manual player | Player QA Manual One evaluates Player QA Manual Two | [ ] |  |

For each combination:

- [ ] Start an evaluation.
- [ ] Save as draft.
- [ ] Leave the page.
- [ ] Reopen the draft.
- [ ] Submit.
- [ ] If reopened by staff, resubmit as the original evaluator.
- [ ] Confirm evaluator account is recognized correctly.
- [ ] Confirm evaluator role snapshot is correct.
- [ ] Confirm Self, Peer, or Coach classification is correct.
- [ ] Confirm subject player is correct.
- [ ] Confirm season snapshot is `TEST - Platform QA 2026`.
- [ ] Confirm team and division snapshots match the target player's QA roster membership.
- [ ] Confirm evaluation-cycle snapshot is correct.
- [ ] Confirm imported and manual accounts have equivalent practical permissions.
- [ ] Confirm no behavior difference is caused only by provisioning method.

Pass / Fail:

```text
Result:
Notes:
```

## Username Collision Tests

Level: Extended edge cases.

Requirements covered: `ACC-003`, `IMP-004`

Automation readiness: Fully automatable

Actual behavior discovered from code:

- Generated usernames use `firstname.lastname`.
- When a generated username already exists in the database, the username service adds suffixes such as `firstname.lastname2`.
- Explicit usernames are normalized to lowercase and trimmed.
- Explicit usernames with letters, numbers, dots, underscores, and hyphens are allowed.
- Explicit usernames that already exist are rejected.
- Coach import detects two ready rows that would use the same final username in the same CSV and marks the later row as a conflict.
- Manual account creation rejects duplicate usernames.
- Manual player-account creation rejects duplicate usernames and refuses to create a second self account for the same player.

Use optional fixture:

```text
test_coach_account_collision_cases.csv
```

Do not use this fixture in a normal smoke test.

Scenarios:

- [ ] Generated username already exists before import.
- [ ] Existing username belongs to the same intended account and email matches an existing coach.
- [ ] Existing username belongs to a different account.
- [ ] Two imported coach rows generate the same base username.
- [ ] Manually requested username conflicts with an existing account.

Verify:

- [ ] Generated username collision suffixes correctly when the existing username is already in the database.
- [ ] Existing coach email is reused safely and password remains unchanged.
- [ ] Explicit duplicate username is reported as a conflict.
- [ ] Two new rows that would generate the same final username do not both create accounts.
- [ ] Conflict rows do not create accounts, assignments, player records, or user-player links.
- [ ] Staff can understand the preview/result message.

Policy decision required:

- Decide whether duplicate generated names in the same coach CSV should suffix automatically instead of marking the later row as a conflict.

Pass / Fail:

```text
Result:
Notes:
```

## Email Reuse and Conflict Tests

Level: Extended edge cases.

Requirements covered: `ACC-004`, `IMP-004`

Automation readiness: Fully automatable

Actual behavior discovered from code:

- Emails are normalized by trimming whitespace and comparing case-insensitively.
- Coach import reuses an existing Coach account by email and keeps that account's password unchanged.
- Coach import does not activate an existing inactive Coach account and does not reset its password.
- Coach import conflicts when the email belongs to a non-Coach account.
- Player account provisioning reuses an existing self-linked user for the same player.
- Player account provisioning conflicts when the imported email belongs to an unrelated existing user.
- Player account provisioning does not change an existing coach role into a player role.

Coach email scenarios:

- [ ] Same coach, same email, repeated import.
- [ ] Different coach identity using an existing coach email.
- [ ] Coach import using an email belonging to a Player account.
- [ ] Coach import using an email belonging to Staff or another non-Coach role.
- [ ] Email differing only by letter case.
- [ ] Leading or trailing whitespace around an email.

Player account-provisioning scenarios:

- [ ] Repeated import with same player and same email.
- [ ] Same player with a changed email.
- [ ] Different player using an existing Player account email.
- [ ] Player import using an email already owned by a Coach account.
- [ ] Email differing only by case.
- [ ] Whitespace normalization.

For each scenario, verify:

- [ ] account reuse behavior
- [ ] conflict behavior
- [ ] preview status
- [ ] whether commit is blocked or row is skipped/conflicted
- [ ] whether a user-player link is created
- [ ] whether an existing role changes
- [ ] whether an unintended duplicate account appears
- [ ] whether the result clearly explains the outcome

Policy decision required:

- Decide whether an existing coach email reused with a different first/last name should require staff review before assignment changes are committed.

Pass / Fail:

```text
Result:
Notes:
```

## Inactive-Account Lifecycle Tests

Level: Standard regression.

Requirements covered: `ACC-005`, `ACC-006`, `ASN-003`

Automation readiness: Fully automatable

Use optional fixture:

```text
test_coaches_inactive_import.csv
```

Also test one deactivated player account and one manually created inactive account where practical.

Steps:

- [ ] Import the inactive coach fixture.
- [ ] Confirm the inactive coach user is created or retained.
- [ ] Confirm the inactive coach cannot sign in.
- [ ] Confirm knowing the correct temporary password does not grant access while inactive.
- [ ] Confirm staff can activate the account from Account Operations.
- [ ] Confirm the activated user can sign in.
- [ ] Confirm forced password change still applies.
- [ ] Confirm the user can log out and sign in with the new password.
- [ ] Confirm the original temporary password no longer works.
- [ ] Deactivate the account again.
- [ ] Confirm login is blocked again.
- [ ] Submit or locate a historical evaluation by the account before deactivation where practical.
- [ ] Confirm historical evaluations remain attributed to the deactivated account.

Actual behavior discovered from code:

- New inactive coach import rows create inactive Django users.
- Existing inactive coach accounts reused by coach import are not activated and do not get a new password.
- Operational password reset preserves inactive account state.
- Account deactivation preserves profile, user-player links, provenance, and historical attribution.

Pass / Fail:

```text
Result:
Notes:
```

## Evaluation Cycle Isolation Tests

Level: Standard regression.

Requirements covered: `EVL-006`, `ANA-005`

Automation readiness: Fully automatable

Use two QA evaluation cycles where supported:

- `TEST - Cycle A`
- `TEST - Cycle B`

Create or verify both cycles through the supported staff/admin workflow available in the environment. Do not invent a route if cycle management is admin-only in the deployed build.

Actual uniqueness rule discovered from code:

```text
One evaluator + one player + one observation type + one evaluation perspective + one evaluation cycle.
Self evaluations are stricter: one self evaluation per player per cycle.
```

Tests:

- [ ] Same coach evaluates the same player once in Cycle A.
- [ ] Same coach evaluates the same player once in Cycle B.
- [ ] Same player completes a self-evaluation once in Cycle A.
- [ ] Same player completes a self-evaluation once in Cycle B.
- [ ] Same player evaluates the same peer once in Cycle A.
- [ ] Same player evaluates the same peer once in Cycle B.
- [ ] Review filters separate Cycle A and Cycle B.
- [ ] Timeline entries show the correct cycle.
- [ ] Player comparison includes only submitted evaluations according to current comparison behavior.
- [ ] Command Center cycle filter changes completion/submitted counts for the selected cycle.
- [ ] Drafts from one cycle do not appear as drafts in another.
- [ ] Reopening an evaluation preserves its original cycle.
- [ ] Inactive cycles do not become the default active cycle.

Policy decision required:

- Confirm whether inactive or closed cycles should prevent new submissions through the UI or whether staff/admin lifecycle controls are sufficient.

Pass / Fail:

```text
Result:
Notes:
```

## Duplicate Evaluation and Repeat Submission Tests

Level: Release-blocking for basic duplicate protection; extended for multi-tab concurrency.

Requirements covered: `EVL-005`, `REV-002`, `NAV-003`, `NAV-004`

Automation readiness: Semi-automatable

Actual behavior discovered from code:

- Starting the same evaluator/player/perspective/cycle evaluation reuses the existing draft or redirects to the submitted detail.
- Service-level duplicate creation is blocked for the same evaluator, player, observation type, perspective, and cycle.
- Self-evaluation duplicate creation is blocked per player and cycle.
- Submission revalidates uniqueness before saving.
- Reopened evaluations reuse the same observation record.

Tests:

- [ ] Start the same evaluation twice in separate browser tabs.
- [ ] Double-click Submit.
- [ ] Refresh immediately after submission.
- [ ] Use browser Back after submission and submit again.
- [ ] Reopen a submitted evaluation and resubmit it.
- [ ] Attempt to create another evaluation for the same evaluator, player, type, perspective, and cycle.
- [ ] Submit an old draft after a newer draft or submission exists.
- [ ] Try two requests close together where practical.

Verify:

- [ ] duplicates are blocked or existing drafts are reused
- [ ] duplicate observations are not created
- [ ] the user receives a useful message or redirect
- [ ] answers are not overwritten unexpectedly during ordinary single-tab use
- [ ] review counts do not increase incorrectly

Risk to document:

- Multi-tab stale-update conflict warnings are not currently a documented feature. If one tab overwrites another tab's saved draft, record it as a known UX risk unless product policy requires optimistic locking.

Pass / Fail:

```text
Result:
Notes:
```

## Browser State and Navigation Tests

Level: Extended edge cases.

Requirements covered: `NAV-003`, `NAV-004`, `EVL-005`

Automation readiness: Semi-automatable

Run for coach, self, and peer evaluations.

### Refresh

- [ ] Begin an evaluation.
- [ ] Enter answers.
- [ ] Save as draft.
- [ ] Refresh the page.
- [ ] Confirm answers remain.
- [ ] Submit.
- [ ] Refresh the success/detail page.
- [ ] Confirm no duplicate submission is created.

### Back and Forward

- [ ] Begin an evaluation.
- [ ] Save a draft.
- [ ] Navigate back.
- [ ] Navigate forward.
- [ ] Confirm state remains valid.
- [ ] Submit once.
- [ ] Use Back.
- [ ] Attempt to submit again.
- [ ] Verify no duplicate is created.

### Multiple Tabs

- [ ] Open the same draft in two tabs.
- [ ] Modify both copies differently.
- [ ] Save one.
- [ ] Save or submit the other.
- [ ] Record whether stale data overwrites newer data.
- [ ] Verify whether the user receives a conflict warning.

Risk to document:

- Stale-update protection is not currently documented as implemented. Treat multi-tab overwrite behavior as an observation unless the product requires a blocking fix.

Pass / Fail:

```text
Result:
Notes:
```

## Archive and Deactivation Behavior Tests

Level: Standard regression.

Requirements covered: `ACC-005`, `ASN-003`, `OPS-002`, `OPS-003`

Automation readiness: Manual

Do not delete records during the normal test run.

### Season

- [ ] Mark `TEST - Platform QA 2026` inactive.
- [ ] Verify it disappears from active import selectors.
- [ ] Verify historical evaluations remain viewable to authorized users.
- [ ] Verify timelines still load.
- [ ] Verify player comparison still works.
- [ ] Verify review filters can still access historical data if the inactive season remains selectable.
- [ ] Verify whether new evaluations can still be started for a cycle tied to the inactive season.

### Team

- [ ] Deactivate `TEST - Alpha`.
- [ ] Verify roster and coach assignment history remains intact.
- [ ] Verify historical evaluation snapshots still display.
- [ ] Verify inactive teams do not appear in active assignment workflows.

### Player Account

- [ ] Deactivate Player QA One's user account.
- [ ] Verify login is blocked.
- [ ] Verify the player record and history still exist.
- [ ] Verify coach and peer evaluations of the player remain visible to authorized reviewers.
- [ ] Verify whether the player appears in new-evaluation selectors.

### Coach Account

- [ ] Deactivate Coach QA One.
- [ ] Verify login is blocked.
- [ ] Verify historical coach evaluations remain attributed correctly.
- [ ] Verify whether the coach appears as an active evaluator or assignment option.

### Membership and Assignment

- [ ] End a player roster membership.
- [ ] End a coach assignment.
- [ ] Verify historical snapshots remain correct.
- [ ] Verify active permissions update appropriately.

Policy decision required:

- Current selectors primarily filter active players, active seasons, active memberships, active teams, and coach-role accounts. Confirm the desired policy for inactive-season historical review filters and inactive player visibility in staff reports.

Pass / Fail:

```text
Result:
Notes:
```

## Expanded Analytics Command Center and Reporting Verification

Level: Release-blocking for basic dashboard integrity; standard regression for detailed counts.

Requirements covered: `ANA-001`, `ANA-002`, `ANA-003`, `ANA-004`, `ANA-005`, `EVL-005`

Automation readiness: Semi-automatable

Current implemented outputs include:

- summary cards
- active player count
- submitted assessment count
- completion rate
- imports needing review
- drafted/matched summary
- recent observations
- coach completion details
- observation status counts
- evaluator-role breakdown
- average score by category
- average score by role
- coach-to-coach spread rows
- import status and row summaries
- draft matching summary
- players without draft context
- player profile timeline
- player comparison
- evaluation review filters

Test process:

1. Record values before creating QA evaluations.
2. Submit a known number of coach, self, and peer evaluations.
3. Refresh `/analytics/`.
4. Confirm submitted counts change by the expected amount.
5. Filter by cycle, division, and team where supported.
6. Confirm QA records do not unexpectedly pollute real-season reporting, or document the filter required to isolate them.
7. Reopen and resubmit one evaluation.
8. Confirm counts do not double-count the reopened/resubmitted record.
9. Deactivate or archive the QA season.
10. Confirm reports treat archived QA data according to current behavior.

For each metric, verify:

- [ ] value before QA activity
- [ ] expected delta
- [ ] value after QA activity
- [ ] cycle filter behavior
- [ ] team/division filter behavior
- [ ] behavior after reopen/resubmit
- [ ] behavior after QA season deactivation

Pay special attention to:

- [ ] coach evaluations
- [ ] self-evaluations
- [ ] peer evaluations
- [ ] evaluator-role labels
- [ ] evaluation-type labels
- [ ] score averages
- [ ] variance rows
- [ ] timeline labels
- [ ] comparison summaries

Policy decision required:

- Command Center labels still use "coach assessment" language in some places because the underlying observation type is `coach_assessment`. Confirm whether broader user-facing labels should change in a future UI polish pass.

Pass / Fail:

```text
Result:
Notes:
```
