# Prompt 85 - Seasons

## User Prompt

```text
Perform Repository Cleanup Phase 5 only: Season Operations View and Query Refactor.

Use continuous loop engineering.

Continue until the Season Operations presentation layer is structurally cleaner, behavior remains unchanged, focused and full verification pass, commits are pushed, and the working tree is clean.

Do not change Season Operations product behavior.

Do not add new routes, pages, fields, permissions, filters, actions, models, migrations, or features.

Do not begin the large test-module split, account-operations refactor, or Platform V2 work.

==================================================
Current State
=============

Repository Cleanup Phases 1 through 4 are complete.

Current repository state includes:

* reconciled documentation;
* Django 4.2.30;
* Ruff, Black, isort, and pre-commit;
* touched-files-only formatting policy;
* refactored player import service;
* refactored coach import service;
* stable public façades for both import workflows.

Seasonal Participation V1 is Feature Complete, Production Ready, and Frozen.

The Season Operations UI is production behavior and must not change.

The current Season Operations presentation layer is concentrated in:

```text
seasons/views.py
```

That module now owns several separate operational areas:

* access control;
* season list/detail/create/edit;
* current-season transitions;
* season-team list/create/edit;
* player membership list/create/edit/end;
* player transfer and additional-membership workflows;
* player season history;
* coach assignment list/create/edit/end;
* coach season history;
* filtering;
* pagination;
* query optimization;
* success/error messaging.

The objective is a behavior-preserving structural refactor.

==================================================
Objective
=========

Reduce the size and mixed responsibilities of:

```text
seasons/views.py
```

Split cohesive view responsibilities into focused modules.

Where useful, extract repeated filtering and queryset construction into focused read/query services.

Preserve:

* all current route names;
* all current URL paths;
* all current templates;
* all current forms;
* permissions;
* redirects;
* pagination;
* query parameters;
* filter behavior;
* messages;
* confirmation behavior;
* service calls;
* transaction behavior;
* historical preservation;
* compatibility-field synchronization.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete refactoring, regression-proofing, documentation, or verification work remains.

PASS

All Phase 5 acceptance criteria are satisfied, tests and tooling pass, commits are pushed, and the working tree is clean.

BLOCKED

The views cannot be safely decomposed without unresolved behavior changes, route changes, or scope expansion.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied criterion.

Moving classes between files without clearer ownership does not count as progress.

==================================================
Established Loop Workflow
=========================

Every loop must:

1. reconcile the committed repository state;
2. read `AGENTS.md`;
3. read current Seasonal Participation and Season Operations documentation;
4. confirm the working tree is clean;
5. inspect all Season Operations routes, views, forms, templates, services, and tests;
6. inventory every current public view class/function imported by `seasons/urls.py`;
7. identify one cohesive structural boundary;
8. create the next prompt archive before implementation;
9. refactor only the selected Season Operations concern;
10. preserve or add focused regression tests;
11. run tooling on touched files only;
12. run focused verification;
13. perform senior-engineer self-review;
14. fix every verified issue;
15. update architecture documentation only if internal ownership materially changes;
16. run full verification;
17. commit refactor, tests, and minimal documentation;
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
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* relevant prompt archives for:

  * Seasonal Participation Phase 5;
  * Seasonal Participation Phase 6;
  * repository cleanup Phases 3 and 4.

Inspect:

* `seasons/views.py`
* `seasons/urls.py`
* `seasons/forms.py`
* `seasons/models.py`
* `seasons/services/`
* `seasons/tests.py`
* every template under `seasons/templates/seasons/`
* navigation links pointing to Season Operations;
* relevant player and account detail views;
* permission helpers used by Season Operations;
* pagination partials and query-string preservation logic.

==================================================
Public Route Preservation
=========================

Inventory every route and view currently registered in:

```text
seasons/urls.py
```

Preserve:

* route names;
* route paths;
* HTTP methods;
* reverse lookups;
* template names;
* context keys;
* redirect targets;
* messages.

Preferred approach:

```text
seasons/views/
    __init__.py
    mixins.py
    seasons.py
    teams.py
    memberships.py
    assignments.py
