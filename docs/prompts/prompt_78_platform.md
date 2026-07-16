# Prompt 78 - Platform

## User Prompt

Implement Seasonal Participation V1 Phase 5 only: Season and Roster Operations UI.

Source prompt file:
`/Users/eugenelin/.codex/attachments/2276d209-6f5f-417a-aef6-676837dec54a/pasted-text.txt`

```text
Implement Seasonal Participation V1 Phase 5 only: Season and Roster Operations UI.

Use continuous loop engineering.

Continue until the Phase 5 scope is production-ready, fully reviewed, documented, tested, committed, pushed, and the working tree is clean.

Do not start Phase 6 or later work.

==================================================
Current State
=============

Seasonal Participation V1 Phases 1 through 4 are complete.

The repository now includes:

* permanent player identity;
* permanent account identity;
* `Season`;
* `SeasonTeam`;
* `PlayerRosterMembership`;
* `CoachSeasonAssignment`;
* transactional seasonal services;
* season-aware player import;
* season-aware coach import;
* season-aware evaluation context;
* immutable submitted evaluation snapshots;
* historical roster, coach-assignment, and evaluation context.

Phase 4 added season-aware evaluation context but deliberately deferred first-class season and roster-management pages.

==================================================
Phase 5 Objective
=================

Create a small, practical staff-facing operations interface for managing seasonal participation records.

Staff should be able to:

1. view seasons;
2. create and edit seasons;
3. safely set the current season;
4. view and manage season-specific teams;
5. view player roster memberships;
6. manually create or update player roster memberships;
7. resolve same-season player team changes that imports currently block;
8. view coach seasonal assignments;
9. manually create or update coach assignments;
10. activate, deactivate, or end memberships and assignments safely;
11. view seasonal history for a player;
12. view seasonal assignment history for a coach.

Do not implement dashboards, longitudinal analytics, exports, or stricter team-based permissions.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete Phase 5 implementation, review, documentation, or verification work remains.

PASS

All Phase 5 acceptance criteria are satisfied, verification passes, commits are pushed, and the working tree is clean.

BLOCKED

A necessary decision requires unresolved product direction, destructive migration, external infrastructure, or architecture expansion outside Phase 5.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied acceptance criterion.

Do not continue through speculative or cosmetic refactoring.

==================================================
Established Loop Workflow
=========================

Every loop must complete the full repository workflow.

Each loop must:

1. Reconcile the current committed repository state.
2. Read `AGENTS.md`, the seasonal plan, user manual, and relevant prompt archives.
3. Confirm the working tree is clean.
4. Inspect the complete seasonal domain and current staff navigation.
5. Identify concrete incomplete acceptance criteria or verified defects.
6. Create the next prompt archive before implementation according to `AGENTS.md`.
7. Implement only selected Phase 5 work.
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
20. Reassess every Phase 5 acceptance criterion.
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
* relevant account-management and Analytics documentation
* relevant prompt archives for Phases 1 through 4

Inspect:

* `seasons/models.py`
* `seasons/services/`
* `seasons/admin.py`
* `seasons/tests.py`
* `players/models.py`
* `players/views.py`
* `players/templates/`
* `players/services/`
* `accounts/models.py`
* `accounts/views.py`
* `accounts/templates/`
* `accounts/services/`
* current staff navigation and operations dashboards
* current permission mixins and service patterns
* existing pagination, filtering, form, and confirmation patterns.

==================================================
Product Boundary
================

Phase 5 is an operations interface.

It should help staff maintain the seasonal records that imports and evaluations depend on.

It should not become:

* a new analytics dashboard;
* a scheduling system;
* a registration system;
* a full team-management product;
* an authorization redesign;
* a mass-editing framework.

Prefer simple server-rendered Django pages.

No JavaScript framework is needed.

==================================================
Permissions
===========

Use existing staff/admin authorization patterns.

Recommended rule:

* only users currently authorized to manage accounts or Analytics operations may access seasonal operations;
* ordinary coaches and players may not access these pages;
* seasonal coach assignments do not grant staff access;
* do not introduce team-scoped administration.

Use a focused permission helper or mixin rather than duplicating checks in every view.

Do not use `is_superuser` alone if current platform permissions already provide a better staff-management rule.

==================================================
Navigation
==========

Add a clear staff-facing entry point such as:

```text
Season Operations
```

Place it in the existing staff/operations navigation where appropriate.

Do not expose it to unauthorized users.

Suggested URL namespace:

```text
/seasons/
```

Possible routes:

```text
/seasons/
/seasons/new/
/seasons/<id>/
/seasons/<id>/edit/
/seasons/<id>/set-current/
/seasons/<id>/teams/
/seasons/<id>/teams/new/
/seasons/teams/<id>/
/seasons/teams/<id>/edit/
/seasons/memberships/
/seasons/memberships/new/
/seasons/memberships/<id>/edit/
/seasons/assignments/
/seasons/assignments/new/
/seasons/assignments/<id>/edit/
```

Use repository-consistent names and route patterns.

==================================================
Season List
===========

Create a season list page.

Display:

* name;
* key;
* current status;
* active status;
* start date;
* end date;
* number of teams;
* number of player memberships;
* number of coach assignments;
* available actions.

Filters:

* active/inactive;
* current;
* search by name/key.

Ordering:

* current first;
* newest date first where practical.

Actions:

* view;
* edit;
* set current;
* activate/deactivate where safe.

Do not allow destructive deletion through the normal UI.

==================================================
Create And Edit Season
======================

Provide forms for:

* key;
* name;
* starts_on;
* ends_on;
* is_active.

Do not allow ordinary form editing of `is_current`.

Setting the current season must use a separate explicit action backed by `season_service.set_current_season(...)` or equivalent.

Validation:

* nonblank normalized key;
* unique key;
* nonblank name;
* valid date range.

If a season is referenced:

* deactivation is allowed where domain rules permit;
* deletion is not exposed.

==================================================
Set Current Season
==================

Provide an explicit confirmation page.

The action must:

* use the transactional current-season service;
* atomically clear the previous current season;
* make the selected season current;
* preserve all historical data.

Display:

* currently selected current season;
* season being promoted;
* consequences for import defaults and evaluation-cycle defaults.

Do not silently activate an inactive season unless the service contract explicitly supports and tests that behavior.

Preferred rule:

* inactive season cannot be made current;
* staff must activate it first.

==================================================
Season Detail
=============

Create a season detail page.

Display:

* season metadata;
* current/active state;
* team count;
* roster membership count;
* coach assignment count;
* evaluation cycle count;
* links to:

  * teams;
  * player memberships;
  * coach assignments;
  * evaluation cycles where existing pages support them.

Do not create new Analytics dashboards.

==================================================
Season Team Management
======================

Provide list/create/edit pages for `SeasonTeam`.

Required fields:

* season;
* name;
* division;
* optional external source;
* optional external identifier;
* is_active.

Use existing `team_service` for:

* normalization;
* safe creation/reuse;
* conflict detection.

Do not duplicate normalization logic in forms or views.

Team list should show:

* season;
* division;
* name;
* active status;
* player count;
* coach count;
* source identifier;
* actions.

Filters:

* season;
* division;
* active state;
* search by team name.

Do not expose destructive deletion.

If the team has memberships, assignments, or observations:

* allow safe display-name correction through the service;
* preserve submitted evaluation snapshots;
* do not rewrite historical snapshot fields.

==================================================
Player Membership List
======================

Create a staff-facing membership list.

Display:

* player;
* season;
* division;
* team;
* roster status;
* primary state;
* active state;
* start/end dates;
* jersey number;
* import/source context;
* actions.

Filters:

* season;
* division;
* team;
* status;
* active;
* primary;
* player search.

Use efficient `select_related` and pagination.

Avoid N+1 queries.

==================================================
Create Player Membership
========================

Provide a form for:

* player;
* season team;
* roster status;
* jersey number;
* starts_on;
* ends_on;
* is_active;
* is_primary;
* optional source/source identifier;
* optional notes/metadata only if consistent with repository conventions.

Use `membership_service.create_membership(...)`.

Do not directly save the model from the view.

Validation:

* date range;
* inactive membership cannot be primary;
* one active primary membership per player/season;
* duplicate same player/team membership behavior follows current service contract;
* membership team determines season.

After creating an active primary membership:

* synchronize `Player.team_name` and `Player.division` through the explicit compatibility helper.

==================================================
Edit Player Membership
======================

Provide an edit form using the membership service.

Allow:

* roster status update;
* jersey number;
* dates;
* active state;
* primary state;
* safe team change only through an explicit operation.

Do not permit arbitrary direct replacement of `season_team` on an existing historical membership if that would rewrite history.

Preferred rule:

* normal edit may update nonidentity roster fields;
* moving to another team should use a dedicated transfer or correction action.

==================================================
Resolve Team Change / Transfer
==============================

Imports currently block same-season active-primary team changes for manual review.

Create a simple staff workflow to resolve this.

The workflow should support:

## Transfer

* end or deactivate the old membership;
* set old membership status to Transferred where appropriate;
* create a new membership for the new team;
* make the new active membership primary;
* preserve the old membership;
* sync compatibility fields.

## Additional Membership

* keep current primary;
* create a non-primary membership for the additional team;
* preserve compatibility fields.

## Correction

Use a conservative contract.

Preferred behavior:

* if no submitted observations reference the old membership, allow a service-driven correction;
* if observations reference the old membership, do not rewrite the historical membership;
* use transfer/new membership instead.

If implementing a general correction workflow is too large, implement Transfer and Additional Membership only and document correction through admin/service review.

Do not silently guess.

==================================================
Deactivate Or End Membership
============================

Provide an explicit confirmation action.

Allow:

* deactivate membership;
* set end date;
* update status.

If deactivating the active primary membership:

* require choosing or creating another primary membership;
* or allow no primary only when staff explicitly confirms and compatibility fields are handled safely.

Do not leave two active primaries.

Do not erase history.

==================================================
Player Season History
=====================

Add a season-history section to an existing player detail page or create a simple staff-only seasonal history page.

Display chronological memberships:

* season;
* team;
* division;
* status;
* primary;
* active;
* dates;
* source/import batch where available.

Show links to relevant submitted evaluations only if existing review permissions and routes make this straightforward.

Do not build a longitudinal analytics report.

==================================================
Coach Assignment List
=====================

Create a staff-facing coach assignment list.

Display:

* coach;
* account email;
* season;
* division;
* team;
* assignment role;
* primary;
* active;
* dates;
* source;
* actions.

Filters:

* season;
* team;
* division;
* role;
* active;
* primary;
* coach search.

Use efficient query loading and pagination.

==================================================
Create Coach Assignment
=======================

Provide a form for:

* coach user;
* season team;
* assignment role;
* active state;
* primary state;
* start/end dates;
* source/source identifier.

Only allow users whose account profile is already Coach.

Do not silently convert a non-coach account.

Use `coach_assignment_service.create_assignment(...)`.

Creating an assignment must not:

* reset password;
* activate the login account;
* change account role;
* grant staff;
* grant superuser;
* create player links.

==================================================
Edit Coach Assignment
=====================

Allow safe updates through the assignment service.

Support:

* role;
* active state;
* primary state;
* dates;
* source fields.

Do not rewrite assignment team/season history through ordinary edit if that would change historical meaning.

Use a dedicated new assignment for another team or season.

==================================================
Deactivate Or End Coach Assignment
==================================

Provide explicit confirmation.

Allow:

* deactivate;
* set end date;
* preserve history.

If ending the primary assignment:

* another assignment may become primary only through an explicit service action;
* do not silently choose among multiple assignments unless the current service already defines a deterministic safe rule.

Do not alter the user account’s activation state.

==================================================
Coach Season History
====================

Add a staff-only season-history section to the coach account detail page or a dedicated page.

Display:

* season;
* team;
* division;
* role;
* active;
* primary;
* dates;
* source.

Do not display password data.

Do not expose unrelated account-management actions beyond existing permissions.

==================================================
Forms And Services
==================

Views must remain thin.

Forms should validate input shape.

Services must own:

* current-season transitions;
* team normalization;
* membership creation/update/transfer;
* compatibility synchronization;
* coach assignment creation/update/deactivation;
* invariant enforcement.

Do not use signals.

Do not duplicate transaction logic in views.

Use `transaction.atomic` and existing locking behavior through services.

==================================================
Request Security
================

Do not trust hidden fields for:

* season;
* player;
* coach;
* season team;
* primary state;
* transfer source membership;
* transfer destination team.

Every object relationship must be server-validated.

Prevent:

* assigning a player membership to a mismatched season;
* modifying another object through ID tampering;
* assigning a non-coach account;
* creating multiple active primary memberships;
* creating multiple active primary coach assignments where prohibited;
* changing submitted evaluation snapshots through roster-management pages.

Use POST for state-changing actions.

Include CSRF protection and confirmation pages.

==================================================
Admin Relationship
==================

Django admin already exists for seasonal models.

The Phase 5 UI should become the safer normal operations path.

Do not remove admin registrations.

Document:

* use Season Operations for normal work;
* use Django admin only for exceptional diagnosis or correction by technical administrators.

Do not attempt to reproduce every admin field in the new UI.

==================================================
Migration
=========

Prefer no schema migration.

A migration is allowed only if repository inspection identifies a narrowly necessary field for safe operations.

Do not:

* create default seasons;
* backfill memberships;
* backfill assignments;
* alter evaluation snapshots;
* remove compatibility fields;
* introduce destructive changes.

If no migration is needed, do not create one.

==================================================
Documentation
=============

Update:

* `docs/USER_MANUAL.md`
* `docs/ARCHITECTURE.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* relevant account and player documentation.

