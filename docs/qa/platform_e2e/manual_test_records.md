# Manual QA Test Records

These records are intentionally excluded from the CSV files so administrators can test manual creation workflows alongside import workflows.

Use artificial data only. Replace every placeholder email address with a controlled test inbox alias before creating accounts.

## Manual Records

| Record | First name | Last name | Username | Email placeholder | Role | Season | Team | Division | Active | Staff | Superuser | Player relationship | Expected password workflow |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Manual coach | Coach | QA Manual | `coach.qa.manual` | `REPLACE_WITH_YOUR_EMAIL+qa-coach-manual@example.com` | Coach | `TEST - Platform QA 2026` | `TEST - Alpha` | `13U House` | Yes | No | No | None | Temporary password shown once; must change password on first login. |
| Manual player one | Player | QA Manual One | `player.qa.manual.one` | `REPLACE_WITH_YOUR_EMAIL+qa-player-manual1@example.com` | Player | `TEST - Platform QA 2026` | `TEST - Alpha` | `13U House` | Yes | No | No | Self, primary | Temporary password shown once for manual account creation; must change password on first login. |
| Manual player two | Player | QA Manual Two | `player.qa.manual.two` | `REPLACE_WITH_YOUR_EMAIL+qa-player-manual2@example.com` | Player | `TEST - Platform QA 2026` | `TEST - Beta` | `13U House` | Yes | No | No | Self, primary | Temporary password shown once for manual account creation; must change password on first login. |

## Manual Coach Creation

Use Account Operations:

```text
/accounts/create/
```

Create:

- username: `coach.qa.manual`
- first name: `Coach`
- last name: `QA Manual`
- email: controlled replacement for `REPLACE_WITH_YOUR_EMAIL+qa-coach-manual@example.com`
- role: `Coach`
- active: checked

Then create a coach assignment:

```text
/seasons/coach-assignments/new/
```

Use:

- coach account: `coach.qa.manual`
- season team: `TEST - Platform QA 2026 / 13U House TEST - Alpha`
- assignment role: `Assistant Coach`
- primary: checked if this is the coach's only active assignment in the season
- active: checked
- start date: `2026-07-01`
- source: `manual_qa`
- source identifier: `qa-assignment-coach-manual`

Verification:

- [ ] User exists.
- [ ] Account role is Coach.
- [ ] User is active.
- [ ] User is not Django staff.
- [ ] User is not a superuser.
- [ ] Coach assignment exists for `TEST - Alpha`.
- [ ] Password change is required before normal platform use.

## Manual Player Creation

For each manual player, create the canonical player first if it does not already exist. Use the player management route available through season membership creation or Django admin if required by the current environment.

Then create a player account:

```text
/accounts/create/player/
```

Use:

- player: the matching manual QA player
- username: table value above
- email: controlled replacement from the table
- role: `Player`
- active: checked

Then create a player roster membership:

```text
/seasons/memberships/new/
```

Use:

- player: matching manual QA player
- season team: matching QA team
- status: `Active`
- primary: checked
- active: checked
- start date: `2026-07-01`
- source: `manual_qa`
- source identifier:
  - `qa-membership-player-manual-001` for Player QA Manual One
  - `qa-membership-player-manual-002` for Player QA Manual Two

Verification for each manual player:

- [ ] Player exists once.
- [ ] User exists once.
- [ ] Account role is Player.
- [ ] User is active.
- [ ] User is not Django staff.
- [ ] User is not a superuser.
- [ ] A primary active self link exists between user and player.
- [ ] A primary active roster membership exists for the correct QA team.
- [ ] Password change is required before normal platform use.
