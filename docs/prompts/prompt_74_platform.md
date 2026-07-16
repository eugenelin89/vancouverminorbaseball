# Prompt 74 - Platform

App/subsystem: platform

Work commit: `f0ea0fe`

Terminal state: `PASS`

## User Prompt

```text
Implement Seasonal Participation V1 Phase 1 only: Season and Roster Foundation.

Use continuous loop engineering.

Continue until the Phase 1 scope is production-ready, fully reviewed, documented, tested, committed, pushed, and the working tree is clean.

Do not start Phase 2 or later work.

==================================================
Current State
=============

Seasonal Participation V1 Phase 0 is complete.

Verified production counts on July 15, 2026:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

Production therefore has no Platform V1 player roster, coach assignment, or Analytics observation data requiring historical backfill.

The migration strategy is empty-state-first:

* schema only;
* no fake legacy season;
* no player roster backfill;
* no coach assignment backfill;
* no observation context backfill;
* existing unrelated legacy application data must remain untouched.

==================================================
Phase 1 Objective
=================

Create the seasonal participation foundation.

Implement:

* new `seasons` Django app;
* `Season`;
* `SeasonTeam`;
* `PlayerRosterMembership`;
* `CoachSeasonAssignment`;
* transactional domain services;
* current-season handling;
* current player membership helpers;
* compatibility helpers for `Player.team_name` and `Player.division`;
* Django admin support;
* migrations;
* comprehensive tests;
* settings registration;
* architecture and administrator documentation updates.

Do not change user-facing import or evaluation workflows yet.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete Phase 1 implementation, review, documentation, or verification work remains.

PASS

All Phase 1 acceptance criteria are satisfied, verification passes, commits are pushed, and the working tree is clean.

BLOCKED

A necessary decision requires unresolved product direction, destructive migration, external infrastructure, or architecture expansion outside Phase 1.

NO_PROGRESS

Two consecutive full loops fail to make meaningful progress toward an unsatisfied acceptance criterion.

Do not continue through speculative or cosmetic refactoring.

==================================================
Established Loop Workflow
=========================

Every loop must complete the full repository workflow.

Each loop must:

1. Reconcile the committed repository state.
2. Read `AGENTS.md` and current seasonal planning documents.
3. Read the previous loop prompt and result.
4. Confirm the working tree is clean.
5. Inspect the complete affected workflow.
6. Identify concrete incomplete acceptance criteria or verified issues.
7. Create the next prompt archive before implementation according to `AGENTS.md`.
8. Implement only the selected Phase 1 work.
9. Add or update focused tests.
10. Run focused verification.
11. Perform senior-engineer self-review.
12. Fix every verified issue.
13. Update relevant documentation.
14. Run the complete verification suite.
15. Commit implementation, tests, migrations, and documentation.
16. Finalize the prompt archive with commit hash, review findings, test results, and terminal state.
17. Commit the prompt archive separately.
18. Push both commits.
19. Re-read the committed diff.
20. Confirm the working tree is clean.
21. Reassess every Phase 1 acceptance criterion.
22. Choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS.
23. If CONTINUE, begin the next loop without requesting confirmation.

Each loop must create:

1. one implementation/review/documentation commit;
2. one prompt archive commit.

Do not combine multiple loops into one commit.

==================================================
Required Repository Review
==========================

Before implementation, read:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`
* current prompt archives related to players, accounts, evaluations, and seasonal planning

Inspect:

* `vancouverminor/settings.py`
* `vancouverminor/urls.py`
* `players/models.py`
* `players/admin.py`
* `players/services/`
* `players/tests.py`
* `accounts/models.py`
* `accounts/admin.py`
* `accounts/services/`
* `accounts/tests.py`
* `analytics/models.py`
* existing migration style in all apps
* current timestamp/metadata patterns
* current service and dataclass conventions

==================================================
Model Ownership
===============

Create a new Django app:

```text
seasons
```

It owns:

* `Season`
* `SeasonTeam`
* `PlayerRosterMembership`
* `CoachSeasonAssignment`

Ownership boundaries:

* `players.Player` remains permanent player identity.
* Django `User` and `accounts.AccountProfile` remain permanent account identity.
* `seasons` owns seasonal roster participation.
* `players` will later orchestrate season-aware player imports through season services.
* `accounts` will later orchestrate coach seasonal assignments through season services.
* `analytics` will later reference or snapshot seasonal context.
* `seasons` must not depend on Analytics business services.
* Views and templates must not create seasonal records directly.

==================================================
Season Model
============

Implement `Season`.

Required behavior:

* stable unique key;
* human-friendly name;
* optional `starts_on`;
* optional `ends_on`;
* `is_active`;
* `is_current`;
* metadata;
* created/updated timestamps.

Examples:

```text
key: 2026-spring
name: 2026 Spring
```

Do not hard-code season types.

Validation requirements:

* key is normalized and nonblank;
* name is nonblank;
* if both dates exist, `ends_on` must not precede `starts_on`;
* historical seasons should be deactivated rather than deleted where practical.

Current-season requirement:

* exactly zero or one current season may exist before initial setup;
* once a season is made current, no second current season may remain;
* changing the current season must be atomic.

Prefer:

* a conditional database unique constraint on `is_current=True` if Django 4.2 and SQLite support it safely;
* transactional service enforcement as the authoritative workflow;
* model validation and tests as additional protection.

Do not require the migration to create a current season automatically.

==================================================
SeasonTeam Model
================

Implement `SeasonTeam`.

Required fields and behavior:

* FK to `Season`;
* team name;
* division;
* normalized team name;
* normalized division;
* optional external source;
* optional external identifier;
* `is_active`;
* metadata;
* timestamps.

Season teams are season-specific.

For example:

```text
2026 Spring / 13U Dodgers
2027 Spring / 13U Dodgers
```

must be different records.

Normalization:

* trim surrounding whitespace;
* use deterministic case-insensitive normalization;
* collapse repeated internal whitespace where practical;
* keep display values separately from normalized values.

Uniqueness:

* unique normalized `(season, division, team name)`;
* when external source and identifier are populated, prevent unsafe duplicate identifiers within one season;
* blank external identifiers must not cause unrelated teams to conflict.

Do not introduce a permanent Team model.

==================================================
PlayerRosterMembership Model
============================

Implement `PlayerRosterMembership`.

Required fields:

* FK to `players.Player`;
* FK to `SeasonTeam`;
* controlled roster status;
* optional jersey number;
* `is_primary`;
* `is_active`;
* optional `starts_on`;
* optional `ends_on`;
* optional source;
* optional source identifier;
* optional FK to `players.PlayerImportBatch` if consistent with dependency direction;
* optional FK to `players.PlayerSourceRow` only if repository inspection confirms it is useful and safe;
* metadata;
* timestamps.

Settle and implement a minimal roster-status list.

Recommended V1 values:

* Active
* Inactive
* Transferred
* Guest
* Removed

Use internal stable keys and friendly labels.

Validation:

* membership season is derived through `season_team.season`;
* if both dates exist, end date must not precede start date;
* primary membership should normally be active;
* inactive or ended memberships remain historical;
* deleting a referenced player or team should follow existing ownership and retention conventions.

Multiplicity:

* allow multiple memberships for one player in one season;
* allow multiple active non-primary memberships;
* allow only one active primary membership per player per season.

The primary rule must be protected through:

* transactional services;
* tests;
* a database constraint where safe and practical.

Do not prohibit legitimate transfers or concurrent participation.

==================================================
CoachSeasonAssignment Model
===========================

Implement `CoachSeasonAssignment`.

Required fields:

* FK to Django `User`;
* FK to `SeasonTeam`;
* controlled assignment role;
* `is_primary`;
* `is_active`;
* optional `starts_on`;
* optional `ends_on`;
* optional source;
* optional source identifier;
* metadata;
* timestamps.

Assignment roles:

* Head Coach
* Assistant Coach
* Manager
* Coordinator
* Evaluator

Use stable internal keys and friendly labels.

Requirements:

* one user may have multiple assignments in a season;
* one team may have multiple coaches;
* account role remains separate from assignment role;
* assignment creation must not set Django `is_staff`;
* assignment creation must not set Django `is_superuser`;
* assignment creation must not reset passwords;
* assignment creation must not silently change `AccountProfile.role`;
* duplicate active assignments for the same user, team, and assignment role should be prevented.

Allow one active primary assignment per user per season where practical.

==================================================
Domain Services
===============

Create a focused service layer in the `seasons` app.

Likely service modules may include:

```text
seasons/services/season_service.py
seasons/services/team_service.py
seasons/services/membership_service.py
seasons/services/coach_assignment_service.py
```

Use fewer modules if that better matches current repository style.

Required operations:

## Season Services

* create season;
* update season;
* set current season atomically;
* get current season;
* activate/deactivate season;
* validate date ranges.

## Team Services

* normalize team/division values;
* create or reuse a season team;
* safely update display metadata;
* resolve by external identifier when available;
* reject ambiguous conflicts.

## Player Membership Services

* create membership;
* update membership;
* set active primary membership atomically;
* deactivate/end membership;
* transfer player by creating a new membership rather than rewriting the old one;
* get memberships for a player and season;
* get current/primary membership;
* derive current team and division.

## Coach Assignment Services

* create assignment;
* update assignment;
* set primary assignment;
* deactivate/end assignment;
* get assignments by user, season, or team;
* ensure no account-role or password side effects.

Use `transaction.atomic` and `select_for_update` where state transitions must be serialized.

Do not use signals.

==================================================
Compatibility Helpers
=====================

Keep:

* `Player.team_name`
* `Player.division`

These remain temporary compatibility/current-display fields.

Implement explicit helper/service behavior to synchronize them from the player’s active primary membership.

Requirements:

* seasonal membership is authoritative;
* compatibility fields may be updated when a workflow explicitly changes the active primary membership;
* do not place synchronization in model signals;
* do not make arbitrary direct membership saves silently rewrite Player;
* provide an explicit service such as:

  * `sync_player_current_team_fields(player)`;
  * or equivalent repository-consistent naming.

If no active primary membership exists:

* choose a clear policy and test it;
* recommended default is to clear compatibility fields only when the service is explicitly called for that purpose;
* do not erase fields incidentally during unrelated reads.

Document that these fields are temporary and nonhistorical.

==================================================
Admin
=====

Register all Phase 1 models in Django admin.

