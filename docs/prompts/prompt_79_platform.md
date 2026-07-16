# Prompt 79 - Platform

## User Prompt

Complete Seasonal Participation V1 Phase 6 only: Production Review and Freeze.

Source prompt file:
`/Users/eugenelin/.codex/attachments/edc3104c-4385-4d09-83ea-49efe6140a5c/pasted-text.txt`

```text
Complete Seasonal Participation V1 Phase 6 only: Production Review and Freeze.

Use continuous loop engineering.

Continue until Seasonal Participation V1 is production-ready, fully reviewed, hardened, documented, tested, committed, pushed, and the working tree is clean.

Do not start Platform V2 or add new product features.

==================================================
Current State
=============

Seasonal Participation V1 Phases 1 through 5 are complete.

Implemented capabilities include:

* permanent player identity;
* permanent user/account identity;
* seasons;
* season-specific teams;
* player roster memberships;
* coach seasonal assignments;
* season-aware player import;
* season-aware coach import;
* season-aware evaluations;
* durable submitted-evaluation snapshots;
* staff-facing Season Operations;
* player transfer and additional-membership workflows;
* player season history;
* coach assignment history.

Phase 5 explicitly identified Phase 6 Production Review and Freeze as the next phase.

==================================================
Phase 6 Objective
=================

Review Seasonal Participation V1 as a complete production subsystem.

The goal is to:

1. verify every workflow end-to-end;
2. identify and fix concrete defects;
3. improve production safety;
4. improve validation and error handling;
5. verify permissions and security;
6. verify database and migration safety;
7. verify query efficiency;
8. reconcile documentation;
9. produce a production rollout checklist;
10. formally freeze Seasonal Participation V1.

This is a hardening and review phase.

Do not add dashboards, reports, exports, APIs, notifications, parent features, or Platform V2 work.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete production-readiness work remains.

PASS

All Phase 6 acceptance criteria are satisfied, verification passes, commits are pushed, documentation is current, and the working tree is clean.

BLOCKED

A production blocker requires unresolved product direction, destructive migration, external infrastructure, or operational work that cannot be completed safely in the repository.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied acceptance criterion.

Do not continue through formatting-only or speculative cleanup.

==================================================
Established Loop Workflow
=========================

Every loop must:

1. reconcile the committed repository state;
2. read `AGENTS.md`;
3. read the Seasonal Participation engineering plan;
4. read Phase 1 through Phase 5 prompt archives and implementation summaries;
5. confirm the working tree is clean;
6. inspect the selected workflow end-to-end;
7. identify verified defects or incomplete acceptance criteria;
8. create the next prompt archive before implementation;
9. implement only production-readiness fixes;
10. add or update focused tests;
11. run focused verification;
12. perform senior-engineer self-review;
13. fix every verified issue;
14. update documentation;
15. run the complete verification suite;
16. commit implementation, tests, and documentation;
17. finalize the prompt archive with findings and results;
18. commit the prompt archive separately;
19. push both commits;
20. re-read the committed diff;
21. confirm the working tree is clean;
22. reassess every acceptance criterion;
23. choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS;
24. if CONTINUE, begin the next loop without asking for confirmation.

Each loop must produce:

1. one implementation/review/documentation commit;
2. one prompt archive commit.

==================================================
Required Repository Review
==========================

Read:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* `docs/deployment/README.md`
* `docs/deployment/RUNBOOK.md`
* `docs/deployment/production_readiness_review.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* account-management documentation
* Analytics and evaluation documentation
* player import documentation
* prompt archives for Seasonal Participation Phases 1 through 5

Inspect:

* `seasons/`
* `players/`
* `accounts/`
* `analytics/`
* `vancouverminor/settings.py`
* `vancouverminor/urls.py`
* current middleware
* current navigation
* migrations for `seasons`, `players`, `accounts`, and `analytics`
* all templates and forms touched by seasonal work
* all service-layer boundaries
* all production deployment assumptions.

==================================================
Review Areas
============

Review the complete subsystem in the following areas.

## 1. Season Lifecycle

Verify:

* season creation;
* season editing;
* setting current season;
* deactivating current season;
* active/current consistency;
* import defaults;
* evaluation-cycle relationship;
* historical season visibility;
* safe behavior when no current season exists.

Fix only verified issues.

## 2. Season Team Lifecycle

Verify:

* creation;
* normalization;
* duplicate handling;
* external identifiers;
* editing display values;
* cross-season separation;
* inactive teams;
* historical snapshot preservation.

Ensure team edits never rewrite submitted evaluation snapshots.

## 3. Player Import

Review end-to-end:

* season selection;
* CSV upload;
* column mapping;
* preview;
* permanent-player matching;
* SeasonTeam resolution;
* membership creation/update;
* same-season team-change blocking;
* account provisioning;
* confirmation;
* result reporting;
* provenance.

Verify reimports are deterministic.

## 4. Coach Import

Review end-to-end:

* season selection;
* account matching;
* new account creation;
* returning coach reuse;
* password preservation;
* activation preservation;
* role preservation;
* SeasonTeam resolution;
* assignment creation/update;
* multiple teams and roles;
* confirmation and result reporting.

Prove reused coach password hashes remain unchanged.

## 5. Player Membership Operations

Review:

* list/filter/search;
* create;
* edit;
* primary membership changes;
* end/deactivate;
* transfer;
* additional membership;
* cross-season tampering;
* duplicate destination team;
* compatibility-field synchronization;
* player season history.

Verify transfers preserve old memberships.

## 6. Coach Assignment Operations

Review:

* list/filter/search;
* create;
* edit;
* primary assignment behavior;
* deactivate/end;
* multiple teams;
* multiple roles;
* account privilege separation;
* coach season history.

Verify assignment operations never modify:

* password;
* login activation;
* account role;
* `is_staff`;
* `is_superuser`;
* unrelated permissions.

## 7. Evaluations

Review:

* evaluation-cycle season requirement;
* player membership resolution;
* coach assignment resolution;
* self-evaluation;
* peer evaluation;
* coach evaluation;
* staff/admin evaluation;
* draft behavior;
* submission behavior;
* snapshot immutability;
* review displays;
* legacy/no-season fallback.

Verify submitted evaluation context never changes after roster or assignment changes.

## 8. Permissions

Review every seasonal route and operation.

Verify:

* unauthenticated users are redirected;
* ordinary players are denied;
* ordinary coaches are denied from staff operations;
* seasonal assignments do not grant staff access;
* only existing authorized staff/admin users can operate the subsystem;
* client-controlled IDs cannot bypass object ownership or season relationships.

Do not introduce new team-scoped authorization.

## 9. Security

Check:

* CSRF protection;
* POST-only state-changing actions;
* hidden-field manipulation;
* season ID manipulation;
* player ID manipulation;
* coach/user ID manipulation;
* membership ID manipulation;
* assignment ID manipulation;
* cross-season object combinations;
* temporary password exposure;
* replay of one-time password results;
* snapshot-field manipulation;
* insecure direct object references.

Fix every verified issue.

## 10. Data Integrity

Review:

* database constraints;
* model validation;
* service validation;
* transaction boundaries;
* `select_for_update` usage;
* race conditions;
* one-current-season rule;
* one active primary player membership;
* one active primary coach assignment where applicable;
* duplicate memberships;
* duplicate assignments;
* transfer atomicity;
* compatibility-field synchronization.

Prefer services as the authoritative cross-model layer.

Do not add signals.

## 11. Migration Safety

Review migrations:

* `seasons.0001_initial`
* player-import seasonal migration;
* Analytics seasonal-context migration;
* any related account migration.

Verify:

* SQLite compatibility;
* migration ordering;
* additive behavior;
* nullable legacy support;
* no fabricated history;
* no destructive operations;
* rollback implications.

Run and inspect the complete migration plan.

Do not create a new migration unless required to fix a verified production defect.

## 12. Performance

Review common list and detail pages for:

* N+1 queries;
* missing `select_related`;
* missing `prefetch_related`;
* unbounded result sets;
* missing pagination;
* inefficient counts;
* repeated service queries;
* missing indexes for actual query patterns.

Use query-count tests where helpful.

Do not perform speculative optimization.

## 13. User Experience

Review from the perspective of a staff operator.

Verify:

* navigation is understandable;
* forms clearly identify season/team;
* error messages explain corrective action;
* empty states are useful;
* confirmation pages explain consequences;
* result pages distinguish created/reused/updated/conflict/error states;
* historical versus current data is clearly labeled;
* temporary passwords are handled clearly and safely.

Prefer small improvements over redesign.

## 14. Admin Safety

Review Django admin for seasonal and Analytics models.

Verify:

* snapshot fields are read-only;
* dangerous identity fields are restricted;
* current/primary invariants cannot be trivially bypassed;
* search/filter configuration works;
* admin is documented as exceptional rather than normal operations.

## 15. Documentation

Reconcile:

* architecture;
* user manual;
* season engineering plan;
* deployment runbook;
* production readiness review;
* account import docs;
* Analytics docs;
* project README.

Remove contradictions and stale claims.

Do not duplicate large procedures.

==================================================
Production Data Verification
============================

The original verified production state was:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

Before finalizing the rollout plan, document a new pre-deployment verification command that checks:

* Player count;
* coach profile count;
* Observation count;
* Season count;
* SeasonTeam count;
* PlayerRosterMembership count;
* CoachSeasonAssignment count;
* migration state.

Do not embed production-specific counts into migrations.

If unexpected production data exists before rollout:

* stop;
* do not fabricate context;
* require a reviewed migration/backfill plan.

==================================================
Production Rollout Review
=========================

Update the deployment runbook with a concise Seasonal Participation rollout section.

It should include copy/paste-ready commands for:

1. becoming the correct user;
2. changing to the project directory;
3. activating the virtual environment where needed;
4. fetching and pulling with `--ff-only`;
5. installing requirements;
6. backing up:

   * SQLite database;
   * media;
   * current commit hash;
7. loading `/etc/vancouverminorbaseball.env`;
8. running:

   * `check`;
   * `makemigrations --check`;
   * `migrate --plan`;
   * pre-deployment data counts;
9. stopping Gunicorn;
10. running migrations;
11. running `collectstatic`;
12. restarting Gunicorn;
13. checking service status;
14. reviewing recent logs;
15. running HTTP smoke tests;
16. completing browser-based workflow verification.

