# Prompt 83 - Players

## User Prompt

Source prompt file:
`/Users/eugenelin/.codex/attachments/237820e8-a329-461c-bc8b-7dc806594fdc/pasted-text.txt`

```text
Perform Repository Cleanup Phase 3 only: Player Import Service Refactor.

Use continuous loop engineering.

Continue until the player import service is structurally cleaner, behavior remains unchanged, focused and full verification pass, commits are pushed, and the working tree is clean.

Do not change player-import product behavior.

Do not add new import fields, models, migrations, screens, permissions, or features.

Do not begin the coach-import refactor, season-view refactor, test-package split, or account-operations refactor.

==================================================
Current State
=============

Repository Cleanup Phases 1 and 2 are complete.

Current repository tooling includes:

* Django 4.2.30;
* Ruff correctness checks;
* Black;
* isort;
* pre-commit;
* repository-wide tooling configuration;
* no whole-repository formatting baseline.

Seasonal Participation V1 is feature complete, production ready, and frozen.

The current player import workflow is production behavior and must not change.

The player import subsystem currently includes a large service module that combines:

* CSV parsing;
* header normalization;
* column mapping;
* row validation;
* player matching;
* preview construction;
* import-batch state;
* SeasonTeam resolution;
* PlayerRosterMembership resolution;
* permanent player creation/update;
* provenance;
* optional account provisioning;
* commit processing;
* result reporting.

The objective is a behavior-preserving structural refactor.

==================================================
Objective
=========

Reduce the size and responsibility of:

```text
players/services/import_service.py
```

Split cohesive responsibilities into focused internal modules while preserving a small, stable public façade for current callers.

The refactor should make future maintenance safer without changing:

* URLs;
* forms;
* views;
* templates;
* session behavior;
* CSV behavior;
* matching behavior;
* roster behavior;
* account provisioning;
* result messages;
* import counts;
* error handling;
* transaction semantics;
* permissions.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete refactoring, regression-proofing, documentation, or verification work remains.

PASS

All Phase 3 acceptance criteria are satisfied, tests and tooling pass, commits are pushed, and the working tree is clean.

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
3. read player-import documentation and relevant prompt archives;
4. confirm the working tree is clean;
5. inspect the complete player-import workflow and all import-service callers;
6. identify one cohesive refactoring boundary;
7. create the next prompt archive before implementation;
8. refactor only the selected player-import concern;
9. preserve or add focused regression tests;
10. run formatting/lint checks on touched Python files;
11. run focused verification;
12. perform senior-engineer self-review;
13. fix every verified issue;
14. update architecture or engineering documentation only if module ownership materially changes;
15. run full verification;
16. commit implementation/tests/documentation;
17. finalize and separately commit the prompt archive;
18. push both commits;
19. re-read the committed diff;
20. confirm the working tree is clean;
21. reassess all acceptance criteria;
22. choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS;
23. if CONTINUE, immediately begin the next loop.

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
* relevant player-import documentation
* `docs/analytics/implementation/engineering/phase_02_player_import_workflow.md`
* relevant Account Management import/provisioning documentation
* Seasonal Participation player-import documentation
* prompt archives related to:

  * player import foundation;
  * player matching;
  * player account provisioning;
  * season-aware player import.

Inspect:

* `players/services/import_service.py`
* every import from `players.services.import_service`
* `players/forms.py`
* `players/views.py`
* `players/models.py`
* `players/tests.py`
* player import templates
* player matching services
* player merge/update services
* source identifier/provenance services
* `accounts/services/provisioning_service.py`
* `seasons/services/team_service.py`
* `seasons/services/membership_service.py`
* current migrations only for dependency understanding.

==================================================
Public API Preservation
=======================

Inventory all current public names imported from `players.services.import_service`.

Preserve current imports wherever practical.

Preferred approach:

* convert `players/services/import_service.py` into a small façade;
* move implementation details to a new internal package;
* re-export existing public dataclasses, constants, and functions.

For example:

```text
players/services/imports/
    __init__.py
    constants.py
    parsing.py
    mapping.py
    preview.py
    commit.py
    roster.py
    result_models.py
```

This is only a suggested structure.

Use repository evidence to choose the smallest clear split.

Do not force every suggested module into existence.

Do not make views import deep internal modules.

==================================================
Recommended Responsibility Boundaries
=====================================

Separate responsibilities where cohesive.

## 1. Data Contracts

Move frozen dataclasses, status constants, and result structures into a focused module when practical.

Examples:

* preview row dataclasses;
* preview result dataclasses;
* commit result rows;
* import result summary;
* stable status/action constants.

Avoid circular imports.

## 2. CSV And Primitive Parsing

Move generic player-import parsing concerns such as:

* UTF-8 decoding;
* header normalization;
* CSV row reading;
* boolean parsing;
* date parsing;
* blank-value handling;
* column-name validation.

Do not change accepted formats or current validation messages.

## 3. Mapping And Row Normalization

Move:

* source-column mapping;
* mapped-row normalization;
* permanent identity field extraction;
* roster field extraction;
* unsupported/missing-column handling.

Do not redesign the mapping workflow.

## 4. Preview Construction

Move:

* row preview assembly;
* action labels;
* validation message aggregation;
* proposed player/team/membership actions;
* preview summary counts.

Preview output must remain identical from the perspective of templates and tests.

## 5. Commit Processing

Move:

* per-row commit orchestration;
* batch-level orchestration;
* transaction boundaries;
* player create/update calls;
* source/provenance persistence;
* optional account provisioning;
* result-row assembly.

Do not alter partial-failure or transaction behavior.

## 6. Seasonal Roster Integration

Move player-import-specific orchestration around:

* SeasonTeam resolution;
* membership create/reuse/update;
* primary-membership behavior;
* compatibility-field synchronization;
* same-season team-change blocking.

Do not move generic seasonal domain rules out of the `seasons` services.

The player importer should call the authoritative season services rather than duplicate them.

## 7. Matching Integration

Keep canonical matching logic in existing player matching services.

The import refactor may create a small adapter/orchestrator, but must not copy or redefine permanent-player matching rules.

==================================================
Behavioral Freeze
=================

The following behavior must remain unchanged.

## Upload And Mapping

* supported CSV encoding;
* required fields;
* optional fields;
* mapping behavior;
* row numbering;
* preview state.

## Permanent Identity

* source identifier matching;
* registration/registrant matching;
* name/birthdate matching;
* conflict detection;
* conservative player reuse;
* no team/division identity matching.

## Seasonal Behavior

* every new import requires an active season;
* selected season remains server-validated;
* SeasonTeam normalization and reuse;
* future seasons create new memberships;
* same-season same-team imports are deterministic;
* same-season primary team changes remain blocked for manual review;
* prior memberships remain historical;
* compatibility fields update only from active primary membership.

## Account Provisioning

* optional provisioning remains unchanged;
* player accounts are permanent;
* existing accounts are reused;
* temporary-password handling remains unchanged;
* one-time password display remains unchanged;
* partial provisioning errors remain reported as before.

## Results

* existing messages;
* existing counters;
* created/reused/conflict/error classifications;
* result-page context;
* provenance.

==================================================
No New Generic Import Framework
===============================

Do not create a broad application-wide import framework.

Do not refactor coach import in this phase.

It is acceptable for player and coach importers to remain separate when their domain behavior differs.

Only extract utilities outside `players` if they are already demonstrably generic and the extraction is small, obvious, and behavior-neutral.

Otherwise keep the new modules under:

```text
players/services/imports/
```

==================================================
Tests
=====

Preserve all existing player-import tests.

Add focused tests only where decomposition exposes an untested contract.

Useful contract-level tests may cover:

* façade exports remain importable;
* parsing produces the same normalized rows;
* preview dataclass equality or field values remain stable;
* commit result counts remain unchanged;
* same-season team-change conflict behavior remains unchanged;
* account provisioning result behavior remains unchanged;
* import transaction behavior remains unchanged.

Do not rewrite the entire test suite merely to match the new module layout.

Tests should continue to exercise behavior through public services and views where possible.

Avoid tests that bind unnecessarily to private implementation details.

==================================================
Import Cycles And Dependency Direction
======================================

Review carefully for circular imports.

Preferred dependency direction:

```text
views/forms
    ->
players.services.import_service façade
    ->
players.services.imports internal modules
    ->
players matching/update/provenance services
    ->
seasons and accounts public services
```

Internal parsing/data-contract modules should not import views, forms, or templates.

Avoid modules that mutually import one another.

Use `TYPE_CHECKING` only where helpful and justified.

==================================================
Code Quality
============

Apply tooling only to touched Python files.

Run:

```bash
ruff check <touched-python-files>
black --check <touched-python-files>
isort --check-only <touched-python-files>
```

If touched files fail formatting:

* format only the touched files;
* do not format unrelated repository files;
* avoid rewriting historical migrations.

Keep:

* explicit type hints where already used;
* frozen dataclasses where appropriate;
* clear function names;
* concise module docstrings only where they provide real navigation value;
* business rules in services;
* no signals.

Remove:

* dead private functions made obsolete by the split;
* duplicate imports;
* obsolete comments;
* circular compatibility wrappers that provide no public value.

==================================================
Documentation
=============

Update documentation only if needed to describe the new internal service layout.

Likely candidates:

* `docs/ARCHITECTURE.md`
* current player-import engineering/status documentation

Do not rewrite the user manual because user behavior must not change.

Do not describe the refactor as a new feature.

==================================================
Scope Restrictions
==================

Do not:

* modify models;
* create migrations;
* change forms or views except import paths if unavoidable;
* change templates;
* change URLs;
* change permissions;
* change CSV fields;
* change matching policy;
* change roster policy;
* change account provisioning behavior;
* change messages intentionally;
* add APIs;
* add JavaScript;
* add caching;
* add background jobs;
* refactor coach import;
* split all tests into packages;
* refactor account operations;
* bulk-format the repository;
* regenerate the flat-file snapshot.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations players --check
DJANGO_SECRET_KEY=test python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test python manage.py test players
DJANGO_SECRET_KEY=test python manage.py test accounts
DJANGO_SECRET_KEY=test python manage.py test seasons
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

The full suite must pass before committing.

==================================================
Senior-Engineer Self-Review
===========================

Review every diff for:

* accidental behavior changes;
* changed validation text;
* changed action labels;
* changed count semantics;
* transaction-boundary drift;
* account-provisioning regressions;
* matching regressions;
* provenance regressions;
* seasonal membership regressions;
* hidden new abstractions;
* circular imports;
* deep-module imports leaking into views;
* duplicated logic;
* dead façade code;
* unnecessary generic framework design;
* formatting churn;
* stale documentation.

Fix every verified issue before committing.

==================================================
Acceptance Criteria
===================

Do not declare PASS until all criteria are satisfied.

A. Structure

* `players/services/import_service.py` is materially smaller;
* cohesive responsibilities moved into focused modules;
* public import API remains stable where practical;
* views do not depend on internal implementation modules.

B. Behavior

* player import behavior remains unchanged;
* preview and result contracts remain unchanged;
* permanent identity matching remains unchanged;
* season-aware membership behavior remains unchanged;
* optional account provisioning remains unchanged.

C. Transactions And Integrity

* transaction boundaries remain equivalent;
* partial-failure behavior remains equivalent;
* provenance remains complete;
* duplicate players and memberships are not introduced.

D. Quality

* no circular imports;
* no duplicated business rules;
* no dead code;
* touched files pass Ruff, Black, and isort checks;
* no unrelated formatting churn.

E. Tests

* focused tests pass;
* full suite passes;
* any newly exposed contract gap has regression coverage.

F. Migration

* no models changed;
* no migrations created;
* migration checks pass.

G. Documentation

* architecture/internal layout docs updated only if needed;
* no user-facing behavior claims changed.

H. Git

* implementation/refactor commit exists;
* prompt archive commit exists;
* both pushed;
* working tree clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally:

1. inventory the public API and callers;
2. establish a small internal `players.services.imports` package;
3. move data contracts and parsing;
4. move preview and commit orchestration where cleanly separable;
5. preserve the façade;
6. remove obsolete code from the original module;
7. run focused and full verification;
8. update minimal architecture documentation if warranted;
9. commit, archive, push, and reassess.

If the complete safe split is too large for one loop, continue with another cohesive boundary.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* materially reduces mixed responsibilities;
* removes verified duplication;
* closes an import-service contract gap;
* fixes a circular dependency risk;
* improves maintainability without behavior change;
* adds missing regression proof.

Moving code between files without clearer ownership does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* developer maintaining CSV parsing;
* developer changing player matching;
* developer changing roster import behavior;
* developer maintaining account provisioning;
* tester diagnosing a row-level failure;
* security reviewer inspecting server-controlled import state;
* production operator relying on deterministic reimports.

Confirm:

* the service is easier to navigate;
* behavior is unchanged;
* the façade is stable;
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
   * behavior-preservation findings;
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
Refactor player import service
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
* parsing split;
* preview split;
* commit split;
* seasonal integration behavior;
* matching behavior;
* account provisioning behavior;
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

`ab8dde1` - Refactor player import service

## Module Structure

Old structure:

```text
players/services/import_service.py
```

New structure:

```text
players/services/import_service.py          # public façade and compatibility exports
players/services/imports/__init__.py        # internal import package marker
players/services/imports/constants.py       # source/action/resolution/field constants
players/services/imports/result_models.py   # import dataclasses/read models
players/services/imports/parsing.py         # CSV and primitive parsing helpers
players/services/imports/mapping.py         # column mapping and row normalization
players/services/imports/matching.py        # import matching adapter using matching_service
players/services/imports/roster.py          # season team and membership integration
players/services/imports/preview.py         # preview construction and preview persistence
players/services/imports/commit.py          # commit orchestration and provenance persistence
```

## Public API Preservation

- Existing callers continue to import from `players.services.import_service`.
- `analytics/forms.py`, `analytics/views.py`, `analytics/tests.py`, and `players/tests.py` were not changed.
- The façade exposes the prior public constants, dataclasses, parsing helpers, preview helpers, and commit helpers through `__all__`.
- Views and forms do not import internal `players.services.imports` modules.

## Behavior Preservation Findings

- CSV parsing, mapping, source inference, row numbering, and size/row limits were moved without intentional behavior changes.
- Preview row shape, action labels, summary counters, row errors, and conflict summaries remain exercised through the existing tests.
- Matching still delegates to `players.services.matching_service`; no matching rules were copied or redefined.
- Season team and membership behavior still delegates to `seasons` services.
- Optional account provisioning remains in commit orchestration and still calls `accounts.services.provisioning_service` lazily.

## Transaction Findings

- `create_import_batch`, `build_import_preview`, and `commit_import_batch` remain transaction-wrapped.
- `commit_import_batch` still locks the import batch with `select_for_update()`.
- Membership updates still use `select_for_update()` where the previous service did.
- Provenance persistence remains part of row commit processing.

## Tests And Tooling

- `pre-commit run --files` on touched files: passed.
- Touched files passed Ruff, Black, and isort through pre-commit.
- Focused verification passed:
  - `DJANGO_SECRET_KEY=test python manage.py check`
  - `DJANGO_SECRET_KEY=test python manage.py makemigrations players --check`
  - `DJANGO_SECRET_KEY=test python manage.py makemigrations seasons --check`
  - `DJANGO_SECRET_KEY=test python manage.py makemigrations accounts --check`
  - `DJANGO_SECRET_KEY=test python manage.py test players accounts seasons` with 285 tests.

## Full Verification

- `DJANGO_SECRET_KEY=test python manage.py check`: passed.
- `DJANGO_SECRET_KEY=test python manage.py makemigrations --check`: passed.
- `DJANGO_SECRET_KEY=test python manage.py migrate --plan`: passed.
- `DJANGO_SECRET_KEY=test python manage.py test`: passed, 458 tests.
- `git diff --check`: passed.

## Commit Diff

```diff
commit ab8dde1beca3164532c613fa7e030ce4a5824d17
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 03:17:03 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 03:17:03 2026 -0700

    Refactor player import service
