# Prompt 89 - Accounts

## User Prompt

```text
Perform Repository Cleanup Phase 7 only: Account Operations Service Refactor.

Use continuous loop engineering.

Continue until the account-operations service is structurally cleaner, behavior remains unchanged, focused and full verification pass, commits are pushed, and the working tree is clean.

Do not change account-management product behavior.

Do not add new account actions, fields, permissions, screens, models, migrations, emails, or features.

Do not begin the final repository audit or Platform V2 work.

==================================================
Current State
=============

Repository Cleanup Phases 1 through 6 are complete.

Current repository state includes:

* reconciled documentation;
* Django 4.2.30;
* Ruff, Black, isort, and pre-commit;
* touched-files-only formatting policy;
* refactored player import service;
* refactored coach import service;
* refactored Season Operations views and query layer;
* focused test packages for accounts, analytics, seasons, and players;
* full test baseline preserved at 458 tests.

Seasonal Participation V1 remains Feature Complete, Production Ready, and Frozen.

The main remaining large mixed-responsibility production module identified during the repository review is:

```text
accounts/services/account_operations_service.py
```

It currently coordinates several distinct areas such as:

* account creation;
* player account creation;
* account editing;
* activation and deactivation;
* password-reset operations;
* password-change requirement operations;
* user-player link operations;
* account detail and list read models;
* operations dashboard data;
* bulk account operations;
* partial-failure reporting;
* privileged-account safety rules.

The objective is a behavior-preserving structural refactor.

==================================================
Objective
=========

Reduce the size and mixed responsibilities of:

```text
accounts/services/account_operations_service.py
```

Split cohesive responsibilities into focused internal modules while preserving a small, stable public façade for all current callers.

The refactor must improve maintainability without changing:

* account creation behavior;
* player-account provisioning behavior;
* account-edit behavior;
* activation/deactivation behavior;
* password-reset behavior;
* password-change requirement behavior;
* user-player link behavior;
* bulk-operation behavior;
* permissions;
* privileged-account safeguards;
* partial-failure behavior;
* result objects;
* validation messages;
* views;
* forms;
* templates;
* routes;
* redirects;
* user-visible messages.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete refactoring, regression-proofing, documentation, or verification work remains.

PASS

All Phase 7 acceptance criteria are satisfied, tests and tooling pass, commits are pushed, and the working tree is clean.

BLOCKED

The service cannot be decomposed safely without unresolved behavior changes, migration changes, or scope expansion.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied criterion.

Moving code between files without clearer responsibility does not count as progress.

==================================================
Established Loop Workflow
=========================

Every loop must:

1. reconcile the committed repository state;
2. read `AGENTS.md`;
3. read current Account Management documentation;
4. confirm the working tree is clean;
5. inspect the complete account-operations workflow and every service caller;
6. inventory the public API exposed by `account_operations_service.py`;
7. identify one cohesive refactoring boundary;
8. create the next prompt archive before implementation;
9. refactor only the selected account-operations concern;
10. preserve or add focused regression tests;
11. run tooling on touched files only;
12. run focused verification;
13. perform senior-engineer self-review;
14. fix every verified issue;
15. update architecture or Account Management implementation documentation only if ownership materially changes;
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
* `docs/account_management/V1_SUMMARY.md`
* relevant Account Management implementation plans and status documents;
* relevant prompt archives for:

  * account creation;
  * account provisioning;
  * user-player links;
  * account activation/deactivation;
  * password reset;
  * bulk account operations;
  * account test split;
  * coach import refactor.

Inspect:

* `accounts/services/account_operations_service.py`
* every import from `accounts.services.account_operations_service`
* `accounts/services/account_query_service.py`
* `accounts/services/profile_service.py`
* `accounts/services/role_service.py`
* `accounts/services/password_service.py`
* `accounts/services/link_service.py`
* `accounts/services/provisioning_service.py`
* `accounts/services/permissions.py`
* `accounts/forms.py`
* `accounts/views.py`
* `accounts/models.py`
* account operation templates;
* `accounts/tests/`
* relevant Analytics and player callers;
* relevant migrations only for dependency understanding.

==================================================
Public API Preservation
=======================

Inventory every public constant, dataclass, function, and result type imported from:

```text
accounts.services.account_operations_service
```

Preserve existing import paths wherever practical.

Preferred approach:

* convert `accounts/services/account_operations_service.py` into a focused public façade;
* move internal implementations into a package;
* re-export existing public functions and data contracts.

Suggested structure:

```text
accounts/services/account_operations/
    __init__.py
    result_models.py
    creation.py
    updates.py
    lifecycle.py
    passwords.py
    links.py
    bulk.py
    read_models.py
```

This is a suggested structure only.

Use actual responsibilities and dependencies to choose the smallest clear split.

Do not force a separate file for every function.

Views, forms, tests, and other apps should continue importing through the façade unless a clearly internal caller is intentionally updated.

==================================================
Recommended Responsibility Boundaries
=====================================

## 1. Result Models And Contracts

Move stable dataclasses and operation-result structures where practical.

Examples may include:

* bulk-operation result;
* per-account failure result;
* account detail read model;
* account list read model;
* dashboard result structures;
* password-reset result structures.

Preserve:

* field names;
* defaults;
* frozen/mutable behavior;
* equality behavior;
* public import paths.

Avoid circular imports.

## 2. Account Creation

Group operations such as:

* account-only creation;
* player-account creation;
* username validation;
* email validation;
* profile creation;
* role assignment;
* initial password behavior;
* optional player-link creation.

Continue delegating to existing authoritative services.

Do not duplicate:

* username rules;
* email matching;
* password rules;
* profile rules;
* role rules;
* player-link rules.

## 3. Account Updates

Group:

* account field updates;
* profile role updates;
* username/email changes;
* first/last-name changes;
* safety validation;
* privileged-account restrictions.

Preserve current rules around:

* staff;
* superuser;
* last active superuser;
* self-modification;
* established account roles.

## 4. Account Lifecycle

Group:

* activation;
* deactivation;
* safety checks;
* self-deactivation prevention;
* last-superuser protection;
* link effects if any;
* account state result reporting.

Do not change whether account deactivation affects seasonal assignments, player links, or historical records.

## 5. Password Operations

Group:

* administrative password reset;
* temporary-password generation;
* password-change requirement;
* password-change requirement clearing;
* one-time password return behavior;
* password privacy rules.

Continue delegating password mechanics to:

```text
accounts.services.password_service
```

Do not duplicate password-generation or hashing logic.

## 6. User-Player Link Operations

Group façade-level orchestration for:

* creating links;
* deactivating links;
* reactivating links;
* setting primary links;
* player-account creation with self-link;
* validation and result reporting.

Keep authoritative link rules in:

```text
accounts.services.link_service
```

Do not copy relationship invariants.

## 7. Bulk Operations

Group:

* bulk activation;
* bulk deactivation;
* bulk password-change requirement;
* bulk clearing of password-change requirement;
* per-row error collection;
* continued processing after partial failures;
* summary counts.

Preserve:

* supported action keys;
* processing order;
* partial-failure behavior;
* validation messages;
* safety rules;
* no bulk password reset.

Bulk operations should call the same authoritative single-account operations.

Do not create parallel business rules.

## 8. Read Models

Review account list, detail, and operations-dashboard functions.

Do not duplicate functionality already owned by:

```text
accounts.services.account_query_service
```

Possible outcomes:

* keep public read functions as façade adapters;
* move account detail/dashboard assembly into a focused read-model module;
* delegate filtering and list query construction to `account_query_service`.

Do not create a generic repository layer.

==================================================
Behavioral Freeze
=================

The following behavior must remain unchanged.

## Account Creation

* username requirements;
* email validation;
* account profile creation;
* account role behavior;
* activation behavior;
* temporary-password behavior;
* forced password-change behavior;
* optional player association;
* duplicate username/email handling.

## Player Account Creation

* permanent account reuse rules;
* self-link creation;
* primary-link behavior;
* player validation;
* temporary-password behavior;
* conflict behavior.

## Account Update

* editable fields;
* role-change behavior;
* staff/superuser safeguards;
* username/email validation;
* profile preservation;
* messages and errors consumed by views.

## Activation And Deactivation

* self-deactivation remains blocked;
* last active superuser protection remains;
* reactivation behavior remains;
* account history remains;
* seasonal assignments are not deleted;
* user-player links behave exactly as currently defined.

## Passwords

* random temporary-password behavior;
* password hash handling;
* `must_change_password` behavior;
* one-time display behavior;
* no password exposure after the operation result is gone;
* no password reset during unrelated account operations.

## Links

* relationship choices;
* primary self-link constraints;
* active/inactive behavior;
* duplicate prevention;
* link-history behavior;
* permanent player identity behavior.

## Bulk Operations

Preserve supported actions:

* Activate;
* Deactivate;
* Require password change;
* Clear password change.

Preserve:

* no bulk password reset;
* per-account processing;
* partial failures;
* self-deactivation safeguard;
* last-superuser safeguard;
* success/failure counts;
* user-facing result messages.

## Permissions

Do not change:

* who may view account operations;
* who may create accounts;
* who may modify roles;
* who may manage privileged accounts;
* who may reset passwords;
* object-level account access.

==================================================
No New Account Framework
========================

Do not create an abstract command bus, generic operation framework, event system, or plugin architecture.

This is a straightforward module decomposition.

Prefer explicit functions and focused modules.

Do not refactor unrelated account services merely to fit a new abstraction.

==================================================
Transaction Review
==================

Before moving code, inventory current transaction boundaries.

Preserve:

* account creation atomicity;
* player-account plus link atomicity;
* role/profile update atomicity;
* password-reset transaction behavior;
* activation/deactivation behavior;
* bulk operation per-account isolation;
* partial-failure continuation.

Do not widen a single-account transaction across the whole bulk operation.

Do not narrow transactions in a way that leaves:

* an account without its expected profile;
* a player account without its intended link;
* inconsistent profile and user state;
* partially applied role or password state.

Any transaction change requires:

* a verified defect;
* explicit regression coverage;
* documentation in the prompt archive.

==================================================
Dependency Direction
====================

Preferred dependency direction:

```text
views/forms
    ->
