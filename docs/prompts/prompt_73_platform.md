# Prompt 73 - Platform

App/subsystem: platform

Work commit: `ba42484`

## User Prompt

```text
Update the Seasonal Participation V1 engineering plan to reflect the verified production state and complete Phase 0 decisions.

This is a documentation-only task.

Do NOT implement application code.

Do NOT create models or migrations.

Do NOT modify services, views, forms, templates, URLs, middleware, settings, tests, or deployment configuration.

Do NOT regenerate `project_flat_file.txt`.

==================================================
Verified Production State
=========================

The following production counts were checked on July 15, 2026:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

These counts were obtained from the production database using the production environment.

Therefore:

* there are no imported Platform V1 players;
* there are no imported coach profiles;
* there are no Analytics observations;
* there is no seasonal player, coach, or evaluation history to reconstruct;
* no fake legacy season is required;
* no player roster backfill is required;
* no coach assignment backfill is required;
* no observation season/team backfill is required.

Existing unrelated production data in legacy apps must remain untouched.

==================================================
Task
====

Review:

* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* `docs/ARCHITECTURE.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`
* `AGENTS.md`
* relevant player, account, Analytics, and import code

Update the Seasonal Participation V1 plan so that it uses an empty-production migration strategy rather than a legacy-data backfill strategy.

Mark Phase 0 complete only after all decisions below are explicitly recorded.

==================================================
Phase 0 Decisions
=================

Record the following decisions unless repository evidence shows a concrete technical conflict.

## 1. New Bounded Context

Create a new Django app named:

```text
seasons
```

It will own:

* `Season`
* `SeasonTeam`
* `PlayerRosterMembership`
* `CoachSeasonAssignment`

This app owns seasonal participation, not permanent identity.

## 2. Permanent Identity

Keep:

* `players.Player` as the permanent player identity;
* Django `User` and `accounts.AccountProfile` as the permanent coach/account identity.

Players and coach accounts must be reused across seasons.

## 3. Season Naming

Use a stable unique key and a human-friendly display name.

Examples:

```text
2026-spring
2026-summer
2027-spring
```

Display names:

```text
2026 Spring
2026 Summer
2027 Spring
```

Do not hard-code a specific list of season types.

## 4. Current Season

Allow exactly one current season.

Use a database constraint if it is safe and supported by SQLite.

If a database-only constraint is impractical, enforce the rule through a transactional service and tests.

Inactive seasons remain historical and must not be deleted when referenced.

## 5. Season Teams

Use season-specific teams only for V1.

Examples:

```text
2026 Spring / 13U Dodgers
2027 Spring / 13U Dodgers
```

These are distinct records.

Do not add a permanent Team model in V1.

## 6. Player Memberships

Allow a player to have multiple memberships in one season.

Support:

* transfers;
* concurrent team participation;
* guest or affiliate participation;
* corrected imports.

Allow only one active primary membership per player per season.

A transfer must create a new membership or stint rather than overwrite the old membership.

## 7. Coach Assignments

Allow one coach to have multiple assignments in one season.

Keep seasonal assignment role separate from permanent account role.

Use a minimal controlled assignment-role list:

* Head Coach
* Assistant Coach
* Manager
* Coordinator
* Evaluator

Document how future roles may be added safely.

## 8. Evaluation Cycles

Treat `Season` and `EvaluationCycle` as distinct concepts.

Relationship:

```text
Season
    has many EvaluationCycles
