# Prompt 87 - Analytics

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

`663ce89` - Split analytics tests by responsibility

## Old Test Structure

```text
analytics/tests.py
```

## New Test Structure

```text
analytics/tests/
    __init__.py
    helpers.py
    test_coach_assessments.py
    test_command_center.py
    test_draft_context.py
    test_evaluation_context.py
    test_evaluation_review.py
    test_evaluation_submission.py
    test_import_views.py
    test_my_evaluations.py
    test_observation_foundation.py
    test_player_experience.py
```

## Test Counts

Before split:

```text
DJANGO_SECRET_KEY=test python manage.py test analytics
Found 132 test(s).
Ran 132 tests successfully.
```

After split:

```text
DJANGO_SECRET_KEY=test python manage.py test analytics
Found 132 test(s).
Ran 132 tests successfully.
```

Full suite remained at 458 tests.

## Shared Helper Changes

The original shared imports, `User = get_user_model()`, and `attach_player_to_season()` helper moved to `analytics/tests/helpers.py`. Test files import only the helper names they use so Ruff `F` checks stay clean.

## Discovery Findings

Django discovers the analytics test package through `python manage.py test analytics`. Targeted module commands also work, including:

```text
DJANGO_SECRET_KEY=test python manage.py test analytics.tests.test_observation_foundation
DJANGO_SECRET_KEY=test python manage.py test analytics.tests.test_evaluation_submission
```

## Patch-Target Findings

No patch targets required changes. No production import paths were changed.

## Verification

Focused verification:

```text
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py test analytics.tests.test_observation_foundation
DJANGO_SECRET_KEY=test python manage.py test analytics.tests.test_evaluation_submission
DJANGO_SECRET_KEY=test python manage.py test analytics
DJANGO_SECRET_KEY=test python manage.py test accounts players seasons analytics
pre-commit run --files analytics/tests/__init__.py analytics/tests/helpers.py analytics/tests/test_import_views.py analytics/tests/test_observation_foundation.py analytics/tests/test_evaluation_context.py analytics/tests/test_draft_context.py analytics/tests/test_player_experience.py analytics/tests/test_command_center.py analytics/tests/test_coach_assessments.py analytics/tests/test_evaluation_submission.py analytics/tests/test_my_evaluations.py analytics/tests/test_evaluation_review.py docs/prompts/prompt_87_analytics.md
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

CONTINUE. Analytics is split; seasons and players remain medium-large test modules and should be reviewed in the next loop.

## Commit Diff

```diff
commit 663ce89ce39a50c0aba4e55c42028c9040601fa2
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 12:12:30 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 12:12:30 2026 -0700

    Split analytics tests by responsibility
---
 analytics/tests.py                             | 2753 ------------------------
 analytics/tests/__init__.py                    |    0
 analytics/tests/helpers.py                     |  242 +++
 analytics/tests/test_coach_assessments.py      |  416 ++++
 analytics/tests/test_command_center.py         |  355 +++
 analytics/tests/test_draft_context.py          |  209 ++
 analytics/tests/test_evaluation_context.py     |  161 ++
 analytics/tests/test_evaluation_review.py      |  365 ++++
 analytics/tests/test_evaluation_submission.py  |  465 ++++
 analytics/tests/test_import_views.py           |  334 +++
 analytics/tests/test_my_evaluations.py         |  572 +++++
 analytics/tests/test_observation_foundation.py |  686 ++++++
 analytics/tests/test_player_experience.py      |  463 ++++
 13 files changed, 4268 insertions(+), 2753 deletions(-)

