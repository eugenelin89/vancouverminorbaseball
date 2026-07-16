# Prompt 77 - Platform

App/subsystem: platform

Work commit: `36d4e25`

Terminal state: `PASS`

## User Prompt

```text
Implement Seasonal Participation V1 Phase 4 only: Season-Aware Evaluation Context.

Use continuous loop engineering.

Continue until the Phase 4 scope is production-ready, fully reviewed, documented, tested, committed, pushed, and the working tree is clean.

Do not start Phase 5 or later work.

==================================================
Current State
=============

Seasonal Participation V1 Phases 1 through 3 are complete.

The repository now includes:

* permanent player identity;
* permanent account identity;
* seasons;
* season-specific teams;
* player roster memberships;
* coach seasonal assignments;
* season-aware player import;
* season-aware coach import;
* permanent player and coach reuse across seasons;
* preserved roster and assignment history;
* no password reset for returning coaches.

Phase 3 explicitly deferred evaluation seasonal context.

Verified production state before the seasonal work began:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

However, before creating any migration, inspect the current production-readiness assumptions and design defensively in case observations now exist in development or other environments.

==================================================
Phase 4 Objective
=================

Make the evaluation workflow season-aware while preserving existing evaluation behavior.

Every new evaluation must have clear seasonal context.

At minimum, a submitted evaluation must preserve:

* season;
* player roster membership;
* player team;
* player division;
* evaluator coach assignment where applicable;
* evaluator team and role snapshot where applicable.

Historical evaluations must not change when:

* a player changes teams;
* a coach changes teams;
* a player has multiple memberships;
* a coach has multiple assignments;
* team display names are corrected;
* compatibility fields change;
* the current season changes.

Do not implement reporting dashboards, roster-management pages, or compatibility-field removal in Phase 4.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete Phase 4 implementation, review, documentation, or verification work remains.

PASS

All Phase 4 acceptance criteria are satisfied, verification passes, commits are pushed, and the working tree is clean.

BLOCKED

A necessary decision requires unresolved product direction, destructive migration, external infrastructure, or architecture expansion outside Phase 4.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied acceptance criterion.

Do not continue through speculative or cosmetic refactoring.

==================================================
Established Loop Workflow
=========================

Every loop must complete the full repository workflow.

Each loop must:

1. Reconcile the current committed repository state.
2. Read `AGENTS.md`, the seasonal plan, evaluation documentation, and relevant prompt archives.
3. Confirm the working tree is clean.
4. Inspect the complete evaluation workflow.
5. Identify concrete incomplete acceptance criteria or verified defects.
6. Create the next prompt archive before implementation according to `AGENTS.md`.
7. Implement only selected Phase 4 work.
8. Add or update focused tests.
9. Run focused verification.
10. Perform senior-engineer self-review.
11. Fix every verified issue.
12. Update relevant documentation.
13. Run the complete verification suite.
14. Commit implementation, tests, migrations, and documentation.
15. Finalize the prompt archive with commit hash, review findings, verification results, and terminal state.
16. Commit the prompt archive separately.
17. Push both commits.
18. Re-read the committed diff.
19. Confirm the working tree is clean.
20. Reassess every Phase 4 acceptance criterion.
21. Choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS.
22. If CONTINUE, begin the next loop without requesting confirmation.

Each loop must create:

1. one implementation/review/documentation commit;
2. one prompt archive commit.

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
* all relevant evaluation documentation
* Analytics implementation/status documentation
* prompt archives for:

  * evaluation access;
  * self-evaluation;
  * coach review;
  * seasonal foundation;
  * player import;
  * coach import.

Inspect:

* `analytics/models.py`
* `analytics/forms.py`
* `analytics/views.py`
* `analytics/urls.py`
* `analytics/services/`
* observation creation/submission services
* evaluation permission services
* evaluation cycle services
* coach review services
* staff review services
* player-facing evaluation services
* evaluation templates
* `analytics/tests.py`
* `seasons/models.py`
* `seasons/services/membership_service.py`
* `seasons/services/coach_assignment_service.py`
* `accounts/services/permissions.py`
* `accounts/services/link_service.py`
* current self-evaluation behavior
* current peer-evaluation behavior
* current role/perspective snapshot behavior.

==================================================
Core Design
===========

Keep permanent identity references.

`Observation` should continue to reference:

* permanent `Player`;
* permanent evaluator `User`;
* evaluation cycle;
* evaluation perspective.

Add seasonal context without replacing permanent identity.

Recommended model additions:

* `EvaluationCycle.season`
* `Observation.season`
* `Observation.player_roster_membership`
* `Observation.evaluator_coach_assignment`

Add immutable snapshot fields where appropriate:

* `player_team_name_snapshot`
* `player_division_snapshot`
* `season_name_snapshot`
* `season_key_snapshot`
* `evaluator_team_name_snapshot`
* `evaluator_division_snapshot`
* `evaluator_assignment_role_snapshot`

Use repository-consistent names if better terminology already exists.

Prefer:

* FK references for structured filtering;
* snapshot fields for historical display stability.

Do not rely solely on live FK values for historical display.

==================================================
Evaluation Cycle And Season
===========================

Treat `Season` and `EvaluationCycle` as distinct concepts.

Relationship:

```text
Season
    has many EvaluationCycles
```

Implement:

* nullable `EvaluationCycle.season` initially for migration safety;
* season required through application workflows for newly created or activated production evaluation cycles;
* existing cycles without a season remain readable;
* staff should be prevented from creating a new usable cycle without selecting a season.

Do not fabricate a season for legacy cycles.

If production or development contains existing cycles:

* leave them nullable;
* do not guess which season they belong to;
* document manual assignment where appropriate.

==================================================
Observation Seasonal Context
============================

Add nullable FK fields initially:

* season;
* player roster membership;
* evaluator coach assignment.

New observations created after Phase 4 must receive seasonal context before submission.

For submitted observations, snapshot fields become authoritative for historical display.

Requirements:

* observation season should normally come from the evaluation cycle;
* player membership must belong to the observation player;
* player membership must belong to the observation season;
* evaluator coach assignment, if present, must belong to the evaluator;
* evaluator coach assignment must belong to the observation season;
* evaluator assignment is optional for player self-evaluation, peer evaluation, staff evaluation, administrator evaluation, and guest evaluation unless repository rules require otherwise.

Do not allow mismatched season, player, membership, evaluator, or assignment references.

==================================================
Context Resolution Rules
========================

Create a focused service to resolve evaluation context.

Likely service name:

```text
analytics/services/evaluation_context_service.py
```

Use repository-consistent naming.

It should resolve:

* season;
* player roster membership;
* evaluator coach assignment;
* player team/division snapshot values;
* evaluator team/division/role snapshot values.

## Season

Preferred source:

1. evaluation cycle season;
2. explicit server-controlled workflow context if the cycle is legacy and unassigned;
3. otherwise block new submission.

Do not trust a client-supplied season independently from the cycle.

## Player Membership

Preferred resolution:

1. selected server-validated player membership;
2. unique active primary membership for the evaluation season;
3. if no primary exists but exactly one active membership exists, use it;
4. if multiple active memberships exist and no safe primary exists, require staff/player choice or block submission;
5. do not guess.

## Evaluator Assignment

For coach evaluations:

1. determine active assignments for evaluator in evaluation season;
2. if the evaluator has an assignment to the player’s team, prefer it;
3. if exactly one relevant assignment exists, use it;
4. if multiple plausible assignments exist, require a server-validated choice or block submission;
5. do not guess.

For non-coach perspectives:

* assignment may be null;
* evaluator role/perspective snapshot remains required according to existing behavior.

==================================================
Submission Snapshot Behavior
============================

Draft observations may refresh seasonal context before first submission.

When an observation is submitted:

* set snapshot fields;
* preserve them immutably;
* do not silently change them if the player or coach later changes teams;
* do not refresh them on normal reads;
* do not refresh them merely because a season becomes inactive;
* do not refresh them because a team name changes.

For reopened or administratively corrected observations:

Use a clear contract.

Recommended behavior:

* preserve original snapshots by default;
* allow explicit service-driven resnapshot only for a documented administrative correction;
* do not resnapshot through ordinary edit/save paths.

==================================================
Self-Evaluation
===============

Preserve current self-evaluation behavior.

For a self-evaluation:

* evaluator and player remain linked through the active self `UserPlayerLink`;
* perspective remains `self`;
* season comes from evaluation cycle;
* player roster membership resolves for that player and season;
* evaluator coach assignment remains null;
* snapshots clearly identify the evaluation as self-evaluation and preserve player season/team context.

If the player has multiple active memberships and no primary membership:

* do not silently choose;
* require a safe workflow decision or block submission with a clear message.

==================================================
Peer Evaluation
===============

Preserve current peer-evaluation access behavior unless seasonal context makes the current workflow impossible.

Phase 4 should not yet introduce broad team-scoped peer permissions unless already required by the existing access contract.

However:

* peer evaluation must preserve the target player’s season/team context;
* evaluator assignment may remain null;
* document that future team-scoped peer restrictions are deferred.

Do not accidentally allow cross-season evaluation.

==================================================
Coach Evaluation
================

Coach evaluation must use season-aware player selection.

Requirements:

* coach chooses an evaluation cycle;
* cycle determines season;
* selectable players must have roster membership in that season;
* coach assignment context must resolve safely;
* if current permissions allow all players, do not silently tighten permissions beyond approved scope;
* if current workflow already limits coach access, convert it to seasonal memberships/assignments.

Separate:

* seasonal context;
* authorization.

Do not make `CoachSeasonAssignment` an authorization grant unless the existing permissions plan explicitly requires it in this phase.

If team-based permission enforcement is too large or materially changes product behavior, preserve current authorization and document stricter team scope as deferred.

==================================================
Staff And Administrator Evaluation
==================================

Staff/admin evaluation should:

* select a cycle;
* use the cycle season;
* select players from that season;
* preserve player membership/team/division snapshots;
* allow evaluator assignment to remain null unless staff also has a relevant coach assignment and repository rules use it.

Do not force staff accounts to have coach assignments.

==================================================
Player Selection
================

Make evaluation player selectors season-aware.

Once an evaluation cycle is selected:

* show only players with membership in the cycle season;
* avoid duplicate player rows when a player has multiple memberships;
* display enough roster context to distinguish memberships;
* if membership selection matters, display team/division;
* preserve permanent player identity.

Possible display:

```text
Christopher Lin — 13U Dodgers
```

For multiple memberships:

```text
Christopher Lin — 13U Dodgers
Christopher Lin — 13U Expos
```

Only show multiple entries when the workflow genuinely needs membership selection.

Do not expose raw IDs unnecessarily.

==================================================
Evaluation Drafts
=================

Review draft creation and editing.

Requirements:

* drafts store seasonal FK context;
* context can be recalculated while still draft if the server-controlled cycle or membership selection changes;
* submitted snapshots remain stable;
* draft access rules remain unchanged;
* no cross-season player switch through manipulated request data.

==================================================
Coach Review
============

Update coach review read models and filters to use seasonal context.

At minimum, display:

* season;
* team snapshot;
* division snapshot;
* evaluation perspective.

Add season filtering if consistent with existing review UX.

Do not build new dashboards.

Historical review must show submitted snapshots rather than current player team fields.

==================================================
Staff Review And Analytics Tables
=================================

Update current staff-facing evaluation tables only as needed to display and filter the new seasonal context.

Use:

* observation snapshots for historical display;
* FK references for filtering where available;
* compatibility fallback only for legacy observations without seasonal context.

Do not implement new charts, comparisons, or Platform V2 summaries.

==================================================
Legacy Observations
===================

Before migration, inspect current data assumptions and tests.

Because verified production originally had zero observations, the expected production migration is additive and may require no backfill.

Do not assume all environments are empty.

Migration behavior:

* add nullable fields;
* do not fabricate seasons;
* do not fabricate memberships;
* do not fabricate coach assignments;
* leave legacy observations with null seasonal context;
* preserve current display through compatibility fallbacks;
* mark or display them as `Legacy / No Season` where appropriate.

If observations now exist in production before deployment:

* stop deployment;
* create a reviewed backfill plan;
* do not guess historical context.

Document a pre-deployment count check.

==================================================
Migration
=========

Authorized additive migrations may include:

* `EvaluationCycle.season`
* seasonal FK fields on `Observation`
* snapshot fields on `Observation`
* required indexes and constraints.

Requirements:

* nullable initially;
* SQLite-safe;
* no fabricated data;
* no destructive field removal;
* no `Player.team_name` removal;
* no `Player.division` removal;
* no data migration unless repository inspection proves deterministic, non-fabricated data exists.

Review migration plan carefully.

==================================================
Validation And Constraints
==========================

Use model validation and services to enforce:

* observation player matches membership player;
* observation season matches membership season;
* evaluation-cycle season matches observation season;
* evaluator matches coach assignment user;
* evaluator assignment season matches observation season;
* submitted observation has required snapshots;
* draft may remain partially contextual only when workflow explicitly permits it.

Use database constraints where practical, but do not force cross-table constraints that Django/SQLite cannot safely enforce.

Service validation is authoritative for cross-model consistency.

==================================================
Forms And Request Security
==========================

Do not trust hidden fields for:

* season;
* player roster membership;
* evaluator assignment;
* team;
* division;
* snapshot values.

Server must derive or validate all context.

Prevent:

* changing player membership to another player’s membership;
* selecting a membership from another season;
* selecting a coach assignment belonging to another user;
* submitting an observation against a cycle from another season;
* changing snapshot values through client input.

Snapshot fields must never be editable from normal forms.

==================================================
Permissions
===========

Preserve current role and access behavior unless seasonal context requires a narrowly scoped correction.

Do not automatically introduce:

* strict team-only coach access;
* seasonal assignment-based authorization;
* peer team restrictions;
* parent permissions.

Those may be future phases.

However, ensure no user can submit against:

* an inactive or inaccessible cycle;
* an invalid player;
* a player outside the cycle season;
* a membership outside the cycle season.

==================================================
Admin
=====

Update Django admin for:

* evaluation-cycle season;
* observation seasonal FK fields;
* read-only snapshot fields.

Admin requirements:

* useful season filters;
* team/division snapshot display where useful;
* snapshot fields read-only;
* no unsafe resnapshot through ordinary admin saves;
* no mismatch between player and membership;
* no mismatch between evaluator and assignment.

If admin editing risks violating invariants, use validation or restrict fields.

==================================================
Documentation
=============

Update:

* `docs/USER_MANUAL.md`
* `docs/ARCHITECTURE.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* relevant Analytics/evaluation documentation
* deployment runbook only for the pre-migration observation count check, if appropriate.

