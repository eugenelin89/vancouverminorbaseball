# Prompt 72 - Platform

App/subsystem: platform

Work commit: `4db1945`

## User Prompt

```text
Create a production-safe engineering plan for season-aware player and coach participation.

This is a documentation-only task.

Do NOT implement application code.

Do NOT create models or migrations.

Do NOT modify services, views, forms, templates, URLs, middleware, settings, tests, or deployment configuration.

Do NOT regenerate `project_flat_file.txt`.

Use the current repository and the latest project flat-file snapshot as the source of truth.

==================================================
Product Problem
===============

The platform currently stores `team_name` and `division` directly on the permanent `Player` record.

That is not sufficient for a long-term player-development platform because players may:

* play for different teams in different seasons;
* move divisions;
* transfer teams;
* participate in more than one team or roster during a season.

The permanent player identity must not be recreated each season.

Historical evaluations must preserve the team, division, and season context that existed when the evaluation was submitted.

Coach accounts must also remain permanent while team assignments change by season.

==================================================
Desired Product Behavior
========================

Staff should continue importing normal player CSV files.

Before or during import, staff should specify the season.

Each player row may contain:

* player identity fields;
* team;
* division;
* optional roster-specific fields.

The import should:

1. match or create the permanent `Player`;
2. find or create the season;
3. find or create the season-specific team;
4. create or update the player’s seasonal roster membership;
5. preserve prior-season records;
6. avoid recreating the same player.

Coach import should work similarly:

1. match or create the permanent user/account;
2. find or create the season-specific team;
3. create or update the coach’s seasonal assignment;
4. preserve prior assignments;
5. avoid recreating accounts;
6. avoid resetting an established coach’s password merely because they are imported for a new season.

==================================================
Recommended Conceptual Model
============================

Use this as the starting point, but inspect the repository and recommend the smallest clean design.

```text
Player
- permanent identity only

Season
- name
- starts_on
- ends_on
- is_active

SeasonTeam
- season
- team name
- division
- optional external identifiers

PlayerRosterMembership
- player
- season team
- roster status
- jersey number
- is_primary
- starts_on
- ends_on
- import provenance

CoachSeasonAssignment
- user/account
- season team
- assignment role/title
- is_primary
- starts_on
- ends_on
- import provenance
```

Names may differ if the repository already has better terminology.

Do not assume each product concept requires a new Django app.

==================================================
Evaluation Context
==================

Review how `analytics.Observation` currently links to:

* permanent player;
* evaluation cycle;
* evaluator;
* evaluator role snapshot;
* evaluation perspective snapshot.

Plan how evaluations should preserve seasonal context.

At minimum, historical evaluations must retain:

* season;
* player team at submission;
* division at submission.

Determine whether the best design is:

* a foreign key to player roster membership;
* a foreign key plus snapshot fields;
* snapshot fields only;
* another minimal design.

Prefer durable historical context over dynamic lookup.

Do not rely only on the player’s current roster membership because that could change later.

Also review whether evaluator team/coach assignment context should be stored or snapshotted.

==================================================
Current Repository Review
=========================

Review:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`
* `docs/evaluations/`
* `docs/account_management/`
* `docs/analytics/`
* existing prompt archives related to players, accounts, evaluations, and imports

Inspect:

* `players/models.py`
* player import models and services
* player matching and merge logic
* player import forms/views/templates
* `accounts/models.py`
* coach import service
* user-player link logic
* account provisioning
* `analytics/models.py`
* observation/evaluation services
* evaluation review services
* evaluation cycles
* current filters by team/division
* existing migrations
* current production deployment assumptions

==================================================
Key Decisions To Resolve
========================

The plan must explicitly decide or recommend defaults for the following.

## 1. Season Model

Define:

* season identifier;
* display name;
* date boundaries;
* active/current status;
* uniqueness rules;
* archive behavior.

Determine whether evaluation cycles should reference seasons directly.

## 2. Team Model

Determine whether teams should be:

* permanent teams plus seasonal instances;
* season-specific teams only;
* another normalized structure.

The model must support the same team name appearing in different seasons without confusing the records.

## 3. Player Membership

Determine:

* whether one player may belong to multiple teams in one season;
* whether transfers are represented as separate stints;
* primary assignment rules;
* active/inactive membership;
* uniqueness constraints;
* how current team is derived.

Default recommendation:

* allow multiple roster memberships or stints per season;
* allow only one active primary membership at a time where practical;
* never overwrite history.

## 4. Coach Assignment

Determine:

* whether one coach may be assigned to multiple teams in a season;
* head coach versus assistant coach representation;
* uniqueness rules;
* active/inactive assignment;
* whether account role and seasonal assignment role remain separate.

Recommend keeping permanent account role separate from seasonal team assignment.

## 5. Import Workflow

Design the player import workflow:

* season selection;
* team/division mapping;
* preview behavior;
* matching permanent players;
* creating roster memberships;
* reimport behavior;
* duplicate/conflict handling;
* transfer/stint handling;
* provenance.

Design the coach import workflow:

* season selection;
* team/division mapping;
* existing account reuse;
* new account creation;
* password behavior;
* assignment creation/update;
* duplicate/conflict handling;
* provenance.

## 6. Existing Fields

Plan what happens to current:

* `Player.team_name`
* `Player.division`

Options may include:

* retain temporarily as cached/current fields;
* deprecate and stop writing;
* migrate and later remove;
* keep as compatibility fields.

Recommend a staged migration path rather than abrupt deletion unless repository evidence supports removal.

## 7. Existing Production Data

Plan deterministic migration for existing production data.

Existing players may already have:

* team name;
* division;
* imported provenance;
* evaluations.

Determine:

