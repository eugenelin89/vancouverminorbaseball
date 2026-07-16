# Prompt 76 - Platform

App/subsystem: platform

Work commit: `b659177`

Terminal state: `PASS`

## User Prompt

```text
Implement Seasonal Participation V1 Phase 3 only: Season-Aware Coach Import.

Use continuous loop engineering.

Continue until the Phase 3 scope is production-ready, fully reviewed, documented, tested, committed, pushed, and the working tree is clean.

Do not start Phase 4 or later work.

==================================================
Current State
=============

Seasonal Participation V1 Phase 1 and Phase 2 are complete.

The repository now contains:

* `seasons.Season`
* `seasons.SeasonTeam`
* `seasons.PlayerRosterMembership`
* `seasons.CoachSeasonAssignment`
* transactional season, team, membership, and assignment services
* current-season handling
* season-aware player import
* permanent player reuse across seasons
* season-specific teams and roster memberships
* same-season player team-change protection
* schema-only seasonal migrations
* comprehensive tests and documentation

Phase 2 made player imports season-aware but deliberately left coach import and evaluations unchanged.

Verified production state before seasonal implementation:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

No historical coach assignment data requires reconstruction.

==================================================
Phase 3 Objective
=================

Make the existing coach CSV import season-aware.

Staff should continue importing normal coach CSV files, but every new coach import must be associated with a selected active season.

For each valid row, the import must:

1. match or create the permanent Django `User`;
2. create or reuse the permanent `accounts.AccountProfile`;
3. resolve or create the row’s `SeasonTeam`;
4. create or update `CoachSeasonAssignment`;
5. preserve previous-season assignments;
6. avoid recreating coach accounts;
7. avoid resetting passwords for established coaches;
8. preserve current account-role and authorization rules;
9. preserve current provenance and conflict reporting.

Do not implement evaluation seasonal context or team-based permissions yet.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete Phase 3 implementation, review, documentation, or verification work remains.

PASS

All Phase 3 acceptance criteria are satisfied, verification passes, commits are pushed, and the working tree is clean.

BLOCKED

A necessary decision requires unresolved product direction, destructive migration, external infrastructure, or architecture expansion outside Phase 3.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied acceptance criterion.

Do not continue through speculative or cosmetic refactoring.

==================================================
Established Loop Workflow
=========================

Every loop must complete the full repository workflow.

Each loop must:

1. Reconcile the current committed repository state.
2. Read `AGENTS.md`, the seasonal plan, and relevant prompt archives.
3. Confirm the working tree is clean.
4. Inspect the complete coach-import workflow.
5. Identify concrete incomplete acceptance criteria or verified defects.
6. Create the next prompt archive before implementation according to `AGENTS.md`.
7. Implement only selected Phase 3 work.
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
20. Reassess every Phase 3 acceptance criterion.
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
* relevant account-management and coach-import documentation
* prompt archives for coach import, account provisioning, Seasonal Phase 1, and Seasonal Phase 2

Inspect:

* `accounts/models.py`
* `accounts/forms.py`
* `accounts/views.py`
* `accounts/urls.py`
* `accounts/services/coach_import_service.py`
* account role and provisioning services
* username and email matching services
* password services
* coach import templates
* `accounts/tests.py`
* `seasons/models.py`
* `seasons/services/team_service.py`
* `seasons/services/coach_assignment_service.py`
* current coach-import routes, preview state, and confirmation flow
* current temporary-password result handling

==================================================
Season Selection
================

Every new coach import batch or upload workflow must be associated with one selected active `Season`.

Preferred UX:

* staff selects the season on the upload page;
* only active seasons are selectable;
* current season is the default when one exists;
* staff may select another active season;
* selected season persists securely through:

  * upload;
  * preview;
  * confirmation;
  * result display.

Do not trust raw hidden form fields without server-side validation.

If the current coach import workflow has no persisted batch model, use secure server-side state consistent with current repository patterns.

Prefer adding a durable coach import batch/provenance model only if the existing workflow or repository conventions justify it.

Do not introduce unnecessary architecture merely to store one form value.

==================================================
CSV Fields
==========

Keep current required coach fields:

* first name;
* last name;
* email.

Continue supporting current optional fields such as:

* username;
* team;
* division;
* is_active;
* notes;
* source ID.

Add season-aware assignment fields:

* assignment role;
* assignment start date;
* assignment end date;
* assignment source ID;
* primary assignment flag only if safe and necessary.

Season is selected at the import level.

One coach import belongs to exactly one season.

If a CSV contains a season column:

* validate it against the selected season;
* or ignore it with clear messaging;
* never silently create a mixed-season import.

==================================================
Team And Division Requirements
==============================

A normal seasonal coach assignment requires:

* selected season;
* team;
* division;
* assignment role.

Use a clear rule for rows without team or division.

Preferred V1 behavior:

* do not create a coach account without the required seasonal assignment during a normal season-aware coach import;
* preview the row;
* report missing team/division as a row error;
* do not create blank or placeholder `SeasonTeam` records.

If repository evidence shows a legitimate organization-wide coordinator use case without a team, stop with BLOCKED rather than inventing a fake team.

==================================================
Assignment Roles
================

Use the existing controlled roles:

* Head Coach
* Assistant Coach
* Manager
* Coordinator
* Evaluator

CSV values must map through strict normalization.

Support practical aliases such as:

* head coach;
* head;
* assistant coach;
* assistant;
* manager;
* coordinator;
* evaluator.

Blank role behavior:

Recommended default:

* Assistant Coach.

Unknown role values must produce a row validation error.

Do not store arbitrary assignment-role text.

Assignment role remains separate from `AccountProfile.role`.

==================================================
Permanent Coach Account Matching
================================

Keep permanent account identity rules.

Matching priority should use:

1. normalized email;
2. supported existing username matching only when safe;
3. current conflict rules.

Required behavior:

## New Email

Create a new coach account.

* create Django `User`;
* assign permanent coach account role through existing account services;
* generate a random temporary password;
* set forced password change according to current rules;
* create seasonal assignment.

## Existing Coach Email

Reuse the existing account.

* do not create another user;
* do not reset the password;
* do not display a temporary password;
* do not re-enable or activate the account unless current import options explicitly permit it;
* create or update the seasonal assignment.

## Existing Non-Coach Email

Preserve current conflict behavior.

Do not silently change an established non-coach account into a coach.

Any role change must go through existing account-operation rules or an explicit reviewed workflow.

## Existing Inactive Coach

Reuse the account identity.

Creating a seasonal assignment must not silently activate the login account unless staff explicitly selected a supported activation option.

==================================================
Password Safety
===============

This is a critical Phase 3 requirement.

Routine seasonal reimport of an existing coach must never:

* reset the password;
* generate a new temporary password;
* set a password-change requirement merely because of the import;
* redisplay an old temporary password;
* email a new password unless an explicit password-reset workflow was separately requested.

Temporary passwords may be created and shown only for genuinely new coach accounts or an explicit supported reset action.

Preserve one-time-display behavior.

Add regression tests proving password hashes remain unchanged for reused coach accounts.

==================================================
SeasonTeam Resolution
=====================

For each valid row:

* use the selected season;
* normalize team and division through `seasons` services;
* find or create `SeasonTeam`;
* reuse equivalent normalized teams within the season;
* keep the same team name in different seasons as distinct records;
* preserve optional external team identifiers when safely available.

Preview must distinguish:

* create season team;
* reuse season team;
* invalid roster context;
* external identifier conflict.

Views and forms must not create teams directly.

==================================================
Coach Assignment Behavior
=========================

For every matched or newly created account, resolve the correct assignment action.

## Same Coach, Same Season, Same Team, Same Role

Reuse or update the existing assignment.

Do not create a duplicate active assignment.

Update only supplied assignment-specific fields.

## Same Coach, New Season

Create a new seasonal assignment.

Preserve all prior-season assignments.

Reuse the same permanent account.

## Same Coach, Same Season, Same Team, Different Role

Do not overwrite prior role history blindly.

Use one clear contract.

Recommended behavior:

* allow a separate assignment for each distinct role;
* prevent duplicate active assignment for the same user/team/role;
* preserve existing roles unless explicitly deactivated.

## Same Coach, Same Season, Different Team

Allow another assignment.

One coach may coach multiple teams in one season.

Do not deactivate or overwrite the previous assignment.

## Primary Assignment

* first active assignment in a season may become primary when no primary exists;
* existing primary assignment remains primary on routine reimport;
* additional assignments must not silently replace it;
* primary state must be derived server-side, not trusted from client input.

==================================================
Assignment Status And Dates
===========================

Support:

* `is_active`;
* optional start date;
* optional end date;
* optional assignment source identifier.

Validation:

* end date cannot precede start date;
* inactive assignment cannot be primary;
* invalid date values produce row errors;
* blank optional fields should not erase existing values during routine reimport unless explicit clearing behavior exists.

Document update semantics.

==================================================
Account Role And Privilege Separation
=====================================

Creating or updating `CoachSeasonAssignment` must not:

* set `User.is_staff`;
* set `User.is_superuser`;
* alter unrelated permissions;
* silently change `AccountProfile.role`;
* create player links;
* change account email or username unless current safe account-import behavior explicitly does so.

Permanent coach role assignment for newly created users must continue through existing account services.

Seasonal assignment roles must not become authorization grants in Phase 3.

==================================================
Preview UX
==========

Update coach-import preview to show:

* selected season;
* matched/new coach account;
* email;
* team;
* division;
* assignment role;
* season-team action;
* assignment action;
* account action;
* activation behavior;
* password behavior;
* conflicts and errors.

Use friendly labels such as:

* Create Coach Account
* Reuse Coach Account
* Create Assignment
* Update Assignment
* Reuse Assignment
* New Season Assignment
* Invalid Assignment Context
* Account Role Conflict

Clearly indicate:

* “Password unchanged” for reused accounts;
* “Temporary password will be generated” only for new accounts.

Do not expose internal IDs unnecessarily.

==================================================
Confirmation And Security
=========================

Confirmation must use server-side preview state.

Do not trust client input for:

* selected season;
* matched user;
* account role;
* password behavior;
* team action;
* assignment role;
* assignment action;
* primary assignment state.

Revalidate before writing.

Use transactional behavior consistent with the existing coach importer.

Ensure account creation/reuse, season-team resolution, assignment creation, and result reporting remain internally consistent.

If partial-row failure behavior is retained:

* report each failure clearly;
* do not leave a newly created coach account without its intended assignment unless current transaction design explicitly permits and reports it;
* prefer per-row atomicity if whole-batch atomicity would unnecessarily discard valid independent rows.

Document transaction scope.

==================================================
Result Page
===========

Report separate counts for:

* coach accounts created;
* coach accounts reused;
* season teams created;
* season teams reused;
* assignments created;
* assignments updated/reused;
* rows skipped;
* conflicts;
* errors.

Display temporary passwords only for new accounts and only once.

For reused accounts, show:

* password unchanged.

Display the selected season prominently.

==================================================
Provenance
==========

Preserve current coach-import provenance.

Each assignment should retain where practical:

* source;
* source identifier;
* relevant import metadata.

Do not duplicate full raw rows in assignment metadata if current import result/provenance already preserves them.

If the coach importer currently lacks a durable batch model, document the limitation and use existing patterns rather than expanding scope unnecessarily.

==================================================
Permissions
===========

Keep existing coach-import authorization unchanged.

Only currently authorized staff users may import coaches.

Do not grant import access based on `CoachSeasonAssignment`.

Do not introduce team-scoped permissions.

==================================================
Migration
=========

A migration is allowed only if narrowly required for durable season selection or coach-import provenance.

Do not:

* backfill coach assignments;
* create a default season;
* create coach assignments from existing profile metadata;
* reset any passwords;
* modify player import;
* modify Analytics observations.

Migration must be additive and SQLite-safe.

If no migration is needed, do not create one.

==================================================
Phase 3 Non-Goals
=================

Do not implement:

* evaluation-cycle season relationships;
* observation season/team/assignment fields;
* evaluation-context snapshots;
* coach team-based permissions;
* coach evaluation restrictions;
* player peer-evaluation scope;
* roster-management dashboards;
* coach assignment management pages outside current import/admin support;
* player season-history pages;
* parent access;
* Platform V2 summaries;
* APIs;
* JavaScript frameworks;
* notifications;
* exports;
* permanent Team model;
* removal of compatibility player fields.

==================================================
Documentation
=============

Update:

* `docs/USER_MANUAL.md`
* `docs/ARCHITECTURE.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* relevant account-management and coach-import documentation

