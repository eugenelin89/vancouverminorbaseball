# Prompt 86 - Accounts

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

`9fcb412` - Split account tests by responsibility

## Old Test Structure

```text
accounts/tests.py
```

## New Test Structure

```text
accounts/tests/
    __init__.py
    helpers.py
    test_account_operations.py
    test_account_services.py
    test_authentication.py
    test_coach_import.py
    test_player_links.py
    test_profiles.py
```

## Test Counts

Before split:

```text
DJANGO_SECRET_KEY=test python manage.py test accounts
Found 194 test(s).
Ran 194 tests successfully.
```

After split:

```text
DJANGO_SECRET_KEY=test python manage.py test accounts
Found 194 test(s).
Ran 194 tests successfully.
```

Full suite remained at 458 tests.

## Shared Helper Changes

The original shared imports and `User = get_user_model()` setup moved to `accounts/tests/helpers.py`. Test files import only the helper names they use so Ruff `F` checks stay clean.

## Discovery Findings

Django discovers the account test package through `python manage.py test accounts`. Targeted module commands also work, including:

```text
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_coach_import
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_account_operations
```

## Patch-Target Findings

No patch targets required changes. No production import paths were changed.

## Verification

Focused verification:

```text
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_coach_import
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_account_operations
DJANGO_SECRET_KEY=test python manage.py test accounts
DJANGO_SECRET_KEY=test python manage.py test accounts players seasons analytics
pre-commit run --files accounts/tests/__init__.py accounts/tests/helpers.py accounts/tests/test_profiles.py accounts/tests/test_account_operations.py accounts/tests/test_player_links.py accounts/tests/test_account_services.py accounts/tests/test_authentication.py accounts/tests/test_coach_import.py docs/prompts/prompt_86_accounts.md
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

CONTINUE. Accounts is split; analytics remains a large test module and should be split in the next loop.

## Commit Diff

```diff
commit 9fcb41213aa05e17f57dfd75155d17bd55a2318c
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 11:59:53 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 11:59:53 2026 -0700

    Split account tests by responsibility
---
 accounts/tests.py                         | 2786 -----------------------------
 accounts/tests/__init__.py                |    0
 accounts/tests/helpers.py                 |  227 +++
 accounts/tests/test_account_operations.py | 1622 +++++++++++++++++
 accounts/tests/test_account_services.py   |  357 ++++
 accounts/tests/test_authentication.py     |  382 ++++
 accounts/tests/test_coach_import.py       |  455 +++++
 accounts/tests/test_player_links.py       |  383 ++++
 accounts/tests/test_profiles.py           |  154 ++
 9 files changed, 3580 insertions(+), 2786 deletions(-)