```

New evaluation cycles should require a season once the seasonal foundation is implemented.

The migration may initially use a nullable relationship for deployment safety, but the application workflow should require a season for newly created production cycles.

## 9. Existing Player Fields

Keep:

* `Player.team_name`
* `Player.division`

temporarily as compatibility/current-display fields.

They are not authoritative historical fields.

During the compatibility period:

* seasonal membership is authoritative;
* the current primary membership may update these fields for existing UI compatibility;
* new imports must not treat these fields as permanent identity;
* removal is deferred until all reads use seasonal services.

## 10. Production Migration Strategy

Because production contains zero players, zero coach profiles, and zero observations:

* create schema only;
* do not create a legacy season;
* do not fabricate roster memberships;
* do not fabricate coach assignments;
* do not backfill observations;
* leave all new tables empty after migration;
* preserve existing legacy app data untouched.

The migration must still be defensive if unexpected rows exist in another environment.

Document whether defensive checks belong in migrations, services, or deployment verification.

## 11. Import Requirement

Once season-aware imports are implemented:

* player import must require a selected season;
* coach import must require a selected season;
* team and division must create or reuse a `SeasonTeam`;
* permanent people must be reused;
* future-season imports must create new memberships or assignments;
* existing coach passwords must not be reset during routine seasonal reimport.

## 12. Evaluation Context

The recommended future design remains:

* FK references to season/team/membership where useful;
* immutable snapshot fields on submitted observations.

However, no evaluation-context migration or backfill is needed during the initial schema foundation because production has zero observations.

==================================================
Update The Plan
===============

Update:

```text
docs/seasons/implementation/engineering/seasonal_participation_v1.md
```

Required changes:

* mark Phase 0 decisions complete;
* record the verified production counts and date;
* replace the legacy-backfill recommendation;
* remove the fake legacy-season recommendation;
* simplify migration and rollback planning;
* identify Phase 1 as the next implementation phase;
* update risks and open questions;
* make clear that production is currently an empty state for Platform V1 roster/evaluation data.

Update:

```text
docs/seasons/README.md
```

Include:

* current status;
* Phase 0 complete;
* Phase 1 next;
* no implementation completed yet.

Update cross-links only if necessary:

* `docs/ARCHITECTURE.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`

Do not duplicate the full decision record elsewhere.

==================================================
Phase 1 Definition
==================

Define the next implementation phase as:

```text
Phase 1 — Season And Roster Foundation
```

Its future scope should be limited to:

* create the `seasons` app;
* add `Season`;
* add `SeasonTeam`;
* add `PlayerRosterMembership`;
* add `CoachSeasonAssignment`;
* add transactional domain services;
* add Django admin support;
* add migrations;
* add comprehensive tests;
* add compatibility helpers for current team/division;
* register the app in settings;
* update architecture and user/admin documentation as needed.

Phase 1 must not yet:

* change player import UI;
* change coach import UI;
* attach evaluation context;
* enforce team-based permissions;
* add roster-management dashboards;
* remove Player fields;
* implement Platform V2 summaries.

==================================================
Acceptance Criteria
===================

Do not declare PASS until:

* verified production counts are documented;
* the migration strategy is empty-state-first;
* no fake historical data is proposed;
* all Phase 0 decisions are explicit;
* model ownership is settled;
* season naming is settled;
* current-season behavior is settled;
* player primary-membership behavior is settled;
* coach assignment roles are settled;
* evaluation-cycle relationship is settled;
* compatibility-field policy is settled;
* Phase 1 scope and non-scope are clear;
* no application code changed;
* `git diff --check` passes;
* documentation commits are pushed;
* the working tree is clean.

==================================================
Loop Engineering
================

Use loop engineering for documentation quality.

Each loop must:

1. inspect the current plan and repository;
2. identify contradictions or remaining undecided items;
3. update only planning documentation and necessary cross-links;
4. review from the perspective of:

   * import operator;
   * administrator;
   * coach;
   * data architect;
   * release engineer;
5. confirm no unsupported historical data is invented;
6. confirm the Phase 1 boundary is narrow and implementable;
7. run `git diff --check`;
8. commit the documentation update;
9. archive the prompt according to `AGENTS.md`;
10. commit the prompt archive separately;
11. push both commits;
12. confirm the working tree is clean;
13. choose:

* CONTINUE;
* PASS;
* BLOCKED;
* NO_PROGRESS.

Do not continue through formatting-only loops.

==================================================
Rules
=====

Documentation only.

No application code.

No models.

No migrations.

No tests.

No settings changes.

No deployment changes.

Do not regenerate `project_flat_file.txt`.

==================================================
Verification
============

Run only:

```bash
git diff --check
```

==================================================
Git Workflow
============

Create two commits:

1.

```text
Finalize seasonal participation phase 0
```

2.

Prompt archive commit according to `AGENTS.md`.

Push both commits.

==================================================
Final Report
============

Report:

* terminal state;
* loops completed;
* files modified;
* verified production counts;
* Phase 0 decisions;
* revised migration strategy;
* Phase 1 scope;
* remaining open questions;
* verification result;
* commits;
* push result;
* confirmation that no application code changed;
* confirmation that the working tree is clean.
```

