# Prompt 84 - Accounts

## User Prompt

Source prompt file:
`/Users/eugenelin/.codex/attachments/0b4505d7-a259-4f04-90a9-e0e8fa7d241b/pasted-text.txt`

```text
Perform Repository Cleanup Phase 4 only: Coach Import Service Refactor.

Use continuous loop engineering.

Continue until the coach import service is structurally cleaner, behavior remains unchanged, focused and full verification pass, commits are pushed, and the working tree is clean.

Do not change coach-import product behavior.

Do not add new import fields, models, migrations, screens, permissions, or features.

Do not begin the Season Operations view refactor, test-package split, account-operations refactor, or any Platform V2 work.

==================================================
Current State
=============

Repository Cleanup Phases 1 through 3 are complete.

Current repository state includes:

* reconciled current documentation;
* Django 4.2.30;
* Ruff correctness checks;
* Black;
* isort;
* pre-commit;
* touched-files-only formatting policy;
* refactored player import service with a stable façade and focused internal package.

Seasonal Participation V1 is Feature Complete, Production Ready, and Frozen.

The current coach import workflow is production behavior and must not change.

The coach import subsystem currently combines several responsibilities in:

```text
accounts/services/coach_import_service.py
```

These responsibilities include:

* CSV decoding;
* header normalization;
* row parsing;
* primitive validation;
* account matching;
* username generation;
* role validation;
* preview construction;
* session serialization;
* SeasonTeam resolution;
* CoachSeasonAssignment resolution;
* new account creation;
* returning-account reuse;
* password handling;
* assignment creation/update;
* commit processing;
* result reporting.

The objective is a behavior-preserving structural refactor.

==================================================
Objective
=========

Reduce the size and mixed responsibilities of:

```text
accounts/services/coach_import_service.py
```

Split cohesive responsibilities into focused internal modules while preserving a small, stable public façade for all current callers.

The refactor must make the coach importer easier to maintain without changing:

* routes;
* forms;
* views;
* templates;
* session workflow;
* CSV fields;
* required fields;
* validation messages;
* account matching;
* account role behavior;
* account activation behavior;
* password behavior;
* SeasonTeam behavior;
* CoachSeasonAssignment behavior;
* preview labels;
* result counters;
* permissions;
* transaction semantics.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete refactoring, regression-proofing, documentation, or verification work remains.

PASS

All Phase 4 acceptance criteria are satisfied, tests and tooling pass, commits are pushed, and the working tree is clean.

BLOCKED

The service cannot be safely decomposed without unresolved behavior changes, migration changes, or scope expansion.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied criterion.

Do not continue through cosmetic file movement alone.

==================================================
Established Loop Workflow
=========================

Every loop must:

1. reconcile the committed repository state;
2. read `AGENTS.md`;
3. read current coach-import and account-management documentation;
4. read the player-import refactor result for pattern guidance;
5. confirm the working tree is clean;
6. inspect the complete coach-import workflow and all service callers;
7. identify one cohesive refactoring boundary;
8. create the next prompt archive before implementation;
9. refactor only the selected coach-import concern;
10. preserve or add focused regression tests;
11. run tooling on touched files only;
12. run focused verification;
13. perform senior-engineer self-review;
14. fix every verified issue;
15. update architecture or engineering documentation only if internal ownership materially changes;
16. run the full verification suite;
17. commit implementation, tests, and minimal documentation;
18. finalize and separately commit the prompt archive;
19. push both commits;
20. re-read the committed diff;
21. confirm the working tree is clean;
22. reassess all acceptance criteria;
23. choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS;
24. if CONTINUE, immediately begin the next loop.

Each loop must create:

1. one refactor/test/documentation commit;
2. one prompt archive commit.

==================================================
Required Repository Review
==========================

Read:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* `docs/account_management/V1_SUMMARY.md`
* relevant account-management implementation documentation
* relevant coach-import documentation
* Seasonal Participation documentation
* prompt archives related to:

  * coach import;
  * account provisioning;
  * account roles;
  * password handling;
  * season-aware coach import;
  * player import service refactor.

Inspect:

* `accounts/services/coach_import_service.py`
* every import from `accounts.services.coach_import_service`
* `accounts/forms.py`
* `accounts/views.py`
* coach import templates
* `accounts/tests.py`
* `accounts/models.py`
* `accounts/services/email_service.py`
* `accounts/services/username_service.py`
* `accounts/services/password_service.py`
* `accounts/services/profile_service.py`
* `accounts/services/role_service.py`
* `accounts/services/permissions.py`
* `seasons/services/team_service.py`
* `seasons/services/coach_assignment_service.py`
* relevant migrations only for dependency understanding.

==================================================
Public API Preservation
=======================

Inventory every public name currently imported from:

```text
accounts.services.coach_import_service
```

Preserve current import paths wherever practical.

Preferred approach:

* convert `accounts/services/coach_import_service.py` into a small façade;
* move internal implementation into a focused package;
* re-export existing public constants, dataclasses, and functions.

Suggested structure:

```text
accounts/services/coach_import/
    __init__.py
    constants.py
    result_models.py
    parsing.py
    matching.py
    assignment.py
    preview.py
    commit.py
```

This is a suggested structure only.

Use repository evidence to choose the smallest clear split.

Do not force unnecessary modules.

Forms and views must continue importing from the public façade rather than deep internal modules.

==================================================
Recommended Responsibility Boundaries
=====================================

Separate responsibilities where cohesive.

## 1. Constants And Data Contracts

Move stable constants and frozen dataclasses where practical.

Examples:

* preview statuses;
* result statuses;
* required and optional CSV columns;
* assignment-role aliases;
* preview row dataclass;
* preview summary dataclass;
* result row dataclass;
* result summary dataclass.

Avoid circular imports.

## 2. CSV And Primitive Parsing

Move:

* uploaded-file decoding;
* header normalization;
* CSV reading;
* boolean parsing;
* date parsing;
* assignment-role parsing;
* blank-value behavior;
* required-column validation.

Do not change accepted formats.

Do not change validation messages intentionally.

## 3. Account Matching

Move coach-import-specific account matching orchestration:

* normalized email matching;
* existing user classification;
* coach versus non-coach conflict detection;
* username proposal;
* new versus reused account action.

Continue using existing authoritative services:

* email normalization and matching;
* username generation and validation;
* account profile services;
* role services.

Do not copy permanent account rules into new modules.

## 4. Season Team And Assignment Integration

Move coach-import-specific orchestration around:

* SeasonTeam preview and resolution;
* assignment-role validation;
* assignment create/reuse/update decisions;
* primary-assignment behavior;
* assignment date handling;
* source identifier handling.

Continue delegating domain rules to:

* `seasons.services.team_service`;
* `seasons.services.coach_assignment_service`.

Do not move generic seasonal business rules into `accounts`.

## 5. Preview Construction

Move:

* per-row preview construction;
* account action labels;
* password-behavior labels;
* team action labels;
* assignment action labels;
* row error aggregation;
* preview counters.

Preview output must remain identical from the perspective of forms, templates, views, and tests.

## 6. Commit Processing

Move:

* per-row transaction orchestration;
* new user creation;
* permanent account profile creation;
* returning-account reuse;
* temporary-password generation for new users;
* password preservation for returning users;
* SeasonTeam resolution;
* assignment create/update;
* result-row construction;
* result counters.

Do not alter current per-row atomicity or batch behavior.

==================================================
Behavioral Freeze
=================

The following behavior must remain unchanged.

## Season Selection

* every new coach import requires an active season;
* current season remains the default where implemented;
* selected season remains server-validated;
* selected season persists through preview and confirmation;
* inactive or manipulated season identifiers remain rejected.

## CSV Behavior

* required columns remain:

  * first name;
  * last name;
  * email;
* optional columns remain unchanged;
* accepted boolean and date formats remain unchanged;
* assignment-role aliases remain unchanged;
* blank assignment role keeps the current default;
* unknown roles remain validation errors.

## Account Matching

* matching remains based on normalized email;
* existing coach accounts are reused;
* existing non-coach accounts remain conflicts;
* no duplicate permanent user is created;
* usernames are generated using current rules;
* account role is not silently changed for established users.

## Password Safety

For returning coaches:

* password hash remains unchanged;
* no temporary password is generated;
* no temporary password is displayed;
* `must_change_password` is not changed merely due to reimport;
* account activation is not changed merely due to assignment import.

For genuinely new coaches:

* secure temporary password is created;
* one-time display behavior remains unchanged;
* `must_change_password=True` remains unchanged;
* current account activation behavior remains unchanged.

## Seasonal Behavior

* SeasonTeam normalization and reuse remain unchanged;
* same team name in another season remains a distinct SeasonTeam;
* new season creates a new assignment;
* prior assignments remain historical;
* same user/team/role assignment is reused or updated deterministically;
* multiple teams and roles remain supported;
* primary assignment behavior remains unchanged.

## Privilege Separation

Coach import must not:

* grant `is_staff`;
* grant `is_superuser`;
* alter unrelated permissions;
* create player links;
* silently alter an established account role;
* reset an established password.

## Preview And Results

Preserve:

* preview row fields;
* preview status semantics;
* action labels;
* password-behavior labels;
* result row fields;
* result status semantics;
* all counters;
* error and conflict classifications;
* temporary-password exposure rules.

==================================================
No Generic Import Framework
===========================

Do not create a broad shared import framework.

Do not refactor the player importer again in this phase.

Player and coach imports have distinct identity and provisioning behavior and may remain separate.

Only extract utilities outside `accounts` if they are already clearly generic and the extraction is minimal, obvious, and behavior-neutral.

Otherwise keep internal modules under:

```text
accounts/services/coach_import/
```

==================================================
Tests
=====

Preserve all existing coach-import tests.

Add focused tests only where decomposition exposes an untested public contract.

Useful contract tests may include:

* façade exports remain importable;
* preview dataclasses retain the same fields;
* CSV parsing behavior remains stable;
* role aliases remain stable;
* returning coach password hash remains unchanged;
* returning coach activation and role remain unchanged;
* new account temporary-password behavior remains unchanged;
* assignment action labels and counters remain stable;
* same-season same-assignment reimport remains deterministic;
* new-season assignment preserves prior history;
* non-coach email conflict remains unchanged.

Do not rewrite the entire account test suite merely because internal modules moved.

Tests should primarily exercise the public service and web workflow.

Avoid coupling tests to private implementation details.

==================================================
Dependency Direction
====================

Preferred dependency direction:

```text
forms/views
    ->