```

This is a suggested structure only.

Use repository evidence to choose the smallest clear split.

`seasons/urls.py` may import from the `seasons.views` package or specific modules, but external route names must remain unchanged.

Do not create a compatibility layer more complicated than the original module.

==================================================
Recommended Responsibility Boundaries
=====================================

## 1. Shared Access And View Helpers

Move shared view-layer behavior such as:

* staff access mixin;
* common permission checks;
* common pagination helpers;
* query-string preservation helpers;
* repeated object lookup helpers;
* common success/error messaging helpers only if they are truly reused.

Do not move business rules into mixins.

Do not duplicate service validation in views.

## 2. Season Views

Group:

* season list;
* season detail;
* season create;
* season edit;
* set-current confirmation/action.

Preserve:

* ordering;
* counts;
* filters;
* inactive/current behavior;
* messages;
* redirect targets;
* service-based current-season transition.

## 3. Team Views

Group:

* season-team list;
* season-team create;
* season-team edit.

Preserve:

* season shortcut behavior;
* inactive-season protection;
* filters;
* counts;
* normalization through services;
* no destructive delete behavior.

## 4. Player Membership Views

Group:

* membership list;
* membership create;
* membership edit;
* membership end/deactivate;
* transfer workflow;
* additional-membership workflow;
* player season history.

Preserve:

* primary-membership rules;
* compatibility synchronization;
* transfer history;
* additional membership behavior;
* submitted evaluation snapshot immutability;
* all confirmation and validation behavior.

## 5. Coach Assignment Views

Group:

* assignment list;
* assignment create;
* assignment edit;
* assignment end/deactivate;
* coach season history.

Preserve:

* account-role validation;
* password immutability;
* activation-state immutability;
* privilege separation;
* primary-assignment behavior;
* historical preservation.

==================================================
Query And Read-Service Review
=============================

Review direct queryset construction in `seasons/views.py`.

Extract repeated or domain-relevant read logic only where it improves ownership.

Possible modules:

```text
seasons/services/season_query_service.py
seasons/services/membership_query_service.py
seasons/services/assignment_query_service.py
```

Only add modules that have a cohesive purpose.

Suitable responsibilities may include:

* season list annotations;
* team counts;
* membership filters;
* assignment filters;
* deterministic ordering;
* select-related/prefetch-related configuration;
* player or coach history querysets.

Do not create a generic repository layer.

Do not hide simple one-line object lookups behind services.

Keep form/request interpretation in views or forms.

Keep state-changing domain behavior in existing authoritative services.

==================================================
Behavioral Freeze
=================

The following behavior must remain unchanged.

## Permissions

* unauthenticated users are redirected;
* authorized staff can access Season Operations;
* ordinary players are denied;
* ordinary coaches are denied;
* seasonal assignments do not grant staff access;
* existing permission helpers remain authoritative.

## Seasons

* season list filters and ordering;
* pagination;
* counts;
* create/edit validation;
* current state not directly editable;
* inactive season cannot be made current;
* set-current action remains explicit and atomic.

## Teams

* list filters;
* pagination;
* create/edit behavior;
* inactive-season shortcut remains blocked;
* normalization remains service-owned;
* historical snapshots remain unchanged.

## Player Memberships

* list filters and pagination;
* create/edit behavior;
* primary membership rules;
* inactive-primary rejection;
* compatibility-field synchronization;
* end/deactivate behavior;
* provenance display;
* player season history.

## Transfers

* transfer preserves old membership;
* old membership becomes ended/inactive/transferred as currently defined;
* new membership becomes primary;
* compatibility fields update;
* additional membership preserves existing primary;
* no submitted evaluation snapshots change.

## Coach Assignments

* list filters and pagination;
* create/edit/end behavior;
* only coach accounts may be assigned;
* no password, role, activation, staff, or superuser changes;
* multiple teams and roles remain supported;
* coach history remains unchanged.

## UX

* template names;
* context keys;
* form errors;
* confirmation pages;
* success messages;
* error messages;
* redirects;
* preserved filter query strings;
* page parameter behavior.

==================================================
No Product Changes
==================

Do not:

* add routes;
* rename routes;
* change URLs;
* add filters;
* remove filters;
* add fields;
* change forms;
* change templates except import/include paths if unavoidable;
* change messages intentionally;
* change navigation;
* add dashboards;
* add charts;
* add exports;
* add APIs;
* add bulk editing;
* add JavaScript;
* change permissions;
* introduce team-scoped authorization;
* remove Django admin support.

==================================================
Tests
=====

Preserve all existing Season Operations tests.

Add focused tests only where decomposition exposes an untested contract.

Potential contract tests:

* all route names still reverse;
* all existing view classes/functions remain reachable through URLs;
* context keys remain stable;
* pagination preserves filters;
* season list ordering remains deterministic;
* inactive-season shortcut remains blocked;
* transfer redirects/messages remain unchanged;
* membership and assignment history ordering remains unchanged;
* unauthorized access remains unchanged.

Do not rewrite all `seasons/tests.py` in this phase.

Do not split the test module yet.

Prefer behavior-level tests through the Django test client.

Avoid tests that depend on internal module paths unless verifying the public route table.

==================================================
Dependency Direction
====================

Preferred dependency direction:

```text
urls
    ->
seasons.views modules
    ->
forms and query/read services
    ->
authoritative state-changing services
    ->
models
```

Views must not:

* own transaction rules;
* implement normalization;
* directly rewrite compatibility fields;
* directly manipulate passwords or account roles;
* update submitted evaluation snapshots.

Query services must not import views, forms, or templates.

Avoid circular imports between view modules.

Use a small `views/__init__.py` only if it improves route imports without hiding ownership.

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

Remove:

* obsolete imports;
* dead helpers;
* duplicated filter logic;
* duplicated pagination logic;
* repeated `select_related` definitions where a clear read service is justified;
* compatibility wrappers with no stable caller.

Keep:

* thin views;
* explicit service calls;
* explicit object validation;
* readable route ownership;
* server-rendered Django patterns.

==================================================
Documentation
=============

Update documentation only if needed to describe the internal view/query layout.

Likely candidate:

* `docs/ARCHITECTURE.md`

Do not change the user manual because user behavior must remain unchanged.

Do not describe the refactor as a feature.

==================================================
Scope Restrictions
==================

Do not:

* modify models;
* create migrations;
* change forms except imports if unavoidable;
* change templates except imports/includes if unavoidable;
* change service business rules;
* change account or player behavior;
* refactor import services again;
* split test packages;
* refactor account operations;
* introduce new shared framework code;
* bulk-format the repository;
* regenerate the project flat-file snapshot.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test python manage.py test seasons
DJANGO_SECRET_KEY=test python manage.py test players
DJANGO_SECRET_KEY=test python manage.py test accounts
DJANGO_SECRET_KEY=test python manage.py test analytics
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

* route-name drift;
* URL-path drift;
* context-key drift;
* template-name drift;
* redirect drift;
* message drift;
* permission drift;
* HTTP-method drift;
* pagination regressions;
* filter preservation regressions;
* N+1 regressions;
* transfer behavior changes;
* compatibility-field regressions;
* account privilege or password side effects;
* snapshot immutability regressions;
* circular imports;
* overly generic query abstractions;
* deep coupling between view modules;
* formatting churn;
* stale documentation.

Fix every verified issue before committing.

==================================================
Acceptance Criteria
===================

Do not declare PASS until all criteria are satisfied.

A. Structure

* `seasons/views.py` no longer contains all operational view responsibilities;
* views are grouped by clear operational area;
* shared mixins/helpers are focused;
* route ownership is easy to understand.

B. Routes And UX

* every existing URL path remains unchanged;
* every existing route name remains unchanged;
* templates and context remain unchanged;
* messages and redirects remain unchanged;
* pagination and filters remain unchanged.

C. Permissions

* access behavior remains unchanged;
* no seasonal role gains staff access;
* object-level validation remains intact.

D. Domain Behavior

* season lifecycle behavior remains unchanged;
* team behavior remains unchanged;
* membership and transfer behavior remain unchanged;
* assignment behavior remains unchanged;
* historical records and snapshots remain preserved.

E. Query Quality

* repeated query logic is reduced where justified;
* list and history pages remain efficiently loaded;
* no N+1 regressions;
* no unnecessary repository abstraction.

F. Quality

* no circular imports;
* no dead code;
* touched files pass Ruff, Black, and isort;
* no unrelated formatting churn.

G. Tests

* focused suites pass;
* full suite passes;
* route and workflow contracts remain covered.

H. Migration

* no model changes;
* no migrations;
* migration checks pass.

I. Documentation

* architecture updated only if internal layout materially changes;
* user-facing documentation remains unchanged.

J. Git

* refactor commit exists;
* prompt archive commit exists;
* both pushed;
* working tree is clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally:

1. inventory routes and public view names;
2. create a focused `seasons.views` package;
3. move shared access helpers;
4. split season, team, membership, and assignment views;
5. extract repeated query logic only where clearly justified;
6. preserve `seasons/urls.py` route names and paths;
7. remove obsolete code from the original module;
8. run tooling and focused/full verification;
9. update minimal architecture documentation if warranted;
10. commit, archive, push, and reassess.

If a safe complete split is too large, continue with another cohesive loop.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* materially clarifies view ownership;
* removes verified duplicated filtering/query logic;
* reduces the risk of route or permission maintenance errors;
* improves maintainability without behavior change;
* adds missing workflow-contract coverage.

Moving classes into arbitrary files without clearer boundaries does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* developer maintaining season lifecycle pages;
* developer maintaining roster operations;
* developer maintaining coach assignment operations;
* tester tracing a route to a view;
* security reviewer inspecting staff access;
* performance reviewer inspecting paginated querysets;
* production operator relying on stable workflows.

Confirm:

* the view layer is easier to navigate;
* all routes and behavior are unchanged;
* query ownership is clear;
* no new feature was introduced;
* the full suite passes.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before implementation;
2. commit refactor, tests, and minimal documentation;
3. update the prompt archive with:

   * implementation commit hash;
   * old and new view structure;
   * route preservation;
   * permission preservation;
   * query/read-service changes;
   * transfer and assignment behavior;
   * tests added or changed;
   * tooling results;
   * full verification;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested implementation commit:

```text
Refactor season operations views
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
* old and new view structure;
* route preservation;
* template/context preservation;
* permission behavior;
* season lifecycle behavior;
* team behavior;
* membership and transfer behavior;
* assignment behavior;
* query/read-service changes;
* pagination/filter behavior;
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

