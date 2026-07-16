# Prompt 88 - Platform

## User Prompt

```text
Perform Repository Cleanup Phase 6 only: Split Large Test Modules.

Use continuous loop engineering.

Continue until the largest Django test modules are reorganized into focused test packages, test behavior remains unchanged, focused and full verification pass, commits are pushed, and the working tree is clean.

Do not change application behavior.

Do not refactor production services, views, models, forms, templates, URLs, permissions, or migrations.

Do not begin the account-operations service refactor, final architecture audit, or Platform V2 work.

==================================================
Current State
=============

Repository Cleanup Phases 1 through 5 are complete.

Current repository state includes:

* reconciled documentation;
* Django 4.2.30;
* Ruff, Black, isort, and pre-commit;
* touched-files-only formatting policy;
* refactored player import service;
* refactored coach import service;
* refactored Season Operations views and query layer;
* stable public façades and route imports.

Seasonal Participation V1 remains Feature Complete, Production Ready, and Frozen.

The main remaining structural maintenance issue is several oversized test modules.

Current large files include approximately:

```text
accounts/tests.py
analytics/tests.py
seasons/tests.py
players/tests.py
```

The largest are `accounts/tests.py` and `analytics/tests.py`.

This phase is strictly a test-organization refactor.

==================================================
Objective
=========

Convert oversized app-level test modules into focused Django test packages.

Improve:

* discoverability;
* ownership;
* navigation;
* merge-conflict risk;
* targeted test execution;
* future maintenance.

Preserve:

* all existing test cases;
* all assertions;
* all fixtures;
* all behavior coverage;
* Django test discovery;
* test database behavior;
* test counts;
* application code.

Do not rewrite tests merely to make them stylistically different.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete test reorganization, regression-proofing, tooling, or verification work remains.

PASS

All Phase 6 acceptance criteria are satisfied, focused and full verification pass, commits are pushed, and the working tree is clean.

BLOCKED

The test modules cannot be safely split without unresolved test-discovery or fixture-order problems.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied criterion.

Moving tests into arbitrary files without clearer ownership does not count as progress.

==================================================
Established Loop Workflow
=========================

Every loop must:

1. reconcile the committed repository state;
2. read `AGENTS.md`;
3. confirm the working tree is clean;
4. inspect the target test module and related production subsystem;
5. inventory test classes, shared fixtures, helpers, and import dependencies;
6. choose one cohesive app or test area;
7. create the next prompt archive before implementation;
8. split tests only;
9. preserve existing assertions and behavior;
10. run tooling on touched files only;
11. run focused verification;
12. perform senior-engineer self-review;
13. fix every verified issue;
14. run the full verification suite;
15. commit the test refactor;
16. finalize and separately commit the prompt archive;
17. push both commits;
18. re-read the committed diff;
19. confirm the working tree is clean;
20. reassess all acceptance criteria;
21. choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS;
22. if CONTINUE, immediately begin the next loop.

Each loop must create:

1. one test-refactor commit;
2. one prompt archive commit.

==================================================
Required Repository Review
==========================

Read:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* relevant prompt archives for repository cleanup Phases 3 through 5.

Inspect:

* `accounts/tests.py`
* `analytics/tests.py`
* `seasons/tests.py`
* `players/tests.py`
* any existing app test packages;
* shared test utilities;
* model factories or fixture helpers if present;
* test imports from production modules;
* any direct imports of test classes or test helpers;
* CI/test commands;
* Django test discovery conventions.

Also inspect the production areas only enough to classify tests correctly.

Do not refactor production code.

==================================================
Recommended Order
=================

Prefer this order:

1. `accounts/tests.py`
2. `analytics/tests.py`
3. `seasons/tests.py`
4. `players/tests.py`

The first loop may split only `accounts`.

Continue into later loops for the remaining apps if needed.

Do not force every app into one enormous commit.

==================================================
Target Structure
================

Use Django test packages such as:

```text
accounts/tests/
    __init__.py
    helpers.py
    test_authentication.py
    test_profiles.py
    test_permissions.py
    test_account_operations.py
    test_player_links.py
    test_coach_import.py
```

```text
analytics/tests/
    __init__.py
    helpers.py
    test_models.py
    test_observations.py
    test_evaluation_context.py
    test_player_evaluations.py
    test_coach_review.py
    test_staff_review.py
    test_permissions.py
```

```text
seasons/tests/
    __init__.py
    helpers.py
    test_models.py
    test_services.py
    test_operations_views.py
    test_permissions.py
    test_import_integration.py
    test_evaluation_integration.py
```

```text
players/tests/
    __init__.py
    helpers.py
    test_models.py
    test_matching.py
    test_import.py
    test_views.py
    test_account_provisioning.py
```

These are suggested structures only.

Use actual test-class responsibilities to choose file boundaries.

Avoid excessive fragmentation.

A file should normally contain a cohesive group of related test classes.

==================================================
Test Discovery
==============

Django must continue discovering all tests through:

```bash
python manage.py test
```

Requirements:

* replace `tests.py` with a `tests/` package cleanly;
* include `tests/__init__.py`;
* do not leave both `tests.py` and `tests/` in the same app;
* preserve app labels and import behavior;
* verify targeted commands such as:

  * `python manage.py test accounts`
  * `python manage.py test analytics`
  * `python manage.py test seasons`
  * `python manage.py test players`.

Do not rename test methods unless necessary.

Do not rename test classes unless necessary.

==================================================
Shared Fixtures And Helpers
===========================

Identify repeated setup code within each test module.

A small `helpers.py` may contain:

* test-only factories;
* fixture builders;
* reusable CSV builders;
* reusable login helpers;
* shared assertion helpers.

Do not create a broad cross-project testing framework.

Keep helpers inside the app unless genuinely shared across multiple apps.

Do not move production behavior into test helpers.

Do not hide important test setup behind overly abstract factories.

Prefer explicit tests over clever test infrastructure.

==================================================
Import Safety
=============

Review for:

* circular imports between test files;
* shared base classes;
* test-only constants;
* module-level database access;
* import-time side effects;
* patched module paths;
* mocks whose target depends on the original module path.

When moving tests:

* preserve patch targets that refer to production symbols;
* update only test-module-local imports;
* do not change production import paths;
* do not move tests in a way that changes mock behavior.

==================================================
Behavioral Freeze
=================

Do not intentionally change:

* assertions;
* expected messages;
* response codes;
* route expectations;
* database-state expectations;
* password tests;
* permission tests;
* migration tests;
* query-count expectations;
* import behavior tests;
* seasonal snapshot tests;
* transaction tests.

If an existing test is objectively broken or flaky:

* document the verified problem;
* fix it narrowly;
* do not weaken the assertion;
* add explanation in the prompt archive.

Do not delete tests merely because they appear redundant unless duplication is proven and coverage remains explicit.

Default rule:

> Move first, simplify later.

==================================================
Accounts Test Package
=====================

Likely groups:

## Authentication

* login;
* logout;
* password change;
* forced password change;
* redirects;
* inactive users.

## Profiles And Roles

* account profiles;
* role changes;
* staff/admin behavior;
* privilege separation.

## Player Links

* user-player links;
* primary self links;
* relationship validation;
* link services.

## Account Operations

* create/edit;
* activate/deactivate;
* password reset;
* bulk operations;
* safety rules.

## Coach Import

* CSV parsing;
* account matching;
* password preservation;
* season selection;
* assignment behavior;
* result reporting.

Keep existing tests unchanged where practical.

==================================================
Analytics Test Package
======================

Likely groups:

## Models And Question Sets

* evaluation cycles;
* question sets;
* observation types;
* defaults and seeds.

## Observation Workflow

* draft;
* submit;
* responses;
* validation;
* duplicate protection.

## Evaluation Context

* season;
* roster membership;
* coach assignment;
* snapshots;
* immutability.

## Player Experience

* self evaluation;
* peer evaluation;
* My Evaluations;
* permissions.

## Coach Review

* coach evaluation;
* review filters;
* historical display.

## Staff Review

* staff tables;
* review pages;
* legacy/no-season behavior.

==================================================
Seasons Test Package
====================

Likely groups:

* models and constraints;
* season services;
* team services;
* membership services;
* coach assignment services;
* operations UI;
* permissions;
* player import integration;
* coach import integration;
* evaluation snapshot regression.

==================================================
Players Test Package
====================

Likely groups:

* player models;
* source identifiers;
* matching;
* import parsing and preview;
* import commit;
* roster integration;
* account provisioning;
* player views.

==================================================
Test Count Preservation
=======================

Before moving tests, record:

* total project test count;
* target app test count;
* test class count where practical.

After moving tests:

* targeted app test count must remain equivalent;
* full project count must remain equivalent unless a verified duplicate or missing test is explicitly addressed;
* any count difference must be explained.

Current full suite baseline:

```text
458 tests
```

Do not declare PASS if tests silently disappear.

==================================================
Code Quality
============

Apply tooling only to touched test files.

Run:

```bash
ruff check <touched-python-files>
black --check <touched-python-files>
isort --check-only <touched-python-files>
```

If formatting fails:

* format only touched files;
* do not format production files;
* do not modify migrations;
* avoid unrelated whitespace churn.

Remove only:

* unused imports;
* duplicate local helper definitions after safe extraction;
* dead test-only helpers with no callers.

Do not perform broad test-style modernization.

==================================================
Documentation
=============

Documentation changes should normally be unnecessary.

Update `docs/ARCHITECTURE.md` only if it explicitly documents test layout and becomes stale.

Do not update the user manual.

Do not present this as a product feature.

==================================================
Scope Restrictions
==================

Do not:

* modify production Python code;
* modify models;
* create migrations;
* change forms;
* change views;
* change services;
* change templates;
* change URLs;
* change permissions;
* change requirements;
* change tooling configuration unless a verified test-discovery issue requires it;
* refactor account operations;
* refactor import services again;
* refactor Season Operations again;
* add product features;
* bulk-format the repository;
* regenerate the flat-file snapshot.

==================================================
Focused Verification Per Loop
=============================

For the app being split, run:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py test <app>
```

Also run directly targeted modules where useful, for example:

```bash
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_coach_import
```

Run related regression apps:

```bash
DJANGO_SECRET_KEY=test python manage.py test accounts players seasons analytics
```

Run pre-commit on all touched files:

```bash
pre-commit run --files <all-touched-files>
```

Run:

```bash
git diff --check
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

* silently missing tests;
* changed test discovery;
* changed patch targets;
* fixture-order dependence;
* shared state leakage;
* duplicate test execution;
* tests no longer isolated;
* accidental assertion changes;
* weakened expectations;
* excessive helper abstraction;
* circular test imports;
* module-level database access;
* test count drift;
* unrelated formatting churn;
* production file changes.

Fix every verified issue before committing.

==================================================
Acceptance Criteria
===================

Do not declare PASS until all criteria are satisfied.

A. Structure

* large test modules are split into cohesive packages;
* file ownership is easy to understand;
* helpers remain small and app-local;
* no excessive fragmentation.

B. Discovery

* Django discovers all tests;
* app-level test commands work;
* module-level targeted commands work;
* no test runs twice;
* no test disappears.

C. Behavior

* assertions remain equivalent;
* application behavior is unchanged;
* mocks and patch targets still work;
* fixtures remain isolated.

D. Test Count

* baseline app counts are preserved;
* full suite remains at 458 tests unless a verified count change is documented;
* unexplained count drift is not allowed.

E. Quality

* no circular imports;
* no dead test helpers;
* touched files pass Ruff, Black, and isort;
* no production files changed;
* no unrelated formatting churn.

F. Migration

* no model changes;
* no migrations;
* migration checks pass.

G. Verification

* targeted app suites pass;
* cross-app regression suites pass;
* full suite passes.

H. Git

* test-refactor commit exists;
* prompt archive commit exists;
* both pushed;
* working tree is clean.

==================================================
Recommended Loop Plan
=====================

Loop 1:

* split `accounts/tests.py`;
* preserve test count;
* run focused and full verification;
* commit, archive, push, reassess.

Loop 2:

* split `analytics/tests.py`;
* preserve test count;
* run focused and full verification;
* commit, archive, push, reassess.

Loop 3:

* split `seasons/tests.py` and `players/tests.py` if still justified;
* preserve test count;
* run focused and full verification;
* commit, archive, push, reassess.

Do not force all loops if smaller modules are still acceptably maintainable after review.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* materially improves test ownership;
* reduces navigation or merge-conflict risk;
* preserves or strengthens regression coverage;
* fixes a verified discovery or fixture issue;
* removes genuine test duplication without losing coverage.

Moving tests into poorly named files does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* developer locating a failing test;
* developer adding account tests;
* developer adding Analytics tests;
* reviewer understanding test ownership;
* CI operator running targeted suites;
* maintainer resolving merge conflicts.

Confirm:

* test organization is clearer;
* all 458 tests still run;
* production code is untouched;
* targeted test commands are easier to use;
* no test coverage silently disappeared.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before moving tests;
2. commit test-file reorganization;
3. update the prompt archive with:

   * implementation commit hash;
   * old and new test structure;
   * test counts before and after;
   * shared helper changes;
   * discovery findings;
   * patch-target findings;
   * tooling results;
   * focused verification;
   * full verification;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested commit messages:

```text
Split account tests by responsibility
```

```text
Split analytics tests by responsibility
```

```text
Split seasonal and player tests by responsibility
```

==================================================
Final Report
============

Report:

* terminal state;
* loops completed;
* objective of each loop;
* files created;
* files removed;
* old and new test structures;
* test counts before and after;
* helper modules created;
* discovery behavior;
* targeted test commands;
* patch-target changes;
* tooling checks;
* focused verification;
* full verification;
* production files changed, which should be none;
* migrations created, which should be none;
* deferred cleanup work;
* commits;
* push results;
* confirmation that application behavior was unchanged;
* confirmation that the working tree is clean.
```