Document:

* where Season Operations is located;
* who can access it;
* how to create seasons and teams;
* how to set the current season;
* how to manage player memberships;
* how to resolve a transfer;
* how to create additional memberships;
* how to manage coach assignments;
* what remains historical;
* how compatibility fields behave;
* current limitations;
* Phase 5 completion;
* next phase.

Do not describe dashboards or longitudinal reports as implemented.

==================================================
Phase 5 Non-Goals
=================

Do not implement:

* new analytics dashboards;
* charts;
* longitudinal comparisons;
* season-over-season reports;
* PDF reports;
* exports;
* APIs;
* notifications;
* bulk roster editing;
* drag-and-drop rosters;
* scheduling;
* registration;
* strict team-scoped permissions;
* peer team restrictions;
* parent access;
* Platform V2 summaries;
* permanent Team model;
* removal of `Player.team_name`;
* removal of `Player.division`;
* snapshot backfills;
* PDP migration.

==================================================
Required Test Coverage
======================

## Permissions

* authorized staff can access;
* ordinary coach denied;
* ordinary player denied;
* unauthenticated user redirected;
* seasonal assignment alone does not grant access.

## Season List And Forms

* list displays counts and states;
* create valid season;
* invalid date range rejected;
* duplicate key rejected;
* edit valid season;
* current state not directly editable;
* inactive season cannot be made current;
* set-current action is atomic;
* previous current season cleared.

## Season Teams

* list/filter/search;
* create through service;
* normalized duplicate reused or rejected safely;
* same team name in another season allowed;
* edit display values safely;
* no historical snapshots rewritten;
* unauthorized access denied.

## Player Memberships

* list/filter/search;
* create active primary membership;
* create non-primary additional membership;
* duplicate active primary blocked;
* inactive primary rejected;
* compatibility fields synchronized;
* edit nonhistorical roster fields;
* deactivation preserves history;
* source/import provenance displayed where available.

## Transfer Workflow

* old membership preserved;
* old membership ended/deactivated;
* transferred status applied where appropriate;
* new membership created;
* new membership primary;
* compatibility fields updated;
* existing submitted observation snapshots unchanged;
* additional membership option preserves old primary;
* tampered player/team IDs rejected.

## Player History

* memberships ordered by season/date;
* historical memberships visible;
* no duplicate rows;
* unauthorized users denied.

## Coach Assignments

* list/filter/search;
* create for coach account;
* non-coach account rejected;
* duplicate active user/team/role prevented;
* multiple teams allowed;
* multiple roles allowed;
* first primary behavior follows service;
* edit role/dates safely;
* deactivate preserves history;
* account password unchanged;
* account activation unchanged;
* profile role unchanged;
* no staff/superuser changes.

## Coach History

* seasonal assignments displayed;
* prior seasons preserved;
* password data absent;
* unauthorized users denied.

## Security

* POST required for state changes;
* CSRF protection remains;
* hidden-ID tampering rejected;
* cross-season object combinations rejected;
* invalid primary-state manipulation rejected;
* submitted evaluation snapshots cannot be edited.

## Regression

* player import remains season-aware;
* coach import remains season-aware;
* evaluations remain season-aware;
* account operations unchanged;
* current tests remain passing;
* no compatibility fields removed.

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
Self-Review Every Loop
======================

Review each diff as a senior Django engineer.

Check:

* permission boundaries;
* thin views;
* service-layer ownership;
* transaction and locking behavior;
* primary-membership invariants;
* primary-assignment invariants;
* transfer history preservation;
* compatibility-field synchronization;
* password and privilege side effects;
* submitted snapshot immutability;
* ID tampering;
* cross-season mismatches;
* accidental destructive edits;
* pagination and N+1 queries;
* stale docs;
* accidental Phase 6+ work.

Fix every verified issue before committing.

==================================================
Phase 5 Acceptance Criteria
===========================

Do not declare PASS until all criteria are satisfied.

A. Access

* authorized staff can access Season Operations;
* unauthorized users cannot;
* seasonal assignments do not grant staff access.

B. Seasons

* staff can list, create, and edit seasons;
* current season is changed through an explicit atomic action;
* inactive season cannot become current;
* no destructive deletion exposed.

C. Teams

* staff can list, create, and edit season teams;
* normalization and uniqueness use services;
* historical evaluation snapshots remain unchanged.

D. Player Memberships

* staff can list, create, and edit memberships safely;
* primary rules enforced;
* compatibility fields synchronized;
* history preserved.

E. Transfers

* blocked import team changes can be resolved;
* transfer creates new membership;
* old membership preserved;
* additional-membership option supported;
* no silent history rewrite.

F. Player History

* staff can view season-by-season roster history.

G. Coach Assignments

* staff can list, create, and edit assignments;
* permanent account identity reused;
* no password, activation, role, staff, or superuser side effects;
* history preserved.

H. Coach History

* staff can view season-by-season assignment history.

I. Security

* state-changing actions use POST and confirmation;
* ID manipulation rejected;
* cross-season mismatches rejected;
* submitted snapshots remain immutable.

J. Migration

* no migration unless narrowly justified;
* no fabricated or destructive data changes.

K. Tests

* focused and full suites pass;
* transfer and privilege regressions covered;
* import and evaluation regressions covered.

L. Documentation

* user manual explains the new operations workflow;
* Phase 5 marked complete only after PASS;
* future reporting remains documented as deferred;
* next phase identified clearly.

M. Git

* implementation commit exists;
* prompt archive commit exists;
* both pushed;
* working tree clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally:

1. add Season Operations permission/mixin and navigation;
2. add season list/detail/create/edit/set-current pages;
3. add season-team pages;
4. add player-membership pages;
5. add transfer/additional-membership workflow;
6. add player season history;
7. add coach-assignment pages;
8. add coach season history;
9. add comprehensive tests;
10. update documentation;
11. run full verification;
12. commit, archive, push, and reassess.

If material defects remain, continue into additional loops.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* satisfies an unsatisfied acceptance criterion;
* fixes a verified authorization or data-integrity defect;
* preserves historical roster or assignment context;
* strengthens transfer safety;
* prevents account/password/privilege side effects;
* adds missing regression proof;
* corrects material documentation drift.

Formatting-only work does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* administrator creating a new season;
* registrar creating teams;
* registrar correcting a roster;
* registrar transferring a player;
* coach assigned to multiple teams;
* staff reviewing player history;
* staff reviewing coach history;
* security reviewer tampering with IDs;
* data architect checking historical preservation;
* release engineer reviewing migration safety.

Confirm:

* operations can be completed without Django admin;
* imports and evaluations still work;
* history is preserved;
* no dashboards or reports were introduced;
* no compatibility fields were removed;
* no Phase 6+ work was started.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before implementation;
2. commit implementation, tests, migrations if any, and documentation;
3. update the prompt archive with:

   * implementation commit hash;
   * files changed;
   * migration summary;
   * permission behavior;
   * season/team workflow;
   * membership and transfer behavior;
   * coach assignment behavior;
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
Implement season and roster operations
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
* permission behavior;
* navigation and routes;
* season-management behavior;
* current-season behavior;
* season-team behavior;
* player-membership behavior;
* transfer/additional-membership behavior;
* compatibility-field behavior;
* player-history behavior;
* coach-assignment behavior;
* password/privilege protections;
* coach-history behavior;
* security protections;
* tests added;
* focused verification;
* full verification;
* documentation updates;
* deferred Phase 6+ work;
* commits;
* push results;
* confirmation that the working tree is clean.
```

## Implementation Commit

16f0de83d35086df6e9516538d78410fcf328ad5

Implement season and roster operations


## Files Changed

```text
16f0de8 Implement season and roster operations
 .../templates/accounts/operations_dashboard.html   |   1 +
 docs/ARCHITECTURE.md                               |   7 +-
 docs/USER_MANUAL.md                                |  87 ++-
 docs/seasons/README.md                             |  19 +-
 .../engineering/seasonal_participation_v1.md       |  32 +-
 pdp/templates/pdp/base.html                        |   3 +
 seasons/forms.py                                   | 158 +++++
 seasons/services/season_service.py                 |   2 +
 seasons/templates/seasons/assignment_end.html      |  16 +
 seasons/templates/seasons/assignment_form.html     |  19 +
 seasons/templates/seasons/assignment_list.html     |  68 +++
 seasons/templates/seasons/base.html                |  19 +
 seasons/templates/seasons/coach_history.html       |  33 ++
 seasons/templates/seasons/membership_end.html      |  16 +
 seasons/templates/seasons/membership_form.html     |  20 +
 seasons/templates/seasons/membership_list.html     |  68 +++
 seasons/templates/seasons/membership_transfer.html |  17 +
 seasons/templates/seasons/player_history.html      |  42 ++
 seasons/templates/seasons/season_detail.html       |  49 ++
 seasons/templates/seasons/season_form.html         |  16 +
 seasons/templates/seasons/season_list.html         |  44 ++
 seasons/templates/seasons/season_set_current.html  |  16 +
 seasons/templates/seasons/team_form.html           |  16 +
 seasons/templates/seasons/team_list.html           |  47 ++
 seasons/tests.py                                   | 309 ++++++++++
 seasons/urls.py                                    |  49 ++
 seasons/views.py                                   | 639 +++++++++++++++++++++
 vancouverminor/urls.py                             |   1 +
 28 files changed, 1788 insertions(+), 25 deletions(-)
```

## Migration Summary

No migrations were added. `makemigrations seasons --check`, `makemigrations players --check`, `makemigrations accounts --check`, and `makemigrations analytics --check` reported no changes.

## Permission Behavior

Season Operations routes are staff-only and require Django `User.is_staff` or `User.is_superuser`. Seasonal player memberships and coach assignments do not grant account access, Django staff, Django superuser, or password privileges.

## Season And Team Workflow

Staff can list, create, edit, and explicitly set current seasons. Staff can list, create, and edit season-specific teams. The current-season operation is POST-confirmed.

## Membership And Transfer Behavior

Staff can create, edit, end, transfer, and add additional player roster memberships. Transfers preserve prior membership history and create a new primary membership. Additional memberships create non-primary guest memberships. Cross-season destination tampering is rejected by form validation.

## Coach Assignment Behavior

Staff can list, create, edit, end, and review history for coach season assignments. Assignment changes preserve account identity and do not reset passwords, activate/deactivate users, change platform roles, or grant Django staff/superuser flags.

## Issues Found And Fixes Applied

- Added Python 3.9-compatible postponed annotations for new view typing.
- Aligned `update_season()` with `deactivate_season()` so a current season cannot remain current after being made inactive through the edit flow.
- Converted end-date workflow validation failures into form errors.
- Added duplicate active destination-team protection for transfer/additional membership workflows.

## Verification

Focused verification passed:

```text
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
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

Result: PASS. Full suite ran 455 tests successfully.

## Remaining Criteria

All Phase 5 acceptance criteria are satisfied. Phase 6 production review and freeze remains deferred.

## Commit Diff