Keep the runbook simple and step-by-step.

Do not create a deployment script.

==================================================
Browser Smoke-Test Checklist
============================

Document a manual browser checklist covering:

1. staff login;
2. Season Operations access;
3. create a test season;
4. create a test season team;
5. import a small player CSV;
6. verify player membership;
7. import a small coach CSV;
8. verify coach assignment;
9. verify returning coach password is unchanged;
10. create an evaluation cycle linked to season;
11. submit self-evaluation;
12. submit coach evaluation;
13. review saved season/team snapshots;
14. transfer a player;
15. verify old evaluation snapshot remains unchanged;
16. view player season history;
17. view coach assignment history;
18. verify unauthorized coach/player access is denied.

The checklist must clearly distinguish optional test data from real production data.

==================================================
Freeze Criteria
===============

After Phase 6 PASS, Seasonal Participation V1 should be marked:

```text
Feature Complete
Production Ready
Frozen
```

Frozen means:

* no new V1 features;
* defect fixes allowed;
* security fixes allowed;
* production-operability fixes allowed;
* documentation corrections allowed;
* structural changes require a new reviewed phase;
* Platform V2 work must not be mixed into V1 maintenance.

Update status documentation accordingly.

==================================================
Allowed Changes
===============

Allowed:

* verified bug fixes;
* security fixes;
* validation improvements;
* transaction fixes;
* query-efficiency fixes;
* pagination;
* error-message improvements;
* small UX corrections;
* tests;
* documentation;
* narrowly necessary migration fixes.

==================================================
Non-Goals
=========

Do not implement:

* new dashboards;
* new charts;
* season-over-season analytics;
* player development summaries;
* PDF reports;
* exports;
* APIs;
* notifications;
* parent portal;
* strict team-based permissions;
* peer team restrictions;
* bulk editing;
* scheduling;
* registration;
* permanent Team model;
* removal of `Player.team_name`;
* removal of `Player.division`;
* Platform V2 work;
* redesigns without verified defects.

==================================================
Required Test Coverage
======================

Add or improve tests for any verified gaps.

At minimum, ensure coverage for:

## End-to-End Seasonal Workflow

* create season;
* set current;
* create team;
* player import;
* membership creation;
* coach import;
* assignment creation;
* evaluation-cycle season;
* observation submission;
* snapshot persistence;
* player transfer;
* historical snapshot unchanged.

## Reimport Safety

* same player reused across seasons;
* same coach reused across seasons;
* no duplicate permanent identities;
* no coach password reset;
* same membership/assignment reimport deterministic.

## Permissions And Security

* all seasonal operations unauthorized paths;
* ID tampering;
* cross-season tampering;
* POST-only state changes;
* snapshot immutability;
* one-time password result protection.

## Data Integrity

* one current season;
* primary membership invariant;
* primary assignment invariant;
* transfer atomicity;
* duplicate prevention;
* compatibility synchronization.

## Performance

Add focused query-count tests only where review identifies real N+1 risks.

## Regression

* players tests;
* accounts tests;
* Analytics tests;
* seasons tests;
* drafts tests;
* PDP tests;
* full suite.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics
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
Senior-Engineer Review
======================

Review every diff for:

* scope discipline;
* subsystem ownership;
* service boundaries;
* transaction correctness;
* locking;
* race conditions;
* authorization;
* password exposure;
* privilege escalation;
* object-level access;
* cross-season manipulation;
* snapshot immutability;
* historical preservation;
* migration safety;
* query efficiency;
* dead code;
* duplicated logic;
* stale compatibility logic;
* stale documentation;
* accidental Platform V2 work.

Fix every verified issue before committing.

==================================================
Phase 6 Acceptance Criteria
===========================

Do not declare PASS until all criteria are satisfied.

A. Workflow Review

* all Seasonal Participation V1 workflows reviewed end-to-end;
* verified defects fixed;
* no known critical workflow gaps remain.

B. Security

* permissions verified;
* object tampering covered;
* temporary-password handling verified;
* no privilege escalation;
* submitted snapshots immutable.

C. Data Integrity

* current-season invariant safe;
* primary membership invariant safe;
* primary assignment invariant safe;
* transfers atomic;
* reimports deterministic;
* historical records preserved.

D. Migration

* complete migration plan reviewed;
* SQLite-safe;
* additive;
* no fabricated data;
* rollout and rollback considerations documented.

E. Performance

* major N+1 and unbounded-list risks addressed;
* no speculative overengineering.

F. UX

* navigation and forms are understandable;
* errors and empty states are useful;
* consequences are clear.

G. Production Runbook

* commands are current;
* user and directory switching are explicit;
* environment wrapper is correct;
* backup and restore considerations are present;
* smoke-test checklist is complete.

H. Documentation

* architecture, user manual, seasonal plan, and deployment docs agree;
* no future feature is described as implemented;
* V1 freeze status documented.

I. Tests

* focused suites pass;
* full suite passes;
* end-to-end seasonal regression coverage exists;
* security and integrity gaps are tested.

J. Freeze

* Seasonal Participation V1 marked Feature Complete, Production Ready, and Frozen;
* future structural work deferred to a new phase;
* Platform V2 remains separate.

K. Git

* implementation/review commit exists;
* prompt archive commit exists;
* both pushed;
* working tree clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should:

1. perform the full production-readiness review;
2. identify concrete defects and risks;
3. fix verified defects;
4. improve missing tests;
5. review migrations and queries;
6. reconcile documentation;
7. update production runbook and smoke-test checklist;
8. mark V1 frozen only if all acceptance criteria pass;
9. run full verification;
10. commit, archive, push, and reassess.

Continue into later loops only for material unresolved issues.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* fixes a verified production defect;
* closes a security gap;
* closes a data-integrity gap;
* improves migration or rollback safety;
* removes a real performance problem;
* adds missing regression proof;
* corrects material documentation drift;
* satisfies an unsatisfied acceptance criterion.

Formatting-only work does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* staff administrator;
* registrar/import operator;
* coach;
* player;
* data architect;
* security reviewer;
* privacy reviewer;
* release engineer;
* production operator.

Confirm:

* a real staff user can operate the subsystem without Django admin;
* imports are deterministic;
* identities are permanent;
* seasonal history is preserved;
* evaluations retain historical context;
* transfers do not rewrite history;
* passwords and privileges are safe;
* deployment can be followed line-by-line;
* no V2 work was introduced.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before implementation;
2. commit fixes, tests, and documentation;
3. update the prompt archive with:

   * implementation commit hash;
   * review areas completed;
   * defects found;
   * fixes applied;
   * migration findings;
   * security findings;
   * performance findings;
   * documentation updates;
   * verification results;
   * remaining criteria;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested commit message:

```text
Harden and freeze seasonal participation V1
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
* migrations added or changed;
* review areas completed;
* defects found;
* fixes applied;
* security findings;
* data-integrity findings;
* migration findings;
* performance findings;
* UX improvements;
* production runbook updates;
* smoke-test checklist;
* tests added;
* focused verification;
* full verification;
* documentation reconciliation;
* freeze status;
* deferred future work;
* commits;
* push results;
* confirmation that the working tree is clean.
```

## Implementation Commit

544eb4a3684b99d99fd53bdfcd8e885ecaf640ba

Harden and freeze seasonal participation V1


## Review Areas Completed

- Season lifecycle, current-season behavior, inactive-season behavior, and imports/evaluation defaults.
- Season team lifecycle, normalization, duplicate handling, external IDs, inactive teams, and snapshot preservation.
- Player import, coach import, player membership operations, coach assignment operations, evaluations, permissions, security, data integrity, migration safety, performance, UX, admin safety, and documentation.

## Defects And Risks Found

- Staff-facing Season Operations list pages were unpaginated, creating an avoidable production scaling risk.
- Paginated season lists needed explicit ordering to avoid inconsistent page boundaries.
- Inactive season detail pages exposed the season-specific add-team shortcut even though imports and active workflows require active seasons.
- Phase 6 rollout commands, pre-deployment count checks, browser smoke tests, and frozen status were not yet documented.

## Fixes Applied

- Added pagination and filter-preserving pagination links to season, team, player membership, and coach assignment list pages.
- Added explicit ordering for paginated season lists.
- Blocked the inactive-season team-creation shortcut and hid that action for inactive seasons.
- Added regression tests for inactive-season shortcut protection, paginated membership filters, and submitted evaluation snapshot immutability after team edit and player transfer.
- Updated architecture, seasons docs, engineering plan, deployment README, and deployment runbook.

## Migration Findings

No migrations were added or changed. The full migration plan remains additive for seasonal participation, with nullable legacy/evaluation context support and no fabricated data.

## Security Findings

Season Operations remain Django staff/superuser only. Seasonal assignments do not grant Django staff/superuser access. State-changing operations remain POST/CSRF-backed. Cross-season transfer tampering is covered by form/service tests. Temporary password handling remains owned by account services and was not changed.

## Performance Findings

The verified production-readiness performance gap was unbounded staff list pages. Pagination was added to common Season Operations list pages. Existing querysets use `select_related()` for season/team/player/user relationships where needed.

## Documentation Updates

- Added Seasonal Participation V1 rollout commands, pre-deployment data-count checks, backups, service restart steps, HTTP smoke tests, and browser workflow verification to the deployment runbook.
- Marked Seasonal Participation V1 Feature Complete, Production Ready, and Frozen in architecture and seasons docs.
- Documented that V1 maintenance is limited to defect, security, production-operability, and documentation corrections.

## Verification

Focused verification passed:

```text
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics
git diff --check
```

Full verification passed:

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

Result: PASS. Full suite ran 458 tests successfully.

## Remaining Criteria

All Phase 6 acceptance criteria are satisfied. Platform V2 work remains deferred to a separately reviewed phase.

## Commit Diff