---
 players/services/import_service.py        | 1245 +++--------------------------
 players/services/imports/__init__.py      |    1 +
 players/services/imports/commit.py        |  391 +++++++++
 players/services/imports/constants.py     |  130 +++
 players/services/imports/mapping.py       |  180 +++++
 players/services/imports/matching.py      |   86 ++
 players/services/imports/parsing.py       |  211 +++++
 players/services/imports/preview.py       |  241 ++++++
 players/services/imports/result_models.py |   77 ++
 players/services/imports/roster.py        |  195 +++++
 10 files changed, 1645 insertions(+), 1112 deletions(-)

diff --git a/players/services/import_service.py b/players/services/import_service.py
index a139e14..525d8e6 100644
--- a/players/services/import_service.py
+++ b/players/services/import_service.py
@@ -1,1116 +1,137 @@
-from __future__ import annotations
-
-import csv
-import io
-from dataclasses import asdict, dataclass, field
-from datetime import date, datetime
-from typing import Any
-
-from django.core.exceptions import PermissionDenied, ValidationError
-from django.db import IntegrityError, transaction
-from django.utils import timezone
-
-from players.models import (
-    Player,
-    PlayerImportBatch,
-    PlayerImportStatus,
-    PlayerSourceIdentifier,
-    PlayerSourceRow,
+"""Public façade for the player import workflow.
+
+Implementation lives in ``players.services.imports`` modules so callers can keep
+using the stable import-service API while the internals stay easier to navigate.
+"""
+
+from players.services.imports.commit import (
+    apply_player_updates,
+    attach_source_identifiers,
+    commit_import_batch,
+    create_import_batch,
+    create_player_from_import,
+    record_import_source_row,
 )
-from players.services.matching_service import (
-    MATCH_AMBIGUOUS,
-    MATCH_EXACT,
-    MATCH_HIGH_CONFIDENCE,
-    MATCH_NO_MATCH,
-    PlayerMatchResult,
-    find_player_match,
-    match_by_identifier,
+from players.services.imports.constants import (
+    ACTION_CREATE,
+    ACTION_ERROR,
+    ACTION_NEEDS_REVIEW,
+    ACTION_SKIP,
+    ACTION_UPDATE,
+    CONFLICT_FIELDS,
+    HEADER_ALIASES,
+    IDENTIFIER_FIELD_TYPES,
+    MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
+    MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
+    MAX_CSV_ROWS,
+    MAX_CSV_UPLOAD_BYTES,
+    PERMANENT_PLAYER_FIELD_KEYS,
+    PLAYER_FIELD_KEYS,
+    RESOLUTION_ACTION_COMMIT,
+    RESOLUTION_ACTION_CREATE_NEW,
+    RESOLUTION_ACTION_USE_CANDIDATE,
+    RESOLUTION_KEEP_EXISTING,
+    RESOLUTION_METADATA_ONLY,
+    RESOLUTION_USE_IMPORTED,
+    SOURCE_CHOICES,
+    SOURCE_MANUAL_STAFF,
+    SOURCE_MEMBER_LIST,
+    SOURCE_ROSTER_DETAIL,
+)
+from players.services.imports.mapping import (
+    build_identity_payload,
+    build_roster_payload,
+    build_source_identifiers,
+)
+from players.services.imports.parsing import (
+    ROSTER_STATUS_ALIASES,
+    build_column_choices,
+    clean_cell,
+    deserialize_preview,
+    detect_source_from_filename,
+    normalize_header,
+)
+from players.services.imports.parsing import normalize_source as _normalize_source
+from players.services.imports.parsing import (
+    parse_birth_year,
+    parse_birthdate,
+    parse_import_date,
+    parse_player_csv,
+    parse_roster_status,
+    serialize_preview,
+    split_full_name,
+    suggest_mapping,
+)
+from players.services.imports.preview import (
+    build_import_preview,
+    current_preview,
+    preview_row,
+)
+from players.services.imports.result_models import (
+    FieldConflict,
+    ImportCommitResult,
+    ImportIdentityRow,
+    ImportPreviewRow,
+    ImportRowResult,
+    ParsedCsvFile,
 )
-from seasons.models import PlayerRosterMembership, RosterStatus, SeasonTeam
-from seasons.services.membership_service import create_membership, sync_player_current_team_fields, update_membership
-from seasons.services.team_service import get_or_create_season_team, normalize_division_value, normalize_team_value
-
-
-SOURCE_MEMBER_LIST = "vcb_member_list_csv"
-SOURCE_ROSTER_DETAIL = "vcb_roster_detail_csv"
-SOURCE_MANUAL_STAFF = "manual_staff_csv"
-
-SOURCE_CHOICES = [
-    (SOURCE_MEMBER_LIST, "VCB member list CSV"),
-    (SOURCE_ROSTER_DETAIL, "VCB roster detail CSV"),
-    (SOURCE_MANUAL_STAFF, "Manual staff CSV"),
-]
-
-MAX_CSV_UPLOAD_BYTES = 5 * 1024 * 1024
-MAX_CSV_ROWS = 5000
-
-MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS = "_provision_player_accounts"
-MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS = "_activate_player_accounts"
-
-ACTION_CREATE = "create"
-ACTION_UPDATE = "update"
-ACTION_NEEDS_REVIEW = "needs_review"
-ACTION_SKIP = "skip"
-ACTION_ERROR = "error"
-
-RESOLUTION_ACTION_COMMIT = "commit"
-RESOLUTION_ACTION_CREATE_NEW = "create_new"
-RESOLUTION_ACTION_USE_CANDIDATE = "use_candidate"
-RESOLUTION_KEEP_EXISTING = "keep_existing"
-RESOLUTION_USE_IMPORTED = "use_imported"
-RESOLUTION_METADATA_ONLY = "metadata_only"
-
-PLAYER_FIELD_KEYS = [
-    "first_name",
-    "last_name",
-    "preferred_name",
-    "birthdate",
-    "birth_year",
-    "gender",
-    "division",
-    "team_name",
-    "primary_positions",
-    "bats",
-    "throws",
-    "school",
-    "graduation_year",
-]
-
-PERMANENT_PLAYER_FIELD_KEYS = [
-    "first_name",
-    "last_name",
-    "preferred_name",
-    "birthdate",
-    "birth_year",
-    "gender",
-    "primary_positions",
-    "bats",
-    "throws",
-    "school",
-    "graduation_year",
-]
 
-CONFLICT_FIELDS = [
-    "first_name",
-    "last_name",
-    "preferred_name",
-    "birthdate",
-    "birth_year",
-    "gender",
-    "primary_positions",
-    "bats",
-    "throws",
-    "school",
-    "graduation_year",
+__all__ = [
+    "ACTION_CREATE",
+    "ACTION_ERROR",
+    "ACTION_NEEDS_REVIEW",
+    "ACTION_SKIP",
+    "ACTION_UPDATE",
+    "CONFLICT_FIELDS",
+    "FieldConflict",
+    "HEADER_ALIASES",
+    "IDENTIFIER_FIELD_TYPES",
+    "ImportCommitResult",
+    "ImportIdentityRow",
+    "ImportPreviewRow",
+    "ImportRowResult",
+    "MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS",
+    "MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS",
+    "MAX_CSV_ROWS",
+    "MAX_CSV_UPLOAD_BYTES",
+    "PERMANENT_PLAYER_FIELD_KEYS",
+    "PLAYER_FIELD_KEYS",
+    "ParsedCsvFile",
+    "RESOLUTION_ACTION_COMMIT",
+    "RESOLUTION_ACTION_CREATE_NEW",
+    "RESOLUTION_ACTION_USE_CANDIDATE",
+    "RESOLUTION_KEEP_EXISTING",
+    "RESOLUTION_METADATA_ONLY",
+    "RESOLUTION_USE_IMPORTED",
+    "ROSTER_STATUS_ALIASES",
+    "SOURCE_CHOICES",
+    "SOURCE_MANUAL_STAFF",
+    "SOURCE_MEMBER_LIST",
+    "SOURCE_ROSTER_DETAIL",
+    "_normalize_source",
+    "apply_player_updates",
+    "attach_source_identifiers",
+    "build_column_choices",
+    "build_identity_payload",
+    "build_import_preview",
+    "build_roster_payload",
+    "build_source_identifiers",
+    "clean_cell",
+    "commit_import_batch",
+    "create_import_batch",
+    "create_player_from_import",
+    "current_preview",
+    "deserialize_preview",
+    "detect_source_from_filename",
+    "normalize_header",
+    "parse_birth_year",
+    "parse_birthdate",
+    "parse_import_date",
+    "parse_player_csv",
+    "parse_roster_status",
+    "preview_row",
+    "record_import_source_row",
+    "serialize_preview",
+    "split_full_name",
+    "suggest_mapping",
 ]
-
-IDENTIFIER_FIELD_TYPES = {
-    "registration_id": "registration_id",
-    "registrant_id": "registrant_id",
-    "team_id": "team_id",
-    "source_player_id": "source_player_id",
-}
-
-HEADER_ALIASES = {
-    "first_name": {"first", "first name", "firstname", "given name", "player first name"},
-    "last_name": {"last", "last name", "lastname", "surname", "family name", "player last name"},
-    "full_name": {"name", "full name", "player", "player name"},
-    "preferred_name": {"preferred", "preferred name", "nickname", "nick name"},
-    "birthdate": {"birthdate", "birth date", "date of birth", "dob"},
-    "birth_year": {"birth year", "year of birth", "yob"},
-    "gender": {"gender", "sex"},
-    "division": {"division", "level", "program"},
-    "team_name": {"team", "team name", "current team"},
-    "roster_status": {"roster status", "status", "membership status"},
-    "jersey_number": {"jersey", "jersey number", "number", "uniform number"},
-    "membership_start_date": {"membership start date", "start date", "starts on", "roster start"},
-    "membership_end_date": {"membership end date", "end date", "ends on", "roster end"},
-    "roster_source_id": {"roster source id", "membership id", "roster id"},
-    "primary_positions": {"position", "positions", "primary position", "primary positions"},
-    "bats": {"bats", "batting", "hits"},
-    "throws": {"throws", "throwing"},
-    "school": {"school"},
-    "graduation_year": {"graduation year", "grad year", "class year"},
-    "registration_id": {"registration id", "registration", "reg id"},
-    "registrant_id": {"registrant id", "member id", "participant id"},
-    "team_id": {"team id", "teamid"},
-    "source_player_id": {"player id", "source player id", "external player id"},
-}
-
-
-@dataclass
-class ImportIdentityRow:
-    row_number: int | None
-    identity: dict[str, Any]
-    original_row: dict[str, Any] = field(default_factory=dict)
-    unmapped_fields: dict[str, Any] = field(default_factory=dict)
-
-
-@dataclass
-class ImportRowResult:
-    row_number: int | None
-    imported: bool
-    errors: list[str] = field(default_factory=list)
-    identity: dict[str, Any] = field(default_factory=dict)
-
-
-@dataclass
-class ParsedCsvFile:
-    file_name: str
-    headers: list[str]
-    normalized_headers: dict[str, str]
-    rows: list[dict[str, Any]]
-    duplicate_headers: list[str] = field(default_factory=list)
-
-
-@dataclass
-class FieldConflict:
-    field_name: str
-    existing_value: str
-    imported_value: str
-    resolution: str = RESOLUTION_KEEP_EXISTING
-
-
-@dataclass
-class ImportPreviewRow:
-    row_number: int
-    identity: dict[str, Any]
-    original_row: dict[str, Any]
-    unmapped_fields: dict[str, Any]
-    source_identifiers: list[dict[str, str]]
-    match_status: str
-    matched_player_id: int | None = None
-    matched_player_name: str = ""
-    candidate_ids: list[int] = field(default_factory=list)
-    candidate_names: list[str] = field(default_factory=list)
-    candidate_options: list[dict[str, Any]] = field(default_factory=list)
-    field_conflicts: list[dict[str, str]] = field(default_factory=list)
-    errors: list[str] = field(default_factory=list)
-    action: str = ACTION_CREATE
-    roster: dict[str, Any] = field(default_factory=dict)
-    season_team: dict[str, Any] = field(default_factory=dict)
-    membership: dict[str, Any] = field(default_factory=dict)
-
-
-@dataclass
-class ImportCommitResult:
-    rows_processed: int = 0
-    created: int = 0
-    updated: int = 0
-    skipped: int = 0
-    conflicts: int = 0
-    season_teams_created: int = 0
-    season_teams_reused: int = 0
-    memberships_created: int = 0
-    memberships_updated: int = 0
-    errors: list[str] = field(default_factory=list)
-    account_provisioning: dict[str, Any] = field(default_factory=dict)
-
-
-def clean_cell(value) -> str:
-    """Return a stripped string suitable for import processing."""
-    return "" if value is None else str(value).strip()
-
-
-def normalize_header(value) -> str:
-    """Normalize an import header for matching mapped columns."""
-    return " ".join(clean_cell(value).casefold().split())
-
-
-def _normalize_source(value: str) -> str:
-    normalized = normalize_header(value).replace(" ", "_")
-    return normalized or SOURCE_MANUAL_STAFF
-
-
-def _ensure_staff(actor):
-    if not actor or not actor.is_authenticated or not (actor.is_staff or actor.is_superuser):
-        raise PermissionDenied("Only staff/admin users can run player imports.")
-
-
-def _json_preview_row(row: ImportPreviewRow) -> dict[str, Any]:
-    return asdict(row)
-
-
-def detect_source_from_filename(filename: str) -> str:
-    """Infer a stable source name from a CSV filename."""
-    lowered = normalize_header(filename)
-    if "roster" in lowered and "detail" in lowered:
-        return SOURCE_ROSTER_DETAIL
-    if "member" in lowered:
-        return SOURCE_MEMBER_LIST
-    return SOURCE_MANUAL_STAFF
-
-
-def parse_player_csv(file_obj) -> ParsedCsvFile:
-    """Parse a player CSV upload and preserve original row values."""
-    file_name = getattr(file_obj, "name", "players.csv")
-    if not file_name.lower().endswith(".csv"):
-        raise ValidationError("Upload a .csv file.")
-    file_size = getattr(file_obj, "size", None)
-    if file_size is not None and file_size > MAX_CSV_UPLOAD_BYTES:
-        raise ValidationError("CSV uploads are limited to 5 MB.")
-
-    raw_data = file_obj.read()
-    raw_size = len(raw_data.encode("utf-8")) if isinstance(raw_data, str) else len(raw_data)
-    if raw_size > MAX_CSV_UPLOAD_BYTES:
-        raise ValidationError("CSV uploads are limited to 5 MB.")
-    if isinstance(raw_data, bytes):
-        raw_data = raw_data.decode("utf-8-sig")
-    file_obj.seek(0)
-
-    reader = csv.DictReader(io.StringIO(raw_data))
-    if not reader.fieldnames:
-        raise ValidationError("The uploaded CSV does not contain a header row.")
-
-    headers = []
-    normalized_headers = {}
-    duplicate_headers = []
-    for header in reader.fieldnames:
-        stripped = clean_cell(header)
-        if not stripped:
-            duplicate_headers.append("<blank header>")
-            continue
-        normalized = normalize_header(stripped)
-        if normalized in normalized_headers:
-            duplicate_headers.append(stripped)
-        normalized_headers[normalized] = stripped
-        headers.append(stripped)
-
-    if duplicate_headers:
-        raise ValidationError("Duplicate or blank column headers were found: " + ", ".join(sorted(set(duplicate_headers))))
-
-    rows = []
-    for row_number, row in enumerate(reader, start=2):
-        if len(rows) >= MAX_CSV_ROWS:
-            raise ValidationError(f"CSV uploads are limited to {MAX_CSV_ROWS} data rows.")
-        original_row = {}
-        cleaned_row = {}
-        for header in reader.fieldnames:
-            stripped = clean_cell(header)
-            original_value = row.get(header, "")
-            original_row[stripped] = original_value
-            cleaned_row[stripped] = clean_cell(original_value)
-        rows.append({"row_number": row_number, "original_row": original_row, "cleaned_row": cleaned_row})
-
-    return ParsedCsvFile(
-        file_name=file_name,
-        headers=headers,
-        normalized_headers=normalized_headers,
-        rows=rows,
-        duplicate_headers=duplicate_headers,
-    )
-
-
-def serialize_preview(preview: dict) -> dict:
-    """Return a JSON-ready preview payload."""
-    return preview
-
-
-def deserialize_preview(payload: dict) -> dict:
-    """Return a preview payload from JSON data."""
-    return payload or {}
-
-
-def build_column_choices(parsed: ParsedCsvFile | dict) -> list[tuple[str, str]]:
-    """Build form choices for parsed CSV headers."""
-    headers = parsed.headers if isinstance(parsed, ParsedCsvFile) else parsed.get("headers", [])
-    return [(header, header) for header in headers]
-
-
-def suggest_mapping(headers: list[str], source: str = "") -> dict[str, str]:
-    """Suggest canonical player field mappings from CSV headers."""
-    mapping = {}
-    normalized_to_header = {normalize_header(header): header for header in headers}
-    for target, aliases in HEADER_ALIASES.items():
-        for alias in aliases:
-            if alias in normalized_to_header:
-                mapping[target] = normalized_to_header[alias]
-                break
-    return mapping
-
-
-def split_full_name(full_name: str) -> tuple[str, str]:
-    """Split a full name into first and last name for import matching."""
-    parts = [part for part in clean_cell(full_name).split() if part]
-    if not parts:
-        return "", ""
-    if len(parts) == 1:
-        return parts[0], ""
-    return parts[0], " ".join(parts[1:])
-
-
-def parse_birthdate(value: str):
-    """Parse common ISO-style birthdate values."""
-    cleaned = clean_cell(value)
-    if not cleaned:
-        return None
-    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
-        try:
-            return datetime.strptime(cleaned, fmt).date()
-        except ValueError:
-            continue
-    return None
-
-
-def parse_import_date(value: str):
-    """Parse optional roster date values from CSV input."""
-    return parse_birthdate(value)
-
-
-ROSTER_STATUS_ALIASES = {
-    "": RosterStatus.ACTIVE,
-    "active": RosterStatus.ACTIVE,
-    "inactive": RosterStatus.INACTIVE,
-    "transferred": RosterStatus.TRANSFERRED,
-    "transfer": RosterStatus.TRANSFERRED,
-    "guest": RosterStatus.GUEST,
-    "removed": RosterStatus.REMOVED,
-    "remove": RosterStatus.REMOVED,
-}
-
-
-def parse_roster_status(value: str) -> str:
-    cleaned = normalize_header(value)
-    if cleaned in ROSTER_STATUS_ALIASES:
-        return ROSTER_STATUS_ALIASES[cleaned]
-    raise ValidationError(f"Unknown roster status '{clean_cell(value)}'.")
-
-
-def parse_birth_year(value: str):
-    """Parse a birth year from a string."""
-    cleaned = clean_cell(value)
-    if not cleaned:
-        return None
-    try:
-        year = int(cleaned)
-    except ValueError:
-        return None
-    if 1900 <= year <= date.today().year:
-        return year
-    return None
-
-
-def _date_to_string(value) -> str:
-    if isinstance(value, date):
-        return value.isoformat()
-    return clean_cell(value)
-
-
-def _parse_identity_value(field_name: str, value):
-    if field_name == "birthdate":
-        return parse_birthdate(value) if not isinstance(value, date) else value
-    if field_name in {"birth_year", "graduation_year"}:
-        return parse_birth_year(value)
-    return clean_cell(value)
-
-
-def _identity_for_storage(identity: dict[str, Any]) -> dict[str, Any]:
-    stored = {}
-    for key, value in identity.items():
-        if isinstance(value, date):
-            stored[key] = value.isoformat()
-        else:
-            stored[key] = value
-    return stored
-
-
-def _identity_for_model(identity: dict[str, Any]) -> dict[str, Any]:
-    model_identity = {}
-    for field_name in PERMANENT_PLAYER_FIELD_KEYS:
-        value = identity.get(field_name)
-        if field_name == "birthdate" and value:
-            value = parse_birthdate(value) if not isinstance(value, date) else value
-        elif field_name in {"birth_year", "graduation_year"} and value:
-            value = parse_birth_year(value)
-        if value not in {"", None}:
-            model_identity[field_name] = value
-    return model_identity
-
-
-def build_roster_payload(row: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
-    """Build season roster context from a source row and optional column mapping."""
-    mapping = mapping or {}
-    status_column = mapping.get("roster_status", "")
-    starts_column = mapping.get("membership_start_date", "")
-    ends_column = mapping.get("membership_end_date", "")
-    try:
-        roster_status = parse_roster_status(row.get(status_column, "")) if status_column else RosterStatus.ACTIVE
-    except ValidationError as exc:
-        roster_status = ""
-        status_errors = list(exc.messages)
-    else:
-        status_errors = []
-
-    starts_on = parse_import_date(row.get(starts_column, "")) if starts_column else None
-    ends_on = parse_import_date(row.get(ends_column, "")) if ends_column else None
-    errors = status_errors
-    if starts_column and clean_cell(row.get(starts_column)) and starts_on is None:
-        errors.append("Membership start date is invalid.")
-    if ends_column and clean_cell(row.get(ends_column)) and ends_on is None:
-        errors.append("Membership end date is invalid.")
-    if starts_on and ends_on and ends_on < starts_on:
-        errors.append("Membership end date cannot be before start date.")
-
-    return {
-        "team_name": clean_cell(row.get(mapping.get("team_name", "team_name"))),
-        "division": clean_cell(row.get(mapping.get("division", "division"))),
-        "roster_status": roster_status,
-        "jersey_number": clean_cell(row.get(mapping.get("jersey_number", ""))) if mapping.get("jersey_number") else "",
-        "starts_on": starts_on.isoformat() if starts_on else "",
-        "ends_on": ends_on.isoformat() if ends_on else "",
-        "roster_source_id": clean_cell(row.get(mapping.get("roster_source_id", ""))) if mapping.get("roster_source_id") else "",
-        "errors": errors,
-    }
-
-
-def build_identity_payload(row: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
-    """Build a player identity payload from a source row and optional column mapping."""
-    mapping = mapping or {}
-    identity = {}
-    full_name_column = mapping.get("full_name", "")
-    full_name = clean_cell(row.get(full_name_column)) if full_name_column else ""
-    for target_field in PLAYER_FIELD_KEYS:
-        source_field = mapping.get(target_field, target_field)
-        identity[target_field] = _parse_identity_value(target_field, row.get(source_field))
-    if full_name and not (identity.get("first_name") and identity.get("last_name")):
-        first_name, last_name = split_full_name(full_name)
-        identity["first_name"] = identity.get("first_name") or first_name
-        identity["last_name"] = identity.get("last_name") or last_name
-    return _identity_for_storage(identity)
-
-
-def build_source_identifiers(row: dict[str, Any], mapping: dict[str, str] | None, source: str) -> list[dict[str, str]]:
-    """Build source identifiers from mapped CSV columns."""
-    mapping = mapping or {}
-    identifiers = []
-    for field_name, identifier_type in IDENTIFIER_FIELD_TYPES.items():
-        column = mapping.get(field_name, "")
-        value = clean_cell(row.get(column)) if column else ""
-        if value:
-            identifiers.append({"source": _normalize_source(source), "identifier_type": identifier_type, "identifier_value": value})
-    return identifiers
-
-
-def _unmapped_fields(row: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
-    mapped_headers = {header for header in mapping.values() if header}
-    return {key: value for key, value in row.items() if key not in mapped_headers and value not in {"", None}}
-
-
-def _parsed_to_snapshot(parsed: ParsedCsvFile) -> dict[str, Any]:
-    return {
-        "file_name": parsed.file_name,
-        "headers": parsed.headers,
-        "normalized_headers": parsed.normalized_headers,
-        "rows": parsed.rows,
-    }
-
-
-def _snapshot_to_parsed(snapshot: dict[str, Any]) -> ParsedCsvFile:
-    parsed = snapshot.get("parsed_csv", snapshot)
-    return ParsedCsvFile(
-        file_name=parsed.get("file_name", ""),
-        headers=parsed.get("headers", []),
-        normalized_headers=parsed.get("normalized_headers", {}),
-        rows=parsed.get("rows", []),
-    )
-
-
-@transaction.atomic
-def create_import_batch(
-    *,
-    file_obj,
-    source: str,
-    uploaded_by,
-    season=None,
-    provision_player_accounts: bool = False,
-    activate_player_accounts: bool = True,
-) -> PlayerImportBatch:
-    """Create a persisted player import batch from a CSV upload."""
-    _ensure_staff(uploaded_by)
-    if season is None:
-        raise ValidationError("Select an active season for this player import.")
-    if not getattr(season, "is_active", False):
-        raise ValidationError("Select an active season for this player import.")
-    parsed = parse_player_csv(file_obj)
-    normalized_source = _normalize_source(source or detect_source_from_filename(parsed.file_name))
-    mapping_config = suggest_mapping(parsed.headers, source=normalized_source)
-    mapping_config[MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS] = bool(provision_player_accounts)
-    mapping_config[MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS] = bool(provision_player_accounts) and bool(activate_player_accounts)
-    batch = PlayerImportBatch.objects.create(
-        source=normalized_source,
-        original_filename=parsed.file_name,
-        uploaded_by=uploaded_by,
-        season=season,
-        status=PlayerImportStatus.UPLOADED,
-        mapping_config=mapping_config,
-        preview_snapshot={"parsed_csv": _parsed_to_snapshot(parsed)},
-        rows_processed=len(parsed.rows),
-    )
-    build_import_preview(import_batch=batch, mapping_config=mapping_config)
-    return batch
-
-
-def _match_identity(identity: dict[str, Any], source_identifiers: list[dict[str, str]]):
-    model_identity = _identity_for_model(identity)
-    match_data = {
-        "first_name": model_identity.get("first_name", ""),
-        "last_name": model_identity.get("last_name", ""),
-        "birthdate": model_identity.get("birthdate"),
-        "birth_year": model_identity.get("birth_year"),
-        "division": identity.get("division", ""),
-    }
-    if source_identifiers:
-        exact_matches = []
-        exact_score = None
-        seen_player_ids = set()
-        for identifier in source_identifiers:
-            identifier_result = match_by_identifier(
-                identifier.get("source", ""),
-                identifier.get("identifier_type", ""),
-                identifier.get("identifier_value", ""),
-            )
-            if identifier_result.status == MATCH_EXACT and identifier_result.player:
-                if identifier_result.player.id not in seen_player_ids:
-                    exact_matches.append(identifier_result.player)
-                    exact_score = identifier_result.score
-                    seen_player_ids.add(identifier_result.player.id)
-        if len(exact_matches) == 1:
-            return PlayerMatchResult(
-                status=MATCH_EXACT,
-                player=exact_matches[0],
-                candidates=exact_matches,
-                reason="Matched by source identifier.",
-                score=exact_score,
-            )
-        if len(exact_matches) > 1:
-            return PlayerMatchResult(
-                status=MATCH_AMBIGUOUS,
-                candidates=exact_matches,
-                reason="Multiple source identifiers matched different players.",
-            )
-    return find_player_match(match_data)
-
-
-def _field_conflicts(player: Player | None, identity: dict[str, Any]) -> list[dict[str, str]]:
-    if not player:
-        return []
-    model_identity = _identity_for_model(identity)
-    conflicts = []
-    for field_name in CONFLICT_FIELDS:
-        imported = model_identity.get(field_name)
-        existing = getattr(player, field_name, None)
-        if existing in {"", None} or imported in {"", None}:
-            continue
-        existing_value = _date_to_string(existing)
-        imported_value = _date_to_string(imported)
-        if existing_value != imported_value:
-            conflicts.append(
-                asdict(
-                    FieldConflict(
-                        field_name=field_name,
-                        existing_value=existing_value,
-                        imported_value=imported_value,
-                    )
-                )
-            )
-    return conflicts
-
-
-def _team_preview(roster: dict[str, Any], season) -> dict[str, Any]:
-    team_name = roster.get("team_name", "")
-    division = roster.get("division", "")
-    if not team_name or not division:
-        return {"action": "invalid_roster_context", "label": "Invalid Roster Context"}
-    normalized_name = normalize_team_value(team_name)
-    normalized_division = normalize_division_value(division)
-    existing = SeasonTeam.objects.filter(
-        season=season,
-        normalized_name=normalized_name,
-        normalized_division=normalized_division,
-    ).first()
-    return {
-        "id": existing.id if existing else None,
-        "name": existing.name if existing else team_name,
-        "division": existing.division if existing else division,
-        "action": "reuse" if existing else "create",
-        "label": "Reuse Season Team" if existing else "Create Season Team",
-    }
-
-
-def _membership_preview(player: Player | None, season_team_preview: dict[str, Any], season, roster: dict[str, Any]) -> dict[str, Any]:
-    if not player:
-        return {"action": "create", "label": "Create Membership", "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE}
-    existing_same_team = None
-    if season_team_preview.get("id"):
-        existing_same_team = PlayerRosterMembership.objects.filter(
-            player=player,
-            season_team_id=season_team_preview["id"],
-        ).first()
-    if existing_same_team:
-        return {
-            "id": existing_same_team.id,
-            "action": "update",
-            "label": "Update Membership",
-            "is_primary": existing_same_team.is_primary,
-        }
-    primary = PlayerRosterMembership.objects.select_related("season_team").filter(
-        player=player,
-        season_team__season=season,
-        is_active=True,
-        is_primary=True,
-    ).first()
-    if primary:
-        return {
-            "id": None,
-            "action": "review_team_change",
-            "label": "Review Team Change",
-            "is_primary": False,
-            "existing_primary": str(primary.season_team),
-        }
-    return {"id": None, "action": "new_season_membership", "label": "New Season Membership", "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE}
-
-
-def preview_row(*, row: dict[str, Any], mapping_config: dict[str, str], source: str, season=None) -> ImportPreviewRow:
-    """Build preview data for a single CSV row."""
-    cleaned_row = row["cleaned_row"]
-    identity = build_identity_payload(cleaned_row, mapping_config)
-    roster = build_roster_payload(cleaned_row, mapping_config)
-    source_identifiers = build_source_identifiers(cleaned_row, mapping_config, source)
-    errors = list(roster.get("errors", []))
-    if not (identity.get("first_name") and identity.get("last_name")):
-        errors.append("Map either a full name column or both first and last name columns.")
-    if not season:
-        errors.append("Select an active season for this import.")
-    if not roster.get("team_name"):
-        errors.append("Team is required for season-aware player import.")
-    if not roster.get("division"):
-        errors.append("Division is required for season-aware player import.")
-    match_result = _match_identity(identity, source_identifiers) if not errors else None
-    field_conflicts = _field_conflicts(getattr(match_result, "player", None), identity) if match_result else []
-    season_team_preview = _team_preview(roster, season) if season and not (not roster.get("team_name") or not roster.get("division")) else {
-        "action": "invalid_roster_context",
-        "label": "Invalid Roster Context",
-    }
-    matched_player = getattr(match_result, "player", None) if match_result else None
-    membership_preview = _membership_preview(matched_player, season_team_preview, season, roster) if season and not errors else {
-        "action": "invalid_roster_context",
-        "label": "Invalid Roster Context",
-        "is_primary": False,
-    }
-    if membership_preview.get("action") == "review_team_change":
-        errors.append(
-            "Player already has an active primary membership in this season. Resolve the team change manually or skip this row."
-        )
-
-    if errors:
-        action = ACTION_ERROR
-        match_status = MATCH_NO_MATCH
-    elif match_result.status == MATCH_EXACT:
-        action = ACTION_NEEDS_REVIEW if field_conflicts else ACTION_UPDATE
-        match_status = match_result.status
-    elif match_result.status == MATCH_HIGH_CONFIDENCE:
-        action = ACTION_NEEDS_REVIEW if field_conflicts else ACTION_UPDATE
-        match_status = match_result.status
-    elif match_result.status == MATCH_AMBIGUOUS:
-        action = ACTION_NEEDS_REVIEW
-        match_status = match_result.status
-    else:
-        action = ACTION_CREATE
-        match_status = MATCH_NO_MATCH
-
-    candidates = getattr(match_result, "candidates", []) if match_result else []
-    return ImportPreviewRow(
-        row_number=row["row_number"],
-        identity=identity,
-        original_row=row["original_row"],
-        unmapped_fields=_unmapped_fields(cleaned_row, mapping_config),
-        source_identifiers=source_identifiers,
-        match_status=match_status,
-        matched_player_id=getattr(matched_player, "id", None),
-        matched_player_name=getattr(matched_player, "display_name", ""),
-        candidate_ids=[candidate.id for candidate in candidates],
-        candidate_names=[candidate.display_name for candidate in candidates],
-        candidate_options=[{"id": candidate.id, "name": candidate.display_name} for candidate in candidates],
-        field_conflicts=field_conflicts,
-        errors=errors,
-        action=action,
-        roster={key: value for key, value in roster.items() if key != "errors"},
-        season_team=season_team_preview,
-        membership=membership_preview,
-    )
-
-
-@transaction.atomic
-def build_import_preview(*, import_batch: PlayerImportBatch, mapping_config: dict[str, str] | None = None) -> dict[str, Any]:
-    """Build and persist an import preview for a batch."""
-    parsed = _snapshot_to_parsed(import_batch.preview_snapshot)
-    mapping_config = mapping_config or import_batch.mapping_config or suggest_mapping(parsed.headers, source=import_batch.source)
-    rows = [
-        _json_preview_row(preview_row(row=row, mapping_config=mapping_config, source=import_batch.source, season=import_batch.season))
-        for row in parsed.rows
-    ]
-    row_errors = [row for row in rows if row["errors"]]
-    conflicted_rows = [row for row in rows if row["action"] == ACTION_NEEDS_REVIEW]
-    preview = {
-        "file_name": parsed.file_name,
-        "source": import_batch.source,
-        "season": {
-            "id": import_batch.season_id,
-            "name": import_batch.season.name if import_batch.season_id else "Legacy / No Season",
-        },
-        "headers": parsed.headers,
-        "mapping_config": mapping_config,
-        "account_provisioning": {
-            "enabled": bool(mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS)),
-            "activate_users": bool(mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS)),
-            "email_column": mapping_config.get("account_email", ""),
-        },
-        "rows": rows,
-        "summary": {
-            "rows_processed": len(rows),
-            "rows_create": sum(1 for row in rows if row["action"] == ACTION_CREATE),
-            "rows_update": sum(1 for row in rows if row["action"] == ACTION_UPDATE),
-            "rows_needs_review": len(conflicted_rows),
-            "rows_error": len(row_errors),
-            "season_teams_create": sum(1 for row in rows if row.get("season_team", {}).get("action") == "create"),
-            "season_teams_reuse": sum(1 for row in rows if row.get("season_team", {}).get("action") == "reuse"),
-            "memberships_create": sum(1 for row in rows if row.get("membership", {}).get("action") in {"create", "new_season_membership"}),
-            "memberships_update": sum(1 for row in rows if row.get("membership", {}).get("action") == "update"),
-        },
-    }
-    import_batch.mapping_config = mapping_config
-    import_batch.preview_snapshot = {"parsed_csv": _parsed_to_snapshot(parsed), "preview": preview}
-    import_batch.row_errors = row_errors
-    import_batch.conflict_summary = {
-        "rows_conflicted": len(conflicted_rows),
-        "row_numbers": [row["row_number"] for row in conflicted_rows],
-    }
-    import_batch.rows_processed = len(rows)
-    import_batch.rows_conflicted = len(conflicted_rows)
-    import_batch.status = PlayerImportStatus.NEEDS_REVIEW if conflicted_rows or row_errors else PlayerImportStatus.PREVIEWED
-    import_batch.save(
-        update_fields=[
-            "mapping_config",
-            "preview_snapshot",
-            "row_errors",
-            "conflict_summary",
-            "rows_processed",
-            "rows_conflicted",
-            "status",
-            "updated_at",
-        ]
-    )
-    return preview
-
-
-def current_preview(import_batch: PlayerImportBatch) -> dict[str, Any]:
-    """Return the current persisted preview for a batch."""
-    return import_batch.preview_snapshot.get("preview", {})
-
-
-def create_player_from_import(identity: dict[str, Any]) -> Player:
-    """Create a canonical player from import identity fields."""
-    return Player.objects.create(**_identity_for_model(identity))
-
-
-def apply_player_updates(player: Player, identity: dict[str, Any], field_resolutions: dict[str, str] | None = None) -> Player:
-    """Fill blank player fields and apply explicit conflict resolutions."""
-    field_resolutions = field_resolutions or {}
-    model_identity = _identity_for_model(identity)
-    changed_fields = []
-    for field_name, imported_value in model_identity.items():
-        existing_value = getattr(player, field_name)
-        should_update = existing_value in {"", None} or field_resolutions.get(field_name) == RESOLUTION_USE_IMPORTED
-        if should_update and imported_value not in {"", None} and existing_value != imported_value:
-            setattr(player, field_name, imported_value)
-            changed_fields.append(field_name)
-    if changed_fields:
-        changed_fields.append("updated_at")
-        player.save(update_fields=changed_fields)
-    return player
-
-
-def attach_source_identifiers(player: Player, identifiers: list[dict[str, str]], metadata: dict[str, Any] | None = None):
-    """Attach source identifiers, reporting duplicate ownership conflicts as errors."""
-    errors = []
-    for identifier in identifiers:
-        source = _normalize_source(identifier["source"])
-        identifier_type = normalize_header(identifier["identifier_type"]).replace(" ", "_")
-        identifier_value = normalize_header(identifier["identifier_value"])
-        existing = PlayerSourceIdentifier.objects.filter(
-            source=source,
-            identifier_type=identifier_type,
-            identifier_value=identifier_value,
-        ).select_related("player").first()
-        if existing:
-            if existing.player_id != player.id:
-                errors.append(
-                    f"Identifier {source}:{identifier_type}:{identifier_value} already belongs to {existing.player.display_name}."
-                )
-            continue
-        try:
-            PlayerSourceIdentifier.objects.create(
-                player=player,
-                source=source,
-                identifier_type=identifier_type,
-                identifier_value=identifier_value,
-                metadata=metadata or {},
-            )
-        except IntegrityError:
-            errors.append(f"Identifier {source}:{identifier_type}:{identifier_value} could not be attached.")
-    return errors
-
-
-def record_import_source_row(player: Player, import_batch: PlayerImportBatch, preview: dict[str, Any], actor) -> PlayerSourceRow:
-    """Record row-level provenance for a committed player import row."""
-    return PlayerSourceRow.objects.create(
-        player=player,
-        import_batch=import_batch,
-        source=import_batch.source,
-        source_filename=import_batch.original_filename,
-        row_number=preview["row_number"],
-        original_row=preview["original_row"],
-        unmapped_fields=preview["unmapped_fields"],
-        imported_by=actor,
-    )
-
-
-def _parse_iso_date(value: str):
-    cleaned = clean_cell(value)
-    if not cleaned:
-        return None
-    try:
-        return datetime.strptime(cleaned, "%Y-%m-%d").date()
-    except ValueError:
-        raise ValidationError("Roster date is invalid.") from None
-
-
-def _membership_update_values(roster: dict[str, Any]) -> dict[str, Any]:
-    values = {}
-    if roster.get("roster_status"):
-        values["status"] = roster["roster_status"]
-        values["is_active"] = roster["roster_status"] in {RosterStatus.ACTIVE, RosterStatus.GUEST}
-        if not values["is_active"]:
-            values["is_primary"] = False
-    if roster.get("jersey_number"):
-        values["jersey_number"] = roster["jersey_number"]
-    if roster.get("starts_on"):
-        values["starts_on"] = _parse_iso_date(roster["starts_on"])
-    if roster.get("ends_on"):
-        values["ends_on"] = _parse_iso_date(roster["ends_on"])
-    if roster.get("roster_source_id"):
-        values["source_identifier"] = roster["roster_source_id"]
-    return values
-
-
-def _commit_membership(player: Player, import_batch: PlayerImportBatch, preview_row_data: dict[str, Any]) -> tuple[str, bool]:
-    if not import_batch.season_id:
-        raise ValidationError("Import batch requires a season before memberships can be committed.")
-    roster = preview_row_data.get("roster", {})
-    team_name = roster.get("team_name", "")
-    division = roster.get("division", "")
-    if not team_name or not division:
-        raise ValidationError("Team and division are required for roster membership.")
-    season_team, team_created = get_or_create_season_team(
-        season=import_batch.season,
-        name=team_name,
-        division=division,
-        external_source=import_batch.source if roster.get("roster_source_id") else "",
-        external_identifier=roster.get("roster_source_id", ""),
-        metadata={"import_batch_id": import_batch.id},
-    )
-    existing = PlayerRosterMembership.objects.select_for_update().filter(player=player, season_team=season_team).first()
-    values = _membership_update_values(roster)
-    values.setdefault("source", import_batch.source)
-    if existing:
-        was_primary = existing.is_primary
-        update_membership(existing, sync_player_fields=was_primary, **values)
-        return "updated", team_created
-
-    primary = PlayerRosterMembership.objects.select_for_update().filter(
-        player=player,
-        season_team__season=import_batch.season,
-        is_active=True,
-        is_primary=True,
-    ).first()
-    if primary:
-        raise ValidationError("Player already has an active primary membership in this season.")
-    status = values.pop("status", roster.get("roster_status") or RosterStatus.ACTIVE)
-    is_active = values.pop("is_active", status in {RosterStatus.ACTIVE, RosterStatus.GUEST})
-    membership = create_membership(
-        player=player,
-        season_team=season_team,
-        status=status,
-        is_primary=is_active,
-        is_active=is_active,
-        source=values.pop("source", import_batch.source),
-        source_identifier=values.pop("source_identifier", roster.get("roster_source_id", "")),
-        import_batch=import_batch,
-        metadata={"row_number": preview_row_data["row_number"]},
-        sync_player_fields=is_active,
-        **values,
-    )
-    if membership.is_primary:
-        sync_player_current_team_fields(player, import_batch.season)
-    return "created", team_created
-
-
-def _resolutions_for_row(resolutions: dict[str, Any], row_number: int) -> tuple[str, dict[str, str]]:
-    row_key = str(row_number)
-    row_resolution = resolutions.get(row_key, {}) if resolutions else {}
-    return row_resolution.get("action", RESOLUTION_ACTION_COMMIT), row_resolution.get("fields", {})
-
-
-def _candidate_id_for_row(resolutions: dict[str, Any], row_number: int) -> int | None:
-    row_key = str(row_number)
-    row_resolution = resolutions.get(row_key, {}) if resolutions else {}
-    candidate_id = row_resolution.get("candidate_id")
-    if not candidate_id:
-        return None
-    try:
-        return int(candidate_id)
-    except (TypeError, ValueError):
-        return None
-
-
-def _unresolved_review_messages(preview: dict[str, Any], resolutions: dict[str, Any]) -> list[str]:
-    messages = []
-    for preview_row_data in preview.get("rows", []):
-        row_number = preview_row_data["row_number"]
-        row_action, field_resolutions = _resolutions_for_row(resolutions, row_number)
-        if row_action == ACTION_SKIP:
-            continue
-        if preview_row_data["action"] == ACTION_ERROR:
-            messages.append(f"Row {row_number}: fix mapping/data errors or explicitly skip the row.")
-            continue
-        if preview_row_data["match_status"] == MATCH_AMBIGUOUS:
-            candidate_id = _candidate_id_for_row(resolutions, row_number)
-            if row_action == RESOLUTION_ACTION_CREATE_NEW:
-                continue
-            if row_action == RESOLUTION_ACTION_USE_CANDIDATE and candidate_id in preview_row_data.get("candidate_ids", []):
-                continue
-            messages.append(f"Row {row_number}: choose an existing candidate, create a new player, or skip the row.")
-            continue
-        if preview_row_data["action"] == ACTION_NEEDS_REVIEW:
-            conflict_fields = {conflict["field_name"] for conflict in preview_row_data.get("field_conflicts", [])}
-            resolved_fields = set(field_resolutions)
-            if conflict_fields and conflict_fields.issubset(resolved_fields):
-                continue
-            messages.append(f"Row {row_number}: resolve all field conflicts or explicitly skip the row.")
-    return messages
-
-
-@transaction.atomic
-def commit_import_batch(*, import_batch: PlayerImportBatch, actor, resolutions: dict[str, Any] | None = None) -> ImportCommitResult:
-    """Commit a previewed import batch to canonical player records."""
-    _ensure_staff(actor)
-    resolutions = resolutions or {}
-    locked_batch = PlayerImportBatch.objects.select_for_update().get(pk=import_batch.pk)
-    if locked_batch.status == PlayerImportStatus.COMMITTED:
-        raise ValidationError("This import batch has already been committed.")
-    if not locked_batch.season_id:
-        raise ValidationError("Select an active season before committing this player import.")
-
-    preview = current_preview(locked_batch)
-    if not preview:
-        preview = build_import_preview(import_batch=locked_batch)
-
-    unresolved_messages = _unresolved_review_messages(preview, resolutions)
-    if unresolved_messages:
-        locked_batch.status = PlayerImportStatus.NEEDS_REVIEW
-        locked_batch.row_errors = unresolved_messages
-        locked_batch.save(update_fields=["status", "row_errors", "updated_at"])
-        raise ValidationError("Resolve or explicitly skip review rows before committing this import.")
-
-    result = ImportCommitResult(rows_processed=len(preview.get("rows", [])))
-    committed_rows = []
-    for preview_row_data in preview.get("rows", []):
-        row_number = preview_row_data["row_number"]
-        row_action, field_resolutions = _resolutions_for_row(resolutions, row_number)
-        if row_action == ACTION_SKIP:
-            result.skipped += 1
-            continue
-        if preview_row_data["action"] == ACTION_ERROR:
-            result.skipped += 1
-            result.errors.append(f"Row {row_number}: {'; '.join(preview_row_data['errors'])}")
-            continue
-
-        player = None
-        if preview_row_data["match_status"] == MATCH_AMBIGUOUS:
-            if row_action == RESOLUTION_ACTION_CREATE_NEW:
-                player = create_player_from_import(preview_row_data["identity"])
-                result.created += 1
-            else:
-                candidate_id = _candidate_id_for_row(resolutions, row_number)
-                player = Player.objects.select_for_update().get(pk=candidate_id)
-                apply_player_updates(player, preview_row_data["identity"])
-                result.updated += 1
-        elif preview_row_data["matched_player_id"]:
-            player = Player.objects.select_for_update().get(pk=preview_row_data["matched_player_id"])
-            apply_player_updates(player, preview_row_data["identity"], field_resolutions=field_resolutions)
-            result.updated += 1
-        else:
-            player = create_player_from_import(preview_row_data["identity"])
-            result.created += 1
-
-        identifier_errors = attach_source_identifiers(
-            player,
-            preview_row_data.get("source_identifiers", []),
-            metadata={"import_batch_id": locked_batch.id, "row_number": row_number},
-        )
-        result.errors.extend([f"Row {row_number}: {error}" for error in identifier_errors])
-        record_import_source_row(player, locked_batch, preview_row_data, actor)
-        membership_action, team_created = _commit_membership(player, locked_batch, preview_row_data)
-        if team_created:
-            result.season_teams_created += 1
-        else:
-            result.season_teams_reused += 1
-        if membership_action == "created":
-            result.memberships_created += 1
-        else:
-            result.memberships_updated += 1
-        committed_rows.append(
-            {
-                "player": player,
-                "row_number": row_number,
-                "original_row": preview_row_data.get("original_row", {}),
-            }
-        )
-
-    if locked_batch.mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS):
-        from accounts.services.provisioning_service import ProvisioningOptions, provision_accounts_for_import
-
-        provisioning_summary = provision_accounts_for_import(
-            locked_batch,
-            committed_rows,
-            actor=actor,
-            options=ProvisioningOptions(
-                enabled=True,
-                activate_users=True,
-                email_column=locked_batch.mapping_config.get("account_email", ""),
-            ),
-        )
-        result.account_provisioning = provisioning_summary.to_dict()
-
-    locked_batch.status = PlayerImportStatus.COMMITTED
-    locked_batch.rows_created = result.created
-    locked_batch.rows_updated = result.updated
-    locked_batch.rows_skipped = result.skipped
-    locked_batch.rows_conflicted = result.conflicts
-    locked_batch.import_summary = asdict(result)
-    locked_batch.row_errors = result.errors
-    locked_batch.committed_at = timezone.now()
-    locked_batch.save(
-        update_fields=[
-            "status",
-            "rows_created",
-            "rows_updated",
-            "rows_skipped",
-            "rows_conflicted",
-            "import_summary",
-            "row_errors",
-            "committed_at",
-            "updated_at",
-        ]
-    )
-    return result
diff --git a/players/services/imports/__init__.py b/players/services/imports/__init__.py
new file mode 100644
index 0000000..de1c212
--- /dev/null
+++ b/players/services/imports/__init__.py
@@ -0,0 +1 @@
+"""Internal player import service modules."""
diff --git a/players/services/imports/commit.py b/players/services/imports/commit.py
new file mode 100644
index 0000000..07a6823
--- /dev/null
+++ b/players/services/imports/commit.py
@@ -0,0 +1,391 @@
+"""Commit orchestration for player import batches."""
+
+from __future__ import annotations
+
+from dataclasses import asdict
+from typing import Any
+
+from django.core.exceptions import PermissionDenied, ValidationError
+from django.db import IntegrityError, transaction
+from django.utils import timezone
+
+from players.models import (
+    Player,
+    PlayerImportBatch,
+    PlayerImportStatus,
+    PlayerSourceIdentifier,
+    PlayerSourceRow,
+)
+from players.services.imports.constants import (
+    ACTION_ERROR,
+    ACTION_NEEDS_REVIEW,
+    ACTION_SKIP,
+    MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
+    MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
+    RESOLUTION_ACTION_COMMIT,
+    RESOLUTION_ACTION_CREATE_NEW,
+    RESOLUTION_ACTION_USE_CANDIDATE,
+    RESOLUTION_USE_IMPORTED,
+)
+from players.services.imports.mapping import (
+    identity_for_model,
+    parsed_to_snapshot,
+)
+from players.services.imports.parsing import (
+    detect_source_from_filename,
+    normalize_header,
+    normalize_source,
+    parse_player_csv,
+    suggest_mapping,
+)
+from players.services.imports.preview import build_import_preview, current_preview
+from players.services.imports.result_models import ImportCommitResult
+from players.services.imports.roster import commit_membership
+from players.services.matching_service import MATCH_AMBIGUOUS
+
+
+def ensure_staff(actor):
+    if (
+        not actor
+        or not actor.is_authenticated
+        or not (actor.is_staff or actor.is_superuser)
+    ):
+        raise PermissionDenied("Only staff/admin users can run player imports.")
+
+
+@transaction.atomic
+def create_import_batch(
+    *,
+    file_obj,
+    source: str,
+    uploaded_by,
+    season=None,
+    provision_player_accounts: bool = False,
+    activate_player_accounts: bool = True,
+) -> PlayerImportBatch:
+    """Create a persisted player import batch from a CSV upload."""
+    ensure_staff(uploaded_by)
+    if season is None:
+        raise ValidationError("Select an active season for this player import.")
+    if not getattr(season, "is_active", False):
+        raise ValidationError("Select an active season for this player import.")
+    parsed = parse_player_csv(file_obj)
+    normalized_source = normalize_source(
+        source or detect_source_from_filename(parsed.file_name)
+    )
+    mapping_config = suggest_mapping(parsed.headers, source=normalized_source)
+    mapping_config[MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS] = bool(
+        provision_player_accounts
+    )
+    mapping_config[MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS] = bool(
+        provision_player_accounts
+    ) and bool(activate_player_accounts)
+    batch = PlayerImportBatch.objects.create(
+        source=normalized_source,
+        original_filename=parsed.file_name,
+        uploaded_by=uploaded_by,
+        season=season,
+        status=PlayerImportStatus.UPLOADED,
+        mapping_config=mapping_config,
+        preview_snapshot={"parsed_csv": parsed_to_snapshot(parsed)},
+        rows_processed=len(parsed.rows),
+    )
+    build_import_preview(import_batch=batch, mapping_config=mapping_config)
+    return batch
+
+
+def create_player_from_import(identity: dict[str, Any]) -> Player:
+    """Create a canonical player from import identity fields."""
+    return Player.objects.create(**identity_for_model(identity))
+
+
+def apply_player_updates(
+    player: Player,
+    identity: dict[str, Any],
+    field_resolutions: dict[str, str] | None = None,
+) -> Player:
+    """Fill blank player fields and apply explicit conflict resolutions."""
+    field_resolutions = field_resolutions or {}
+    model_identity = identity_for_model(identity)
+    changed_fields = []
+    for field_name, imported_value in model_identity.items():
+        existing_value = getattr(player, field_name)
+        should_update = (
+            existing_value in {"", None}
+            or field_resolutions.get(field_name) == RESOLUTION_USE_IMPORTED
+        )
+        if (
+            should_update
+            and imported_value not in {"", None}
+            and existing_value != imported_value
+        ):
+            setattr(player, field_name, imported_value)
+            changed_fields.append(field_name)
+    if changed_fields:
+        changed_fields.append("updated_at")
+        player.save(update_fields=changed_fields)
+    return player
+
+
+def attach_source_identifiers(
+    player: Player,
+    identifiers: list[dict[str, str]],
+    metadata: dict[str, Any] | None = None,
+):
+    """Attach source identifiers, reporting duplicate ownership conflicts as errors."""
+    errors = []
+    for identifier in identifiers:
+        source = normalize_source(identifier["source"])
+        identifier_type = normalize_header(identifier["identifier_type"]).replace(
+            " ", "_"
+        )
+        identifier_value = normalize_header(identifier["identifier_value"])
+        existing = (
+            PlayerSourceIdentifier.objects.filter(
+                source=source,
+                identifier_type=identifier_type,
+                identifier_value=identifier_value,
+            )
+            .select_related("player")
+            .first()
+        )
+        if existing:
+            if existing.player_id != player.id:
+                errors.append(
+                    f"Identifier {source}:{identifier_type}:{identifier_value} "
+                    f"already belongs to {existing.player.display_name}."
+                )
+            continue
+        try:
+            PlayerSourceIdentifier.objects.create(
+                player=player,
+                source=source,
+                identifier_type=identifier_type,
+                identifier_value=identifier_value,
+                metadata=metadata or {},
+            )
+        except IntegrityError:
+            errors.append(
+                f"Identifier {source}:{identifier_type}:{identifier_value} could not be attached."
+            )
+    return errors
+
+
+def record_import_source_row(
+    player: Player, import_batch: PlayerImportBatch, preview: dict[str, Any], actor
+) -> PlayerSourceRow:
+    """Record row-level provenance for a committed player import row."""
+    return PlayerSourceRow.objects.create(
+        player=player,
+        import_batch=import_batch,
+        source=import_batch.source,
+        source_filename=import_batch.original_filename,
+        row_number=preview["row_number"],
+        original_row=preview["original_row"],
+        unmapped_fields=preview["unmapped_fields"],
+        imported_by=actor,
+    )
+
+
+def resolutions_for_row(
+    resolutions: dict[str, Any], row_number: int
+) -> tuple[str, dict[str, str]]:
+    row_key = str(row_number)
+    row_resolution = resolutions.get(row_key, {}) if resolutions else {}
+    return row_resolution.get("action", RESOLUTION_ACTION_COMMIT), row_resolution.get(
+        "fields", {}
+    )
+
+
+def candidate_id_for_row(resolutions: dict[str, Any], row_number: int) -> int | None:
+    row_key = str(row_number)
+    row_resolution = resolutions.get(row_key, {}) if resolutions else {}
+    candidate_id = row_resolution.get("candidate_id")
+    if not candidate_id:
+        return None
+    try:
+        return int(candidate_id)
+    except (TypeError, ValueError):
+        return None
+
+
+def unresolved_review_messages(
+    preview: dict[str, Any], resolutions: dict[str, Any]
+) -> list[str]:
+    messages = []
+    for preview_row_data in preview.get("rows", []):
+        row_number = preview_row_data["row_number"]
+        row_action, field_resolutions = resolutions_for_row(resolutions, row_number)
+        if row_action == ACTION_SKIP:
+            continue
+        if preview_row_data["action"] == ACTION_ERROR:
+            messages.append(
+                f"Row {row_number}: fix mapping/data errors or explicitly skip the row."
+            )
+            continue
+        if preview_row_data["match_status"] == MATCH_AMBIGUOUS:
+            candidate_id = candidate_id_for_row(resolutions, row_number)
+            if row_action == RESOLUTION_ACTION_CREATE_NEW:
+                continue
+            if (
+                row_action == RESOLUTION_ACTION_USE_CANDIDATE
+                and candidate_id in preview_row_data.get("candidate_ids", [])
+            ):
+                continue
+            messages.append(
+                f"Row {row_number}: choose an existing candidate, create a new player, "
+                "or skip the row."
+            )
+            continue
+        if preview_row_data["action"] == ACTION_NEEDS_REVIEW:
+            conflict_fields = {
+                conflict["field_name"]
+                for conflict in preview_row_data.get("field_conflicts", [])
+            }
+            resolved_fields = set(field_resolutions)
+            if conflict_fields and conflict_fields.issubset(resolved_fields):
+                continue
+            messages.append(
+                f"Row {row_number}: resolve all field conflicts or explicitly skip the row."
+            )
+    return messages
+
+
+@transaction.atomic
+def commit_import_batch(
+    *,
+    import_batch: PlayerImportBatch,
+    actor,
+    resolutions: dict[str, Any] | None = None,
+) -> ImportCommitResult:
+    """Commit a previewed import batch to canonical player records."""
+    ensure_staff(actor)
+    resolutions = resolutions or {}
+    locked_batch = PlayerImportBatch.objects.select_for_update().get(pk=import_batch.pk)
+    if locked_batch.status == PlayerImportStatus.COMMITTED:
+        raise ValidationError("This import batch has already been committed.")
+    if not locked_batch.season_id:
+        raise ValidationError(
+            "Select an active season before committing this player import."
+        )
+
+    preview = current_preview(locked_batch)
+    if not preview:
+        preview = build_import_preview(import_batch=locked_batch)
+
+    unresolved_messages = unresolved_review_messages(preview, resolutions)
+    if unresolved_messages:
+        locked_batch.status = PlayerImportStatus.NEEDS_REVIEW
+        locked_batch.row_errors = unresolved_messages
+        locked_batch.save(update_fields=["status", "row_errors", "updated_at"])
+        raise ValidationError(
+            "Resolve or explicitly skip review rows before committing this import."
+        )
+
+    result = ImportCommitResult(rows_processed=len(preview.get("rows", [])))
+    committed_rows = []
+    for preview_row_data in preview.get("rows", []):
+        row_number = preview_row_data["row_number"]
+        row_action, field_resolutions = resolutions_for_row(resolutions, row_number)
+        if row_action == ACTION_SKIP:
+            result.skipped += 1
+            continue
+        if preview_row_data["action"] == ACTION_ERROR:
+            result.skipped += 1
+            result.errors.append(
+                f"Row {row_number}: {'; '.join(preview_row_data['errors'])}"
+            )
+            continue
+
+        player = None
+        if preview_row_data["match_status"] == MATCH_AMBIGUOUS:
+            if row_action == RESOLUTION_ACTION_CREATE_NEW:
+                player = create_player_from_import(preview_row_data["identity"])
+                result.created += 1
+            else:
+                candidate_id = candidate_id_for_row(resolutions, row_number)
+                player = Player.objects.select_for_update().get(pk=candidate_id)
+                apply_player_updates(player, preview_row_data["identity"])
+                result.updated += 1
+        elif preview_row_data["matched_player_id"]:
+            player = Player.objects.select_for_update().get(
+                pk=preview_row_data["matched_player_id"]
+            )
+            apply_player_updates(
+                player,
+                preview_row_data["identity"],
+                field_resolutions=field_resolutions,
+            )
+            result.updated += 1
+        else:
+            player = create_player_from_import(preview_row_data["identity"])
+            result.created += 1
+
+        identifier_errors = attach_source_identifiers(
+            player,
+            preview_row_data.get("source_identifiers", []),
+            metadata={"import_batch_id": locked_batch.id, "row_number": row_number},
+        )
+        result.errors.extend(
+            [f"Row {row_number}: {error}" for error in identifier_errors]
+        )
+        record_import_source_row(player, locked_batch, preview_row_data, actor)
+        membership_action, team_created = commit_membership(
+            player, locked_batch, preview_row_data
+        )
+        if team_created:
+            result.season_teams_created += 1
+        else:
+            result.season_teams_reused += 1
+        if membership_action == "created":
+            result.memberships_created += 1
+        else:
+            result.memberships_updated += 1
+        committed_rows.append(
+            {
+                "player": player,
+                "row_number": row_number,
+                "original_row": preview_row_data.get("original_row", {}),
+            }
+        )
+
+    if locked_batch.mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS):
+        from accounts.services.provisioning_service import (
+            ProvisioningOptions,
+            provision_accounts_for_import,
+        )
+
+        provisioning_summary = provision_accounts_for_import(
+            locked_batch,
+            committed_rows,
+            actor=actor,
+            options=ProvisioningOptions(
+                enabled=True,
+                activate_users=True,
+                email_column=locked_batch.mapping_config.get("account_email", ""),
+            ),
+        )
+        result.account_provisioning = provisioning_summary.to_dict()
+
+    locked_batch.status = PlayerImportStatus.COMMITTED
+    locked_batch.rows_created = result.created
+    locked_batch.rows_updated = result.updated
+    locked_batch.rows_skipped = result.skipped
+    locked_batch.rows_conflicted = result.conflicts
+    locked_batch.import_summary = asdict(result)
+    locked_batch.row_errors = result.errors
+    locked_batch.committed_at = timezone.now()
+    locked_batch.save(
+        update_fields=[
+            "status",
+            "rows_created",
+            "rows_updated",
+            "rows_skipped",
+            "rows_conflicted",
+            "import_summary",
+            "row_errors",
+            "committed_at",
+            "updated_at",
+        ]
+    )
+    return result
diff --git a/players/services/imports/constants.py b/players/services/imports/constants.py
new file mode 100644
index 0000000..b239bf3
--- /dev/null
+++ b/players/services/imports/constants.py
@@ -0,0 +1,130 @@
+"""Constants used by the player import workflow."""
+
+SOURCE_MEMBER_LIST = "vcb_member_list_csv"
+SOURCE_ROSTER_DETAIL = "vcb_roster_detail_csv"
+SOURCE_MANUAL_STAFF = "manual_staff_csv"
+
+SOURCE_CHOICES = [
+    (SOURCE_MEMBER_LIST, "VCB member list CSV"),
+    (SOURCE_ROSTER_DETAIL, "VCB roster detail CSV"),
+    (SOURCE_MANUAL_STAFF, "Manual staff CSV"),
+]
+
+MAX_CSV_UPLOAD_BYTES = 5 * 1024 * 1024
+MAX_CSV_ROWS = 5000
+
+MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS = "_provision_player_accounts"
+MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS = "_activate_player_accounts"
+
+ACTION_CREATE = "create"
+ACTION_UPDATE = "update"
+ACTION_NEEDS_REVIEW = "needs_review"
+ACTION_SKIP = "skip"
+ACTION_ERROR = "error"
+
+RESOLUTION_ACTION_COMMIT = "commit"
+RESOLUTION_ACTION_CREATE_NEW = "create_new"
+RESOLUTION_ACTION_USE_CANDIDATE = "use_candidate"
+RESOLUTION_KEEP_EXISTING = "keep_existing"
+RESOLUTION_USE_IMPORTED = "use_imported"
+RESOLUTION_METADATA_ONLY = "metadata_only"
+
+PLAYER_FIELD_KEYS = [
+    "first_name",
+    "last_name",
+    "preferred_name",
+    "birthdate",
+    "birth_year",
+    "gender",
+    "division",
+    "team_name",
+    "primary_positions",
+    "bats",
+    "throws",
+    "school",
+    "graduation_year",
+]
+
+PERMANENT_PLAYER_FIELD_KEYS = [
+    "first_name",
+    "last_name",
+    "preferred_name",
+    "birthdate",
+    "birth_year",
+    "gender",
+    "primary_positions",
+    "bats",
+    "throws",
+    "school",
+    "graduation_year",
+]
+
+CONFLICT_FIELDS = [
+    "first_name",
+    "last_name",
+    "preferred_name",
+    "birthdate",
+    "birth_year",
+    "gender",
+    "primary_positions",
+    "bats",
+    "throws",
+    "school",
+    "graduation_year",
+]
+
+IDENTIFIER_FIELD_TYPES = {
+    "registration_id": "registration_id",
+    "registrant_id": "registrant_id",
+    "team_id": "team_id",
+    "source_player_id": "source_player_id",
+}
+
+HEADER_ALIASES = {
+    "first_name": {
+        "first",
+        "first name",
+        "firstname",
+        "given name",
+        "player first name",
+    },
+    "last_name": {
+        "last",
+        "last name",
+        "lastname",
+        "surname",
+        "family name",
+        "player last name",
+    },
+    "full_name": {"name", "full name", "player", "player name"},
+    "preferred_name": {"preferred", "preferred name", "nickname", "nick name"},
+    "birthdate": {"birthdate", "birth date", "date of birth", "dob"},
+    "birth_year": {"birth year", "year of birth", "yob"},
+    "gender": {"gender", "sex"},
+    "division": {"division", "level", "program"},
+    "team_name": {"team", "team name", "current team"},
+    "roster_status": {"roster status", "status", "membership status"},
+    "jersey_number": {"jersey", "jersey number", "number", "uniform number"},
+    "membership_start_date": {
+        "membership start date",
+        "start date",
+        "starts on",
+        "roster start",
+    },
+    "membership_end_date": {"membership end date", "end date", "ends on", "roster end"},
+    "roster_source_id": {"roster source id", "membership id", "roster id"},
+    "primary_positions": {
+        "position",
+        "positions",
+        "primary position",
+        "primary positions",
+    },
+    "bats": {"bats", "batting", "hits"},
+    "throws": {"throws", "throwing"},
+    "school": {"school"},
+    "graduation_year": {"graduation year", "grad year", "class year"},
+    "registration_id": {"registration id", "registration", "reg id"},
+    "registrant_id": {"registrant id", "member id", "participant id"},
+    "team_id": {"team id", "teamid"},
+    "source_player_id": {"player id", "source player id", "external player id"},
+}
diff --git a/players/services/imports/mapping.py b/players/services/imports/mapping.py
new file mode 100644
index 0000000..5018a94
--- /dev/null
+++ b/players/services/imports/mapping.py
@@ -0,0 +1,180 @@
+"""Column mapping and row normalization for player imports."""
+
+from __future__ import annotations
+
+from datetime import date
+from typing import Any
+
+from django.core.exceptions import ValidationError
+
+from players.services.imports.constants import (
+    IDENTIFIER_FIELD_TYPES,
+    PERMANENT_PLAYER_FIELD_KEYS,
+    PLAYER_FIELD_KEYS,
+)
+from players.services.imports.parsing import (
+    clean_cell,
+    normalize_source,
+    parse_birth_year,
+    parse_birthdate,
+    parse_import_date,
+    parse_roster_status,
+    split_full_name,
+)
+from players.services.imports.result_models import ParsedCsvFile
+from seasons.models import RosterStatus
+
+
+def date_to_string(value) -> str:
+    if isinstance(value, date):
+        return value.isoformat()
+    return clean_cell(value)
+
+
+def parse_identity_value(field_name: str, value):
+    if field_name == "birthdate":
+        return parse_birthdate(value) if not isinstance(value, date) else value
+    if field_name in {"birth_year", "graduation_year"}:
+        return parse_birth_year(value)
+    return clean_cell(value)
+
+
+def identity_for_storage(identity: dict[str, Any]) -> dict[str, Any]:
+    stored = {}
+    for key, value in identity.items():
+        if isinstance(value, date):
+            stored[key] = value.isoformat()
+        else:
+            stored[key] = value
+    return stored
+
+
+def identity_for_model(identity: dict[str, Any]) -> dict[str, Any]:
+    model_identity = {}
+    for field_name in PERMANENT_PLAYER_FIELD_KEYS:
+        value = identity.get(field_name)
+        if field_name == "birthdate" and value:
+            value = parse_birthdate(value) if not isinstance(value, date) else value
+        elif field_name in {"birth_year", "graduation_year"} and value:
+            value = parse_birth_year(value)
+        if value not in {"", None}:
+            model_identity[field_name] = value
+    return model_identity
+
+
+def build_roster_payload(
+    row: dict[str, Any], mapping: dict[str, str] | None = None
+) -> dict[str, Any]:
+    """Build season roster context from a source row and optional column mapping."""
+    mapping = mapping or {}
+    status_column = mapping.get("roster_status", "")
+    starts_column = mapping.get("membership_start_date", "")
+    ends_column = mapping.get("membership_end_date", "")
+    try:
+        roster_status = (
+            parse_roster_status(row.get(status_column, ""))
+            if status_column
+            else RosterStatus.ACTIVE
+        )
+    except ValidationError as exc:
+        roster_status = ""
+        status_errors = list(exc.messages)
+    else:
+        status_errors = []
+
+    starts_on = parse_import_date(row.get(starts_column, "")) if starts_column else None
+    ends_on = parse_import_date(row.get(ends_column, "")) if ends_column else None
+    errors = status_errors
+    if starts_column and clean_cell(row.get(starts_column)) and starts_on is None:
+        errors.append("Membership start date is invalid.")
+    if ends_column and clean_cell(row.get(ends_column)) and ends_on is None:
+        errors.append("Membership end date is invalid.")
+    if starts_on and ends_on and ends_on < starts_on:
+        errors.append("Membership end date cannot be before start date.")
+
+    return {
+        "team_name": clean_cell(row.get(mapping.get("team_name", "team_name"))),
+        "division": clean_cell(row.get(mapping.get("division", "division"))),
+        "roster_status": roster_status,
+        "jersey_number": (
+            clean_cell(row.get(mapping.get("jersey_number", "")))
+            if mapping.get("jersey_number")
+            else ""
+        ),
+        "starts_on": starts_on.isoformat() if starts_on else "",
+        "ends_on": ends_on.isoformat() if ends_on else "",
+        "roster_source_id": (
+            clean_cell(row.get(mapping.get("roster_source_id", "")))
+            if mapping.get("roster_source_id")
+            else ""
+        ),
+        "errors": errors,
+    }
+
+
+def build_identity_payload(
+    row: dict[str, Any], mapping: dict[str, str] | None = None
+) -> dict[str, Any]:
+    """Build a player identity payload from a source row and optional column mapping."""
+    mapping = mapping or {}
+    identity = {}
+    full_name_column = mapping.get("full_name", "")
+    full_name = clean_cell(row.get(full_name_column)) if full_name_column else ""
+    for target_field in PLAYER_FIELD_KEYS:
+        source_field = mapping.get(target_field, target_field)
+        identity[target_field] = parse_identity_value(
+            target_field, row.get(source_field)
+        )
+    if full_name and not (identity.get("first_name") and identity.get("last_name")):
+        first_name, last_name = split_full_name(full_name)
+        identity["first_name"] = identity.get("first_name") or first_name
+        identity["last_name"] = identity.get("last_name") or last_name
+    return identity_for_storage(identity)
+
+
+def build_source_identifiers(
+    row: dict[str, Any], mapping: dict[str, str] | None, source: str
+) -> list[dict[str, str]]:
+    """Build source identifiers from mapped CSV columns."""
+    mapping = mapping or {}
+    identifiers = []
+    for field_name, identifier_type in IDENTIFIER_FIELD_TYPES.items():
+        column = mapping.get(field_name, "")
+        value = clean_cell(row.get(column)) if column else ""
+        if value:
+            identifiers.append(
+                {
+                    "source": normalize_source(source),
+                    "identifier_type": identifier_type,
+                    "identifier_value": value,
+                }
+            )
+    return identifiers
+
+
+def unmapped_fields(row: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
+    mapped_headers = {header for header in mapping.values() if header}
+    return {
+        key: value
+        for key, value in row.items()
+        if key not in mapped_headers and value not in {"", None}
+    }
+
+
+def parsed_to_snapshot(parsed: ParsedCsvFile) -> dict[str, Any]:
+    return {
+        "file_name": parsed.file_name,
+        "headers": parsed.headers,
+        "normalized_headers": parsed.normalized_headers,
+        "rows": parsed.rows,
+    }
+
+
+def snapshot_to_parsed(snapshot: dict[str, Any]) -> ParsedCsvFile:
+    parsed = snapshot.get("parsed_csv", snapshot)
+    return ParsedCsvFile(
+        file_name=parsed.get("file_name", ""),
+        headers=parsed.get("headers", []),
+        normalized_headers=parsed.get("normalized_headers", {}),
+        rows=parsed.get("rows", []),
+    )
diff --git a/players/services/imports/matching.py b/players/services/imports/matching.py
new file mode 100644
index 0000000..6a4ef56
--- /dev/null
+++ b/players/services/imports/matching.py
@@ -0,0 +1,86 @@
+"""Player matching adapter used by the import preview."""
+
+from __future__ import annotations
+
+from dataclasses import asdict
+from typing import Any
+
+from players.models import Player
+from players.services.imports.constants import CONFLICT_FIELDS
+from players.services.imports.mapping import date_to_string, identity_for_model
+from players.services.imports.result_models import FieldConflict
+from players.services.matching_service import (
+    MATCH_AMBIGUOUS,
+    MATCH_EXACT,
+    PlayerMatchResult,
+    find_player_match,
+    match_by_identifier,
+)
+
+
+def match_identity(identity: dict[str, Any], source_identifiers: list[dict[str, str]]):
+    model_identity = identity_for_model(identity)
+    match_data = {
+        "first_name": model_identity.get("first_name", ""),
+        "last_name": model_identity.get("last_name", ""),
+        "birthdate": model_identity.get("birthdate"),
+        "birth_year": model_identity.get("birth_year"),
+        "division": identity.get("division", ""),
+    }
+    if source_identifiers:
+        exact_matches = []
+        exact_score = None
+        seen_player_ids = set()
+        for identifier in source_identifiers:
+            identifier_result = match_by_identifier(
+                identifier.get("source", ""),
+                identifier.get("identifier_type", ""),
+                identifier.get("identifier_value", ""),
+            )
+            if identifier_result.status == MATCH_EXACT and identifier_result.player:
+                if identifier_result.player.id not in seen_player_ids:
+                    exact_matches.append(identifier_result.player)
+                    exact_score = identifier_result.score
+                    seen_player_ids.add(identifier_result.player.id)
+        if len(exact_matches) == 1:
+            return PlayerMatchResult(
+                status=MATCH_EXACT,
+                player=exact_matches[0],
+                candidates=exact_matches,
+                reason="Matched by source identifier.",
+                score=exact_score,
+            )
+        if len(exact_matches) > 1:
+            return PlayerMatchResult(
+                status=MATCH_AMBIGUOUS,
+                candidates=exact_matches,
+                reason="Multiple source identifiers matched different players.",
+            )
+    return find_player_match(match_data)
+
+
+def field_conflicts(
+    player: Player | None, identity: dict[str, Any]
+) -> list[dict[str, str]]:
+    if not player:
+        return []
+    model_identity = identity_for_model(identity)
+    conflicts = []
+    for field_name in CONFLICT_FIELDS:
+        imported = model_identity.get(field_name)
+        existing = getattr(player, field_name, None)
+        if existing in {"", None} or imported in {"", None}:
+            continue
+        existing_value = date_to_string(existing)
+        imported_value = date_to_string(imported)
+        if existing_value != imported_value:
+            conflicts.append(
+                asdict(
+                    FieldConflict(
+                        field_name=field_name,
+                        existing_value=existing_value,
+                        imported_value=imported_value,
+                    )
+                )
+            )
+    return conflicts
diff --git a/players/services/imports/parsing.py b/players/services/imports/parsing.py
new file mode 100644
index 0000000..aaa33f9
--- /dev/null
+++ b/players/services/imports/parsing.py
@@ -0,0 +1,211 @@
+"""CSV and primitive parsing helpers for player imports."""
+
+from __future__ import annotations
+
+import csv
+import io
+from datetime import date, datetime
+
+from django.core.exceptions import ValidationError
+
+from players.services.imports.constants import (
+    HEADER_ALIASES,
+    MAX_CSV_ROWS,
+    MAX_CSV_UPLOAD_BYTES,
+    SOURCE_MANUAL_STAFF,
+    SOURCE_MEMBER_LIST,
+    SOURCE_ROSTER_DETAIL,
+)
+from players.services.imports.result_models import ParsedCsvFile
+from seasons.models import RosterStatus
+
+
+def clean_cell(value) -> str:
+    """Return a stripped string suitable for import processing."""
+    return "" if value is None else str(value).strip()
+
+
+def normalize_header(value) -> str:
+    """Normalize an import header for matching mapped columns."""
+    return " ".join(clean_cell(value).casefold().split())
+
+
+def normalize_source(value: str) -> str:
+    normalized = normalize_header(value).replace(" ", "_")
+    return normalized or SOURCE_MANUAL_STAFF
+
+
+def detect_source_from_filename(filename: str) -> str:
+    """Infer a stable source name from a CSV filename."""
+    lowered = normalize_header(filename)
+    if "roster" in lowered and "detail" in lowered:
+        return SOURCE_ROSTER_DETAIL
+    if "member" in lowered:
+        return SOURCE_MEMBER_LIST
+    return SOURCE_MANUAL_STAFF
+
+
+def parse_player_csv(file_obj) -> ParsedCsvFile:
+    """Parse a player CSV upload and preserve original row values."""
+    file_name = getattr(file_obj, "name", "players.csv")
+    if not file_name.lower().endswith(".csv"):
+        raise ValidationError("Upload a .csv file.")
+    file_size = getattr(file_obj, "size", None)
+    if file_size is not None and file_size > MAX_CSV_UPLOAD_BYTES:
+        raise ValidationError("CSV uploads are limited to 5 MB.")
+
+    raw_data = file_obj.read()
+    raw_size = (
+        len(raw_data.encode("utf-8")) if isinstance(raw_data, str) else len(raw_data)
+    )
+    if raw_size > MAX_CSV_UPLOAD_BYTES:
+        raise ValidationError("CSV uploads are limited to 5 MB.")
+    if isinstance(raw_data, bytes):
+        raw_data = raw_data.decode("utf-8-sig")
+    file_obj.seek(0)
+
+    reader = csv.DictReader(io.StringIO(raw_data))
+    if not reader.fieldnames:
+        raise ValidationError("The uploaded CSV does not contain a header row.")
+
+    headers = []
+    normalized_headers = {}
+    duplicate_headers = []
+    for header in reader.fieldnames:
+        stripped = clean_cell(header)
+        if not stripped:
+            duplicate_headers.append("<blank header>")
+            continue
+        normalized = normalize_header(stripped)
+        if normalized in normalized_headers:
+            duplicate_headers.append(stripped)
+        normalized_headers[normalized] = stripped
+        headers.append(stripped)
+
+    if duplicate_headers:
+        raise ValidationError(
+            "Duplicate or blank column headers were found: "
+            + ", ".join(sorted(set(duplicate_headers)))
+        )
+
+    rows = []
+    for row_number, row in enumerate(reader, start=2):
+        if len(rows) >= MAX_CSV_ROWS:
+            raise ValidationError(
+                f"CSV uploads are limited to {MAX_CSV_ROWS} data rows."
+            )
+        original_row = {}
+        cleaned_row = {}
+        for header in reader.fieldnames:
+            stripped = clean_cell(header)
+            original_value = row.get(header, "")
+            original_row[stripped] = original_value
+            cleaned_row[stripped] = clean_cell(original_value)
+        rows.append(
+            {
+                "row_number": row_number,
+                "original_row": original_row,
+                "cleaned_row": cleaned_row,
+            }
+        )
+
+    return ParsedCsvFile(
+        file_name=file_name,
+        headers=headers,
+        normalized_headers=normalized_headers,
+        rows=rows,
+        duplicate_headers=duplicate_headers,
+    )
+
+
+def serialize_preview(preview: dict) -> dict:
+    """Return a JSON-ready preview payload."""
+    return preview
+
+
+def deserialize_preview(payload: dict) -> dict:
+    """Return a preview payload from JSON data."""
+    return payload or {}
+
+
+def build_column_choices(parsed: ParsedCsvFile | dict) -> list[tuple[str, str]]:
+    """Build form choices for parsed CSV headers."""
+    headers = (
+        parsed.headers
+        if isinstance(parsed, ParsedCsvFile)
+        else parsed.get("headers", [])
+    )
+    return [(header, header) for header in headers]
+
+
+def suggest_mapping(headers: list[str], source: str = "") -> dict[str, str]:
+    """Suggest canonical player field mappings from CSV headers."""
+    mapping = {}
+    normalized_to_header = {normalize_header(header): header for header in headers}
+    for target, aliases in HEADER_ALIASES.items():
+        for alias in aliases:
+            if alias in normalized_to_header:
+                mapping[target] = normalized_to_header[alias]
+                break
+    return mapping
+
+
+def split_full_name(full_name: str) -> tuple[str, str]:
+    """Split a full name into first and last name for import matching."""
+    parts = [part for part in clean_cell(full_name).split() if part]
+    if not parts:
+        return "", ""
+    if len(parts) == 1:
+        return parts[0], ""
+    return parts[0], " ".join(parts[1:])
+
+
+def parse_birthdate(value: str):
+    """Parse common ISO-style birthdate values."""
+    cleaned = clean_cell(value)
+    if not cleaned:
+        return None
+    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
+        try:
+            return datetime.strptime(cleaned, fmt).date()
+        except ValueError:
+            continue
+    return None
+
+
+def parse_import_date(value: str):
+    """Parse optional roster date values from CSV input."""
+    return parse_birthdate(value)
+
+
+ROSTER_STATUS_ALIASES = {
+    "": RosterStatus.ACTIVE,
+    "active": RosterStatus.ACTIVE,
+    "inactive": RosterStatus.INACTIVE,
+    "transferred": RosterStatus.TRANSFERRED,
+    "transfer": RosterStatus.TRANSFERRED,
+    "guest": RosterStatus.GUEST,
+    "removed": RosterStatus.REMOVED,
+    "remove": RosterStatus.REMOVED,
+}
+
+
+def parse_roster_status(value: str) -> str:
+    cleaned = normalize_header(value)
+    if cleaned in ROSTER_STATUS_ALIASES:
+        return ROSTER_STATUS_ALIASES[cleaned]
+    raise ValidationError(f"Unknown roster status '{clean_cell(value)}'.")
+
+
+def parse_birth_year(value: str):
+    """Parse a birth year from a string."""
+    cleaned = clean_cell(value)
+    if not cleaned:
+        return None
+    try:
+        year = int(cleaned)
+    except ValueError:
+        return None
+    if 1900 <= year <= date.today().year:
+        return year
+    return None
diff --git a/players/services/imports/preview.py b/players/services/imports/preview.py
new file mode 100644
index 0000000..c23bd2b
--- /dev/null
+++ b/players/services/imports/preview.py
@@ -0,0 +1,241 @@
+"""Preview construction for player import batches."""
+
+from __future__ import annotations
+
+from dataclasses import asdict
+from typing import Any
+
+from django.db import transaction
+
+from players.models import PlayerImportBatch, PlayerImportStatus
+from players.services.imports.constants import (
+    ACTION_CREATE,
+    ACTION_ERROR,
+    ACTION_NEEDS_REVIEW,
+    ACTION_UPDATE,
+    MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
+)
+from players.services.imports.mapping import (
+    build_identity_payload,
+    build_roster_payload,
+    build_source_identifiers,
+    parsed_to_snapshot,
+    snapshot_to_parsed,
+    unmapped_fields,
+)
+from players.services.imports.matching import field_conflicts, match_identity
+from players.services.imports.parsing import suggest_mapping
+from players.services.imports.result_models import ImportPreviewRow
+from players.services.imports.roster import (
+    membership_preview as build_membership_preview,
+)
+from players.services.imports.roster import (
+    team_preview,
+)
+from players.services.matching_service import (
+    MATCH_AMBIGUOUS,
+    MATCH_EXACT,
+    MATCH_HIGH_CONFIDENCE,
+    MATCH_NO_MATCH,
+)
+
+
+def json_preview_row(row: ImportPreviewRow) -> dict[str, Any]:
+    return asdict(row)
+
+
+def preview_row(
+    *, row: dict[str, Any], mapping_config: dict[str, str], source: str, season=None
+) -> ImportPreviewRow:
+    """Build preview data for a single CSV row."""
+    cleaned_row = row["cleaned_row"]
+    identity = build_identity_payload(cleaned_row, mapping_config)
+    roster = build_roster_payload(cleaned_row, mapping_config)
+    source_identifiers = build_source_identifiers(cleaned_row, mapping_config, source)
+    errors = list(roster.get("errors", []))
+    if not (identity.get("first_name") and identity.get("last_name")):
+        errors.append(
+            "Map either a full name column or both first and last name columns."
+        )
+    if not season:
+        errors.append("Select an active season for this import.")
+    if not roster.get("team_name"):
+        errors.append("Team is required for season-aware player import.")
+    if not roster.get("division"):
+        errors.append("Division is required for season-aware player import.")
+    match_result = match_identity(identity, source_identifiers) if not errors else None
+    field_conflict_rows = (
+        field_conflicts(getattr(match_result, "player", None), identity)
+        if match_result
+        else []
+    )
+    season_team_preview = (
+        team_preview(roster, season)
+        if season and not (not roster.get("team_name") or not roster.get("division"))
+        else {
+            "action": "invalid_roster_context",
+            "label": "Invalid Roster Context",
+        }
+    )
+    matched_player = getattr(match_result, "player", None) if match_result else None
+    membership_preview_data = (
+        build_membership_preview(matched_player, season_team_preview, season, roster)
+        if season and not errors
+        else {
+            "action": "invalid_roster_context",
+            "label": "Invalid Roster Context",
+            "is_primary": False,
+        }
+    )
+    if membership_preview_data.get("action") == "review_team_change":
+        errors.append(
+            "Player already has an active primary membership in this season. "
+            "Resolve the team change manually or skip this row."
+        )
+
+    if errors:
+        action = ACTION_ERROR
+        match_status = MATCH_NO_MATCH
+    elif match_result.status == MATCH_EXACT:
+        action = ACTION_NEEDS_REVIEW if field_conflict_rows else ACTION_UPDATE
+        match_status = match_result.status
+    elif match_result.status == MATCH_HIGH_CONFIDENCE:
+        action = ACTION_NEEDS_REVIEW if field_conflict_rows else ACTION_UPDATE
+        match_status = match_result.status
+    elif match_result.status == MATCH_AMBIGUOUS:
+        action = ACTION_NEEDS_REVIEW
+        match_status = match_result.status
+    else:
+        action = ACTION_CREATE
+        match_status = MATCH_NO_MATCH
+
+    candidates = getattr(match_result, "candidates", []) if match_result else []
+    return ImportPreviewRow(
+        row_number=row["row_number"],
+        identity=identity,
+        original_row=row["original_row"],
+        unmapped_fields=unmapped_fields(cleaned_row, mapping_config),
+        source_identifiers=source_identifiers,
+        match_status=match_status,
+        matched_player_id=getattr(matched_player, "id", None),
+        matched_player_name=getattr(matched_player, "display_name", ""),
+        candidate_ids=[candidate.id for candidate in candidates],
+        candidate_names=[candidate.display_name for candidate in candidates],
+        candidate_options=[
+            {"id": candidate.id, "name": candidate.display_name}
+            for candidate in candidates
+        ],
+        field_conflicts=field_conflict_rows,
+        errors=errors,
+        action=action,
+        roster={key: value for key, value in roster.items() if key != "errors"},
+        season_team=season_team_preview,
+        membership=membership_preview_data,
+    )
+
+
+@transaction.atomic
+def build_import_preview(
+    *, import_batch: PlayerImportBatch, mapping_config: dict[str, str] | None = None
+) -> dict[str, Any]:
+    """Build and persist an import preview for a batch."""
+    parsed = snapshot_to_parsed(import_batch.preview_snapshot)
+    mapping_config = (
+        mapping_config
+        or import_batch.mapping_config
+        or suggest_mapping(parsed.headers, source=import_batch.source)
+    )
+    rows = [
+        json_preview_row(
+            preview_row(
+                row=row,
+                mapping_config=mapping_config,
+                source=import_batch.source,
+                season=import_batch.season,
+            )
+        )
+        for row in parsed.rows
+    ]
+    row_errors = [row for row in rows if row["errors"]]
+    conflicted_rows = [row for row in rows if row["action"] == ACTION_NEEDS_REVIEW]
+    preview = {
+        "file_name": parsed.file_name,
+        "source": import_batch.source,
+        "season": {
+            "id": import_batch.season_id,
+            "name": (
+                import_batch.season.name
+                if import_batch.season_id
+                else "Legacy / No Season"
+            ),
+        },
+        "headers": parsed.headers,
+        "mapping_config": mapping_config,
+        "account_provisioning": {
+            "enabled": bool(mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS)),
+            "activate_users": bool(
+                mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS)
+            ),
+            "email_column": mapping_config.get("account_email", ""),
+        },
+        "rows": rows,
+        "summary": {
+            "rows_processed": len(rows),
+            "rows_create": sum(1 for row in rows if row["action"] == ACTION_CREATE),
+            "rows_update": sum(1 for row in rows if row["action"] == ACTION_UPDATE),
+            "rows_needs_review": len(conflicted_rows),
+            "rows_error": len(row_errors),
+            "season_teams_create": sum(
+                1
+                for row in rows
+                if row.get("season_team", {}).get("action") == "create"
+            ),
+            "season_teams_reuse": sum(
+                1 for row in rows if row.get("season_team", {}).get("action") == "reuse"
+            ),
+            "memberships_create": sum(
+                1
+                for row in rows
+                if row.get("membership", {}).get("action")
+                in {"create", "new_season_membership"}
+            ),
+            "memberships_update": sum(
+                1 for row in rows if row.get("membership", {}).get("action") == "update"
+            ),
+        },
+    }
+    import_batch.mapping_config = mapping_config
+    import_batch.preview_snapshot = {
+        "parsed_csv": parsed_to_snapshot(parsed),
+        "preview": preview,
+    }
+    import_batch.row_errors = row_errors
+    import_batch.conflict_summary = {
+        "rows_conflicted": len(conflicted_rows),
+        "row_numbers": [row["row_number"] for row in conflicted_rows],
+    }
+    import_batch.rows_processed = len(rows)
+    import_batch.rows_conflicted = len(conflicted_rows)
+    import_batch.status = (
+        PlayerImportStatus.NEEDS_REVIEW
+        if conflicted_rows or row_errors
+        else PlayerImportStatus.PREVIEWED
+    )
+    import_batch.save(
+        update_fields=[
+            "mapping_config",
+            "preview_snapshot",
+            "row_errors",
+            "conflict_summary",
+            "rows_processed",
+            "rows_conflicted",
+            "status",
+            "updated_at",
+        ]
+    )
+    return preview
+
+
+def current_preview(import_batch: PlayerImportBatch) -> dict[str, Any]:
+    """Return the current persisted preview for a batch."""
+    return import_batch.preview_snapshot.get("preview", {})
diff --git a/players/services/imports/result_models.py b/players/services/imports/result_models.py
new file mode 100644
index 0000000..31e72a9
--- /dev/null
+++ b/players/services/imports/result_models.py
@@ -0,0 +1,77 @@
+"""Data contracts for player import parsing, preview, and commit results."""
+
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+from typing import Any
+
+from players.services.imports.constants import ACTION_CREATE, RESOLUTION_KEEP_EXISTING
+
+
+@dataclass
+class ImportIdentityRow:
+    row_number: int | None
+    identity: dict[str, Any]
+    original_row: dict[str, Any] = field(default_factory=dict)
+    unmapped_fields: dict[str, Any] = field(default_factory=dict)
+
+
+@dataclass
+class ImportRowResult:
+    row_number: int | None
+    imported: bool
+    errors: list[str] = field(default_factory=list)
+    identity: dict[str, Any] = field(default_factory=dict)
+
+
+@dataclass
+class ParsedCsvFile:
+    file_name: str
+    headers: list[str]
+    normalized_headers: dict[str, str]
+    rows: list[dict[str, Any]]
+    duplicate_headers: list[str] = field(default_factory=list)
+
+
+@dataclass
+class FieldConflict:
+    field_name: str
+    existing_value: str
+    imported_value: str
+    resolution: str = RESOLUTION_KEEP_EXISTING
+
+
+@dataclass
+class ImportPreviewRow:
+    row_number: int
+    identity: dict[str, Any]
+    original_row: dict[str, Any]
+    unmapped_fields: dict[str, Any]
+    source_identifiers: list[dict[str, str]]
+    match_status: str
+    matched_player_id: int | None = None
+    matched_player_name: str = ""
+    candidate_ids: list[int] = field(default_factory=list)
+    candidate_names: list[str] = field(default_factory=list)
+    candidate_options: list[dict[str, Any]] = field(default_factory=list)
+    field_conflicts: list[dict[str, str]] = field(default_factory=list)
+    errors: list[str] = field(default_factory=list)
+    action: str = ACTION_CREATE
+    roster: dict[str, Any] = field(default_factory=dict)
+    season_team: dict[str, Any] = field(default_factory=dict)
+    membership: dict[str, Any] = field(default_factory=dict)
+
+
+@dataclass
+class ImportCommitResult:
+    rows_processed: int = 0
+    created: int = 0
+    updated: int = 0
+    skipped: int = 0
+    conflicts: int = 0
+    season_teams_created: int = 0
+    season_teams_reused: int = 0
+    memberships_created: int = 0
+    memberships_updated: int = 0
+    errors: list[str] = field(default_factory=list)
+    account_provisioning: dict[str, Any] = field(default_factory=dict)
diff --git a/players/services/imports/roster.py b/players/services/imports/roster.py
new file mode 100644
index 0000000..4a86545
--- /dev/null
+++ b/players/services/imports/roster.py
@@ -0,0 +1,195 @@
+"""Seasonal roster integration for player imports."""
+
+from __future__ import annotations
+
+from datetime import datetime
+from typing import Any
+
+from django.core.exceptions import ValidationError
+
+from players.models import Player, PlayerImportBatch
+from players.services.imports.parsing import clean_cell
+from seasons.models import PlayerRosterMembership, RosterStatus, SeasonTeam
+from seasons.services.membership_service import (
+    create_membership,
+    sync_player_current_team_fields,
+    update_membership,
+)
+from seasons.services.team_service import (
+    get_or_create_season_team,
+    normalize_division_value,
+    normalize_team_value,
+)
+
+
+def team_preview(roster: dict[str, Any], season) -> dict[str, Any]:
+    team_name = roster.get("team_name", "")
+    division = roster.get("division", "")
+    if not team_name or not division:
+        return {"action": "invalid_roster_context", "label": "Invalid Roster Context"}
+    normalized_name = normalize_team_value(team_name)
+    normalized_division = normalize_division_value(division)
+    existing = SeasonTeam.objects.filter(
+        season=season,
+        normalized_name=normalized_name,
+        normalized_division=normalized_division,
+    ).first()
+    return {
+        "id": existing.id if existing else None,
+        "name": existing.name if existing else team_name,
+        "division": existing.division if existing else division,
+        "action": "reuse" if existing else "create",
+        "label": "Reuse Season Team" if existing else "Create Season Team",
+    }
+
+
+def membership_preview(
+    player: Player | None,
+    season_team_preview: dict[str, Any],
+    season,
+    roster: dict[str, Any],
+) -> dict[str, Any]:
+    if not player:
+        return {
+            "action": "create",
+            "label": "Create Membership",
+            "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE,
+        }
+    existing_same_team = None
+    if season_team_preview.get("id"):
+        existing_same_team = PlayerRosterMembership.objects.filter(
+            player=player,
+            season_team_id=season_team_preview["id"],
+        ).first()
+    if existing_same_team:
+        return {
+            "id": existing_same_team.id,
+            "action": "update",
+            "label": "Update Membership",
+            "is_primary": existing_same_team.is_primary,
+        }
+    primary = (
+        PlayerRosterMembership.objects.select_related("season_team")
+        .filter(
+            player=player,
+            season_team__season=season,
+            is_active=True,
+            is_primary=True,
+        )
+        .first()
+    )
+    if primary:
+        return {
+            "id": None,
+            "action": "review_team_change",
+            "label": "Review Team Change",
+            "is_primary": False,
+            "existing_primary": str(primary.season_team),
+        }
+    return {
+        "id": None,
+        "action": "new_season_membership",
+        "label": "New Season Membership",
+        "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE,
+    }
+
+
+def parse_iso_date(value: str):
+    cleaned = clean_cell(value)
+    if not cleaned:
+        return None
+    try:
+        return datetime.strptime(cleaned, "%Y-%m-%d").date()
+    except ValueError:
+        raise ValidationError("Roster date is invalid.") from None
+
+
+def membership_update_values(roster: dict[str, Any]) -> dict[str, Any]:
+    values = {}
+    if roster.get("roster_status"):
+        values["status"] = roster["roster_status"]
+        values["is_active"] = roster["roster_status"] in {
+            RosterStatus.ACTIVE,
+            RosterStatus.GUEST,
+        }
+        if not values["is_active"]:
+            values["is_primary"] = False
+    if roster.get("jersey_number"):
+        values["jersey_number"] = roster["jersey_number"]
+    if roster.get("starts_on"):
+        values["starts_on"] = parse_iso_date(roster["starts_on"])
+    if roster.get("ends_on"):
+        values["ends_on"] = parse_iso_date(roster["ends_on"])
+    if roster.get("roster_source_id"):
+        values["source_identifier"] = roster["roster_source_id"]
+    return values
+
+
+def commit_membership(
+    player: Player, import_batch: PlayerImportBatch, preview_row_data: dict[str, Any]
+) -> tuple[str, bool]:
+    if not import_batch.season_id:
+        raise ValidationError(
+            "Import batch requires a season before memberships can be committed."
+        )
+    roster = preview_row_data.get("roster", {})
+    team_name = roster.get("team_name", "")
+    division = roster.get("division", "")
+    if not team_name or not division:
+        raise ValidationError("Team and division are required for roster membership.")
+    season_team, team_created = get_or_create_season_team(
+        season=import_batch.season,
+        name=team_name,
+        division=division,
+        external_source=import_batch.source if roster.get("roster_source_id") else "",
+        external_identifier=roster.get("roster_source_id", ""),
+        metadata={"import_batch_id": import_batch.id},
+    )
+    existing = (
+        PlayerRosterMembership.objects.select_for_update()
+        .filter(player=player, season_team=season_team)
+        .first()
+    )
+    values = membership_update_values(roster)
+    values.setdefault("source", import_batch.source)
+    if existing:
+        was_primary = existing.is_primary
+        update_membership(existing, sync_player_fields=was_primary, **values)
+        return "updated", team_created
+
+    primary = (
+        PlayerRosterMembership.objects.select_for_update()
+        .filter(
+            player=player,
+            season_team__season=import_batch.season,
+            is_active=True,
+            is_primary=True,
+        )
+        .first()
+    )
+    if primary:
+        raise ValidationError(
+            "Player already has an active primary membership in this season."
+        )
+    status = values.pop("status", roster.get("roster_status") or RosterStatus.ACTIVE)
+    is_active = values.pop(
+        "is_active", status in {RosterStatus.ACTIVE, RosterStatus.GUEST}
+    )
+    membership = create_membership(
+        player=player,
+        season_team=season_team,
+        status=status,
+        is_primary=is_active,
+        is_active=is_active,
+        source=values.pop("source", import_batch.source),
+        source_identifier=values.pop(
+            "source_identifier", roster.get("roster_source_id", "")
+        ),
+        import_batch=import_batch,
+        metadata={"row_number": preview_row_data["row_number"]},
+        sync_player_fields=is_active,
+        **values,
+    )
+    if membership.is_primary:
+        sync_player_current_team_fields(player, import_batch.season)
+    return "created", team_created
```

## Terminal State

PASS