`70fe730` - Refactor season operations views

## Old View Structure

```text
seasons/views.py
```

## New View Structure

```text
seasons/views/
    __init__.py
    mixins.py
    seasons.py
    teams.py
    memberships.py
    assignments.py
seasons/services/season_query_service.py
```

## Route Preservation

All existing Season Operations URL paths and route names remain registered through `seasons/urls.py`. The public `seasons.views` import path is preserved through `seasons/views/__init__.py` re-exports.

## Permission Preservation

The existing `SeasonOperationsStaffRequiredMixin` behavior is unchanged and remains based on `accounts.services.permissions.is_staff_or_admin`.

## Query / Read-Service Changes

Repeated Season Operations list and history queryset construction moved into `seasons.services.season_query_service`. State-changing workflows continue to call the existing authoritative services.

## Transfer And Assignment Behavior

Player transfer/additional-membership workflows and coach assignment create/edit/end workflows were moved into focused view modules without intentional behavior changes. Existing service calls, messages, redirects, and templates were preserved.

## Verification

Focused verification:

```text
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test python manage.py makemigrations analytics --check
DJANGO_SECRET_KEY=test python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test python manage.py test seasons
DJANGO_SECRET_KEY=test python manage.py test players
DJANGO_SECRET_KEY=test python manage.py test accounts
DJANGO_SECRET_KEY=test python manage.py test analytics
pre-commit run --files seasons/services/season_query_service.py seasons/views/__init__.py seasons/views/mixins.py seasons/views/seasons.py seasons/views/teams.py seasons/views/memberships.py seasons/views/assignments.py docs/prompts/prompt_85_seasons.md
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

PASS.

## Commit Diff

```diff
commit 70fe730aab2c3177791690095d1c3b71c7417e59
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 11:36:00 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 11:36:00 2026 -0700

    Refactor season operations views
---
 seasons/services/season_query_service.py | 154 ++++++++
 seasons/views.py                         | 653 -------------------------------
 seasons/views/__init__.py                |  49 +++
 seasons/views/assignments.py             | 199 ++++++++++
 seasons/views/memberships.py             | 255 ++++++++++++
 seasons/views/mixins.py                  |  20 +
 seasons/views/seasons.py                 | 116 ++++++
 seasons/views/teams.py                   | 119 ++++++
 8 files changed, 912 insertions(+), 653 deletions(-)

