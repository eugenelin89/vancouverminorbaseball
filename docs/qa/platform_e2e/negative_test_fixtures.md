# Negative Test Fixtures

These fixtures are optional. Do not use them during the normal production smoke test or happy-path release validation.

Replace all placeholder email addresses with controlled test inbox aliases before importing.

## `test_coaches_inactive_import.csv`

Purpose:

- Verify that coach import supports inactive accounts.
- Verify inactive imported accounts cannot sign in until staff activates them.
- Verify activation does not change role, staff status, superuser status, assignment history, or temporary-password behavior.

Prerequisites:

- QA season `TEST - Platform QA 2026` exists and is active.
- QA team `TEST - Alpha` exists or may be created by import.
- The placeholder email has been replaced with a controlled test inbox alias.

Expected outcome:

- One coach account is created with role Coach.
- `User.is_active` is false.
- The coach season assignment is created as inactive.
- A temporary password is shown once on the result page.
- The inactive coach cannot sign in until activated through Account Operations.
- After activation, the coach must change password before normal platform use.

Cleanup:

- Deactivate `coach.qa.inactive` after the lifecycle test.
- End or deactivate the inactive coach assignment if it is not needed for future regression testing.

## `test_coach_account_collision_cases.csv`

Purpose:

- Exercise coach import username and email collision behavior without modifying the happy-path coach fixture.
- Verify preview and result messages are clear enough for staff.

Prerequisites:

- Run the standard player and coach imports first.
- The standard imports should have created or reused `coach.qa.one` and the Player QA One account.
- Replace every placeholder email address with controlled test inbox aliases using the same aliases used for the standard fixture where the row intentionally references an existing account.

Expected outcome:

- Row using Coach QA One's existing coach email should reuse the existing coach account and keep its password unchanged.
- Row using Player QA One's email should conflict because the email belongs to a non-coach account.
- Two rows that generate the same `collision.coach` username should leave one row ready and mark the other as a username conflict in preview.
- Explicit username `coach.qa.one` should conflict because that username already exists.
- The whitespace email row should trim and normalize the email before account creation.

Cleanup:

- Deactivate any new collision-test coach accounts.
- Remove temporary passwords from notes.
- Confirm no `players.Player` records or `UserPlayerLink` rows were created by the coach collision fixture.

## Player Account-Provisioning Collision Tests

No separate mixed-schema CSV is included because player account-provisioning collision tests are safest through the existing player import workflow:

- Use a working copy of `test_players_import.csv`.
- Change one player row's `account_email` to match an existing unrelated player account email.
- Change another player row's `account_email` to match an existing coach account email.
- Re-import through `/analytics/imports/new/` with account provisioning enabled.

Expected outcome:

- Same player with the same email should reuse or already-link safely.
- Different player using an existing player email should conflict and should not create a self link.
- Player import using an email owned by a coach account should conflict and should not change the coach role.
- Case-only email differences and surrounding whitespace should normalize to the same existing email.

Policy decision required:

- Decide whether QA should maintain permanent collision-test player records or only use disposable working copies during extended regression.