Document:

* evaluation cycle and season relationship;
* player roster context;
* coach assignment context;
* snapshot behavior;
* self-evaluation behavior;
* coach evaluation behavior;
* staff/admin behavior;
* historical display guarantees;
* legacy/no-season behavior;
* current limitations;
* Phase 4 completion;
* next phase.

Do not describe future roster management or reports as implemented.

==================================================
Phase 4 Non-Goals
=================

Do not implement:

* season administration pages;
* roster-management dashboards;
* coach assignment management pages;
* player season-history pages;
* new analytics dashboards;
* season comparison reports;
* longitudinal reports;
* Platform V2 player summaries;
* stricter team-based coach permissions unless already required;
* peer team restrictions;
* parent access;
* notifications;
* exports;
* APIs;
* JavaScript frameworks;
* removal of `Player.team_name`;
* removal of `Player.division`;
* permanent Team model;
* migration of PDP data.

==================================================
Required Test Coverage
======================

## Evaluation Cycle

* cycle can reference season;
* new usable cycle requires season through workflow;
* legacy cycle without season remains readable;
* inactive/invalid season rejected where appropriate.

## Context Resolution

* observation season derives from cycle;
* correct player membership resolves;
* player/membership mismatch rejected;
* season/membership mismatch rejected;
* unique active primary membership used;
* single active non-primary fallback works if contract allows;
* ambiguous multiple memberships blocked;
* coach assignment resolves for coach evaluation;
* evaluator/assignment mismatch rejected;
* assignment/season mismatch rejected.

## Snapshot Behavior

* submitted observation stores season/team/division snapshots;
* coach assignment snapshots stored where applicable;
* later roster changes do not alter snapshots;
* later team display-name changes do not alter snapshots;
* later coach assignment changes do not alter snapshots;
* ordinary edits do not resnapshot submitted observation;
* drafts may refresh before submission according to contract.

## Self-Evaluation

* self-evaluation remains allowed;
* self perspective preserved;
* player membership context stored;
* no evaluator coach assignment required;
* ambiguous player memberships handled safely.

## Peer Evaluation

* peer behavior remains available according to current rules;
* target player season context preserved;
* cross-season target rejected;
* no accidental team-scope expansion.

## Coach Evaluation

* player selector uses cycle season;
* valid coach evaluation stores player and evaluator context;
* multiple coach assignments resolved safely;
* manipulated assignment rejected;
* password/account behavior unaffected.

## Staff/Admin Evaluation

* staff can select players in cycle season;
* staff does not require coach assignment;
* player context snapshot stored.

## Review Pages

* coach review displays season/team/division snapshots;
* staff review displays historical snapshots;
* legacy observation displays safely;
* season filters work if implemented;
* no current Player team field overwrites historical display.

## Security

* client cannot forge season;
* client cannot forge membership;
* client cannot forge evaluator assignment;
* client cannot submit snapshots;
* cross-player membership rejected;
* cross-season membership rejected;
* inactive/inaccessible cycle rejected.

## Migration

* migrations apply to empty database;
* nullable legacy records remain valid;
* no seasons or memberships fabricated;
* new observations use required context through service workflow.

## Regression

* player import remains season-aware;
* coach import remains season-aware;
* existing account behavior unchanged;
* self-evaluation remains functional;
* evaluation perspective labels remain correct;
* draft workflows remain working;
* PDP remains working.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
git diff --check
```

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

* permanent identity versus seasonal context;
* snapshot immutability;
* incorrect dynamic historical display;
* player/membership mismatch;
* evaluator/assignment mismatch;
* cycle/season mismatch;
* draft versus submitted behavior;
* cross-season manipulation;
* client-controlled snapshot values;
* authorization drift;
* accidental team-based permission expansion;
* nullable legacy behavior;
* migration safety;
* indexes and query patterns;
* N+1 queries;
* stale docs;
* accidental Phase 5+ work.

Fix every verified issue before committing.

==================================================
Phase 4 Acceptance Criteria
===========================

Do not declare PASS until all criteria are satisfied.

A. Evaluation Cycles

* cycle-season relationship exists;
* new workflows require season;
* legacy cycles remain readable.

B. Observation Context

* new observations store season;
* player membership stored where required;
* evaluator assignment stored where applicable;
* mismatches rejected.

C. Historical Snapshots

* submitted snapshots are durable;
* later roster/team/assignment changes do not alter display;
* snapshot fields are not client-controlled.

D. Evaluation Perspectives

* self, peer, coach, staff, and guest behavior remains correct;
* seasonal context does not alter perspective labels.

E. Player Selection

* selectors use evaluation-cycle season;
* cross-season players rejected;
* multiple-membership ambiguity handled safely.

F. Coach Context

* coach assignment resolved safely;
* evaluator assignment is not fabricated;
* staff/admin do not require coach assignment.

G. Reviews

* coach and staff review display historical season/team/division context;
* legacy observations remain readable.

H. Security

* season, membership, assignment, and snapshots cannot be forged;
* cross-player and cross-season combinations are rejected.

I. Migration

* additive and SQLite-safe;
* nullable legacy support;
* no fabricated history;
* migration plan reviewed.

J. Tests

* focused and full suites pass;
* snapshot regressions covered;
* manipulation cases covered;
* imports and accounts remain stable.

K. Documentation

* Phase 4 accurately documented;
* historical guarantees explained;
* future phases not described as complete;
* next phase identified clearly.

L. Git

* implementation commit exists;
* prompt archive commit exists;
* both pushed;
* working tree clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally:

1. add cycle-season and observation context fields;
2. add schema migration;
3. implement evaluation context service;
4. integrate observation creation/submission;
5. update season-aware selectors;
6. update review read models;
7. add snapshot behavior;
8. add comprehensive tests;
9. update documentation;
10. run full verification;
11. commit, archive, push, and reassess.

If material defects remain, continue into additional loops.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* satisfies an unsatisfied acceptance criterion;
* fixes a verified historical-data, authorization, or context-integrity defect;
* prevents forged or mismatched context;
* strengthens snapshot immutability;
* adds missing regression proof;
* corrects material documentation drift.

Formatting-only work does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* player submitting self-evaluation;
* player submitting peer evaluation;
* coach evaluating players;
* coach with multiple assignments;
* staff evaluating players;
* staff reviewing historical evaluations;
* data architect reviewing longitudinal integrity;
* security reviewer manipulating form data;
* release engineer reviewing migrations.

Confirm:

* historical evaluations retain correct season/team context;
* player and coach imports remain unchanged;
* no roster-management or reporting expansion occurred;
* no compatibility fields were removed;
* no Phase 5+ work was introduced.

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
   * context-resolution rules;
   * snapshot behavior;
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
Implement season-aware evaluation context
```

==================================================
Final Report
============

Report:

* terminal state;
* loops completed;
* objective of each loop;
* files created;
* files modified;
* migration changes;
* evaluation-cycle season behavior;
* observation context fields;
* player membership resolution;
* evaluator assignment resolution;
* snapshot behavior;
* self-evaluation behavior;
* peer-evaluation behavior;
* coach-evaluation behavior;
* staff/admin behavior;
* review-page behavior;
* legacy observation behavior;
* security protections;
* tests added;
* focused verification;
* full verification;
* documentation updates;
* deferred Phase 5+ work;
* commits;
* push results;
* confirmation that the working tree is clean.
```

## Implementation Notes

Terminal state: PASS

Implementation commit: `36d4e25`

Summary:
- Added nullable `EvaluationCycle.season` and seasonal context fields on `Observation`.
- Added `analytics.services.evaluation_context_service` to resolve player roster membership, coach assignment, and immutable display snapshots.
- Integrated context resolution into observation creation/submission and season-aware player selectors.
- Updated coach/staff review displays and filters to use submitted snapshots with legacy fallback.
- Updated admin, tests, deployment runbook, user manual, and seasonal architecture/status docs.

Migration summary:
- Added additive SQLite-safe Analytics migration `0004_evaluationcycle_season_and_more`.
- No destructive field removals.
- No fabricated seasons, memberships, assignments, or observation backfill.

Verification:
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py check`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py migrate --plan`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py test players`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py test drafts`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py test pdp`
- `DJANGO_SECRET_KEY=test-only-not-production python manage.py test`
- `git diff --check`

Remaining criteria:
- Phase 4 acceptance criteria satisfied.
- Phase 5 read-model/UI work remains deferred.

## Implementation Commit Diff