Admin requirements:

* useful list columns;
* filters by season, division, status, activity, and primary state;
* search for season key/name, team name, player name, username/email;
* autocomplete fields where helpful;
* timestamps read-only;
* metadata excluded or read-only according to current project conventions.

Admin must not bypass important domain invariants.

Where admin direct edits could violate current-season or primary-membership rules:

* use validation;
* override admin save behavior carefully;
* or restrict fields and require service-based actions.

Do not build first-class roster-management application pages in Phase 1.

==================================================
Migrations
==========

Create normal Django migrations for the new app.

Production strategy:

* schema only;
* no data migrations;
* no default season;
* no fake legacy records;
* no player backfill;
* no coach backfill;
* no Analytics backfill.

All new tables should remain empty immediately after production migration.

Migrations must be safe on SQLite and Django 4.2.

Before final PASS, review:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py migrate --plan
```

Also confirm migration application succeeds through the test suite.

==================================================
Defensive Empty-State Verification
==================================

Do not encode production row-count assumptions into the schema migration.

Document a deployment verification step that rechecks:

```text
Players
Coach profiles
Observations
```

before production migration.

If unexpected rows exist at deployment time:

* deployment should stop;
* no automatic fabricated backfill should run;
* a separate reviewed migration/backfill plan should be created.

Update deployment or seasonal implementation documentation with this narrow verification requirement.

Do not modify deployment scripts.

==================================================
Settings And App Registration
=============================

Register the `seasons` app in `INSTALLED_APPS`.

Follow current settings style.

Do not change unrelated settings.

Do not add routes unless the app needs no public URLs in Phase 1.

A URL module is not required unless repository conventions demand it.

==================================================
Documentation
=============

Update:

* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md` only if administrators need to know that the foundation exists but has no user-facing workflow
* deployment documentation only for the empty-state verification requirement, if appropriate

Document:

* Phase 1 implementation status;
* model ownership;
* roster statuses;
* assignment roles;
* current-season rule;
* primary membership rule;
* compatibility-field behavior;
* empty-state migration behavior;
* absence of import UI changes;
* absence of evaluation-context changes;
* next phase: season-aware player import.

Do not describe future import behavior as already implemented.

==================================================
Phase 1 Non-Goals
=================

Do not implement:

* player import season selection;
* player import membership creation;
* coach import season selection;
* coach assignment creation from imports;
* changes to coach password behavior;
* `EvaluationCycle.season`;
* observation season/team/membership fields;
* evaluation snapshots;
* team-based evaluation permissions;
* peer scope restrictions;
* roster-management dashboards;
* player season-history pages;
* coach assignment application pages;
* Platform V2 summaries;
* charts;
* APIs;
* JavaScript;
* notifications;
* exports;
* deletion of `Player.team_name`;
* deletion of `Player.division`;
* migration of PDP or other legacy data.

==================================================
Required Test Coverage
======================

Add comprehensive tests.

## Season Tests

* create valid season;
* unique key;
* date validation;
* zero current seasons allowed before setup;
* set first current season;
* changing current season clears previous current;
* concurrent/service path preserves one current season;
* inactive historical seasons remain queryable.

## SeasonTeam Tests

* create team in season;
* same normalized team/division reused or rejected according to service contract;
* same team name in different seasons allowed;
* normalization handles case and whitespace;
* external identifiers are scoped safely;
* blank identifiers do not conflict.

## Player Membership Tests

* player may join one team;
* same player may join different seasons;
* same player may have multiple memberships in one season;
* only one active primary membership per player/season;
* non-primary concurrent memberships allowed;
* transfer creates new membership;
* old membership history remains;
* date validation;
* current membership derivation;
* compatibility field synchronization;
* no implicit compatibility rewrite from unrelated reads.

## Coach Assignment Tests

* create assignment;
* multiple assignments in a season allowed;
* multiple coaches on one team allowed;
* duplicate active user/team/role rejected;
* only one active primary assignment per user/season if implemented;
* assignment does not change account role;
* assignment does not grant staff;
* assignment does not grant superuser;
* assignment does not change password;
* date validation.

## Admin Tests

* models registered;
* staff/superuser access behaves according to existing admin rules;
* searchable/autocomplete configuration does not fail;
* invalid current/primary state cannot be created through supported admin paths.

## Migration And Regression Tests

* migrations apply to empty database;
* new tables begin empty;
* existing players/accounts/analytics tests continue passing;
* no import workflow behavior changes;
* no evaluation workflow behavior changes;
* no account password behavior changes.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
git diff --check
```

If another app changes, run its focused tests.

==================================================
Full Verification Every Loop
============================

Every loop must run:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py migrate --plan
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics
DJANGO_SECRET_KEY=test-only-not-production python manage.py test drafts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test pdp
DJANGO_SECRET_KEY=test-only-not-production python manage.py test
git diff --check
```

All commands must pass before an implementation commit.

==================================================
Self-Review Every Loop
======================

Review each diff as a senior Django engineer.

Check:

* bounded-context ownership;
* dependency direction;
* SQLite compatibility;
* conditional constraints;
* uniqueness rules;
* race conditions;
* transaction boundaries;
* use of `select_for_update`;
* validation gaps;
* primary membership invariants;
* current-season invariants;
* account-role side effects;
* password side effects;
* compatibility-field side effects;
* unsafe deletion behavior;
* admin bypasses;
* migration safety;
* N+1 query risks;
* naming consistency;
* dead code;
* unused imports;
* stale documentation;
* accidental Phase 2 work.

Fix every verified issue before committing.

==================================================
Phase 1 Acceptance Criteria
===========================

Do not declare PASS until all criteria are satisfied.

A. App And Ownership

* `seasons` app exists and is registered;
* ownership boundaries match the plan;
* no circular business-service dependencies exist.

B. Season

* season key/name/date behavior implemented;
* current-season transition is atomic;
* no more than one current season exists;
* no default season is fabricated.

C. Season Team

* teams are season-specific;
* normalization is deterministic;
* uniqueness is safe;
* same team name may exist in different seasons.

D. Player Membership

* permanent player reused;
* multiple memberships per season allowed;
* one active primary per season enforced;
* transfers preserve history;
* current membership can be derived safely.

E. Coach Assignment

* permanent user reused;
* multiple assignments allowed;
* assignment role separate from account role;
* no password or privilege side effects;
* duplicate rules enforced.

F. Compatibility

* current Player team/division compatibility helpers exist;
* seasonal membership is authoritative;
* no signal-based synchronization;
* no historical claims are made from compatibility fields.

G. Migration

* schema-only migration;
* no data fabrication;
* new tables empty on empty database;
* SQLite migration plan reviewed.

H. Admin

* models are manageable safely through admin;
* important invariants cannot be trivially bypassed;
* search/filter behavior is useful.

I. Tests

* focused tests pass;
* full suite passes;
* regression behavior remains unchanged.

J. Documentation

* Phase 1 marked complete only after implementation passes;
* next phase is clearly Phase 2;
* imports and evaluations are still documented as not season-aware yet;
* empty-state production strategy is documented.

K. Git

* implementation commit exists;
* prompt archive commit exists;
* both are pushed;
* working tree is clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally implement the complete narrow Phase 1 foundation:

1. create and register `seasons` app;
2. implement models and migrations;
3. implement domain services;
4. implement compatibility helpers;
5. register admin;
6. add comprehensive tests;
7. update documentation;
8. run full verification;
9. commit, archive, push, and reassess.

If review finds material defects, continue into further loops.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* satisfies an unsatisfied acceptance criterion;
* fixes a verified defect;
* strengthens migration safety;
* closes a transaction or constraint gap;
* prevents privilege/password side effects;
* adds missing regression proof;
* corrects material documentation drift.

Formatting-only work does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* administrator creating seasons;
* registrar planning future imports;
* coach with multiple assignments;
* player with multiple roster stints;
* data architect reviewing history;
* security reviewer checking privilege separation;
* release engineer reviewing SQLite migration safety.

Confirm:

* Phase 1 is a stable foundation;
* no Phase 2 import workflow was accidentally implemented;
* no evaluation context was added;
* production migration is additive and empty-state-first.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before implementation;
2. commit implementation, migration, tests, and documentation;
3. update the prompt archive with:

   * implementation commit hash;
   * files changed;
   * migration summary;
   * issues found;
   * fixes applied;
   * verification results;
   * remaining criteria;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested implementation commit message:

```text
Implement season and roster foundation
```

Use a different concise message for later review loops if needed.

==================================================
Final Report
============

Report:

* terminal state;
* number of loops;
* objective of each loop;
* files created;
* files modified;
* models added;
* services added;
* constraints and transaction rules;
* roster-status decision;
* coach-assignment-role decision;
* current-season behavior;
* primary membership behavior;
* compatibility-field behavior;
* migration summary;
* empty-state verification strategy;
* admin behavior;
* tests added;
* focused verification results;
* full verification results;
* documentation updates;
* deferred Phase 2+ work;
* commits;
* push results;
* confirmation that the working tree is clean.
```

## Implementation Summary

- Implemented Seasonal Participation V1 Phase 1 only.
- Added the `seasons` Django app with schema-only initial migration.
- Added `Season`, `SeasonTeam`, `PlayerRosterMembership`, and `CoachSeasonAssignment`.
- Added transactional services for current season, teams, player memberships, coach assignments, and Player current team/division compatibility fields.
- Added Django admin registration and comprehensive tests.
- Registered `seasons` in `INSTALLED_APPS`.
- Updated architecture, seasonal docs, deployment runbook, and user manual.

## Files Changed

- `vancouverminor/settings.py`
- `seasons/`
- `docs/ARCHITECTURE.md`
- `docs/USER_MANUAL.md`
- `docs/deployment/RUNBOOK.md`
- `docs/seasons/README.md`
- `docs/seasons/implementation/engineering/seasonal_participation_v1.md`

## Migration Summary

- Added `seasons/migrations/0001_initial.py`.
- Migration is schema-only.
- No default season, legacy season, player roster backfill, coach assignment backfill, or observation context backfill is created.

## Review Findings And Fixes

- Fixed season key normalization so it runs before `SlugField` validation.
- Adjusted duplicate-current-season test expectations to match model validation on the supported save path.
- Fixed `update_membership(..., is_primary=False)` and `update_assignment(..., is_primary=False)` so primary flags are actually unset.
- Added regression tests for the primary-unset service paths.

## Verification Results

Passed:

```text
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py migrate --plan
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics
DJANGO_SECRET_KEY=test-only-not-production python manage.py test drafts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test pdp
DJANGO_SECRET_KEY=test-only-not-production python manage.py test
git diff --check
```

Full suite result: 427 tests passed.

## Remaining Criteria

- Phase 1 criteria are satisfied.
- Phase 2 remains deferred: season-aware player import.
- No Phase 2 import workflow, coach import workflow, or Analytics evaluation context was implemented.

## Work Commit Diff

```diff
commit f0ea0fe1e039c2af377c20348114d11a55e2cdd3
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 15 18:53:32 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 15 18:53:32 2026 -0700

    Implement season and roster foundation

diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 2592025..46133de 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -171,6 +171,44 @@ Documentation:
 - [Account Management V1 Summary](account_management/V1_SUMMARY.md)
 - [Account Management V1 Engineering Plan](account_management/implementation/account_management_v1.md)
 
+### Seasons
+
+Purpose:
+
+`seasons` owns season-aware roster participation.
+
+Responsibilities:
+
+- seasons and current-season state
+- season-specific teams
+- player roster memberships
+- coach season assignments
+- compatibility helpers for current player team/division display
+
+What it owns:
+
+- seasonal participation records
+- current-season transition services
+- primary roster membership and primary coach assignment services
+
+What it must not own:
+
+- permanent player identity
+- Django login identity
+- account roles or permissions
+- player import parsing/matching
+- coach account provisioning
+- Analytics observations or evaluation context snapshots
+
+Current status:
+
+Seasonal Participation V1 Phase 1 foundation is implemented. The schema, services, admin registration, and tests exist, but player imports, coach imports, and evaluations are not season-aware yet.
+
+Documentation:
+
+- [Seasons README](seasons/README.md)
+- [Seasonal Participation V1 Engineering Plan](seasons/implementation/engineering/seasonal_participation_v1.md)
+
 ### Drafts
 
 Purpose:
@@ -229,6 +267,10 @@ Documentation:
 | Player source identifiers | Players |
 | Player imports | Players |
 | Player matching | Players |
+| Seasons | Seasons |
+| Season-specific teams | Seasons |
+| Player roster memberships | Seasons |
+| Coach season assignments | Seasons |
 | Authentication | Accounts |
 | Login/logout/password change | Accounts |
 | Account metadata | Accounts |
@@ -257,9 +299,13 @@ Documentation:
 
 Analytics ─────► Players
 Analytics ─────► Accounts
+Analytics ─────► Seasons
 
 Drafts ────────► Players
 
+Players ───────► Seasons
+Accounts ──────► Seasons
+
 PDP (legacy, transitionary)
 ```
 
@@ -269,6 +315,7 @@ Dependency guidance:
 - Do not directly manipulate another subsystem's models when an owning service exists.
 - `players` owns player identity and imports.
 - `accounts` owns account identity and user-player relationships.
+- `seasons` owns season-specific teams, player roster memberships, and coach assignments.
 - `analytics` may consume `players` and `accounts`, but must not own their business rules.
 - `drafts` may reference player identity, but draft workflow remains in `drafts`.
 - PDP is legacy and should not become the dependency target for new platform work.
@@ -280,6 +327,7 @@ Dependency guidance:
 | Players | V1 | Complete |
 | Analytics | V1 | Complete |
 | Account Management | V1 | Complete / Frozen |
+| Seasons | V1 Phase 1 | Foundation complete |
 | Drafts | Active | Active development |
 | PDP | Legacy | Transitionary |
 | LeagueHub | Planned | Planned |
@@ -294,6 +342,7 @@ The platform currently has:
 - production-ready Analytics V1 workflow
 - production-ready Account Management V1 foundation
 - production-ready staff-facing Account Operations
+- season-aware roster participation foundation
 - account provisioning from player imports
 - forced password-change account flow
 - staff-only Analytics command center and reporting tables
@@ -310,6 +359,7 @@ Likely future areas:
 
 - Account Management V2
 - Analytics V2
+- Seasonal Participation Phase 2
 - Drafts expansion
 - LeagueHub
 - Video
@@ -339,6 +389,11 @@ Analytics:
 - [Analytics Implementation Status](analytics/implementation/STATUS.md)
 - [Analytics Local Development](analytics/local_development.md)
 
+Seasons:
+
+- [Seasons README](seasons/README.md)
+- [Seasonal Participation V1 Engineering Plan](seasons/implementation/engineering/seasonal_participation_v1.md)
+
 Prompts and archives:
 
 - [Prompt Archive](prompts/README.md)
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 88bab1e..4a1cc37 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -7,6 +7,7 @@ The platform helps Vancouver Community Baseball manage:
 - player records
 - account access
 - player and coach imports
+- season and roster foundations
 - evaluations
 - player history
 - draft preparation
@@ -14,6 +15,8 @@ The platform helps Vancouver Community Baseball manage:
 
 This is a user manual, not a technical deployment guide. Deployment information lives in [docs/deployment/](deployment/README.md).
 
+Season-aware roster foundations now exist in the system, but normal player import, coach import, and evaluation pages are not season-aware yet. Staff should continue using the current import and evaluation workflows until the next seasonal import phase is implemented.
+
 ## Start Here
 
 ### Sign In
diff --git a/docs/deployment/RUNBOOK.md b/docs/deployment/RUNBOOK.md
index f2f9e98..c6442cf 100644
--- a/docs/deployment/RUNBOOK.md
+++ b/docs/deployment/RUNBOOK.md
@@ -96,6 +96,18 @@ Review planned migrations:
 python manage.py migrate --plan
 ```
 
+### Seasonal Participation Empty-State Check
+
+Before applying the initial `seasons` app migration, verify production still has no Platform V1 roster/evaluation data requiring seasonal backfill:
+
+```text
+Players: 0
+Coach profiles: 0
+Observations: 0
+```
+
+If these counts are no longer zero, stop the deployment and create a reviewed migration/backfill plan. Do not fabricate legacy seasons, player roster memberships, coach assignments, or observation context during the schema migration.
+
 Apply migrations:
 
 ```bash
diff --git a/docs/seasons/README.md b/docs/seasons/README.md
index d71704a..08e2251 100644
--- a/docs/seasons/README.md
+++ b/docs/seasons/README.md
@@ -19,6 +19,8 @@ The VCB platform already has permanent player identity, account identity, evalua
 
 Phase 0 planning decisions are complete.
 
+Phase 1 - Season And Roster Foundation is implemented.
+
 Verified production state on July 15, 2026:
 
 ```text
@@ -29,8 +31,26 @@ Observations: 0
 
 Because production is empty for Platform V1 roster/evaluation data, the migration strategy is schema-only first. No fake legacy season, player roster backfill, coach assignment backfill, or observation context backfill is planned for production.
 
+Implemented foundation:
+
+- `Season`
+- `SeasonTeam`
+- `PlayerRosterMembership`
+- `CoachSeasonAssignment`
+- transactional domain services
+- Django admin registration
+- schema-only migration
+- tests for current-season, roster membership, coach assignment, compatibility, and admin behavior
+
+Current limitations:
+
+- player import does not require or create seasonal memberships yet;
+- coach import does not require or create seasonal assignments yet;
+- evaluations do not yet store season/team/membership context;
+- there are no first-class roster-management pages yet.
+
 Next phase:
 
-- Phase 1 - Season And Roster Foundation.
+- Phase 2 - Season-Aware Player Import.
 
-No application code, models, migrations, services, views, templates, URLs, settings, or tests have been implemented for Seasonal Participation V1 yet.
+No user-facing import or evaluation workflow changes were made in Phase 1.
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
index 26bcc6a..baab82b 100644
--- a/docs/seasons/implementation/engineering/seasonal_participation_v1.md
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -1,6 +1,6 @@
 # Seasonal Participation V1 Engineering Plan
 
-Status: Phase 0 complete. Phase 1 is the next implementation phase.
+Status: Phase 1 foundation complete. Phase 2 is the next implementation phase.
 
 Created: 2026-07-15.
 
@@ -648,19 +648,23 @@ Decisions recorded:
 
 ### Phase 1 - Season And Roster Foundation
 
-- Add `seasons` app and models.
-- Add `Season`.
-- Add `SeasonTeam`.
-- Add `PlayerRosterMembership`.
-- Add `CoachSeasonAssignment`.
-- Add transactional domain services for season lookup, team lookup, player membership creation/update, coach assignment creation/update, current season handling, and current team/division compatibility.
-- Add admin configuration.
-- Add migrations.
-- Add comprehensive tests.
-- Add compatibility helpers for current team/division.
-- Register the app in settings.
-- Update architecture and user/admin documentation as needed.
-- Keep existing import/UI behavior unchanged except compatibility helpers if required.
+Status: complete.
+
+Completed:
+
+- Added `seasons` app and models.
+- Added `Season`.
+- Added `SeasonTeam`.
+- Added `PlayerRosterMembership`.
+- Added `CoachSeasonAssignment`.
+- Added transactional domain services for season lookup, team lookup, player membership creation/update, coach assignment creation/update, current season handling, and current team/division compatibility.
+- Added admin configuration.
+- Added schema-only migration.
+- Added comprehensive tests.
+- Added compatibility helpers for current team/division.
+- Registered the app in settings.
+- Updated architecture, seasonal, user/admin, and deployment documentation as needed.
+- Kept existing import/UI behavior unchanged except compatibility helpers.
 
 Phase 1 must not:
 
@@ -809,11 +813,11 @@ Rollback considerations:
 
 ## 27. Recommended First Implementation Phase
 
-Start with Phase 1 - Season And Roster Foundation.
+Start with Phase 2 - Season-Aware Player Import.
 
-Phase 0 decisions are complete. Phase 1 should add the model foundation, transactional domain services, admin support, migrations, tests, and compatibility helpers without changing player import UI, coach import UI, evaluation context, team-based permissions, roster dashboards, or Platform V2 summaries.
+Phase 1 decisions and implementation are complete. Phase 2 should update player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services.
 
-Before implementing Phase 1, re-run the production-readiness verification counts so the migration remains empty-state-first.
+Before implementing Phase 2, verify that Phase 1 production migration completed with empty seasonal tables and no fabricated history.
 
 ## 28. Acceptance Criteria
 