* what default season should represent existing data;
* whether a migration should create a legacy/current season;
* how existing player records become roster memberships;
* how existing evaluations receive season/team context;
* how to avoid guessing unsupported history.

Do not fabricate historical seasons.

## 8. Evaluation Cycles

Review whether evaluation cycles and seasons are:

* the same concept;
* related but distinct;
* optionally linked.

Recommend the cleanest model.

Likely distinction:

* season = roster/organizational period;
* evaluation cycle = feedback window within a season.

## 9. Team-Based Permissions

Review future implications for:

* which coaches may evaluate which players;
* coach review filtering;
* team/division filters;
* player peer-evaluation scope;
* staff access.

Do not implement restrictions yet unless required for the plan.

Document likely future rules and dependencies.

## 10. Performance

Plan query patterns and indexing for:

* current roster by season/team;
* player history;
* coach assignments;
* evaluation review filters;
* imports;
* player development summaries.

Identify likely indexes and uniqueness constraints.

==================================================
Architecture Principles
=======================

Preserve current subsystem ownership:

* `players` owns permanent player identity, player matching, imports, and roster membership;
* `accounts` owns permanent login identity, account roles, provisioning, and user-player links;
* seasonal coach assignments may belong in `accounts` unless repository evidence supports another owner;
* `analytics` owns evaluation cycles, observations, and historical evaluation context;
* views remain thin;
* services own business logic;
* templates remain presentation-only.

Avoid circular dependencies.

Do not make `Player` season-specific.

Do not make Django `User` season-specific.

==================================================
Deliverable
===========

Create:

```text
docs/seasons/implementation/engineering/seasonal_participation_v1.md
```

The document should contain:

1. Executive summary
2. Current problem
3. Goals
4. Non-goals
5. Current architecture findings
6. Recommended domain model
7. Model ownership
8. Season and team design
9. Player roster membership design
10. Coach assignment design
11. Evaluation context design
12. Player import design
13. Coach import design
14. Reimport and duplicate behavior
15. Transfer and multi-team behavior
16. Existing data migration strategy
17. Compatibility strategy for current player fields
18. Evaluation-cycle relationship
19. Permission implications
20. Security and privacy
21. Performance and indexing
22. Proposed implementation phases
23. Test strategy
24. Deployment and rollback considerations
25. Risks
26. Open questions
27. Recommended first implementation phase
28. Acceptance criteria

Also create:

```text
docs/seasons/README.md
```

This should become the landing page for season and roster documentation.

Update only if necessary:

* `docs/ARCHITECTURE.md`
* `docs/product/PLATFORM_V2_ROADMAP.md`

Only add short cross-links or prerequisite notes.

==================================================
Recommended Implementation Phases
=================================

The plan should propose phases similar to:

## Phase 0 — Decisions And Compatibility

* finalize terminology;
* decide season/team/membership constraints;
* decide migration defaults;
* decide evaluation-cycle relationship;
* decide compatibility fields.

## Phase 1 — Season, Team, And Player Membership Foundation

* add models and migrations;
* migrate existing player team/division data;
* preserve compatibility;
* no import UI changes yet unless required.

## Phase 2 — Season-Aware Player Import

* season selection;
* team mapping;
* roster membership creation/update;
* reimport behavior;
* preview/result UX.

## Phase 3 — Coach Seasonal Assignment

* season-aware coach import;
* account reuse;
* assignment records;
* no unnecessary password resets.

## Phase 4 — Evaluation Context

* attach or snapshot season/team/division context;
* migrate existing observations;
* preserve historical accuracy;
* update review filters and labels.

## Phase 5 — Read Models And UI

* roster views;
* player season history;
* coach assignment views;
* season-aware filters.

## Phase 6 — Production Review And Freeze

* architecture review;
* migration review;
* security/privacy review;
* performance review;
* documentation and user-manual reconciliation;
* production readiness.

Adjust phases based on repository findings.

==================================================
Acceptance Criteria For The Plan
================================

Do not declare PASS until the plan clearly explains:

* permanent players are reused across seasons;
* permanent coach accounts are reused across seasons;
* seasonal team history is preserved;
* future imports do not recreate people unnecessarily;
* historical evaluations retain season/team/division context;
* reimports are deterministic;
* transfers and multi-team cases are handled;
* password behavior for existing coaches is safe;
* existing production data has a migration strategy;
* current `Player.team_name` and `division` have a compatibility plan;
* evaluation cycles and seasons have a defined relationship;
* subsystem ownership is clear;
* migration phases are safe and reversible where practical;
* tests and deployment steps are defined;
* no application code changed.

==================================================
Loop Engineering
================

Use loop engineering for planning quality.

Continue until a valid terminal state is reached.

Each loop must:

1. inspect the repository and previous planning work;
2. identify contradictions, missing decisions, unsafe assumptions, or migration gaps;
3. improve only the planning documentation and necessary cross-links;
4. review from the perspective of:

   * administrator;
   * registrar/import operator;
   * coach;
   * player;
   * product owner;
   * data architect;
   * privacy reviewer;
   * release engineer;
5. verify current behavior versus proposed behavior;
6. remove implementation claims that are not yet true;
7. run `git diff --check`;
8. commit the planning documentation;
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
Plan seasonal player and coach participation
```

2.

Prompt archive commit according to `AGENTS.md`.

Push both commits.

==================================================
Final Report
============

Report:

* terminal state;
* number of loops;
* files created;
* files modified;
* recommended model;
* season/team decision;
* player membership decision;
* coach assignment decision;
* evaluation context decision;
* player import design;
* coach import design;
* reimport behavior;
* transfer/multi-team behavior;
* migration strategy;
* compatibility strategy;
* implementation phases;
* risks;
* open questions;
* verification result;
* commits;
* push result;
* confirmation that no application code changed;
* confirmation that the working tree is clean.
```