Document:

* season selection requirement;
* supported coach and assignment fields;
* permanent coach-account reuse;
* new-season assignment behavior;
* multiple-team behavior;
* role behavior;
* password-preservation behavior;
* account activation behavior;
* selected-season visibility;
* current limitations;
* Phase 3 completion;
* next phase: evaluation seasonal context.

Do not describe evaluations or team-based permissions as season-aware.

==================================================
Required Test Coverage
======================

## Season Selection

* current season defaults;
* another active season can be selected;
* inactive season rejected;
* missing season rejected;
* selected season persists securely;
* manipulated season ID rejected.

## Team Resolution

* team created in selected season;
* normalized equivalent team reused;
* same team name in a different season is distinct;
* missing team rejected;
* missing division rejected;
* unsafe external identifier conflict handled.

## New Coach Account

* user created;
* profile created/reused correctly;
* coach role assigned through existing services;
* temporary password generated once;
* forced password-change behavior preserved;
* assignment created.

## Existing Coach Reuse

* account reused by normalized email;
* no duplicate user;
* password hash unchanged;
* no new temporary password;
* password-change flag not altered unintentionally;
* new-season assignment created;
* prior assignments preserved.

## Existing Non-Coach Conflict

* row conflicts;
* account role not silently changed;
* assignment not created unless current approved rules allow it;
* password unchanged.

## Inactive Coach

* account reused;
* assignment behavior follows contract;
* account not silently activated;
* password unchanged.

## Assignment Creation

* first assignment created;
* same assignment reimport reused or updated;
* new season creates new assignment;
* same coach may have multiple teams in one season;
* same coach may have multiple roles where allowed;
* duplicate active same user/team/role rejected;
* first active assignment becomes primary when appropriate;
* later assignments do not silently replace primary.

## Assignment Fields

* valid role aliases accepted;
* blank role defaults safely;
* invalid role rejected;
* valid dates accepted;
* invalid date range rejected;
* inactive assignment cannot be primary;
* blank optional fields preserve existing values.

## Privilege Safety

* assignment does not grant staff;
* assignment does not grant superuser;
* assignment does not alter unrelated permissions;
* assignment does not create player links;
* assignment does not silently change profile role.

## Security

* non-staff denied;
* selected season cannot be manipulated;
* matched user cannot be replaced through request data;
* role cannot be forged through hidden input;
* primary assignment cannot be forged;
* reused-account password is never exposed;
* temporary password result cannot be replayed.

## Result Reporting

* account-created count;
* account-reused count;
* team-created/reused counts;
* assignment-created/reused counts;
* conflict/error counts;
* season display;
* password result labels.

## Regression

* player import remains season-aware and unchanged;
* account operations unchanged;
* evaluation workflows unchanged;
* player-account provisioning unchanged;
* seasons tests remain passing;
* drafts and PDP remain passing.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
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

* permanent account identity versus seasonal assignment;
* account-role separation;
* password-preservation guarantees;
* temporary-password exposure;
* normalized email matching;
* duplicate assignment creation;
* primary-assignment invariants;
* team normalization;
* transaction boundaries;
* partial failures;
* provenance integrity;
* inactive-account behavior;
* hidden-field manipulation;
* SQLite migration safety;
* N+1 queries;
* stale docs;
* accidental Phase 4+ work.

Fix every verified issue before committing.

==================================================
Phase 3 Acceptance Criteria
===========================

Do not declare PASS until all criteria are satisfied.

A. Season Selection

* every new coach import requires a valid active season;
* selected season persists securely;
* current season defaults appropriately.

B. Permanent Account Identity

* new coaches receive one permanent account;
* existing coaches are reused across seasons;
* no duplicate seasonal accounts;
* existing non-coach conflicts remain safe.

C. Password Safety

* new accounts receive temporary passwords according to current policy;
* existing coach passwords remain unchanged;
* reused accounts do not receive redisplayed temporary passwords;
* password-change flags are not reset unintentionally.

D. Season Teams

* teams are created/reused within the selected season;
* equivalent normalized teams are reused;
* same team across seasons remains distinct;
* missing assignment context is rejected.

E. Coach Assignments

* valid rows create or update seasonal assignments;
* new season creates new assignment;
* prior assignments remain historical;
* multiple teams and roles are supported according to contract;
* duplicate active same user/team/role is prevented;
* primary assignment behavior is safe.

F. Privilege Separation

* assignment role remains separate from permanent account role;
* no staff/superuser escalation;
* no silent role changes;
* no player links created.

G. UX

* preview clearly shows season, account, team, role, and assignment actions;
* password behavior is explicit;
* results report accounts, teams, assignments, conflicts, and errors.

H. Migration

* migration is additive if needed;
* no default season;
* no historical assignment fabrication;
* SQLite plan reviewed.

I. Tests

* focused and full suites pass;
* password hash regressions covered;
* security manipulation cases covered;
* account and player import regressions covered.

J. Documentation

* user manual accurately explains season-aware coach import;
* Phase 3 marked complete only after PASS;
* evaluations remain documented as not season-aware;
* next phase identified as Phase 4.

K. Git

* implementation commit exists;
* prompt archive commit exists;
* both pushed;
* working tree clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally:

1. add secure season selection to coach import;
2. extend coach row parsing for assignment fields;
3. preserve permanent-account matching;
4. revise reused-account password behavior;
5. resolve SeasonTeam;
6. create/update CoachSeasonAssignment;
7. update preview/results;
8. add comprehensive tests;
9. update documentation;
10. run full verification;
11. commit, archive, push, and reassess.

If material defects remain, continue into further loops.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* satisfies an unsatisfied acceptance criterion;
* fixes a verified password, privilege, or data-integrity issue;
* prevents duplicate permanent accounts or assignments;
* strengthens transaction/provenance safety;
* adds missing regression proof;
* corrects material documentation drift.

Formatting-only work does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* registrar importing new coaches;
* registrar reimporting returning coaches;
* coach assigned to a new team next season;
* coach working with multiple teams;
* existing coach concerned about account access;
* security reviewer checking passwords and privileges;
* release engineer reviewing migrations.

Confirm:

* Phase 3 is usable for real seasonal coach import;
* permanent coach accounts are reused;
* established passwords are preserved;
* prior assignments remain historical;
* player import remains unchanged;
* evaluation context remains unchanged;
* no Phase 4+ work was introduced.

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
Implement season-aware coach import
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
* season-selection behavior;
* account-matching behavior;
* new-account behavior;
* existing-account reuse behavior;
* password-preservation behavior;
* team resolution behavior;
* assignment behavior;
* primary-assignment behavior;
* privilege-separation behavior;
* preview/result UX;
* security protections;
* tests added;
* focused verification;
* full verification;
* documentation updates;
* deferred Phase 4+ work;
* commits;
* push results;
* confirmation that the working tree is clean.

```

## Implementation Notes

Terminal state: PASS

Implementation commit: `b659177`

Summary:
- Made coach CSV import require a selected active season.
- Reused or created permanent coach accounts while creating/updating `CoachSeasonAssignment` rows.
- Preserved existing coach passwords, activation state, and account roles when reusing coach accounts.
- Updated preview/result pages and documentation for season-aware coach import behavior.
- Added regression coverage for season selection, assignment creation/update, role/date validation, duplicate handling, and existing coach reuse.

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

## Implementation Commit Diff

```text
commit b6591775511e8aa442b9257d96524b2febd29a02
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 15 22:53:59 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 15 22:53:59 2026 -0700

    Implement season-aware coach import

diff --git a/accounts/forms.py b/accounts/forms.py
index 9e77ab9..152d171 100644
--- a/accounts/forms.py
+++ b/accounts/forms.py
@@ -8,6 +8,8 @@ from accounts.services.account_operations_service import (
     BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
 )
 from players.models import Player