accounts.services.account_operations_service façade
    ->
accounts.services.account_operations internal modules
    ->
existing profile/role/password/link/query/username/email services
    ->
models
```

Internal operation modules must not import:

* views;
* forms;
* templates.

Avoid mutual imports between operation modules.

Bulk operations should depend on public single-account operation functions or a stable internal application layer—not copy their validation.

Read-model modules should not depend on write-operation modules unless strictly necessary.

==================================================
Tests
=====

Preserve the existing 194-account-test baseline.

Current full project baseline:

```text
458 tests
```

Preserve existing tests in:

```text
accounts/tests/
```

Add focused tests only where the decomposition exposes an untested public contract.

Useful contract tests may include:

* all façade exports remain importable;
* account creation output remains stable;
* player account and self-link remain atomic;
* update result behavior remains stable;
* self-deactivation remains blocked;
* last active superuser cannot be deactivated;
* password reset returns a temporary password exactly once;
* password-change flags behave unchanged;
* bulk operations reuse single-account rules;
* bulk partial failures do not stop valid remaining accounts;
* no bulk password reset action exists;
* read-model field names remain unchanged.

Do not rewrite the account tests simply because internal modules moved.

Tests should primarily call:

* the public façade;
* account views;
* existing operation forms.

Avoid testing private module structure unless verifying the façade contract.

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

* dead private functions;
* duplicate validation;
* obsolete imports;
* stale comments;
* compatibility wrappers with no callers;
* repeated result assembly where a stable data contract already exists.

Keep:

* explicit function names;
* clear result types;
* authoritative service delegation;
* meaningful transaction boundaries;
* no signals;
* no hidden side effects.

==================================================
Documentation
=============

Update documentation only if needed to describe the new internal Account Operations layout.

Potential documents:

* `docs/ARCHITECTURE.md`
* `docs/account_management/V1_SUMMARY.md`
* current Account Management implementation status documentation.

Do not update the user manual because user-facing behavior must remain unchanged.

Do not describe the refactor as a product feature.

==================================================
Scope Restrictions
==================

Do not:

* modify models;
* create migrations;
* change forms except import paths if unavoidable;
* change views except import paths if unavoidable;
* change templates;
* change URLs;
* change permissions;
* change messages intentionally;
* change supported bulk actions;
* add bulk password reset;
* change password-generation rules;
* change user-player relationship rules;
* change account role semantics;
* change Django staff/superuser semantics;
* refactor coach import again;
* refactor player import again;
* refactor Season Operations again;
* reorganize tests again;
* add APIs;
* add JavaScript;
* add background jobs;
* add notifications;
* bulk-format the repository;
* regenerate the project flat-file snapshot;
* begin Platform V2.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test python manage.py test accounts
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_account_operations
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_account_services
DJANGO_SECRET_KEY=test python manage.py test accounts players seasons analytics
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

* public API drift;
* changed result dataclasses;
* changed error messages;
* permission drift;
* privilege escalation;
* password exposure;
* password hash changes during unrelated operations;
* self-deactivation regressions;
* last-superuser regressions;
* player-link regressions;
* transaction-boundary drift;
* orphan accounts;
* profile/user inconsistency;
* bulk-operation behavior drift;
* partial-failure drift;
* circular imports;
* duplicated rules;
* unnecessary abstractions;
* formatting churn;
* stale documentation.

Fix every verified issue before committing.

==================================================
Acceptance Criteria
===================

Do not declare PASS until all criteria are satisfied.

A. Structure

* `account_operations_service.py` is materially smaller;
* cohesive responsibilities are separated;
* public imports remain stable where practical;
* callers do not depend on deep internal modules.

B. Account Creation

* account-only creation remains unchanged;
* player-account creation remains unchanged;
* profile and role behavior remain unchanged;
* temporary-password behavior remains unchanged.

C. Updates And Lifecycle

* account updates remain unchanged;
* activation/deactivation remain unchanged;
* self-deactivation remains blocked;
* last-active-superuser protection remains.

D. Password Safety

* password reset remains explicit;
* unrelated operations never change password hashes;
* password-change requirement behavior remains unchanged;
* one-time password behavior remains unchanged.

E. Links

* player-link creation/deactivation/reactivation remains unchanged;
* primary-link rules remain unchanged;
* account/player identity remains permanent.

F. Bulk Operations

* supported actions remain unchanged;
* single-account services remain authoritative;
* partial failures remain isolated;
* no bulk password reset is introduced;
* result counts and messages remain unchanged.

G. Read Models

* list, detail, and dashboard contracts remain unchanged;
* query logic is not duplicated unnecessarily;
* no generic repository abstraction is introduced.

H. Transactions And Integrity

* transaction boundaries remain equivalent;
* no orphan accounts;
* no profile/user inconsistency;
* no incomplete player links;
* bulk isolation remains intact.

I. Quality

* no circular imports;
* no duplicated business rules;
* no dead code;
* touched files pass Ruff, Black, and isort;
* no unrelated formatting churn.

J. Tests

* account suite remains at 194 tests unless a documented regression test is added;
* full suite remains at least 458 tests;
* focused suites pass;
* full suite passes.

K. Migration

* no model changes;
* no migrations;
* migration checks pass.

L. Documentation

* internal architecture documentation updated only if needed;
* user-facing documentation remains unchanged.

M. Git

* refactor commit exists;
* prompt archive commit exists;
* both pushed;
* working tree is clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally:

1. inventory every public façade export and caller;
2. create a focused `accounts.services.account_operations` package;
3. move result contracts;
4. split creation and account-update behavior;
5. split lifecycle and password operations;
6. split link and bulk orchestration;
7. reconcile read-model ownership with `account_query_service`;
8. preserve the façade;
9. remove obsolete code from the original module;
10. run tooling and focused/full verification;
11. update minimal architecture documentation if warranted;
12. commit, archive, push, and reassess.

If the safe decomposition is too large, continue with another cohesive loop.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* materially reduces mixed responsibilities;
* removes verified duplication;
* clarifies authoritative service ownership;
* strengthens transaction or password-safety proof;
* improves maintainability without behavior change;
* adds missing public-contract regression coverage.

Moving functions into arbitrary files does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* administrator creating accounts;
* administrator updating roles;
* administrator resetting passwords;
* administrator running bulk operations;
* player receiving a linked account;
* security reviewer checking privileged accounts;
* developer maintaining account queries;
* tester diagnosing a partial bulk failure.

Confirm:

* the service is easier to navigate;
* public behavior is unchanged;
* password and privilege boundaries remain safe;
* bulk operations still use authoritative single-account rules;
* no unrelated subsystem was changed;
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
   * account creation behavior;
   * lifecycle behavior;
   * password findings;
   * link behavior;
   * bulk-operation behavior;
   * transaction findings;
   * tests added or changed;
   * tooling results;
   * focused verification;
   * full verification;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested implementation commit:

```text
Refactor account operations service
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
* account creation behavior;
* account update behavior;
* lifecycle behavior;
* password behavior;
* user-player link behavior;
* bulk-operation behavior;
* read-model behavior;
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

`ecc8fe1` - Refactor account operations service

## Old Module Structure

```text
accounts/services/account_operations_service.py
```

## New Module Structure

```text
accounts/services/account_operations_service.py    # public facade
accounts/services/account_operations/
    __init__.py
    bulk.py
    contracts.py
    creation.py
    lifecycle.py
    links.py
    passwords.py
    read_models.py
    shared.py
    updates.py
```

## Public API Preservation

Existing callers continue to import through `accounts.services.account_operations_service`. The facade re-exports the same public dataclasses, constants, and functions used by forms, views, and tests.

## Account Creation Behavior

Account-only creation and player-account creation moved to `accounts.services.account_operations.creation`. The code still delegates username validation, email validation, profile role updates, temporary-password behavior, and player provisioning to the existing authoritative services.

## Account Update And Lifecycle Behavior

Account updates moved to `updates.py`; activation and deactivation moved to `lifecycle.py`. Existing staff/superuser safeguards, self-deactivation protection, and last-active-superuser protection are preserved through shared validation helpers.

