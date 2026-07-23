# Production Smoke Test

Use this checklist after deployment. It is intentionally shorter than the full E2E script and should fit into one short testing session.

Do not use optional negative fixtures during the smoke test.

## Smoke Test Mode

Requirements covered: `OPS-001`

Choose one mode before starting.

### Mode A: First Deployment

Expected behavior:

- imports create new player, coach, account, roster membership, and assignment records;
- evaluations create new observation records;
- temporary passwords are captured only where newly created accounts require them.

### Mode B: Repeat Deployment

Expected behavior:

- imports reuse existing players, coaches, accounts, roster memberships, and assignments;
- account provisioning reuses or reports already-linked player accounts;
- evaluations reuse existing drafts or submitted records;
- submitted evaluations are reopened, edited, and resubmitted where appropriate;
- no duplicate records are created.

## Run Information

```text
Tester:
Date:
Environment:
Commit:
Evaluation Cycle:
Smoke Test Mode:
Expected Result:
Overall result:
Critical defects:
Non-critical defects:
```

## Setup

Requirements covered: `OPS-001`, `OPS-002`

- [ ] Confirm the deployed commit.
- [ ] Confirm a recent database backup exists.
- [ ] Confirm QA season `TEST - Platform QA 2026` is active for testing.
- [ ] Confirm `TEST - Alpha` and `TEST - Beta` exist.
- [ ] Replace CSV placeholder emails with controlled test aliases.
- [ ] Activate only the QA accounts required for this smoke test.

## Admin Workflow

Requirements covered: `IMP-001`, `IMP-002`, `IMP-003`, `IMP-004`, `ACC-001`, `ACC-002`, `ACC-003`, `ACC-004`, `ACC-005`, `ACC-006`, `ACC-007`, `ASN-001`, `ASN-002`, `NAV-001`

- [ ] Sign in as an administrator or Django staff user.
- [ ] Open Operations Home `/analytics/`.
- [ ] Confirm Imports, User Accounts, Seasons, Evaluations, and Review links work.
- [ ] Import or re-import `test_players_import.csv`.
- [ ] Import or re-import `test_coaches_import.csv`.
- [ ] Create or verify one manual account from `manual_test_records.md`.

First deployment:

- [ ] Player import creates the expected QA players.
- [ ] Player import creates active roster memberships.
- [ ] Player account provisioning creates or links player accounts.
- [ ] Coach import creates the expected QA coaches.
- [ ] Coach import creates coach assignments.
- [ ] Manual account creation creates the selected manual QA account.

Repeat deployment:

- [ ] Player import reuses or updates existing QA players.
- [ ] Player import does not create duplicate player accounts, self links, or active roster memberships.
- [ ] Coach import reuses existing coach accounts.
- [ ] Coach import does not create duplicate active coach assignments.
- [ ] Manual account already exists or is verified without recreating it.

## Coach Workflow

Requirements covered: `EVL-001`, `EVL-004`, `EVL-005`, `EVL-007`, `REV-002`, `REV-003`

- [ ] Sign in as imported coach `coach.qa.one`.
- [ ] Sign in as manual coach `coach.qa.manual`.

First deployment:

- [ ] Imported coach creates, saves, reopens, and submits one coach evaluation.
- [ ] Manual coach submits one evaluation of an imported player.

Repeat deployment:

- [ ] If the imported coach evaluation is already submitted, reopen it from staff review.
- [ ] Edit one answer as the original imported coach.
- [ ] Resubmit the same imported-coach evaluation.
- [ ] If the manual coach evaluation is already submitted, reopen it from staff review.
- [ ] Edit one answer as the original manual coach.
- [ ] Resubmit the same manual-coach evaluation.
- [ ] Confirm both workflows reused existing observation records and created no duplicates.

## Player Workflow

Requirements covered: `EVL-002`, `EVL-003`, `EVL-004`, `EVL-005`, `EVL-007`, `SEC-003`, `REV-003`

- [ ] Sign in as imported player `player.qa.one`.
- [ ] Sign in as manual player `player.qa.manual.one`.

First deployment:

- [ ] Imported player submits one self-evaluation.
- [ ] Imported player submits one peer evaluation of a manual player.
- [ ] Manual player submits one self-evaluation or one peer evaluation of an imported player.

Repeat deployment:

- [ ] If the imported player's self-evaluation already exists, reopen it from staff review.
- [ ] Edit one answer as the imported player.
- [ ] Resubmit the same self-evaluation.
- [ ] If the imported player's peer evaluation already exists, reopen it from staff review.
- [ ] Edit one answer as the imported player.
- [ ] Resubmit the same peer evaluation.
- [ ] If the manual player's evaluation already exists, reopen it from staff review.
- [ ] Edit one answer as the manual player.
- [ ] Resubmit the same evaluation.
- [ ] Confirm no duplicate self or peer evaluation records were created.

## Review Workflow

Requirements covered: `REV-001`, `REV-002`, `REV-003`, `EVL-005`, `ANA-001`, `ANA-002`, `ANA-003`, `ANA-004`, `ANA-005`

- [ ] Sign back in as administrator or Django staff.
- [ ] Confirm all smoke-test evaluations appear in `/analytics/evaluation-review/`.
- [ ] Record the observation IDs for each smoke-test evaluation.
- [ ] Reopen one evaluation from `/analytics/observations/review/` if no repeat-mode reopen was already performed.
- [ ] Resubmit it as the original evaluator.
- [ ] Confirm the same observation ID was reused.
- [ ] Confirm no duplicate evaluation was created for the same evaluator, player, perspective, and cycle.
- [ ] Confirm the player timeline includes the submitted evaluations.
- [ ] Confirm player comparison includes submitted evaluation scores.
- [ ] Confirm key Command Center metrics changed by the expected amount.

## Security Workflow

Requirements covered: `SEC-001`, `SEC-002`, `SEC-003`, `SEC-004`

- [ ] Coach receives 403 from `/analytics/imports/`.
- [ ] Coach receives 403 from `/accounts/`.
- [ ] Player receives 403 from `/analytics/evaluation-review/`.
- [ ] Player receives 403 from `/accounts/`.
- [ ] Anonymous user is redirected to login from `/analytics/`.

## Cleanup

Requirements covered: `OPS-003`

- [ ] Deactivate QA accounts not needed for continued testing.
- [ ] Archive or deactivate the QA season when appropriate.
- [ ] Remove temporary passwords from notes.
- [ ] Preserve screenshots and notes for any defects.
- [ ] Record final Pass or Fail above.
