# Account Management V1

Account Management V1 is the platform account foundation for the VCB baseball system. It is the shared identity layer for current and future subsystems that need authenticated users, account metadata, or user-to-player relationships.

It separates login identity from baseball player identity while still allowing the two to be connected when needed. The subsystem uses Django's built-in `User` model for authentication, adds account profile and role metadata in the `accounts` app, and links users to canonical `players.Player` records through explicit relationship records.

Account Management centralizes authentication, account metadata, and user-player relationships while intentionally keeping those concerns out of `players`, `analytics`, and `drafts`. Those apps may consume Account Management services, but they should not own login-account business rules.

Account Management V1 exists to solve these problems:

- give the platform a production-oriented login/account layer independent of legacy PDP behavior
- define account roles without changing Django staff/superuser permissions
- connect login users to canonical players without putting auth fields on `players.Player`
- optionally provision player login accounts from player imports
- force temporary-password users to change passwords before using normal app pages
- preserve Analytics V1 behavior where any authenticated user may evaluate any player

Relationship to other subsystems:

- `players`: owns canonical player identity. Account Management links to `players.Player` but does not replace it.
- `analytics`: owns observations, reports, timelines, comparisons, and evaluator workflows. It may use account roles later, but Account Management does not own Analytics data.
- `drafts`: owns draft workflows. Account Management does not change draft behavior.
- `pdp`: legacy/transitionary. PDP remains installed and functional, but Account Management is the platform-forward account layer.

## Guiding Principles

- Player identity is independent from login identity because the same canonical player record must serve Analytics, drafts, future PDP, video, attendance, recruiting, awards, and portals.
- Django `User` remains the authentication authority so the platform can rely on Django's mature password hashing, session handling, admin integration, and auth ecosystem.
- Authentication and authorization are separate concerns. Logging in proves identity; staff/admin access is still controlled by Django staff/superuser flags.
- Business rules belong in services because account creation, linking, provisioning, and role decisions need to be reusable, testable, and explicit.
- Provisioning is explicit and idempotent because imports may be retried and must not create duplicate users, profiles, or links.
- Middleware enforces authentication state only. It should redirect users who must change passwords, not orchestrate account workflows.
- Future portals should consume Account Management services rather than owning account logic themselves.

## Design Principles

- Player identity is independent from login identity. `players.Player` must not depend on Django `User`.
- Authentication and authorization are separate concerns. Django `User.is_staff` and `User.is_superuser` control staff/admin access; `AccountProfile.role` is platform role metadata.
- Services own business rules. Views, templates, import UI, and middleware should call services rather than duplicating account logic.
- Views stay thin. Account views primarily call Django auth views or account services.
- Templates stay presentational. They render forms and account summaries only.
- Explicit services are preferred over signals. Account profiles, links, and provisioning are created through service calls so behavior remains intentional and testable.
- Middleware is used only for authentication enforcement. It should redirect forced-password users and avoid wider account orchestration.
- Provisioning is idempotent. Re-running import provisioning should not create duplicate users, profiles, or player links.
- Account provisioning activates imported player accounts immediately, while still requiring temporary-password users to change passwords before normal access.

## Architecture Overview

```text
Django User
    |
    | one-to-one
    v
accounts.AccountProfile
    |
    | role, import provenance, password-change requirement
    |
    | many-to-many through explicit links
    v
accounts.UserPlayerLink
    |
    | relationship: self, parent, guardian, coach, staff
    v
players.Player
    |
    | referenced by
    v
analytics.Observation / drafts workflows / future apps
```

Ownership:

- `accounts` owns login-account metadata, platform roles, account provisioning, user-player links, auth redirects, and forced-password enforcement.
- `players` owns player identity, imports, matching, aliases, source identifiers, source rows, and player tags.
- `analytics` owns observations, evaluator snapshots, metrics, reports, timelines, comparisons, and Analytics UI.
- `drafts` owns draft process and selections.
- `pdp` owns legacy PDP behavior until it is explicitly retired.

Dependency direction:

```text
accounts -> players

analytics -> players
analytics -> accounts

drafts -> players

pdp (legacy, transitionary)
```

Cross-subsystem business rules should normally flow through services. For example, player import remains in `players.services.import_service`, account provisioning remains in `accounts.services.provisioning_service`, and Analytics should call those services instead of directly manipulating another subsystem's models.