accounts.services.coach_import_service façade
    ->
accounts.services.coach_import internal modules
    ->
existing account identity/profile/password services
    ->
seasons public services
```

Internal parsing and data-contract modules must not import:

* forms;
* views;
* templates.

Avoid mutual imports between internal modules.

Use lazy imports only where they prevent a real dependency cycle and preserve clarity.

==================================================
Transaction Review
==================

Inventory current transaction behavior before moving code.

Preserve:

* preview as read-only behavior;
* confirmation transaction scope;
* per-row atomicity or batch atomicity exactly as currently implemented;
* rollback behavior when assignment creation fails;
* behavior when new account creation succeeds but assignment creation fails;
* partial-failure reporting;
* one-time password result behavior.

Do not accidentally leave orphaned new accounts if the current workflow prevents that.

Do not widen or narrow transaction boundaries without a verified defect and explicit regression coverage.

==================================================
Code Quality
============

Apply tooling only to touched files.

Run:

```bash
ruff check <touched-python-files>
black --check <touched-python-files>
isort --check-only <touched-python-files>
```

If formatting fails:

* format only touched files;
* do not format unrelated files;
* do not modify migrations.

Keep:

* frozen dataclasses;
* existing user-facing messages;
* explicit service calls;
* stable public façade;
* service-owned business logic;
* no signals.

Remove:

* dead private functions;
* duplicate imports;
* obsolete comments;
* duplicated account or seasonal rules;
* compatibility wrappers that serve no stable public caller.

==================================================
Documentation
=============

Update documentation only if necessary to describe the new internal service layout.

Potential documents:

* `docs/ARCHITECTURE.md`
* current Account Management implementation/status documentation.

Do not change user-facing documentation because user behavior must remain unchanged.

Do not present the refactor as a new feature.

==================================================
Scope Restrictions
==================

Do not:

* modify models;
* create migrations;
* change URLs;
* change forms except import paths if unavoidable;
* change views except import paths if unavoidable;
* change templates;
* change permissions;
* add CSV fields;
* change required columns;
* change account matching;
* change password behavior;
* change role behavior;
* change activation behavior;
* change assignment behavior;
* change messages intentionally;
* refactor player import;
* refactor Season Operations views;
* split all test modules;
* refactor account operations;
* add APIs;
* add JavaScript;
* add caching;
* add background jobs;
* bulk-format the repository;
* regenerate the project flat-file snapshot.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test python manage.py test accounts
DJANGO_SECRET_KEY=test python manage.py test seasons
DJANGO_SECRET_KEY=test python manage.py test players
git diff --check
```

Run pre-commit on all touched files:

```bash
pre-commit run --files <all-touched-files>
```

==================================================
Full Verification Every Loop
============================

Run:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
DJANGO_SECRET_KEY=test python manage.py migrate --plan
DJANGO_SECRET_KEY=test python manage.py test
git diff --check
```

The complete suite must pass before committing.

==================================================
Senior-Engineer Self-Review
===========================

Review every diff for:

* accidental account behavior changes;
* changed validation text;
* changed role aliases;
* changed preview fields;
* changed result counters;
* transaction-boundary drift;
* password hash changes for reused users;
* temporary-password exposure;
* role escalation;
* activation changes;
* assignment duplication;
* primary-assignment regressions;
* SeasonTeam normalization regressions;
* provenance loss;
* circular imports;
* deep-module imports leaking into views;
* duplicated rules;
* dead façade code;
* unnecessary generic abstractions;
* formatting churn;
* stale documentation.

Fix every verified issue before committing.

==================================================
Acceptance Criteria
===================

Do not declare PASS until all criteria are satisfied.

A. Structure

* `accounts/services/coach_import_service.py` is materially smaller;
* cohesive responsibilities are split into focused modules;
* public imports remain stable where practical;
* views and forms do not import internal modules.

B. Account Behavior

* new coach creation remains unchanged;
* returning coach reuse remains unchanged;
* non-coach conflict behavior remains unchanged;
* username behavior remains unchanged;
* account role and activation behavior remain unchanged.

C. Password Safety

* reused coach password hash remains unchanged;
* reused coach receives no temporary password;
* new coach temporary-password behavior remains unchanged;
* one-time display remains unchanged;
* password-change flag behavior remains unchanged.

D. Seasonal Behavior

* SeasonTeam behavior remains unchanged;
* assignment create/update/reuse behavior remains unchanged;
* multiple teams and roles remain supported;
* primary-assignment behavior remains unchanged;
* prior assignments remain historical.

E. Transactions And Integrity

* transaction boundaries remain equivalent;
* no orphan new accounts are introduced;
* partial-failure reporting remains equivalent;
* duplicate users and assignments are not introduced.

F. Quality

* no circular imports;
* no duplicated business rules;
* no dead code;
* touched files pass Ruff, Black, and isort;
* no unrelated formatting churn.

G. Tests

* focused suites pass;
* full suite passes;
* password preservation has explicit regression coverage;
* any newly exposed contract gap is tested.

H. Migration

* no model changes;
* no migrations;
* migration checks pass.

I. Documentation

* architecture/internal layout docs updated only if needed;
* user-facing behavior docs remain unchanged.

J. Git

* refactor commit exists;
* prompt archive commit exists;
* both pushed;
* working tree is clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally:

1. inventory public names and callers;
2. create a focused `accounts.services.coach_import` package;
3. move constants and result models;
4. move parsing and account matching;
5. move seasonal assignment integration;
6. move preview and commit orchestration;
7. preserve the façade;
8. remove obsolete code from the original module;
9. run tooling and full verification;
10. update minimal architecture documentation if warranted;
11. commit, archive, push, and reassess.

If the complete safe split is too large, continue with another cohesive loop.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* materially reduces mixed responsibilities;
* removes verified duplication;
* strengthens password-preservation proof;
* fixes a dependency-cycle risk;
* improves maintainability without behavior change;
* adds missing contract-level regression coverage.

Moving code without clearer ownership does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* developer maintaining CSV parsing;
* developer maintaining account matching;
* developer maintaining password behavior;
* developer maintaining seasonal assignments;
* tester diagnosing row-level conflicts;
* security reviewer inspecting password and privilege boundaries;
* production operator relying on deterministic seasonal reimports.

Confirm:

* the importer is easier to navigate;
* all current behavior remains intact;
* the public façade remains stable;
* password handling is unchanged and safe;
* no unrelated subsystem was refactored;
* the full suite passes.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before implementation;
2. commit refactor, tests, and minimal documentation;
3. update the prompt archive with:

   * implementation commit hash;
   * old and new module structure;
   * public API preservation;
   * account matching behavior;
   * password-preservation findings;
   * assignment behavior;
   * transaction findings;
   * tests added or changed;
   * tooling results;
   * full verification;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested implementation commit:

```text
Refactor coach import service
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
* old and new module structure;
* public façade behavior;
* CSV parsing split;
* account matching split;
* preview split;
* commit split;
* password behavior;
* account role and activation behavior;
* seasonal team behavior;
* assignment behavior;
* transaction behavior;
* regression tests;
* tooling checks;
* focused verification;
* full verification;
* documentation changes;
* deferred cleanup work;
* commits;
* push result;
* confirmation that no application behavior intentionally changed;
* confirmation that no migrations were created;
* confirmation that the working tree is clean.
```

## Implementation Commit

`005c651` - Refactor coach import service

## Module Structure

Old structure:

```text
accounts/services/coach_import_service.py
```

New structure:

```text
accounts/services/coach_import_service.py        # public façade and compatibility exports
accounts/services/coach_import/__init__.py       # internal import package marker
accounts/services/coach_import/constants.py      # columns, preview statuses, result statuses, role aliases
accounts/services/coach_import/result_models.py  # frozen preview/result dataclasses
accounts/services/coach_import/parsing.py        # CSV, boolean, date, role, and season parsing helpers
accounts/services/coach_import/matching.py       # account role lookup helper
accounts/services/coach_import/assignment.py     # SeasonTeam and CoachSeasonAssignment integration
accounts/services/coach_import/preview.py        # preview construction and preview counters
accounts/services/coach_import/commit.py         # account creation/reuse, password handling, commit results
```

## Public API Preservation

- Existing callers continue importing from `accounts.services.coach_import_service`.
- `accounts/views.py` and `accounts/tests.py` import paths were not changed.
- The façade re-exports current public constants, dataclasses, `User`, `preview_coach_import`, `preview_coach_import_file`, and `commit_coach_import` through `__all__`.
- Forms and views do not import internal `accounts.services.coach_import` modules.

## Account Matching Behavior

- Normalized email matching still delegates to `accounts.services.email_service.find_existing_email_user()` and `normalize_email()`.
- Existing coach users are still classified through account profile role metadata.
- Existing non-coach users still produce conflicts.
- Username validation/generation still delegates to `username_service`.

## Password Preservation Findings

- Reused coaches still go through the reuse path and retain their password hash.
- Reused coaches still receive no temporary password and report `Password unchanged`.
- New coaches still receive a secure temporary password from `password_service.set_random_temporary_password()`.
- New coaches still get `must_change_password=True`.
- Temporary passwords remain present only in result rows for newly created coaches.

## Assignment Behavior

- SeasonTeam lookup and creation still delegates to `seasons.services.team_service`.
- Coach assignment creation/update still delegates to `seasons.services.coach_assignment_service`.
- Assignment role parsing and aliases were preserved.
- Primary assignment behavior is preserved through `get_primary_assignment()` before creating a primary active assignment.

## Transaction Findings

- `commit_assignment`, `reuse_existing_coach`, and `create_coach` remain transaction-wrapped.
- `commit_coach_import` remains batch-iterative rather than broadening to one batch transaction.
- User reuse still locks the existing user with `select_for_update()`.
- Assignment update still locks matching assignments with `select_for_update()`.

## Tests And Tooling

- `pre-commit run --files` on touched files: passed.
- Touched files passed Ruff, Black, and isort through pre-commit.
- Focused verification passed:
  - `DJANGO_SECRET_KEY=test python manage.py check`
  - `DJANGO_SECRET_KEY=test python manage.py makemigrations accounts --check`
  - `DJANGO_SECRET_KEY=test python manage.py makemigrations seasons --check`
  - `DJANGO_SECRET_KEY=test python manage.py test accounts seasons players` with 285 tests.

## Full Verification

- `DJANGO_SECRET_KEY=test python manage.py check`: passed.
- `DJANGO_SECRET_KEY=test python manage.py makemigrations --check`: passed.
- `DJANGO_SECRET_KEY=test python manage.py migrate --plan`: passed.
- `DJANGO_SECRET_KEY=test python manage.py test`: passed, 458 tests.
- `git diff --check`: passed.

## Commit Diff

```diff
commit 005c6518d673a1745aaf3efdaaef4a92bfe1c975
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 11:14:03 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 11:14:03 2026 -0700

    Refactor coach import service
