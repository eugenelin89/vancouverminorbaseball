# Production Smoke Test

Use this checklist after deployment. It is intentionally shorter than the full E2E script and should fit into one short testing session.

Do not use optional negative fixtures during the smoke test.

## Run Information

```text
Tester:
Date:
Environment:
Commit:
Overall result:
Critical defects:
Non-critical defects:
```

## Setup

- [ ] Confirm the deployed commit.
- [ ] Confirm a recent database backup exists.
- [ ] Confirm QA season `TEST - Platform QA 2026` is active for testing.
- [ ] Confirm `TEST - Alpha` and `TEST - Beta` exist.
- [ ] Replace CSV placeholder emails with controlled test aliases.
- [ ] Activate only the QA accounts required for this smoke test.

## Admin Workflow

- [ ] Sign in as an administrator or Django staff user.
- [ ] Open Operations Home `/analytics/`.
- [ ] Confirm Imports, User Accounts, Seasons, Evaluations, and Review links work.
- [ ] Import or re-import `test_players_import.csv`.
- [ ] Verify no duplicate players, player accounts, self links, or active roster memberships are created.
- [ ] Import or re-import `test_coaches_import.csv`.
- [ ] Verify no duplicate coach accounts or active coach assignments are created.
- [ ] Create or verify one manual account from `manual_test_records.md`.

## Coach Workflow

- [ ] Sign in as imported coach `coach.qa.one`.
- [ ] Create, save, reopen, and submit one coach evaluation.
- [ ] Sign in as manual coach `coach.qa.manual`.
- [ ] Submit one evaluation of an imported player.

## Player Workflow

- [ ] Sign in as imported player `player.qa.one`.
- [ ] Submit one self-evaluation.
- [ ] Submit one peer evaluation of a manual player.
- [ ] Sign in as manual player `player.qa.manual.one`.
- [ ] Submit one self-evaluation or one peer evaluation of an imported player.

## Review Workflow

- [ ] Sign back in as administrator or Django staff.
- [ ] Confirm all smoke-test evaluations appear in `/analytics/evaluation-review/`.
- [ ] Reopen one evaluation from `/analytics/observations/review/`.
- [ ] Resubmit it as the original evaluator.
- [ ] Confirm no duplicate evaluation is created.
- [ ] Confirm the player timeline includes the submitted evaluations.
- [ ] Confirm player comparison includes submitted evaluation scores.
- [ ] Confirm key Command Center metrics changed by the expected amount.

## Security Workflow

- [ ] Coach receives 403 from `/analytics/imports/`.
- [ ] Coach receives 403 from `/accounts/`.
- [ ] Player receives 403 from `/analytics/evaluation-review/`.
- [ ] Player receives 403 from `/accounts/`.
- [ ] Anonymous user is redirected to login from `/analytics/`.

## Cleanup

- [ ] Deactivate QA accounts not needed for continued testing.
- [ ] Archive or deactivate the QA season when appropriate.
- [ ] Remove temporary passwords from notes.
- [ ] Preserve screenshots and notes for any defects.
- [ ] Record final Pass or Fail above.