diff --git a/accounts/tests.py b/accounts/tests.py
deleted file mode 100644
index ad535e4..0000000
--- a/accounts/tests.py
+++ /dev/null
@@ -1,2786 +0,0 @@
-from django.contrib import admin
-from django.contrib.messages import get_messages
-from django.contrib.auth import get_user_model
-from django.conf import settings
-from django.core.exceptions import ValidationError
-from django.core.files.uploadedfile import SimpleUploadedFile
-from django.db import IntegrityError, transaction
-from django.test import TestCase
-from django.urls import reverse
-from django.contrib.auth import SESSION_KEY
-
-from accounts.models import AccountProfile, AccountRole, UserPlayerLink, UserPlayerRelationship
-from accounts.services.account_operations_service import (
-    activate_account,
-    bulk_account_operation,
-    create_account_only,
-    create_player_account,
-    create_user_player_link,
-    deactivate_account,
-    deactivate_user_player_link,
-    get_account_detail,
-    get_account_list,
-    get_account_operations_dashboard,
-    reactivate_user_player_link,
-    reset_account_password,
-    set_primary_user_player_link,
-    update_account,
-)
-from accounts.services.account_query_service import AccountListFilters, count_players_without_self_link, filter_account_users
-from accounts.services.auth_redirect_service import (
-    ACCOUNT_LOGIN_PATH,
-    ACCOUNT_LOGOUT_PATH,
-    ACCOUNT_PASSWORD_PATH,
-    ACCOUNT_PROFILE_PATH,
-    ANALYTICS_HOME_PATH,
-    is_password_change_allowed_path,
-    landing_url_for_user,
-    should_force_password_change,
-)
-from accounts.services.coach_import_service import (
-    RESULT_CONFLICT,
-    RESULT_CREATED,
-    RESULT_REUSED,
-    commit_coach_import,
-    preview_coach_import,
-)
-from accounts.services.email_service import emails_equal, find_existing_email_user, normalize_email
-from accounts.services.permissions import (
-    can_access_account_operations,
-    can_change_account_role,
-    can_manage_accounts,
-    can_manage_privileged_accounts,
-    can_submit_evaluations,
-    can_view_account_detail,
-    can_view_account_list,
-    can_view_account_operations_dashboard,
-    can_view_account_profile,
-)
-from accounts.services.link_service import (
-    activate_link,
-    deactivate_link,
-    get_players_for_user,
-    get_primary_player,
-    get_primary_user,
-    get_users_for_player,
-    is_player_self,
-    link_user_to_player,
-    set_primary_self_link,
-    unlink_user_from_player,
-)
-from accounts.services.password_service import (
-    generate_birthdate_password,
-    generate_random_temporary_password,
-    mark_password_change_required,
-    set_temporary_password,
-)
-from accounts.services.provisioning_service import (
-    STATUS_ALREADY_LINKED,
-    STATUS_CONFLICT,
-    STATUS_CREATED,
-    STATUS_SKIPPED,
-    ProvisioningOptions,
-    ProvisioningSummary,
-    provision_accounts_for_import,
-    provision_player_account,
-)
-from accounts.services.profile_service import get_account_role, get_or_create_account_profile, set_account_role
-from accounts.services.role_service import default_role_for_user, role_for_user, role_label, validate_role
-from accounts.services.username_service import (
-    base_username_for_player,
-    base_username_for_person,
-    normalize_username_part,
-    validate_available_username,
-    validate_available_username_for_user,
-    username_for_player,
-    username_for_person,
-)
-from analytics.services.permissions import can_submit_coach_assessment
-from players.models import Player, PlayerImportBatch
-from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, SeasonTeam
-from seasons.services.season_service import create_season
-
-
-User = get_user_model()
-
-
-class AccountProfileServiceTests(TestCase):
-    def test_get_or_create_account_profile_creates_guest_profile_for_regular_user(self):
-        user = User.objects.create_user(username="player", password="testpass")
-
-        profile = get_or_create_account_profile(user)
-        second = get_or_create_account_profile(user)
-
-        self.assertEqual(profile, second)
-        self.assertEqual(profile.role, AccountRole.GUEST_EVALUATOR)
-        self.assertFalse(profile.must_change_password)
-        self.assertFalse(profile.created_from_import)
-        self.assertIsNone(profile.import_batch)
-
-    def test_default_role_uses_django_admin_flags_for_new_profiles(self):
-        staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        admin_user = User.objects.create_superuser(username="admin", password="testpass")
-
-        self.assertEqual(get_or_create_account_profile(staff).role, AccountRole.STAFF)
-        self.assertEqual(get_or_create_account_profile(admin_user).role, AccountRole.ADMIN)
-
-    def test_role_for_user_falls_back_without_profile(self):
-        staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        regular = User.objects.create_user(username="regular", password="testpass")
-
-        self.assertEqual(role_for_user(staff), AccountRole.STAFF)
-        self.assertEqual(role_for_user(regular), AccountRole.GUEST_EVALUATOR)
-
-    def test_set_account_role_changes_only_profile_role(self):
-        user = User.objects.create_user(username="coach", password="testpass")
-
-        profile = set_account_role(user, AccountRole.COACH)
-        user.refresh_from_db()
-
-        self.assertEqual(profile.role, AccountRole.COACH)
-        self.assertEqual(get_account_role(user), AccountRole.COACH)
-        self.assertFalse(user.is_staff)
-        self.assertFalse(user.is_superuser)
-
-    def test_role_validation_and_labels(self):
-        self.assertEqual(validate_role(AccountRole.PLAYER), AccountRole.PLAYER)
-        self.assertEqual(role_label(AccountRole.PARENT), "Parent")
-
-        with self.assertRaises(ValidationError):
-            validate_role("unsupported")
-
-    def test_profile_creation_requires_authenticated_user(self):
-        with self.assertRaises(ValidationError):
-            get_or_create_account_profile(None)
-
-
-class AccountPermissionTests(TestCase):
-    def setUp(self):
-        self.user = User.objects.create_user(username="user", password="testpass")
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.superuser = User.objects.create_superuser(username="admin", password="testpass")
-        self.profile = get_or_create_account_profile(self.user)
-
-    def test_staff_admin_permissions_use_django_flags(self):
-        self.assertFalse(can_manage_accounts(self.user))
-        self.assertFalse(can_change_account_role(self.user))
-        self.assertTrue(can_manage_accounts(self.staff))
-        self.assertTrue(can_change_account_role(self.staff))
-
-    def test_account_operations_permissions_use_django_staff_flags(self):
-        self.profile.role = AccountRole.STAFF
-        self.profile.save(update_fields=["role", "updated_at"])
-
-        self.assertFalse(can_access_account_operations(self.user))
-        self.assertFalse(can_view_account_operations_dashboard(self.user))
-        self.assertFalse(can_view_account_list(self.user))
-        self.assertFalse(can_view_account_detail(self.user, self.staff))
-        self.assertTrue(can_access_account_operations(self.staff))
-        self.assertTrue(can_view_account_operations_dashboard(self.staff))
-        self.assertTrue(can_view_account_list(self.staff))
-        self.assertTrue(can_view_account_detail(self.staff, self.user))
-        self.assertTrue(can_access_account_operations(self.superuser))
-
-    def test_coach_role_does_not_grant_account_operations_access(self):
-        self.profile.role = AccountRole.COACH
-        self.profile.save(update_fields=["role", "updated_at"])
-
-        self.assertFalse(self.user.is_staff)
-        self.assertFalse(self.user.is_superuser)
-        self.assertFalse(can_access_account_operations(self.user))
-
-    def test_privileged_account_management_is_superuser_only(self):
-        self.assertFalse(can_manage_privileged_accounts(self.user))
-        self.assertFalse(can_manage_privileged_accounts(self.staff))
-        self.assertTrue(can_manage_privileged_accounts(self.superuser))
-
-    def test_regular_user_can_view_own_profile_but_not_manage_accounts(self):
-        other = User.objects.create_user(username="other", password="testpass")
-
-        self.assertTrue(can_view_account_profile(self.user, self.profile))
-        self.assertFalse(can_view_account_profile(other, self.profile))
-        self.assertTrue(can_view_account_profile(self.staff, self.profile))
-
-    def test_any_authenticated_user_can_submit_evaluations(self):
-        self.assertTrue(can_submit_evaluations(self.user))
-        self.assertFalse(can_submit_evaluations(None))
-
-
-class AccountAdminTests(TestCase):
-    def test_account_profile_registered_in_admin(self):
-        self.assertIn(AccountProfile, admin.site._registry)
-
-    def test_user_player_link_registered_in_admin(self):
-        self.assertIn(UserPlayerLink, admin.site._registry)
-        link_admin = admin.site._registry[UserPlayerLink]
-
-        self.assertEqual(link_admin.exclude, ("metadata",))
-        self.assertIn("user", link_admin.list_display)
-        self.assertIn("player", link_admin.list_display)
-        self.assertIn("relationship", link_admin.list_display)
-        self.assertIn("created_at", link_admin.readonly_fields)
-        self.assertIn("updated_at", link_admin.readonly_fields)
-
-
-class AccountOperationsServiceTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.coach = User.objects.create_user(
-            username="coach.one",
-            password="testpass",
-            first_name="Coach",
-            last_name="One",
-            email="coach@example.com",
-        )
-        self.player_user = User.objects.create_user(
-            username="alex.player",
-            password="testpass",
-            first_name="Alex",
-            last_name="Player",
-            email="alex@example.com",
-        )
-        self.inactive_user = User.objects.create_user(username="inactive", password="testpass", is_active=False)
-        self.import_batch = PlayerImportBatch.objects.create(
-            source="manual_staff_csv",
-            original_filename="players.csv",
-            uploaded_by=self.staff,
-        )
-        set_account_role(self.coach, AccountRole.COACH)
-        player_profile = set_account_role(self.player_user, AccountRole.PLAYER)
-        player_profile.created_from_import = True
-        player_profile.import_batch = self.import_batch
-        player_profile.must_change_password = True
-        player_profile.save(
-            update_fields=["created_from_import", "import_batch", "must_change_password", "updated_at"]
-        )
-        get_or_create_account_profile(self.inactive_user)
-        self.player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")
-        self.unlinked_player = Player.objects.create(first_name="No", last_name="Account")
-        link_user_to_player(
-            self.player_user,
-            self.player,
-            relationship=UserPlayerRelationship.SELF,
-            created_from_import=True,
-            import_batch=self.import_batch,
-        )
-
-    def usernames_for_filters(self, **kwargs):
-        return [user.username for user in filter_account_users(AccountListFilters(**kwargs))]
-
-    def test_account_query_filters_by_search_text(self):
-        self.assertEqual(self.usernames_for_filters(search="coach@example.com"), ["coach.one"])
-        self.assertEqual(self.usernames_for_filters(search="Alex"), ["alex.player"])
-
-    def test_account_query_filters_by_role(self):
-        self.assertEqual(self.usernames_for_filters(role=AccountRole.COACH), ["coach.one"])
-        self.assertEqual(self.usernames_for_filters(role=AccountRole.PLAYER), ["alex.player"])
-
-    def test_account_query_filters_by_active_status(self):
-        self.assertEqual(self.usernames_for_filters(active_status="no"), ["inactive"])
-
-    def test_account_query_filters_by_staff_and_superuser_status(self):
-        admin_user = User.objects.create_superuser(username="admin", password="testpass")
-        get_or_create_account_profile(admin_user)
-
-        self.assertEqual(self.usernames_for_filters(staff_status="yes"), ["admin", "staff"])
-        self.assertEqual(self.usernames_for_filters(superuser_status="yes"), ["admin"])
-
-    def test_account_query_filters_by_imported_and_password_status(self):
-        self.assertEqual(self.usernames_for_filters(imported_status="yes"), ["alex.player"])
-        self.assertEqual(self.usernames_for_filters(must_change_password="yes"), ["alex.player"])
-
-    def test_account_query_filters_by_linked_status(self):
-        self.assertEqual(self.usernames_for_filters(linked_status="linked"), ["alex.player"])
-        self.assertCountEqual(
-            self.usernames_for_filters(linked_status="unlinked"),
-            ["coach.one", "inactive", "staff"],
-        )
-
-    def test_dashboard_counts_include_account_health_metrics(self):
-        dashboard = get_account_operations_dashboard()
-        cards = {card.label: card.value for card in dashboard.summary_cards}
-
-        self.assertEqual(cards["Total accounts"], 4)
-        self.assertEqual(cards["Active accounts"], 3)
-        self.assertEqual(cards["Inactive accounts"], 1)
-        self.assertEqual(cards["Imported accounts"], 1)
-        self.assertEqual(cards["Password change required"], 1)
-        self.assertEqual(cards["Users without player links"], 3)
-        self.assertEqual(cards["Players without self-linked accounts"], 1)
-        self.assertEqual(dashboard.users_requiring_password_change[0].user, self.player_user)
-
-    def test_account_list_context_returns_rows_and_choices(self):
-        context = get_account_list(AccountListFilters(role=AccountRole.COACH))
-
-        self.assertEqual(context.total_count, 1)
-        self.assertEqual(context.rows[0].user, self.coach)
-        self.assertEqual(context.rows[0].role_label, "Coach")
-        self.assertIn((AccountRole.COACH, "Coach"), context.role_choices)
-
-    def test_account_detail_context_includes_profile_and_linked_players(self):
-        context = get_account_detail(self.player_user.id)
-
-        self.assertEqual(context.user, self.player_user)
-        self.assertEqual(context.role, AccountRole.PLAYER)
-        self.assertEqual(context.role_label, "Player")
-        self.assertEqual(len(context.linked_players), 1)
-        linked = context.linked_players[0]
-        self.assertEqual(linked.player, self.player)
-        self.assertEqual(linked.relationship, "Self")
-        self.assertTrue(linked.is_primary)
-        self.assertTrue(linked.is_active)
-        self.assertTrue(linked.created_from_import)
-        self.assertEqual(linked.import_label, "players.csv")
-
-    def test_players_without_self_link_count(self):
-        self.assertEqual(count_players_without_self_link(), 1)
-
-    def test_create_account_only_creates_user_profile_and_temporary_password(self):
-        result = create_account_only(
-            actor=self.staff,
-            username="New.Coach",
-            first_name="New",
-            last_name="Coach",
-            email="New.Coach@example.com",
-            role=AccountRole.COACH,
-            is_active=True,
-        )
-
-        user = User.objects.get(username="new.coach")
-        profile = user.account_profile
-        self.assertEqual(result.user, user)
-        self.assertEqual(result.username, "new.coach")
-        self.assertEqual(result.role, AccountRole.COACH)
-        self.assertEqual(result.role_label, "Coach")
-        self.assertTrue(result.temporary_password)
-        self.assertTrue(user.check_password(result.temporary_password))
-        self.assertNotIn(result.temporary_password, repr(result))
-        self.assertEqual(user.email, "new.coach@example.com")
-        self.assertEqual(profile.role, AccountRole.COACH)
-        self.assertTrue(profile.must_change_password)
-        self.assertFalse(profile.created_from_import)
-        self.assertIsNone(profile.import_batch)
-        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
-
-    def test_create_account_only_can_create_inactive_account(self):
-        result = create_account_only(
-            actor=self.staff,
-            username="inactive.coach",
-            role=AccountRole.COACH,
-            is_active=False,
-        )
-
-        self.assertFalse(User.objects.get(pk=result.user.id).is_active)
-        self.assertTrue(result.user.account_profile.must_change_password)
-
-    def test_create_account_only_rejects_duplicate_username_and_email(self):
-        User.objects.create_user(username="duplicate", email="duplicate@example.com")
-
-        with self.assertRaises(ValidationError):
-            create_account_only(actor=self.staff, username="DUPLICATE", role=AccountRole.COACH)
-        with self.assertRaises(ValidationError):
-            create_account_only(
-                actor=self.staff,
-                username="unique",
-                email="Duplicate@Example.com",
-                role=AccountRole.COACH,
-            )
-
-    def test_create_account_only_admin_requires_superuser(self):
-        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
-
-        with self.assertRaises(ValidationError):
-            create_account_only(actor=self.staff, username="admin.account", role=AccountRole.ADMIN)
-
-        result = create_account_only(actor=superuser, username="admin.account", role=AccountRole.ADMIN)
-
-        self.assertEqual(result.role, AccountRole.ADMIN)
-        self.assertFalse(result.user.is_staff)
-        self.assertFalse(result.user.is_superuser)
-
-    def test_create_player_account_uses_existing_player_and_provisioning_logic(self):
-        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
-
-        result = create_player_account(actor=self.staff, player=player, email="Blake@example.com")
-
-        user = User.objects.get(username="blake.player")
-        profile = user.account_profile
-        link = UserPlayerLink.objects.get(user=user, player=player)
-        self.assertEqual(result.user, user)
-        self.assertEqual(result.player, player)
-        self.assertEqual(result.temporary_password, "20130602")
-        self.assertTrue(user.check_password(result.temporary_password))
-        self.assertEqual(user.email, "blake@example.com")
-        self.assertEqual(profile.role, AccountRole.PLAYER)
-        self.assertTrue(profile.must_change_password)
-        self.assertTrue(user.is_active)
-        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
-        self.assertTrue(link.is_primary)
-        self.assertFalse(profile.created_from_import)
-        self.assertIsNone(profile.import_batch)
-        self.assertFalse(link.created_from_import)
-        self.assertIsNone(link.import_batch)
-
-    def test_create_player_account_accepts_optional_username_and_inactive_flag(self):
-        player = Player.objects.create(first_name="Casey", last_name="Player", birthdate="2014-07-03")
-
-        result = create_player_account(actor=self.staff, player=player, username="Custom.Player", is_active=False)
-
-        self.assertEqual(result.username, "custom.player")
-        self.assertFalse(User.objects.get(username="custom.player").is_active)
-
-    def test_create_player_account_rejects_duplicate_email_username_and_player_account(self):
-        player = Player.objects.create(first_name="Dana", last_name="Player", birthdate="2015-08-04")
-        User.objects.create_user(username="taken", email="taken@example.com")
-
-        with self.assertRaises(ValidationError):
-            create_player_account(actor=self.staff, player=player, username="taken")
-        with self.assertRaises(ValidationError):
-            create_player_account(actor=self.staff, player=player, email="taken@example.com")
-
-        create_player_account(actor=self.staff, player=player, username="dana.player")
-        with self.assertRaises(ValidationError):
-            create_player_account(actor=self.staff, player=player, username="dana.player2")
-
-        self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)
-
-    def test_create_player_account_requires_existing_player_birthdate_and_player_role(self):
-        player = Player.objects.create(first_name="No", last_name="Birthdate")
-
-        with self.assertRaises(ValidationError):
-            create_player_account(actor=self.staff, player=player)
-        with self.assertRaises(ValidationError):
-            create_player_account(actor=self.staff, player=self.player, role=AccountRole.COACH)
-
-    def test_update_account_changes_lifecycle_username_email_and_role(self):
-        result = update_account(
-            actor=self.staff,
-            user_id=self.coach.id,
-            username=" Coach.Updated ",
-            first_name="Updated",
-            last_name="Coach",
-            email="UPDATED@example.com",
-            role=AccountRole.GUEST_EVALUATOR,
-            is_active=False,
-        )
-
-        self.coach.refresh_from_db()
-        self.assertEqual(result.username, "coach.updated")
-        self.assertEqual(result.role, AccountRole.GUEST_EVALUATOR)
-        self.assertFalse(result.is_active)
-        self.assertEqual(self.coach.username, "coach.updated")
-        self.assertEqual(self.coach.email, "updated@example.com")
-        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
-        self.assertFalse(self.coach.is_staff)
-        self.assertFalse(self.coach.is_superuser)
-
-    def test_update_account_rejects_duplicate_username_and_email(self):
-        User.objects.create_user(username="taken", email="taken@example.com")
-
-        with self.assertRaises(ValidationError):
-            update_account(
-                actor=self.staff,
-                user_id=self.coach.id,
-                username="TAKEN",
-                email="coach@example.com",
-                role=AccountRole.COACH,
-            )
-        with self.assertRaises(ValidationError):
-            update_account(
-                actor=self.staff,
-                user_id=self.coach.id,
-                username="coach.one",
-                email="Taken@Example.com",
-                role=AccountRole.COACH,
-            )
-
-    def test_update_account_admin_role_requires_superuser(self):
-        with self.assertRaises(ValidationError):
-            update_account(
-                actor=self.staff,
-                user_id=self.coach.id,
-                username="coach.one",
-                role=AccountRole.ADMIN,
-            )
-
-        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
-        result = update_account(
-            actor=superuser,
-            user_id=self.coach.id,
-            username="coach.one",
-            role=AccountRole.ADMIN,
-        )
-
-        self.coach.refresh_from_db()
-        self.assertEqual(result.role, AccountRole.ADMIN)
-        self.assertEqual(self.coach.account_profile.role, AccountRole.ADMIN)
-        self.assertFalse(self.coach.is_staff)
-        self.assertFalse(self.coach.is_superuser)
-
-    def test_account_operation_services_require_staff_actor(self):
-        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
-            create_account_only(actor=self.coach, username="not.allowed", role=AccountRole.COACH)
-        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
-            create_player_account(actor=self.coach, player=self.player)
-        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
-            update_account(
-                actor=self.coach,
-                user_id=self.player_user.id,
-                username="alex.player",
-                role=AccountRole.PLAYER,
-            )
-        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
-            reset_account_password(actor=self.coach, user_id=self.player_user.id)
-        with self.assertRaisesMessage(ValidationError, "Only staff users can manage accounts"):
-            bulk_account_operation(actor=self.coach, action="activate", user_ids=[self.player_user.id])
-
-    def test_staff_cannot_mutate_staff_or_superuser_accounts(self):
-        other_staff = User.objects.create_user(username="other.staff", password="testpass", is_staff=True)
-        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
-        superuser_actor = User.objects.create_superuser(username="ops.admin2", password="testpass")
-
-        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
-            update_account(
-                actor=self.staff,
-                user_id=other_staff.id,
-                username="other.staff",
-                role=AccountRole.STAFF,
-            )
-        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
-            activate_account(actor=self.staff, user_id=other_staff.id)
-        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
-            deactivate_account(actor=self.staff, user_id=superuser.id)
-        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
-            reset_account_password(actor=self.staff, user_id=superuser.id)
-        with self.assertRaisesMessage(ValidationError, "Only superusers can manage staff or superuser accounts"):
-            create_user_player_link(
-                actor=self.staff,
-                user_id=other_staff.id,
-                player=self.player,
-                relationship=UserPlayerRelationship.STAFF,
-            )
-
-        result = reset_account_password(actor=superuser_actor, user_id=other_staff.id)
-        other_staff.refresh_from_db()
-        self.assertTrue(other_staff.check_password(result.temporary_password))
-
-    def test_activate_and_deactivate_account_preserve_profile_and_links(self):
-        deactivate_result = deactivate_account(actor=self.staff, user_id=self.player_user.id)
-        self.player_user.refresh_from_db()
-        link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)
-
-        self.assertFalse(deactivate_result.is_active)
-        self.assertFalse(self.player_user.is_active)
-        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
-        self.assertTrue(link.is_active)
-
-        activate_result = activate_account(actor=self.staff, user_id=self.player_user.id)
-        self.player_user.refresh_from_db()
-
-        self.assertTrue(activate_result.is_active)
-        self.assertTrue(self.player_user.is_active)
-        self.assertTrue(UserPlayerLink.objects.get(pk=link.pk).is_active)
-
-    def test_deactivate_account_rejects_self_deactivation(self):
-        with self.assertRaises(ValidationError):
-            deactivate_account(actor=self.staff, user_id=self.staff.id)
-
-        self.staff.refresh_from_db()
-        self.assertTrue(self.staff.is_active)
-
-    def test_update_account_rejects_self_deactivation(self):
-        with self.assertRaises(ValidationError):
-            update_account(
-                actor=self.staff,
-                user_id=self.staff.id,
-                username="staff",
-                role=AccountRole.STAFF,
-                is_active=False,
-            )
-
-        self.staff.refresh_from_db()
-        self.assertTrue(self.staff.is_active)
-
-    def test_deactivate_account_rejects_last_active_superuser(self):
-        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
-
-        with self.assertRaises(ValidationError):
-            deactivate_account(actor=self.staff, user_id=superuser.id)
-
-        superuser.refresh_from_db()
-        self.assertTrue(superuser.is_active)
-
-    def test_deactivate_account_allows_superuser_actor_when_another_active_superuser_exists(self):
-        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
-        actor = User.objects.create_superuser(username="ops.actor", password="testpass")
-        User.objects.create_superuser(username="ops.admin2", password="testpass")
-
-        result = deactivate_account(actor=actor, user_id=superuser.id)
-
-        self.assertFalse(result.is_active)
-
-    def test_account_operations_manage_player_links_through_services(self):
-        link_result = create_user_player_link(
-            actor=self.staff,
-            user_id=self.coach.id,
-            player=self.player,
-            relationship=UserPlayerRelationship.COACH,
-            is_primary=False,
-        )
-
-        self.assertTrue(link_result.is_active)
-        self.assertFalse(link_result.is_primary)
-        with self.assertRaises(ValidationError):
-            create_user_player_link(
-                actor=self.staff,
-                user_id=self.coach.id,
-                player=self.player,
-                relationship=UserPlayerRelationship.COACH,
-                is_primary=False,
-            )
-
-        deactivated = deactivate_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id)
-        self.assertFalse(deactivated.is_active)
-        self.assertFalse(UserPlayerLink.objects.get(pk=link_result.link.id).is_primary)
-
-        reactivated = reactivate_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id)
-        self.assertTrue(reactivated.is_active)
-
-    def test_account_operations_set_primary_self_link_switches_existing_primary(self):
-        other_player = Player.objects.create(first_name="Second", last_name="Player")
-        first_link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)
-        second_link = create_user_player_link(
-            actor=self.staff,
-            user_id=self.player_user.id,
-            player=other_player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=False,
-        ).link
-
-        result = set_primary_user_player_link(actor=self.staff, user_id=self.player_user.id, link_id=second_link.id)
-        first_link.refresh_from_db()
-        second_link.refresh_from_db()
-
-        self.assertTrue(result.is_primary)
-        self.assertFalse(first_link.is_primary)
-        self.assertTrue(second_link.is_primary)
-        self.assertEqual(UserPlayerLink.objects.filter(user=self.player_user, is_primary=True, is_active=True).count(), 1)
-
-    def test_account_operations_reject_primary_non_self_link(self):
-        link = create_user_player_link(
-            actor=self.staff,
-            user_id=self.coach.id,
-            player=self.player,
-            relationship=UserPlayerRelationship.PARENT,
-            is_primary=False,
-        ).link
-
-        with self.assertRaises(ValidationError):
-            set_primary_user_player_link(actor=self.staff, user_id=self.coach.id, link_id=link.id)
-
-    def test_reset_account_password_uses_birthdate_for_player_account(self):
-        self.player_user.account_profile.must_change_password = False
-        self.player_user.account_profile.save(update_fields=["must_change_password", "updated_at"])
-        original_link_count = UserPlayerLink.objects.filter(user=self.player_user).count()
-
-        result = reset_account_password(actor=self.staff, user_id=self.player_user.id)
-
-        self.player_user.refresh_from_db()
-        self.assertEqual(result.user, self.player_user)
-        self.assertEqual(result.username, "alex.player")
-        self.assertEqual(result.temporary_password, "20120501")
-        self.assertTrue(self.player_user.check_password("20120501"))
-        self.assertTrue(self.player_user.account_profile.must_change_password)
-        self.assertTrue(self.player_user.is_active)
-        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
-        self.assertTrue(self.player_user.account_profile.created_from_import)
-        self.assertEqual(self.player_user.account_profile.import_batch, self.import_batch)
-        self.assertEqual(UserPlayerLink.objects.filter(user=self.player_user).count(), original_link_count)
-        self.assertNotIn(result.temporary_password, repr(result))
-
-    def test_reset_account_password_uses_random_password_for_non_player_account(self):
-        self.coach.account_profile.must_change_password = False
-        self.coach.account_profile.save(update_fields=["must_change_password", "updated_at"])
-
-        result = reset_account_password(actor=self.staff, user_id=self.coach.id)
-
-        self.coach.refresh_from_db()
-        self.assertTrue(result.temporary_password)
-        self.assertNotEqual(result.temporary_password, "20120501")
-        self.assertTrue(self.coach.check_password(result.temporary_password))
-        self.assertTrue(self.coach.account_profile.must_change_password)
-        self.assertTrue(self.coach.is_active)
-        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
-        self.assertFalse(UserPlayerLink.objects.filter(user=self.coach, relationship=UserPlayerRelationship.SELF).exists())
-        self.assertNotIn(result.temporary_password, repr(result))
-
-    def test_reset_account_password_preserves_inactive_account_state(self):
-        self.assertFalse(self.inactive_user.is_active)
-
-        result = reset_account_password(actor=self.staff, user_id=self.inactive_user.id)
-
-        self.inactive_user.refresh_from_db()
-        self.assertFalse(self.inactive_user.is_active)
-        self.assertTrue(self.inactive_user.check_password(result.temporary_password))
-        self.assertTrue(self.inactive_user.account_profile.must_change_password)
-
-    def test_reset_account_password_rejects_player_account_missing_birthdate(self):
-        player = Player.objects.create(first_name="No", last_name="Birthdate")
-        user = User.objects.create_user(username="no.birthdate", password="testpass")
-        set_account_role(user, AccountRole.PLAYER)
-        link_user_to_player(user, player)
-
-        with self.assertRaises(ValidationError):
-            reset_account_password(actor=self.staff, user_id=user.id)
-
-    def test_bulk_account_operation_activates_accounts(self):
-        result = bulk_account_operation(actor=self.staff, action="activate", user_ids=[self.inactive_user.id])
-
-        self.inactive_user.refresh_from_db()
-        self.assertEqual(result.processed, 1)
-        self.assertEqual(result.successful, 1)
-        self.assertEqual(result.failed, 0)
-        self.assertTrue(self.inactive_user.is_active)
-
-    def test_bulk_account_operation_deactivates_accounts(self):
-        result = bulk_account_operation(actor=self.staff, action="deactivate", user_ids=[self.coach.id])
-
-        self.coach.refresh_from_db()
-        self.assertEqual(result.processed, 1)
-        self.assertEqual(result.successful, 1)
-        self.assertFalse(self.coach.is_active)
-
-    def test_bulk_account_operation_sets_password_change_requirement(self):
-        mark_password_change_required(self.coach, False)
-
-        result = bulk_account_operation(
-            actor=self.staff,
-            action="require_password_change",
-            user_ids=[self.coach.id],
-        )
-
-        self.coach.refresh_from_db()
-        self.assertEqual(result.successful, 1)
-        self.assertTrue(self.coach.account_profile.must_change_password)
-
-    def test_bulk_account_operation_clears_password_change_requirement(self):
-        mark_password_change_required(self.player_user, True)
-
-        result = bulk_account_operation(
-            actor=self.staff,
-            action="clear_password_change",
-            user_ids=[self.player_user.id],
-        )
-
-        self.player_user.refresh_from_db()
-        self.assertEqual(result.successful, 1)
-        self.assertFalse(self.player_user.account_profile.must_change_password)
-
-    def test_bulk_account_operation_continues_after_failure(self):
-        result = bulk_account_operation(
-            actor=self.staff,
-            action="deactivate",
-            user_ids=[self.staff.id, self.coach.id],
-        )
-
-        self.staff.refresh_from_db()
-        self.coach.refresh_from_db()
-        self.assertEqual(result.processed, 2)
-        self.assertEqual(result.successful, 1)
-        self.assertEqual(result.failed, 1)
-        self.assertEqual(result.errors[0].username, "staff")
-        self.assertIn("cannot deactivate your own account", result.errors[0].message)
-        self.assertTrue(self.staff.is_active)
-        self.assertFalse(self.coach.is_active)
-
-    def test_bulk_account_operation_rejects_empty_selection_and_unknown_action(self):
-        with self.assertRaises(ValidationError):
-            bulk_account_operation(actor=self.staff, action="activate", user_ids=[])
-        with self.assertRaises(ValidationError):
-            bulk_account_operation(actor=self.staff, action="unsupported", user_ids=[self.coach.id])
-
-    def test_bulk_account_operation_reports_missing_users(self):
-        result = bulk_account_operation(actor=self.staff, action="activate", user_ids=[999999])
-
-        self.assertEqual(result.processed, 1)
-        self.assertEqual(result.successful, 0)
-        self.assertEqual(result.failed, 1)
-        self.assertEqual(result.errors[0].username, "Unknown account")
-        self.assertEqual(result.errors[0].message, "Account not found.")
-
-    def test_bulk_account_operation_rejects_last_superuser_deactivation(self):
-        superuser = User.objects.create_superuser(username="ops.admin", password="testpass")
-
-        result = bulk_account_operation(actor=self.staff, action="deactivate", user_ids=[superuser.id])
-
-        superuser.refresh_from_db()
-        self.assertEqual(result.successful, 0)
-        self.assertEqual(result.failed, 1)
-        self.assertEqual(result.errors[0].username, "ops.admin")
-        self.assertIn("last active superuser", result.errors[0].message)
-        self.assertTrue(superuser.is_active)
-
-
-class UserPlayerLinkModelTests(TestCase):
-    def setUp(self):
-        self.user = User.objects.create_user(username="player", password="testpass")
-        self.other_user = User.objects.create_user(username="other", password="testpass")
-        self.player = Player.objects.create(first_name="Alex", last_name="Player")
-        self.other_player = Player.objects.create(first_name="Blake", last_name="Player")
-
-    def test_user_player_link_can_link_user_to_player(self):
-        link = UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=True,
-        )
-
-        self.assertEqual(link.user, self.user)
-        self.assertEqual(link.player, self.player)
-        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
-        self.assertTrue(link.is_active)
-        self.assertTrue(link.is_primary)
-
-    def test_user_can_link_to_multiple_players(self):
-        UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.PARENT,
-        )
-        UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.other_player,
-            relationship=UserPlayerRelationship.PARENT,
-        )
-
-        self.assertEqual(UserPlayerLink.objects.filter(user=self.user, is_active=True).count(), 2)
-
-    def test_player_can_link_to_multiple_users(self):
-        UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.PARENT,
-        )
-        UserPlayerLink.objects.create(
-            user=self.other_user,
-            player=self.player,
-            relationship=UserPlayerRelationship.GUARDIAN,
-        )
-
-        self.assertEqual(UserPlayerLink.objects.filter(player=self.player, is_active=True).count(), 2)
-
-    def test_duplicate_active_relationship_is_blocked_but_inactive_history_is_allowed(self):
-        UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.PARENT,
-        )
-
-        with self.assertRaises(IntegrityError):
-            with transaction.atomic():
-                UserPlayerLink.objects.create(
-                    user=self.user,
-                    player=self.player,
-                    relationship=UserPlayerRelationship.PARENT,
-                )
-
-        UserPlayerLink.objects.filter(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.PARENT,
-        ).update(is_active=False)
-        UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.PARENT,
-        )
-
-        self.assertEqual(
-            UserPlayerLink.objects.filter(
-                user=self.user,
-                player=self.player,
-                relationship=UserPlayerRelationship.PARENT,
-            ).count(),
-            2,
-        )
-
-    def test_only_one_active_primary_self_link_per_user(self):
-        UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=True,
-        )
-
-        with self.assertRaises(IntegrityError):
-            with transaction.atomic():
-                UserPlayerLink.objects.create(
-                    user=self.user,
-                    player=self.other_player,
-                    relationship=UserPlayerRelationship.SELF,
-                    is_primary=True,
-                )
-
-    def test_only_one_active_primary_self_link_per_player(self):
-        UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=True,
-        )
-
-        with self.assertRaises(IntegrityError):
-            with transaction.atomic():
-                UserPlayerLink.objects.create(
-                    user=self.other_user,
-                    player=self.player,
-                    relationship=UserPlayerRelationship.SELF,
-                    is_primary=True,
-                )
-
-    def test_import_provenance_fields_persist(self):
-        import_batch = PlayerImportBatch.objects.create(
-            source="manual_staff_csv",
-            original_filename="players.csv",
-            uploaded_by=self.other_user,
-        )
-
-        link = UserPlayerLink.objects.create(
-            user=self.user,
-            player=self.player,
-            relationship=UserPlayerRelationship.SELF,
-            created_from_import=True,
-            import_batch=import_batch,
-            metadata={"row": 2},
-        )
-
-        self.assertTrue(link.created_from_import)
-        self.assertEqual(link.import_batch, import_batch)
-        self.assertEqual(link.metadata, {"row": 2})
-
-
-class UserPlayerLinkServiceTests(TestCase):
-    def setUp(self):
-        self.user = User.objects.create_user(username="player", password="testpass")
-        self.other_user = User.objects.create_user(username="other", password="testpass")
-        self.player = Player.objects.create(first_name="Alex", last_name="Player")
-        self.other_player = Player.objects.create(first_name="Blake", last_name="Player")
-
-    def test_link_user_to_player_creates_active_link(self):
-        link = link_user_to_player(self.user, self.player)
-
-        self.assertEqual(link.user, self.user)
-        self.assertEqual(link.player, self.player)
-        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
-        self.assertTrue(link.is_primary)
-        self.assertTrue(link.is_active)
-
-    def test_link_user_to_player_reuses_existing_active_link(self):
-        link = link_user_to_player(self.user, self.player, metadata={"source": "initial"})
-        same_link = link_user_to_player(self.user, self.player, created_from_import=True, metadata={"source": "updated"})
-
-        self.assertEqual(link.pk, same_link.pk)
-        self.assertTrue(same_link.created_from_import)
-        self.assertEqual(same_link.metadata, {"source": "updated"})
-        self.assertEqual(UserPlayerLink.objects.count(), 1)
-
-    def test_link_user_to_player_rejects_invalid_inputs(self):
-        with self.assertRaises(ValidationError):
-            link_user_to_player(None, self.player)
-        with self.assertRaises(ValidationError):
-            link_user_to_player(self.user, None)
-        with self.assertRaises(ValidationError):
-            link_user_to_player(self.user, self.player, relationship="unsupported")
-        with self.assertRaises(ValidationError):
-            link_user_to_player(self.user, self.player, metadata=["not", "dict"])
-
-    def test_link_user_to_player_rejects_primary_non_self_link(self):
-        with self.assertRaises(ValidationError):
-            link_user_to_player(
-                self.user,
-                self.player,
-                relationship=UserPlayerRelationship.PARENT,
-                is_primary=True,
-            )
-
-    def test_link_user_to_player_rejects_primary_self_conflicts(self):
-        link_user_to_player(self.user, self.player)
-
-        with self.assertRaises(ValidationError):
-            link_user_to_player(self.user, self.other_player)
-        with self.assertRaises(ValidationError):
-            link_user_to_player(self.other_user, self.player)
-
-    def test_deactivate_link_marks_inactive_and_clears_primary(self):
-        link = link_user_to_player(self.user, self.player)
-
-        deactivate_link(link)
-        link.refresh_from_db()
-
-        self.assertFalse(link.is_active)
-        self.assertFalse(link.is_primary)
-
-    def test_activate_link_reactivates_valid_inactive_link(self):
-        link = link_user_to_player(self.user, self.player)
-        deactivate_link(link)
-
-        activate_link(link)
-        link.refresh_from_db()
-
-        self.assertTrue(link.is_active)
-        self.assertFalse(link.is_primary)
-
-    def test_activate_link_rejects_duplicate_active_relationship(self):
-        link = link_user_to_player(
-            self.user,
-            self.player,
-            relationship=UserPlayerRelationship.PARENT,
-            is_primary=False,
-        )
-        deactivate_link(link)
-        link_user_to_player(
-            self.user,
-            self.player,
-            relationship=UserPlayerRelationship.PARENT,
-            is_primary=False,
-        )
-
-        with self.assertRaises(ValidationError):
-            activate_link(link)
-
-    def test_unlink_user_from_player_deactivates_matching_links(self):
-        link_user_to_player(
-            self.user,
-            self.player,
-            relationship=UserPlayerRelationship.PARENT,
-            is_primary=False,
-        )
-        link_user_to_player(
-            self.user,
-            self.player,
-            relationship=UserPlayerRelationship.COACH,
-            is_primary=False,
-        )
-
-        count = unlink_user_from_player(self.user, self.player, relationship=UserPlayerRelationship.PARENT)
-
-        self.assertEqual(count, 1)
-        self.assertFalse(
-            UserPlayerLink.objects.get(
-                user=self.user,
-                player=self.player,
-                relationship=UserPlayerRelationship.PARENT,
-            ).is_active
-        )
-        self.assertTrue(
-            UserPlayerLink.objects.get(
-                user=self.user,
-                player=self.player,
-                relationship=UserPlayerRelationship.COACH,
-            ).is_active
-        )
-
-    def test_lookup_helpers_default_to_active_links(self):
-        active_link = link_user_to_player(
-            self.user,
-            self.player,
-            relationship=UserPlayerRelationship.PARENT,
-            is_primary=False,
-        )
-        inactive_link = link_user_to_player(
-            self.user,
-            self.other_player,
-            relationship=UserPlayerRelationship.PARENT,
-            is_primary=False,
-        )
-        deactivate_link(inactive_link)
-
-        self.assertEqual(list(get_players_for_user(self.user)), [self.player])
-        self.assertCountEqual(list(get_players_for_user(self.user, active_only=False)), [self.player, self.other_player])
-        self.assertEqual(list(get_users_for_player(self.player)), [self.user])
-        self.assertEqual(list(get_users_for_player(self.other_player)), [])
-        self.assertEqual(list(get_users_for_player(self.other_player, active_only=False)), [self.user])
-        self.assertTrue(active_link.is_active)
-
-    def test_primary_and_self_helpers(self):
-        link_user_to_player(self.user, self.player)
-
-        self.assertEqual(get_primary_player(self.user), self.player)
-        self.assertEqual(get_primary_user(self.player), self.user)
-        self.assertTrue(is_player_self(self.user, self.player))
-        self.assertFalse(is_player_self(self.user, self.other_player))
-
-    def test_set_primary_self_link_switches_primary_link(self):
-        first_link = link_user_to_player(self.user, self.player)
-        second_link = link_user_to_player(
-            self.user,
-            self.other_player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=False,
-        )
-
-        set_primary_self_link(second_link)
-        first_link.refresh_from_db()
-        second_link.refresh_from_db()
-
-        self.assertFalse(first_link.is_primary)
-        self.assertTrue(second_link.is_primary)
-        self.assertTrue(second_link.is_active)
-        self.assertEqual(get_primary_player(self.user), self.other_player)
-
-    def test_set_primary_self_link_rejects_non_self_link(self):
-        parent_link = link_user_to_player(
-            self.user,
-            self.player,
-            relationship=UserPlayerRelationship.PARENT,
-            is_primary=False,
-        )
-
-        with self.assertRaises(ValidationError):
-            set_primary_self_link(parent_link)
-
-    def test_is_player_self_ignores_inactive_or_non_self_links(self):
-        parent_link = link_user_to_player(
-            self.user,
-            self.player,
-            relationship=UserPlayerRelationship.PARENT,
-            is_primary=False,
-        )
-
-        self.assertFalse(is_player_self(self.user, self.player))
-
-        deactivate_link(parent_link)
-        self.assertFalse(is_player_self(self.user, self.player))
-
-
-class AccountUsernameServiceTests(TestCase):
-    def test_username_parts_normalize_unicode_and_unsafe_characters(self):
-        self.assertEqual(normalize_username_part("  José   García!  "), "josegarcia")
-
-    def test_base_username_for_player_uses_first_dot_last(self):
-        player = Player.objects.create(first_name="José", last_name="García", birthdate="2012-05-01")
-
-        self.assertEqual(base_username_for_player(player), "jose.garcia")
-
-    def test_username_for_player_uses_deterministic_suffixes(self):
-        player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")
-        User.objects.create_user(username="alex.player")
-        User.objects.create_user(username="alex.player2")
-
-        self.assertEqual(username_for_player(player), "alex.player3")
-
-    def test_validate_available_username_rejects_duplicates_and_unsafe_values(self):
-        User.objects.create_user(username="coach.one")
-
-        self.assertEqual(validate_available_username("new.user"), "new.user")
-        self.assertEqual(validate_available_username("  Coach.Two  "), "coach.two")
-        with self.assertRaises(ValidationError):
-            validate_available_username("coach.ONE")
-        with self.assertRaises(ValidationError):
-            validate_available_username("bad username")
-
-    def test_validate_available_username_for_user_allows_current_user(self):
-        user = User.objects.create_user(username="coach.one")
-        User.objects.create_user(username="other")
-
-        self.assertEqual(validate_available_username_for_user(user, " Coach.One "), "coach.one")
-        with self.assertRaises(ValidationError):
-            validate_available_username_for_user(user, "OTHER")
-
-
-class AccountEmailServiceTests(TestCase):
-    def test_email_normalization_and_comparison(self):
-        self.assertEqual(normalize_email("  PLAYER@Example.COM "), "player@example.com")
-        self.assertTrue(emails_equal("PLAYER@example.com", "player@EXAMPLE.com"))
-
-    def test_find_existing_email_user_is_case_insensitive(self):
-        user = User.objects.create_user(username="user", email="Player@Example.com")
-
-        self.assertEqual(find_existing_email_user("player@example.COM"), user)
-
-
-class AccountPasswordServiceTests(TestCase):
-    def test_generate_birthdate_password_uses_yyyymmdd(self):
-        player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")
-
-        self.assertEqual(generate_birthdate_password(player), "20120501")
-
-    def test_generate_birthdate_password_requires_birthdate(self):
-        player = Player.objects.create(first_name="Alex", last_name="Player")
-
-        with self.assertRaises(ValidationError):
-            generate_birthdate_password(player)
-
-    def test_set_temporary_password_hashes_password_and_marks_profile(self):
-        user = User.objects.create_user(username="player")
-        player = Player.objects.create(first_name="Alex", last_name="Player", birthdate="2012-05-01")
-
-        set_temporary_password(user, player)
-        mark_password_change_required(user)
-        user.refresh_from_db()
-
-        self.assertNotEqual(user.password, "20120501")
-        self.assertTrue(user.check_password("20120501"))
-        self.assertTrue(user.account_profile.must_change_password)
-
-    def test_generate_random_temporary_password_is_secure_length(self):
-        password = generate_random_temporary_password()
-
-        self.assertGreaterEqual(len(password), 12)
-        self.assertNotEqual(password, generate_random_temporary_password())
-
-
-class AccountProvisioningServiceTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.player = Player.objects.create(first_name="José", last_name="García", birthdate="2012-05-01")
-        self.import_batch = PlayerImportBatch.objects.create(
-            source="manual_staff_csv",
-            original_filename="players.csv",
-            uploaded_by=self.staff,
-        )
-
-    def test_provision_player_account_creates_active_player_account_profile_and_link(self):
-        result = provision_player_account(
-            self.player,
-            import_batch=self.import_batch,
-            actor=self.staff,
-            email="Player@Example.com",
-            row_number=2,
-        )
-
-        user = User.objects.get(username="jose.garcia")
-        profile = user.account_profile
-        link = UserPlayerLink.objects.get(user=user, player=self.player)
-        self.assertEqual(result.status, STATUS_CREATED)
-        self.assertEqual(result.username, "jose.garcia")
-        self.assertTrue(user.is_active)
-        self.assertEqual(user.email, "player@example.com")
-        self.assertTrue(user.check_password("20120501"))
-        self.assertEqual(profile.role, AccountRole.PLAYER)
-        self.assertTrue(profile.must_change_password)
-        self.assertTrue(profile.created_from_import)
-        self.assertEqual(profile.import_batch, self.import_batch)
-        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
-        self.assertTrue(link.created_from_import)
-        self.assertEqual(link.import_batch, self.import_batch)
-
-    def test_provision_player_account_can_activate_user_when_explicit(self):
-        result = provision_player_account(self.player, import_batch=self.import_batch, activate_user=True)
-
-        self.assertEqual(result.status, STATUS_CREATED)
-        self.assertTrue(User.objects.get(pk=result.user_id).is_active)
-
-    def test_provision_player_account_skips_missing_birthdate(self):
-        player = Player.objects.create(first_name="No", last_name="Birthdate")
-
-        result = provision_player_account(player, import_batch=self.import_batch, row_number=3)
-
-        self.assertEqual(result.status, STATUS_SKIPPED)
-        self.assertFalse(User.objects.filter(username="no.birthdate").exists())
-
-    def test_provision_player_account_is_idempotent_for_existing_link(self):
-        first = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)
-        second = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)
-
-        self.assertEqual(first.status, STATUS_CREATED)
-        self.assertEqual(second.status, STATUS_ALREADY_LINKED)
-        self.assertEqual(User.objects.filter(username="jose.garcia").count(), 1)
-        self.assertEqual(UserPlayerLink.objects.filter(player=self.player).count(), 1)
-        self.assertEqual(AccountProfile.objects.filter(user_id=first.user_id).count(), 1)
-
-    def test_provision_player_account_reuses_inactive_self_link_without_duplicates(self):
-        user = User.objects.create_user(username="existing.player", email="existing@example.com")
-        profile = get_or_create_account_profile(user)
-        link = link_user_to_player(
-            user,
-            self.player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=True,
-            created_from_import=True,
-            import_batch=self.import_batch,
-        )
-        deactivate_link(link)
-
-        result = provision_player_account(
-            self.player,
-            import_batch=self.import_batch,
-            email="existing@example.com",
-            row_number=2,
-        )
-        link.refresh_from_db()
-        profile.refresh_from_db()
-
-        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
-        self.assertEqual(result.user_id, user.id)
-        self.assertTrue(link.is_active)
-        self.assertTrue(link.is_primary)
-        self.assertEqual(User.objects.filter(username="existing.player").count(), 1)
-        self.assertEqual(AccountProfile.objects.filter(user=user).count(), 1)
-        self.assertEqual(UserPlayerLink.objects.filter(user=user, player=self.player).count(), 1)
-
-    def test_provision_player_account_preserves_manual_link_provenance(self):
-        user = User.objects.create_user(username="manual.player", email="manual@example.com")
-        profile = get_or_create_account_profile(user)
-        link = link_user_to_player(user, self.player)
-        deactivate_link(link)
-
-        result = provision_player_account(
-            self.player,
-            import_batch=self.import_batch,
-            email="manual@example.com",
-            row_number=2,
-        )
-        profile.refresh_from_db()
-        link.refresh_from_db()
-
-        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
-        self.assertFalse(profile.created_from_import)
-        self.assertIsNone(profile.import_batch)
-        self.assertFalse(link.created_from_import)
-        self.assertIsNone(link.import_batch)
-
-    def test_provision_player_account_remains_idempotent_after_link_deactivation_and_reactivation(self):
-        first = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)
-        link = UserPlayerLink.objects.get(player=self.player, user_id=first.user_id)
-        deactivate_link(link)
-
-        second = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)
-        third = provision_player_account(self.player, import_batch=self.import_batch, row_number=2)
-
-        link.refresh_from_db()
-        self.assertEqual(second.status, STATUS_ALREADY_LINKED)
-        self.assertEqual(third.status, STATUS_ALREADY_LINKED)
-        self.assertTrue(link.is_active)
-        self.assertEqual(User.objects.filter(username="jose.garcia").count(), 1)
-        self.assertEqual(AccountProfile.objects.filter(user_id=first.user_id).count(), 1)
-        self.assertEqual(UserPlayerLink.objects.filter(player=self.player, user_id=first.user_id).count(), 1)
-
-    def test_provision_player_account_conflicts_on_unrelated_email(self):
-        User.objects.create_user(username="other", email="player@example.com")
-
-        result = provision_player_account(self.player, import_batch=self.import_batch, email="PLAYER@example.com")
-
-        self.assertEqual(result.status, STATUS_CONFLICT)
-        self.assertFalse(UserPlayerLink.objects.filter(player=self.player).exists())
-
-    def test_provision_player_account_does_not_downgrade_existing_staff_link(self):
-        staff_profile = get_or_create_account_profile(self.staff)
-        staff_profile.role = AccountRole.STAFF
-        staff_profile.save(update_fields=["role", "updated_at"])
-        link_user_to_player(self.staff, self.player)
-
-        result = provision_player_account(self.player, import_batch=self.import_batch)
-        staff_profile.refresh_from_db()
-
-        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
-        self.assertEqual(staff_profile.role, AccountRole.STAFF)
-        self.assertFalse(staff_profile.created_from_import)
-        self.assertIsNone(staff_profile.import_batch)
-
-    def test_provisioning_summary_serializes_safe_counts_without_plaintext_passwords(self):
-        summary = provision_accounts_for_import(
-            self.import_batch,
-            [{"player": self.player, "row_number": 2, "original_row": {"Email": "player@example.com"}}],
-            actor=self.staff,
-            options=ProvisioningOptions(enabled=True, activate_users=False, email_column="Email"),
-        )
-
-        serialized = summary.to_dict()
-        self.assertIsInstance(summary, ProvisioningSummary)
-        self.assertEqual(serialized["users_created"], 1)
-        self.assertEqual(serialized["already_linked"], 0)
-        self.assertNotIn("20120501", str(serialized))
-        self.assertNotIn("password", str(serialized).casefold())
-
-
-class AccountRegressionTests(TestCase):
-    def test_phase_two_creates_user_player_link_but_no_provisioning_models(self):
-        model_names = {model.__name__ for model in AccountProfile._meta.apps.get_models()}
-
-        self.assertIn("AccountProfile", model_names)
-        self.assertIn("UserPlayerLink", model_names)
-        self.assertNotIn("AccountProvisioningBatch", model_names)
-
-    def test_players_player_does_not_gain_direct_user_field(self):
-        self.assertNotIn("user", {field.name for field in Player._meta.fields})
-
-    def test_analytics_evaluation_permission_remains_any_authenticated_user(self):
-        user = User.objects.create_user(username="evaluator", password="testpass")
-
-        self.assertTrue(can_submit_coach_assessment(user))
-        self.assertFalse(can_submit_coach_assessment(None))
-
-
-class AccountAuthRedirectServiceTests(TestCase):
-    def test_landing_url_for_user(self):
-        anonymous = None
-        staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        regular = User.objects.create_user(username="regular", password="testpass")
-
-        self.assertEqual(landing_url_for_user(anonymous), ACCOUNT_LOGIN_PATH)
-        self.assertEqual(landing_url_for_user(staff), ANALYTICS_HOME_PATH)
-        self.assertEqual(landing_url_for_user(regular), ACCOUNT_PROFILE_PATH)
-
-    def test_should_force_password_change(self):
-        user = User.objects.create_user(username="user", password="testpass")
-        profile = get_or_create_account_profile(user)
-
-        self.assertFalse(should_force_password_change(user))
-        profile.must_change_password = True
-        profile.save(update_fields=["must_change_password", "updated_at"])
-        self.assertTrue(should_force_password_change(user))
-
-    def test_missing_account_profile_is_safe(self):
-        user = User.objects.create_user(username="user", password="testpass")
-
-        self.assertFalse(should_force_password_change(user))
-
-    def test_allowed_paths(self):
-        user = User.objects.create_user(username="user", password="testpass")
-        superuser = User.objects.create_superuser(username="admin", password="testpass")
-
-        self.assertTrue(is_password_change_allowed_path(ACCOUNT_PASSWORD_PATH, user))
-        self.assertTrue(is_password_change_allowed_path(ACCOUNT_LOGOUT_PATH, user))
-        self.assertTrue(is_password_change_allowed_path(ACCOUNT_LOGIN_PATH, user))
-        self.assertTrue(is_password_change_allowed_path("/static/app.css", user))
-        self.assertTrue(is_password_change_allowed_path("/media/avatar.png", user))
-        self.assertFalse(is_password_change_allowed_path("/admin/", user))
-        self.assertTrue(is_password_change_allowed_path("/admin/", superuser))
-        self.assertFalse(is_password_change_allowed_path("/analytics/", user))
-
-
-class AccountAuthViewTests(TestCase):
-    def setUp(self):
-        self.user = User.objects.create_user(username="user", password="testpass")
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-
-    def test_login_page_renders(self):
-        response = self.client.get(reverse("accounts:login"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Account Login")
-
-    def test_non_staff_login_lands_at_profile(self):
-        response = self.client.post(
-            reverse("accounts:login"),
-            {"username": "user", "password": "testpass"},
-        )
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], landing_url_for_user(self.user))
-
-    def test_staff_login_lands_at_analytics(self):
-        response = self.client.post(
-            reverse("accounts:login"),
-            {"username": "staff", "password": "testpass"},
-        )
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], landing_url_for_user(self.staff))
-
-    def test_safe_next_parameter_is_respected_without_forced_password_change(self):
-        response = self.client.post(
-            f"{reverse('accounts:login')}?next=/analytics/assessments/",
-            {"username": "user", "password": "testpass"},
-        )
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], "/analytics/assessments/")
-
-    def test_forced_password_change_overrides_next_parameter(self):
-        profile = get_or_create_account_profile(self.user)
-        profile.must_change_password = True
-        profile.save(update_fields=["must_change_password", "updated_at"])
-
-        response = self.client.post(
-            f"{reverse('accounts:login')}?next=/analytics/assessments/",
-            {"username": "user", "password": "testpass"},
-        )
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], ACCOUNT_PASSWORD_PATH)
-
-    def test_logout_redirects_to_account_login(self):
-        self.client.force_login(self.user)
-
-        response = self.client.post(reverse("accounts:logout"))
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], ACCOUNT_LOGIN_PATH)
-
-    def test_password_page_renders_for_authenticated_user(self):
-        self.client.force_login(self.user)
-
-        response = self.client.get(reverse("accounts:password-change"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Update Password")
-
-    def test_password_change_clears_flag_and_keeps_user_logged_in(self):
-        profile = get_or_create_account_profile(self.user)
-        profile.must_change_password = True
-        profile.save(update_fields=["must_change_password", "updated_at"])
-        self.client.force_login(self.user)
-
-        response = self.client.post(
-            reverse("accounts:password-change"),
-            {
-                "old_password": "testpass",
-                "new_password1": "new-strong-pass-123",
-                "new_password2": "new-strong-pass-123",
-            },
-        )
-
-        profile.refresh_from_db()
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], landing_url_for_user(self.user))
-        self.assertFalse(profile.must_change_password)
-        self.assertIn(SESSION_KEY, self.client.session)
-        self.user.refresh_from_db()
-        self.assertTrue(self.user.check_password("new-strong-pass-123"))
-
-        landing_response = self.client.get(response["Location"])
-        self.assertEqual(landing_response.status_code, 200)
-        self.assertNotEqual(landing_response.get("Location"), ACCOUNT_PASSWORD_PATH)
-
-    def test_password_change_redirects_staff_to_landing_service_url(self):
-        profile = get_or_create_account_profile(self.staff)
-        profile.must_change_password = True
-        profile.save(update_fields=["must_change_password", "updated_at"])
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:password-change"),
-            {
-                "old_password": "testpass",
-                "new_password1": "new-strong-pass-123",
-                "new_password2": "new-strong-pass-123",
-            },
-        )
-
-        profile.refresh_from_db()
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], landing_url_for_user(self.staff))
-        self.assertFalse(profile.must_change_password)
-        self.assertIn(SESSION_KEY, self.client.session)
-
-    def test_inactive_user_cannot_login(self):
-        inactive = User.objects.create_user(username="inactive", password="testpass", is_active=False)
-        get_or_create_account_profile(inactive)
-
-        response = self.client.post(
-            reverse("accounts:login"),
-            {"username": "inactive", "password": "testpass"},
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertNotIn(SESSION_KEY, self.client.session)
-
-    def test_profile_page_renders_basic_account_info(self):
-        get_or_create_account_profile(self.user)
-        self.client.force_login(self.user)
-
-        response = self.client.get(reverse("accounts:profile"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Account Profile")
-        self.assertContains(response, "Guest Evaluator")
-
-    def test_profile_submit_evaluation_link_uses_service_permissions(self):
-        cases = [
-            (AccountRole.COACH, True),
-            (AccountRole.PLAYER, True),
-            (AccountRole.GUEST_EVALUATOR, True),
-            (AccountRole.PARENT, False),
-        ]
-        for role, should_see_link in cases:
-            with self.subTest(role=role):
-                user = User.objects.create_user(username=f"profile-{role}", password="testpass")
-                set_account_role(user, role)
-                self.client.force_login(user)
-
-                response = self.client.get(reverse("accounts:profile"))
-
-                if should_see_link:
-                    self.assertContains(response, reverse("analytics:evaluation-list"))
-                    self.assertContains(response, "Submit Evaluation")
-                else:
-                    self.assertNotContains(response, reverse("analytics:evaluation-list"))
-                    self.assertNotContains(response, "Submit Evaluation")
-                self.client.logout()
-
-    def test_profile_my_evaluations_link_requires_self_link(self):
-        player = Player.objects.create(first_name="Linked", last_name="Player")
-        player_user = User.objects.create_user(username="linked-player", password="testpass")
-        coach = User.objects.create_user(username="unlinked-coach", password="testpass")
-        parent = User.objects.create_user(username="unlinked-parent", password="testpass")
-        set_account_role(player_user, AccountRole.PLAYER)
-        set_account_role(coach, AccountRole.COACH)
-        set_account_role(parent, AccountRole.PARENT)
-        link_user_to_player(player_user, player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-
-        self.client.force_login(player_user)
-        response = self.client.get(reverse("accounts:profile"))
-        self.assertContains(response, reverse("analytics:my-evaluations"))
-        self.assertContains(response, "My Evaluations")
-
-        for user in [coach, parent]:
-            with self.subTest(user=user.username):
-                self.client.force_login(user)
-                response = self.client.get(reverse("accounts:profile"))
-                self.assertNotContains(response, reverse("analytics:my-evaluations"))
-                self.client.logout()
-
-
-class CoachImportServiceTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        self.next_season = create_season(key="2027-spring", name="2027 Spring")
-
-    def csv_text(self, rows):
-        return "first_name,last_name,email,username,team,division,is_active,notes,source_id,assignment_role,assignment_start_date,assignment_end_date,assignment_source_id\n" + "\n".join(rows)
-
-    def test_valid_csv_creates_active_coach_with_one_time_password(self):
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,Lead coach,C001"]),
-            season=self.season,
-        )
-
-        user = User.objects.get(email="casey@example.com")
-        profile = user.account_profile
-        result_row = result.rows[0]
-        self.assertEqual(result_row.status, RESULT_CREATED)
-        self.assertEqual(user.username, "casey.coach")
-        self.assertEqual(user.first_name, "Casey")
-        self.assertEqual(user.last_name, "Coach")
-        self.assertTrue(user.is_active)
-        self.assertEqual(profile.role, AccountRole.COACH)
-        self.assertTrue(profile.must_change_password)
-        self.assertEqual(profile.metadata["team"], "Reds")
-        self.assertEqual(profile.metadata["division"], "13U")
-        self.assertTrue(result_row.temporary_password)
-        self.assertTrue(user.check_password(result_row.temporary_password))
-        self.assertNotIn(result_row.temporary_password, repr(result_row))
-        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
-        self.assertEqual(Player.objects.count(), 0)
-        self.assertEqual(result.users_created, 1)
-        self.assertEqual(result.active_accounts, 1)
-        self.assertEqual(result.inactive_accounts, 0)
-        self.assertEqual(result.password_change_required, 1)
-        assignment = CoachSeasonAssignment.objects.select_related("season_team").get(user=user)
-        self.assertEqual(assignment.season_team.season, self.season)
-        self.assertEqual(assignment.season_team.name, "Reds")
-        self.assertEqual(assignment.assignment_role, CoachAssignmentRole.ASSISTANT_COACH)
-        self.assertTrue(assignment.is_primary)
-        self.assertEqual(result.season_teams_created, 1)
-        self.assertEqual(result.assignments_created, 1)
-
-    def test_coach_import_requires_active_season(self):
-        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
-
-        preview = preview_coach_import(self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]))
-        inactive_preview = preview_coach_import(
-            self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]),
-            season=inactive,
-        )
-
-        self.assertEqual(preview.error_count, 1)
-        self.assertIn("Select an active season", preview.row_errors[0])
-        self.assertEqual(inactive_preview.error_count, 1)
-        self.assertIn("Select an active season", inactive_preview.row_errors[0])
-
-    def test_assignment_role_aliases_and_dates_are_persisted(self):
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Head,Coach,head@example.com,,Reds,13U,true,,C001,head,2026-04-01,2026-08-31,A001"]),
-            season=self.season,
-        )
-
-        assignment = CoachSeasonAssignment.objects.get(user__email="head@example.com")
-        self.assertEqual(result.rows[0].assignment_role_label, "Head Coach")
-        self.assertEqual(assignment.assignment_role, CoachAssignmentRole.HEAD_COACH)
-        self.assertEqual(assignment.starts_on.isoformat(), "2026-04-01")
-        self.assertEqual(assignment.ends_on.isoformat(), "2026-08-31")
-        self.assertEqual(assignment.source_identifier, "a001")
-
-    def test_invalid_assignment_role_and_date_range_are_row_errors(self):
-        preview = preview_coach_import(
-            self.csv_text(
-                [
-                    "Bad,Role,bad.role@example.com,,Reds,13U,true,,C001,owner,,,",
-                    "Bad,Dates,bad.dates@example.com,,Reds,13U,true,,C002,assistant,2026-08-31,2026-04-01,",
-                ]
-            ),
-            season=self.season,
-        )
-
-        self.assertEqual(preview.error_count, 2)
-        self.assertIn("Unknown assignment role", preview.rows[0].messages[0])
-        self.assertIn("end date", preview.rows[1].messages[0])
-
-    def test_missing_team_or_division_blocks_row(self):
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(
-                [
-                    "No,Team,no.team@example.com,,,13U,true,,",
-                    "No,Division,no.division@example.com,,Reds,,true,,",
-                ]
-            ),
-            season=self.season,
-        )
-
-        self.assertEqual(result.errors, 2)
-        self.assertFalse(User.objects.filter(email__in=["no.team@example.com", "no.division@example.com"]).exists())
-        self.assertFalse(SeasonTeam.objects.exists())
-
-    def test_imported_coach_can_be_inactive(self):
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Inactive,Coach,inactive.coach@example.com,,Reds,13U,false,,"]),
-            season=self.season,
-        )
-
-        user = User.objects.get(username="inactive.coach")
-        self.assertFalse(user.is_active)
-        self.assertFalse(result.rows[0].is_active)
-        self.assertEqual(result.inactive_accounts, 1)
-
-    def test_explicit_username_is_normalized_and_validated(self):
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["User,Name,user.name@example.com,Explicit.User,Reds,13U,true,,"]),
-            season=self.season,
-        )
-
-        self.assertEqual(result.rows[0].username, "explicit.user")
-        self.assertTrue(User.objects.filter(username="explicit.user").exists())
-
-    def test_generated_username_collision_uses_suffix(self):
-        User.objects.create_user(username="casey.coach", email="other@example.com")
-
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Casey,Coach,casey2@example.com,,Reds,13U,true,,"]),
-            season=self.season,
-        )
-
-        self.assertEqual(result.rows[0].username, "casey.coach2")
-        self.assertTrue(User.objects.filter(username="casey.coach2").exists())
-
-    def test_duplicate_email_with_existing_coach_reuses_account(self):
-        existing = User.objects.create_user(username="existing.coach", email="coach@example.com", password="oldpass")
-        set_account_role(existing, AccountRole.COACH)
-        original_password_hash = existing.password
-
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Existing,Coach,COACH@example.com,,Reds,13U,true,,"]),
-            season=self.season,
-        )
-
-        existing.refresh_from_db()
-        existing.account_profile.refresh_from_db()
-        self.assertEqual(result.rows[0].status, RESULT_REUSED)
-        self.assertEqual(result.existing_coaches_reused, 1)
-        self.assertEqual(User.objects.filter(email__iexact="coach@example.com").count(), 1)
-        self.assertFalse(existing.account_profile.must_change_password)
-        self.assertFalse(result.rows[0].temporary_password)
-        self.assertEqual(existing.password, original_password_hash)
-        self.assertEqual(existing.account_profile.role, AccountRole.COACH)
-        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)
-
-    def test_existing_inactive_coach_is_not_activated_or_reset(self):
-        existing = User.objects.create_user(username="inactive.existing", email="inactive-existing@example.com", password="oldpass", is_active=False)
-        profile = set_account_role(existing, AccountRole.COACH)
-        profile.must_change_password = False
-        profile.save(update_fields=["must_change_password", "updated_at"])
-        original_password_hash = existing.password
-
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Inactive,Existing,inactive-existing@example.com,,Reds,13U,true,,"]),
-            season=self.season,
-        )
-
-        existing.refresh_from_db()
-        profile.refresh_from_db()
-        self.assertEqual(result.rows[0].status, RESULT_REUSED)
-        self.assertFalse(existing.is_active)
-        self.assertEqual(existing.password, original_password_hash)
-        self.assertFalse(result.rows[0].temporary_password)
-        self.assertFalse(profile.must_change_password)
-        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)
-
-    def test_reimport_same_assignment_updates_without_duplicate_or_password_reset(self):
-        first = commit_coach_import(
-            self.staff,
-            self.csv_text(["Return,Coach,return@example.com,,Reds,13U,true,,C001,assistant,,,A001"]),
-            season=self.season,
-        )
-        user = User.objects.get(email="return@example.com")
-        original_password_hash = user.password
-
-        second = commit_coach_import(
-            self.staff,
-            self.csv_text(["Return,Coach,return@example.com,,Reds,13U,true,Updated notes,C001,assistant,2026-04-01,,A001"]),
-            season=self.season,
-        )
-
-        user.refresh_from_db()
-        assignment = CoachSeasonAssignment.objects.get(user=user)
-        self.assertEqual(first.users_created, 1)
-        self.assertEqual(second.existing_coaches_reused, 1)
-        self.assertEqual(second.assignments_updated, 1)
-        self.assertEqual(CoachSeasonAssignment.objects.filter(user=user).count(), 1)
-        self.assertEqual(assignment.starts_on.isoformat(), "2026-04-01")
-        self.assertEqual(user.password, original_password_hash)
-        self.assertFalse(second.rows[0].temporary_password)
-
-    def test_new_season_creates_new_assignment_and_distinct_team(self):
-        commit_coach_import(
-            self.staff,
-            self.csv_text(["Season,Coach,season@example.com,,Reds,13U,true,,"]),
-            season=self.season,
-        )
-        user = User.objects.get(email="season@example.com")
-
-        commit_coach_import(
-            self.staff,
-            self.csv_text(["Season,Coach,season@example.com,,Reds,13U,true,,"]),
-            season=self.next_season,
-        )
-
-        self.assertEqual(CoachSeasonAssignment.objects.filter(user=user).count(), 2)
-        self.assertEqual(SeasonTeam.objects.filter(name="Reds", division="13U").count(), 2)
-
-    def test_same_coach_can_have_multiple_teams_and_roles_without_replacing_primary(self):
-        commit_coach_import(
-            self.staff,
-            self.csv_text(
-                [
-                    "Multi,Coach,multi@example.com,,Reds,13U,true,,C001,head,,,",
-                    "Multi,Coach,multi@example.com,,Blues,13U,true,,C002,assistant,,,",
-                    "Multi,Coach,multi@example.com,,Reds,13U,true,,C003,evaluator,,,",
-                ]
-            ),
-            season=self.season,
-        )
-        user = User.objects.get(email="multi@example.com")
-        assignments = CoachSeasonAssignment.objects.filter(user=user, season_team__season=self.season)
-
-        self.assertEqual(assignments.count(), 3)
-        self.assertEqual(assignments.filter(is_primary=True).count(), 1)
-        self.assertEqual(assignments.get(is_primary=True).assignment_role, CoachAssignmentRole.HEAD_COACH)
-
-    def test_csv_season_mismatch_is_rejected(self):
-        preview = preview_coach_import(
-            "first_name,last_name,email,team,division,season\nMismatch,Coach,mismatch@example.com,Reds,13U,2027 Spring\n",
-            season=self.season,
-        )
-
-        self.assertEqual(preview.rows[0].status, "error")
-        self.assertIn("season does not match", preview.rows[0].messages[0])
-
-    def test_duplicate_email_with_non_coach_conflicts(self):
-        existing = User.objects.create_user(username="player.user", email="shared@example.com")
-        set_account_role(existing, AccountRole.PLAYER)
-
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Shared,Coach,shared@example.com,,Reds,13U,true,,"]),
-            season=self.season,
-        )
-
-        self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
-        self.assertEqual(result.conflicts, 1)
-        self.assertEqual(User.objects.count(), 2)
-        self.assertFalse(CoachSeasonAssignment.objects.exists())
-
-    def test_explicit_duplicate_username_conflicts(self):
-        User.objects.create_user(username="taken.name")
-
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Taken,Name,taken@example.com,taken.name,Reds,13U,true,,"]),
-            season=self.season,
-        )
-
-        self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
-        self.assertFalse(User.objects.filter(email="taken@example.com").exists())
-
-    def test_duplicate_email_reuses_created_coach_but_duplicate_username_conflicts(self):
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(
-                [
-                    "First,Coach,first@example.com,same.username,Reds,13U,true,,",
-                    "Second,Coach,first@example.com,other.username,Reds,13U,true,,",
-                    "Third,Coach,third@example.com,same.username,Reds,13U,true,,",
-                ]
-            ),
-            season=self.season,
-        )
-
-        self.assertEqual(result.users_created, 1)
-        self.assertEqual(result.existing_coaches_reused, 1)
-        self.assertEqual(result.conflicts, 1)
-        self.assertTrue(User.objects.filter(email="first@example.com").exists())
-        self.assertFalse(User.objects.filter(email="third@example.com").exists())
-        self.assertEqual(CoachSeasonAssignment.objects.filter(user__email="first@example.com").count(), 1)
-
-    def test_blank_csv_fields_do_not_wipe_existing_metadata(self):
-        existing = User.objects.create_user(username="metadata.coach", email="metadata@example.com")
-        profile = set_account_role(existing, AccountRole.COACH)
-        profile.metadata = {"team": "Reds", "division": "13U", "notes": "Keep this", "custom": "value"}
-        profile.save(update_fields=["metadata", "updated_at"])
-
-        result = commit_coach_import(
-            self.staff,
-            self.csv_text(["Metadata,Coach,metadata@example.com,,Reds,13U,true,,"]),
-            season=self.season,
-        )
-
-        profile.refresh_from_db()
-        self.assertEqual(result.rows[0].status, RESULT_REUSED)
-        self.assertEqual(profile.metadata["team"], "Reds")
-        self.assertEqual(profile.metadata["division"], "13U")
-        self.assertEqual(profile.metadata["notes"], "Keep this")
-        self.assertEqual(profile.metadata["custom"], "value")
-        self.assertFalse(result.rows[0].temporary_password)
-        self.assertFalse(profile.created_from_import)
-        self.assertIsNone(profile.import_batch)
-
-    def test_missing_required_fields_produce_row_errors(self):
-        preview = preview_coach_import("first_name,last_name,email,team,division\nMissing,Email,,Reds,13U\n", season=self.season)
-        result = commit_coach_import(self.staff, "first_name,last_name,email,team,division\nMissing,Email,,Reds,13U\n", season=self.season)
-
-        self.assertEqual(preview.rows[0].status, "error")
-        self.assertIn("Missing required field", preview.rows[0].messages[0])
-        self.assertEqual(result.errors, 1)
-        self.assertEqual(User.objects.count(), 1)
-
-    def test_missing_required_columns_produce_import_error(self):
-        result = commit_coach_import(self.staff, "first_name,last_name\nNo,Email\n", season=self.season)
-
-        self.assertEqual(result.errors, 1)
-        self.assertIn("Missing required column", result.rows[0].messages[0])
-
-    def test_regular_user_cannot_commit_coach_import(self):
-        regular = User.objects.create_user(username="regular", password="testpass")
-
-        with self.assertRaisesMessage(ValidationError, "Only staff users can import coaches"):
-            commit_coach_import(regular, self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]), season=self.season)
-
-    def test_username_for_person_uses_same_normalization_style(self):
-        self.assertEqual(base_username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne")
-        self.assertEqual(username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne")
-
-
-class AccountOperationsViewTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.superuser = User.objects.create_superuser(username="admin", password="testpass")
-        self.regular = User.objects.create_user(username="regular", password="testpass")
-        self.coach = User.objects.create_user(
-            username="coach.one",
-            password="testpass",
-            first_name="Coach",
-            last_name="One",
-            email="coach@example.com",
-        )
-        set_account_role(self.coach, AccountRole.COACH)
-        profile = get_or_create_account_profile(self.regular)
-        profile.role = AccountRole.STAFF
-        profile.save(update_fields=["role", "updated_at"])
-        self.player = Player.objects.create(first_name="Alex", last_name="Player")
-        link_user_to_player(self.coach, self.player, relationship=UserPlayerRelationship.COACH, is_primary=False)
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-
-    def test_dashboard_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:operations-dashboard"))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_superuser_can_access_dashboard(self):
-        self.client.force_login(self.superuser)
-
-        response = self.client.get(reverse("accounts:operations-dashboard"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Account Operations")
-
-    def test_dashboard_renders_expected_summary_cards(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("accounts:operations-dashboard"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Total accounts")
-        self.assertContains(response, "Active accounts")
-        self.assertContains(response, "Inactive accounts")
-        self.assertContains(response, "Password change required")
-        self.assertContains(response, "Users without player links")
-        self.assertContains(response, "Players without self-linked accounts")
-        self.assertContains(response, reverse("accounts:account-create"))
-        self.assertContains(response, reverse("accounts:player-account-create"))
-        self.assertContains(response, reverse("accounts:coach-import-list"))
-
-    def test_user_list_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:user-list"))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_user_list_renders_users_and_filters(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("accounts:user-list"), {"q": "coach", "role": AccountRole.COACH})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Account Users")
-        self.assertContains(response, "coach.one")
-        self.assertContains(response, "Coach")
-        self.assertNotContains(response, "regular")
-        self.assertContains(response, "Bulk action")
-        self.assertContains(response, "Select all accounts shown")
-
-    def test_user_list_bulk_post_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.post(
-            reverse("accounts:user-list"),
-            {"action": "activate", "user_ids": [self.coach.id], "visible_user_ids": [self.coach.id]},
-        )
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_staff_can_bulk_activate_from_user_list(self):
-        self.coach.is_active = False
-        self.coach.save(update_fields=["is_active"])
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-list"),
-            {"action": "activate", "user_ids": [self.coach.id], "visible_user_ids": [self.coach.id]},
-        )
-
-        self.coach.refresh_from_db()
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "1 succeeded, 0 failed")
-        self.assertTrue(self.coach.is_active)
-
-    def test_staff_can_bulk_require_and_clear_password_change_from_user_list(self):
-        mark_password_change_required(self.coach, False)
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-list"),
-            {
-                "action": "require_password_change",
-                "user_ids": [self.coach.id],
-                "visible_user_ids": [self.coach.id],
-            },
-        )
-
-        self.coach.refresh_from_db()
-        self.assertEqual(response.status_code, 200)
-        self.assertTrue(self.coach.account_profile.must_change_password)
-
-        response = self.client.post(
-            reverse("accounts:user-list"),
-            {
-                "action": "clear_password_change",
-                "user_ids": [self.coach.id],
-                "visible_user_ids": [self.coach.id],
-            },
-        )
-
-        self.coach.refresh_from_db()
-        self.assertEqual(response.status_code, 200)
-        self.assertFalse(self.coach.account_profile.must_change_password)
-
-    def test_staff_bulk_deactivate_reports_self_failure_and_successes(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-list"),
-            {
-                "action": "deactivate",
-                "user_ids": [self.staff.id, self.coach.id],
-                "visible_user_ids": [self.staff.id, self.coach.id],
-            },
-        )
-
-        self.staff.refresh_from_db()
-        self.coach.refresh_from_db()
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "1 succeeded, 1 failed")
-        self.assertContains(response, "staff")
-        self.assertContains(response, "cannot deactivate your own account")
-        self.assertTrue(self.staff.is_active)
-        self.assertFalse(self.coach.is_active)
-
-    def test_staff_bulk_action_rejects_empty_selection_and_unknown_action(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-list"),
-            {"action": "activate", "visible_user_ids": [self.coach.id]},
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Select at least one account")
-
-        response = self.client.post(
-            reverse("accounts:user-list"),
-            {"action": "unsupported", "user_ids": [self.coach.id], "visible_user_ids": [self.coach.id]},
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Select a valid choice")
-
-    def test_staff_bulk_select_all_uses_visible_user_ids(self):
-        self.coach.is_active = False
-        self.coach.save(update_fields=["is_active"])
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-list"),
-            {"action": "activate", "select_all": "on", "visible_user_ids": [self.coach.id]},
-        )
-
-        self.coach.refresh_from_db()
-        self.assertEqual(response.status_code, 200)
-        self.assertTrue(self.coach.is_active)
-
-    def test_user_detail_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_user_detail_missing_account_returns_404(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": 999999}))
-
-        self.assertEqual(response.status_code, 404)
-
-    def test_user_detail_renders_profile_and_linked_players(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "coach.one")
-        self.assertContains(response, "coach@example.com")
-        self.assertContains(response, "Coach")
-        self.assertContains(response, "Alex Player")
-        self.assertContains(response, reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))
-        self.assertContains(response, reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))
-        self.assertContains(response, reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}))
-
-    def test_user_edit_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_staff_can_edit_account_lifecycle_username_and_role(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
-            {
-                "username": " Coach.Updated ",
-                "first_name": "Updated",
-                "last_name": "Coach",
-                "email": "updated@example.com",
-                "role": AccountRole.GUEST_EVALUATOR,
-            },
-        )
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
-        self.coach.refresh_from_db()
-        self.assertEqual(self.coach.username, "coach.updated")
-        self.assertFalse(self.coach.is_active)
-        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
-        self.assertFalse(self.coach.is_staff)
-        self.assertFalse(self.coach.is_superuser)
-
-    def test_staff_user_edit_rejects_duplicate_username_and_admin_role(self):
-        User.objects.create_user(username="taken")
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
-            {
-                "username": "taken",
-                "role": AccountRole.COACH,
-                "is_active": "on",
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Username is already in use")
-
-        response = self.client.post(
-            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
-            {
-                "username": "coach.one",
-                "role": AccountRole.ADMIN,
-                "is_active": "on",
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Only superusers can assign admin role")
-        self.coach.refresh_from_db()
-        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
-
-    def test_staff_user_edit_rejects_staff_or_superuser_target(self):
-        other_staff = User.objects.create_user(username="other.staff", password="testpass", is_staff=True)
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-edit", kwargs={"user_id": other_staff.id}),
-            {
-                "username": "other.staff",
-                "role": AccountRole.STAFF,
-                "is_active": "on",
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Only superusers can manage staff or superuser accounts")
-
-    def test_user_links_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:user-links", kwargs={"user_id": self.coach.id}))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_staff_can_create_deactivate_and_reactivate_link(self):
-        other_player = Player.objects.create(first_name="Blake", last_name="Player")
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
-            {
-                "action": "create",
-                "player": other_player.id,
-                "relationship": UserPlayerRelationship.PARENT,
-            },
-        )
-
-        self.assertEqual(response.status_code, 302)
-        link = UserPlayerLink.objects.get(user=self.coach, player=other_player, relationship=UserPlayerRelationship.PARENT)
-        self.assertTrue(link.is_active)
-        self.assertFalse(link.is_primary)
-
-        response = self.client.post(
-            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
-            {"action": "deactivate", "link_id": link.id},
-        )
-        self.assertEqual(response.status_code, 302)
-        link.refresh_from_db()
-        self.assertFalse(link.is_active)
-
-        response = self.client.post(
-            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
-            {"action": "reactivate", "link_id": link.id},
-        )
-        self.assertEqual(response.status_code, 302)
-        link.refresh_from_db()
-        self.assertTrue(link.is_active)
-
-    def test_staff_can_set_primary_self_link_from_links_page(self):
-        first_player = Player.objects.create(first_name="Self", last_name="One")
-        second_player = Player.objects.create(first_name="Self", last_name="Two")
-        first_link = link_user_to_player(self.coach, first_player, relationship=UserPlayerRelationship.SELF)
-        second_link = link_user_to_player(
-            self.coach,
-            second_player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=False,
-        )
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
-            {"action": "set_primary", "link_id": second_link.id},
-        )
-
-        self.assertEqual(response.status_code, 302)
-        first_link.refresh_from_db()
-        second_link.refresh_from_db()
-        self.assertFalse(first_link.is_primary)
-        self.assertTrue(second_link.is_primary)
-
-    def test_links_page_rejects_duplicate_active_link(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
-            {
-                "action": "create",
-                "player": self.player.id,
-                "relationship": UserPlayerRelationship.COACH,
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "An active link already exists")
-
-    def test_links_page_handles_invalid_link_id_as_form_error(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
-            {"action": "deactivate", "link_id": "999999"},
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Player link not found")
-
-    def test_links_page_handles_unknown_action_as_form_error(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
-            {"action": "unsupported", "link_id": "1"},
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Unsupported link action")
-
-    def test_password_reset_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_staff_can_reset_non_player_password_and_see_password_once(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}),
-            {"confirm": "on"},
-        )
-
-        self.coach.refresh_from_db()
-        temporary_password = response.context["password_reset_result"].temporary_password
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Password Reset Complete")
-        self.assertContains(response, temporary_password)
-        self.assertTrue(self.coach.check_password(temporary_password))
-        self.assertTrue(self.coach.account_profile.must_change_password)
-        self.assertNotIn(temporary_password, " ".join(str(message) for message in get_messages(response.wsgi_request)))
-
-        refresh_response = self.client.get(reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}))
-        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}))
-        self.assertNotContains(refresh_response, temporary_password)
-        self.assertNotContains(detail_response, temporary_password)
-
-    def test_staff_can_reset_player_password_with_birthdate_password(self):
-        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
-        user = User.objects.create_user(username="blake.player", password="testpass")
-        set_account_role(user, AccountRole.PLAYER)
-        link_user_to_player(user, player)
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-password-reset", kwargs={"user_id": user.id}),
-            {"confirm": "on"},
-        )
-
-        user.refresh_from_db()
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "20130602")
-        self.assertTrue(user.check_password("20130602"))
-        self.assertTrue(user.account_profile.must_change_password)
-
-    def test_password_reset_does_not_run_without_confirmation(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}), {})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "This field is required")
-        self.coach.refresh_from_db()
-        self.assertTrue(self.coach.check_password("testpass"))
-
-    def test_password_reset_missing_account_returns_404(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("accounts:user-password-reset", kwargs={"user_id": 999999}))
-
-        self.assertEqual(response.status_code, 404)
-
-    def test_staff_password_reset_rejects_staff_or_superuser_target(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:user-password-reset", kwargs={"user_id": self.superuser.id}),
-            {"confirm": "on"},
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Only superusers can manage staff or superuser accounts")
-        self.superuser.refresh_from_db()
-        self.assertTrue(self.superuser.check_password("testpass"))
-
-    def test_profile_page_links_staff_to_account_operations(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("accounts:profile"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, reverse("accounts:operations-dashboard"))
-
-    def test_profile_page_does_not_link_regular_user_to_account_operations(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:profile"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertNotContains(response, reverse("accounts:operations-dashboard"))
-
-    def test_account_create_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:account-create"))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_staff_can_create_account_only_and_see_one_time_password(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:account-create"),
-            {
-                "username": "new.evaluator",
-                "first_name": "New",
-                "last_name": "Evaluator",
-                "email": "new@example.com",
-                "role": AccountRole.GUEST_EVALUATOR,
-                "is_active": "on",
-            },
-        )
-
-        user = User.objects.get(username="new.evaluator")
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Account Created")
-        self.assertContains(response, "Temporary password")
-        temporary_password = response.context["created_account"].temporary_password
-        self.assertIn(temporary_password, response.content.decode())
-        self.assertNotIn(temporary_password, " ".join(str(message) for message in get_messages(response.wsgi_request)))
-        self.assertTrue(user.account_profile.must_change_password)
-        self.assertEqual(user.account_profile.role, AccountRole.GUEST_EVALUATOR)
-        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
-
-        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
-        self.assertNotContains(detail_response, temporary_password)
-        get_response = self.client.get(reverse("accounts:account-create"))
-        self.assertNotContains(get_response, temporary_password)
-
-    def test_staff_cannot_create_admin_account(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:account-create"),
-            {
-                "username": "admin.try",
-                "role": AccountRole.ADMIN,
-                "is_active": "on",
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Only superusers can create admin accounts")
-        self.assertNotContains(response, "Temporary password")
-        self.assertFalse(User.objects.filter(username="admin.try").exists())
-
-    def test_player_account_create_requires_staff(self):
-        self.client.force_login(self.regular)
-
-        response = self.client.get(reverse("accounts:player-account-create"))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_staff_can_create_player_account_for_existing_player(self):
-        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:player-account-create"),
-            {
-                "player": player.id,
-                "email": "blake@example.com",
-                "role": AccountRole.PLAYER,
-                "is_active": "on",
-            },
-        )
-
-        user = User.objects.get(username="blake.player")
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Player Account Created")
-        self.assertContains(response, "20130602")
-        self.assertNotIn("20130602", " ".join(str(message) for message in get_messages(response.wsgi_request)))
-        self.assertTrue(user.check_password("20130602"))
-        self.assertTrue(user.account_profile.must_change_password)
-        self.assertEqual(UserPlayerLink.objects.get(user=user).player, player)
-
-        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
-        self.assertNotContains(detail_response, "20130602")
-        get_response = self.client.get(reverse("accounts:player-account-create"))
-        self.assertNotContains(get_response, "20130602")
-
-    def test_player_account_create_rejects_duplicate_player_account(self):
-        player = Player.objects.create(first_name="Blake", last_name="Player", birthdate="2013-06-02")
-        create_player_account(actor=self.staff, player=player)
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("accounts:player-account-create"),
-            {
-                "player": player.id,
-                "role": AccountRole.PLAYER,
-                "is_active": "on",
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Player already has a linked user account")
-        self.assertEqual(UserPlayerLink.objects.filter(player=player, relationship=UserPlayerRelationship.SELF).count(), 1)
-
-    def test_coach_import_pages_require_staff(self):
-        self.client.force_login(self.regular)
-
-        urls = [
-            reverse("accounts:coach-import-list"),
-            reverse("accounts:coach-import-new"),
-            reverse("accounts:coach-import-preview"),
-            reverse("accounts:coach-import-confirm"),
-        ]
-
-        for url in urls:
-            response = self.client.get(url)
-            self.assertEqual(response.status_code, 403)
-
-    def test_staff_can_preview_and_confirm_coach_import(self):
-        self.client.force_login(self.staff)
-        csv_file = SimpleUploadedFile(
-            "coaches.csv",
-            b"first_name,last_name,email,team,division\nNew,Coach,new.coach@example.com,Reds,13U\n",
-            content_type="text/csv",
-        )
-
-        upload_response = self.client.post(reverse("accounts:coach-import-new"), {"season": str(self.season.id), "csv_file": csv_file})
-        self.assertEqual(upload_response.status_code, 302)
-        self.assertEqual(upload_response["Location"], reverse("accounts:coach-import-preview"))
-
-        preview_response = self.client.get(reverse("accounts:coach-import-preview"))
-        self.assertEqual(preview_response.status_code, 200)
-        self.assertContains(preview_response, "Ready to create")
-        self.assertContains(preview_response, "new.coach@example.com")
-
-        confirm_response = self.client.post(reverse("accounts:coach-import-confirm"), {"confirm": "on"})
-        self.assertEqual(confirm_response.status_code, 200)
-        self.assertContains(confirm_response, "Coach Import Result")
-        self.assertContains(confirm_response, "Temporary password")
-        user = User.objects.get(username="new.coach")
-        temporary_password = confirm_response.context["result"].rows[0].temporary_password
-        self.assertTrue(user.check_password(temporary_password))
-        self.assertTrue(user.is_active)
-        self.assertEqual(user.account_profile.role, AccountRole.COACH)
-        self.assertTrue(user.account_profile.must_change_password)
-        self.assertEqual(CoachSeasonAssignment.objects.filter(user=user, season_team__season=self.season).count(), 1)
-        self.assertFalse(user.is_staff)
-        self.assertFalse(user.is_superuser)
-        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
-        self.assertEqual(Player.objects.count(), 1)
-        self.assertNotIn("coach_import_csv", self.client.session)
-
-        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": user.id}))
-        self.assertNotContains(detail_response, temporary_password)
-        list_response = self.client.get(reverse("accounts:coach-import-list"))
-        self.assertNotContains(list_response, temporary_password)
-        preview_again = self.client.get(reverse("accounts:coach-import-preview"))
-        self.assertEqual(preview_again.status_code, 302)
-        confirm_again = self.client.get(reverse("accounts:coach-import-confirm"))
-        self.assertEqual(confirm_again.status_code, 302)
-
-    def test_coach_import_preview_rejects_manipulated_inactive_season(self):
-        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
-        self.client.force_login(self.staff)
-        session = self.client.session
-        session["coach_import_csv"] = "first_name,last_name,email,team,division\nBad,Season,bad.season@example.com,Reds,13U\n"
-        session["coach_import_season_id"] = inactive.id
-        session.save()
-
-        preview_response = self.client.get(reverse("accounts:coach-import-preview"))
-        confirm_response = self.client.post(reverse("accounts:coach-import-confirm"), {"confirm": "on"})
-
-        self.assertEqual(preview_response.status_code, 302)
-        self.assertEqual(preview_response["Location"], reverse("accounts:coach-import-new"))
-        self.assertEqual(confirm_response.status_code, 302)
-        self.assertFalse(User.objects.filter(email="bad.season@example.com").exists())
-
-    def test_coach_import_reuses_existing_coach_and_blocks_non_coach_email(self):
-        existing_coach = User.objects.create_user(username="existing.coach", email="existing@example.com")
-        set_account_role(existing_coach, AccountRole.COACH)
-        existing_player = User.objects.create_user(username="existing.player", email="player@example.com")
-        set_account_role(existing_player, AccountRole.PLAYER)
-        self.client.force_login(self.staff)
-        csv_file = SimpleUploadedFile(
-            "coaches.csv",
-            (
-                "first_name,last_name,email,team,division\n"
-                "Existing,Coach,existing@example.com,Reds,13U\n"
-                "Existing,Player,player@example.com,Reds,13U\n"
-            ).encode(),
-            content_type="text/csv",
-        )
-
-        self.client.post(reverse("accounts:coach-import-new"), {"season": str(self.season.id), "csv_file": csv_file})
-        response = self.client.post(reverse("accounts:coach-import-confirm"), {"confirm": "on"})
-
-        self.assertEqual(response.status_code, 200)
-        result = response.context["result"]
-        self.assertEqual(result.existing_coaches_reused, 1)
-        self.assertEqual(result.conflicts, 1)
-        temporary_password = result.rows[0].temporary_password
-        existing_coach.refresh_from_db()
-        self.assertFalse(temporary_password)
-        self.assertFalse(existing_coach.account_profile.must_change_password)
-        self.assertEqual(existing_coach.account_profile.role, AccountRole.COACH)
-        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing_coach, season_team__season=self.season).count(), 1)
-        self.assertEqual(User.objects.filter(email__iexact="existing@example.com").count(), 1)
-        self.assertEqual(User.objects.filter(email__iexact="player@example.com").count(), 1)
-
-        detail_response = self.client.get(reverse("accounts:user-detail", kwargs={"user_id": existing_coach.id}))
-        self.assertNotContains(detail_response, "Password unchanged")
-
-
-class AccountPasswordMiddlewareTests(TestCase):
-    def setUp(self):
-        self.user = User.objects.create_user(username="user", password="testpass")
-        self.profile = get_or_create_account_profile(self.user)
-
-    def require_password_change(self):
-        self.profile.must_change_password = True
-        self.profile.save(update_fields=["must_change_password", "updated_at"])
-        self.client.force_login(self.user)
-
-    def test_forced_password_user_redirected_from_normal_page(self):
-        self.require_password_change()
-
-        response = self.client.get(reverse("analytics:assessment-list"))
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], ACCOUNT_PASSWORD_PATH)
-
-    def test_allowed_paths_do_not_redirect_loop(self):
-        self.require_password_change()
-
-        self.assertEqual(self.client.get(reverse("accounts:password-change")).status_code, 200)
-        self.assertNotEqual(self.client.get(reverse("accounts:login")).status_code, 302)
-        self.assertEqual(self.client.post(reverse("accounts:logout")).status_code, 302)
-
-    def test_password_page_post_is_not_blocked_by_middleware(self):
-        self.require_password_change()
-
-        response = self.client.post(
-            reverse("accounts:password-change"),
-            {
-                "old_password": "wrong-password",
-                "new_password1": "new-strong-pass-123",
-                "new_password2": "new-strong-pass-123",
-            },
-        )
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Update Password")
-
-    def test_middleware_does_not_redirect_after_successful_password_change(self):
-        self.require_password_change()
-
-        response = self.client.post(
-            reverse("accounts:password-change"),
-            {
-                "old_password": "testpass",
-                "new_password1": "new-strong-pass-123",
-                "new_password2": "new-strong-pass-123",
-            },
-        )
-
-        self.profile.refresh_from_db()
-        self.assertEqual(response.status_code, 302)
-        self.assertFalse(self.profile.must_change_password)
-        profile_response = self.client.get(reverse("accounts:profile"))
-        self.assertEqual(profile_response.status_code, 200)
-
-    def test_static_media_and_superuser_admin_paths_are_allowed(self):
-        superuser = User.objects.create_superuser(username="admin", password="testpass")
-        profile = get_or_create_account_profile(superuser)
-        profile.must_change_password = True
-        profile.save(update_fields=["must_change_password", "updated_at"])
-        self.client.force_login(superuser)
-
-        self.assertNotEqual(self.client.get("/static/app.css").status_code, 302)
-        self.assertNotEqual(self.client.get("/media/app.png").status_code, 302)
-        self.assertNotEqual(self.client.get("/admin/").status_code, 302)
-
-    def test_user_without_forced_password_change_is_not_redirected(self):
-        self.client.force_login(self.user)
-
-        response = self.client.get(reverse("accounts:profile"))
-
-        self.assertEqual(response.status_code, 200)
-
-    def test_missing_account_profile_is_safe(self):
-        user = User.objects.create_user(username="missing-profile", password="testpass")
-        self.client.force_login(user)
-
-        response = self.client.get(reverse("accounts:profile"))
-
-        self.assertEqual(response.status_code, 200)
-
-
-class AccountPdpCoexistenceTests(TestCase):
-    def test_pdp_login_route_still_renders(self):
-        response = self.client.get(reverse("pdp:login"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Athlete Login")
-
-    def test_pdp_routes_and_middleware_remain_installed(self):
-        self.assertEqual(reverse("pdp:login"), "/pdp/login/")
-        self.assertIn("pdp.middleware.FirstLoginPasswordChangeMiddleware", settings.MIDDLEWARE)
-        self.assertIn("accounts.middleware.AccountPasswordChangeRequiredMiddleware", settings.MIDDLEWARE)
-        self.assertLess(
-            settings.MIDDLEWARE.index("pdp.middleware.FirstLoginPasswordChangeMiddleware"),
-            settings.MIDDLEWARE.index("accounts.middleware.AccountPasswordChangeRequiredMiddleware"),
-        )
-
-    def test_global_login_settings_are_account_forward(self):
-        self.assertEqual(settings.LOGIN_URL, ACCOUNT_LOGIN_PATH)
-        self.assertEqual(settings.LOGIN_REDIRECT_URL, ACCOUNT_PROFILE_PATH)
-
-    def test_account_operations_routes_are_platform_account_routes(self):
-        self.assertEqual(reverse("accounts:operations-dashboard"), "/accounts/")
-        self.assertEqual(reverse("accounts:user-list"), "/accounts/users/")
diff --git a/accounts/tests/__init__.py b/accounts/tests/__init__.py
new file mode 100644
index 0000000..e69de29
diff --git a/accounts/tests/helpers.py b/accounts/tests/helpers.py
new file mode 100644
index 0000000..738d53d
--- /dev/null
+++ b/accounts/tests/helpers.py
@@ -0,0 +1,227 @@
+from django.conf import settings
+from django.contrib import admin
+from django.contrib.auth import SESSION_KEY, get_user_model
+from django.contrib.messages import get_messages
+from django.core.exceptions import ValidationError
+from django.core.files.uploadedfile import SimpleUploadedFile
+from django.db import IntegrityError, transaction
+from django.test import TestCase
+from django.urls import reverse
+
+from accounts.models import (
+    AccountProfile,
+    AccountRole,
+    UserPlayerLink,
+    UserPlayerRelationship,
+)
+from accounts.services.account_operations_service import (
+    activate_account,
+    bulk_account_operation,
+    create_account_only,
+    create_player_account,
+    create_user_player_link,
+    deactivate_account,
+    deactivate_user_player_link,
+    get_account_detail,
+    get_account_list,
+    get_account_operations_dashboard,
+    reactivate_user_player_link,
+    reset_account_password,
+    set_primary_user_player_link,
+    update_account,
+)
+from accounts.services.account_query_service import (
+    AccountListFilters,
+    count_players_without_self_link,
+    filter_account_users,
+)
+from accounts.services.auth_redirect_service import (
+    ACCOUNT_LOGIN_PATH,
+    ACCOUNT_LOGOUT_PATH,
+    ACCOUNT_PASSWORD_PATH,
+    ACCOUNT_PROFILE_PATH,
+    ANALYTICS_HOME_PATH,
+    is_password_change_allowed_path,
+    landing_url_for_user,
+    should_force_password_change,
+)
+from accounts.services.coach_import_service import (
+    RESULT_CONFLICT,
+    RESULT_CREATED,
+    RESULT_REUSED,
+    commit_coach_import,
+    preview_coach_import,
+)
+from accounts.services.email_service import (
+    emails_equal,
+    find_existing_email_user,
+    normalize_email,
+)
+from accounts.services.link_service import (
+    activate_link,
+    deactivate_link,
+    get_players_for_user,
+    get_primary_player,
+    get_primary_user,
+    get_users_for_player,
+    is_player_self,
+    link_user_to_player,
+    set_primary_self_link,
+    unlink_user_from_player,
+)
+from accounts.services.password_service import (
+    generate_birthdate_password,
+    generate_random_temporary_password,
+    mark_password_change_required,
+    set_temporary_password,
+)
+from accounts.services.permissions import (
+    can_access_account_operations,
+    can_change_account_role,
+    can_manage_accounts,
+    can_manage_privileged_accounts,
+    can_submit_evaluations,
+    can_view_account_detail,
+    can_view_account_list,
+    can_view_account_operations_dashboard,
+    can_view_account_profile,
+)
+from accounts.services.profile_service import (
+    get_account_role,
+    get_or_create_account_profile,
+    set_account_role,
+)
+from accounts.services.provisioning_service import (
+    STATUS_ALREADY_LINKED,
+    STATUS_CONFLICT,
+    STATUS_CREATED,
+    STATUS_SKIPPED,
+    ProvisioningOptions,
+    ProvisioningSummary,
+    provision_accounts_for_import,
+    provision_player_account,
+)
+from accounts.services.role_service import (
+    default_role_for_user,
+    role_for_user,
+    role_label,
+    validate_role,
+)
+from accounts.services.username_service import (
+    base_username_for_person,
+    base_username_for_player,
+    normalize_username_part,
+    username_for_person,
+    username_for_player,
+    validate_available_username,
+    validate_available_username_for_user,
+)
+from analytics.services.permissions import can_submit_coach_assessment
+from players.models import Player, PlayerImportBatch
+from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, SeasonTeam
+from seasons.services.season_service import create_season
+
+User = get_user_model()
+
+__all__ = (
+    "ACCOUNT_LOGIN_PATH",
+    "ACCOUNT_LOGOUT_PATH",
+    "ACCOUNT_PASSWORD_PATH",
+    "ACCOUNT_PROFILE_PATH",
+    "ANALYTICS_HOME_PATH",
+    "AccountListFilters",
+    "AccountProfile",
+    "AccountRole",
+    "CoachAssignmentRole",
+    "CoachSeasonAssignment",
+    "IntegrityError",
+    "Player",
+    "PlayerImportBatch",
+    "ProvisioningOptions",
+    "ProvisioningSummary",
+    "RESULT_CONFLICT",
+    "RESULT_CREATED",
+    "RESULT_REUSED",
+    "SESSION_KEY",
+    "STATUS_ALREADY_LINKED",
+    "STATUS_CONFLICT",
+    "STATUS_CREATED",
+    "STATUS_SKIPPED",
+    "SeasonTeam",
+    "SimpleUploadedFile",
+    "TestCase",
+    "User",
+    "UserPlayerLink",
+    "UserPlayerRelationship",
+    "ValidationError",
+    "activate_account",
+    "activate_link",
+    "admin",
+    "base_username_for_person",
+    "base_username_for_player",
+    "bulk_account_operation",
+    "can_access_account_operations",
+    "can_change_account_role",
+    "can_manage_accounts",
+    "can_manage_privileged_accounts",
+    "can_submit_coach_assessment",
+    "can_submit_evaluations",
+    "can_view_account_detail",
+    "can_view_account_list",
+    "can_view_account_operations_dashboard",
+    "can_view_account_profile",
+    "commit_coach_import",
+    "count_players_without_self_link",
+    "create_account_only",
+    "create_player_account",
+    "create_season",
+    "create_user_player_link",
+    "deactivate_account",
+    "deactivate_link",
+    "deactivate_user_player_link",
+    "default_role_for_user",
+    "emails_equal",
+    "filter_account_users",
+    "find_existing_email_user",
+    "generate_birthdate_password",
+    "generate_random_temporary_password",
+    "get_account_detail",
+    "get_account_list",
+    "get_account_operations_dashboard",
+    "get_account_role",
+    "get_messages",
+    "get_or_create_account_profile",
+    "get_players_for_user",
+    "get_primary_player",
+    "get_primary_user",
+    "get_users_for_player",
+    "is_password_change_allowed_path",
+    "is_player_self",
+    "landing_url_for_user",
+    "link_user_to_player",
+    "mark_password_change_required",
+    "normalize_email",
+    "normalize_username_part",
+    "preview_coach_import",
+    "provision_accounts_for_import",
+    "provision_player_account",
+    "reactivate_user_player_link",
+    "reset_account_password",
+    "reverse",
+    "role_for_user",
+    "role_label",
+    "set_account_role",
+    "set_primary_self_link",
+    "set_primary_user_player_link",
+    "set_temporary_password",
+    "settings",
+    "should_force_password_change",
+    "transaction",
+    "unlink_user_from_player",
+    "update_account",
+    "username_for_person",
+    "username_for_player",
+    "validate_available_username",
+    "validate_available_username_for_user",
+    "validate_role",
+)
diff --git a/accounts/tests/test_account_operations.py b/accounts/tests/test_account_operations.py
new file mode 100644
index 0000000..3012878
--- /dev/null
+++ b/accounts/tests/test_account_operations.py
@@ -0,0 +1,1622 @@
+from accounts.tests.helpers import (
+    AccountListFilters,
+    AccountRole,
+    CoachSeasonAssignment,
+    Player,
+    PlayerImportBatch,
+    SimpleUploadedFile,
+    TestCase,
+    User,
+    UserPlayerLink,
+    UserPlayerRelationship,
+    ValidationError,
+    activate_account,
+    bulk_account_operation,
+    count_players_without_self_link,
+    create_account_only,
+    create_player_account,
+    create_season,
+    create_user_player_link,
+    deactivate_account,
+    deactivate_user_player_link,
+    filter_account_users,
+    get_account_detail,
+    get_account_list,
+    get_account_operations_dashboard,
+    get_messages,
+    get_or_create_account_profile,
+    link_user_to_player,
+    mark_password_change_required,
+    reactivate_user_player_link,
+    reset_account_password,
+    reverse,
+    set_account_role,
+    set_primary_user_player_link,
+    update_account,
+)
+
+
+class AccountOperationsServiceTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.coach = User.objects.create_user(
+            username="coach.one",
+            password="testpass",
+            first_name="Coach",
+            last_name="One",
+            email="coach@example.com",
+        )
+        self.player_user = User.objects.create_user(
+            username="alex.player",
+            password="testpass",
+            first_name="Alex",
+            last_name="Player",
+            email="alex@example.com",
+        )
+        self.inactive_user = User.objects.create_user(
+            username="inactive", password="testpass", is_active=False
+        )
+        self.import_batch = PlayerImportBatch.objects.create(
+            source="manual_staff_csv",
+            original_filename="players.csv",
+            uploaded_by=self.staff,
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        player_profile = set_account_role(self.player_user, AccountRole.PLAYER)
+        player_profile.created_from_import = True
+        player_profile.import_batch = self.import_batch
+        player_profile.must_change_password = True
+        player_profile.save(
+            update_fields=[
+                "created_from_import",
+                "import_batch",
+                "must_change_password",
+                "updated_at",
+            ]
+        )
+        get_or_create_account_profile(self.inactive_user)
+        self.player = Player.objects.create(
+            first_name="Alex", last_name="Player", birthdate="2012-05-01"
+        )
+        self.unlinked_player = Player.objects.create(
+            first_name="No", last_name="Account"
+        )
+        link_user_to_player(
+            self.player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            created_from_import=True,
+            import_batch=self.import_batch,
+        )
+
+    def usernames_for_filters(self, **kwargs):
+        return [
+            user.username for user in filter_account_users(AccountListFilters(**kwargs))
+        ]
+
+    def test_account_query_filters_by_search_text(self):
+        self.assertEqual(
+            self.usernames_for_filters(search="coach@example.com"), ["coach.one"]
+        )
+        self.assertEqual(self.usernames_for_filters(search="Alex"), ["alex.player"])
+
+    def test_account_query_filters_by_role(self):
+        self.assertEqual(
+            self.usernames_for_filters(role=AccountRole.COACH), ["coach.one"]
+        )
+        self.assertEqual(
+            self.usernames_for_filters(role=AccountRole.PLAYER), ["alex.player"]
+        )
+
+    def test_account_query_filters_by_active_status(self):
+        self.assertEqual(self.usernames_for_filters(active_status="no"), ["inactive"])
+
+    def test_account_query_filters_by_staff_and_superuser_status(self):
+        admin_user = User.objects.create_superuser(
+            username="admin", password="testpass"
+        )
+        get_or_create_account_profile(admin_user)
+
+        self.assertEqual(
+            self.usernames_for_filters(staff_status="yes"), ["admin", "staff"]
+        )
+        self.assertEqual(self.usernames_for_filters(superuser_status="yes"), ["admin"])
+
+    def test_account_query_filters_by_imported_and_password_status(self):
+        self.assertEqual(
+            self.usernames_for_filters(imported_status="yes"), ["alex.player"]
+        )
+        self.assertEqual(
+            self.usernames_for_filters(must_change_password="yes"), ["alex.player"]
+        )
+
+    def test_account_query_filters_by_linked_status(self):
+        self.assertEqual(
+            self.usernames_for_filters(linked_status="linked"), ["alex.player"]
+        )
+        self.assertCountEqual(
+            self.usernames_for_filters(linked_status="unlinked"),
+            ["coach.one", "inactive", "staff"],
+        )
+
+    def test_dashboard_counts_include_account_health_metrics(self):
+        dashboard = get_account_operations_dashboard()
+        cards = {card.label: card.value for card in dashboard.summary_cards}
+
+        self.assertEqual(cards["Total accounts"], 4)
+        self.assertEqual(cards["Active accounts"], 3)
+        self.assertEqual(cards["Inactive accounts"], 1)
+        self.assertEqual(cards["Imported accounts"], 1)
+        self.assertEqual(cards["Password change required"], 1)
+        self.assertEqual(cards["Users without player links"], 3)
+        self.assertEqual(cards["Players without self-linked accounts"], 1)
+        self.assertEqual(
+            dashboard.users_requiring_password_change[0].user, self.player_user
+        )
+
+    def test_account_list_context_returns_rows_and_choices(self):
+        context = get_account_list(AccountListFilters(role=AccountRole.COACH))
+
+        self.assertEqual(context.total_count, 1)
+        self.assertEqual(context.rows[0].user, self.coach)
+        self.assertEqual(context.rows[0].role_label, "Coach")
+        self.assertIn((AccountRole.COACH, "Coach"), context.role_choices)
+
+    def test_account_detail_context_includes_profile_and_linked_players(self):
+        context = get_account_detail(self.player_user.id)
+
+        self.assertEqual(context.user, self.player_user)
+        self.assertEqual(context.role, AccountRole.PLAYER)
+        self.assertEqual(context.role_label, "Player")
+        self.assertEqual(len(context.linked_players), 1)
+        linked = context.linked_players[0]
+        self.assertEqual(linked.player, self.player)
+        self.assertEqual(linked.relationship, "Self")
+        self.assertTrue(linked.is_primary)
+        self.assertTrue(linked.is_active)
+        self.assertTrue(linked.created_from_import)
+        self.assertEqual(linked.import_label, "players.csv")
+
+    def test_players_without_self_link_count(self):
+        self.assertEqual(count_players_without_self_link(), 1)
+
+    def test_create_account_only_creates_user_profile_and_temporary_password(self):
+        result = create_account_only(
+            actor=self.staff,
+            username="New.Coach",
+            first_name="New",
+            last_name="Coach",
+            email="New.Coach@example.com",
+            role=AccountRole.COACH,
+            is_active=True,
+        )
+
+        user = User.objects.get(username="new.coach")
+        profile = user.account_profile
+        self.assertEqual(result.user, user)
+        self.assertEqual(result.username, "new.coach")
+        self.assertEqual(result.role, AccountRole.COACH)
+        self.assertEqual(result.role_label, "Coach")
+        self.assertTrue(result.temporary_password)
+        self.assertTrue(user.check_password(result.temporary_password))
+        self.assertNotIn(result.temporary_password, repr(result))
+        self.assertEqual(user.email, "new.coach@example.com")
+        self.assertEqual(profile.role, AccountRole.COACH)
+        self.assertTrue(profile.must_change_password)
+        self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+
+    def test_create_account_only_can_create_inactive_account(self):
+        result = create_account_only(
+            actor=self.staff,
+            username="inactive.coach",
+            role=AccountRole.COACH,
+            is_active=False,
+        )
+
+        self.assertFalse(User.objects.get(pk=result.user.id).is_active)
+        self.assertTrue(result.user.account_profile.must_change_password)
+
+    def test_create_account_only_rejects_duplicate_username_and_email(self):
+        User.objects.create_user(username="duplicate", email="duplicate@example.com")
+
+        with self.assertRaises(ValidationError):
+            create_account_only(
+                actor=self.staff, username="DUPLICATE", role=AccountRole.COACH
+            )
+        with self.assertRaises(ValidationError):
+            create_account_only(
+                actor=self.staff,
+                username="unique",
+                email="Duplicate@Example.com",
+                role=AccountRole.COACH,
+            )
+
+    def test_create_account_only_admin_requires_superuser(self):
+        superuser = User.objects.create_superuser(
+            username="ops.admin", password="testpass"
+        )
+
+        with self.assertRaises(ValidationError):
+            create_account_only(
+                actor=self.staff, username="admin.account", role=AccountRole.ADMIN
+            )
+
+        result = create_account_only(
+            actor=superuser, username="admin.account", role=AccountRole.ADMIN
+        )
+
+        self.assertEqual(result.role, AccountRole.ADMIN)
+        self.assertFalse(result.user.is_staff)
+        self.assertFalse(result.user.is_superuser)
+
+    def test_create_player_account_uses_existing_player_and_provisioning_logic(self):
+        player = Player.objects.create(
+            first_name="Blake", last_name="Player", birthdate="2013-06-02"
+        )
+
+        result = create_player_account(
+            actor=self.staff, player=player, email="Blake@example.com"
+        )
+
+        user = User.objects.get(username="blake.player")
+        profile = user.account_profile
+        link = UserPlayerLink.objects.get(user=user, player=player)
+        self.assertEqual(result.user, user)
+        self.assertEqual(result.player, player)
+        self.assertEqual(result.temporary_password, "20130602")
+        self.assertTrue(user.check_password(result.temporary_password))
+        self.assertEqual(user.email, "blake@example.com")
+        self.assertEqual(profile.role, AccountRole.PLAYER)
+        self.assertTrue(profile.must_change_password)
+        self.assertTrue(user.is_active)
+        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
+        self.assertTrue(link.is_primary)
+        self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
+        self.assertFalse(link.created_from_import)
+        self.assertIsNone(link.import_batch)
+
+    def test_create_player_account_accepts_optional_username_and_inactive_flag(self):
+        player = Player.objects.create(
+            first_name="Casey", last_name="Player", birthdate="2014-07-03"
+        )
+
+        result = create_player_account(
+            actor=self.staff, player=player, username="Custom.Player", is_active=False
+        )
+
+        self.assertEqual(result.username, "custom.player")
+        self.assertFalse(User.objects.get(username="custom.player").is_active)
+
+    def test_create_player_account_rejects_duplicate_email_username_and_player_account(
+        self,
+    ):
+        player = Player.objects.create(
+            first_name="Dana", last_name="Player", birthdate="2015-08-04"
+        )
+        User.objects.create_user(username="taken", email="taken@example.com")
+
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player, username="taken")
+        with self.assertRaises(ValidationError):
+            create_player_account(
+                actor=self.staff, player=player, email="taken@example.com"
+            )
+
+        create_player_account(actor=self.staff, player=player, username="dana.player")
+        with self.assertRaises(ValidationError):
+            create_player_account(
+                actor=self.staff, player=player, username="dana.player2"
+            )
+
+        self.assertEqual(
+            UserPlayerLink.objects.filter(
+                player=player, relationship=UserPlayerRelationship.SELF
+            ).count(),
+            1,
+        )
+
+    def test_create_player_account_requires_existing_player_birthdate_and_player_role(
+        self,
+    ):
+        player = Player.objects.create(first_name="No", last_name="Birthdate")
+
+        with self.assertRaises(ValidationError):
+            create_player_account(actor=self.staff, player=player)
+        with self.assertRaises(ValidationError):
+            create_player_account(
+                actor=self.staff, player=self.player, role=AccountRole.COACH
+            )
+
+    def test_update_account_changes_lifecycle_username_email_and_role(self):
+        result = update_account(
+            actor=self.staff,
+            user_id=self.coach.id,
+            username=" Coach.Updated ",
+            first_name="Updated",
+            last_name="Coach",
+            email="UPDATED@example.com",
+            role=AccountRole.GUEST_EVALUATOR,
+            is_active=False,
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.username, "coach.updated")
+        self.assertEqual(result.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(result.is_active)
+        self.assertEqual(self.coach.username, "coach.updated")
+        self.assertEqual(self.coach.email, "updated@example.com")
+        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_update_account_rejects_duplicate_username_and_email(self):
+        User.objects.create_user(username="taken", email="taken@example.com")
+
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="TAKEN",
+                email="coach@example.com",
+                role=AccountRole.COACH,
+            )
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="coach.one",
+                email="Taken@Example.com",
+                role=AccountRole.COACH,
+            )
+
+    def test_update_account_admin_role_requires_superuser(self):
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.coach.id,
+                username="coach.one",
+                role=AccountRole.ADMIN,
+            )
+
+        superuser = User.objects.create_superuser(
+            username="ops.admin", password="testpass"
+        )
+        result = update_account(
+            actor=superuser,
+            user_id=self.coach.id,
+            username="coach.one",
+            role=AccountRole.ADMIN,
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.role, AccountRole.ADMIN)
+        self.assertEqual(self.coach.account_profile.role, AccountRole.ADMIN)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_account_operation_services_require_staff_actor(self):
+        with self.assertRaisesMessage(
+            ValidationError, "Only staff users can manage accounts"
+        ):
+            create_account_only(
+                actor=self.coach, username="not.allowed", role=AccountRole.COACH
+            )
+        with self.assertRaisesMessage(
+            ValidationError, "Only staff users can manage accounts"
+        ):
+            create_player_account(actor=self.coach, player=self.player)
+        with self.assertRaisesMessage(
+            ValidationError, "Only staff users can manage accounts"
+        ):
+            update_account(
+                actor=self.coach,
+                user_id=self.player_user.id,
+                username="alex.player",
+                role=AccountRole.PLAYER,
+            )
+        with self.assertRaisesMessage(
+            ValidationError, "Only staff users can manage accounts"
+        ):
+            reset_account_password(actor=self.coach, user_id=self.player_user.id)
+        with self.assertRaisesMessage(
+            ValidationError, "Only staff users can manage accounts"
+        ):
+            bulk_account_operation(
+                actor=self.coach, action="activate", user_ids=[self.player_user.id]
+            )
+
+    def test_staff_cannot_mutate_staff_or_superuser_accounts(self):
+        other_staff = User.objects.create_user(
+            username="other.staff", password="testpass", is_staff=True
+        )
+        superuser = User.objects.create_superuser(
+            username="ops.admin", password="testpass"
+        )
+        superuser_actor = User.objects.create_superuser(
+            username="ops.admin2", password="testpass"
+        )
+
+        with self.assertRaisesMessage(
+            ValidationError, "Only superusers can manage staff or superuser accounts"
+        ):
+            update_account(
+                actor=self.staff,
+                user_id=other_staff.id,
+                username="other.staff",
+                role=AccountRole.STAFF,
+            )
+        with self.assertRaisesMessage(
+            ValidationError, "Only superusers can manage staff or superuser accounts"
+        ):
+            activate_account(actor=self.staff, user_id=other_staff.id)
+        with self.assertRaisesMessage(
+            ValidationError, "Only superusers can manage staff or superuser accounts"
+        ):
+            deactivate_account(actor=self.staff, user_id=superuser.id)
+        with self.assertRaisesMessage(
+            ValidationError, "Only superusers can manage staff or superuser accounts"
+        ):
+            reset_account_password(actor=self.staff, user_id=superuser.id)
+        with self.assertRaisesMessage(
+            ValidationError, "Only superusers can manage staff or superuser accounts"
+        ):
+            create_user_player_link(
+                actor=self.staff,
+                user_id=other_staff.id,
+                player=self.player,
+                relationship=UserPlayerRelationship.STAFF,
+            )
+
+        result = reset_account_password(actor=superuser_actor, user_id=other_staff.id)
+        other_staff.refresh_from_db()
+        self.assertTrue(other_staff.check_password(result.temporary_password))
+
+    def test_activate_and_deactivate_account_preserve_profile_and_links(self):
+        deactivate_result = deactivate_account(
+            actor=self.staff, user_id=self.player_user.id
+        )
+        self.player_user.refresh_from_db()
+        link = UserPlayerLink.objects.get(user=self.player_user, player=self.player)
+
+        self.assertFalse(deactivate_result.is_active)
+        self.assertFalse(self.player_user.is_active)
+        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
+        self.assertTrue(link.is_active)
+
+        activate_result = activate_account(
+            actor=self.staff, user_id=self.player_user.id
+        )
+        self.player_user.refresh_from_db()
+
+        self.assertTrue(activate_result.is_active)
+        self.assertTrue(self.player_user.is_active)
+        self.assertTrue(UserPlayerLink.objects.get(pk=link.pk).is_active)
+
+    def test_deactivate_account_rejects_self_deactivation(self):
+        with self.assertRaises(ValidationError):
+            deactivate_account(actor=self.staff, user_id=self.staff.id)
+
+        self.staff.refresh_from_db()
+        self.assertTrue(self.staff.is_active)
+
+    def test_update_account_rejects_self_deactivation(self):
+        with self.assertRaises(ValidationError):
+            update_account(
+                actor=self.staff,
+                user_id=self.staff.id,
+                username="staff",
+                role=AccountRole.STAFF,
+                is_active=False,
+            )
+
+        self.staff.refresh_from_db()
+        self.assertTrue(self.staff.is_active)
+
+    def test_deactivate_account_rejects_last_active_superuser(self):
+        superuser = User.objects.create_superuser(
+            username="ops.admin", password="testpass"
+        )
+
+        with self.assertRaises(ValidationError):
+            deactivate_account(actor=self.staff, user_id=superuser.id)
+
+        superuser.refresh_from_db()
+        self.assertTrue(superuser.is_active)
+
+    def test_deactivate_account_allows_superuser_actor_when_another_active_superuser_exists(
+        self,
+    ):
+        superuser = User.objects.create_superuser(
+            username="ops.admin", password="testpass"
+        )
+        actor = User.objects.create_superuser(username="ops.actor", password="testpass")
+        User.objects.create_superuser(username="ops.admin2", password="testpass")
+
+        result = deactivate_account(actor=actor, user_id=superuser.id)
+
+        self.assertFalse(result.is_active)
+
+    def test_account_operations_manage_player_links_through_services(self):
+        link_result = create_user_player_link(
+            actor=self.staff,
+            user_id=self.coach.id,
+            player=self.player,
+            relationship=UserPlayerRelationship.COACH,
+            is_primary=False,
+        )
+
+        self.assertTrue(link_result.is_active)
+        self.assertFalse(link_result.is_primary)
+        with self.assertRaises(ValidationError):
+            create_user_player_link(
+                actor=self.staff,
+                user_id=self.coach.id,
+                player=self.player,
+                relationship=UserPlayerRelationship.COACH,
+                is_primary=False,
+            )
+
+        deactivated = deactivate_user_player_link(
+            actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id
+        )
+        self.assertFalse(deactivated.is_active)
+        self.assertFalse(UserPlayerLink.objects.get(pk=link_result.link.id).is_primary)
+
+        reactivated = reactivate_user_player_link(
+            actor=self.staff, user_id=self.coach.id, link_id=link_result.link.id
+        )
+        self.assertTrue(reactivated.is_active)
+
+    def test_account_operations_set_primary_self_link_switches_existing_primary(self):
+        other_player = Player.objects.create(first_name="Second", last_name="Player")
+        first_link = UserPlayerLink.objects.get(
+            user=self.player_user, player=self.player
+        )
+        second_link = create_user_player_link(
+            actor=self.staff,
+            user_id=self.player_user.id,
+            player=other_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        ).link
+
+        result = set_primary_user_player_link(
+            actor=self.staff, user_id=self.player_user.id, link_id=second_link.id
+        )
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+
+        self.assertTrue(result.is_primary)
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+        self.assertEqual(
+            UserPlayerLink.objects.filter(
+                user=self.player_user, is_primary=True, is_active=True
+            ).count(),
+            1,
+        )
+
+    def test_account_operations_reject_primary_non_self_link(self):
+        link = create_user_player_link(
+            actor=self.staff,
+            user_id=self.coach.id,
+            player=self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        ).link
+
+        with self.assertRaises(ValidationError):
+            set_primary_user_player_link(
+                actor=self.staff, user_id=self.coach.id, link_id=link.id
+            )
+
+    def test_reset_account_password_uses_birthdate_for_player_account(self):
+        self.player_user.account_profile.must_change_password = False
+        self.player_user.account_profile.save(
+            update_fields=["must_change_password", "updated_at"]
+        )
+        original_link_count = UserPlayerLink.objects.filter(
+            user=self.player_user
+        ).count()
+
+        result = reset_account_password(actor=self.staff, user_id=self.player_user.id)
+
+        self.player_user.refresh_from_db()
+        self.assertEqual(result.user, self.player_user)
+        self.assertEqual(result.username, "alex.player")
+        self.assertEqual(result.temporary_password, "20120501")
+        self.assertTrue(self.player_user.check_password("20120501"))
+        self.assertTrue(self.player_user.account_profile.must_change_password)
+        self.assertTrue(self.player_user.is_active)
+        self.assertEqual(self.player_user.account_profile.role, AccountRole.PLAYER)
+        self.assertTrue(self.player_user.account_profile.created_from_import)
+        self.assertEqual(
+            self.player_user.account_profile.import_batch, self.import_batch
+        )
+        self.assertEqual(
+            UserPlayerLink.objects.filter(user=self.player_user).count(),
+            original_link_count,
+        )
+        self.assertNotIn(result.temporary_password, repr(result))
+
+    def test_reset_account_password_uses_random_password_for_non_player_account(self):
+        self.coach.account_profile.must_change_password = False
+        self.coach.account_profile.save(
+            update_fields=["must_change_password", "updated_at"]
+        )
+
+        result = reset_account_password(actor=self.staff, user_id=self.coach.id)
+
+        self.coach.refresh_from_db()
+        self.assertTrue(result.temporary_password)
+        self.assertNotEqual(result.temporary_password, "20120501")
+        self.assertTrue(self.coach.check_password(result.temporary_password))
+        self.assertTrue(self.coach.account_profile.must_change_password)
+        self.assertTrue(self.coach.is_active)
+        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
+        self.assertFalse(
+            UserPlayerLink.objects.filter(
+                user=self.coach, relationship=UserPlayerRelationship.SELF
+            ).exists()
+        )
+        self.assertNotIn(result.temporary_password, repr(result))
+
+    def test_reset_account_password_preserves_inactive_account_state(self):
+        self.assertFalse(self.inactive_user.is_active)
+
+        result = reset_account_password(actor=self.staff, user_id=self.inactive_user.id)
+
+        self.inactive_user.refresh_from_db()
+        self.assertFalse(self.inactive_user.is_active)
+        self.assertTrue(self.inactive_user.check_password(result.temporary_password))
+        self.assertTrue(self.inactive_user.account_profile.must_change_password)
+
+    def test_reset_account_password_rejects_player_account_missing_birthdate(self):
+        player = Player.objects.create(first_name="No", last_name="Birthdate")
+        user = User.objects.create_user(username="no.birthdate", password="testpass")
+        set_account_role(user, AccountRole.PLAYER)
+        link_user_to_player(user, player)
+
+        with self.assertRaises(ValidationError):
+            reset_account_password(actor=self.staff, user_id=user.id)
+
+    def test_bulk_account_operation_activates_accounts(self):
+        result = bulk_account_operation(
+            actor=self.staff, action="activate", user_ids=[self.inactive_user.id]
+        )
+
+        self.inactive_user.refresh_from_db()
+        self.assertEqual(result.processed, 1)
+        self.assertEqual(result.successful, 1)
+        self.assertEqual(result.failed, 0)
+        self.assertTrue(self.inactive_user.is_active)
+
+    def test_bulk_account_operation_deactivates_accounts(self):
+        result = bulk_account_operation(
+            actor=self.staff, action="deactivate", user_ids=[self.coach.id]
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.processed, 1)
+        self.assertEqual(result.successful, 1)
+        self.assertFalse(self.coach.is_active)
+
+    def test_bulk_account_operation_sets_password_change_requirement(self):
+        mark_password_change_required(self.coach, False)
+
+        result = bulk_account_operation(
+            actor=self.staff,
+            action="require_password_change",
+            user_ids=[self.coach.id],
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(result.successful, 1)
+        self.assertTrue(self.coach.account_profile.must_change_password)
+
+    def test_bulk_account_operation_clears_password_change_requirement(self):
+        mark_password_change_required(self.player_user, True)
+
+        result = bulk_account_operation(
+            actor=self.staff,
+            action="clear_password_change",
+            user_ids=[self.player_user.id],
+        )
+
+        self.player_user.refresh_from_db()
+        self.assertEqual(result.successful, 1)
+        self.assertFalse(self.player_user.account_profile.must_change_password)
+
+    def test_bulk_account_operation_continues_after_failure(self):
+        result = bulk_account_operation(
+            actor=self.staff,
+            action="deactivate",
+            user_ids=[self.staff.id, self.coach.id],
+        )
+
+        self.staff.refresh_from_db()
+        self.coach.refresh_from_db()
+        self.assertEqual(result.processed, 2)
+        self.assertEqual(result.successful, 1)
+        self.assertEqual(result.failed, 1)
+        self.assertEqual(result.errors[0].username, "staff")
+        self.assertIn("cannot deactivate your own account", result.errors[0].message)
+        self.assertTrue(self.staff.is_active)
+        self.assertFalse(self.coach.is_active)
+
+    def test_bulk_account_operation_rejects_empty_selection_and_unknown_action(self):
+        with self.assertRaises(ValidationError):
+            bulk_account_operation(actor=self.staff, action="activate", user_ids=[])
+        with self.assertRaises(ValidationError):
+            bulk_account_operation(
+                actor=self.staff, action="unsupported", user_ids=[self.coach.id]
+            )
+
+    def test_bulk_account_operation_reports_missing_users(self):
+        result = bulk_account_operation(
+            actor=self.staff, action="activate", user_ids=[999999]
+        )
+
+        self.assertEqual(result.processed, 1)
+        self.assertEqual(result.successful, 0)
+        self.assertEqual(result.failed, 1)
+        self.assertEqual(result.errors[0].username, "Unknown account")
+        self.assertEqual(result.errors[0].message, "Account not found.")
+
+    def test_bulk_account_operation_rejects_last_superuser_deactivation(self):
+        superuser = User.objects.create_superuser(
+            username="ops.admin", password="testpass"
+        )
+
+        result = bulk_account_operation(
+            actor=self.staff, action="deactivate", user_ids=[superuser.id]
+        )
+
+        superuser.refresh_from_db()
+        self.assertEqual(result.successful, 0)
+        self.assertEqual(result.failed, 1)
+        self.assertEqual(result.errors[0].username, "ops.admin")
+        self.assertIn("last active superuser", result.errors[0].message)
+        self.assertTrue(superuser.is_active)
+
+
+class AccountOperationsViewTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.superuser = User.objects.create_superuser(
+            username="admin", password="testpass"
+        )
+        self.regular = User.objects.create_user(username="regular", password="testpass")
+        self.coach = User.objects.create_user(
+            username="coach.one",
+            password="testpass",
+            first_name="Coach",
+            last_name="One",
+            email="coach@example.com",
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        profile = get_or_create_account_profile(self.regular)
+        profile.role = AccountRole.STAFF
+        profile.save(update_fields=["role", "updated_at"])
+        self.player = Player.objects.create(first_name="Alex", last_name="Player")
+        link_user_to_player(
+            self.coach,
+            self.player,
+            relationship=UserPlayerRelationship.COACH,
+            is_primary=False,
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+
+    def test_dashboard_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_superuser_can_access_dashboard(self):
+        self.client.force_login(self.superuser)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Operations")
+
+    def test_dashboard_renders_expected_summary_cards(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:operations-dashboard"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Total accounts")
+        self.assertContains(response, "Active accounts")
+        self.assertContains(response, "Inactive accounts")
+        self.assertContains(response, "Password change required")
+        self.assertContains(response, "Users without player links")
+        self.assertContains(response, "Players without self-linked accounts")
+        self.assertContains(response, reverse("accounts:account-create"))
+        self.assertContains(response, reverse("accounts:player-account-create"))
+        self.assertContains(response, reverse("accounts:coach-import-list"))
+
+    def test_user_list_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:user-list"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_user_list_renders_users_and_filters(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("accounts:user-list"), {"q": "coach", "role": AccountRole.COACH}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Users")
+        self.assertContains(response, "coach.one")
+        self.assertContains(response, "Coach")
+        self.assertNotContains(response, "regular")
+        self.assertContains(response, "Bulk action")
+        self.assertContains(response, "Select all accounts shown")
+
+    def test_user_list_bulk_post_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "activate",
+                "user_ids": [self.coach.id],
+                "visible_user_ids": [self.coach.id],
+            },
+        )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_bulk_activate_from_user_list(self):
+        self.coach.is_active = False
+        self.coach.save(update_fields=["is_active"])
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "activate",
+                "user_ids": [self.coach.id],
+                "visible_user_ids": [self.coach.id],
+            },
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "1 succeeded, 0 failed")
+        self.assertTrue(self.coach.is_active)
+
+    def test_staff_can_bulk_require_and_clear_password_change_from_user_list(self):
+        mark_password_change_required(self.coach, False)
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "require_password_change",
+                "user_ids": [self.coach.id],
+                "visible_user_ids": [self.coach.id],
+            },
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertTrue(self.coach.account_profile.must_change_password)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "clear_password_change",
+                "user_ids": [self.coach.id],
+                "visible_user_ids": [self.coach.id],
+            },
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertFalse(self.coach.account_profile.must_change_password)
+
+    def test_staff_bulk_deactivate_reports_self_failure_and_successes(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "deactivate",
+                "user_ids": [self.staff.id, self.coach.id],
+                "visible_user_ids": [self.staff.id, self.coach.id],
+            },
+        )
+
+        self.staff.refresh_from_db()
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "1 succeeded, 1 failed")
+        self.assertContains(response, "staff")
+        self.assertContains(response, "cannot deactivate your own account")
+        self.assertTrue(self.staff.is_active)
+        self.assertFalse(self.coach.is_active)
+
+    def test_staff_bulk_action_rejects_empty_selection_and_unknown_action(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {"action": "activate", "visible_user_ids": [self.coach.id]},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Select at least one account")
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "unsupported",
+                "user_ids": [self.coach.id],
+                "visible_user_ids": [self.coach.id],
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Select a valid choice")
+
+    def test_staff_bulk_select_all_uses_visible_user_ids(self):
+        self.coach.is_active = False
+        self.coach.save(update_fields=["is_active"])
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-list"),
+            {
+                "action": "activate",
+                "select_all": "on",
+                "visible_user_ids": [self.coach.id],
+            },
+        )
+
+        self.coach.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertTrue(self.coach.is_active)
+
+    def test_user_detail_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(
+            reverse("accounts:user-detail", kwargs={"user_id": self.coach.id})
+        )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_user_detail_missing_account_returns_404(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("accounts:user-detail", kwargs={"user_id": 999999})
+        )
+
+        self.assertEqual(response.status_code, 404)
+
+    def test_user_detail_renders_profile_and_linked_players(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("accounts:user-detail", kwargs={"user_id": self.coach.id})
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "coach.one")
+        self.assertContains(response, "coach@example.com")
+        self.assertContains(response, "Coach")
+        self.assertContains(response, "Alex Player")
+        self.assertContains(
+            response, reverse("accounts:user-edit", kwargs={"user_id": self.coach.id})
+        )
+        self.assertContains(
+            response, reverse("accounts:user-links", kwargs={"user_id": self.coach.id})
+        )
+        self.assertContains(
+            response,
+            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}),
+        )
+
+    def test_user_edit_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id})
+        )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_edit_account_lifecycle_username_and_role(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": " Coach.Updated ",
+                "first_name": "Updated",
+                "last_name": "Coach",
+                "email": "updated@example.com",
+                "role": AccountRole.GUEST_EVALUATOR,
+            },
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(
+            response["Location"],
+            reverse("accounts:user-detail", kwargs={"user_id": self.coach.id}),
+        )
+        self.coach.refresh_from_db()
+        self.assertEqual(self.coach.username, "coach.updated")
+        self.assertFalse(self.coach.is_active)
+        self.assertEqual(self.coach.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(self.coach.is_staff)
+        self.assertFalse(self.coach.is_superuser)
+
+    def test_staff_user_edit_rejects_duplicate_username_and_admin_role(self):
+        User.objects.create_user(username="taken")
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": "taken",
+                "role": AccountRole.COACH,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Username is already in use")
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": self.coach.id}),
+            {
+                "username": "coach.one",
+                "role": AccountRole.ADMIN,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Only superusers can assign admin role")
+        self.coach.refresh_from_db()
+        self.assertEqual(self.coach.account_profile.role, AccountRole.COACH)
+
+    def test_staff_user_edit_rejects_staff_or_superuser_target(self):
+        other_staff = User.objects.create_user(
+            username="other.staff", password="testpass", is_staff=True
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-edit", kwargs={"user_id": other_staff.id}),
+            {
+                "username": "other.staff",
+                "role": AccountRole.STAFF,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(
+            response, "Only superusers can manage staff or superuser accounts"
+        )
+
+    def test_user_links_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id})
+        )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_deactivate_and_reactivate_link(self):
+        other_player = Player.objects.create(first_name="Blake", last_name="Player")
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {
+                "action": "create",
+                "player": other_player.id,
+                "relationship": UserPlayerRelationship.PARENT,
+            },
+        )
+
+        self.assertEqual(response.status_code, 302)
+        link = UserPlayerLink.objects.get(
+            user=self.coach,
+            player=other_player,
+            relationship=UserPlayerRelationship.PARENT,
+        )
+        self.assertTrue(link.is_active)
+        self.assertFalse(link.is_primary)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "deactivate", "link_id": link.id},
+        )
+        self.assertEqual(response.status_code, 302)
+        link.refresh_from_db()
+        self.assertFalse(link.is_active)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "reactivate", "link_id": link.id},
+        )
+        self.assertEqual(response.status_code, 302)
+        link.refresh_from_db()
+        self.assertTrue(link.is_active)
+
+    def test_staff_can_set_primary_self_link_from_links_page(self):
+        first_player = Player.objects.create(first_name="Self", last_name="One")
+        second_player = Player.objects.create(first_name="Self", last_name="Two")
+        first_link = link_user_to_player(
+            self.coach, first_player, relationship=UserPlayerRelationship.SELF
+        )
+        second_link = link_user_to_player(
+            self.coach,
+            second_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "set_primary", "link_id": second_link.id},
+        )
+
+        self.assertEqual(response.status_code, 302)
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+
+    def test_links_page_rejects_duplicate_active_link(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {
+                "action": "create",
+                "player": self.player.id,
+                "relationship": UserPlayerRelationship.COACH,
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "An active link already exists")
+
+    def test_links_page_handles_invalid_link_id_as_form_error(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "deactivate", "link_id": "999999"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player link not found")
+
+    def test_links_page_handles_unknown_action_as_form_error(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-links", kwargs={"user_id": self.coach.id}),
+            {"action": "unsupported", "link_id": "1"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Unsupported link action")
+
+    def test_password_reset_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(
+            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id})
+        )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_reset_non_player_password_and_see_password_once(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}),
+            {"confirm": "on"},
+        )
+
+        self.coach.refresh_from_db()
+        temporary_password = response.context[
+            "password_reset_result"
+        ].temporary_password
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Password Reset Complete")
+        self.assertContains(response, temporary_password)
+        self.assertTrue(self.coach.check_password(temporary_password))
+        self.assertTrue(self.coach.account_profile.must_change_password)
+        self.assertNotIn(
+            temporary_password,
+            " ".join(str(message) for message in get_messages(response.wsgi_request)),
+        )
+
+        refresh_response = self.client.get(
+            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id})
+        )
+        detail_response = self.client.get(
+            reverse("accounts:user-detail", kwargs={"user_id": self.coach.id})
+        )
+        self.assertNotContains(refresh_response, temporary_password)
+        self.assertNotContains(detail_response, temporary_password)
+
+    def test_staff_can_reset_player_password_with_birthdate_password(self):
+        player = Player.objects.create(
+            first_name="Blake", last_name="Player", birthdate="2013-06-02"
+        )
+        user = User.objects.create_user(username="blake.player", password="testpass")
+        set_account_role(user, AccountRole.PLAYER)
+        link_user_to_player(user, player)
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-password-reset", kwargs={"user_id": user.id}),
+            {"confirm": "on"},
+        )
+
+        user.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "20130602")
+        self.assertTrue(user.check_password("20130602"))
+        self.assertTrue(user.account_profile.must_change_password)
+
+    def test_password_reset_does_not_run_without_confirmation(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:user-password-reset", kwargs={"user_id": self.coach.id}),
+            {},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "This field is required")
+        self.coach.refresh_from_db()
+        self.assertTrue(self.coach.check_password("testpass"))
+
+    def test_password_reset_missing_account_returns_404(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("accounts:user-password-reset", kwargs={"user_id": 999999})
+        )
+
+        self.assertEqual(response.status_code, 404)
+
+    def test_staff_password_reset_rejects_staff_or_superuser_target(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse(
+                "accounts:user-password-reset", kwargs={"user_id": self.superuser.id}
+            ),
+            {"confirm": "on"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(
+            response, "Only superusers can manage staff or superuser accounts"
+        )
+        self.superuser.refresh_from_db()
+        self.assertTrue(self.superuser.check_password("testpass"))
+
+    def test_profile_page_links_staff_to_account_operations(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, reverse("accounts:operations-dashboard"))
+
+    def test_profile_page_does_not_link_regular_user_to_account_operations(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertNotContains(response, reverse("accounts:operations-dashboard"))
+
+    def test_account_create_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:account-create"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_account_only_and_see_one_time_password(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:account-create"),
+            {
+                "username": "new.evaluator",
+                "first_name": "New",
+                "last_name": "Evaluator",
+                "email": "new@example.com",
+                "role": AccountRole.GUEST_EVALUATOR,
+                "is_active": "on",
+            },
+        )
+
+        user = User.objects.get(username="new.evaluator")
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Created")
+        self.assertContains(response, "Temporary password")
+        temporary_password = response.context["created_account"].temporary_password
+        self.assertIn(temporary_password, response.content.decode())
+        self.assertNotIn(
+            temporary_password,
+            " ".join(str(message) for message in get_messages(response.wsgi_request)),
+        )
+        self.assertTrue(user.account_profile.must_change_password)
+        self.assertEqual(user.account_profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+
+        detail_response = self.client.get(
+            reverse("accounts:user-detail", kwargs={"user_id": user.id})
+        )
+        self.assertNotContains(detail_response, temporary_password)
+        get_response = self.client.get(reverse("accounts:account-create"))
+        self.assertNotContains(get_response, temporary_password)
+
+    def test_staff_cannot_create_admin_account(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:account-create"),
+            {
+                "username": "admin.try",
+                "role": AccountRole.ADMIN,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Only superusers can create admin accounts")
+        self.assertNotContains(response, "Temporary password")
+        self.assertFalse(User.objects.filter(username="admin.try").exists())
+
+    def test_player_account_create_requires_staff(self):
+        self.client.force_login(self.regular)
+
+        response = self.client.get(reverse("accounts:player-account-create"))
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_create_player_account_for_existing_player(self):
+        player = Player.objects.create(
+            first_name="Blake", last_name="Player", birthdate="2013-06-02"
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:player-account-create"),
+            {
+                "player": player.id,
+                "email": "blake@example.com",
+                "role": AccountRole.PLAYER,
+                "is_active": "on",
+            },
+        )
+
+        user = User.objects.get(username="blake.player")
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player Account Created")
+        self.assertContains(response, "20130602")
+        self.assertNotIn(
+            "20130602",
+            " ".join(str(message) for message in get_messages(response.wsgi_request)),
+        )
+        self.assertTrue(user.check_password("20130602"))
+        self.assertTrue(user.account_profile.must_change_password)
+        self.assertEqual(UserPlayerLink.objects.get(user=user).player, player)
+
+        detail_response = self.client.get(
+            reverse("accounts:user-detail", kwargs={"user_id": user.id})
+        )
+        self.assertNotContains(detail_response, "20130602")
+        get_response = self.client.get(reverse("accounts:player-account-create"))
+        self.assertNotContains(get_response, "20130602")
+
+    def test_player_account_create_rejects_duplicate_player_account(self):
+        player = Player.objects.create(
+            first_name="Blake", last_name="Player", birthdate="2013-06-02"
+        )
+        create_player_account(actor=self.staff, player=player)
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:player-account-create"),
+            {
+                "player": player.id,
+                "role": AccountRole.PLAYER,
+                "is_active": "on",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player already has a linked user account")
+        self.assertEqual(
+            UserPlayerLink.objects.filter(
+                player=player, relationship=UserPlayerRelationship.SELF
+            ).count(),
+            1,
+        )
+
+    def test_coach_import_pages_require_staff(self):
+        self.client.force_login(self.regular)
+
+        urls = [
+            reverse("accounts:coach-import-list"),
+            reverse("accounts:coach-import-new"),
+            reverse("accounts:coach-import-preview"),
+            reverse("accounts:coach-import-confirm"),
+        ]
+
+        for url in urls:
+            response = self.client.get(url)
+            self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_preview_and_confirm_coach_import(self):
+        self.client.force_login(self.staff)
+        csv_file = SimpleUploadedFile(
+            "coaches.csv",
+            b"first_name,last_name,email,team,division\nNew,Coach,new.coach@example.com,Reds,13U\n",
+            content_type="text/csv",
+        )
+
+        upload_response = self.client.post(
+            reverse("accounts:coach-import-new"),
+            {"season": str(self.season.id), "csv_file": csv_file},
+        )
+        self.assertEqual(upload_response.status_code, 302)
+        self.assertEqual(
+            upload_response["Location"], reverse("accounts:coach-import-preview")
+        )
+
+        preview_response = self.client.get(reverse("accounts:coach-import-preview"))
+        self.assertEqual(preview_response.status_code, 200)
+        self.assertContains(preview_response, "Ready to create")
+        self.assertContains(preview_response, "new.coach@example.com")
+
+        confirm_response = self.client.post(
+            reverse("accounts:coach-import-confirm"), {"confirm": "on"}
+        )
+        self.assertEqual(confirm_response.status_code, 200)
+        self.assertContains(confirm_response, "Coach Import Result")
+        self.assertContains(confirm_response, "Temporary password")
+        user = User.objects.get(username="new.coach")
+        temporary_password = (
+            confirm_response.context["result"].rows[0].temporary_password
+        )
+        self.assertTrue(user.check_password(temporary_password))
+        self.assertTrue(user.is_active)
+        self.assertEqual(user.account_profile.role, AccountRole.COACH)
+        self.assertTrue(user.account_profile.must_change_password)
+        self.assertEqual(
+            CoachSeasonAssignment.objects.filter(
+                user=user, season_team__season=self.season
+            ).count(),
+            1,
+        )
+        self.assertFalse(user.is_staff)
+        self.assertFalse(user.is_superuser)
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+        self.assertEqual(Player.objects.count(), 1)
+        self.assertNotIn("coach_import_csv", self.client.session)
+
+        detail_response = self.client.get(
+            reverse("accounts:user-detail", kwargs={"user_id": user.id})
+        )
+        self.assertNotContains(detail_response, temporary_password)
+        list_response = self.client.get(reverse("accounts:coach-import-list"))
+        self.assertNotContains(list_response, temporary_password)
+        preview_again = self.client.get(reverse("accounts:coach-import-preview"))
+        self.assertEqual(preview_again.status_code, 302)
+        confirm_again = self.client.get(reverse("accounts:coach-import-confirm"))
+        self.assertEqual(confirm_again.status_code, 302)
+
+    def test_coach_import_preview_rejects_manipulated_inactive_season(self):
+        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
+        self.client.force_login(self.staff)
+        session = self.client.session
+        session["coach_import_csv"] = (
+            "first_name,last_name,email,team,division\nBad,Season,bad.season@example.com,Reds,13U\n"
+        )
+        session["coach_import_season_id"] = inactive.id
+        session.save()
+
+        preview_response = self.client.get(reverse("accounts:coach-import-preview"))
+        confirm_response = self.client.post(
+            reverse("accounts:coach-import-confirm"), {"confirm": "on"}
+        )
+
+        self.assertEqual(preview_response.status_code, 302)
+        self.assertEqual(
+            preview_response["Location"], reverse("accounts:coach-import-new")
+        )
+        self.assertEqual(confirm_response.status_code, 302)
+        self.assertFalse(User.objects.filter(email="bad.season@example.com").exists())
+
+    def test_coach_import_reuses_existing_coach_and_blocks_non_coach_email(self):
+        existing_coach = User.objects.create_user(
+            username="existing.coach", email="existing@example.com"
+        )
+        set_account_role(existing_coach, AccountRole.COACH)
+        existing_player = User.objects.create_user(
+            username="existing.player", email="player@example.com"
+        )
+        set_account_role(existing_player, AccountRole.PLAYER)
+        self.client.force_login(self.staff)
+        csv_file = SimpleUploadedFile(
+            "coaches.csv",
+            (
+                "first_name,last_name,email,team,division\n"
+                "Existing,Coach,existing@example.com,Reds,13U\n"
+                "Existing,Player,player@example.com,Reds,13U\n"
+            ).encode(),
+            content_type="text/csv",
+        )
+
+        self.client.post(
+            reverse("accounts:coach-import-new"),
+            {"season": str(self.season.id), "csv_file": csv_file},
+        )
+        response = self.client.post(
+            reverse("accounts:coach-import-confirm"), {"confirm": "on"}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        result = response.context["result"]
+        self.assertEqual(result.existing_coaches_reused, 1)
+        self.assertEqual(result.conflicts, 1)
+        temporary_password = result.rows[0].temporary_password
+        existing_coach.refresh_from_db()
+        self.assertFalse(temporary_password)
+        self.assertFalse(existing_coach.account_profile.must_change_password)
+        self.assertEqual(existing_coach.account_profile.role, AccountRole.COACH)
+        self.assertEqual(
+            CoachSeasonAssignment.objects.filter(
+                user=existing_coach, season_team__season=self.season
+            ).count(),
+            1,
+        )
+        self.assertEqual(
+            User.objects.filter(email__iexact="existing@example.com").count(), 1
+        )
+        self.assertEqual(
+            User.objects.filter(email__iexact="player@example.com").count(), 1
+        )
+
+        detail_response = self.client.get(
+            reverse("accounts:user-detail", kwargs={"user_id": existing_coach.id})
+        )
+        self.assertNotContains(detail_response, "Password unchanged")
diff --git a/accounts/tests/test_account_services.py b/accounts/tests/test_account_services.py
new file mode 100644
index 0000000..1b2e04f
--- /dev/null
+++ b/accounts/tests/test_account_services.py
@@ -0,0 +1,357 @@
+from accounts.tests.helpers import (
+    STATUS_ALREADY_LINKED,
+    STATUS_CONFLICT,
+    STATUS_CREATED,
+    STATUS_SKIPPED,
+    AccountProfile,
+    AccountRole,
+    Player,
+    PlayerImportBatch,
+    ProvisioningOptions,
+    ProvisioningSummary,
+    TestCase,
+    User,
+    UserPlayerLink,
+    UserPlayerRelationship,
+    ValidationError,
+    base_username_for_player,
+    can_submit_coach_assessment,
+    deactivate_link,
+    emails_equal,
+    find_existing_email_user,
+    generate_birthdate_password,
+    generate_random_temporary_password,
+    get_or_create_account_profile,
+    link_user_to_player,
+    mark_password_change_required,
+    normalize_email,
+    normalize_username_part,
+    provision_accounts_for_import,
+    provision_player_account,
+    set_temporary_password,
+    username_for_player,
+    validate_available_username,
+    validate_available_username_for_user,
+)
+
+
+class AccountUsernameServiceTests(TestCase):
+    def test_username_parts_normalize_unicode_and_unsafe_characters(self):
+        self.assertEqual(normalize_username_part("  José   García!  "), "josegarcia")
+
+    def test_base_username_for_player_uses_first_dot_last(self):
+        player = Player.objects.create(
+            first_name="José", last_name="García", birthdate="2012-05-01"
+        )
+
+        self.assertEqual(base_username_for_player(player), "jose.garcia")
+
+    def test_username_for_player_uses_deterministic_suffixes(self):
+        player = Player.objects.create(
+            first_name="Alex", last_name="Player", birthdate="2012-05-01"
+        )
+        User.objects.create_user(username="alex.player")
+        User.objects.create_user(username="alex.player2")
+
+        self.assertEqual(username_for_player(player), "alex.player3")
+
+    def test_validate_available_username_rejects_duplicates_and_unsafe_values(self):
+        User.objects.create_user(username="coach.one")
+
+        self.assertEqual(validate_available_username("new.user"), "new.user")
+        self.assertEqual(validate_available_username("  Coach.Two  "), "coach.two")
+        with self.assertRaises(ValidationError):
+            validate_available_username("coach.ONE")
+        with self.assertRaises(ValidationError):
+            validate_available_username("bad username")
+
+    def test_validate_available_username_for_user_allows_current_user(self):
+        user = User.objects.create_user(username="coach.one")
+        User.objects.create_user(username="other")
+
+        self.assertEqual(
+            validate_available_username_for_user(user, " Coach.One "), "coach.one"
+        )
+        with self.assertRaises(ValidationError):
+            validate_available_username_for_user(user, "OTHER")
+
+
+class AccountEmailServiceTests(TestCase):
+    def test_email_normalization_and_comparison(self):
+        self.assertEqual(normalize_email("  PLAYER@Example.COM "), "player@example.com")
+        self.assertTrue(emails_equal("PLAYER@example.com", "player@EXAMPLE.com"))
+
+    def test_find_existing_email_user_is_case_insensitive(self):
+        user = User.objects.create_user(username="user", email="Player@Example.com")
+
+        self.assertEqual(find_existing_email_user("player@example.COM"), user)
+
+
+class AccountPasswordServiceTests(TestCase):
+    def test_generate_birthdate_password_uses_yyyymmdd(self):
+        player = Player.objects.create(
+            first_name="Alex", last_name="Player", birthdate="2012-05-01"
+        )
+
+        self.assertEqual(generate_birthdate_password(player), "20120501")
+
+    def test_generate_birthdate_password_requires_birthdate(self):
+        player = Player.objects.create(first_name="Alex", last_name="Player")
+
+        with self.assertRaises(ValidationError):
+            generate_birthdate_password(player)
+
+    def test_set_temporary_password_hashes_password_and_marks_profile(self):
+        user = User.objects.create_user(username="player")
+        player = Player.objects.create(
+            first_name="Alex", last_name="Player", birthdate="2012-05-01"
+        )
+
+        set_temporary_password(user, player)
+        mark_password_change_required(user)
+        user.refresh_from_db()
+
+        self.assertNotEqual(user.password, "20120501")
+        self.assertTrue(user.check_password("20120501"))
+        self.assertTrue(user.account_profile.must_change_password)
+
+    def test_generate_random_temporary_password_is_secure_length(self):
+        password = generate_random_temporary_password()
+
+        self.assertGreaterEqual(len(password), 12)
+        self.assertNotEqual(password, generate_random_temporary_password())
+
+
+class AccountProvisioningServiceTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.player = Player.objects.create(
+            first_name="José", last_name="García", birthdate="2012-05-01"
+        )
+        self.import_batch = PlayerImportBatch.objects.create(
+            source="manual_staff_csv",
+            original_filename="players.csv",
+            uploaded_by=self.staff,
+        )
+
+    def test_provision_player_account_creates_active_player_account_profile_and_link(
+        self,
+    ):
+        result = provision_player_account(
+            self.player,
+            import_batch=self.import_batch,
+            actor=self.staff,
+            email="Player@Example.com",
+            row_number=2,
+        )
+
+        user = User.objects.get(username="jose.garcia")
+        profile = user.account_profile
+        link = UserPlayerLink.objects.get(user=user, player=self.player)
+        self.assertEqual(result.status, STATUS_CREATED)
+        self.assertEqual(result.username, "jose.garcia")
+        self.assertTrue(user.is_active)
+        self.assertEqual(user.email, "player@example.com")
+        self.assertTrue(user.check_password("20120501"))
+        self.assertEqual(profile.role, AccountRole.PLAYER)
+        self.assertTrue(profile.must_change_password)
+        self.assertTrue(profile.created_from_import)
+        self.assertEqual(profile.import_batch, self.import_batch)
+        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
+        self.assertTrue(link.created_from_import)
+        self.assertEqual(link.import_batch, self.import_batch)
+
+    def test_provision_player_account_can_activate_user_when_explicit(self):
+        result = provision_player_account(
+            self.player, import_batch=self.import_batch, activate_user=True
+        )
+
+        self.assertEqual(result.status, STATUS_CREATED)
+        self.assertTrue(User.objects.get(pk=result.user_id).is_active)
+
+    def test_provision_player_account_skips_missing_birthdate(self):
+        player = Player.objects.create(first_name="No", last_name="Birthdate")
+
+        result = provision_player_account(
+            player, import_batch=self.import_batch, row_number=3
+        )
+
+        self.assertEqual(result.status, STATUS_SKIPPED)
+        self.assertFalse(User.objects.filter(username="no.birthdate").exists())
+
+    def test_provision_player_account_is_idempotent_for_existing_link(self):
+        first = provision_player_account(
+            self.player, import_batch=self.import_batch, row_number=2
+        )
+        second = provision_player_account(
+            self.player, import_batch=self.import_batch, row_number=2
+        )
+
+        self.assertEqual(first.status, STATUS_CREATED)
+        self.assertEqual(second.status, STATUS_ALREADY_LINKED)
+        self.assertEqual(User.objects.filter(username="jose.garcia").count(), 1)
+        self.assertEqual(UserPlayerLink.objects.filter(player=self.player).count(), 1)
+        self.assertEqual(
+            AccountProfile.objects.filter(user_id=first.user_id).count(), 1
+        )
+
+    def test_provision_player_account_reuses_inactive_self_link_without_duplicates(
+        self,
+    ):
+        user = User.objects.create_user(
+            username="existing.player", email="existing@example.com"
+        )
+        profile = get_or_create_account_profile(user)
+        link = link_user_to_player(
+            user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+            created_from_import=True,
+            import_batch=self.import_batch,
+        )
+        deactivate_link(link)
+
+        result = provision_player_account(
+            self.player,
+            import_batch=self.import_batch,
+            email="existing@example.com",
+            row_number=2,
+        )
+        link.refresh_from_db()
+        profile.refresh_from_db()
+
+        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
+        self.assertEqual(result.user_id, user.id)
+        self.assertTrue(link.is_active)
+        self.assertTrue(link.is_primary)
+        self.assertEqual(User.objects.filter(username="existing.player").count(), 1)
+        self.assertEqual(AccountProfile.objects.filter(user=user).count(), 1)
+        self.assertEqual(
+            UserPlayerLink.objects.filter(user=user, player=self.player).count(), 1
+        )
+
+    def test_provision_player_account_preserves_manual_link_provenance(self):
+        user = User.objects.create_user(
+            username="manual.player", email="manual@example.com"
+        )
+        profile = get_or_create_account_profile(user)
+        link = link_user_to_player(user, self.player)
+        deactivate_link(link)
+
+        result = provision_player_account(
+            self.player,
+            import_batch=self.import_batch,
+            email="manual@example.com",
+            row_number=2,
+        )
+        profile.refresh_from_db()
+        link.refresh_from_db()
+
+        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
+        self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
+        self.assertFalse(link.created_from_import)
+        self.assertIsNone(link.import_batch)
+
+    def test_provision_player_account_remains_idempotent_after_link_deactivation_and_reactivation(
+        self,
+    ):
+        first = provision_player_account(
+            self.player, import_batch=self.import_batch, row_number=2
+        )
+        link = UserPlayerLink.objects.get(player=self.player, user_id=first.user_id)
+        deactivate_link(link)
+
+        second = provision_player_account(
+            self.player, import_batch=self.import_batch, row_number=2
+        )
+        third = provision_player_account(
+            self.player, import_batch=self.import_batch, row_number=2
+        )
+
+        link.refresh_from_db()
+        self.assertEqual(second.status, STATUS_ALREADY_LINKED)
+        self.assertEqual(third.status, STATUS_ALREADY_LINKED)
+        self.assertTrue(link.is_active)
+        self.assertEqual(User.objects.filter(username="jose.garcia").count(), 1)
+        self.assertEqual(
+            AccountProfile.objects.filter(user_id=first.user_id).count(), 1
+        )
+        self.assertEqual(
+            UserPlayerLink.objects.filter(
+                player=self.player, user_id=first.user_id
+            ).count(),
+            1,
+        )
+
+    def test_provision_player_account_conflicts_on_unrelated_email(self):
+        User.objects.create_user(username="other", email="player@example.com")
+
+        result = provision_player_account(
+            self.player, import_batch=self.import_batch, email="PLAYER@example.com"
+        )
+
+        self.assertEqual(result.status, STATUS_CONFLICT)
+        self.assertFalse(UserPlayerLink.objects.filter(player=self.player).exists())
+
+    def test_provision_player_account_does_not_downgrade_existing_staff_link(self):
+        staff_profile = get_or_create_account_profile(self.staff)
+        staff_profile.role = AccountRole.STAFF
+        staff_profile.save(update_fields=["role", "updated_at"])
+        link_user_to_player(self.staff, self.player)
+
+        result = provision_player_account(self.player, import_batch=self.import_batch)
+        staff_profile.refresh_from_db()
+
+        self.assertEqual(result.status, STATUS_ALREADY_LINKED)
+        self.assertEqual(staff_profile.role, AccountRole.STAFF)
+        self.assertFalse(staff_profile.created_from_import)
+        self.assertIsNone(staff_profile.import_batch)
+
+    def test_provisioning_summary_serializes_safe_counts_without_plaintext_passwords(
+        self,
+    ):
+        summary = provision_accounts_for_import(
+            self.import_batch,
+            [
+                {
+                    "player": self.player,
+                    "row_number": 2,
+                    "original_row": {"Email": "player@example.com"},
+                }
+            ],
+            actor=self.staff,
+            options=ProvisioningOptions(
+                enabled=True, activate_users=False, email_column="Email"
+            ),
+        )
+
+        serialized = summary.to_dict()
+        self.assertIsInstance(summary, ProvisioningSummary)
+        self.assertEqual(serialized["users_created"], 1)
+        self.assertEqual(serialized["already_linked"], 0)
+        self.assertNotIn("20120501", str(serialized))
+        self.assertNotIn("password", str(serialized).casefold())
+
+
+class AccountRegressionTests(TestCase):
+    def test_phase_two_creates_user_player_link_but_no_provisioning_models(self):
+        model_names = {
+            model.__name__ for model in AccountProfile._meta.apps.get_models()
+        }
+
+        self.assertIn("AccountProfile", model_names)
+        self.assertIn("UserPlayerLink", model_names)
+        self.assertNotIn("AccountProvisioningBatch", model_names)
+
+    def test_players_player_does_not_gain_direct_user_field(self):
+        self.assertNotIn("user", {field.name for field in Player._meta.fields})
+
+    def test_analytics_evaluation_permission_remains_any_authenticated_user(self):
+        user = User.objects.create_user(username="evaluator", password="testpass")
+
+        self.assertTrue(can_submit_coach_assessment(user))
+        self.assertFalse(can_submit_coach_assessment(None))
diff --git a/accounts/tests/test_authentication.py b/accounts/tests/test_authentication.py
new file mode 100644
index 0000000..4354094
--- /dev/null
+++ b/accounts/tests/test_authentication.py
@@ -0,0 +1,382 @@
+from accounts.tests.helpers import (
+    ACCOUNT_LOGIN_PATH,
+    ACCOUNT_LOGOUT_PATH,
+    ACCOUNT_PASSWORD_PATH,
+    ACCOUNT_PROFILE_PATH,
+    ANALYTICS_HOME_PATH,
+    SESSION_KEY,
+    AccountRole,
+    Player,
+    TestCase,
+    User,
+    UserPlayerRelationship,
+    get_or_create_account_profile,
+    is_password_change_allowed_path,
+    landing_url_for_user,
+    link_user_to_player,
+    reverse,
+    set_account_role,
+    settings,
+    should_force_password_change,
+)
+
+
+class AccountAuthRedirectServiceTests(TestCase):
+    def test_landing_url_for_user(self):
+        anonymous = None
+        staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        regular = User.objects.create_user(username="regular", password="testpass")
+
+        self.assertEqual(landing_url_for_user(anonymous), ACCOUNT_LOGIN_PATH)
+        self.assertEqual(landing_url_for_user(staff), ANALYTICS_HOME_PATH)
+        self.assertEqual(landing_url_for_user(regular), ACCOUNT_PROFILE_PATH)
+
+    def test_should_force_password_change(self):
+        user = User.objects.create_user(username="user", password="testpass")
+        profile = get_or_create_account_profile(user)
+
+        self.assertFalse(should_force_password_change(user))
+        profile.must_change_password = True
+        profile.save(update_fields=["must_change_password", "updated_at"])
+        self.assertTrue(should_force_password_change(user))
+
+    def test_missing_account_profile_is_safe(self):
+        user = User.objects.create_user(username="user", password="testpass")
+
+        self.assertFalse(should_force_password_change(user))
+
+    def test_allowed_paths(self):
+        user = User.objects.create_user(username="user", password="testpass")
+        superuser = User.objects.create_superuser(username="admin", password="testpass")
+
+        self.assertTrue(is_password_change_allowed_path(ACCOUNT_PASSWORD_PATH, user))
+        self.assertTrue(is_password_change_allowed_path(ACCOUNT_LOGOUT_PATH, user))
+        self.assertTrue(is_password_change_allowed_path(ACCOUNT_LOGIN_PATH, user))
+        self.assertTrue(is_password_change_allowed_path("/static/app.css", user))
+        self.assertTrue(is_password_change_allowed_path("/media/avatar.png", user))
+        self.assertFalse(is_password_change_allowed_path("/admin/", user))
+        self.assertTrue(is_password_change_allowed_path("/admin/", superuser))
+        self.assertFalse(is_password_change_allowed_path("/analytics/", user))
+
+
+class AccountAuthViewTests(TestCase):
+    def setUp(self):
+        self.user = User.objects.create_user(username="user", password="testpass")
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+
+    def test_login_page_renders(self):
+        response = self.client.get(reverse("accounts:login"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Login")
+
+    def test_non_staff_login_lands_at_profile(self):
+        response = self.client.post(
+            reverse("accounts:login"),
+            {"username": "user", "password": "testpass"},
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], landing_url_for_user(self.user))
+
+    def test_staff_login_lands_at_analytics(self):
+        response = self.client.post(
+            reverse("accounts:login"),
+            {"username": "staff", "password": "testpass"},
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], landing_url_for_user(self.staff))
+
+    def test_safe_next_parameter_is_respected_without_forced_password_change(self):
+        response = self.client.post(
+            f"{reverse('accounts:login')}?next=/analytics/assessments/",
+            {"username": "user", "password": "testpass"},
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], "/analytics/assessments/")
+
+    def test_forced_password_change_overrides_next_parameter(self):
+        profile = get_or_create_account_profile(self.user)
+        profile.must_change_password = True
+        profile.save(update_fields=["must_change_password", "updated_at"])
+
+        response = self.client.post(
+            f"{reverse('accounts:login')}?next=/analytics/assessments/",
+            {"username": "user", "password": "testpass"},
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], ACCOUNT_PASSWORD_PATH)
+
+    def test_logout_redirects_to_account_login(self):
+        self.client.force_login(self.user)
+
+        response = self.client.post(reverse("accounts:logout"))
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], ACCOUNT_LOGIN_PATH)
+
+    def test_password_page_renders_for_authenticated_user(self):
+        self.client.force_login(self.user)
+
+        response = self.client.get(reverse("accounts:password-change"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Update Password")
+
+    def test_password_change_clears_flag_and_keeps_user_logged_in(self):
+        profile = get_or_create_account_profile(self.user)
+        profile.must_change_password = True
+        profile.save(update_fields=["must_change_password", "updated_at"])
+        self.client.force_login(self.user)
+
+        response = self.client.post(
+            reverse("accounts:password-change"),
+            {
+                "old_password": "testpass",
+                "new_password1": "new-strong-pass-123",
+                "new_password2": "new-strong-pass-123",
+            },
+        )
+
+        profile.refresh_from_db()
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], landing_url_for_user(self.user))
+        self.assertFalse(profile.must_change_password)
+        self.assertIn(SESSION_KEY, self.client.session)
+        self.user.refresh_from_db()
+        self.assertTrue(self.user.check_password("new-strong-pass-123"))
+
+        landing_response = self.client.get(response["Location"])
+        self.assertEqual(landing_response.status_code, 200)
+        self.assertNotEqual(landing_response.get("Location"), ACCOUNT_PASSWORD_PATH)
+
+    def test_password_change_redirects_staff_to_landing_service_url(self):
+        profile = get_or_create_account_profile(self.staff)
+        profile.must_change_password = True
+        profile.save(update_fields=["must_change_password", "updated_at"])
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("accounts:password-change"),
+            {
+                "old_password": "testpass",
+                "new_password1": "new-strong-pass-123",
+                "new_password2": "new-strong-pass-123",
+            },
+        )
+
+        profile.refresh_from_db()
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], landing_url_for_user(self.staff))
+        self.assertFalse(profile.must_change_password)
+        self.assertIn(SESSION_KEY, self.client.session)
+
+    def test_inactive_user_cannot_login(self):
+        inactive = User.objects.create_user(
+            username="inactive", password="testpass", is_active=False
+        )
+        get_or_create_account_profile(inactive)
+
+        response = self.client.post(
+            reverse("accounts:login"),
+            {"username": "inactive", "password": "testpass"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertNotIn(SESSION_KEY, self.client.session)
+
+    def test_profile_page_renders_basic_account_info(self):
+        get_or_create_account_profile(self.user)
+        self.client.force_login(self.user)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account Profile")
+        self.assertContains(response, "Guest Evaluator")
+
+    def test_profile_submit_evaluation_link_uses_service_permissions(self):
+        cases = [
+            (AccountRole.COACH, True),
+            (AccountRole.PLAYER, True),
+            (AccountRole.GUEST_EVALUATOR, True),
+            (AccountRole.PARENT, False),
+        ]
+        for role, should_see_link in cases:
+            with self.subTest(role=role):
+                user = User.objects.create_user(
+                    username=f"profile-{role}", password="testpass"
+                )
+                set_account_role(user, role)
+                self.client.force_login(user)
+
+                response = self.client.get(reverse("accounts:profile"))
+
+                if should_see_link:
+                    self.assertContains(response, reverse("analytics:evaluation-list"))
+                    self.assertContains(response, "Submit Evaluation")
+                else:
+                    self.assertNotContains(
+                        response, reverse("analytics:evaluation-list")
+                    )
+                    self.assertNotContains(response, "Submit Evaluation")
+                self.client.logout()
+
+    def test_profile_my_evaluations_link_requires_self_link(self):
+        player = Player.objects.create(first_name="Linked", last_name="Player")
+        player_user = User.objects.create_user(
+            username="linked-player", password="testpass"
+        )
+        coach = User.objects.create_user(username="unlinked-coach", password="testpass")
+        parent = User.objects.create_user(
+            username="unlinked-parent", password="testpass"
+        )
+        set_account_role(player_user, AccountRole.PLAYER)
+        set_account_role(coach, AccountRole.COACH)
+        set_account_role(parent, AccountRole.PARENT)
+        link_user_to_player(
+            player_user,
+            player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+
+        self.client.force_login(player_user)
+        response = self.client.get(reverse("accounts:profile"))
+        self.assertContains(response, reverse("analytics:my-evaluations"))
+        self.assertContains(response, "My Evaluations")
+
+        for user in [coach, parent]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                response = self.client.get(reverse("accounts:profile"))
+                self.assertNotContains(response, reverse("analytics:my-evaluations"))
+                self.client.logout()
+
+
+class AccountPasswordMiddlewareTests(TestCase):
+    def setUp(self):
+        self.user = User.objects.create_user(username="user", password="testpass")
+        self.profile = get_or_create_account_profile(self.user)
+
+    def require_password_change(self):
+        self.profile.must_change_password = True
+        self.profile.save(update_fields=["must_change_password", "updated_at"])
+        self.client.force_login(self.user)
+
+    def test_forced_password_user_redirected_from_normal_page(self):
+        self.require_password_change()
+
+        response = self.client.get(reverse("analytics:assessment-list"))
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(response["Location"], ACCOUNT_PASSWORD_PATH)
+
+    def test_allowed_paths_do_not_redirect_loop(self):
+        self.require_password_change()
+
+        self.assertEqual(
+            self.client.get(reverse("accounts:password-change")).status_code, 200
+        )
+        self.assertNotEqual(self.client.get(reverse("accounts:login")).status_code, 302)
+        self.assertEqual(self.client.post(reverse("accounts:logout")).status_code, 302)
+
+    def test_password_page_post_is_not_blocked_by_middleware(self):
+        self.require_password_change()
+
+        response = self.client.post(
+            reverse("accounts:password-change"),
+            {
+                "old_password": "wrong-password",
+                "new_password1": "new-strong-pass-123",
+                "new_password2": "new-strong-pass-123",
+            },
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Update Password")
+
+    def test_middleware_does_not_redirect_after_successful_password_change(self):
+        self.require_password_change()
+
+        response = self.client.post(
+            reverse("accounts:password-change"),
+            {
+                "old_password": "testpass",
+                "new_password1": "new-strong-pass-123",
+                "new_password2": "new-strong-pass-123",
+            },
+        )
+
+        self.profile.refresh_from_db()
+        self.assertEqual(response.status_code, 302)
+        self.assertFalse(self.profile.must_change_password)
+        profile_response = self.client.get(reverse("accounts:profile"))
+        self.assertEqual(profile_response.status_code, 200)
+
+    def test_static_media_and_superuser_admin_paths_are_allowed(self):
+        superuser = User.objects.create_superuser(username="admin", password="testpass")
+        profile = get_or_create_account_profile(superuser)
+        profile.must_change_password = True
+        profile.save(update_fields=["must_change_password", "updated_at"])
+        self.client.force_login(superuser)
+
+        self.assertNotEqual(self.client.get("/static/app.css").status_code, 302)
+        self.assertNotEqual(self.client.get("/media/app.png").status_code, 302)
+        self.assertNotEqual(self.client.get("/admin/").status_code, 302)
+
+    def test_user_without_forced_password_change_is_not_redirected(self):
+        self.client.force_login(self.user)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+
+    def test_missing_account_profile_is_safe(self):
+        user = User.objects.create_user(username="missing-profile", password="testpass")
+        self.client.force_login(user)
+
+        response = self.client.get(reverse("accounts:profile"))
+
+        self.assertEqual(response.status_code, 200)
+
+
+class AccountPdpCoexistenceTests(TestCase):
+    def test_pdp_login_route_still_renders(self):
+        response = self.client.get(reverse("pdp:login"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Athlete Login")
+
+    def test_pdp_routes_and_middleware_remain_installed(self):
+        self.assertEqual(reverse("pdp:login"), "/pdp/login/")
+        self.assertIn(
+            "pdp.middleware.FirstLoginPasswordChangeMiddleware", settings.MIDDLEWARE
+        )
+        self.assertIn(
+            "accounts.middleware.AccountPasswordChangeRequiredMiddleware",
+            settings.MIDDLEWARE,
+        )
+        self.assertLess(
+            settings.MIDDLEWARE.index(
+                "pdp.middleware.FirstLoginPasswordChangeMiddleware"
+            ),
+            settings.MIDDLEWARE.index(
+                "accounts.middleware.AccountPasswordChangeRequiredMiddleware"
+            ),
+        )
+
+    def test_global_login_settings_are_account_forward(self):
+        self.assertEqual(settings.LOGIN_URL, ACCOUNT_LOGIN_PATH)
+        self.assertEqual(settings.LOGIN_REDIRECT_URL, ACCOUNT_PROFILE_PATH)
+
+    def test_account_operations_routes_are_platform_account_routes(self):
+        self.assertEqual(reverse("accounts:operations-dashboard"), "/accounts/")
+        self.assertEqual(reverse("accounts:user-list"), "/accounts/users/")
diff --git a/accounts/tests/test_coach_import.py b/accounts/tests/test_coach_import.py
new file mode 100644
index 0000000..ed4a6f3
--- /dev/null
+++ b/accounts/tests/test_coach_import.py
@@ -0,0 +1,455 @@
+from accounts.tests.helpers import (
+    RESULT_CONFLICT,
+    RESULT_CREATED,
+    RESULT_REUSED,
+    AccountRole,
+    CoachAssignmentRole,
+    CoachSeasonAssignment,
+    Player,
+    SeasonTeam,
+    TestCase,
+    User,
+    UserPlayerLink,
+    ValidationError,
+    base_username_for_person,
+    commit_coach_import,
+    create_season,
+    preview_coach_import,
+    set_account_role,
+    username_for_person,
+)
+
+
+class CoachImportServiceTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        self.next_season = create_season(key="2027-spring", name="2027 Spring")
+
+    def csv_text(self, rows):
+        return (
+            "first_name,last_name,email,username,team,division,is_active,notes,source_id,assignment_role,assignment_start_date,assignment_end_date,assignment_source_id\n"
+            + "\n".join(rows)
+        )
+
+    def test_valid_csv_creates_active_coach_with_one_time_password(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(
+                ["Casey,Coach,casey@example.com,,Reds,13U,true,Lead coach,C001"]
+            ),
+            season=self.season,
+        )
+
+        user = User.objects.get(email="casey@example.com")
+        profile = user.account_profile
+        result_row = result.rows[0]
+        self.assertEqual(result_row.status, RESULT_CREATED)
+        self.assertEqual(user.username, "casey.coach")
+        self.assertEqual(user.first_name, "Casey")
+        self.assertEqual(user.last_name, "Coach")
+        self.assertTrue(user.is_active)
+        self.assertEqual(profile.role, AccountRole.COACH)
+        self.assertTrue(profile.must_change_password)
+        self.assertEqual(profile.metadata["team"], "Reds")
+        self.assertEqual(profile.metadata["division"], "13U")
+        self.assertTrue(result_row.temporary_password)
+        self.assertTrue(user.check_password(result_row.temporary_password))
+        self.assertNotIn(result_row.temporary_password, repr(result_row))
+        self.assertFalse(UserPlayerLink.objects.filter(user=user).exists())
+        self.assertEqual(Player.objects.count(), 0)
+        self.assertEqual(result.users_created, 1)
+        self.assertEqual(result.active_accounts, 1)
+        self.assertEqual(result.inactive_accounts, 0)
+        self.assertEqual(result.password_change_required, 1)
+        assignment = CoachSeasonAssignment.objects.select_related("season_team").get(
+            user=user
+        )
+        self.assertEqual(assignment.season_team.season, self.season)
+        self.assertEqual(assignment.season_team.name, "Reds")
+        self.assertEqual(
+            assignment.assignment_role, CoachAssignmentRole.ASSISTANT_COACH
+        )
+        self.assertTrue(assignment.is_primary)
+        self.assertEqual(result.season_teams_created, 1)
+        self.assertEqual(result.assignments_created, 1)
+
+    def test_coach_import_requires_active_season(self):
+        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
+
+        preview = preview_coach_import(
+            self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"])
+        )
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
+            self.csv_text(
+                [
+                    "Head,Coach,head@example.com,,Reds,13U,true,,C001,head,2026-04-01,2026-08-31,A001"
+                ]
+            ),
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
+        self.assertFalse(
+            User.objects.filter(
+                email__in=["no.team@example.com", "no.division@example.com"]
+            ).exists()
+        )
+        self.assertFalse(SeasonTeam.objects.exists())
+
+    def test_imported_coach_can_be_inactive(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(
+                ["Inactive,Coach,inactive.coach@example.com,,Reds,13U,false,,"]
+            ),
+            season=self.season,
+        )
+
+        user = User.objects.get(username="inactive.coach")
+        self.assertFalse(user.is_active)
+        self.assertFalse(result.rows[0].is_active)
+        self.assertEqual(result.inactive_accounts, 1)
+
+    def test_explicit_username_is_normalized_and_validated(self):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(
+                ["User,Name,user.name@example.com,Explicit.User,Reds,13U,true,,"]
+            ),
+            season=self.season,
+        )
+
+        self.assertEqual(result.rows[0].username, "explicit.user")
+        self.assertTrue(User.objects.filter(username="explicit.user").exists())
+
+    def test_generated_username_collision_uses_suffix(self):
+        User.objects.create_user(username="casey.coach", email="other@example.com")
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Casey,Coach,casey2@example.com,,Reds,13U,true,,"]),
+            season=self.season,
+        )
+
+        self.assertEqual(result.rows[0].username, "casey.coach2")
+        self.assertTrue(User.objects.filter(username="casey.coach2").exists())
+
+    def test_duplicate_email_with_existing_coach_reuses_account(self):
+        existing = User.objects.create_user(
+            username="existing.coach", email="coach@example.com", password="oldpass"
+        )
+        set_account_role(existing, AccountRole.COACH)
+        original_password_hash = existing.password
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Existing,Coach,COACH@example.com,,Reds,13U,true,,"]),
+            season=self.season,
+        )
+
+        existing.refresh_from_db()
+        existing.account_profile.refresh_from_db()
+        self.assertEqual(result.rows[0].status, RESULT_REUSED)
+        self.assertEqual(result.existing_coaches_reused, 1)
+        self.assertEqual(
+            User.objects.filter(email__iexact="coach@example.com").count(), 1
+        )
+        self.assertFalse(existing.account_profile.must_change_password)
+        self.assertFalse(result.rows[0].temporary_password)
+        self.assertEqual(existing.password, original_password_hash)
+        self.assertEqual(existing.account_profile.role, AccountRole.COACH)
+        self.assertEqual(CoachSeasonAssignment.objects.filter(user=existing).count(), 1)
+
+    def test_existing_inactive_coach_is_not_activated_or_reset(self):
+        existing = User.objects.create_user(
+            username="inactive.existing",
+            email="inactive-existing@example.com",
+            password="oldpass",
+            is_active=False,
+        )
+        profile = set_account_role(existing, AccountRole.COACH)
+        profile.must_change_password = False
+        profile.save(update_fields=["must_change_password", "updated_at"])
+        original_password_hash = existing.password
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(
+                ["Inactive,Existing,inactive-existing@example.com,,Reds,13U,true,,"]
+            ),
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
+            self.csv_text(
+                [
+                    "Return,Coach,return@example.com,,Reds,13U,true,,C001,assistant,,,A001"
+                ]
+            ),
+            season=self.season,
+        )
+        user = User.objects.get(email="return@example.com")
+        original_password_hash = user.password
+
+        second = commit_coach_import(
+            self.staff,
+            self.csv_text(
+                [
+                    "Return,Coach,return@example.com,,Reds,13U,true,Updated notes,C001,assistant,2026-04-01,,A001"
+                ]
+            ),
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
+        self.assertEqual(
+            SeasonTeam.objects.filter(name="Reds", division="13U").count(), 2
+        )
+
+    def test_same_coach_can_have_multiple_teams_and_roles_without_replacing_primary(
+        self,
+    ):
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
+        assignments = CoachSeasonAssignment.objects.filter(
+            user=user, season_team__season=self.season
+        )
+
+        self.assertEqual(assignments.count(), 3)
+        self.assertEqual(assignments.filter(is_primary=True).count(), 1)
+        self.assertEqual(
+            assignments.get(is_primary=True).assignment_role,
+            CoachAssignmentRole.HEAD_COACH,
+        )
+
+    def test_csv_season_mismatch_is_rejected(self):
+        preview = preview_coach_import(
+            "first_name,last_name,email,team,division,season\nMismatch,Coach,mismatch@example.com,Reds,13U,2027 Spring\n",
+            season=self.season,
+        )
+
+        self.assertEqual(preview.rows[0].status, "error")
+        self.assertIn("season does not match", preview.rows[0].messages[0])
+
+    def test_duplicate_email_with_non_coach_conflicts(self):
+        existing = User.objects.create_user(
+            username="player.user", email="shared@example.com"
+        )
+        set_account_role(existing, AccountRole.PLAYER)
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Shared,Coach,shared@example.com,,Reds,13U,true,,"]),
+            season=self.season,
+        )
+
+        self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
+        self.assertEqual(result.conflicts, 1)
+        self.assertEqual(User.objects.count(), 2)
+        self.assertFalse(CoachSeasonAssignment.objects.exists())
+
+    def test_explicit_duplicate_username_conflicts(self):
+        User.objects.create_user(username="taken.name")
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Taken,Name,taken@example.com,taken.name,Reds,13U,true,,"]),
+            season=self.season,
+        )
+
+        self.assertEqual(result.rows[0].status, RESULT_CONFLICT)
+        self.assertFalse(User.objects.filter(email="taken@example.com").exists())
+
+    def test_duplicate_email_reuses_created_coach_but_duplicate_username_conflicts(
+        self,
+    ):
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(
+                [
+                    "First,Coach,first@example.com,same.username,Reds,13U,true,,",
+                    "Second,Coach,first@example.com,other.username,Reds,13U,true,,",
+                    "Third,Coach,third@example.com,same.username,Reds,13U,true,,",
+                ]
+            ),
+            season=self.season,
+        )
+
+        self.assertEqual(result.users_created, 1)
+        self.assertEqual(result.existing_coaches_reused, 1)
+        self.assertEqual(result.conflicts, 1)
+        self.assertTrue(User.objects.filter(email="first@example.com").exists())
+        self.assertFalse(User.objects.filter(email="third@example.com").exists())
+        self.assertEqual(
+            CoachSeasonAssignment.objects.filter(
+                user__email="first@example.com"
+            ).count(),
+            1,
+        )
+
+    def test_blank_csv_fields_do_not_wipe_existing_metadata(self):
+        existing = User.objects.create_user(
+            username="metadata.coach", email="metadata@example.com"
+        )
+        profile = set_account_role(existing, AccountRole.COACH)
+        profile.metadata = {
+            "team": "Reds",
+            "division": "13U",
+            "notes": "Keep this",
+            "custom": "value",
+        }
+        profile.save(update_fields=["metadata", "updated_at"])
+
+        result = commit_coach_import(
+            self.staff,
+            self.csv_text(["Metadata,Coach,metadata@example.com,,Reds,13U,true,,"]),
+            season=self.season,
+        )
+
+        profile.refresh_from_db()
+        self.assertEqual(result.rows[0].status, RESULT_REUSED)
+        self.assertEqual(profile.metadata["team"], "Reds")
+        self.assertEqual(profile.metadata["division"], "13U")
+        self.assertEqual(profile.metadata["notes"], "Keep this")
+        self.assertEqual(profile.metadata["custom"], "value")
+        self.assertFalse(result.rows[0].temporary_password)
+        self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
+
+    def test_missing_required_fields_produce_row_errors(self):
+        preview = preview_coach_import(
+            "first_name,last_name,email,team,division\nMissing,Email,,Reds,13U\n",
+            season=self.season,
+        )
+        result = commit_coach_import(
+            self.staff,
+            "first_name,last_name,email,team,division\nMissing,Email,,Reds,13U\n",
+            season=self.season,
+        )
+
+        self.assertEqual(preview.rows[0].status, "error")
+        self.assertIn("Missing required field", preview.rows[0].messages[0])
+        self.assertEqual(result.errors, 1)
+        self.assertEqual(User.objects.count(), 1)
+
+    def test_missing_required_columns_produce_import_error(self):
+        result = commit_coach_import(
+            self.staff, "first_name,last_name\nNo,Email\n", season=self.season
+        )
+
+        self.assertEqual(result.errors, 1)
+        self.assertIn("Missing required column", result.rows[0].messages[0])
+
+    def test_regular_user_cannot_commit_coach_import(self):
+        regular = User.objects.create_user(username="regular", password="testpass")
+
+        with self.assertRaisesMessage(
+            ValidationError, "Only staff users can import coaches"
+        ):
+            commit_coach_import(
+                regular,
+                self.csv_text(["Casey,Coach,casey@example.com,,Reds,13U,true,,"]),
+                season=self.season,
+            )
+
+    def test_username_for_person_uses_same_normalization_style(self):
+        self.assertEqual(
+            base_username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne"
+        )
+        self.assertEqual(username_for_person("Jos\u00e9", "Van Horne"), "jose.vanhorne")
diff --git a/accounts/tests/test_player_links.py b/accounts/tests/test_player_links.py
new file mode 100644
index 0000000..186dde1
--- /dev/null
+++ b/accounts/tests/test_player_links.py
@@ -0,0 +1,383 @@
+from accounts.tests.helpers import (
+    IntegrityError,
+    Player,
+    PlayerImportBatch,
+    TestCase,
+    User,
+    UserPlayerLink,
+    UserPlayerRelationship,
+    ValidationError,
+    activate_link,
+    deactivate_link,
+    get_players_for_user,
+    get_primary_player,
+    get_primary_user,
+    get_users_for_player,
+    is_player_self,
+    link_user_to_player,
+    set_primary_self_link,
+    transaction,
+    unlink_user_from_player,
+)
+
+
+class UserPlayerLinkModelTests(TestCase):
+    def setUp(self):
+        self.user = User.objects.create_user(username="player", password="testpass")
+        self.other_user = User.objects.create_user(
+            username="other", password="testpass"
+        )
+        self.player = Player.objects.create(first_name="Alex", last_name="Player")
+        self.other_player = Player.objects.create(
+            first_name="Blake", last_name="Player"
+        )
+
+    def test_user_player_link_can_link_user_to_player(self):
+        link = UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+
+        self.assertEqual(link.user, self.user)
+        self.assertEqual(link.player, self.player)
+        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
+        self.assertTrue(link.is_active)
+        self.assertTrue(link.is_primary)
+
+    def test_user_can_link_to_multiple_players(self):
+        UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.PARENT,
+        )
+        UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.other_player,
+            relationship=UserPlayerRelationship.PARENT,
+        )
+
+        self.assertEqual(
+            UserPlayerLink.objects.filter(user=self.user, is_active=True).count(), 2
+        )
+
+    def test_player_can_link_to_multiple_users(self):
+        UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.PARENT,
+        )
+        UserPlayerLink.objects.create(
+            user=self.other_user,
+            player=self.player,
+            relationship=UserPlayerRelationship.GUARDIAN,
+        )
+
+        self.assertEqual(
+            UserPlayerLink.objects.filter(player=self.player, is_active=True).count(), 2
+        )
+
+    def test_duplicate_active_relationship_is_blocked_but_inactive_history_is_allowed(
+        self,
+    ):
+        UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.PARENT,
+        )
+
+        with self.assertRaises(IntegrityError):
+            with transaction.atomic():
+                UserPlayerLink.objects.create(
+                    user=self.user,
+                    player=self.player,
+                    relationship=UserPlayerRelationship.PARENT,
+                )
+
+        UserPlayerLink.objects.filter(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.PARENT,
+        ).update(is_active=False)
+        UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.PARENT,
+        )
+
+        self.assertEqual(
+            UserPlayerLink.objects.filter(
+                user=self.user,
+                player=self.player,
+                relationship=UserPlayerRelationship.PARENT,
+            ).count(),
+            2,
+        )
+
+    def test_only_one_active_primary_self_link_per_user(self):
+        UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+
+        with self.assertRaises(IntegrityError):
+            with transaction.atomic():
+                UserPlayerLink.objects.create(
+                    user=self.user,
+                    player=self.other_player,
+                    relationship=UserPlayerRelationship.SELF,
+                    is_primary=True,
+                )
+
+    def test_only_one_active_primary_self_link_per_player(self):
+        UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+
+        with self.assertRaises(IntegrityError):
+            with transaction.atomic():
+                UserPlayerLink.objects.create(
+                    user=self.other_user,
+                    player=self.player,
+                    relationship=UserPlayerRelationship.SELF,
+                    is_primary=True,
+                )
+
+    def test_import_provenance_fields_persist(self):
+        import_batch = PlayerImportBatch.objects.create(
+            source="manual_staff_csv",
+            original_filename="players.csv",
+            uploaded_by=self.other_user,
+        )
+
+        link = UserPlayerLink.objects.create(
+            user=self.user,
+            player=self.player,
+            relationship=UserPlayerRelationship.SELF,
+            created_from_import=True,
+            import_batch=import_batch,
+            metadata={"row": 2},
+        )
+
+        self.assertTrue(link.created_from_import)
+        self.assertEqual(link.import_batch, import_batch)
+        self.assertEqual(link.metadata, {"row": 2})
+
+
+class UserPlayerLinkServiceTests(TestCase):
+    def setUp(self):
+        self.user = User.objects.create_user(username="player", password="testpass")
+        self.other_user = User.objects.create_user(
+            username="other", password="testpass"
+        )
+        self.player = Player.objects.create(first_name="Alex", last_name="Player")
+        self.other_player = Player.objects.create(
+            first_name="Blake", last_name="Player"
+        )
+
+    def test_link_user_to_player_creates_active_link(self):
+        link = link_user_to_player(self.user, self.player)
+
+        self.assertEqual(link.user, self.user)
+        self.assertEqual(link.player, self.player)
+        self.assertEqual(link.relationship, UserPlayerRelationship.SELF)
+        self.assertTrue(link.is_primary)
+        self.assertTrue(link.is_active)
+
+    def test_link_user_to_player_reuses_existing_active_link(self):
+        link = link_user_to_player(
+            self.user, self.player, metadata={"source": "initial"}
+        )
+        same_link = link_user_to_player(
+            self.user,
+            self.player,
+            created_from_import=True,
+            metadata={"source": "updated"},
+        )
+
+        self.assertEqual(link.pk, same_link.pk)
+        self.assertTrue(same_link.created_from_import)
+        self.assertEqual(same_link.metadata, {"source": "updated"})
+        self.assertEqual(UserPlayerLink.objects.count(), 1)
+
+    def test_link_user_to_player_rejects_invalid_inputs(self):
+        with self.assertRaises(ValidationError):
+            link_user_to_player(None, self.player)
+        with self.assertRaises(ValidationError):
+            link_user_to_player(self.user, None)
+        with self.assertRaises(ValidationError):
+            link_user_to_player(self.user, self.player, relationship="unsupported")
+        with self.assertRaises(ValidationError):
+            link_user_to_player(self.user, self.player, metadata=["not", "dict"])
+
+    def test_link_user_to_player_rejects_primary_non_self_link(self):
+        with self.assertRaises(ValidationError):
+            link_user_to_player(
+                self.user,
+                self.player,
+                relationship=UserPlayerRelationship.PARENT,
+                is_primary=True,
+            )
+
+    def test_link_user_to_player_rejects_primary_self_conflicts(self):
+        link_user_to_player(self.user, self.player)
+
+        with self.assertRaises(ValidationError):
+            link_user_to_player(self.user, self.other_player)
+        with self.assertRaises(ValidationError):
+            link_user_to_player(self.other_user, self.player)
+
+    def test_deactivate_link_marks_inactive_and_clears_primary(self):
+        link = link_user_to_player(self.user, self.player)
+
+        deactivate_link(link)
+        link.refresh_from_db()
+
+        self.assertFalse(link.is_active)
+        self.assertFalse(link.is_primary)
+
+    def test_activate_link_reactivates_valid_inactive_link(self):
+        link = link_user_to_player(self.user, self.player)
+        deactivate_link(link)
+
+        activate_link(link)
+        link.refresh_from_db()
+
+        self.assertTrue(link.is_active)
+        self.assertFalse(link.is_primary)
+
+    def test_activate_link_rejects_duplicate_active_relationship(self):
+        link = link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+        deactivate_link(link)
+        link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+
+        with self.assertRaises(ValidationError):
+            activate_link(link)
+
+    def test_unlink_user_from_player_deactivates_matching_links(self):
+        link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+        link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.COACH,
+            is_primary=False,
+        )
+
+        count = unlink_user_from_player(
+            self.user, self.player, relationship=UserPlayerRelationship.PARENT
+        )
+
+        self.assertEqual(count, 1)
+        self.assertFalse(
+            UserPlayerLink.objects.get(
+                user=self.user,
+                player=self.player,
+                relationship=UserPlayerRelationship.PARENT,
+            ).is_active
+        )
+        self.assertTrue(
+            UserPlayerLink.objects.get(
+                user=self.user,
+                player=self.player,
+                relationship=UserPlayerRelationship.COACH,
+            ).is_active
+        )
+
+    def test_lookup_helpers_default_to_active_links(self):
+        active_link = link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+        inactive_link = link_user_to_player(
+            self.user,
+            self.other_player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+        deactivate_link(inactive_link)
+
+        self.assertEqual(list(get_players_for_user(self.user)), [self.player])
+        self.assertCountEqual(
+            list(get_players_for_user(self.user, active_only=False)),
+            [self.player, self.other_player],
+        )
+        self.assertEqual(list(get_users_for_player(self.player)), [self.user])
+        self.assertEqual(list(get_users_for_player(self.other_player)), [])
+        self.assertEqual(
+            list(get_users_for_player(self.other_player, active_only=False)),
+            [self.user],
+        )
+        self.assertTrue(active_link.is_active)
+
+    def test_primary_and_self_helpers(self):
+        link_user_to_player(self.user, self.player)
+
+        self.assertEqual(get_primary_player(self.user), self.player)
+        self.assertEqual(get_primary_user(self.player), self.user)
+        self.assertTrue(is_player_self(self.user, self.player))
+        self.assertFalse(is_player_self(self.user, self.other_player))
+
+    def test_set_primary_self_link_switches_primary_link(self):
+        first_link = link_user_to_player(self.user, self.player)
+        second_link = link_user_to_player(
+            self.user,
+            self.other_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+
+        set_primary_self_link(second_link)
+        first_link.refresh_from_db()
+        second_link.refresh_from_db()
+
+        self.assertFalse(first_link.is_primary)
+        self.assertTrue(second_link.is_primary)
+        self.assertTrue(second_link.is_active)
+        self.assertEqual(get_primary_player(self.user), self.other_player)
+
+    def test_set_primary_self_link_rejects_non_self_link(self):
+        parent_link = link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+
+        with self.assertRaises(ValidationError):
+            set_primary_self_link(parent_link)
+
+    def test_is_player_self_ignores_inactive_or_non_self_links(self):
+        parent_link = link_user_to_player(
+            self.user,
+            self.player,
+            relationship=UserPlayerRelationship.PARENT,
+            is_primary=False,
+        )
+
+        self.assertFalse(is_player_self(self.user, self.player))
+
+        deactivate_link(parent_link)
+        self.assertFalse(is_player_self(self.user, self.player))
diff --git a/accounts/tests/test_profiles.py b/accounts/tests/test_profiles.py
new file mode 100644
index 0000000..82b7cfd
--- /dev/null
+++ b/accounts/tests/test_profiles.py
@@ -0,0 +1,154 @@
+from accounts.tests.helpers import (
+    AccountProfile,
+    AccountRole,
+    TestCase,
+    User,
+    UserPlayerLink,
+    ValidationError,
+    admin,
+    can_access_account_operations,
+    can_change_account_role,
+    can_manage_accounts,
+    can_manage_privileged_accounts,
+    can_submit_evaluations,
+    can_view_account_detail,
+    can_view_account_list,
+    can_view_account_operations_dashboard,
+    can_view_account_profile,
+    get_account_role,
+    get_or_create_account_profile,
+    role_for_user,
+    role_label,
+    set_account_role,
+    validate_role,
+)
+
+
+class AccountProfileServiceTests(TestCase):
+    def test_get_or_create_account_profile_creates_guest_profile_for_regular_user(self):
+        user = User.objects.create_user(username="player", password="testpass")
+
+        profile = get_or_create_account_profile(user)
+        second = get_or_create_account_profile(user)
+
+        self.assertEqual(profile, second)
+        self.assertEqual(profile.role, AccountRole.GUEST_EVALUATOR)
+        self.assertFalse(profile.must_change_password)
+        self.assertFalse(profile.created_from_import)
+        self.assertIsNone(profile.import_batch)
+
+    def test_default_role_uses_django_admin_flags_for_new_profiles(self):
+        staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        admin_user = User.objects.create_superuser(
+            username="admin", password="testpass"
+        )
+
+        self.assertEqual(get_or_create_account_profile(staff).role, AccountRole.STAFF)
+        self.assertEqual(
+            get_or_create_account_profile(admin_user).role, AccountRole.ADMIN
+        )
+
+    def test_role_for_user_falls_back_without_profile(self):
+        staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        regular = User.objects.create_user(username="regular", password="testpass")
+
+        self.assertEqual(role_for_user(staff), AccountRole.STAFF)
+        self.assertEqual(role_for_user(regular), AccountRole.GUEST_EVALUATOR)
+
+    def test_set_account_role_changes_only_profile_role(self):
+        user = User.objects.create_user(username="coach", password="testpass")
+
+        profile = set_account_role(user, AccountRole.COACH)
+        user.refresh_from_db()
+
+        self.assertEqual(profile.role, AccountRole.COACH)
+        self.assertEqual(get_account_role(user), AccountRole.COACH)
+        self.assertFalse(user.is_staff)
+        self.assertFalse(user.is_superuser)
+
+    def test_role_validation_and_labels(self):
+        self.assertEqual(validate_role(AccountRole.PLAYER), AccountRole.PLAYER)
+        self.assertEqual(role_label(AccountRole.PARENT), "Parent")
+
+        with self.assertRaises(ValidationError):
+            validate_role("unsupported")
+
+    def test_profile_creation_requires_authenticated_user(self):
+        with self.assertRaises(ValidationError):
+            get_or_create_account_profile(None)
+
+
+class AccountPermissionTests(TestCase):
+    def setUp(self):
+        self.user = User.objects.create_user(username="user", password="testpass")
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.superuser = User.objects.create_superuser(
+            username="admin", password="testpass"
+        )
+        self.profile = get_or_create_account_profile(self.user)
+
+    def test_staff_admin_permissions_use_django_flags(self):
+        self.assertFalse(can_manage_accounts(self.user))
+        self.assertFalse(can_change_account_role(self.user))
+        self.assertTrue(can_manage_accounts(self.staff))
+        self.assertTrue(can_change_account_role(self.staff))
+
+    def test_account_operations_permissions_use_django_staff_flags(self):
+        self.profile.role = AccountRole.STAFF
+        self.profile.save(update_fields=["role", "updated_at"])
+
+        self.assertFalse(can_access_account_operations(self.user))
+        self.assertFalse(can_view_account_operations_dashboard(self.user))
+        self.assertFalse(can_view_account_list(self.user))
+        self.assertFalse(can_view_account_detail(self.user, self.staff))
+        self.assertTrue(can_access_account_operations(self.staff))
+        self.assertTrue(can_view_account_operations_dashboard(self.staff))
+        self.assertTrue(can_view_account_list(self.staff))
+        self.assertTrue(can_view_account_detail(self.staff, self.user))
+        self.assertTrue(can_access_account_operations(self.superuser))
+
+    def test_coach_role_does_not_grant_account_operations_access(self):
+        self.profile.role = AccountRole.COACH
+        self.profile.save(update_fields=["role", "updated_at"])
+
+        self.assertFalse(self.user.is_staff)
+        self.assertFalse(self.user.is_superuser)
+        self.assertFalse(can_access_account_operations(self.user))
+
+    def test_privileged_account_management_is_superuser_only(self):
+        self.assertFalse(can_manage_privileged_accounts(self.user))
+        self.assertFalse(can_manage_privileged_accounts(self.staff))
+        self.assertTrue(can_manage_privileged_accounts(self.superuser))
+
+    def test_regular_user_can_view_own_profile_but_not_manage_accounts(self):
+        other = User.objects.create_user(username="other", password="testpass")
+
+        self.assertTrue(can_view_account_profile(self.user, self.profile))
+        self.assertFalse(can_view_account_profile(other, self.profile))
+        self.assertTrue(can_view_account_profile(self.staff, self.profile))
+
+    def test_any_authenticated_user_can_submit_evaluations(self):
+        self.assertTrue(can_submit_evaluations(self.user))
+        self.assertFalse(can_submit_evaluations(None))
+
+
+class AccountAdminTests(TestCase):
+    def test_account_profile_registered_in_admin(self):
+        self.assertIn(AccountProfile, admin.site._registry)
+
+    def test_user_player_link_registered_in_admin(self):
+        self.assertIn(UserPlayerLink, admin.site._registry)
+        link_admin = admin.site._registry[UserPlayerLink]
+
+        self.assertEqual(link_admin.exclude, ("metadata",))
+        self.assertIn("user", link_admin.list_display)
+        self.assertIn("player", link_admin.list_display)
+        self.assertIn("relationship", link_admin.list_display)
+        self.assertIn("created_at", link_admin.readonly_fields)
+        self.assertIn("updated_at", link_admin.readonly_fields)
```