## Work Commit Diff

```diff
commit ba42484e962c9df0fc1f98cb5bb4eb6551d2ac1c
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 15 14:39:28 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 15 14:39:28 2026 -0700

    Finalize seasonal participation phase 0

diff --git a/docs/seasons/README.md b/docs/seasons/README.md
index bf0ad0c..d71704a 100644
--- a/docs/seasons/README.md
+++ b/docs/seasons/README.md
@@ -17,5 +17,20 @@ The VCB platform already has permanent player identity, account identity, evalua
 
 ## Current Status
 
-Planning only. No application code, models, migrations, services, views, templates, or tests have been implemented for Seasonal Participation V1.
+Phase 0 planning decisions are complete.
 
+Verified production state on July 15, 2026:
+
+```text
+Players: 0
+Coach profiles: 0
+Observations: 0
+```
+
+Because production is empty for Platform V1 roster/evaluation data, the migration strategy is schema-only first. No fake legacy season, player roster backfill, coach assignment backfill, or observation context backfill is planned for production.
+
+Next phase:
+
+- Phase 1 - Season And Roster Foundation.
+
+No application code, models, migrations, services, views, templates, URLs, settings, or tests have been implemented for Seasonal Participation V1 yet.
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
index aa2586b..26bcc6a 100644
--- a/docs/seasons/implementation/engineering/seasonal_participation_v1.md
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -1,18 +1,38 @@
 # Seasonal Participation V1 Engineering Plan
 
-Status: Planning only.
+Status: Phase 0 complete. Phase 1 is the next implementation phase.
 
 Created: 2026-07-15.
 
+## Verified Production State
+
+Production counts were checked in the production environment on July 15, 2026:
+
+```text
+Players: 0
+Coach profiles: 0
+Observations: 0
+```
+
+This means production currently has no Platform V1 player roster data, coach profile data, or Analytics evaluation data to migrate into seasonal records. Existing unrelated production data in legacy apps must remain untouched.
+
+Migration planning for Seasonal Participation V1 should therefore be empty-state-first:
+
+- no fake legacy season is required;
+- no player roster backfill is required;
+- no coach assignment backfill is required;
+- no observation season/team backfill is required;
+- new seasonal tables should be empty immediately after the schema migration in production.
+
 ## 1. Executive Summary
 
 The platform currently treats `players.Player` as the permanent player identity, but it still stores `team_name` and `division` directly on that permanent record. That is workable for a first import workflow, but it is not safe for long-term player development because players and coaches can move teams, divisions, or rosters across seasons.
 
 Seasonal Participation V1 should introduce season-aware roster context without recreating people. Permanent player identity remains stable in `players.Player`; permanent login identity remains stable in Django `User` and `accounts.AccountProfile`; evaluations remain owned by `analytics`. The new seasonal layer should record which players and coaches participated with which season-specific teams, and `analytics.Observation` should preserve the season/team/division context that existed when an evaluation was submitted.
 
-Recommended model direction:
+Settled model direction:
 
-- Add a small season/roster bounded context, preferably a new `seasons` app.
+- Add a new `seasons` app for the season/roster bounded context.
 - Add `Season` and `SeasonTeam`.
 - Add `PlayerRosterMembership` for player stints on season teams.
 - Add `CoachSeasonAssignment` for coach assignments on season teams.
@@ -52,7 +72,7 @@ Coach import currently creates or reuses coach accounts and stores `team` and `d
 - Support transfers and multi-team participation without overwriting history.
 - Keep existing Platform V1 behavior stable during the migration.
 - Keep subsystem ownership clear and avoid circular dependencies.