## Work Commit Diff

```diff
commit 4db1945eb8119955c247dc6c479130da3a071847
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 15 14:19:53 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 15 14:19:53 2026 -0700

    Plan seasonal player and coach participation

diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 23c68c6..2592025 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -11,6 +11,7 @@ The platform is intended to become the central baseball operations system for Va
 Long-term capabilities may include:
 
 - player management
+- season-aware roster participation
 - player imports and identity matching
 - evaluations and coach assessments
 - analytics, reporting, timelines, and comparisons
@@ -123,6 +124,7 @@ Documentation:
 Product strategy:
 
 - [Platform V2 Roadmap](product/PLATFORM_V2_ROADMAP.md)
+- [Seasonal Participation V1 Engineering Plan](seasons/implementation/engineering/seasonal_participation_v1.md)
 
 ### Account Management
 
diff --git a/docs/product/PLATFORM_V2_ROADMAP.md b/docs/product/PLATFORM_V2_ROADMAP.md
index 7414777..3bd083a 100644
--- a/docs/product/PLATFORM_V2_ROADMAP.md
+++ b/docs/product/PLATFORM_V2_ROADMAP.md
@@ -10,6 +10,8 @@ The recommended next product milestone is:
 Platform V2: Player Development Intelligence
 ```
 
+Before deeper player-development intelligence work, the platform needs season-aware roster participation so permanent players and coach accounts can be reused across seasons while evaluations retain historical team/division context. See [Seasonal Participation V1 Engineering Plan](../seasons/implementation/engineering/seasonal_participation_v1.md).
+
 Platform V2 should turn collected evaluation data into useful player-development decision support. It should not begin with large dashboards, AI, rankings, or parent-facing raw data. The next immediate activity should be a real-world pilot using the completed Platform V1 workflows. Product decisions for Platform V2 should be driven by pilot evidence, data quality, privacy requirements, and user value.
 
 Recommended first implementation phase after pilot validation:
diff --git a/docs/seasons/README.md b/docs/seasons/README.md
new file mode 100644
index 0000000..bf0ad0c
--- /dev/null
+++ b/docs/seasons/README.md
@@ -0,0 +1,21 @@
+# Seasons And Roster Participation
+
+This folder contains planning and architecture notes for season-aware player and coach participation.
+
+The VCB platform already has permanent player identity, account identity, evaluations, imports, and account operations. The next production-readiness gap is seasonal participation: the same player or coach can belong to different teams across seasons, while historical evaluations must preserve the team, division, and season context that existed when they were submitted.
+
+## Current Planning Document
+
+- [Seasonal Participation V1 Engineering Plan](implementation/engineering/seasonal_participation_v1.md)
+
+## Ownership Summary
+
+- `players` continues to own permanent player identity, matching, and player import orchestration.
+- `accounts` continues to own Django users, account profiles, account roles, provisioning, and login identity.
+- Seasonal roster and team concepts should live in a dedicated season/roster bounded context unless implementation discovery proves a smaller existing owner is safer.
+- `analytics` should snapshot or link to seasonal context when evaluations are submitted.
+
+## Current Status
+
+Planning only. No application code, models, migrations, services, views, templates, or tests have been implemented for Seasonal Participation V1.
+
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
new file mode 100644
index 0000000..aa2586b
--- /dev/null
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -0,0 +1,769 @@
+# Seasonal Participation V1 Engineering Plan
+
+Status: Planning only.
+
+Created: 2026-07-15.
+
+## 1. Executive Summary
+
+The platform currently treats `players.Player` as the permanent player identity, but it still stores `team_name` and `division` directly on that permanent record. That is workable for a first import workflow, but it is not safe for long-term player development because players and coaches can move teams, divisions, or rosters across seasons.
+
+Seasonal Participation V1 should introduce season-aware roster context without recreating people. Permanent player identity remains stable in `players.Player`; permanent login identity remains stable in Django `User` and `accounts.AccountProfile`; evaluations remain owned by `analytics`. The new seasonal layer should record which players and coaches participated with which season-specific teams, and `analytics.Observation` should preserve the season/team/division context that existed when an evaluation was submitted.
+
+Recommended model direction:
+
+- Add a small season/roster bounded context, preferably a new `seasons` app.
+- Add `Season` and `SeasonTeam`.
+- Add `PlayerRosterMembership` for player stints on season teams.
+- Add `CoachSeasonAssignment` for coach assignments on season teams.
+- Add durable evaluation-context fields or references on `analytics.Observation`.
+- Keep `Player.team_name` and `Player.division` temporarily as compatibility/current-display fields during migration, then deprecate them after season-aware views and filters are proven.
+
+## 2. Current Problem
+
+Current `players.Player` records include:
+
+- `division`
+- `team_name`
+
+Those fields describe a roster state, not permanent player identity. If staff import a player again next season with a new team or division, updating those fields rewrites the apparent current and historical context for every view that reads from `Player`.
+
+Current submitted evaluations reference:
+
+- `players.Player`
+- `analytics.EvaluationCycle`
+- evaluator `User`
+- `EvaluatorRole`
+- evaluator role snapshot fields
+- evaluation perspective snapshot
+
+They do not currently store the player's season, team, or division at submission time. Review services currently derive `player_team` and `player_division` from `Observation.player.team_name` and `Observation.player.division`, which means historical display can change when the player record changes.
+
+Coach import currently creates or reuses coach accounts and stores `team` and `division` in profile metadata. It does not create season-specific coach assignments, and reused coaches currently receive a new temporary password during import. That is not safe for reimporting established coaches for a new season.
+
+## 3. Goals
+
+- Reuse permanent `players.Player` records across seasons.
+- Reuse permanent coach `User` and `AccountProfile` records across seasons.
+- Represent team/division participation as season-specific history.
+- Preserve prior-season roster and coach assignment records.
+- Preserve evaluation season/team/division context as it existed when each evaluation was submitted.
+- Make player and coach imports deterministic when repeated.
+- Support transfers and multi-team participation without overwriting history.
+- Keep existing Platform V1 behavior stable during the migration.
+- Keep subsystem ownership clear and avoid circular dependencies.
+- Provide a safe production migration path for existing data.
+
+## 4. Non-Goals
+
+Seasonal Participation V1 should not implement:
+
+- new player identity rules;
+- player merge or account merge;
+- coach-to-player permission restrictions unless separately approved;
+- roster-management dashboards beyond the planned implementation phases;
+- scheduling, attendance, registration, payments, or league operations;
+- parent portal changes;
+- draft workflow changes except future read-only context integration;
+- PDP migration;
+- historical season reconstruction beyond what current data supports;
+- deletion of existing `Player.team_name` or `Player.division` during the first implementation phase.
+
+## 5. Current Architecture Findings
+
+`players` currently owns:
+
+- `Player`
+- `PlayerAlias`
+- `PlayerSourceIdentifier`
+- `PlayerImportBatch`
+- `PlayerSourceRow`
+- `PlayerTag`
+- player import parsing, preview, matching, conflict handling, provenance, and optional account provisioning.
+
+`accounts` currently owns:
+
+- `AccountProfile`
+- `UserPlayerLink`
+- account roles
+- username, email, password, provisioning, account operations, link management, and coach import.
+
+`analytics` currently owns:
+
+- `Observation`
+- `ObservationResponse`
+- `EvaluationCycle`
+- observation types, sources, evaluator roles, questions, question sets, services, review filters, metrics, timeline, comparison, command center, and player-facing/coach-facing evaluation access.
+
+Important current coupling:
+
+- Player import maps `team_name` and `division` into `Player`.
+- Player matching can use `division` as context.
+- Analytics player search, metrics, review, and command center filters read `Player.team_name` and `Player.division`.
+- Coach import accepts `team` and `division` but persists them as metadata only.
+- `EvaluationCycle` has no season link.
+
+## 6. Recommended Domain Model
+
+Use the following domain concepts.
+
+### Season
+
+Represents an organizational/roster period, such as `2026 Spring`, `2026 Summer`, or `2026`.
+
+Fields to consider:
+
+- `key`: stable slug or identifier, unique.
+- `name`: display name.
+- `starts_on`: nullable date.
+- `ends_on`: nullable date.
+- `is_active`: whether the season is available for current workflows.
+- `is_current`: optional single-current flag if needed for default UI.
+- `metadata`: JSON for import/source-specific context.
+- timestamps.
+
+Recommended uniqueness:
+
+- unique `key`.
+- optional constraint to allow only one `is_current=True`, if implemented.
+
+Archive behavior:
+
+- Do not delete seasons that have memberships, assignments, imports, cycles, or observations.
+- Mark inactive rather than deleting.
+
+### SeasonTeam
+
+Represents a team within one season.
+
+Fields to consider:
+
+- `season`: FK to `Season`.
+- `name`: team display name.
+- `division`: division/program label for that season team.
+- `normalized_name`: normalized team name for imports.
+- `normalized_division`: normalized division for imports.
+- `external_source`: optional source name.
+- `external_identifier`: optional source ID.
+- `is_active`.
+- `metadata`.
+- timestamps.
+
+Recommended uniqueness:
+
+- unique `(season, normalized_name, normalized_division)`.
+- optional unique `(season, external_source, external_identifier)` when both source fields are present.
+
+Recommendation:
+
+Use season-specific teams only for V1. Avoid a separate permanent `Team` model until the organization needs long-lived team brands independent of season.
+
+### PlayerRosterMembership
+
+Represents one player's roster stint on one season team.
+
+Fields to consider:
+
+- `player`: FK to `players.Player`.
+- `season_team`: FK to `SeasonTeam`.
+- `status`: active, inactive, transferred, removed, injured, guest, or equivalent controlled values.
+- `jersey_number`: optional string.
+- `roster_role`: optional label if needed later.
+- `is_primary`: primary roster assignment for current display/filter defaults.
+- `starts_on`: nullable date.
+- `ends_on`: nullable date.
+- `source`: import/manual source label.
+- `source_identifier`: optional source row/team/player membership ID.
+- `import_batch`: nullable FK to `players.PlayerImportBatch` if player import remains the provenance batch.
+- `source_row`: nullable FK to `players.PlayerSourceRow` if a direct row link is useful.
+- `metadata`.
+- timestamps.
+
+Recommended uniqueness:
+
+- prevent exact duplicate active memberships for the same `(player, season_team, source_identifier)` when source identifier exists.
+- prevent exact duplicate active memberships for the same `(player, season_team, starts_on, ends_on)` when dates are supplied.
+- allow multiple memberships in one season because transfers and multi-team participation are real.
+- enforce only one active primary membership per `(player, season)` where practical.
+
+Current team derivation:
+
+- Current team should be derived from active primary membership in the current season.
+- If no primary exists, derive from the latest active membership in the current season.
+- If no current-season membership exists, return blank or a clear no-current-roster state.
+
+### CoachSeasonAssignment
+
+Represents one coach/user assignment to one season team.
+
+Fields to consider:
+
+- `user`: FK to Django `User`.
+- `season_team`: FK to `SeasonTeam`.
+- `assignment_role`: head coach, assistant coach, coordinator, evaluator, manager, or text/title.
+- `is_primary`.
+- `is_active`.
+- `starts_on`.
+- `ends_on`.
+- `source`.
+- `source_identifier`.
+- `metadata`.
+- timestamps.
+
+Recommended uniqueness:
+
+- prevent duplicate active assignment for the same `(user, season_team, assignment_role)`.
+- allow one coach to be assigned to multiple teams in a season.
+- allow one team to have multiple coaches.
+- optionally enforce one active primary assignment per `(user, season)` where practical.
+
+Important distinction:
+
+`AccountProfile.role` remains permanent platform metadata. `CoachSeasonAssignment.assignment_role` is seasonal team context. Changing a seasonal assignment must not grant Django staff/superuser access and must not rewrite the permanent account role except through existing account services when staff intentionally changes the account role.
+
+## 7. Model Ownership
+
+Recommended ownership:
+
+- New `seasons` app owns `Season`, `SeasonTeam`, `PlayerRosterMembership`, and `CoachSeasonAssignment`.
+- `players` continues to own `Player`, player matching, source identifiers, source rows, and player import orchestration.
+- `accounts` continues to own `User`, `AccountProfile`, `UserPlayerLink`, account provisioning, passwords, roles, and coach account creation/reuse.
+- `analytics` owns evaluation cycles and observations, including submitted evaluation context snapshots.
+
+Why a new `seasons` app is recommended:
+
+- Seasonal participation is shared by players, accounts, analytics, and future roster/attendance/video work.
+- Putting coach assignments in `accounts` would couple account identity to roster history.
+- Putting player memberships in `players` would make player identity responsible for team operations.
+- Putting season teams in `analytics` would make evaluations own roster structure.
+
+Allowed dependencies:
+
+- `seasons` may reference `players.Player` and Django `User`.
+- `players` import services may call `seasons` services to create/update season/team/membership records.
+- `accounts` coach import services may call `seasons` services to create/update coach assignments.
+- `analytics` may reference or snapshot `seasons` records when observations are submitted.
+
+Avoid:
+
+- `seasons` calling analytics services.
+- views directly creating roster memberships or assignments.
+- templates inferring current team from historical memberships.
+
+## 8. Season And Team Design
+
+Season and evaluation cycle should be related but distinct:
+
+- Season = roster/organizational period.
+- Evaluation cycle = feedback window within a season.
+
+Recommended `EvaluationCycle` change:
+
+- Add nullable FK `season` to `Season`.
+- Keep `starts_on` and `ends_on` on `EvaluationCycle`.
+- Allow cycles without a season during compatibility migration.
+- Require a season for new production cycles after Phase 4.
+
+SeasonTeam should be season-specific, not permanent:
+
+- `13U Expos` in 2026 and `13U Expos` in 2027 are separate `SeasonTeam` rows.
+- This prevents future imports from accidentally rewriting prior-year rosters.
+- If the organization later needs long-lived team lineage, add a separate permanent team concept in a future plan.
+
+## 9. Player Roster Membership Design
+
+One player may have multiple memberships in one season.
+
+Supported cases:
+
+- transfer from one team to another;
+- call-up or affiliate/guest participation;
+- concurrent development roster plus game roster;
+- corrected import with same membership.
+
+Primary rules:
+
+- A player should have at most one active primary membership per season.
+- A non-primary membership may be active at the same time.
+- Setting a new active primary membership should demote or end the prior active primary membership through a service, not direct model saves.
+
+Transfer rules:
+
+- Transfers should create a new membership/stint rather than overwriting the old team.
+- The previous membership can receive `ends_on` and status `transferred` or `inactive`.
+- If dates are unknown, use the import date or leave dates null with metadata explaining the source.
+
+## 10. Coach Assignment Design
+
+One coach may have multiple assignments in one season.
+
+Supported cases:
+
+- head coach of one team and assistant coach of another;
+- coordinator across multiple teams;
+- guest evaluator for a team;
+- staff member also coaching.
+
+Assignment role should be separate from account role:
+
+- `AccountProfile.role=coach` means the user is generally a coach in the platform.
+- `CoachSeasonAssignment.assignment_role=head_coach` means the user has a season-team role.
+
+Password behavior:
+
+- Creating a new coach account should set a random temporary password and `must_change_password=True`.
+- Reusing an established coach account for a new season must not reset the password by default.
+- Reused accounts should only be forced to change password if they already require it or staff explicitly chooses a reset.
+
+## 11. Evaluation Context Design
+
+Historical evaluations must retain the context that existed when submitted.
+
+Recommended design:
+
+- Add nullable FK `player_roster_membership` to `Observation`.
+- Add nullable FK `season` to `Observation`.
+- Add nullable FK `season_team` to `Observation`.
+- Add snapshot fields on `Observation`:
+  - `player_season_name`
+  - `player_team_name`
+  - `player_division`
+- Consider evaluator context:
+  - nullable FK `evaluator_coach_assignment` for coach/staff/guest evaluators when available;
+  - snapshot fields `evaluator_team_name`, `evaluator_division`, `evaluator_assignment_role`.
+
+Why FK plus snapshot is recommended:
+
+- FK provides structured filtering and drill-down while the referenced records exist.
+- Snapshot fields preserve display text if season/team names are later corrected.
+- Existing observations can be backfilled with best-known current fields without pretending to reconstruct unsupported history.
+
+Submission behavior:
+
+- When an observation is submitted, resolve player context for the observation cycle's season.
+- Prefer active primary roster membership for `(player, season)`.
+- If none exists, prefer active non-primary membership.
+- If multiple equally valid memberships exist, require staff/evaluator selection or record an unresolved/no-roster context.
+- Snapshot season/team/division before saving submitted state.
+- Do not recalculate snapshots after submission except through an explicit staff correction workflow.
+
+Existing draft or reopened observations:
+
+- Drafts may refresh context until submitted.
+- Reopened observations should preserve the original submitted context unless staff explicitly resubmits with a correction policy.
+
+## 12. Player Import Design
+
+Player import should remain staff-facing and owned by `players/services/import_service.py`, with seasonal participation delegated to season services.
+
+CSV behavior:
+
+- Staff must select a season before preview/confirm, or the CSV must include an accepted season column.
+- `team`/`team_name` and `division` should map to `SeasonTeam`, not permanently overwrite player identity.
+- Identity fields continue to match/create `Player`.
+- Roster fields create/update `PlayerRosterMembership`.
+
+Recommended source fields:
+
+- Permanent player identity: name, preferred name, birthdate, birth year, gender, school, bats, throws, positions.
+- Roster context: season, team, division, jersey number, roster status, starts_on, ends_on, source roster ID.
+- Source identifiers: registration ID, registrant ID, source player ID.
+
+Preview behavior:
+
+- Show matched or new permanent player.
+- Show season.
+- Show season team to be created or reused.
+- Show membership action: create, update, transfer/stint, skip, conflict.
+- Show whether compatibility `Player.team_name` and `division` will be updated for current display.
+
+Confirm behavior:
+
+- Within one transaction per import batch or one safe transaction per row, depending on current service pattern.
+- Create/reuse `Season`.
+- Create/reuse `SeasonTeam`.
+- Create/update `Player`.
+- Create/update `PlayerRosterMembership`.
+- Record `PlayerSourceRow`.
+- Preserve prior memberships.
+
+## 13. Coach Import Design
+
+Coach import should stay in `accounts/services/coach_import_service.py` for account provisioning, with season/team assignment delegated to season services.
+
+CSV behavior:
+
+- Required account fields remain `first_name`, `last_name`, `email`.
+- Staff must select a season before preview/confirm, or the CSV must include an accepted season column.
+- `team` and `division` create/reuse `SeasonTeam`.
+- Assignment fields create/update `CoachSeasonAssignment`.
+
+Recommended optional fields:
+
+- username
+- team
+- division
+- assignment_role
+- is_active
+- starts_on
+- ends_on
+- source_id
+- notes
+
+Account behavior:
+
+- New coach account: create user, role `coach`, active by default unless CSV says inactive, random temporary password, `must_change_password=True`.
+- Existing coach account: reuse account, update assignment, do not reset password by default.
+- Existing non-coach account: conflict unless staff chooses a supported role update through account operations.
+- Existing inactive coach: assignment may be created, but account activation should require explicit import option or account operation.
+
+Result behavior:
+
+- Report users created, coaches reused, assignments created, assignments updated, conflicts, skipped rows, active/inactive accounts.
+- Temporary passwords are shown only for newly created accounts or explicit password reset actions.
+
+## 14. Reimport And Duplicate Behavior
+
+Player reimport should be deterministic:
+
+- Same source identifier and same season team updates the existing membership/provenance.
+- Same permanent player and same season team without source identifier should update the existing active membership if no conflicting dates/status exist.
+- Different team in same season should create a new membership/stint unless staff chooses to transfer/end the prior primary membership.
+- Different season should create a new season-team membership and preserve old membership.
+
+Coach reimport should be deterministic:
+
+- Same email and same season team/assignment role reuses the account and updates the assignment.
+- Same email and different season creates or updates a different assignment.
+- Existing coach password is not reset just because the row is reimported.
+- Duplicate email rows in the same CSV should remain a conflict unless a deterministic merge rule is explicitly added.
+
+Conflicts should block only unsafe rows where possible. Valid rows may continue if the current import workflow supports partial commits and clear result reporting.
+
+## 15. Transfer And Multi-Team Behavior
+
+Transfers:
+
+- Do not edit the prior team out of history.
+- Create a new membership/stint.
+- Mark prior active primary membership inactive/transferred when staff confirms a transfer.
+- Preserve original import provenance.
+
+Multi-team participation:
+
+- Allow concurrent non-primary memberships.
+- Require one active primary membership for current-display defaults when practical.
+- Show all memberships in season history views.
+
+Ambiguous imports:
+
+- If a player has multiple active memberships in the selected season and the CSV row lacks enough team/division information, mark the row for review.
+- Do not guess which membership should receive roster-specific updates.
+
+## 16. Existing Data Migration Strategy
+
+Do not fabricate historical seasons.
+
+Recommended migration:
+
+1. Create a default compatibility season, such as `Legacy / Pre-Season-Aware Data`, or a staff-approved current season such as `2026`.
+2. For every existing player with `team_name` or `division`, create/reuse a `SeasonTeam` in that season.
+3. Create one `PlayerRosterMembership` per player/team/division combination.
+4. Mark membership provenance as `legacy_player_fields`.
+5. For existing observations, set season/team/division context from the player's current legacy fields and mark metadata as `legacy_context_backfill`.
+6. Do not claim the backfilled context is historically exact.
+7. Leave observations with no player team/division as no-roster-context rather than inventing values.
+
+Production safety:
+
+- Use idempotent data migrations or explicit management command with dry-run/review output.
+- Record counts before and after migration.
+- Back up the production database before applying migrations.
+- Run migration in staging or a production copy first.
+
+## 17. Compatibility Strategy For Current Player Fields
+
+`Player.team_name` and `Player.division` should not be deleted immediately.
+
+Recommended staged approach:
+
+- Phase 1: keep fields and populate membership records from them.
+- Phase 2: stop treating them as authoritative in new imports; write seasonal membership records first.
+- Phase 2 compatibility: optionally update `Player.team_name` and `Player.division` from current active primary membership for existing UI compatibility.
+- Phase 4/5: update analytics filters, player search, metrics, and review views to use seasonal context.
+- Later: mark fields deprecated in code/docs.
+- Future cleanup: remove fields only after all reads have moved to season services and production has passed a full release cycle.
+
+Matching-service compatibility:
+
+- `division` may remain a matching hint temporarily.
+- New matching should prefer permanent identifiers/name/birthdate and use season/team only as context, not identity.
+
+## 18. Evaluation-Cycle Relationship
+
+Season and evaluation cycle are related but not identical.
+
+Recommended rule:
+
+- A season may have many evaluation cycles.
+- An evaluation cycle may belong to one season.
+- Evaluations should use their cycle's season as the first context lookup.
+
+Examples:
+
+- `2026 Spring` season may include `Preseason Evaluation`, `Midseason Check-In`, and `Year-End Evaluation` cycles.
+- A winter clinic cycle may belong to a clinic season or have no season during compatibility migration.
+
+If a cycle has no season:
+
+- Submission should fall back to current player membership only during compatibility.
+- The observation should clearly mark context source as fallback in metadata.
+
+## 19. Permission Implications
+
+Do not introduce team-restricted permissions in the first schema phase unless explicitly approved.
+
+Future likely rules:
+
+- Staff/admin can manage all seasons, rosters, assignments, and evaluations.
+- Coaches may eventually evaluate players on assigned teams.
+- Coaches may review evaluations according to assignment scope.
+- Players may evaluate players in allowed peer scope, likely same season/team or approved cycle.
+- Guest evaluators may be scoped by explicit assignment or staff-created access.
+
+Dependencies before enforcing team scope:
+
+- reliable `CoachSeasonAssignment` records;
+- reliable player memberships;
+- active season defaults;
+- clear exception rules for guest evaluators and coordinators;
+- privacy review for player peer-evaluation scope.
+
+## 20. Security And Privacy
+
+- Do not expose all roster history to players unless a player-facing policy approves it.
+- Player-facing evaluations should continue to hide evaluator names unless policy changes.
+- Coach review filters should not grant access to users without review permission.
+- Account role metadata must not grant Django `is_staff` or `is_superuser`.
+- Coach assignment role must not grant account permissions by itself.
+- Temporary passwords must not be reset or displayed for reused coach accounts unless staff explicitly performs a password reset.
+- Import provenance may contain sensitive source-row data and should remain staff/admin-only.
+- Seasonal records should preserve history through inactive/end-dated rows rather than destructive deletion.
+
+## 21. Performance And Indexing
+
+Likely indexes:
+
+- `Season`: `key`, `is_active`, `is_current`, `starts_on`, `ends_on`.
+- `SeasonTeam`: `(season, normalized_division, normalized_name)`, `(season, division)`, `(is_active, season)`.
+- `PlayerRosterMembership`: `(player, season_team)`, `(season_team, is_active)`, `(player, is_primary, is_active)`, `(starts_on, ends_on)`, optional source identifier fields.
+- `CoachSeasonAssignment`: `(user, season_team)`, `(season_team, is_active)`, `(user, is_primary, is_active)`, assignment role.
+- `Observation`: `season`, `season_team`, `player_roster_membership`, `(season, season_team, status)`, `(evaluation_cycle, season_team, status)`.
+- `EvaluationCycle`: `season`, `(season, is_active)`.
+
+Query patterns to optimize:
+
+- current roster for season/team;
+- player season history;
+- coach assignments by season/team;
+- evaluation review filters by season/team/division/cycle;
+- command center metrics by season/team/division/cycle;
+- import preview duplicate detection.
+
+Use `select_related()` for season/team/membership references in evaluation review and timeline services.
+
+## 22. Proposed Implementation Phases
+
+### Phase 0 - Decisions And Compatibility
+
+- Finalize naming: app name, model names, status values, and assignment roles.
+- Decide active/current season behavior.
+- Decide whether `EvaluationCycle.season` is required for new cycles.
+- Decide legacy backfill season name.
+- Decide compatibility-write policy for `Player.team_name` and `Player.division`.
+- Document accepted transfer and multi-team behavior.
+
+### Phase 1 - Season, Team, And Player Membership Foundation
+
+- Add `seasons` app and models.
+- Add services for season lookup, team lookup, player membership creation/update, current membership derivation, and legacy backfill helpers.
+- Add admin configuration.
+- Add migrations.
+- Backfill legacy player team/division into memberships.
+- Keep existing import/UI behavior unchanged except compatibility display helpers if required.
+
+### Phase 2 - Season-Aware Player Import
+
+- Add season selection to player import.
+- Map team/division to `SeasonTeam`.
+- Create/update `PlayerRosterMembership`.
+- Preserve `PlayerSourceRow` provenance.
+- Maintain compatibility fields from current primary membership if approved.
+- Update import preview, conflict review, confirm, and tests.
+
+### Phase 3 - Coach Seasonal Assignment
+
+- Add season selection to coach import.
+- Map team/division to `SeasonTeam`.
+- Create/update `CoachSeasonAssignment`.
+- Reuse existing coach accounts without password reset by default.
+- Report assignment results separately from account creation/reuse.
+- Add tests for existing-account password preservation.
+
+### Phase 4 - Evaluation Context
+
+- Add `EvaluationCycle.season`.
+- Add observation season/team/membership references and snapshot fields.
+- Backfill existing observations with legacy context.
+- Update observation creation/submission services to snapshot context at submission.
+- Update player-facing, coach-facing, and staff review read models to use snapshots.
+- Preserve submitted snapshots across later roster changes.
+
+### Phase 5 - Read Models And UI
+
+- Add staff roster history views if needed.
+- Update player profile/timeline to show season history.
+- Update player search, command center, coach review, and metrics filters to use season-aware services.
+- Add safe empty states for no current roster.
+- Keep templates presentation-only.
+
+### Phase 6 - Production Review And Freeze
+
+- Architecture review.
+- Migration review on production copy.
+- Security/privacy review.
+- Performance review for season/team filters.
+- User manual and deployment documentation reconciliation.
+- Production readiness and rollback plan.
+
+## 23. Test Strategy
+
+Model/service tests:
+
+- season uniqueness and current/active behavior;
+- season-team uniqueness within season;
+- player may have memberships in multiple seasons;
+- player may have multiple memberships in one season;
+- primary membership constraints;
+- transfers preserve old membership;
+- coach may have multiple assignments;
+- coach assignment role does not change account permissions;
+- current membership derivation.
+
+Import tests:
+
+- player import creates/reuses season and season team;
+- player import creates permanent player once across seasons;
+- reimport updates membership deterministically;
+- import with new season preserves previous membership;
+- transfer import creates new stint;
+- ambiguous multi-team import requires review;
+- coach import creates assignment;
+- coach reimport reuses account and assignment;
+- existing coach password is not reset on seasonal reimport.
+
+Analytics tests:
+
+- submitted observation snapshots player season/team/division;
+- later roster change does not change old evaluation display;
+- evaluation cycle season drives context lookup;
+- no roster context is handled safely;
+- coach review filters by season/team/division;
+- player My Evaluations keeps privacy rules;
+- metrics use season-aware filters without changing access rules.
+
+Migration tests:
+
+- legacy player fields produce a compatibility season/team/membership;
+- existing observations receive backfilled context with metadata;
+- blank legacy fields do not produce fabricated teams;
+- migration is idempotent where practical.
+
+Regression tests:
+
+- existing player import still works during compatibility phase;
+- existing coach import still works during compatibility phase;
+- account operations unchanged;
+- existing evaluation submission/review permissions unchanged unless a phase explicitly changes them.
+
+## 24. Deployment And Rollback Considerations
+
+Deployment should be staged:
+
+1. Deploy schema-only season foundation with compatibility reads intact.
+2. Run legacy backfill in staging or a production database copy.
+3. Verify counts and spot-check player histories.
+4. Deploy player import changes after foundation is stable.
+5. Deploy coach assignment changes after player seasonal model is proven.
+6. Deploy evaluation context changes with a tested observation backfill.
+7. Update UI/read models after data is available.
+
+Rollback considerations:
+
+- Do not remove `Player.team_name` or `Player.division` during early phases.
+- Do not make new non-null FKs on existing observations in the first migration.
+- Use nullable references and snapshot fields while backfill is validated.
+- Keep compatibility display paths until a full production cycle has passed.
+- Back up the database before data migrations.
+- Avoid irreversible destructive migrations.
+
+## 25. Risks
+
+- Existing production data may not contain enough information to reconstruct true historical season/team context.
+- Backfilled evaluations could be mistaken for exact historical truth unless metadata and documentation are clear.
+- Primary membership constraints can be difficult to enforce perfectly on all databases with nullable dates.
+- Coach import currently resets reused coach passwords; this must change before season-aware reimports.
+- Existing analytics filters and metrics currently read from `Player.team_name` and `Player.division`.
+- Introducing team-scoped permissions too early could block valid evaluators.
+- A new `seasons` app creates a shared dependency that needs clear service boundaries.
+- Transfer handling requires staff UX decisions, not just schema.
+
+## 26. Open Questions
+
+- What is the official season naming convention for VCB?
+- Should there be exactly one current season?
+- Should evaluation cycles be required to have a season after migration?
+- What legacy season should existing production data use?
+- Should current `Player.team_name` and `division` be maintained as cached compatibility fields, or only deprecated and left untouched?
+- What roster statuses are needed for V1?
+- What coach assignment roles are needed for V1?
+- Should staff be able to manually edit memberships and assignments in admin only, or through first-class UI?
+- How should imported transfer rows explicitly signal transfer versus concurrent membership?
+- Should player peer-evaluation scope eventually be limited to same season/team?
+
+## 27. Recommended First Implementation Phase
+
+Start with Phase 0 - Decisions And Compatibility.
+
+Do not begin models or migrations until the following are explicitly decided:
+
+- season naming and current-season policy;
+- legacy backfill season;
+- compatibility policy for `Player.team_name` and `Player.division`;
+- required relationship between `EvaluationCycle` and `Season`;
+- primary membership rules;
+- coach assignment roles;
+- whether a new `seasons` app is accepted as the shared owner.
+
+After those decisions, Phase 1 should add the model foundation and legacy backfill without changing user-facing import or evaluation workflows.
+
+## 28. Acceptance Criteria
+
+The Seasonal Participation V1 plan is acceptable when:
+
+- permanent players are reused across seasons;
+- permanent coach accounts are reused across seasons;
+- seasonal team history is preserved;
+- future imports do not recreate people unnecessarily;
+- historical evaluations retain season/team/division context;
+- reimports are deterministic;
+- transfers and multi-team cases are handled;
+- password behavior for existing coaches is safe;
+- existing production data has a migration strategy;
+- current `Player.team_name` and `division` have a compatibility plan;
+- evaluation cycles and seasons have a defined relationship;
+- subsystem ownership is clear;
+- migration phases are safe and reversible where practical;
+- tests and deployment steps are defined;
+- no application code changed during this planning task.
+
```