+from seasons.models import Season
+from seasons.services.season_service import get_current_season
 
 
 ACCOUNT_ONLY_ROLE_CHOICES = (
@@ -89,8 +91,16 @@ class BulkAccountOperationForm(forms.Form):
 
 
 class CoachImportUploadForm(forms.Form):
+    season = forms.ModelChoiceField(queryset=Season.objects.none(), help_text="Choose the season for this coach import.")
     csv_file = forms.FileField(label="Coach CSV")
 
+    def __init__(self, *args, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by("-is_current", "-starts_on", "name")
+        current = get_current_season()
+        if current and current.is_active:
+            self.fields["season"].initial = current
+
 
 class CoachImportConfirmForm(forms.Form):
     confirm = forms.BooleanField(required=True, label="Create or reuse the valid coach accounts shown in the preview.")
diff --git a/accounts/services/coach_import_service.py b/accounts/services/coach_import_service.py
index a5ba666..a587da1 100644
--- a/accounts/services/coach_import_service.py
+++ b/accounts/services/coach_import_service.py
@@ -2,6 +2,7 @@ from __future__ import annotations
 
 import csv
 from dataclasses import dataclass, field, replace
+from datetime import datetime
 from io import StringIO
 
 from django.contrib.auth import get_user_model
@@ -14,12 +15,27 @@ from accounts.services.password_service import set_random_temporary_password
 from accounts.services.permissions import can_manage_accounts
 from accounts.services.profile_service import get_or_create_account_profile, set_account_role
 from accounts.services.username_service import validate_available_username, username_for_person
+from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, Season, SeasonTeam
+from seasons.services.coach_assignment_service import create_assignment, get_primary_assignment, update_assignment
+from seasons.services.team_service import get_or_create_season_team, normalize_division_value, normalize_team_value
 
 
 User = get_user_model()
 
 REQUIRED_COLUMNS = {"first_name", "last_name", "email"}
-OPTIONAL_COLUMNS = {"username", "team", "division", "is_active", "notes", "source_id"}
+OPTIONAL_COLUMNS = {
+    "username",
+    "team",
+    "division",
+    "is_active",
+    "notes",
+    "source_id",
+    "season",
+    "assignment_role",
+    "assignment_start_date",
+    "assignment_end_date",
+    "assignment_source_id",
+}
 SUPPORTED_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS
 
 STATUS_READY = "ready"
@@ -47,6 +63,18 @@ class CoachImportRowPreview:
     is_active: bool = True
     notes: str = ""
     source_id: str = ""
+    assignment_role: str = CoachAssignmentRole.ASSISTANT_COACH
+    assignment_role_label: str = CoachAssignmentRole.ASSISTANT_COACH.label
+    assignment_start_date: str = ""
+    assignment_end_date: str = ""
+    assignment_source_id: str = ""
+    season_team_action: str = ""
+    season_team_label: str = ""
+    assignment_action: str = ""
+    assignment_label: str = ""
+    account_action: str = ""
+    account_label: str = ""
+    password_behavior: str = ""
     status: str = STATUS_READY
     messages: list[str] = field(default_factory=list)
     existing_user_id: int | None = None
@@ -65,6 +93,8 @@ class CoachImportPreview:
     rows: list[CoachImportRowPreview]
     headers: list[str]
     row_errors: list[str]
+    season_id: int | None = None
+    season_name: str = ""
 
     @property
     def rows_processed(self) -> int:
@@ -90,6 +120,22 @@ class CoachImportPreview:
     def can_confirm(self) -> bool:
         return any(row.can_commit for row in self.rows)
 
+    @property
+    def season_teams_create(self) -> int:
+        return sum(1 for row in self.rows if row.season_team_action == "create")
+
+    @property
+    def season_teams_reuse(self) -> int:
+        return sum(1 for row in self.rows if row.season_team_action == "reuse")
+
+    @property
+    def assignments_create(self) -> int:
+        return sum(1 for row in self.rows if row.assignment_action == "create")
+
+    @property
+    def assignments_update(self) -> int:
+        return sum(1 for row in self.rows if row.assignment_action in {"update", "reuse"})
+
 
 @dataclass(frozen=True)
 class CoachImportResultRow:
@@ -99,12 +145,20 @@ class CoachImportResultRow:
     user_id: int | None = None
     is_active: bool = False
     temporary_password: str = field(default="", repr=False)
+    season_name: str = ""
+    team: str = ""
+    division: str = ""
+    assignment_role_label: str = ""
+    assignment_status: str = ""
+    password_behavior: str = ""
     messages: list[str] = field(default_factory=list)
 
 
 @dataclass(frozen=True)
 class CoachImportResult:
     rows: list[CoachImportResultRow]
+    season_id: int | None = None
+    season_name: str = ""
 
     @property
     def rows_processed(self) -> int:
@@ -140,7 +194,23 @@ class CoachImportResult:
 
     @property
     def password_change_required(self) -> int:
-        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED})
+        return sum(1 for row in self.rows if row.status == RESULT_CREATED)
+
+    @property
+    def season_teams_created(self) -> int:
+        return sum(1 for row in self.rows if "season team created" in row.messages)
+
+    @property
+    def season_teams_reused(self) -> int:
+        return sum(1 for row in self.rows if "season team reused" in row.messages)
+
+    @property
+    def assignments_created(self) -> int:
+        return sum(1 for row in self.rows if row.assignment_status == "created")
+
+    @property
+    def assignments_updated(self) -> int:
+        return sum(1 for row in self.rows if row.assignment_status in {"updated", "reused"})
 
 
 def _validate_actor(actor) -> None:
@@ -159,6 +229,43 @@ def _parse_bool(value, default=True) -> bool:
     raise ValidationError("is_active must be true or false.")
 
 
+ROLE_ALIASES = {
+    "": CoachAssignmentRole.ASSISTANT_COACH,
+    "assistant": CoachAssignmentRole.ASSISTANT_COACH,
+    "assistant coach": CoachAssignmentRole.ASSISTANT_COACH,
+    "assistant_coach": CoachAssignmentRole.ASSISTANT_COACH,
+    "head": CoachAssignmentRole.HEAD_COACH,
+    "head coach": CoachAssignmentRole.HEAD_COACH,
+    "head_coach": CoachAssignmentRole.HEAD_COACH,
+    "manager": CoachAssignmentRole.MANAGER,
+    "coordinator": CoachAssignmentRole.COORDINATOR,
+    "evaluator": CoachAssignmentRole.EVALUATOR,
+}
+
+
+def _parse_assignment_role(value: str) -> str:
+    normalized = _normalize_header(value).replace("_", " ")
+    if normalized in ROLE_ALIASES:
+        return ROLE_ALIASES[normalized]
+    raise ValidationError(f"Unknown assignment role '{str(value or '').strip()}'.")
+
+
+def _assignment_role_label(value: str) -> str:
+    return CoachAssignmentRole(value).label
+
+
+def _parse_import_date(value: str):
+    cleaned = str(value or "").strip()
+    if not cleaned:
+        return None
+    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
+        try:
+            return datetime.strptime(cleaned, fmt).date()
+        except ValueError:
+            continue
+    raise ValidationError("Assignment date is invalid.")
+
+
 def _decode_csv_file(uploaded_file) -> str:
     uploaded_file.seek(0)
     raw = uploaded_file.read()
@@ -199,7 +306,42 @@ def _role_for_user(user) -> str:
     return get_or_create_account_profile(user).role
 
 
-def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
+def _season_matches(row_value: str, season: Season) -> bool:
+    normalized = str(row_value or "").strip().casefold()
+    return normalized in {season.key.casefold(), season.name.casefold()}
+
+
+def _season_team_preview(*, season: Season, team: str, division: str) -> tuple[str, str]:
+    normalized_team = normalize_team_value(team)
+    normalized_division = normalize_division_value(division)
+    existing = SeasonTeam.objects.filter(
+        season=season,
+        normalized_name=normalized_team,
+        normalized_division=normalized_division,
+    ).first()
+    if existing:
+        return "reuse", "Reuse Season Team"
+    return "create", "Create Season Team"
+
+
+def _assignment_preview(*, user, season: Season, team: str, division: str, assignment_role: str, is_active: bool) -> tuple[str, str]:
+    if not user:
+        return "create", "Create Assignment"
+    normalized_team = normalize_team_value(team)
+    normalized_division = normalize_division_value(division)
+    existing = CoachSeasonAssignment.objects.select_related("season_team").filter(
+        user=user,
+        season_team__season=season,
+        season_team__normalized_name=normalized_team,
+        season_team__normalized_division=normalized_division,
+        assignment_role=assignment_role,
+    ).first()
+    if existing:
+        return "update", "Update Assignment" if is_active else "Update Inactive Assignment"
+    return "create", "Create Assignment"
+
+
+def _preview_row(row_number: int, row: dict[str, str], season: Season) -> CoachImportRowPreview:
     messages = []
     first_name = row.get("first_name", "").strip()
     last_name = row.get("last_name", "").strip()
@@ -209,13 +351,53 @@ def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
     division = row.get("division", "").strip()
     notes = row.get("notes", "").strip()
     source_id = row.get("source_id", "").strip()
+    assignment_source_id = row.get("assignment_source_id", "").strip() or source_id
+    starts_raw = row.get("assignment_start_date", "").strip()
+    ends_raw = row.get("assignment_end_date", "").strip()
 
     try:
         is_active = _parse_bool(row.get("is_active", ""), default=True)
+        assignment_role = _parse_assignment_role(row.get("assignment_role", ""))
+        starts_on = _parse_import_date(starts_raw)
+        ends_on = _parse_import_date(ends_raw)
     except ValidationError as exc:
         return CoachImportRowPreview(row_number=row_number, status=STATUS_ERROR, messages=list(exc.messages))
+    if starts_on and ends_on and ends_on < starts_on:
+        return CoachImportRowPreview(row_number=row_number, status=STATUS_ERROR, messages=["Assignment end date cannot be before start date."])
 
-    missing_fields = [label for label, value in [("first_name", first_name), ("last_name", last_name), ("email", email)] if not value]
+    season_value = row.get("season", "").strip()
+    if season_value and not _season_matches(season_value, season):
+        return CoachImportRowPreview(
+            row_number=row_number,
+            first_name=first_name,
+            last_name=last_name,
+            email=email,
+            username=explicit_username,
+            team=team,
+            division=division,
+            is_active=is_active,
+            notes=notes,
+            source_id=source_id,
+            assignment_role=assignment_role,
+            assignment_role_label=_assignment_role_label(assignment_role),
+            assignment_start_date=starts_raw,
+            assignment_end_date=ends_raw,
+            assignment_source_id=assignment_source_id,
+            status=STATUS_ERROR,
+            messages=["CSV season does not match the selected import season."],
+        )
+
+    missing_fields = [
+        label
+        for label, value in [
+            ("first_name", first_name),
+            ("last_name", last_name),
+            ("email", email),
+            ("team", team),
+            ("division", division),
+        ]
+        if not value
+    ]
     if missing_fields:
         return CoachImportRowPreview(
             row_number=row_number,
@@ -228,14 +410,28 @@ def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
             is_active=is_active,
             notes=notes,
             source_id=source_id,
+            assignment_role=assignment_role,
+            assignment_role_label=_assignment_role_label(assignment_role),
+            assignment_start_date=starts_raw,
+            assignment_end_date=ends_raw,
+            assignment_source_id=assignment_source_id,
             status=STATUS_ERROR,
             messages=[f"Missing required field(s): {', '.join(missing_fields)}."],
         )
 
     existing_email_user = find_existing_email_user(email)