## Password Findings

Password reset and password-change requirement operations moved to `passwords.py`. Password generation and password setting still delegate to `accounts.services.password_service`, and temporary passwords remain returned only through operation result objects.

## Link Behavior

User-player link orchestration moved to `links.py`. Authoritative relationship, activation, deactivation, and primary-link rules remain in `accounts.services.link_service`.

## Bulk-Operation Behavior

Bulk orchestration moved to `bulk.py`. Supported bulk actions are unchanged, no bulk password reset action was added, and bulk operations continue to call the single-account lifecycle/password functions per account so partial failures remain isolated.

## Read-Model Behavior

Dashboard, account list, and account detail assembly moved to `read_models.py`. Query filtering and list construction still delegate to `accounts.services.account_query_service`.

## Transaction Findings

Single-account transaction boundaries remain on the same public operations: account creation, player-account creation, account update, activate/deactivate, link operations, password reset, and password-change requirement changes. Bulk operations still do not wrap all selected accounts in one transaction.

## Tests Changed

No tests were modified. Existing account operation and account service tests covered the facade and behavior after decomposition.

## Tooling Results

```text
pre-commit run --files accounts/services/account_operations_service.py accounts/services/account_operations/__init__.py accounts/services/account_operations/contracts.py accounts/services/account_operations/shared.py accounts/services/account_operations/read_models.py accounts/services/account_operations/updates.py accounts/services/account_operations/lifecycle.py accounts/services/account_operations/links.py accounts/services/account_operations/passwords.py accounts/services/account_operations/bulk.py accounts/services/account_operations/creation.py docs/prompts/prompt_89_accounts.md
```

Result: passed.

## Focused Verification

```text
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_account_operations
DJANGO_SECRET_KEY=test python manage.py test accounts.tests.test_account_services
DJANGO_SECRET_KEY=test python manage.py test accounts
DJANGO_SECRET_KEY=test python manage.py test accounts players seasons analytics
git diff --check
```

Result: all checks passed. Account suite remained at 194 tests. Cross-app regression suite ran 417 tests successfully.

## Full Verification

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
commit ecc8fe14017ea07a20747a9a597c1529a5d6fd2c
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Thu Jul 16 13:13:12 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Thu Jul 16 13:13:12 2026 -0700

    Refactor account operations service
---
 accounts/services/account_operations/__init__.py   |   1 +
 accounts/services/account_operations/bulk.py       | 103 +++
 accounts/services/account_operations/contracts.py  | 126 ++++
 accounts/services/account_operations/creation.py   | 111 ++++
 accounts/services/account_operations/lifecycle.py  |  34 +
 accounts/services/account_operations/links.py      |  72 +++
 accounts/services/account_operations/passwords.py  |  58 ++
 .../services/account_operations/read_models.py     | 164 +++++
 accounts/services/account_operations/shared.py     | 124 ++++
 accounts/services/account_operations/updates.py    |  48 ++
 accounts/services/account_operations_service.py    | 707 +++------------------
 11 files changed, 921 insertions(+), 627 deletions(-)