diff --git a/analytics/tests.py b/analytics/tests.py
deleted file mode 100644
index adb75da..0000000
--- a/analytics/tests.py
+++ /dev/null
@@ -1,2753 +0,0 @@
-from datetime import timedelta
-from decimal import Decimal
-from unittest.mock import patch
-
-from django.contrib import admin
-from django.contrib.auth import get_user_model
-from django.core.exceptions import ValidationError
-from django.core.files.uploadedfile import SimpleUploadedFile
-from django.db import IntegrityError, transaction
-from django.test import TestCase
-from django.urls import reverse
-from django.utils import timezone
-
-from accounts.models import AccountRole, UserPlayerRelationship
-from accounts.services.link_service import activate_link, deactivate_link, link_user_to_player
-from accounts.services.profile_service import set_account_role
-from analytics.models import (
-    EVALUATION_PERSPECTIVE_COACH,
-    EVALUATION_PERSPECTIVE_GUEST,
-    EVALUATION_PERSPECTIVE_PEER,
-    EVALUATION_PERSPECTIVE_SELF,
-    EVALUATION_PERSPECTIVE_STAFF,
-    OBSERVATION_STATUS_DRAFT,
-    OBSERVATION_STATUS_REOPENED,
-    OBSERVATION_STATUS_SUBMITTED,
-    OBSERVATION_TYPE_COACH_ASSESSMENT,
-    RESPONSE_TYPE_RATING_1_5,
-    RESPONSE_TYPE_TEXT,
-    EvaluationCycle,
-    EvaluatorRole,
-    Observation,
-    ObservationQuestion,
-    ObservationQuestionSet,
-    ObservationResponse,
-    ObservationSource,
-    ObservationType,
-)
-from analytics.assessment_forms import CoachAssessmentForm
-from analytics.services.observation_service import (
-    create_coach_assessment_observation,
-    create_observation,
-    default_coach_assessment_question_set,
-    get_observation_detail,
-    save_observation_responses,
-    submit_observation,
-    validate_required_responses,
-)
-from analytics.services.comparison_service import (
-    get_player_comparison,
-    get_player_score_summary,
-)
-from analytics.services.metrics_service import (
-    completion_metrics,
-    draft_matching_metrics,
-    import_metrics,
-    observation_metrics,
-    recent_submitted_observations,
-)
-from analytics.services.player_service import (
-    DRAFT_STATUS_AVAILABLE,
-    DRAFT_STATUS_DRAFTED,
-    DRAFT_STATUS_NO_CONTEXT,
-    EVALUATION_HAS_ANY,
-    EVALUATION_HAS_SUBMITTED,
-    EVALUATION_NO_SUBMITTED,
-    EVALUATION_NOT_STARTED,
-    active_player_ids,
-    parse_player_search_filters,
-    search_players,
-)
-from analytics.services.permissions import (
-    can_evaluate_player,
-    can_submit_evaluation,
-    can_view_own_evaluation_draft,
-    evaluation_perspective_for_user,
-    evaluator_role_for_user,
-)
-from analytics.services.reporting_service import get_command_center_context
-from analytics.services.draft_service import get_draft_context_for_draft_player, get_draft_contexts_for_draft
-from analytics.services.evaluation_access_service import get_my_evaluation_detail, get_my_evaluations
-from analytics.services.question_service import (
-    COACH_ASSESSMENT_RUBRIC,
-    DEFAULT_COACH_ASSESSMENT_QUESTIONS,
-    DEFAULT_EVALUATOR_ROLES,
-    DEFAULT_OBSERVATION_SOURCES,
-    ROLE_ADMIN,
-    ROLE_COACH,
-    ROLE_GUEST_EVALUATOR,
-    ROLE_PLAYER,
-    ROLE_STAFF,
-    SOURCE_COACH,
-    ensure_default_coach_assessment_setup,
-    get_active_questions,
-    get_question_set_for_cycle,
-)
-from analytics.services.timeline_service import get_player_timeline
-from drafts.models import Draft, DraftAction, DraftActionType, DraftPlayer, DraftTeam
-from players.models import Player, PlayerImportBatch, PlayerImportStatus, PlayerSourceRow, PlayerTag
-from players.services.import_service import SOURCE_MEMBER_LIST
-from players.services.tag_service import assign_tag
-from seasons.services.season_service import create_season
-from seasons.services.team_service import get_or_create_season_team
-from seasons.services.membership_service import create_membership
-from seasons.services.coach_assignment_service import create_assignment
-
-
-User = get_user_model()
-
-
-def attach_player_to_season(player, season, *, team_name=None, division=None, is_primary=True):
-    season_team, _ = get_or_create_season_team(
-        season=season,
-        name=team_name or player.team_name or "Expos",
-        division=division or player.division or "13U",
-    )
-    return create_membership(player=player, season_team=season_team, is_primary=is_primary, is_active=True)
-
-
-class AnalyticsImportViewTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.user = User.objects.create_user(username="user", password="testpass")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-
-    def upload(self):
-        return SimpleUploadedFile(
-            "member list for 13u house.csv",
-            b"First,Last,Gender,Division,Team\nEugene,Lin,M,13U,Expos\n",
-            content_type="text/csv",
-        )
-
-    def test_import_views_require_staff(self):
-        response = self.client.get(reverse("analytics:import-list"))
-        self.assertEqual(response.status_code, 302)
-
-        self.client.force_login(self.user)
-        response = self.client.get(reverse("analytics:import-list"))
-        self.assertEqual(response.status_code, 403)
-
-    def test_staff_can_open_import_list(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:import-list"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Player Imports")
-
-    def test_upload_redirects_to_preview(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("analytics:import-new"),
-            {"season": str(self.season.pk), "source": SOURCE_MEMBER_LIST, "csv_file": self.upload()},
-        )
-
-        self.assertEqual(response.status_code, 302)
-        batch = PlayerImportBatch.objects.get()
-        self.assertEqual(response["Location"], reverse("analytics:import-preview", kwargs={"pk": batch.pk}))
-
-    def test_upload_can_enable_account_provisioning_options(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("analytics:import-new"),
-            {
-                "source": SOURCE_MEMBER_LIST,
-                "season": str(self.season.pk),
-                "csv_file": SimpleUploadedFile(
-                    "member.csv",
-                    b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n",
-                    content_type="text/csv",
-                ),
-                "provision_player_accounts": "on",
-            },
-        )
-
-        batch = PlayerImportBatch.objects.get()
-        self.assertEqual(response.status_code, 302)
-        self.assertTrue(batch.mapping_config["_provision_player_accounts"])
-        self.assertTrue(batch.mapping_config["_activate_player_accounts"])
-
-    def test_preview_can_map_account_email_and_preserves_provisioning_options(self):
-        self.client.force_login(self.staff)
-        batch = PlayerImportBatch.objects.create(
-            source=SOURCE_MEMBER_LIST,
-            original_filename="member.csv",
-            uploaded_by=self.staff,
-            season=self.season,
-            mapping_config={"_provision_player_accounts": True, "_activate_player_accounts": False},
-            preview_snapshot={
-                "parsed_csv": {
-                    "file_name": "member.csv",
-                    "headers": ["First", "Last", "DOB", "Email", "Division", "Team"],
-                    "normalized_headers": {"first": "First", "last": "Last", "dob": "DOB", "email": "Email", "division": "Division", "team": "Team"},
-                    "rows": [
-                        {
-                            "row_number": 2,
-                            "original_row": {"First": "Eugene", "Last": "Lin", "DOB": "2012-05-01", "Email": "eugene@example.com", "Division": "13U", "Team": "Expos"},
-                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "DOB": "2012-05-01", "Email": "eugene@example.com", "Division": "13U", "Team": "Expos"},
-                        }
-                    ],
-                }
-            },
-        )
-
-        response = self.client.post(
-            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
-            {"first_name": "First", "last_name": "Last", "birthdate": "DOB", "account_email": "Email", "division": "Division", "team_name": "Team"},
-        )
-
-        batch.refresh_from_db()
-        self.assertEqual(response.status_code, 302)
-        self.assertTrue(batch.mapping_config["_provision_player_accounts"])
-        self.assertEqual(batch.mapping_config["account_email"], "Email")
-        self.assertTrue(batch.preview_snapshot["preview"]["account_provisioning"]["enabled"])
-        self.assertTrue(batch.preview_snapshot["preview"]["account_provisioning"]["activate_users"])
-
-    def test_preview_refresh_and_confirm_import(self):
-        self.client.force_login(self.staff)
-        batch = PlayerImportBatch.objects.create(
-            source=SOURCE_MEMBER_LIST,
-            original_filename="member.csv",
-            uploaded_by=self.staff,
-            season=self.season,
-            preview_snapshot={
-                "parsed_csv": {
-                    "file_name": "member.csv",
-                    "headers": ["First", "Last", "Division", "Team"],
-                    "normalized_headers": {"first": "First", "last": "Last", "division": "Division", "team": "Team"},
-                    "rows": [
-                        {
-                            "row_number": 2,
-                            "original_row": {"First": "Eugene", "Last": "Lin", "Division": "13U", "Team": "Expos"},
-                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "Division": "13U", "Team": "Expos"},
-                        }
-                    ],
-                }
-            },
-        )
-
-        preview_response = self.client.post(
-            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
-            {"first_name": "First", "last_name": "Last", "division": "Division", "team_name": "Team"},
-        )
-        self.assertEqual(preview_response.status_code, 302)
-
-        confirm_response = self.client.post(reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True)
-
-        self.assertEqual(confirm_response.status_code, 200)
-        self.assertTrue(Player.objects.filter(first_name="Eugene", last_name="Lin").exists())
-        self.assertContains(confirm_response, "Import Result")
-
-    def test_import_detail_shows_safe_account_provisioning_summary(self):
-        self.client.force_login(self.staff)
-        response = self.client.post(
-            reverse("analytics:import-new"),
-            {
-                "source": SOURCE_MEMBER_LIST,
-                "season": str(self.season.pk),
-                "csv_file": SimpleUploadedFile(
-                    "member.csv",
-                    b"First,Last,DOB,Division,Team\nEugene,Lin,2012-05-01,13U,Expos\n",
-                    content_type="text/csv",
-                ),
-                "provision_player_accounts": "on",
-            },
-        )
-        batch = PlayerImportBatch.objects.get()
-
-        response = self.client.post(reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True)
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Account provisioning")
-        self.assertContains(response, "Users Created")
-        self.assertNotContains(response, "20120501")
-
-    def test_conflict_page_displays_review_rows(self):
-        self.client.force_login(self.staff)
-        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
-        upload_response = self.client.post(
-            reverse("analytics:import-new"),
-            {
-                "source": SOURCE_MEMBER_LIST,
-                "season": str(self.season.pk),
-                "csv_file": SimpleUploadedFile(
-                    "member.csv",
-                    b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n",
-                    content_type="text/csv",
-                ),
-            },
-        )
-        batch = PlayerImportBatch.objects.get()
-
-        response = self.client.get(reverse("analytics:import-conflicts", kwargs={"pk": batch.pk}))
-
-        self.assertEqual(upload_response.status_code, 302)
-        self.assertContains(response, "Row 2")
-        self.assertContains(response, "preferred_name")
-
-    def test_preview_routes_review_rows_through_conflict_review(self):
-        self.client.force_login(self.staff)
-        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
-        self.client.post(
-            reverse("analytics:import-new"),
-            {
-                "source": SOURCE_MEMBER_LIST,
-                "season": str(self.season.pk),
-                "csv_file": SimpleUploadedFile(
-                    "member.csv",
-                    b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n",
-                    content_type="text/csv",
-                ),
-            },
-        )
-        batch = PlayerImportBatch.objects.get()
-
-        response = self.client.get(reverse("analytics:import-preview", kwargs={"pk": batch.pk}))
-
-        self.assertContains(response, "Review Rows")
-        self.assertNotContains(response, "Confirm Import")
-
-    def test_conflict_page_can_commit_ambiguous_row_to_selected_candidate(self):
-        self.client.force_login(self.staff)
-        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
-        selected = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
-        self.client.post(
-            reverse("analytics:import-new"),
-            {
-                "source": SOURCE_MEMBER_LIST,
-                "season": str(self.season.pk),
-                "csv_file": SimpleUploadedFile(
-                    "member.csv",
-                    b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n",
-                    content_type="text/csv",
-                ),
-            },
-        )
-        batch = PlayerImportBatch.objects.get()
-
-        response = self.client.post(
-            reverse("analytics:import-confirm", kwargs={"pk": batch.pk}),
-            {"row_2_action": "use_candidate", "row_2_candidate": str(selected.id)},
-            follow=True,
-        )
-
-        selected.refresh_from_db()
-        self.assertEqual(response.status_code, 200)
-        self.assertEqual(selected.team_name, "Expos")
-        self.assertEqual(PlayerSourceRow.objects.get().player, selected)
-
-
-class AnalyticsObservationFoundationTests(TestCase):
-    def setUp(self):
-        self.evaluator = User.objects.create_user(username="coach", password="testpass")
-        self.other_evaluator = User.objects.create_user(username="othercoach", password="testpass")
-        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U", team_name="Expos")
-        self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="13U", team_name="Expos")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        self.player_membership = attach_player_to_season(self.player, self.season)
-        attach_player_to_season(self.other_player, self.season)
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.role = EvaluatorRole.objects.get(key=ROLE_COACH)
-        self.source = ObservationSource.objects.get(key=SOURCE_COACH)
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-
-    def required_response_payload(self):
-        return {
-            question: 4
-            for question in self.setup_result.question_set.questions.filter(
-                response_type=RESPONSE_TYPE_RATING_1_5,
-                is_required=True,
-                is_active=True,
-            )
-        }
-
-    def test_default_setup_creates_coach_assessment_configuration(self):
-        self.assertTrue(ObservationType.objects.filter(key=OBSERVATION_TYPE_COACH_ASSESSMENT).exists())
-        self.assertEqual(ObservationSource.objects.count(), len(DEFAULT_OBSERVATION_SOURCES))
-        self.assertEqual(EvaluatorRole.objects.count(), len(DEFAULT_EVALUATOR_ROLES))
-        self.assertEqual(self.setup_result.question_set.rubric, COACH_ASSESSMENT_RUBRIC)
-        self.assertEqual(self.setup_result.question_set.questions.count(), len(DEFAULT_COACH_ASSESSMENT_QUESTIONS))
-        self.assertEqual(
-            self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_TEXT).count(),
-            1,
-        )
-        self.assertEqual(
-            self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).count(),
-            len(DEFAULT_COACH_ASSESSMENT_QUESTIONS) - 1,
-        )
-
-    def test_default_setup_is_idempotent(self):
-        first_question_count = ObservationQuestion.objects.count()
-
-        second_result = ensure_default_coach_assessment_setup()
-
-        self.assertEqual(ObservationQuestion.objects.count(), first_question_count)
-        self.assertEqual(second_result.questions_created, 0)
-
-    def test_default_setup_does_not_overwrite_existing_questions(self):
-        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-        question.prompt = "Edited prompt"
-        question.display_order = 99
-        question.is_required = False
-        question.save()
-
-        ensure_default_coach_assessment_setup()
-
-        question.refresh_from_db()
-        self.assertEqual(question.prompt, "Edited prompt")
-        self.assertEqual(question.display_order, 99)
-        self.assertFalse(question.is_required)
-
-    def test_cycle_slug_generation_creates_unique_slugs(self):
-        second_cycle = EvaluationCycle.objects.create(name=self.cycle.name, cycle_type="Coach Assessment")
-
-        self.assertEqual(self.cycle.slug, "2026-13u-coach-assessment")
-        self.assertEqual(second_cycle.slug, "2026-13u-coach-assessment-2")
-
-    def test_question_set_version_is_unique_per_observation_type(self):
-        with self.assertRaises(IntegrityError):
-            with transaction.atomic():
-                ObservationQuestionSet.objects.create(
-                    observation_type=self.setup_result.observation_type,
-                    name="Duplicate",
-                    version=1,
-                )
-
-    def test_question_key_is_unique_per_question_set(self):
-        first_question = self.setup_result.question_set.questions.first()
-
-        with self.assertRaises(IntegrityError):
-            with transaction.atomic():
-                ObservationQuestion.objects.create(
-                    question_set=self.setup_result.question_set,
-                    key=first_question.key,
-                    prompt="Duplicate",
-                    response_type=RESPONSE_TYPE_RATING_1_5,
-                )
-
-    def test_get_active_questions_and_cycle_question_set(self):
-        questions = list(get_active_questions(self.setup_result.question_set))
-
-        self.assertEqual(questions[0].display_order, 1)
-        self.assertEqual(get_question_set_for_cycle(self.cycle), self.setup_result.question_set)
-        fallback_cycle = EvaluationCycle.objects.create(name="Fallback Cycle", cycle_type="Coach Assessment")
-        self.assertEqual(get_question_set_for_cycle(fallback_cycle), self.setup_result.question_set)
-
-    def test_cycle_rejects_non_coach_assessment_question_set(self):
-        other_type = ObservationType.objects.create(key="tryout", name="Tryout")
-        other_question_set = ObservationQuestionSet.objects.create(observation_type=other_type, name="Tryout", version=1)
-
-        with self.assertRaises(ValidationError):
-            EvaluationCycle.objects.create(
-                name="Invalid Cycle",
-                cycle_type="Coach Assessment",
-                coach_assessment_question_set=other_question_set,
-            )
-
-    def test_create_coach_assessment_references_players_player_and_snapshots_role(self):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-            evaluator_role=self.role,
-            source=self.source,
-        )
-
-        observation = result.observation
-        self.assertEqual(observation.player, self.player)
-        self.assertEqual(observation.evaluator_role_key, ROLE_COACH)
-        self.assertEqual(observation.evaluator_role_name, "Coach")
-        self.assertEqual(observation.observation_type_key, OBSERVATION_TYPE_COACH_ASSESSMENT)
-
-    def test_evaluation_submission_permissions_by_role(self):
-        anonymous = None
-        coach = User.objects.create_user(username="rolecoach", password="testpass")
-        player_user = User.objects.create_user(username="roleplayer", password="testpass")
-        staff_user = User.objects.create_user(username="rolestaff", password="testpass", is_staff=True)
-        guest = User.objects.create_user(username="roleguest", password="testpass")
-        parent = User.objects.create_user(username="roleparent", password="testpass")
-        set_account_role(coach, AccountRole.COACH)
-        set_account_role(player_user, AccountRole.PLAYER)
-        set_account_role(staff_user, AccountRole.STAFF)
-        set_account_role(guest, AccountRole.GUEST_EVALUATOR)
-        set_account_role(parent, AccountRole.PARENT)
-
-        self.assertFalse(can_submit_evaluation(anonymous))
-        self.assertTrue(can_submit_evaluation(coach))
-        self.assertTrue(can_submit_evaluation(player_user))
-        self.assertTrue(can_submit_evaluation(staff_user))
-        self.assertTrue(can_submit_evaluation(guest))
-        self.assertFalse(can_submit_evaluation(parent))
-
-    def test_self_evaluation_is_allowed_with_active_self_link_only(self):
-        player_user = User.objects.create_user(username="selflinked", password="testpass")
-        set_account_role(player_user, AccountRole.PLAYER)
-        link = link_user_to_player(player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-
-        self.assertTrue(can_evaluate_player(player_user, self.player))
-        self.assertTrue(can_evaluate_player(player_user, self.other_player))
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=player_user,
-        )
-        self.assertEqual(result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF)
-
-        deactivate_link(link)
-        self.assertFalse(can_evaluate_player(player_user, self.player))
-        with self.assertRaises(ValidationError):
-            evaluation_perspective_for_user(player_user, self.player)
-
-    def test_evaluation_perspective_is_server_derived_by_role(self):
-        users = [
-            (AccountRole.COACH, EVALUATION_PERSPECTIVE_COACH),
-            (AccountRole.PLAYER, EVALUATION_PERSPECTIVE_PEER),
-            (AccountRole.STAFF, EVALUATION_PERSPECTIVE_STAFF),
-            (AccountRole.ADMIN, EVALUATION_PERSPECTIVE_STAFF),
-            (AccountRole.GUEST_EVALUATOR, EVALUATION_PERSPECTIVE_GUEST),
-        ]
-        for account_role, expected_perspective in users:
-            with self.subTest(account_role=account_role):
-                evaluator = User.objects.create_user(username=f"perspective-{account_role}", password="testpass")
-                set_account_role(evaluator, account_role)
-                self.assertEqual(evaluation_perspective_for_user(evaluator, self.other_player), expected_perspective)
-
-    def test_parent_role_cannot_create_observation(self):
-        parent = User.objects.create_user(username="parent", password="testpass")
-        set_account_role(parent, AccountRole.PARENT)
-
-        with self.assertRaises(ValidationError):
-            create_coach_assessment_observation(
-                player=self.player,
-                evaluation_cycle=self.cycle,
-                evaluator=parent,
-            )
-
-    def test_evaluator_role_for_user_maps_account_roles(self):
-        expectations = [
-            (AccountRole.COACH, ROLE_COACH),
-            (AccountRole.PLAYER, ROLE_PLAYER),
-            (AccountRole.STAFF, ROLE_STAFF),
-            (AccountRole.ADMIN, ROLE_ADMIN),
-            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
-        ]
-        for account_role, evaluator_role_key in expectations:
-            with self.subTest(account_role=account_role):
-                user = User.objects.create_user(username=f"{account_role}-user", password="testpass")
-                set_account_role(user, account_role)
-
-                evaluator_role = evaluator_role_for_user(user)
-
-                self.assertEqual(evaluator_role.key, evaluator_role_key)
-
-    def test_coach_assessment_snapshots_actual_account_role_by_default(self):
-        role_expectations = [
-            (AccountRole.COACH, ROLE_COACH),
-            (AccountRole.PLAYER, ROLE_PLAYER),
-            (AccountRole.STAFF, ROLE_STAFF),
-            (AccountRole.ADMIN, ROLE_ADMIN),
-            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
-        ]
-        for index, (account_role, evaluator_role_key) in enumerate(role_expectations, start=1):
-            with self.subTest(account_role=account_role):
-                evaluator = User.objects.create_user(username=f"snapshot-{account_role}", password="testpass")
-                set_account_role(evaluator, account_role)
-                player = Player.objects.create(first_name=f"Snapshot{index}", last_name="Target", division="13U")
-                attach_player_to_season(player, self.season)
-
-                result = create_coach_assessment_observation(
-                    player=player,
-                    evaluation_cycle=self.cycle,
-                    evaluator=evaluator,
-                )
-
-                self.assertEqual(result.observation.evaluator_role_key, evaluator_role_key)
-                self.assertEqual(result.observation.evaluator_role, EvaluatorRole.objects.get(key=evaluator_role_key))
-
-    def test_draft_view_helpers_are_limited_to_own_drafts(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        ).observation
-        self.assertTrue(can_view_own_evaluation_draft(self.evaluator, observation))
-        self.assertFalse(can_view_own_evaluation_draft(self.other_evaluator, observation))
-
-        observation.status = OBSERVATION_STATUS_SUBMITTED
-        observation.save(update_fields=["status", "updated_at"])
-        self.assertFalse(can_view_own_evaluation_draft(self.evaluator, observation))
-
-    def test_submitted_observation_sets_submitted_at(self):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-            responses=self.required_response_payload(),
-        )
-        submitted = submit_observation(result.observation)
-
-        self.assertIsNotNone(submitted.submitted_at)
-
-    def test_coach_assessment_requires_evaluator(self):
-        with self.assertRaises(ValidationError):
-            create_coach_assessment_observation(
-                player=self.player,
-                evaluation_cycle=self.cycle,
-                evaluator=None,
-            )
-
-    def test_create_observation_rejects_mismatched_question_set_type(self):
-        other_type = ObservationType.objects.create(key="tryout", name="Tryout")
-        other_question_set = ObservationQuestionSet.objects.create(observation_type=other_type, name="Tryout", version=1)
-
-        with self.assertRaises(ValidationError):
-            create_observation(
-                player=self.player,
-                evaluation_cycle=self.cycle,
-                observation_type=self.setup_result.observation_type,
-                question_set=other_question_set,
-                source=self.source,
-                evaluator=self.evaluator,
-                evaluator_role=self.role,
-            )
-
-    def test_save_numeric_text_and_payload_responses(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        ).observation
-        rating_question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
-
-        created, updated = save_observation_responses(
-            observation,
-            [
-                {"question": rating_question, "value": 4, "payload": {"source": "test"}},
-                {"question": text_question.key, "value": "Good teammate."},
-            ],
-        )
-
-        rating_response = ObservationResponse.objects.get(observation=observation, question=rating_question)
-        text_response = ObservationResponse.objects.get(observation=observation, question=text_question)
-        self.assertEqual(created, 2)
-        self.assertEqual(updated, 0)
-        self.assertEqual(rating_response.numeric_value, Decimal("4.00"))
-        self.assertEqual(rating_response.payload, {"source": "test"})
-        self.assertEqual(text_response.text_value, "Good teammate.")
-
-    def test_save_response_updates_existing_response(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        ).observation
-        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-
-        save_observation_responses(observation, {question: 3})
-        created, updated = save_observation_responses(observation, {question: 5})
-
-        response = ObservationResponse.objects.get(observation=observation, question=question)
-        self.assertEqual(created, 0)
-        self.assertEqual(updated, 1)
-        self.assertEqual(response.numeric_value, Decimal("5.00"))
-
-    def test_invalid_rating_is_rejected(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        ).observation
-        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-
-        with self.assertRaises(ValidationError):
-            save_observation_responses(observation, {question: 6})
-
-    def test_decimal_and_non_finite_ratings_are_rejected(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        ).observation
-        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-
-        for value in ["3.5", "NaN", "Infinity"]:
-            with self.subTest(value=value):
-                with self.assertRaises(ValidationError):
-                    save_observation_responses(observation, {question: value})
-
-    def test_question_from_different_question_set_is_rejected(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        ).observation
-        other_question_set = ObservationQuestionSet.objects.create(
-            observation_type=self.setup_result.observation_type,
-            name="Other",
-            version=2,
-        )
-        other_question = ObservationQuestion.objects.create(
-            question_set=other_question_set,
-            key="other_question",
-            prompt="Other question",
-            response_type=RESPONSE_TYPE_RATING_1_5,
-        )
-
-        with self.assertRaises(ValidationError):
-            save_observation_responses(observation, {other_question: 3})
-
-    def test_duplicate_coach_assessment_is_prevented_for_same_evaluator_player_cycle(self):
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        )
-
-        with self.assertRaises(ValidationError):
-            create_coach_assessment_observation(
-                player=self.player,
-                evaluation_cycle=self.cycle,
-                evaluator=self.evaluator,
-            )
-
-    def test_duplicate_self_evaluation_is_prevented_for_player_cycle(self):
-        first_player_user = User.objects.create_user(username="self-one", password="testpass")
-        second_player_user = User.objects.create_user(username="self-two", password="testpass")
-        set_account_role(first_player_user, AccountRole.PLAYER)
-        set_account_role(second_player_user, AccountRole.PLAYER)
-        link_user_to_player(first_player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-        link_user_to_player(second_player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=False)
-
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=first_player_user,
-        )
-
-        with self.assertRaises(ValidationError):
-            create_coach_assessment_observation(
-                player=self.player,
-                evaluation_cycle=self.cycle,
-                evaluator=second_player_user,
-            )
-
-    def test_self_and_peer_evaluations_from_same_player_are_distinct(self):
-        player_user = User.objects.create_user(username="self-peer", password="testpass")
-        set_account_role(player_user, AccountRole.PLAYER)
-        link_user_to_player(player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-
-        self_result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=player_user,
-        )
-        peer_result = create_coach_assessment_observation(
-            player=self.other_player,
-            evaluation_cycle=self.cycle,
-            evaluator=player_user,
-        )
-
-        self.assertEqual(self_result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF)
-        self.assertEqual(peer_result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER)
-
-    def test_multiple_evaluators_can_assess_same_player_cycle(self):
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        )
-        second = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.other_evaluator,
-        )
-
-        self.assertEqual(second.observation.player, self.player)
-        self.assertEqual(Observation.objects.filter(player=self.player, evaluation_cycle=self.cycle).count(), 2)
-
-    def test_same_evaluator_can_assess_different_players_and_cycles(self):
-        other_cycle = EvaluationCycle.objects.create(name="2026 15U Coach Assessment", cycle_type="Coach Assessment")
-
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        )
-        create_coach_assessment_observation(
-            player=self.other_player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        )
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=other_cycle,
-            evaluator=self.evaluator,
-        )
-
-        self.assertEqual(Observation.objects.filter(evaluator=self.evaluator).count(), 3)
-
-    def test_submit_observation_and_detail_loader(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        ).observation
-        save_observation_responses(observation, self.required_response_payload())
-
-        submitted = submit_observation(observation, actor=self.evaluator)
-        detail = get_observation_detail(submitted.id)
-
-        self.assertEqual(submitted.status, OBSERVATION_STATUS_SUBMITTED)
-        self.assertIsNotNone(submitted.submitted_at)
-        self.assertEqual(detail.player, self.player)
-
-    def test_submit_observation_requires_required_responses(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.evaluator,
-        ).observation
-
-        with self.assertRaises(ValidationError):
-            validate_required_responses(observation)
-        with self.assertRaises(ValidationError):
-            submit_observation(observation, actor=self.evaluator)
-
-    def test_default_question_set_wrapper(self):
-        self.assertEqual(default_coach_assessment_question_set(), self.setup_result.question_set)
-
-    def test_phase_three_models_registered_in_admin(self):
-        for model in [
-            EvaluationCycle,
-            ObservationType,
-            ObservationSource,
-            EvaluatorRole,
-            ObservationQuestionSet,
-            ObservationQuestion,
-            Observation,
-            ObservationResponse,
-        ]:
-            self.assertIn(model, admin.site._registry)
-
-
-class SeasonalEvaluationContextTests(TestCase):
-    def setUp(self):
-        self.coach = User.objects.create_user(username="season-coach", password="testpass")
-        set_account_role(self.coach, AccountRole.COACH)
-        self.player = Player.objects.create(first_name="Season", last_name="Player", division="13U", team_name="Reds")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        self.other_season = create_season(key="2027-spring", name="2027 Spring")
-        self.membership = attach_player_to_season(self.player, self.season, team_name="Reds", division="13U")
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 Spring Evaluations",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-
-    def rating_payload(self, value=4):
-        return {
-            question: value
-            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-        }
-
-    def test_submitted_observation_stores_immutable_season_and_roster_snapshots(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=self.rating_payload(),
-        ).observation
-
-        submitted = submit_observation(observation, actor=self.coach)
-        self.membership.season_team.name = "Corrected Reds"
-        self.membership.season_team.division = "14U"
-        self.membership.season_team.save()
-        self.player.team_name = "Live Team"
-        self.player.division = "Live Division"
-        self.player.save(update_fields=["team_name", "division", "updated_at"])
-        submitted.refresh_from_db()
-
-        self.assertEqual(submitted.season, self.season)
-        self.assertEqual(submitted.player_roster_membership, self.membership)
-        self.assertEqual(submitted.season_name_snapshot, "2026 Spring")
-        self.assertEqual(submitted.season_key_snapshot, "2026-spring")
-        self.assertEqual(submitted.player_team_name_snapshot, "Reds")
-        self.assertEqual(submitted.player_division_snapshot, "13U")
-
-    def test_coach_assignment_snapshot_is_stored_when_resolved(self):
-        assignment = create_assignment(user=self.coach, season_team=self.membership.season_team, assignment_role="head_coach", is_primary=True)
-
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=self.rating_payload(),
-        ).observation
-        submitted = submit_observation(observation, actor=self.coach)
-
-        self.assertEqual(submitted.evaluator_coach_assignment, assignment)
-        self.assertEqual(submitted.evaluator_team_name_snapshot, "Reds")
-        self.assertEqual(submitted.evaluator_division_snapshot, "13U")
-        self.assertEqual(submitted.evaluator_assignment_role_snapshot, "Head Coach")
-
-    def test_cross_player_or_cross_season_membership_is_rejected(self):
-        other_player = Player.objects.create(first_name="Other", last_name="Player", division="13U")
-        other_membership = attach_player_to_season(other_player, self.season)
-        cross_season_membership = attach_player_to_season(self.player, self.other_season)
-
-        with self.assertRaisesMessage(ValidationError, "does not belong to this player"):
-            create_coach_assessment_observation(
-                player=self.player,
-                evaluation_cycle=self.cycle,
-                evaluator=self.coach,
-                player_roster_membership=other_membership,
-            )
-        with self.assertRaisesMessage(ValidationError, "does not belong to this evaluation season"):
-            create_coach_assessment_observation(
-                player=self.player,
-                evaluation_cycle=self.cycle,
-                evaluator=self.coach,
-                player_roster_membership=cross_season_membership,
-            )
-
-    def test_ambiguous_multiple_memberships_without_primary_are_blocked(self):
-        player = Player.objects.create(first_name="Multi", last_name="Member", division="13U")
-        attach_player_to_season(player, self.season, team_name="Reds", division="13U", is_primary=False)
-        attach_player_to_season(player, self.season, team_name="Blues", division="13U", is_primary=False)
-
-        with self.assertRaisesMessage(ValidationError, "multiple active memberships"):
-            create_coach_assessment_observation(player=player, evaluation_cycle=self.cycle, evaluator=self.coach)
-
-    def test_review_uses_snapshot_values_not_live_player_fields(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=self.rating_payload(),
-        ).observation
-        submitted = submit_observation(observation, actor=self.coach)
-        self.player.team_name = "Changed Live Team"
-        self.player.division = "Changed Live Division"
-        self.player.save(update_fields=["team_name", "division", "updated_at"])
-        set_account_role(self.coach, AccountRole.COACH)
-
-        from analytics.services.evaluation_review_service import get_evaluation_review_detail
-
-        detail = get_evaluation_review_detail(self.coach, submitted.id)
-
-        self.assertEqual(detail.season_name, "2026 Spring")
-        self.assertEqual(detail.player_team, "Reds")
-        self.assertEqual(detail.player_division, "13U")
-
-
-class AnalyticsDraftContextServiceTests(TestCase):
-    def setUp(self):
-        self.coach = User.objects.create_user(username="coach", password="testpass")
-        self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
-        self.third_coach = User.objects.create_user(username="thirdcoach", password="testpass")
-        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U", team_name="Expos")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        attach_player_to_season(self.player, self.season)
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-        self.draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
-        self.team = DraftTeam.objects.create(draft=self.draft, name="Expos Navy", display_order=1)
-        DraftTeam.objects.create(draft=self.draft, name="Expos Gold", display_order=2)
-        self.draft_player = DraftPlayer.objects.create(
-            draft=self.draft,
-            first_name="Eugene",
-            last_name="Lin",
-            full_name="Eugene Lin",
-            extra_data={"Birth Year": "2012"},
-        )
-
-    def submitted_observation(self, evaluator, rating=4):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=evaluator,
-            responses={
-                question: rating
-                for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-            },
-        )
-        return submit_observation(result.observation, actor=evaluator)
-
-    def test_draft_context_retrieves_submitted_observation_and_selection(self):
-        expected_round_question = ObservationQuestion.objects.create(
-            question_set=self.setup_result.question_set,
-            key="expected_draft_round",
-            prompt="Expected draft round",
-            response_type=RESPONSE_TYPE_TEXT,
-            metadata={"draft_context_field": "expected_draft_round"},
-            display_order=100,
-        )
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses={
-                **{
-                    question: 4
-                    for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-                },
-                expected_round_question: "2",
-            },
-        ).observation
-        submit_observation(observation, actor=self.coach)
-        DraftAction.objects.create(
-            draft=self.draft,
-            action_type=DraftActionType.PLAYER_DRAFTED,
-            player=self.draft_player,
-            to_team=self.team,
-            pick_number=3,
-        )
-
-        context = get_draft_context_for_draft_player(self.draft_player)
-
-        self.assertTrue(context.is_matched)
-        self.assertEqual(context.matched_player, self.player)
-        self.assertEqual(context.pick_number, 3)
-        self.assertEqual(context.selected_round, 2)
-        self.assertEqual(context.selected_team, self.team)
-        self.assertEqual(context.submitted_observation_count, 1)
-        self.assertEqual(context.latest_observation.expected_draft_round, "2")
-        self.assertEqual(context.average_rating, Decimal("4"))
-
-    def test_draft_context_is_empty_when_no_submitted_observations_exist(self):
-        context = get_draft_context_for_draft_player(self.draft_player)
-
-        self.assertTrue(context.is_matched)
-        self.assertEqual(context.submitted_observation_count, 0)
-        self.assertIsNone(context.average_rating)
-
-    def test_draft_context_excludes_draft_and_reopened_observations(self):
-        self.submitted_observation(self.coach, rating=5)
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.other_coach,
-            status=OBSERVATION_STATUS_DRAFT,
-            responses={
-                question: 1
-                for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-            },
-        )
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.third_coach,
-            status=OBSERVATION_STATUS_REOPENED,
-            responses={
-                question: 1
-                for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-            },
-        )
-
-        context = get_draft_context_for_draft_player(self.draft_player)
-
-        self.assertEqual(context.submitted_observation_count, 1)
-        self.assertEqual(context.latest_observation.evaluator_name, self.coach.username)
-
-    def test_multiple_submitted_observations_are_ordered_newest_first(self):
-        older = self.submitted_observation(self.coach, rating=3)
-        newer = self.submitted_observation(self.other_coach, rating=5)
-        Observation.objects.filter(pk=older.pk).update(submitted_at=timezone.now() - timedelta(days=2))
-        Observation.objects.filter(pk=newer.pk).update(submitted_at=timezone.now() - timedelta(hours=1))
-
-        context = get_draft_context_for_draft_player(self.draft_player)
-
-        self.assertEqual(context.submitted_observation_count, 2)
-        self.assertEqual([summary.evaluator_name for summary in context.observations], [self.other_coach.username, self.coach.username])
-        self.assertEqual(context.average_rating, Decimal("4"))
-
-    def test_draft_context_reports_unmatched_player(self):
-        unmatched = DraftPlayer.objects.create(
-            draft=self.draft,
-            first_name="No",
-            last_name="Match",
-            full_name="No Match",
-        )
-
-        context = get_draft_context_for_draft_player(unmatched)
-
-        self.assertFalse(context.is_matched)
-        self.assertEqual(context.submitted_observation_count, 0)
-
-    def test_ambiguous_player_match_does_not_select_observations(self):
-        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
-
-        context = get_draft_contexts_for_draft(self.draft)[self.draft_player.id]
-
-        self.assertFalse(context.is_matched)
-        self.assertEqual(context.match_status, "ambiguous")
-        self.assertEqual(context.submitted_observation_count, 0)
-
-
-class PlayerExperienceServiceTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.coach = User.objects.create_user(username="coach", password="testpass")
-        self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
-        self.player = Player.objects.create(
-            first_name="Eugene",
-            last_name="Lin",
-            birth_year=2012,
-            division="13U",
-            team_name="Expos",
-        )
-        self.other_player = Player.objects.create(
-            first_name="Alex",
-            last_name="Chen",
-            birth_year=2011,
-            division="15U",
-            team_name="Mounties",
-        )
-        self.no_context_player = Player.objects.create(first_name="No", last_name="Context", division="13U")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        attach_player_to_season(self.player, self.season)
-        attach_player_to_season(self.other_player, self.season)
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-        self.draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
-        self.team = DraftTeam.objects.create(draft=self.draft, name="Expos Navy", display_order=1)
-        DraftTeam.objects.create(draft=self.draft, name="Expos Gold", display_order=2)
-        self.draft_player = DraftPlayer.objects.create(
-            draft=self.draft,
-            first_name="Eugene",
-            last_name="Lin",
-            full_name="Eugene Lin",
-            extra_data={"Birth Year": "2012"},
-        )
-
-    def rating_payload(self, value=4):
-        return {
-            question: value
-            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-        }
-
-    def submit_assessment(self, evaluator=None, player=None, value=4):
-        result = create_coach_assessment_observation(
-            player=player or self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=evaluator or self.coach,
-            responses=self.rating_payload(value),
-        )
-        return submit_observation(result.observation, actor=evaluator or self.coach)
-
-    def test_timeline_includes_submitted_assessment_import_and_draft_context(self):
-        observation = self.submit_assessment()
-        PlayerSourceRow.objects.create(
-            player=self.player,
-            source="vcb_member_list_csv",
-            source_filename="members.csv",
-            row_number=2,
-            original_row={"private": "do not render"},
-        )
-        DraftAction.objects.create(
-            draft=self.draft,
-            action_type=DraftActionType.PLAYER_DRAFTED,
-            player=self.draft_player,
-            to_team=self.team,
-            pick_number=1,
-        )
-
-        timeline = get_player_timeline(self.player)
-
-        self.assertEqual(timeline.coach_assessment_count, 1)
-        self.assertEqual(timeline.import_count, 1)
-        self.assertEqual(timeline.draft_context_count, 1)
-        self.assertEqual({item.kind for item in timeline.items}, {"coach_assessment", "import", "draft_context"})
-        self.assertTrue(any(str(observation.id) in item.url for item in timeline.items if item.url))
-
-    def test_timeline_excludes_draft_and_reopened_observations(self):
-        submitted = self.submit_assessment(evaluator=self.coach, value=5)
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.other_coach,
-            status=OBSERVATION_STATUS_DRAFT,
-            responses=self.rating_payload(1),
-        )
-        third_coach = User.objects.create_user(username="thirdcoach", password="testpass")
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=third_coach,
-            status=OBSERVATION_STATUS_REOPENED,
-            responses=self.rating_payload(1),
-        )
-
-        timeline = get_player_timeline(self.player)
-
-        self.assertEqual(timeline.coach_assessment_count, 1)
-        self.assertEqual(timeline.items[0].metadata.get("evaluator"), submitted.evaluator.username)
-
-    def test_timeline_handles_no_entries(self):
-        timeline = get_player_timeline(self.other_player)
-
-        self.assertEqual(timeline.items, [])
-        self.assertEqual(timeline.coach_assessment_count, 0)
-
-    def test_comparison_computes_scores_notes_tags_and_draft_context(self):
-        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses={**self.rating_payload(4), text_question: "Strong arm."},
-        ).observation
-        submit_observation(observation, actor=self.coach)
-        assign_tag(self.player, "Strong Prospect")
-        DraftAction.objects.create(
-            draft=self.draft,
-            action_type=DraftActionType.PLAYER_DRAFTED,
-            player=self.draft_player,
-            to_team=self.team,
-            pick_number=1,
-        )
-
-        summary = get_player_score_summary(self.player)
-        comparison = get_player_comparison([self.other_player, self.player])
-
-        self.assertEqual(summary.average_rating, Decimal("4"))
-        self.assertEqual(summary.evaluator_count, 1)
-        self.assertIn("Strong arm.", summary.notes)
-        self.assertEqual([tag.name for tag in summary.tags], ["Strong Prospect"])
-        self.assertEqual(len(summary.draft_contexts), 1)
-        self.assertEqual([player.id for player in comparison.players], [self.other_player.id, self.player.id])
-        self.assertIn("Throw", comparison.category_names)
-
-    def test_search_filters_by_name_team_division_birth_year_tag_source_and_evaluation(self):
-        assign_tag(self.player, "Future AAA")
-        PlayerSourceRow.objects.create(player=self.player, source="vcb_member_list_csv", source_filename="members.csv")
-        self.submit_assessment()
-
-        expectations = [
-            ({"q": "Eug"}, [self.player]),
-            ({"team": "Expos"}, [self.player]),
-            ({"division": "13U"}, [self.no_context_player, self.player]),
-            ({"birth_year": "2012"}, [self.player]),
-            ({"tag": "future-aaa"}, [self.player]),
-            ({"source": "vcb_member_list_csv"}, [self.player]),
-            ({"evaluation": EVALUATION_HAS_SUBMITTED}, [self.player]),
-            ({"evaluation": EVALUATION_NO_SUBMITTED}, [self.other_player, self.no_context_player]),
-            ({"evaluation": EVALUATION_HAS_ANY}, [self.player]),
-            ({"evaluation": EVALUATION_NOT_STARTED}, [self.other_player, self.no_context_player]),
-        ]
-        for params, expected_players in expectations:
-            with self.subTest(params=params):
-                result = search_players(parse_player_search_filters(params))
-                self.assertEqual([player.id for player in result.players], [player.id for player in expected_players])
-
-    def test_search_filters_by_draft_status_and_ignores_invalid_birth_year(self):
-        available_player = Player.objects.create(first_name="Ava", last_name="Lopez", birth_year=2012, division="13U")
-        DraftPlayer.objects.create(
-            draft=self.draft,
-            first_name="Ava",
-            last_name="Lopez",
-            full_name="Ava Lopez",
-            extra_data={"Birth Year": "2012"},
-        )
-        DraftAction.objects.create(
-            draft=self.draft,
-            action_type=DraftActionType.PLAYER_DRAFTED,
-            player=self.draft_player,
-            to_team=self.team,
-            pick_number=1,
-        )
-
-        drafted = search_players(parse_player_search_filters({"draft_status": DRAFT_STATUS_DRAFTED}))
-        available = search_players(parse_player_search_filters({"draft_status": DRAFT_STATUS_AVAILABLE}))
-        no_context = search_players(parse_player_search_filters({"draft_status": DRAFT_STATUS_NO_CONTEXT}))
-        invalid = search_players(parse_player_search_filters({"birth_year": "not-a-year"}))
-
-        self.assertIn(self.player, drafted.players)
-        self.assertIn(available_player, available.players)
-        self.assertIn(self.no_context_player, no_context.players)
-        self.assertIn(self.player, invalid.players)
-
-
-class PlayerExperienceViewTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.coach = User.objects.create_user(username="coach", password="testpass")
-        self.player = Player.objects.create(
-            first_name="Eugene",
-            last_name="Lin",
-            birth_year=2012,
-            division="13U",
-            team_name="Expos",
-            bats="R",
-            throws="R",
-            primary_positions="SS",
-        )
-        self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="15U", team_name="Mounties")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        attach_player_to_season(self.player, self.season)
-        attach_player_to_season(self.other_player, self.season, team_name="Mounties", division="15U")
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-
-    def rating_payload(self, value=4):
-        return {
-            question: value
-            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-        }
-
-    def test_player_experience_views_require_staff(self):
-        profile_url = reverse("analytics:player-profile", kwargs={"player_id": self.player.id})
-        for url in [reverse("analytics:player-search"), profile_url, reverse("analytics:player-compare")]:
-            with self.subTest(url=url):
-                self.client.logout()
-                self.assertEqual(self.client.get(url).status_code, 302)
-                self.client.force_login(self.coach)
-                self.assertEqual(self.client.get(url).status_code, 403)
-
-    def test_player_search_view_renders_filters_and_results(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:player-search"), {"q": "Eugene"})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Player Search")
-        self.assertContains(response, self.player.display_name)
-        self.assertNotContains(response, self.other_player.display_name)
-
-    def test_player_profile_renders_phase_six_context_without_raw_import_json(self):
-        assign_tag(self.player, "Strong Prospect")
-        PlayerSourceRow.objects.create(
-            player=self.player,
-            source="vcb_member_list_csv",
-            source_filename="members.csv",
-            row_number=2,
-            original_row={"private": "secret value"},
-        )
-        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses={**self.rating_payload(4), text_question: "Good teammate."},
-        ).observation
-        submit_observation(observation, actor=self.coach)
-        draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
-        team = DraftTeam.objects.create(draft=draft, name="Expos Navy", display_order=1)
-        DraftTeam.objects.create(draft=draft, name="Expos Gold", display_order=2)
-        draft_player = DraftPlayer.objects.create(
-            draft=draft,
-            first_name="Eugene",
-            last_name="Lin",
-            full_name="Eugene Lin",
-            extra_data={"Birth Year": "2012"},
-        )
-        DraftAction.objects.create(
-            draft=draft,
-            action_type=DraftActionType.PLAYER_DRAFTED,
-            player=draft_player,
-            to_team=team,
-            pick_number=1,
-        )
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:player-profile", kwargs={"player_id": self.player.id}))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Strong Prospect")
-        self.assertContains(response, "vcb_member_list_csv")
-        self.assertContains(response, "Good teammate.")
-        self.assertContains(response, "Draft Context")
-        self.assertContains(response, "Timeline")
-        self.assertNotContains(response, "secret value")
-
-    def test_player_profile_empty_states(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:player-profile", kwargs={"player_id": self.other_player.id}))
-
-        self.assertContains(response, "No tags assigned.")
-        self.assertContains(response, "No imported source rows.")
-        self.assertContains(response, "No draft context found.")
-        self.assertContains(response, "No submitted coach assessments yet.")
-        self.assertContains(response, "No timeline entries yet.")
-
-    def test_player_compare_handles_empty_selected_and_selected_players(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=self.rating_payload(4),
-        ).observation
-        submit_observation(observation, actor=self.coach)
-        self.client.force_login(self.staff)
-
-        empty_response = self.client.get(reverse("analytics:player-compare"))
-        selected_response = self.client.get(reverse("analytics:player-compare"), {"players": [str(self.player.id), str(self.other_player.id)]})
-
-        self.assertContains(empty_response, "Select players to compare.")
-        self.assertContains(selected_response, self.player.display_name)
-        self.assertContains(selected_response, "4.0")
-        self.assertContains(selected_response, "No submitted assessments")
-
-    def test_player_compare_caps_selected_players(self):
-        extra_players = [
-            Player.objects.create(first_name=f"Player{i}", last_name="Test", division="13U")
-            for i in range(10)
-        ]
-        ids = [str(player.id) for player in extra_players]
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:player-compare"), {"players": ids})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertEqual(len(response.context["selected_players"]), 6)
-
-    def test_phase_six_regression_existing_pages_render(self):
-        self.client.force_login(self.staff)
-
-        self.assertEqual(self.client.get(reverse("analytics:assessment-list")).status_code, 200)
-        self.assertEqual(self.client.get(reverse("analytics:observation-review-list")).status_code, 200)
-        self.assertEqual(self.client.get(reverse("analytics:import-list")).status_code, 200)
-
-
-class AnalyticsCommandCenterServiceTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.coach = User.objects.create_user(username="coach", password="testpass")
-        self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
-        self.player = Player.objects.create(
-            first_name="Eugene",
-            last_name="Lin",
-            birth_year=2012,
-            division="13U",
-            team_name="Expos",
-        )
-        self.other_player = Player.objects.create(
-            first_name="Alex",
-            last_name="Chen",
-            birth_year=2011,
-            division="15U",
-            team_name="Mounties",
-        )
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        attach_player_to_season(self.player, self.season)
-        attach_player_to_season(self.other_player, self.season, team_name="Mounties", division="15U")
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-
-    def rating_payload(self, value=4):
-        return {
-            question: value
-            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-        }
-
-    def submit_assessment(self, evaluator=None, player=None, value=4):
-        result = create_coach_assessment_observation(
-            player=player or self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=evaluator or self.coach,
-            responses=self.rating_payload(value),
-        )
-        return submit_observation(result.observation, actor=evaluator or self.coach)
-
-    def test_player_population_helpers_live_in_player_service(self):
-        self.assertIn(self.player.id, active_player_ids(division="13U"))
-        self.assertNotIn(self.other_player.id, active_player_ids(division="13U"))
-
-        result = search_players(parse_player_search_filters({"q": "Eugene"}))
-
-        self.assertEqual(result.players, [self.player])
-
-    def test_completion_and_observation_metrics_respect_cycle_and_filters(self):
-        self.submit_assessment(value=5)
-        create_coach_assessment_observation(
-            player=self.other_player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.other_coach,
-            status=OBSERVATION_STATUS_DRAFT,
-            responses=self.rating_payload(2),
-        )
-
-        completion = completion_metrics(cycle=self.cycle, division="13U")
-        observations = observation_metrics(cycle=self.cycle, division="13U")
-
-        self.assertEqual(completion.total_active_players, 1)
-        self.assertEqual(completion.players_with_submitted_assessment, 1)
-        self.assertEqual(completion.players_without_submitted_assessment, 0)
-        self.assertEqual(completion.completion_rate, Decimal("100"))
-        self.assertEqual(observations.submitted_count, 1)
-        self.assertEqual(observations.draft_count, 0)
-        self.assertEqual(observations.by_category_average[0].average, Decimal("5"))
-
-    def test_metrics_exclude_draft_and_reopened_from_submitted_rating_summaries(self):
-        self.submit_assessment(evaluator=self.coach, value=5)
-        create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.other_coach,
-            status=OBSERVATION_STATUS_REOPENED,
-            responses=self.rating_payload(1),
-        )
-
-        observations = observation_metrics(cycle=self.cycle)
-
-        averages = {row.label: row.average for row in observations.by_category_average}
-        self.assertTrue(averages)
-        self.assertEqual(set(averages.values()), {Decimal("5")})
-
-    def test_coach_to_coach_spread_requires_two_evaluators(self):
-        self.submit_assessment(evaluator=self.coach, value=2)
-        self.submit_assessment(evaluator=self.other_coach, value=5)
-
-        observations = observation_metrics(cycle=self.cycle)
-
-        self.assertTrue(observations.variance_rows)
-        self.assertEqual(observations.variance_rows[0].player, self.player)
-        self.assertEqual(observations.variance_rows[0].spread, Decimal("3"))
-
-    def test_import_summary_counts_statuses_and_rows(self):
-        PlayerImportBatch.objects.create(
-            source="member_list",
-            original_filename="members.csv",
-            status=PlayerImportStatus.NEEDS_REVIEW,
-            rows_created=1,
-            rows_updated=2,
-            rows_skipped=3,
-            rows_conflicted=4,
-        )
-        PlayerImportBatch.objects.create(
-            source="member_list",
-            original_filename="committed.csv",
-            status=PlayerImportStatus.COMMITTED,
-        )
-
-        summary = import_metrics()
-
-        self.assertEqual(summary.total_batches, 2)
-        self.assertEqual(summary.needs_review_count, 1)
-        self.assertEqual(summary.committed_count, 1)
-        self.assertEqual(summary.rows_created, 1)
-        self.assertEqual(summary.rows_conflicted, 4)
-        self.assertEqual(len(summary.recent_batches), 2)
-
-    def test_draft_matching_summary_uses_draft_context_and_detects_mismatch(self):
-        expected_round_question = ObservationQuestion.objects.create(
-            question_set=self.setup_result.question_set,
-            key="expected_draft_round",
-            prompt="Expected draft round",
-            response_type=RESPONSE_TYPE_TEXT,
-            metadata={"draft_context_field": "expected_draft_round"},
-            display_order=100,
-        )
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses={**self.rating_payload(4), expected_round_question: "1"},
-        ).observation
-        submit_observation(observation, actor=self.coach)
-        draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
-        team = DraftTeam.objects.create(draft=draft, name="Expos Navy", display_order=1)
-        DraftTeam.objects.create(draft=draft, name="Expos Gold", display_order=2)
-        draft_player = DraftPlayer.objects.create(
-            draft=draft,
-            first_name="Eugene",
-            last_name="Lin",
-            full_name="Eugene Lin",
-            extra_data={"Birth Year": "2012"},
-        )
-        DraftPlayer.objects.create(draft=draft, first_name="No", last_name="Match", full_name="No Match")
-        DraftAction.objects.create(
-            draft=draft,
-            action_type=DraftActionType.PLAYER_DRAFTED,
-            player=draft_player,
-            to_team=team,
-            pick_number=3,
-        )
-
-        summary = draft_matching_metrics(division="13U")
-
-        self.assertEqual(summary.matched_player_count, 1)
-        self.assertEqual(summary.drafted_player_count, 1)
-        self.assertEqual(summary.no_context_player_count, 0)
-        self.assertEqual(summary.unmatched_draft_player_count, 1)
-        self.assertEqual(summary.expected_round_mismatch_count, 1)
-        self.assertEqual(summary.mismatches[0].player, self.player)
-
-    def test_recent_observations_are_ordered_and_limited(self):
-        older = self.submit_assessment(evaluator=self.coach, value=3)
-        newer = self.submit_assessment(evaluator=self.other_coach, value=4)
-        Observation.objects.filter(pk=older.pk).update(submitted_at=timezone.now() - timedelta(days=1))
-        Observation.objects.filter(pk=newer.pk).update(submitted_at=timezone.now())
-
-        observations = recent_submitted_observations(cycle=self.cycle, limit=1)
-
-        self.assertEqual(observations, [Observation.objects.get(pk=newer.pk)])
-
-    def test_reporting_context_is_grouped_and_template_ready(self):
-        self.submit_assessment()
-
-        context = get_command_center_context(cycle_id=self.cycle.id, division="13U")
-
-        self.assertTrue(context.summary_cards)
-        self.assertEqual(context.completion_summary.active_cycle, self.cycle)
-        self.assertTrue(context.observation_summary.by_category_average)
-        self.assertIsNotNone(context.import_summary)
-        self.assertIsNotNone(context.draft_summary)
-        self.assertTrue(context.recent_observations)
-        self.assertTrue(context.navigation_links)
-        self.assertFalse(hasattr(context, "total_active_players"))
-
-
-class AnalyticsCommandCenterViewTests(TestCase):
-    def setUp(self):
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.coach = User.objects.create_user(username="coach", password="testpass")
-        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U", team_name="Expos")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        attach_player_to_season(self.player, self.season)
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-
-    def rating_payload(self, value=4):
-        return {
-            question: value
-            for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)
-        }
-
-    def test_command_center_requires_staff(self):
-        url = reverse("analytics:command-center")
-        self.assertEqual(self.client.get(url).status_code, 302)
-
-        self.client.force_login(self.coach)
-        self.assertEqual(self.client.get(url).status_code, 403)
-
-    def test_staff_can_render_command_center_links_and_empty_states(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:command-center"), {"cycle": "not-a-number"})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Analytics Command Center")
-        self.assertContains(response, reverse("analytics:import-list"))
-        self.assertContains(response, reverse("analytics:player-search"))
-        self.assertContains(response, reverse("analytics:player-compare"))
-        self.assertContains(response, reverse("analytics:assessment-list"))
-        self.assertContains(response, reverse("analytics:observation-review-list"))
-        self.assertContains(response, "No player imports yet.")
-        self.assertContains(response, "No submitted observations yet.")
-
-    def test_command_center_renders_populated_summaries_and_filters(self):
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=self.rating_payload(4),
-        ).observation
-        submit_observation(observation, actor=self.coach)
-        PlayerImportBatch.objects.create(source="member_list", original_filename="members.csv", status=PlayerImportStatus.COMMITTED)
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:command-center"), {"division": "13U", "team": "Expos"})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Submitted assessments")
-        self.assertContains(response, "Completion rate")
-        self.assertContains(response, "Average Score By Category")
-        self.assertContains(response, "members.csv")
-        self.assertContains(response, self.player.display_name)
-        self.assertEqual(response.context["filters"]["division"], "13U")
-        self.assertEqual(response.context["filters"]["team"], "Expos")
-
-    def test_phase_seven_regression_existing_pages_render(self):
-        self.client.force_login(self.staff)
-
-        self.assertEqual(self.client.get(reverse("analytics:player-search")).status_code, 200)
-        self.assertEqual(self.client.get(reverse("analytics:player-profile", kwargs={"player_id": self.player.id})).status_code, 200)
-        self.assertEqual(self.client.get(reverse("analytics:player-compare")).status_code, 200)
-        self.assertEqual(self.client.get(reverse("analytics:import-list")).status_code, 200)
-        self.assertEqual(self.client.get(reverse("analytics:assessment-list")).status_code, 200)
-        self.assertEqual(self.client.get(reverse("analytics:observation-review-list")).status_code, 200)
-
-
-class CoachAssessmentWorkflowTests(TestCase):
-    def setUp(self):
-        self.coach = User.objects.create_user(username="coach", password="testpass")
-        self.other_coach = User.objects.create_user(username="othercoach", password="testpass")
-        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
-        self.player = Player.objects.create(first_name="Eugene", last_name="Lin", division="13U", team_name="Expos")
-        self.other_player = Player.objects.create(first_name="Alex", last_name="Chen", division="13U", team_name="Expos")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        attach_player_to_season(self.player, self.season)
-        attach_player_to_season(self.other_player, self.season)
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-
-    def response_payload(self, include_required=True):
-        data = {}
-        for question in self.setup_result.question_set.questions.filter(is_active=True):
-            field_name = f"question_{question.id}"
-            if question.response_type == RESPONSE_TYPE_RATING_1_5 and include_required:
-                data[field_name] = "4"
-            elif question.response_type == RESPONSE_TYPE_TEXT:
-                data[field_name] = "Good teammate."
-        return data
-
-    def test_dynamic_form_uses_configured_questions(self):
-        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-        question.prompt = "Edited dynamic question"
-        question.save()
-
-        form = CoachAssessmentForm(question_set=self.setup_result.question_set)
-
-        self.assertIn(f"question_{question.id}", form.fields)
-        self.assertEqual(form.fields[f"question_{question.id}"].label, "Edited dynamic question")
-
-    def test_assessment_list_requires_login_and_lists_players(self):
-        response = self.client.get(reverse("analytics:assessment-list"))
-        self.assertEqual(response.status_code, 302)
-
-        self.client.force_login(self.coach)
-        response = self.client.get(reverse("analytics:assessment-list"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.player.display_name)
-        self.assertContains(response, "Not started")
-
-    def test_invalid_cycle_parameter_does_not_crash_assessment_list(self):
-        self.client.force_login(self.coach)
-
-        response = self.client.get(reverse("analytics:assessment-list"), {"cycle": "not-a-number"})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.player.display_name)
-
-    def test_coach_can_open_dynamic_assessment_form_for_any_active_player(self):
-        prompt = self.setup_result.question_set.questions.first().prompt
-        self.client.force_login(self.coach)
-
-        response = self.client.get(reverse("analytics:assessment-player", kwargs={"player_id": self.other_player.id}))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.other_player.display_name)
-        self.assertContains(response, prompt)
-
-    def test_invalid_cycle_parameter_does_not_crash_assessment_form(self):
-        self.client.force_login(self.coach)
-
-        response = self.client.get(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}), {"cycle": "bad"})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.player.display_name)
-
-    def test_assessment_edit_uses_submit_permission_helper(self):
-        self.client.force_login(self.coach)
-
-        with patch("analytics.views.can_submit_coach_assessment", return_value=False):
-            response = self.client.get(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_coach_can_save_partial_draft(self):
-        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-        self.client.force_login(self.coach)
-
-        response = self.client.post(
-            reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}),
-            {"action": "save_draft", f"question_{question.id}": "3"},
-        )
-
-        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
-        self.assertEqual(observation.responses.get(question=question).numeric_value, Decimal("3.00"))
-
-    def test_submit_missing_required_responses_is_rejected(self):
-        self.client.force_login(self.coach)
-
-        response = self.client.post(
-            reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}),
-            {"action": "submit"},
-        )
-
-        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
-        self.assertEqual(response.status_code, 200)
-        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
-        self.assertContains(response, "This field is required")
-
-    def test_coach_can_submit_complete_assessment(self):
-        self.client.force_login(self.coach)
-        data = {"action": "submit"}
-        data.update(self.response_payload())
-
-        response = self.client.post(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}), data)
-
-        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
-        self.assertIsNotNone(observation.submitted_at)
-        self.assertEqual(observation.responses.count(), len(self.response_payload()))
-
-    def test_submitted_assessment_redirects_instead_of_creating_duplicate(self):
-        self.client.force_login(self.coach)
-        data = {"action": "submit"}
-        data.update(self.response_payload())
-        self.client.post(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}), data)
-        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
-
-        response = self.client.get(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}))
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
-        self.assertEqual(Observation.objects.filter(player=self.player, evaluator=self.coach).count(), 1)
-
-    def test_multiple_evaluators_can_submit_for_same_player(self):
-        for user in [self.coach, self.other_coach]:
-            self.client.force_login(user)
-            data = {"action": "submit"}
-            data.update(self.response_payload())
-            self.client.post(reverse("analytics:assessment-player", kwargs={"player_id": self.player.id}), data)
-
-        self.assertEqual(Observation.objects.filter(player=self.player, status=OBSERVATION_STATUS_SUBMITTED).count(), 2)
-
-    def test_coach_cannot_view_or_edit_other_evaluator_observation(self):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.other_coach,
-            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
-        )
-        submit_observation(result.observation)
-        self.client.force_login(self.coach)
-
-        detail_response = self.client.get(reverse("analytics:assessment-detail", kwargs={"observation_id": result.observation.id}))
-        edit_response = self.client.get(reverse("analytics:assessment-edit", kwargs={"observation_id": result.observation.id}))
-
-        self.assertEqual(detail_response.status_code, 403)
-        self.assertEqual(edit_response.status_code, 403)
-
-    def test_coach_detail_context_controls_edit_and_back_link(self):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-        )
-        self.client.force_login(self.coach)
-
-        response = self.client.get(reverse("analytics:assessment-detail", kwargs={"observation_id": result.observation.id}))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, reverse("analytics:assessment-edit", kwargs={"observation_id": result.observation.id}))
-        self.assertContains(response, f'href="{reverse("analytics:assessment-list")}"')
-
-    def test_staff_review_requires_staff_and_displays_observation(self):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
-        )
-        submit_observation(result.observation)
-
-        self.client.force_login(self.coach)
-        self.assertEqual(self.client.get(reverse("analytics:observation-review-list")).status_code, 403)
-
-        self.client.force_login(self.staff)
-        list_response = self.client.get(reverse("analytics:observation-review-list"))
-        detail_response = self.client.get(reverse("analytics:observation-review-detail", kwargs={"observation_id": result.observation.id}))
-
-        self.assertEqual(list_response.status_code, 200)
-        self.assertContains(list_response, self.player.display_name)
-        self.assertEqual(detail_response.status_code, 200)
-        self.assertContains(detail_response, result.observation.evaluator.username)
-
-    def test_staff_review_search_uses_single_q_filter(self):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
-        )
-        submit_observation(result.observation)
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:observation-review-list"), {"q": self.coach.username})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.player.display_name)
-
-    def test_invalid_cycle_parameter_does_not_crash_staff_review_list(self):
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:observation-review-list"), {"cycle": "bad"})
-
-        self.assertEqual(response.status_code, 200)
-
-    def test_staff_review_detail_back_link_returns_to_review_list(self):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
-        )
-        submit_observation(result.observation)
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:observation-review-detail", kwargs={"observation_id": result.observation.id}))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, f'href="{reverse("analytics:observation-review-list")}"')
-
-    def test_staff_can_reopen_submitted_observation(self):
-        result = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses={question: 4 for question in self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5)},
-        )
-        submit_observation(result.observation)
-        original_perspective = result.observation.evaluation_perspective
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("analytics:observation-review-detail", kwargs={"observation_id": result.observation.id}),
-            {"action": "reopen"},
-        )
-
-        result.observation.refresh_from_db()
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(result.observation.status, OBSERVATION_STATUS_REOPENED)
-        self.assertEqual(result.observation.evaluation_perspective, original_perspective)
-
-
-class EvaluationAccessSubmissionViewTests(TestCase):
-    def setUp(self):
-        self.coach = User.objects.create_user(username="coach-evaluator", password="testpass")
-        self.player_user = User.objects.create_user(username="player-evaluator", password="testpass")
-        self.guest = User.objects.create_user(username="guest-evaluator", password="testpass")
-        self.parent = User.objects.create_user(username="parent-user", password="testpass")
-        self.staff = User.objects.create_user(username="staff-evaluator", password="testpass", is_staff=True)
-        set_account_role(self.coach, AccountRole.COACH)
-        set_account_role(self.player_user, AccountRole.PLAYER)
-        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
-        set_account_role(self.parent, AccountRole.PARENT)
-        set_account_role(self.staff, AccountRole.STAFF)
-        self.self_player = Player.objects.create(first_name="Self", last_name="Player", division="13U", team_name="Expos")
-        self.target_player = Player.objects.create(first_name="Target", last_name="Player", division="13U", team_name="Expos")
-        self.inactive_player = Player.objects.create(first_name="Inactive", last_name="Player", division="13U", is_active=False)
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        attach_player_to_season(self.self_player, self.season)
-        attach_player_to_season(self.target_player, self.season)
-        link_user_to_player(self.player_user, self.self_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-
-    def response_payload(self, include_required=True):
-        data = {}
-        for question in self.setup_result.question_set.questions.filter(is_active=True):
-            field_name = f"question_{question.id}"
-            if question.response_type == RESPONSE_TYPE_RATING_1_5 and include_required:
-                data[field_name] = "4"
-            elif question.response_type == RESPONSE_TYPE_TEXT:
-                data[field_name] = "Good teammate."
-        return data
-
-    def service_response_payload(self):
-        return {
-            question: 4
-            for question in self.setup_result.question_set.questions.filter(
-                response_type=RESPONSE_TYPE_RATING_1_5,
-                is_required=True,
-                is_active=True,
-            )
-        }
-
-    def test_evaluation_list_permissions(self):
-        self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 302)
-        for user in [self.player_user, self.coach, self.guest, self.staff]:
-            with self.subTest(user=user.username):
-                self.client.force_login(user)
-                response = self.client.get(reverse("analytics:evaluation-list"))
-                self.assertEqual(response.status_code, 200)
-                self.assertContains(response, "Evaluations")
-                self.client.logout()
-
-        self.client.force_login(self.parent)
-        self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 403)
-
-    def test_evaluation_list_allows_self_and_uses_evaluation_copy(self):
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:evaluation-list"), {"q": "Player"})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Evaluate Player")
-        self.assertContains(response, "My submission")
-        self.assertContains(response, "Self Evaluation")
-        self.assertContains(response, reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
-        self.assertContains(response, reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
-
-    def test_player_can_open_evaluation_form_for_another_player(self):
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
-
-        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, f"Evaluate {self.target_player.display_name}")
-        self.assertContains(response, "Submit Evaluation")
-        self.assertContains(response, "Peer Evaluation")
-        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
-        self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
-        self.assertEqual(observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER)
-
-    def test_player_can_evaluate_self_but_not_inactive_player(self):
-        self.client.force_login(self.player_user)
-
-        self_response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
-        self_observation = Observation.objects.get(player=self.self_player, evaluator=self.player_user)
-        self.assertEqual(self_response.status_code, 200)
-        self.assertContains(self_response, "Self Evaluation")
-        self.assertEqual(self_observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF)
-        self.assertEqual(
-            self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.inactive_player.id})).status_code,
-            404,
-        )
-
-    def test_player_can_save_draft_and_resume(self):
-        question = self.setup_result.question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-        self.client.force_login(self.player_user)
-
-        response = self.client.post(
-            reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}),
-            {"action": "save_draft", f"question_{question.id}": "3"},
-        )
-        second_response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
-
-        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
-        self.assertEqual(second_response.status_code, 200)
-        self.assertEqual(Observation.objects.filter(player=self.target_player, evaluator=self.player_user).count(), 1)
-        self.assertEqual(observation.responses.get(question=question).numeric_value, Decimal("3.00"))
-
-    def test_player_can_submit_complete_evaluation(self):
-        self.client.force_login(self.player_user)
-        data = {"action": "submit"}
-        data.update(self.response_payload())
-
-        response = self.client.post(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}), data)
-
-        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
-        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
-        self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
-        self.assertEqual(observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER)
-
-    def test_player_self_evaluation_draft_resumes_and_submitted_duplicate_redirects(self):
-        self.client.force_login(self.player_user)
-        first_response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
-        second_response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
-        observation = Observation.objects.get(player=self.self_player, evaluator=self.player_user)
-
-        self.assertEqual(first_response.status_code, 200)
-        self.assertEqual(second_response.status_code, 200)
-        self.assertEqual(observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF)
-        self.assertEqual(Observation.objects.filter(player=self.self_player, evaluator=self.player_user).count(), 1)
-
-        data = {"action": "submit"}
-        data.update(self.response_payload())
-        self.client.post(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}), data)
-        response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.self_player.id}))
-        observation.refresh_from_db()
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
-        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
-
-    def test_submitted_evaluation_detail_is_private_to_evaluator_and_staff(self):
-        result = create_coach_assessment_observation(
-            player=self.target_player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.player_user,
-            responses=self.service_response_payload(),
-        )
-        observation = submit_observation(result.observation, actor=self.player_user)
-        detail_url = reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id})
-
-        self.client.force_login(self.player_user)
-        self.assertEqual(self.client.get(detail_url).status_code, 200)
-
-        for user in [self.coach, self.guest]:
-            with self.subTest(user=user.username):
-                self.client.force_login(user)
-                self.assertEqual(self.client.get(detail_url).status_code, 403)
-
-        self.client.force_login(self.staff)
-        self.assertEqual(self.client.get(detail_url).status_code, 200)
-
-    def test_player_cannot_view_another_evaluators_submitted_detail(self):
-        other_player_user = User.objects.create_user(username="other-player-evaluator", password="testpass")
-        set_account_role(other_player_user, AccountRole.PLAYER)
-        result = create_coach_assessment_observation(
-            player=self.target_player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=self.service_response_payload(),
-        )
-        observation = submit_observation(result.observation, actor=self.coach)
-
-        self.client.force_login(other_player_user)
-        response = self.client.get(reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_missing_required_responses_are_blocked(self):
-        self.client.force_login(self.player_user)
-
-        response = self.client.post(
-            reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}),
-            {"action": "submit"},
-        )
-
-        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
-        self.assertEqual(response.status_code, 200)
-        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
-        self.assertContains(response, "This field is required")
-
-    def test_submitted_evaluation_cannot_be_duplicated(self):
-        self.client.force_login(self.player_user)
-        data = {"action": "submit"}
-        data.update(self.response_payload())
-        self.client.post(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}), data)
-        observation = Observation.objects.get(player=self.target_player, evaluator=self.player_user)
-
-        response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": self.target_player.id}))
-
-        self.assertEqual(response.status_code, 302)
-        self.assertEqual(response["Location"], reverse("analytics:assessment-detail", kwargs={"observation_id": observation.id}))
-        self.assertEqual(Observation.objects.filter(player=self.target_player, evaluator=self.player_user).count(), 1)
-
-    def test_evaluation_list_submitted_copy_is_own_submission(self):
-        result = create_coach_assessment_observation(
-            player=self.target_player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.player_user,
-            responses=self.service_response_payload(),
-        )
-        submit_observation(result.observation, actor=self.player_user)
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:evaluation-list"), {"q": "Target"})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "View My Submission")
-        self.assertNotContains(response, ">View<")
-        self.assertNotContains(response, "evaluations about me")
-
-    def test_evaluation_list_uses_current_cycle_without_cycle_selector(self):
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:evaluation-list"), {"cycle": "999"})
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.cycle.name)
-        self.assertNotContains(response, 'name="cycle"')
-
-    def test_coach_and_guest_role_snapshots_continue_to_work(self):
-        for user, expected_role in [(self.coach, ROLE_COACH), (self.guest, ROLE_GUEST_EVALUATOR)]:
-            with self.subTest(user=user.username):
-                target = Player.objects.create(first_name=user.username, last_name="Target", division="13U")
-                attach_player_to_season(target, self.season)
-                self.client.force_login(user)
-                response = self.client.get(reverse("analytics:evaluation-player", kwargs={"player_id": target.id}))
-
-                observation = Observation.objects.get(player=target, evaluator=user)
-                self.assertEqual(response.status_code, 200)
-                self.assertEqual(observation.evaluator_role_key, expected_role)
-                self.client.logout()
-
-
-class MyEvaluationsViewTests(TestCase):
-    def setUp(self):
-        self.player_user = User.objects.create_user(
-            username="linked-player-user",
-            password="testpass",
-            first_name="Linked",
-            last_name="User",
-            email="linked@example.com",
-        )
-        self.other_player_user = User.objects.create_user(username="other-linked-player", password="testpass")
-        self.coach = User.objects.create_user(
-            username="coach-private-name",
-            password="testpass",
-            first_name="Coach",
-            last_name="Private",
-            email="coach-private@example.com",
-        )
-        self.guest = User.objects.create_user(username="guest-evaluator-private", password="testpass")
-        self.parent = User.objects.create_user(username="parent-no-self", password="testpass")
-        self.staff = User.objects.create_user(username="staff-review", password="testpass", is_staff=True)
-        set_account_role(self.player_user, AccountRole.PLAYER)
-        set_account_role(self.other_player_user, AccountRole.PLAYER)
-        set_account_role(self.coach, AccountRole.COACH)
-        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
-        set_account_role(self.parent, AccountRole.PARENT)
-        set_account_role(self.staff, AccountRole.STAFF)
-        self.player = Player.objects.create(first_name="Linked", last_name="Player", division="13U")
-        self.second_player = Player.objects.create(first_name="Second", last_name="Player", division="15U")
-        self.other_player = Player.objects.create(first_name="Other", last_name="Player", division="13U")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        attach_player_to_season(self.player, self.season)
-        attach_player_to_season(self.second_player, self.season, team_name="Mounties", division="15U")
-        attach_player_to_season(self.other_player, self.season)
-        link_user_to_player(self.player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-        link_user_to_player(self.other_player_user, self.other_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-
-    def service_response_payload(self, value=4, note="Good teammate."):
-        payload = {
-            question: value
-            for question in self.setup_result.question_set.questions.filter(
-                response_type=RESPONSE_TYPE_RATING_1_5,
-                is_required=True,
-                is_active=True,
-            )
-        }
-        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
-        payload[text_question] = note
-        return payload
-
-    def submitted_observation(self, player=None, evaluator=None, value=4, note="Good teammate."):
-        result = create_coach_assessment_observation(
-            player=player or self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=evaluator or self.coach,
-            responses=self.service_response_payload(value=value, note=note),
-        )
-        return submit_observation(result.observation, actor=evaluator or self.coach)
-
-    def test_my_evaluations_requires_login_and_handles_no_self_link(self):
-        self.assertEqual(self.client.get(reverse("analytics:my-evaluations")).status_code, 302)
-
-        self.client.force_login(self.parent)
-        response = self.client.get(reverse("analytics:my-evaluations"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "No player record is linked to your account.")
-
-    def test_player_can_view_submitted_evaluations_about_self(self):
-        observation = self.submitted_observation(note="Shows leadership.")
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:my-evaluations"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.player.display_name)
-        self.assertContains(response, self.cycle.name)
-        self.assertContains(response, "Coach")
-        self.assertContains(response, "Coach Evaluation")
-        self.assertContains(response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-
-    def test_my_evaluation_detail_hides_evaluator_identity_and_shows_feedback(self):
-        observation = self.submitted_observation(value=5, note="Strong instincts.")
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.player.display_name)
-        self.assertContains(response, "Coach Evaluation")
-        self.assertContains(response, "Evaluator Role")
-        self.assertContains(response, "Coach")
-        self.assertContains(response, self.cycle.name)
-        self.assertContains(response, "Strong instincts.")
-        self.assertContains(response, "5")
-        self.assertNotContains(response, self.coach.username)
-        self.assertNotContains(response, self.coach.email)
-        self.assertNotContains(response, self.coach.get_full_name())
-
-        players, summaries = get_my_evaluations(self.player_user)
-        detail = get_my_evaluation_detail(self.player_user, observation.id)
-        self.assertEqual(players, [self.player])
-        self.assertEqual(summaries[0].observation_id, observation.id)
-        self.assertFalse(hasattr(summaries[0], "observation"))
-        self.assertEqual(detail.observation_id, observation.id)
-        self.assertFalse(hasattr(detail, "observation"))
-
-    def test_my_evaluations_show_self_label_without_external_identity(self):
-        self_observation = self.submitted_observation(player=self.player, evaluator=self.player_user, note="My reflection.")
-        self.client.force_login(self.player_user)
-
-        list_response = self.client.get(reverse("analytics:my-evaluations"))
-        detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": self_observation.id}))
-
-        self.assertContains(list_response, "Self Evaluation")
-        self.assertContains(detail_response, "Self Evaluation")
-        self.assertContains(detail_response, "My reflection.")
-
-    def test_nonexistent_my_evaluation_detail_returns_404(self):
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": 999999}))
-
-        self.assertEqual(response.status_code, 404)
-
-    def test_player_cannot_view_another_players_evaluation_by_url(self):
-        observation = self.submitted_observation(player=self.other_player, evaluator=self.coach)
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-
-        self.assertEqual(response.status_code, 403)
-
-    def test_draft_and_reopened_observations_are_not_player_results(self):
-        draft = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=self.service_response_payload(),
-        ).observation
-        reopened = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.guest,
-            responses=self.service_response_payload(),
-        ).observation
-        reopened.status = OBSERVATION_STATUS_REOPENED
-        reopened.save(update_fields=["status", "updated_at"])
-        self.client.force_login(self.player_user)
-
-        list_response = self.client.get(reverse("analytics:my-evaluations"))
-        draft_detail = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": draft.id}))
-        reopened_detail = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": reopened.id}))
-
-        self.assertNotContains(list_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": draft.id}))
-        self.assertNotContains(list_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": reopened.id}))
-        self.assertEqual(draft_detail.status_code, 403)
-        self.assertEqual(reopened_detail.status_code, 403)
-
-    def test_multiple_self_links_are_listed_and_player_specific_route_enforces_ownership(self):
-        link_user_to_player(
-            self.player_user,
-            self.second_player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=False,
-        )
-        inactive_player = Player.objects.create(first_name="Inactive", last_name="Linked")
-        inactive_link = link_user_to_player(
-            self.player_user,
-            inactive_player,
-            relationship=UserPlayerRelationship.SELF,
-            is_primary=False,
-        )
-        deactivate_link(inactive_link)
-        first_observation = self.submitted_observation(player=self.player, evaluator=self.coach)
-        second_observation = self.submitted_observation(player=self.second_player, evaluator=self.guest)
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:my-evaluations"))
-        player_response = self.client.get(reverse("analytics:my-evaluations-player", kwargs={"player_id": self.second_player.id}))
-        first_detail = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": first_observation.id}))
-        second_detail = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": second_observation.id}))
-        forbidden_response = self.client.get(reverse("analytics:my-evaluations-player", kwargs={"player_id": self.other_player.id}))
-
-        self.assertContains(response, self.player.display_name)
-        self.assertContains(response, self.second_player.display_name)
-        self.assertNotContains(response, inactive_player.display_name)
-        self.assertContains(response, reverse("analytics:my-evaluations-player", kwargs={"player_id": self.player.id}))
-        self.assertContains(response, reverse("analytics:my-evaluations-player", kwargs={"player_id": self.second_player.id}))
-        self.assertContains(response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": first_observation.id}))
-        self.assertContains(player_response, self.second_player.display_name)
-        self.assertContains(player_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": second_observation.id}))
-        self.assertNotContains(player_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": first_observation.id}))
-        self.assertEqual(first_detail.status_code, 200)
-        self.assertEqual(second_detail.status_code, 200)
-        self.assertEqual(forbidden_response.status_code, 403)
-
-    def test_coach_without_self_link_cannot_view_player_result_detail(self):
-        observation = self.submitted_observation()
-        self.client.force_login(self.coach)
-
-        list_response = self.client.get(reverse("analytics:my-evaluations"))
-        detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-
-        self.assertContains(list_response, "No player record is linked to your account.")
-        self.assertEqual(detail_response.status_code, 403)
-
-        self.client.force_login(self.parent)
-        parent_detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-        self.assertEqual(parent_detail_response.status_code, 403)
-
-    def test_inactive_self_link_removes_my_evaluations_access(self):
-        observation = self.submitted_observation()
-        link = self.player_user.player_links.get(player=self.player, relationship=UserPlayerRelationship.SELF)
-        deactivate_link(link)
-        self.client.force_login(self.player_user)
-
-        list_response = self.client.get(reverse("analytics:my-evaluations"))
-        detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-        profile_response = self.client.get(reverse("accounts:profile"))
-
-        self.assertContains(list_response, "No player record is linked to your account.")
-        self.assertNotContains(list_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-        self.assertEqual(detail_response.status_code, 403)
-        self.assertNotContains(profile_response, reverse("analytics:my-evaluations"))
-
-        activate_link(link)
-        restored_list_response = self.client.get(reverse("analytics:my-evaluations"))
-        restored_detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-        restored_profile_response = self.client.get(reverse("accounts:profile"))
-        self.assertContains(restored_list_response, reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-        self.assertEqual(restored_detail_response.status_code, 200)
-        self.assertContains(restored_profile_response, reverse("analytics:my-evaluations"))
-
-    def test_inactive_player_is_not_available_in_my_evaluations(self):
-        observation = self.submitted_observation()
-        self.player.is_active = False
-        self.player.save(update_fields=["is_active", "updated_at"])
-        self.client.force_login(self.player_user)
-
-        list_response = self.client.get(reverse("analytics:my-evaluations"))
-        player_response = self.client.get(reverse("analytics:my-evaluations-player", kwargs={"player_id": self.player.id}))
-        detail_response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-        profile_response = self.client.get(reverse("accounts:profile"))
-
-        self.assertContains(list_response, "No player record is linked to your account.")
-        self.assertEqual(player_response.status_code, 403)
-        self.assertEqual(detail_response.status_code, 403)
-        self.assertNotContains(profile_response, reverse("analytics:my-evaluations"))
-
-    def test_staff_with_self_link_receives_player_safe_my_evaluation_output(self):
-        staff_player = Player.objects.create(first_name="Staff", last_name="Player")
-        attach_player_to_season(staff_player, self.season)
-        link_user_to_player(self.staff, staff_player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-        observation = self.submitted_observation(player=staff_player, evaluator=self.coach, note="Private staff-linked result.")
-        self.client.force_login(self.staff)
-
-        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, "Private staff-linked result.")
-        self.assertContains(response, "Coach")
-        self.assertNotContains(response, self.coach.username)
-        self.assertNotContains(response, self.coach.email)
-        self.assertNotContains(response, self.coach.get_full_name())
-
-    def test_my_evaluation_responses_follow_question_display_order(self):
-        question_set = self.setup_result.question_set
-        first_question = question_set.questions.filter(response_type=RESPONSE_TYPE_RATING_1_5).first()
-        second_question = question_set.questions.filter(response_type=RESPONSE_TYPE_TEXT).first()
-        first_question.display_order = 20
-        first_question.save(update_fields=["display_order", "updated_at"])
-        second_question.display_order = 10
-        second_question.prompt = "Appears before the rating"
-        second_question.save(update_fields=["display_order", "prompt", "updated_at"])
-        observation = create_coach_assessment_observation(
-            player=self.player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=[
-                {"question": first_question, "value": 4},
-                {"question": second_question, "value": "Ordered note."},
-            ],
-        ).observation
-        for required_question in question_set.questions.filter(
-            response_type=RESPONSE_TYPE_RATING_1_5,
-            is_required=True,
-            is_active=True,
-        ).exclude(pk=first_question.pk):
-            ObservationResponse.objects.create(
-                observation=observation,
-                question=required_question,
-                response_type=required_question.response_type,
-                numeric_value=Decimal("3"),
-            )
-        observation = submit_observation(observation, actor=self.coach)
-        self.client.force_login(self.player_user)
-
-        response = self.client.get(reverse("analytics:my-evaluation-detail", kwargs={"observation_id": observation.id}))
-
-        self.assertEqual(response.status_code, 200)
-        content = response.content.decode()
-        self.assertLess(content.index("Appears before the rating"), content.index(first_question.prompt))
-
-    def test_staff_review_and_submission_routes_still_work(self):
-        observation = self.submitted_observation()
-        self.client.force_login(self.staff)
-
-        self.assertEqual(self.client.get(reverse("analytics:observation-review-list")).status_code, 200)
-        self.assertEqual(
-            self.client.get(reverse("analytics:observation-review-detail", kwargs={"observation_id": observation.id})).status_code,
-            200,
-        )
-
-        self.client.force_login(self.player_user)
-        self.assertEqual(self.client.get(reverse("analytics:evaluation-list")).status_code, 200)
-
-
-class EvaluationReviewViewTests(TestCase):
-    def setUp(self):
-        self.coach = User.objects.create_user(
-            username="coach-review",
-            password="testpass",
-            first_name="Casey",
-            last_name="Coach",
-            email="coach-review@example.com",
-        )
-        self.second_coach = User.objects.create_user(
-            username="second-coach-review",
-            password="testpass",
-            first_name="Sam",
-            last_name="Coach",
-            email="sam-coach@example.com",
-        )
-        self.player_user = User.objects.create_user(username="player-review", password="testpass")
-        self.parent = User.objects.create_user(username="parent-review", password="testpass")
-        self.guest = User.objects.create_user(username="guest-review", password="testpass")
-        self.staff = User.objects.create_user(username="staff-review-phase5", password="testpass", is_staff=True)
-        self.role_staff = User.objects.create_user(username="role-staff-review", password="testpass")
-        self.role_admin = User.objects.create_user(username="role-admin-review", password="testpass")
-        set_account_role(self.coach, AccountRole.COACH)
-        set_account_role(self.second_coach, AccountRole.COACH)
-        set_account_role(self.player_user, AccountRole.PLAYER)
-        set_account_role(self.parent, AccountRole.PARENT)
-        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
-        set_account_role(self.staff, AccountRole.STAFF)
-        set_account_role(self.role_staff, AccountRole.STAFF)
-        set_account_role(self.role_admin, AccountRole.ADMIN)
-        self.player = Player.objects.create(first_name="Target", last_name="One", division="13U", team_name="Reds")
-        self.second_player = Player.objects.create(first_name="Target", last_name="Two", division="15U", team_name="Blues")
-        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
-        self.second_season = create_season(key="2026-summer", name="2026 Summer")
-        attach_player_to_season(self.player, self.season, team_name="Reds", division="13U")
-        attach_player_to_season(self.second_player, self.season, team_name="Reds", division="13U")
-        attach_player_to_season(self.second_player, self.second_season, team_name="Blues", division="15U")
-        self.setup_result = ensure_default_coach_assessment_setup()
-        self.cycle = EvaluationCycle.objects.create(
-            name="2026 13U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.season,
-        )
-        self.second_cycle = EvaluationCycle.objects.create(
-            name="2026 15U Coach Assessment",
-            cycle_type="Coach Assessment",
-            coach_assessment_question_set=self.setup_result.question_set,
-            season=self.second_season,
-        )
-
-    def service_response_payload(self, value=4, note="Good teammate."):
-        payload = {
-            question: value
-            for question in self.setup_result.question_set.questions.filter(
-                response_type=RESPONSE_TYPE_RATING_1_5,
-                is_required=True,
-                is_active=True,
-            )
-        }
-        text_question = self.setup_result.question_set.questions.get(response_type=RESPONSE_TYPE_TEXT)
-        payload[text_question] = note
-        return payload
-
-    def submitted_observation(self, player=None, evaluator=None, cycle=None, value=4, note="Good teammate."):
-        result = create_coach_assessment_observation(
-            player=player or self.player,
-            evaluation_cycle=cycle or self.cycle,
-            evaluator=evaluator or self.coach,
-            responses=self.service_response_payload(value=value, note=note),
-        )
-        return submit_observation(result.observation, actor=evaluator or self.coach)
-
-    def test_coach_can_review_all_submitted_evaluations(self):
-        first = self.submitted_observation(player=self.player, evaluator=self.coach, note="First submitted.")
-        second = self.submitted_observation(player=self.second_player, evaluator=self.second_coach, cycle=self.second_cycle, note="Second submitted.")
-        link_user_to_player(self.player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-        self_observation = self.submitted_observation(player=self.player, evaluator=self.player_user, note="Self submitted.")
-        self.client.force_login(self.coach)
-
-        response = self.client.get(reverse("analytics:evaluation-review-list"))
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.player.display_name)
-        self.assertContains(response, self.second_player.display_name)
-        self.assertContains(response, "Casey Coach")
-        self.assertContains(response, "Sam Coach")
-        self.assertContains(response, "Self Evaluation")
-        self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": first.id}))
-        self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": second.id}))
-        self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": self_observation.id}))
-        self.assertNotContains(response, self.coach.email)
-
-    def test_coach_review_access_rules(self):
-        self.submitted_observation()
-        for user in [self.player_user, self.parent, self.guest]:
-            with self.subTest(user=user.username):
-                self.client.force_login(user)
-                response = self.client.get(reverse("analytics:evaluation-review-list"))
-                self.assertEqual(response.status_code, 403)
-                self.client.logout()
-
-        for user in [self.coach, self.staff, self.role_staff, self.role_admin]:
-            with self.subTest(user=user.username):
-                self.client.force_login(user)
-                response = self.client.get(reverse("analytics:evaluation-review-list"))
-                self.assertEqual(response.status_code, 200)
-                self.client.logout()
-
-    def test_coach_role_does_not_grant_account_operations(self):
-        self.client.force_login(self.coach)
-
-        self.assertEqual(self.client.get(reverse("accounts:operations-dashboard")).status_code, 403)
-
-    def test_coach_review_filters_individually_and_in_combination(self):
-        first = self.submitted_observation(player=self.player, evaluator=self.coach, note="Reds note.")
-        second = self.submitted_observation(player=self.second_player, evaluator=self.second_coach, cycle=self.second_cycle, note="Blues note.")
-        link_user_to_player(self.player_user, self.player, relationship=UserPlayerRelationship.SELF, is_primary=True)
-        self_observation = self.submitted_observation(player=self.player, evaluator=self.player_user, note="Self note.")
-        today = timezone.localdate().isoformat()
-        self.client.force_login(self.coach)
-
-        cases = [
-            ({"q": "One"}, first, second),
-            ({"player": str(self.player.id)}, first, second),
-            ({"evaluator": str(self.coach.id)}, first, second),
-            ({"evaluator": "second-coach"}, second, first),
-            ({"evaluator_role": ROLE_COACH}, first, None),
-            ({"perspective": EVALUATION_PERSPECTIVE_SELF}, self_observation, first),
-            ({"perspective": EVALUATION_PERSPECTIVE_COACH}, first, self_observation),
-            ({"team": "Reds"}, first, second),
-            ({"division": "15U"}, second, first),
-            ({"cycle": str(self.second_cycle.id)}, second, first),
-            ({"submitted_from": today, "submitted_to": today}, first, None),
-            ({"q": "Target", "team": "Blues", "cycle": str(self.second_cycle.id)}, second, first),
-        ]
-        for params, included, excluded in cases:
-            with self.subTest(params=params):
-                response = self.client.get(reverse("analytics:evaluation-review-list"), params)
-                self.assertEqual(response.status_code, 200)
-                self.assertContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": included.id}))
-                if excluded:
-                    self.assertNotContains(response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": excluded.id}))
-
-    def test_coach_review_excludes_draft_and_reopened_observations(self):
-        submitted = self.submitted_observation(player=self.player, evaluator=self.coach)
-        draft = create_coach_assessment_observation(
-            player=self.second_player,
-            evaluation_cycle=self.cycle,
-            evaluator=self.coach,
-            responses=self.service_response_payload(),
-        ).observation
-        reopened = create_coach_assessment_observation(
-            player=self.second_player,
-            evaluation_cycle=self.second_cycle,
-            evaluator=self.second_coach,
-            responses=self.service_response_payload(),
-        ).observation
-        reopened.status = OBSERVATION_STATUS_REOPENED
-        reopened.save(update_fields=["status", "updated_at"])
-        self.client.force_login(self.coach)
-
-        list_response = self.client.get(reverse("analytics:evaluation-review-list"))
-        draft_detail = self.client.get(reverse("analytics:evaluation-review-detail", kwargs={"observation_id": draft.id}))
-        reopened_detail = self.client.get(reverse("analytics:evaluation-review-detail", kwargs={"observation_id": reopened.id}))
-
-        self.assertContains(list_response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": submitted.id}))
-        self.assertNotContains(list_response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": draft.id}))
-        self.assertNotContains(list_response, reverse("analytics:evaluation-review-detail", kwargs={"observation_id": reopened.id}))
-        self.assertEqual(draft_detail.status_code, 404)
-        self.assertEqual(reopened_detail.status_code, 404)
-
-    def test_coach_review_detail_is_read_only_and_exposes_safe_evaluator_identity(self):
-        observation = self.submitted_observation(note="Review detail note.")
-        self.client.force_login(self.coach)
-
-        response = self.client.get(reverse("analytics:evaluation-review-detail", kwargs={"observation_id": observation.id}))
-        post_response = self.client.post(reverse("analytics:evaluation-review-detail", kwargs={"observation_id": observation.id}), {"action": "reopen"})
-        observation.refresh_from_db()
-
-        self.assertEqual(response.status_code, 200)
-        self.assertContains(response, self.player.display_name)
-        self.assertContains(response, "Casey Coach")
-        self.assertContains(response, "Coach")
-        self.assertContains(response, "Review detail note.")
-        self.assertNotContains(response, self.coach.email)
-        self.assertNotContains(response, "Reopen")
-        self.assertEqual(post_response.status_code, 405)
-        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
-
-    def test_staff_review_reopen_remains_separate(self):
-        observation = self.submitted_observation()
-        self.client.force_login(self.staff)
-
-        response = self.client.post(
-            reverse("analytics:observation-review-detail", kwargs={"observation_id": observation.id}),
-            {"action": "reopen"},
-            follow=True,
-        )
-        observation.refresh_from_db()
-
-        self.assertEqual(response.status_code, 200)
-        self.assertEqual(observation.status, OBSERVATION_STATUS_REOPENED)
diff --git a/analytics/tests/__init__.py b/analytics/tests/__init__.py
new file mode 100644
index 0000000..e69de29
diff --git a/analytics/tests/helpers.py b/analytics/tests/helpers.py
new file mode 100644
index 0000000..50b7a3e
--- /dev/null
+++ b/analytics/tests/helpers.py
@@ -0,0 +1,242 @@
+from datetime import timedelta
+from decimal import Decimal
+from unittest.mock import patch
+
+from django.contrib import admin
+from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+from django.core.files.uploadedfile import SimpleUploadedFile
+from django.db import IntegrityError, transaction
+from django.test import TestCase
+from django.urls import reverse
+from django.utils import timezone
+
+from accounts.models import AccountRole, UserPlayerRelationship
+from accounts.services.link_service import (
+    activate_link,
+    deactivate_link,
+    link_user_to_player,
+)
+from accounts.services.profile_service import set_account_role
+from analytics.assessment_forms import CoachAssessmentForm
+from analytics.models import (
+    EVALUATION_PERSPECTIVE_COACH,
+    EVALUATION_PERSPECTIVE_GUEST,
+    EVALUATION_PERSPECTIVE_PEER,
+    EVALUATION_PERSPECTIVE_SELF,
+    EVALUATION_PERSPECTIVE_STAFF,
+    OBSERVATION_STATUS_DRAFT,
+    OBSERVATION_STATUS_REOPENED,
+    OBSERVATION_STATUS_SUBMITTED,
+    OBSERVATION_TYPE_COACH_ASSESSMENT,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    EvaluationCycle,
+    EvaluatorRole,
+    Observation,
+    ObservationQuestion,
+    ObservationQuestionSet,
+    ObservationResponse,
+    ObservationSource,
+    ObservationType,
+)
+from analytics.services.comparison_service import (
+    get_player_comparison,
+    get_player_score_summary,
+)
+from analytics.services.draft_service import (
+    get_draft_context_for_draft_player,
+    get_draft_contexts_for_draft,
+)
+from analytics.services.evaluation_access_service import (
+    get_my_evaluation_detail,
+    get_my_evaluations,
+)
+from analytics.services.metrics_service import (
+    completion_metrics,
+    draft_matching_metrics,
+    import_metrics,
+    observation_metrics,
+    recent_submitted_observations,
+)
+from analytics.services.observation_service import (
+    create_coach_assessment_observation,
+    create_observation,
+    default_coach_assessment_question_set,
+    get_observation_detail,
+    save_observation_responses,
+    submit_observation,
+    validate_required_responses,
+)
+from analytics.services.permissions import (
+    can_evaluate_player,
+    can_submit_evaluation,
+    can_view_own_evaluation_draft,
+    evaluation_perspective_for_user,
+    evaluator_role_for_user,
+)
+from analytics.services.player_service import (
+    DRAFT_STATUS_AVAILABLE,
+    DRAFT_STATUS_DRAFTED,
+    DRAFT_STATUS_NO_CONTEXT,
+    EVALUATION_HAS_ANY,
+    EVALUATION_HAS_SUBMITTED,
+    EVALUATION_NO_SUBMITTED,
+    EVALUATION_NOT_STARTED,
+    active_player_ids,
+    parse_player_search_filters,
+    search_players,
+)
+from analytics.services.question_service import (
+    COACH_ASSESSMENT_RUBRIC,
+    DEFAULT_COACH_ASSESSMENT_QUESTIONS,
+    DEFAULT_EVALUATOR_ROLES,
+    DEFAULT_OBSERVATION_SOURCES,
+    ROLE_ADMIN,
+    ROLE_COACH,
+    ROLE_GUEST_EVALUATOR,
+    ROLE_PLAYER,
+    ROLE_STAFF,
+    SOURCE_COACH,
+    ensure_default_coach_assessment_setup,
+    get_active_questions,
+    get_question_set_for_cycle,
+)
+from analytics.services.reporting_service import get_command_center_context
+from analytics.services.timeline_service import get_player_timeline
+from drafts.models import Draft, DraftAction, DraftActionType, DraftPlayer, DraftTeam
+from players.models import (
+    Player,
+    PlayerImportBatch,
+    PlayerImportStatus,
+    PlayerSourceRow,
+    PlayerTag,
+)
+from players.services.import_service import SOURCE_MEMBER_LIST
+from players.services.tag_service import assign_tag
+from seasons.services.coach_assignment_service import create_assignment
+from seasons.services.membership_service import create_membership
+from seasons.services.season_service import create_season
+from seasons.services.team_service import get_or_create_season_team
+
+User = get_user_model()
+
+
+def attach_player_to_season(
+    player, season, *, team_name=None, division=None, is_primary=True
+):
+    season_team, _ = get_or_create_season_team(
+        season=season,
+        name=team_name or player.team_name or "Expos",
+        division=division or player.division or "13U",
+    )
+    return create_membership(
+        player=player, season_team=season_team, is_primary=is_primary, is_active=True
+    )
+
+
+__all__ = (
+    "AccountRole",
+    "COACH_ASSESSMENT_RUBRIC",
+    "CoachAssessmentForm",
+    "DEFAULT_COACH_ASSESSMENT_QUESTIONS",
+    "DEFAULT_EVALUATOR_ROLES",
+    "DEFAULT_OBSERVATION_SOURCES",
+    "DRAFT_STATUS_AVAILABLE",
+    "DRAFT_STATUS_DRAFTED",
+    "DRAFT_STATUS_NO_CONTEXT",
+    "Decimal",
+    "Draft",
+    "DraftAction",
+    "DraftActionType",
+    "DraftPlayer",
+    "DraftTeam",
+    "EVALUATION_HAS_ANY",
+    "EVALUATION_HAS_SUBMITTED",
+    "EVALUATION_NOT_STARTED",
+    "EVALUATION_NO_SUBMITTED",
+    "EVALUATION_PERSPECTIVE_COACH",
+    "EVALUATION_PERSPECTIVE_GUEST",
+    "EVALUATION_PERSPECTIVE_PEER",
+    "EVALUATION_PERSPECTIVE_SELF",
+    "EVALUATION_PERSPECTIVE_STAFF",
+    "EvaluationCycle",
+    "EvaluatorRole",
+    "IntegrityError",
+    "OBSERVATION_STATUS_DRAFT",
+    "OBSERVATION_STATUS_REOPENED",
+    "OBSERVATION_STATUS_SUBMITTED",
+    "OBSERVATION_TYPE_COACH_ASSESSMENT",
+    "Observation",
+    "ObservationQuestion",
+    "ObservationQuestionSet",
+    "ObservationResponse",
+    "ObservationSource",
+    "ObservationType",
+    "Player",
+    "PlayerImportBatch",
+    "PlayerImportStatus",
+    "PlayerSourceRow",
+    "PlayerTag",
+    "RESPONSE_TYPE_RATING_1_5",
+    "RESPONSE_TYPE_TEXT",
+    "ROLE_ADMIN",
+    "ROLE_COACH",
+    "ROLE_GUEST_EVALUATOR",
+    "ROLE_PLAYER",
+    "ROLE_STAFF",
+    "SOURCE_COACH",
+    "SOURCE_MEMBER_LIST",
+    "SimpleUploadedFile",
+    "TestCase",
+    "User",
+    "UserPlayerRelationship",
+    "ValidationError",
+    "activate_link",
+    "active_player_ids",
+    "admin",
+    "assign_tag",
+    "attach_player_to_season",
+    "can_evaluate_player",
+    "can_submit_evaluation",
+    "can_view_own_evaluation_draft",
+    "completion_metrics",
+    "create_assignment",
+    "create_coach_assessment_observation",
+    "create_membership",
+    "create_observation",
+    "create_season",
+    "deactivate_link",
+    "default_coach_assessment_question_set",
+    "draft_matching_metrics",
+    "ensure_default_coach_assessment_setup",
+    "evaluation_perspective_for_user",
+    "evaluator_role_for_user",
+    "get_active_questions",
+    "get_command_center_context",
+    "get_draft_context_for_draft_player",
+    "get_draft_contexts_for_draft",
+    "get_my_evaluation_detail",
+    "get_my_evaluations",
+    "get_observation_detail",
+    "get_or_create_season_team",
+    "get_player_comparison",
+    "get_player_score_summary",
+    "get_player_timeline",
+    "get_question_set_for_cycle",
+    "import_metrics",
+    "link_user_to_player",
+    "observation_metrics",
+    "parse_player_search_filters",
+    "patch",
+    "recent_submitted_observations",
+    "reverse",
+    "save_observation_responses",
+    "search_players",
+    "set_account_role",
+    "submit_observation",
+    "timedelta",
+    "timezone",
+    "transaction",
+    "validate_required_responses",
+)
diff --git a/analytics/tests/test_coach_assessments.py b/analytics/tests/test_coach_assessments.py
new file mode 100644
index 0000000..c9aac3d
--- /dev/null
+++ b/analytics/tests/test_coach_assessments.py
@@ -0,0 +1,416 @@
+from analytics.tests.helpers import (
+    OBSERVATION_STATUS_DRAFT,
+    OBSERVATION_STATUS_REOPENED,
+    OBSERVATION_STATUS_SUBMITTED,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    CoachAssessmentForm,
+    Decimal,
+    EvaluationCycle,
+    Observation,
+    Player,
+    TestCase,
+    User,
+    attach_player_to_season,
+    create_coach_assessment_observation,
+    create_season,
+    ensure_default_coach_assessment_setup,
+    patch,
+    reverse,
+    submit_observation,
+)
+
+
+class CoachAssessmentWorkflowTests(TestCase):
+    def setUp(self):
+        self.coach = User.objects.create_user(username="coach", password="testpass")
+        self.other_coach = User.objects.create_user(
+            username="othercoach", password="testpass"
+        )
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.player = Player.objects.create(
+            first_name="Eugene", last_name="Lin", division="13U", team_name="Expos"
+        )
+        self.other_player = Player.objects.create(
+            first_name="Alex", last_name="Chen", division="13U", team_name="Expos"
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.other_player, self.season)
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+
+    def response_payload(self, include_required=True):
+        data = {}
+        for question in self.setup_result.question_set.questions.filter(is_active=True):
+            field_name = f"question_{question.id}"
+            if question.response_type == RESPONSE_TYPE_RATING_1_5 and include_required:
+                data[field_name] = "4"
+            elif question.response_type == RESPONSE_TYPE_TEXT:
+                data[field_name] = "Good teammate."
+        return data
+
+    def test_dynamic_form_uses_configured_questions(self):
+        question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        question.prompt = "Edited dynamic question"
+        question.save()
+
+        form = CoachAssessmentForm(question_set=self.setup_result.question_set)
+
+        self.assertIn(f"question_{question.id}", form.fields)
+        self.assertEqual(
+            form.fields[f"question_{question.id}"].label, "Edited dynamic question"
+        )
+
+    def test_assessment_list_requires_login_and_lists_players(self):
+        response = self.client.get(reverse("analytics:assessment-list"))
+        self.assertEqual(response.status_code, 302)
+
+        self.client.force_login(self.coach)
+        response = self.client.get(reverse("analytics:assessment-list"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, "Not started")
+
+    def test_invalid_cycle_parameter_does_not_crash_assessment_list(self):
+        self.client.force_login(self.coach)
+
+        response = self.client.get(
+            reverse("analytics:assessment-list"), {"cycle": "not-a-number"}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+
+    def test_coach_can_open_dynamic_assessment_form_for_any_active_player(self):
+        prompt = self.setup_result.question_set.questions.first().prompt
+        self.client.force_login(self.coach)
+
+        response = self.client.get(
+            reverse(
+                "analytics:assessment-player",
+                kwargs={"player_id": self.other_player.id},
+            )
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.other_player.display_name)
+        self.assertContains(response, prompt)
+
+    def test_invalid_cycle_parameter_does_not_crash_assessment_form(self):
+        self.client.force_login(self.coach)
+
+        response = self.client.get(
+            reverse(
+                "analytics:assessment-player", kwargs={"player_id": self.player.id}
+            ),
+            {"cycle": "bad"},
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+
+    def test_assessment_edit_uses_submit_permission_helper(self):
+        self.client.force_login(self.coach)
+
+        with patch("analytics.views.can_submit_coach_assessment", return_value=False):
+            response = self.client.get(
+                reverse(
+                    "analytics:assessment-player", kwargs={"player_id": self.player.id}
+                )
+            )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_coach_can_save_partial_draft(self):
+        question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        self.client.force_login(self.coach)
+
+        response = self.client.post(
+            reverse(
+                "analytics:assessment-player", kwargs={"player_id": self.player.id}
+            ),
+            {"action": "save_draft", f"question_{question.id}": "3"},
+        )
+
+        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
+        self.assertEqual(
+            observation.responses.get(question=question).numeric_value, Decimal("3.00")
+        )
+
+    def test_submit_missing_required_responses_is_rejected(self):
+        self.client.force_login(self.coach)
+
+        response = self.client.post(
+            reverse(
+                "analytics:assessment-player", kwargs={"player_id": self.player.id}
+            ),
+            {"action": "submit"},
+        )
+
+        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
+        self.assertContains(response, "This field is required")
+
+    def test_coach_can_submit_complete_assessment(self):
+        self.client.force_login(self.coach)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+
+        response = self.client.post(
+            reverse(
+                "analytics:assessment-player", kwargs={"player_id": self.player.id}
+            ),
+            data,
+        )
+
+        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
+        self.assertIsNotNone(observation.submitted_at)
+        self.assertEqual(observation.responses.count(), len(self.response_payload()))
+
+    def test_submitted_assessment_redirects_instead_of_creating_duplicate(self):
+        self.client.force_login(self.coach)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+        self.client.post(
+            reverse(
+                "analytics:assessment-player", kwargs={"player_id": self.player.id}
+            ),
+            data,
+        )
+        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
+
+        response = self.client.get(
+            reverse("analytics:assessment-player", kwargs={"player_id": self.player.id})
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(
+            response["Location"],
+            reverse(
+                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
+            ),
+        )
+        self.assertEqual(
+            Observation.objects.filter(
+                player=self.player, evaluator=self.coach
+            ).count(),
+            1,
+        )
+
+    def test_multiple_evaluators_can_submit_for_same_player(self):
+        for user in [self.coach, self.other_coach]:
+            self.client.force_login(user)
+            data = {"action": "submit"}
+            data.update(self.response_payload())
+            self.client.post(
+                reverse(
+                    "analytics:assessment-player", kwargs={"player_id": self.player.id}
+                ),
+                data,
+            )
+
+        self.assertEqual(
+            Observation.objects.filter(
+                player=self.player, status=OBSERVATION_STATUS_SUBMITTED
+            ).count(),
+            2,
+        )
+
+    def test_coach_cannot_view_or_edit_other_evaluator_observation(self):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.other_coach,
+            responses={
+                question: 4
+                for question in self.setup_result.question_set.questions.filter(
+                    response_type=RESPONSE_TYPE_RATING_1_5
+                )
+            },
+        )
+        submit_observation(result.observation)
+        self.client.force_login(self.coach)
+
+        detail_response = self.client.get(
+            reverse(
+                "analytics:assessment-detail",
+                kwargs={"observation_id": result.observation.id},
+            )
+        )
+        edit_response = self.client.get(
+            reverse(
+                "analytics:assessment-edit",
+                kwargs={"observation_id": result.observation.id},
+            )
+        )
+
+        self.assertEqual(detail_response.status_code, 403)
+        self.assertEqual(edit_response.status_code, 403)
+
+    def test_coach_detail_context_controls_edit_and_back_link(self):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+        )
+        self.client.force_login(self.coach)
+
+        response = self.client.get(
+            reverse(
+                "analytics:assessment-detail",
+                kwargs={"observation_id": result.observation.id},
+            )
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:assessment-edit",
+                kwargs={"observation_id": result.observation.id},
+            ),
+        )
+        self.assertContains(response, f'href="{reverse("analytics:assessment-list")}"')
+
+    def test_staff_review_requires_staff_and_displays_observation(self):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses={
+                question: 4
+                for question in self.setup_result.question_set.questions.filter(
+                    response_type=RESPONSE_TYPE_RATING_1_5
+                )
+            },
+        )
+        submit_observation(result.observation)
+
+        self.client.force_login(self.coach)
+        self.assertEqual(
+            self.client.get(reverse("analytics:observation-review-list")).status_code,
+            403,
+        )
+
+        self.client.force_login(self.staff)
+        list_response = self.client.get(reverse("analytics:observation-review-list"))
+        detail_response = self.client.get(
+            reverse(
+                "analytics:observation-review-detail",
+                kwargs={"observation_id": result.observation.id},
+            )
+        )
+
+        self.assertEqual(list_response.status_code, 200)
+        self.assertContains(list_response, self.player.display_name)
+        self.assertEqual(detail_response.status_code, 200)
+        self.assertContains(detail_response, result.observation.evaluator.username)
+
+    def test_staff_review_search_uses_single_q_filter(self):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses={
+                question: 4
+                for question in self.setup_result.question_set.questions.filter(
+                    response_type=RESPONSE_TYPE_RATING_1_5
+                )
+            },
+        )
+        submit_observation(result.observation)
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("analytics:observation-review-list"), {"q": self.coach.username}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+
+    def test_invalid_cycle_parameter_does_not_crash_staff_review_list(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("analytics:observation-review-list"), {"cycle": "bad"}
+        )
+
+        self.assertEqual(response.status_code, 200)
+
+    def test_staff_review_detail_back_link_returns_to_review_list(self):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses={
+                question: 4
+                for question in self.setup_result.question_set.questions.filter(
+                    response_type=RESPONSE_TYPE_RATING_1_5
+                )
+            },
+        )
+        submit_observation(result.observation)
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse(
+                "analytics:observation-review-detail",
+                kwargs={"observation_id": result.observation.id},
+            )
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(
+            response, f'href="{reverse("analytics:observation-review-list")}"'
+        )
+
+    def test_staff_can_reopen_submitted_observation(self):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses={
+                question: 4
+                for question in self.setup_result.question_set.questions.filter(
+                    response_type=RESPONSE_TYPE_RATING_1_5
+                )
+            },
+        )
+        submit_observation(result.observation)
+        original_perspective = result.observation.evaluation_perspective
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse(
+                "analytics:observation-review-detail",
+                kwargs={"observation_id": result.observation.id},
+            ),
+            {"action": "reopen"},
+        )
+
+        result.observation.refresh_from_db()
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(result.observation.status, OBSERVATION_STATUS_REOPENED)
+        self.assertEqual(
+            result.observation.evaluation_perspective, original_perspective
+        )
diff --git a/analytics/tests/test_command_center.py b/analytics/tests/test_command_center.py
new file mode 100644
index 0000000..28b62b3
--- /dev/null
+++ b/analytics/tests/test_command_center.py
@@ -0,0 +1,355 @@
+from analytics.tests.helpers import (
+    OBSERVATION_STATUS_DRAFT,
+    OBSERVATION_STATUS_REOPENED,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    Decimal,
+    Draft,
+    DraftAction,
+    DraftActionType,
+    DraftPlayer,
+    DraftTeam,
+    EvaluationCycle,
+    Observation,
+    ObservationQuestion,
+    Player,
+    PlayerImportBatch,
+    PlayerImportStatus,
+    TestCase,
+    User,
+    active_player_ids,
+    attach_player_to_season,
+    completion_metrics,
+    create_coach_assessment_observation,
+    create_season,
+    draft_matching_metrics,
+    ensure_default_coach_assessment_setup,
+    get_command_center_context,
+    import_metrics,
+    observation_metrics,
+    parse_player_search_filters,
+    recent_submitted_observations,
+    reverse,
+    search_players,
+    submit_observation,
+    timedelta,
+    timezone,
+)
+
+
+class AnalyticsCommandCenterServiceTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.coach = User.objects.create_user(username="coach", password="testpass")
+        self.other_coach = User.objects.create_user(
+            username="othercoach", password="testpass"
+        )
+        self.player = Player.objects.create(
+            first_name="Eugene",
+            last_name="Lin",
+            birth_year=2012,
+            division="13U",
+            team_name="Expos",
+        )
+        self.other_player = Player.objects.create(
+            first_name="Alex",
+            last_name="Chen",
+            birth_year=2011,
+            division="15U",
+            team_name="Mounties",
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(
+            self.other_player, self.season, team_name="Mounties", division="15U"
+        )
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+
+    def rating_payload(self, value=4):
+        return {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5
+            )
+        }
+
+    def submit_assessment(self, evaluator=None, player=None, value=4):
+        result = create_coach_assessment_observation(
+            player=player or self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=evaluator or self.coach,
+            responses=self.rating_payload(value),
+        )
+        return submit_observation(result.observation, actor=evaluator or self.coach)
+
+    def test_player_population_helpers_live_in_player_service(self):
+        self.assertIn(self.player.id, active_player_ids(division="13U"))
+        self.assertNotIn(self.other_player.id, active_player_ids(division="13U"))
+
+        result = search_players(parse_player_search_filters({"q": "Eugene"}))
+
+        self.assertEqual(result.players, [self.player])
+
+    def test_completion_and_observation_metrics_respect_cycle_and_filters(self):
+        self.submit_assessment(value=5)
+        create_coach_assessment_observation(
+            player=self.other_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.other_coach,
+            status=OBSERVATION_STATUS_DRAFT,
+            responses=self.rating_payload(2),
+        )
+
+        completion = completion_metrics(cycle=self.cycle, division="13U")
+        observations = observation_metrics(cycle=self.cycle, division="13U")
+
+        self.assertEqual(completion.total_active_players, 1)
+        self.assertEqual(completion.players_with_submitted_assessment, 1)
+        self.assertEqual(completion.players_without_submitted_assessment, 0)
+        self.assertEqual(completion.completion_rate, Decimal("100"))
+        self.assertEqual(observations.submitted_count, 1)
+        self.assertEqual(observations.draft_count, 0)
+        self.assertEqual(observations.by_category_average[0].average, Decimal("5"))
+
+    def test_metrics_exclude_draft_and_reopened_from_submitted_rating_summaries(self):
+        self.submit_assessment(evaluator=self.coach, value=5)
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.other_coach,
+            status=OBSERVATION_STATUS_REOPENED,
+            responses=self.rating_payload(1),
+        )
+
+        observations = observation_metrics(cycle=self.cycle)
+
+        averages = {row.label: row.average for row in observations.by_category_average}
+        self.assertTrue(averages)
+        self.assertEqual(set(averages.values()), {Decimal("5")})
+
+    def test_coach_to_coach_spread_requires_two_evaluators(self):
+        self.submit_assessment(evaluator=self.coach, value=2)
+        self.submit_assessment(evaluator=self.other_coach, value=5)
+
+        observations = observation_metrics(cycle=self.cycle)
+
+        self.assertTrue(observations.variance_rows)
+        self.assertEqual(observations.variance_rows[0].player, self.player)
+        self.assertEqual(observations.variance_rows[0].spread, Decimal("3"))
+
+    def test_import_summary_counts_statuses_and_rows(self):
+        PlayerImportBatch.objects.create(
+            source="member_list",
+            original_filename="members.csv",
+            status=PlayerImportStatus.NEEDS_REVIEW,
+            rows_created=1,
+            rows_updated=2,
+            rows_skipped=3,
+            rows_conflicted=4,
+        )
+        PlayerImportBatch.objects.create(
+            source="member_list",
+            original_filename="committed.csv",
+            status=PlayerImportStatus.COMMITTED,
+        )
+
+        summary = import_metrics()
+
+        self.assertEqual(summary.total_batches, 2)
+        self.assertEqual(summary.needs_review_count, 1)
+        self.assertEqual(summary.committed_count, 1)
+        self.assertEqual(summary.rows_created, 1)
+        self.assertEqual(summary.rows_conflicted, 4)
+        self.assertEqual(len(summary.recent_batches), 2)
+
+    def test_draft_matching_summary_uses_draft_context_and_detects_mismatch(self):
+        expected_round_question = ObservationQuestion.objects.create(
+            question_set=self.setup_result.question_set,
+            key="expected_draft_round",
+            prompt="Expected draft round",
+            response_type=RESPONSE_TYPE_TEXT,
+            metadata={"draft_context_field": "expected_draft_round"},
+            display_order=100,
+        )
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses={**self.rating_payload(4), expected_round_question: "1"},
+        ).observation
+        submit_observation(observation, actor=self.coach)
+        draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
+        team = DraftTeam.objects.create(draft=draft, name="Expos Navy", display_order=1)
+        DraftTeam.objects.create(draft=draft, name="Expos Gold", display_order=2)
+        draft_player = DraftPlayer.objects.create(
+            draft=draft,
+            first_name="Eugene",
+            last_name="Lin",
+            full_name="Eugene Lin",
+            extra_data={"Birth Year": "2012"},
+        )
+        DraftPlayer.objects.create(
+            draft=draft, first_name="No", last_name="Match", full_name="No Match"
+        )
+        DraftAction.objects.create(
+            draft=draft,
+            action_type=DraftActionType.PLAYER_DRAFTED,
+            player=draft_player,
+            to_team=team,
+            pick_number=3,
+        )
+
+        summary = draft_matching_metrics(division="13U")
+
+        self.assertEqual(summary.matched_player_count, 1)
+        self.assertEqual(summary.drafted_player_count, 1)
+        self.assertEqual(summary.no_context_player_count, 0)
+        self.assertEqual(summary.unmatched_draft_player_count, 1)
+        self.assertEqual(summary.expected_round_mismatch_count, 1)
+        self.assertEqual(summary.mismatches[0].player, self.player)
+
+    def test_recent_observations_are_ordered_and_limited(self):
+        older = self.submit_assessment(evaluator=self.coach, value=3)
+        newer = self.submit_assessment(evaluator=self.other_coach, value=4)
+        Observation.objects.filter(pk=older.pk).update(
+            submitted_at=timezone.now() - timedelta(days=1)
+        )
+        Observation.objects.filter(pk=newer.pk).update(submitted_at=timezone.now())
+
+        observations = recent_submitted_observations(cycle=self.cycle, limit=1)
+
+        self.assertEqual(observations, [Observation.objects.get(pk=newer.pk)])
+
+    def test_reporting_context_is_grouped_and_template_ready(self):
+        self.submit_assessment()
+
+        context = get_command_center_context(cycle_id=self.cycle.id, division="13U")
+
+        self.assertTrue(context.summary_cards)
+        self.assertEqual(context.completion_summary.active_cycle, self.cycle)
+        self.assertTrue(context.observation_summary.by_category_average)
+        self.assertIsNotNone(context.import_summary)
+        self.assertIsNotNone(context.draft_summary)
+        self.assertTrue(context.recent_observations)
+        self.assertTrue(context.navigation_links)
+        self.assertFalse(hasattr(context, "total_active_players"))
+
+
+class AnalyticsCommandCenterViewTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.coach = User.objects.create_user(username="coach", password="testpass")
+        self.player = Player.objects.create(
+            first_name="Eugene", last_name="Lin", division="13U", team_name="Expos"
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        attach_player_to_season(self.player, self.season)
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+
+    def rating_payload(self, value=4):
+        return {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5
+            )
+        }
+
+    def test_command_center_requires_staff(self):
+        url = reverse("analytics:command-center")
+        self.assertEqual(self.client.get(url).status_code, 302)
+
+        self.client.force_login(self.coach)
+        self.assertEqual(self.client.get(url).status_code, 403)
+
+    def test_staff_can_render_command_center_links_and_empty_states(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("analytics:command-center"), {"cycle": "not-a-number"}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Analytics Command Center")
+        self.assertContains(response, reverse("analytics:import-list"))
+        self.assertContains(response, reverse("analytics:player-search"))
+        self.assertContains(response, reverse("analytics:player-compare"))
+        self.assertContains(response, reverse("analytics:assessment-list"))
+        self.assertContains(response, reverse("analytics:observation-review-list"))
+        self.assertContains(response, "No player imports yet.")
+        self.assertContains(response, "No submitted observations yet.")
+
+    def test_command_center_renders_populated_summaries_and_filters(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.rating_payload(4),
+        ).observation
+        submit_observation(observation, actor=self.coach)
+        PlayerImportBatch.objects.create(
+            source="member_list",
+            original_filename="members.csv",
+            status=PlayerImportStatus.COMMITTED,
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("analytics:command-center"), {"division": "13U", "team": "Expos"}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Submitted assessments")
+        self.assertContains(response, "Completion rate")
+        self.assertContains(response, "Average Score By Category")
+        self.assertContains(response, "members.csv")
+        self.assertContains(response, self.player.display_name)
+        self.assertEqual(response.context["filters"]["division"], "13U")
+        self.assertEqual(response.context["filters"]["team"], "Expos")
+
+    def test_phase_seven_regression_existing_pages_render(self):
+        self.client.force_login(self.staff)
+
+        self.assertEqual(
+            self.client.get(reverse("analytics:player-search")).status_code, 200
+        )
+        self.assertEqual(
+            self.client.get(
+                reverse(
+                    "analytics:player-profile", kwargs={"player_id": self.player.id}
+                )
+            ).status_code,
+            200,
+        )
+        self.assertEqual(
+            self.client.get(reverse("analytics:player-compare")).status_code, 200
+        )
+        self.assertEqual(
+            self.client.get(reverse("analytics:import-list")).status_code, 200
+        )
+        self.assertEqual(
+            self.client.get(reverse("analytics:assessment-list")).status_code, 200
+        )
+        self.assertEqual(
+            self.client.get(reverse("analytics:observation-review-list")).status_code,
+            200,
+        )
diff --git a/analytics/tests/test_draft_context.py b/analytics/tests/test_draft_context.py
new file mode 100644
index 0000000..7d1f8db
--- /dev/null
+++ b/analytics/tests/test_draft_context.py
@@ -0,0 +1,209 @@
+from analytics.tests.helpers import (
+    OBSERVATION_STATUS_DRAFT,
+    OBSERVATION_STATUS_REOPENED,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    Decimal,
+    Draft,
+    DraftAction,
+    DraftActionType,
+    DraftPlayer,
+    DraftTeam,
+    EvaluationCycle,
+    Observation,
+    ObservationQuestion,
+    Player,
+    TestCase,
+    User,
+    attach_player_to_season,
+    create_coach_assessment_observation,
+    create_season,
+    ensure_default_coach_assessment_setup,
+    get_draft_context_for_draft_player,
+    get_draft_contexts_for_draft,
+    submit_observation,
+    timedelta,
+    timezone,
+)
+
+
+class AnalyticsDraftContextServiceTests(TestCase):
+    def setUp(self):
+        self.coach = User.objects.create_user(username="coach", password="testpass")
+        self.other_coach = User.objects.create_user(
+            username="othercoach", password="testpass"
+        )
+        self.third_coach = User.objects.create_user(
+            username="thirdcoach", password="testpass"
+        )
+        self.player = Player.objects.create(
+            first_name="Eugene",
+            last_name="Lin",
+            birth_year=2012,
+            division="13U",
+            team_name="Expos",
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        attach_player_to_season(self.player, self.season)
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+        self.draft = Draft.objects.create(
+            name="2026 VCB 13U", year=2026, division="13U"
+        )
+        self.team = DraftTeam.objects.create(
+            draft=self.draft, name="Expos Navy", display_order=1
+        )
+        DraftTeam.objects.create(draft=self.draft, name="Expos Gold", display_order=2)
+        self.draft_player = DraftPlayer.objects.create(
+            draft=self.draft,
+            first_name="Eugene",
+            last_name="Lin",
+            full_name="Eugene Lin",
+            extra_data={"Birth Year": "2012"},
+        )
+
+    def submitted_observation(self, evaluator, rating=4):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=evaluator,
+            responses={
+                question: rating
+                for question in self.setup_result.question_set.questions.filter(
+                    response_type=RESPONSE_TYPE_RATING_1_5
+                )
+            },
+        )
+        return submit_observation(result.observation, actor=evaluator)
+
+    def test_draft_context_retrieves_submitted_observation_and_selection(self):
+        expected_round_question = ObservationQuestion.objects.create(
+            question_set=self.setup_result.question_set,
+            key="expected_draft_round",
+            prompt="Expected draft round",
+            response_type=RESPONSE_TYPE_TEXT,
+            metadata={"draft_context_field": "expected_draft_round"},
+            display_order=100,
+        )
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses={
+                **{
+                    question: 4
+                    for question in self.setup_result.question_set.questions.filter(
+                        response_type=RESPONSE_TYPE_RATING_1_5
+                    )
+                },
+                expected_round_question: "2",
+            },
+        ).observation
+        submit_observation(observation, actor=self.coach)
+        DraftAction.objects.create(
+            draft=self.draft,
+            action_type=DraftActionType.PLAYER_DRAFTED,
+            player=self.draft_player,
+            to_team=self.team,
+            pick_number=3,
+        )
+
+        context = get_draft_context_for_draft_player(self.draft_player)
+
+        self.assertTrue(context.is_matched)
+        self.assertEqual(context.matched_player, self.player)
+        self.assertEqual(context.pick_number, 3)
+        self.assertEqual(context.selected_round, 2)
+        self.assertEqual(context.selected_team, self.team)
+        self.assertEqual(context.submitted_observation_count, 1)
+        self.assertEqual(context.latest_observation.expected_draft_round, "2")
+        self.assertEqual(context.average_rating, Decimal("4"))
+
+    def test_draft_context_is_empty_when_no_submitted_observations_exist(self):
+        context = get_draft_context_for_draft_player(self.draft_player)
+
+        self.assertTrue(context.is_matched)
+        self.assertEqual(context.submitted_observation_count, 0)
+        self.assertIsNone(context.average_rating)
+
+    def test_draft_context_excludes_draft_and_reopened_observations(self):
+        self.submitted_observation(self.coach, rating=5)
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.other_coach,
+            status=OBSERVATION_STATUS_DRAFT,
+            responses={
+                question: 1
+                for question in self.setup_result.question_set.questions.filter(
+                    response_type=RESPONSE_TYPE_RATING_1_5
+                )
+            },
+        )
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.third_coach,
+            status=OBSERVATION_STATUS_REOPENED,
+            responses={
+                question: 1
+                for question in self.setup_result.question_set.questions.filter(
+                    response_type=RESPONSE_TYPE_RATING_1_5
+                )
+            },
+        )
+
+        context = get_draft_context_for_draft_player(self.draft_player)
+
+        self.assertEqual(context.submitted_observation_count, 1)
+        self.assertEqual(context.latest_observation.evaluator_name, self.coach.username)
+
+    def test_multiple_submitted_observations_are_ordered_newest_first(self):
+        older = self.submitted_observation(self.coach, rating=3)
+        newer = self.submitted_observation(self.other_coach, rating=5)
+        Observation.objects.filter(pk=older.pk).update(
+            submitted_at=timezone.now() - timedelta(days=2)
+        )
+        Observation.objects.filter(pk=newer.pk).update(
+            submitted_at=timezone.now() - timedelta(hours=1)
+        )
+
+        context = get_draft_context_for_draft_player(self.draft_player)
+
+        self.assertEqual(context.submitted_observation_count, 2)
+        self.assertEqual(
+            [summary.evaluator_name for summary in context.observations],
+            [self.other_coach.username, self.coach.username],
+        )
+        self.assertEqual(context.average_rating, Decimal("4"))
+
+    def test_draft_context_reports_unmatched_player(self):
+        unmatched = DraftPlayer.objects.create(
+            draft=self.draft,
+            first_name="No",
+            last_name="Match",
+            full_name="No Match",
+        )
+
+        context = get_draft_context_for_draft_player(unmatched)
+
+        self.assertFalse(context.is_matched)
+        self.assertEqual(context.submitted_observation_count, 0)
+
+    def test_ambiguous_player_match_does_not_select_observations(self):
+        Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
+
+        context = get_draft_contexts_for_draft(self.draft)[self.draft_player.id]
+
+        self.assertFalse(context.is_matched)
+        self.assertEqual(context.match_status, "ambiguous")
+        self.assertEqual(context.submitted_observation_count, 0)
diff --git a/analytics/tests/test_evaluation_context.py b/analytics/tests/test_evaluation_context.py
new file mode 100644
index 0000000..58eeab4
--- /dev/null
+++ b/analytics/tests/test_evaluation_context.py
@@ -0,0 +1,161 @@
+from analytics.tests.helpers import (
+    RESPONSE_TYPE_RATING_1_5,
+    AccountRole,
+    EvaluationCycle,
+    Player,
+    TestCase,
+    User,
+    ValidationError,
+    attach_player_to_season,
+    create_assignment,
+    create_coach_assessment_observation,
+    create_season,
+    ensure_default_coach_assessment_setup,
+    set_account_role,
+    submit_observation,
+)
+
+
+class SeasonalEvaluationContextTests(TestCase):
+    def setUp(self):
+        self.coach = User.objects.create_user(
+            username="season-coach", password="testpass"
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        self.player = Player.objects.create(
+            first_name="Season", last_name="Player", division="13U", team_name="Reds"
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        self.other_season = create_season(key="2027-spring", name="2027 Spring")
+        self.membership = attach_player_to_season(
+            self.player, self.season, team_name="Reds", division="13U"
+        )
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
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5
+            )
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
+        assignment = create_assignment(
+            user=self.coach,
+            season_team=self.membership.season_team,
+            assignment_role="head_coach",
+            is_primary=True,
+        )
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
+        other_player = Player.objects.create(
+            first_name="Other", last_name="Player", division="13U"
+        )
+        other_membership = attach_player_to_season(other_player, self.season)
+        cross_season_membership = attach_player_to_season(
+            self.player, self.other_season
+        )
+
+        with self.assertRaisesMessage(
+            ValidationError, "does not belong to this player"
+        ):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=self.coach,
+                player_roster_membership=other_membership,
+            )
+        with self.assertRaisesMessage(
+            ValidationError, "does not belong to this evaluation season"
+        ):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=self.coach,
+                player_roster_membership=cross_season_membership,
+            )
+
+    def test_ambiguous_multiple_memberships_without_primary_are_blocked(self):
+        player = Player.objects.create(
+            first_name="Multi", last_name="Member", division="13U"
+        )
+        attach_player_to_season(
+            player, self.season, team_name="Reds", division="13U", is_primary=False
+        )
+        attach_player_to_season(
+            player, self.season, team_name="Blues", division="13U", is_primary=False
+        )
+
+        with self.assertRaisesMessage(ValidationError, "multiple active memberships"):
+            create_coach_assessment_observation(
+                player=player, evaluation_cycle=self.cycle, evaluator=self.coach
+            )
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
+        from analytics.services.evaluation_review_service import (
+            get_evaluation_review_detail,
+        )
+
+        detail = get_evaluation_review_detail(self.coach, submitted.id)
+
+        self.assertEqual(detail.season_name, "2026 Spring")
+        self.assertEqual(detail.player_team, "Reds")
+        self.assertEqual(detail.player_division, "13U")
diff --git a/analytics/tests/test_evaluation_review.py b/analytics/tests/test_evaluation_review.py
new file mode 100644
index 0000000..77f4749
--- /dev/null
+++ b/analytics/tests/test_evaluation_review.py
@@ -0,0 +1,365 @@
+from analytics.tests.helpers import (
+    EVALUATION_PERSPECTIVE_COACH,
+    EVALUATION_PERSPECTIVE_SELF,
+    OBSERVATION_STATUS_REOPENED,
+    OBSERVATION_STATUS_SUBMITTED,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    ROLE_COACH,
+    AccountRole,
+    EvaluationCycle,
+    Player,
+    TestCase,
+    User,
+    UserPlayerRelationship,
+    attach_player_to_season,
+    create_coach_assessment_observation,
+    create_season,
+    ensure_default_coach_assessment_setup,
+    link_user_to_player,
+    reverse,
+    set_account_role,
+    submit_observation,
+    timezone,
+)
+
+
+class EvaluationReviewViewTests(TestCase):
+    def setUp(self):
+        self.coach = User.objects.create_user(
+            username="coach-review",
+            password="testpass",
+            first_name="Casey",
+            last_name="Coach",
+            email="coach-review@example.com",
+        )
+        self.second_coach = User.objects.create_user(
+            username="second-coach-review",
+            password="testpass",
+            first_name="Sam",
+            last_name="Coach",
+            email="sam-coach@example.com",
+        )
+        self.player_user = User.objects.create_user(
+            username="player-review", password="testpass"
+        )
+        self.parent = User.objects.create_user(
+            username="parent-review", password="testpass"
+        )
+        self.guest = User.objects.create_user(
+            username="guest-review", password="testpass"
+        )
+        self.staff = User.objects.create_user(
+            username="staff-review-phase5", password="testpass", is_staff=True
+        )
+        self.role_staff = User.objects.create_user(
+            username="role-staff-review", password="testpass"
+        )
+        self.role_admin = User.objects.create_user(
+            username="role-admin-review", password="testpass"
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        set_account_role(self.second_coach, AccountRole.COACH)
+        set_account_role(self.player_user, AccountRole.PLAYER)
+        set_account_role(self.parent, AccountRole.PARENT)
+        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
+        set_account_role(self.staff, AccountRole.STAFF)
+        set_account_role(self.role_staff, AccountRole.STAFF)
+        set_account_role(self.role_admin, AccountRole.ADMIN)
+        self.player = Player.objects.create(
+            first_name="Target", last_name="One", division="13U", team_name="Reds"
+        )
+        self.second_player = Player.objects.create(
+            first_name="Target", last_name="Two", division="15U", team_name="Blues"
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        self.second_season = create_season(key="2026-summer", name="2026 Summer")
+        attach_player_to_season(
+            self.player, self.season, team_name="Reds", division="13U"
+        )
+        attach_player_to_season(
+            self.second_player, self.season, team_name="Reds", division="13U"
+        )
+        attach_player_to_season(
+            self.second_player, self.second_season, team_name="Blues", division="15U"
+        )
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+        self.second_cycle = EvaluationCycle.objects.create(
+            name="2026 15U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.second_season,
+        )
+
+    def service_response_payload(self, value=4, note="Good teammate."):
+        payload = {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+        text_question = self.setup_result.question_set.questions.get(
+            response_type=RESPONSE_TYPE_TEXT
+        )
+        payload[text_question] = note
+        return payload
+
+    def submitted_observation(
+        self, player=None, evaluator=None, cycle=None, value=4, note="Good teammate."
+    ):
+        result = create_coach_assessment_observation(
+            player=player or self.player,
+            evaluation_cycle=cycle or self.cycle,
+            evaluator=evaluator or self.coach,
+            responses=self.service_response_payload(value=value, note=note),
+        )
+        return submit_observation(result.observation, actor=evaluator or self.coach)
+
+    def test_coach_can_review_all_submitted_evaluations(self):
+        first = self.submitted_observation(
+            player=self.player, evaluator=self.coach, note="First submitted."
+        )
+        second = self.submitted_observation(
+            player=self.second_player,
+            evaluator=self.second_coach,
+            cycle=self.second_cycle,
+            note="Second submitted.",
+        )
+        link_user_to_player(
+            self.player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+        self_observation = self.submitted_observation(
+            player=self.player, evaluator=self.player_user, note="Self submitted."
+        )
+        self.client.force_login(self.coach)
+
+        response = self.client.get(reverse("analytics:evaluation-review-list"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, self.second_player.display_name)
+        self.assertContains(response, "Casey Coach")
+        self.assertContains(response, "Sam Coach")
+        self.assertContains(response, "Self Evaluation")
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": first.id},
+            ),
+        )
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": second.id},
+            ),
+        )
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": self_observation.id},
+            ),
+        )
+        self.assertNotContains(response, self.coach.email)
+
+    def test_coach_review_access_rules(self):
+        self.submitted_observation()
+        for user in [self.player_user, self.parent, self.guest]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                response = self.client.get(reverse("analytics:evaluation-review-list"))
+                self.assertEqual(response.status_code, 403)
+                self.client.logout()
+
+        for user in [self.coach, self.staff, self.role_staff, self.role_admin]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                response = self.client.get(reverse("analytics:evaluation-review-list"))
+                self.assertEqual(response.status_code, 200)
+                self.client.logout()
+
+    def test_coach_role_does_not_grant_account_operations(self):
+        self.client.force_login(self.coach)
+
+        self.assertEqual(
+            self.client.get(reverse("accounts:operations-dashboard")).status_code, 403
+        )
+
+    def test_coach_review_filters_individually_and_in_combination(self):
+        first = self.submitted_observation(
+            player=self.player, evaluator=self.coach, note="Reds note."
+        )
+        second = self.submitted_observation(
+            player=self.second_player,
+            evaluator=self.second_coach,
+            cycle=self.second_cycle,
+            note="Blues note.",
+        )
+        link_user_to_player(
+            self.player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+        self_observation = self.submitted_observation(
+            player=self.player, evaluator=self.player_user, note="Self note."
+        )
+        today = timezone.localdate().isoformat()
+        self.client.force_login(self.coach)
+
+        cases = [
+            ({"q": "One"}, first, second),
+            ({"player": str(self.player.id)}, first, second),
+            ({"evaluator": str(self.coach.id)}, first, second),
+            ({"evaluator": "second-coach"}, second, first),
+            ({"evaluator_role": ROLE_COACH}, first, None),
+            ({"perspective": EVALUATION_PERSPECTIVE_SELF}, self_observation, first),
+            ({"perspective": EVALUATION_PERSPECTIVE_COACH}, first, self_observation),
+            ({"team": "Reds"}, first, second),
+            ({"division": "15U"}, second, first),
+            ({"cycle": str(self.second_cycle.id)}, second, first),
+            ({"submitted_from": today, "submitted_to": today}, first, None),
+            (
+                {"q": "Target", "team": "Blues", "cycle": str(self.second_cycle.id)},
+                second,
+                first,
+            ),
+        ]
+        for params, included, excluded in cases:
+            with self.subTest(params=params):
+                response = self.client.get(
+                    reverse("analytics:evaluation-review-list"), params
+                )
+                self.assertEqual(response.status_code, 200)
+                self.assertContains(
+                    response,
+                    reverse(
+                        "analytics:evaluation-review-detail",
+                        kwargs={"observation_id": included.id},
+                    ),
+                )
+                if excluded:
+                    self.assertNotContains(
+                        response,
+                        reverse(
+                            "analytics:evaluation-review-detail",
+                            kwargs={"observation_id": excluded.id},
+                        ),
+                    )
+
+    def test_coach_review_excludes_draft_and_reopened_observations(self):
+        submitted = self.submitted_observation(player=self.player, evaluator=self.coach)
+        draft = create_coach_assessment_observation(
+            player=self.second_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.service_response_payload(),
+        ).observation
+        reopened = create_coach_assessment_observation(
+            player=self.second_player,
+            evaluation_cycle=self.second_cycle,
+            evaluator=self.second_coach,
+            responses=self.service_response_payload(),
+        ).observation
+        reopened.status = OBSERVATION_STATUS_REOPENED
+        reopened.save(update_fields=["status", "updated_at"])
+        self.client.force_login(self.coach)
+
+        list_response = self.client.get(reverse("analytics:evaluation-review-list"))
+        draft_detail = self.client.get(
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": draft.id},
+            )
+        )
+        reopened_detail = self.client.get(
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": reopened.id},
+            )
+        )
+
+        self.assertContains(
+            list_response,
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": submitted.id},
+            ),
+        )
+        self.assertNotContains(
+            list_response,
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": draft.id},
+            ),
+        )
+        self.assertNotContains(
+            list_response,
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": reopened.id},
+            ),
+        )
+        self.assertEqual(draft_detail.status_code, 404)
+        self.assertEqual(reopened_detail.status_code, 404)
+
+    def test_coach_review_detail_is_read_only_and_exposes_safe_evaluator_identity(self):
+        observation = self.submitted_observation(note="Review detail note.")
+        self.client.force_login(self.coach)
+
+        response = self.client.get(
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+        post_response = self.client.post(
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": observation.id},
+            ),
+            {"action": "reopen"},
+        )
+        observation.refresh_from_db()
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, "Casey Coach")
+        self.assertContains(response, "Coach")
+        self.assertContains(response, "Review detail note.")
+        self.assertNotContains(response, self.coach.email)
+        self.assertNotContains(response, "Reopen")
+        self.assertEqual(post_response.status_code, 405)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
+
+    def test_staff_review_reopen_remains_separate(self):
+        observation = self.submitted_observation()
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse(
+                "analytics:observation-review-detail",
+                kwargs={"observation_id": observation.id},
+            ),
+            {"action": "reopen"},
+            follow=True,
+        )
+        observation.refresh_from_db()
+
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_REOPENED)
diff --git a/analytics/tests/test_evaluation_submission.py b/analytics/tests/test_evaluation_submission.py
new file mode 100644
index 0000000..c7fcd0d
--- /dev/null
+++ b/analytics/tests/test_evaluation_submission.py
@@ -0,0 +1,465 @@
+from analytics.tests.helpers import (
+    EVALUATION_PERSPECTIVE_PEER,
+    EVALUATION_PERSPECTIVE_SELF,
+    OBSERVATION_STATUS_DRAFT,
+    OBSERVATION_STATUS_SUBMITTED,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    ROLE_COACH,
+    ROLE_GUEST_EVALUATOR,
+    ROLE_PLAYER,
+    AccountRole,
+    Decimal,
+    EvaluationCycle,
+    Observation,
+    Player,
+    TestCase,
+    User,
+    UserPlayerRelationship,
+    attach_player_to_season,
+    create_coach_assessment_observation,
+    create_season,
+    ensure_default_coach_assessment_setup,
+    link_user_to_player,
+    reverse,
+    set_account_role,
+    submit_observation,
+)
+
+
+class EvaluationAccessSubmissionViewTests(TestCase):
+    def setUp(self):
+        self.coach = User.objects.create_user(
+            username="coach-evaluator", password="testpass"
+        )
+        self.player_user = User.objects.create_user(
+            username="player-evaluator", password="testpass"
+        )
+        self.guest = User.objects.create_user(
+            username="guest-evaluator", password="testpass"
+        )
+        self.parent = User.objects.create_user(
+            username="parent-user", password="testpass"
+        )
+        self.staff = User.objects.create_user(
+            username="staff-evaluator", password="testpass", is_staff=True
+        )
+        set_account_role(self.coach, AccountRole.COACH)
+        set_account_role(self.player_user, AccountRole.PLAYER)
+        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
+        set_account_role(self.parent, AccountRole.PARENT)
+        set_account_role(self.staff, AccountRole.STAFF)
+        self.self_player = Player.objects.create(
+            first_name="Self", last_name="Player", division="13U", team_name="Expos"
+        )
+        self.target_player = Player.objects.create(
+            first_name="Target", last_name="Player", division="13U", team_name="Expos"
+        )
+        self.inactive_player = Player.objects.create(
+            first_name="Inactive", last_name="Player", division="13U", is_active=False
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        attach_player_to_season(self.self_player, self.season)
+        attach_player_to_season(self.target_player, self.season)
+        link_user_to_player(
+            self.player_user,
+            self.self_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+
+    def response_payload(self, include_required=True):
+        data = {}
+        for question in self.setup_result.question_set.questions.filter(is_active=True):
+            field_name = f"question_{question.id}"
+            if question.response_type == RESPONSE_TYPE_RATING_1_5 and include_required:
+                data[field_name] = "4"
+            elif question.response_type == RESPONSE_TYPE_TEXT:
+                data[field_name] = "Good teammate."
+        return data
+
+    def service_response_payload(self):
+        return {
+            question: 4
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+
+    def test_evaluation_list_permissions(self):
+        self.assertEqual(
+            self.client.get(reverse("analytics:evaluation-list")).status_code, 302
+        )
+        for user in [self.player_user, self.coach, self.guest, self.staff]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                response = self.client.get(reverse("analytics:evaluation-list"))
+                self.assertEqual(response.status_code, 200)
+                self.assertContains(response, "Evaluations")
+                self.client.logout()
+
+        self.client.force_login(self.parent)
+        self.assertEqual(
+            self.client.get(reverse("analytics:evaluation-list")).status_code, 403
+        )
+
+    def test_evaluation_list_allows_self_and_uses_evaluation_copy(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse("analytics:evaluation-list"), {"q": "Player"}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Evaluate Player")
+        self.assertContains(response, "My submission")
+        self.assertContains(response, "Self Evaluation")
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
+            ),
+        )
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            ),
+        )
+
+    def test_player_can_open_evaluation_form_for_another_player(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            )
+        )
+
+        observation = Observation.objects.get(
+            player=self.target_player, evaluator=self.player_user
+        )
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, f"Evaluate {self.target_player.display_name}")
+        self.assertContains(response, "Submit Evaluation")
+        self.assertContains(response, "Peer Evaluation")
+        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
+        self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
+        self.assertEqual(
+            observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER
+        )
+
+    def test_player_can_evaluate_self_but_not_inactive_player(self):
+        self.client.force_login(self.player_user)
+
+        self_response = self.client.get(
+            reverse(
+                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
+            )
+        )
+        self_observation = Observation.objects.get(
+            player=self.self_player, evaluator=self.player_user
+        )
+        self.assertEqual(self_response.status_code, 200)
+        self.assertContains(self_response, "Self Evaluation")
+        self.assertEqual(
+            self_observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF
+        )
+        self.assertEqual(
+            self.client.get(
+                reverse(
+                    "analytics:evaluation-player",
+                    kwargs={"player_id": self.inactive_player.id},
+                )
+            ).status_code,
+            404,
+        )
+
+    def test_player_can_save_draft_and_resume(self):
+        question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        self.client.force_login(self.player_user)
+
+        response = self.client.post(
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            ),
+            {"action": "save_draft", f"question_{question.id}": "3"},
+        )
+        second_response = self.client.get(
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            )
+        )
+
+        observation = Observation.objects.get(
+            player=self.target_player, evaluator=self.player_user
+        )
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(
+            response["Location"],
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            ),
+        )
+        self.assertEqual(second_response.status_code, 200)
+        self.assertEqual(
+            Observation.objects.filter(
+                player=self.target_player, evaluator=self.player_user
+            ).count(),
+            1,
+        )
+        self.assertEqual(
+            observation.responses.get(question=question).numeric_value, Decimal("3.00")
+        )
+
+    def test_player_can_submit_complete_evaluation(self):
+        self.client.force_login(self.player_user)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+
+        response = self.client.post(
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            ),
+            data,
+        )
+
+        observation = Observation.objects.get(
+            player=self.target_player, evaluator=self.player_user
+        )
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(
+            response["Location"],
+            reverse(
+                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
+            ),
+        )
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
+        self.assertEqual(observation.evaluator_role_key, ROLE_PLAYER)
+        self.assertEqual(
+            observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER
+        )
+
+    def test_player_self_evaluation_draft_resumes_and_submitted_duplicate_redirects(
+        self,
+    ):
+        self.client.force_login(self.player_user)
+        first_response = self.client.get(
+            reverse(
+                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
+            )
+        )
+        second_response = self.client.get(
+            reverse(
+                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
+            )
+        )
+        observation = Observation.objects.get(
+            player=self.self_player, evaluator=self.player_user
+        )
+
+        self.assertEqual(first_response.status_code, 200)
+        self.assertEqual(second_response.status_code, 200)
+        self.assertEqual(
+            observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF
+        )
+        self.assertEqual(
+            Observation.objects.filter(
+                player=self.self_player, evaluator=self.player_user
+            ).count(),
+            1,
+        )
+
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+        self.client.post(
+            reverse(
+                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
+            ),
+            data,
+        )
+        response = self.client.get(
+            reverse(
+                "analytics:evaluation-player", kwargs={"player_id": self.self_player.id}
+            )
+        )
+        observation.refresh_from_db()
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(
+            response["Location"],
+            reverse(
+                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
+            ),
+        )
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
+
+    def test_submitted_evaluation_detail_is_private_to_evaluator_and_staff(self):
+        result = create_coach_assessment_observation(
+            player=self.target_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.player_user,
+            responses=self.service_response_payload(),
+        )
+        observation = submit_observation(result.observation, actor=self.player_user)
+        detail_url = reverse(
+            "analytics:assessment-detail", kwargs={"observation_id": observation.id}
+        )
+
+        self.client.force_login(self.player_user)
+        self.assertEqual(self.client.get(detail_url).status_code, 200)
+
+        for user in [self.coach, self.guest]:
+            with self.subTest(user=user.username):
+                self.client.force_login(user)
+                self.assertEqual(self.client.get(detail_url).status_code, 403)
+
+        self.client.force_login(self.staff)
+        self.assertEqual(self.client.get(detail_url).status_code, 200)
+
+    def test_player_cannot_view_another_evaluators_submitted_detail(self):
+        other_player_user = User.objects.create_user(
+            username="other-player-evaluator", password="testpass"
+        )
+        set_account_role(other_player_user, AccountRole.PLAYER)
+        result = create_coach_assessment_observation(
+            player=self.target_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.service_response_payload(),
+        )
+        observation = submit_observation(result.observation, actor=self.coach)
+
+        self.client.force_login(other_player_user)
+        response = self.client.get(
+            reverse(
+                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
+            )
+        )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_missing_required_responses_are_blocked(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.post(
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            ),
+            {"action": "submit"},
+        )
+
+        observation = Observation.objects.get(
+            player=self.target_player, evaluator=self.player_user
+        )
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_DRAFT)
+        self.assertContains(response, "This field is required")
+
+    def test_submitted_evaluation_cannot_be_duplicated(self):
+        self.client.force_login(self.player_user)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+        self.client.post(
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            ),
+            data,
+        )
+        observation = Observation.objects.get(
+            player=self.target_player, evaluator=self.player_user
+        )
+
+        response = self.client.get(
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            )
+        )
+
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(
+            response["Location"],
+            reverse(
+                "analytics:assessment-detail", kwargs={"observation_id": observation.id}
+            ),
+        )
+        self.assertEqual(
+            Observation.objects.filter(
+                player=self.target_player, evaluator=self.player_user
+            ).count(),
+            1,
+        )
+
+    def test_evaluation_list_submitted_copy_is_own_submission(self):
+        result = create_coach_assessment_observation(
+            player=self.target_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.player_user,
+            responses=self.service_response_payload(),
+        )
+        submit_observation(result.observation, actor=self.player_user)
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse("analytics:evaluation-list"), {"q": "Target"}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "View My Submission")
+        self.assertNotContains(response, ">View<")
+        self.assertNotContains(response, "evaluations about me")
+
+    def test_evaluation_list_uses_current_cycle_without_cycle_selector(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse("analytics:evaluation-list"), {"cycle": "999"}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.cycle.name)
+        self.assertNotContains(response, 'name="cycle"')
+
+    def test_coach_and_guest_role_snapshots_continue_to_work(self):
+        for user, expected_role in [
+            (self.coach, ROLE_COACH),
+            (self.guest, ROLE_GUEST_EVALUATOR),
+        ]:
+            with self.subTest(user=user.username):
+                target = Player.objects.create(
+                    first_name=user.username, last_name="Target", division="13U"
+                )
+                attach_player_to_season(target, self.season)
+                self.client.force_login(user)
+                response = self.client.get(
+                    reverse(
+                        "analytics:evaluation-player", kwargs={"player_id": target.id}
+                    )
+                )
+
+                observation = Observation.objects.get(player=target, evaluator=user)
+                self.assertEqual(response.status_code, 200)
+                self.assertEqual(observation.evaluator_role_key, expected_role)
+                self.client.logout()
diff --git a/analytics/tests/test_import_views.py b/analytics/tests/test_import_views.py
new file mode 100644
index 0000000..9382cee
--- /dev/null
+++ b/analytics/tests/test_import_views.py
@@ -0,0 +1,334 @@
+from analytics.tests.helpers import (
+    SOURCE_MEMBER_LIST,
+    Player,
+    PlayerImportBatch,
+    PlayerSourceRow,
+    SimpleUploadedFile,
+    TestCase,
+    User,
+    create_season,
+    reverse,
+)
+
+
+class AnalyticsImportViewTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.user = User.objects.create_user(username="user", password="testpass")
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+
+    def upload(self):
+        return SimpleUploadedFile(
+            "member list for 13u house.csv",
+            b"First,Last,Gender,Division,Team\nEugene,Lin,M,13U,Expos\n",
+            content_type="text/csv",
+        )
+
+    def test_import_views_require_staff(self):
+        response = self.client.get(reverse("analytics:import-list"))
+        self.assertEqual(response.status_code, 302)
+
+        self.client.force_login(self.user)
+        response = self.client.get(reverse("analytics:import-list"))
+        self.assertEqual(response.status_code, 403)
+
+    def test_staff_can_open_import_list(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("analytics:import-list"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player Imports")
+
+    def test_upload_redirects_to_preview(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("analytics:import-new"),
+            {
+                "season": str(self.season.pk),
+                "source": SOURCE_MEMBER_LIST,
+                "csv_file": self.upload(),
+            },
+        )
+
+        self.assertEqual(response.status_code, 302)
+        batch = PlayerImportBatch.objects.get()
+        self.assertEqual(
+            response["Location"],
+            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
+        )
+
+    def test_upload_can_enable_account_provisioning_options(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.post(
+            reverse("analytics:import-new"),
+            {
+                "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
+                "csv_file": SimpleUploadedFile(
+                    "member.csv",
+                    b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n",
+                    content_type="text/csv",
+                ),
+                "provision_player_accounts": "on",
+            },
+        )
+
+        batch = PlayerImportBatch.objects.get()
+        self.assertEqual(response.status_code, 302)
+        self.assertTrue(batch.mapping_config["_provision_player_accounts"])
+        self.assertTrue(batch.mapping_config["_activate_player_accounts"])
+
+    def test_preview_can_map_account_email_and_preserves_provisioning_options(self):
+        self.client.force_login(self.staff)
+        batch = PlayerImportBatch.objects.create(
+            source=SOURCE_MEMBER_LIST,
+            original_filename="member.csv",
+            uploaded_by=self.staff,
+            season=self.season,
+            mapping_config={
+                "_provision_player_accounts": True,
+                "_activate_player_accounts": False,
+            },
+            preview_snapshot={
+                "parsed_csv": {
+                    "file_name": "member.csv",
+                    "headers": ["First", "Last", "DOB", "Email", "Division", "Team"],
+                    "normalized_headers": {
+                        "first": "First",
+                        "last": "Last",
+                        "dob": "DOB",
+                        "email": "Email",
+                        "division": "Division",
+                        "team": "Team",
+                    },
+                    "rows": [
+                        {
+                            "row_number": 2,
+                            "original_row": {
+                                "First": "Eugene",
+                                "Last": "Lin",
+                                "DOB": "2012-05-01",
+                                "Email": "eugene@example.com",
+                                "Division": "13U",
+                                "Team": "Expos",
+                            },
+                            "cleaned_row": {
+                                "First": "Eugene",
+                                "Last": "Lin",
+                                "DOB": "2012-05-01",
+                                "Email": "eugene@example.com",
+                                "Division": "13U",
+                                "Team": "Expos",
+                            },
+                        }
+                    ],
+                }
+            },
+        )
+
+        response = self.client.post(
+            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
+            {
+                "first_name": "First",
+                "last_name": "Last",
+                "birthdate": "DOB",
+                "account_email": "Email",
+                "division": "Division",
+                "team_name": "Team",
+            },
+        )
+
+        batch.refresh_from_db()
+        self.assertEqual(response.status_code, 302)
+        self.assertTrue(batch.mapping_config["_provision_player_accounts"])
+        self.assertEqual(batch.mapping_config["account_email"], "Email")
+        self.assertTrue(
+            batch.preview_snapshot["preview"]["account_provisioning"]["enabled"]
+        )
+        self.assertTrue(
+            batch.preview_snapshot["preview"]["account_provisioning"]["activate_users"]
+        )
+
+    def test_preview_refresh_and_confirm_import(self):
+        self.client.force_login(self.staff)
+        batch = PlayerImportBatch.objects.create(
+            source=SOURCE_MEMBER_LIST,
+            original_filename="member.csv",
+            uploaded_by=self.staff,
+            season=self.season,
+            preview_snapshot={
+                "parsed_csv": {
+                    "file_name": "member.csv",
+                    "headers": ["First", "Last", "Division", "Team"],
+                    "normalized_headers": {
+                        "first": "First",
+                        "last": "Last",
+                        "division": "Division",
+                        "team": "Team",
+                    },
+                    "rows": [
+                        {
+                            "row_number": 2,
+                            "original_row": {
+                                "First": "Eugene",
+                                "Last": "Lin",
+                                "Division": "13U",
+                                "Team": "Expos",
+                            },
+                            "cleaned_row": {
+                                "First": "Eugene",
+                                "Last": "Lin",
+                                "Division": "13U",
+                                "Team": "Expos",
+                            },
+                        }
+                    ],
+                }
+            },
+        )
+
+        preview_response = self.client.post(
+            reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
+            {
+                "first_name": "First",
+                "last_name": "Last",
+                "division": "Division",
+                "team_name": "Team",
+            },
+        )
+        self.assertEqual(preview_response.status_code, 302)
+
+        confirm_response = self.client.post(
+            reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True
+        )
+
+        self.assertEqual(confirm_response.status_code, 200)
+        self.assertTrue(
+            Player.objects.filter(first_name="Eugene", last_name="Lin").exists()
+        )
+        self.assertContains(confirm_response, "Import Result")
+
+    def test_import_detail_shows_safe_account_provisioning_summary(self):
+        self.client.force_login(self.staff)
+        response = self.client.post(
+            reverse("analytics:import-new"),
+            {
+                "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
+                "csv_file": SimpleUploadedFile(
+                    "member.csv",
+                    b"First,Last,DOB,Division,Team\nEugene,Lin,2012-05-01,13U,Expos\n",
+                    content_type="text/csv",
+                ),
+                "provision_player_accounts": "on",
+            },
+        )
+        batch = PlayerImportBatch.objects.get()
+
+        response = self.client.post(
+            reverse("analytics:import-confirm", kwargs={"pk": batch.pk}), follow=True
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Account provisioning")
+        self.assertContains(response, "Users Created")
+        self.assertNotContains(response, "20120501")
+
+    def test_conflict_page_displays_review_rows(self):
+        self.client.force_login(self.staff)
+        Player.objects.create(
+            first_name="Eugene",
+            last_name="Lin",
+            birthdate="2012-05-01",
+            preferred_name="Old",
+        )
+        upload_response = self.client.post(
+            reverse("analytics:import-new"),
+            {
+                "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
+                "csv_file": SimpleUploadedFile(
+                    "member.csv",
+                    b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n",
+                    content_type="text/csv",
+                ),
+            },
+        )
+        batch = PlayerImportBatch.objects.get()
+
+        response = self.client.get(
+            reverse("analytics:import-conflicts", kwargs={"pk": batch.pk})
+        )
+
+        self.assertEqual(upload_response.status_code, 302)
+        self.assertContains(response, "Row 2")
+        self.assertContains(response, "preferred_name")
+
+    def test_preview_routes_review_rows_through_conflict_review(self):
+        self.client.force_login(self.staff)
+        Player.objects.create(
+            first_name="Eugene",
+            last_name="Lin",
+            birthdate="2012-05-01",
+            preferred_name="Old",
+        )
+        self.client.post(
+            reverse("analytics:import-new"),
+            {
+                "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
+                "csv_file": SimpleUploadedFile(
+                    "member.csv",
+                    b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n",
+                    content_type="text/csv",
+                ),
+            },
+        )
+        batch = PlayerImportBatch.objects.get()
+
+        response = self.client.get(
+            reverse("analytics:import-preview", kwargs={"pk": batch.pk})
+        )
+
+        self.assertContains(response, "Review Rows")
+        self.assertNotContains(response, "Confirm Import")
+
+    def test_conflict_page_can_commit_ambiguous_row_to_selected_candidate(self):
+        self.client.force_login(self.staff)
+        Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
+        selected = Player.objects.create(
+            first_name="Eugene", last_name="Lin", birth_year=2012, division="13U"
+        )
+        self.client.post(
+            reverse("analytics:import-new"),
+            {
+                "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
+                "csv_file": SimpleUploadedFile(
+                    "member.csv",
+                    b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n",
+                    content_type="text/csv",
+                ),
+            },
+        )
+        batch = PlayerImportBatch.objects.get()
+
+        response = self.client.post(
+            reverse("analytics:import-confirm", kwargs={"pk": batch.pk}),
+            {"row_2_action": "use_candidate", "row_2_candidate": str(selected.id)},
+            follow=True,
+        )
+
+        selected.refresh_from_db()
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(selected.team_name, "Expos")
+        self.assertEqual(PlayerSourceRow.objects.get().player, selected)
diff --git a/analytics/tests/test_my_evaluations.py b/analytics/tests/test_my_evaluations.py
new file mode 100644
index 0000000..7269006
--- /dev/null
+++ b/analytics/tests/test_my_evaluations.py
@@ -0,0 +1,572 @@
+from analytics.tests.helpers import (
+    OBSERVATION_STATUS_REOPENED,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    AccountRole,
+    Decimal,
+    EvaluationCycle,
+    ObservationResponse,
+    Player,
+    TestCase,
+    User,
+    UserPlayerRelationship,
+    activate_link,
+    attach_player_to_season,
+    create_coach_assessment_observation,
+    create_season,
+    deactivate_link,
+    ensure_default_coach_assessment_setup,
+    get_my_evaluation_detail,
+    get_my_evaluations,
+    link_user_to_player,
+    reverse,
+    set_account_role,
+    submit_observation,
+)
+
+
+class MyEvaluationsViewTests(TestCase):
+    def setUp(self):
+        self.player_user = User.objects.create_user(
+            username="linked-player-user",
+            password="testpass",
+            first_name="Linked",
+            last_name="User",
+            email="linked@example.com",
+        )
+        self.other_player_user = User.objects.create_user(
+            username="other-linked-player", password="testpass"
+        )
+        self.coach = User.objects.create_user(
+            username="coach-private-name",
+            password="testpass",
+            first_name="Coach",
+            last_name="Private",
+            email="coach-private@example.com",
+        )
+        self.guest = User.objects.create_user(
+            username="guest-evaluator-private", password="testpass"
+        )
+        self.parent = User.objects.create_user(
+            username="parent-no-self", password="testpass"
+        )
+        self.staff = User.objects.create_user(
+            username="staff-review", password="testpass", is_staff=True
+        )
+        set_account_role(self.player_user, AccountRole.PLAYER)
+        set_account_role(self.other_player_user, AccountRole.PLAYER)
+        set_account_role(self.coach, AccountRole.COACH)
+        set_account_role(self.guest, AccountRole.GUEST_EVALUATOR)
+        set_account_role(self.parent, AccountRole.PARENT)
+        set_account_role(self.staff, AccountRole.STAFF)
+        self.player = Player.objects.create(
+            first_name="Linked", last_name="Player", division="13U"
+        )
+        self.second_player = Player.objects.create(
+            first_name="Second", last_name="Player", division="15U"
+        )
+        self.other_player = Player.objects.create(
+            first_name="Other", last_name="Player", division="13U"
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(
+            self.second_player, self.season, team_name="Mounties", division="15U"
+        )
+        attach_player_to_season(self.other_player, self.season)
+        link_user_to_player(
+            self.player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+        link_user_to_player(
+            self.other_player_user,
+            self.other_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+
+    def service_response_payload(self, value=4, note="Good teammate."):
+        payload = {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+        text_question = self.setup_result.question_set.questions.get(
+            response_type=RESPONSE_TYPE_TEXT
+        )
+        payload[text_question] = note
+        return payload
+
+    def submitted_observation(
+        self, player=None, evaluator=None, value=4, note="Good teammate."
+    ):
+        result = create_coach_assessment_observation(
+            player=player or self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=evaluator or self.coach,
+            responses=self.service_response_payload(value=value, note=note),
+        )
+        return submit_observation(result.observation, actor=evaluator or self.coach)
+
+    def test_my_evaluations_requires_login_and_handles_no_self_link(self):
+        self.assertEqual(
+            self.client.get(reverse("analytics:my-evaluations")).status_code, 302
+        )
+
+        self.client.force_login(self.parent)
+        response = self.client.get(reverse("analytics:my-evaluations"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "No player record is linked to your account.")
+
+    def test_player_can_view_submitted_evaluations_about_self(self):
+        observation = self.submitted_observation(note="Shows leadership.")
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:my-evaluations"))
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, self.cycle.name)
+        self.assertContains(response, "Coach")
+        self.assertContains(response, "Coach Evaluation")
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            ),
+        )
+
+    def test_my_evaluation_detail_hides_evaluator_identity_and_shows_feedback(self):
+        observation = self.submitted_observation(value=5, note="Strong instincts.")
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, "Coach Evaluation")
+        self.assertContains(response, "Evaluator Role")
+        self.assertContains(response, "Coach")
+        self.assertContains(response, self.cycle.name)
+        self.assertContains(response, "Strong instincts.")
+        self.assertContains(response, "5")
+        self.assertNotContains(response, self.coach.username)
+        self.assertNotContains(response, self.coach.email)
+        self.assertNotContains(response, self.coach.get_full_name())
+
+        players, summaries = get_my_evaluations(self.player_user)
+        detail = get_my_evaluation_detail(self.player_user, observation.id)
+        self.assertEqual(players, [self.player])
+        self.assertEqual(summaries[0].observation_id, observation.id)
+        self.assertFalse(hasattr(summaries[0], "observation"))
+        self.assertEqual(detail.observation_id, observation.id)
+        self.assertFalse(hasattr(detail, "observation"))
+
+    def test_my_evaluations_show_self_label_without_external_identity(self):
+        self_observation = self.submitted_observation(
+            player=self.player, evaluator=self.player_user, note="My reflection."
+        )
+        self.client.force_login(self.player_user)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        detail_response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": self_observation.id},
+            )
+        )
+
+        self.assertContains(list_response, "Self Evaluation")
+        self.assertContains(detail_response, "Self Evaluation")
+        self.assertContains(detail_response, "My reflection.")
+
+    def test_nonexistent_my_evaluation_detail_returns_404(self):
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse("analytics:my-evaluation-detail", kwargs={"observation_id": 999999})
+        )
+
+        self.assertEqual(response.status_code, 404)
+
+    def test_player_cannot_view_another_players_evaluation_by_url(self):
+        observation = self.submitted_observation(
+            player=self.other_player, evaluator=self.coach
+        )
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+
+        self.assertEqual(response.status_code, 403)
+
+    def test_draft_and_reopened_observations_are_not_player_results(self):
+        draft = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.service_response_payload(),
+        ).observation
+        reopened = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.guest,
+            responses=self.service_response_payload(),
+        ).observation
+        reopened.status = OBSERVATION_STATUS_REOPENED
+        reopened.save(update_fields=["status", "updated_at"])
+        self.client.force_login(self.player_user)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        draft_detail = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail", kwargs={"observation_id": draft.id}
+            )
+        )
+        reopened_detail = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail", kwargs={"observation_id": reopened.id}
+            )
+        )
+
+        self.assertNotContains(
+            list_response,
+            reverse(
+                "analytics:my-evaluation-detail", kwargs={"observation_id": draft.id}
+            ),
+        )
+        self.assertNotContains(
+            list_response,
+            reverse(
+                "analytics:my-evaluation-detail", kwargs={"observation_id": reopened.id}
+            ),
+        )
+        self.assertEqual(draft_detail.status_code, 403)
+        self.assertEqual(reopened_detail.status_code, 403)
+
+    def test_multiple_self_links_are_listed_and_player_specific_route_enforces_ownership(
+        self,
+    ):
+        link_user_to_player(
+            self.player_user,
+            self.second_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+        inactive_player = Player.objects.create(
+            first_name="Inactive", last_name="Linked"
+        )
+        inactive_link = link_user_to_player(
+            self.player_user,
+            inactive_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+        deactivate_link(inactive_link)
+        first_observation = self.submitted_observation(
+            player=self.player, evaluator=self.coach
+        )
+        second_observation = self.submitted_observation(
+            player=self.second_player, evaluator=self.guest
+        )
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(reverse("analytics:my-evaluations"))
+        player_response = self.client.get(
+            reverse(
+                "analytics:my-evaluations-player",
+                kwargs={"player_id": self.second_player.id},
+            )
+        )
+        first_detail = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": first_observation.id},
+            )
+        )
+        second_detail = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": second_observation.id},
+            )
+        )
+        forbidden_response = self.client.get(
+            reverse(
+                "analytics:my-evaluations-player",
+                kwargs={"player_id": self.other_player.id},
+            )
+        )
+
+        self.assertContains(response, self.player.display_name)
+        self.assertContains(response, self.second_player.display_name)
+        self.assertNotContains(response, inactive_player.display_name)
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:my-evaluations-player", kwargs={"player_id": self.player.id}
+            ),
+        )
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:my-evaluations-player",
+                kwargs={"player_id": self.second_player.id},
+            ),
+        )
+        self.assertContains(
+            response,
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": first_observation.id},
+            ),
+        )
+        self.assertContains(player_response, self.second_player.display_name)
+        self.assertContains(
+            player_response,
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": second_observation.id},
+            ),
+        )
+        self.assertNotContains(
+            player_response,
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": first_observation.id},
+            ),
+        )
+        self.assertEqual(first_detail.status_code, 200)
+        self.assertEqual(second_detail.status_code, 200)
+        self.assertEqual(forbidden_response.status_code, 403)
+
+    def test_coach_without_self_link_cannot_view_player_result_detail(self):
+        observation = self.submitted_observation()
+        self.client.force_login(self.coach)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        detail_response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+
+        self.assertContains(
+            list_response, "No player record is linked to your account."
+        )
+        self.assertEqual(detail_response.status_code, 403)
+
+        self.client.force_login(self.parent)
+        parent_detail_response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+        self.assertEqual(parent_detail_response.status_code, 403)
+
+    def test_inactive_self_link_removes_my_evaluations_access(self):
+        observation = self.submitted_observation()
+        link = self.player_user.player_links.get(
+            player=self.player, relationship=UserPlayerRelationship.SELF
+        )
+        deactivate_link(link)
+        self.client.force_login(self.player_user)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        detail_response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+        profile_response = self.client.get(reverse("accounts:profile"))
+
+        self.assertContains(
+            list_response, "No player record is linked to your account."
+        )
+        self.assertNotContains(
+            list_response,
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            ),
+        )
+        self.assertEqual(detail_response.status_code, 403)
+        self.assertNotContains(profile_response, reverse("analytics:my-evaluations"))
+
+        activate_link(link)
+        restored_list_response = self.client.get(reverse("analytics:my-evaluations"))
+        restored_detail_response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+        restored_profile_response = self.client.get(reverse("accounts:profile"))
+        self.assertContains(
+            restored_list_response,
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            ),
+        )
+        self.assertEqual(restored_detail_response.status_code, 200)
+        self.assertContains(
+            restored_profile_response, reverse("analytics:my-evaluations")
+        )
+
+    def test_inactive_player_is_not_available_in_my_evaluations(self):
+        observation = self.submitted_observation()
+        self.player.is_active = False
+        self.player.save(update_fields=["is_active", "updated_at"])
+        self.client.force_login(self.player_user)
+
+        list_response = self.client.get(reverse("analytics:my-evaluations"))
+        player_response = self.client.get(
+            reverse(
+                "analytics:my-evaluations-player", kwargs={"player_id": self.player.id}
+            )
+        )
+        detail_response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+        profile_response = self.client.get(reverse("accounts:profile"))
+
+        self.assertContains(
+            list_response, "No player record is linked to your account."
+        )
+        self.assertEqual(player_response.status_code, 403)
+        self.assertEqual(detail_response.status_code, 403)
+        self.assertNotContains(profile_response, reverse("analytics:my-evaluations"))
+
+    def test_staff_with_self_link_receives_player_safe_my_evaluation_output(self):
+        staff_player = Player.objects.create(first_name="Staff", last_name="Player")
+        attach_player_to_season(staff_player, self.season)
+        link_user_to_player(
+            self.staff,
+            staff_player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+        observation = self.submitted_observation(
+            player=staff_player,
+            evaluator=self.coach,
+            note="Private staff-linked result.",
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Private staff-linked result.")
+        self.assertContains(response, "Coach")
+        self.assertNotContains(response, self.coach.username)
+        self.assertNotContains(response, self.coach.email)
+        self.assertNotContains(response, self.coach.get_full_name())
+
+    def test_my_evaluation_responses_follow_question_display_order(self):
+        question_set = self.setup_result.question_set
+        first_question = question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        second_question = question_set.questions.filter(
+            response_type=RESPONSE_TYPE_TEXT
+        ).first()
+        first_question.display_order = 20
+        first_question.save(update_fields=["display_order", "updated_at"])
+        second_question.display_order = 10
+        second_question.prompt = "Appears before the rating"
+        second_question.save(update_fields=["display_order", "prompt", "updated_at"])
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=[
+                {"question": first_question, "value": 4},
+                {"question": second_question, "value": "Ordered note."},
+            ],
+        ).observation
+        for required_question in question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5,
+            is_required=True,
+            is_active=True,
+        ).exclude(pk=first_question.pk):
+            ObservationResponse.objects.create(
+                observation=observation,
+                question=required_question,
+                response_type=required_question.response_type,
+                numeric_value=Decimal("3"),
+            )
+        observation = submit_observation(observation, actor=self.coach)
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+
+        self.assertEqual(response.status_code, 200)
+        content = response.content.decode()
+        self.assertLess(
+            content.index("Appears before the rating"),
+            content.index(first_question.prompt),
+        )
+
+    def test_staff_review_and_submission_routes_still_work(self):
+        observation = self.submitted_observation()
+        self.client.force_login(self.staff)
+
+        self.assertEqual(
+            self.client.get(reverse("analytics:observation-review-list")).status_code,
+            200,
+        )
+        self.assertEqual(
+            self.client.get(
+                reverse(
+                    "analytics:observation-review-detail",
+                    kwargs={"observation_id": observation.id},
+                )
+            ).status_code,
+            200,
+        )
+
+        self.client.force_login(self.player_user)
+        self.assertEqual(
+            self.client.get(reverse("analytics:evaluation-list")).status_code, 200
+        )
diff --git a/analytics/tests/test_observation_foundation.py b/analytics/tests/test_observation_foundation.py
new file mode 100644
index 0000000..280946c
--- /dev/null
+++ b/analytics/tests/test_observation_foundation.py
@@ -0,0 +1,686 @@
+from analytics.tests.helpers import (
+    COACH_ASSESSMENT_RUBRIC,
+    DEFAULT_COACH_ASSESSMENT_QUESTIONS,
+    DEFAULT_EVALUATOR_ROLES,
+    DEFAULT_OBSERVATION_SOURCES,
+    EVALUATION_PERSPECTIVE_COACH,
+    EVALUATION_PERSPECTIVE_GUEST,
+    EVALUATION_PERSPECTIVE_PEER,
+    EVALUATION_PERSPECTIVE_SELF,
+    EVALUATION_PERSPECTIVE_STAFF,
+    OBSERVATION_STATUS_SUBMITTED,
+    OBSERVATION_TYPE_COACH_ASSESSMENT,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    ROLE_ADMIN,
+    ROLE_COACH,
+    ROLE_GUEST_EVALUATOR,
+    ROLE_PLAYER,
+    ROLE_STAFF,
+    SOURCE_COACH,
+    AccountRole,
+    Decimal,
+    EvaluationCycle,
+    EvaluatorRole,
+    IntegrityError,
+    Observation,
+    ObservationQuestion,
+    ObservationQuestionSet,
+    ObservationResponse,
+    ObservationSource,
+    ObservationType,
+    Player,
+    TestCase,
+    User,
+    UserPlayerRelationship,
+    ValidationError,
+    admin,
+    attach_player_to_season,
+    can_evaluate_player,
+    can_submit_evaluation,
+    can_view_own_evaluation_draft,
+    create_coach_assessment_observation,
+    create_observation,
+    create_season,
+    deactivate_link,
+    default_coach_assessment_question_set,
+    ensure_default_coach_assessment_setup,
+    evaluation_perspective_for_user,
+    evaluator_role_for_user,
+    get_active_questions,
+    get_observation_detail,
+    get_question_set_for_cycle,
+    link_user_to_player,
+    save_observation_responses,
+    set_account_role,
+    submit_observation,
+    transaction,
+    validate_required_responses,
+)
+
+
+class AnalyticsObservationFoundationTests(TestCase):
+    def setUp(self):
+        self.evaluator = User.objects.create_user(username="coach", password="testpass")
+        self.other_evaluator = User.objects.create_user(
+            username="othercoach", password="testpass"
+        )
+        self.player = Player.objects.create(
+            first_name="Eugene", last_name="Lin", division="13U", team_name="Expos"
+        )
+        self.other_player = Player.objects.create(
+            first_name="Alex", last_name="Chen", division="13U", team_name="Expos"
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        self.player_membership = attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.other_player, self.season)
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.role = EvaluatorRole.objects.get(key=ROLE_COACH)
+        self.source = ObservationSource.objects.get(key=SOURCE_COACH)
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+
+    def required_response_payload(self):
+        return {
+            question: 4
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+                is_active=True,
+            )
+        }
+
+    def test_default_setup_creates_coach_assessment_configuration(self):
+        self.assertTrue(
+            ObservationType.objects.filter(
+                key=OBSERVATION_TYPE_COACH_ASSESSMENT
+            ).exists()
+        )
+        self.assertEqual(
+            ObservationSource.objects.count(), len(DEFAULT_OBSERVATION_SOURCES)
+        )
+        self.assertEqual(EvaluatorRole.objects.count(), len(DEFAULT_EVALUATOR_ROLES))
+        self.assertEqual(self.setup_result.question_set.rubric, COACH_ASSESSMENT_RUBRIC)
+        self.assertEqual(
+            self.setup_result.question_set.questions.count(),
+            len(DEFAULT_COACH_ASSESSMENT_QUESTIONS),
+        )
+        self.assertEqual(
+            self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_TEXT
+            ).count(),
+            1,
+        )
+        self.assertEqual(
+            self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5
+            ).count(),
+            len(DEFAULT_COACH_ASSESSMENT_QUESTIONS) - 1,
+        )
+
+    def test_default_setup_is_idempotent(self):
+        first_question_count = ObservationQuestion.objects.count()
+
+        second_result = ensure_default_coach_assessment_setup()
+
+        self.assertEqual(ObservationQuestion.objects.count(), first_question_count)
+        self.assertEqual(second_result.questions_created, 0)
+
+    def test_default_setup_does_not_overwrite_existing_questions(self):
+        question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        question.prompt = "Edited prompt"
+        question.display_order = 99
+        question.is_required = False
+        question.save()
+
+        ensure_default_coach_assessment_setup()
+
+        question.refresh_from_db()
+        self.assertEqual(question.prompt, "Edited prompt")
+        self.assertEqual(question.display_order, 99)
+        self.assertFalse(question.is_required)
+
+    def test_cycle_slug_generation_creates_unique_slugs(self):
+        second_cycle = EvaluationCycle.objects.create(
+            name=self.cycle.name, cycle_type="Coach Assessment"
+        )
+
+        self.assertEqual(self.cycle.slug, "2026-13u-coach-assessment")
+        self.assertEqual(second_cycle.slug, "2026-13u-coach-assessment-2")
+
+    def test_question_set_version_is_unique_per_observation_type(self):
+        with self.assertRaises(IntegrityError):
+            with transaction.atomic():
+                ObservationQuestionSet.objects.create(
+                    observation_type=self.setup_result.observation_type,
+                    name="Duplicate",
+                    version=1,
+                )
+
+    def test_question_key_is_unique_per_question_set(self):
+        first_question = self.setup_result.question_set.questions.first()
+
+        with self.assertRaises(IntegrityError):
+            with transaction.atomic():
+                ObservationQuestion.objects.create(
+                    question_set=self.setup_result.question_set,
+                    key=first_question.key,
+                    prompt="Duplicate",
+                    response_type=RESPONSE_TYPE_RATING_1_5,
+                )
+
+    def test_get_active_questions_and_cycle_question_set(self):
+        questions = list(get_active_questions(self.setup_result.question_set))
+
+        self.assertEqual(questions[0].display_order, 1)
+        self.assertEqual(
+            get_question_set_for_cycle(self.cycle), self.setup_result.question_set
+        )
+        fallback_cycle = EvaluationCycle.objects.create(
+            name="Fallback Cycle", cycle_type="Coach Assessment"
+        )
+        self.assertEqual(
+            get_question_set_for_cycle(fallback_cycle), self.setup_result.question_set
+        )
+
+    def test_cycle_rejects_non_coach_assessment_question_set(self):
+        other_type = ObservationType.objects.create(key="tryout", name="Tryout")
+        other_question_set = ObservationQuestionSet.objects.create(
+            observation_type=other_type, name="Tryout", version=1
+        )
+
+        with self.assertRaises(ValidationError):
+            EvaluationCycle.objects.create(
+                name="Invalid Cycle",
+                cycle_type="Coach Assessment",
+                coach_assessment_question_set=other_question_set,
+            )
+
+    def test_create_coach_assessment_references_players_player_and_snapshots_role(self):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+            evaluator_role=self.role,
+            source=self.source,
+        )
+
+        observation = result.observation
+        self.assertEqual(observation.player, self.player)
+        self.assertEqual(observation.evaluator_role_key, ROLE_COACH)
+        self.assertEqual(observation.evaluator_role_name, "Coach")
+        self.assertEqual(
+            observation.observation_type_key, OBSERVATION_TYPE_COACH_ASSESSMENT
+        )
+
+    def test_evaluation_submission_permissions_by_role(self):
+        anonymous = None
+        coach = User.objects.create_user(username="rolecoach", password="testpass")
+        player_user = User.objects.create_user(
+            username="roleplayer", password="testpass"
+        )
+        staff_user = User.objects.create_user(
+            username="rolestaff", password="testpass", is_staff=True
+        )
+        guest = User.objects.create_user(username="roleguest", password="testpass")
+        parent = User.objects.create_user(username="roleparent", password="testpass")
+        set_account_role(coach, AccountRole.COACH)
+        set_account_role(player_user, AccountRole.PLAYER)
+        set_account_role(staff_user, AccountRole.STAFF)
+        set_account_role(guest, AccountRole.GUEST_EVALUATOR)
+        set_account_role(parent, AccountRole.PARENT)
+
+        self.assertFalse(can_submit_evaluation(anonymous))
+        self.assertTrue(can_submit_evaluation(coach))
+        self.assertTrue(can_submit_evaluation(player_user))
+        self.assertTrue(can_submit_evaluation(staff_user))
+        self.assertTrue(can_submit_evaluation(guest))
+        self.assertFalse(can_submit_evaluation(parent))
+
+    def test_self_evaluation_is_allowed_with_active_self_link_only(self):
+        player_user = User.objects.create_user(
+            username="selflinked", password="testpass"
+        )
+        set_account_role(player_user, AccountRole.PLAYER)
+        link = link_user_to_player(
+            player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+
+        self.assertTrue(can_evaluate_player(player_user, self.player))
+        self.assertTrue(can_evaluate_player(player_user, self.other_player))
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=player_user,
+        )
+        self.assertEqual(
+            result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF
+        )
+
+        deactivate_link(link)
+        self.assertFalse(can_evaluate_player(player_user, self.player))
+        with self.assertRaises(ValidationError):
+            evaluation_perspective_for_user(player_user, self.player)
+
+    def test_evaluation_perspective_is_server_derived_by_role(self):
+        users = [
+            (AccountRole.COACH, EVALUATION_PERSPECTIVE_COACH),
+            (AccountRole.PLAYER, EVALUATION_PERSPECTIVE_PEER),
+            (AccountRole.STAFF, EVALUATION_PERSPECTIVE_STAFF),
+            (AccountRole.ADMIN, EVALUATION_PERSPECTIVE_STAFF),
+            (AccountRole.GUEST_EVALUATOR, EVALUATION_PERSPECTIVE_GUEST),
+        ]
+        for account_role, expected_perspective in users:
+            with self.subTest(account_role=account_role):
+                evaluator = User.objects.create_user(
+                    username=f"perspective-{account_role}", password="testpass"
+                )
+                set_account_role(evaluator, account_role)
+                self.assertEqual(
+                    evaluation_perspective_for_user(evaluator, self.other_player),
+                    expected_perspective,
+                )
+
+    def test_parent_role_cannot_create_observation(self):
+        parent = User.objects.create_user(username="parent", password="testpass")
+        set_account_role(parent, AccountRole.PARENT)
+
+        with self.assertRaises(ValidationError):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=parent,
+            )
+
+    def test_evaluator_role_for_user_maps_account_roles(self):
+        expectations = [
+            (AccountRole.COACH, ROLE_COACH),
+            (AccountRole.PLAYER, ROLE_PLAYER),
+            (AccountRole.STAFF, ROLE_STAFF),
+            (AccountRole.ADMIN, ROLE_ADMIN),
+            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
+        ]
+        for account_role, evaluator_role_key in expectations:
+            with self.subTest(account_role=account_role):
+                user = User.objects.create_user(
+                    username=f"{account_role}-user", password="testpass"
+                )
+                set_account_role(user, account_role)
+
+                evaluator_role = evaluator_role_for_user(user)
+
+                self.assertEqual(evaluator_role.key, evaluator_role_key)
+
+    def test_coach_assessment_snapshots_actual_account_role_by_default(self):
+        role_expectations = [
+            (AccountRole.COACH, ROLE_COACH),
+            (AccountRole.PLAYER, ROLE_PLAYER),
+            (AccountRole.STAFF, ROLE_STAFF),
+            (AccountRole.ADMIN, ROLE_ADMIN),
+            (AccountRole.GUEST_EVALUATOR, ROLE_GUEST_EVALUATOR),
+        ]
+        for index, (account_role, evaluator_role_key) in enumerate(
+            role_expectations, start=1
+        ):
+            with self.subTest(account_role=account_role):
+                evaluator = User.objects.create_user(
+                    username=f"snapshot-{account_role}", password="testpass"
+                )
+                set_account_role(evaluator, account_role)
+                player = Player.objects.create(
+                    first_name=f"Snapshot{index}", last_name="Target", division="13U"
+                )
+                attach_player_to_season(player, self.season)
+
+                result = create_coach_assessment_observation(
+                    player=player,
+                    evaluation_cycle=self.cycle,
+                    evaluator=evaluator,
+                )
+
+                self.assertEqual(
+                    result.observation.evaluator_role_key, evaluator_role_key
+                )
+                self.assertEqual(
+                    result.observation.evaluator_role,
+                    EvaluatorRole.objects.get(key=evaluator_role_key),
+                )
+
+    def test_draft_view_helpers_are_limited_to_own_drafts(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        self.assertTrue(can_view_own_evaluation_draft(self.evaluator, observation))
+        self.assertFalse(
+            can_view_own_evaluation_draft(self.other_evaluator, observation)
+        )
+
+        observation.status = OBSERVATION_STATUS_SUBMITTED
+        observation.save(update_fields=["status", "updated_at"])
+        self.assertFalse(can_view_own_evaluation_draft(self.evaluator, observation))
+
+    def test_submitted_observation_sets_submitted_at(self):
+        result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+            responses=self.required_response_payload(),
+        )
+        submitted = submit_observation(result.observation)
+
+        self.assertIsNotNone(submitted.submitted_at)
+
+    def test_coach_assessment_requires_evaluator(self):
+        with self.assertRaises(ValidationError):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=None,
+            )
+
+    def test_create_observation_rejects_mismatched_question_set_type(self):
+        other_type = ObservationType.objects.create(key="tryout", name="Tryout")
+        other_question_set = ObservationQuestionSet.objects.create(
+            observation_type=other_type, name="Tryout", version=1
+        )
+
+        with self.assertRaises(ValidationError):
+            create_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                observation_type=self.setup_result.observation_type,
+                question_set=other_question_set,
+                source=self.source,
+                evaluator=self.evaluator,
+                evaluator_role=self.role,
+            )
+
+    def test_save_numeric_text_and_payload_responses(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        rating_question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        text_question = self.setup_result.question_set.questions.get(
+            response_type=RESPONSE_TYPE_TEXT
+        )
+
+        created, updated = save_observation_responses(
+            observation,
+            [
+                {
+                    "question": rating_question,
+                    "value": 4,
+                    "payload": {"source": "test"},
+                },
+                {"question": text_question.key, "value": "Good teammate."},
+            ],
+        )
+
+        rating_response = ObservationResponse.objects.get(
+            observation=observation, question=rating_question
+        )
+        text_response = ObservationResponse.objects.get(
+            observation=observation, question=text_question
+        )
+        self.assertEqual(created, 2)
+        self.assertEqual(updated, 0)
+        self.assertEqual(rating_response.numeric_value, Decimal("4.00"))
+        self.assertEqual(rating_response.payload, {"source": "test"})
+        self.assertEqual(text_response.text_value, "Good teammate.")
+
+    def test_save_response_updates_existing_response(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+
+        save_observation_responses(observation, {question: 3})
+        created, updated = save_observation_responses(observation, {question: 5})
+
+        response = ObservationResponse.objects.get(
+            observation=observation, question=question
+        )
+        self.assertEqual(created, 0)
+        self.assertEqual(updated, 1)
+        self.assertEqual(response.numeric_value, Decimal("5.00"))
+
+    def test_invalid_rating_is_rejected(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+
+        with self.assertRaises(ValidationError):
+            save_observation_responses(observation, {question: 6})
+
+    def test_decimal_and_non_finite_ratings_are_rejected(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+
+        for value in ["3.5", "NaN", "Infinity"]:
+            with self.subTest(value=value):
+                with self.assertRaises(ValidationError):
+                    save_observation_responses(observation, {question: value})
+
+    def test_question_from_different_question_set_is_rejected(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        other_question_set = ObservationQuestionSet.objects.create(
+            observation_type=self.setup_result.observation_type,
+            name="Other",
+            version=2,
+        )
+        other_question = ObservationQuestion.objects.create(
+            question_set=other_question_set,
+            key="other_question",
+            prompt="Other question",
+            response_type=RESPONSE_TYPE_RATING_1_5,
+        )
+
+        with self.assertRaises(ValidationError):
+            save_observation_responses(observation, {other_question: 3})
+
+    def test_duplicate_coach_assessment_is_prevented_for_same_evaluator_player_cycle(
+        self,
+    ):
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        )
+
+        with self.assertRaises(ValidationError):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=self.evaluator,
+            )
+
+    def test_duplicate_self_evaluation_is_prevented_for_player_cycle(self):
+        first_player_user = User.objects.create_user(
+            username="self-one", password="testpass"
+        )
+        second_player_user = User.objects.create_user(
+            username="self-two", password="testpass"
+        )
+        set_account_role(first_player_user, AccountRole.PLAYER)
+        set_account_role(second_player_user, AccountRole.PLAYER)
+        link_user_to_player(
+            first_player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+        link_user_to_player(
+            second_player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=False,
+        )
+
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=first_player_user,
+        )
+
+        with self.assertRaises(ValidationError):
+            create_coach_assessment_observation(
+                player=self.player,
+                evaluation_cycle=self.cycle,
+                evaluator=second_player_user,
+            )
+
+    def test_self_and_peer_evaluations_from_same_player_are_distinct(self):
+        player_user = User.objects.create_user(
+            username="self-peer", password="testpass"
+        )
+        set_account_role(player_user, AccountRole.PLAYER)
+        link_user_to_player(
+            player_user,
+            self.player,
+            relationship=UserPlayerRelationship.SELF,
+            is_primary=True,
+        )
+
+        self_result = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=player_user,
+        )
+        peer_result = create_coach_assessment_observation(
+            player=self.other_player,
+            evaluation_cycle=self.cycle,
+            evaluator=player_user,
+        )
+
+        self.assertEqual(
+            self_result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_SELF
+        )
+        self.assertEqual(
+            peer_result.observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER
+        )
+
+    def test_multiple_evaluators_can_assess_same_player_cycle(self):
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        )
+        second = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.other_evaluator,
+        )
+
+        self.assertEqual(second.observation.player, self.player)
+        self.assertEqual(
+            Observation.objects.filter(
+                player=self.player, evaluation_cycle=self.cycle
+            ).count(),
+            2,
+        )
+
+    def test_same_evaluator_can_assess_different_players_and_cycles(self):
+        other_cycle = EvaluationCycle.objects.create(
+            name="2026 15U Coach Assessment", cycle_type="Coach Assessment"
+        )
+
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        )
+        create_coach_assessment_observation(
+            player=self.other_player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        )
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=other_cycle,
+            evaluator=self.evaluator,
+        )
+
+        self.assertEqual(
+            Observation.objects.filter(evaluator=self.evaluator).count(), 3
+        )
+
+    def test_submit_observation_and_detail_loader(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        save_observation_responses(observation, self.required_response_payload())
+
+        submitted = submit_observation(observation, actor=self.evaluator)
+        detail = get_observation_detail(submitted.id)
+
+        self.assertEqual(submitted.status, OBSERVATION_STATUS_SUBMITTED)
+        self.assertIsNotNone(submitted.submitted_at)
+        self.assertEqual(detail.player, self.player)
+
+    def test_submit_observation_requires_required_responses(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+
+        with self.assertRaises(ValidationError):
+            validate_required_responses(observation)
+        with self.assertRaises(ValidationError):
+            submit_observation(observation, actor=self.evaluator)
+
+    def test_default_question_set_wrapper(self):
+        self.assertEqual(
+            default_coach_assessment_question_set(), self.setup_result.question_set
+        )
+
+    def test_phase_three_models_registered_in_admin(self):
+        for model in [
+            EvaluationCycle,
+            ObservationType,
+            ObservationSource,
+            EvaluatorRole,
+            ObservationQuestionSet,
+            ObservationQuestion,
+            Observation,
+            ObservationResponse,
+        ]:
+            self.assertIn(model, admin.site._registry)
diff --git a/analytics/tests/test_player_experience.py b/analytics/tests/test_player_experience.py
new file mode 100644
index 0000000..9aa4601
--- /dev/null
+++ b/analytics/tests/test_player_experience.py
@@ -0,0 +1,463 @@
+from analytics.tests.helpers import (
+    DRAFT_STATUS_AVAILABLE,
+    DRAFT_STATUS_DRAFTED,
+    DRAFT_STATUS_NO_CONTEXT,
+    EVALUATION_HAS_ANY,
+    EVALUATION_HAS_SUBMITTED,
+    EVALUATION_NO_SUBMITTED,
+    EVALUATION_NOT_STARTED,
+    OBSERVATION_STATUS_DRAFT,
+    OBSERVATION_STATUS_REOPENED,
+    RESPONSE_TYPE_RATING_1_5,
+    RESPONSE_TYPE_TEXT,
+    Decimal,
+    Draft,
+    DraftAction,
+    DraftActionType,
+    DraftPlayer,
+    DraftTeam,
+    EvaluationCycle,
+    Player,
+    PlayerSourceRow,
+    TestCase,
+    User,
+    assign_tag,
+    attach_player_to_season,
+    create_coach_assessment_observation,
+    create_season,
+    ensure_default_coach_assessment_setup,
+    get_player_comparison,
+    get_player_score_summary,
+    get_player_timeline,
+    parse_player_search_filters,
+    reverse,
+    search_players,
+    submit_observation,
+)
+
+
+class PlayerExperienceServiceTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.coach = User.objects.create_user(username="coach", password="testpass")
+        self.other_coach = User.objects.create_user(
+            username="othercoach", password="testpass"
+        )
+        self.player = Player.objects.create(
+            first_name="Eugene",
+            last_name="Lin",
+            birth_year=2012,
+            division="13U",
+            team_name="Expos",
+        )
+        self.other_player = Player.objects.create(
+            first_name="Alex",
+            last_name="Chen",
+            birth_year=2011,
+            division="15U",
+            team_name="Mounties",
+        )
+        self.no_context_player = Player.objects.create(
+            first_name="No", last_name="Context", division="13U"
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(self.other_player, self.season)
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+        self.draft = Draft.objects.create(
+            name="2026 VCB 13U", year=2026, division="13U"
+        )
+        self.team = DraftTeam.objects.create(
+            draft=self.draft, name="Expos Navy", display_order=1
+        )
+        DraftTeam.objects.create(draft=self.draft, name="Expos Gold", display_order=2)
+        self.draft_player = DraftPlayer.objects.create(
+            draft=self.draft,
+            first_name="Eugene",
+            last_name="Lin",
+            full_name="Eugene Lin",
+            extra_data={"Birth Year": "2012"},
+        )
+
+    def rating_payload(self, value=4):
+        return {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5
+            )
+        }
+
+    def submit_assessment(self, evaluator=None, player=None, value=4):
+        result = create_coach_assessment_observation(
+            player=player or self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=evaluator or self.coach,
+            responses=self.rating_payload(value),
+        )
+        return submit_observation(result.observation, actor=evaluator or self.coach)
+
+    def test_timeline_includes_submitted_assessment_import_and_draft_context(self):
+        observation = self.submit_assessment()
+        PlayerSourceRow.objects.create(
+            player=self.player,
+            source="vcb_member_list_csv",
+            source_filename="members.csv",
+            row_number=2,
+            original_row={"private": "do not render"},
+        )
+        DraftAction.objects.create(
+            draft=self.draft,
+            action_type=DraftActionType.PLAYER_DRAFTED,
+            player=self.draft_player,
+            to_team=self.team,
+            pick_number=1,
+        )
+
+        timeline = get_player_timeline(self.player)
+
+        self.assertEqual(timeline.coach_assessment_count, 1)
+        self.assertEqual(timeline.import_count, 1)
+        self.assertEqual(timeline.draft_context_count, 1)
+        self.assertEqual(
+            {item.kind for item in timeline.items},
+            {"coach_assessment", "import", "draft_context"},
+        )
+        self.assertTrue(
+            any(str(observation.id) in item.url for item in timeline.items if item.url)
+        )
+
+    def test_timeline_excludes_draft_and_reopened_observations(self):
+        submitted = self.submit_assessment(evaluator=self.coach, value=5)
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.other_coach,
+            status=OBSERVATION_STATUS_DRAFT,
+            responses=self.rating_payload(1),
+        )
+        third_coach = User.objects.create_user(
+            username="thirdcoach", password="testpass"
+        )
+        create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=third_coach,
+            status=OBSERVATION_STATUS_REOPENED,
+            responses=self.rating_payload(1),
+        )
+
+        timeline = get_player_timeline(self.player)
+
+        self.assertEqual(timeline.coach_assessment_count, 1)
+        self.assertEqual(
+            timeline.items[0].metadata.get("evaluator"), submitted.evaluator.username
+        )
+
+    def test_timeline_handles_no_entries(self):
+        timeline = get_player_timeline(self.other_player)
+
+        self.assertEqual(timeline.items, [])
+        self.assertEqual(timeline.coach_assessment_count, 0)
+
+    def test_comparison_computes_scores_notes_tags_and_draft_context(self):
+        text_question = self.setup_result.question_set.questions.get(
+            response_type=RESPONSE_TYPE_TEXT
+        )
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses={**self.rating_payload(4), text_question: "Strong arm."},
+        ).observation
+        submit_observation(observation, actor=self.coach)
+        assign_tag(self.player, "Strong Prospect")
+        DraftAction.objects.create(
+            draft=self.draft,
+            action_type=DraftActionType.PLAYER_DRAFTED,
+            player=self.draft_player,
+            to_team=self.team,
+            pick_number=1,
+        )
+
+        summary = get_player_score_summary(self.player)
+        comparison = get_player_comparison([self.other_player, self.player])
+
+        self.assertEqual(summary.average_rating, Decimal("4"))
+        self.assertEqual(summary.evaluator_count, 1)
+        self.assertIn("Strong arm.", summary.notes)
+        self.assertEqual([tag.name for tag in summary.tags], ["Strong Prospect"])
+        self.assertEqual(len(summary.draft_contexts), 1)
+        self.assertEqual(
+            [player.id for player in comparison.players],
+            [self.other_player.id, self.player.id],
+        )
+        self.assertIn("Throw", comparison.category_names)
+
+    def test_search_filters_by_name_team_division_birth_year_tag_source_and_evaluation(
+        self,
+    ):
+        assign_tag(self.player, "Future AAA")
+        PlayerSourceRow.objects.create(
+            player=self.player,
+            source="vcb_member_list_csv",
+            source_filename="members.csv",
+        )
+        self.submit_assessment()
+
+        expectations = [
+            ({"q": "Eug"}, [self.player]),
+            ({"team": "Expos"}, [self.player]),
+            ({"division": "13U"}, [self.no_context_player, self.player]),
+            ({"birth_year": "2012"}, [self.player]),
+            ({"tag": "future-aaa"}, [self.player]),
+            ({"source": "vcb_member_list_csv"}, [self.player]),
+            ({"evaluation": EVALUATION_HAS_SUBMITTED}, [self.player]),
+            (
+                {"evaluation": EVALUATION_NO_SUBMITTED},
+                [self.other_player, self.no_context_player],
+            ),
+            ({"evaluation": EVALUATION_HAS_ANY}, [self.player]),
+            (
+                {"evaluation": EVALUATION_NOT_STARTED},
+                [self.other_player, self.no_context_player],
+            ),
+        ]
+        for params, expected_players in expectations:
+            with self.subTest(params=params):
+                result = search_players(parse_player_search_filters(params))
+                self.assertEqual(
+                    [player.id for player in result.players],
+                    [player.id for player in expected_players],
+                )
+
+    def test_search_filters_by_draft_status_and_ignores_invalid_birth_year(self):
+        available_player = Player.objects.create(
+            first_name="Ava", last_name="Lopez", birth_year=2012, division="13U"
+        )
+        DraftPlayer.objects.create(
+            draft=self.draft,
+            first_name="Ava",
+            last_name="Lopez",
+            full_name="Ava Lopez",
+            extra_data={"Birth Year": "2012"},
+        )
+        DraftAction.objects.create(
+            draft=self.draft,
+            action_type=DraftActionType.PLAYER_DRAFTED,
+            player=self.draft_player,
+            to_team=self.team,
+            pick_number=1,
+        )
+
+        drafted = search_players(
+            parse_player_search_filters({"draft_status": DRAFT_STATUS_DRAFTED})
+        )
+        available = search_players(
+            parse_player_search_filters({"draft_status": DRAFT_STATUS_AVAILABLE})
+        )
+        no_context = search_players(
+            parse_player_search_filters({"draft_status": DRAFT_STATUS_NO_CONTEXT})
+        )
+        invalid = search_players(
+            parse_player_search_filters({"birth_year": "not-a-year"})
+        )
+
+        self.assertIn(self.player, drafted.players)
+        self.assertIn(available_player, available.players)
+        self.assertIn(self.no_context_player, no_context.players)
+        self.assertIn(self.player, invalid.players)
+
+
+class PlayerExperienceViewTests(TestCase):
+    def setUp(self):
+        self.staff = User.objects.create_user(
+            username="staff", password="testpass", is_staff=True
+        )
+        self.coach = User.objects.create_user(username="coach", password="testpass")
+        self.player = Player.objects.create(
+            first_name="Eugene",
+            last_name="Lin",
+            birth_year=2012,
+            division="13U",
+            team_name="Expos",
+            bats="R",
+            throws="R",
+            primary_positions="SS",
+        )
+        self.other_player = Player.objects.create(
+            first_name="Alex", last_name="Chen", division="15U", team_name="Mounties"
+        )
+        self.season = create_season(
+            key="2026-spring", name="2026 Spring", is_current=True
+        )
+        attach_player_to_season(self.player, self.season)
+        attach_player_to_season(
+            self.other_player, self.season, team_name="Mounties", division="15U"
+        )
+        self.setup_result = ensure_default_coach_assessment_setup()
+        self.cycle = EvaluationCycle.objects.create(
+            name="2026 13U Coach Assessment",
+            cycle_type="Coach Assessment",
+            coach_assessment_question_set=self.setup_result.question_set,
+            season=self.season,
+        )
+
+    def rating_payload(self, value=4):
+        return {
+            question: value
+            for question in self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5
+            )
+        }
+
+    def test_player_experience_views_require_staff(self):
+        profile_url = reverse(
+            "analytics:player-profile", kwargs={"player_id": self.player.id}
+        )
+        for url in [
+            reverse("analytics:player-search"),
+            profile_url,
+            reverse("analytics:player-compare"),
+        ]:
+            with self.subTest(url=url):
+                self.client.logout()
+                self.assertEqual(self.client.get(url).status_code, 302)
+                self.client.force_login(self.coach)
+                self.assertEqual(self.client.get(url).status_code, 403)
+
+    def test_player_search_view_renders_filters_and_results(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(reverse("analytics:player-search"), {"q": "Eugene"})
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Player Search")
+        self.assertContains(response, self.player.display_name)
+        self.assertNotContains(response, self.other_player.display_name)
+
+    def test_player_profile_renders_phase_six_context_without_raw_import_json(self):
+        assign_tag(self.player, "Strong Prospect")
+        PlayerSourceRow.objects.create(
+            player=self.player,
+            source="vcb_member_list_csv",
+            source_filename="members.csv",
+            row_number=2,
+            original_row={"private": "secret value"},
+        )
+        text_question = self.setup_result.question_set.questions.get(
+            response_type=RESPONSE_TYPE_TEXT
+        )
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses={**self.rating_payload(4), text_question: "Good teammate."},
+        ).observation
+        submit_observation(observation, actor=self.coach)
+        draft = Draft.objects.create(name="2026 VCB 13U", year=2026, division="13U")
+        team = DraftTeam.objects.create(draft=draft, name="Expos Navy", display_order=1)
+        DraftTeam.objects.create(draft=draft, name="Expos Gold", display_order=2)
+        draft_player = DraftPlayer.objects.create(
+            draft=draft,
+            first_name="Eugene",
+            last_name="Lin",
+            full_name="Eugene Lin",
+            extra_data={"Birth Year": "2012"},
+        )
+        DraftAction.objects.create(
+            draft=draft,
+            action_type=DraftActionType.PLAYER_DRAFTED,
+            player=draft_player,
+            to_team=team,
+            pick_number=1,
+        )
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("analytics:player-profile", kwargs={"player_id": self.player.id})
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertContains(response, "Strong Prospect")
+        self.assertContains(response, "vcb_member_list_csv")
+        self.assertContains(response, "Good teammate.")
+        self.assertContains(response, "Draft Context")
+        self.assertContains(response, "Timeline")
+        self.assertNotContains(response, "secret value")
+
+    def test_player_profile_empty_states(self):
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse(
+                "analytics:player-profile", kwargs={"player_id": self.other_player.id}
+            )
+        )
+
+        self.assertContains(response, "No tags assigned.")
+        self.assertContains(response, "No imported source rows.")
+        self.assertContains(response, "No draft context found.")
+        self.assertContains(response, "No submitted coach assessments yet.")
+        self.assertContains(response, "No timeline entries yet.")
+
+    def test_player_compare_handles_empty_selected_and_selected_players(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.coach,
+            responses=self.rating_payload(4),
+        ).observation
+        submit_observation(observation, actor=self.coach)
+        self.client.force_login(self.staff)
+
+        empty_response = self.client.get(reverse("analytics:player-compare"))
+        selected_response = self.client.get(
+            reverse("analytics:player-compare"),
+            {"players": [str(self.player.id), str(self.other_player.id)]},
+        )
+
+        self.assertContains(empty_response, "Select players to compare.")
+        self.assertContains(selected_response, self.player.display_name)
+        self.assertContains(selected_response, "4.0")
+        self.assertContains(selected_response, "No submitted assessments")
+
+    def test_player_compare_caps_selected_players(self):
+        extra_players = [
+            Player.objects.create(
+                first_name=f"Player{i}", last_name="Test", division="13U"
+            )
+            for i in range(10)
+        ]
+        ids = [str(player.id) for player in extra_players]
+        self.client.force_login(self.staff)
+
+        response = self.client.get(
+            reverse("analytics:player-compare"), {"players": ids}
+        )
+
+        self.assertEqual(response.status_code, 200)
+        self.assertEqual(len(response.context["selected_players"]), 6)
+
+    def test_phase_six_regression_existing_pages_render(self):
+        self.client.force_login(self.staff)
+
+        self.assertEqual(
+            self.client.get(reverse("analytics:assessment-list")).status_code, 200
+        )
+        self.assertEqual(
+            self.client.get(reverse("analytics:observation-review-list")).status_code,
+            200,
+        )
+        self.assertEqual(
+            self.client.get(reverse("analytics:import-list")).status_code, 200
+        )
```