```text
commit 36d4e25b22b6f5244725dd0483ccbad189297ebd
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 15 23:45:29 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 15 23:45:29 2026 -0700

    Implement season-aware evaluation context

diff --git a/analytics/admin.py b/analytics/admin.py
index b1c1ea9..fe1f86b 100644
--- a/analytics/admin.py
+++ b/analytics/admin.py
@@ -18,8 +18,8 @@ class TimeStampedAdmin(admin.ModelAdmin):
 
 @admin.register(EvaluationCycle)
 class EvaluationCycleAdmin(TimeStampedAdmin):
-    list_display = ("name", "cycle_type", "is_active", "starts_on", "ends_on", "coach_assessment_question_set")
-    list_filter = ("is_active", "cycle_type")
+    list_display = ("name", "cycle_type", "season", "is_active", "starts_on", "ends_on", "coach_assessment_question_set")
+    list_filter = ("is_active", "cycle_type", "season")
     search_fields = ("name", "slug")
     prepopulated_fields = {"slug": ("name",)}
 
@@ -95,6 +95,7 @@ class ObservationAdmin(TimeStampedAdmin):
     list_display = (
         "player",
         "evaluation_cycle",
+        "season",
         "observation_type",
         "status",
         "evaluator",
@@ -102,7 +103,7 @@ class ObservationAdmin(TimeStampedAdmin):
         "evaluation_perspective",
         "submitted_at",
     )
-    list_filter = ("status", "observation_type", "evaluation_cycle", "evaluator_role_key", "evaluation_perspective", "source")
+    list_filter = ("status", "season", "observation_type", "evaluation_cycle", "evaluator_role_key", "evaluation_perspective", "source")
     search_fields = ("player__first_name", "player__last_name", "evaluator__username", "evaluator__email")
     readonly_fields = TimeStampedAdmin.readonly_fields + (
         "submitted_at",
@@ -110,6 +111,13 @@ class ObservationAdmin(TimeStampedAdmin):
         "evaluator_role_key",
         "evaluator_role_name",
         "evaluation_perspective",
+        "season_name_snapshot",
+        "season_key_snapshot",
+        "player_team_name_snapshot",
+        "player_division_snapshot",
+        "evaluator_team_name_snapshot",
+        "evaluator_division_snapshot",
+        "evaluator_assignment_role_snapshot",
     )
     inlines = [ObservationResponseInline]
 
diff --git a/analytics/migrations/0004_evaluationcycle_season_and_more.py b/analytics/migrations/0004_evaluationcycle_season_and_more.py
new file mode 100644
index 0000000..5389df7
--- /dev/null
+++ b/analytics/migrations/0004_evaluationcycle_season_and_more.py
@@ -0,0 +1,86 @@
+# Generated by Django 4.2.25 on 2026-07-16 06:16
+
+from django.db import migrations, models
+import django.db.models.deletion
+
+
+class Migration(migrations.Migration):
+
+    dependencies = [
+        ('seasons', '0001_initial'),
+        ('analytics', '0003_remove_observation_analytics_unique_coach_assessment_per_evaluator_and_more'),
+    ]
+
+    operations = [
+        migrations.AddField(
+            model_name='evaluationcycle',
+            name='season',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='evaluation_cycles', to='seasons.season'),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='evaluator_assignment_role_snapshot',
+            field=models.CharField(blank=True, editable=False, max_length=80),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='evaluator_coach_assignment',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='observations', to='seasons.coachseasonassignment'),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='evaluator_division_snapshot',
+            field=models.CharField(blank=True, editable=False, max_length=80),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='evaluator_team_name_snapshot',
+            field=models.CharField(blank=True, editable=False, max_length=120),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='player_division_snapshot',
+            field=models.CharField(blank=True, editable=False, max_length=80),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='player_roster_membership',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='observations', to='seasons.playerrostermembership'),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='player_team_name_snapshot',
+            field=models.CharField(blank=True, editable=False, max_length=120),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='season',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='observations', to='seasons.season'),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='season_key_snapshot',
+            field=models.CharField(blank=True, editable=False, max_length=80),
+        ),
+        migrations.AddField(
+            model_name='observation',
+            name='season_name_snapshot',
+            field=models.CharField(blank=True, editable=False, max_length=120),
+        ),
+        migrations.AddIndex(
+            model_name='evaluationcycle',
+            index=models.Index(fields=['season', 'is_active'], name='analytics_e_season__ed70e0_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='observation',
+            index=models.Index(fields=['season', 'status'], name='analytics_o_season__b14210_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='observation',
+            index=models.Index(fields=['season', 'player_roster_membership', 'status'], name='analytics_o_season__1bdeda_idx'),
+        ),
+        migrations.AddIndex(
+            model_name='observation',
+            index=models.Index(fields=['evaluator_coach_assignment', 'status'], name='analytics_o_evaluat_462a1b_idx'),
+        ),
+    ]
diff --git a/analytics/models.py b/analytics/models.py
index baf66f4..27de1f4 100644
--- a/analytics/models.py
+++ b/analytics/models.py
@@ -160,6 +160,13 @@ class EvaluationCycle(TimeStampedModel):
     name = models.CharField(max_length=160)
     slug = models.SlugField(max_length=180, unique=True, blank=True)
     cycle_type = models.CharField(max_length=80)
+    season = models.ForeignKey(
+        "seasons.Season",
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="evaluation_cycles",
+    )
     description = models.TextField(blank=True)
     starts_on = models.DateField(null=True, blank=True)
     ends_on = models.DateField(null=True, blank=True)
@@ -177,6 +184,7 @@ class EvaluationCycle(TimeStampedModel):
         ordering = ["-starts_on", "-created_at", "name"]
         indexes = [
             models.Index(fields=["is_active", "starts_on"]),
+            models.Index(fields=["season", "is_active"]),
             models.Index(fields=["cycle_type", "is_active"]),
             models.Index(fields=["slug"]),
         ]
@@ -233,6 +241,27 @@ class ObservationQuestion(TimeStampedModel):
 class Observation(TimeStampedModel):
     player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="observations")
     evaluation_cycle = models.ForeignKey(EvaluationCycle, on_delete=models.PROTECT, related_name="observations")
+    season = models.ForeignKey(
+        "seasons.Season",
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="observations",
+    )
+    player_roster_membership = models.ForeignKey(
+        "seasons.PlayerRosterMembership",
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="observations",
+    )
+    evaluator_coach_assignment = models.ForeignKey(
+        "seasons.CoachSeasonAssignment",
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="observations",
+    )
     observation_type = models.ForeignKey(ObservationType, on_delete=models.PROTECT, related_name="observations")
     observation_type_key = models.CharField(max_length=80, editable=False)
     question_set = models.ForeignKey(ObservationQuestionSet, on_delete=models.PROTECT, related_name="observations")
@@ -260,6 +289,13 @@ class Observation(TimeStampedModel):
     )
     status = models.CharField(max_length=40, choices=OBSERVATION_STATUS_CHOICES, default=OBSERVATION_STATUS_DRAFT)
     submitted_at = models.DateTimeField(null=True, blank=True)
+    season_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
+    season_key_snapshot = models.CharField(max_length=80, blank=True, editable=False)
+    player_team_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
+    player_division_snapshot = models.CharField(max_length=80, blank=True, editable=False)
+    evaluator_team_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
+    evaluator_division_snapshot = models.CharField(max_length=80, blank=True, editable=False)
+    evaluator_assignment_role_snapshot = models.CharField(max_length=80, blank=True, editable=False)
     notes = models.TextField(blank=True)
     source_metadata = models.JSONField(default=dict, blank=True)
     metadata = models.JSONField(default=dict, blank=True)
@@ -284,6 +320,9 @@ class Observation(TimeStampedModel):
         indexes = [
             models.Index(fields=["player", "-created_at"]),
             models.Index(fields=["evaluation_cycle", "observation_type", "status"]),
+            models.Index(fields=["season", "status"]),
+            models.Index(fields=["season", "player_roster_membership", "status"]),
+            models.Index(fields=["evaluator_coach_assignment", "status"]),
             models.Index(fields=["evaluator", "evaluation_cycle"]),
             models.Index(fields=["evaluator_role_key", "evaluation_cycle"]),
             models.Index(fields=["evaluation_perspective", "evaluation_cycle"]),
@@ -291,6 +330,24 @@ class Observation(TimeStampedModel):
             models.Index(fields=["submitted_at"]),
         ]
 
+    def clean(self):
+        errors = {}
+        if self.evaluation_cycle_id and self.season_id and self.evaluation_cycle.season_id:
+            if self.evaluation_cycle.season_id != self.season_id:
+                errors["season"] = "Observation season must match the evaluation cycle season."
+        if self.player_roster_membership_id:
+            if self.player_roster_membership.player_id != self.player_id:
+                errors["player_roster_membership"] = "Player roster membership must belong to the observation player."
+            if self.season_id and self.player_roster_membership.season.id != self.season_id:
+                errors["player_roster_membership"] = "Player roster membership must belong to the observation season."
+        if self.evaluator_coach_assignment_id:
+            if self.evaluator_id and self.evaluator_coach_assignment.user_id != self.evaluator_id:
+                errors["evaluator_coach_assignment"] = "Evaluator coach assignment must belong to the evaluator."
+            if self.season_id and self.evaluator_coach_assignment.season.id != self.season_id:
+                errors["evaluator_coach_assignment"] = "Evaluator coach assignment must belong to the observation season."
+        if errors:
+            raise ValidationError(errors)
+
     def save(self, *args, **kwargs):
         if self.observation_type_id:
             self.observation_type_key = self.observation_type.key
diff --git a/analytics/services/coach_assessment_service.py b/analytics/services/coach_assessment_service.py
index 240aeed..ed18069 100644
--- a/analytics/services/coach_assessment_service.py
+++ b/analytics/services/coach_assessment_service.py
@@ -17,9 +17,11 @@ from analytics.models import (
     ObservationQuestionSet,
 )
 from analytics.services.observation_service import create_coach_assessment_observation
+from analytics.services.evaluation_context_service import apply_evaluation_context, resolve_evaluation_context
 from analytics.services.permissions import can_evaluate_player, evaluation_perspective_for_user
 from analytics.services.question_service import get_active_questions, get_coach_assessment_type, get_question_set_for_cycle
 from players.models import Player
+from seasons.models import PlayerRosterMembership
 
 
 @dataclass
@@ -27,15 +29,19 @@ class PlayerAssessmentStatus:
     player: Player
     observation: Observation | None
     status: str
+    player_roster_membership: PlayerRosterMembership | None = None
+    player_team: str = ""
+    player_division: str = ""
     evaluation_perspective: str = ""
     evaluation_perspective_label: str = ""
 
 
 def get_active_coach_assessment_cycle(cycle_id: int | None = None) -> EvaluationCycle | None:
-    queryset = EvaluationCycle.objects.filter(is_active=True).order_by("-starts_on", "-created_at", "name")
+    queryset = EvaluationCycle.objects.select_related("season").filter(is_active=True).order_by("-starts_on", "-created_at", "name")
     if cycle_id:
         return queryset.filter(pk=cycle_id).first()
-    return queryset.filter(coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT).first()
+    coach_cycles = queryset.filter(coach_assessment_question_set__observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT)
+    return coach_cycles.filter(season__isnull=False).first() or coach_cycles.first()
 
 
 def list_players_for_assessment(query: str = "", division: str = "", team: str = ""):
@@ -49,6 +55,28 @@ def list_players_for_assessment(query: str = "", division: str = "", team: str =
     return players
 
 
+def list_memberships_for_assessment(cycle: EvaluationCycle, query: str = "", division: str = "", team: str = ""):
+    """Return season-roster rows for player selectors when a cycle has season context."""
+    if not cycle.season_id:
+        return list_players_for_assessment(query=query, division=division, team=team)
+    memberships = (
+        PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season")
+        .filter(player__is_active=True, is_active=True, season_team__season=cycle.season)
+        .order_by("player__last_name", "player__first_name", "season_team__division", "season_team__name", "id")
+    )
+    if query:
+        memberships = memberships.filter(
+            Q(player__first_name__icontains=query)
+            | Q(player__last_name__icontains=query)
+            | Q(player__preferred_name__icontains=query)
+        )
+    if division:
+        memberships = memberships.filter(season_team__division__iexact=division)
+    if team:
+        memberships = memberships.filter(season_team__name__iexact=team)
+    return memberships
+
+
 def get_existing_coach_assessment(
     player: Player,
     cycle: EvaluationCycle,
@@ -70,24 +98,65 @@ def get_existing_coach_assessment(
 
 
 @transaction.atomic
-def get_or_create_draft_coach_assessment(player: Player, cycle: EvaluationCycle, evaluator) -> Observation:
+def get_or_create_draft_coach_assessment(
+    player: Player,
+    cycle: EvaluationCycle,
+    evaluator,
+    *,
+    player_roster_membership: PlayerRosterMembership | None = None,
+) -> Observation:
     evaluation_perspective = evaluation_perspective_for_user(evaluator, player)
     existing = get_existing_coach_assessment(player, cycle, evaluator, evaluation_perspective=evaluation_perspective)
     if existing:
+        if player_roster_membership and existing.status in {OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED}:
+            context = resolve_evaluation_context(
+                player=player,
+                evaluation_cycle=cycle,
+                evaluator=evaluator,
+                evaluation_perspective=evaluation_perspective,
+                player_roster_membership=player_roster_membership,
+                require_season=False,
+            )
+            apply_evaluation_context(existing, context, refresh_snapshots=True)
+            existing.save(
+                update_fields=[
+                    "season",
+                    "player_roster_membership",
+                    "evaluator_coach_assignment",
+                    "season_name_snapshot",
+                    "season_key_snapshot",
+                    "player_team_name_snapshot",
+                    "player_division_snapshot",
+                    "evaluator_team_name_snapshot",
+                    "evaluator_division_snapshot",
+                    "evaluator_assignment_role_snapshot",
+                    "updated_at",
+                ]
+            )
         return existing
     result = create_coach_assessment_observation(
         player=player,
         evaluation_cycle=cycle,
         evaluator=evaluator,
         evaluation_perspective=evaluation_perspective,
+        player_roster_membership=player_roster_membership,
         question_set=get_question_set_for_cycle(cycle, get_coach_assessment_type()),
         status=OBSERVATION_STATUS_DRAFT,
     )
     return result.observation
 
 
-def assessment_status_for_players(players, cycle: EvaluationCycle, evaluator) -> list[PlayerAssessmentStatus]:
-    player_list = list(players)
+def assessment_status_for_players(players_or_memberships, cycle: EvaluationCycle, evaluator) -> list[PlayerAssessmentStatus]:
+    input_list = list(players_or_memberships)
+    target_rows = []
+    player_list = []
+    for item in input_list:
+        if isinstance(item, PlayerRosterMembership):
+            target_rows.append((item.player, item))
+            player_list.append(item.player)
+        else:
+            target_rows.append((item, None))
+            player_list.append(item)
     observations = {
         (observation.player_id, observation.evaluation_perspective): observation
         for observation in Observation.objects.filter(
@@ -98,7 +167,7 @@ def assessment_status_for_players(players, cycle: EvaluationCycle, evaluator) ->
         )
     }
     statuses = []
-    for player in player_list:
+    for player, membership in target_rows:
         perspective = ""
         label = ""
         observation = None
@@ -111,6 +180,9 @@ def assessment_status_for_players(players, cycle: EvaluationCycle, evaluator) ->
                 player=player,
                 observation=observation,
                 status=observation.status if observation else "not_started",
+                player_roster_membership=membership,
+                player_team=membership.season_team.name if membership else player.team_name,
+                player_division=membership.season_team.division if membership else player.division,
                 evaluation_perspective=perspective,
                 evaluation_perspective_label=label,
             )
diff --git a/analytics/services/evaluation_access_service.py b/analytics/services/evaluation_access_service.py
index d59c26a..2e7c34b 100644
--- a/analytics/services/evaluation_access_service.py
+++ b/analytics/services/evaluation_access_service.py
@@ -17,7 +17,7 @@ from analytics.services.coach_assessment_service import (
     get_active_coach_assessment_cycle,
     get_existing_coach_assessment,
     get_or_create_draft_coach_assessment,
-    list_players_for_assessment,
+    list_memberships_for_assessment,
 )
 from analytics.services.permissions import (
     can_evaluate_player,
@@ -34,6 +34,9 @@ class EvaluationTargetStatus:
     observation: Observation | None
     status: str
     can_evaluate: bool
+    player_roster_membership: object = None
+    player_team: str = ""
+    player_division: str = ""
     evaluation_perspective_label: str = ""
 
 
@@ -87,19 +90,19 @@ def get_evaluation_target_list(user, params) -> EvaluationTargetList:
     if not cycle:
         return EvaluationTargetList(cycle=None, player_statuses=[], query=query, division=division, team=team)
 
-    players = list(list_players_for_assessment(query=query, division=division, team=team))
-    statuses_by_player_id = {
-        item.player.id: item for item in assessment_status_for_players(players, cycle, user)
-    }
+    targets = list(list_memberships_for_assessment(cycle, query=query, division=division, team=team))
     player_statuses = [
         EvaluationTargetStatus(
-            player=player,
-            observation=statuses_by_player_id[player.id].observation,
-            status=statuses_by_player_id[player.id].status,
-            can_evaluate=can_evaluate_player(user, player),
-            evaluation_perspective_label=statuses_by_player_id[player.id].evaluation_perspective_label,
+            player=item.player,
+            observation=item.observation,
+            status=item.status,
+            can_evaluate=item.status != "unavailable" and can_evaluate_player(user, item.player),
+            player_roster_membership=item.player_roster_membership,
+            player_team=item.player_team,
+            player_division=item.player_division,
+            evaluation_perspective_label=item.evaluation_perspective_label,
         )
-        for player in players
+        for item in assessment_status_for_players(targets, cycle, user)
     ]
     return EvaluationTargetList(
         cycle=cycle,
@@ -116,14 +119,14 @@ def get_existing_evaluation_for_player(user, player: Player, cycle: EvaluationCy
 
 
 @transaction.atomic
-def get_or_create_evaluation_for_player(user, player: Player, cycle: EvaluationCycle) -> Observation:
+def get_or_create_evaluation_for_player(user, player: Player, cycle: EvaluationCycle, player_roster_membership=None) -> Observation:
     """Return or create the evaluator's draft evaluation for a target player."""
     if not can_evaluate_player(user, player):
         raise PermissionDenied("You cannot evaluate this player.")
     existing = get_existing_evaluation_for_player(user, player, cycle)
     if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
         return existing
-    return get_or_create_draft_coach_assessment(player, cycle, user)
+    return get_or_create_draft_coach_assessment(player, cycle, user, player_roster_membership=player_roster_membership)
 
 
 def active_evaluation_cycle() -> EvaluationCycle | None:
diff --git a/analytics/services/evaluation_context_service.py b/analytics/services/evaluation_context_service.py
new file mode 100644
index 0000000..4bdca60
--- /dev/null
+++ b/analytics/services/evaluation_context_service.py
@@ -0,0 +1,192 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+
+from django.core.exceptions import ValidationError
+
+from accounts.models import AccountRole
+from accounts.services.role_service import role_for_user
+from analytics.models import EVALUATION_PERSPECTIVE_COACH, OBSERVATION_STATUS_SUBMITTED, EvaluationCycle, Observation
+from players.models import Player
+from seasons.models import CoachSeasonAssignment, PlayerRosterMembership, Season
+
+
+@dataclass(frozen=True)
+class EvaluationSeasonContext:
+    season: Season | None
+    player_roster_membership: PlayerRosterMembership | None = None
+    evaluator_coach_assignment: CoachSeasonAssignment | None = None
+    season_name_snapshot: str = ""
+    season_key_snapshot: str = ""
+    player_team_name_snapshot: str = ""
+    player_division_snapshot: str = ""
+    evaluator_team_name_snapshot: str = ""
+    evaluator_division_snapshot: str = ""
+    evaluator_assignment_role_snapshot: str = ""
+
+
+def _active_player_memberships(player: Player, season: Season):
+    return (
+        PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
+        .filter(player=player, season_team__season=season, is_active=True)
+        .order_by("-is_primary", "-starts_on", "-created_at", "-id")
+    )
+
+
+def resolve_player_membership(
+    *,
+    player: Player,
+    season: Season,
+    player_roster_membership: PlayerRosterMembership | None = None,
+) -> PlayerRosterMembership:
+    """Resolve a target player's membership for an evaluation season without guessing ambiguous cases."""
+    if player_roster_membership is not None:
+        membership = PlayerRosterMembership.objects.select_related("season_team", "season_team__season").get(
+            pk=player_roster_membership.pk
+        )
+        if membership.player_id != player.id:
+            raise ValidationError("Selected player membership does not belong to this player.")
+        if membership.season.id != season.id:
+            raise ValidationError("Selected player membership does not belong to this evaluation season.")
+        if not membership.is_active:
+            raise ValidationError("Selected player membership is inactive.")
+        return membership
+
+    memberships = list(_active_player_memberships(player, season))
+    if not memberships:
+        raise ValidationError("This player is not on an active roster for the evaluation season.")
+    primary_memberships = [membership for membership in memberships if membership.is_primary]
+    if len(primary_memberships) == 1:
+        return primary_memberships[0]
+    if len(primary_memberships) > 1:
+        raise ValidationError("This player has multiple primary memberships for the evaluation season.")
+    if len(memberships) == 1:
+        return memberships[0]
+    raise ValidationError("This player has multiple active memberships for the evaluation season. Select a roster team.")
+
+
+def resolve_evaluator_assignment(
+    *,
+    evaluator,
+    season: Season,
+    player_roster_membership: PlayerRosterMembership | None,
+    evaluation_perspective: str,
+    evaluator_coach_assignment: CoachSeasonAssignment | None = None,
+) -> CoachSeasonAssignment | None:
+    """Resolve a coach assignment snapshot for coach evaluations only."""
+    if evaluator_coach_assignment is not None:
+        assignment = CoachSeasonAssignment.objects.select_related("season_team", "season_team__season").get(
+            pk=evaluator_coach_assignment.pk
+        )
+        if assignment.user_id != evaluator.id:
+            raise ValidationError("Selected coach assignment does not belong to this evaluator.")
+        if assignment.season.id != season.id:
+            raise ValidationError("Selected coach assignment does not belong to this evaluation season.")
+        if not assignment.is_active:
+            raise ValidationError("Selected coach assignment is inactive.")
+        return assignment
+
+    if not evaluator or evaluation_perspective != EVALUATION_PERSPECTIVE_COACH:
+        return None
+    if role_for_user(evaluator) != AccountRole.COACH:
+        return None
+
+    assignments = list(
+        CoachSeasonAssignment.objects.select_related("season_team", "season_team__season")
+        .filter(user=evaluator, season_team__season=season, is_active=True)
+        .order_by("-is_primary", "season_team__division", "season_team__name", "id")
+    )
+    if not assignments:
+        return None
+    if player_roster_membership:
+        team_matches = [
+            assignment
+            for assignment in assignments
+            if assignment.season_team_id == player_roster_membership.season_team_id
+        ]
+        if len(team_matches) == 1:
+            return team_matches[0]
+        if len(team_matches) > 1:
+            raise ValidationError("This coach has multiple assignments for the player's team. Select a coach assignment.")
+    if len(assignments) == 1:
+        return assignments[0]
+    primary_assignments = [assignment for assignment in assignments if assignment.is_primary]
+    if len(primary_assignments) == 1:
+        return primary_assignments[0]
+    raise ValidationError("This coach has multiple active assignments for the evaluation season. Select a coach assignment.")
+
+
+def resolve_evaluation_context(
+    *,
+    player: Player,
+    evaluation_cycle: EvaluationCycle,
+    evaluator=None,
+    evaluation_perspective: str = "",
+    player_roster_membership: PlayerRosterMembership | None = None,
+    evaluator_coach_assignment: CoachSeasonAssignment | None = None,
+    require_season: bool = True,
+) -> EvaluationSeasonContext:
+    """Resolve the season, roster membership, assignment, and display snapshots for an observation."""
+    season = evaluation_cycle.season
+    if season is None:
+        if require_season:
+            raise ValidationError("Evaluation cycle must have a season before this evaluation can be submitted.")
+        return EvaluationSeasonContext(season=None)
+
+    membership = resolve_player_membership(
+        player=player,
+        season=season,
+        player_roster_membership=player_roster_membership,
+    )
+    assignment = resolve_evaluator_assignment(
+        evaluator=evaluator,
+        season=season,
+        player_roster_membership=membership,
+        evaluation_perspective=evaluation_perspective,
+        evaluator_coach_assignment=evaluator_coach_assignment,
+    )
+    return EvaluationSeasonContext(
+        season=season,
+        player_roster_membership=membership,
+        evaluator_coach_assignment=assignment,
+        season_name_snapshot=season.name,
+        season_key_snapshot=season.key,
+        player_team_name_snapshot=membership.season_team.name,
+        player_division_snapshot=membership.season_team.division,
+        evaluator_team_name_snapshot=assignment.season_team.name if assignment else "",
+        evaluator_division_snapshot=assignment.season_team.division if assignment else "",
+        evaluator_assignment_role_snapshot=assignment.get_assignment_role_display() if assignment else "",
+    )
+
+
+def apply_evaluation_context(
+    observation: Observation,
+    context: EvaluationSeasonContext,
+    *,
+    refresh_snapshots: bool = False,
+) -> Observation:
+    """Apply resolved context to an observation, preserving submitted snapshots unless explicitly refreshed."""
+    observation.season = context.season
+    observation.player_roster_membership = context.player_roster_membership
+    observation.evaluator_coach_assignment = context.evaluator_coach_assignment
+    if observation.status != OBSERVATION_STATUS_SUBMITTED or refresh_snapshots:
+        observation.season_name_snapshot = context.season_name_snapshot
+        observation.season_key_snapshot = context.season_key_snapshot
+        observation.player_team_name_snapshot = context.player_team_name_snapshot
+        observation.player_division_snapshot = context.player_division_snapshot
+        observation.evaluator_team_name_snapshot = context.evaluator_team_name_snapshot
+        observation.evaluator_division_snapshot = context.evaluator_division_snapshot
+        observation.evaluator_assignment_role_snapshot = context.evaluator_assignment_role_snapshot
+    return observation
+
+
+def observation_display_season(observation: Observation) -> str:
+    return observation.season_name_snapshot or (observation.season.name if observation.season_id else "Legacy / No Season")
+
+
+def observation_display_player_team(observation: Observation) -> str:
+    return observation.player_team_name_snapshot or observation.player.team_name
+
+
+def observation_display_player_division(observation: Observation) -> str:
+    return observation.player_division_snapshot or observation.player.division
diff --git a/analytics/services/evaluation_review_service.py b/analytics/services/evaluation_review_service.py
index 4a89668..17fba2c 100644
--- a/analytics/services/evaluation_review_service.py
+++ b/analytics/services/evaluation_review_service.py
@@ -15,6 +15,7 @@ from analytics.models import (
     Observation,
 )
 from analytics.services.permissions import can_review_submitted_evaluations, can_view_evaluation_review_detail
+from seasons.models import Season
 
 
 @dataclass(frozen=True)
@@ -26,6 +27,7 @@ class EvaluationReviewFilters:
     perspective: str = ""
     team: str = ""
     division: str = ""
+    season: str = ""
     cycle: str = ""
     submitted_from: str = ""
     submitted_to: str = ""
@@ -35,6 +37,7 @@ class EvaluationReviewFilters:
 class EvaluationReviewRow:
     observation_id: int
     player_name: str
+    season_name: str
     player_team: str
     player_division: str
     evaluator_name: str
@@ -56,6 +59,7 @@ class EvaluationReviewQuestionResponse:
 class EvaluationReviewDetail:
     observation_id: int
     player_name: str
+    season_name: str
     player_team: str
     player_division: str
     evaluator_name: str
@@ -71,6 +75,7 @@ class EvaluationReviewList:
     filters: EvaluationReviewFilters
     rows: list[EvaluationReviewRow]
     total_count: int
+    seasons: object
     cycles: object
     evaluator_roles: object
     perspective_choices: object
@@ -85,6 +90,7 @@ def parse_evaluation_review_filters(params) -> EvaluationReviewFilters:
         perspective=(params.get("perspective") or "").strip(),
         team=(params.get("team") or "").strip(),
         division=(params.get("division") or "").strip(),
+        season=(params.get("season") or "").strip(),
         cycle=(params.get("cycle") or "").strip(),
         submitted_from=(params.get("submitted_from") or "").strip(),
         submitted_to=(params.get("submitted_to") or "").strip(),
@@ -99,7 +105,7 @@ def _display_user(user) -> str:
 
 def submitted_evaluation_queryset(filters: EvaluationReviewFilters | None = None):
     queryset = (
-        Observation.objects.select_related("player", "evaluation_cycle", "evaluator", "evaluator_role")
+        Observation.objects.select_related("player", "evaluation_cycle", "season", "evaluator", "evaluator_role")
         .filter(
             observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
             status=OBSERVATION_STATUS_SUBMITTED,
@@ -127,9 +133,17 @@ def submitted_evaluation_queryset(filters: EvaluationReviewFilters | None = None
     if filters.perspective:
         queryset = queryset.filter(evaluation_perspective=filters.perspective)
     if filters.team:
-        queryset = queryset.filter(player__team_name__icontains=filters.team)
+        queryset = queryset.filter(
+            Q(player_team_name_snapshot__gt="", player_team_name_snapshot__icontains=filters.team)
+            | Q(player_team_name_snapshot="", player__team_name__icontains=filters.team)
+        )
     if filters.division:
-        queryset = queryset.filter(player__division__icontains=filters.division)
+        queryset = queryset.filter(
+            Q(player_division_snapshot__gt="", player_division_snapshot__icontains=filters.division)
+            | Q(player_division_snapshot="", player__division__icontains=filters.division)
+        )
+    if filters.season.isdigit():
+        queryset = queryset.filter(season_id=int(filters.season))
     if filters.cycle.isdigit():
         queryset = queryset.filter(evaluation_cycle_id=int(filters.cycle))
 
@@ -152,8 +166,9 @@ def get_evaluation_review_list(user, params) -> EvaluationReviewList:
         EvaluationReviewRow(
             observation_id=observation.id,
             player_name=observation.player.display_name,
-            player_team=observation.player.team_name,
-            player_division=observation.player.division,
+            season_name=observation.season_name_snapshot or (observation.season.name if observation.season_id else "Legacy / No Season"),
+            player_team=observation.player_team_name_snapshot or observation.player.team_name,
+            player_division=observation.player_division_snapshot or observation.player.division,
             evaluator_name=_display_user(observation.evaluator),
             evaluator_role_name=observation.evaluator_role_name or "Evaluator",
             evaluation_perspective_label=observation.evaluation_perspective_label,
@@ -166,6 +181,7 @@ def get_evaluation_review_list(user, params) -> EvaluationReviewList:
         filters=filters,
         rows=rows,
         total_count=len(rows),
+        seasons=Season.objects.filter(is_active=True).order_by("-is_current", "-starts_on", "name"),
         cycles=EvaluationCycle.objects.filter(is_active=True).order_by("-starts_on", "-created_at", "name"),
         evaluator_roles=EvaluatorRole.objects.filter(is_active=True).order_by("name"),
         perspective_choices=EVALUATION_PERSPECTIVE_CHOICES,
@@ -192,8 +208,9 @@ def get_evaluation_review_detail(user, observation_id: int) -> EvaluationReviewD
     return EvaluationReviewDetail(
         observation_id=observation.id,
         player_name=observation.player.display_name,
-        player_team=observation.player.team_name,
-        player_division=observation.player.division,
+        season_name=observation.season_name_snapshot or (observation.season.name if observation.season_id else "Legacy / No Season"),
+        player_team=observation.player_team_name_snapshot or observation.player.team_name,
+        player_division=observation.player_division_snapshot or observation.player.division,
         evaluator_name=_display_user(observation.evaluator),
         evaluator_role_name=observation.evaluator_role_name or "Evaluator",
         evaluation_perspective_label=observation.evaluation_perspective_label,
diff --git a/analytics/services/observation_service.py b/analytics/services/observation_service.py
index ca6dfb8..3b33362 100644
--- a/analytics/services/observation_service.py
+++ b/analytics/services/observation_service.py
@@ -34,6 +34,8 @@ from analytics.services.question_service import (
 )
 from analytics.services.permissions import can_evaluate_player, evaluation_perspective_for_user, evaluator_role_for_user
 from players.models import Player
+from seasons.models import CoachSeasonAssignment, PlayerRosterMembership
+from analytics.services.evaluation_context_service import apply_evaluation_context, resolve_evaluation_context
 
 
 @dataclass
@@ -138,6 +140,8 @@ def create_observation(
     evaluator=None,
     evaluator_role: EvaluatorRole | None = None,
     evaluation_perspective: str | None = None,
+    player_roster_membership: PlayerRosterMembership | None = None,
+    evaluator_coach_assignment: CoachSeasonAssignment | None = None,
     status: str = OBSERVATION_STATUS_DRAFT,
     notes: str = "",
     source_metadata: dict[str, Any] | None = None,
@@ -159,6 +163,15 @@ def create_observation(
         evaluator=evaluator,
         evaluation_perspective=evaluation_perspective,
     )
+    context = resolve_evaluation_context(
+        player=player,
+        evaluation_cycle=evaluation_cycle,
+        evaluator=evaluator,
+        evaluation_perspective=evaluation_perspective,
+        player_roster_membership=player_roster_membership,
+        evaluator_coach_assignment=evaluator_coach_assignment,
+        require_season=False,
+    )
     observation = Observation(
         player=player,
         evaluation_cycle=evaluation_cycle,
@@ -174,6 +187,7 @@ def create_observation(
         metadata=metadata or {},
     )
     _snapshot_role(observation, evaluator_role)
+    apply_evaluation_context(observation, context, refresh_snapshots=True)
     if status == OBSERVATION_STATUS_SUBMITTED:
         observation.submitted_at = timezone.now()
     try:
@@ -191,6 +205,8 @@ def create_coach_assessment_observation(
     evaluator,
     evaluator_role: EvaluatorRole | None = None,
     evaluation_perspective: str | None = None,
+    player_roster_membership: PlayerRosterMembership | None = None,
+    evaluator_coach_assignment: CoachSeasonAssignment | None = None,
     source: ObservationSource | None = None,
     question_set: ObservationQuestionSet | None = None,
     status: str = OBSERVATION_STATUS_DRAFT,
@@ -216,6 +232,8 @@ def create_coach_assessment_observation(
         evaluator=evaluator,
         evaluator_role=evaluator_role,
         evaluation_perspective=evaluation_perspective,
+        player_roster_membership=player_roster_membership,
+        evaluator_coach_assignment=evaluator_coach_assignment,
         status=status,
         notes=notes,
         source_metadata=source_metadata,
@@ -298,9 +316,35 @@ def submit_observation(observation: Observation, actor=None) -> Observation:
             exclude_observation=locked_observation,
         )
     validate_required_responses(locked_observation)
+    context = resolve_evaluation_context(
+        player=locked_observation.player,
+        evaluation_cycle=locked_observation.evaluation_cycle,
+        evaluator=locked_observation.evaluator,
+        evaluation_perspective=locked_observation.evaluation_perspective,
+        player_roster_membership=locked_observation.player_roster_membership,
+        evaluator_coach_assignment=locked_observation.evaluator_coach_assignment,
+        require_season=True,
+    )
+    apply_evaluation_context(locked_observation, context, refresh_snapshots=True)
     locked_observation.status = OBSERVATION_STATUS_SUBMITTED
     locked_observation.submitted_at = timezone.now()
-    locked_observation.save(update_fields=["status", "submitted_at", "updated_at"])
+    locked_observation.save(
+        update_fields=[
+            "season",
+            "player_roster_membership",
+            "evaluator_coach_assignment",
+            "season_name_snapshot",
+            "season_key_snapshot",
+            "player_team_name_snapshot",
+            "player_division_snapshot",
+            "evaluator_team_name_snapshot",
+            "evaluator_division_snapshot",
+            "evaluator_assignment_role_snapshot",
+            "status",
+            "submitted_at",
+            "updated_at",
+        ]
+    )
     return locked_observation
 
 
@@ -310,6 +354,11 @@ def get_observation_detail(observation_id: int) -> Observation:
         Observation.objects.select_related(
             "player",
             "evaluation_cycle",
+            "season",
+            "player_roster_membership",
+            "player_roster_membership__season_team",
+            "evaluator_coach_assignment",
+            "evaluator_coach_assignment__season_team",
             "observation_type",
             "question_set",
             "source",
diff --git a/analytics/templates/analytics/assessment_detail.html b/analytics/templates/analytics/assessment_detail.html
index 6a92a16..032a869 100644
--- a/analytics/templates/analytics/assessment_detail.html
+++ b/analytics/templates/analytics/assessment_detail.html
@@ -7,6 +7,11 @@
 <article class="pdp-card">
     <h2>Assessment</h2>
     <p>Type: {{ observation.evaluation_perspective_label }}</p>
+    <p>Season: {{ observation.season_name_snapshot|default:"Legacy / No Season" }}</p>
+    <p>Roster: {{ observation.player_division_snapshot|default:observation.player.division }} {{ observation.player_team_name_snapshot|default:observation.player.team_name }}</p>
+    {% if observation.evaluator_team_name_snapshot %}
+        <p>Evaluator Assignment: {{ observation.evaluator_assignment_role_snapshot }} · {{ observation.evaluator_division_snapshot }} {{ observation.evaluator_team_name_snapshot }}</p>
+    {% endif %}
     <p>Evaluator: {{ observation.evaluator }} · Role: {{ observation.evaluator_role_name }}</p>
     {% if observation.submitted_at %}<p>Submitted: {{ observation.submitted_at }}</p>{% endif %}
     {% for group in question_groups %}
diff --git a/analytics/templates/analytics/assessment_form.html b/analytics/templates/analytics/assessment_form.html
index 241887d..405ed4a 100644
--- a/analytics/templates/analytics/assessment_form.html
+++ b/analytics/templates/analytics/assessment_form.html
@@ -7,6 +7,9 @@
 <article class="pdp-card pdp-card--form">
     <h2>Coach Assessment</h2>
     <p>{{ observation.evaluation_perspective_label }}</p>
+    {% if observation.season_name_snapshot %}
+        <p>{{ observation.season_name_snapshot }} · {{ observation.player_division_snapshot }} {{ observation.player_team_name_snapshot }}</p>
+    {% endif %}
     {% if question_set.rubric.labels %}
         <p>
             {% for value, label in question_set.rubric.labels.items %}
@@ -16,6 +19,9 @@
     {% endif %}
     <form method="post" class="pdp-form">
         {% csrf_token %}
+        {% if observation.player_roster_membership_id %}
+            <input type="hidden" name="membership" value="{{ observation.player_roster_membership_id }}">
+        {% endif %}
         {{ form.non_field_errors }}
         {% for group in question_groups %}
             <section class="pdp-list__item pdp-list__item--stack">
diff --git a/analytics/templates/analytics/assessment_list.html b/analytics/templates/analytics/assessment_list.html
index e07c226..46a4d3e 100644
--- a/analytics/templates/analytics/assessment_list.html
+++ b/analytics/templates/analytics/assessment_list.html
@@ -41,8 +41,8 @@
                     {% for item in player_statuses %}
                         <tr>
                             <td>{{ item.player.display_name }}</td>
-                            <td>{{ item.player.division }}</td>
-                            <td>{{ item.player.team_name }}</td>
+                            <td>{{ item.player_division }}</td>
+                            <td>{{ item.player_team }}</td>
                             <td>{{ item.evaluation_perspective_label }}</td>
                             <td>{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
                             <td>
@@ -51,7 +51,7 @@
                                 {% elif item.observation %}
                                     <a class="button button--primary" href="{% url 'analytics:assessment-edit' observation_id=item.observation.id %}">Continue</a>
                                 {% else %}
-                                    <a class="button button--primary" href="{% url 'analytics:assessment-player' player_id=item.player.id %}">Start</a>
+                                    <a class="button button--primary" href="{% url 'analytics:assessment-player' player_id=item.player.id %}{% if item.player_roster_membership %}?membership={{ item.player_roster_membership.id }}{% endif %}">Start</a>
                                 {% endif %}
                             </td>
                         </tr>
diff --git a/analytics/templates/analytics/evaluation_form.html b/analytics/templates/analytics/evaluation_form.html
index 7bd2a48..3f40a0e 100644
--- a/analytics/templates/analytics/evaluation_form.html
+++ b/analytics/templates/analytics/evaluation_form.html
@@ -7,6 +7,9 @@
 <article class="pdp-card pdp-card--form">
     <h2>Evaluation</h2>
     <p>{{ observation.evaluation_perspective_label }}</p>
+    {% if observation.season_name_snapshot %}
+        <p>{{ observation.season_name_snapshot }} · {{ observation.player_division_snapshot }} {{ observation.player_team_name_snapshot }}</p>
+    {% endif %}
     {% if question_set.rubric.labels %}
         <p>
             {% for value, label in question_set.rubric.labels.items %}
@@ -16,6 +19,9 @@
     {% endif %}
     <form method="post" class="pdp-form">
         {% csrf_token %}
+        {% if observation.player_roster_membership_id %}
+            <input type="hidden" name="membership" value="{{ observation.player_roster_membership_id }}">
+        {% endif %}
         {{ form.non_field_errors }}
         {% for group in question_groups %}
             <section class="pdp-list__item pdp-list__item--stack">
diff --git a/analytics/templates/analytics/evaluation_list.html b/analytics/templates/analytics/evaluation_list.html
index 77210fe..33d08f2 100644
--- a/analytics/templates/analytics/evaluation_list.html
+++ b/analytics/templates/analytics/evaluation_list.html
@@ -41,8 +41,8 @@
                     {% for item in player_statuses %}
                         <tr>
                             <td>{{ item.player.display_name }}</td>
-                            <td>{{ item.player.division }}</td>
-                            <td>{{ item.player.team_name }}</td>
+                            <td>{{ item.player_division }}</td>
+                            <td>{{ item.player_team }}</td>
                             <td>{{ item.evaluation_perspective_label }}</td>
                             <td>{% include "analytics/_assessment_status_badge.html" with status=item.status %}</td>
                             <td>
@@ -51,9 +51,9 @@
                                 {% elif item.observation and item.status == "submitted" %}
                                     <a class="button button--ghost" href="{% url 'analytics:assessment-detail' observation_id=item.observation.id %}">View My Submission</a>
                                 {% elif item.observation %}
-                                    <a class="button button--primary" href="{% url 'analytics:evaluation-player' player_id=item.player.id %}">Continue</a>
+                                    <a class="button button--primary" href="{% url 'analytics:evaluation-player' player_id=item.player.id %}{% if item.player_roster_membership %}?membership={{ item.player_roster_membership.id }}{% endif %}">Continue</a>
                                 {% else %}
-                                    <a class="button button--primary" href="{% url 'analytics:evaluation-player' player_id=item.player.id %}">Evaluate Player</a>
+                                    <a class="button button--primary" href="{% url 'analytics:evaluation-player' player_id=item.player.id %}{% if item.player_roster_membership %}?membership={{ item.player_roster_membership.id }}{% endif %}">Evaluate Player</a>
                                 {% endif %}
                             </td>
                         </tr>
diff --git a/analytics/templates/analytics/evaluation_review_detail.html b/analytics/templates/analytics/evaluation_review_detail.html
index 0280bab..d0d3849 100644
--- a/analytics/templates/analytics/evaluation_review_detail.html
+++ b/analytics/templates/analytics/evaluation_review_detail.html
@@ -9,6 +9,8 @@
     <dl class="pdp-definition-list">
         <dt>Player</dt>
         <dd>{{ detail.player_name }}</dd>
+        <dt>Season</dt>
+        <dd>{{ detail.season_name }}</dd>
         <dt>Team</dt>
         <dd>{{ detail.player_team }}</dd>
         <dt>Division</dt>
diff --git a/analytics/templates/analytics/evaluation_review_list.html b/analytics/templates/analytics/evaluation_review_list.html
index 8ca8b92..0a204a7 100644
--- a/analytics/templates/analytics/evaluation_review_list.html
+++ b/analytics/templates/analytics/evaluation_review_list.html
@@ -45,6 +45,15 @@
             Division
             <input type="text" name="division" value="{{ filters.division }}">
         </label>
+        <label>
+            Season
+            <select name="season">
+                <option value="">All</option>
+                {% for season in seasons %}
+                    <option value="{{ season.id }}" {% if filters.season == season.id|stringformat:"s" %}selected{% endif %}>{{ season.name }}</option>
+                {% endfor %}
+            </select>
+        </label>
         <label>
             Cycle
             <select name="cycle">
@@ -70,6 +79,7 @@
             <thead>
                 <tr>
                     <th>Player</th>
+                    <th>Season</th>
                     <th>Team</th>
                     <th>Division</th>
                     <th>Evaluator</th>
@@ -84,6 +94,7 @@
                 {% for row in rows %}
                     <tr>
                         <td>{{ row.player_name }}</td>
+                        <td>{{ row.season_name }}</td>
                         <td>{{ row.player_team }}</td>
                         <td>{{ row.player_division }}</td>
                         <td>{{ row.evaluator_name }}</td>
@@ -94,7 +105,7 @@
                         <td><a class="button button--ghost" href="{% url 'analytics:evaluation-review-detail' observation_id=row.observation_id %}">Review</a></td>
                     </tr>
                 {% empty %}
-                    <tr><td colspan="9">No submitted evaluations found.</td></tr>
+                    <tr><td colspan="10">No submitted evaluations found.</td></tr>
                 {% endfor %}
             </tbody>
         </table>
diff --git a/analytics/templates/analytics/observation_review_list.html b/analytics/templates/analytics/observation_review_list.html
index d2b3d69..ae6c787 100644
--- a/analytics/templates/analytics/observation_review_list.html
+++ b/analytics/templates/analytics/observation_review_list.html
@@ -27,6 +27,8 @@
             <thead>
                 <tr>
                     <th>Player</th>
+                    <th>Season</th>
+                    <th>Roster</th>
                     <th>Cycle</th>
                     <th>Evaluator</th>
                     <th>Type</th>
@@ -39,6 +41,8 @@
                 {% for observation in observations %}
                     <tr>
                         <td>{{ observation.player.display_name }}</td>
+                        <td>{{ observation.season_name_snapshot|default:"Legacy / No Season" }}</td>
+                        <td>{{ observation.player_division_snapshot|default:observation.player.division }} {{ observation.player_team_name_snapshot|default:observation.player.team_name }}</td>
                         <td>{{ observation.evaluation_cycle.name }}</td>
                         <td>{{ observation.evaluator }}</td>
                         <td>{{ observation.evaluation_perspective_label }}</td>
@@ -47,7 +51,7 @@
                         <td><a class="button button--ghost" href="{% url 'analytics:observation-review-detail' observation_id=observation.id %}">Review</a></td>
                     </tr>
                 {% empty %}
-                    <tr><td colspan="7">No observations found.</td></tr>
+                    <tr><td colspan="9">No observations found.</td></tr>
                 {% endfor %}
             </tbody>
         </table>
diff --git a/analytics/tests.py b/analytics/tests.py
index 8ff8c20..adb75da 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -99,11 +99,23 @@ from players.models import Player, PlayerImportBatch, PlayerImportStatus, Player
 from players.services.import_service import SOURCE_MEMBER_LIST
 from players.services.tag_service import assign_tag
 from seasons.services.season_service import create_season
+from seasons.services.team_service import get_or_create_season_team
+from seasons.services.membership_service import create_membership
+from seasons.services.coach_assignment_service import create_assignment
 
 
 User = get_user_model()
 
 
+def attach_player_to_season(player, season, *, team_name=None, division=None, is_primary=True):
+    season_team, _ = get_or_create_season_team(
+        season=season,
+        name=team_name or player.team_name or "Expos",
+        division=division or player.division or "13U",
+    )
+    return create_membership(player=player, season_team=season_team, is_primary=is_primary, is_active=True)
+
+
 class AnalyticsImportViewTests(TestCase):
     def setUp(self):
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
@@ -341,8 +353,11 @@ class AnalyticsObservationFoundationTests(TestCase):
     def setUp(self):
         self.evaluator = User.objects.create_user(username="coach", password="testpass")
         self.other_evaluator = User.objects.create_user(username="othercoach", password="testpass")
-        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U")
-        self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="13U")
+        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U", team_name="Expos")
+        self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="13U", team_name="Expos")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        self.player_membership = attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.other_player, self.season)
         self.setup_result = ensure_default_coach_assessment_setup()
         self.role = EvaluatorRole.objects.get(key=ROLE_COACH)
         self.source = ObservationSource.objects.get(key=SOURCE_COACH)
@@ -350,6 +365,7 @@ class AnalyticsObservationFoundationTests(TestCase):
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
 
     def required_response_payload(self):
@@ -554,6 +570,7 @@ class AnalyticsObservationFoundationTests(TestCase):
                 evaluator = User.objects.create_user(username=f"snapshot-{account_role}", password="testpass")
                 set_account_role(evaluator, account_role)
                 player = Player.objects.create(first_name=f"Snapshot{index}", last_name="Target", division="13U")
+                attach_player_to_season(player, self.season)
 
                 result = create_coach_assessment_observation(
                     player=player,
@@ -831,17 +848,132 @@ class AnalyticsObservationFoundationTests(TestCase):
             self.assertIn(model, admin.site._registry)
 
 
+class SeasonalEvaluationContextTests(TestCase):
+    def setUp(self):
+        self.coach = User.objects.create_user(username="season-coach", password="testpass")
+        set_account_role(self.coach, AccountRole.COACH)
+        self.player = Player.objects.create(first_name="Season", last_name="Player", division="13U", team_name="Reds")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        self.other_season = create_season(key="2027-spring", name="2027 Spring")
+        self.membership = attach_player_to_season(self.player, self.season, team_name="Reds", division="13U")
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 Spring Evaluations",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+
+    def rating_payload(self, value=4):
+        return {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
+        }
+
+    def test_submitted_observation_stores_immutable_season_and_roster_snapshots(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.rating_payload(),
+        ).observation
+
+        submitted = submit_observation(observation, actor=self.coach)
+        self.membership.season_team.name = "Corrected Reds"
+        self.membership.season_team.division = "14U"
+        self.membership.season_team.save()
+        self.player.team_name = "Live Team"
+        self.player.division = "Live Division"
+        self.player.save(update_fields=["team_name", "division", "updated_at"])
+        submitted.refresh_from_db()
+
+        self.assertEqual(submitted.season, self.season)
+        self.assertEqual(submitted.player_roster_membership, self.membership)
+        self.assertEqual(submitted.season_name_snapshot, "2026 Spring")
+        self.assertEqual(submitted.season_key_snapshot, "2026-spring")
+        self.assertEqual(submitted.player_team_name_snapshot, "Reds")
+        self.assertEqual(submitted.player_division_snapshot, "13U")
+
+    def test_coach_assignment_snapshot_is_stored_when_resolved(self):
+        assignment = create_assignment(user=self.coach, season_team=self.membership.season_team, assignment_role="head_coach", is_primary=True)
+
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.rating_payload(),
+        ).observation
+        submitted = submit_observation(observation, actor=self.coach)
+
+        self.assertEqual(submitted.evaluator_coach_assignment, assignment)
+        self.assertEqual(submitted.evaluator_team_name_snapshot, "Reds")
+        self.assertEqual(submitted.evaluator_division_snapshot, "13U")
+        self.assertEqual(submitted.evaluator_assignment_role_snapshot, "Head Coach")
+
+    def test_cross_player_or_cross_season_membership_is_rejected(self):
+        other_player = Player.objects.create(first_name="Other", last_name="Player", division="13U")
+        other_membership = attach_player_to_season(other_player, self.season)
+        cross_season_membership = attach_player_to_season(self.player, self.other_season)
+
+        with self.assertRaisesMessage(ValidationError, "does not belong to this player"):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=self.coach,
+                player_roster_membership=other_membership,
+            )
+        with self.assertRaisesMessage(ValidationError, "does not belong to this evaluation season"):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=self.coach,
+                player_roster_membership=cross_season_membership,
+            )
+
+    def test_ambiguous_multiple_memberships_without_primary_are_blocked(self):
+        player = Player.objects.create(first_name="Multi", last_name="Member", division="13U")
+        attach_player_to_season(player, self.season, team_name="Reds", division="13U", is_primary=False)
+        attach_player_to_season(player, self.season, team_name="Blues", division="13U", is_primary=False)
+
+        with self.assertRaisesMessage(ValidationError, "multiple active memberships"):
+            create_coach_assessment_observation(player=player, evaluation_cycle=self.cycle, evaluator=self.coach)
+
+    def test_review_uses_snapshot_values_not_live_player_fields(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.rating_payload(),
+        ).observation
+        submitted = submit_observation(observation, actor=self.coach)
+        self.player.team_name = "Changed Live Team"
+        self.player.division = "Changed Live Division"
+        self.player.save(update_fields=["team_name", "division", "updated_at"])
+        set_account_role(self.coach, AccountRole.COACH)
+
+        from analytics.services.evaluation_review_service import get_evaluation_review_detail
+
+        detail = get_evaluation_review_detail(self.coach, submitted.id)
+
+        self.assertEqual(detail.season_name, "2026 Spring")
+        self.assertEqual(detail.player_team, "Reds")
+        self.assertEqual(detail.player_division, "13U")
+
+
 class AnalyticsDraftContextServiceTests(TestCase):
     def setUp(self):
         self.coach = User.objects.create_user(username="coach", password="testpass")
         self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
         self.third_coach = User.objects.create_user(username="thirdcoach", password="testpass")
-        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
+        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U", team_name="Expos")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        attach_player_to_season(self.player, self.season)
         self.setup_result = ensure_default_coach_assessment_setup()
         self.cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
         self.draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
         self.team = DraftTeam.objects.create(draft=self.draft, name="Expos Navy", display_order=1)
@@ -997,11 +1129,15 @@ class PlayerExperienceServiceTests(TestCase):
             team_name="Mounties",
         )
         self.no_context_player = Player.objects.create(first_name="No", last_name="Context", division="13U")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.other_player, self.season)
         self.setup_result = ensure_default_coach_assessment_setup()
         self.cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
         self.draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
         self.team = DraftTeam.objects.create(draft=self.draft, name="Expos Navy", display_order=1)
@@ -1177,11 +1313,15 @@ class PlayerExperienceViewTests(TestCase):
             primary_positions="SS",
         )
         self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="15U", team_name="Mounties")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.other_player, self.season, team_name="Mounties", division="15U")
         self.setup_result = ensure_default_coach_assessment_setup()
         self.cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
 
     def rating_payload(self, value=4):
@@ -1324,11 +1464,15 @@ class AnalyticsCommandCenterServiceTests(TestCase):
             division="15U",
             team_name="Mounties",
         )
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.other_player, self.season, team_name="Mounties", division="15U")
         self.setup_result = ensure_default_coach_assessment_setup()
         self.cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
 
     def rating_payload(self, value=4):
@@ -1500,11 +1644,14 @@ class AnalyticsCommandCenterViewTests(TestCase):
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
         self.coach = User.objects.create_user(username="coach", password="testpass")
         self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U", team_name="Expos")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        attach_player_to_season(self.player, self.season)
         self.setup_result = ensure_default_coach_assessment_setup()
         self.cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
 
     def rating_payload(self, value=4):
@@ -1575,11 +1722,15 @@ class CoachAssessmentWorkflowTests(TestCase):
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
         self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U", team_name="Expos")
         self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="13U", team_name="Expos")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.other_player, self.season)
         self.setup_result = ensure_default_coach_assessment_setup()
         self.cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
 
     def response_payload(self, include_required=True):
@@ -1834,12 +1985,16 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         self.self_player = Player.objects.create(first_name="Self", last_name="Player", division="13U", team_name="Expos")
         self.target_player = Player.objects.create(first_name="Target", last_name="Player", division="13U", team_name="Expos")
         self.inactive_player = Player.objects.create(first_name="Inactive", last_name="Player", division="13U", is_active=False)
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        attach_player_to_season(self.self_player, self.season)
+        attach_player_to_season(self.target_player, self.season)
         link_user_to_player(self.player_user, self.self_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
         self.setup_result = ensure_default_coach_assessment_setup()
         self.cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
 
     def response_payload(self, include_required=True):
@@ -2059,6 +2214,7 @@ class EvaluationAccessSubmissionViewTests(TestCase):
         for user, expected_role in [(self.coach, ROLE_COACH), (self.guest, ROLE_GUEST_EVALUATOR)]:
             with self.subTest(user=user.username):
                 target = Player.objects.create(first_name=user.username, last_name="Target", division="13U")
+                attach_player_to_season(target, self.season)
                 self.client.force_login(user)
                 response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": target.id}))
 
@@ -2097,6 +2253,10 @@ class MyEvaluationsViewTests(TestCase):
         self.player = Player.objects.create(first_name="Linked", last_name="Player", division="13U")
         self.second_player = Player.objects.create(first_name="Second", last_name="Player", division="15U")
         self.other_player = Player.objects.create(first_name="Other", last_name="Player", division="13U")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.second_player, self.season, team_name="Mounties", division="15U")
+        attach_player_to_season(self.other_player, self.season)
         link_user_to_player(self.player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
         link_user_to_player(self.other_player_user, self.other_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
         self.setup_result = ensure_default_coach_assessment_setup()
@@ -2104,6 +2264,7 @@ class MyEvaluationsViewTests(TestCase):
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
 
     def service_response_payload(self, value=4, note="Good teammate."):
@@ -2321,6 +2482,7 @@ class MyEvaluationsViewTests(TestCase):
 
     def test_staff_with_self_link_receives_player_safe_my_evaluation_output(self):
         staff_player = Player.objects.create(first_name="Staff", last_name="Player")
+        attach_player_to_season(staff_player, self.season)
         link_user_to_player(self.staff, staff_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
         observation = self.submitted_observation(player=staff_player, evaluator=self.coach, note="Private staff-linked result.")
         self.client.force_login(self.staff)
@@ -2418,16 +2580,23 @@ class EvaluationReviewViewTests(TestCase):
         set_account_role(self.role_admin, AccountRole.ADMIN)
         self.player = Player.objects.create(first_name="Target", last_name="One", division="13U", team_name="Reds")
         self.second_player = Player.objects.create(first_name="Target", last_name="Two", division="15U", team_name="Blues")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        self.second_season = create_season(key="2026-summer", name="2026 Summer")
+        attach_player_to_season(self.player, self.season, team_name="Reds", division="13U")
+        attach_player_to_season(self.second_player, self.season, team_name="Reds", division="13U")
+        attach_player_to_season(self.second_player, self.second_season, team_name="Blues", division="15U")
         self.setup_result = ensure_default_coach_assessment_setup()
         self.cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
         )
         self.second_cycle = EvaluationCycle.objects.create(
             name="2026 15U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=self.setup_result.question_set,
+            season=self.second_season,
         )
 
     def service_response_payload(self, value=4, note="Good teammate."):
diff --git a/analytics/views.py b/analytics/views.py
index e0c123b..53f4621 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -16,7 +16,7 @@ from analytics.services.coach_assessment_service import (
     get_existing_coach_assessment,
     get_or_create_draft_coach_assessment,
     group_questions_for_display,
-    list_players_for_assessment,
+    list_memberships_for_assessment,
     reopen_observation,
 )
 from analytics.services.comparison_service import (
@@ -54,6 +54,7 @@ from analytics.services.reporting_service import get_command_center_context
 from analytics.services.timeline_service import get_player_timeline
 from players.models import PlayerImportBatch
 from players.models import Player
+from seasons.models import PlayerRosterMembership
 from players.services.import_service import (
     MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
     MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
@@ -306,7 +307,11 @@ class EvaluationPlayerView(EvaluationSubmitterRequiredMixin, TemplateView):
         player = get_object_or_404(Player, pk=kwargs["player_id"], is_active=True)
         if not can_evaluate_player(request.user, player):
             raise PermissionDenied("You cannot evaluate this player.")
-        self.observation = get_or_create_evaluation_for_player(request.user, player, cycle)
+        membership = None
+        membership_id = request.GET.get("membership") or request.POST.get("membership")
+        if membership_id:
+            membership = get_object_or_404(PlayerRosterMembership, pk=membership_id)
+        self.observation = get_or_create_evaluation_for_player(request.user, player, cycle, player_roster_membership=membership)
         if self.observation.status == OBSERVATION_STATUS_SUBMITTED:
             return redirect("analytics:assessment-detail", observation_id=self.observation.pk)
         return super().dispatch(request, *args, **kwargs)
@@ -425,6 +430,7 @@ class EvaluationReviewListView(EvaluationReviewRequiredMixin, TemplateView):
                 "review_list": review_list,
                 "rows": review_list.rows,
                 "filters": review_list.filters,
+                "seasons": review_list.seasons,
                 "cycles": review_list.cycles,
                 "evaluator_roles": review_list.evaluator_roles,
                 "perspective_choices": review_list.perspective_choices,
@@ -462,7 +468,7 @@ class CoachAssessmentListView(LoginRequiredMixin, TemplateView):
         players = Player.objects.none()
         player_statuses = []
         if cycle:
-            players = list_players_for_assessment(query=query, division=division, team=team)
+            players = list_memberships_for_assessment(cycle, query=query, division=division, team=team)
             player_statuses = assessment_status_for_players(list(players), cycle, self.request.user)
         context.update(
             {
@@ -505,7 +511,16 @@ class CoachAssessmentEditView(LoginRequiredMixin, TemplateView):
             existing = get_existing_coach_assessment(player, cycle, request.user)
             if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
                 return redirect("analytics:assessment-detail", observation_id=existing.pk)
-            self.observation = get_or_create_draft_coach_assessment(player, cycle, request.user)
+            membership = None
+            membership_id = request.GET.get("membership") or request.POST.get("membership")
+            if membership_id:
+                membership = get_object_or_404(PlayerRosterMembership, pk=membership_id)
+            self.observation = get_or_create_draft_coach_assessment(
+                player,
+                cycle,
+                request.user,
+                player_roster_membership=membership,
+            )
         return super().dispatch(request, *args, **kwargs)
 
     def get_form(self, data=None, require_required=False):
@@ -590,9 +605,15 @@ class StaffObservationReviewListView(AnalyticsStaffRequiredMixin, ListView):
     paginate_by = 25
 
     def get_queryset(self):
-        queryset = Observation.objects.select_related("player", "evaluation_cycle", "observation_type", "evaluator", "evaluator_role", "source").filter(
-            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT
-        )
+        queryset = Observation.objects.select_related(
+            "player",
+            "evaluation_cycle",
+            "season",
+            "observation_type",
+            "evaluator",
+            "evaluator_role",
+            "source",
+        ).filter(observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT)
         status = self.request.GET.get("status", "").strip()
         cycle = normalize_cycle_id(self.request.GET.get("cycle"))
         q = self.request.GET.get("q", "").strip()
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 58e31f2..0d352fd 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -202,7 +202,7 @@ What it must not own:
 
 Current status:
 
-Seasonal Participation V1 Phase 1 foundation, Phase 2 season-aware player import, and Phase 3 season-aware coach import are implemented. The schema, services, admin registration, tests, player import integration, and coach import integration exist. Player imports now create or update season teams and player roster memberships. Coach imports now create or update season teams and coach season assignments while preserving permanent coach accounts. Evaluations are not season-aware yet.
+Seasonal Participation V1 Phase 1 foundation, Phase 2 season-aware player import, Phase 3 season-aware coach import, and Phase 4 season-aware evaluation context are implemented. The schema, services, admin registration, tests, player import integration, coach import integration, and evaluation context integration exist. Player imports now create or update season teams and player roster memberships. Coach imports now create or update season teams and coach season assignments while preserving permanent coach accounts. New season-linked evaluations preserve season, player roster membership, player team/division snapshots, and coach assignment snapshots where applicable.
 
 Documentation:
 
@@ -344,6 +344,7 @@ The platform currently has:
 - production-ready staff-facing Account Operations
 - season-aware roster participation foundation
 - season-aware player and coach import integration
+- season-aware evaluation context and submitted-evaluation snapshots
 - account provisioning from player imports
 - forced password-change account flow
 - staff-only Analytics command center and reporting tables
@@ -360,7 +361,7 @@ Likely future areas:
 
 - Account Management V2
 - Analytics V2
-- Seasonal Participation Phase 4
+- Seasonal Participation Phase 5
 - Drafts expansion
 - LeagueHub
 - Video
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 9dc8ceb..310b4fb 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -15,7 +15,7 @@ The platform helps Vancouver Community Baseball manage:
 
 This is a user manual, not a technical deployment guide. Deployment information lives in [docs/deployment/](deployment/README.md).
 
-Season-aware roster foundations now exist in the system. Player and coach imports are now season-aware: staff choose an active season, and imported team/division information creates roster participation records or coach assignments for that season. Evaluation pages are not season-aware yet, so staff should continue using the current evaluation workflows until that seasonal phase is implemented.
+Season-aware roster foundations now exist in the system. Player imports, coach imports, and evaluations are season-aware: staff choose an active season for imports, imported team/division information creates roster participation records or coach assignments, and submitted evaluations preserve the season/team/division context that existed when the evaluation was submitted.
 
 ## Start Here
 
@@ -394,6 +394,9 @@ Parent accounts do not submit evaluations unless staff gives that user an evalua
 - Self evaluations are labeled Self Evaluation.
 - The system records who submitted the evaluation.
 - The evaluator's role/category and evaluation type are recorded for reporting and historical context.
+- The evaluation cycle determines the season for new evaluations when the cycle has a season.
+- The player list uses roster membership for that evaluation season.
+- Submitted evaluations preserve the season, team, and division at the time of submission.
 - Submitted evaluations become part of the player's Analytics record.
 
 ### Ratings And Notes
@@ -466,6 +469,8 @@ Coach review is read-only. It shows submitted evaluations only. Coaches cannot r
 
 Coach review shows evaluator names, role/category, and evaluation type. It does not show evaluator email addresses, passwords, import metadata, or unrelated account details.
 
+Coach review displays the saved season/team/division from the submitted evaluation. Later roster changes do not rewrite historical evaluation context.
+
 ## Staff Analytics
 
 ### Purpose
@@ -561,6 +566,8 @@ Staff can review submitted evaluations from:
 
 This page still uses `observations` in the URL because that is the internal Analytics record name. Staff review is used to inspect submitted evaluations and reopen them if corrections are needed.
 
+Staff review shows saved season and roster context for submitted evaluations. Older legacy records without season context may display as `Legacy / No Season`.
+
 ## Player Imports
 
 ### Purpose
diff --git a/docs/analytics/architecture/03_analytics.md b/docs/analytics/architecture/03_analytics.md
index 4673bc0..f60ca34 100644
--- a/docs/analytics/architecture/03_analytics.md
+++ b/docs/analytics/architecture/03_analytics.md
@@ -29,6 +29,9 @@ Each observation should include:
 
 - player reference to `players.Player`
 - evaluation cycle
+- season context when the evaluation cycle belongs to a season
+- roster membership and coach assignment references when available
+- submitted season/team/division snapshots for historical display stability
 - observation type
 - observation source/provider
 - evaluator/user who submitted or imported the observation, when applicable
diff --git a/docs/deployment/RUNBOOK.md b/docs/deployment/RUNBOOK.md
index c6442cf..3a29709 100644
--- a/docs/deployment/RUNBOOK.md
+++ b/docs/deployment/RUNBOOK.md
@@ -98,7 +98,7 @@ python manage.py migrate --plan
 
 ### Seasonal Participation Empty-State Check
 
-Before applying the initial `seasons` app migration, verify production still has no Platform V1 roster/evaluation data requiring seasonal backfill:
+Before applying the initial `seasons` app migration or the Analytics migration that adds observation season context, verify production still has no Platform V1 roster/evaluation data requiring seasonal backfill:
 
 ```text
 Players: 0