+    season_team_action, season_team_label = _season_team_preview(season=season, team=team, division=division)
     if existing_email_user:
         existing_role = _role_for_user(existing_email_user)
         if existing_role == AccountRole.COACH:
+            assignment_action, assignment_label = _assignment_preview(
+                user=existing_email_user,
+                season=season,
+                team=team,
+                division=division,
+                assignment_role=assignment_role,
+                is_active=is_active,
+            )
             return CoachImportRowPreview(
                 row_number=row_number,
                 first_name=first_name,
@@ -247,8 +443,20 @@ def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
                 is_active=is_active,
                 notes=notes,
                 source_id=source_id,
+                assignment_role=assignment_role,
+                assignment_role_label=_assignment_role_label(assignment_role),
+                assignment_start_date=starts_raw,
+                assignment_end_date=ends_raw,
+                assignment_source_id=assignment_source_id,
+                season_team_action=season_team_action,
+                season_team_label=season_team_label,
+                assignment_action=assignment_action,
+                assignment_label=assignment_label,
+                account_action="reuse",
+                account_label="Reuse Coach Account",
+                password_behavior="Password unchanged",
                 status=STATUS_REUSE,
-                messages=["Existing coach account will be reused."],
+                messages=["Existing coach account will be reused.", "Password unchanged."],
                 existing_user_id=existing_email_user.id,
             )
         return CoachImportRowPreview(
@@ -262,6 +470,16 @@ def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
             is_active=is_active,
             notes=notes,
             source_id=source_id,
+            assignment_role=assignment_role,
+            assignment_role_label=_assignment_role_label(assignment_role),
+            assignment_start_date=starts_raw,
+            assignment_end_date=ends_raw,
+            assignment_source_id=assignment_source_id,
+            season_team_action=season_team_action,
+            season_team_label=season_team_label,
+            account_action="conflict",
+            account_label="Account Role Conflict",
+            password_behavior="Password unchanged",
             status=STATUS_CONFLICT,
             messages=["Email belongs to an existing non-coach account."],
             existing_user_id=existing_email_user.id,
@@ -282,6 +500,13 @@ def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
             is_active=is_active,
             notes=notes,
             source_id=source_id,
+            assignment_role=assignment_role,
+            assignment_role_label=_assignment_role_label(assignment_role),
+            assignment_start_date=starts_raw,
+            assignment_end_date=ends_raw,
+            assignment_source_id=assignment_source_id,
+            season_team_action=season_team_action,
+            season_team_label=season_team_label,
             status=STATUS_CONFLICT,
             messages=list(exc.messages),
         )
@@ -298,25 +523,41 @@ def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
         is_active=is_active,
         notes=notes,
         source_id=source_id,
+        assignment_role=assignment_role,
+        assignment_role_label=_assignment_role_label(assignment_role),
+        assignment_start_date=starts_raw,
+        assignment_end_date=ends_raw,
+        assignment_source_id=assignment_source_id,
+        season_team_action=season_team_action,
+        season_team_label=season_team_label,
+        assignment_action="create",
+        assignment_label="Create Assignment",
+        account_action="create",
+        account_label="Create Coach Account",
+        password_behavior="Temporary password will be generated",
         status=STATUS_READY,
         messages=messages,
     )
 
 
-def preview_coach_import(csv_text: str) -> CoachImportPreview:
+def preview_coach_import(csv_text: str, season: Season | None = None) -> CoachImportPreview:
     """Return a non-persistent preview for a coach CSV import."""
+    if season is None:
+        return CoachImportPreview(rows=[], headers=[], row_errors=["Select an active season for this coach import."])
+    if not season.is_active:
+        return CoachImportPreview(rows=[], headers=[], row_errors=["Select an active season for this coach import."])
     try:
         headers, rows = _read_csv(csv_text)
     except ValidationError as exc:
-        return CoachImportPreview(rows=[], headers=[], row_errors=list(exc.messages))
+        return CoachImportPreview(rows=[], headers=[], row_errors=list(exc.messages), season_id=season.id, season_name=season.name)
 
     preview_rows = []
     seen_emails = set()
-    seen_usernames = set()
+    username_owner_email = {}
     for index, row in enumerate(rows, start=2):
-        preview_row = _preview_row(index, row)
+        preview_row = _preview_row(index, row, season)
         if preview_row.email:
-            if preview_row.email in seen_emails:
+            if preview_row.email in seen_emails and preview_row.status == STATUS_CONFLICT:
                 preview_row = replace(
                     preview_row,
                     status=STATUS_CONFLICT,
@@ -325,20 +566,21 @@ def preview_coach_import(csv_text: str) -> CoachImportPreview:
             seen_emails.add(preview_row.email)
         final_username = preview_row.final_username
         if preview_row.status == STATUS_READY and final_username:
-            if final_username in seen_usernames:
+            owner_email = username_owner_email.get(final_username)
+            if owner_email and owner_email != preview_row.email:
                 preview_row = replace(
                     preview_row,
                     status=STATUS_CONFLICT,
                     messages=[*preview_row.messages, "Username appears more than once in this CSV."],
                 )
-            seen_usernames.add(final_username)
+            username_owner_email[final_username] = preview_row.email
         preview_rows.append(preview_row)
-    return CoachImportPreview(rows=preview_rows, headers=headers, row_errors=[])
+    return CoachImportPreview(rows=preview_rows, headers=headers, row_errors=[], season_id=season.id, season_name=season.name)
 
 
-def preview_coach_import_file(uploaded_file) -> CoachImportPreview:
+def preview_coach_import_file(uploaded_file, season: Season | None = None) -> CoachImportPreview:
     """Read an uploaded CSV file and return a coach import preview."""
-    return preview_coach_import(_decode_csv_file(uploaded_file))
+    return preview_coach_import(_decode_csv_file(uploaded_file), season=season)
 
 
 def _metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
@@ -349,6 +591,7 @@ def _metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
             "division": row.division,
             "notes": row.notes,
             "source_id": row.source_id,
+            "assignment_role": row.assignment_role,
             "source": "coach_roster",
         }.items()
         if value
@@ -360,19 +603,64 @@ def _profile_metadata(profile) -> dict:
 
 
 @transaction.atomic
-def _reuse_existing_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
+def _commit_assignment(user, row: CoachImportRowPreview, season: Season) -> tuple[str, bool]:
+    season_team, team_created = get_or_create_season_team(
+        season=season,
+        name=row.team,
+        division=row.division,
+        metadata={"source": "coach_roster"},
+    )
+    assignment = CoachSeasonAssignment.objects.select_for_update().filter(
+        user=user,
+        season_team=season_team,
+        assignment_role=row.assignment_role,
+    ).first()
+    starts_on = _parse_import_date(row.assignment_start_date)
+    ends_on = _parse_import_date(row.assignment_end_date)
+    updates = {"is_active": row.is_active}
+    if not row.is_active:
+        updates["is_primary"] = False
+    if starts_on:
+        updates["starts_on"] = starts_on
+    if ends_on:
+        updates["ends_on"] = ends_on
+    if row.assignment_source_id:
+        updates["source_identifier"] = row.assignment_source_id
+    updates["source"] = "coach_roster"
+    updates["metadata"] = {key: value for key, value in {"notes": row.notes, "source_id": row.source_id}.items() if value}
+    if assignment:
+        update_assignment(assignment, **updates)
+        return "updated", team_created
+    is_primary = row.is_active and get_primary_assignment(user, season) is None
+    create_assignment(
+        user=user,
+        season_team=season_team,
+        assignment_role=row.assignment_role,
+        is_primary=is_primary,
+        is_active=row.is_active,
+        starts_on=starts_on,
+        ends_on=ends_on,
+        source="coach_roster",
+        source_identifier=row.assignment_source_id,
+        metadata={key: value for key, value in {"notes": row.notes, "source_id": row.source_id}.items() if value},
+    )
+    return "created", team_created
+
+
+@transaction.atomic
+def _reuse_existing_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResultRow:
     user = User.objects.select_for_update().select_related("account_profile").get(pk=row.existing_user_id)
-    profile = set_account_role(user, AccountRole.COACH)
+    profile = get_or_create_account_profile(user)
+    if profile.role != AccountRole.COACH:
+        raise ValidationError("Existing account is not a coach.")
     metadata = {**_profile_metadata(profile), **_metadata_for_row(row)}
     profile.metadata = metadata
-    profile.must_change_password = True
-    profile.save(update_fields=["metadata", "must_change_password", "updated_at"])
+    profile.save(update_fields=["metadata", "updated_at"])
     user.first_name = user.first_name or row.first_name
     user.last_name = user.last_name or row.last_name
     user.email = user.email or row.email
-    user.is_active = row.is_active
-    user.save(update_fields=["first_name", "last_name", "email", "is_active"])
-    temporary_password = set_random_temporary_password(user)
+    user.save(update_fields=["first_name", "last_name", "email"])
+    assignment_action, team_created = _commit_assignment(user, row, season)
     status_message = "inactive" if not user.is_active else "active"
     return CoachImportResultRow(
         row_number=row.row_number,
@@ -380,13 +668,23 @@ def _reuse_existing_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
         username=user.username,
         user_id=user.id,
         is_active=user.is_active,
-        temporary_password=temporary_password,
-        messages=[status_message],
+        season_name=season.name,
+        team=row.team,
+        division=row.division,
+        assignment_role_label=row.assignment_role_label,
+        assignment_status=assignment_action,
+        password_behavior="Password unchanged",
+        messages=[
+            status_message,
+            "password unchanged",
+            "season team created" if team_created else "season team reused",
+            f"assignment {assignment_action}",
+        ],
     )
 
 
 @transaction.atomic
