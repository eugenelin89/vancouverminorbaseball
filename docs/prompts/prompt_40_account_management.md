# Prompt 40: Account Management

## User Prompt

```text
Review the Platform V1 Account Operations engineering plan only.

Do NOT implement application code.

Do NOT create migrations.

Do NOT modify models, services, views, templates, URLs, tests, or settings.

Only review and improve the engineering plan.

Files to review:

- docs/account_management/implementation/engineering/platform_v1_account_operations.md

Also inspect for consistency:

- docs/account_management/V1_SUMMARY.md
- docs/ARCHITECTURE.md
- docs/account_management/implementation/account_management_v1.md

==================================================
Goals
==================================================

Improve the engineering plan without changing the overall architecture.

The goal is to ensure implementation can proceed phase-by-phase with minimal ambiguity.

==================================================
Required Improvements
==================================================

1. Separate manual account creation workflows

Clarify that there are two distinct operational workflows:

A. Account-only creation

Examples:
- coach
- guest evaluator
- staff

These create:

- User
- AccountProfile

and optionally later create links.

B. Player account creation

Clarify that player identity already exists in players.Player.

Creating a player account should:

- locate an existing Player
- provision a User
- create AccountProfile
- create UserPlayerLink

Do not duplicate player creation logic inside accounts.

--------------------------------------------------

2. Strengthen Account Operations dashboard

Expand the proposed `/accounts/` landing page.

Recommend operational summary cards.

Examples:

- Total accounts
- Active accounts
- Inactive accounts
- Imported accounts
- Accounts requiring password change
- Players without accounts
- Users without player links
- Recent account operations (if available)

Clarify that this is an operational dashboard rather than merely a navigation page.

--------------------------------------------------

3. Clarify username policy

Document that:

- username generation remains owned by username_service
- default format is firstname.lastname
- collisions are resolved by the username service
- all manual username changes go through username_service

Views must never implement username rules.

--------------------------------------------------

4. Clarify parent relationships

Document explicitly:

- one parent may link to multiple players
- one player may have multiple parents/guardians

Clarify that this is expected behavior.

--------------------------------------------------

5. Clarify deactivation philosophy

Strengthen the wording that:

deactivation is the normal lifecycle

deletion is exceptional

Account operations should preserve history whenever possible.

--------------------------------------------------

6. Add deferred features

Under "Not Included" add:

- account merge
- duplicate account resolution
- player merge via account operations

State that these require dedicated planning because they affect authentication, user-player links, and historical data.

--------------------------------------------------

7. Add future coach import note

Do NOT add coach import to Platform V1 implementation.

Instead add a note that:

once manual coach operations are proven stable, a future engineering plan may introduce bulk coach import using the same service architecture established for player provisioning.

This should remain explicitly outside the scope of the current implementation roadmap.

--------------------------------------------------

8. Preserve architecture

Ensure the engineering plan continues to reinforce:

- players owns player identity
- accounts owns authentication
- analytics owns evaluations
- drafts owns draft workflow

No subsystem should bypass another subsystem's services.

==================================================
Final Report
==================================================

Report:

- files modified
- documentation improvements made
- architectural clarifications added
- confirmation that no application code was changed
```

## App / Subsystem

account_management

## Work Commit

`66b9208`

## Work Commit Diff