## What V1 Implements

## Phase 1

Foundation.

Implemented:

- `accounts` Django app
- `AccountProfile`
- `AccountRole`
- account profile admin
- `profile_service`
- `role_service`
- `permissions`
- tests for profile creation, default roles, role changes, and permission helpers

Purpose:

Phase 1 introduced platform-owned account metadata around Django `User`. It did not replace Django auth or create a custom user model. It established the role vocabulary used by later account, provisioning, and reporting workflows.

## Phase 2

User <-> Player linking.

Implemented:

- `UserPlayerLink`
- `UserPlayerRelationship`
- relationship choices: `self`, `parent`, `guardian`, `coach`, `staff`
- database constraints for active links and primary self links
- account/player link admin
- `link_service`
- tests for constraints, service behavior, deactivation/reactivation, lookup helpers, and ownership boundaries

Purpose:

Phase 2 connected login identities to canonical player identities without adding a `user` field to `players.Player`. The link is an account concern, not a player identity concern.

Important behavior:

- A user can be linked to multiple players.
- A player can be linked to multiple users.
- Active duplicate relationships are blocked.
- A user can have at most one active primary `self` player link.
- A player can have at most one active primary `self` user link.
- Inactive links preserve history and can be corrected without deleting rows.

## Phase 3

Player import account provisioning.

Implemented:

- `username_service`
- `email_service`
- `password_service`
- `provisioning_service`
- optional account-provisioning controls in the existing Analytics import UI
- integration from `players.services.import_service.commit_import_batch()` to account provisioning
- `ProvisioningOptions`
- `ProvisioningResult`
- `ProvisioningSummary`
- idempotent user/profile/link provisioning
- safe import summary counts
- tests for provisioning, duplicate email handling, missing birthdate handling, idempotency, import integration, and no plaintext password leakage

Purpose:

Phase 3 allows staff/admin player imports to optionally provision Django login accounts for committed `players.Player` records. Player identity import remains owned by `players`; account provisioning is owned by `accounts`.

Provisioning behavior:

- Account provisioning is optional.
- Provisioning runs only after player identity rows are committed.
- Existing safe self-linked users are reused.
- Existing unrelated email users produce conflicts.
- Missing birthdate skips account creation.
- New player accounts are active immediately after import provisioning.
- Temporary passwords are generated from player birthdate as `YYYYMMDD`.
- Passwords are set through Django password hashing.
- Plaintext passwords are never stored in summaries, metadata, source rows, or import snapshots.

Provisioning is idempotent. Re-running it should not create duplicate `User`, `AccountProfile`, or `UserPlayerLink` records.

## Phase 4

Authentication and forced password change.

Implemented:

- `/accounts/login/`
- `/accounts/logout/`
- `/accounts/password/`
- `/accounts/profile/`
- account auth templates
- `AccountPasswordChangeRequiredMiddleware`
- `auth_redirect_service`
- project URL registration for `accounts`
- account-forward `LOGIN_URL` and `LOGIN_REDIRECT_URL`
- PDP coexistence tests
- tests for login, logout, password change, forced-password redirects, inactive users, session preservation, and redirect-loop prevention

Purpose:

Phase 4 provides the platform-forward account login flow independent of PDP. It enforces password changes for users with `AccountProfile.must_change_password=True`.

Authentication behavior:

- Login uses Django auth.
- Safe `next` URLs are respected unless forced password change is required.
- Forced-password users are redirected to `/accounts/password/`.
- Password page, login, logout, static/media paths, and superuser admin access are allowed while password change is required.
- Successful password change explicitly saves the new password, clears `must_change_password`, updates the session auth hash, adds a success message, and redirects through `landing_url_for_user()`.
- Staff/admin users land at `/analytics/`.
- Non-staff users land at `/accounts/profile/`.
- PDP routes and middleware remain installed for legacy coexistence.

## Platform V1 Account Operations

Platform V1 Account Operations extends Account Management V1 with staff-facing production operations. These workflows are implemented through Phase F and are frozen for Platform V1.

Implemented sequence:

- Phase A - Account Operations Foundation.
- Phase B - Manual Account Creation.
- Phase C - Account Lifecycle and Link Management.
- Phase D - Operational Password Reset.
- Phase E - Bulk Operations.
- Phase F - Production Hardening / Freeze. This was a freeze review, not a feature phase.