-- Provide a safe production migration path for existing data.
+- Provide a safe production migration path that recognizes current production is empty for Platform V1 roster/evaluation data.
 
 ## 4. Non-Goals
 
@@ -67,7 +87,8 @@ Seasonal Participation V1 should not implement:
 - draft workflow changes except future read-only context integration;
 - PDP migration;
 - historical season reconstruction beyond what current data supports;
-- deletion of existing `Player.team_name` or `Player.division` during the first implementation phase.
+- deletion of existing `Player.team_name` or `Player.division` during the first implementation phase;
+- legacy app data migration or cleanup.
 
 ## 5. Current Architecture Findings
 
@@ -122,10 +143,17 @@ Fields to consider:
 - `metadata`: JSON for import/source-specific context.
 - timestamps.
 
-Recommended uniqueness:
+Settled uniqueness and current-season behavior:
 
 - unique `key`.
-- optional constraint to allow only one `is_current=True`, if implemented.
+- allow exactly one current season.
+- use a conditional database constraint for `is_current=True` if it is safe on SQLite; otherwise enforce the rule through a transactional service and tests.
+
+Season naming:
+
+- `key` should be stable and unique, using values such as `2026-spring`, `2026-summer`, or `2027-spring`.
+- `name` should be human-friendly, using values such as `2026 Spring`, `2026 Summer`, or `2027 Spring`.
+- Do not hard-code a fixed list of season types.
 
 Archive behavior:
 
@@ -223,14 +251,14 @@ Important distinction:
 
 ## 7. Model Ownership
 
-Recommended ownership:
+Settled ownership:
 
 - New `seasons` app owns `Season`, `SeasonTeam`, `PlayerRosterMembership`, and `CoachSeasonAssignment`.
 - `players` continues to own `Player`, player matching, source identifiers, source rows, and player import orchestration.
 - `accounts` continues to own `User`, `AccountProfile`, `UserPlayerLink`, account provisioning, passwords, roles, and coach account creation/reuse.
 - `analytics` owns evaluation cycles and observations, including submitted evaluation context snapshots.
 
-Why a new `seasons` app is recommended:
+Why the new `seasons` app is used:
 
 - Seasonal participation is shared by players, accounts, analytics, and future roster/attendance/video work.
 - Putting coach assignments in `accounts` would couple account identity to roster history.
@@ -262,7 +290,7 @@ Recommended `EvaluationCycle` change:
 - Add nullable FK `season` to `Season`.
 - Keep `starts_on` and `ends_on` on `EvaluationCycle`.
 - Allow cycles without a season during compatibility migration.
-- Require a season for new production cycles after Phase 4.
+- Require a season in the application workflow for newly created production cycles once the seasonal foundation is implemented.
 
 SeasonTeam should be season-specific, not permanent:
 
@@ -272,7 +300,7 @@ SeasonTeam should be season-specific, not permanent:
 
 ## 9. Player Roster Membership Design
 
-One player may have multiple memberships in one season.
+Settled behavior: a player may have multiple memberships in one season.
 
 Supported cases:
 
@@ -283,6 +311,7 @@ Supported cases:
 
 Primary rules:
 
+- A player may have multiple memberships in one season.
 - A player should have at most one active primary membership per season.
 - A non-primary membership may be active at the same time.
 - Setting a new active primary membership should demote or end the prior active primary membership through a service, not direct model saves.
@@ -295,7 +324,7 @@ Transfer rules:
 
 ## 10. Coach Assignment Design
 
-One coach may have multiple assignments in one season.
+Settled behavior: one coach may have multiple assignments in one season.
 
 Supported cases:
 
@@ -304,6 +333,16 @@ Supported cases:
 - guest evaluator for a team;
 - staff member also coaching.
 
+Use this minimal controlled assignment-role list for V1:
+
+- Head Coach
+- Assistant Coach
+- Manager
+- Coordinator
+- Evaluator
+
+Future roles may be added through an explicit migration or controlled-choice update after confirming how they affect imports, filters, and permissions.
+
 Assignment role should be separate from account role:
 
 - `AccountProfile.role=coach` means the user is generally a coach in the platform.