```diff
diff --git a/docs/account_management/implementation/engineering/platform_v1_account_operations.md b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
index eef4fd4..3ba10f4 100644
--- a/docs/account_management/implementation/engineering/platform_v1_account_operations.md
+++ b/docs/account_management/implementation/engineering/platform_v1_account_operations.md
@@ -14,6 +14,7 @@ The objectives are:
 - preserve the existing separation between Django login identity, account metadata, and player identity;
 - keep account operations in the `accounts` bounded context;
 - reuse existing services wherever possible;
+- preserve the ownership boundaries where `players` owns player identity, `accounts` owns authentication/account state, `analytics` owns evaluations and reporting, and `drafts` owns draft workflow;
 - avoid exposing plaintext temporary passwords or duplicating account business rules in views.

 ## 2. Scope
@@ -37,6 +38,20 @@ This work includes operational account-management functionality for Platform V1:
 - Linked user display.
 - Bulk operations where they are simple, safe, and clearly reversible.

+Manual account creation has two distinct workflows:
+
+1. Account-only creation.
+   - Examples: coach, guest evaluator, staff.
+   - Creates a Django `User`.
+   - Creates or updates `accounts.AccountProfile`.
+   - May optionally add `UserPlayerLink` records later.
+2. Player account creation.
+   - Starts from an existing canonical `players.Player`.
+   - Provisions a Django `User`.
+   - Creates or updates `accounts.AccountProfile`.
+   - Creates a `UserPlayerLink` to the existing player.
+   - Must not create or duplicate player identity inside `accounts`.
+
 The work should use the existing models:

 - Django `User`
@@ -64,6 +79,9 @@ This plan does not include:
 - Background jobs.
 - Caching.
 - Audit logging, unless a separate accepted plan introduces it.
+- Account merge.
+- Duplicate account resolution.
+- Player merge through account operations.
 - Custom `AUTH_USER_MODEL`.
 - PDP account migration.
 - Analytics evaluator workflow changes.
@@ -96,7 +114,7 @@ Recommended routes:

 Recommended page responsibilities:

-- `/accounts/`: Account Operations landing page with summary counts, common actions, and links.
+- `/accounts/`: Account Operations dashboard with summary counts, issue queues, common actions, and links.
 - `/accounts/users/`: Searchable user list with filters for role, active status, staff status, linked-player status, and forced password-change status.
 - `/accounts/users/create/`: Manual account creation form.
 - `/accounts/users/<id>/`: Account detail page showing Django user fields, account profile role, password-change state, linked players, and safe operational actions.
@@ -109,6 +127,19 @@ Recommended page responsibilities:
 - `/accounts/users/<id>/deactivate/`: Confirmation page for deactivating a user.
 - `/accounts/players/<player_id>/users/`: Player-centered view of linked users.

+The `/accounts/` page should be an operational dashboard, not merely a navigation page. Recommended summary cards:
+
+- Total accounts.
+- Active accounts.
+- Inactive accounts.
+- Imported accounts.
+- Accounts requiring password change.
+- Players without accounts.
+- Users without player links.
+- Recent account operations, if the data is already available without adding audit logging.
+
+The dashboard should link to filtered user lists or player lists where possible. It should not introduce a reporting engine, charts, caching, background jobs, or audit-log model.
+
 Navigation:

 - Add an Account Operations link for staff users where staff operational navigation already exists.
@@ -119,6 +150,14 @@ Templates should be server-rendered and consistent with the existing simple Djan

 ## 5. Operations

+### Account-Only Creation Versus Player Account Creation
+
+Account-only creation is for users whose login account can exist independently of a specific player link, such as coaches, staff, and guest evaluators. It creates `User` and `AccountProfile` records through account services. Player links may be added later through link management.
+
+Player account creation is different. Player identity must already exist as `players.Player`. Account Operations should locate the existing player, call account provisioning/account operation services to create a `User` and `AccountProfile`, and create a `UserPlayerLink` through `link_service`.
+
+Accounts must not duplicate player creation, player matching, or player merge behavior. If a player does not exist yet, staff should use the player import/player identity workflow owned by `players` before creating the login account.
+
 ### Creating Coach Accounts

 Workflow:
@@ -146,8 +185,8 @@ Workflow:
 Rules:

 - Parent role does not grant staff access.
-- A parent can be linked to multiple players.
-- A player can have multiple parent or guardian links.
+- One parent may be linked to multiple players. This is expected behavior for siblings or multi-player households.
+- One player may have multiple parents or guardians. This is expected behavior and should not be treated as a duplicate-link problem unless the same active `(user, player, relationship)` already exists.

 ### Creating Guest Evaluators

@@ -199,7 +238,9 @@ Workflow:

 Rules:

-- Do not delete users for routine deactivation.
+- Deactivation is the normal account lifecycle operation.
+- Deletion is exceptional and should not be part of routine Account Operations.
+- Preserve account, profile, link, observation, and import history whenever possible.
 - Deactivation should block login.
 - Existing observations and historical links remain valid.
 - Superuser self-deactivation should be blocked.
@@ -219,6 +260,10 @@ Rules:
 - Username changes must be explicit and recorded in user-facing confirmation messaging.
 - The service should avoid changing linked players or account role.
 - Existing `username_service` should remain the owner of username normalization and uniqueness helpers.
+- The default generated username format remains `firstname.lastname`.
+- Username collisions must be resolved by `username_service`.
+- Manual username changes must go through `username_service`.
+- Views must never implement username generation, normalization, or collision rules.

 ### Changing Roles

@@ -358,7 +403,8 @@ Continue using existing service boundaries.
 `accounts.services.account_operations_service`

 - Thin orchestration layer for staff account operations that touch multiple account services.
-- Manual account creation.
+- Account-only creation for coach, guest evaluator, parent, and staff accounts.
+- Player account creation from an existing `players.Player`.
 - User activation/deactivation.
 - Username changes.
 - Role changes.
@@ -367,6 +413,15 @@ Continue using existing service boundaries.

 Do not place account operation business logic in views, Analytics services, or player services.

+Player lookup for player-account creation should use `players` services or query helpers. Account Operations may select an existing player, but it must not implement player matching or duplicate player identity rules.
+
+No subsystem should bypass another subsystem's services:
+
+- `players` owns player identity and player import/matching.
+- `accounts` owns authentication, profiles, roles, passwords, usernames, and user-player links.
+- `analytics` owns evaluations, observations, evaluator snapshots, metrics, reports, and Analytics UI.
+- `drafts` owns draft workflow and draft actions.
+
 ## 7. Permissions

 Account operations must preserve the distinction between Django permissions and platform roles.
@@ -479,14 +534,17 @@ Goals:

 - Allow staff to create coach, parent, player, and guest evaluator accounts.
 - Allow superusers to create staff accounts.
+- Keep account-only creation distinct from player account creation.

 Deliverables:

 - `/accounts/users/create/`;
-- service-backed manual account creation;
+- service-backed account-only creation for coach, parent, guest evaluator, and staff users;
+- service-backed player account creation that starts from an existing `players.Player`;
 - role assignment through `profile_service`;
 - temporary password setup through `password_service`;
-- tests for duplicate username/email, role defaults, staff restrictions, and password-change requirement.
+- optional user-player link creation through `link_service`;
+- tests for duplicate username/email, role defaults, staff restrictions, player-account creation from existing players, no player duplication, and password-change requirement.

 ### Phase C: Link Management

@@ -551,11 +609,18 @@ Possible deliverables:

 Bulk operations should be deferred if implementation pressure would weaken safety or clarity.

+### Explicitly Deferred: Bulk Coach Import
+
+Bulk coach import is outside the current Platform V1 Account Operations roadmap. Once manual coach operations are proven stable, a future engineering plan may introduce bulk coach import using the same service architecture established for player provisioning.
+
+That future plan should define CSV format, matching rules, duplicate detection, role assignment, password reset behavior, and safety checks before implementation begins.
+
 ## 10. Risks

 - Incorrect role assignment could make reporting and evaluator snapshots misleading.
 - Confusing `AccountProfile.role` with Django `is_staff` / `is_superuser` could accidentally grant or deny operational access.
 - Duplicate users may be created if search and creation do not check username and email carefully.
+- Duplicate account resolution and account merge are intentionally deferred because they can affect authentication, user-player links, historical observations, and operational history.
 - Incorrect user-player links could expose player context to the wrong account.
 - Deleting links instead of deactivating them would lose operational history.
 - Deactivating users incorrectly could lock out staff or superusers.
@@ -575,6 +640,7 @@ Bulk operations should be deferred if implementation pressure would weaken safet
 - Should assigning `AccountProfile.role=admin` require superuser even if it does not grant Django admin access?
 - Should changing `User.is_staff` be included in this operational UI, or remain in Django admin for Platform V1?
 - Should bulk operations be included in the initial implementation or deferred until after single-account workflows are proven in production?
+- Should account merge and duplicate account resolution be planned as a later Platform V1 operations extension or deferred to a future platform version?
 - Should account-operation changes eventually produce audit records? This plan treats audit logging as out of scope, but production operations may require it later.

 ## Definition Of Done
diff --git a/project_flat_file.txt b/project_flat_file.txt
index 9192df2..6430961 100644
--- a/project_flat_file.txt
+++ b/project_flat_file.txt
@@ -12972,6 +12972,7 @@ The objectives are:
 - preserve the existing separation between Django login identity, account metadata, and player identity;
 - keep account operations in the `accounts` bounded context;
 - reuse existing services wherever possible;
+- preserve the ownership boundaries where `players` owns player identity, `accounts` owns authentication/account state, `analytics` owns evaluations and reporting, and `drafts` owns draft workflow;
 - avoid exposing plaintext temporary passwords or duplicating account business rules in views.

 ## 2. Scope
@@ -12995,6 +12996,20 @@ This work includes operational account-management functionality for Platform V1:
 - Linked user display.
 - Bulk operations where they are simple, safe, and clearly reversible.

+Manual account creation has two distinct workflows:
+
+1. Account-only creation.
+   - Examples: coach, guest evaluator, staff.
+   - Creates a Django `User`.
+   - Creates or updates `accounts.AccountProfile`.
+   - May optionally add `UserPlayerLink` records later.
+2. Player account creation.
+   - Starts from an existing canonical `players.Player`.
+   - Provisions a Django `User`.
+   - Creates or updates `accounts.AccountProfile`.
+   - Creates a `UserPlayerLink` to the existing player.
+   - Must not create or duplicate player identity inside `accounts`.
+
 The work should use the existing models:

 - Django `User`
@@ -13022,6 +13037,9 @@ This plan does not include:
 - Background jobs.
 - Caching.
 - Audit logging, unless a separate accepted plan introduces it.
+- Account merge.
+- Duplicate account resolution.
+- Player merge through account operations.
 - Custom `AUTH_USER_MODEL`.
 - PDP account migration.
 - Analytics evaluator workflow changes.
@@ -13054,7 +13072,7 @@ Recommended routes:

 Recommended page responsibilities:

-- `/accounts/`: Account Operations landing page with summary counts, common actions, and links.
+- `/accounts/`: Account Operations dashboard with summary counts, issue queues, common actions, and links.
 - `/accounts/users/`: Searchable user list with filters for role, active status, staff status, linked-player status, and forced password-change status.
 - `/accounts/users/create/`: Manual account creation form.
 - `/accounts/users/<id>/`: Account detail page showing Django user fields, account profile role, password-change state, linked players, and safe operational actions.
@@ -13067,6 +13085,19 @@ Recommended page responsibilities:
 - `/accounts/users/<id>/deactivate/`: Confirmation page for deactivating a user.
 - `/accounts/players/<player_id>/users/`: Player-centered view of linked users.

+The `/accounts/` page should be an operational dashboard, not merely a navigation page. Recommended summary cards:
+
+- Total accounts.
+- Active accounts.
+- Inactive accounts.
+- Imported accounts.
+- Accounts requiring password change.
+- Players without accounts.
+- Users without player links.
+- Recent account operations, if the data is already available without adding audit logging.
+
+The dashboard should link to filtered user lists or player lists where possible. It should not introduce a reporting engine, charts, caching, background jobs, or audit-log model.
+
 Navigation:

 - Add an Account Operations link for staff users where staff operational navigation already exists.
@@ -13077,6 +13108,14 @@ Templates should be server-rendered and consistent with the existing simple Djan

 ## 5. Operations

+### Account-Only Creation Versus Player Account Creation
+
+Account-only creation is for users whose login account can exist independently of a specific player link, such as coaches, staff, and guest evaluators. It creates `User` and `AccountProfile` records through account services. Player links may be added later through link management.
+
+Player account creation is different. Player identity must already exist as `players.Player`. Account Operations should locate the existing player, call account provisioning/account operation services to create a `User` and `AccountProfile`, and create a `UserPlayerLink` through `link_service`.
+
+Accounts must not duplicate player creation, player matching, or player merge behavior. If a player does not exist yet, staff should use the player import/player identity workflow owned by `players` before creating the login account.
+
 ### Creating Coach Accounts

 Workflow:
@@ -13104,8 +13143,8 @@ Workflow:
 Rules:

 - Parent role does not grant staff access.
-- A parent can be linked to multiple players.
-- A player can have multiple parent or guardian links.
+- One parent may be linked to multiple players. This is expected behavior for siblings or multi-player households.
+- One player may have multiple parents or guardians. This is expected behavior and should not be treated as a duplicate-link problem unless the same active `(user, player, relationship)` already exists.

 ### Creating Guest Evaluators

@@ -13157,7 +13196,9 @@ Workflow:

 Rules:

-- Do not delete users for routine deactivation.
+- Deactivation is the normal account lifecycle operation.
+- Deletion is exceptional and should not be part of routine Account Operations.
+- Preserve account, profile, link, observation, and import history whenever possible.
 - Deactivation should block login.
 - Existing observations and historical links remain valid.
 - Superuser self-deactivation should be blocked.
@@ -13177,6 +13218,10 @@ Rules:
 - Username changes must be explicit and recorded in user-facing confirmation messaging.
 - The service should avoid changing linked players or account role.
 - Existing `username_service` should remain the owner of username normalization and uniqueness helpers.
+- The default generated username format remains `firstname.lastname`.
+- Username collisions must be resolved by `username_service`.
+- Manual username changes must go through `username_service`.
+- Views must never implement username generation, normalization, or collision rules.

 ### Changing Roles

@@ -13316,7 +13361,8 @@ Continue using existing service boundaries.
 `accounts.services.account_operations_service`

 - Thin orchestration layer for staff account operations that touch multiple account services.
-- Manual account creation.
+- Account-only creation for coach, guest evaluator, parent, and staff accounts.
+- Player account creation from an existing `players.Player`.
 - User activation/deactivation.
 - Username changes.
 - Role changes.
@@ -13325,6 +13371,15 @@ Continue using existing service boundaries.

 Do not place account operation business logic in views, Analytics services, or player services.

+Player lookup for player-account creation should use `players` services or query helpers. Account Operations may select an existing player, but it must not implement player matching or duplicate player identity rules.
+
+No subsystem should bypass another subsystem's services:
+
+- `players` owns player identity and player import/matching.
+- `accounts` owns authentication, profiles, roles, passwords, usernames, and user-player links.
+- `analytics` owns evaluations, observations, evaluator snapshots, metrics, reports, and Analytics UI.
+- `drafts` owns draft workflow and draft actions.
+
 ## 7. Permissions

 Account operations must preserve the distinction between Django permissions and platform roles.
@@ -13437,14 +13492,17 @@ Goals:

 - Allow staff to create coach, parent, player, and guest evaluator accounts.
 - Allow superusers to create staff accounts.
+- Keep account-only creation distinct from player account creation.

 Deliverables:

 - `/accounts/users/create/`;
-- service-backed manual account creation;
+- service-backed account-only creation for coach, parent, guest evaluator, and staff users;
+- service-backed player account creation that starts from an existing `players.Player`;
 - role assignment through `profile_service`;
 - temporary password setup through `password_service`;
-- tests for duplicate username/email, role defaults, staff restrictions, and password-change requirement.
+- optional user-player link creation through `link_service`;
+- tests for duplicate username/email, role defaults, staff restrictions, player-account creation from existing players, no player duplication, and password-change requirement.

 ### Phase C: Link Management

@@ -13509,11 +13567,18 @@ Possible deliverables:

 Bulk operations should be deferred if implementation pressure would weaken safety or clarity.

+### Explicitly Deferred: Bulk Coach Import
+
+Bulk coach import is outside the current Platform V1 Account Operations roadmap. Once manual coach operations are proven stable, a future engineering plan may introduce bulk coach import using the same service architecture established for player provisioning.
+
+That future plan should define CSV format, matching rules, duplicate detection, role assignment, password reset behavior, and safety checks before implementation begins.
+
 ## 10. Risks

 - Incorrect role assignment could make reporting and evaluator snapshots misleading.
 - Confusing `AccountProfile.role` with Django `is_staff` / `is_superuser` could accidentally grant or deny operational access.
 - Duplicate users may be created if search and creation do not check username and email carefully.
+- Duplicate account resolution and account merge are intentionally deferred because they can affect authentication, user-player links, historical observations, and operational history.
 - Incorrect user-player links could expose player context to the wrong account.
 - Deleting links instead of deactivating them would lose operational history.
 - Deactivating users incorrectly could lock out staff or superusers.
@@ -13533,6 +13598,7 @@ Bulk operations should be deferred if implementation pressure would weaken safet
 - Should assigning `AccountProfile.role=admin` require superuser even if it does not grant Django admin access?
 - Should changing `User.is_staff` be included in this operational UI, or remain in Django admin for Platform V1?
 - Should bulk operations be included in the initial implementation or deferred until after single-account workflows are proven in production?
+- Should account merge and duplicate account resolution be planned as a later Platform V1 operations extension or deferred to a future platform version?
 - Should account-operation changes eventually produce audit records? This plan treats audit logging as out of scope, but production operations may require it later.

 ## Definition Of Done
```