```diff
diff --git a/accounts/templates/accounts/operations_dashboard.html b/accounts/templates/accounts/operations_dashboard.html
index 76d6ba2..e0daa34 100644
--- a/accounts/templates/accounts/operations_dashboard.html
+++ b/accounts/templates/accounts/operations_dashboard.html
@@ -11,6 +11,7 @@
             <a class="button button--primary" href="{% url 'accounts:account-create' %}">Create Account</a>
             <a class="button button--ghost" href="{% url 'accounts:player-account-create' %}">Create Player Account</a>
             <a class="button button--ghost" href="{% url 'accounts:coach-import-list' %}">Import Coaches</a>
+            <a class="button button--ghost" href="{% url 'seasons:season-list' %}">Season Operations</a>
         </div>
     </article>
 
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 0d352fd..803ecaa 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -202,7 +202,7 @@ What it must not own:
 
 Current status:
 
-Seasonal Participation V1 Phase 1 foundation, Phase 2 season-aware player import, Phase 3 season-aware coach import, and Phase 4 season-aware evaluation context are implemented. The schema, services, admin registration, tests, player import integration, coach import integration, and evaluation context integration exist. Player imports now create or update season teams and player roster memberships. Coach imports now create or update season teams and coach season assignments while preserving permanent coach accounts. New season-linked evaluations preserve season, player roster membership, player team/division snapshots, and coach assignment snapshots where applicable.
+Seasonal Participation V1 Phase 1 foundation, Phase 2 season-aware player import, Phase 3 season-aware coach import, Phase 4 season-aware evaluation context, and Phase 5 season/roster operations UI are implemented. The schema, services, admin registration, tests, player import integration, coach import integration, evaluation context integration, and staff-facing season operations pages exist. Staff can manage seasons, season teams, player roster memberships, transfers/additional memberships, player season history, coach assignments, and coach season history. Player imports now create or update season teams and player roster memberships. Coach imports now create or update season teams and coach season assignments while preserving permanent coach accounts. New season-linked evaluations preserve season, player roster membership, player team/division snapshots, and coach assignment snapshots where applicable.
 
 Documentation:
 
@@ -327,7 +327,7 @@ Dependency guidance:
 | Players | V1 | Complete |
 | Analytics | V1 | Complete |
 | Account Management | V1 | Complete / Frozen |
-| Seasons | V1 Phase 3 | Coach import integration complete |
+| Seasons | V1 Phase 5 | Season and roster operations UI complete |
 | Drafts | Active | Active development |
 | PDP | Legacy | Transitionary |
 | LeagueHub | Planned | Planned |
@@ -345,6 +345,7 @@ The platform currently has:
 - season-aware roster participation foundation
 - season-aware player and coach import integration
 - season-aware evaluation context and submitted-evaluation snapshots
+- staff-facing season and roster operations UI
 - account provisioning from player imports
 - forced password-change account flow
 - staff-only Analytics command center and reporting tables
@@ -361,7 +362,7 @@ Likely future areas:
 
 - Account Management V2
 - Analytics V2
-- Seasonal Participation Phase 5
+- Seasonal Participation Phase 6 production review and freeze
 - Drafts expansion
 - LeagueHub
 - Video
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 310b4fb..a69ab6c 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -7,7 +7,7 @@ The platform helps Vancouver Community Baseball manage:
 - player records
 - account access
 - player and coach imports
-- season and roster foundations
+- season and roster operations
 - evaluations
 - player history
 - draft preparation
@@ -15,7 +15,7 @@ The platform helps Vancouver Community Baseball manage:
 
 This is a user manual, not a technical deployment guide. Deployment information lives in [docs/deployment/](deployment/README.md).
 
-Season-aware roster foundations now exist in the system. Player imports, coach imports, and evaluations are season-aware: staff choose an active season for imports, imported team/division information creates roster participation records or coach assignments, and submitted evaluations preserve the season/team/division context that existed when the evaluation was submitted.
+Season-aware roster operations now exist in the system. Staff can manage seasons, teams, player roster memberships, transfers, coach assignments, and season history without using Django admin. Player imports, coach imports, and evaluations are season-aware: staff choose an active season for imports, imported team/division information creates roster participation records or coach assignments, and submitted evaluations preserve the season/team/division context that existed when the evaluation was submitted.
 
 ## Start Here
 
@@ -78,8 +78,9 @@ Use this section when you are responsible for account access, operational setup,
 2. Review accounts requiring password change and users without player links.
 3. Create or update staff, coach, parent, guest evaluator, or player accounts.
 4. Import coach accounts when onboarding a roster.
-5. Confirm staff-only access is controlled by Django staff/superuser permissions.
-6. Use Analytics to confirm imports, evaluations, and review workflows are healthy.
+5. Open Season Operations to create seasons, teams, roster memberships, and coach assignments.
+6. Confirm staff-only access is controlled by Django staff/superuser permissions.
+7. Use Analytics to confirm imports, evaluations, and review workflows are healthy.
 
 ### Pages Normally Used
 
@@ -88,6 +89,7 @@ Use this section when you are responsible for account access, operational setup,
 - `/accounts/create/`
 - `/accounts/create/player/`
 - `/accounts/imports/coaches/`
+- `/seasons/`
 - `/analytics/`
 - `/admin/`
 
@@ -117,9 +119,10 @@ Start at:
 2. Review evaluation activity, import summaries, and completion status.
 3. Search for players from `/analytics/players/`.
 4. Import or update players from `/analytics/imports/`.
-5. Review submitted evaluations from `/analytics/observations/review/`.
-6. Compare players or review player profiles when preparing decisions.
-7. Use Account Operations if users need access help.
+5. Use `/seasons/` to review or correct season teams, roster memberships, transfers, and coach assignments.
+6. Review submitted evaluations from `/analytics/observations/review/`.
+7. Compare players or review player profiles when preparing decisions.
+8. Use Account Operations if users need access help.
 
 ### Pages Normally Used
 
@@ -129,6 +132,7 @@ Start at:
 - `/analytics/imports/`
 - `/analytics/observations/review/`
 - `/analytics/evaluation-review/`
+- `/seasons/`
 - `/accounts/`
 - `/drafts/`
 
@@ -355,6 +359,75 @@ Supported relationships:
 
 A parent or guardian may link to multiple players. A player may have multiple parents or guardians. Normal unlinking deactivates the link instead of deleting it so history is preserved.
 
+## Season Operations
+
+### Purpose
+
+Season Operations lets staff manage season-aware roster context without using Django admin.
+
+### Who Uses It
+
+Staff and administrators with Django staff/superuser access.
+
+Seasonal assignments do not grant access by themselves. A coach assignment records baseball context for a season and team; it does not make the user a Django staff member or superuser.
+
+### Typical Workflow
+
+1. Open `/seasons/`.
+2. Create or edit the season.
+3. Set the current season explicitly when the organization is ready.
+4. Create season-specific teams.
+5. Create or correct player roster memberships.
+6. Use transfer/additional-membership actions when a player changes teams or plays on multiple teams.
+7. Review player season history.
+8. Create or correct coach season assignments.
+9. Review coach season history.
+
+### Related Pages
+
+- `/seasons/`
+- `/seasons/new/`
+- `/seasons/<season_id>/`
+- `/seasons/teams/`
+- `/seasons/memberships/`
+- `/seasons/players/<player_id>/history/`
+- `/seasons/coach-assignments/`
+- `/seasons/coaches/<user_id>/history/`
+
+### Seasons And Current Season
+
+Staff can create and edit seasons. One season can be marked current at a time. Setting the current season is an explicit confirmation action so staff do not accidentally change import and evaluation defaults.
+
+Inactive seasons remain visible for history. Normal operations preserve history instead of deleting records.
+
+### Teams
+
+Teams are scoped to a season. The same team name can exist in different seasons without being treated as the same roster record.
+
+### Player Memberships
+
+Player memberships record a player's roster stint on a season team. Staff can:
+
+- create memberships;
+- edit status, dates, jersey number, source, and primary membership;
+- end memberships without deleting history;
+- transfer a player to another team in the same season;
+- add an additional non-primary membership for multi-team participation;
+- view the player's season-by-season history.
+
+A player may have multiple memberships in a season, but only one active primary membership per season. Transfers preserve the prior membership as historical context.
+
+### Coach Assignments
+
+Coach assignments record a coach user's season-specific team assignment. Staff can:
+
+- create assignments;
+- edit assignment role, dates, primary flag, source, and active state;
+- end assignments without deleting history;
+- view the coach's season-by-season assignment history.
+
+Coach assignment changes do not reset passwords, change account activation, change platform role, or grant Django staff/superuser access.
+
 ## Evaluations
 
 ### Purpose
diff --git a/docs/seasons/README.md b/docs/seasons/README.md
index ee3fd7b..f925efb 100644
--- a/docs/seasons/README.md
+++ b/docs/seasons/README.md
@@ -27,6 +27,8 @@ Phase 3 - Season-Aware Coach Import is implemented.
 
 Phase 4 - Season-Aware Evaluation Context is implemented.
 
+Phase 5 - Season And Roster Operations UI is implemented.
+
 Verified production state on July 15, 2026:
 
 ```text
@@ -80,13 +82,24 @@ Implemented evaluation context:
 - review pages display submitted snapshots instead of live player team fields;
 - legacy observations without season context remain readable as `Legacy / No Season`.
 
+Implemented season operations UI:
+
+- staff can list, create, edit, and explicitly set current seasons;
+- staff can list, create, and edit season teams;
+- staff can list, create, edit, end, transfer, and add additional player roster memberships;
+- staff can view player season history;
+- staff can list, create, edit, and end coach season assignments;
+- staff can view coach season history;
+- seasonal assignment changes do not reset passwords, change activation, change platform roles, or grant Django staff/superuser access;
+- state-changing operations use staff-only POST workflows and preserve historical records.
+
 Current limitations:
 
-- there are no first-class roster-management pages yet.
 - stricter team-scoped coach permissions and peer team restrictions are deferred.
+- dashboards, charts, exports, reports, and strict team-scoped permissions remain deferred.
 
 Next phase:
 
-- Phase 5 - Read Models And UI.
+- Phase 6 - Production Review And Freeze.
 
-Seasonal evaluation context was added in Phase 4 without adding dashboards, reports, roster-management pages, or stricter team-based authorization.
+Seasonal operations UI was added in Phase 5 without adding dashboards, reports, exports, APIs, bulk editing, or stricter team-based authorization.
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
index 42b5090..c1abbb5 100644
--- a/docs/seasons/implementation/engineering/seasonal_participation_v1.md
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -1,6 +1,6 @@
 # Seasonal Participation V1 Engineering Plan
 
-Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 season-aware coach import complete. Phase 4 season-aware evaluation context complete. Phase 5 is the next implementation phase.
+Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 season-aware coach import complete. Phase 4 season-aware evaluation context complete. Phase 5 season and roster operations UI complete. Phase 6 production review and freeze is the next implementation phase.
 
 Created: 2026-07-15.
 
@@ -709,13 +709,21 @@ Status: complete.
 - Update player-facing, coach-facing, and staff review read models to use snapshots.
 - Preserve submitted snapshots across later roster changes.
 
-### Phase 5 - Read Models And UI
+### Phase 5 - Season And Roster Operations UI
 
-- Add staff roster history views if needed.
-- Update player profile/timeline to show season history.
-- Update player search, command center, coach review, and metrics filters to use season-aware services.
-- Add safe empty states for no current roster.
-- Keep templates presentation-only.
+Status: complete.
+
+- Added staff-only season operations routes under `/seasons/`.
+- Added season list, detail, create, edit, and explicit set-current pages.
+- Added season-team list, create, and edit pages.
+- Added player roster membership list, create, edit, end, transfer, additional membership, and player history pages.
+- Added coach assignment list, create, edit, end, and coach history pages.
+- Kept state-changing operations behind POST/CSRF workflows.
+- Preserved player roster and coach assignment history through inactive/end-dated records rather than deletion.
+- Preserved existing evaluation snapshot behavior; season operations do not rewrite submitted evaluations.
+- Kept templates presentation-only and business rules in existing `seasons` services.
+- Added tests for permissions, season management, team management, memberships, transfer/additional membership behavior, cross-season tampering, player history, coach assignments, coach history, and privilege/password non-effects.
+- Did not add dashboards, charts, reports, exports, APIs, bulk editing, strict team-scoped authorization, new models, or migrations.
 
 ### Phase 6 - Production Review And Freeze
 
@@ -786,7 +794,8 @@ Deployment should be staged:
 4. Deploy player import changes after foundation is stable.
 5. Deploy coach assignment changes after player seasonal model is proven.
 6. Deploy evaluation context changes with snapshot behavior for new submissions.
-7. Update UI/read models after data is available.
+7. Deploy season and roster operations UI after import/evaluation context behavior is validated.
+8. Perform production review and freeze.
 
 Rollback considerations:
 
@@ -810,7 +819,6 @@ Rollback considerations:
 ## 26. Open Questions
 
 - What roster statuses are needed for V1?
-- Should staff be able to manually edit memberships and assignments in admin only, or through first-class UI?
 - How should imported transfer rows explicitly signal transfer versus concurrent membership?
 - Should player peer-evaluation scope eventually be limited to same season/team?
 - Should the exact one-current-season rule be database-enforced on SQLite, service-enforced, or both?
@@ -818,11 +826,11 @@ Rollback considerations:
 
 ## 27. Recommended Next Implementation Phase
 
-Start with Phase 5 - Read Models And UI.
+Start with Phase 6 - Production Review And Freeze.
 
-Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services. Phase 3 updated coach import to require a selected season, create or reuse `SeasonTeam`, and create/update `CoachSeasonAssignment` through `seasons` services while preserving existing coach passwords. Phase 4 added season-linked evaluation cycles, observation seasonal context fields, submitted-evaluation snapshots, season-aware player selectors, and snapshot-based review display.
+Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services. Phase 3 updated coach import to require a selected season, create or reuse `SeasonTeam`, and create/update `CoachSeasonAssignment` through `seasons` services while preserving existing coach passwords. Phase 4 added season-linked evaluation cycles, observation seasonal context fields, submitted-evaluation snapshots, season-aware player selectors, and snapshot-based review display. Phase 5 added staff-facing season and roster operations UI.
 
