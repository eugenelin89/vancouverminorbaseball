Review the existing Platform E2E QA package under:

`docs/qa/platform_e2e/`

This is an incremental improvement only.

Do **not** rewrite or reorganize the package.

Do **not** modify application code.

Do **not** change existing documented behavior unless code inspection proves the documentation is incorrect.

The current QA package is already comprehensive. This task is intended to make it more reliable for long-term production use.

---

# Goal

Address the remaining QA design issues:

1. Make the production smoke test repeatable across deployments.
2. Distinguish "create" workflows from "reuse existing" workflows.
3. Improve long-term QA data management.
4. Make repeated production deployments require almost no cleanup.
5. Add a small amount of operational guidance for future maintainers.

---

# 1. Review Current Evaluation Uniqueness Rules

Verify the actual uniqueness behavior from the code.

Current documentation states that evaluations are unique by something equivalent to:

```text
Evaluator
+ Player
+ Observation Type
+ Perspective
+ Evaluation Cycle
```

and that self evaluations are unique per:

```text
Player
+ Evaluation Cycle
```

Confirm this is still correct.

If it differs, update the documentation accordingly.

Do not guess.

---

# 2. Improve Production Smoke Test Repeatability

Review:

```text
production_smoke_test.md
```

Currently the smoke test assumes new evaluations can always be submitted.

That is not necessarily true because previous smoke tests may already have created submitted evaluations.

Modify the smoke test so it is repeatable indefinitely.

Preferred approach:

For each evaluation workflow, explicitly distinguish:

## First deployment

Create a brand-new evaluation.

## Subsequent deployments

If an evaluation already exists:

- reopen it if appropriate
- edit one answer
- resubmit it
- verify the same record was reused
- verify no duplicate record was created

The smoke test should never require deleting QA data simply to make the next deployment test work.

---

# 3. Add Smoke-Test Mode

Add a small section near the beginning of:

```text
production_smoke_test.md
```

called:

```markdown
Smoke Test Mode
```

with two supported modes.

## Mode A

First deployment

Expected behavior:

- imports create new records
- evaluations create new records

## Mode B

Repeat deployment

Expected behavior:

- imports reuse existing records
- account provisioning reuses existing accounts
- evaluations reopen or reuse existing records
- duplicate records are not created

This should make it obvious which expectations apply during repeated releases.

---

# 4. Record Evaluation Cycle

Add to the smoke-test header:

```text
Evaluation Cycle:

Smoke Test Mode:

Expected Result:
```

This allows historical smoke-test records to identify exactly which cycle was used.

---

# 5. Separate Create vs Reuse Expectations

Throughout the smoke test, explicitly distinguish:

Creation checks

Example:

```text
First deployment:

□ account created
□ evaluation created
□ assignment created
```

versus

Repeat deployment:

```text
□ account reused

□ player reused

□ assignment reused

□ evaluation reopened

□ no duplicate created
```

Avoid wording that implies every deployment should create new data.

---

# 6. Add Recommended Long-Term QA Strategy

Update README.md.

Add a short section:

```markdown
Recommended Long-Term QA Strategy
```

Recommend maintaining one permanent QA environment.

Example:

```text
Season:

TEST - Platform QA

Evaluation Cycles:

TEST - Smoke YYYY-MM-DD

or

TEST - Release 1.8.2
```

Document that:

Players

Coaches

Teams

Accounts

remain permanent.

Only evaluation cycles grow over time.

This minimizes maintenance.

---

# 7. Add Evaluation Cycle Guidance

Document recommended practice.

For example:

Full regression:

Create:

```text
TEST - Cycle A

TEST - Cycle B
```

Smoke tests:

Either

create a new smoke-test cycle

OR

reuse an existing smoke-test cycle and reopen evaluations.

Document both supported approaches.

Do not prescribe one unless the application already requires it.

---

# 8. Add QA Data Retention Guidance

Extend:

```text
cleanup_checklist.md
```

Clarify that normally:

Do NOT delete

- QA players
- QA coaches
- QA teams
- QA accounts

Instead:

Deactivate when appropriate.

Archive seasons if necessary.

Keep historical evaluations.

Delete only when intentionally resetting the QA environment.

---

# 9. Add QA Environment Lifecycle

Add a new README section:

```markdown
QA Environment Lifecycle
```

Example:

Build once

↓

Use for many releases

↓

Archive when obsolete

↓

Create a new QA environment only if the data model changes significantly.

This helps prevent unnecessary recreation of fixtures every release.

---

# 10. Add Future Regression Guidance

Add a brief note.