@@ -106,7 +106,7 @@ Coach profiles: 0
 Observations: 0
 ```
 
-If these counts are no longer zero, stop the deployment and create a reviewed migration/backfill plan. Do not fabricate legacy seasons, player roster memberships, coach assignments, or observation context during the schema migration.
+If these counts are no longer zero, stop the deployment and create a reviewed migration/backfill plan. Do not fabricate legacy seasons, player roster memberships, coach assignments, or observation context during the schema migration. Existing observations in non-production environments should remain nullable and display as `Legacy / No Season` unless a reviewed backfill plan exists.
 
 Apply migrations:
 
diff --git a/docs/seasons/README.md b/docs/seasons/README.md
index 47c34f9..ee3fd7b 100644
--- a/docs/seasons/README.md
+++ b/docs/seasons/README.md
@@ -25,6 +25,8 @@ Phase 2 - Season-Aware Player Import is implemented.
 
 Phase 3 - Season-Aware Coach Import is implemented.
 
+Phase 4 - Season-Aware Evaluation Context is implemented.
+
 Verified production state on July 15, 2026:
 
 ```text
@@ -69,13 +71,22 @@ Implemented coach import integration:
 - prior-season assignments are preserved;
 - coaches may have multiple teams and roles in the same season.
 
+Implemented evaluation context:
+
+- evaluation cycles can reference a season;
+- new evaluations created against a season-linked cycle resolve the player's roster membership for that season;
+- coach evaluations resolve a coach season assignment when one can be determined safely;
+- submitted evaluations preserve season, team, division, and coach-assignment snapshots;
+- review pages display submitted snapshots instead of live player team fields;
+- legacy observations without season context remain readable as `Legacy / No Season`.
+
 Current limitations:
 