Implemented routes:

- `/accounts/`: staff Account Operations dashboard.
- `/accounts/users/`: staff account list with search, filters, and safe bulk actions.
- `/accounts/users/<id>/`: account detail page.
- `/accounts/create/`: account-only creation for coach, parent, staff, guest evaluator, and other non-player login accounts.
- `/accounts/create/player/`: player-account creation for an existing canonical `players.Player`.
- `/accounts/users/<id>/edit/`: username, email, role, and active-state editing.
- `/accounts/users/<id>/links/`: user-player link create/deactivate/reactivate/primary management.
- `/accounts/users/<id>/password/`: operational password reset.

Main staff workflows:

- review account summary cards and issue queues;
- search and filter accounts by username, name, email, role, active status, staff/superuser status, import status, password-change requirement, and link status;
- create account-only users without creating players;
- create player login accounts from existing `players.Player` records;
- edit username, email, `AccountProfile.role`, and active status;
- activate and deactivate accounts without deleting profile, link, or provenance history;
- link and unlink users and players through `UserPlayerLink`;
- reset a user's password and require password change on next login;
- bulk activate, deactivate, require password change, and clear password-change requirement.

Service ownership:

- `account_query_service` owns account list query/filter behavior.
- `account_operations_service` is the stable public facade for staff Account Operations.
- `accounts.services.account_operations.*` contains the internal Account Operations implementation modules for result contracts, read models, creation, updates, lifecycle, password operations, link orchestration, and bulk operations.
- `username_service` owns username normalization and collision rules.
- `password_service` owns temporary-password generation and password-change flags.
- `link_service` owns all user-player link rules.
- `profile_service` owns account role updates.
- `provisioning_service` owns import/player account provisioning.

Security model:

- Account Operations pages are staff-only and require Django `User.is_staff` or `User.is_superuser`.
- `AccountProfile.role` is platform metadata only.
- `AccountProfile.role = staff` does not grant Django staff access.
- `AccountProfile.role = admin` does not grant Django superuser access.
- Creating or editing an account role never mutates `User.is_staff` or `User.is_superuser`.
- Assigning the platform `admin` role is restricted to Django superusers even though the role itself does not grant Django admin access.
- The system blocks self-deactivation and last-active-superuser deactivation.

Password exposure rules:

- Temporary passwords are shown only immediately after account creation or staff password reset.
- Temporary passwords are not stored in import summaries, metadata, source rows, messages, or account detail pages.
- Player-account temporary passwords use canonical player birthdate as `YYYYMMDD`.
- Non-player operational passwords use generated random temporary passwords.
- All temporary passwords force `must_change_password=True`.

Provenance rules:

- Import-provisioned accounts and links preserve `created_from_import` and `import_batch`.
- Manual account creation does not create import provenance.
- Account activation/deactivation preserves account profile, user-player link, and import provenance history.
- User-player links are deactivated/reactivated rather than deleted in normal operations.

Deferred from Platform V1 Account Operations:

- audit logging;
- account merge;
- duplicate account resolution;
- invitation and email verification flows;
- parent import;
- portal dashboards;
- self-service password recovery email flow.

Season-aware coach import is implemented separately under Seasonal Participation V1 Phase 3. It reuses Account Management services for account creation/reuse, while seasonal team assignments belong to the `seasons` app.

## Service Boundaries

`profile_service`

- Creates or returns `AccountProfile`.
- Sets account roles without changing Django staff/superuser flags.
- Provides account role lookup.

`role_service`

- Defines default role behavior.
- Validates role keys.
- Converts role keys to display labels.
- Falls back to Django staff/superuser state when a profile is missing.

`permissions`

- Contains account permission helpers.
- Uses Django `is_staff` and `is_superuser` for staff/admin account surfaces.
- Keeps evaluation-submission permission broad for V1: any authenticated user can submit evaluations.

`link_service`

- Owns user-player relationship rules.
- Creates, updates, activates, deactivates, and queries `UserPlayerLink`.
- Enforces primary self-link semantics and active duplicate protection.
- Should be used by future views/admin actions instead of writing link rules inline.

`username_service`

- Generates deterministic usernames from player names.
- Normalizes Unicode names to safe username tokens.
- Resolves username collisions with numeric suffixes.

`email_service`