---
 accounts/services/coach_import/__init__.py      |   1 +
 accounts/services/coach_import/assignment.py    | 140 ++++
 accounts/services/coach_import/commit.py        | 224 +++++++
 accounts/services/coach_import/constants.py     |  43 ++
 accounts/services/coach_import/matching.py      |  10 +
 accounts/services/coach_import/parsing.py       |  88 +++
 accounts/services/coach_import/preview.py       | 331 +++++++++
 accounts/services/coach_import/result_models.py | 195 ++++++
 accounts/services/coach_import_service.py       | 848 ++----------------------
 9 files changed, 1088 insertions(+), 792 deletions(-)

diff --git a/accounts/services/coach_import/__init__.py b/accounts/services/coach_import/__init__.py
new file mode 100644
index 0000000..31ae42a
--- /dev/null
+++ b/accounts/services/coach_import/__init__.py
@@ -0,0 +1 @@
+"""Internal coach import service modules."""
diff --git a/accounts/services/coach_import/assignment.py b/accounts/services/coach_import/assignment.py
new file mode 100644
index 0000000..3e72549
--- /dev/null
+++ b/accounts/services/coach_import/assignment.py
@@ -0,0 +1,140 @@
+"""Season team and coach-assignment integration for coach imports."""
+
+from __future__ import annotations
+
+from django.db import transaction
+
+from accounts.services.coach_import.parsing import parse_import_date
+from accounts.services.coach_import.result_models import CoachImportRowPreview
+from seasons.models import CoachSeasonAssignment, Season
+from seasons.services.coach_assignment_service import (
+    create_assignment,
+    get_primary_assignment,
+    update_assignment,
+)
+from seasons.services.team_service import (
+    get_or_create_season_team,
+    normalize_division_value,
+    normalize_team_value,
+)
+
+
+def season_team_preview(*, season: Season, team: str, division: str) -> tuple[str, str]:
+    normalized_team = normalize_team_value(team)
+    normalized_division = normalize_division_value(division)
+    existing = season.teams.filter(
+        normalized_name=normalized_team,
+        normalized_division=normalized_division,
+    ).first()
+    if existing:
+        return "reuse", "Reuse Season Team"
+    return "create", "Create Season Team"
+
+
+def assignment_preview(
+    *,
+    user,
+    season: Season,
+    team: str,
+    division: str,
+    assignment_role: str,
+    is_active: bool,
+) -> tuple[str, str]:
+    if not user:
+        return "create", "Create Assignment"
+    normalized_team = normalize_team_value(team)
+    normalized_division = normalize_division_value(division)
+    existing = (
+        CoachSeasonAssignment.objects.select_related("season_team")
+        .filter(
+            user=user,
+            season_team__season=season,
+            season_team__normalized_name=normalized_team,
+            season_team__normalized_division=normalized_division,
+            assignment_role=assignment_role,
+        )
+        .first()
+    )
+    if existing:
+        return "update", (
+            "Update Assignment" if is_active else "Update Inactive Assignment"
+        )
+    return "create", "Create Assignment"
+
+
+def metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
+    return {
+        key: value
+        for key, value in {
+            "team": row.team,
+            "division": row.division,
+            "notes": row.notes,
+            "source_id": row.source_id,
+            "assignment_role": row.assignment_role,
+            "source": "coach_roster",
+        }.items()
+        if value
+    }
+
+
+def profile_metadata(profile) -> dict:
+    return profile.metadata if isinstance(profile.metadata, dict) else {}
+
+
+@transaction.atomic
+def commit_assignment(
+    user, row: CoachImportRowPreview, season: Season
+) -> tuple[str, bool]:
+    season_team, team_created = get_or_create_season_team(
+        season=season,
+        name=row.team,
+        division=row.division,
+        metadata={"source": "coach_roster"},
+    )
+    assignment = (
+        CoachSeasonAssignment.objects.select_for_update()
+        .filter(
+            user=user,
+            season_team=season_team,
+            assignment_role=row.assignment_role,
+        )
+        .first()
+    )
+    starts_on = parse_import_date(row.assignment_start_date)
+    ends_on = parse_import_date(row.assignment_end_date)
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
+    updates["metadata"] = {
+        key: value
+        for key, value in {"notes": row.notes, "source_id": row.source_id}.items()
+        if value
+    }
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
+        metadata={
+            key: value
+            for key, value in {"notes": row.notes, "source_id": row.source_id}.items()
+            if value
+        },
+    )
+    return "created", team_created
diff --git a/accounts/services/coach_import/commit.py b/accounts/services/coach_import/commit.py
new file mode 100644
index 0000000..9890c65
--- /dev/null
+++ b/accounts/services/coach_import/commit.py
@@ -0,0 +1,224 @@
+"""Commit orchestration for staff coach imports."""
+
+from __future__ import annotations
+
+from dataclasses import replace
+
+from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+from django.db import transaction
+
+from accounts.models import AccountRole
+from accounts.services.coach_import.assignment import (
+    commit_assignment,
+    metadata_for_row,
+    profile_metadata,
+)
+from accounts.services.coach_import.constants import (
+    RESULT_CONFLICT,
+    RESULT_CREATED,
+    RESULT_ERROR,
+    RESULT_REUSED,
+    STATUS_CONFLICT,
+    STATUS_READY,
+    STATUS_REUSE,
+)
+from accounts.services.coach_import.matching import role_for_user
+from accounts.services.coach_import.preview import preview_coach_import
+from accounts.services.coach_import.result_models import (
+    CoachImportResult,
+    CoachImportResultRow,
+    CoachImportRowPreview,
+)
+from accounts.services.email_service import find_existing_email_user
+from accounts.services.password_service import set_random_temporary_password
+from accounts.services.permissions import can_manage_accounts
+from accounts.services.profile_service import (
+    get_or_create_account_profile,
+    set_account_role,
+)
+from seasons.models import Season
+
+User = get_user_model()
+
+
+def validate_actor(actor) -> None:
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can import coaches.")
+
+
+@transaction.atomic
+def reuse_existing_coach(
+    row: CoachImportRowPreview, season: Season
+) -> CoachImportResultRow:
+    user = (
+        User.objects.select_for_update()
+        .select_related("account_profile")
+        .get(pk=row.existing_user_id)
+    )
+    profile = get_or_create_account_profile(user)
+    if profile.role != AccountRole.COACH:
+        raise ValidationError("Existing account is not a coach.")
+    metadata = {**profile_metadata(profile), **metadata_for_row(row)}
+    profile.metadata = metadata
+    profile.save(update_fields=["metadata", "updated_at"])
+    user.first_name = user.first_name or row.first_name
+    user.last_name = user.last_name or row.last_name
+    user.email = user.email or row.email
+    user.save(update_fields=["first_name", "last_name", "email"])
+    assignment_action, team_created = commit_assignment(user, row, season)
+    status_message = "inactive" if not user.is_active else "active"
+    return CoachImportResultRow(
+        row_number=row.row_number,
+        status=RESULT_REUSED,
+        username=user.username,
+        user_id=user.id,
+        is_active=user.is_active,
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
+    )
+
+
+@transaction.atomic
+def create_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResultRow:
+    user = User.objects.create(
+        username=row.final_username,
+        first_name=row.first_name,
+        last_name=row.last_name,
+        email=row.email,
+        is_active=row.is_active,
+    )
+    temporary_password = set_random_temporary_password(user)
+    profile = set_account_role(user, AccountRole.COACH)
+    profile.must_change_password = True
+    profile.metadata = {**profile_metadata(profile), **metadata_for_row(row)}
+    profile.save(update_fields=["must_change_password", "metadata", "updated_at"])
+    assignment_action, team_created = commit_assignment(user, row, season)
+    status_message = "inactive" if not user.is_active else "active"
+    return CoachImportResultRow(
+        row_number=row.row_number,
+        status=RESULT_CREATED,
+        username=user.username,
+        user_id=user.id,
+        is_active=user.is_active,
+        temporary_password=temporary_password,
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
+    )
+
+
+def commit_coach_import(
+    actor, csv_text: str, season: Season | None = None
+) -> CoachImportResult:
+    """Create or reuse coach accounts from CSV text and return one-time passwords."""
+    validate_actor(actor)
+    preview = preview_coach_import(csv_text, season=season)
+    result_rows = []
+
+    for error in preview.row_errors:
+        result_rows.append(
+            CoachImportResultRow(row_number=0, status=RESULT_ERROR, messages=[error])
+        )
+
+    for row in preview.rows:
+        if row.status == STATUS_READY:
+            try:
+                existing_user = find_existing_email_user(row.email)
+                if existing_user and role_for_user(existing_user) == AccountRole.COACH:
+                    result_rows.append(
+                        reuse_existing_coach(
+                            replace(row, existing_user_id=existing_user.id), season
+                        )
+                    )
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
+                            messages=[
+                                "Email belongs to an existing non-coach account."
+                            ],
+                        )
+                    )
+                else:
+                    result_rows.append(create_coach(row, season))
+            except ValidationError as exc:
+                result_rows.append(
+                    CoachImportResultRow(
+                        row_number=row.row_number,
+                        status=RESULT_ERROR,
+                        messages=list(exc.messages),
+                    )
+                )
+        elif row.status == STATUS_REUSE:
+            try:
+                result_rows.append(reuse_existing_coach(row, season))
+            except ValidationError as exc:
+                result_rows.append(
+                    CoachImportResultRow(
+                        row_number=row.row_number,
+                        status=RESULT_ERROR,
+                        messages=list(exc.messages),
+                    )
+                )
+        elif row.status == STATUS_CONFLICT:
+            result_rows.append(
+                CoachImportResultRow(
+                    row_number=row.row_number,
+                    status=RESULT_CONFLICT,
+                    username=row.final_username,
+                    user_id=row.existing_user_id,
+                    season_name=season.name if season else "",
+                    team=row.team,
+                    division=row.division,
+                    assignment_role_label=row.assignment_role_label,
+                    password_behavior="Password unchanged",
+                    messages=row.messages,
+                )
+            )
+        else:
+            result_rows.append(
+                CoachImportResultRow(
+                    row_number=row.row_number,
+                    status=RESULT_ERROR,
+                    username=row.final_username,
+                    season_name=season.name if season else "",
+                    team=row.team,
+                    division=row.division,
+                    assignment_role_label=row.assignment_role_label,
+                    messages=row.messages,
+                )
+            )
+
+    return CoachImportResult(
+        rows=result_rows,
+        season_id=season.id if season else None,
+        season_name=season.name if season else "",
+    )
diff --git a/accounts/services/coach_import/constants.py b/accounts/services/coach_import/constants.py
new file mode 100644
index 0000000..06ff949
--- /dev/null
+++ b/accounts/services/coach_import/constants.py
@@ -0,0 +1,43 @@
+"""Constants for the staff coach import workflow."""
+
+from seasons.models import CoachAssignmentRole
+
+REQUIRED_COLUMNS = {"first_name", "last_name", "email"}
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
+SUPPORTED_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS
+
+STATUS_READY = "ready"
+STATUS_REUSE = "reuse"
+STATUS_CONFLICT = "conflict"
+STATUS_ERROR = "error"
+
+RESULT_CREATED = "created"
+RESULT_REUSED = "reused"
+RESULT_CONFLICT = "conflict"
+RESULT_ERROR = "error"
+RESULT_SKIPPED = "skipped"
+
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
diff --git a/accounts/services/coach_import/matching.py b/accounts/services/coach_import/matching.py
new file mode 100644
index 0000000..eb78ddf
--- /dev/null
+++ b/accounts/services/coach_import/matching.py
@@ -0,0 +1,10 @@
+"""Account matching helpers for coach imports."""
+
+from accounts.services.profile_service import get_or_create_account_profile
+
+
+def role_for_user(user) -> str:
+    profile = getattr(user, "account_profile", None)
+    if profile:
+        return profile.role
+    return get_or_create_account_profile(user).role
diff --git a/accounts/services/coach_import/parsing.py b/accounts/services/coach_import/parsing.py
new file mode 100644
index 0000000..05cf4f7
--- /dev/null
+++ b/accounts/services/coach_import/parsing.py
@@ -0,0 +1,88 @@
+"""CSV and primitive parsing helpers for coach imports."""
+
+from __future__ import annotations
+
+import csv
+from datetime import datetime
+from io import StringIO
+
+from django.core.exceptions import ValidationError
+
+from accounts.services.coach_import.constants import (
+    REQUIRED_COLUMNS,
+    ROLE_ALIASES,
+    SUPPORTED_COLUMNS,
+)
+from seasons.models import CoachAssignmentRole
+
+
+def parse_bool(value, default=True) -> bool:
+    text = str(value or "").strip().casefold()
+    if not text:
+        return default
+    if text in {"1", "true", "yes", "y", "active"}:
+        return True
+    if text in {"0", "false", "no", "n", "inactive"}:
+        return False
+    raise ValidationError("is_active must be true or false.")
+
+
+def normalize_header(header: str) -> str:
+    return str(header or "").strip().casefold().replace(" ", "_")
+
+
+def parse_assignment_role(value: str) -> str:
+    normalized = normalize_header(value).replace("_", " ")
+    if normalized in ROLE_ALIASES:
+        return ROLE_ALIASES[normalized]
+    raise ValidationError(f"Unknown assignment role '{str(value or '').strip()}'.")
+
+
+def assignment_role_label(value: str) -> str:
+    return CoachAssignmentRole(value).label
+
+
+def parse_import_date(value: str):
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
+def decode_csv_file(uploaded_file) -> str:
+    uploaded_file.seek(0)
+    raw = uploaded_file.read()
+    if isinstance(raw, str):
+        return raw
+    try:
+        return raw.decode("utf-8-sig")
+    except UnicodeDecodeError as exc:
+        raise ValidationError("Coach import CSV must be UTF-8 encoded.") from exc
+
+
+def read_csv(csv_text: str) -> tuple[list[str], list[dict[str, str]]]:
+    reader = csv.DictReader(StringIO(csv_text))
+    headers = [normalize_header(header) for header in (reader.fieldnames or [])]
+    missing = sorted(REQUIRED_COLUMNS - set(headers))
+    if missing:
+        raise ValidationError(f"Missing required column(s): {', '.join(missing)}.")
+
+    rows = []
+    for raw_row in reader:
+        normalized_row = {}
+        for header, value in raw_row.items():
+            normalized_header = normalize_header(header)
+            if normalized_header in SUPPORTED_COLUMNS:
+                normalized_row[normalized_header] = str(value or "").strip()
+        rows.append(normalized_row)
+    return headers, rows
+
+
+def season_matches(row_value: str, season) -> bool:
+    normalized = str(row_value or "").strip().casefold()
+    return normalized in {season.key.casefold(), season.name.casefold()}
diff --git a/accounts/services/coach_import/preview.py b/accounts/services/coach_import/preview.py
new file mode 100644
index 0000000..95e204a
--- /dev/null
+++ b/accounts/services/coach_import/preview.py
@@ -0,0 +1,331 @@
+"""Preview construction for staff coach imports."""
+
+from __future__ import annotations
+
+from dataclasses import replace
+
+from django.core.exceptions import ValidationError
+
+from accounts.models import AccountRole
+from accounts.services.coach_import.assignment import (
+    assignment_preview,
+    season_team_preview,
+)
+from accounts.services.coach_import.constants import (
+    STATUS_CONFLICT,
+    STATUS_ERROR,
+    STATUS_READY,
+    STATUS_REUSE,
+)
+from accounts.services.coach_import.matching import role_for_user
+from accounts.services.coach_import.parsing import (
+    assignment_role_label,
+    decode_csv_file,
+    parse_assignment_role,
+    parse_bool,
+    parse_import_date,
+    read_csv,
+    season_matches,
+)
+from accounts.services.coach_import.result_models import (
+    CoachImportPreview,
+    CoachImportRowPreview,
+)
+from accounts.services.email_service import find_existing_email_user, normalize_email
+from accounts.services.username_service import (
+    username_for_person,
+    validate_available_username,
+)
+from seasons.models import Season
+
+
+def preview_row(
+    row_number: int, row: dict[str, str], season: Season
+) -> CoachImportRowPreview:
+    messages = []
+    first_name = row.get("first_name", "").strip()
+    last_name = row.get("last_name", "").strip()
+    email = normalize_email(row.get("email", ""))
+    explicit_username = row.get("username", "").strip()
+    team = row.get("team", "").strip()
+    division = row.get("division", "").strip()
+    notes = row.get("notes", "").strip()
+    source_id = row.get("source_id", "").strip()
+    assignment_source_id = row.get("assignment_source_id", "").strip() or source_id
+    starts_raw = row.get("assignment_start_date", "").strip()
+    ends_raw = row.get("assignment_end_date", "").strip()
+
+    try:
+        is_active = parse_bool(row.get("is_active", ""), default=True)
+        assignment_role = parse_assignment_role(row.get("assignment_role", ""))
+        starts_on = parse_import_date(starts_raw)
+        ends_on = parse_import_date(ends_raw)
+    except ValidationError as exc:
+        return CoachImportRowPreview(
+            row_number=row_number, status=STATUS_ERROR, messages=list(exc.messages)
+        )
+    if starts_on and ends_on and ends_on < starts_on:
+        return CoachImportRowPreview(
+            row_number=row_number,
+            status=STATUS_ERROR,
+            messages=["Assignment end date cannot be before start date."],
+        )
+
+    season_value = row.get("season", "").strip()
+    if season_value and not season_matches(season_value, season):
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
+            assignment_role_label=assignment_role_label(assignment_role),
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
+    if missing_fields:
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
+            assignment_role_label=assignment_role_label(assignment_role),
+            assignment_start_date=starts_raw,
+            assignment_end_date=ends_raw,
+            assignment_source_id=assignment_source_id,
+            status=STATUS_ERROR,
+            messages=[f"Missing required field(s): {', '.join(missing_fields)}."],
+        )
+
+    existing_email_user = find_existing_email_user(email)
+    season_team_action, season_team_label = season_team_preview(
+        season=season, team=team, division=division
+    )
+    if existing_email_user:
+        existing_role = role_for_user(existing_email_user)
+        if existing_role == AccountRole.COACH:
+            assignment_action, assignment_label = assignment_preview(
+                user=existing_email_user,
+                season=season,
+                team=team,
+                division=division,
+                assignment_role=assignment_role,
+                is_active=is_active,
+            )
+            return CoachImportRowPreview(
+                row_number=row_number,
+                first_name=first_name,
+                last_name=last_name,
+                email=email,
+                username=existing_email_user.username,
+                team=team,
+                division=division,
+                is_active=is_active,
+                notes=notes,
+                source_id=source_id,
+                assignment_role=assignment_role,
+                assignment_role_label=assignment_role_label(assignment_role),
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
+                status=STATUS_REUSE,
+                messages=[
+                    "Existing coach account will be reused.",
+                    "Password unchanged.",
+                ],
+                existing_user_id=existing_email_user.id,
+            )
+        return CoachImportRowPreview(
+            row_number=row_number,
+            first_name=first_name,
+            last_name=last_name,
+            email=email,
+            username=existing_email_user.username,
+            team=team,
+            division=division,
+            is_active=is_active,
+            notes=notes,
+            source_id=source_id,
+            assignment_role=assignment_role,
+            assignment_role_label=assignment_role_label(assignment_role),
+            assignment_start_date=starts_raw,
+            assignment_end_date=ends_raw,
+            assignment_source_id=assignment_source_id,
+            season_team_action=season_team_action,
+            season_team_label=season_team_label,
+            account_action="conflict",
+            account_label="Account Role Conflict",
+            password_behavior="Password unchanged",
+            status=STATUS_CONFLICT,
+            messages=["Email belongs to an existing non-coach account."],
+            existing_user_id=existing_email_user.id,
+        )
+
+    try:
+        username = (
+            validate_available_username(explicit_username) if explicit_username else ""
+        )
+        generated_username = (
+            "" if username else username_for_person(first_name, last_name)
+        )
+    except ValidationError as exc:
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
+            assignment_role_label=assignment_role_label(assignment_role),
+            assignment_start_date=starts_raw,
+            assignment_end_date=ends_raw,
+            assignment_source_id=assignment_source_id,
+            season_team_action=season_team_action,
+            season_team_label=season_team_label,
+            status=STATUS_CONFLICT,
+            messages=list(exc.messages),
+        )
+
+    return CoachImportRowPreview(
+        row_number=row_number,
+        first_name=first_name,
+        last_name=last_name,
+        email=email,
+        username=username,
+        generated_username=generated_username,
+        team=team,
+        division=division,
+        is_active=is_active,
+        notes=notes,
+        source_id=source_id,
+        assignment_role=assignment_role,
+        assignment_role_label=assignment_role_label(assignment_role),
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
+        status=STATUS_READY,
+        messages=messages,
+    )
+
+
+def preview_coach_import(
+    csv_text: str, season: Season | None = None
+) -> CoachImportPreview:
+    """Return a non-persistent preview for a coach CSV import."""
+    if season is None:
+        return CoachImportPreview(
+            rows=[],
+            headers=[],
+            row_errors=["Select an active season for this coach import."],
+        )
+    if not season.is_active:
+        return CoachImportPreview(
+            rows=[],
+            headers=[],
+            row_errors=["Select an active season for this coach import."],
+        )
+    try:
+        headers, rows = read_csv(csv_text)
+    except ValidationError as exc:
+        return CoachImportPreview(
+            rows=[],
+            headers=[],
+            row_errors=list(exc.messages),
+            season_id=season.id,
+            season_name=season.name,
+        )
+
+    preview_rows = []
+    seen_emails = set()
+    username_owner_email = {}
+    for index, row in enumerate(rows, start=2):
+        row_preview = preview_row(index, row, season)
+        if row_preview.email:
+            if (
+                row_preview.email in seen_emails
+                and row_preview.status == STATUS_CONFLICT
+            ):
+                row_preview = replace(
+                    row_preview,
+                    status=STATUS_CONFLICT,
+                    messages=[
+                        *row_preview.messages,
+                        "Email appears more than once in this CSV.",
+                    ],
+                )
+            seen_emails.add(row_preview.email)
+        final_username = row_preview.final_username
+        if row_preview.status == STATUS_READY and final_username:
+            owner_email = username_owner_email.get(final_username)
+            if owner_email and owner_email != row_preview.email:
+                row_preview = replace(
+                    row_preview,
+                    status=STATUS_CONFLICT,
+                    messages=[
+                        *row_preview.messages,
+                        "Username appears more than once in this CSV.",
+                    ],
+                )
+            username_owner_email[final_username] = row_preview.email
+        preview_rows.append(row_preview)
+    return CoachImportPreview(
+        rows=preview_rows,
+        headers=headers,
+        row_errors=[],
+        season_id=season.id,
+        season_name=season.name,
+    )
+
+
+def preview_coach_import_file(
+    uploaded_file, season: Season | None = None
+) -> CoachImportPreview:
+    """Read an uploaded CSV file and return a coach import preview."""
+    return preview_coach_import(decode_csv_file(uploaded_file), season=season)
diff --git a/accounts/services/coach_import/result_models.py b/accounts/services/coach_import/result_models.py
new file mode 100644
index 0000000..b3ec7c4
--- /dev/null
+++ b/accounts/services/coach_import/result_models.py
@@ -0,0 +1,195 @@
+"""Data contracts for coach import preview and commit results."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+
+from accounts.services.coach_import.constants import (
+    RESULT_CONFLICT,
+    RESULT_CREATED,
+    RESULT_ERROR,
+    RESULT_REUSED,
+    RESULT_SKIPPED,
+    STATUS_CONFLICT,
+    STATUS_ERROR,
+    STATUS_READY,
+    STATUS_REUSE,
+)
+from seasons.models import CoachAssignmentRole
+
+
+@dataclass(frozen=True)
+class CoachImportRowPreview:
+    row_number: int
+    first_name: str = ""
+    last_name: str = ""
+    email: str = ""
+    username: str = ""
+    generated_username: str = ""
+    team: str = ""
+    division: str = ""
+    is_active: bool = True
+    notes: str = ""
+    source_id: str = ""
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
+    status: str = STATUS_READY
+    messages: list[str] = field(default_factory=list)
+    existing_user_id: int | None = None
+
+    @property
+    def final_username(self) -> str:
+        return self.username or self.generated_username
+
+    @property
+    def can_commit(self) -> bool:
+        return self.status in {STATUS_READY, STATUS_REUSE}
+
+
+@dataclass(frozen=True)
+class CoachImportPreview:
+    rows: list[CoachImportRowPreview]
+    headers: list[str]
+    row_errors: list[str]
+    season_id: int | None = None
+    season_name: str = ""
+
+    @property
+    def rows_processed(self) -> int:
+        return len(self.rows)
+
+    @property
+    def ready_count(self) -> int:
+        return sum(1 for row in self.rows if row.status == STATUS_READY)
+
+    @property
+    def reuse_count(self) -> int:
+        return sum(1 for row in self.rows if row.status == STATUS_REUSE)
+
+    @property
+    def conflict_count(self) -> int:
+        return sum(1 for row in self.rows if row.status == STATUS_CONFLICT)
+
+    @property
+    def error_count(self) -> int:
+        return len(self.row_errors) + sum(
+            1 for row in self.rows if row.status == STATUS_ERROR
+        )
+
+    @property
+    def can_confirm(self) -> bool:
+        return any(row.can_commit for row in self.rows)
+
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
+        return sum(
+            1 for row in self.rows if row.assignment_action in {"update", "reuse"}
+        )
+
+
+@dataclass(frozen=True)
+class CoachImportResultRow:
+    row_number: int
+    status: str
+    username: str = ""
+    user_id: int | None = None
+    is_active: bool = False
+    temporary_password: str = field(default="", repr=False)
+    season_name: str = ""
+    team: str = ""
+    division: str = ""
+    assignment_role_label: str = ""
+    assignment_status: str = ""
+    password_behavior: str = ""
+    messages: list[str] = field(default_factory=list)
+
+
+@dataclass(frozen=True)
+class CoachImportResult:
+    rows: list[CoachImportResultRow]
+    season_id: int | None = None
+    season_name: str = ""
+
+    @property
+    def rows_processed(self) -> int:
+        return len(self.rows)
+
+    @property
+    def users_created(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_CREATED)
+
+    @property
+    def existing_coaches_reused(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_REUSED)
+
+    @property
+    def conflicts(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_CONFLICT)
+
+    @property
+    def errors(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_ERROR)
+
+    @property
+    def skipped_rows(self) -> int:
+        return sum(1 for row in self.rows if row.status == RESULT_SKIPPED)
+
+    @property
+    def active_accounts(self) -> int:
+        return sum(
+            1
+            for row in self.rows
+            if row.status in {RESULT_CREATED, RESULT_REUSED} and row.is_active
+        )
+
+    @property
+    def inactive_accounts(self) -> int:
+        return sum(
+            1
+            for row in self.rows
+            if row.status in {RESULT_CREATED, RESULT_REUSED} and not row.is_active
+        )
+
+    @property
+    def password_change_required(self) -> int:
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
+        return sum(
+            1 for row in self.rows if row.assignment_status in {"updated", "reused"}
+        )
diff --git a/accounts/services/coach_import_service.py b/accounts/services/coach_import_service.py
index a587da1..71050bd 100644
--- a/accounts/services/coach_import_service.py
+++ b/accounts/services/coach_import_service.py
@@ -1,792 +1,56 @@
-from __future__ import annotations
-
-import csv
-from dataclasses import dataclass, field, replace
-from datetime import datetime
-from io import StringIO
-
-from django.contrib.auth import get_user_model
-from django.core.exceptions import ValidationError
-from django.db import transaction
-
-from accounts.models import AccountRole
-from accounts.services.email_service import find_existing_email_user, normalize_email
-from accounts.services.password_service import set_random_temporary_password
-from accounts.services.permissions import can_manage_accounts
-from accounts.services.profile_service import get_or_create_account_profile, set_account_role
-from accounts.services.username_service import validate_available_username, username_for_person
-from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, Season, SeasonTeam
-from seasons.services.coach_assignment_service import create_assignment, get_primary_assignment, update_assignment
-from seasons.services.team_service import get_or_create_season_team, normalize_division_value, normalize_team_value
-
-
-User = get_user_model()
-
-REQUIRED_COLUMNS = {"first_name", "last_name", "email"}
-OPTIONAL_COLUMNS = {
-    "username",
-    "team",
-    "division",
-    "is_active",
-    "notes",
-    "source_id",
-    "season",
-    "assignment_role",
-    "assignment_start_date",
-    "assignment_end_date",
-    "assignment_source_id",
-}
-SUPPORTED_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS
-
-STATUS_READY = "ready"
-STATUS_REUSE = "reuse"
-STATUS_CONFLICT = "conflict"
-STATUS_ERROR = "error"
-
-RESULT_CREATED = "created"
-RESULT_REUSED = "reused"
-RESULT_CONFLICT = "conflict"
-RESULT_ERROR = "error"
-RESULT_SKIPPED = "skipped"
-
-
-@dataclass(frozen=True)
-class CoachImportRowPreview:
-    row_number: int
-    first_name: str = ""
-    last_name: str = ""
-    email: str = ""
-    username: str = ""
-    generated_username: str = ""
-    team: str = ""
-    division: str = ""
-    is_active: bool = True
-    notes: str = ""
-    source_id: str = ""
-    assignment_role: str = CoachAssignmentRole.ASSISTANT_COACH
-    assignment_role_label: str = CoachAssignmentRole.ASSISTANT_COACH.label
-    assignment_start_date: str = ""
-    assignment_end_date: str = ""
-    assignment_source_id: str = ""
-    season_team_action: str = ""
-    season_team_label: str = ""
-    assignment_action: str = ""
-    assignment_label: str = ""
-    account_action: str = ""
-    account_label: str = ""
-    password_behavior: str = ""
-    status: str = STATUS_READY
-    messages: list[str] = field(default_factory=list)
-    existing_user_id: int | None = None
-
-    @property
-    def final_username(self) -> str:
-        return self.username or self.generated_username
-
-    @property
-    def can_commit(self) -> bool:
-        return self.status in {STATUS_READY, STATUS_REUSE}
-
-
-@dataclass(frozen=True)
-class CoachImportPreview:
-    rows: list[CoachImportRowPreview]
-    headers: list[str]
-    row_errors: list[str]
-    season_id: int | None = None
-    season_name: str = ""
-
-    @property
-    def rows_processed(self) -> int:
-        return len(self.rows)
-
-    @property
-    def ready_count(self) -> int:
-        return sum(1 for row in self.rows if row.status == STATUS_READY)
-
-    @property
-    def reuse_count(self) -> int:
-        return sum(1 for row in self.rows if row.status == STATUS_REUSE)
-
-    @property
-    def conflict_count(self) -> int:
-        return sum(1 for row in self.rows if row.status == STATUS_CONFLICT)
-
-    @property
-    def error_count(self) -> int:
-        return len(self.row_errors) + sum(1 for row in self.rows if row.status == STATUS_ERROR)
-
-    @property
-    def can_confirm(self) -> bool:
-        return any(row.can_commit for row in self.rows)
-
-    @property
-    def season_teams_create(self) -> int:
-        return sum(1 for row in self.rows if row.season_team_action == "create")
-
-    @property
-    def season_teams_reuse(self) -> int:
-        return sum(1 for row in self.rows if row.season_team_action == "reuse")
-
-    @property
-    def assignments_create(self) -> int:
-        return sum(1 for row in self.rows if row.assignment_action == "create")
-
-    @property
-    def assignments_update(self) -> int:
-        return sum(1 for row in self.rows if row.assignment_action in {"update", "reuse"})
-
-
-@dataclass(frozen=True)
-class CoachImportResultRow:
-    row_number: int
-    status: str
-    username: str = ""
-    user_id: int | None = None
-    is_active: bool = False
-    temporary_password: str = field(default="", repr=False)
-    season_name: str = ""
-    team: str = ""
-    division: str = ""
-    assignment_role_label: str = ""
-    assignment_status: str = ""
-    password_behavior: str = ""
-    messages: list[str] = field(default_factory=list)
-
-
-@dataclass(frozen=True)
-class CoachImportResult:
-    rows: list[CoachImportResultRow]
-    season_id: int | None = None
-    season_name: str = ""
-
-    @property
-    def rows_processed(self) -> int:
-        return len(self.rows)
-
-    @property
-    def users_created(self) -> int:
-        return sum(1 for row in self.rows if row.status == RESULT_CREATED)
-
-    @property
-    def existing_coaches_reused(self) -> int:
-        return sum(1 for row in self.rows if row.status == RESULT_REUSED)
-
-    @property
-    def conflicts(self) -> int:
-        return sum(1 for row in self.rows if row.status == RESULT_CONFLICT)
-
-    @property
-    def errors(self) -> int:
-        return sum(1 for row in self.rows if row.status == RESULT_ERROR)
-
-    @property
-    def skipped_rows(self) -> int:
-        return sum(1 for row in self.rows if row.status == RESULT_SKIPPED)
-
-    @property
-    def active_accounts(self) -> int:
-        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and row.is_active)
-
-    @property
-    def inactive_accounts(self) -> int:
-        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and not row.is_active)
-
-    @property
-    def password_change_required(self) -> int:
-        return sum(1 for row in self.rows if row.status == RESULT_CREATED)
-
-    @property
-    def season_teams_created(self) -> int:
-        return sum(1 for row in self.rows if "season team created" in row.messages)
-
-    @property
-    def season_teams_reused(self) -> int:
-        return sum(1 for row in self.rows if "season team reused" in row.messages)
-
-    @property
-    def assignments_created(self) -> int:
-        return sum(1 for row in self.rows if row.assignment_status == "created")
-
-    @property
-    def assignments_updated(self) -> int:
-        return sum(1 for row in self.rows if row.assignment_status in {"updated", "reused"})
-
-
-def _validate_actor(actor) -> None:
-    if not can_manage_accounts(actor):
-        raise ValidationError("Only staff users can import coaches.")
-
-
-def _parse_bool(value, default=True) -> bool:
-    text = str(value or "").strip().casefold()
-    if not text:
-        return default
-    if text in {"1", "true", "yes", "y", "active"}:
-        return True
-    if text in {"0", "false", "no", "n", "inactive"}:
-        return False
-    raise ValidationError("is_active must be true or false.")
-
-
-ROLE_ALIASES = {
-    "": CoachAssignmentRole.ASSISTANT_COACH,
-    "assistant": CoachAssignmentRole.ASSISTANT_COACH,
-    "assistant coach": CoachAssignmentRole.ASSISTANT_COACH,
-    "assistant_coach": CoachAssignmentRole.ASSISTANT_COACH,
-    "head": CoachAssignmentRole.HEAD_COACH,
-    "head coach": CoachAssignmentRole.HEAD_COACH,
-    "head_coach": CoachAssignmentRole.HEAD_COACH,
-    "manager": CoachAssignmentRole.MANAGER,
-    "coordinator": CoachAssignmentRole.COORDINATOR,
-    "evaluator": CoachAssignmentRole.EVALUATOR,
-}
-
-
-def _parse_assignment_role(value: str) -> str:
-    normalized = _normalize_header(value).replace("_", " ")
-    if normalized in ROLE_ALIASES:
-        return ROLE_ALIASES[normalized]
-    raise ValidationError(f"Unknown assignment role '{str(value or '').strip()}'.")
-
-
-def _assignment_role_label(value: str) -> str:
-    return CoachAssignmentRole(value).label
-
-
-def _parse_import_date(value: str):
-    cleaned = str(value or "").strip()
-    if not cleaned:
-        return None
-    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
-        try:
-            return datetime.strptime(cleaned, fmt).date()
-        except ValueError:
-            continue
-    raise ValidationError("Assignment date is invalid.")
-
-
-def _decode_csv_file(uploaded_file) -> str:
-    uploaded_file.seek(0)
-    raw = uploaded_file.read()
-    if isinstance(raw, str):
-        return raw
-    try:
-        return raw.decode("utf-8-sig")
-    except UnicodeDecodeError as exc:
-        raise ValidationError("Coach import CSV must be UTF-8 encoded.") from exc
-
-
-def _normalize_header(header: str) -> str:
-    return str(header or "").strip().casefold().replace(" ", "_")
-
-
-def _read_csv(csv_text: str) -> tuple[list[str], list[dict[str, str]]]:
-    reader = csv.DictReader(StringIO(csv_text))
-    headers = [_normalize_header(header) for header in (reader.fieldnames or [])]
-    missing = sorted(REQUIRED_COLUMNS - set(headers))
-    if missing:
-        raise ValidationError(f"Missing required column(s): {', '.join(missing)}.")
-
-    rows = []
-    for raw_row in reader:
-        normalized_row = {}
-        for header, value in raw_row.items():
-            normalized_header = _normalize_header(header)
-            if normalized_header in SUPPORTED_COLUMNS:
-                normalized_row[normalized_header] = str(value or "").strip()
-        rows.append(normalized_row)
-    return headers, rows
-
-
-def _role_for_user(user) -> str:
-    profile = getattr(user, "account_profile", None)
-    if profile:
-        return profile.role
-    return get_or_create_account_profile(user).role
-
-
-def _season_matches(row_value: str, season: Season) -> bool:
-    normalized = str(row_value or "").strip().casefold()
-    return normalized in {season.key.casefold(), season.name.casefold()}
-
-
-def _season_team_preview(*, season: Season, team: str, division: str) -> tuple[str, str]:
-    normalized_team = normalize_team_value(team)
-    normalized_division = normalize_division_value(division)
-    existing = SeasonTeam.objects.filter(
-        season=season,
-        normalized_name=normalized_team,
-        normalized_division=normalized_division,
-    ).first()
-    if existing:
-        return "reuse", "Reuse Season Team"
-    return "create", "Create Season Team"
-
-
-def _assignment_preview(*, user, season: Season, team: str, division: str, assignment_role: str, is_active: bool) -> tuple[str, str]:
-    if not user:
-        return "create", "Create Assignment"
-    normalized_team = normalize_team_value(team)
-    normalized_division = normalize_division_value(division)
-    existing = CoachSeasonAssignment.objects.select_related("season_team").filter(
-        user=user,
-        season_team__season=season,
-        season_team__normalized_name=normalized_team,
-        season_team__normalized_division=normalized_division,
-        assignment_role=assignment_role,
-    ).first()
-    if existing:
-        return "update", "Update Assignment" if is_active else "Update Inactive Assignment"
-    return "create", "Create Assignment"
-
-
-def _preview_row(row_number: int, row: dict[str, str], season: Season) -> CoachImportRowPreview:
-    messages = []
-    first_name = row.get("first_name", "").strip()
-    last_name = row.get("last_name", "").strip()
-    email = normalize_email(row.get("email", ""))
-    explicit_username = row.get("username", "").strip()
-    team = row.get("team", "").strip()
-    division = row.get("division", "").strip()
-    notes = row.get("notes", "").strip()
-    source_id = row.get("source_id", "").strip()
-    assignment_source_id = row.get("assignment_source_id", "").strip() or source_id
-    starts_raw = row.get("assignment_start_date", "").strip()
-    ends_raw = row.get("assignment_end_date", "").strip()
-
-    try:
-        is_active = _parse_bool(row.get("is_active", ""), default=True)
-        assignment_role = _parse_assignment_role(row.get("assignment_role", ""))
-        starts_on = _parse_import_date(starts_raw)
-        ends_on = _parse_import_date(ends_raw)
-    except ValidationError as exc:
-        return CoachImportRowPreview(row_number=row_number, status=STATUS_ERROR, messages=list(exc.messages))
-    if starts_on and ends_on and ends_on < starts_on:
-        return CoachImportRowPreview(row_number=row_number, status=STATUS_ERROR, messages=["Assignment end date cannot be before start date."])
-
-    season_value = row.get("season", "").strip()
-    if season_value and not _season_matches(season_value, season):
-        return CoachImportRowPreview(
-            row_number=row_number,
-            first_name=first_name,
-            last_name=last_name,
-            email=email,
-            username=explicit_username,
-            team=team,
-            division=division,
-            is_active=is_active,
-            notes=notes,
-            source_id=source_id,
-            assignment_role=assignment_role,
-            assignment_role_label=_assignment_role_label(assignment_role),
-            assignment_start_date=starts_raw,
-            assignment_end_date=ends_raw,
-            assignment_source_id=assignment_source_id,
-            status=STATUS_ERROR,
-            messages=["CSV season does not match the selected import season."],
-        )
-
-    missing_fields = [
-        label
-        for label, value in [
-            ("first_name", first_name),
-            ("last_name", last_name),
-            ("email", email),
-            ("team", team),
-            ("division", division),
-        ]
-        if not value
-    ]
-    if missing_fields:
-        return CoachImportRowPreview(
-            row_number=row_number,
-            first_name=first_name,
-            last_name=last_name,
-            email=email,
-            username=explicit_username,
-            team=team,
-            division=division,
-            is_active=is_active,
-            notes=notes,
-            source_id=source_id,
-            assignment_role=assignment_role,
-            assignment_role_label=_assignment_role_label(assignment_role),
-            assignment_start_date=starts_raw,
-            assignment_end_date=ends_raw,
-            assignment_source_id=assignment_source_id,
-            status=STATUS_ERROR,
-            messages=[f"Missing required field(s): {', '.join(missing_fields)}."],
-        )
-
-    existing_email_user = find_existing_email_user(email)
-    season_team_action, season_team_label = _season_team_preview(season=season, team=team, division=division)
-    if existing_email_user:
-        existing_role = _role_for_user(existing_email_user)
-        if existing_role == AccountRole.COACH:
-            assignment_action, assignment_label = _assignment_preview(
-                user=existing_email_user,
-                season=season,
-                team=team,
-                division=division,
-                assignment_role=assignment_role,
-                is_active=is_active,
-            )
-            return CoachImportRowPreview(
-                row_number=row_number,
-                first_name=first_name,
-                last_name=last_name,
-                email=email,
-                username=existing_email_user.username,
-                team=team,
-                division=division,
-                is_active=is_active,
-                notes=notes,
-                source_id=source_id,
-                assignment_role=assignment_role,
-                assignment_role_label=_assignment_role_label(assignment_role),
-                assignment_start_date=starts_raw,
-                assignment_end_date=ends_raw,
-                assignment_source_id=assignment_source_id,
-                season_team_action=season_team_action,
-                season_team_label=season_team_label,
-                assignment_action=assignment_action,
-                assignment_label=assignment_label,
-                account_action="reuse",
-                account_label="Reuse Coach Account",
-                password_behavior="Password unchanged",
-                status=STATUS_REUSE,
-                messages=["Existing coach account will be reused.", "Password unchanged."],
-                existing_user_id=existing_email_user.id,
-            )
-        return CoachImportRowPreview(
-            row_number=row_number,
-            first_name=first_name,
-            last_name=last_name,
-            email=email,
-            username=existing_email_user.username,
-            team=team,
-            division=division,
-            is_active=is_active,
-            notes=notes,
-            source_id=source_id,
-            assignment_role=assignment_role,
-            assignment_role_label=_assignment_role_label(assignment_role),
-            assignment_start_date=starts_raw,
-            assignment_end_date=ends_raw,
-            assignment_source_id=assignment_source_id,
-            season_team_action=season_team_action,
-            season_team_label=season_team_label,
-            account_action="conflict",
-            account_label="Account Role Conflict",
-            password_behavior="Password unchanged",
-            status=STATUS_CONFLICT,
-            messages=["Email belongs to an existing non-coach account."],
-            existing_user_id=existing_email_user.id,
-        )
-
-    try:
-        username = validate_available_username(explicit_username) if explicit_username else ""
-        generated_username = "" if username else username_for_person(first_name, last_name)
-    except ValidationError as exc:
-        return CoachImportRowPreview(
-            row_number=row_number,
-            first_name=first_name,
-            last_name=last_name,
-            email=email,
-            username=explicit_username,
-            team=team,
-            division=division,
-            is_active=is_active,
-            notes=notes,
-            source_id=source_id,
-            assignment_role=assignment_role,
-            assignment_role_label=_assignment_role_label(assignment_role),
-            assignment_start_date=starts_raw,
-            assignment_end_date=ends_raw,
-            assignment_source_id=assignment_source_id,
-            season_team_action=season_team_action,
-            season_team_label=season_team_label,
-            status=STATUS_CONFLICT,
-            messages=list(exc.messages),
-        )
-
-    return CoachImportRowPreview(
-        row_number=row_number,
-        first_name=first_name,
-        last_name=last_name,
-        email=email,
-        username=username,
-        generated_username=generated_username,
-        team=team,
-        division=division,
-        is_active=is_active,
-        notes=notes,
-        source_id=source_id,
-        assignment_role=assignment_role,
-        assignment_role_label=_assignment_role_label(assignment_role),
-        assignment_start_date=starts_raw,
-        assignment_end_date=ends_raw,
-        assignment_source_id=assignment_source_id,
-        season_team_action=season_team_action,
-        season_team_label=season_team_label,
-        assignment_action="create",
-        assignment_label="Create Assignment",
-        account_action="create",
-        account_label="Create Coach Account",
-        password_behavior="Temporary password will be generated",
-        status=STATUS_READY,
-        messages=messages,
-    )
-
-
-def preview_coach_import(csv_text: str, season: Season | None = None) -> CoachImportPreview:
-    """Return a non-persistent preview for a coach CSV import."""
-    if season is None:
-        return CoachImportPreview(rows=[], headers=[], row_errors=["Select an active season for this coach import."])
-    if not season.is_active:
-        return CoachImportPreview(rows=[], headers=[], row_errors=["Select an active season for this coach import."])
-    try:
-        headers, rows = _read_csv(csv_text)
-    except ValidationError as exc:
-        return CoachImportPreview(rows=[], headers=[], row_errors=list(exc.messages), season_id=season.id, season_name=season.name)
-
-    preview_rows = []
-    seen_emails = set()
-    username_owner_email = {}
-    for index, row in enumerate(rows, start=2):
-        preview_row = _preview_row(index, row, season)
-        if preview_row.email:
-            if preview_row.email in seen_emails and preview_row.status == STATUS_CONFLICT:
-                preview_row = replace(
-                    preview_row,
-                    status=STATUS_CONFLICT,
-                    messages=[*preview_row.messages, "Email appears more than once in this CSV."],
-                )
-            seen_emails.add(preview_row.email)
-        final_username = preview_row.final_username
-        if preview_row.status == STATUS_READY and final_username:
-            owner_email = username_owner_email.get(final_username)
-            if owner_email and owner_email != preview_row.email:
-                preview_row = replace(
-                    preview_row,
-                    status=STATUS_CONFLICT,
-                    messages=[*preview_row.messages, "Username appears more than once in this CSV."],
-                )
-            username_owner_email[final_username] = preview_row.email
-        preview_rows.append(preview_row)
-    return CoachImportPreview(rows=preview_rows, headers=headers, row_errors=[], season_id=season.id, season_name=season.name)
-
-
-def preview_coach_import_file(uploaded_file, season: Season | None = None) -> CoachImportPreview:
-    """Read an uploaded CSV file and return a coach import preview."""
-    return preview_coach_import(_decode_csv_file(uploaded_file), season=season)
-
-
-def _metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
-    return {
-        key: value
-        for key, value in {
-            "team": row.team,
-            "division": row.division,
-            "notes": row.notes,
-            "source_id": row.source_id,
-            "assignment_role": row.assignment_role,
-            "source": "coach_roster",
-        }.items()
-        if value
-    }
-
-
-def _profile_metadata(profile) -> dict:
-    return profile.metadata if isinstance(profile.metadata, dict) else {}
-
-
-@transaction.atomic
-def _commit_assignment(user, row: CoachImportRowPreview, season: Season) -> tuple[str, bool]:
-    season_team, team_created = get_or_create_season_team(
-        season=season,
-        name=row.team,
-        division=row.division,
-        metadata={"source": "coach_roster"},
-    )
-    assignment = CoachSeasonAssignment.objects.select_for_update().filter(
-        user=user,
-        season_team=season_team,
-        assignment_role=row.assignment_role,
-    ).first()
-    starts_on = _parse_import_date(row.assignment_start_date)
-    ends_on = _parse_import_date(row.assignment_end_date)
-    updates = {"is_active": row.is_active}
-    if not row.is_active:
-        updates["is_primary"] = False
-    if starts_on:
-        updates["starts_on"] = starts_on
-    if ends_on:
-        updates["ends_on"] = ends_on
-    if row.assignment_source_id:
-        updates["source_identifier"] = row.assignment_source_id
-    updates["source"] = "coach_roster"
-    updates["metadata"] = {key: value for key, value in {"notes": row.notes, "source_id": row.source_id}.items() if value}
-    if assignment:
-        update_assignment(assignment, **updates)
-        return "updated", team_created
-    is_primary = row.is_active and get_primary_assignment(user, season) is None
-    create_assignment(
-        user=user,
-        season_team=season_team,
-        assignment_role=row.assignment_role,
-        is_primary=is_primary,
-        is_active=row.is_active,
-        starts_on=starts_on,
-        ends_on=ends_on,
-        source="coach_roster",
-        source_identifier=row.assignment_source_id,
-        metadata={key: value for key, value in {"notes": row.notes, "source_id": row.source_id}.items() if value},
-    )
-    return "created", team_created
-
-
-@transaction.atomic
-def _reuse_existing_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResultRow:
-    user = User.objects.select_for_update().select_related("account_profile").get(pk=row.existing_user_id)
-    profile = get_or_create_account_profile(user)
-    if profile.role != AccountRole.COACH:
-        raise ValidationError("Existing account is not a coach.")
-    metadata = {**_profile_metadata(profile), **_metadata_for_row(row)}
-    profile.metadata = metadata
-    profile.save(update_fields=["metadata", "updated_at"])
-    user.first_name = user.first_name or row.first_name
-    user.last_name = user.last_name or row.last_name
-    user.email = user.email or row.email
-    user.save(update_fields=["first_name", "last_name", "email"])
-    assignment_action, team_created = _commit_assignment(user, row, season)
-    status_message = "inactive" if not user.is_active else "active"
-    return CoachImportResultRow(
-        row_number=row.row_number,
-        status=RESULT_REUSED,
-        username=user.username,
-        user_id=user.id,
-        is_active=user.is_active,
-        season_name=season.name,
-        team=row.team,
-        division=row.division,
-        assignment_role_label=row.assignment_role_label,
-        assignment_status=assignment_action,
-        password_behavior="Password unchanged",
-        messages=[
-            status_message,
-            "password unchanged",
-            "season team created" if team_created else "season team reused",
-            f"assignment {assignment_action}",
-        ],
-    )
-
-
-@transaction.atomic
-def _create_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResultRow:
-    user = User.objects.create(
-        username=row.final_username,
-        first_name=row.first_name,
-        last_name=row.last_name,
-        email=row.email,
-        is_active=row.is_active,
-    )
-    temporary_password = set_random_temporary_password(user)
-    profile = set_account_role(user, AccountRole.COACH)
-    profile.must_change_password = True
-    profile.metadata = {**_profile_metadata(profile), **_metadata_for_row(row)}
-    profile.save(update_fields=["must_change_password", "metadata", "updated_at"])
-    assignment_action, team_created = _commit_assignment(user, row, season)
-    status_message = "inactive" if not user.is_active else "active"
-    return CoachImportResultRow(
-        row_number=row.row_number,
-        status=RESULT_CREATED,
-        username=user.username,
-        user_id=user.id,
-        is_active=user.is_active,
-        temporary_password=temporary_password,
-        season_name=season.name,
-        team=row.team,
-        division=row.division,
-        assignment_role_label=row.assignment_role_label,
-        assignment_status=assignment_action,
-        password_behavior="Temporary password generated",
-        messages=[
-            status_message,
-            "temporary password generated",
-            "season team created" if team_created else "season team reused",
-            f"assignment {assignment_action}",
-        ],
-    )
-
-
-def commit_coach_import(actor, csv_text: str, season: Season | None = None) -> CoachImportResult:
-    """Create or reuse coach accounts from CSV text and return one-time passwords."""
-    _validate_actor(actor)
-    preview = preview_coach_import(csv_text, season=season)
-    result_rows = []
-
-    for error in preview.row_errors:
-        result_rows.append(CoachImportResultRow(row_number=0, status=RESULT_ERROR, messages=[error]))
-
-    for row in preview.rows:
-        if row.status == STATUS_READY:
-            try:
-                existing_user = find_existing_email_user(row.email)
-                if existing_user and _role_for_user(existing_user) == AccountRole.COACH:
-                    result_rows.append(_reuse_existing_coach(replace(row, existing_user_id=existing_user.id), season))
-                elif existing_user:
-                    result_rows.append(
-                        CoachImportResultRow(
-                            row_number=row.row_number,
-                            status=RESULT_CONFLICT,
-                            username=row.final_username,
-                            user_id=existing_user.id,
-                            season_name=season.name,
-                            team=row.team,
-                            division=row.division,
-                            assignment_role_label=row.assignment_role_label,
-                            password_behavior="Password unchanged",
-                            messages=["Email belongs to an existing non-coach account."],
-                        )
-                    )
-                else:
-                    result_rows.append(_create_coach(row, season))
-            except ValidationError as exc:
-                result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
-        elif row.status == STATUS_REUSE:
-            try:
-                result_rows.append(_reuse_existing_coach(row, season))
-            except ValidationError as exc:
-                result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
-        elif row.status == STATUS_CONFLICT:
-            result_rows.append(
-                CoachImportResultRow(
-                    row_number=row.row_number,
-                    status=RESULT_CONFLICT,
-                    username=row.final_username,
-                    user_id=row.existing_user_id,
-                    season_name=season.name if season else "",
-                    team=row.team,
-                    division=row.division,
-                    assignment_role_label=row.assignment_role_label,
-                    password_behavior="Password unchanged",
-                    messages=row.messages,
-                )
-            )
-        else:
-            result_rows.append(
-                CoachImportResultRow(
-                    row_number=row.row_number,
-                    status=RESULT_ERROR,
-                    username=row.final_username,
-                    season_name=season.name if season else "",
-                    team=row.team,
-                    division=row.division,
-                    assignment_role_label=row.assignment_role_label,
-                    messages=row.messages,
-                )
-            )
-
-    return CoachImportResult(rows=result_rows, season_id=season.id if season else None, season_name=season.name if season else "")
+"""Public façade for the staff coach import workflow.
+
+Implementation lives in ``accounts.services.coach_import`` modules so callers
+can keep using the stable coach-import service API while internals stay focused.
+"""
+
+from accounts.services.coach_import.commit import User, commit_coach_import
+from accounts.services.coach_import.constants import (
+    OPTIONAL_COLUMNS,
+    REQUIRED_COLUMNS,
+    RESULT_CONFLICT,
+    RESULT_CREATED,
+    RESULT_ERROR,
+    RESULT_REUSED,
+    RESULT_SKIPPED,
+    ROLE_ALIASES,
+    STATUS_CONFLICT,
+    STATUS_ERROR,
+    STATUS_READY,
+    STATUS_REUSE,
+    SUPPORTED_COLUMNS,
+)
+from accounts.services.coach_import.preview import (
+    preview_coach_import,
+    preview_coach_import_file,
+)
+from accounts.services.coach_import.result_models import (
+    CoachImportPreview,
+    CoachImportResult,
+    CoachImportResultRow,
+    CoachImportRowPreview,
+)
+
+__all__ = [
+    "CoachImportPreview",
+    "CoachImportResult",
+    "CoachImportResultRow",
+    "CoachImportRowPreview",
+    "OPTIONAL_COLUMNS",
+    "REQUIRED_COLUMNS",
+    "RESULT_CONFLICT",
+    "RESULT_CREATED",
+    "RESULT_ERROR",
+    "RESULT_REUSED",
+    "RESULT_SKIPPED",
+    "ROLE_ALIASES",
+    "STATUS_CONFLICT",
+    "STATUS_ERROR",
+    "STATUS_READY",
+    "STATUS_REUSE",
+    "SUPPORTED_COLUMNS",
+    "User",
+    "commit_coach_import",
+    "preview_coach_import",
+    "preview_coach_import_file",
+]
```

## Terminal State

PASS