diff --git a/seasons/services/season_query_service.py b/seasons/services/season_query_service.py
new file mode 100644
index 0000000..486b443
--- /dev/null
+++ b/seasons/services/season_query_service.py
@@ -0,0 +1,154 @@
+from __future__ import annotations
+
+from django.db.models import Count, Q
+
+from seasons.models import (
+    CoachSeasonAssignment,
+    PlayerRosterMembership,
+    Season,
+    SeasonTeam,
+)
+
+
+def clean_int(value: str | None) -> str | None:
+    value = str(value or "").strip()
+    return value if value.isdigit() else None
+
+
+def season_list_queryset():
+    return Season.objects.annotate(
+        team_count=Count("teams", distinct=True),
+        membership_count=Count("teams__player_memberships", distinct=True),
+        assignment_count=Count("teams__coach_assignments", distinct=True),
+    ).order_by("-starts_on", "name", "id")
+
+
+def season_detail_team_queryset(season: Season):
+    return season.teams.annotate(
+        membership_count=Count("player_memberships", distinct=True),
+        assignment_count=Count("coach_assignments", distinct=True),
+    ).order_by("division", "name", "id")
+
+
+def season_options_queryset():
+    return Season.objects.order_by("-is_current", "-starts_on", "name")
+
+
+def team_options_queryset():
+    return SeasonTeam.objects.select_related("season").order_by(
+        "-season__is_current",
+        "season__name",
+        "division",
+        "name",
+    )
+
+
+def team_list_queryset(*, season_id: str | None = None):
+    queryset = SeasonTeam.objects.select_related("season").annotate(
+        membership_count=Count("player_memberships", distinct=True),
+        assignment_count=Count("coach_assignments", distinct=True),
+    )
+    season_id = clean_int(season_id)
+    if season_id:
+        queryset = queryset.filter(season_id=season_id)
+    return queryset.order_by(
+        "-season__is_current", "season__name", "division", "name", "id"
+    )
+
+
+def membership_list_queryset(params):
+    queryset = PlayerRosterMembership.objects.select_related(
+        "player", "season_team", "season_team__season"
+    )
+    season_id = clean_int(params.get("season"))
+    team_id = clean_int(params.get("team"))
+    active = params.get("active")
+    search = params.get("q", "").strip()
+    if season_id:
+        queryset = queryset.filter(season_team__season_id=season_id)
+    if team_id:
+        queryset = queryset.filter(season_team_id=team_id)
+    if active == "yes":
+        queryset = queryset.filter(is_active=True)
+    elif active == "no":
+        queryset = queryset.filter(is_active=False)
+    if search:
+        queryset = queryset.filter(
+            Q(player__first_name__icontains=search)
+            | Q(player__last_name__icontains=search)
+        )
+    return queryset.order_by(
+        "-season_team__season__is_current",
+        "season_team__season__name",
+        "player__last_name",
+        "player__first_name",
+        "id",
+    )
+
+
+def player_history_membership_queryset(player):
+    return (
+        PlayerRosterMembership.objects.select_related(
+            "season_team", "season_team__season"
+        )
+        .filter(player=player)
+        .order_by(
+            "-season_team__season__starts_on",
+            "-season_team__season__is_current",
+            "season_team__division",
+            "season_team__name",
+            "-starts_on",
+            "id",
+        )
+    )
+
+
+def assignment_list_queryset(params):
+    queryset = CoachSeasonAssignment.objects.select_related(
+        "user",
+        "season_team",
+        "season_team__season",
+        "user__account_profile",
+    )
+    season_id = clean_int(params.get("season"))
+    team_id = clean_int(params.get("team"))
+    active = params.get("active")
+    search = params.get("q", "").strip()
+    if season_id:
+        queryset = queryset.filter(season_team__season_id=season_id)
+    if team_id:
+        queryset = queryset.filter(season_team_id=team_id)
+    if active == "yes":
+        queryset = queryset.filter(is_active=True)
+    elif active == "no":
+        queryset = queryset.filter(is_active=False)
+    if search:
+        queryset = queryset.filter(
+            Q(user__first_name__icontains=search)
+            | Q(user__last_name__icontains=search)
+            | Q(user__username__icontains=search)
+        )
+    return queryset.order_by(
+        "-season_team__season__is_current",
+        "season_team__season__name",
+        "user__last_name",
+        "user__first_name",
+        "id",
+    )
+
+
+def coach_history_assignment_queryset(coach):
+    return (
+        CoachSeasonAssignment.objects.select_related(
+            "season_team", "season_team__season"
+        )
+        .filter(user=coach)
+        .order_by(
+            "-season_team__season__starts_on",
+            "-season_team__season__is_current",
+            "season_team__division",
+            "season_team__name",
+            "-starts_on",
+            "id",
+        )
+    )
diff --git a/seasons/views.py b/seasons/views.py
deleted file mode 100644
index d63a4f8..0000000
--- a/seasons/views.py
+++ /dev/null
@@ -1,653 +0,0 @@
-from __future__ import annotations
-
-from django.contrib import messages
-from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
-from django.core.exceptions import PermissionDenied, ValidationError
-from django.db.models import Count, Q
-from django.http import Http404
-from django.shortcuts import get_object_or_404, redirect
-from django.views.generic import FormView, ListView, TemplateView
-
-from accounts.services.permissions import is_staff_or_admin
-from players.models import Player
-from seasons.forms import (
-    CoachAssignmentEndForm,
-    CoachSeasonAssignmentForm,
-    ConfirmCurrentSeasonForm,
-    PlayerMembershipEndForm,
-    PlayerMembershipTransferForm,
-    PlayerRosterMembershipForm,
-    SeasonForm,
-    SeasonTeamForm,
-)
-from seasons.models import CoachSeasonAssignment, PlayerRosterMembership, RosterStatus, Season, SeasonTeam
-from seasons.services.coach_assignment_service import create_assignment, deactivate_assignment, update_assignment
-from seasons.services.membership_service import create_membership, deactivate_membership, transfer_player, update_membership
-from seasons.services.season_service import create_season, set_current_season, update_season
-from seasons.services.team_service import get_or_create_season_team, update_season_team
-
-
-class SeasonOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
-    def test_func(self):
-        return is_staff_or_admin(self.request.user)
-
-
-class SeasonPaginationMixin:
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        query = self.request.GET.copy()
-        query.pop("page", None)
-        encoded = query.urlencode()
-        context["pagination_query"] = f"{encoded}&" if encoded else ""
-        return context
-
-
-def _clean_int(value: str) -> str | None:
-    value = str(value or "").strip()
-    return value if value.isdigit() else None
-
-
-class SeasonListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
-    model = Season
-    template_name = "seasons/season_list.html"
-    context_object_name = "seasons"
-    paginate_by = 50
-
-    def get_queryset(self):
-        return Season.objects.annotate(
-            team_count=Count("teams", distinct=True),
-            membership_count=Count("teams__player_memberships", distinct=True),
-            assignment_count=Count("teams__coach_assignments", distinct=True),
-        ).order_by("-starts_on", "name", "id")
-
-
-class SeasonDetailView(SeasonOperationsStaffRequiredMixin, TemplateView):
-    template_name = "seasons/season_detail.html"
-
-    def dispatch(self, request, *args, **kwargs):
-        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        teams = (
-            self.season.teams.annotate(
-                membership_count=Count("player_memberships", distinct=True),
-                assignment_count=Count("coach_assignments", distinct=True),
-            )
-            .order_by("division", "name", "id")
-        )
-        context.update({"season": self.season, "teams": teams})
-        return context
-
-
-class SeasonCreateView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/season_form.html"
-    form_class = SeasonForm
-
-    def form_valid(self, form):
-        try:
-            season = create_season(**form.cleaned_data)
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Season created.")
-        return redirect("seasons:season-detail", season_id=season.id)
-
-
-class SeasonEditView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/season_form.html"
-    form_class = SeasonForm
-
-    def dispatch(self, request, *args, **kwargs):
-        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_initial(self):
-        return {
-            "key": self.season.key,
-            "name": self.season.name,
-            "starts_on": self.season.starts_on,
-            "ends_on": self.season.ends_on,
-            "is_active": self.season.is_active,
-        }
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["season"] = self.season
-        return context
-
-    def form_valid(self, form):
-        try:
-            update_season(self.season, **form.cleaned_data)
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Season updated.")
-        return redirect("seasons:season-detail", season_id=self.season.id)
-
-
-class SeasonSetCurrentView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/season_set_current.html"
-    form_class = ConfirmCurrentSeasonForm
-
-    def dispatch(self, request, *args, **kwargs):
-        self.season = get_object_or_404(Season, pk=kwargs["season_id"])
-        if not self.season.is_active:
-            raise PermissionDenied("Inactive seasons cannot be made current.")
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["season"] = self.season
-        return context
-
-    def form_valid(self, form):
-        set_current_season(self.season)
-        messages.success(self.request, f"{self.season.name} is now the current season.")
-        return redirect("seasons:season-detail", season_id=self.season.id)
-
-
-class SeasonTeamListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
-    model = SeasonTeam
-    template_name = "seasons/team_list.html"
-    context_object_name = "teams"
-    paginate_by = 50
-
-    def get_queryset(self):
-        queryset = SeasonTeam.objects.select_related("season").annotate(
-            membership_count=Count("player_memberships", distinct=True),
-            assignment_count=Count("coach_assignments", distinct=True),
-        )
-        season_id = _clean_int(self.request.GET.get("season"))
-        if season_id:
-            queryset = queryset.filter(season_id=season_id)
-        return queryset.order_by("-season__is_current", "season__name", "division", "name", "id")
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["seasons"] = Season.objects.order_by("-is_current", "-starts_on", "name")
-        context["selected_season_id"] = self.request.GET.get("season", "")
-        return context
-
-
-class SeasonTeamCreateView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/team_form.html"
-    form_class = SeasonTeamForm
-
-    def get_form_kwargs(self):
-        kwargs = super().get_form_kwargs()
-        season_id = self.kwargs.get("season_id")
-        if season_id:
-            kwargs["fixed_season"] = get_object_or_404(Season, pk=season_id, is_active=True)
-        return kwargs
-
-    def form_valid(self, form):
-        data = form.cleaned_data
-        try:
-            team, created = get_or_create_season_team(
-                season=data["season"],
-                name=data["name"],
-                division=data["division"],
-                external_source=data.get("external_source", ""),
-                external_identifier=data.get("external_identifier", ""),
-            )
-            if not created:
-                update_season_team(team, is_active=data.get("is_active", False))
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Season team created." if created else "Existing season team reused.")
-        return redirect("seasons:team-list")
-
-
-class SeasonTeamEditView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/team_form.html"
-    form_class = SeasonTeamForm
-
-    def dispatch(self, request, *args, **kwargs):
-        self.team = get_object_or_404(SeasonTeam.objects.select_related("season"), pk=kwargs["team_id"])
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_form_kwargs(self):
-        kwargs = super().get_form_kwargs()
-        kwargs["fixed_season"] = self.team.season
-        return kwargs
-
-    def get_initial(self):
-        return {
-            "season": self.team.season,
-            "name": self.team.name,
-            "division": self.team.division,
-            "external_source": self.team.external_source,
-            "external_identifier": self.team.external_identifier,
-            "is_active": self.team.is_active,
-        }
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["team"] = self.team
-        return context
-
-    def form_valid(self, form):
-        data = form.cleaned_data
-        try:
-            update_season_team(
-                self.team,
-                name=data["name"],
-                division=data["division"],
-                external_source=data.get("external_source", ""),
-                external_identifier=data.get("external_identifier", ""),
-                is_active=data.get("is_active", False),
-            )
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Season team updated.")
-        return redirect("seasons:team-list")
-
-
-class PlayerMembershipListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
-    model = PlayerRosterMembership
-    template_name = "seasons/membership_list.html"
-    context_object_name = "memberships"
-    paginate_by = 50
-
-    def get_queryset(self):
-        queryset = PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season")
-        season_id = _clean_int(self.request.GET.get("season"))
-        team_id = _clean_int(self.request.GET.get("team"))
-        active = self.request.GET.get("active")
-        search = self.request.GET.get("q", "").strip()
-        if season_id:
-            queryset = queryset.filter(season_team__season_id=season_id)
-        if team_id:
-            queryset = queryset.filter(season_team_id=team_id)
-        if active == "yes":
-            queryset = queryset.filter(is_active=True)
-        elif active == "no":
-            queryset = queryset.filter(is_active=False)
-        if search:
-            queryset = queryset.filter(Q(player__first_name__icontains=search) | Q(player__last_name__icontains=search))
-        return queryset.order_by("-season_team__season__is_current", "season_team__season__name", "player__last_name", "player__first_name", "id")
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context.update(
-            {
-                "seasons": Season.objects.order_by("-is_current", "-starts_on", "name"),
-                "teams": SeasonTeam.objects.select_related("season").order_by("-season__is_current", "season__name", "division", "name"),
-                "filters": {
-                    "season": self.request.GET.get("season", ""),
-                    "team": self.request.GET.get("team", ""),
-                    "active": self.request.GET.get("active", ""),
-                    "q": self.request.GET.get("q", ""),
-                },
-            }
-        )
-        return context
-
-
-class PlayerMembershipCreateView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/membership_form.html"
-    form_class = PlayerRosterMembershipForm
-
-    def form_valid(self, form):
-        data = form.cleaned_data
-        try:
-            membership = create_membership(
-                player=data["player"],
-                season_team=data["season_team"],
-                status=data["status"],
-                jersey_number=data.get("jersey_number", ""),
-                is_primary=data.get("is_primary", False),
-                is_active=data.get("is_active", False),
-                starts_on=data.get("starts_on"),
-                ends_on=data.get("ends_on"),
-                source=data.get("source", ""),
-                source_identifier=data.get("source_identifier", ""),
-                sync_player_fields=True,
-            )
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Player membership created.")
-        return redirect("seasons:player-history", player_id=membership.player_id)
-
-
-class PlayerMembershipEditView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/membership_form.html"
-    form_class = PlayerRosterMembershipForm
-
-    def dispatch(self, request, *args, **kwargs):
-        self.membership = get_object_or_404(
-            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
-            pk=kwargs["membership_id"],
-        )
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_form_kwargs(self):
-        kwargs = super().get_form_kwargs()
-        kwargs["fixed_season"] = self.membership.season
-        kwargs["editing"] = True
-        return kwargs
-
-    def get_initial(self):
-        return {
-            "player": self.membership.player,
-            "season_team": self.membership.season_team,
-            "status": self.membership.status,
-            "jersey_number": self.membership.jersey_number,
-            "is_primary": self.membership.is_primary,
-            "is_active": self.membership.is_active,
-            "starts_on": self.membership.starts_on,
-            "ends_on": self.membership.ends_on,
-            "source": self.membership.source,
-            "source_identifier": self.membership.source_identifier,
-        }
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["membership"] = self.membership
-        return context
-
-    def form_valid(self, form):
-        data = form.cleaned_data
-        try:
-            update_membership(
-                self.membership,
-                status=data["status"],
-                jersey_number=data.get("jersey_number", ""),
-                is_primary=data.get("is_primary", False),
-                is_active=data.get("is_active", False),
-                starts_on=data.get("starts_on"),
-                ends_on=data.get("ends_on"),
-                source=data.get("source", ""),
-                source_identifier=data.get("source_identifier", ""),
-                sync_player_fields=True,
-            )
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Player membership updated.")
-        return redirect("seasons:player-history", player_id=self.membership.player_id)
-
-
-class PlayerMembershipEndView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/membership_end.html"
-    form_class = PlayerMembershipEndForm
-
-    def dispatch(self, request, *args, **kwargs):
-        self.membership = get_object_or_404(
-            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
-            pk=kwargs["membership_id"],
-        )
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["membership"] = self.membership
-        return context
-
-    def form_valid(self, form):
-        try:
-            deactivate_membership(
-                self.membership,
-                status=form.cleaned_data["status"],
-                ends_on=form.cleaned_data.get("ends_on"),
-                sync_player_fields=True,
-            )
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Player membership ended.")
-        return redirect("seasons:player-history", player_id=self.membership.player_id)
-
-
-class PlayerMembershipTransferView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/membership_transfer.html"
-    form_class = PlayerMembershipTransferForm
-
-    def dispatch(self, request, *args, **kwargs):
-        self.membership = get_object_or_404(
-            PlayerRosterMembership.objects.select_related("player", "season_team", "season_team__season"),
-            pk=kwargs["membership_id"],
-        )
-        if not self.membership.is_active:
-            raise PermissionDenied("Only active memberships can be transferred or extended.")
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_form_kwargs(self):
-        kwargs = super().get_form_kwargs()
-        kwargs["source_membership"] = self.membership
-        return kwargs
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["membership"] = self.membership
-        return context
-
-    def form_valid(self, form):
-        data = form.cleaned_data
-        try:
-            if data["action"] == PlayerMembershipTransferForm.ACTION_TRANSFER:
-                transfer_player(
-                    player=self.membership.player,
-                    to_season_team=data["season_team"],
-                    from_membership=self.membership,
-                    transfer_date=data.get("transfer_date"),
-                    source=data.get("source", ""),
-                    source_identifier=data.get("source_identifier", ""),
-                    metadata={"created_by": "season_operations_ui"},
-                )
-                messages.success(self.request, "Player transferred.")
-            elif data["action"] == PlayerMembershipTransferForm.ACTION_ADDITIONAL:
-                create_membership(
-                    player=self.membership.player,
-                    season_team=data["season_team"],
-                    status=RosterStatus.GUEST,
-                    jersey_number=data.get("jersey_number", ""),
-                    is_primary=False,
-                    is_active=True,
-                    starts_on=data.get("transfer_date"),
-                    source=data.get("source", ""),
-                    source_identifier=data.get("source_identifier", ""),
-                    sync_player_fields=True,
-                )
-                messages.success(self.request, "Additional membership created.")
-            else:
-                raise ValidationError("Unsupported membership action.")
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        return redirect("seasons:player-history", player_id=self.membership.player_id)
-
-
-class PlayerSeasonHistoryView(SeasonOperationsStaffRequiredMixin, TemplateView):
-    template_name = "seasons/player_history.html"
-
-    def dispatch(self, request, *args, **kwargs):
-        self.player = get_object_or_404(Player, pk=kwargs["player_id"])
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        memberships = (
-            PlayerRosterMembership.objects.select_related("season_team", "season_team__season")
-            .filter(player=self.player)
-            .order_by("-season_team__season__starts_on", "-season_team__season__is_current", "season_team__division", "season_team__name", "-starts_on", "id")
-        )
-        context.update({"player": self.player, "memberships": memberships})
-        return context
-
-
-class CoachAssignmentListView(SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView):
-    model = CoachSeasonAssignment
-    template_name = "seasons/assignment_list.html"
-    context_object_name = "assignments"
-    paginate_by = 50
-
-    def get_queryset(self):
-        queryset = CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season", "user__account_profile")
-        season_id = _clean_int(self.request.GET.get("season"))
-        team_id = _clean_int(self.request.GET.get("team"))
-        active = self.request.GET.get("active")
-        search = self.request.GET.get("q", "").strip()
-        if season_id:
-            queryset = queryset.filter(season_team__season_id=season_id)
-        if team_id:
-            queryset = queryset.filter(season_team_id=team_id)
-        if active == "yes":
-            queryset = queryset.filter(is_active=True)
-        elif active == "no":
-            queryset = queryset.filter(is_active=False)
-        if search:
-            queryset = queryset.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | Q(user__username__icontains=search))
-        return queryset.order_by("-season_team__season__is_current", "season_team__season__name", "user__last_name", "user__first_name", "id")
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context.update(
-            {
-                "seasons": Season.objects.order_by("-is_current", "-starts_on", "name"),
-                "teams": SeasonTeam.objects.select_related("season").order_by("-season__is_current", "season__name", "division", "name"),
-                "filters": {
-                    "season": self.request.GET.get("season", ""),
-                    "team": self.request.GET.get("team", ""),
-                    "active": self.request.GET.get("active", ""),
-                    "q": self.request.GET.get("q", ""),
-                },
-            }
-        )
-        return context
-
-
-class CoachAssignmentCreateView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/assignment_form.html"
-    form_class = CoachSeasonAssignmentForm
-
-    def form_valid(self, form):
-        data = form.cleaned_data
-        try:
-            assignment = create_assignment(
-                user=data["user"],
-                season_team=data["season_team"],
-                assignment_role=data["assignment_role"],
-                is_primary=data.get("is_primary", False),
-                is_active=data.get("is_active", False),
-                starts_on=data.get("starts_on"),
-                ends_on=data.get("ends_on"),
-                source=data.get("source", ""),
-                source_identifier=data.get("source_identifier", ""),
-            )
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Coach assignment created.")
-        return redirect("seasons:coach-history", user_id=assignment.user_id)
-
-
-class CoachAssignmentEditView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/assignment_form.html"
-    form_class = CoachSeasonAssignmentForm
-
-    def dispatch(self, request, *args, **kwargs):
-        self.assignment = get_object_or_404(
-            CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season"),
-            pk=kwargs["assignment_id"],
-        )
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_form_kwargs(self):
-        kwargs = super().get_form_kwargs()
-        kwargs["fixed_season"] = self.assignment.season
-        kwargs["editing"] = True
-        return kwargs
-
-    def get_initial(self):
-        return {
-            "user": self.assignment.user,
-            "season_team": self.assignment.season_team,
-            "assignment_role": self.assignment.assignment_role,
-            "is_primary": self.assignment.is_primary,
-            "is_active": self.assignment.is_active,
-            "starts_on": self.assignment.starts_on,
-            "ends_on": self.assignment.ends_on,
-            "source": self.assignment.source,
-            "source_identifier": self.assignment.source_identifier,
-        }
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["assignment"] = self.assignment
-        return context
-
-    def form_valid(self, form):
-        data = form.cleaned_data
-        original_flags = (self.assignment.user.is_staff, self.assignment.user.is_superuser, self.assignment.user.password)
-        try:
-            update_assignment(
-                self.assignment,
-                assignment_role=data["assignment_role"],
-                is_primary=data.get("is_primary", False),
-                is_active=data.get("is_active", False),
-                starts_on=data.get("starts_on"),
-                ends_on=data.get("ends_on"),
-                source=data.get("source", ""),
-                source_identifier=data.get("source_identifier", ""),
-            )
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        self.assignment.user.refresh_from_db()
-        if original_flags != (self.assignment.user.is_staff, self.assignment.user.is_superuser, self.assignment.user.password):
-            raise ValidationError("Coach assignment updates must not change account privileges or password state.")
-        messages.success(self.request, "Coach assignment updated.")
-        return redirect("seasons:coach-history", user_id=self.assignment.user_id)
-
-
-class CoachAssignmentEndView(SeasonOperationsStaffRequiredMixin, FormView):
-    template_name = "seasons/assignment_end.html"
-    form_class = CoachAssignmentEndForm
-
-    def dispatch(self, request, *args, **kwargs):
-        self.assignment = get_object_or_404(
-            CoachSeasonAssignment.objects.select_related("user", "season_team", "season_team__season"),
-            pk=kwargs["assignment_id"],
-        )
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        context["assignment"] = self.assignment
-        return context
-
-    def form_valid(self, form):
-        try:
-            deactivate_assignment(self.assignment, ends_on=form.cleaned_data.get("ends_on"))
-        except ValidationError as exc:
-            form.add_error(None, exc)
-            return self.form_invalid(form)
-        messages.success(self.request, "Coach assignment ended.")
-        return redirect("seasons:coach-history", user_id=self.assignment.user_id)
-
-
-class CoachSeasonHistoryView(SeasonOperationsStaffRequiredMixin, TemplateView):
-    template_name = "seasons/coach_history.html"
-
-    def dispatch(self, request, *args, **kwargs):
-        User = CoachSeasonAssignment._meta.get_field("user").remote_field.model
-        self.coach = get_object_or_404(User, pk=kwargs["user_id"])
-        if not hasattr(self.coach, "account_profile") or self.coach.account_profile.role != "coach":
-            raise Http404("Coach not found.")
-        return super().dispatch(request, *args, **kwargs)
-
-    def get_context_data(self, **kwargs):
-        context = super().get_context_data(**kwargs)
-        assignments = (
-            CoachSeasonAssignment.objects.select_related("season_team", "season_team__season")
-            .filter(user=self.coach)
-            .order_by("-season_team__season__starts_on", "-season_team__season__is_current", "season_team__division", "season_team__name", "-starts_on", "id")
-        )
-        context.update({"coach": self.coach, "assignments": assignments})
-        return context
diff --git a/seasons/views/__init__.py b/seasons/views/__init__.py
new file mode 100644
index 0000000..5679865
--- /dev/null
+++ b/seasons/views/__init__.py
@@ -0,0 +1,49 @@
+from seasons.views.assignments import (
+    CoachAssignmentCreateView,
+    CoachAssignmentEditView,
+    CoachAssignmentEndView,
+    CoachAssignmentListView,
+    CoachSeasonHistoryView,
+)
+from seasons.views.memberships import (
+    PlayerMembershipCreateView,
+    PlayerMembershipEditView,
+    PlayerMembershipEndView,
+    PlayerMembershipListView,
+    PlayerMembershipTransferView,
+    PlayerSeasonHistoryView,
+)
+from seasons.views.seasons import (
+    SeasonCreateView,
+    SeasonDetailView,
+    SeasonEditView,
+    SeasonListView,
+    SeasonSetCurrentView,
+)
+from seasons.views.teams import (
+    SeasonTeamCreateView,
+    SeasonTeamEditView,
+    SeasonTeamListView,
+)
+
+__all__ = [
+    "CoachAssignmentCreateView",
+    "CoachAssignmentEditView",
+    "CoachAssignmentEndView",
+    "CoachAssignmentListView",
+    "CoachSeasonHistoryView",
+    "PlayerMembershipCreateView",
+    "PlayerMembershipEditView",
+    "PlayerMembershipEndView",
+    "PlayerMembershipListView",
+    "PlayerMembershipTransferView",
+    "PlayerSeasonHistoryView",
+    "SeasonCreateView",
+    "SeasonDetailView",
+    "SeasonEditView",
+    "SeasonListView",
+    "SeasonSetCurrentView",
+    "SeasonTeamCreateView",
+    "SeasonTeamEditView",
+    "SeasonTeamListView",
+]
diff --git a/seasons/views/assignments.py b/seasons/views/assignments.py
new file mode 100644
index 0000000..c35dcad
--- /dev/null
+++ b/seasons/views/assignments.py
@@ -0,0 +1,199 @@
+from __future__ import annotations
+
+from django.contrib import messages
+from django.core.exceptions import ValidationError
+from django.http import Http404
+from django.shortcuts import get_object_or_404, redirect
+from django.views.generic import FormView, ListView, TemplateView
+
+from seasons.forms import CoachAssignmentEndForm, CoachSeasonAssignmentForm
+from seasons.models import CoachSeasonAssignment
+from seasons.services.coach_assignment_service import (
+    create_assignment,
+    deactivate_assignment,
+    update_assignment,
+)
+from seasons.services.season_query_service import (
+    assignment_list_queryset,
+    coach_history_assignment_queryset,
+    season_options_queryset,
+    team_options_queryset,
+)
+from seasons.views.mixins import (
+    SeasonOperationsStaffRequiredMixin,
+    SeasonPaginationMixin,
+)
+
+
+class CoachAssignmentListView(
+    SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView
+):
+    model = CoachSeasonAssignment
+    template_name = "seasons/assignment_list.html"
+    context_object_name = "assignments"
+    paginate_by = 50
+
+    def get_queryset(self):
+        return assignment_list_queryset(self.request.GET)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context.update(
+            {
+                "seasons": season_options_queryset(),
+                "teams": team_options_queryset(),
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
+            CoachSeasonAssignment.objects.select_related(
+                "user", "season_team", "season_team__season"
+            ),
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
+        original_flags = (
+            self.assignment.user.is_staff,
+            self.assignment.user.is_superuser,
+            self.assignment.user.password,
+        )
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
+        if original_flags != (
+            self.assignment.user.is_staff,
+            self.assignment.user.is_superuser,
+            self.assignment.user.password,
+        ):
+            raise ValidationError(
+                "Coach assignment updates must not change account privileges or password state."
+            )
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
+            CoachSeasonAssignment.objects.select_related(
+                "user", "season_team", "season_team__season"
+            ),
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
+            deactivate_assignment(
+                self.assignment, ends_on=form.cleaned_data.get("ends_on")
+            )
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
+        if (
+            not hasattr(self.coach, "account_profile")
+            or self.coach.account_profile.role != "coach"
+        ):
+            raise Http404("Coach not found.")
+        return super().dispatch(request, *args, **kwargs)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        assignments = coach_history_assignment_queryset(self.coach)
+        context.update({"coach": self.coach, "assignments": assignments})
+        return context
diff --git a/seasons/views/memberships.py b/seasons/views/memberships.py
new file mode 100644
index 0000000..be1b7c5
--- /dev/null
+++ b/seasons/views/memberships.py
@@ -0,0 +1,255 @@
+from __future__ import annotations
+
+from django.contrib import messages
+from django.core.exceptions import PermissionDenied, ValidationError
+from django.shortcuts import get_object_or_404, redirect
+from django.views.generic import FormView, ListView, TemplateView
+
+from players.models import Player
+from seasons.forms import (
+    PlayerMembershipEndForm,
+    PlayerMembershipTransferForm,
+    PlayerRosterMembershipForm,
+)
+from seasons.models import PlayerRosterMembership, RosterStatus
+from seasons.services.membership_service import (
+    create_membership,
+    deactivate_membership,
+    transfer_player,
+    update_membership,
+)
+from seasons.services.season_query_service import (
+    membership_list_queryset,
+    player_history_membership_queryset,
+    season_options_queryset,
+    team_options_queryset,
+)
+from seasons.views.mixins import (
+    SeasonOperationsStaffRequiredMixin,
+    SeasonPaginationMixin,
+)
+
+
+class PlayerMembershipListView(
+    SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView
+):
+    model = PlayerRosterMembership
+    template_name = "seasons/membership_list.html"
+    context_object_name = "memberships"
+    paginate_by = 50
+
+    def get_queryset(self):
+        return membership_list_queryset(self.request.GET)
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context.update(
+            {
+                "seasons": season_options_queryset(),
+                "teams": team_options_queryset(),
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
+            PlayerRosterMembership.objects.select_related(
+                "player", "season_team", "season_team__season"
+            ),
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
+            PlayerRosterMembership.objects.select_related(
+                "player", "season_team", "season_team__season"
+            ),
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
+            PlayerRosterMembership.objects.select_related(
+                "player", "season_team", "season_team__season"
+            ),
+            pk=kwargs["membership_id"],
+        )
+        if not self.membership.is_active:
+            raise PermissionDenied(
+                "Only active memberships can be transferred or extended."
+            )
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
+        memberships = player_history_membership_queryset(self.player)
+        context.update({"player": self.player, "memberships": memberships})
+        return context
diff --git a/seasons/views/mixins.py b/seasons/views/mixins.py
new file mode 100644
index 0000000..7d43bc7
--- /dev/null
+++ b/seasons/views/mixins.py
@@ -0,0 +1,20 @@
+from __future__ import annotations
+
+from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
+
+from accounts.services.permissions import is_staff_or_admin
+
+
+class SeasonOperationsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
+    def test_func(self):
+        return is_staff_or_admin(self.request.user)
+
+
+class SeasonPaginationMixin:
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        query = self.request.GET.copy()
+        query.pop("page", None)
+        encoded = query.urlencode()
+        context["pagination_query"] = f"{encoded}&" if encoded else ""
+        return context
diff --git a/seasons/views/seasons.py b/seasons/views/seasons.py
new file mode 100644
index 0000000..a92e0ac
--- /dev/null
+++ b/seasons/views/seasons.py
@@ -0,0 +1,116 @@
+from __future__ import annotations
+
+from django.contrib import messages
+from django.core.exceptions import PermissionDenied, ValidationError
+from django.shortcuts import get_object_or_404, redirect
+from django.views.generic import FormView, ListView, TemplateView
+
+from seasons.forms import ConfirmCurrentSeasonForm, SeasonForm
+from seasons.models import Season
+from seasons.services.season_query_service import (
+    season_detail_team_queryset,
+    season_list_queryset,
+)
+from seasons.services.season_service import (
+    create_season,
+    set_current_season,
+    update_season,
+)
+from seasons.views.mixins import (
+    SeasonOperationsStaffRequiredMixin,
+    SeasonPaginationMixin,
+)
+
+
+class SeasonListView(
+    SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView
+):
+    model = Season
+    template_name = "seasons/season_list.html"
+    context_object_name = "seasons"
+    paginate_by = 50
+
+    def get_queryset(self):
+        return season_list_queryset()
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
+        context.update(
+            {"season": self.season, "teams": season_detail_team_queryset(self.season)}
+        )
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
diff --git a/seasons/views/teams.py b/seasons/views/teams.py
new file mode 100644
index 0000000..542150e
--- /dev/null
+++ b/seasons/views/teams.py
@@ -0,0 +1,119 @@
+from __future__ import annotations
+
+from django.contrib import messages
+from django.core.exceptions import ValidationError
+from django.shortcuts import get_object_or_404, redirect
+from django.views.generic import FormView, ListView
+
+from seasons.forms import SeasonTeamForm
+from seasons.models import Season, SeasonTeam
+from seasons.services.season_query_service import (
+    season_options_queryset,
+    team_list_queryset,
+)
+from seasons.services.team_service import get_or_create_season_team, update_season_team
+from seasons.views.mixins import (
+    SeasonOperationsStaffRequiredMixin,
+    SeasonPaginationMixin,
+)
+
+
+class SeasonTeamListView(
+    SeasonOperationsStaffRequiredMixin, SeasonPaginationMixin, ListView
+):
+    model = SeasonTeam
+    template_name = "seasons/team_list.html"
+    context_object_name = "teams"
+    paginate_by = 50
+
+    def get_queryset(self):
+        return team_list_queryset(season_id=self.request.GET.get("season"))
+
+    def get_context_data(self, **kwargs):
+        context = super().get_context_data(**kwargs)
+        context["seasons"] = season_options_queryset()
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
+            kwargs["fixed_season"] = get_object_or_404(
+                Season, pk=season_id, is_active=True
+            )
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
+        messages.success(
+            self.request,
+            "Season team created." if created else "Existing season team reused.",
+        )
+        return redirect("seasons:team-list")
+
+
+class SeasonTeamEditView(SeasonOperationsStaffRequiredMixin, FormView):
+    template_name = "seasons/team_form.html"
+    form_class = SeasonTeamForm
+
+    def dispatch(self, request, *args, **kwargs):
+        self.team = get_object_or_404(
+            SeasonTeam.objects.select_related("season"), pk=kwargs["team_id"]
+        )
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
```