## Implementation Commit

`b8623a1` - Split seasonal and player tests by responsibility

## Old Test Structure

```text
seasons/tests.py
players/tests.py
```

## New Test Structure

```text
seasons/tests/
    __init__.py
    helpers.py
    test_admin.py
    test_assignments.py
    test_memberships.py
    test_models.py
    test_operations_views.py

players/tests/
    __init__.py
    helpers.py
    test_import_workflow.py
    test_models.py
    test_services.py
```

## Test Counts

Before split:

```text
DJANGO_SECRET_KEY=test python manage.py test seasons
Found 44 test(s).
Ran 44 tests successfully.

DJANGO_SECRET_KEY=test python manage.py test players
Found 47 test(s).
Ran 47 tests successfully.
```

After split:

```text
DJANGO_SECRET_KEY=test python manage.py test seasons
Found 44 test(s).
Ran 44 tests successfully.

DJANGO_SECRET_KEY=test python manage.py test players
Found 47 test(s).
Ran 47 tests successfully.
```

Full suite remained at 458 tests.

## Shared Helper Changes

The original shared imports and `User = get_user_model()` setup moved into app-local helper modules:

```text
seasons/tests/helpers.py
players/tests/helpers.py
```

Test files import only the helper names they use so Ruff `F` checks stay clean.

## Discovery Findings

Django discovers both test packages through app-level commands. Targeted module commands also work, including:

```text
DJANGO_SECRET_KEY=test python manage.py test seasons.tests.test_operations_views
DJANGO_SECRET_KEY=test python manage.py test players.tests.test_import_workflow
```

## Patch-Target Findings

No patch targets required changes. No production import paths were changed.

## Verification

Focused verification:

```text
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py test seasons.tests.test_operations_views
DJANGO_SECRET_KEY=test python manage.py test players.tests.test_import_workflow
DJANGO_SECRET_KEY=test python manage.py test seasons
DJANGO_SECRET_KEY=test python manage.py test players
DJANGO_SECRET_KEY=test python manage.py test accounts players seasons analytics
pre-commit run --files seasons/tests/__init__.py seasons/tests/helpers.py seasons/tests/test_models.py seasons/tests/test_memberships.py seasons/tests/test_assignments.py seasons/tests/test_admin.py seasons/tests/test_operations_views.py players/tests/__init__.py players/tests/helpers.py players/tests/test_models.py players/tests/test_services.py players/tests/test_import_workflow.py docs/prompts/prompt_88_platform.md
```

Full verification:

```text
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
DJANGO_SECRET_KEY=test python manage.py migrate --plan
DJANGO_SECRET_KEY=test python manage.py test
git diff --check
```

Result: all checks passed. Full suite ran 458 tests successfully.

## Terminal State

PASS. The large app-level test modules were split into focused packages while preserving discovery and test counts.

## Commit Diff