When adding future platform features, extend the QA package rather than replacing it.

Examples:

new evaluator roles

new observation types

new dashboards

new reports

new permissions

new importers

should each receive:

- one smoke-test item
- one release-blocking test if appropriate
- one full regression section if needed

This encourages the QA package to evolve incrementally instead of being rewritten.

---

# 11. Validation

Re-run:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
git diff --check
```

Validate that:

- no existing happy-path fixtures changed unnecessarily
- smoke test remains concise
- documentation remains internally consistent
- no unsupported claims were introduced

---

# 12. Completion Report

Report:

1. Files modified.
2. New sections added.
3. Smoke-test repeatability improvements.
4. README improvements.
5. Cleanup improvements.
6. Whether the package now supports repeated production deployments without requiring QA data deletion.
7. Any remaining policy decisions.

Commit with a message similar to:

```text
Improve long-term QA workflow and smoke-test repeatability
```

Do not push unless explicitly instructed.

==================================================
Implementation Commit Diff
==================================================

```diff
commit 613b2d4d15eded012ae2656e464261c8560b9ec5
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 23 14:43:32 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 23 14:43:32 2026 -0700

    Improve long-term QA workflow and smoke-test repeatability
---
 docs/qa/platform_e2e/README.md                | 97 +++++++++++++++++++++++++++
 docs/qa/platform_e2e/cleanup_checklist.md     | 23 ++++++-
 docs/qa/platform_e2e/production_smoke_test.md | 89 +++++++++++++++++++++---
 3 files changed, 199 insertions(+), 10 deletions(-)

diff --git a/docs/qa/platform_e2e/README.md b/docs/qa/platform_e2e/README.md
index e5a7ae4..a5ad520 100644
--- a/docs/qa/platform_e2e/README.md
+++ b/docs/qa/platform_e2e/README.md
@@ -74,6 +74,103 @@ Production smoke test

 Do not import optional negative fixtures during a normal production smoke test. Use them only when deliberately testing collision or inactive-account behavior.

+## Recommended Long-Term QA Strategy
+
+Maintain one permanent QA environment instead of recreating fixtures for every release.
+
+Recommended permanent season:
+
+```text
+TEST - Platform QA
+```
+
+The current fixture season remains:
+
+```text
+TEST - Platform QA 2026
+```
+
+Either naming style is acceptable as long as it is clearly isolated from real seasons.
+
+Recommended evaluation-cycle naming:
+
+```text
+TEST - Smoke YYYY-MM-DD
+```
+
+or:
+
+```text
+TEST - Release 1.8.2
+```
+
+Long-term practice:
+
+- keep QA players permanent;
+- keep QA coaches permanent;
+- keep QA teams permanent;
+- keep QA accounts permanent but deactivate them when not needed;
+- keep historical QA evaluations unless intentionally resetting the QA environment;
+- create new evaluation cycles over time when a clean smoke-test run is useful;
+- reuse existing evaluation cycles by reopening and resubmitting records when repeatability is more important than a clean cycle.
+
+This keeps repeated production deployments fast and minimizes cleanup.
+
+## Evaluation Cycle Guidance
+
+Full regression:
+
+- create or reuse `TEST - Cycle A`;
+- create or reuse `TEST - Cycle B`;
+- verify that identical evaluator/player/perspective combinations can be tested independently in each cycle.
+
+Smoke tests support either approach:
+
+- create a new smoke-test cycle such as `TEST - Smoke 2026-07-23`; or
+- reuse an existing smoke-test cycle and reopen/resubmit existing evaluations.
+
+The application does not require one approach over the other. Choose based on whether the release needs clean cycle-specific counts or repeatable low-maintenance checks.
+
+Current uniqueness behavior:
+
+```text
+Evaluator + Player + Observation Type + Perspective + Evaluation Cycle
+```
+
+Self-evaluations also enforce:
+
+```text
+Player + Evaluation Cycle
+```
+
+This means repeated smoke tests in the same cycle should reuse/reopen existing evaluations rather than trying to create new duplicate evaluations.
+
+## QA Environment Lifecycle
+
+```text
+Build once
+-> use for many releases
+-> archive when obsolete
+-> create a new QA environment only when the data model or product workflow changes significantly
+```
+
+When future platform features are added, extend this QA package instead of replacing it.
+
+Examples:
+
+- new evaluator roles;
+- new observation types;
+- new dashboards;
+- new reports;
+- new permissions;
+- new importers.
+
+Each future feature should receive:
+
+- one smoke-test item;
+- one release-blocking test if appropriate;
+- one full regression section if needed.
+
 ## Important Import Notes

 - Player import and coach import use different CSV schemas.