@@ -319,7 +358,7 @@ Password behavior:
 
 Historical evaluations must retain the context that existed when submitted.
 
-Recommended design:
+Recommended future design:
 
 - Add nullable FK `player_roster_membership` to `Observation`.
 - Add nullable FK `season` to `Observation`.
@@ -336,7 +375,7 @@ Why FK plus snapshot is recommended:
 
 - FK provides structured filtering and drill-down while the referenced records exist.
 - Snapshot fields preserve display text if season/team names are later corrected.
-- Existing observations can be backfilled with best-known current fields without pretending to reconstruct unsupported history.
+- Existing observations in non-production environments can be backfilled with best-known current fields without pretending to reconstruct unsupported history.
 
 Submission behavior:
 
@@ -351,6 +390,7 @@ Existing draft or reopened observations:
 
 - Drafts may refresh context until submitted.
 - Reopened observations should preserve the original submitted context unless staff explicitly resubmits with a correction policy.
+- No production observation-context migration or backfill is required during the initial schema foundation because verified production has zero observations.
 
 ## 12. Player Import Design
 
@@ -460,26 +500,35 @@ Ambiguous imports:
 - If a player has multiple active memberships in the selected season and the CSV row lacks enough team/division information, mark the row for review.
 - Do not guess which membership should receive roster-specific updates.
 
-## 16. Existing Data Migration Strategy
+## 16. Production Migration Strategy
+
+Production is empty for Platform V1 roster/evaluation data.
 
-Do not fabricate historical seasons.
+Verified production counts on July 15, 2026:
 
-Recommended migration:
+```text
+Players: 0
+Coach profiles: 0
+Observations: 0
+```
 
-1. Create a default compatibility season, such as `Legacy / Pre-Season-Aware Data`, or a staff-approved current season such as `2026`.
-2. For every existing player with `team_name` or `division`, create/reuse a `SeasonTeam` in that season.
-3. Create one `PlayerRosterMembership` per player/team/division combination.
-4. Mark membership provenance as `legacy_player_fields`.
-5. For existing observations, set season/team/division context from the player's current legacy fields and mark metadata as `legacy_context_backfill`.
-6. Do not claim the backfilled context is historically exact.
-7. Leave observations with no player team/division as no-roster-context rather than inventing values.
+Production migration should therefore:
+
+1. Create schema only.
+2. Do not create a legacy season.
+3. Do not fabricate player roster memberships.
+4. Do not fabricate coach assignments.
+5. Do not backfill observations.
+6. Leave all new seasonal tables empty after migration.
+7. Preserve unrelated legacy app data untouched.
 
 Production safety:
 
-- Use idempotent data migrations or explicit management command with dry-run/review output.
-- Record counts before and after migration.
+- Run deployment verification before migration to confirm production still has zero Platform V1 players, coach profiles, and observations.
+- If unexpected Platform V1 rows exist in another environment, do not guess history. Use a defensive management command or explicit service-backed backfill plan that produces reviewable counts and metadata.
+- Keep defensive checks in deployment verification and service/management-command logic rather than fabricating records in the schema migration.
 - Back up the production database before applying migrations.
-- Run migration in staging or a production copy first.
+- Run the migration in staging or a production copy first.
 
 ## 17. Compatibility Strategy For Current Player Fields
 
@@ -487,7 +536,7 @@ Production safety:
 
 Recommended staged approach:
 
-- Phase 1: keep fields and populate membership records from them.
+- Phase 1: keep fields, add compatibility helpers, and do not populate production memberships from them because verified production has zero players.
 - Phase 2: stop treating them as authoritative in new imports; write seasonal membership records first.
 - Phase 2 compatibility: optionally update `Player.team_name` and `Player.division` from current active primary membership for existing UI compatibility.
 - Phase 4/5: update analytics filters, player search, metrics, and review views to use seasonal context.