-Before implementing Phase 5, verify that Phase 4 production rollout completed successfully and that new submitted evaluations are recording expected season, roster membership, and snapshot values.
+Before implementing Phase 6, verify that Phase 5 production rollout completed successfully and staff can complete season, team, membership, transfer, and coach assignment workflows without Django admin.
 
 ## 28. Acceptance Criteria
 
diff --git a/pdp/templates/pdp/base.html b/pdp/templates/pdp/base.html
index 32c6b61..4b42fde 100644
--- a/pdp/templates/pdp/base.html
+++ b/pdp/templates/pdp/base.html
@@ -24,6 +24,9 @@
                     <a href="{% url 'pdp:home' %}">Home</a>
                     <a href="{% url 'pdp:coach-dashboard' %}">Coach</a>
                     <a href="{% url 'pdp:parent-dashboard' %}">Parent</a>
+                    {% if request.user.is_staff or request.user.is_superuser %}
+                        <a href="{% url 'seasons:season-list' %}">Seasons</a>
+                    {% endif %}
                     <a href="{% url 'pdp:import-workbench' %}">Imports</a>
                     <a href="{% url 'pdp:drill-library' %}">Drills</a>
                     <a href="{% url 'pdp:password-change' %}">Password</a>
diff --git a/seasons/forms.py b/seasons/forms.py
new file mode 100644
index 0000000..bcbd06d
--- /dev/null
+++ b/seasons/forms.py
@@ -0,0 +1,158 @@
+from django import forms
+from django.contrib.auth import get_user_model
+
+from accounts.models import AccountProfile, AccountRole
+from players.models import Player
+from seasons.models import (
+    CoachAssignmentRole,
+    CoachSeasonAssignment,
+    PlayerRosterMembership,
+    RosterStatus,
+    Season,
+    SeasonTeam,
+)
+
+
+class DateInput(forms.DateInput):
+    input_type = "date"
+
+
+class SeasonForm(forms.Form):
+    key = forms.SlugField(max_length=80)
+    name = forms.CharField(max_length=120)
+    starts_on = forms.DateField(required=False, widget=DateInput)
+    ends_on = forms.DateField(required=False, widget=DateInput)
+    is_active = forms.BooleanField(required=False, initial=True)
+
+
+class ConfirmCurrentSeasonForm(forms.Form):
+    confirm = forms.BooleanField(required=True, label="I understand this will make this the current season.")
+
+
+class SeasonTeamForm(forms.Form):
+    season = forms.ModelChoiceField(queryset=Season.objects.none())
+    name = forms.CharField(max_length=120)
+    division = forms.CharField(max_length=80)
+    external_source = forms.CharField(max_length=80, required=False)
+    external_identifier = forms.CharField(max_length=160, required=False)
+    is_active = forms.BooleanField(required=False, initial=True)
+
+    def __init__(self, *args, **kwargs):
+        fixed_season = kwargs.pop("fixed_season", None)
+        super().__init__(*args, **kwargs)
+        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by("-is_current", "-starts_on", "name")
+        if fixed_season:
+            self.fields["season"].initial = fixed_season
+            self.fields["season"].disabled = True
+
+
+class PlayerRosterMembershipForm(forms.Form):
+    player = forms.ModelChoiceField(queryset=Player.objects.none())
+    season_team = forms.ModelChoiceField(queryset=SeasonTeam.objects.none())
+    status = forms.ChoiceField(choices=RosterStatus.choices, initial=RosterStatus.ACTIVE)
+    jersey_number = forms.CharField(max_length=20, required=False)
+    is_primary = forms.BooleanField(required=False)
+    is_active = forms.BooleanField(required=False, initial=True)
+    starts_on = forms.DateField(required=False, widget=DateInput)
+    ends_on = forms.DateField(required=False, widget=DateInput)
+    source = forms.CharField(max_length=80, required=False)
+    source_identifier = forms.CharField(max_length=160, required=False)
+
+    def __init__(self, *args, **kwargs):
+        fixed_season = kwargs.pop("fixed_season", None)
+        editing = kwargs.pop("editing", False)
+        super().__init__(*args, **kwargs)
+        self.fields["player"].queryset = Player.objects.filter(is_active=True).order_by("last_name", "first_name", "id")
+        teams = SeasonTeam.objects.select_related("season").filter(is_active=True).order_by("-season__is_current", "season__name", "division", "name")
+        if fixed_season:
+            teams = teams.filter(season=fixed_season)
+        self.fields["season_team"].queryset = teams
+        if editing:
+            self.fields["player"].disabled = True
+            self.fields["season_team"].disabled = True
+
+
+class PlayerMembershipEndForm(forms.Form):
+    status = forms.ChoiceField(
+        choices=(
+            (RosterStatus.INACTIVE, "Inactive"),
+            (RosterStatus.REMOVED, "Removed"),
+            (RosterStatus.TRANSFERRED, "Transferred"),
+        ),
+        initial=RosterStatus.INACTIVE,
+    )
+    ends_on = forms.DateField(required=False, widget=DateInput)
+    confirm = forms.BooleanField(required=True, label="I understand this preserves history and ends the active membership.")
+
+
+class PlayerMembershipTransferForm(forms.Form):
+    ACTION_TRANSFER = "transfer"
+    ACTION_ADDITIONAL = "additional"
+    ACTION_CHOICES = (
+        (ACTION_TRANSFER, "Transfer and make destination primary"),
+        (ACTION_ADDITIONAL, "Add additional non-primary membership"),
+    )
+
+    action = forms.ChoiceField(choices=ACTION_CHOICES, initial=ACTION_TRANSFER)
+    season_team = forms.ModelChoiceField(queryset=SeasonTeam.objects.none(), label="Destination team")
+    transfer_date = forms.DateField(required=False, widget=DateInput)
+    jersey_number = forms.CharField(max_length=20, required=False)
+    source = forms.CharField(max_length=80, required=False)
+    source_identifier = forms.CharField(max_length=160, required=False)
+
+    def __init__(self, *args, source_membership: PlayerRosterMembership, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.source_membership = source_membership
+        self.fields["season_team"].queryset = (
+            SeasonTeam.objects.filter(season=source_membership.season, is_active=True)
+            .exclude(pk=source_membership.season_team_id)
+            .order_by("division", "name", "id")
+        )
+
+    def clean_season_team(self):
+        season_team = self.cleaned_data["season_team"]
+        duplicate = (
+            PlayerRosterMembership.objects.filter(
+                player=self.source_membership.player,
+                season_team=season_team,
+                is_active=True,
+            )
+            .exclude(pk=self.source_membership.pk)
+            .exists()
+        )
+        if duplicate:
+            raise forms.ValidationError("This player already has an active membership on the destination team.")
+        return season_team
+
+
+class CoachSeasonAssignmentForm(forms.Form):
+    user = forms.ModelChoiceField(queryset=get_user_model().objects.none(), label="Coach account")
+    season_team = forms.ModelChoiceField(queryset=SeasonTeam.objects.none())
+    assignment_role = forms.ChoiceField(choices=CoachAssignmentRole.choices, initial=CoachAssignmentRole.ASSISTANT_COACH)
+    is_primary = forms.BooleanField(required=False)
+    is_active = forms.BooleanField(required=False, initial=True)
+    starts_on = forms.DateField(required=False, widget=DateInput)
+    ends_on = forms.DateField(required=False, widget=DateInput)
+    source = forms.CharField(max_length=80, required=False)
+    source_identifier = forms.CharField(max_length=160, required=False)
+
+    def __init__(self, *args, **kwargs):
+        fixed_season = kwargs.pop("fixed_season", None)
+        editing = kwargs.pop("editing", False)
+        super().__init__(*args, **kwargs)
+        coach_user_ids = AccountProfile.objects.filter(role=AccountRole.COACH).values("user_id")
+        self.fields["user"].queryset = (
+            get_user_model().objects.filter(id__in=coach_user_ids).order_by("last_name", "first_name", "username", "id")
+        )
+        teams = SeasonTeam.objects.select_related("season").filter(is_active=True).order_by("-season__is_current", "season__name", "division", "name")
+        if fixed_season:
+            teams = teams.filter(season=fixed_season)
+        self.fields["season_team"].queryset = teams
+        if editing:
+            self.fields["user"].disabled = True
+            self.fields["season_team"].disabled = True
+
+
+class CoachAssignmentEndForm(forms.Form):
+    ends_on = forms.DateField(required=False, widget=DateInput)
+    confirm = forms.BooleanField(required=True, label="I understand this preserves history and ends the active assignment.")
diff --git a/seasons/services/season_service.py b/seasons/services/season_service.py
index 9bebc2e..8879918 100644
--- a/seasons/services/season_service.py
+++ b/seasons/services/season_service.py
@@ -54,6 +54,8 @@ def update_season(season: Season, **updates) -> Season:
         season.is_current = requested_current
     for field, value in updates.items():
         setattr(season, field, value)
+    if season.is_current and not season.is_active:
+        season.is_current = False
     season.save()
     return season
 
diff --git a/seasons/templates/seasons/assignment_end.html b/seasons/templates/seasons/assignment_end.html
new file mode 100644
index 0000000..71ea17e
--- /dev/null
+++ b/seasons/templates/seasons/assignment_end.html
@@ -0,0 +1,16 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}End Coach Assignment{% endblock %}
+{% block seasons_subtitle %}Ending an assignment preserves historical coach context.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <p>End {{ assignment.user.get_full_name|default:assignment.user.username }} on {{ assignment.season_team.division }} {{ assignment.season_team.name }}?</p>
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">End Assignment</button>
+        <a class="button button--ghost" href="{% url 'seasons:coach-history' assignment.user_id %}">Cancel</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/assignment_form.html b/seasons/templates/seasons/assignment_form.html
new file mode 100644
index 0000000..cf7095d
--- /dev/null
+++ b/seasons/templates/seasons/assignment_form.html
@@ -0,0 +1,19 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}{% if assignment %}Edit Coach Assignment{% else %}Create Coach Assignment{% endif %}{% endblock %}
+{% block seasons_subtitle %}Assignments are seasonal team context only; they do not change account permissions.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.non_field_errors }}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">{% if assignment %}Save Assignment{% else %}Create Assignment{% endif %}</button>
+        {% if assignment %}
+            <a class="button button--ghost" href="{% url 'seasons:coach-assignment-end' assignment.id %}">End Assignment</a>
+        {% endif %}
+        <a class="button button--ghost" href="{% url 'seasons:coach-assignment-list' %}">Cancel</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/assignment_list.html b/seasons/templates/seasons/assignment_list.html
new file mode 100644
index 0000000..16a063c
--- /dev/null
+++ b/seasons/templates/seasons/assignment_list.html
@@ -0,0 +1,68 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}Coach Assignments{% endblock %}
+{% block seasons_subtitle %}Season-specific coach-to-team assignments.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <form method="get" class="pdp-form">
+        <label>Search <input type="text" name="q" value="{{ filters.q }}" placeholder="Coach name or username"></label>
+        <label>
+            Season
+            <select name="season">
+                <option value="">All seasons</option>
+                {% for season in seasons %}
+                    <option value="{{ season.id }}"{% if filters.season == season.id|stringformat:"s" %} selected{% endif %}>{{ season.name }}</option>
+                {% endfor %}
+            </select>
+        </label>
+        <label>
+            Team
+            <select name="team">
+                <option value="">All teams</option>
+                {% for team in teams %}
+                    <option value="{{ team.id }}"{% if filters.team == team.id|stringformat:"s" %} selected{% endif %}>{{ team.season.name }} / {{ team.division }} {{ team.name }}</option>
+                {% endfor %}
+            </select>
+        </label>
+        <label>
+            Active
+            <select name="active">
+                <option value="">Any</option>
+                <option value="yes"{% if filters.active == "yes" %} selected{% endif %}>Active</option>
+                <option value="no"{% if filters.active == "no" %} selected{% endif %}>Inactive</option>
+            </select>
+        </label>
+        <button class="button button--primary" type="submit">Apply</button>
+        <a class="button button--ghost" href="{% url 'seasons:coach-assignment-list' %}">Reset</a>
+        <a class="button button--ghost" href="{% url 'seasons:coach-assignment-new' %}">Create Assignment</a>
+    </form>
+</article>
+<article class="pdp-card">
+    <div class="table-wrap">
+        <table class="pdp-table">
+            <thead>
+                <tr><th>Coach</th><th>Season</th><th>Team</th><th>Role</th><th>Primary</th><th>Active</th><th></th></tr>
+            </thead>
+            <tbody>
+                {% for assignment in assignments %}
+                    <tr>
+                        <td>{{ assignment.user.get_full_name|default:assignment.user.username }}</td>
+                        <td>{{ assignment.season.name }}</td>
+                        <td>{{ assignment.season_team.division }} {{ assignment.season_team.name }}</td>
+                        <td>{{ assignment.get_assignment_role_display }}</td>
+                        <td>{% if assignment.is_primary %}Yes{% else %}No{% endif %}</td>
+                        <td>{% if assignment.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td>
+                            <a class="button button--ghost" href="{% url 'seasons:coach-history' assignment.user_id %}">History</a>
+                            <a class="button button--ghost" href="{% url 'seasons:coach-assignment-edit' assignment.id %}">Edit</a>
+                        </td>
+                    </tr>
+                {% empty %}
+                    <tr><td colspan="7">No coach assignments match these filters.</td></tr>
+                {% endfor %}
+            </tbody>
+        </table>
+    </div>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/base.html b/seasons/templates/seasons/base.html
new file mode 100644
index 0000000..e0cccb0
--- /dev/null
+++ b/seasons/templates/seasons/base.html
@@ -0,0 +1,19 @@
+{% extends "pdp/base.html" %}
+
+{% block pdp_title %}{% block seasons_title %}Season Operations{% endblock %}{% endblock %}
+{% block pdp_subtitle %}{% block seasons_subtitle %}Manage seasons, roster memberships, and coach assignments.{% endblock %}{% endblock %}
+
+{% block pdp_content %}
+<section class="pdp-grid pdp-grid--single">
+    <article class="pdp-card">
+        <h2>Season Operations</h2>
+        <div class="pdp-actions">
+            <a class="button button--ghost" href="{% url 'seasons:season-list' %}">Seasons</a>
+            <a class="button button--ghost" href="{% url 'seasons:team-list' %}">Teams</a>
+            <a class="button button--ghost" href="{% url 'seasons:membership-list' %}">Player Memberships</a>
+            <a class="button button--ghost" href="{% url 'seasons:coach-assignment-list' %}">Coach Assignments</a>
+        </div>
+    </article>
+    {% block seasons_content %}{% endblock %}
+</section>
+{% endblock %}
diff --git a/seasons/templates/seasons/coach_history.html b/seasons/templates/seasons/coach_history.html
new file mode 100644
index 0000000..7193a68
--- /dev/null
+++ b/seasons/templates/seasons/coach_history.html
@@ -0,0 +1,33 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}Coach Season History{% endblock %}
+{% block seasons_subtitle %}Season-by-season assignment history for {{ coach.get_full_name|default:coach.username }}.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <h2>{{ coach.get_full_name|default:coach.username }}</h2>
+    <div class="table-wrap">
+        <table class="pdp-table">
+            <thead>
+                <tr><th>Season</th><th>Team</th><th>Role</th><th>Primary</th><th>Active</th><th>Dates</th><th>Source</th><th></th></tr>
+            </thead>
+            <tbody>
+                {% for assignment in assignments %}
+                    <tr>
+                        <td>{{ assignment.season.name }}</td>
+                        <td>{{ assignment.season_team.division }} {{ assignment.season_team.name }}</td>
+                        <td>{{ assignment.get_assignment_role_display }}</td>
+                        <td>{% if assignment.is_primary %}Yes{% else %}No{% endif %}</td>
+                        <td>{% if assignment.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td>{{ assignment.starts_on|default:"-" }} - {{ assignment.ends_on|default:"-" }}</td>
+                        <td>{{ assignment.source|default:"manual" }}</td>
+                        <td><a class="button button--ghost" href="{% url 'seasons:coach-assignment-edit' assignment.id %}">Edit</a></td>
+                    </tr>
+                {% empty %}
+                    <tr><td colspan="8">No season assignments are recorded for this coach.</td></tr>
+                {% endfor %}
+            </tbody>
+        </table>
+    </div>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/membership_end.html b/seasons/templates/seasons/membership_end.html
new file mode 100644
index 0000000..1b16111
--- /dev/null
+++ b/seasons/templates/seasons/membership_end.html
@@ -0,0 +1,16 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}End Player Membership{% endblock %}
+{% block seasons_subtitle %}Ending a membership preserves the historical record.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <p>End {{ membership.player.display_name }} on {{ membership.season_team.division }} {{ membership.season_team.name }}?</p>
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">End Membership</button>
+        <a class="button button--ghost" href="{% url 'seasons:player-history' membership.player_id %}">Cancel</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/membership_form.html b/seasons/templates/seasons/membership_form.html
new file mode 100644
index 0000000..191f98b
--- /dev/null
+++ b/seasons/templates/seasons/membership_form.html
@@ -0,0 +1,20 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}{% if membership %}Edit Player Membership{% else %}Create Player Membership{% endif %}{% endblock %}
+{% block seasons_subtitle %}Player membership changes preserve roster history.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.non_field_errors }}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">{% if membership %}Save Membership{% else %}Create Membership{% endif %}</button>
+        {% if membership %}
+            <a class="button button--ghost" href="{% url 'seasons:membership-transfer' membership.id %}">Transfer or Add Team</a>
+            <a class="button button--ghost" href="{% url 'seasons:membership-end' membership.id %}">End Membership</a>
+        {% endif %}
+        <a class="button button--ghost" href="{% url 'seasons:membership-list' %}">Cancel</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/membership_list.html b/seasons/templates/seasons/membership_list.html
new file mode 100644
index 0000000..008aed9
--- /dev/null
+++ b/seasons/templates/seasons/membership_list.html
@@ -0,0 +1,68 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}Player Memberships{% endblock %}
+{% block seasons_subtitle %}Roster stints are preserved as season history.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <form method="get" class="pdp-form">
+        <label>Search <input type="text" name="q" value="{{ filters.q }}" placeholder="Player name"></label>
+        <label>
+            Season
+            <select name="season">
+                <option value="">All seasons</option>
+                {% for season in seasons %}
+                    <option value="{{ season.id }}"{% if filters.season == season.id|stringformat:"s" %} selected{% endif %}>{{ season.name }}</option>
+                {% endfor %}
+            </select>
+        </label>
+        <label>
+            Team
+            <select name="team">
+                <option value="">All teams</option>
+                {% for team in teams %}
+                    <option value="{{ team.id }}"{% if filters.team == team.id|stringformat:"s" %} selected{% endif %}>{{ team.season.name }} / {{ team.division }} {{ team.name }}</option>
+                {% endfor %}
+            </select>
+        </label>
+        <label>
+            Active
+            <select name="active">
+                <option value="">Any</option>
+                <option value="yes"{% if filters.active == "yes" %} selected{% endif %}>Active</option>
+                <option value="no"{% if filters.active == "no" %} selected{% endif %}>Inactive</option>
+            </select>
+        </label>
+        <button class="button button--primary" type="submit">Apply</button>
+        <a class="button button--ghost" href="{% url 'seasons:membership-list' %}">Reset</a>
+        <a class="button button--ghost" href="{% url 'seasons:membership-new' %}">Create Membership</a>
+    </form>
+</article>
+<article class="pdp-card">
+    <div class="table-wrap">
+        <table class="pdp-table">
+            <thead>
+                <tr><th>Player</th><th>Season</th><th>Team</th><th>Status</th><th>Primary</th><th>Active</th><th></th></tr>
+            </thead>
+            <tbody>
+                {% for membership in memberships %}
+                    <tr>
+                        <td>{{ membership.player.display_name }}</td>
+                        <td>{{ membership.season.name }}</td>
+                        <td>{{ membership.season_team.division }} {{ membership.season_team.name }}</td>
+                        <td>{{ membership.get_status_display }}</td>
+                        <td>{% if membership.is_primary %}Yes{% else %}No{% endif %}</td>
+                        <td>{% if membership.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td>
+                            <a class="button button--ghost" href="{% url 'seasons:player-history' membership.player_id %}">History</a>
+                            <a class="button button--ghost" href="{% url 'seasons:membership-edit' membership.id %}">Edit</a>
+                        </td>
+                    </tr>
+                {% empty %}
+                    <tr><td colspan="7">No player memberships match these filters.</td></tr>
+                {% endfor %}
+            </tbody>
+        </table>
+    </div>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/membership_transfer.html b/seasons/templates/seasons/membership_transfer.html
new file mode 100644
index 0000000..511919a
--- /dev/null
+++ b/seasons/templates/seasons/membership_transfer.html
@@ -0,0 +1,17 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}Transfer or Add Membership{% endblock %}
+{% block seasons_subtitle %}Transfers end the old primary membership; additional memberships preserve the existing primary team.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <p>{{ membership.player.display_name }} currently has membership with {{ membership.season_team.division }} {{ membership.season_team.name }} for {{ membership.season.name }}.</p>
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.non_field_errors }}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">Save Membership Change</button>
+        <a class="button button--ghost" href="{% url 'seasons:player-history' membership.player_id %}">Cancel</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/player_history.html b/seasons/templates/seasons/player_history.html
new file mode 100644
index 0000000..e016cb7
--- /dev/null
+++ b/seasons/templates/seasons/player_history.html
@@ -0,0 +1,42 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}Player Season History{% endblock %}
+{% block seasons_subtitle %}Season-by-season roster history for {{ player.display_name }}.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <h2>{{ player.display_name }}</h2>
+    <div class="pdp-actions">
+        <a class="button button--ghost" href="{% url 'analytics:player-profile' player.id %}">Analytics Profile</a>
+        <a class="button button--ghost" href="{% url 'seasons:membership-new' %}">Create Membership</a>
+    </div>
+    <div class="table-wrap">
+        <table class="pdp-table">
+            <thead>
+                <tr><th>Season</th><th>Team</th><th>Status</th><th>Primary</th><th>Active</th><th>Dates</th><th>Source</th><th></th></tr>
+            </thead>
+            <tbody>
+                {% for membership in memberships %}
+                    <tr>
+                        <td>{{ membership.season.name }}</td>
+                        <td>{{ membership.season_team.division }} {{ membership.season_team.name }}</td>
+                        <td>{{ membership.get_status_display }}</td>
+                        <td>{% if membership.is_primary %}Yes{% else %}No{% endif %}</td>
+                        <td>{% if membership.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td>{{ membership.starts_on|default:"-" }} - {{ membership.ends_on|default:"-" }}</td>
+                        <td>{{ membership.source|default:"manual" }}</td>
+                        <td>
+                            <a class="button button--ghost" href="{% url 'seasons:membership-edit' membership.id %}">Edit</a>
+                            {% if membership.is_active %}
+                                <a class="button button--ghost" href="{% url 'seasons:membership-transfer' membership.id %}">Transfer/Add</a>
+                            {% endif %}
+                        </td>
+                    </tr>
+                {% empty %}
+                    <tr><td colspan="8">No season memberships are recorded for this player.</td></tr>
+                {% endfor %}
+            </tbody>
+        </table>
+    </div>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/season_detail.html b/seasons/templates/seasons/season_detail.html
new file mode 100644
index 0000000..68eb237
--- /dev/null
+++ b/seasons/templates/seasons/season_detail.html
@@ -0,0 +1,49 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}{{ season.name }}{% endblock %}
+{% block seasons_subtitle %}Season teams, memberships, and coach assignment entry points.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <dl class="pdp-definition-list">
+        <dt>Key</dt><dd>{{ season.key }}</dd>
+        <dt>Dates</dt><dd>{{ season.starts_on|default:"-" }} - {{ season.ends_on|default:"-" }}</dd>
+        <dt>Current</dt><dd>{% if season.is_current %}Yes{% else %}No{% endif %}</dd>
+        <dt>Active</dt><dd>{% if season.is_active %}Active{% else %}Inactive{% endif %}</dd>
+    </dl>
+    <div class="pdp-actions">
+        <a class="button button--primary" href="{% url 'seasons:season-edit' season.id %}">Edit Season</a>
+        {% if season.is_active and not season.is_current %}
+            <a class="button button--ghost" href="{% url 'seasons:season-set-current' season.id %}">Set Current</a>
+        {% endif %}
+        <a class="button button--ghost" href="{% url 'seasons:season-team-new' season.id %}">Add Team</a>
+        <a class="button button--ghost" href="{% url 'seasons:membership-list' %}?season={{ season.id }}">Player Memberships</a>
+        <a class="button button--ghost" href="{% url 'seasons:coach-assignment-list' %}?season={{ season.id }}">Coach Assignments</a>
+    </div>
+</article>
+
+<article class="pdp-card">
+    <h2>Teams</h2>
+    <div class="table-wrap">
+        <table class="pdp-table">
+            <thead>
+                <tr><th>Team</th><th>Division</th><th>Active</th><th>Memberships</th><th>Assignments</th><th></th></tr>
+            </thead>
+            <tbody>
+                {% for team in teams %}
+                    <tr>
+                        <td>{{ team.name }}</td>
+                        <td>{{ team.division }}</td>
+                        <td>{% if team.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td>{{ team.membership_count }}</td>
+                        <td>{{ team.assignment_count }}</td>
+                        <td><a class="button button--ghost" href="{% url 'seasons:team-edit' team.id %}">Edit</a></td>
+                    </tr>
+                {% empty %}
+                    <tr><td colspan="6">No teams are recorded for this season.</td></tr>
+                {% endfor %}
+            </tbody>
+        </table>
+    </div>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/season_form.html b/seasons/templates/seasons/season_form.html
new file mode 100644
index 0000000..4020ae9
--- /dev/null
+++ b/seasons/templates/seasons/season_form.html
@@ -0,0 +1,16 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}{% if season %}Edit Season{% else %}Create Season{% endif %}{% endblock %}
+{% block seasons_subtitle %}Season records identify roster and evaluation context.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.non_field_errors }}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">{% if season %}Save Season{% else %}Create Season{% endif %}</button>
+        <a class="button button--ghost" href="{% if season %}{% url 'seasons:season-detail' season.id %}{% else %}{% url 'seasons:season-list' %}{% endif %}">Cancel</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/season_list.html b/seasons/templates/seasons/season_list.html
new file mode 100644
index 0000000..9d31c87
--- /dev/null
+++ b/seasons/templates/seasons/season_list.html
@@ -0,0 +1,44 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}Seasons{% endblock %}
+{% block seasons_subtitle %}Create seasons and choose the current operational season.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <div class="pdp-actions">
+        <a class="button button--primary" href="{% url 'seasons:season-new' %}">Create Season</a>
+    </div>
+    <div class="table-wrap">
+        <table class="pdp-table">
+            <thead>
+                <tr>
+                    <th>Season</th>
+                    <th>Dates</th>
+                    <th>Current</th>
+                    <th>Active</th>
+                    <th>Teams</th>
+                    <th>Memberships</th>
+                    <th>Assignments</th>
+                    <th></th>
+                </tr>
+            </thead>
+            <tbody>
+                {% for season in seasons %}
+                    <tr>
+                        <td>{{ season.name }}<br><small>{{ season.key }}</small></td>
+                        <td>{{ season.starts_on|default:"-" }} - {{ season.ends_on|default:"-" }}</td>
+                        <td>{% if season.is_current %}Yes{% else %}No{% endif %}</td>
+                        <td>{% if season.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td>{{ season.team_count }}</td>
+                        <td>{{ season.membership_count }}</td>
+                        <td>{{ season.assignment_count }}</td>
+                        <td><a class="button button--ghost" href="{% url 'seasons:season-detail' season.id %}">Open</a></td>
+                    </tr>
+                {% empty %}
+                    <tr><td colspan="8">No seasons have been created.</td></tr>
+                {% endfor %}
+            </tbody>
+        </table>
+    </div>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/season_set_current.html b/seasons/templates/seasons/season_set_current.html
new file mode 100644
index 0000000..8347443
--- /dev/null
+++ b/seasons/templates/seasons/season_set_current.html
@@ -0,0 +1,16 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}Set Current Season{% endblock %}
+{% block seasons_subtitle %}Only one season can be current at a time.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <p>Set <strong>{{ season.name }}</strong> as the current season?</p>
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">Set Current Season</button>
+        <a class="button button--ghost" href="{% url 'seasons:season-detail' season.id %}">Cancel</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/team_form.html b/seasons/templates/seasons/team_form.html
new file mode 100644
index 0000000..124d819
--- /dev/null
+++ b/seasons/templates/seasons/team_form.html
@@ -0,0 +1,16 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}{% if team %}Edit Season Team{% else %}Create Season Team{% endif %}{% endblock %}
+{% block seasons_subtitle %}Teams are scoped to one season.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <form method="post" class="pdp-form">
+        {% csrf_token %}
+        {{ form.non_field_errors }}
+        {{ form.as_p }}
+        <button class="button button--primary" type="submit">{% if team %}Save Team{% else %}Create Team{% endif %}</button>
+        <a class="button button--ghost" href="{% url 'seasons:team-list' %}">Cancel</a>
+    </form>
+</article>
+{% endblock %}
diff --git a/seasons/templates/seasons/team_list.html b/seasons/templates/seasons/team_list.html
new file mode 100644
index 0000000..237190a
--- /dev/null
+++ b/seasons/templates/seasons/team_list.html
@@ -0,0 +1,47 @@
+{% extends "seasons/base.html" %}
+
+{% block seasons_title %}Season Teams{% endblock %}
+{% block seasons_subtitle %}Season-specific team and division records.{% endblock %}
+
+{% block seasons_content %}
+<article class="pdp-card">
+    <form method="get" class="pdp-form">
+        <label>
+            Season
+            <select name="season">
+                <option value="">All seasons</option>
+                {% for season in seasons %}
+                    <option value="{{ season.id }}"{% if selected_season_id == season.id|stringformat:"s" %} selected{% endif %}>{{ season.name }}</option>
+                {% endfor %}
+            </select>
+        </label>
+        <button class="button button--primary" type="submit">Apply</button>
+        <a class="button button--ghost" href="{% url 'seasons:team-list' %}">Reset</a>
+        <a class="button button--ghost" href="{% url 'seasons:team-new' %}">Create Team</a>
+    </form>
+</article>
+<article class="pdp-card">
+    <div class="table-wrap">
+        <table class="pdp-table">
+            <thead>
+                <tr><th>Season</th><th>Team</th><th>Division</th><th>Active</th><th>Memberships</th><th>Assignments</th><th></th></tr>
+            </thead>
+            <tbody>
+                {% for team in teams %}
+                    <tr>
+                        <td>{{ team.season.name }}</td>
+                        <td>{{ team.name }}</td>
+                        <td>{{ team.division }}</td>
+                        <td>{% if team.is_active %}Active{% else %}Inactive{% endif %}</td>
+                        <td>{{ team.membership_count }}</td>
+                        <td>{{ team.assignment_count }}</td>
+                        <td><a class="button button--ghost" href="{% url 'seasons:team-edit' team.id %}">Edit</a></td>
+                    </tr>
+                {% empty %}
+                    <tr><td colspan="7">No teams match these filters.</td></tr>
+                {% endfor %}
+            </tbody>
+        </table>
+    </div>
+</article>
+{% endblock %}
diff --git a/seasons/tests.py b/seasons/tests.py
index b6c5002..fa39f86 100644
--- a/seasons/tests.py
+++ b/seasons/tests.py
@@ -6,6 +6,7 @@ from django.contrib.auth import get_user_model
 from django.core.exceptions import ValidationError
 from django.db import transaction
 from django.test import TestCase