diff --git a/docs/qa/platform_e2e/cleanup_checklist.md b/docs/qa/platform_e2e/cleanup_checklist.md
index 2f8082b..9b6755f 100644
--- a/docs/qa/platform_e2e/cleanup_checklist.md
+++ b/docs/qa/platform_e2e/cleanup_checklist.md
@@ -2,6 +2,8 @@

 Use this checklist after the end-to-end QA run. Prefer deactivation and archival over deletion unless a backup and cascade review have been completed.

+Normal cleanup should preserve the QA environment for future releases. Do not delete QA players, coaches, teams, accounts, or evaluations unless the team is intentionally resetting the QA environment.
+
 ## Before Cleanup

 - [ ] Defects, screenshots, and test notes have been recorded.
@@ -19,7 +21,7 @@ Search Account Operations at:
 /accounts/users/
 ```

-Deactivate these test accounts:
+Deactivate these test accounts when they are not needed for repeat testing. Do not delete them during normal cleanup:

 - [ ] `coach.qa.one`
 - [ ] `coach.qa.two`
@@ -41,6 +43,12 @@ Verify:
 - [ ] Temporary passwords are not stored in shared notes, tickets, screenshots, or chat logs.
 - [ ] Inactive-account lifecycle fixtures are not left enabled unless intentionally retained for repeat testing.

+Retention guidance:
+
+- [ ] QA accounts are retained for the next deployment smoke test.
+- [ ] QA account usernames and emails remain clearly identifiable as QA data.
+- [ ] Accounts are deactivated rather than deleted when not in use.
+
 ## User-Player Links

 For each QA player account:
@@ -68,6 +76,12 @@ Clean up:
 - [ ] Confirm QA teams no longer appear in normal active selectors, or document why they remain visible.
 - [ ] Confirm QA records are not visible in real operational selectors unless the selector intentionally includes inactive or historical data.

+Retention guidance:
+
+- [ ] QA season is retained unless the QA environment is intentionally being retired.
+- [ ] QA teams are retained unless the QA environment is intentionally being retired.
+- [ ] A new QA season is created only when the existing QA data no longer matches the product model.
+
 ## Roster Memberships And Coach Assignments

 - [ ] End or deactivate QA player roster memberships if repeat smoke testing is not planned.
@@ -83,6 +97,12 @@ Clean up:
 - [ ] Document any intentionally retained QA evaluations, including season, cycle, and players involved.
 - [ ] Delete evaluations only after backup and cascade review.

+Retention guidance:
+
+- [ ] Historical QA evaluations are kept for trend, timeline, review, and repeat-deployment testing unless a reset is intentional.
+- [ ] Evaluation cycles are closed, deactivated, or clearly named instead of deleting evaluations.
+- [ ] New smoke-test cycles can be added over time without rebuilding players, coaches, teams, or accounts.
+
 ## Negative-Test Fixtures

 - [ ] Deactivate collision-test accounts.
@@ -99,4 +119,5 @@ Clean up:
 - [ ] QA records are clearly identifiable by `QA` or `TEST -`.
 - [ ] QA season is not current/default.
 - [ ] QA records are not visible in normal real-season operational selectors unless intentionally retained.
+- [ ] The QA environment can be reused for the next production deployment without deleting records.
 - [ ] The cleanup outcome is recorded in the QA run notes.
diff --git a/docs/qa/platform_e2e/production_smoke_test.md b/docs/qa/platform_e2e/production_smoke_test.md
index d68de95..6446183 100644
--- a/docs/qa/platform_e2e/production_smoke_test.md
+++ b/docs/qa/platform_e2e/production_smoke_test.md
@@ -4,6 +4,28 @@ Use this checklist after deployment. It is intentionally shorter than the full E

 Do not use optional negative fixtures during the smoke test.

+## Smoke Test Mode
+
+Choose one mode before starting.
+
+### Mode A: First Deployment
+
+Expected behavior:
+
+- imports create new player, coach, account, roster membership, and assignment records;
+- evaluations create new observation records;
+- temporary passwords are captured only where newly created accounts require them.
+
+### Mode B: Repeat Deployment
+
+Expected behavior:
+
+- imports reuse existing players, coaches, accounts, roster memberships, and assignments;
+- account provisioning reuses or reports already-linked player accounts;
+- evaluations reuse existing drafts or submitted records;
+- submitted evaluations are reopened, edited, and resubmitted where appropriate;
+- no duplicate records are created.
+
 ## Run Information

 ```text
