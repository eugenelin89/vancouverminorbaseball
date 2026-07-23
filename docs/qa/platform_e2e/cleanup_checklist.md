# Platform E2E QA Cleanup Checklist

Use this checklist after the end-to-end QA run. Prefer deactivation and archival over deletion unless a backup and cascade review have been completed.

## Before Cleanup

- [ ] Defects, screenshots, and test notes have been recorded.
- [ ] Temporary passwords copied during testing are destroyed or removed from notes.
- [ ] The QA season is not required for immediate retesting.
- [ ] A recent database backup exists.

## Accounts

Search Account Operations at:

```text
/accounts/users/
```

Deactivate these test accounts:

- [ ] `coach.qa.one`
- [ ] `coach.qa.two`
- [ ] `coach.qa.manual`
- [ ] `player.qa.one`
- [ ] `player.qa.two`
- [ ] `player.qa.three`
- [ ] `player.qa.four`
- [ ] `player.qa.manual.one`
- [ ] `player.qa.manual.two`

Verify:

- [ ] No QA account has Django staff access unless intentionally granted for testing.
- [ ] No QA account is a superuser.
- [ ] QA accounts requiring password change are either deactivated or documented for retest.
- [ ] Temporary passwords are not stored in shared notes, tickets, screenshots, or chat logs.

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
- [ ] Confirm QA teams no longer appear in normal active selectors, or document why they remain visible.

## Roster Memberships And Coach Assignments

- [ ] End or deactivate QA player roster memberships if repeat smoke testing is not planned.
- [ ] End or deactivate QA coach assignments if repeat smoke testing is not planned.
- [ ] Preserve historical records where they are needed to verify evaluation snapshots.

## Analytics Data

- [ ] Verify reports and review pages no longer include QA data in normal operating filters, or document the QA season filter users should apply.
- [ ] Preserve submitted QA evaluations if they are useful for regression testing.
- [ ] Delete evaluations only after backup and cascade review.

## Final Cleanup Review

- [ ] No real users are assigned to the QA season.
- [ ] No real players are linked to QA accounts.
- [ ] QA records are clearly identifiable by `QA` or `TEST -`.
- [ ] The cleanup outcome is recorded in the QA run notes.