-def _create_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
+def _create_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResultRow:
     user = User.objects.create(
         username=row.final_username,
         first_name=row.first_name,
@@ -399,6 +697,7 @@ def _create_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
     profile.must_change_password = True
     profile.metadata = {**_profile_metadata(profile), **_metadata_for_row(row)}
     profile.save(update_fields=["must_change_password", "metadata", "updated_at"])
+    assignment_action, team_created = _commit_assignment(user, row, season)
     status_message = "inactive" if not user.is_active else "active"
     return CoachImportResultRow(
         row_number=row.row_number,
@@ -407,14 +706,25 @@ def _create_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
         user_id=user.id,
         is_active=user.is_active,
         temporary_password=temporary_password,
-        messages=[status_message],
+        season_name=season.name,
+        team=row.team,
+        division=row.division,
+        assignment_role_label=row.assignment_role_label,
+        assignment_status=assignment_action,
+        password_behavior="Temporary password generated",
+        messages=[
+            status_message,
+            "temporary password generated",
+            "season team created" if team_created else "season team reused",
+            f"assignment {assignment_action}",
+        ],
     )
 
 
-def commit_coach_import(actor, csv_text: str) -> CoachImportResult:
+def commit_coach_import(actor, csv_text: str, season: Season | None = None) -> CoachImportResult:
     """Create or reuse coach accounts from CSV text and return one-time passwords."""
     _validate_actor(actor)
-    preview = preview_coach_import(csv_text)
+    preview = preview_coach_import(csv_text, season=season)
     result_rows = []
 
     for error in preview.row_errors:
@@ -423,12 +733,31 @@ def commit_coach_import(actor, csv_text: str) -> CoachImportResult:
     for row in preview.rows:
         if row.status == STATUS_READY:
             try:
-                result_rows.append(_create_coach(row))
+                existing_user = find_existing_email_user(row.email)
+                if existing_user and _role_for_user(existing_user) == AccountRole.COACH:
+                    result_rows.append(_reuse_existing_coach(replace(row, existing_user_id=existing_user.id), season))
+                elif existing_user:
+                    result_rows.append(
+                        CoachImportResultRow(
+                            row_number=row.row_number,
+                            status=RESULT_CONFLICT,
+                            username=row.final_username,
+                            user_id=existing_user.id,
+                            season_name=season.name,
+                            team=row.team,
+                            division=row.division,
+                            assignment_role_label=row.assignment_role_label,
+                            password_behavior="Password unchanged",
+                            messages=["Email belongs to an existing non-coach account."],
+                        )
+                    )
+                else:
+                    result_rows.append(_create_coach(row, season))
             except ValidationError as exc:
                 result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
         elif row.status == STATUS_REUSE:
             try:
-                result_rows.append(_reuse_existing_coach(row))
+                result_rows.append(_reuse_existing_coach(row, season))
             except ValidationError as exc:
                 result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
         elif row.status == STATUS_CONFLICT:
@@ -438,6 +767,11 @@ def commit_coach_import(actor, csv_text: str) -> CoachImportResult:
                     status=RESULT_CONFLICT,
                     username=row.final_username,
                     user_id=row.existing_user_id,
+                    season_name=season.name if season else "",
+                    team=row.team,
+                    division=row.division,
+                    assignment_role_label=row.assignment_role_label,
+                    password_behavior="Password unchanged",
                     messages=row.messages,
                 )
             )
@@ -447,8 +781,12 @@ def commit_coach_import(actor, csv_text: str) -> CoachImportResult:
                     row_number=row.row_number,
                     status=RESULT_ERROR,
                     username=row.final_username,
+                    season_name=season.name if season else "",
+                    team=row.team,
+                    division=row.division,
+                    assignment_role_label=row.assignment_role_label,
                     messages=row.messages,
                 )
             )
 
-    return CoachImportResult(rows=result_rows)
+    return CoachImportResult(rows=result_rows, season_id=season.id if season else None, season_name=season.name if season else "")
diff --git a/accounts/templates/accounts/coach_import_list.html b/accounts/templates/accounts/coach_import_list.html
index 0a5c3ed..0cfb499 100644
--- a/accounts/templates/accounts/coach_import_list.html
+++ b/accounts/templates/accounts/coach_import_list.html
@@ -8,7 +8,8 @@
     <article class="pdp-card">
         <h2>Coach CSV</h2>
         <p>Required columns: first_name, last_name, email.</p>
-        <p>Optional columns: username, team, division, is_active, notes, source_id.</p>
+        <p>Season is selected during upload. Required assignment columns: team and division.</p>
+        <p>Optional columns: username, is_active, notes, source_id, assignment_role, assignment_start_date, assignment_end_date, assignment_source_id.</p>
         <div class="pdp-actions">
             <a class="button button--primary" href="{% url 'accounts:coach-import-new' %}">Upload Coach CSV</a>
             <a class="button button--ghost" href="{% url 'accounts:operations-dashboard' %}">Account Operations</a>
diff --git a/accounts/templates/accounts/coach_import_preview.html b/accounts/templates/accounts/coach_import_preview.html
index eb0121b..1483b81 100644
--- a/accounts/templates/accounts/coach_import_preview.html
+++ b/accounts/templates/accounts/coach_import_preview.html
@@ -8,11 +8,16 @@
     <article class="pdp-card">
         <h2>Summary</h2>
         <dl class="pdp-definition-list">
+            <dt>Season</dt><dd>{{ preview.season_name|default:"-" }}</dd>
             <dt>Rows processed</dt><dd>{{ preview.rows_processed }}</dd>
             <dt>Ready to create</dt><dd>{{ preview.ready_count }}</dd>
             <dt>Existing coaches to reuse</dt><dd>{{ preview.reuse_count }}</dd>
             <dt>Conflicts</dt><dd>{{ preview.conflict_count }}</dd>
             <dt>Errors</dt><dd>{{ preview.error_count }}</dd>
+            <dt>Season teams to create</dt><dd>{{ preview.season_teams_create }}</dd>
+            <dt>Season teams to reuse</dt><dd>{{ preview.season_teams_reuse }}</dd>
+            <dt>Assignments to create</dt><dd>{{ preview.assignments_create }}</dd>
+            <dt>Assignments to update/reuse</dt><dd>{{ preview.assignments_update }}</dd>
         </dl>
         {% if preview.row_errors %}
             <ul>
@@ -33,6 +38,11 @@
                         <th>Name</th>
                         <th>Email</th>
                         <th>Username</th>
+                        <th>Team</th>
+                        <th>Role</th>
+                        <th>Account</th>
+                        <th>Assignment</th>
+                        <th>Password</th>
                         <th>Active</th>
                         <th>Status</th>
                         <th>Messages</th>
@@ -45,6 +55,11 @@
                             <td>{{ row.first_name }} {{ row.last_name }}</td>
                             <td>{{ row.email }}</td>
                             <td>{{ row.final_username|default:"-" }}</td>
+                            <td>{{ row.division }} {{ row.team }}</td>
+                            <td>{{ row.assignment_role_label }}</td>
+                            <td>{{ row.account_label|default:"-" }}</td>
+                            <td>{{ row.assignment_label|default:"-" }}</td>
+                            <td>{{ row.password_behavior|default:"-" }}</td>
                             <td>{{ row.is_active|yesno:"Yes,No" }}</td>
                             <td>{{ row.status }}</td>
                             <td>
@@ -56,7 +71,7 @@
                             </td>
                         </tr>
                     {% empty %}
-                        <tr><td colspan="7">No rows found.</td></tr>
+                        <tr><td colspan="12">No rows found.</td></tr>
                     {% endfor %}
                 </tbody>
             </table>
@@ -65,8 +80,8 @@
 
     <article class="pdp-card">
         <h2>Confirm</h2>
-        <p>Only rows marked ready or reuse will be processed. Rows marked reuse will use the existing coach account and reset that coach's temporary password. The coach must change the password on next login.</p>
-        <p>Temporary passwords are shown once on the result page.</p>
+        <p>Only rows marked ready or reuse will be processed. Reused coach accounts keep their existing passwords unchanged.</p>
+        <p>Temporary passwords are generated and shown once only for newly created coach accounts.</p>
         <form method="post" action="{% url 'accounts:coach-import-confirm' %}" class="pdp-form">
             {% csrf_token %}
             <label>
diff --git a/accounts/templates/accounts/coach_import_result.html b/accounts/templates/accounts/coach_import_result.html
index cef292e..823da42 100644
--- a/accounts/templates/accounts/coach_import_result.html
+++ b/accounts/templates/accounts/coach_import_result.html
@@ -8,9 +8,14 @@
     <article class="pdp-card">
         <h2>Summary</h2>
         <dl class="pdp-definition-list">
+            <dt>Season</dt><dd>{{ result.season_name|default:"-" }}</dd>
             <dt>Rows processed</dt><dd>{{ result.rows_processed }}</dd>
             <dt>Users created</dt><dd>{{ result.users_created }}</dd>
             <dt>Existing coaches reused</dt><dd>{{ result.existing_coaches_reused }}</dd>
+            <dt>Season teams created</dt><dd>{{ result.season_teams_created }}</dd>
+            <dt>Season teams reused</dt><dd>{{ result.season_teams_reused }}</dd>
+            <dt>Assignments created</dt><dd>{{ result.assignments_created }}</dd>
+            <dt>Assignments updated/reused</dt><dd>{{ result.assignments_updated }}</dd>
             <dt>Conflicts</dt><dd>{{ result.conflicts }}</dd>
             <dt>Errors</dt><dd>{{ result.errors }}</dd>
             <dt>Skipped rows</dt><dd>{{ result.skipped_rows }}</dd>
@@ -29,6 +34,10 @@
                         <th>Row</th>
                         <th>Status</th>
                         <th>Username</th>
+                        <th>Team</th>
+                        <th>Role</th>
+                        <th>Assignment</th>
+                        <th>Password</th>
                         <th>Active</th>
                         <th>Temporary password</th>
                         <th>Messages</th>
@@ -46,6 +55,10 @@
                                     {{ row.username|default:"-" }}
                                 {% endif %}
                             </td>
+                            <td>{{ row.division }} {{ row.team }}</td>
+                            <td>{{ row.assignment_role_label|default:"-" }}</td>
+                            <td>{{ row.assignment_status|default:"-" }}</td>
+                            <td>{{ row.password_behavior|default:"-" }}</td>
                             <td>{% if row.user_id %}{{ row.is_active|yesno:"Yes,No" }}{% else %}-{% endif %}</td>
                             <td><strong>{{ row.temporary_password|default:"-" }}</strong></td>
                             <td>
@@ -57,7 +70,7 @@
                             </td>
                         </tr>
                     {% empty %}
-                        <tr><td colspan="6">No rows processed.</td></tr>
+                        <tr><td colspan="10">No rows processed.</td></tr>
                     {% endfor %}
                 </tbody>
             </table>
diff --git a/accounts/templates/accounts/coach_import_upload.html b/accounts/templates/accounts/coach_import_upload.html
index 7874464..7d1b44b 100644
--- a/accounts/templates/accounts/coach_import_upload.html
+++ b/accounts/templates/accounts/coach_import_upload.html
@@ -10,6 +10,11 @@
         <form method="post" enctype="multipart/form-data" class="pdp-form">
             {% csrf_token %}
             {{ form.non_field_errors }}