diff --git a/seasons/__init__.py b/seasons/__init__.py
new file mode 100644
index 0000000..8b13789
--- /dev/null
+++ b/seasons/__init__.py
@@ -0,0 +1 @@
+
diff --git a/seasons/admin.py b/seasons/admin.py
new file mode 100644
index 0000000..328a0e6
--- /dev/null
+++ b/seasons/admin.py
@@ -0,0 +1,61 @@
+from django.contrib import admin
+
+from seasons.models import CoachSeasonAssignment, PlayerRosterMembership, Season, SeasonTeam
+
+
+class TimeStampedAdmin(admin.ModelAdmin):
+    readonly_fields = ("created_at", "updated_at")
+
+
+@admin.register(Season)
+class SeasonAdmin(TimeStampedAdmin):
+    list_display = ("name", "key", "starts_on", "ends_on", "is_current", "is_active", "updated_at")
+    list_filter = ("is_current", "is_active", "starts_on")
+    search_fields = ("key", "name")
+    readonly_fields = TimeStampedAdmin.readonly_fields
+
+
+@admin.register(SeasonTeam)
+class SeasonTeamAdmin(TimeStampedAdmin):
+    list_display = ("season", "division", "name", "external_source", "external_identifier", "is_active", "updated_at")
+    list_filter = ("season", "division", "is_active")
+    search_fields = ("name", "division", "normalized_name", "normalized_division", "external_identifier")
+    autocomplete_fields = ("season",)
+    readonly_fields = TimeStampedAdmin.readonly_fields + ("normalized_name", "normalized_division")
+    exclude = ("metadata",)
+
+
+@admin.register(PlayerRosterMembership)
+class PlayerRosterMembershipAdmin(TimeStampedAdmin):
+    list_display = ("player", "season_team", "status", "jersey_number", "is_primary", "is_active", "starts_on", "ends_on")
+    list_filter = ("season_team__season", "season_team__division", "status", "is_primary", "is_active")
+    search_fields = (
+        "player__first_name",
+        "player__last_name",
+        "player__preferred_name",
+        "season_team__name",
+        "season_team__division",
+        "source_identifier",
+    )
+    autocomplete_fields = ("player", "season_team", "import_batch")
+    readonly_fields = TimeStampedAdmin.readonly_fields
+    exclude = ("metadata",)
+
+
+@admin.register(CoachSeasonAssignment)
+class CoachSeasonAssignmentAdmin(TimeStampedAdmin):
+    list_display = ("user", "season_team", "assignment_role", "is_primary", "is_active", "starts_on", "ends_on")
+    list_filter = ("season_team__season", "season_team__division", "assignment_role", "is_primary", "is_active")
+    search_fields = (
+        "user__username",
+        "user__email",
+        "user__first_name",
+        "user__last_name",
+        "season_team__name",
+        "season_team__division",
+        "source_identifier",
+    )
+    autocomplete_fields = ("user", "season_team")
+    readonly_fields = TimeStampedAdmin.readonly_fields
+    exclude = ("metadata",)
+
diff --git a/seasons/apps.py b/seasons/apps.py
new file mode 100644
index 0000000..1b14d90
--- /dev/null
+++ b/seasons/apps.py
@@ -0,0 +1,7 @@
+from django.apps import AppConfig
+
+
+class SeasonsConfig(AppConfig):
+    default_auto_field = "django.db.models.BigAutoField"
+    name = "seasons"
+
diff --git a/seasons/migrations/0001_initial.py b/seasons/migrations/0001_initial.py
new file mode 100644
index 0000000..86242c5
--- /dev/null
+++ b/seasons/migrations/0001_initial.py
@@ -0,0 +1,212 @@
+# Generated by Django 4.2.25 on 2026-07-16 01:39
+
+from django.conf import settings
+from django.db import migrations, models
+import django.db.models.deletion
+
+
+class Migration(migrations.Migration):
+
+    initial = True
+
+    dependencies = [
+        ('players', '0002_playerimportbatch_and_more'),
+        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
+    ]
+
+    operations = [
+        migrations.CreateModel(
+            name='CoachSeasonAssignment',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('assignment_role', models.CharField(choices=[('head_coach', 'Head Coach'), ('assistant_coach', 'Assistant Coach'), ('manager', 'Manager'), ('coordinator', 'Coordinator'), ('evaluator', 'Evaluator')], max_length=40)),
+                ('is_primary', models.BooleanField(default=False)),
+                ('is_active', models.BooleanField(default=True)),
+                ('starts_on', models.DateField(blank=True, null=True)),
+                ('ends_on', models.DateField(blank=True, null=True)),
+                ('source', models.CharField(blank=True, max_length=80)),
+                ('source_identifier', models.CharField(blank=True, max_length=160)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['season_team__season__name', 'user__username', 'assignment_role', 'id'],
+            },
+        ),
+        migrations.CreateModel(
+            name='PlayerRosterMembership',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('transferred', 'Transferred'), ('guest', 'Guest'), ('removed', 'Removed')], default='active', max_length=40)),
+                ('jersey_number', models.CharField(blank=True, max_length=20)),
+                ('is_primary', models.BooleanField(default=False)),
+                ('is_active', models.BooleanField(default=True)),
+                ('starts_on', models.DateField(blank=True, null=True)),
+                ('ends_on', models.DateField(blank=True, null=True)),
+                ('source', models.CharField(blank=True, max_length=80)),
+                ('source_identifier', models.CharField(blank=True, max_length=160)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['season_team__season__name', 'player__last_name', 'player__first_name', 'id'],
+            },
+        ),
+        migrations.CreateModel(
+            name='Season',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('key', models.SlugField(max_length=80, unique=True)),
+                ('name', models.CharField(max_length=120)),
+                ('starts_on', models.DateField(blank=True, null=True)),
+                ('ends_on', models.DateField(blank=True, null=True)),
+                ('is_active', models.BooleanField(default=True)),
+                ('is_current', models.BooleanField(default=False)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+            ],
+            options={
+                'ordering': ['-starts_on', 'name', 'id'],
+            },
+        ),
+        migrations.CreateModel(
+            name='SeasonTeam',
+            fields=[
+                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
+                ('created_at', models.DateTimeField(auto_now_add=True)),
+                ('updated_at', models.DateTimeField(auto_now=True)),
+                ('name', models.CharField(max_length=120)),
+                ('division', models.CharField(max_length=80)),
+                ('normalized_name', models.CharField(editable=False, max_length=120)),
+                ('normalized_division', models.CharField(editable=False, max_length=80)),
+                ('external_source', models.CharField(blank=True, max_length=80)),
+                ('external_identifier', models.CharField(blank=True, max_length=160)),
+                ('is_active', models.BooleanField(default=True)),
+                ('metadata', models.JSONField(blank=True, default=dict)),
+                ('season', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='teams', to='seasons.season')),
+            ],
+            options={
+                'ordering': ['season__name', 'normalized_division', 'normalized_name', 'id'],
+            },
+        ),
+        migrations.AddIndex(
+            model_name='season',
+            index=models.Index(fields=['key'], name='seasons_sea_key_19cf1b_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='season',
+            index=models.Index(fields=['is_active', 'starts_on'], name='seasons_sea_is_acti_4d2b6d_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='season',
+            index=models.Index(fields=['is_current'], name='seasons_sea_is_curr_fa354e_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='season',
+            constraint=models.UniqueConstraint(condition=models.Q(('is_current', True)), fields=('is_current',), name='seasons_unique_current_season'),
+        ),
+        migrations.AddField(
+            model_name='playerrostermembership',
+            name='import_batch',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='roster_memberships', to='players.playerimportbatch'),
+        ),
+        migrations.AddField(
+            model_name='playerrostermembership',
+            name='player',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roster_memberships', to='players.player'),
+        ),
+        migrations.AddField(
+            model_name='playerrostermembership',
+            name='season_team',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='player_memberships', to='seasons.seasonteam'),
+        ),
+        migrations.AddField(
+            model_name='coachseasonassignment',
+            name='season_team',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='coach_assignments', to='seasons.seasonteam'),
+        ),
+        migrations.AddField(
+            model_name='coachseasonassignment',
+            name='user',
+            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='season_assignments', to=settings.AUTH_USER_MODEL),
+        ),
+        migrations.AddIndex(
+            model_name='seasonteam',
+            index=models.Index(fields=['season', 'normalized_division', 'normalized_name'], name='seasons_sea_season__255742_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='seasonteam',
+            index=models.Index(fields=['season', 'division'], name='seasons_sea_season__ebc575_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='seasonteam',
+            index=models.Index(fields=['season', 'is_active'], name='seasons_sea_season__faa9ab_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='seasonteam',
+            index=models.Index(fields=['external_source', 'external_identifier'], name='seasons_sea_externa_d9520f_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='seasonteam',
+            constraint=models.UniqueConstraint(fields=('season', 'normalized_division', 'normalized_name'), name='seasons_unique_team_per_season_division'),
+        ),
+        migrations.AddConstraint(
+            model_name='seasonteam',
+            constraint=models.UniqueConstraint(condition=models.Q(models.Q(('external_source', ''), _negated=True), models.Q(('external_identifier', ''), _negated=True)), fields=('season', 'external_source', 'external_identifier'), name='seasons_unique_team_external_identifier'),
+        ),
+        migrations.AddIndex(
+            model_name='playerrostermembership',
+            index=models.Index(fields=['player', 'is_active'], name='seasons_pla_player__612c11_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='playerrostermembership',
+            index=models.Index(fields=['season_team', 'is_active'], name='seasons_pla_season__528f3e_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='playerrostermembership',
+            index=models.Index(fields=['player', 'is_primary', 'is_active'], name='seasons_pla_player__a38126_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='playerrostermembership',
+            index=models.Index(fields=['starts_on', 'ends_on'], name='seasons_pla_starts__1e6e88_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='playerrostermembership',
+            index=models.Index(fields=['source', 'source_identifier'], name='seasons_pla_source_31c641_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='playerrostermembership',
+            index=models.Index(fields=['import_batch'], name='seasons_pla_import__f10afb_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='playerrostermembership',
+            constraint=models.UniqueConstraint(condition=models.Q(models.Q(('source', ''), _negated=True), models.Q(('source_identifier', ''), _negated=True)), fields=('player', 'season_team', 'source', 'source_identifier'), name='seasons_unique_player_membership_source'),
+        ),
+        migrations.AddIndex(
+            model_name='coachseasonassignment',
+            index=models.Index(fields=['user', 'is_active'], name='seasons_coa_user_id_e9754f_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='coachseasonassignment',
+            index=models.Index(fields=['season_team', 'is_active'], name='seasons_coa_season__110fa1_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='coachseasonassignment',
+            index=models.Index(fields=['user', 'is_primary', 'is_active'], name='seasons_coa_user_id_52b4e2_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='coachseasonassignment',
+            index=models.Index(fields=['assignment_role', 'is_active'], name='seasons_coa_assignm_f413bf_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='coachseasonassignment',
+            index=models.Index(fields=['source', 'source_identifier'], name='seasons_coa_source_c3a514_idx'),
+        ),
+        migrations.AddConstraint(
+            model_name='coachseasonassignment',
+            constraint=models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('user', 'season_team', 'assignment_role'), name='seasons_unique_active_coach_assignment'),
+        ),
+    ]
diff --git a/seasons/migrations/__init__.py b/seasons/migrations/__init__.py
new file mode 100644
index 0000000..8b13789
--- /dev/null
+++ b/seasons/migrations/__init__.py
@@ -0,0 +1 @@
+
diff --git a/seasons/models.py b/seasons/models.py
new file mode 100644
index 0000000..a49ce17
--- /dev/null
+++ b/seasons/models.py
@@ -0,0 +1,264 @@
+from __future__ import annotations
+
+from django.conf import settings
+from django.core.exceptions import ValidationError
+from django.db import models
+from django.db.models import Q
+from django.utils.text import slugify
+
+
+def normalize_lookup_value(value: str) -> str:
+    return " ".join(str(value or "").strip().casefold().split())
+
+
+def normalize_slug_value(value: str) -> str:
+    normalized = normalize_lookup_value(value)
+    return slugify(normalized)
+
+
+class TimeStampedModel(models.Model):
+    created_at = models.DateTimeField(auto_now_add=True)
+    updated_at = models.DateTimeField(auto_now=True)
+
+    class Meta:
+        abstract = True
+
+
+class Season(TimeStampedModel):
+    key = models.SlugField(max_length=80, unique=True)
+    name = models.CharField(max_length=120)
+    starts_on = models.DateField(null=True, blank=True)
+    ends_on = models.DateField(null=True, blank=True)
+    is_active = models.BooleanField(default=True)
+    is_current = models.BooleanField(default=False)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["-starts_on", "name", "id"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["is_current"],
+                condition=Q(is_current=True),
+                name="seasons_unique_current_season",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["key"]),
+            models.Index(fields=["is_active", "starts_on"]),
+            models.Index(fields=["is_current"]),
+        ]
+
+    def clean(self):
+        self.key = normalize_slug_value(self.key)
+        self.name = str(self.name or "").strip()
+        if not self.key:
+            raise ValidationError({"key": "Season key is required."})
+        if not self.name:
+            raise ValidationError({"name": "Season name is required."})
+        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
+            raise ValidationError({"ends_on": "Season end date cannot be before the start date."})
+
+    def save(self, *args, **kwargs):
+        self.key = normalize_slug_value(self.key)
+        self.name = str(self.name or "").strip()
+        self.full_clean()
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return self.name
+
+
+class SeasonTeam(TimeStampedModel):
+    season = models.ForeignKey(Season, on_delete=models.PROTECT, related_name="teams")
+    name = models.CharField(max_length=120)
+    division = models.CharField(max_length=80)
+    normalized_name = models.CharField(max_length=120, editable=False)
+    normalized_division = models.CharField(max_length=80, editable=False)
+    external_source = models.CharField(max_length=80, blank=True)
+    external_identifier = models.CharField(max_length=160, blank=True)
+    is_active = models.BooleanField(default=True)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["season__name", "normalized_division", "normalized_name", "id"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["season", "normalized_division", "normalized_name"],
+                name="seasons_unique_team_per_season_division",
+            ),
+            models.UniqueConstraint(
+                fields=["season", "external_source", "external_identifier"],
+                condition=~Q(external_source="") & ~Q(external_identifier=""),
+                name="seasons_unique_team_external_identifier",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["season", "normalized_division", "normalized_name"]),
+            models.Index(fields=["season", "division"]),
+            models.Index(fields=["season", "is_active"]),
+            models.Index(fields=["external_source", "external_identifier"]),
+        ]
+
+    def clean(self):
+        self.name = str(self.name or "").strip()
+        self.division = str(self.division or "").strip()
+        self.normalized_name = normalize_lookup_value(self.name)
+        self.normalized_division = normalize_lookup_value(self.division)
+        self.external_source = normalize_lookup_value(self.external_source).replace(" ", "_")
+        self.external_identifier = normalize_lookup_value(self.external_identifier)
+        if not self.name:
+            raise ValidationError({"name": "Team name is required."})
+        if not self.division:
+            raise ValidationError({"division": "Division is required."})
+
+    def save(self, *args, **kwargs):
+        self.full_clean()
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return f"{self.season} / {self.division} {self.name}"
+
+
+class RosterStatus(models.TextChoices):
+    ACTIVE = "active", "Active"
+    INACTIVE = "inactive", "Inactive"
+    TRANSFERRED = "transferred", "Transferred"
+    GUEST = "guest", "Guest"
+    REMOVED = "removed", "Removed"
+
+
+class PlayerRosterMembership(TimeStampedModel):
+    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="roster_memberships")
+    season_team = models.ForeignKey(SeasonTeam, on_delete=models.PROTECT, related_name="player_memberships")
+    status = models.CharField(max_length=40, choices=RosterStatus.choices, default=RosterStatus.ACTIVE)
+    jersey_number = models.CharField(max_length=20, blank=True)
+    is_primary = models.BooleanField(default=False)
+    is_active = models.BooleanField(default=True)
+    starts_on = models.DateField(null=True, blank=True)
+    ends_on = models.DateField(null=True, blank=True)
+    source = models.CharField(max_length=80, blank=True)
+    source_identifier = models.CharField(max_length=160, blank=True)
+    import_batch = models.ForeignKey(
+        "players.PlayerImportBatch",
+        null=True,
+        blank=True,
+        on_delete=models.SET_NULL,
+        related_name="roster_memberships",
+    )
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["season_team__season__name", "player__last_name", "player__first_name", "id"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["player", "season_team", "source", "source_identifier"],
+                condition=~Q(source="") & ~Q(source_identifier=""),
+                name="seasons_unique_player_membership_source",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["player", "is_active"]),
+            models.Index(fields=["season_team", "is_active"]),
+            models.Index(fields=["player", "is_primary", "is_active"]),
+            models.Index(fields=["starts_on", "ends_on"]),
+            models.Index(fields=["source", "source_identifier"]),
+            models.Index(fields=["import_batch"]),
+        ]
+
+    @property
+    def season(self) -> Season:
+        return self.season_team.season
+
+    def clean(self):
+        self.source = normalize_lookup_value(self.source).replace(" ", "_")
+        self.source_identifier = normalize_lookup_value(self.source_identifier)
+        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
+            raise ValidationError({"ends_on": "Membership end date cannot be before the start date."})
+        if self.is_primary and not self.is_active:
+            raise ValidationError({"is_primary": "Only active memberships can be primary."})
+        if self.is_primary and self.is_active and self.player_id and self.season_team_id:
+            queryset = PlayerRosterMembership.objects.filter(
+                player_id=self.player_id,
+                season_team__season_id=self.season_team.season_id,
+                is_active=True,
+                is_primary=True,
+            )
+            if self.pk:
+                queryset = queryset.exclude(pk=self.pk)
+            if queryset.exists():
+                raise ValidationError({"is_primary": "This player already has an active primary membership for this season."})
+
+    def save(self, *args, **kwargs):
+        self.full_clean()
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return f"{self.player} - {self.season_team}"
+
+
+class CoachAssignmentRole(models.TextChoices):
+    HEAD_COACH = "head_coach", "Head Coach"
+    ASSISTANT_COACH = "assistant_coach", "Assistant Coach"
+    MANAGER = "manager", "Manager"
+    COORDINATOR = "coordinator", "Coordinator"
+    EVALUATOR = "evaluator", "Evaluator"
+
+
+class CoachSeasonAssignment(TimeStampedModel):
+    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="season_assignments")
+    season_team = models.ForeignKey(SeasonTeam, on_delete=models.PROTECT, related_name="coach_assignments")
+    assignment_role = models.CharField(max_length=40, choices=CoachAssignmentRole.choices)
+    is_primary = models.BooleanField(default=False)
+    is_active = models.BooleanField(default=True)
+    starts_on = models.DateField(null=True, blank=True)
+    ends_on = models.DateField(null=True, blank=True)
+    source = models.CharField(max_length=80, blank=True)
+    source_identifier = models.CharField(max_length=160, blank=True)
+    metadata = models.JSONField(default=dict, blank=True)
+
+    class Meta:
+        ordering = ["season_team__season__name", "user__username", "assignment_role", "id"]
+        constraints = [
+            models.UniqueConstraint(
+                fields=["user", "season_team", "assignment_role"],
+                condition=Q(is_active=True),
+                name="seasons_unique_active_coach_assignment",
+            ),
+        ]
+        indexes = [
+            models.Index(fields=["user", "is_active"]),
+            models.Index(fields=["season_team", "is_active"]),
+            models.Index(fields=["user", "is_primary", "is_active"]),
+            models.Index(fields=["assignment_role", "is_active"]),
+            models.Index(fields=["source", "source_identifier"]),
+        ]
+
+    @property
+    def season(self) -> Season:
+        return self.season_team.season
+
+    def clean(self):
+        self.source = normalize_lookup_value(self.source).replace(" ", "_")
+        self.source_identifier = normalize_lookup_value(self.source_identifier)
+        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
+            raise ValidationError({"ends_on": "Assignment end date cannot be before the start date."})
+        if self.is_primary and not self.is_active:
+            raise ValidationError({"is_primary": "Only active assignments can be primary."})
+        if self.is_primary and self.is_active and self.user_id and self.season_team_id:
+            queryset = CoachSeasonAssignment.objects.filter(
+                user_id=self.user_id,
+                season_team__season_id=self.season_team.season_id,
+                is_active=True,
+                is_primary=True,
+            )
+            if self.pk:
+                queryset = queryset.exclude(pk=self.pk)
+            if queryset.exists():
+                raise ValidationError({"is_primary": "This user already has an active primary assignment for this season."})
+
+    def save(self, *args, **kwargs):
+        self.full_clean()
+        super().save(*args, **kwargs)
+
+    def __str__(self) -> str:
+        return f"{self.user} - {self.get_assignment_role_display()} - {self.season_team}"
diff --git a/seasons/services/__init__.py b/seasons/services/__init__.py
new file mode 100644
index 0000000..8b13789
--- /dev/null
+++ b/seasons/services/__init__.py
@@ -0,0 +1 @@
+
diff --git a/seasons/services/coach_assignment_service.py b/seasons/services/coach_assignment_service.py
new file mode 100644
index 0000000..ed4908e
--- /dev/null
+++ b/seasons/services/coach_assignment_service.py
@@ -0,0 +1,105 @@
+from __future__ import annotations
+
+from django.core.exceptions import ValidationError
+from django.db import transaction
+
+from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, Season, SeasonTeam
+
+
+def assignments_for_user(user, season: Season | None = None):
+    queryset = CoachSeasonAssignment.objects.select_related("season_team", "season_team__season").filter(user=user)
+    if season:
+        queryset = queryset.filter(season_team__season=season)
+    return queryset.order_by("-is_primary", "-is_active", "season_team__division", "season_team__name", "id")
+
+
+def assignments_for_team(season_team: SeasonTeam):
+    return (
+        CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season")
+        .filter(season_team=season_team)
+        .order_by("-is_primary", "assignment_role", "user__last_name", "user__first_name", "id")
+    )
+
+
+def get_primary_assignment(user, season: Season) -> CoachSeasonAssignment | None:
+    return (
+        CoachSeasonAssignment.objects.select_related("season_team", "season_team__season")
+        .filter(user=user, season_team__season=season, is_active=True, is_primary=True)
+        .order_by("id")
+        .first()
+    )
+
+
+@transaction.atomic
+def create_assignment(
+    *,
+    user,
+    season_team: SeasonTeam,
+    assignment_role: str = CoachAssignmentRole.ASSISTANT_COACH,
+    is_primary: bool = False,
+    is_active: bool = True,
+    starts_on=None,
+    ends_on=None,
+    source: str = "",
+    source_identifier: str = "",
+    metadata: dict | None = None,
+) -> CoachSeasonAssignment:
+    assignment = CoachSeasonAssignment(
+        user=user,
+        season_team=season_team,
+        assignment_role=assignment_role,
+        is_primary=False,
+        is_active=is_active,
+        starts_on=starts_on,
+        ends_on=ends_on,
+        source=source,
+        source_identifier=source_identifier,
+        metadata=metadata or {},
+    )
+    assignment.save()
+    if is_primary:
+        assignment = set_primary_assignment(assignment)
+    return assignment
+
+
+@transaction.atomic
+def update_assignment(assignment: CoachSeasonAssignment, **updates) -> CoachSeasonAssignment:
+    requested_primary = updates.pop("is_primary", None)
+    for field, value in updates.items():
+        setattr(assignment, field, value)
+    if requested_primary is False:
+        assignment.is_primary = False
+    assignment.save()
+    if requested_primary is True and not assignment.is_primary:
+        assignment = set_primary_assignment(assignment)
+    return assignment
+
+
+@transaction.atomic
+def set_primary_assignment(assignment: CoachSeasonAssignment) -> CoachSeasonAssignment:
+    if not assignment.is_active:
+        raise ValidationError("Only active assignments can be primary.")
+    locked = CoachSeasonAssignment.objects.select_for_update().filter(
+        user=assignment.user,
+        season_team__season=assignment.season,
+        is_active=True,
+    )
+    locked.exclude(pk=assignment.pk).filter(is_primary=True).update(is_primary=False)
+    assignment = CoachSeasonAssignment.objects.select_for_update().get(pk=assignment.pk)
+    assignment.is_primary = True
+    assignment.save(update_fields=["is_primary", "updated_at"])
+    return assignment
+
+
+@transaction.atomic
+def deactivate_assignment(
+    assignment: CoachSeasonAssignment,
+    *,
+    ends_on=None,
+) -> CoachSeasonAssignment:
+    assignment.is_active = False
+    assignment.is_primary = False
+    if ends_on is not None:
+        assignment.ends_on = ends_on
+    assignment.save()
+    return assignment
diff --git a/seasons/services/membership_service.py b/seasons/services/membership_service.py
new file mode 100644
index 0000000..1051ab7
--- /dev/null
+++ b/seasons/services/membership_service.py
@@ -0,0 +1,195 @@
+from __future__ import annotations
+
+from django.core.exceptions import ValidationError
+from django.db import transaction
+
+from players.models import Player
+from seasons.models import PlayerRosterMembership, RosterStatus, Season, SeasonTeam
+
+
+def memberships_for_player(player: Player, season: Season | None = None):
+    queryset = PlayerRosterMembership.objects.select_related("season_team", "season_team__season").filter(player=player)
+    if season:
+        queryset = queryset.filter(season_team__season=season)
+    return queryset.order_by("-is_primary", "-is_active", "season_team__division", "season_team__name", "id")
+
+
+def get_primary_membership(player: Player, season: Season) -> PlayerRosterMembership | None:
+    return (
+        PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
+        .filter(player=player, season_team__season=season, is_active=True, is_primary=True)
+        .order_by("id")
+        .first()
+    )
+
+
+def get_current_membership(player: Player, season: Season) -> PlayerRosterMembership | None:
+    primary = get_primary_membership(player, season)
+    if primary:
+        return primary
+    return (
+        PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
+        .filter(player=player, season_team__season=season, is_active=True)
+        .order_by("-starts_on", "-created_at", "-id")
+        .first()
+    )
+
+
+def current_team_division(player: Player, season: Season) -> tuple[str, str]:
+    membership = get_current_membership(player, season)
+    if not membership:
+        return "", ""
+    return membership.season_team.name, membership.season_team.division
+
+
+@transaction.atomic
+def create_membership(
+    *,
+    player: Player,
+    season_team: SeasonTeam,
+    status: str = RosterStatus.ACTIVE,
+    jersey_number: str = "",
+    is_primary: bool = False,
+    is_active: bool = True,
+    starts_on=None,
+    ends_on=None,
+    source: str = "",
+    source_identifier: str = "",
+    import_batch=None,
+    metadata: dict | None = None,
+    sync_player_fields: bool = False,
+) -> PlayerRosterMembership:
+    membership = PlayerRosterMembership(
+        player=player,
+        season_team=season_team,
+        status=status,
+        jersey_number=jersey_number,
+        is_primary=False,
+        is_active=is_active,
+        starts_on=starts_on,
+        ends_on=ends_on,
+        source=source,
+        source_identifier=source_identifier,
+        import_batch=import_batch,
+        metadata=metadata or {},
+    )
+    membership.save()
+    if is_primary:
+        membership = set_primary_membership(membership, sync_player_fields=sync_player_fields)
+    elif sync_player_fields:
+        sync_player_current_team_fields(player, season_team.season)
+    return membership
+
+
+@transaction.atomic
+def update_membership(membership: PlayerRosterMembership, *, sync_player_fields: bool = False, **updates) -> PlayerRosterMembership:
+    requested_primary = updates.pop("is_primary", None)
+    for field, value in updates.items():
+        setattr(membership, field, value)
+    if requested_primary is False:
+        membership.is_primary = False
+    membership.save()
+    if requested_primary is True and not membership.is_primary:
+        membership = set_primary_membership(membership, sync_player_fields=sync_player_fields)
+    elif sync_player_fields:
+        sync_player_current_team_fields(membership.player, membership.season)
+    return membership
+
+
+@transaction.atomic
+def set_primary_membership(
+    membership: PlayerRosterMembership,
+    *,
+    sync_player_fields: bool = True,
+) -> PlayerRosterMembership:
+    if not membership.is_active:
+        raise ValidationError("Only active memberships can be primary.")
+    locked = PlayerRosterMembership.objects.select_for_update().filter(
+        player=membership.player,
+        season_team__season=membership.season,
+        is_active=True,
+    )
+    locked.exclude(pk=membership.pk).filter(is_primary=True).update(is_primary=False)
+    membership = PlayerRosterMembership.objects.select_for_update().get(pk=membership.pk)
+    membership.is_primary = True
+    membership.save(update_fields=["is_primary", "updated_at"])
+    if sync_player_fields:
+        sync_player_current_team_fields(membership.player, membership.season)
+    return membership
+
+
+@transaction.atomic
+def deactivate_membership(
+    membership: PlayerRosterMembership,
+    *,
+    status: str = RosterStatus.INACTIVE,
+    ends_on=None,
+    sync_player_fields: bool = False,
+) -> PlayerRosterMembership:
+    membership.is_active = False
+    membership.is_primary = False
+    membership.status = status
+    if ends_on is not None:
+        membership.ends_on = ends_on
+    membership.save()
+    if sync_player_fields:
+        sync_player_current_team_fields(membership.player, membership.season)
+    return membership
+
+
+@transaction.atomic
+def transfer_player(
+    *,
+    player: Player,
+    to_season_team: SeasonTeam,
+    from_membership: PlayerRosterMembership | None = None,
+    transfer_date=None,
+    source: str = "",
+    source_identifier: str = "",
+    metadata: dict | None = None,
+) -> PlayerRosterMembership:
+    season = to_season_team.season
+    if from_membership is None:
+        from_membership = get_primary_membership(player, season)
+    if from_membership:
+        deactivate_membership(
+            from_membership,
+            status=RosterStatus.TRANSFERRED,
+            ends_on=transfer_date,
+            sync_player_fields=False,
+        )
+    return create_membership(
+        player=player,
+        season_team=to_season_team,
+        status=RosterStatus.ACTIVE,
+        is_primary=True,
+        is_active=True,
+        starts_on=transfer_date,
+        source=source,
+        source_identifier=source_identifier,
+        metadata=metadata,
+        sync_player_fields=True,
+    )
+
+
+def sync_player_current_team_fields(player: Player, season: Season | None = None, *, clear_when_missing: bool = False) -> Player:
+    """Explicitly sync temporary Player team/division fields from the active primary membership."""
+    if season is None:
+        primary = (
+            PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
+            .filter(player=player, is_active=True, is_primary=True, season_team__season__is_current=True)
+            .order_by("-season_team__season__starts_on", "-created_at", "-id")
+            .first()
+        )
+    else:
+        primary = get_primary_membership(player, season)
+
+    if primary:
+        player.team_name = primary.season_team.name
+        player.division = primary.season_team.division
+        player.save(update_fields=["team_name", "division", "updated_at"])
+    elif clear_when_missing:
+        player.team_name = ""
+        player.division = ""
+        player.save(update_fields=["team_name", "division", "updated_at"])
+    return player
diff --git a/seasons/services/season_service.py b/seasons/services/season_service.py
new file mode 100644
index 0000000..9bebc2e
--- /dev/null
+++ b/seasons/services/season_service.py
@@ -0,0 +1,93 @@
+from __future__ import annotations
+
+from django.core.exceptions import ValidationError
+from django.db import transaction
+
+from seasons.models import Season
+
+
+def create_season(
+    *,
+    key: str,
+    name: str,
+    starts_on=None,
+    ends_on=None,
+    is_active: bool = True,
+    is_current: bool = False,
+    metadata: dict | None = None,
+) -> Season:
+    """Create a season, using the current-season service when needed."""
+    if is_current:
+        season = Season(
+            key=key,
+            name=name,
+            starts_on=starts_on,
+            ends_on=ends_on,
+            is_active=is_active,
+            is_current=False,
+            metadata=metadata or {},
+        )
+        season.save()
+        return set_current_season(season)
+    season = Season(
+        key=key,
+        name=name,
+        starts_on=starts_on,
+        ends_on=ends_on,
+        is_active=is_active,
+        metadata=metadata or {},
+    )
+    season.save()
+    return season
+
+
+@transaction.atomic
+def update_season(season: Season, **updates) -> Season:
+    """Update season fields with model validation."""
+    requested_current = updates.pop("is_current", None)
+    if requested_current is True and not season.is_current:
+        for field, value in updates.items():
+            setattr(season, field, value)
+        season.save()
+        return set_current_season(season)
+    if requested_current is not None:
+        season.is_current = requested_current
+    for field, value in updates.items():
+        setattr(season, field, value)
+    season.save()
+    return season
+
+
+def get_current_season() -> Season | None:
+    """Return the current season, or None before initial setup."""
+    return Season.objects.filter(is_current=True).order_by("id").first()
+
+
+@transaction.atomic
+def set_current_season(season: Season) -> Season:
+    """Atomically mark one season current and clear all others."""
+    locked = list(Season.objects.select_for_update().all())
+    if season.pk is None:
+        raise ValidationError("Save the season before making it current.")
+    Season.objects.exclude(pk=season.pk).filter(is_current=True).update(is_current=False)
+    if season not in locked:
+        season = Season.objects.select_for_update().get(pk=season.pk)
+    season.is_current = True
+    season.save(update_fields=["is_current", "updated_at"])
+    return season
+
+
+def activate_season(season: Season) -> Season:
+    season.is_active = True
+    season.save(update_fields=["is_active", "updated_at"])
+    return season
+
+
+def deactivate_season(season: Season) -> Season:
+    season.is_active = False
+    if season.is_current:
+        season.is_current = False
+        season.save(update_fields=["is_active", "is_current", "updated_at"])
+    else:
+        season.save(update_fields=["is_active", "updated_at"])
+    return season
diff --git a/seasons/services/team_service.py b/seasons/services/team_service.py
new file mode 100644
index 0000000..78f03cd
--- /dev/null
+++ b/seasons/services/team_service.py
@@ -0,0 +1,77 @@
+from __future__ import annotations
+
+from django.core.exceptions import ValidationError
+from django.db import transaction
+
+from seasons.models import Season, SeasonTeam, normalize_lookup_value
+
+
+def normalize_team_value(value: str) -> str:
+    return normalize_lookup_value(value)
+
+
+def normalize_division_value(value: str) -> str:
+    return normalize_lookup_value(value)
+
+
+@transaction.atomic
+def get_or_create_season_team(
+    *,
+    season: Season,
+    name: str,
+    division: str,
+    external_source: str = "",
+    external_identifier: str = "",
+    metadata: dict | None = None,
+) -> tuple[SeasonTeam, bool]:
+    """Create or reuse a season-specific team."""
+    normalized_name = normalize_team_value(name)
+    normalized_division = normalize_division_value(division)
+    if not normalized_name:
+        raise ValidationError("Team name is required.")
+    if not normalized_division:
+        raise ValidationError("Division is required.")
+
+    normalized_source = normalize_lookup_value(external_source).replace(" ", "_")
+    normalized_identifier = normalize_lookup_value(external_identifier)
+    if normalized_source and normalized_identifier:
+        existing_by_external = SeasonTeam.objects.select_for_update().filter(
+            season=season,
+            external_source=normalized_source,
+            external_identifier=normalized_identifier,
+        ).first()
+        if existing_by_external:
+            if (
+                existing_by_external.normalized_name != normalized_name
+                or existing_by_external.normalized_division != normalized_division
+            ):
+                raise ValidationError("External team identifier points to a different season team.")
+            return existing_by_external, False
+
+    team = SeasonTeam.objects.select_for_update().filter(
+        season=season,
+        normalized_name=normalized_name,
+        normalized_division=normalized_division,
+    ).first()
+    if team:
+        return team, False
+
+    team = SeasonTeam(
+        season=season,
+        name=name,
+        division=division,
+        external_source=external_source,
+        external_identifier=external_identifier,
+        metadata=metadata or {},
+    )
+    team.save()
+    return team, True
+
+
+@transaction.atomic
+def update_season_team(team: SeasonTeam, **updates) -> SeasonTeam:
+    for field, value in updates.items():
+        setattr(team, field, value)
+    team.save()
+    return team
+
diff --git a/seasons/tests.py b/seasons/tests.py
new file mode 100644
index 0000000..b6c5002
--- /dev/null
+++ b/seasons/tests.py
@@ -0,0 +1,398 @@
+from datetime import date
+
+from django.apps import apps
+from django.contrib import admin
+from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+from django.db import transaction
+from django.test import TestCase
+
+from accounts.models import AccountRole
+from accounts.services.profile_service import get_or_create_account_profile, set_account_role
+from players.models import Player
+from seasons.models import (
+    CoachAssignmentRole,
+    CoachSeasonAssignment,
+    PlayerRosterMembership,
+    RosterStatus,
+    Season,
+    SeasonTeam,
+)
+from seasons.services.coach_assignment_service import (
+    assignments_for_team,
+    assignments_for_user,
+    create_assignment,
+    deactivate_assignment,
+    get_primary_assignment,
+    set_primary_assignment,
+    update_assignment,
+)
+from seasons.services.membership_service import (
+    create_membership,
+    current_team_division,
+    deactivate_membership,
+    get_current_membership,
+    get_primary_membership,
+    memberships_for_player,
+    sync_player_current_team_fields,
+    transfer_player,
+    update_membership,
+)
+from seasons.services.season_service import create_season, deactivate_season, get_current_season, set_current_season
+from seasons.services.team_service import get_or_create_season_team
+
+
+User = get_user_model()
+
+
+class SeasonModelServiceTests(TestCase):
+    def test_seasons_app_is_installed(self):
+        self.assertTrue(apps.is_installed("seasons"))
+
+    def test_create_valid_season_normalizes_key(self):
+        season = create_season(key=" 2026 Spring ", name=" 2026 Spring ", starts_on=date(2026, 4, 1))
+
+        self.assertEqual(season.key, "2026-spring")
+        self.assertEqual(season.name, "2026 Spring")
+        self.assertTrue(season.is_active)
+        self.assertFalse(season.is_current)
+
+    def test_season_key_is_unique(self):
+        create_season(key="2026-spring", name="2026 Spring")
+
+        with self.assertRaises(ValidationError):
+            create_season(key="2026 Spring", name="Duplicate")
+
+    def test_season_requires_key_name_and_valid_dates(self):
+        with self.assertRaises(ValidationError):
+            create_season(key="", name="2026 Spring")
+        with self.assertRaises(ValidationError):
+            create_season(key="2026-spring", name="")
+        with self.assertRaises(ValidationError):
+            create_season(key="2026-spring", name="2026 Spring", starts_on=date(2026, 8, 1), ends_on=date(2026, 4, 1))
+
+    def test_zero_current_seasons_allowed_before_setup(self):
+        create_season(key="2026-spring", name="2026 Spring")
+
+        self.assertIsNone(get_current_season())
+
+    def test_set_first_current_season_and_switch_current(self):
+        spring = create_season(key="2026-spring", name="2026 Spring")
+        summer = create_season(key="2026-summer", name="2026 Summer")
+
+        set_current_season(spring)
+        self.assertEqual(get_current_season(), spring)
+
+        set_current_season(summer)
+        spring.refresh_from_db()
+        summer.refresh_from_db()
+        self.assertFalse(spring.is_current)
+        self.assertTrue(summer.is_current)
+        self.assertEqual(get_current_season(), summer)
+
+    def test_model_validation_prevents_second_current_season(self):
+        create_season(key="2026-spring", name="2026 Spring", is_current=True)
+
+        with self.assertRaises(ValidationError):
+            with transaction.atomic():
+                Season.objects.create(key="2026-summer", name="2026 Summer", is_current=True)
+
+    def test_inactive_historical_season_remains_queryable(self):
+        season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+
+        deactivate_season(season)
+        season.refresh_from_db()
+
+        self.assertFalse(season.is_active)
+        self.assertFalse(season.is_current)
+        self.assertEqual(Season.objects.get(pk=season.pk), season)
+
+
+class SeasonTeamTests(TestCase):
+    def setUp(self):
+        self.spring = create_season(key="2026-spring", name="2026 Spring")
+        self.next_spring = create_season(key="2027-spring", name="2027 Spring")
+
+    def test_create_team_normalizes_values(self):
+        team, created = get_or_create_season_team(season=self.spring, name="  Dodgers  ", division=" 13U   House ")
+
+        self.assertTrue(created)
+        self.assertEqual(team.normalized_name, "dodgers")
+        self.assertEqual(team.normalized_division, "13u house")
+
+    def test_same_normalized_team_division_reused(self):
+        first, created_first = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
+        second, created_second = get_or_create_season_team(season=self.spring, name=" dodgers ", division=" 13u ")
+
+        self.assertTrue(created_first)
+        self.assertFalse(created_second)
+        self.assertEqual(first, second)
+
+    def test_same_team_name_in_different_seasons_allowed(self):
+        first, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
+        second, _ = get_or_create_season_team(season=self.next_spring, name="Dodgers", division="13U")
+
+        self.assertNotEqual(first, second)
+
+    def test_external_identifier_scoped_to_season_and_blank_does_not_conflict(self):
+        first, _ = get_or_create_season_team(
+            season=self.spring,
+            name="Dodgers",
+            division="13U",
+            external_source="Roster",
+            external_identifier="ABC",
+        )
+        second, created_second = get_or_create_season_team(
+            season=self.next_spring,
+            name="Dodgers",
+            division="13U",
+            external_source="Roster",
+            external_identifier="ABC",
+        )
+        blank_one, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
+        blank_two, _ = get_or_create_season_team(season=self.spring, name="Mounties", division="13U")
+
+        self.assertNotEqual(first, second)
+        self.assertTrue(created_second)
+        self.assertNotEqual(blank_one, blank_two)
+
+    def test_external_identifier_conflict_rejected(self):
+        get_or_create_season_team(
+            season=self.spring,
+            name="Dodgers",
+            division="13U",
+            external_source="Roster",
+            external_identifier="ABC",
+        )
+
+        with self.assertRaises(ValidationError):
+            get_or_create_season_team(
+                season=self.spring,
+                name="Expos",
+                division="13U",
+                external_source="roster",
+                external_identifier="abc",
+            )
+
+
+class PlayerMembershipTests(TestCase):
+    def setUp(self):
+        self.spring = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        self.next_spring = create_season(key="2027-spring", name="2027 Spring")
+        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
+        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
+        self.mounties, _ = get_or_create_season_team(season=self.next_spring, name="Mounties", division="15U")
+        self.player = Player.objects.create(first_name="Alex", last_name="Player", team_name="Legacy", division="Legacy")
+
+    def test_player_may_join_one_team_and_different_seasons(self):
+        first = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+        second = create_membership(player=self.player, season_team=self.mounties, is_primary=True)
+
+        self.assertEqual(first.player, self.player)
+        self.assertEqual(second.player, self.player)
+        self.assertEqual(memberships_for_player(self.player).count(), 2)
+
+    def test_multiple_memberships_in_one_season_and_non_primary_concurrent_allowed(self):
+        primary = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+        guest = create_membership(player=self.player, season_team=self.expos, status=RosterStatus.GUEST, is_primary=False)
+
+        self.assertTrue(primary.is_primary)
+        self.assertFalse(guest.is_primary)
+        self.assertEqual(memberships_for_player(self.player, self.spring).count(), 2)
+
+    def test_only_one_active_primary_membership_per_player_season(self):
+        first = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+        second = create_membership(player=self.player, season_team=self.expos, is_primary=True)
+
+        first.refresh_from_db()
+        second.refresh_from_db()
+        self.assertFalse(first.is_primary)
+        self.assertTrue(second.is_primary)
+        self.assertEqual(get_primary_membership(self.player, self.spring), second)
+
+    def test_update_membership_can_unset_primary(self):
+        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+
+        update_membership(membership, is_primary=False)
+        membership.refresh_from_db()
+
+        self.assertFalse(membership.is_primary)
+
+    def test_direct_duplicate_primary_membership_is_rejected(self):
+        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+
+        with self.assertRaises(ValidationError):
+            PlayerRosterMembership.objects.create(player=self.player, season_team=self.expos, is_primary=True)
+
+    def test_transfer_creates_new_membership_and_preserves_history(self):
+        old = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+
+        new = transfer_player(player=self.player, to_season_team=self.expos, transfer_date=date(2026, 6, 1))
+        old.refresh_from_db()
+        self.player.refresh_from_db()
+
+        self.assertFalse(old.is_active)
+        self.assertFalse(old.is_primary)
+        self.assertEqual(old.status, RosterStatus.TRANSFERRED)
+        self.assertEqual(old.ends_on, date(2026, 6, 1))
+        self.assertTrue(new.is_primary)
+        self.assertEqual(self.player.team_name, "Expos")
+        self.assertEqual(self.player.division, "13U")
+
+    def test_date_validation(self):
+        with self.assertRaises(ValidationError):
+            create_membership(
+                player=self.player,
+                season_team=self.dodgers,
+                starts_on=date(2026, 8, 1),
+                ends_on=date(2026, 7, 1),
+            )
+
+    def test_current_membership_derivation_and_team_division(self):
+        create_membership(player=self.player, season_team=self.dodgers, is_primary=False)
+        primary = create_membership(player=self.player, season_team=self.expos, is_primary=True)
+
+        self.assertEqual(get_current_membership(self.player, self.spring), primary)
+        self.assertEqual(current_team_division(self.player, self.spring), ("Expos", "13U"))
+
+    def test_compatibility_sync_is_explicit_and_can_clear_when_requested(self):
+        create_membership(player=self.player, season_team=self.dodgers, is_primary=True, sync_player_fields=False)
+        self.player.refresh_from_db()
+
+        self.assertEqual(self.player.team_name, "Legacy")
+        sync_player_current_team_fields(self.player, self.spring)
+        self.player.refresh_from_db()
+        self.assertEqual(self.player.team_name, "Dodgers")
+        self.assertEqual(self.player.division, "13U")
+
+        deactivate_membership(get_primary_membership(self.player, self.spring), sync_player_fields=False)
+        sync_player_current_team_fields(self.player, self.spring, clear_when_missing=False)
+        self.player.refresh_from_db()
+        self.assertEqual(self.player.team_name, "Dodgers")
+
+        sync_player_current_team_fields(self.player, self.spring, clear_when_missing=True)
+        self.player.refresh_from_db()
+        self.assertEqual(self.player.team_name, "")
+        self.assertEqual(self.player.division, "")
+
+
+class CoachAssignmentTests(TestCase):
+    def setUp(self):
+        self.spring = create_season(key="2026-spring", name="2026 Spring")
+        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
+        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
+        self.coach = User.objects.create_user(
+            username="coach",
+            password="original-pass",
+            first_name="Casey",
+            last_name="Coach",
+            email="coach@example.com",
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+
+    def test_create_assignment_and_query_helpers(self):
+        assignment = create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+            is_primary=True,
+        )
+
+        self.assertEqual(assignments_for_user(self.coach, self.spring).first(), assignment)
+        self.assertEqual(assignments_for_team(self.dodgers).first(), assignment)
+        self.assertEqual(get_primary_assignment(self.coach, self.spring), assignment)
+
+    def test_multiple_assignments_and_multiple_coaches_allowed(self):
+        other = User.objects.create_user(username="other", password="testpass")
+
+        first = create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
+        second = create_assignment(user=self.coach, season_team=self.expos, assignment_role=CoachAssignmentRole.EVALUATOR)
+        third = create_assignment(user=other, season_team=self.dodgers, assignment_role=CoachAssignmentRole.ASSISTANT_COACH)
+
+        self.assertEqual({first, second}, set(assignments_for_user(self.coach, self.spring)))
+        self.assertIn(third, list(assignments_for_team(self.dodgers)))
+
+    def test_duplicate_active_user_team_role_rejected(self):
+        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
+
+        with self.assertRaises(ValidationError):
+            create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
+
+    def test_only_one_active_primary_assignment_per_user_season(self):
+        first = create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH, is_primary=True)
+        second = create_assignment(user=self.coach, season_team=self.expos, assignment_role=CoachAssignmentRole.EVALUATOR, is_primary=True)
+
+        first.refresh_from_db()
+        second.refresh_from_db()
+        self.assertFalse(first.is_primary)
+        self.assertTrue(second.is_primary)
+
+    def test_update_assignment_can_unset_primary(self):
+        assignment = create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+            is_primary=True,
+        )
+
+        update_assignment(assignment, is_primary=False)
+        assignment.refresh_from_db()
+
+        self.assertFalse(assignment.is_primary)
+
+    def test_direct_duplicate_primary_assignment_is_rejected(self):
+        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH, is_primary=True)
+
+        with self.assertRaises(ValidationError):
+            CoachSeasonAssignment.objects.create(
+                user=self.coach,
+                season_team=self.expos,
+                assignment_role=CoachAssignmentRole.EVALUATOR,
+                is_primary=True,
+            )
+
+    def test_assignment_has_no_account_role_privilege_or_password_side_effects(self):
+        original_password = self.coach.password
+        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
+        self.coach.refresh_from_db()
+        profile = get_or_create_account_profile(self.coach)
+
+        self.assertEqual(profile.role, AccountRole.COACH)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+        self.assertEqual(self.coach.password, original_password)
+
+    def test_assignment_date_validation_and_deactivation(self):
+        with self.assertRaises(ValidationError):
+            create_assignment(
+                user=self.coach,
+                season_team=self.dodgers,
+                assignment_role=CoachAssignmentRole.HEAD_COACH,
+                starts_on=date(2026, 8, 1),
+                ends_on=date(2026, 7, 1),
+            )
+
+        assignment = create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+            is_primary=True,
+        )
+        deactivate_assignment(assignment, ends_on=date(2026, 8, 1))
+        assignment.refresh_from_db()
+        self.assertFalse(assignment.is_active)
+        self.assertFalse(assignment.is_primary)
+        self.assertEqual(assignment.ends_on, date(2026, 8, 1))
+
+
+class SeasonsAdminTests(TestCase):
+    def test_models_registered_in_admin(self):
+        for model in [Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment]:
+            self.assertIn(model, admin.site._registry)
+
+    def test_admin_configuration_is_searchable_and_readonly_timestamps(self):
+        for model in [Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment]:
+            model_admin = admin.site._registry[model]
+            self.assertIn("created_at", model_admin.readonly_fields)
+            self.assertIn("updated_at", model_admin.readonly_fields)
+            self.assertTrue(model_admin.search_fields)
diff --git a/vancouverminor/settings.py b/vancouverminor/settings.py
index b3f2865..2eaa7a7 100644
--- a/vancouverminor/settings.py
+++ b/vancouverminor/settings.py
@@ -61,6 +61,7 @@ INSTALLED_APPS = [
     'leaguehub',
     'scholarships',
     'players',
+    'seasons',
     'analytics',
     'accounts',
 ]
```