+from django.urls import reverse
 
 from accounts.models import AccountRole
 from accounts.services.profile_service import get_or_create_account_profile, set_account_role
@@ -396,3 +397,311 @@ class SeasonsAdminTests(TestCase):
             self.assertIn("created_at", model_admin.readonly_fields)
             self.assertIn("updated_at", model_admin.readonly_fields)
             self.assertTrue(model_admin.search_fields)
+
+
+class SeasonOperationsUITests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.regular = User.objects.create_user(username="regular", password="testpass")
+        self.coach = User.objects.create_user(
+            username="coach",
+            password="original-pass",
+            first_name="Casey",
+            last_name="Coach",
+            email="coach@example.com",
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        self.player = Player.objects.create(first_name="Alex", last_name="Player")
+        self.spring = create_season(key="2026-spring", name="2026 Spring", starts_on=date(2026, 4, 1), is_current=True)
+        self.summer = create_season(key="2026-summer", name="2026 Summer")
+        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
+        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
+        self.mounties, _ = get_or_create_season_team(season=self.summer, name="Mounties", division="15U")
+
+    def login_staff(self):
+        self.client.force_login(self.staff)
+
+    def test_season_operations_require_staff(self):
+        url = reverse("seasons:season-list")
+
+        self.assertEqual(self.client.get(url).status_code, 302)
+        self.client.force_login(self.regular)
+        self.assertEqual(self.client.get(url).status_code, 403)
+
+        self.login_staff()
+        response = self.client.get(url)
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "2026 Spring")
+
+    def test_staff_can_create_edit_and_set_current_season(self):
+        self.login_staff()
+
+        response = self.client.post(
+            reverse("seasons:season-new"),
+            {
+                "key": "2027-spring",
+                "name": "2027 Spring",
+                "starts_on": "2027-04-01",
+                "ends_on": "",
+                "is_active": "on",
+            },
+        )
+        season = Season.objects.get(key="2027-spring")
+        self.assertRedirects(response, reverse("seasons:season-detail", kwargs={"season_id": season.id}))
+
+        response = self.client.post(
+            reverse("seasons:season-edit", kwargs={"season_id": season.id}),
+            {
+                "key": "2027-spring",
+                "name": "2027 Spring Updated",
+                "starts_on": "2027-04-01",
+                "ends_on": "2027-08-31",
+                "is_active": "on",
+            },
+        )
+        self.assertRedirects(response, reverse("seasons:season-detail", kwargs={"season_id": season.id}))
+        season.refresh_from_db()
+        self.assertEqual(season.name, "2027 Spring Updated")
+
+        self.client.post(reverse("seasons:season-set-current", kwargs={"season_id": season.id}), {"confirm": "on"})
+        self.spring.refresh_from_db()
+        season.refresh_from_db()
+        self.assertFalse(self.spring.is_current)
+        self.assertTrue(season.is_current)
+
+        self.client.post(
+            reverse("seasons:season-edit", kwargs={"season_id": season.id}),
+            {
+                "key": "2027-spring",
+                "name": "2027 Spring Updated",
+                "starts_on": "2027-04-01",
+                "ends_on": "2027-08-31",
+            },
+        )
+        season.refresh_from_db()
+        self.assertFalse(season.is_active)
+        self.assertFalse(season.is_current)
+
+    def test_staff_can_create_and_edit_season_team(self):
+        self.login_staff()
+
+        response = self.client.post(
+            reverse("seasons:season-team-new", kwargs={"season_id": self.spring.id}),
+            {
+                "season": self.spring.id,
+                "name": "Cardinals",
+                "division": "13U",
+                "external_source": "Roster",
+                "external_identifier": "TEAM-1",
+                "is_active": "on",
+            },
+        )
+        self.assertRedirects(response, reverse("seasons:team-list"))
+        team = SeasonTeam.objects.get(name="Cardinals")
+
+        response = self.client.post(
+            reverse("seasons:team-edit", kwargs={"team_id": team.id}),
+            {
+                "season": self.summer.id,
+                "name": "Cardinals Updated",
+                "division": "13U",
+                "external_source": "Roster",
+                "external_identifier": "TEAM-1",
+                "is_active": "on",
+            },
+        )
+        self.assertRedirects(response, reverse("seasons:team-list"))
+        team.refresh_from_db()
+        self.assertEqual(team.name, "Cardinals Updated")
+        self.assertEqual(team.season, self.spring)
+
+    def test_staff_can_manage_membership_history_transfer_and_additional_membership(self):
+        self.login_staff()
+        create_response = self.client.post(
+            reverse("seasons:membership-new"),
+            {
+                "player": self.player.id,
+                "season_team": self.dodgers.id,
+                "status": RosterStatus.ACTIVE,
+                "jersey_number": "12",
+                "is_primary": "on",
+                "is_active": "on",
+                "starts_on": "2026-04-01",
+                "ends_on": "",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+        membership = PlayerRosterMembership.objects.get(player=self.player, season_team=self.dodgers)
+        self.assertRedirects(create_response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
+        self.assertTrue(membership.is_primary)
+
+        response = self.client.post(
+            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
+            {
+                "action": "additional",
+                "season_team": self.expos.id,
+                "transfer_date": "2026-05-01",
+                "jersey_number": "8",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+        self.assertRedirects(response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
+        membership.refresh_from_db()
+        additional = PlayerRosterMembership.objects.get(player=self.player, season_team=self.expos)
+        self.assertTrue(membership.is_active)
+        self.assertTrue(membership.is_primary)
+        self.assertEqual(additional.status, RosterStatus.GUEST)
+        self.assertFalse(additional.is_primary)
+
+        response = self.client.post(
+            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
+            {
+                "action": "transfer",
+                "season_team": self.expos.id,
+                "transfer_date": "2026-06-01",
+                "jersey_number": "",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "already has")
+
+        additional.delete()
+        response = self.client.post(
+            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
+            {
+                "action": "transfer",
+                "season_team": self.expos.id,
+                "transfer_date": "2026-06-01",
+                "jersey_number": "",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+        self.assertRedirects(response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
+        membership.refresh_from_db()
+        transferred = PlayerRosterMembership.objects.get(player=self.player, season_team=self.expos)
+        self.assertFalse(membership.is_active)
+        self.assertEqual(membership.status, RosterStatus.TRANSFERRED)
+        self.assertTrue(transferred.is_primary)
+
+    def test_transfer_rejects_cross_season_destination_tampering(self):
+        self.login_staff()
+        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+
+        response = self.client.post(
+            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
+            {
+                "action": "transfer",
+                "season_team": self.mounties.id,
+                "transfer_date": "2026-06-01",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        membership.refresh_from_db()
+        self.assertTrue(membership.is_active)
+        self.assertEqual(PlayerRosterMembership.objects.filter(player=self.player).count(), 1)
+
+    def test_player_history_and_invalid_filter_ids_render(self):
+        self.login_staff()
+        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+
+        response = self.client.get(reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Dodgers")
+
+        response = self.client.get(reverse("seasons:membership-list") + "?season=bad&team=bad")
+        self.assertEqual(response.status_code, 200)
+
+    def test_staff_can_create_edit_end_coach_assignment_without_account_side_effects(self):
+        original_password = self.coach.password
+        self.login_staff()
+
+        response = self.client.post(
+            reverse("seasons:coach-assignment-new"),
+            {
+                "user": self.coach.id,
+                "season_team": self.dodgers.id,
+                "assignment_role": CoachAssignmentRole.HEAD_COACH,
+                "is_primary": "on",
+                "is_active": "on",
+                "starts_on": "2026-04-01",
+                "ends_on": "",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+        assignment = CoachSeasonAssignment.objects.get(user=self.coach, season_team=self.dodgers)
+        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
+
+        response = self.client.post(
+            reverse("seasons:coach-assignment-edit", kwargs={"assignment_id": assignment.id}),
+            {
+                "user": self.regular.id,
+                "season_team": self.mounties.id,
+                "assignment_role": CoachAssignmentRole.EVALUATOR,
+                "is_primary": "on",
+                "is_active": "on",
+                "starts_on": "2026-04-01",
+                "ends_on": "",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
+        assignment.refresh_from_db()
+        self.coach.refresh_from_db()
+        profile = get_or_create_account_profile(self.coach)
+        self.assertEqual(assignment.user, self.coach)
+        self.assertEqual(assignment.season_team, self.dodgers)
+        self.assertEqual(assignment.assignment_role, CoachAssignmentRole.EVALUATOR)
+        self.assertEqual(profile.role, AccountRole.COACH)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+        self.assertEqual(self.coach.password, original_password)
+
+        response = self.client.post(
+            reverse("seasons:coach-assignment-end", kwargs={"assignment_id": assignment.id}),
+            {"ends_on": "2026-08-01", "confirm": "on"},
+        )
+        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
+        assignment.refresh_from_db()
+        self.assertFalse(assignment.is_active)
+        self.assertFalse(assignment.is_primary)
+        self.assertEqual(assignment.ends_on, date(2026, 8, 1))
+
+    def test_non_coach_user_cannot_be_assigned_as_coach(self):
+        self.login_staff()
+
+        response = self.client.post(
+            reverse("seasons:coach-assignment-new"),
+            {
+                "user": self.regular.id,
+                "season_team": self.dodgers.id,
+                "assignment_role": CoachAssignmentRole.HEAD_COACH,
+                "is_primary": "on",
+                "is_active": "on",
+                "starts_on": "",
+                "ends_on": "",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertFalse(CoachSeasonAssignment.objects.filter(user=self.regular).exists())
+
+    def test_coach_history_requires_coach_profile(self):
+        self.login_staff()
+
+        response = self.client.get(reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
+        self.assertEqual(response.status_code, 200)
+
+        response = self.client.get(reverse("seasons:coach-history", kwargs={"user_id": self.regular.id}))
+        self.assertEqual(response.status_code, 404)
diff --git a/seasons/urls.py b/seasons/urls.py
new file mode 100644
index 0000000..514abd4
--- /dev/null
+++ b/seasons/urls.py
@@ -0,0 +1,49 @@
+from django.urls import path
+
+from seasons.views import (
+    CoachAssignmentCreateView,
+    CoachAssignmentEditView,
+    CoachAssignmentEndView,
+    CoachAssignmentListView,
+    CoachSeasonHistoryView,
+    PlayerMembershipCreateView,
+    PlayerMembershipEditView,
+    PlayerMembershipEndView,
+    PlayerMembershipListView,
+    PlayerMembershipTransferView,
+    PlayerSeasonHistoryView,
+    SeasonCreateView,
+    SeasonDetailView,
+    SeasonEditView,
+    SeasonListView,
+    SeasonSetCurrentView,
+    SeasonTeamCreateView,
+    SeasonTeamEditView,
+    SeasonTeamListView,
+)
+
+
+app_name = "seasons"
+
+urlpatterns = [
+    path("", SeasonListView.as_view(), name="season-list"),
+    path("new/", SeasonCreateView.as_view(), name="season-new"),
+    path("<int:season_id>/", SeasonDetailView.as_view(), name="season-detail"),
+    path("<int:season_id>/edit/", SeasonEditView.as_view(), name="season-edit"),
+    path("<int:season_id>/set-current/", SeasonSetCurrentView.as_view(), name="season-set-current"),
+    path("teams/", SeasonTeamListView.as_view(), name="team-list"),
+    path("teams/new/", SeasonTeamCreateView.as_view(), name="team-new"),
+    path("<int:season_id>/teams/new/", SeasonTeamCreateView.as_view(), name="season-team-new"),
+    path("teams/<int:team_id>/edit/", SeasonTeamEditView.as_view(), name="team-edit"),
+    path("memberships/", PlayerMembershipListView.as_view(), name="membership-list"),
+    path("memberships/new/", PlayerMembershipCreateView.as_view(), name="membership-new"),
+    path("memberships/<int:membership_id>/edit/", PlayerMembershipEditView.as_view(), name="membership-edit"),
+    path("memberships/<int:membership_id>/end/", PlayerMembershipEndView.as_view(), name="membership-end"),
+    path("memberships/<int:membership_id>/transfer/", PlayerMembershipTransferView.as_view(), name="membership-transfer"),
+    path("players/<int:player_id>/history/", PlayerSeasonHistoryView.as_view(), name="player-history"),
+    path("coach-assignments/", CoachAssignmentListView.as_view(), name="coach-assignment-list"),
+    path("coach-assignments/new/", CoachAssignmentCreateView.as_view(), name="coach-assignment-new"),
+    path("coach-assignments/<int:assignment_id>/edit/", CoachAssignmentEditView.as_view(), name="coach-assignment-edit"),
+    path("coach-assignments/<int:assignment_id>/end/", CoachAssignmentEndView.as_view(), name="coach-assignment-end"),
+    path("coaches/<int:user_id>/history/", CoachSeasonHistoryView.as_view(), name="coach-history"),
+]
diff --git a/seasons/views.py b/seasons/views.py
new file mode 100644
index 0000000..4445c1c
--- /dev/null
+++ b/seasons/views.py
@@ -0,0 +1,639 @@
+from __future__ import annotations
+
+from django.contrib import messages
+from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
+from django.core.exceptions import PermissionDenied, ValidationError
+from django.db.models import Count, Q
+from django.http import Http404
+from django.shortcuts import get_object_or_404, redirect
+from django.views.generic import FormView, ListView, TemplateView
+
+from accounts.services.permissions import is_staff_or_admin
+from players.models import Player
+from seasons.forms import (
+    CoachAssignmentEndForm,
+    CoachSeasonAssignmentForm,
+    ConfirmCurrentSeasonForm,
+    PlayerMembershipEndForm,
+    PlayerMembershipTransferForm,
+    PlayerRosterMembershipForm,
+    SeasonForm,
+    SeasonTeamForm,
+)
+from seasons.models import CoachSeasonAssignment, PlayerRosterMembership, RosterStatus, Season, SeasonTeam
+from seasons.services.coach_assignment_service import create_assignment, deactivate_assignment, update_assignment
+from seasons.services.membership_service import create_membership, deactivate_membership, transfer_player, update_membership
+from seasons.services.season_service import create_season, set_current_season, update_season
+from seasons.services.team_service import get_or_create_season_team, update_season_team
+
+
+class SeasonOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
+    def test_func(self):
+        return is_staff_or_admin(self.request.user)
+
+
+def _clean_int(value: str) -> str | None:
+    value = str(value or "").strip()
+    return value if value.isdigit() else None
+
+
+class SeasonListView(SeasonOperationsStaffRequiredMixin, ListView):
+    model = Season
+    template_name = "seasons/season_list.html"
+    context_object_name = "seasons"
+
+    def get_queryset(self):
+        return Season.objects.annotate(
+            team_count=Count("teams", distinct=True),
+            membership_count=Count("teams__player_memberships", distinct=True),
+            assignment_count=Count("teams__coach_assignments", distinct=True),
+        )
+
+
+class SeasonDetailView(SeasonOperationsStaffRequiredMixin, TemplateView):
+    template_name = "seasons/season_detail.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        teams = (
+            self.season.teams.annotate(
+                membership_count=Count("player_memberships", distinct=True),
+                assignment_count=Count("coach_assignments", distinct=True),
+            )
+            .order_by("division", "name", "id")
+        )
+        context.update({"season": self.season, "teams": teams})
+        return context
+
+
+class SeasonCreateView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/season_form.html"
+    form_class = SeasonForm
+
+    def form_valid(self, form):
+        try:
+            season = create_season(**form.cleaned_data)
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Season created.")
+        return redirect("seasons:season-detail", season_id=season.id)
+
+
+class SeasonEditView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/season_form.html"
+    form_class = SeasonForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_initial(self):
+        return {
+            "key": self.season.key,
+            "name": self.season.name,
+            "starts_on": self.season.starts_on,
+            "ends_on": self.season.ends_on,
+            "is_active": self.season.is_active,
+        }
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["season"] = self.season
+        return context
+
+    def form_valid(self, form):
+        try:
+            update_season(self.season, **form.cleaned_data)
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Season updated.")
+        return redirect("seasons:season-detail", season_id=self.season.id)
+
+
+class SeasonSetCurrentView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/season_set_current.html"
+    form_class = ConfirmCurrentSeasonForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
+        if not self.season.is_active:
+            raise PermissionDenied("Inactive seasons cannot be made current.")
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["season"] = self.season
+        return context
+
+    def form_valid(self, form):
+        set_current_season(self.season)
+        messages.success(self.request, f"{self.season.name} is now the current season.")
+        return redirect("seasons:season-detail", season_id=self.season.id)
+
+
+class SeasonTeamListView(SeasonOperationsStaffRequiredMixin, ListView):
+    model = SeasonTeam
+    template_name = "seasons/team_list.html"
+    context_object_name = "teams"
+
+    def get_queryset(self):
+        queryset = SeasonTeam.objects.select_related("season").annotate(
+            membership_count=Count("player_memberships", distinct=True),
+            assignment_count=Count("coach_assignments", distinct=True),
+        )
+        season_id = _clean_int(self.request.GET.get("season"))
+        if season_id:
+            queryset = queryset.filter(season_id=season_id)
+        return queryset.order_by("-season__is_current", "season__name", "division", "name", "id")
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["seasons"] = Season.objects.order_by("-is_current", "-starts_on", "name")
+        context["selected_season_id"] = self.request.GET.get("season", "")
+        return context
+
+
+class SeasonTeamCreateView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/team_form.html"
+    form_class = SeasonTeamForm
+
+    def get_form_kwargs(self):
+        kwargs = super().get_form_kwargs()
+        season_id = self.kwargs.get("season_id")
+        if season_id:
+            kwargs["fixed_season"] = get_object_or_404(Season, pk=season_id)
+        return kwargs
+
+    def form_valid(self, form):
+        data = form.cleaned_data
+        try:
+            team, created = get_or_create_season_team(
+                season=data["season"],
+                name=data["name"],
+                division=data["division"],
+                external_source=data.get("external_source", ""),
+                external_identifier=data.get("external_identifier", ""),
+            )
+            if not created:
+                update_season_team(team, is_active=data.get("is_active", False))
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Season team created." if created else "Existing season team reused.")
+        return redirect("seasons:team-list")
+
+
+class SeasonTeamEditView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/team_form.html"
+    form_class = SeasonTeamForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.team = get_object_or_404(SeasonTeam.objects.select_related("season"), pk=kwargs["team_id"])
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_form_kwargs(self):
+        kwargs = super().get_form_kwargs()
+        kwargs["fixed_season"] = self.team.season
+        return kwargs
+
+    def get_initial(self):
+        return {
+            "season": self.team.season,
+            "name": self.team.name,
+            "division": self.team.division,
+            "external_source": self.team.external_source,
+            "external_identifier": self.team.external_identifier,
+            "is_active": self.team.is_active,
+        }
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["team"] = self.team
+        return context
+
+    def form_valid(self, form):
+        data = form.cleaned_data
+        try:
+            update_season_team(
+                self.team,
+                name=data["name"],
+                division=data["division"],
+                external_source=data.get("external_source", ""),
+                external_identifier=data.get("external_identifier", ""),
+                is_active=data.get("is_active", False),
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Season team updated.")
+        return redirect("seasons:team-list")
+
+
+class PlayerMembershipListView(SeasonOperationsStaffRequiredMixin, ListView):
+    model = PlayerRosterMembership
+    template_name = "seasons/membership_list.html"
+    context_object_name = "memberships"
+
+    def get_queryset(self):
+        queryset = PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season")
+        season_id = _clean_int(self.request.GET.get("season"))
+        team_id = _clean_int(self.request.GET.get("team"))
+        active = self.request.GET.get("active")
+        search = self.request.GET.get("q", "").strip()
+        if season_id:
+            queryset = queryset.filter(season_team__season_id=season_id)
+        if team_id:
+            queryset = queryset.filter(season_team_id=team_id)
+        if active == "yes":
+            queryset = queryset.filter(is_active=True)
+        elif active == "no":
+            queryset = queryset.filter(is_active=False)
+        if search:
+            queryset = queryset.filter(Q(player__first_name__icontains=search) | Q(player__last_name__icontains=search))
+        return queryset.order_by("-season_team__season__is_current", "season_team__season__name", "player__last_name", "player__first_name", "id")
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context.update(
+            {
+                "seasons": Season.objects.order_by("-is_current", "-starts_on", "name"),
+                "teams": SeasonTeam.objects.select_related("season").order_by("-season__is_current", "season__name", "division", "name"),
+                "filters": {
+                    "season": self.request.GET.get("season", ""),
+                    "team": self.request.GET.get("team", ""),
+                    "active": self.request.GET.get("active", ""),
+                    "q": self.request.GET.get("q", ""),
+                },
+            }
+        )
+        return context
+
+
+class PlayerMembershipCreateView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/membership_form.html"
+    form_class = PlayerRosterMembershipForm
+
+    def form_valid(self, form):
+        data = form.cleaned_data
+        try:
+            membership = create_membership(
+                player=data["player"],
+                season_team=data["season_team"],
+                status=data["status"],
+                jersey_number=data.get("jersey_number", ""),
+                is_primary=data.get("is_primary", False),
+                is_active=data.get("is_active", False),
+                starts_on=data.get("starts_on"),
+                ends_on=data.get("ends_on"),
+                source=data.get("source", ""),
+                source_identifier=data.get("source_identifier", ""),
+                sync_player_fields=True,
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Player membership created.")
+        return redirect("seasons:player-history", player_id=membership.player_id)
+
+
+class PlayerMembershipEditView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/membership_form.html"
+    form_class = PlayerRosterMembershipForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.membership = get_object_or_404(
+            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
+            pk=kwargs["membership_id"],
+        )
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_form_kwargs(self):
+        kwargs = super().get_form_kwargs()
+        kwargs["fixed_season"] = self.membership.season
+        kwargs["editing"] = True
+        return kwargs
+
+    def get_initial(self):
+        return {
+            "player": self.membership.player,
+            "season_team": self.membership.season_team,
+            "status": self.membership.status,
+            "jersey_number": self.membership.jersey_number,
+            "is_primary": self.membership.is_primary,
+            "is_active": self.membership.is_active,
+            "starts_on": self.membership.starts_on,
+            "ends_on": self.membership.ends_on,
+            "source": self.membership.source,
+            "source_identifier": self.membership.source_identifier,
+        }
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["membership"] = self.membership
+        return context
+
+    def form_valid(self, form):
+        data = form.cleaned_data
+        try:
+            update_membership(
+                self.membership,
+                status=data["status"],
+                jersey_number=data.get("jersey_number", ""),
+                is_primary=data.get("is_primary", False),
+                is_active=data.get("is_active", False),
+                starts_on=data.get("starts_on"),
+                ends_on=data.get("ends_on"),
+                source=data.get("source", ""),
+                source_identifier=data.get("source_identifier", ""),
+                sync_player_fields=True,
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Player membership updated.")
+        return redirect("seasons:player-history", player_id=self.membership.player_id)
+
+
+class PlayerMembershipEndView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/membership_end.html"
+    form_class = PlayerMembershipEndForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.membership = get_object_or_404(
+            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
+            pk=kwargs["membership_id"],
+        )
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["membership"] = self.membership
+        return context
+
+    def form_valid(self, form):
+        try:
+            deactivate_membership(
+                self.membership,
+                status=form.cleaned_data["status"],
+                ends_on=form.cleaned_data.get("ends_on"),
+                sync_player_fields=True,
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Player membership ended.")
+        return redirect("seasons:player-history", player_id=self.membership.player_id)
+
+
+class PlayerMembershipTransferView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/membership_transfer.html"
+    form_class = PlayerMembershipTransferForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.membership = get_object_or_404(
+            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
+            pk=kwargs["membership_id"],
+        )
+        if not self.membership.is_active:
+            raise PermissionDenied("Only active memberships can be transferred or extended.")
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_form_kwargs(self):
+        kwargs = super().get_form_kwargs()
+        kwargs["source_membership"] = self.membership
+        return kwargs
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["membership"] = self.membership
+        return context
+
+    def form_valid(self, form):
+        data = form.cleaned_data
+        try:
+            if data["action"] == PlayerMembershipTransferForm.ACTION_TRANSFER:
+                transfer_player(
+                    player=self.membership.player,
+                    to_season_team=data["season_team"],
+                    from_membership=self.membership,
+                    transfer_date=data.get("transfer_date"),
+                    source=data.get("source", ""),
+                    source_identifier=data.get("source_identifier", ""),
+                    metadata={"created_by": "season_operations_ui"},
+                )
+                messages.success(self.request, "Player transferred.")
+            elif data["action"] == PlayerMembershipTransferForm.ACTION_ADDITIONAL:
+                create_membership(
+                    player=self.membership.player,
+                    season_team=data["season_team"],
+                    status=RosterStatus.GUEST,
+                    jersey_number=data.get("jersey_number", ""),
+                    is_primary=False,
+                    is_active=True,
+                    starts_on=data.get("transfer_date"),
+                    source=data.get("source", ""),
+                    source_identifier=data.get("source_identifier", ""),
+                    sync_player_fields=True,
+                )
+                messages.success(self.request, "Additional membership created.")
+            else:
+                raise ValidationError("Unsupported membership action.")
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        return redirect("seasons:player-history", player_id=self.membership.player_id)
+
+
+class PlayerSeasonHistoryView(SeasonOperationsStaffRequiredMixin, TemplateView):
+    template_name = "seasons/player_history.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        self.player = get_object_or_404(Player, pk=kwargs["player_id"])
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        memberships = (
+            PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
+            .filter(player=self.player)
+            .order_by("-season_team__season__starts_on", "-season_team__season__is_current", "season_team__division", "season_team__name", "-starts_on", "id")
+        )
+        context.update({"player": self.player, "memberships": memberships})
+        return context
+
+
+class CoachAssignmentListView(SeasonOperationsStaffRequiredMixin, ListView):
+    model = CoachSeasonAssignment
+    template_name = "seasons/assignment_list.html"
+    context_object_name = "assignments"
+
+    def get_queryset(self):
+        queryset = CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season", "user__account_profile")
+        season_id = _clean_int(self.request.GET.get("season"))
+        team_id = _clean_int(self.request.GET.get("team"))
+        active = self.request.GET.get("active")
+        search = self.request.GET.get("q", "").strip()
+        if season_id:
+            queryset = queryset.filter(season_team__season_id=season_id)
+        if team_id:
+            queryset = queryset.filter(season_team_id=team_id)
+        if active == "yes":
+            queryset = queryset.filter(is_active=True)
+        elif active == "no":
+            queryset = queryset.filter(is_active=False)
+        if search:
+            queryset = queryset.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | Q(user__username__icontains=search))
+        return queryset.order_by("-season_team__season__is_current", "season_team__season__name", "user__last_name", "user__first_name", "id")
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context.update(
+            {
+                "seasons": Season.objects.order_by("-is_current", "-starts_on", "name"),
+                "teams": SeasonTeam.objects.select_related("season").order_by("-season__is_current", "season__name", "division", "name"),
+                "filters": {
+                    "season": self.request.GET.get("season", ""),
+                    "team": self.request.GET.get("team", ""),
+                    "active": self.request.GET.get("active", ""),
+                    "q": self.request.GET.get("q", ""),
+                },
+            }
+        )
+        return context
+
+
+class CoachAssignmentCreateView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/assignment_form.html"
+    form_class = CoachSeasonAssignmentForm
+
+    def form_valid(self, form):
+        data = form.cleaned_data
+        try:
+            assignment = create_assignment(
+                user=data["user"],
+                season_team=data["season_team"],
+                assignment_role=data["assignment_role"],
+                is_primary=data.get("is_primary", False),
+                is_active=data.get("is_active", False),
+                starts_on=data.get("starts_on"),
+                ends_on=data.get("ends_on"),
+                source=data.get("source", ""),
+                source_identifier=data.get("source_identifier", ""),
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Coach assignment created.")
+        return redirect("seasons:coach-history", user_id=assignment.user_id)
+
+
+class CoachAssignmentEditView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/assignment_form.html"
+    form_class = CoachSeasonAssignmentForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.assignment = get_object_or_404(
+            CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season"),
+            pk=kwargs["assignment_id"],
+        )
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_form_kwargs(self):
+        kwargs = super().get_form_kwargs()
+        kwargs["fixed_season"] = self.assignment.season
+        kwargs["editing"] = True
+        return kwargs
+
+    def get_initial(self):
+        return {
+            "user": self.assignment.user,
+            "season_team": self.assignment.season_team,
+            "assignment_role": self.assignment.assignment_role,
+            "is_primary": self.assignment.is_primary,
+            "is_active": self.assignment.is_active,
+            "starts_on": self.assignment.starts_on,
+            "ends_on": self.assignment.ends_on,
+            "source": self.assignment.source,
+            "source_identifier": self.assignment.source_identifier,
+        }
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["assignment"] = self.assignment
+        return context
+
+    def form_valid(self, form):
+        data = form.cleaned_data
+        original_flags = (self.assignment.user.is_staff, self.assignment.user.is_superuser, self.assignment.user.password)
+        try:
+            update_assignment(
+                self.assignment,
+                assignment_role=data["assignment_role"],
+                is_primary=data.get("is_primary", False),
+                is_active=data.get("is_active", False),
+                starts_on=data.get("starts_on"),
+                ends_on=data.get("ends_on"),
+                source=data.get("source", ""),
+                source_identifier=data.get("source_identifier", ""),
+            )
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        self.assignment.user.refresh_from_db()
+        if original_flags != (self.assignment.user.is_staff, self.assignment.user.is_superuser, self.assignment.user.password):
+            raise ValidationError("Coach assignment updates must not change account privileges or password state.")
+        messages.success(self.request, "Coach assignment updated.")
+        return redirect("seasons:coach-history", user_id=self.assignment.user_id)
+
+
+class CoachAssignmentEndView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/assignment_end.html"
+    form_class = CoachAssignmentEndForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.assignment = get_object_or_404(
+            CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season"),
+            pk=kwargs["assignment_id"],
+        )
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["assignment"] = self.assignment
+        return context
+
+    def form_valid(self, form):
+        try:
+            deactivate_assignment(self.assignment, ends_on=form.cleaned_data.get("ends_on"))
+        except ValidationError as exc:
+            form.add_error(None, exc)
+            return self.form_invalid(form)
+        messages.success(self.request, "Coach assignment ended.")
+        return redirect("seasons:coach-history", user_id=self.assignment.user_id)
+
+
+class CoachSeasonHistoryView(SeasonOperationsStaffRequiredMixin, TemplateView):
+    template_name = "seasons/coach_history.html"
+
+    def dispatch(self, request, *args, **kwargs):
+        User = CoachSeasonAssignment._meta.get_field("user").remote_field.model
+        self.coach = get_object_or_404(User, pk=kwargs["user_id"])
+        if not hasattr(self.coach, "account_profile") or self.coach.account_profile.role != "coach":
+            raise Http404("Coach not found.")
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        assignments = (
+            CoachSeasonAssignment.objects.select_related("season_team", "season_team__season")
+            .filter(user=self.coach)
+            .order_by("-season_team__season__starts_on", "-season_team__season__is_current", "season_team__division", "season_team__name", "-starts_on", "id")
+        )
+        context.update({"coach": self.coach, "assignments": assignments})
+        return context
diff --git a/vancouverminor/urls.py b/vancouverminor/urls.py
index 10758bb..910f848 100644
--- a/vancouverminor/urls.py
+++ b/vancouverminor/urls.py
@@ -24,6 +24,7 @@ urlpatterns = [
     path('accounts/', include('accounts.urls')),
     path('drafts/', include('drafts.urls')),
     path('analytics/', include('analytics.urls')),
+    path('seasons/', include('seasons.urls')),
     path('leaguehub/', include('leaguehub.urls')),
     path('pdp/', include('pdp.urls')),
     path('scholarships/', include('scholarships.urls')),
```

## Terminal State

PASS