+            <label>
+                Season
+                {{ form.season }}
+                {{ form.season.errors }}
+            </label>
             <label>
                 Coach CSV
                 {{ form.csv_file }}
diff --git a/accounts/tests.py b/accounts/tests.py
index c4d16a8..ad535e4 100644
--- a/accounts/tests.py
+++ b/accounts/tests.py
@@ -97,6 +97,8 @@ from accounts.services.username_service import (
 )
 from analytics.services.permissions import can_submit_coach_assessment
 from players.models import Player, PlayerImportBatch
+from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, SeasonTeam
+from seasons.services.season_service import create_season
 
 
 User = get_user_model()
@@ -1635,14 +1637,17 @@ class AccountAuthViewTests(TestCase):
 class CoachImportServiceTests(TestCase):
     def setUp(self):
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        self.next_season = create_season(key="2027-spring", name="2027 Spring")
 
     def csv_text(self, rows):
-        return "first_name,last_name,email,username,team,division,is_active,notes,source_id\n" + "\n".join(rows)
+        return "first_name,last_name,email,username,team,division,is_active,notes,source_id,assignment_role,assignment_start_date,assignment_end_date,assignment_source_id\n" + "\n".join(rows)
 
     def test_valid_csv_creates_active_coach_with_one_time_password(self):
         result = commit_coach_import(
             self.staff,
             self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,Lead coach,C001"]),
+            season=self.season,
         )
 
         user = User.objects.get(email="casey@example.com")
@@ -1666,11 +1671,78 @@ class CoachImportServiceTests(TestCase):
         self.assertEqual(result.active_accounts, 1)
         self.assertEqual(result.inactive_accounts, 0)
         self.assertEqual(result.password_change_required, 1)
+        assignment = CoachSeasonAssignment.objects.select_related("season_team").get(user=user)
+        self.assertEqual(assignment.season_team.season, self.season)
+        self.assertEqual(assignment.season_team.name, "Reds")
+        self.assertEqual(assignment.assignment_role, CoachAssignmentRole.ASSISTANT_COACH)
+        self.assertTrue(assignment.is_primary)
+        self.assertEqual(result.season_teams_created, 1)
+        self.assertEqual(result.assignments_created, 1)
+
+    def test_coach_import_requires_active_season(self):
+        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
+
+        preview = preview_coach_import(self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]))
+        inactive_preview = preview_coach_import(
+            self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]),
+            season=inactive,
+        )
+
+        self.assertEqual(preview.error_count, 1)
+        self.assertIn("Select an active season", preview.row_errors[0])
+        self.assertEqual(inactive_preview.error_count, 1)
+        self.assertIn("Select an active season", inactive_preview.row_errors[0])
+
+    def test_assignment_role_aliases_and_dates_are_persisted(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Head,Coach,head@example.com,,Reds,13U,true,,C001,head,2026-04-01,2026-08-31,A001"]),
+            season=self.season,
+        )
+
+        assignment = CoachSeasonAssignment.objects.get(user__email="head@example.com")
+        self.assertEqual(result.rows[0].assignment_role_label, "Head Coach")
+        self.assertEqual(assignment.assignment_role, CoachAssignmentRole.HEAD_COACH)
+        self.assertEqual(assignment.starts_on.isoformat(), "2026-04-01")
+        self.assertEqual(assignment.ends_on.isoformat(), "2026-08-31")
+        self.assertEqual(assignment.source_identifier, "a001")
+
+    def test_invalid_assignment_role_and_date_range_are_row_errors(self):
+        preview = preview_coach_import(
+            self.csv_text(
+                [
+                    "Bad,Role,bad.role@example.com,,Reds,13U,true,,C001,owner,,,",
+                    "Bad,Dates,bad.dates@example.com,,Reds,13U,true,,C002,assistant,2026-08-31,2026-04-01,",
+                ]
+            ),
+            season=self.season,
+        )
+
+        self.assertEqual(preview.error_count, 2)
+        self.assertIn("Unknown assignment role", preview.rows[0].messages[0])
+        self.assertIn("end date", preview.rows[1].messages[0])
+
+    def test_missing_team_or_division_blocks_row(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(
+                [
+                    "No,Team,no.team@example.com,,,13U,true,,",
+                    "No,Division,no.division@example.com,,Reds,,true,,",
+                ]
+            ),
+            season=self.season,
+        )
+
+        self.assertEqual(result.errors, 2)
+        self.assertFalse(User.objects.filter(email__in=["no.team@example.com", "no.division@example.com"]).exists())
+        self.assertFalse(SeasonTeam.objects.exists())
 
     def test_imported_coach_can_be_inactive(self):
         result = commit_coach_import(
             self.staff,
-            self.csv_text(["Inactive,Coach,inactive.coach@example.com,,,,false,,"]),
+            self.csv_text(["Inactive,Coach,inactive.coach@example.com,,Reds,13U,false,,"]),
+            season=self.season,
         )
 
         user = User.objects.get(username="inactive.coach")
@@ -1681,7 +1753,8 @@ class CoachImportServiceTests(TestCase):
     def test_explicit_username_is_normalized_and_validated(self):
         result = commit_coach_import(
             self.staff,
-            self.csv_text(["User,Name,user.name@example.com,Explicit.User,,,,,"]),
+            self.csv_text(["User,Name,user.name@example.com,Explicit.User,Reds,13U,true,,"]),
+            season=self.season,
         )
 
         self.assertEqual(result.rows[0].username, "explicit.user")
@@ -1692,7 +1765,8 @@ class CoachImportServiceTests(TestCase):
 
         result = commit_coach_import(
             self.staff,
-            self.csv_text(["Casey,Coach,casey2@example.com,,,,,,"]),
+            self.csv_text(["Casey,Coach,casey2@example.com,,Reds,13U,true,,"]),
+            season=self.season,
         )
 
         self.assertEqual(result.rows[0].username, "casey.coach2")
@@ -1705,17 +1779,112 @@ class CoachImportServiceTests(TestCase):
 
         result = commit_coach_import(
             self.staff,
-            self.csv_text(["Existing,Coach,COACH@example.com,,,,,,"]),
+            self.csv_text(["Existing,Coach,COACH@example.com,,Reds,13U,true,,"]),
+            season=self.season,
         )
 
         existing.refresh_from_db()
+        existing.account_profile.refresh_from_db()
         self.assertEqual(result.rows[0].status, RESULT_REUSED)
         self.assertEqual(result.existing_coaches_reused, 1)
         self.assertEqual(User.objects.filter(email__iexact="coach@example.com").count(), 1)
-        self.assertTrue(existing.account_profile.must_change_password)
-        self.assertTrue(existing.check_password(result.rows[0].temporary_password))
-        self.assertNotEqual(existing.password, original_password_hash)
+        self.assertFalse(existing.account_profile.must_change_password)
+        self.assertFalse(result.rows[0].temporary_password)
+        self.assertEqual(existing.password, original_password_hash)
         self.assertEqual(existing.account_profile.role, AccountRole.COACH)
+        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)
+
+    def test_existing_inactive_coach_is_not_activated_or_reset(self):
+        existing = User.objects.create_user(username="inactive.existing", email="inactive-existing@example.com", password="oldpass", is_active=False)
+        profile = set_account_role(existing, AccountRole.COACH)
+        profile.must_change_password = False
+        profile.save(update_fields=["must_change_password", "updated_at"])
+        original_password_hash = existing.password
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Inactive,Existing,inactive-existing@example.com,,Reds,13U,true,,"]),
+            season=self.season,
+        )
+
+        existing.refresh_from_db()
+        profile.refresh_from_db()
+        self.assertEqual(result.rows[0].status, RESULT_REUSED)
+        self.assertFalse(existing.is_active)
+        self.assertEqual(existing.password, original_password_hash)
+        self.assertFalse(result.rows[0].temporary_password)
+        self.assertFalse(profile.must_change_password)
+        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)
+
+    def test_reimport_same_assignment_updates_without_duplicate_or_password_reset(self):
+        first = commit_coach_import(
+            self.staff,
+            self.csv_text(["Return,Coach,return@example.com,,Reds,13U,true,,C001,assistant,,,A001"]),
+            season=self.season,
+        )
+        user = User.objects.get(email="return@example.com")
+        original_password_hash = user.password
+
+        second = commit_coach_import(
+            self.staff,
+            self.csv_text(["Return,Coach,return@example.com,,Reds,13U,true,Updated notes,C001,assistant,2026-04-01,,A001"]),
+            season=self.season,
+        )
+
+        user.refresh_from_db()
+        assignment = CoachSeasonAssignment.objects.get(user=user)
+        self.assertEqual(first.users_created, 1)
+        self.assertEqual(second.existing_coaches_reused, 1)
+        self.assertEqual(second.assignments_updated, 1)
+        self.assertEqual(CoachSeasonAssignment.objects.filter(user=user).count(), 1)
+        self.assertEqual(assignment.starts_on.isoformat(), "2026-04-01")
+        self.assertEqual(user.password, original_password_hash)
+        self.assertFalse(second.rows[0].temporary_password)
+
+    def test_new_season_creates_new_assignment_and_distinct_team(self):
+        commit_coach_import(
+            self.staff,
+            self.csv_text(["Season,Coach,season@example.com,,Reds,13U,true,,"]),
+            season=self.season,
+        )
+        user = User.objects.get(email="season@example.com")
+
+        commit_coach_import(
+            self.staff,
+            self.csv_text(["Season,Coach,season@example.com,,Reds,13U,true,,"]),
+            season=self.next_season,
+        )
+
+        self.assertEqual(CoachSeasonAssignment.objects.filter(user=user).count(), 2)
+        self.assertEqual(SeasonTeam.objects.filter(name="Reds", division="13U").count(), 2)
+
+    def test_same_coach_can_have_multiple_teams_and_roles_without_replacing_primary(self):
+        commit_coach_import(
+            self.staff,
+            self.csv_text(
+                [
+                    "Multi,Coach,multi@example.com,,Reds,13U,true,,C001,head,,,",
+                    "Multi,Coach,multi@example.com,,Blues,13U,true,,C002,assistant,,,",
+                    "Multi,Coach,multi@example.com,,Reds,13U,true,,C003,evaluator,,,",
+                ]
+            ),
+            season=self.season,
+        )
+        user = User.objects.get(email="multi@example.com")
+        assignments = CoachSeasonAssignment.objects.filter(user=user, season_team__season=self.season)
+
+        self.assertEqual(assignments.count(), 3)
+        self.assertEqual(assignments.filter(is_primary=True).count(), 1)
+        self.assertEqual(assignments.get(is_primary=True).assignment_role, CoachAssignmentRole.HEAD_COACH)
+
+    def test_csv_season_mismatch_is_rejected(self):
+        preview = preview_coach_import(
+            "first_name,last_name,email,team,division,season\nMismatch,Coach,mismatch@example.com,Reds,13U,2027 Spring\n",
+            season=self.season,
+        )
+
+        self.assertEqual(preview.rows[0].status, "error")
+        self.assertIn("season does not match", preview.rows[0].messages[0])
 
     def test_duplicate_email_with_non_coach_conflicts(self):
         existing = User.objects.create_user(username="player.user", email="shared@example.com")