-- evaluations do not yet store season/team/membership context;
 - there are no first-class roster-management pages yet.
+- stricter team-scoped coach permissions and peer team restrictions are deferred.
 
 Next phase:
 
-- Phase 4 - Evaluation Context.
+- Phase 5 - Read Models And UI.
 
-No evaluation workflow changes were made in Phase 3.
+Seasonal evaluation context was added in Phase 4 without adding dashboards, reports, roster-management pages, or stricter team-based authorization.
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
index bb0069a..42b5090 100644
--- a/docs/seasons/implementation/engineering/seasonal_participation_v1.md
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -1,6 +1,6 @@
 # Seasonal Participation V1 Engineering Plan
 
-Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 season-aware coach import complete. Phase 4 is the next implementation phase.
+Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 season-aware coach import complete. Phase 4 season-aware evaluation context complete. Phase 5 is the next implementation phase.
 
 Created: 2026-07-15.
 
@@ -700,6 +700,8 @@ Status: complete.
 
 ### Phase 4 - Evaluation Context
 
+Status: complete.
+
 - Add `EvaluationCycle.season`.
 - Add observation season/team/membership references and snapshot fields.
 - Do not backfill production observations unless new observations exist by then and a separate reviewed migration plan is approved.
@@ -800,8 +802,7 @@ Rollback considerations:
 - Another environment may contain Platform V1 data even though production is empty; any optional backfill path must be explicit and reviewable.
 - Future production data could be created between planning and Phase 1 deployment; pre-migration verification must re-check counts.
 - Primary membership constraints can be difficult to enforce perfectly on all databases with nullable dates.
