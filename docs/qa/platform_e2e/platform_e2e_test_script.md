# VCB Platform End-To-End QA Test Script

Use this script to test account provisioning, player imports, coach imports, season assignments, and evaluation workflows in an isolated QA season.

Do not use real personal data. Replace all placeholder email addresses before importing.

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

## I. Review Workflow

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