@@ -1723,40 +1892,46 @@ class CoachImportServiceTests(TestCase):
 
         result = commit_coach_import(
             self.staff,
-            self.csv_text(["Shared,Coach,shared@example.com,,,,,,"]),
+            self.csv_text(["Shared,Coach,shared@example.com,,Reds,13U,true,,"]),
+            season=self.season,
         )
 
         self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
         self.assertEqual(result.conflicts, 1)
         self.assertEqual(User.objects.count(), 2)
+        self.assertFalse(CoachSeasonAssignment.objects.exists())
 
     def test_explicit_duplicate_username_conflicts(self):
         User.objects.create_user(username="taken.name")
 
         result = commit_coach_import(
             self.staff,
-            self.csv_text(["Taken,Name,taken@example.com,taken.name,,,,,"]),
+            self.csv_text(["Taken,Name,taken@example.com,taken.name,Reds,13U,true,,"]),
+            season=self.season,
         )
 
         self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
         self.assertFalse(User.objects.filter(email="taken@example.com").exists())
 
-    def test_duplicate_email_and_username_within_same_csv_conflict(self):
+    def test_duplicate_email_reuses_created_coach_but_duplicate_username_conflicts(self):
         result = commit_coach_import(
             self.staff,
             self.csv_text(
                 [
-                    "First,Coach,first@example.com,same.username,,,,,",
-                    "Second,Coach,first@example.com,other.username,,,,,",
-                    "Third,Coach,third@example.com,same.username,,,,,",
+                    "First,Coach,first@example.com,same.username,Reds,13U,true,,",
+                    "Second,Coach,first@example.com,other.username,Reds,13U,true,,",
+                    "Third,Coach,third@example.com,same.username,Reds,13U,true,,",
                 ]
             ),
+            season=self.season,
         )
 
         self.assertEqual(result.users_created, 1)
-        self.assertEqual(result.conflicts, 2)
+        self.assertEqual(result.existing_coaches_reused, 1)
+        self.assertEqual(result.conflicts, 1)
         self.assertTrue(User.objects.filter(email="first@example.com").exists())
         self.assertFalse(User.objects.filter(email="third@example.com").exists())
+        self.assertEqual(CoachSeasonAssignment.objects.filter(user__email="first@example.com").count(), 1)
 
     def test_blank_csv_fields_do_not_wipe_existing_metadata(self):
         existing = User.objects.create_user(username="metadata.coach", email="metadata@example.com")
@@ -1766,7 +1941,8 @@ class CoachImportServiceTests(TestCase):
 
         result = commit_coach_import(
             self.staff,
-            self.csv_text(["Metadata,Coach,metadata@example.com,,,,,,"]),
+            self.csv_text(["Metadata,Coach,metadata@example.com,,Reds,13U,true,,"]),
+            season=self.season,
         )
 
         profile.refresh_from_db()
@@ -1775,13 +1951,13 @@ class CoachImportServiceTests(TestCase):
         self.assertEqual(profile.metadata["division"], "13U")
         self.assertEqual(profile.metadata["notes"], "Keep this")
         self.assertEqual(profile.metadata["custom"], "value")
-        self.assertNotIn(result.rows[0].temporary_password, str(profile.metadata))
+        self.assertFalse(result.rows[0].temporary_password)
         self.assertFalse(profile.created_from_import)
         self.assertIsNone(profile.import_batch)
 
     def test_missing_required_fields_produce_row_errors(self):
-        preview = preview_coach_import("first_name,last_name,email\nMissing,Email,\n")
-        result = commit_coach_import(self.staff, "first_name,last_name,email\nMissing,Email,\n")
+        preview = preview_coach_import("first_name,last_name,email,team,division\nMissing,Email,,Reds,13U\n", season=self.season)
+        result = commit_coach_import(self.staff, "first_name,last_name,email,team,division\nMissing,Email,,Reds,13U\n", season=self.season)
 
         self.assertEqual(preview.rows[0].status, "error")
         self.assertIn("Missing required field", preview.rows[0].messages[0])
@@ -1789,7 +1965,7 @@ class CoachImportServiceTests(TestCase):
         self.assertEqual(User.objects.count(), 1)
 
     def test_missing_required_columns_produce_import_error(self):
-        result = commit_coach_import(self.staff, "first_name,last_name\nNo,Email\n")
+        result = commit_coach_import(self.staff, "first_name,last_name\nNo,Email\n", season=self.season)
 
         self.assertEqual(result.errors, 1)
         self.assertIn("Missing required column", result.rows[0].messages[0])
@@ -1798,7 +1974,7 @@ class CoachImportServiceTests(TestCase):
         regular = User.objects.create_user(username="regular", password="testpass")
 
         with self.assertRaisesMessage(ValidationError, "Only staff users can import coaches"):
-            commit_coach_import(regular, self.csv_text(["Casey,Coach,casey@example.com,,,,,,"]))
+            commit_coach_import(regular, self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]), season=self.season)
 
     def test_username_for_person_uses_same_normalization_style(self):
         self.assertEqual(base_username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne")
@@ -1823,6 +1999,7 @@ class AccountOperationsViewTests(TestCase):
         profile.save(update_fields=["role", "updated_at"])
         self.player = Player.objects.create(first_name="Alex", last_name="Player")
         link_user_to_player(self.coach, self.player, relationship=UserPlayerRelationship.COACH, is_primary=False)
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
 
     def test_dashboard_requires_staff(self):
         self.client.force_login(self.regular)
@@ -2412,7 +2589,7 @@ class AccountOperationsViewTests(TestCase):
             content_type="text/csv",
         )
 
-        upload_response = self.client.post(reverse("accounts:coach-import-new"), {"csv_file": csv_file})
+        upload_response = self.client.post(reverse("accounts:coach-import-new"), {"season": str(self.season.id), "csv_file": csv_file})
         self.assertEqual(upload_response.status_code, 302)
         self.assertEqual(upload_response["Location"], reverse("accounts:coach-import-preview"))
 
@@ -2431,6 +2608,7 @@ class AccountOperationsViewTests(TestCase):
         self.assertTrue(user.is_active)
         self.assertEqual(user.account_profile.role, AccountRole.COACH)
         self.assertTrue(user.account_profile.must_change_password)
+        self.assertEqual(CoachSeasonAssignment.objects.filter(user=user, season_team__season=self.season).count(), 1)
         self.assertFalse(user.is_staff)
         self.assertFalse(user.is_superuser)
         self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
@@ -2446,6 +2624,22 @@ class AccountOperationsViewTests(TestCase):
         confirm_again = self.client.get(reverse("accounts:coach-import-confirm"))
         self.assertEqual(confirm_again.status_code, 302)
 
+    def test_coach_import_preview_rejects_manipulated_inactive_season(self):
+        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
+        self.client.force_login(self.staff)
+        session = self.client.session
+        session["coach_import_csv"] = "first_name,last_name,email,team,division\nBad,Season,bad.season@example.com,Reds,13U\n"
+        session["coach_import_season_id"] = inactive.id
+        session.save()
+
+        preview_response = self.client.get(reverse("accounts:coach-import-preview"))
+        confirm_response = self.client.post(reverse("accounts:coach-import-confirm"), {"confirm": "on"})
+
+        self.assertEqual(preview_response.status_code, 302)
+        self.assertEqual(preview_response["Location"], reverse("accounts:coach-import-new"))
+        self.assertEqual(confirm_response.status_code, 302)
+        self.assertFalse(User.objects.filter(email="bad.season@example.com").exists())
+
     def test_coach_import_reuses_existing_coach_and_blocks_non_coach_email(self):
         existing_coach = User.objects.create_user(username="existing.coach", email="existing@example.com")
         set_account_role(existing_coach, AccountRole.COACH)
@@ -2455,14 +2649,14 @@ class AccountOperationsViewTests(TestCase):
         csv_file = SimpleUploadedFile(
             "coaches.csv",
             (
-                "first_name,last_name,email\n"
-                "Existing,Coach,existing@example.com\n"
-                "Existing,Player,player@example.com\n"
+                "first_name,last_name,email,team,division\n"
+                "Existing,Coach,existing@example.com,Reds,13U\n"
+                "Existing,Player,player@example.com,Reds,13U\n"
             ).encode(),
             content_type="text/csv",
         )
 
-        self.client.post(reverse("accounts:coach-import-new"), {"csv_file": csv_file})
+        self.client.post(reverse("accounts:coach-import-new"), {"season": str(self.season.id), "csv_file": csv_file})
         response = self.client.post(reverse("accounts:coach-import-confirm"), {"confirm": "on"})
 
         self.assertEqual(response.status_code, 200)
@@ -2471,14 +2665,15 @@ class AccountOperationsViewTests(TestCase):
         self.assertEqual(result.conflicts, 1)
         temporary_password = result.rows[0].temporary_password
         existing_coach.refresh_from_db()
-        self.assertTrue(existing_coach.check_password(temporary_password))
-        self.assertTrue(existing_coach.account_profile.must_change_password)
+        self.assertFalse(temporary_password)
+        self.assertFalse(existing_coach.account_profile.must_change_password)
         self.assertEqual(existing_coach.account_profile.role, AccountRole.COACH)
+        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing_coach, season_team__season=self.season).count(), 1)
         self.assertEqual(User.objects.filter(email__iexact="existing@example.com").count(), 1)
         self.assertEqual(User.objects.filter(email__iexact="player@example.com").count(), 1)
 
         detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": existing_coach.id}))
-        self.assertNotContains(detail_response, temporary_password)
+        self.assertNotContains(detail_response, "Password unchanged")
 
 
 class AccountPasswordMiddlewareTests(TestCase):
diff --git a/accounts/views.py b/accounts/views.py
index 801a46e..8dde743 100644
--- a/accounts/views.py
+++ b/accounts/views.py
@@ -48,6 +48,7 @@ from accounts.services.permissions import (
 )
 from accounts.services.profile_service import get_account_role
 from accounts.services.role_service import role_label
+from seasons.models import Season
 
 
 class AccountOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