-- Coach import currently resets reused coach passwords; this must change before season-aware reimports.
-- Existing analytics filters and metrics currently read from `Player.team_name` and `Player.division`.
+- Existing analytics metrics and non-evaluation player experience surfaces still rely partly on compatibility `Player.team_name` and `Player.division` fields.
 - Introducing team-scoped permissions too early could block valid evaluators.
 - A new `seasons` app creates a shared dependency that needs clear service boundaries.
 - Transfer handling requires staff UX decisions, not just schema.
@@ -817,11 +818,11 @@ Rollback considerations:
 
 ## 27. Recommended Next Implementation Phase
 
-Start with Phase 4 - Evaluation Context.
+Start with Phase 5 - Read Models And UI.
 
-Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services. Phase 3 updated coach import to require a selected season, create or reuse `SeasonTeam`, and create/update `CoachSeasonAssignment` through `seasons` services while preserving existing coach passwords.
+Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services. Phase 3 updated coach import to require a selected season, create or reuse `SeasonTeam`, and create/update `CoachSeasonAssignment` through `seasons` services while preserving existing coach passwords. Phase 4 added season-linked evaluation cycles, observation seasonal context fields, submitted-evaluation snapshots, season-aware player selectors, and snapshot-based review display.
 
-Before implementing Phase 4, verify that Phase 3 production rollout completed successfully and that imported coach rows are creating expected season teams and coach assignments.
+Before implementing Phase 5, verify that Phase 4 production rollout completed successfully and that new submitted evaluations are recording expected season, roster membership, and snapshot values.
 
 ## 28. Acceptance Criteria
 