@@ -576,21 +625,52 @@ Use `select_related()` for season/team/membership references in evaluation revie
 
 ### Phase 0 - Decisions And Compatibility
 
-- Finalize naming: app name, model names, status values, and assignment roles.
-- Decide active/current season behavior.
-- Decide whether `EvaluationCycle.season` is required for new cycles.
-- Decide legacy backfill season name.
-- Decide compatibility-write policy for `Player.team_name` and `Player.division`.
-- Document accepted transfer and multi-team behavior.
-
-### Phase 1 - Season, Team, And Player Membership Foundation
+Status: complete.
+
+Decisions recorded:
+
+- Use a new `seasons` app.
+- Keep `players.Player` as permanent player identity.
+- Keep Django `User` and `accounts.AccountProfile` as permanent coach/account identity.
+- Use stable season keys such as `2026-spring` and display names such as `2026 Spring`.
+- Allow exactly one current season.
+- Use season-specific teams only for V1; do not add a permanent `Team` model.
+- Allow multiple player memberships in one season.
+- Allow only one active primary membership per player per season.
+- Represent transfers as new memberships/stints rather than overwriting old memberships.
+- Allow one coach to have multiple assignments in one season.
+- Keep seasonal coach assignment role separate from permanent account role.
+- Use V1 assignment roles: Head Coach, Assistant Coach, Manager, Coordinator, Evaluator.
+- Treat `Season` and `EvaluationCycle` as distinct; a season has many evaluation cycles.
+- New production evaluation cycles should require a season once the foundation exists.
+- Keep `Player.team_name` and `Player.division` temporarily as compatibility/current-display fields.
+- Use an empty-production migration strategy because verified production has zero players, zero coach profiles, and zero observations.
+
+### Phase 1 - Season And Roster Foundation
 
 - Add `seasons` app and models.
-- Add services for season lookup, team lookup, player membership creation/update, current membership derivation, and legacy backfill helpers.
+- Add `Season`.
+- Add `SeasonTeam`.
+- Add `PlayerRosterMembership`.
+- Add `CoachSeasonAssignment`.
+- Add transactional domain services for season lookup, team lookup, player membership creation/update, coach assignment creation/update, current season handling, and current team/division compatibility.
 - Add admin configuration.
 - Add migrations.
-- Backfill legacy player team/division into memberships.
-- Keep existing import/UI behavior unchanged except compatibility display helpers if required.
+- Add comprehensive tests.
+- Add compatibility helpers for current team/division.
+- Register the app in settings.
+- Update architecture and user/admin documentation as needed.
+- Keep existing import/UI behavior unchanged except compatibility helpers if required.
+
+Phase 1 must not:
+
+- change player import UI;
+- change coach import UI;
+- attach evaluation context;
+- enforce team-based permissions;
+- add roster-management dashboards;
+- remove `Player.team_name` or `Player.division`;
+- implement Platform V2 summaries.
 
 ### Phase 2 - Season-Aware Player Import
 
@@ -614,7 +694,7 @@ Use `select_related()` for season/team/membership references in evaluation revie
 
 - Add `EvaluationCycle.season`.
 - Add observation season/team/membership references and snapshot fields.
-- Backfill existing observations with legacy context.
+- Do not backfill production observations unless new observations exist by then and a separate reviewed migration plan is approved.
 - Update observation creation/submission services to snapshot context at submission.
 - Update player-facing, coach-facing, and staff review read models to use snapshots.
 - Preserve submitted snapshots across later roster changes.
@@ -674,10 +754,10 @@ Analytics tests:
 
 Migration tests:
 
-- legacy player fields produce a compatibility season/team/membership;
-- existing observations receive backfilled context with metadata;
-- blank legacy fields do not produce fabricated teams;
-- migration is idempotent where practical.
+- schema migration leaves new seasonal tables empty in an empty production-equivalent database;
+- defensive verification detects unexpected existing Platform V1 rows before any optional backfill path;
+- blank legacy fields do not produce fabricated teams if a non-production backfill helper is later used;
+- migration and verification steps are idempotent where practical.
 
 Regression tests:
 