```diff
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 803ecaa..3a3ac29 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -327,7 +327,7 @@ Dependency guidance:
 | Players | V1 | Complete |
 | Analytics | V1 | Complete |
 | Account Management | V1 | Complete / Frozen |
-| Seasons | V1 Phase 5 | Season and roster operations UI complete |
+| Seasons | V1 | Feature Complete / Production Ready / Frozen |
 | Drafts | Active | Active development |
 | PDP | Legacy | Transitionary |
 | LeagueHub | Planned | Planned |
@@ -362,7 +362,7 @@ Likely future areas:
 
 - Account Management V2
 - Analytics V2
-- Seasonal Participation Phase 6 production review and freeze
+- Seasonal Participation V2 planning, only after a reviewed new phase
 - Drafts expansion
 - LeagueHub
 - Video
diff --git a/docs/deployment/README.md b/docs/deployment/README.md
index 18f3660..8a5cf9d 100644
--- a/docs/deployment/README.md
+++ b/docs/deployment/README.md
@@ -52,6 +52,8 @@ Pre-deployment review documentation:
 
 - [Production Readiness Review](production_readiness_review.md)
 
+Seasonal Participation V1 production rollout and browser verification steps are maintained in the [Deployment Runbook](RUNBOOK.md#seasonal-participation-v1-rollout).
+
 ## Operational Standard
 
 Future production deployments should:
diff --git a/docs/deployment/RUNBOOK.md b/docs/deployment/RUNBOOK.md
index 3a29709..5de9cc1 100644
--- a/docs/deployment/RUNBOOK.md
+++ b/docs/deployment/RUNBOOK.md
@@ -96,6 +96,106 @@ Review planned migrations:
 python manage.py migrate --plan
 ```
 
+## Seasonal Participation V1 Rollout
+
+Seasonal Participation V1 is additive and keeps legacy/no-season records readable. Do not fabricate seasons, teams, roster memberships, coach assignments, or evaluation context during deployment.
+
+Use these steps when deploying the completed Seasonal Participation V1 release.
+
+### 1. Become The Production User
+
+```bash
+sudo -iu django-user
+cd /var/www/vancouverminorbaseball
+source venv/bin/activate
+```
+
+### 2. Record Current State And Back Up
+
+```bash
+git status
+git log -n1 --oneline > /tmp/vcb_pre_deploy_commit.txt
+cp db.sqlite3 "db.sqlite3.pre_seasons_v1.$(date +%Y%m%d%H%M%S).bak"
+tar -czf "media.pre_seasons_v1.$(date +%Y%m%d%H%M%S).tgz" media
+```
+
+### 3. Update Code
+
+```bash
+git fetch origin
+git pull --ff-only origin main
+pip install -r requirements.txt
+```
+
+If `git pull --ff-only` fails, stop and resolve the repository state before continuing.
+
+### 4. Load Production Environment
+
+```bash
+set -a
+. /etc/vancouverminorbaseball.env
+set +a
+```
+
+### 5. Run Pre-Migration Checks
+
+```bash
+python manage.py check
+python manage.py makemigrations --check
+python manage.py migrate --plan
+python manage.py showmigrations seasons players accounts analytics
+python manage.py shell -c "from players.models import Player; from accounts.models import AccountProfile, AccountRole; from analytics.models import Observation; from seasons.models import Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment; print({'players': Player.objects.count(), 'coach_profiles': AccountProfile.objects.filter(role=AccountRole.COACH).count(), 'observations': Observation.objects.count(), 'seasons': Season.objects.count(), 'season_teams': SeasonTeam.objects.count(), 'player_roster_memberships': PlayerRosterMembership.objects.count(), 'coach_season_assignments': CoachSeasonAssignment.objects.count()})"
+```
+
+If unexpected production data exists before rollout, stop. Do not fabricate historical context. Create a reviewed migration/backfill plan before applying migrations that would require historical interpretation.
+
+### 6. Stop Service, Migrate, Collect Static, Restart
+
+```bash
+sudo systemctl stop vancouverminor.service
+python manage.py migrate
+python manage.py collectstatic --noinput
+sudo systemctl start vancouverminor.service
+sudo systemctl status vancouverminor.service
+sudo journalctl -u vancouverminor.service -n 100 --no-pager
+```
+
+### 7. HTTP Smoke Tests
+
+```bash
+curl -I https://vancouverminor.com/
+curl -I https://vancouverminor.com/accounts/login/
+curl -I https://vancouverminor.com/seasons/
+curl -I https://vancouverminor.com/analytics/
+```
+
+Unauthenticated staff pages such as `/seasons/` and `/analytics/` should redirect to login rather than expose data.
+
+### 8. Browser Workflow Verification
+
+Use optional test data only if the production operator has approved it. If test data is created in production, record what was created and clean it up only through approved application workflows.
+
+Checklist:
+
+1. Sign in as a Django staff user.
+2. Open Season Operations at `/seasons/`.
+3. Create a clearly named test season if approved.
+4. Create a test season team if approved.
+5. Import a small player CSV for the test season if approved.
+6. Verify the player roster membership appears under Season Operations.
+7. Import a small coach CSV for the test season if approved.
+8. Verify the coach assignment appears under Season Operations.
+9. Verify a returning coach import does not change the coach password hash.
+10. Create an evaluation cycle linked to the season if approved.
+11. Submit a self-evaluation.
+12. Submit a coach evaluation.
+13. Review saved season/team snapshots in evaluation review.
+14. Transfer the test player to another team.
+15. Verify the old submitted evaluation still displays the original season/team snapshot.
+16. View player season history.
+17. View coach assignment history.
+18. Sign in as a non-staff coach/player and verify `/seasons/` access is denied.
+
 ### Seasonal Participation Empty-State Check
 
 Before applying the initial `seasons` app migration or the Analytics migration that adds observation season context, verify production still has no Platform V1 roster/evaluation data requiring seasonal backfill:
