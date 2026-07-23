# Platform E2E QA Cleanup Checklist

Use this checklist after the end-to-end QA run. Prefer deactivation and archival over deletion unless a backup and cascade review have been completed.

Normal cleanup should preserve the QA environment for future releases. Do not delete QA players, coaches, teams, accounts, or evaluations unless the team is intentionally resetting the QA environment.

## Before Cleanup

- [ ] Defects, screenshots, and test notes have been recorded.
- [ ] Evidence needed for open defects has been preserved.
- [ ] Temporary passwords copied during testing are destroyed or removed from notes.
- [ ] Temporary passwords have been removed from tickets, shared documents, chat logs, and screenshots unless the artifact is access-controlled and required for a defect.
- [ ] The QA season is not required for immediate retesting.
- [ ] A recent database backup exists.

## Accounts

Search Account Operations at:

```text
/accounts/users/
```

Deactivate these test accounts when they are not needed for repeat testing. Do not delete them during normal cleanup:

- [ ] `coach.qa.one`
- [ ] `coach.qa.two`
- [ ] `coach.qa.manual`
- [ ] `player.qa.one`
- [ ] `player.qa.two`
- [ ] `player.qa.three`
- [ ] `player.qa.four`
- [ ] `player.qa.manual.one`
- [ ] `player.qa.manual.two`
- [ ] `coach.qa.inactive`
- [ ] any accounts created from `test_coach_account_collision_cases.csv`

Verify:

- [ ] No QA account has Django staff access unless intentionally granted for testing.
- [ ] No QA account is a superuser.
- [ ] QA accounts requiring password change are either deactivated or documented for retest.
- [ ] Temporary passwords are not stored in shared notes, tickets, screenshots, or chat logs.
- [ ] Inactive-account lifecycle fixtures are not left enabled unless intentionally retained for repeat testing.

Retention guidance:

- [ ] QA accounts are retained for the next deployment smoke test.
- [ ] QA account usernames and emails remain clearly identifiable as QA data.
- [ ] Accounts are deactivated rather than deleted when not in use.

## User-Player Links

For each QA player account:

- [ ] Confirm self links are attached only to QA player records.
- [ ] Confirm no real player is linked to a QA user.
- [ ] Do not delete links unless cascade behavior has been reviewed.

## Season And Teams

Use Season Operations:

```text
/seasons/
```

Clean up:

- [ ] Confirm `TEST - Platform QA 2026` is not the current/default season.
- [ ] Mark `TEST - Platform QA 2026` inactive if the QA run is complete.
- [ ] Mark `TEST - Alpha` inactive if supported by the current workflow.
- [ ] Mark `TEST - Beta` inactive if supported by the current workflow.
- [ ] Close, deactivate, or archive `TEST - Cycle A` if it was created.
- [ ] Close, deactivate, or archive `TEST - Cycle B` if it was created.
- [ ] Confirm QA teams no longer appear in normal active selectors, or document why they remain visible.
- [ ] Confirm QA records are not visible in real operational selectors unless the selector intentionally includes inactive or historical data.

Retention guidance:

- [ ] QA season is retained unless the QA environment is intentionally being retired.
- [ ] QA teams are retained unless the QA environment is intentionally being retired.
- [ ] A new QA season is created only when the existing QA data no longer matches the product model.

## Roster Memberships And Coach Assignments

- [ ] End or deactivate QA player roster memberships if repeat smoke testing is not planned.
- [ ] End or deactivate QA coach assignments if repeat smoke testing is not planned.
- [ ] Preserve historical records where they are needed to verify evaluation snapshots.

## Analytics Data

- [ ] Verify reports and review pages no longer include QA data in normal operating filters, or document the QA season filter users should apply.
- [ ] Verify dashboard metrics are not filtered incorrectly after QA season deactivation.
- [ ] Verify command-center counts are understood if QA data remains in all-time aggregates.
- [ ] Preserve submitted QA evaluations if they are useful for regression testing.
- [ ] Document any intentionally retained QA evaluations, including season, cycle, and players involved.
- [ ] Delete evaluations only after backup and cascade review.

Retention guidance:

- [ ] Historical QA evaluations are kept for trend, timeline, review, and repeat-deployment testing unless a reset is intentional.
- [ ] Evaluation cycles are closed, deactivated, or clearly named instead of deleting evaluations.
- [ ] New smoke-test cycles can be added over time without rebuilding players, coaches, teams, or accounts.

## Negative-Test Fixtures

- [ ] Deactivate collision-test accounts.
- [ ] Confirm inactive-coach fixture accounts remain inactive after testing.
- [ ] Confirm collision-test imports did not create real player records.
- [ ] Confirm collision-test imports did not create user-player links.
- [ ] Remove temporary passwords from notes.
- [ ] Keep negative-test result notes separate from normal smoke-test sign-off.

## Final Cleanup Review

- [ ] No real users are assigned to the QA season.
- [ ] No real players are linked to QA accounts.
- [ ] QA records are clearly identifiable by `QA` or `TEST -`.
- [ ] QA season is not current/default.
- [ ] QA records are not visible in normal real-season operational selectors unless intentionally retained.
- [ ] The QA environment can be reused for the next production deployment without deleting records.
- [ ] The cleanup outcome is recorded in the QA run notes.