@@ -691,26 +771,26 @@ Regression tests:
 Deployment should be staged:
 
 1. Deploy schema-only season foundation with compatibility reads intact.
-2. Run legacy backfill in staging or a production database copy.
-3. Verify counts and spot-check player histories.
+2. Verify production still has zero Platform V1 players, coach profiles, and observations before applying schema.
+3. Confirm new seasonal tables are empty after migration.
 4. Deploy player import changes after foundation is stable.
 5. Deploy coach assignment changes after player seasonal model is proven.
-6. Deploy evaluation context changes with a tested observation backfill.
+6. Deploy evaluation context changes with snapshot behavior for new submissions.
 7. Update UI/read models after data is available.
 
 Rollback considerations:
 
 - Do not remove `Player.team_name` or `Player.division` during early phases.
 - Do not make new non-null FKs on existing observations in the first migration.
-- Use nullable references and snapshot fields while backfill is validated.
+- Use nullable references and snapshot fields while context behavior is validated.
 - Keep compatibility display paths until a full production cycle has passed.
 - Back up the database before data migrations.
 - Avoid irreversible destructive migrations.
 
 ## 25. Risks
 
-- Existing production data may not contain enough information to reconstruct true historical season/team context.
-- Backfilled evaluations could be mistaken for exact historical truth unless metadata and documentation are clear.
+- Another environment may contain Platform V1 data even though production is empty; any optional backfill path must be explicit and reviewable.
+- Future production data could be created between planning and Phase 1 deployment; pre-migration verification must re-check counts.
 - Primary membership constraints can be difficult to enforce perfectly on all databases with nullable dates.
 - Coach import currently resets reused coach passwords; this must change before season-aware reimports.
 - Existing analytics filters and metrics currently read from `Player.team_name` and `Player.division`.
@@ -720,32 +800,20 @@ Rollback considerations:
 
 ## 26. Open Questions
 
-- What is the official season naming convention for VCB?
-- Should there be exactly one current season?
-- Should evaluation cycles be required to have a season after migration?
-- What legacy season should existing production data use?
-- Should current `Player.team_name` and `division` be maintained as cached compatibility fields, or only deprecated and left untouched?
 - What roster statuses are needed for V1?
-- What coach assignment roles are needed for V1?
 - Should staff be able to manually edit memberships and assignments in admin only, or through first-class UI?
 - How should imported transfer rows explicitly signal transfer versus concurrent membership?
 - Should player peer-evaluation scope eventually be limited to same season/team?
+- Should the exact one-current-season rule be database-enforced on SQLite, service-enforced, or both?
+- Should compatibility writes to `Player.team_name` and `Player.division` happen automatically when primary membership changes, or only during import/service workflows?
 
 ## 27. Recommended First Implementation Phase
 
-Start with Phase 0 - Decisions And Compatibility.
+Start with Phase 1 - Season And Roster Foundation.
 
-Do not begin models or migrations until the following are explicitly decided:
+Phase 0 decisions are complete. Phase 1 should add the model foundation, transactional domain services, admin support, migrations, tests, and compatibility helpers without changing player import UI, coach import UI, evaluation context, team-based permissions, roster dashboards, or Platform V2 summaries.
 
-- season naming and current-season policy;
-- legacy backfill season;
-- compatibility policy for `Player.team_name` and `Player.division`;
-- required relationship between `EvaluationCycle` and `Season`;
-- primary membership rules;
-- coach assignment roles;
-- whether a new `seasons` app is accepted as the shared owner.
-
-After those decisions, Phase 1 should add the model foundation and legacy backfill without changing user-facing import or evaluation workflows.
+Before implementing Phase 1, re-run the production-readiness verification counts so the migration remains empty-state-first.
 
 ## 28. Acceptance Criteria
 
@@ -766,4 +834,3 @@ The Seasonal Participation V1 plan is acceptable when:
 - migration phases are safe and reversible where practical;
 - tests and deployment steps are defined;
 - no application code changed during this planning task.
-
```