diff --git a/accounts/services/account_operations/__init__.py b/accounts/services/account_operations/__init__.py
new file mode 100644
index 0000000..c07f741
--- /dev/null
+++ b/accounts/services/account_operations/__init__.py
@@ -0,0 +1 @@
+"""Internal modules for staff Account Operations orchestration."""
diff --git a/accounts/services/account_operations/bulk.py b/accounts/services/account_operations/bulk.py
new file mode 100644
index 0000000..4acfe4a
--- /dev/null
+++ b/accounts/services/account_operations/bulk.py
@@ -0,0 +1,103 @@
+from __future__ import annotations
+
+from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+
+from accounts.services.permissions import can_manage_accounts
+
+from .contracts import (
+    BULK_ACCOUNT_ACTIONS,
+    BULK_ACTION_ACTIVATE,
+    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
+    BULK_ACTION_DEACTIVATE,
+    BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
+    BulkOperationError,
+    BulkOperationResult,
+)
+from .lifecycle import activate_account, deactivate_account
+from .passwords import set_account_password_change_required
+
+User = get_user_model()
+
+
+def _clean_bulk_user_ids(user_ids):
+    clean_ids = []
+    seen = set()
+    for raw_user_id in user_ids or []:
+        raw_value = str(raw_user_id or "").strip()
+        if not raw_value or raw_value in seen:
+            continue
+        seen.add(raw_value)
+        try:
+            clean_ids.append(int(raw_value))
+        except (TypeError, ValueError):
+            clean_ids.append(raw_value)
+    return clean_ids
+
+
+def _bulk_error_username(user_id) -> str:
+    if isinstance(user_id, int):
+        username = (
+            User.objects.filter(pk=user_id).values_list("username", flat=True).first()
+        )
+        if username:
+            return username
+    return "Unknown account"
+
+
+def _validation_message(exc: ValidationError) -> str:
+    if hasattr(exc, "messages"):
+        return "; ".join(exc.messages)
+    return str(exc)
+
+
+def bulk_account_operation(*, actor, action: str, user_ids) -> BulkOperationResult:
+    """Apply a safe account operation to selected users and collect per-account failures."""
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can manage accounts.")
+    if action not in BULK_ACCOUNT_ACTIONS:
+        raise ValidationError("Unsupported bulk action.")
+
+    clean_user_ids = _clean_bulk_user_ids(user_ids)
+    if not clean_user_ids:
+        raise ValidationError("Select at least one account.")
+
+    successful = 0
+    errors = []
+    for user_id in clean_user_ids:
+        username = _bulk_error_username(user_id)
+        if not isinstance(user_id, int):
+            errors.append(
+                BulkOperationError(username=username, message="Account not found.")
+            )
+            continue
+        try:
+            if action == BULK_ACTION_ACTIVATE:
+                activate_account(actor=actor, user_id=user_id)
+            elif action == BULK_ACTION_DEACTIVATE:
+                deactivate_account(actor=actor, user_id=user_id)
+            elif action == BULK_ACTION_REQUIRE_PASSWORD_CHANGE:
+                set_account_password_change_required(
+                    actor=actor, user_id=user_id, required=True
+                )
+            elif action == BULK_ACTION_CLEAR_PASSWORD_CHANGE:
+                set_account_password_change_required(
+                    actor=actor, user_id=user_id, required=False
+                )
+        except User.DoesNotExist:
+            errors.append(
+                BulkOperationError(username=username, message="Account not found.")
+            )
+        except ValidationError as exc:
+            errors.append(
+                BulkOperationError(username=username, message=_validation_message(exc))
+            )
+        else:
+            successful += 1
+
+    return BulkOperationResult(
+        processed=len(clean_user_ids),
+        successful=successful,
+        failed=len(errors),
+        errors=errors,
+    )
diff --git a/accounts/services/account_operations/contracts.py b/accounts/services/account_operations/contracts.py
new file mode 100644
index 0000000..0d51e38
--- /dev/null
+++ b/accounts/services/account_operations/contracts.py
@@ -0,0 +1,126 @@
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+
+from django.contrib.auth import get_user_model
+
+from accounts.models import UserPlayerLink
+from accounts.services.account_query_service import AccountListFilters
+from players.models import Player
+
+User = get_user_model()
+
+
+@dataclass(frozen=True)
+class AccountSummaryCard:
+    label: str
+    value: int
+    help_text: str = ""
+    url: str = ""
+
+
+@dataclass(frozen=True)
+class AccountListRow:
+    user: User
+    role: str
+    role_label: str
+    linked_player_count: int
+    detail_url: str
+
+
+@dataclass(frozen=True)
+class LinkedPlayerRow:
+    link: UserPlayerLink
+    player: object
+    relationship: str
+    is_primary: bool
+    is_active: bool
+    created_from_import: bool
+    import_label: str
+
+
+@dataclass(frozen=True)
+class AccountOperationsDashboard:
+    summary_cards: list[AccountSummaryCard]
+    users_requiring_password_change: list[AccountListRow]
+    unlinked_users: list[AccountListRow]
+    players_without_self_link_count: int
+    generated_at: object
+
+
+@dataclass(frozen=True)
+class AccountListContext:
+    filters: AccountListFilters
+    rows: list[AccountListRow]
+    role_choices: tuple
+    total_count: int
+
+
+@dataclass(frozen=True)
+class AccountDetailContext:
+    user: User
+    role: str
+    role_label: str
+    linked_players: list[LinkedPlayerRow]
+
+
+@dataclass(frozen=True)
+class CreatedAccountResult:
+    user: User
+    username: str
+    temporary_password: str = field(repr=False)
+    role: str
+    role_label: str
+    player: Player | None = None
+
+
+@dataclass(frozen=True)
+class UpdatedAccountResult:
+    user: User
+    username: str
+    role: str
+    role_label: str
+    is_active: bool
+
+
+@dataclass(frozen=True)
+class UpdatedLinkResult:
+    link: UserPlayerLink
+    user: User
+    player: Player
+    relationship: str
+    is_primary: bool
+    is_active: bool
+
+
+@dataclass(frozen=True)
+class PasswordResetResult:
+    user: User
+    username: str
+    temporary_password: str = field(repr=False)
+
+
+BULK_ACTION_ACTIVATE = "activate"
+BULK_ACTION_DEACTIVATE = "deactivate"
+BULK_ACTION_REQUIRE_PASSWORD_CHANGE = "require_password_change"
+BULK_ACTION_CLEAR_PASSWORD_CHANGE = "clear_password_change"
+BULK_ACCOUNT_ACTIONS = {
+    BULK_ACTION_ACTIVATE,
+    BULK_ACTION_DEACTIVATE,
+    BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
+    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
+}
+
+
+@dataclass(frozen=True)
+class BulkOperationError:
+    username: str
+    message: str
+
+
+@dataclass(frozen=True)
+class BulkOperationResult:
+    processed: int
+    successful: int
+    failed: int
+    errors: list[BulkOperationError] = field(default_factory=list, repr=False)
diff --git a/accounts/services/account_operations/creation.py b/accounts/services/account_operations/creation.py
new file mode 100644
index 0000000..57b5184
--- /dev/null
+++ b/accounts/services/account_operations/creation.py
@@ -0,0 +1,111 @@
+from __future__ import annotations
+
+from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+from django.db import transaction
+
+from accounts.models import AccountRole
+from accounts.services.password_service import (
+    generate_birthdate_password,
+    mark_password_change_required,
+    set_random_temporary_password,
+)
+from accounts.services.profile_service import (
+    get_or_create_account_profile,
+    set_account_role,
+)
+from accounts.services.provisioning_service import (
+    STATUS_CREATED,
+    provision_player_account,
+)
+from accounts.services.role_service import role_label
+from accounts.services.username_service import validate_available_username
+from players.models import Player
+
+from .contracts import CreatedAccountResult
+from .shared import validate_actor_can_create_role, validate_email_available
+
+User = get_user_model()
+
+
+@transaction.atomic
+def create_account_only(
+    *,
+    actor,
+    username: str,
+    first_name: str = "",
+    last_name: str = "",
+    email: str = "",
+    role: str = AccountRole.GUEST_EVALUATOR,
+    is_active: bool = True,
+) -> CreatedAccountResult:
+    """Create a login account without creating or linking a player."""
+    validate_actor_can_create_role(actor, role)
+    username = validate_available_username(username)
+    normalized_email = validate_email_available(email)
+    user = User.objects.create(
+        username=username,
+        first_name=str(first_name or "").strip(),
+        last_name=str(last_name or "").strip(),
+        email=normalized_email,
+        is_active=bool(is_active),
+    )
+    temporary_password = set_random_temporary_password(user)
+    profile = get_or_create_account_profile(user)
+    if profile.created_from_import or profile.import_batch_id:
+        raise ValidationError("Manual accounts cannot use import provenance.")
+    set_account_role(user, role, actor=actor)
+    mark_password_change_required(user, True)
+    user.refresh_from_db()
+    return CreatedAccountResult(
+        user=user,
+        username=user.username,
+        temporary_password=temporary_password,
+        role=role,
+        role_label=role_label(role),
+    )
+
+
+@transaction.atomic
+def create_player_account(
+    *,
+    actor,
+    player,
+    username: str = "",
+    email: str = "",
+    role: str = AccountRole.PLAYER,
+    is_active: bool = True,
+) -> CreatedAccountResult:
+    """Create a login account for an existing canonical player."""
+    if not isinstance(player, Player):
+        raise ValidationError("A valid existing player is required.")
+    validate_actor_can_create_role(actor, role)
+    if role != AccountRole.PLAYER:
+        raise ValidationError(
+            "Player account creation must use the player role in Phase B."
+        )
+    normalized_email = validate_email_available(email)
+    result = provision_player_account(
+        player,
+        actor=actor,
+        email=normalized_email,
+        activate_user=bool(is_active),
+        username=username,
+    )
+    if result.status != STATUS_CREATED or not result.user_id:
+        message = (
+            "; ".join(result.messages)
+            if result.messages
+            else "Player account could not be created."
+        )
+        raise ValidationError(message)
+    user = User.objects.get(pk=result.user_id)
+    temporary_password = generate_birthdate_password(player)
+    return CreatedAccountResult(
+        user=user,
+        username=user.username,
+        temporary_password=temporary_password,
+        role=role,
+        role_label=role_label(role),
+        player=player,
+    )
diff --git a/accounts/services/account_operations/lifecycle.py b/accounts/services/account_operations/lifecycle.py
new file mode 100644
index 0000000..41baeac
--- /dev/null
+++ b/accounts/services/account_operations/lifecycle.py
@@ -0,0 +1,34 @@
+from __future__ import annotations
+
+from django.db import transaction
+
+from .contracts import UpdatedAccountResult
+from .shared import (
+    get_user_for_update,
+    updated_account_result,
+    validate_account_deactivation_allowed,
+    validate_actor_can_manage_target,
+)
+
+
+@transaction.atomic
+def activate_account(*, actor, user_id: int) -> UpdatedAccountResult:
+    """Activate an existing account without changing profile or link history."""
+    user = get_user_for_update(user_id)
+    validate_actor_can_manage_target(actor, user)
+    if not user.is_active:
+        user.is_active = True
+        user.save(update_fields=["is_active"])
+    return updated_account_result(user)
+
+
+@transaction.atomic
+def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
+    """Deactivate an existing account without deleting account data or links."""
+    user = get_user_for_update(user_id)
+    if user.is_active:
+        validate_account_deactivation_allowed(actor, user)
+        validate_actor_can_manage_target(actor, user)
+        user.is_active = False
+        user.save(update_fields=["is_active"])
+    return updated_account_result(user)
diff --git a/accounts/services/account_operations/links.py b/accounts/services/account_operations/links.py
new file mode 100644
index 0000000..5a80c3a
--- /dev/null
+++ b/accounts/services/account_operations/links.py
@@ -0,0 +1,72 @@
+from __future__ import annotations
+
+from django.db import transaction
+
+from accounts.services.link_service import (
+    activate_link,
+    deactivate_link,
+    link_user_to_player,
+    set_primary_self_link,
+    validate_no_active_relationship_conflict,
+)
+from players.models import Player
+
+from .contracts import UpdatedLinkResult
+from .shared import (
+    get_link_for_user,
+    get_user_for_update,
+    updated_link_result,
+    validate_actor_can_manage_target,
+)
+
+
+@transaction.atomic
+def create_user_player_link(
+    *,
+    actor,
+    user_id: int,
+    player: Player,
+    relationship: str,
+    is_primary: bool = False,
+) -> UpdatedLinkResult:
+    """Create an active user/player link through the account operations workflow."""
+    user = get_user_for_update(user_id)
+    validate_actor_can_manage_target(actor, user)
+    validate_no_active_relationship_conflict(user, player, relationship)
+    link = link_user_to_player(
+        user, player, relationship=relationship, is_primary=is_primary
+    )
+    return updated_link_result(link)
+
+
+@transaction.atomic
+def deactivate_user_player_link(
+    *, actor, user_id: int, link_id: int
+) -> UpdatedLinkResult:
+    """Deactivate a user/player link without deleting its history."""
+    user = get_user_for_update(user_id)
+    validate_actor_can_manage_target(actor, user)
+    link = get_link_for_user(user, link_id)
+    return updated_link_result(deactivate_link(link, actor=actor))
+
+
+@transaction.atomic
+def reactivate_user_player_link(
+    *, actor, user_id: int, link_id: int
+) -> UpdatedLinkResult:
+    """Reactivate an existing inactive user/player link when constraints allow it."""
+    user = get_user_for_update(user_id)
+    validate_actor_can_manage_target(actor, user)
+    link = get_link_for_user(user, link_id)
+    return updated_link_result(activate_link(link, actor=actor))
+
+
+@transaction.atomic
+def set_primary_user_player_link(
+    *, actor, user_id: int, link_id: int
+) -> UpdatedLinkResult:
+    """Set an existing self link as the active primary player link."""
+    user = get_user_for_update(user_id)
+    validate_actor_can_manage_target(actor, user)
+    link = get_link_for_user(user, link_id)
+    return updated_link_result(set_primary_self_link(link, actor=actor))
diff --git a/accounts/services/account_operations/passwords.py b/accounts/services/account_operations/passwords.py
new file mode 100644
index 0000000..b78b87a
--- /dev/null
+++ b/accounts/services/account_operations/passwords.py
@@ -0,0 +1,58 @@
+from __future__ import annotations
+
+from django.db import transaction
+
+from accounts.models import UserPlayerRelationship
+from accounts.services.password_service import (
+    generate_birthdate_password,
+    mark_password_change_required,
+    set_random_temporary_password,
+    set_temporary_password,
+)
+
+from .contracts import PasswordResetResult, UpdatedAccountResult
+from .shared import (
+    get_user_for_update,
+    updated_account_result,
+    validate_actor_can_manage_target,
+)
+
+
+def _player_for_password_reset(user):
+    link = (
+        user.player_links.select_related("player")
+        .filter(relationship=UserPlayerRelationship.SELF, is_active=True)
+        .order_by("-is_primary", "id")
+        .first()
+    )
+    return link.player if link else None
+
+
+@transaction.atomic
+def reset_account_password(*, actor, user_id: int) -> PasswordResetResult:
+    """Reset an existing account password and require password change on next login."""
+    user = get_user_for_update(user_id)
+    validate_actor_can_manage_target(actor, user)
+    player = _player_for_password_reset(user)
+    if player:
+        temporary_password = generate_birthdate_password(player)
+        set_temporary_password(user, player)
+    else:
+        temporary_password = set_random_temporary_password(user)
+    mark_password_change_required(user, True)
+    user.refresh_from_db()
+    return PasswordResetResult(
+        user=user, username=user.username, temporary_password=temporary_password
+    )
+
+
+@transaction.atomic
+def set_account_password_change_required(
+    *, actor, user_id: int, required: bool
+) -> UpdatedAccountResult:
+    """Set the password-change requirement for an existing account."""
+    user = get_user_for_update(user_id)
+    validate_actor_can_manage_target(actor, user)
+    mark_password_change_required(user, bool(required))
+    user.refresh_from_db()
+    return updated_account_result(user)
diff --git a/accounts/services/account_operations/read_models.py b/accounts/services/account_operations/read_models.py
new file mode 100644
index 0000000..f66d964
--- /dev/null
+++ b/accounts/services/account_operations/read_models.py
@@ -0,0 +1,164 @@
+from __future__ import annotations
+
+from django.contrib.auth import get_user_model
+from django.urls import reverse
+from django.utils import timezone
+
+from accounts.models import AccountRole, UserPlayerLink
+from accounts.services import account_query_service
+from accounts.services.account_query_service import AccountListFilters
+from accounts.services.role_service import role_label
+
+from .contracts import (
+    AccountDetailContext,
+    AccountListContext,
+    AccountListRow,
+    AccountOperationsDashboard,
+    AccountSummaryCard,
+    LinkedPlayerRow,
+)
+from .shared import role_for_user
+
+User = get_user_model()
+
+
+def list_row(user: User) -> AccountListRow:
+    role = role_for_user(user)
+    linked_count = getattr(user, "active_player_link_count", None)
+    if linked_count is None:
+        linked_count = user.player_links.filter(is_active=True).count()
+    return AccountListRow(
+        user=user,
+        role=role,
+        role_label=role_label(role),
+        linked_player_count=linked_count,
+        detail_url=reverse("accounts:user-detail", kwargs={"user_id": user.id}),
+    )
+
+
+def linked_player_row(link: UserPlayerLink) -> LinkedPlayerRow:
+    import_label = ""
+    if link.import_batch_id:
+        import_label = link.import_batch.original_filename
+    return LinkedPlayerRow(
+        link=link,
+        player=link.player,
+        relationship=link.get_relationship_display(),
+        is_primary=link.is_primary,
+        is_active=link.is_active,
+        created_from_import=link.created_from_import,
+        import_label=import_label,
+    )
+
+
+def get_account_operations_dashboard() -> AccountOperationsDashboard:
+    """Return the read-only Account Operations dashboard context."""
+    users = User.objects.select_related("account_profile")
+    total_accounts = users.count()
+    active_accounts = users.filter(is_active=True).count()
+    inactive_accounts = users.filter(is_active=False).count()
+    imported_accounts = users.filter(account_profile__created_from_import=True).count()
+    password_change_accounts = users.filter(
+        account_profile__must_change_password=True
+    ).count()
+    unlinked_users_count = account_query_service.filter_account_users(
+        AccountListFilters(linked_status="unlinked")
+    ).count()
+    players_without_self_link_count = (
+        account_query_service.count_players_without_self_link()
+    )
+
+    summary_cards = [
+        AccountSummaryCard(
+            "Total accounts",
+            total_accounts,
+            "All Django user accounts.",
+            reverse("accounts:user-list"),
+        ),
+        AccountSummaryCard(
+            "Active accounts",
+            active_accounts,
+            "Accounts that can authenticate.",
+            reverse("accounts:user-list") + "?active=yes",
+        ),
+        AccountSummaryCard(
+            "Inactive accounts",
+            inactive_accounts,
+            "Accounts blocked from login.",
+            reverse("accounts:user-list") + "?active=no",
+        ),
+        AccountSummaryCard(
+            "Imported accounts",
+            imported_accounts,
+            "Accounts created from player imports.",
+            reverse("accounts:user-list") + "?imported=yes",
+        ),
+        AccountSummaryCard(
+            "Password change required",
+            password_change_accounts,
+            "Users who must change a temporary password.",
+            reverse("accounts:user-list") + "?must_change_password=yes",
+        ),
+        AccountSummaryCard(
+            "Users without player links",
+            unlinked_users_count,
+            "Accounts with no active player links.",
+            reverse("accounts:user-list") + "?linked=unlinked",
+        ),
+        AccountSummaryCard(
+            "Players without self-linked accounts",
+            players_without_self_link_count,
+            "Active players without an active self-linked user account.",
+        ),
+    ]
+
+    password_rows = [
+        list_row(user)
+        for user in account_query_service.filter_account_users(
+            AccountListFilters(must_change_password="yes")
+        )[:10]
+    ]
+    unlinked_rows = [
+        list_row(user)
+        for user in account_query_service.filter_account_users(
+            AccountListFilters(linked_status="unlinked")
+        )[:10]
+    ]
+    return AccountOperationsDashboard(
+        summary_cards=summary_cards,
+        users_requiring_password_change=password_rows,
+        unlinked_users=unlinked_rows,
+        players_without_self_link_count=players_without_self_link_count,
+        generated_at=timezone.now(),
+    )
+
+
+def get_account_list(filters: AccountListFilters) -> AccountListContext:
+    """Return read-only account list rows for staff account operations."""
+    queryset = account_query_service.filter_account_users(filters)
+    rows = [list_row(user) for user in queryset]
+    return AccountListContext(
+        filters=filters,
+        rows=rows,
+        role_choices=AccountRole.choices,
+        total_count=len(rows),
+    )
+
+
+def get_account_detail(user_id: int) -> AccountDetailContext:
+    """Return read-only detail context for one account."""
+    user = account_query_service.get_account_user(user_id)
+    links = user.player_links.select_related("player", "import_batch").order_by(
+        "-is_active",
+        "relationship",
+        "player__last_name",
+        "player__first_name",
+        "id",
+    )
+    role = role_for_user(user)
+    return AccountDetailContext(
+        user=user,
+        role=role,
+        role_label=role_label(role),
+        linked_players=[linked_player_row(link) for link in links],
+    )
diff --git a/accounts/services/account_operations/shared.py b/accounts/services/account_operations/shared.py
new file mode 100644
index 0000000..644a21e
--- /dev/null
+++ b/accounts/services/account_operations/shared.py
@@ -0,0 +1,124 @@
+from __future__ import annotations
+
+from django.contrib.auth import get_user_model
+from django.core.exceptions import ValidationError
+
+from accounts.models import AccountRole, UserPlayerLink
+from accounts.services.email_service import find_existing_email_user, normalize_email
+from accounts.services.permissions import (
+    can_manage_accounts,
+    can_manage_privileged_accounts,
+)
+from accounts.services.role_service import role_label
+from accounts.services.username_service import validate_available_username_for_user
+
+from .contracts import UpdatedAccountResult, UpdatedLinkResult
+
+User = get_user_model()
+
+
+def validate_actor_can_create_role(actor, role: str) -> None:
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can manage accounts.")
+    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
+        raise ValidationError("Only superusers can create admin accounts.")
+
+
+def validate_actor_can_assign_role(actor, role: str) -> None:
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can manage accounts.")
+    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
+        raise ValidationError("Only superusers can assign admin role.")
+
+
+def validate_actor_can_manage_target(actor, user: User) -> None:
+    if not can_manage_accounts(actor):
+        raise ValidationError("Only staff users can manage accounts.")
+    if (user.is_staff or user.is_superuser) and not can_manage_privileged_accounts(
+        actor
+    ):
+        raise ValidationError("Only superusers can manage staff or superuser accounts.")
+
+
+def validate_account_deactivation_allowed(actor, user: User) -> None:
+    if actor and getattr(actor, "id", None) == user.id:
+        raise ValidationError("You cannot deactivate your own account.")
+    if user.is_superuser and user.is_active:
+        other_active_superusers = (
+            User.objects.filter(is_superuser=True, is_active=True)
+            .exclude(pk=user.pk)
+            .exists()
+        )
+        if not other_active_superusers:
+            raise ValidationError(
+                "You cannot deactivate the last active superuser account."
+            )
+
+
+def validate_email_available(email: str) -> str:
+    normalized = normalize_email(email)
+    if normalized and find_existing_email_user(normalized):
+        raise ValidationError("Email is already in use.")
+    return normalized
+
+
+def validate_email_available_for_user(user: User, email: str) -> str:
+    normalized = normalize_email(email)
+    if normalized:
+        existing_user = find_existing_email_user(normalized)
+        if existing_user and existing_user.pk != user.pk:
+            raise ValidationError("Email is already in use.")
+    return normalized
+
+
+def role_for_user(user: User) -> str:
+    profile = getattr(user, "account_profile", None)
+    if profile:
+        return profile.role
+    if user.is_superuser:
+        return AccountRole.ADMIN
+    if user.is_staff:
+        return AccountRole.STAFF
+    return AccountRole.GUEST_EVALUATOR
+
+
+def updated_account_result(user: User) -> UpdatedAccountResult:
+    role = role_for_user(user)
+    return UpdatedAccountResult(
+        user=user,
+        username=user.username,
+        role=role,
+        role_label=role_label(role),
+        is_active=user.is_active,
+    )
+
+
+def updated_link_result(link: UserPlayerLink) -> UpdatedLinkResult:
+    return UpdatedLinkResult(
+        link=link,
+        user=link.user,
+        player=link.player,
+        relationship=link.relationship,
+        is_primary=link.is_primary,
+        is_active=link.is_active,
+    )
+
+
+def get_user_for_update(user_id: int) -> User:
+    return (
+        User.objects.select_for_update()
+        .select_related("account_profile")
+        .get(pk=user_id)
+    )
+
+
+def get_link_for_user(user: User, link_id: int) -> UserPlayerLink:
+    return (
+        UserPlayerLink.objects.select_for_update()
+        .select_related("user", "player")
+        .get(pk=link_id, user=user)
+    )
+
+
+def normalize_available_username_for_user(user: User, username: str) -> str:
+    return validate_available_username_for_user(user, username)
diff --git a/accounts/services/account_operations/updates.py b/accounts/services/account_operations/updates.py
new file mode 100644
index 0000000..71a9765
--- /dev/null
+++ b/accounts/services/account_operations/updates.py
@@ -0,0 +1,48 @@
+from __future__ import annotations
+
+from django.db import transaction
+
+from accounts.models import AccountRole
+from accounts.services.profile_service import set_account_role
+
+from .contracts import UpdatedAccountResult
+from .shared import (
+    get_user_for_update,
+    normalize_available_username_for_user,
+    updated_account_result,
+    validate_account_deactivation_allowed,
+    validate_actor_can_assign_role,
+    validate_actor_can_manage_target,
+    validate_email_available_for_user,
+)
+
+
+@transaction.atomic
+def update_account(
+    *,
+    actor,
+    user_id: int,
+    username: str,
+    first_name: str = "",
+    last_name: str = "",
+    email: str = "",
+    role: str = AccountRole.GUEST_EVALUATOR,
+    is_active: bool = True,
+) -> UpdatedAccountResult:
+    """Update lifecycle and profile fields for an existing account."""
+    validate_actor_can_assign_role(actor, role)
+    user = get_user_for_update(user_id)
+    if user.is_active and not bool(is_active):
+        validate_account_deactivation_allowed(actor, user)
+    validate_actor_can_manage_target(actor, user)
+    user.username = normalize_available_username_for_user(user, username)
+    user.first_name = str(first_name or "").strip()
+    user.last_name = str(last_name or "").strip()
+    user.email = validate_email_available_for_user(user, email)
+    user.is_active = bool(is_active)
+    user.save(
+        update_fields=["username", "first_name", "last_name", "email", "is_active"]
+    )
+    set_account_role(user, role, actor=actor)
+    user.refresh_from_db()
+    return updated_account_result(user)
diff --git a/accounts/services/account_operations_service.py b/accounts/services/account_operations_service.py
index bbd5aca..4a12642 100644
--- a/accounts/services/account_operations_service.py
+++ b/accounts/services/account_operations_service.py
@@ -1,632 +1,85 @@
-from __future__ import annotations
+"""Public façade for staff Account Operations services.

-from dataclasses import dataclass, field
+Keep imports through this module stable for views, forms, tests, and future callers.
+Implementation details live in ``accounts.services.account_operations``.
+"""