diff --git a/drafts/tests.py b/drafts/tests.py
index e8c1440..3a509dd 100644
--- a/drafts/tests.py
+++ b/drafts/tests.py
@@ -7,6 +7,9 @@ from analytics.models import RESPONSE_TYPE_RATING_1_5, EvaluationCycle
 from analytics.services.observation_service import create_coach_assessment_observation, submit_observation
 from analytics.services.question_service import ensure_default_coach_assessment_setup
 from players.models import Player
+from seasons.services.membership_service import create_membership
+from seasons.services.season_service import create_season
+from seasons.services.team_service import get_or_create_season_team
 
 from .models import Draft, DraftActionType, DraftPlayer, DraftStatus
 from .services import (
@@ -141,12 +144,16 @@ class DraftViewTests(TestCase):
 
     def test_command_center_renders_read_only_analytics_draft_context(self):
         coach = get_user_model().objects.create_user(username="context-coach", password="secret123")
-        player = Player.objects.create(first_name="Ava", last_name="Lopez", birth_year=2012, division="13U")
+        player = Player.objects.create(first_name="Ava", last_name="Lopez", birth_year=2012, division="13U", team_name="Expos")
+        season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        season_team, _ = get_or_create_season_team(season=season, name="Expos", division="13U")
+        create_membership(player=player, season_team=season_team, is_primary=True, is_active=True)
         setup_result = ensure_default_coach_assessment_setup()
         cycle = EvaluationCycle.objects.create(
             name="2026 13U Coach Assessment",
             cycle_type="Coach Assessment",
             coach_assessment_question_set=setup_result.question_set,
+            season=season,
         )
         draft_player = DraftPlayer.objects.create(
             draft=self.draft,

```