@@ -11,6 +33,9 @@ Tester:
 Date:
 Environment:
 Commit:
+Evaluation Cycle:
+Smoke Test Mode:
+Expected Result:
 Overall result:
 Critical defects:
 Non-critical defects:
@@ -31,33 +56,79 @@ Non-critical defects:
 - [ ] Open Operations Home `/analytics/`.
 - [ ] Confirm Imports, User Accounts, Seasons, Evaluations, and Review links work.
 - [ ] Import or re-import `test_players_import.csv`.
-- [ ] Verify no duplicate players, player accounts, self links, or active roster memberships are created.
 - [ ] Import or re-import `test_coaches_import.csv`.
-- [ ] Verify no duplicate coach accounts or active coach assignments are created.
 - [ ] Create or verify one manual account from `manual_test_records.md`.

+First deployment:
+
+- [ ] Player import creates the expected QA players.
+- [ ] Player import creates active roster memberships.
+- [ ] Player account provisioning creates or links player accounts.
+- [ ] Coach import creates the expected QA coaches.
+- [ ] Coach import creates coach assignments.
+- [ ] Manual account creation creates the selected manual QA account.
+
+Repeat deployment:
+
+- [ ] Player import reuses or updates existing QA players.
+- [ ] Player import does not create duplicate player accounts, self links, or active roster memberships.
+- [ ] Coach import reuses existing coach accounts.
+- [ ] Coach import does not create duplicate active coach assignments.
+- [ ] Manual account already exists or is verified without recreating it.
+
 ## Coach Workflow

 - [ ] Sign in as imported coach `coach.qa.one`.
-- [ ] Create, save, reopen, and submit one coach evaluation.
 - [ ] Sign in as manual coach `coach.qa.manual`.
-- [ ] Submit one evaluation of an imported player.
+
+First deployment:
+
+- [ ] Imported coach creates, saves, reopens, and submits one coach evaluation.
+- [ ] Manual coach submits one evaluation of an imported player.
+
+Repeat deployment:
+
+- [ ] If the imported coach evaluation is already submitted, reopen it from staff review.
+- [ ] Edit one answer as the original imported coach.
+- [ ] Resubmit the same imported-coach evaluation.
+- [ ] If the manual coach evaluation is already submitted, reopen it from staff review.
+- [ ] Edit one answer as the original manual coach.
+- [ ] Resubmit the same manual-coach evaluation.
+- [ ] Confirm both workflows reused existing observation records and created no duplicates.

 ## Player Workflow

 - [ ] Sign in as imported player `player.qa.one`.
-- [ ] Submit one self-evaluation.
-- [ ] Submit one peer evaluation of a manual player.
 - [ ] Sign in as manual player `player.qa.manual.one`.
-- [ ] Submit one self-evaluation or one peer evaluation of an imported player.
+
+First deployment:
+
+- [ ] Imported player submits one self-evaluation.
+- [ ] Imported player submits one peer evaluation of a manual player.
+- [ ] Manual player submits one self-evaluation or one peer evaluation of an imported player.
+
+Repeat deployment:
+
+- [ ] If the imported player's self-evaluation already exists, reopen it from staff review.
+- [ ] Edit one answer as the imported player.
+- [ ] Resubmit the same self-evaluation.
+- [ ] If the imported player's peer evaluation already exists, reopen it from staff review.
+- [ ] Edit one answer as the imported player.
+- [ ] Resubmit the same peer evaluation.
+- [ ] If the manual player's evaluation already exists, reopen it from staff review.
+- [ ] Edit one answer as the manual player.
+- [ ] Resubmit the same evaluation.
+- [ ] Confirm no duplicate self or peer evaluation records were created.

 ## Review Workflow

 - [ ] Sign back in as administrator or Django staff.
 - [ ] Confirm all smoke-test evaluations appear in `/analytics/evaluation-review/`.
-- [ ] Reopen one evaluation from `/analytics/observations/review/`.
+- [ ] Record the observation IDs for each smoke-test evaluation.
+- [ ] Reopen one evaluation from `/analytics/observations/review/` if no repeat-mode reopen was already performed.
 - [ ] Resubmit it as the original evaluator.
-- [ ] Confirm no duplicate evaluation is created.
+- [ ] Confirm the same observation ID was reused.
+- [ ] Confirm no duplicate evaluation was created for the same evaluator, player, perspective, and cycle.
 - [ ] Confirm the player timeline includes the submitted evaluations.
 - [ ] Confirm player comparison includes submitted evaluation scores.
 - [ ] Confirm key Command Center metrics changed by the expected amount.

```