- Normalizes emails for comparison.
- Performs case-insensitive existing-user lookup.
- Keeps email matching rules out of provisioning orchestration.

`password_service`

- Generates birthdate-based temporary passwords.
- Sets hashed temporary passwords.
- Marks and clears `must_change_password`.
- Does not expose plaintext passwords beyond immediate password-setting.

`provisioning_service`

- Orchestrates account provisioning from committed player rows.
- Owns `ProvisioningOptions`, `ProvisioningResult`, and `ProvisioningSummary`.
- Calls username, email, password, profile, and link services.
- Owns idempotency and safe existing-account reuse decisions.
- Must remain the home for account provisioning orchestration.

`auth_redirect_service`

- Owns account URL constants used by auth redirect behavior.
- Determines landing URLs for authenticated users.
- Determines whether a user must change password.
- Determines paths allowed during forced password change.

## Ownership Boundaries

`players` owns:

- canonical player identity
- player imports
- player matching
- player aliases and source identifiers
- source row provenance
- player tags

`players` must not own:

- Django login users
- account roles
- user-player auth relationships
- password rules
- account provisioning decisions

`accounts` owns:

- account profiles
- account roles
- user-player links
- account provisioning
- username/email/password account services
- account auth redirects
- forced password-change middleware
- minimal account profile page

`accounts` must not own:

- canonical player identity
- player import parsing or matching
- Analytics observations
- draft workflow
- PDP migration

`analytics` owns:

- observations and evaluator snapshots
- coach assessment workflows
- reports, metrics, timelines, comparisons
- Analytics UI
- staff-facing player import screens as a current integration surface

`analytics` must not own:

- account provisioning logic
- account roles
- user-player link rules
- player identity import business logic

`drafts` owns:

- draft process
- draft selections
- draft actions and views

`drafts` must not own account or player identity logic.

`pdp` owns:

- legacy PDP models, routes, middleware, and views

`pdp` must not become the dependency for future account identity. New account work should use `accounts` and `players`.

## Authentication Flow

```text
CSV import
    |
    v
players.services.import_service
    |
    | optional account provisioning enabled
    v
accounts.services.provisioning_service
    |
    v
active Django User + AccountProfile + UserPlayerLink
    |
    v
staff Account Operations visibility and correction tools
    |
    v
/accounts/login/
    |
    v
AccountPasswordChangeRequiredMiddleware
    |
    | must_change_password=True
    v
/accounts/password/
    |
    v
clear must_change_password + preserve session
    |
    v
landing_url_for_user()
```

The forced-password middleware is intentionally narrow. It does not provision accounts, decide roles, activate users, or manage links. It only enforces that authenticated users with `must_change_password=True` cannot access normal pages until their password is changed.

## Security Model

Temporary passwords:

- Generated only from canonical `players.Player.birthdate`.
- Format is `YYYYMMDD`.
- Used only as a bootstrap password.
- Must be changed before normal access.

Imported users:

- Imported player accounts are active immediately after provisioning.
- Provisioned users must change the temporary password before normal app access.
- Inactive users still cannot authenticate through Django auth if an administrator later deactivates an account.

Password hashing:

- Passwords are set through Django `User.set_password()`.
- Plaintext temporary passwords are not stored.
- Plaintext passwords are not serialized into import summaries, metadata, source rows, messages, or tests.

Forced password change:

- `AccountProfile.must_change_password=True` blocks normal app access.
- Middleware allows only login, logout, password-change, static/media paths, and superuser admin access.
- Successful password change clears the flag before redirect.
- Session authentication is preserved with `update_session_auth_hash()`.

Role handling:

- `AccountProfile.role` is platform metadata.
- Role values do not grant Django admin or staff access.
- Staff/admin surfaces continue to use `User.is_staff` or `User.is_superuser`.
- `admin` account role alone does not grant Django admin access.

## Current Limitations

These are intentional V1 deferrals:

- email invitation workflow
- email verification workflow
- self-service password recovery email flow
- self-registration
- account merge
- duplicate account resolution
- coach import
- parent import
- player portal
- parent portal
- coach portal
- portal dashboards
- evaluator role snapshot integration with Account Management roles
- audit history for account changes
- custom user model
- social login or SSO
- PDP retirement

These should be layered into future versions or explicit implementation phases. They should not be backfilled into V1 without a separate plan.

## Technical Decisions