-from django.contrib.auth import get_user_model
-from django.core.exceptions import ValidationError
-from django.db import transaction
-from django.urls import reverse
-from django.utils import timezone
-
-from accounts.models import AccountRole, UserPlayerLink, UserPlayerRelationship
-from accounts.services import account_query_service
-from accounts.services.account_query_service import AccountListFilters
-from accounts.services.email_service import find_existing_email_user, normalize_email
-from accounts.services.link_service import (
-    activate_link,
-    deactivate_link,
-    link_user_to_player,
-    set_primary_self_link,
-    validate_no_active_relationship_conflict,
-)
-from accounts.services.password_service import (
-    generate_birthdate_password,
-    mark_password_change_required,
-    set_random_temporary_password,
-    set_temporary_password,
-)
-from accounts.services.permissions import can_manage_accounts, can_manage_privileged_accounts
-from accounts.services.profile_service import get_or_create_account_profile, set_account_role
-from accounts.services.provisioning_service import STATUS_CREATED, provision_player_account
-from accounts.services.role_service import role_label
-from accounts.services.username_service import validate_available_username, validate_available_username_for_user
-from players.models import Player
-
-
-User = get_user_model()
-
-
-@dataclass(frozen=True)
-class AccountSummaryCard:
-    label: str
-    value: int
-    help_text: str = ""
-    url: str = ""
-
-
-@dataclass(frozen=True)
-class AccountListRow:
-    user: User
-    role: str
-    role_label: str
-    linked_player_count: int
-    detail_url: str
-
-
-@dataclass(frozen=True)
-class LinkedPlayerRow:
-    link: UserPlayerLink
-    player: object
-    relationship: str
-    is_primary: bool
-    is_active: bool
-    created_from_import: bool
-    import_label: str
-
-
-@dataclass(frozen=True)
-class AccountOperationsDashboard:
-    summary_cards: list[AccountSummaryCard]
-    users_requiring_password_change: list[AccountListRow]
-    unlinked_users: list[AccountListRow]
-    players_without_self_link_count: int
-    generated_at: object
-
-
-@dataclass(frozen=True)
-class AccountListContext:
-    filters: AccountListFilters
-    rows: list[AccountListRow]
-    role_choices: tuple
-    total_count: int
-
-
-@dataclass(frozen=True)
-class AccountDetailContext:
-    user: User
-    role: str
-    role_label: str
-    linked_players: list[LinkedPlayerRow]
-
-
-@dataclass(frozen=True)
-class CreatedAccountResult:
-    user: User
-    username: str
-    temporary_password: str = field(repr=False)
-    role: str
-    role_label: str
-    player: Player | None = None
-
-
-@dataclass(frozen=True)
-class UpdatedAccountResult:
-    user: User
-    username: str
-    role: str
-    role_label: str
-    is_active: bool
-
-
-@dataclass(frozen=True)
-class UpdatedLinkResult:
-    link: UserPlayerLink
-    user: User
-    player: Player
-    relationship: str
-    is_primary: bool
-    is_active: bool
-
-
-@dataclass(frozen=True)
-class PasswordResetResult:
-    user: User
-    username: str
-    temporary_password: str = field(repr=False)
-
-
-BULK_ACTION_ACTIVATE = "activate"
-BULK_ACTION_DEACTIVATE = "deactivate"
-BULK_ACTION_REQUIRE_PASSWORD_CHANGE = "require_password_change"
-BULK_ACTION_CLEAR_PASSWORD_CHANGE = "clear_password_change"
-BULK_ACCOUNT_ACTIONS = {
+from accounts.services.account_operations.bulk import bulk_account_operation
+from accounts.services.account_operations.contracts import (
+    BULK_ACCOUNT_ACTIONS,
     BULK_ACTION_ACTIVATE,
+    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
     BULK_ACTION_DEACTIVATE,
     BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
-    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
-}
-
-
-@dataclass(frozen=True)
-class BulkOperationError:
-    username: str
-    message: str
-
-
-@dataclass(frozen=True)
-class BulkOperationResult:
-    processed: int
-    successful: int
-    failed: int
-    errors: list[BulkOperationError] = field(default_factory=list, repr=False)
-
-
-def _validate_actor_can_create_role(actor, role: str) -> None:
-    if not can_manage_accounts(actor):
-        raise ValidationError("Only staff users can manage accounts.")
-    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
-        raise ValidationError("Only superusers can create admin accounts.")
-
-
-def _validate_actor_can_assign_role(actor, role: str) -> None:
-    if not can_manage_accounts(actor):
-        raise ValidationError("Only staff users can manage accounts.")
-    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
-        raise ValidationError("Only superusers can assign admin role.")
-
-
-def _validate_actor_can_manage_target(actor, user: User) -> None:
-    if not can_manage_accounts(actor):
-        raise ValidationError("Only staff users can manage accounts.")
-    if (user.is_staff or user.is_superuser) and not can_manage_privileged_accounts(actor):
-        raise ValidationError("Only superusers can manage staff or superuser accounts.")
-
-
-def _validate_account_deactivation_allowed(actor, user: User) -> None:
-    if actor and getattr(actor, "id", None) == user.id:
-        raise ValidationError("You cannot deactivate your own account.")
-    if user.is_superuser and user.is_active:
-        other_active_superusers = User.objects.filter(is_superuser=True, is_active=True).exclude(pk=user.pk).exists()
-        if not other_active_superusers:
-            raise ValidationError("You cannot deactivate the last active superuser account.")
-
-
-def _validate_email_available(email: str) -> str:
-    normalized = normalize_email(email)
-    if normalized and find_existing_email_user(normalized):
-        raise ValidationError("Email is already in use.")
-    return normalized
-
-
-def _validate_email_available_for_user(user: User, email: str) -> str:
-    normalized = normalize_email(email)
-    if normalized:
-        existing_user = find_existing_email_user(normalized)
-        if existing_user and existing_user.pk != user.pk:
-            raise ValidationError("Email is already in use.")
-    return normalized
-
-
-def _role_for_user(user: User) -> str:
-    profile = getattr(user, "account_profile", None)
-    if profile:
-        return profile.role
-    if user.is_superuser:
-        return AccountRole.ADMIN
-    if user.is_staff:
-        return AccountRole.STAFF
-    return AccountRole.GUEST_EVALUATOR
-
-
-def _list_row(user: User) -> AccountListRow:
-    role = _role_for_user(user)
-    linked_count = getattr(user, "active_player_link_count", None)
-    if linked_count is None:
-        linked_count = user.player_links.filter(is_active=True).count()
-    return AccountListRow(
-        user=user,
-        role=role,
-        role_label=role_label(role),
-        linked_player_count=linked_count,
-        detail_url=reverse("accounts:user-detail", kwargs={"user_id": user.id}),
-    )
-
-
-def _linked_player_row(link: UserPlayerLink) -> LinkedPlayerRow:
-    import_label = ""
-    if link.import_batch_id:
-        import_label = link.import_batch.original_filename
-    return LinkedPlayerRow(
-        link=link,
-        player=link.player,
-        relationship=link.get_relationship_display(),
-        is_primary=link.is_primary,
-        is_active=link.is_active,
-        created_from_import=link.created_from_import,
-        import_label=import_label,
-    )
-
-
-def _updated_account_result(user: User) -> UpdatedAccountResult:
-    role = _role_for_user(user)
-    return UpdatedAccountResult(
-        user=user,
-        username=user.username,
-        role=role,
-        role_label=role_label(role),
-        is_active=user.is_active,
-    )
-
-
-def _updated_link_result(link: UserPlayerLink) -> UpdatedLinkResult:
-    return UpdatedLinkResult(
-        link=link,
-        user=link.user,
-        player=link.player,
-        relationship=link.relationship,
-        is_primary=link.is_primary,
-        is_active=link.is_active,
-    )
-
-
-def _get_user_for_update(user_id: int) -> User:
-    return User.objects.select_for_update().select_related("account_profile").get(pk=user_id)
-
-
-def _get_link_for_user(user: User, link_id: int) -> UserPlayerLink:
-    return UserPlayerLink.objects.select_for_update().select_related("user", "player").get(pk=link_id, user=user)
-
-
-def _player_for_password_reset(user: User) -> Player | None:
-    link = (
-        UserPlayerLink.objects.select_related("player")
-        .filter(user=user, relationship=UserPlayerRelationship.SELF, is_active=True)
-        .order_by("-is_primary", "id")
-        .first()
-    )
-    return link.player if link else None
-
-
-def get_account_operations_dashboard() -> AccountOperationsDashboard:
-    """Return the read-only Account Operations dashboard context."""
-    users = User.objects.select_related("account_profile")
-    total_accounts = users.count()
-    active_accounts = users.filter(is_active=True).count()
-    inactive_accounts = users.filter(is_active=False).count()
-    imported_accounts = users.filter(account_profile__created_from_import=True).count()
-    password_change_accounts = users.filter(account_profile__must_change_password=True).count()
-    unlinked_users_count = account_query_service.filter_account_users(
-        AccountListFilters(linked_status="unlinked")
-    ).count()
-    players_without_self_link_count = account_query_service.count_players_without_self_link()
-
-    summary_cards = [
-        AccountSummaryCard("Total accounts", total_accounts, "All Django user accounts.", reverse("accounts:user-list")),
-        AccountSummaryCard("Active accounts", active_accounts, "Accounts that can authenticate.", reverse("accounts:user-list") + "?active=yes"),
-        AccountSummaryCard("Inactive accounts", inactive_accounts, "Accounts blocked from login.", reverse("accounts:user-list") + "?active=no"),
-        AccountSummaryCard("Imported accounts", imported_accounts, "Accounts created from player imports.", reverse("accounts:user-list") + "?imported=yes"),
-        AccountSummaryCard(
-            "Password change required",
-            password_change_accounts,
-            "Users who must change a temporary password.",
-            reverse("accounts:user-list") + "?must_change_password=yes",
-        ),
-        AccountSummaryCard(
-            "Users without player links",
-            unlinked_users_count,
-            "Accounts with no active player links.",
-            reverse("accounts:user-list") + "?linked=unlinked",
-        ),
-        AccountSummaryCard(
-            "Players without self-linked accounts",
-            players_without_self_link_count,
-            "Active players without an active self-linked user account.",
-        ),
-    ]
-
-    password_rows = [
-        _list_row(user)
-        for user in account_query_service.filter_account_users(AccountListFilters(must_change_password="yes"))[:10]
-    ]
-    unlinked_rows = [
-        _list_row(user)
-        for user in account_query_service.filter_account_users(AccountListFilters(linked_status="unlinked"))[:10]
-    ]
-    return AccountOperationsDashboard(
-        summary_cards=summary_cards,
-        users_requiring_password_change=password_rows,
-        unlinked_users=unlinked_rows,
-        players_without_self_link_count=players_without_self_link_count,
-        generated_at=timezone.now(),
-    )
-
-
-def get_account_list(filters: AccountListFilters) -> AccountListContext:
-    """Return read-only account list rows for staff account operations."""
-    queryset = account_query_service.filter_account_users(filters)
-    rows = [_list_row(user) for user in queryset]
-    return AccountListContext(
-        filters=filters,
-        rows=rows,
-        role_choices=AccountRole.choices,
-        total_count=len(rows),
-    )
-
-
-def get_account_detail(user_id: int) -> AccountDetailContext:
-    """Return read-only detail context for one account."""
-    user = account_query_service.get_account_user(user_id)
-    links = user.player_links.select_related("player", "import_batch").order_by(
-        "-is_active",
-        "relationship",
-        "player__last_name",
-        "player__first_name",
-        "id",
-    )
-    role = _role_for_user(user)
-    return AccountDetailContext(
-        user=user,
-        role=role,
-        role_label=role_label(role),
-        linked_players=[_linked_player_row(link) for link in links],
-    )
-
-
-@transaction.atomic
-def update_account(
-    *,
-    actor,
-    user_id: int,
-    username: str,
-    first_name: str = "",
-    last_name: str = "",
-    email: str = "",
-    role: str = AccountRole.GUEST_EVALUATOR,
-    is_active: bool = True,
-) -> UpdatedAccountResult:
-    """Update lifecycle and profile fields for an existing account."""
-    _validate_actor_can_assign_role(actor, role)
-    user = _get_user_for_update(user_id)
-    if user.is_active and not bool(is_active):
-        _validate_account_deactivation_allowed(actor, user)
-    _validate_actor_can_manage_target(actor, user)
-    user.username = validate_available_username_for_user(user, username)
-    user.first_name = str(first_name or "").strip()
-    user.last_name = str(last_name or "").strip()
-    user.email = _validate_email_available_for_user(user, email)
-    user.is_active = bool(is_active)
-    user.save(update_fields=["username", "first_name", "last_name", "email", "is_active"])
-    set_account_role(user, role, actor=actor)
-    user.refresh_from_db()
-    return _updated_account_result(user)
-
-
-@transaction.atomic
-def activate_account(*, actor, user_id: int) -> UpdatedAccountResult:
-    """Activate an existing account without changing profile or link history."""
-    user = _get_user_for_update(user_id)
-    _validate_actor_can_manage_target(actor, user)
-    if not user.is_active:
-        user.is_active = True
-        user.save(update_fields=["is_active"])
-    return _updated_account_result(user)
-
-
-@transaction.atomic
-def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
-    """Deactivate an existing account without deleting account data or links."""
-    user = _get_user_for_update(user_id)
-    if user.is_active:
-        _validate_account_deactivation_allowed(actor, user)
-        _validate_actor_can_manage_target(actor, user)
-        user.is_active = False
-        user.save(update_fields=["is_active"])
-    return _updated_account_result(user)
-
-
-@transaction.atomic
-def create_user_player_link(
-    *,
-    actor,
-    user_id: int,
-    player: Player,
-    relationship: str,
-    is_primary: bool = False,
-) -> UpdatedLinkResult:
-    """Create an active user/player link through the account operations workflow."""
-    user = _get_user_for_update(user_id)
-    _validate_actor_can_manage_target(actor, user)
-    validate_no_active_relationship_conflict(user, player, relationship)
-    link = link_user_to_player(user, player, relationship=relationship, is_primary=is_primary)
-    return _updated_link_result(link)
-
-
-@transaction.atomic
-def deactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
-    """Deactivate a user/player link without deleting its history."""
-    user = _get_user_for_update(user_id)
-    _validate_actor_can_manage_target(actor, user)
-    link = _get_link_for_user(user, link_id)
-    return _updated_link_result(deactivate_link(link, actor=actor))
-
-
-@transaction.atomic
-def reactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
-    """Reactivate an existing inactive user/player link when constraints allow it."""
-    user = _get_user_for_update(user_id)
-    _validate_actor_can_manage_target(actor, user)
-    link = _get_link_for_user(user, link_id)
-    return _updated_link_result(activate_link(link, actor=actor))
-
-
-@transaction.atomic
-def set_primary_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
-    """Set an existing self link as the active primary player link."""
-    user = _get_user_for_update(user_id)
-    _validate_actor_can_manage_target(actor, user)
-    link = _get_link_for_user(user, link_id)
-    return _updated_link_result(set_primary_self_link(link, actor=actor))
-
-
-@transaction.atomic
-def reset_account_password(*, actor, user_id: int) -> PasswordResetResult:
-    """Reset an existing account password and require password change on next login."""
-    user = _get_user_for_update(user_id)
-    _validate_actor_can_manage_target(actor, user)
-    player = _player_for_password_reset(user)
-    if player:
-        temporary_password = generate_birthdate_password(player)
-        set_temporary_password(user, player)
-    else:
-        temporary_password = set_random_temporary_password(user)
-    mark_password_change_required(user, True)
-    user.refresh_from_db()
-    return PasswordResetResult(user=user, username=user.username, temporary_password=temporary_password)
-
-
-@transaction.atomic
-def set_account_password_change_required(*, actor, user_id: int, required: bool) -> UpdatedAccountResult:
-    """Set the password-change requirement for an existing account."""
-    user = _get_user_for_update(user_id)
-    _validate_actor_can_manage_target(actor, user)
-    mark_password_change_required(user, bool(required))
-    user.refresh_from_db()
-    return _updated_account_result(user)
-
-
-def _clean_bulk_user_ids(user_ids):
-    clean_ids = []
-    seen = set()
-    for raw_user_id in user_ids or []:
-        raw_value = str(raw_user_id or "").strip()
-        if not raw_value or raw_value in seen:
-            continue
-        seen.add(raw_value)
-        try:
-            clean_ids.append(int(raw_value))
-        except (TypeError, ValueError):
-            clean_ids.append(raw_value)
-    return clean_ids
-
-
-def _bulk_error_username(user_id) -> str:
-    if isinstance(user_id, int):
-        username = User.objects.filter(pk=user_id).values_list("username", flat=True).first()
-        if username:
-            return username
-    return "Unknown account"
-
-
-def _validation_message(exc: ValidationError) -> str:
-    if hasattr(exc, "messages"):
-        return "; ".join(exc.messages)
-    return str(exc)
-
-
-def bulk_account_operation(*, actor, action: str, user_ids) -> BulkOperationResult:
-    """Apply a safe account operation to selected users and collect per-account failures."""
-    if not can_manage_accounts(actor):
-        raise ValidationError("Only staff users can manage accounts.")
-    if action not in BULK_ACCOUNT_ACTIONS:
-        raise ValidationError("Unsupported bulk action.")
-
-    clean_user_ids = _clean_bulk_user_ids(user_ids)
-    if not clean_user_ids:
-        raise ValidationError("Select at least one account.")
-
-    successful = 0
-    errors = []
-    for user_id in clean_user_ids:
-        username = _bulk_error_username(user_id)
-        if not isinstance(user_id, int):
-            errors.append(BulkOperationError(username=username, message="Account not found."))
-            continue
-        try:
-            if action == BULK_ACTION_ACTIVATE:
-                activate_account(actor=actor, user_id=user_id)
-            elif action == BULK_ACTION_DEACTIVATE:
-                deactivate_account(actor=actor, user_id=user_id)
-            elif action == BULK_ACTION_REQUIRE_PASSWORD_CHANGE:
-                set_account_password_change_required(actor=actor, user_id=user_id, required=True)
-            elif action == BULK_ACTION_CLEAR_PASSWORD_CHANGE:
-                set_account_password_change_required(actor=actor, user_id=user_id, required=False)
-        except User.DoesNotExist:
-            errors.append(BulkOperationError(username=username, message="Account not found."))
-        except ValidationError as exc:
-            errors.append(BulkOperationError(username=username, message=_validation_message(exc)))
-        else:
-            successful += 1
-
-    return BulkOperationResult(
-        processed=len(clean_user_ids),
-        successful=successful,
-        failed=len(errors),
-        errors=errors,
-    )
-
-
-@transaction.atomic
-def create_account_only(
-    *,
-    actor,
-    username: str,
-    first_name: str = "",
-    last_name: str = "",
-    email: str = "",
-    role: str = AccountRole.GUEST_EVALUATOR,
-    is_active: bool = True,
-) -> CreatedAccountResult:
-    """Create a login account without creating or linking a player."""
-    _validate_actor_can_create_role(actor, role)
-    username = validate_available_username(username)
-    normalized_email = _validate_email_available(email)
-    user = User.objects.create(
-        username=username,
-        first_name=str(first_name or "").strip(),
-        last_name=str(last_name or "").strip(),
-        email=normalized_email,
-        is_active=bool(is_active),
-    )
-    temporary_password = set_random_temporary_password(user)
-    profile = get_or_create_account_profile(user)
-    if profile.created_from_import or profile.import_batch_id:
-        raise ValidationError("Manual accounts cannot use import provenance.")
-    set_account_role(user, role, actor=actor)
-    mark_password_change_required(user, True)
-    user.refresh_from_db()
-    return CreatedAccountResult(
-        user=user,
-        username=user.username,
-        temporary_password=temporary_password,
-        role=role,
-        role_label=role_label(role),
-    )
-
-
-@transaction.atomic
-def create_player_account(
-    *,
-    actor,
-    player,
-    username: str = "",
-    email: str = "",
-    role: str = AccountRole.PLAYER,
-    is_active: bool = True,
-) -> CreatedAccountResult:
-    """Create a login account for an existing canonical player."""
-    if not isinstance(player, Player):
-        raise ValidationError("A valid existing player is required.")
-    _validate_actor_can_create_role(actor, role)
-    if role != AccountRole.PLAYER:
-        raise ValidationError("Player account creation must use the player role in Phase B.")
-    normalized_email = _validate_email_available(email)
-    result = provision_player_account(
-        player,
-        actor=actor,
-        email=normalized_email,
-        activate_user=bool(is_active),
-        username=username,
-    )
-    if result.status != STATUS_CREATED or not result.user_id:
-        message = "; ".join(result.messages) if result.messages else "Player account could not be created."
-        raise ValidationError(message)
-    user = User.objects.get(pk=result.user_id)
-    temporary_password = generate_birthdate_password(player)
-    return CreatedAccountResult(
-        user=user,
-        username=user.username,
-        temporary_password=temporary_password,
-        role=role,
-        role_label=role_label(role),
-        player=player,
-    )
+    AccountDetailContext,
+    AccountListContext,
+    AccountListRow,
+    AccountOperationsDashboard,
+    AccountSummaryCard,
+    BulkOperationError,
+    BulkOperationResult,
+    CreatedAccountResult,
+    LinkedPlayerRow,
+    PasswordResetResult,
+    UpdatedAccountResult,
+    UpdatedLinkResult,
+)
+from accounts.services.account_operations.creation import (
+    create_account_only,
+    create_player_account,
+)
+from accounts.services.account_operations.lifecycle import (
+    activate_account,
+    deactivate_account,
+)
+from accounts.services.account_operations.links import (
+    create_user_player_link,
+    deactivate_user_player_link,
+    reactivate_user_player_link,
+    set_primary_user_player_link,
+)
+from accounts.services.account_operations.passwords import (
+    reset_account_password,
+    set_account_password_change_required,
+)
+from accounts.services.account_operations.read_models import (
+    get_account_detail,
+    get_account_list,
+    get_account_operations_dashboard,
+)
+from accounts.services.account_operations.updates import update_account
+
+__all__ = [
+    "BULK_ACCOUNT_ACTIONS",
+    "BULK_ACTION_ACTIVATE",
+    "BULK_ACTION_CLEAR_PASSWORD_CHANGE",
+    "BULK_ACTION_DEACTIVATE",
+    "BULK_ACTION_REQUIRE_PASSWORD_CHANGE",
+    "AccountDetailContext",
+    "AccountListContext",
+    "AccountListRow",
+    "AccountOperationsDashboard",
+    "AccountSummaryCard",
+    "BulkOperationError",
+    "BulkOperationResult",
+    "CreatedAccountResult",
+    "LinkedPlayerRow",
+    "PasswordResetResult",
+    "UpdatedAccountResult",
+    "UpdatedLinkResult",
+    "activate_account",
+    "bulk_account_operation",
+    "create_account_only",
+    "create_player_account",
+    "create_user_player_link",
+    "deactivate_account",
+    "deactivate_user_player_link",
+    "get_account_detail",
+    "get_account_list",
+    "get_account_operations_dashboard",
+    "reactivate_user_player_link",
+    "reset_account_password",
+    "set_account_password_change_required",
+    "set_primary_user_player_link",
+    "update_account",
+]
```