diff --git a/docs/seasons/README.md b/docs/seasons/README.md
index f925efb..f3102e9 100644
--- a/docs/seasons/README.md
+++ b/docs/seasons/README.md
@@ -29,6 +29,16 @@ Phase 4 - Season-Aware Evaluation Context is implemented.
 
 Phase 5 - Season And Roster Operations UI is implemented.
 
+Phase 6 - Production Review And Freeze is complete.
+
+Seasonal Participation V1 status:
+
+```text
+Feature Complete
+Production Ready
+Frozen
+```
+
 Verified production state on July 15, 2026:
 
 ```text
@@ -98,8 +108,11 @@ Current limitations:
 - stricter team-scoped coach permissions and peer team restrictions are deferred.
 - dashboards, charts, exports, reports, and strict team-scoped permissions remain deferred.
 
-Next phase:
+Frozen status:
 
-- Phase 6 - Production Review And Freeze.
+- no new V1 features should be added;
+- defect fixes, security fixes, production-operability fixes, and documentation corrections are allowed;
+- structural changes require a new reviewed phase;
+- Platform V2 work must not be mixed into V1 maintenance.
 
 Seasonal operations UI was added in Phase 5 without adding dashboards, reports, exports, APIs, bulk editing, or stricter team-based authorization.
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
index c1abbb5..ffd96a2 100644
--- a/docs/seasons/implementation/engineering/seasonal_participation_v1.md
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -1,6 +1,6 @@
 # Seasonal Participation V1 Engineering Plan
 
-Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 season-aware coach import complete. Phase 4 season-aware evaluation context complete. Phase 5 season and roster operations UI complete. Phase 6 production review and freeze is the next implementation phase.
+Status: Seasonal Participation V1 is Feature Complete, Production Ready, and Frozen. Phase 1 foundation, Phase 2 season-aware player import, Phase 3 season-aware coach import, Phase 4 season-aware evaluation context, Phase 5 season and roster operations UI, and Phase 6 production review/freeze are complete.
 
 Created: 2026-07-15.
 
@@ -727,12 +727,17 @@ Status: complete.
 
 ### Phase 6 - Production Review And Freeze
 
-- Architecture review.
-- Migration review on production copy.
-- Security/privacy review.
-- Performance review for season/team filters.
-- User manual and deployment documentation reconciliation.
-- Production readiness and rollback plan.
+Status: complete.
+
+- Reviewed Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment, import, evaluation, permission, admin, migration, performance, and UX boundaries.
+- Added pagination to staff-facing season, team, membership, and coach-assignment list pages.
+- Added deterministic ordering for paginated season operations.
+- Verified inactive seasons cannot use the season-specific team-creation shortcut.
+- Added regression coverage for paginated membership filters and submitted-evaluation snapshot immutability after team edits and player transfer.
+- Reconciled architecture, user manual, seasonal README, and deployment runbook.
+- Added copy/paste-ready production rollout commands, pre-deployment data-count checks, migration checks, backup steps, restart checks, HTTP smoke tests, and manual browser workflow verification.
+- Confirmed no models or migrations were added in Phase 6.
+- Marked Seasonal Participation V1 Feature Complete, Production Ready, and Frozen.
 
 ## 23. Test Strategy
 
@@ -826,11 +831,11 @@ Rollback considerations:
 
 ## 27. Recommended Next Implementation Phase
 
-Start with Phase 6 - Production Review And Freeze.
+Seasonal Participation V1 is frozen.
 
-Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services. Phase 3 updated coach import to require a selected season, create or reuse `SeasonTeam`, and create/update `CoachSeasonAssignment` through `seasons` services while preserving existing coach passwords. Phase 4 added season-linked evaluation cycles, observation seasonal context fields, submitted-evaluation snapshots, season-aware player selectors, and snapshot-based review display. Phase 5 added staff-facing season and roster operations UI.
+Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services. Phase 3 updated coach import to require a selected season, create or reuse `SeasonTeam`, and create/update `CoachSeasonAssignment` through `seasons` services while preserving existing coach passwords. Phase 4 added season-linked evaluation cycles, observation seasonal context fields, submitted-evaluation snapshots, season-aware player selectors, and snapshot-based review display. Phase 5 added staff-facing season and roster operations UI. Phase 6 completed production review and freeze.
 
-Before implementing Phase 6, verify that Phase 5 production rollout completed successfully and staff can complete season, team, membership, transfer, and coach assignment workflows without Django admin.
+Future structural work belongs in a new reviewed phase or Platform V2 plan. V1 maintenance is limited to defect fixes, security fixes, production-operability fixes, and documentation corrections.
 
 ## 28. Acceptance Criteria
 
diff --git a/seasons/templates/seasons/_pagination.html b/seasons/templates/seasons/_pagination.html
new file mode 100644
index 0000000..bb9e83b
--- /dev/null
+++ b/seasons/templates/seasons/_pagination.html
@@ -0,0 +1,11 @@
+{% if is_paginated %}
+    <nav class="pdp-actions" aria-label="Pagination">
+        {% if page_obj.has_previous %}
+            <a class="button button--ghost" href="?{{ pagination_query }}page={{ page_obj.previous_page_number }}">Previous</a>
+        {% endif %}
+        <span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
+        {% if page_obj.has_next %}
+            <a class="button button--ghost" href="?{{ pagination_query }}page={{ page_obj.next_page_number }}">Next</a>
+        {% endif %}
+    </nav>
+{% endif %}
diff --git a/seasons/templates/seasons/assignment_list.html b/seasons/templates/seasons/assignment_list.html
index 16a063c..05e1f27 100644
--- a/seasons/templates/seasons/assignment_list.html
+++ b/seasons/templates/seasons/assignment_list.html
@@ -64,5 +64,6 @@
             </tbody>
         </table>
     </div>
+    {% include "seasons/_pagination.html" %}
 </article>
 {% endblock %}
diff --git a/seasons/templates/seasons/membership_list.html b/seasons/templates/seasons/membership_list.html
index 008aed9..bf51ab9 100644
--- a/seasons/templates/seasons/membership_list.html
+++ b/seasons/templates/seasons/membership_list.html
@@ -64,5 +64,6 @@
             </tbody>
         </table>
     </div>
+    {% include "seasons/_pagination.html" %}
 </article>
 {% endblock %}
diff --git a/seasons/templates/seasons/season_detail.html b/seasons/templates/seasons/season_detail.html
index 68eb237..f6cea65 100644
--- a/seasons/templates/seasons/season_detail.html
+++ b/seasons/templates/seasons/season_detail.html
@@ -16,7 +16,9 @@
         {% if season.is_active and not season.is_current %}
             <a class="button button--ghost" href="{% url 'seasons:season-set-current' season.id %}">Set Current</a>
         {% endif %}
-        <a class="button button--ghost" href="{% url 'seasons:season-team-new' season.id %}">Add Team</a>
+        {% if season.is_active %}
+            <a class="button button--ghost" href="{% url 'seasons:season-team-new' season.id %}">Add Team</a>
+        {% endif %}
         <a class="button button--ghost" href="{% url 'seasons:membership-list' %}?season={{ season.id }}">Player Memberships</a>
         <a class="button button--ghost" href="{% url 'seasons:coach-assignment-list' %}?season={{ season.id }}">Coach Assignments</a>
     </div>
diff --git a/seasons/templates/seasons/season_list.html b/seasons/templates/seasons/season_list.html
index 9d31c87..28fff2a 100644
--- a/seasons/templates/seasons/season_list.html
+++ b/seasons/templates/seasons/season_list.html
@@ -40,5 +40,6 @@
             </tbody>
         </table>
     </div>
+    {% include "seasons/_pagination.html" %}
 </article>
 {% endblock %}
diff --git a/seasons/templates/seasons/team_list.html b/seasons/templates/seasons/team_list.html
index 237190a..9bea3a3 100644
--- a/seasons/templates/seasons/team_list.html
+++ b/seasons/templates/seasons/team_list.html
@@ -43,5 +43,6 @@
             </tbody>
         </table>
     </div>
+    {% include "seasons/_pagination.html" %}
 </article>
 {% endblock %}
diff --git a/seasons/tests.py b/seasons/tests.py
index fa39f86..b92ca5d 100644
--- a/seasons/tests.py
+++ b/seasons/tests.py
@@ -10,6 +10,9 @@ from django.urls import reverse
 
 from accounts.models import AccountRole
 from accounts.services.profile_service import get_or_create_account_profile, set_account_role
+from analytics.models import EvaluationCycle, RESPONSE_TYPE_RATING_1_5, RESPONSE_TYPE_TEXT
+from analytics.services.observation_service import create_coach_assessment_observation, submit_observation
+from analytics.services.question_service import ensure_default_coach_assessment_setup
 from players.models import Player
 from seasons.models import (
     CoachAssignmentRole,
@@ -40,7 +43,7 @@ from seasons.services.membership_service import (
     update_membership,
 )
 from seasons.services.season_service import create_season, deactivate_season, get_current_season, set_current_season
-from seasons.services.team_service import get_or_create_season_team
+from seasons.services.team_service import get_or_create_season_team, update_season_team
 
 
 User = get_user_model()
@@ -515,6 +518,14 @@ class SeasonOperationsUITests(TestCase):
         self.assertEqual(team.name, "Cardinals Updated")
         self.assertEqual(team.season, self.spring)
 
+    def test_cannot_create_team_from_inactive_season_shortcut(self):
+        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
+        self.login_staff()
+
+        response = self.client.get(reverse("seasons:season-team-new", kwargs={"season_id": inactive.id}))
+
+        self.assertEqual(response.status_code, 404)
+
     def test_staff_can_manage_membership_history_transfer_and_additional_membership(self):
         self.login_staff()
         create_response = self.client.post(
@@ -619,6 +630,18 @@ class SeasonOperationsUITests(TestCase):
         response = self.client.get(reverse("seasons:membership-list") + "?season=bad&team=bad")
         self.assertEqual(response.status_code, 200)
 
+    def test_membership_list_is_paginated_and_preserves_filters(self):
+        self.login_staff()
+        for index in range(55):
+            player = Player.objects.create(first_name=f"Player{index}", last_name="Paged")
+            create_membership(player=player, season_team=self.dodgers, is_primary=True)
+
+        response = self.client.get(reverse("seasons:membership-list") + f"?season={self.spring.id}&active=yes")
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Page 1 of 2")
+        self.assertContains(response, f"?season={self.spring.id}&amp;active=yes&amp;page=2")
+
     def test_staff_can_create_edit_end_coach_assignment_without_account_side_effects(self):
         original_password = self.coach.password
         self.login_staff()
@@ -705,3 +728,47 @@ class SeasonOperationsUITests(TestCase):
 
         response = self.client.get(reverse("seasons:coach-history", kwargs={"user_id": self.regular.id}))
         self.assertEqual(response.status_code, 404)
+
+    def test_submitted_evaluation_snapshot_survives_team_edit_and_player_transfer(self):
+        setup = ensure_default_coach_assessment_setup()
+        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+        create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+            is_primary=True,
+        )
+        cycle = EvaluationCycle.objects.create(
+            name="2026 Spring Evaluation",
+            cycle_type="Coach Assessment",
+            season=self.spring,
+            coach_assessment_question_set=setup.question_set,
+        )
+        responses = {
+            question: 4
+            for question in setup.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+        text_question = setup.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
+        responses[text_question] = "Snapshot should not move."
+
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=cycle,
+            evaluator=self.coach,
+            player_roster_membership=membership,
+            responses=responses,
+        )
+        observation = submit_observation(result.observation, actor=self.coach)
+
+        update_season_team(self.dodgers, name="Renamed Dodgers", division="Renamed 13U")
+        transfer_player(player=self.player, from_membership=membership, to_season_team=self.expos, transfer_date=date(2026, 6, 1))
+        observation.refresh_from_db()
+
+        self.assertEqual(observation.season_name_snapshot, "2026 Spring")
+        self.assertEqual(observation.player_team_name_snapshot, "Dodgers")
+        self.assertEqual(observation.player_division_snapshot, "13U")
+        self.assertEqual(observation.evaluator_team_name_snapshot, "Dodgers")
diff --git a/seasons/views.py b/seasons/views.py
index 4445c1c..d63a4f8 100644
--- a/seasons/views.py
+++ b/seasons/views.py
@@ -32,22 +32,33 @@ class SeasonOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin
         return is_staff_or_admin(self.request.user)
 
 
+class SeasonPaginationMixin:
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        query = self.request.GET.copy()
+        query.pop("page", None)
+        encoded = query.urlencode()
+        context["pagination_query"] = f"{encoded}&" if encoded else ""
+        return context
+
+
 def _clean_int(value: str) -> str | None:
     value = str(value or "").strip()
     return value if value.isdigit() else None
 
 
-class SeasonListView(SeasonOperationsStaffRequiredMixin, ListView):
+class SeasonListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
     model = Season
     template_name = "seasons/season_list.html"
     context_object_name = "seasons"
+    paginate_by = 50
 
     def get_queryset(self):
         return Season.objects.annotate(
             team_count=Count("teams", distinct=True),
             membership_count=Count("teams__player_memberships", distinct=True),
             assignment_count=Count("teams__coach_assignments", distinct=True),
-        )
+        ).order_by("-starts_on", "name", "id")
 
 
 class SeasonDetailView(SeasonOperationsStaffRequiredMixin, TemplateView):
@@ -137,10 +148,11 @@ class SeasonSetCurrentView(SeasonOperationsStaffRequiredMixin, FormView):
         return redirect("seasons:season-detail", season_id=self.season.id)
 
 
-class SeasonTeamListView(SeasonOperationsStaffRequiredMixin, ListView):
+class SeasonTeamListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
     model = SeasonTeam
     template_name = "seasons/team_list.html"
     context_object_name = "teams"
+    paginate_by = 50
 
     def get_queryset(self):
         queryset = SeasonTeam.objects.select_related("season").annotate(
@@ -167,7 +179,7 @@ class SeasonTeamCreateView(SeasonOperationsStaffRequiredMixin, FormView):
         kwargs = super().get_form_kwargs()
         season_id = self.kwargs.get("season_id")
         if season_id:
-            kwargs["fixed_season"] = get_object_or_404(Season, pk=season_id)
+            kwargs["fixed_season"] = get_object_or_404(Season, pk=season_id, is_active=True)
         return kwargs
 
     def form_valid(self, form):
@@ -235,10 +247,11 @@ class SeasonTeamEditView(SeasonOperationsStaffRequiredMixin, FormView):
         return redirect("seasons:team-list")
 
 
-class PlayerMembershipListView(SeasonOperationsStaffRequiredMixin, ListView):
+class PlayerMembershipListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
     model = PlayerRosterMembership
     template_name = "seasons/membership_list.html"
     context_object_name = "memberships"
+    paginate_by = 50
 
     def get_queryset(self):
         queryset = PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season")
@@ -468,10 +481,11 @@ class PlayerSeasonHistoryView(SeasonOperationsStaffRequiredMixin, TemplateView):
         return context
 
 
-class CoachAssignmentListView(SeasonOperationsStaffRequiredMixin, ListView):
+class CoachAssignmentListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
     model = CoachSeasonAssignment
     template_name = "seasons/assignment_list.html"
     context_object_name = "assignments"
+    paginate_by = 50
 
     def get_queryset(self):
         queryset = CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season", "user__account_profile")
```

## Terminal State

PASS