Why `UserPlayerLink` exists:

- A player identity and a login identity are different concepts.
- A player can have multiple related users.
- A user can have multiple related players.
- Relationship history can be preserved without changing `players.Player`.

Why `Player` has no `user` field:

- `players.Player` is canonical baseball identity shared across Analytics, drafts, future PDP, video, attendance, recruiting, awards, and portals.
- Authentication is one consumer of player identity, not part of player identity itself.

Why Django `User` was retained:

- Django `User` already provides mature authentication behavior.
- Password hashing, password validation, sessions, and login/logout integration are proven and maintained by Django.
- Django admin and staff tooling work naturally with the built-in auth model.
- The existing project already uses Django auth, so retaining it avoids a risky custom `AUTH_USER_MODEL` migration.
- Django's permission ecosystem remains available for future account-management surfaces.
- Account-specific metadata can live in `AccountProfile` without overloading or replacing the auth model.

Why services are used instead of signals:

- Account creation, linking, and provisioning have important safety rules.
- Explicit services make behavior testable and avoid hidden side effects.
- Future staff/admin workflows can call the same services.

Why provisioning is idempotent:

- Staff may rerun imports or provisioning.
- Duplicate users, profiles, or self-links would create security and operational risks.
- Idempotent services allow safe retries.

Why imported users are activated immediately:

- The operational workflow expects imported player accounts to be usable immediately.
- Forced password change reduces the risk of temporary birthdate passwords being used for normal access.
- Staff can still deactivate accounts manually through Django admin if needed.

Why birthdate temporary passwords are used:

- This matches the current operational bootstrap requirement.
- It is allowed only because forced password change blocks normal app access.
- Long-term replacement should be invitation or password setup links.

Why PDP remains installed:

- PDP is legacy/transitionary but not retired in V1.
- Removing PDP requires its own migration and regression plan.
- Account Management V1 coexists with PDP while establishing the future account boundary.

## Testing

Account Management V1 includes regression coverage across:

- `accounts`
- `players`
- `analytics`
- `drafts`
- `pdp`

Coverage includes:

- account profile defaults and role changes
- permission helpers
- user-player link constraints and services
- username normalization and deterministic suffixes
- email normalization and safe existing-user lookup
- birthdate password generation and hashing
- account provisioning creation, idempotency, duplicate email conflicts, missing birthdate skips, and safe summaries
- player import integration with optional account provisioning
- login/logout/password-change views
- forced-password middleware behavior
- redirect-loop prevention
- inactive user login blocking
- PDP coexistence
- ownership-boundary regressions

Every core V1 phase concluded with implementation review and regression testing. Platform V1 Account Operations has also completed Phase F production hardening/freeze review.

## Lessons Learned

- Explicit services scaled better than signals because account behavior stayed visible and testable.
- Idempotent provisioning simplified import retries and reduced duplicate-account risk.
- Separating player identity from authentication reduced coupling across `players`, `analytics`, and future portals.
- Thin views made refactoring easier because business rules stayed in service modules.
- Review and fix passes after each phase improved architecture quality before the subsystem was frozen.

## Platform Status

```text
Players             V1 Complete
Analytics           V1 Complete
Account Management  V1 Complete
Drafts              Active
LeagueHub           Planned
Video               Planned
```

This status is a high-level orientation for engineers joining the repository. Account Management V1 should now be treated as stable platform infrastructure while future subsystem work builds on top of it.

## Version Status

Account Management V1

Status:

```text
COMPLETE
FROZEN
```

Account Management V1 core account infrastructure is complete. Platform V1 Account Operations is implemented through Phase F and is frozen for Platform V1.

V1 should remain stable. Future work should be added through a new version or explicit implementation phase.

## Future Versions

Likely Account Management V2 work:

- evaluator identity integration
- mapping account roles into Analytics evaluator role snapshots
- email invitation workflow
- email verification workflow
- self-service password recovery email flow
- audit history
- account merge
- duplicate account resolution
- coach import
- parent import
- player portal
- parent portal
- coach portal
- PDP retirement and migration planning

Future versions should continue the V1 principles:

- keep player identity independent from login identity
- keep account business logic in `accounts` services
- keep player import identity logic in `players`
- keep Analytics observation/reporting logic in `analytics`
- avoid hidden signal behavior unless a clear operational need appears
- preserve conservative security defaults