@@ -186,7 +187,8 @@ class CoachImportUploadView(AccountOperationsStaffRequiredMixin, FormView):
     def form_valid(self, form):
         try:
             csv_file = form.cleaned_data["csv_file"]
-            preview_coach_import_file(csv_file)
+            season = form.cleaned_data["season"]
+            preview_coach_import_file(csv_file, season=season)
             csv_file.seek(0)
             raw = csv_file.read()
             csv_text = raw if isinstance(raw, str) else raw.decode("utf-8-sig")
@@ -194,6 +196,7 @@ class CoachImportUploadView(AccountOperationsStaffRequiredMixin, FormView):
             form.add_error(None, exc)
             return self.form_invalid(form)
         self.request.session["coach_import_csv"] = csv_text
+        self.request.session["coach_import_season_id"] = season.id
         self.request.session.modified = True
         return redirect("accounts:coach-import-preview")
 
@@ -206,13 +209,18 @@ class CoachImportPreviewView(AccountOperationsStaffRequiredMixin, FormView):
         if not request.user.is_authenticated or not self.test_func():
             return super().dispatch(request, *args, **kwargs)
         self.csv_text = request.session.get("coach_import_csv", "")
+        self.season_id = request.session.get("coach_import_season_id")
         if not self.csv_text:
             messages.error(request, "Upload a coach CSV before previewing an import.")
             return redirect("accounts:coach-import-new")
+        self.season = Season.objects.filter(pk=self.season_id, is_active=True).first()
+        if not self.season:
+            messages.error(request, "Select an active season before previewing a coach import.")
+            return redirect("accounts:coach-import-new")
         return super().dispatch(request, *args, **kwargs)
 
     def get_preview(self):
-        return preview_coach_import(self.csv_text)
+        return preview_coach_import(self.csv_text, season=self.season)
 
     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
@@ -235,15 +243,21 @@ class CoachImportConfirmView(AccountOperationsStaffRequiredMixin, TemplateView):
             messages.error(request, "Confirm the coach import before continuing.")
             return redirect("accounts:coach-import-preview")
         csv_text = request.session.get("coach_import_csv", "")
+        season_id = request.session.get("coach_import_season_id")
         if not csv_text:
             messages.error(request, "Upload a coach CSV before confirming an import.")
             return redirect("accounts:coach-import-new")
+        season = Season.objects.filter(pk=season_id, is_active=True).first()
+        if not season:
+            messages.error(request, "Select an active season before confirming a coach import.")
+            return redirect("accounts:coach-import-new")
         try:
-            result = commit_coach_import(request.user, csv_text)
+            result = commit_coach_import(request.user, csv_text, season=season)
         except ValidationError as exc:
             messages.error(request, "; ".join(exc.messages))
             return redirect("accounts:coach-import-preview")
         request.session.pop("coach_import_csv", None)
+        request.session.pop("coach_import_season_id", None)
         request.session.modified = True
         return self.render_to_response(self.get_context_data(result=result))
 
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 4a21fc2..58e31f2 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -202,7 +202,7 @@ What it must not own:
 
 Current status:
 
-Seasonal Participation V1 Phase 1 foundation and Phase 2 season-aware player import are implemented. The schema, services, admin registration, tests, and player import integration exist. Player imports now require a selected active season and create or update season teams and player roster memberships. Coach imports and evaluations are not season-aware yet.
+Seasonal Participation V1 Phase 1 foundation, Phase 2 season-aware player import, and Phase 3 season-aware coach import are implemented. The schema, services, admin registration, tests, player import integration, and coach import integration exist. Player imports now create or update season teams and player roster memberships. Coach imports now create or update season teams and coach season assignments while preserving permanent coach accounts. Evaluations are not season-aware yet.
 
 Documentation:
 
@@ -327,7 +327,7 @@ Dependency guidance:
 | Players | V1 | Complete |
 | Analytics | V1 | Complete |
 | Account Management | V1 | Complete / Frozen |
-| Seasons | V1 Phase 2 | Player import integration complete |
+| Seasons | V1 Phase 3 | Coach import integration complete |
 | Drafts | Active | Active development |
 | PDP | Legacy | Transitionary |
 | LeagueHub | Planned | Planned |
@@ -343,6 +343,7 @@ The platform currently has:
 - production-ready Account Management V1 foundation
 - production-ready staff-facing Account Operations
 - season-aware roster participation foundation
+- season-aware player and coach import integration
 - account provisioning from player imports
 - forced password-change account flow
 - staff-only Analytics command center and reporting tables
@@ -359,7 +360,7 @@ Likely future areas:
 
 - Account Management V2
 - Analytics V2
-- Seasonal Participation Phase 3
+- Seasonal Participation Phase 4
 - Drafts expansion
 - LeagueHub
 - Video
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index d000a40..9dc8ceb 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -15,7 +15,7 @@ The platform helps Vancouver Community Baseball manage:
 
 This is a user manual, not a technical deployment guide. Deployment information lives in [docs/deployment/](deployment/README.md).
 
-Season-aware roster foundations now exist in the system. Player imports are now season-aware: staff choose an active season, and imported team/division information creates roster participation records for that season. Coach import and evaluation pages are not season-aware yet, so staff should continue using the current coach import and evaluation workflows until those seasonal phases are implemented.
+Season-aware roster foundations now exist in the system. Player and coach imports are now season-aware: staff choose an active season, and imported team/division information creates roster participation records or coach assignments for that season. Evaluation pages are not season-aware yet, so staff should continue using the current evaluation workflows until that seasonal phase is implemented.
 
 ## Start Here
 
@@ -330,10 +330,16 @@ Optional CSV columns:
 - `is_active`
 - `notes`
 - `source_id`
+- `assignment_role`
+- `assignment_start_date`
+- `assignment_end_date`
+- `assignment_source_id`
+
+Staff must select an active season when uploading the coach CSV. Team and division are required for the seasonal coach assignment.
 
 Coach import creates or reuses coach login accounts. It does not create player records and does not create coach-to-player links.
 
-Imported coach accounts are active by default and must change password on first login.
+New imported coach accounts are active by default and must change password on first login. Returning coach accounts are reused without changing their password or activation status.
 
 ### User-Player Links
 
diff --git a/docs/account_management/V1_SUMMARY.md b/docs/account_management/V1_SUMMARY.md
index d45e225..14f3bb7 100644
--- a/docs/account_management/V1_SUMMARY.md
+++ b/docs/account_management/V1_SUMMARY.md
@@ -286,11 +286,12 @@ Deferred from Platform V1 Account Operations:
 - account merge;
 - duplicate account resolution;
 - invitation and email verification flows;
-- coach import;
 - parent import;
 - portal dashboards;
 - self-service password recovery email flow.
 
+Season-aware coach import is implemented separately under Seasonal Participation V1 Phase 3. It reuses Account Management services for account creation/reuse, while seasonal team assignments belong to the `seasons` app.
+
 ## Service Boundaries
 
 `profile_service`
diff --git a/docs/account_management/implementation/engineering/platform_v1_account_operations.md b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
index a1ee442..b7f92b8 100644
--- a/docs/account_management/implementation/engineering/platform_v1_account_operations.md
+++ b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
@@ -651,6 +651,8 @@ Bulk coach import is outside the current Platform V1 Account Operations roadmap.
 
 That future plan should define CSV format, matching rules, duplicate detection, role assignment, password reset behavior, and safety checks before implementation begins.
 
+Status note: Seasonal Participation V1 Phase 3 later implemented season-aware coach import through the existing `accounts` coach import service while storing seasonal team assignments in `seasons`. Account Operations itself remains frozen.
+
 ## 10. Risks
 
 - Incorrect role assignment could make reporting and evaluator snapshots misleading.
diff --git a/docs/seasons/README.md b/docs/seasons/README.md
index 59af133..47c34f9 100644
--- a/docs/seasons/README.md
+++ b/docs/seasons/README.md
@@ -23,6 +23,8 @@ Phase 1 - Season And Roster Foundation is implemented.
 
 Phase 2 - Season-Aware Player Import is implemented.
 
+Phase 3 - Season-Aware Coach Import is implemented.
+
 Verified production state on July 15, 2026:
 
 ```text
@@ -55,14 +57,25 @@ Implemented player import integration:
 - same-season active primary team changes are blocked for manual review;
 - prior-season memberships are preserved.
 
+Implemented coach import integration:
+
+- coach imports require a selected active season;
+- imported rows require team, division, and an assignment role;
+- new coach accounts receive one-time temporary passwords and must change them on first login;
+- existing coach accounts are reused without password reset or activation changes;
+- existing non-coach accounts remain conflicts;
+- season teams are created or reused through `seasons` services;
+- coach season assignments are created or updated through `seasons` services;
+- prior-season assignments are preserved;
+- coaches may have multiple teams and roles in the same season.
+
 Current limitations:
 
-- coach import does not require or create seasonal assignments yet;
 - evaluations do not yet store season/team/membership context;
 - there are no first-class roster-management pages yet.
 
 Next phase:
 
-- Phase 3 - Season-Aware Coach Import.
+- Phase 4 - Evaluation Context.
 
-No coach import or evaluation workflow changes were made in Phase 2.
+No evaluation workflow changes were made in Phase 3.
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
index 04d9e39..bb0069a 100644
--- a/docs/seasons/implementation/engineering/seasonal_participation_v1.md
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -1,6 +1,6 @@
 # Seasonal Participation V1 Engineering Plan
 
-Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 is the next implementation phase.
+Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 season-aware coach import complete. Phase 4 is the next implementation phase.
 
 Created: 2026-07-15.
 
@@ -689,6 +689,8 @@ Status: complete.
 
 ### Phase 3 - Coach Seasonal Assignment
 
+Status: complete.
+
 - Add season selection to coach import.
 - Map team/division to `SeasonTeam`.
 - Create/update `CoachSeasonAssignment`.
@@ -815,11 +817,11 @@ Rollback considerations:
 
 ## 27. Recommended Next Implementation Phase
 
-Start with Phase 3 - Coach Seasonal Assignment.
+Start with Phase 4 - Evaluation Context.
 
-Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services.
+Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services. Phase 3 updated coach import to require a selected season, create or reuse `SeasonTeam`, and create/update `CoachSeasonAssignment` through `seasons` services while preserving existing coach passwords.
 
-Before implementing Phase 3, verify that Phase 2 production migration completed successfully and that imported player rows are creating expected season teams and roster memberships.
+Before implementing Phase 4, verify that Phase 3 production rollout completed successfully and that imported coach rows are creating expected season teams and coach assignments.
 
 ## 28. Acceptance Criteria
 

```