```diff
commit b8623a19e753fe3f8c387a528f78dd541618c909
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 12:22:29 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 12:22:29 2026 -0700

    Split seasonal and player tests by responsibility
---
 players/tests/__init__.py                          |   0
 players/tests/helpers.py                           | 114 +++
 .../{tests.py => tests/test_import_workflow.py}    | 487 ++++++-------
 players/tests/test_models.py                       | 100 +++
 players/tests/test_services.py                     | 138 ++++
 seasons/tests.py                                   | 774 ---------------------
 seasons/tests/__init__.py                          |   0
 seasons/tests/helpers.py                           | 112 +++
 seasons/tests/test_admin.py                        |  31 +
 seasons/tests/test_assignments.py                  | 175 +++++
 seasons/tests/test_memberships.py                  | 174 +++++
 seasons/tests/test_models.py                       | 166 +++++
 seasons/tests/test_operations_views.py             | 493 +++++++++++++
 13 files changed, 1728 insertions(+), 1036 deletions(-)

diff --git a/players/tests/__init__.py b/players/tests/__init__.py
new file mode 100644
index 0000000..e69de29
diff --git a/players/tests/helpers.py b/players/tests/helpers.py
new file mode 100644
index 0000000..7acf1bd
--- /dev/null
+++ b/players/tests/helpers.py
@@ -0,0 +1,114 @@
+from datetime import date
+
+from django.apps import apps
+from django.contrib import admin
+from django.contrib.auth import get_user_model
+from django.core.exceptions import PermissionDenied, ValidationError
+from django.core.files.uploadedfile import SimpleUploadedFile
+from django.db import IntegrityError, transaction
+from django.test import TestCase
+
+from accounts.models import AccountProfile, UserPlayerLink
+from players.models import (
+    Player,
+    PlayerAlias,
+    PlayerImportBatch,
+    PlayerImportStatus,
+    PlayerSourceIdentifier,
+    PlayerSourceRow,
+    PlayerTag,
+)
+from players.services import import_service
+from players.services.identity_service import add_source_identifier, create_player
+from players.services.import_service import (
+    ACTION_CREATE,
+    ACTION_ERROR,
+    ACTION_NEEDS_REVIEW,
+    ACTION_SKIP,
+    ACTION_UPDATE,
+    MAX_CSV_ROWS,
+    MAX_CSV_UPLOAD_BYTES,
+    RESOLUTION_ACTION_CREATE_NEW,
+    RESOLUTION_ACTION_USE_CANDIDATE,
+    SOURCE_MEMBER_LIST,
+    SOURCE_ROSTER_DETAIL,
+    build_import_preview,
+    commit_import_batch,
+    create_import_batch,
+    parse_player_csv,
+    suggest_mapping,
+)
+from players.services.matching_service import (
+    MATCH_AMBIGUOUS,
+    MATCH_EXACT,
+    MATCH_HIGH_CONFIDENCE,
+    MATCH_NO_MATCH,
+    find_player_match,
+    match_by_identifier,
+    match_by_name_and_birthdate,
+)
+from players.services.tag_service import (
+    active_tags,
+    assign_tag,
+    players_with_tag,
+    remove_tag,
+)
+from seasons.models import PlayerRosterMembership, SeasonTeam
+from seasons.services.season_service import create_season
+
+User = get_user_model()
+
+__all__ = (
+    "ACTION_CREATE",
+    "ACTION_ERROR",
+    "ACTION_NEEDS_REVIEW",
+    "ACTION_SKIP",
+    "ACTION_UPDATE",
+    "AccountProfile",
+    "IntegrityError",
+    "MATCH_AMBIGUOUS",
+    "MATCH_EXACT",
+    "MATCH_HIGH_CONFIDENCE",
+    "MATCH_NO_MATCH",
+    "MAX_CSV_ROWS",
+    "MAX_CSV_UPLOAD_BYTES",
+    "PermissionDenied",
+    "Player",
+    "PlayerAlias",
+    "PlayerImportBatch",
+    "PlayerImportStatus",
+    "PlayerRosterMembership",
+    "PlayerSourceIdentifier",
+    "PlayerSourceRow",
+    "PlayerTag",
+    "RESOLUTION_ACTION_CREATE_NEW",
+    "RESOLUTION_ACTION_USE_CANDIDATE",
+    "SOURCE_MEMBER_LIST",
+    "SOURCE_ROSTER_DETAIL",
+    "SeasonTeam",
+    "SimpleUploadedFile",
+    "TestCase",
+    "User",
+    "UserPlayerLink",
+    "ValidationError",
+    "active_tags",
+    "add_source_identifier",
+    "admin",
+    "apps",
+    "assign_tag",
+    "build_import_preview",
+    "commit_import_batch",
+    "create_import_batch",
+    "create_player",
+    "create_season",
+    "date",
+    "find_player_match",
+    "import_service",
+    "match_by_identifier",
+    "match_by_name_and_birthdate",
+    "parse_player_csv",
+    "players_with_tag",
+    "remove_tag",
+    "suggest_mapping",
+    "transaction",
+)
diff --git a/players/tests.py b/players/tests/test_import_workflow.py
similarity index 53%
rename from players/tests.py
rename to players/tests/test_import_workflow.py
index 89bc2b9..89513dc 100644
--- a/players/tests.py
+++ b/players/tests/test_import_workflow.py
@@ -1,242 +1,60 @@
-from datetime import date
-
-from django.apps import apps
-from django.contrib.auth import get_user_model
-from django.core.exceptions import PermissionDenied, ValidationError
-from django.core.files.uploadedfile import SimpleUploadedFile
-from django.contrib import admin
-from django.db import IntegrityError, transaction
-from django.test import TestCase
-
-from accounts.models import AccountProfile, UserPlayerLink
-from players.models import Player, PlayerAlias, PlayerImportBatch, PlayerImportStatus, PlayerSourceIdentifier, PlayerSourceRow, PlayerTag
-from players.services import import_service
-from players.services.identity_service import add_source_identifier, create_player
-from players.services.import_service import (
+from players.tests.helpers import (
     ACTION_CREATE,
     ACTION_ERROR,
     ACTION_NEEDS_REVIEW,
     ACTION_SKIP,
     ACTION_UPDATE,
+    MATCH_AMBIGUOUS,
     MAX_CSV_ROWS,
     MAX_CSV_UPLOAD_BYTES,
     RESOLUTION_ACTION_CREATE_NEW,
     RESOLUTION_ACTION_USE_CANDIDATE,
     SOURCE_MEMBER_LIST,
     SOURCE_ROSTER_DETAIL,
+    AccountProfile,
+    PermissionDenied,
+    Player,
+    PlayerImportStatus,
+    PlayerRosterMembership,
+    PlayerSourceRow,
+    SimpleUploadedFile,
+    TestCase,
+    User,
+    UserPlayerLink,
+    ValidationError,
+    add_source_identifier,
     build_import_preview,
     commit_import_batch,
     create_import_batch,
+    create_season,
     parse_player_csv,
     suggest_mapping,
 )
-from players.services.matching_service import (
-    MATCH_AMBIGUOUS,
-    MATCH_EXACT,
-    MATCH_HIGH_CONFIDENCE,
-    MATCH_NO_MATCH,
-    find_player_match,
-    match_by_identifier,
-    match_by_name_and_birthdate,
-)
-from players.services.tag_service import active_tags, assign_tag, players_with_tag, remove_tag
-from seasons.models import PlayerRosterMembership, SeasonTeam
-from seasons.services.season_service import create_season
-
-
-User = get_user_model()
-
-
-class PlayerModelTests(TestCase):
-    def test_player_full_name_and_display_name(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin", preferred_name="Gene")
-
-        self.assertEqual(player.full_name, "Eugene Lin")
-        self.assertEqual(player.display_name, "Gene Lin")
-        self.assertEqual(str(player), "Gene Lin")
-
-    def test_player_model_has_no_pdp_dependency(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-        related_models = [
-            field.remote_field.model
-            for field in Player._meta.fields
-            if getattr(field, "remote_field", None) and field.remote_field
-        ]
-
-        self.assertEqual(related_models, [])
-        self.assertEqual(player.full_name, "Eugene Lin")
-
-    def test_alias_saves_normalized_value(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-        alias = PlayerAlias.objects.create(player=player, alias="  Gene   LIN  ", source="manual")
-
-        self.assertEqual(alias.normalized_alias, "gene lin")
-
-    def test_duplicate_alias_for_same_player_is_rejected(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-        PlayerAlias.objects.create(player=player, alias="Gene Lin")
-
-        with self.assertRaises(IntegrityError):
-            with transaction.atomic():
-                PlayerAlias.objects.create(player=player, alias=" gene   lin ")
-
-    def test_same_alias_can_exist_for_different_players(self):
-        player_one = Player.objects.create(first_name="Eugene", last_name="Lin")
-        player_two = Player.objects.create(first_name="Gene", last_name="Lynn")
-
-        PlayerAlias.objects.create(player=player_one, alias="Gene")
-        PlayerAlias.objects.create(player=player_two, alias="Gene")
-
-        self.assertEqual(PlayerAlias.objects.filter(normalized_alias="gene").count(), 2)
-
-    def test_source_identifier_uniqueness_uses_source_type_and_value(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-        PlayerSourceIdentifier.objects.create(
-            player=player,
-            source="Registration",
-            identifier_type="Registrant ID",
-            identifier_value=" ABC-123 ",
-        )
-
-        with self.assertRaises(IntegrityError):
-            with transaction.atomic():
-                PlayerSourceIdentifier.objects.create(
-                    player=player,
-                    source="registration",
-                    identifier_type="registrant id",
-                    identifier_value="abc-123",
-                )
-
-    def test_source_row_preserves_provenance(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-        row = PlayerSourceRow.objects.create(
-            player=player,
-            source="Roster Import",
-            source_filename="roster.csv",
-            row_number=4,
-            original_row={"First": "Eugene", "Last": "Lin", "Extra": "Value"},
-            unmapped_fields={"Extra": "Value"},
-        )
-
-        self.assertEqual(row.source, "roster import")
-        self.assertEqual(row.original_row["First"], "Eugene")
-        self.assertEqual(row.unmapped_fields, {"Extra": "Value"})
-
-    def test_tag_assignment_and_removal(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-        tag = PlayerTag.objects.create(name="Strong Arm")
-
-        tag.players.add(player)
-        self.assertEqual(list(player.tags.all()), [tag])
-
-        tag.players.remove(player)
-        self.assertFalse(player.tags.exists())
-
-
-class PlayerServiceTests(TestCase):
-    def test_create_player_service_creates_canonical_player(self):
-        player = create_player(first_name="Eugene", last_name="Lin", division="13U")
-
-        self.assertEqual(player.full_name, "Eugene Lin")
-        self.assertEqual(player.division, "13U")
-
-    def test_add_source_identifier_service_normalizes_values(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-        identifier = add_source_identifier(
-            player,
-            source="Registration",
-            identifier_type="Registrant ID",
-            identifier_value=" ABC-123 ",
-        )
-
-        self.assertEqual(identifier.source, "registration")
-        self.assertEqual(identifier.identifier_type, "registrant id")
-        self.assertEqual(identifier.identifier_value, "abc-123")
-
-    def test_match_by_identifier_returns_exact_match(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-        add_source_identifier(player, "registration", "registrant_id", "abc-123")
-
-        result = match_by_identifier("Registration", "Registrant_ID", " ABC-123 ")
-
-        self.assertEqual(result.status, MATCH_EXACT)
-        self.assertEqual(result.player, player)
-
-    def test_name_and_birthdate_returns_high_confidence_match(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate=date(2012, 5, 1))
-
-        result = match_by_name_and_birthdate("eugene", "lin", date(2012, 5, 1))
-
-        self.assertEqual(result.status, MATCH_HIGH_CONFIDENCE)
-        self.assertEqual(result.player, player)
-
-    def test_duplicate_name_candidates_return_ambiguous(self):
-        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
-        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
-
-        result = find_player_match(
-            {
-                "first_name": "Eugene",
-                "last_name": "Lin",
-                "birth_year": 2012,
-                "division": "13U",
-            }
-        )
-
-        self.assertEqual(result.status, MATCH_AMBIGUOUS)
-        self.assertEqual(len(result.candidates), 2)
-
-    def test_unknown_identity_returns_no_match(self):
-        result = find_player_match({"first_name": "Unknown", "last_name": "Player"})
-
-        self.assertEqual(result.status, MATCH_NO_MATCH)
-        self.assertIsNone(result.player)
-
-    def test_tag_service_assigns_removes_and_filters_tags(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin")
-
-        tag = assign_tag(player, "Strong Arm")
-
-        self.assertEqual(tag.slug, "strong-arm")
-        self.assertEqual(list(players_with_tag("strong-arm")), [player])
-        self.assertEqual(list(active_tags()), [tag])
-
-        remove_tag(player, "Strong Arm")
-        self.assertFalse(players_with_tag("strong-arm").exists())
-
-    def test_import_service_builds_identity_payload(self):
-        row = {"First": " Eugene ", "Last": " Lin ", "Division": "13U", "Unused": "x"}
-        payload = import_service.build_identity_payload(
-            row,
-            mapping={"first_name": "First", "last_name": "Last", "division": "Division"},
-        )
-
-        self.assertEqual(payload["first_name"], "Eugene")
-        self.assertEqual(payload["last_name"], "Lin")
-        self.assertEqual(payload["division"], "13U")
-        self.assertEqual(import_service.normalize_header(" First   Name "), "first name")
-
-
-class PlayerIntegrationTests(TestCase):
-    def test_players_app_is_installed(self):
-        self.assertTrue(apps.is_installed("players"))
-
-    def test_player_models_are_registered_in_admin(self):
-        for model in [Player, PlayerAlias, PlayerImportBatch, PlayerSourceIdentifier, PlayerSourceRow, PlayerTag]:
-            self.assertIn(model, admin.site._registry)


 class PlayerImportWorkflowTests(TestCase):
     def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
         self.user = User.objects.create_user(username="user", password="testpass")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )

-    def upload(self, name="member list for 13u house.csv", body=b"First,Last,Gender,Division,Team\nEugene,Lin,M,13U,Expos\n"):
+    def upload(
+        self,
+        name="member list for 13u house.csv",
+        body=b"First,Last,Gender,Division,Team\nEugene,Lin,M,13U,Expos\n",
+    ):
         return SimpleUploadedFile(name, body, content_type="text/csv")

     def test_parse_csv_handles_bom_and_preserves_rows(self):
-        parsed = parse_player_csv(self.upload(body="\ufeffFirst,Last,Extra\nEugene,Lin,Value\n".encode("utf-8")))
+        parsed = parse_player_csv(
+            self.upload(
+                body="\ufeffFirst,Last,Extra\nEugene,Lin,Value\n".encode("utf-8")
+            )
+        )

         self.assertEqual(parsed.headers, ["First", "Last", "Extra"])
         self.assertEqual(parsed.rows[0]["row_number"], 2)
@@ -250,7 +68,12 @@ class PlayerImportWorkflowTests(TestCase):

     def test_parse_csv_rejects_oversized_uploads(self):
         with self.assertRaises(ValidationError):
-            parse_player_csv(self.upload(body=b"First,Last\n" + (b"A,B\n" * ((MAX_CSV_UPLOAD_BYTES // 4) + 1))))
+            parse_player_csv(
+                self.upload(
+                    body=b"First,Last\n"
+                    + (b"A,B\n" * ((MAX_CSV_UPLOAD_BYTES // 4) + 1))
+                )
+            )

     def test_parse_csv_rejects_too_many_rows(self):
         rows = b"".join([b"A,B\n" for _ in range(MAX_CSV_ROWS + 1)])
@@ -259,8 +82,13 @@ class PlayerImportWorkflowTests(TestCase):
             parse_player_csv(self.upload(body=b"First,Last\n" + rows))

     def test_suggest_mapping_for_member_and_roster_headers(self):
-        member_mapping = suggest_mapping(["First", "Last", "Gender", "Team"], source=SOURCE_MEMBER_LIST)
-        roster_mapping = suggest_mapping(["First Name", "Last Name", "DOB", "Registration ID"], source=SOURCE_ROSTER_DETAIL)
+        member_mapping = suggest_mapping(
+            ["First", "Last", "Gender", "Team"], source=SOURCE_MEMBER_LIST
+        )
+        roster_mapping = suggest_mapping(
+            ["First Name", "Last Name", "DOB", "Registration ID"],
+            source=SOURCE_ROSTER_DETAIL,
+        )

         self.assertEqual(member_mapping["first_name"], "First")
         self.assertEqual(member_mapping["team_name"], "Team")
@@ -269,10 +97,17 @@ class PlayerImportWorkflowTests(TestCase):

     def test_create_import_batch_requires_staff(self):
         with self.assertRaises(PermissionDenied):
-            create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.user)
+            create_import_batch(
+                file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.user
+            )

     def test_preview_classifies_new_player_as_create(self):
-        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        batch = create_import_batch(
+            file_obj=self.upload(),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=self.season,
+        )
         preview = batch.preview_snapshot["preview"]

         self.assertEqual(preview["rows"][0]["action"], ACTION_CREATE)
@@ -283,9 +118,18 @@ class PlayerImportWorkflowTests(TestCase):
         inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)

         with self.assertRaises(ValidationError):
-            create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff)
+            create_import_batch(
+                file_obj=self.upload(),
+                source=SOURCE_MEMBER_LIST,
+                uploaded_by=self.staff,
+            )
         with self.assertRaises(ValidationError):
-            create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=inactive)
+            create_import_batch(
+                file_obj=self.upload(),
+                source=SOURCE_MEMBER_LIST,
+                uploaded_by=self.staff,
+                season=inactive,
+            )

     def test_preview_classifies_source_identifier_match_as_update(self):
         player = Player.objects.create(first_name="Eugene", last_name="Lin")
@@ -324,8 +168,12 @@ class PlayerImportWorkflowTests(TestCase):
     def test_preview_marks_conflicting_source_identifiers_as_ambiguous(self):
         player_one = Player.objects.create(first_name="Eugene", last_name="Lin")
         player_two = Player.objects.create(first_name="Gene", last_name="Lynn")
-        add_source_identifier(player_one, SOURCE_ROSTER_DETAIL, "registration_id", "REG-1")
-        add_source_identifier(player_two, SOURCE_ROSTER_DETAIL, "registrant_id", "MEM-1")
+        add_source_identifier(
+            player_one, SOURCE_ROSTER_DETAIL, "registration_id", "REG-1"
+        )
+        add_source_identifier(
+            player_two, SOURCE_ROSTER_DETAIL, "registrant_id", "MEM-1"
+        )
         batch = create_import_batch(
             file_obj=self.upload(
                 name="roster detail for 13u house.csv",
@@ -382,10 +230,16 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(row["field_conflicts"][0]["field_name"], "first_name")

     def test_preview_ambiguous_match_and_missing_name_error(self):
-        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
-        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
+        Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
+        Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n,Missing,2012,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n,Missing,2012,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=self.season,
@@ -397,14 +251,23 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(rows[1]["action"], ACTION_ERROR)

     def test_commit_creates_player_and_source_row(self):
-        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        batch = create_import_batch(
+            file_obj=self.upload(),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=self.season,
+        )

         result = commit_import_batch(import_batch=batch, actor=self.staff)

         player = Player.objects.get(first_name="Eugene", last_name="Lin")
         self.assertEqual(result.created, 1)
-        self.assertEqual(PlayerSourceRow.objects.get(player=player).import_batch_id, batch.id)
-        membership = PlayerRosterMembership.objects.select_related("season_team").get(player=player)
+        self.assertEqual(
+            PlayerSourceRow.objects.get(player=player).import_batch_id, batch.id
+        )
+        membership = PlayerRosterMembership.objects.select_related("season_team").get(
+            player=player
+        )
         self.assertEqual(membership.season_team.season, self.season)
         self.assertEqual(membership.season_team.name, "Expos")
         self.assertEqual(membership.season_team.division, "13U")
@@ -415,12 +278,19 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(batch.status, PlayerImportStatus.COMMITTED)

     def test_commit_reuses_same_team_membership_in_same_season(self):
-        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        first_batch = create_import_batch(
+            file_obj=self.upload(),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=self.season,
+        )
         commit_import_batch(import_batch=first_batch, actor=self.staff)
         player = Player.objects.get(first_name="Eugene", last_name="Lin")
         add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")
         second_batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team,Jersey\nEugene,Lin,MEM-1,13U,Expos,27\n"),
+            file_obj=self.upload(
+                body=b"First,Last,Registrant ID,Division,Team,Jersey\nEugene,Lin,MEM-1,13U,Expos,27\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=self.season,
@@ -430,17 +300,31 @@ class PlayerImportWorkflowTests(TestCase):

         self.assertEqual(result.updated, 1)
         self.assertEqual(result.memberships_updated, 1)
-        self.assertEqual(PlayerRosterMembership.objects.filter(player=player, season_team__season=self.season).count(), 1)
-        self.assertEqual(PlayerRosterMembership.objects.get(player=player).jersey_number, "27")
+        self.assertEqual(
+            PlayerRosterMembership.objects.filter(
+                player=player, season_team__season=self.season
+            ).count(),
+            1,
+        )
+        self.assertEqual(
+            PlayerRosterMembership.objects.get(player=player).jersey_number, "27"
+        )

     def test_commit_preserves_prior_season_and_creates_future_membership(self):
-        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        first_batch = create_import_batch(
+            file_obj=self.upload(),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=self.season,
+        )
         commit_import_batch(import_batch=first_batch, actor=self.staff)
         player = Player.objects.get(first_name="Eugene", last_name="Lin")
         add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")
         next_season = create_season(key="2027-spring", name="2027 Spring")
         next_batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team\nEugene,Lin,MEM-1,15U,Mounties\n"),
+            file_obj=self.upload(
+                body=b"First,Last,Registrant ID,Division,Team\nEugene,Lin,MEM-1,15U,Mounties\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=next_season,
@@ -448,22 +332,39 @@ class PlayerImportWorkflowTests(TestCase):

         commit_import_batch(import_batch=next_batch, actor=self.staff)

-        self.assertEqual(PlayerRosterMembership.objects.filter(player=player).count(), 2)
+        self.assertEqual(
+            PlayerRosterMembership.objects.filter(player=player).count(), 2
+        )
         self.assertTrue(
-            PlayerRosterMembership.objects.filter(player=player, season_team__season=self.season, season_team__name="Expos").exists()
+            PlayerRosterMembership.objects.filter(
+                player=player,
+                season_team__season=self.season,
+                season_team__name="Expos",
+            ).exists()
         )
         self.assertTrue(
-            PlayerRosterMembership.objects.filter(player=player, season_team__season=next_season, season_team__name="Mounties").exists()
+            PlayerRosterMembership.objects.filter(
+                player=player,
+                season_team__season=next_season,
+                season_team__name="Mounties",
+            ).exists()
         )

     def test_preview_blocks_same_season_team_change_for_active_primary(self):
-        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        first_batch = create_import_batch(
+            file_obj=self.upload(),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=self.season,
+        )
         commit_import_batch(import_batch=first_batch, actor=self.staff)
         player = Player.objects.get(first_name="Eugene", last_name="Lin")
         add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")

         change_batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team\nEugene,Lin,MEM-1,13U,Mounties\n"),
+            file_obj=self.upload(
+                body=b"First,Last,Registrant ID,Division,Team\nEugene,Lin,MEM-1,13U,Mounties\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=self.season,
@@ -474,7 +375,9 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertIn("active primary membership", " ".join(row["errors"]))

     def test_commit_updates_blanks_without_overwriting_conflicts(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01")
+        player = Player.objects.create(
+            first_name="Eugene", last_name="Lin", birthdate="2012-05-01"
+        )
         add_source_identifier(player, SOURCE_ROSTER_DETAIL, "registration_id", "REG-1")
         batch = create_import_batch(
             file_obj=self.upload(
@@ -493,24 +396,42 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(player.team_name, "Expos")

     def test_commit_applies_use_imported_resolution(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
+        player = Player.objects.create(
+            first_name="Eugene",
+            last_name="Lin",
+            birthdate="2012-05-01",
+            preferred_name="Old",
+        )
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=self.season,
         )
-        resolutions = {"2": {"action": "commit", "fields": {"preferred_name": "use_imported"}}}
+        resolutions = {
+            "2": {"action": "commit", "fields": {"preferred_name": "use_imported"}}
+        }

-        commit_import_batch(import_batch=batch, actor=self.staff, resolutions=resolutions)
+        commit_import_batch(
+            import_batch=batch, actor=self.staff, resolutions=resolutions
+        )

         player.refresh_from_db()
         self.assertEqual(player.preferred_name, "New")

     def test_commit_rejects_unresolved_review_rows_without_mutating_player(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
+        player = Player.objects.create(
+            first_name="Eugene",
+            last_name="Lin",
+            birthdate="2012-05-01",
+            preferred_name="Old",
+        )
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=self.season,
@@ -533,7 +454,11 @@ class PlayerImportWorkflowTests(TestCase):
             season=self.season,
         )

-        result = commit_import_batch(import_batch=batch, actor=self.staff, resolutions={"2": {"action": ACTION_SKIP}})
+        result = commit_import_batch(
+            import_batch=batch,
+            actor=self.staff,
+            resolutions={"2": {"action": ACTION_SKIP}},
+        )

         batch.refresh_from_db()
         self.assertEqual(result.skipped, 1)
@@ -541,10 +466,16 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertFalse(Player.objects.exists())

     def test_commit_resolves_ambiguous_match_to_selected_candidate(self):
-        player_one = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
-        player_two = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
+        player_one = Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
+        player_two = Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=self.season,
@@ -553,7 +484,12 @@ class PlayerImportWorkflowTests(TestCase):
         result = commit_import_batch(
             import_batch=batch,
             actor=self.staff,
-            resolutions={"2": {"action": RESOLUTION_ACTION_USE_CANDIDATE, "candidate_id": str(player_two.id)}},
+            resolutions={
+                "2": {
+                    "action": RESOLUTION_ACTION_USE_CANDIDATE,
+                    "candidate_id": str(player_two.id),
+                }
+            },
         )

         player_two.refresh_from_db()
@@ -564,10 +500,16 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertFalse(PlayerSourceRow.objects.filter(player=player_one).exists())

     def test_commit_can_create_new_player_from_ambiguous_row(self):
-        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
-        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
+        Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
+        Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=self.season,
@@ -583,7 +525,12 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(Player.objects.count(), 3)

     def test_commit_prevents_double_commit(self):
-        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        batch = create_import_batch(
+            file_obj=self.upload(),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=self.season,
+        )
         commit_import_batch(import_batch=batch, actor=self.staff)

         with self.assertRaises(ValidationError):
@@ -591,7 +538,9 @@ class PlayerImportWorkflowTests(TestCase):

     def test_commit_without_provisioning_leaves_account_models_unchanged(self):
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Division,Team\nEugene,Lin,2012-05-01,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,DOB,Division,Team\nEugene,Lin,2012-05-01,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             season=self.season,
@@ -605,7 +554,9 @@ class PlayerImportWorkflowTests(TestCase):

     def test_commit_with_provisioning_creates_eligible_account_and_safe_summary(self):
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             provision_player_accounts=True,
@@ -623,7 +574,11 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertTrue(user.is_active)
         self.assertEqual(user.email, "eugene@example.com")
         self.assertTrue(user.check_password("20120501"))
-        self.assertTrue(UserPlayerLink.objects.filter(user=user, player=player, relationship="self").exists())
+        self.assertTrue(
+            UserPlayerLink.objects.filter(
+                user=user, player=player, relationship="self"
+            ).exists()
+        )
         summary = batch.import_summary["account_provisioning"]
         self.assertEqual(summary["users_created"], 1)
         self.assertEqual(summary["already_linked"], 0)
@@ -631,7 +586,9 @@ class PlayerImportWorkflowTests(TestCase):

     def test_commit_with_provisioning_skips_missing_birthdate_without_rollback(self):
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Division,Team\nEugene,Lin,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,Division,Team\nEugene,Lin,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             provision_player_accounts=True,
@@ -641,14 +598,18 @@ class PlayerImportWorkflowTests(TestCase):
         commit_import_batch(import_batch=batch, actor=self.staff)

         batch.refresh_from_db()
-        self.assertTrue(Player.objects.filter(first_name="Eugene", last_name="Lin").exists())
+        self.assertTrue(
+            Player.objects.filter(first_name="Eugene", last_name="Lin").exists()
+        )
         self.assertFalse(User.objects.filter(username="eugene.lin").exists())
         self.assertEqual(batch.import_summary["account_provisioning"]["skipped"], 1)

     def test_commit_with_provisioning_reports_duplicate_unrelated_email_conflict(self):
         User.objects.create_user(username="existing", email="eugene@example.com")
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"),
+            file_obj=self.upload(
+                body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"
+            ),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             provision_player_accounts=True,
@@ -661,6 +622,8 @@ class PlayerImportWorkflowTests(TestCase):
         commit_import_batch(import_batch=batch, actor=self.staff)

         batch.refresh_from_db()
-        self.assertTrue(Player.objects.filter(first_name="Eugene", last_name="Lin").exists())
+        self.assertTrue(
+            Player.objects.filter(first_name="Eugene", last_name="Lin").exists()
+        )
         self.assertFalse(User.objects.filter(username="eugene.lin").exists())
         self.assertEqual(batch.import_summary["account_provisioning"]["conflicts"], 1)
diff --git a/players/tests/test_models.py b/players/tests/test_models.py
new file mode 100644
index 0000000..57d8ef5
--- /dev/null
+++ b/players/tests/test_models.py
@@ -0,0 +1,100 @@
+from players.tests.helpers import (
+    IntegrityError,
+    Player,
+    PlayerAlias,
+    PlayerSourceIdentifier,
+    PlayerSourceRow,
+    PlayerTag,
+    TestCase,
+    transaction,
+)
+
+
+class PlayerModelTests(TestCase):
+    def test_player_full_name_and_display_name(self):
+        player = Player.objects.create(
+            first_name="Eugene", last_name="Lin", preferred_name="Gene"
+        )
+
+        self.assertEqual(player.full_name, "Eugene Lin")
+        self.assertEqual(player.display_name, "Gene Lin")
+        self.assertEqual(str(player), "Gene Lin")
+
+    def test_player_model_has_no_pdp_dependency(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+        related_models = [
+            field.remote_field.model
+            for field in Player._meta.fields
+            if getattr(field, "remote_field", None) and field.remote_field
+        ]
+
+        self.assertEqual(related_models, [])
+        self.assertEqual(player.full_name, "Eugene Lin")
+
+    def test_alias_saves_normalized_value(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+        alias = PlayerAlias.objects.create(
+            player=player, alias="  Gene   LIN  ", source="manual"
+        )
+
+        self.assertEqual(alias.normalized_alias, "gene lin")
+
+    def test_duplicate_alias_for_same_player_is_rejected(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+        PlayerAlias.objects.create(player=player, alias="Gene Lin")
+
+        with self.assertRaises(IntegrityError):
+            with transaction.atomic():
+                PlayerAlias.objects.create(player=player, alias=" gene   lin ")
+
+    def test_same_alias_can_exist_for_different_players(self):
+        player_one = Player.objects.create(first_name="Eugene", last_name="Lin")
+        player_two = Player.objects.create(first_name="Gene", last_name="Lynn")
+
+        PlayerAlias.objects.create(player=player_one, alias="Gene")
+        PlayerAlias.objects.create(player=player_two, alias="Gene")
+
+        self.assertEqual(PlayerAlias.objects.filter(normalized_alias="gene").count(), 2)
+
+    def test_source_identifier_uniqueness_uses_source_type_and_value(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+        PlayerSourceIdentifier.objects.create(
+            player=player,
+            source="Registration",
+            identifier_type="Registrant ID",
+            identifier_value=" ABC-123 ",
+        )
+
+        with self.assertRaises(IntegrityError):
+            with transaction.atomic():
+                PlayerSourceIdentifier.objects.create(
+                    player=player,
+                    source="registration",
+                    identifier_type="registrant id",
+                    identifier_value="abc-123",
+                )
+
+    def test_source_row_preserves_provenance(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+        row = PlayerSourceRow.objects.create(
+            player=player,
+            source="Roster Import",
+            source_filename="roster.csv",
+            row_number=4,
+            original_row={"First": "Eugene", "Last": "Lin", "Extra": "Value"},
+            unmapped_fields={"Extra": "Value"},
+        )
+
+        self.assertEqual(row.source, "roster import")
+        self.assertEqual(row.original_row["First"], "Eugene")
+        self.assertEqual(row.unmapped_fields, {"Extra": "Value"})
+
+    def test_tag_assignment_and_removal(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+        tag = PlayerTag.objects.create(name="Strong Arm")
+
+        tag.players.add(player)
+        self.assertEqual(list(player.tags.all()), [tag])
+
+        tag.players.remove(player)
+        self.assertFalse(player.tags.exists())
diff --git a/players/tests/test_services.py b/players/tests/test_services.py
new file mode 100644
index 0000000..256a15b
--- /dev/null
+++ b/players/tests/test_services.py
@@ -0,0 +1,138 @@
+from players.tests.helpers import (
+    MATCH_AMBIGUOUS,
+    MATCH_EXACT,
+    MATCH_HIGH_CONFIDENCE,
+    MATCH_NO_MATCH,
+    Player,
+    PlayerAlias,
+    PlayerImportBatch,
+    PlayerSourceIdentifier,
+    PlayerSourceRow,
+    PlayerTag,
+    TestCase,
+    active_tags,
+    add_source_identifier,
+    admin,
+    apps,
+    assign_tag,
+    create_player,
+    date,
+    find_player_match,
+    import_service,
+    match_by_identifier,
+    match_by_name_and_birthdate,
+    players_with_tag,
+    remove_tag,
+)
+
+
+class PlayerServiceTests(TestCase):
+    def test_create_player_service_creates_canonical_player(self):
+        player = create_player(first_name="Eugene", last_name="Lin", division="13U")
+
+        self.assertEqual(player.full_name, "Eugene Lin")
+        self.assertEqual(player.division, "13U")
+
+    def test_add_source_identifier_service_normalizes_values(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+        identifier = add_source_identifier(
+            player,
+            source="Registration",
+            identifier_type="Registrant ID",
+            identifier_value=" ABC-123 ",
+        )
+
+        self.assertEqual(identifier.source, "registration")
+        self.assertEqual(identifier.identifier_type, "registrant id")
+        self.assertEqual(identifier.identifier_value, "abc-123")
+
+    def test_match_by_identifier_returns_exact_match(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+        add_source_identifier(player, "registration", "registrant_id", "abc-123")
+
+        result = match_by_identifier("Registration", "Registrant_ID", " ABC-123 ")
+
+        self.assertEqual(result.status, MATCH_EXACT)
+        self.assertEqual(result.player, player)
+
+    def test_name_and_birthdate_returns_high_confidence_match(self):
+        player = Player.objects.create(
+            first_name="Eugene", last_name="Lin", birthdate=date(2012, 5, 1)
+        )
+
+        result = match_by_name_and_birthdate("eugene", "lin", date(2012, 5, 1))
+
+        self.assertEqual(result.status, MATCH_HIGH_CONFIDENCE)
+        self.assertEqual(result.player, player)
+
+    def test_duplicate_name_candidates_return_ambiguous(self):
+        Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
+        Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
+
+        result = find_player_match(
+            {
+                "first_name": "Eugene",
+                "last_name": "Lin",
+                "birth_year": 2012,
+                "division": "13U",
+            }
+        )
+
+        self.assertEqual(result.status, MATCH_AMBIGUOUS)
+        self.assertEqual(len(result.candidates), 2)
+
+    def test_unknown_identity_returns_no_match(self):
+        result = find_player_match({"first_name": "Unknown", "last_name": "Player"})
+
+        self.assertEqual(result.status, MATCH_NO_MATCH)
+        self.assertIsNone(result.player)
+
+    def test_tag_service_assigns_removes_and_filters_tags(self):
+        player = Player.objects.create(first_name="Eugene", last_name="Lin")
+
+        tag = assign_tag(player, "Strong Arm")
+
+        self.assertEqual(tag.slug, "strong-arm")
+        self.assertEqual(list(players_with_tag("strong-arm")), [player])
+        self.assertEqual(list(active_tags()), [tag])
+
+        remove_tag(player, "Strong Arm")
+        self.assertFalse(players_with_tag("strong-arm").exists())
+
+    def test_import_service_builds_identity_payload(self):
+        row = {"First": " Eugene ", "Last": " Lin ", "Division": "13U", "Unused": "x"}
+        payload = import_service.build_identity_payload(
+            row,
+            mapping={
+                "first_name": "First",
+                "last_name": "Last",
+                "division": "Division",
+            },
+        )
+
+        self.assertEqual(payload["first_name"], "Eugene")
+        self.assertEqual(payload["last_name"], "Lin")
+        self.assertEqual(payload["division"], "13U")
+        self.assertEqual(
+            import_service.normalize_header(" First   Name "), "first name"
+        )
+
+
+class PlayerIntegrationTests(TestCase):
+    def test_players_app_is_installed(self):
+        self.assertTrue(apps.is_installed("players"))
+
+    def test_player_models_are_registered_in_admin(self):
+        for model in [
+            Player,
+            PlayerAlias,
+            PlayerImportBatch,
+            PlayerSourceIdentifier,
+            PlayerSourceRow,
+            PlayerTag,
+        ]:
+            self.assertIn(model, admin.site._registry)
diff --git a/seasons/tests.py b/seasons/tests.py
deleted file mode 100644
index b92ca5d..0000000
--- a/seasons/tests.py
+++ /dev/null
@@ -1,774 +0,0 @@
-from datetime import date
-
-from django.apps import apps
-from django.contrib import admin
-from django.contrib.auth import get_user_model
-from django.core.exceptions import ValidationError
-from django.db import transaction
-from django.test import TestCase
-from django.urls import reverse
-
-from accounts.models import AccountRole
-from accounts.services.profile_service import get_or_create_account_profile, set_account_role
-from analytics.models import EvaluationCycle, RESPONSE_TYPE_RATING_1_5, RESPONSE_TYPE_TEXT
-from analytics.services.observation_service import create_coach_assessment_observation, submit_observation
-from analytics.services.question_service import ensure_default_coach_assessment_setup
-from players.models import Player
-from seasons.models import (
-    CoachAssignmentRole,
-    CoachSeasonAssignment,
-    PlayerRosterMembership,
-    RosterStatus,
-    Season,
-    SeasonTeam,
-)
-from seasons.services.coach_assignment_service import (
-    assignments_for_team,
-    assignments_for_user,
-    create_assignment,
-    deactivate_assignment,
-    get_primary_assignment,
-    set_primary_assignment,
-    update_assignment,
-)
-from seasons.services.membership_service import (
-    create_membership,
-    current_team_division,
-    deactivate_membership,
-    get_current_membership,
-    get_primary_membership,
-    memberships_for_player,
-    sync_player_current_team_fields,
-    transfer_player,
-    update_membership,
-)
-from seasons.services.season_service import create_season, deactivate_season, get_current_season, set_current_season
-from seasons.services.team_service import get_or_create_season_team, update_season_team
-
-
-User = get_user_model()
-
-
-class SeasonModelServiceTests(TestCase):
-    def test_seasons_app_is_installed(self):
-        self.assertTrue(apps.is_installed("seasons"))
-
-    def test_create_valid_season_normalizes_key(self):
-        season = create_season(key=" 2026 Spring ", name=" 2026 Spring ", starts_on=date(2026, 4, 1))
-
-        self.assertEqual(season.key, "2026-spring")
-        self.assertEqual(season.name, "2026 Spring")
-        self.assertTrue(season.is_active)
-        self.assertFalse(season.is_current)
-
-    def test_season_key_is_unique(self):
-        create_season(key="2026-spring", name="2026 Spring")
-
-        with self.assertRaises(ValidationError):
-            create_season(key="2026 Spring", name="Duplicate")
-
-    def test_season_requires_key_name_and_valid_dates(self):
-        with self.assertRaises(ValidationError):
-            create_season(key="", name="2026 Spring")
-        with self.assertRaises(ValidationError):
-            create_season(key="2026-spring", name="")
-        with self.assertRaises(ValidationError):
-            create_season(key="2026-spring", name="2026 Spring", starts_on=date(2026, 8, 1), ends_on=date(2026, 4, 1))
-
-    def test_zero_current_seasons_allowed_before_setup(self):
-        create_season(key="2026-spring", name="2026 Spring")
-
-        self.assertIsNone(get_current_season())
-
-    def test_set_first_current_season_and_switch_current(self):
-        spring = create_season(key="2026-spring", name="2026 Spring")
-        summer = create_season(key="2026-summer", name="2026 Summer")
-
-        set_current_season(spring)
-        self.assertEqual(get_current_season(), spring)
-
-        set_current_season(summer)
-        spring.refresh_from_db()
-        summer.refresh_from_db()
-        self.assertFalse(spring.is_current)
-        self.assertTrue(summer.is_current)
-        self.assertEqual(get_current_season(), summer)
-
-    def test_model_validation_prevents_second_current_season(self):
-        create_season(key="2026-spring", name="2026 Spring", is_current=True)
-
-        with self.assertRaises(ValidationError):
-            with transaction.atomic():
-                Season.objects.create(key="2026-summer", name="2026 Summer", is_current=True)
-
-    def test_inactive_historical_season_remains_queryable(self):
-        season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-
-        deactivate_season(season)
-        season.refresh_from_db()
-
-        self.assertFalse(season.is_active)
-        self.assertFalse(season.is_current)
-        self.assertEqual(Season.objects.get(pk=season.pk), season)
-
-
-class SeasonTeamTests(TestCase):
-    def setUp(self):
-        self.spring = create_season(key="2026-spring", name="2026 Spring")
-        self.next_spring = create_season(key="2027-spring", name="2027 Spring")
-
-    def test_create_team_normalizes_values(self):
-        team, created = get_or_create_season_team(season=self.spring, name="  Dodgers  ", division=" 13U   House ")
-
-        self.assertTrue(created)
-        self.assertEqual(team.normalized_name, "dodgers")
-        self.assertEqual(team.normalized_division, "13u house")
-
-    def test_same_normalized_team_division_reused(self):
-        first, created_first = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
-        second, created_second = get_or_create_season_team(season=self.spring, name=" dodgers ", division=" 13u ")
-
-        self.assertTrue(created_first)
-        self.assertFalse(created_second)
-        self.assertEqual(first, second)
-
-    def test_same_team_name_in_different_seasons_allowed(self):
-        first, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
-        second, _ = get_or_create_season_team(season=self.next_spring, name="Dodgers", division="13U")
-
-        self.assertNotEqual(first, second)
-
-    def test_external_identifier_scoped_to_season_and_blank_does_not_conflict(self):
-        first, _ = get_or_create_season_team(
-            season=self.spring,
-            name="Dodgers",
-            division="13U",
-            external_source="Roster",
-            external_identifier="ABC",
-        )
-        second, created_second = get_or_create_season_team(
-            season=self.next_spring,
-            name="Dodgers",
-            division="13U",
-            external_source="Roster",
-            external_identifier="ABC",
-        )
-        blank_one, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
-        blank_two, _ = get_or_create_season_team(season=self.spring, name="Mounties", division="13U")
-
-        self.assertNotEqual(first, second)
-        self.assertTrue(created_second)
-        self.assertNotEqual(blank_one, blank_two)
-
-    def test_external_identifier_conflict_rejected(self):
-        get_or_create_season_team(
-            season=self.spring,
-            name="Dodgers",
-            division="13U",
-            external_source="Roster",
-            external_identifier="ABC",
-        )
-
-        with self.assertRaises(ValidationError):
-            get_or_create_season_team(
-                season=self.spring,
-                name="Expos",
-                division="13U",
-                external_source="roster",
-                external_identifier="abc",
-            )
-
-
-class PlayerMembershipTests(TestCase):
-    def setUp(self):
-        self.spring = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        self.next_spring = create_season(key="2027-spring", name="2027 Spring")
-        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
-        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
-        self.mounties, _ = get_or_create_season_team(season=self.next_spring, name="Mounties", division="15U")
-        self.player = Player.objects.create(first_name="Alex", last_name="Player", team_name="Legacy", division="Legacy")
-
-    def test_player_may_join_one_team_and_different_seasons(self):
-        first = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-        second = create_membership(player=self.player, season_team=self.mounties, is_primary=True)
-
-        self.assertEqual(first.player, self.player)
-        self.assertEqual(second.player, self.player)
-        self.assertEqual(memberships_for_player(self.player).count(), 2)
-
-    def test_multiple_memberships_in_one_season_and_non_primary_concurrent_allowed(self):
-        primary = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-        guest = create_membership(player=self.player, season_team=self.expos, status=RosterStatus.GUEST, is_primary=False)
-
-        self.assertTrue(primary.is_primary)
-        self.assertFalse(guest.is_primary)
-        self.assertEqual(memberships_for_player(self.player, self.spring).count(), 2)
-
-    def test_only_one_active_primary_membership_per_player_season(self):
-        first = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-        second = create_membership(player=self.player, season_team=self.expos, is_primary=True)
-
-        first.refresh_from_db()
-        second.refresh_from_db()
-        self.assertFalse(first.is_primary)
-        self.assertTrue(second.is_primary)
-        self.assertEqual(get_primary_membership(self.player, self.spring), second)
-
-    def test_update_membership_can_unset_primary(self):
-        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-
-        update_membership(membership, is_primary=False)
-        membership.refresh_from_db()
-
-        self.assertFalse(membership.is_primary)
-
-    def test_direct_duplicate_primary_membership_is_rejected(self):
-        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-
-        with self.assertRaises(ValidationError):
-            PlayerRosterMembership.objects.create(player=self.player, season_team=self.expos, is_primary=True)
-
-    def test_transfer_creates_new_membership_and_preserves_history(self):
-        old = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-
-        new = transfer_player(player=self.player, to_season_team=self.expos, transfer_date=date(2026, 6, 1))
-        old.refresh_from_db()
-        self.player.refresh_from_db()
-
-        self.assertFalse(old.is_active)
-        self.assertFalse(old.is_primary)
-        self.assertEqual(old.status, RosterStatus.TRANSFERRED)
-        self.assertEqual(old.ends_on, date(2026, 6, 1))
-        self.assertTrue(new.is_primary)
-        self.assertEqual(self.player.team_name, "Expos")
-        self.assertEqual(self.player.division, "13U")
-
-    def test_date_validation(self):
-        with self.assertRaises(ValidationError):
-            create_membership(
-                player=self.player,
-                season_team=self.dodgers,
-                starts_on=date(2026, 8, 1),
-                ends_on=date(2026, 7, 1),
-            )
-
-    def test_current_membership_derivation_and_team_division(self):
-        create_membership(player=self.player, season_team=self.dodgers, is_primary=False)
-        primary = create_membership(player=self.player, season_team=self.expos, is_primary=True)
-
-        self.assertEqual(get_current_membership(self.player, self.spring), primary)
-        self.assertEqual(current_team_division(self.player, self.spring), ("Expos", "13U"))
-
-    def test_compatibility_sync_is_explicit_and_can_clear_when_requested(self):
-        create_membership(player=self.player, season_team=self.dodgers, is_primary=True, sync_player_fields=False)
-        self.player.refresh_from_db()
-
-        self.assertEqual(self.player.team_name, "Legacy")
-        sync_player_current_team_fields(self.player, self.spring)
-        self.player.refresh_from_db()
-        self.assertEqual(self.player.team_name, "Dodgers")
-        self.assertEqual(self.player.division, "13U")
-
-        deactivate_membership(get_primary_membership(self.player, self.spring), sync_player_fields=False)
-        sync_player_current_team_fields(self.player, self.spring, clear_when_missing=False)
-        self.player.refresh_from_db()
-        self.assertEqual(self.player.team_name, "Dodgers")
-
-        sync_player_current_team_fields(self.player, self.spring, clear_when_missing=True)
-        self.player.refresh_from_db()
-        self.assertEqual(self.player.team_name, "")
-        self.assertEqual(self.player.division, "")
-
-
-class CoachAssignmentTests(TestCase):
-    def setUp(self):
-        self.spring = create_season(key="2026-spring", name="2026 Spring")
-        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
-        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
-        self.coach = User.objects.create_user(
-            username="coach",
-            password="original-pass",
-            first_name="Casey",
-            last_name="Coach",
-            email="coach@example.com",
-        )
-        set_account_role(self.coach, AccountRole.COACH)
-
-    def test_create_assignment_and_query_helpers(self):
-        assignment = create_assignment(
-            user=self.coach,
-            season_team=self.dodgers,
-            assignment_role=CoachAssignmentRole.HEAD_COACH,
-            is_primary=True,
-        )
-
-        self.assertEqual(assignments_for_user(self.coach, self.spring).first(), assignment)
-        self.assertEqual(assignments_for_team(self.dodgers).first(), assignment)
-        self.assertEqual(get_primary_assignment(self.coach, self.spring), assignment)
-
-    def test_multiple_assignments_and_multiple_coaches_allowed(self):
-        other = User.objects.create_user(username="other", password="testpass")
-
-        first = create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
-        second = create_assignment(user=self.coach, season_team=self.expos, assignment_role=CoachAssignmentRole.EVALUATOR)
-        third = create_assignment(user=other, season_team=self.dodgers, assignment_role=CoachAssignmentRole.ASSISTANT_COACH)
-
-        self.assertEqual({first, second}, set(assignments_for_user(self.coach, self.spring)))
-        self.assertIn(third, list(assignments_for_team(self.dodgers)))
-
-    def test_duplicate_active_user_team_role_rejected(self):
-        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
-
-        with self.assertRaises(ValidationError):
-            create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
-
-    def test_only_one_active_primary_assignment_per_user_season(self):
-        first = create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH, is_primary=True)
-        second = create_assignment(user=self.coach, season_team=self.expos, assignment_role=CoachAssignmentRole.EVALUATOR, is_primary=True)
-
-        first.refresh_from_db()
-        second.refresh_from_db()
-        self.assertFalse(first.is_primary)
-        self.assertTrue(second.is_primary)
-
-    def test_update_assignment_can_unset_primary(self):
-        assignment = create_assignment(
-            user=self.coach,
-            season_team=self.dodgers,
-            assignment_role=CoachAssignmentRole.HEAD_COACH,
-            is_primary=True,
-        )
-
-        update_assignment(assignment, is_primary=False)
-        assignment.refresh_from_db()
-
-        self.assertFalse(assignment.is_primary)
-
-    def test_direct_duplicate_primary_assignment_is_rejected(self):
-        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH, is_primary=True)
-
-        with self.assertRaises(ValidationError):
-            CoachSeasonAssignment.objects.create(
-                user=self.coach,
-                season_team=self.expos,
-                assignment_role=CoachAssignmentRole.EVALUATOR,
-                is_primary=True,
-            )
-
-    def test_assignment_has_no_account_role_privilege_or_password_side_effects(self):
-        original_password = self.coach.password
-        create_assignment(user=self.coach, season_team=self.dodgers, assignment_role=CoachAssignmentRole.HEAD_COACH)
-        self.coach.refresh_from_db()
-        profile = get_or_create_account_profile(self.coach)
-
-        self.assertEqual(profile.role, AccountRole.COACH)
-        self.assertFalse(self.coach.is_staff)
-        self.assertFalse(self.coach.is_superuser)
-        self.assertEqual(self.coach.password, original_password)
-
-    def test_assignment_date_validation_and_deactivation(self):
-        with self.assertRaises(ValidationError):
-            create_assignment(
-                user=self.coach,
-                season_team=self.dodgers,
-                assignment_role=CoachAssignmentRole.HEAD_COACH,
-                starts_on=date(2026, 8, 1),
-                ends_on=date(2026, 7, 1),
-            )
-
-        assignment = create_assignment(
-            user=self.coach,
-            season_team=self.dodgers,
-            assignment_role=CoachAssignmentRole.HEAD_COACH,
-            is_primary=True,
-        )
-        deactivate_assignment(assignment, ends_on=date(2026, 8, 1))
-        assignment.refresh_from_db()
-        self.assertFalse(assignment.is_active)
-        self.assertFalse(assignment.is_primary)
-        self.assertEqual(assignment.ends_on, date(2026, 8, 1))
-
-
-class SeasonsAdminTests(TestCase):
-    def test_models_registered_in_admin(self):
-        for model in [Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment]:
-            self.assertIn(model, admin.site._registry)
-
-    def test_admin_configuration_is_searchable_and_readonly_timestamps(self):
-        for model in [Season, SeasonTeam, PlayerRosterMembership, CoachSeasonAssignment]:
-            model_admin = admin.site._registry[model]
-            self.assertIn("created_at", model_admin.readonly_fields)
-            self.assertIn("updated_at", model_admin.readonly_fields)
-            self.assertTrue(model_admin.search_fields)
-
-
-class SeasonOperationsUITests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.regular = User.objects.create_user(username="regular", password="testpass")
-        self.coach = User.objects.create_user(
-            username="coach",
-            password="original-pass",
-            first_name="Casey",
-            last_name="Coach",
-            email="coach@example.com",
-        )
-        set_account_role(self.coach, AccountRole.COACH)
-        self.player = Player.objects.create(first_name="Alex", last_name="Player")
-        self.spring = create_season(key="2026-spring", name="2026 Spring", starts_on=date(2026, 4, 1), is_current=True)
-        self.summer = create_season(key="2026-summer", name="2026 Summer")
-        self.dodgers, _ = get_or_create_season_team(season=self.spring, name="Dodgers", division="13U")
-        self.expos, _ = get_or_create_season_team(season=self.spring, name="Expos", division="13U")
-        self.mounties, _ = get_or_create_season_team(season=self.summer, name="Mounties", division="15U")
-
-    def login_staff(self):
-        self.client.force_login(self.staff)
-
-    def test_season_operations_require_staff(self):
-        url = reverse("seasons:season-list")
-
-        self.assertEqual(self.client.get(url).status_code, 302)
-        self.client.force_login(self.regular)
-        self.assertEqual(self.client.get(url).status_code, 403)
-
-        self.login_staff()
-        response = self.client.get(url)
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "2026 Spring")
-
-    def test_staff_can_create_edit_and_set_current_season(self):
-        self.login_staff()
-
-        response = self.client.post(
-            reverse("seasons:season-new"),
-            {
-                "key": "2027-spring",
-                "name": "2027 Spring",
-                "starts_on": "2027-04-01",
-                "ends_on": "",
-                "is_active": "on",
-            },
-        )
-        season = Season.objects.get(key="2027-spring")
-        self.assertRedirects(response, reverse("seasons:season-detail", kwargs={"season_id": season.id}))
-
-        response = self.client.post(
-            reverse("seasons:season-edit", kwargs={"season_id": season.id}),
-            {
-                "key": "2027-spring",
-                "name": "2027 Spring Updated",
-                "starts_on": "2027-04-01",
-                "ends_on": "2027-08-31",
-                "is_active": "on",
-            },
-        )
-        self.assertRedirects(response, reverse("seasons:season-detail", kwargs={"season_id": season.id}))
-        season.refresh_from_db()
-        self.assertEqual(season.name, "2027 Spring Updated")
-
-        self.client.post(reverse("seasons:season-set-current", kwargs={"season_id": season.id}), {"confirm": "on"})
-        self.spring.refresh_from_db()
-        season.refresh_from_db()
-        self.assertFalse(self.spring.is_current)
-        self.assertTrue(season.is_current)
-
-        self.client.post(
-            reverse("seasons:season-edit", kwargs={"season_id": season.id}),
-            {
-                "key": "2027-spring",
-                "name": "2027 Spring Updated",
-                "starts_on": "2027-04-01",
-                "ends_on": "2027-08-31",
-            },
-        )
-        season.refresh_from_db()
-        self.assertFalse(season.is_active)
-        self.assertFalse(season.is_current)
-
-    def test_staff_can_create_and_edit_season_team(self):
-        self.login_staff()
-
-        response = self.client.post(
-            reverse("seasons:season-team-new", kwargs={"season_id": self.spring.id}),
-            {
-                "season": self.spring.id,
-                "name": "Cardinals",
-                "division": "13U",
-                "external_source": "Roster",
-                "external_identifier": "TEAM-1",
-                "is_active": "on",
-            },
-        )
-        self.assertRedirects(response, reverse("seasons:team-list"))
-        team = SeasonTeam.objects.get(name="Cardinals")
-
-        response = self.client.post(
-            reverse("seasons:team-edit", kwargs={"team_id": team.id}),
-            {
-                "season": self.summer.id,
-                "name": "Cardinals Updated",
-                "division": "13U",
-                "external_source": "Roster",
-                "external_identifier": "TEAM-1",
-                "is_active": "on",
-            },
-        )
-        self.assertRedirects(response, reverse("seasons:team-list"))
-        team.refresh_from_db()
-        self.assertEqual(team.name, "Cardinals Updated")
-        self.assertEqual(team.season, self.spring)
-
-    def test_cannot_create_team_from_inactive_season_shortcut(self):
-        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
-        self.login_staff()
-
-        response = self.client.get(reverse("seasons:season-team-new", kwargs={"season_id": inactive.id}))
-
-        self.assertEqual(response.status_code, 404)
-
-    def test_staff_can_manage_membership_history_transfer_and_additional_membership(self):
-        self.login_staff()
-        create_response = self.client.post(
-            reverse("seasons:membership-new"),
-            {
-                "player": self.player.id,
-                "season_team": self.dodgers.id,
-                "status": RosterStatus.ACTIVE,
-                "jersey_number": "12",
-                "is_primary": "on",
-                "is_active": "on",
-                "starts_on": "2026-04-01",
-                "ends_on": "",
-                "source": "manual",
-                "source_identifier": "",
-            },
-        )
-        membership = PlayerRosterMembership.objects.get(player=self.player, season_team=self.dodgers)
-        self.assertRedirects(create_response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
-        self.assertTrue(membership.is_primary)
-
-        response = self.client.post(
-            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
-            {
-                "action": "additional",
-                "season_team": self.expos.id,
-                "transfer_date": "2026-05-01",
-                "jersey_number": "8",
-                "source": "manual",
-                "source_identifier": "",
-            },
-        )
-        self.assertRedirects(response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
-        membership.refresh_from_db()
-        additional = PlayerRosterMembership.objects.get(player=self.player, season_team=self.expos)
-        self.assertTrue(membership.is_active)
-        self.assertTrue(membership.is_primary)
-        self.assertEqual(additional.status, RosterStatus.GUEST)
-        self.assertFalse(additional.is_primary)
-
-        response = self.client.post(
-            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
-            {
-                "action": "transfer",
-                "season_team": self.expos.id,
-                "transfer_date": "2026-06-01",
-                "jersey_number": "",
-                "source": "manual",
-                "source_identifier": "",
-            },
-        )
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "already has")
-
-        additional.delete()
-        response = self.client.post(
-            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
-            {
-                "action": "transfer",
-                "season_team": self.expos.id,
-                "transfer_date": "2026-06-01",
-                "jersey_number": "",
-                "source": "manual",
-                "source_identifier": "",
-            },
-        )
-        self.assertRedirects(response, reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
-        membership.refresh_from_db()
-        transferred = PlayerRosterMembership.objects.get(player=self.player, season_team=self.expos)
-        self.assertFalse(membership.is_active)
-        self.assertEqual(membership.status, RosterStatus.TRANSFERRED)
-        self.assertTrue(transferred.is_primary)
-
-    def test_transfer_rejects_cross_season_destination_tampering(self):
-        self.login_staff()
-        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-
-        response = self.client.post(
-            reverse("seasons:membership-transfer", kwargs={"membership_id": membership.id}),
-            {
-                "action": "transfer",
-                "season_team": self.mounties.id,
-                "transfer_date": "2026-06-01",
-                "source": "manual",
-                "source_identifier": "",
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        membership.refresh_from_db()
-        self.assertTrue(membership.is_active)
-        self.assertEqual(PlayerRosterMembership.objects.filter(player=self.player).count(), 1)
-
-    def test_player_history_and_invalid_filter_ids_render(self):
-        self.login_staff()
-        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-
-        response = self.client.get(reverse("seasons:player-history", kwargs={"player_id": self.player.id}))
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Dodgers")
-
-        response = self.client.get(reverse("seasons:membership-list") + "?season=bad&team=bad")
-        self.assertEqual(response.status_code, 200)
-
-    def test_membership_list_is_paginated_and_preserves_filters(self):
-        self.login_staff()
-        for index in range(55):
-            player = Player.objects.create(first_name=f"Player{index}", last_name="Paged")
-            create_membership(player=player, season_team=self.dodgers, is_primary=True)
-
-        response = self.client.get(reverse("seasons:membership-list") + f"?season={self.spring.id}&active=yes")
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Page 1 of 2")
-        self.assertContains(response, f"?season={self.spring.id}&amp;active=yes&amp;page=2")
-
-    def test_staff_can_create_edit_end_coach_assignment_without_account_side_effects(self):
-        original_password = self.coach.password
-        self.login_staff()
-
-        response = self.client.post(
-            reverse("seasons:coach-assignment-new"),
-            {
-                "user": self.coach.id,
-                "season_team": self.dodgers.id,
-                "assignment_role": CoachAssignmentRole.HEAD_COACH,
-                "is_primary": "on",
-                "is_active": "on",
-                "starts_on": "2026-04-01",
-                "ends_on": "",
-                "source": "manual",
-                "source_identifier": "",
-            },
-        )
-        assignment = CoachSeasonAssignment.objects.get(user=self.coach, season_team=self.dodgers)
-        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
-
-        response = self.client.post(
-            reverse("seasons:coach-assignment-edit", kwargs={"assignment_id": assignment.id}),
-            {
-                "user": self.regular.id,
-                "season_team": self.mounties.id,
-                "assignment_role": CoachAssignmentRole.EVALUATOR,
-                "is_primary": "on",
-                "is_active": "on",
-                "starts_on": "2026-04-01",
-                "ends_on": "",
-                "source": "manual",
-                "source_identifier": "",
-            },
-        )
-        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
-        assignment.refresh_from_db()
-        self.coach.refresh_from_db()
-        profile = get_or_create_account_profile(self.coach)
-        self.assertEqual(assignment.user, self.coach)
-        self.assertEqual(assignment.season_team, self.dodgers)
-        self.assertEqual(assignment.assignment_role, CoachAssignmentRole.EVALUATOR)
-        self.assertEqual(profile.role, AccountRole.COACH)
-        self.assertFalse(self.coach.is_staff)
-        self.assertFalse(self.coach.is_superuser)
-        self.assertEqual(self.coach.password, original_password)
-
-        response = self.client.post(
-            reverse("seasons:coach-assignment-end", kwargs={"assignment_id": assignment.id}),
-            {"ends_on": "2026-08-01", "confirm": "on"},
-        )
-        self.assertRedirects(response, reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
-        assignment.refresh_from_db()
-        self.assertFalse(assignment.is_active)
-        self.assertFalse(assignment.is_primary)
-        self.assertEqual(assignment.ends_on, date(2026, 8, 1))
-
-    def test_non_coach_user_cannot_be_assigned_as_coach(self):
-        self.login_staff()
-
-        response = self.client.post(
-            reverse("seasons:coach-assignment-new"),
-            {
-                "user": self.regular.id,
-                "season_team": self.dodgers.id,
-                "assignment_role": CoachAssignmentRole.HEAD_COACH,
-                "is_primary": "on",
-                "is_active": "on",
-                "starts_on": "",
-                "ends_on": "",
-                "source": "manual",
-                "source_identifier": "",
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertFalse(CoachSeasonAssignment.objects.filter(user=self.regular).exists())
-
-    def test_coach_history_requires_coach_profile(self):
-        self.login_staff()
-
-        response = self.client.get(reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}))
-        self.assertEqual(response.status_code, 200)
-
-        response = self.client.get(reverse("seasons:coach-history", kwargs={"user_id": self.regular.id}))
-        self.assertEqual(response.status_code, 404)
-
-    def test_submitted_evaluation_snapshot_survives_team_edit_and_player_transfer(self):
-        setup = ensure_default_coach_assessment_setup()
-        membership = create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
-        create_assignment(
-            user=self.coach,
-            season_team=self.dodgers,
-            assignment_role=CoachAssignmentRole.HEAD_COACH,
-            is_primary=True,
-        )
-        cycle = EvaluationCycle.objects.create(
-            name="2026 Spring Evaluation",
-            cycle_type="Coach Assessment",
-            season=self.spring,
-            coach_assessment_question_set=setup.question_set,
-        )
-        responses = {
-            question: 4
-            for question in setup.question_set.questions.filter(
-                response_type=RESPONSE_TYPE_RATING_1_5,
-                is_required=True,
-                is_active=True,
-            )
-        }
-        text_question = setup.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
-        responses[text_question] = "Snapshot should not move."
-
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=cycle,
-            evaluator=self.coach,
-            player_roster_membership=membership,
-            responses=responses,
-        )
-        observation = submit_observation(result.observation, actor=self.coach)
-
-        update_season_team(self.dodgers, name="Renamed Dodgers", division="Renamed 13U")
-        transfer_player(player=self.player, from_membership=membership, to_season_team=self.expos, transfer_date=date(2026, 6, 1))
-        observation.refresh_from_db()
-
-        self.assertEqual(observation.season_name_snapshot, "2026 Spring")
-        self.assertEqual(observation.player_team_name_snapshot, "Dodgers")
-        self.assertEqual(observation.player_division_snapshot, "13U")
-        self.assertEqual(observation.evaluator_team_name_snapshot, "Dodgers")
diff --git a/seasons/tests/__init__.py b/seasons/tests/__init__.py
new file mode 100644
index 0000000..e69de29
diff --git a/seasons/tests/helpers.py b/seasons/tests/helpers.py
new file mode 100644
index 0000000..d57711d
--- /dev/null
+++ b/seasons/tests/helpers.py
@@ -0,0 +1,112 @@
+from datetime import date
+
+from django.apps import apps
+from django.contrib import admin
+from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+from django.db import transaction
+from django.test import TestCase
+from django.urls import reverse
+
+from accounts.models import AccountRole
+from accounts.services.profile_service import (
+    get_or_create_account_profile,
+    set_account_role,
+)
+from analytics.models import (
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    EvaluationCycle,
+)
+from analytics.services.observation_service import (
+    create_coach_assessment_observation,
+    submit_observation,
+)
+from analytics.services.question_service import ensure_default_coach_assessment_setup
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
+from seasons.services.season_service import (
+    create_season,
+    deactivate_season,
+    get_current_season,
+    set_current_season,
+)
+from seasons.services.team_service import get_or_create_season_team, update_season_team
+
+User = get_user_model()
+
+__all__ = (
+    "AccountRole",
+    "CoachAssignmentRole",
+    "CoachSeasonAssignment",
+    "EvaluationCycle",
+    "Player",
+    "PlayerRosterMembership",
+    "RESPONSE_TYPE_RATING_1_5",
+    "RESPONSE_TYPE_TEXT",
+    "RosterStatus",
+    "Season",
+    "SeasonTeam",
+    "TestCase",
+    "User",
+    "ValidationError",
+    "admin",
+    "apps",
+    "assignments_for_team",
+    "assignments_for_user",
+    "create_assignment",
+    "create_coach_assessment_observation",
+    "create_membership",
+    "create_season",
+    "current_team_division",
+    "date",
+    "deactivate_assignment",
+    "deactivate_membership",
+    "deactivate_season",
+    "ensure_default_coach_assessment_setup",
+    "get_current_membership",
+    "get_current_season",
+    "get_or_create_account_profile",
+    "get_or_create_season_team",
+    "get_primary_assignment",
+    "get_primary_membership",
+    "memberships_for_player",
+    "reverse",
+    "set_account_role",
+    "set_current_season",
+    "set_primary_assignment",
+    "submit_observation",
+    "sync_player_current_team_fields",
+    "transaction",
+    "transfer_player",
+    "update_assignment",
+    "update_membership",
+    "update_season_team",
+)
diff --git a/seasons/tests/test_admin.py b/seasons/tests/test_admin.py
new file mode 100644
index 0000000..30e49c2
--- /dev/null
+++ b/seasons/tests/test_admin.py
@@ -0,0 +1,31 @@
+from seasons.tests.helpers import (
+    CoachSeasonAssignment,
+    PlayerRosterMembership,
+    Season,
+    SeasonTeam,
+    TestCase,
+    admin,
+)
+
+
+class SeasonsAdminTests(TestCase):
+    def test_models_registered_in_admin(self):
+        for model in [
+            Season,
+            SeasonTeam,
+            PlayerRosterMembership,
+            CoachSeasonAssignment,
+        ]:
+            self.assertIn(model, admin.site._registry)
+
+    def test_admin_configuration_is_searchable_and_readonly_timestamps(self):
+        for model in [
+            Season,
+            SeasonTeam,
+            PlayerRosterMembership,
+            CoachSeasonAssignment,
+        ]:
+            model_admin = admin.site._registry[model]
+            self.assertIn("created_at", model_admin.readonly_fields)
+            self.assertIn("updated_at", model_admin.readonly_fields)
+            self.assertTrue(model_admin.search_fields)
diff --git a/seasons/tests/test_assignments.py b/seasons/tests/test_assignments.py
new file mode 100644
index 0000000..45f74e3
--- /dev/null
+++ b/seasons/tests/test_assignments.py
@@ -0,0 +1,175 @@
+from seasons.tests.helpers import (
+    AccountRole,
+    CoachAssignmentRole,
+    CoachSeasonAssignment,
+    TestCase,
+    User,
+    ValidationError,
+    assignments_for_team,
+    assignments_for_user,
+    create_assignment,
+    create_season,
+    date,
+    deactivate_assignment,
+    get_or_create_account_profile,
+    get_or_create_season_team,
+    get_primary_assignment,
+    set_account_role,
+    update_assignment,
+)
+
+
+class CoachAssignmentTests(TestCase):
+    def setUp(self):
+        self.spring = create_season(key="2026-spring", name="2026 Spring")
+        self.dodgers, _ = get_or_create_season_team(
+            season=self.spring, name="Dodgers", division="13U"
+        )
+        self.expos, _ = get_or_create_season_team(
+            season=self.spring, name="Expos", division="13U"
+        )
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
+        self.assertEqual(
+            assignments_for_user(self.coach, self.spring).first(), assignment
+        )
+        self.assertEqual(assignments_for_team(self.dodgers).first(), assignment)
+        self.assertEqual(get_primary_assignment(self.coach, self.spring), assignment)
+
+    def test_multiple_assignments_and_multiple_coaches_allowed(self):
+        other = User.objects.create_user(username="other", password="testpass")
+
+        first = create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+        )
+        second = create_assignment(
+            user=self.coach,
+            season_team=self.expos,
+            assignment_role=CoachAssignmentRole.EVALUATOR,
+        )
+        third = create_assignment(
+            user=other,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.ASSISTANT_COACH,
+        )
+
+        self.assertEqual(
+            {first, second}, set(assignments_for_user(self.coach, self.spring))
+        )
+        self.assertIn(third, list(assignments_for_team(self.dodgers)))
+
+    def test_duplicate_active_user_team_role_rejected(self):
+        create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+        )
+
+        with self.assertRaises(ValidationError):
+            create_assignment(
+                user=self.coach,
+                season_team=self.dodgers,
+                assignment_role=CoachAssignmentRole.HEAD_COACH,
+            )
+
+    def test_only_one_active_primary_assignment_per_user_season(self):
+        first = create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+            is_primary=True,
+        )
+        second = create_assignment(
+            user=self.coach,
+            season_team=self.expos,
+            assignment_role=CoachAssignmentRole.EVALUATOR,
+            is_primary=True,
+        )
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
+        create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+            is_primary=True,
+        )
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
+        create_assignment(
+            user=self.coach,
+            season_team=self.dodgers,
+            assignment_role=CoachAssignmentRole.HEAD_COACH,
+        )
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
diff --git a/seasons/tests/test_memberships.py b/seasons/tests/test_memberships.py
new file mode 100644
index 0000000..60642a1
--- /dev/null
+++ b/seasons/tests/test_memberships.py
@@ -0,0 +1,174 @@
+from seasons.tests.helpers import (
+    Player,
+    PlayerRosterMembership,
+    RosterStatus,
+    TestCase,
+    ValidationError,
+    create_membership,
+    create_season,
+    current_team_division,
+    date,
+    deactivate_membership,
+    get_current_membership,
+    get_or_create_season_team,
+    get_primary_membership,
+    memberships_for_player,
+    sync_player_current_team_fields,
+    transfer_player,
+    update_membership,
+)
+
+
+class PlayerMembershipTests(TestCase):
+    def setUp(self):
+        self.spring = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        self.next_spring = create_season(key="2027-spring", name="2027 Spring")
+        self.dodgers, _ = get_or_create_season_team(
+            season=self.spring, name="Dodgers", division="13U"
+        )
+        self.expos, _ = get_or_create_season_team(
+            season=self.spring, name="Expos", division="13U"
+        )
+        self.mounties, _ = get_or_create_season_team(
+            season=self.next_spring, name="Mounties", division="15U"
+        )
+        self.player = Player.objects.create(
+            first_name="Alex", last_name="Player", team_name="Legacy", division="Legacy"
+        )
+
+    def test_player_may_join_one_team_and_different_seasons(self):
+        first = create_membership(
+            player=self.player, season_team=self.dodgers, is_primary=True
+        )
+        second = create_membership(
+            player=self.player, season_team=self.mounties, is_primary=True
+        )
+
+        self.assertEqual(first.player, self.player)
+        self.assertEqual(second.player, self.player)
+        self.assertEqual(memberships_for_player(self.player).count(), 2)
+
+    def test_multiple_memberships_in_one_season_and_non_primary_concurrent_allowed(
+        self,
+    ):
+        primary = create_membership(
+            player=self.player, season_team=self.dodgers, is_primary=True
+        )
+        guest = create_membership(
+            player=self.player,
+            season_team=self.expos,
+            status=RosterStatus.GUEST,
+            is_primary=False,
+        )
+
+        self.assertTrue(primary.is_primary)
+        self.assertFalse(guest.is_primary)
+        self.assertEqual(memberships_for_player(self.player, self.spring).count(), 2)
+
+    def test_only_one_active_primary_membership_per_player_season(self):
+        first = create_membership(
+            player=self.player, season_team=self.dodgers, is_primary=True
+        )
+        second = create_membership(
+            player=self.player, season_team=self.expos, is_primary=True
+        )
+
+        first.refresh_from_db()
+        second.refresh_from_db()
+        self.assertFalse(first.is_primary)
+        self.assertTrue(second.is_primary)
+        self.assertEqual(get_primary_membership(self.player, self.spring), second)
+
+    def test_update_membership_can_unset_primary(self):
+        membership = create_membership(
+            player=self.player, season_team=self.dodgers, is_primary=True
+        )
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
+            PlayerRosterMembership.objects.create(
+                player=self.player, season_team=self.expos, is_primary=True
+            )
+
+    def test_transfer_creates_new_membership_and_preserves_history(self):
+        old = create_membership(
+            player=self.player, season_team=self.dodgers, is_primary=True
+        )
+
+        new = transfer_player(
+            player=self.player,
+            to_season_team=self.expos,
+            transfer_date=date(2026, 6, 1),
+        )
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
+        create_membership(
+            player=self.player, season_team=self.dodgers, is_primary=False
+        )
+        primary = create_membership(
+            player=self.player, season_team=self.expos, is_primary=True
+        )
+
+        self.assertEqual(get_current_membership(self.player, self.spring), primary)
+        self.assertEqual(
+            current_team_division(self.player, self.spring), ("Expos", "13U")
+        )
+
+    def test_compatibility_sync_is_explicit_and_can_clear_when_requested(self):
+        create_membership(
+            player=self.player,
+            season_team=self.dodgers,
+            is_primary=True,
+            sync_player_fields=False,
+        )
+        self.player.refresh_from_db()
+
+        self.assertEqual(self.player.team_name, "Legacy")
+        sync_player_current_team_fields(self.player, self.spring)
+        self.player.refresh_from_db()
+        self.assertEqual(self.player.team_name, "Dodgers")
+        self.assertEqual(self.player.division, "13U")
+
+        deactivate_membership(
+            get_primary_membership(self.player, self.spring), sync_player_fields=False
+        )
+        sync_player_current_team_fields(
+            self.player, self.spring, clear_when_missing=False
+        )
+        self.player.refresh_from_db()
+        self.assertEqual(self.player.team_name, "Dodgers")
+
+        sync_player_current_team_fields(
+            self.player, self.spring, clear_when_missing=True
+        )
+        self.player.refresh_from_db()
+        self.assertEqual(self.player.team_name, "")
+        self.assertEqual(self.player.division, "")
diff --git a/seasons/tests/test_models.py b/seasons/tests/test_models.py
new file mode 100644
index 0000000..31eafb5
--- /dev/null
+++ b/seasons/tests/test_models.py
@@ -0,0 +1,166 @@
+from seasons.tests.helpers import (
+    Season,
+    TestCase,
+    ValidationError,
+    apps,
+    create_season,
+    date,
+    deactivate_season,
+    get_current_season,
+    get_or_create_season_team,
+    set_current_season,
+    transaction,
+)
+
+
+class SeasonModelServiceTests(TestCase):
+    def test_seasons_app_is_installed(self):
+        self.assertTrue(apps.is_installed("seasons"))
+
+    def test_create_valid_season_normalizes_key(self):
+        season = create_season(
+            key=" 2026 Spring ", name=" 2026 Spring ", starts_on=date(2026, 4, 1)
+        )
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
+            create_season(
+                key="2026-spring",
+                name="2026 Spring",
+                starts_on=date(2026, 8, 1),
+                ends_on=date(2026, 4, 1),
+            )
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
+                Season.objects.create(
+                    key="2026-summer", name="2026 Summer", is_current=True
+                )
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
+        team, created = get_or_create_season_team(
+            season=self.spring, name="  Dodgers  ", division=" 13U   House "
+        )
+
+        self.assertTrue(created)
+        self.assertEqual(team.normalized_name, "dodgers")
+        self.assertEqual(team.normalized_division, "13u house")
+
+    def test_same_normalized_team_division_reused(self):
+        first, created_first = get_or_create_season_team(
+            season=self.spring, name="Dodgers", division="13U"
+        )
+        second, created_second = get_or_create_season_team(
+            season=self.spring, name=" dodgers ", division=" 13u "
+        )
+
+        self.assertTrue(created_first)
+        self.assertFalse(created_second)
+        self.assertEqual(first, second)
+
+    def test_same_team_name_in_different_seasons_allowed(self):
+        first, _ = get_or_create_season_team(
+            season=self.spring, name="Dodgers", division="13U"
+        )
+        second, _ = get_or_create_season_team(
+            season=self.next_spring, name="Dodgers", division="13U"
+        )
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
+        blank_one, _ = get_or_create_season_team(
+            season=self.spring, name="Expos", division="13U"
+        )
+        blank_two, _ = get_or_create_season_team(
+            season=self.spring, name="Mounties", division="13U"
+        )
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
diff --git a/seasons/tests/test_operations_views.py b/seasons/tests/test_operations_views.py
new file mode 100644
index 0000000..5fd9035
--- /dev/null
+++ b/seasons/tests/test_operations_views.py
@@ -0,0 +1,493 @@
+from seasons.tests.helpers import (
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    AccountRole,
+    CoachAssignmentRole,
+    CoachSeasonAssignment,
+    EvaluationCycle,
+    Player,
+    PlayerRosterMembership,
+    RosterStatus,
+    Season,
+    SeasonTeam,
+    TestCase,
+    User,
+    create_assignment,
+    create_coach_assessment_observation,
+    create_membership,
+    create_season,
+    date,
+    ensure_default_coach_assessment_setup,
+    get_or_create_account_profile,
+    get_or_create_season_team,
+    reverse,
+    set_account_role,
+    submit_observation,
+    transfer_player,
+    update_season_team,
+)
+
+
+class SeasonOperationsUITests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
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
+        self.spring = create_season(
+            key="2026-spring",
+            name="2026 Spring",
+            starts_on=date(2026, 4, 1),
+            is_current=True,
+        )
+        self.summer = create_season(key="2026-summer", name="2026 Summer")
+        self.dodgers, _ = get_or_create_season_team(
+            season=self.spring, name="Dodgers", division="13U"
+        )
+        self.expos, _ = get_or_create_season_team(
+            season=self.spring, name="Expos", division="13U"
+        )
+        self.mounties, _ = get_or_create_season_team(
+            season=self.summer, name="Mounties", division="15U"
+        )
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
+        self.assertRedirects(
+            response, reverse("seasons:season-detail", kwargs={"season_id": season.id})
+        )
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
+        self.assertRedirects(
+            response, reverse("seasons:season-detail", kwargs={"season_id": season.id})
+        )
+        season.refresh_from_db()
+        self.assertEqual(season.name, "2027 Spring Updated")
+
+        self.client.post(
+            reverse("seasons:season-set-current", kwargs={"season_id": season.id}),
+            {"confirm": "on"},
+        )
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
+    def test_cannot_create_team_from_inactive_season_shortcut(self):
+        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
+        self.login_staff()
+
+        response = self.client.get(
+            reverse("seasons:season-team-new", kwargs={"season_id": inactive.id})
+        )
+
+        self.assertEqual(response.status_code, 404)
+
+    def test_staff_can_manage_membership_history_transfer_and_additional_membership(
+        self,
+    ):
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
+        membership = PlayerRosterMembership.objects.get(
+            player=self.player, season_team=self.dodgers
+        )
+        self.assertRedirects(
+            create_response,
+            reverse("seasons:player-history", kwargs={"player_id": self.player.id}),
+        )
+        self.assertTrue(membership.is_primary)
+
+        response = self.client.post(
+            reverse(
+                "seasons:membership-transfer", kwargs={"membership_id": membership.id}
+            ),
+            {
+                "action": "additional",
+                "season_team": self.expos.id,
+                "transfer_date": "2026-05-01",
+                "jersey_number": "8",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+        self.assertRedirects(
+            response,
+            reverse("seasons:player-history", kwargs={"player_id": self.player.id}),
+        )
+        membership.refresh_from_db()
+        additional = PlayerRosterMembership.objects.get(
+            player=self.player, season_team=self.expos
+        )
+        self.assertTrue(membership.is_active)
+        self.assertTrue(membership.is_primary)
+        self.assertEqual(additional.status, RosterStatus.GUEST)
+        self.assertFalse(additional.is_primary)
+
+        response = self.client.post(
+            reverse(
+                "seasons:membership-transfer", kwargs={"membership_id": membership.id}
+            ),
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
+            reverse(
+                "seasons:membership-transfer", kwargs={"membership_id": membership.id}
+            ),
+            {
+                "action": "transfer",
+                "season_team": self.expos.id,
+                "transfer_date": "2026-06-01",
+                "jersey_number": "",
+                "source": "manual",
+                "source_identifier": "",
+            },
+        )
+        self.assertRedirects(
+            response,
+            reverse("seasons:player-history", kwargs={"player_id": self.player.id}),
+        )
+        membership.refresh_from_db()
+        transferred = PlayerRosterMembership.objects.get(
+            player=self.player, season_team=self.expos
+        )
+        self.assertFalse(membership.is_active)
+        self.assertEqual(membership.status, RosterStatus.TRANSFERRED)
+        self.assertTrue(transferred.is_primary)
+
+    def test_transfer_rejects_cross_season_destination_tampering(self):
+        self.login_staff()
+        membership = create_membership(
+            player=self.player, season_team=self.dodgers, is_primary=True
+        )
+
+        response = self.client.post(
+            reverse(
+                "seasons:membership-transfer", kwargs={"membership_id": membership.id}
+            ),
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
+        self.assertEqual(
+            PlayerRosterMembership.objects.filter(player=self.player).count(), 1
+        )
+
+    def test_player_history_and_invalid_filter_ids_render(self):
+        self.login_staff()
+        create_membership(player=self.player, season_team=self.dodgers, is_primary=True)
+
+        response = self.client.get(
+            reverse("seasons:player-history", kwargs={"player_id": self.player.id})
+        )
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Dodgers")
+
+        response = self.client.get(
+            reverse("seasons:membership-list") + "?season=bad&team=bad"
+        )
+        self.assertEqual(response.status_code, 200)
+
+    def test_membership_list_is_paginated_and_preserves_filters(self):
+        self.login_staff()
+        for index in range(55):
+            player = Player.objects.create(
+                first_name=f"Player{index}", last_name="Paged"
+            )
+            create_membership(player=player, season_team=self.dodgers, is_primary=True)
+
+        response = self.client.get(
+            reverse("seasons:membership-list") + f"?season={self.spring.id}&active=yes"
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Page 1 of 2")
+        self.assertContains(
+            response, f"?season={self.spring.id}&amp;active=yes&amp;page=2"
+        )
+
+    def test_staff_can_create_edit_end_coach_assignment_without_account_side_effects(
+        self,
+    ):
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
+        assignment = CoachSeasonAssignment.objects.get(
+            user=self.coach, season_team=self.dodgers
+        )
+        self.assertRedirects(
+            response,
+            reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}),
+        )
+
+        response = self.client.post(
+            reverse(
+                "seasons:coach-assignment-edit", kwargs={"assignment_id": assignment.id}
+            ),
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
+        self.assertRedirects(
+            response,
+            reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}),
+        )
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
+            reverse(
+                "seasons:coach-assignment-end", kwargs={"assignment_id": assignment.id}
+            ),
+            {"ends_on": "2026-08-01", "confirm": "on"},
+        )
+        self.assertRedirects(
+            response,
+            reverse("seasons:coach-history", kwargs={"user_id": self.coach.id}),
+        )
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
+        self.assertFalse(
+            CoachSeasonAssignment.objects.filter(user=self.regular).exists()
+        )
+
+    def test_coach_history_requires_coach_profile(self):
+        self.login_staff()
+
+        response = self.client.get(
+            reverse("seasons:coach-history", kwargs={"user_id": self.coach.id})
+        )
+        self.assertEqual(response.status_code, 200)
+
+        response = self.client.get(
+            reverse("seasons:coach-history", kwargs={"user_id": self.regular.id})
+        )
+        self.assertEqual(response.status_code, 404)
+
+    def test_submitted_evaluation_snapshot_survives_team_edit_and_player_transfer(self):
+        setup = ensure_default_coach_assessment_setup()
+        membership = create_membership(
+            player=self.player, season_team=self.dodgers, is_primary=True
+        )
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
+        text_question = setup.question_set.questions.get(
+            response_type=RESPONSE_TYPE_TEXT
+        )
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
+        transfer_player(
+            player=self.player,
+            from_membership=membership,
+            to_season_team=self.expos,
+            transfer_date=date(2026, 6, 1),
+        )
+        observation.refresh_from_db()
+
+        self.assertEqual(observation.season_name_snapshot, "2026 Spring")
+        self.assertEqual(observation.player_team_name_snapshot, "Dodgers")
+        self.assertEqual(observation.player_division_snapshot, "13U")
+        self.assertEqual(observation.evaluator_team_name_snapshot, "Dodgers")
```
