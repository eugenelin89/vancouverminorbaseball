# Platform V1 Account Operations Engineering Plan

## 1. Objectives

Players V1, Analytics V1, Account Management V1, and the platform architecture documentation are complete and frozen. The remaining gap is operational: staff can authenticate users, provision accounts from imports, link users to players, and force password changes, but they do not yet have production-ready screens for day-to-day account management.

This plan defines the remaining account-management work required to make Platform V1 production-ready. It extends Platform V1 operations without introducing a new architecture version.

The objectives are:

- give authorized staff a clear way to search, inspect, create, update, activate, deactivate, and reset user accounts;
- manage coach, parent, staff, player, and guest evaluator accounts without using Django admin for routine operations;
- manually link and unlink users to canonical `players.Player` records;
- preserve the existing separation between Django login identity, account metadata, and player identity;
- keep account operations in the `accounts` bounded context;
- reuse existing services wherever possible;
- avoid exposing plaintext temporary passwords or duplicating account business rules in views.

## 2. Scope

This work includes operational account-management functionality for Platform V1:

- Staff account administration.
- Coach account management.
- Parent account management.
- Guest evaluator account management.
- Manual account creation.
- Manual player linking.
- Manual player unlinking.
- Account role management.
- Account activation and deactivation.
- Password reset to a temporary password.
- Username management.
- Account search and filtering.
- Account detail page.
- Linked player display.
- Linked user display.
- Bulk operations where they are simple, safe, and clearly reversible.

The work should use the existing models:

- Django `User`
- `accounts.AccountProfile`
- `accounts.UserPlayerLink`
- `players.Player`

New account-operation services may be added if they clarify orchestration, but new models should not be introduced unless implementation reveals a concrete production requirement that cannot be handled with existing data.

## 3. What Is NOT Included

This plan does not include:

- OAuth.
- SSO.
- Social login.
- Email verification.
- Invitation emails.
- Notification delivery.
- Parent portal dashboards.
- Player portal dashboards.
- Coach portal dashboards.
- Fine-grained permission management UI.
- API endpoints.
- Background jobs.
- Caching.
- Audit logging, unless a separate accepted plan introduces it.
- Custom `AUTH_USER_MODEL`.
- PDP account migration.
- Analytics evaluator workflow changes.
- Draft workflow changes.
- Saved reports or analytics dashboards.

## 4. Proposed UI

Create staff-only account operations pages under `/accounts/`.

Recommended routes:

```text
/accounts/
/accounts/users/
/accounts/users/create/
/accounts/users/<id>/
/accounts/users/<id>/edit/
/accounts/users/<id>/links/
/accounts/users/<id>/links/add/
/accounts/users/<id>/links/<link_id>/deactivate/
/accounts/users/<id>/links/<link_id>/activate/
/accounts/users/<id>/password/
/accounts/users/<id>/username/
/accounts/users/<id>/role/
/accounts/users/<id>/activate/
/accounts/users/<id>/deactivate/
/accounts/players/<player_id>/users/
```

Recommended page responsibilities:

- `/accounts/`: Account Operations landing page with summary counts, common actions, and links.
- `/accounts/users/`: Searchable user list with filters for role, active status, staff status, linked-player status, and forced password-change status.
- `/accounts/users/create/`: Manual account creation form.
- `/accounts/users/<id>/`: Account detail page showing Django user fields, account profile role, password-change state, linked players, and safe operational actions.
- `/accounts/users/<id>/edit/`: Basic editable account metadata such as first name, last name, and email.
- `/accounts/users/<id>/links/`: User-player link management page.
- `/accounts/users/<id>/password/`: Staff password reset page that forces password change.
- `/accounts/users/<id>/username/`: Username change page.
- `/accounts/users/<id>/role/`: Role management page.
- `/accounts/users/<id>/activate/`: Confirmation page for activating a user.
- `/accounts/users/<id>/deactivate/`: Confirmation page for deactivating a user.
- `/accounts/players/<player_id>/users/`: Player-centered view of linked users.

Navigation:

- Add an Account Operations link for staff users where staff operational navigation already exists.
- The Analytics Command Center may link to Account Operations because Analytics staff will often discover account issues while reviewing imports, assessments, and players.
- Do not make Analytics own or render account-operation business logic. Links should route to `accounts` pages.

Templates should be server-rendered and consistent with the existing simple Django template approach. Avoid JavaScript-driven admin workflows for Platform V1 operations.

## 5. Operations

### Creating Coach Accounts

Workflow:

1. Staff opens manual account creation.
2. Staff enters username, name, email, and role `coach`.
3. Staff chooses whether the account is active immediately.
4. Service creates Django `User`, creates or updates `AccountProfile`, sets role `coach`, sets temporary password, and marks password change required.
5. Staff may optionally link coach account to players using relationship `coach`.

Rules:

- Coach role does not automatically grant Django staff access.
- Staff access requires `User.is_staff=True` or `User.is_superuser=True`.
- Password should be generated or entered through a safe staff reset workflow; do not display stored plaintext.

### Creating Parent Accounts

Workflow:

1. Staff creates a user with role `parent`.
2. Staff links the account to one or more players with relationship `parent` or `guardian`.
3. User must change password on first login.

Rules:

- Parent role does not grant staff access.
- A parent can be linked to multiple players.
- A player can have multiple parent or guardian links.

### Creating Guest Evaluators

Workflow:

1. Staff creates a user with role `guest_evaluator`.
2. Staff may leave the account unlinked, or link it to known players if operationally useful.
3. User must change password on first login.

Rules:

- Guest evaluators can authenticate and submit evaluations only if existing Analytics permissions allow authenticated evaluation.
- Guest evaluator role is metadata for reporting and evaluator snapshots, not staff access.

### Creating Staff Accounts

Workflow:

1. Superuser creates or updates a user.
2. Superuser sets `User.is_staff=True` where staff operational access is required.
3. Superuser sets `AccountProfile.role` to `staff` or `admin` as appropriate.
4. User must change password on first login if a temporary password is set.

Rules:

- Staff account operations should require superuser for creating or granting staff/superuser capabilities.
- `AccountProfile.role=staff` alone must not grant staff-only view access.
- `AccountProfile.role=admin` alone must not grant Django admin access.

### Activating Imported Players

Current import provisioning creates active users immediately and requires password change. Account Operations should provide visibility and correction tools:

- show imported player accounts;
- show whether password change is still required;
- allow staff to activate inactive imported accounts if one was manually deactivated;
- allow staff to deactivate accounts that should not be usable.

Activation should call an account service and update Django `User.is_active`. If `AccountProfile.is_active` remains present, service behavior must keep it consistent or clearly define it as platform metadata.

### Deactivating Users

Workflow:

1. Staff opens user detail.
2. Staff confirms deactivation.
3. Service sets `User.is_active=False`.
4. Service preserves `AccountProfile` and `UserPlayerLink` history.

Rules:

- Do not delete users for routine deactivation.
- Deactivation should block login.
- Existing observations and historical links remain valid.
- Superuser self-deactivation should be blocked.
- Staff should not be able to deactivate the last superuser.

### Changing Usernames

Workflow:

1. Staff opens username change page.
2. Staff enters a new username or uses a suggested username.
3. Service validates normalization, uniqueness, and collision rules.
4. Service updates `User.username`.

Rules:

- Username changes must be explicit and recorded in user-facing confirmation messaging.
- The service should avoid changing linked players or account role.
- Existing `username_service` should remain the owner of username normalization and uniqueness helpers.

### Changing Roles

Workflow:

1. Staff opens role page.
2. Staff selects a valid `AccountProfile.role`.
3. Service updates account profile role.

Rules:

- Role changes do not change Django `is_staff` or `is_superuser`.
- Role changes do not alter historical Analytics evaluator snapshots.
- Superuser should be required for assigning `admin` role or making a user staff through Django flags.

### Resetting Passwords

Workflow:

1. Staff opens password reset page.
2. Staff chooses a reset mode:
   - generated random temporary password; or
   - birthdate-based temporary password for self-linked player accounts, if still accepted operationally.
3. Service sets the password through Django password hashing.
4. Service sets `must_change_password=True`.
5. Staff is shown only the temporary password at the moment of reset if the chosen workflow requires staff delivery.

Rules:

- Never store plaintext passwords.
- Never write plaintext passwords into logs, import summaries, metadata, source rows, or snapshots.
- Password reset should not deactivate the user.
- Password reset should preserve sessions only for the current user password-change flow, not staff reset of other accounts.

### Linking Users To Players

Workflow:

1. Staff opens user link page.
2. Staff searches for a canonical `players.Player`.
3. Staff selects relationship: `self`, `parent`, `guardian`, `coach`, or `staff`.
4. Service creates or updates the active link.

Rules:

- Use `accounts.services.link_service`.
- Respect active duplicate relationship constraints.
- Respect primary self-link constraints.
- Do not add auth fields to `players.Player`.

### Unlinking Users

Workflow:

1. Staff opens user link page.
2. Staff deactivates a link.
3. Service marks the link inactive instead of deleting it.

Rules:

- Preserve link history.
- Unlinking should not deactivate the user.
- Unlinking should not alter player identity.

### Viewing Linked Players

Account detail should display:

- active linked players;
- inactive linked players if staff chooses to show history;
- relationship type;
- primary status;
- import provenance where relevant.

### Viewing Linked Users

Player-centered account view should display:

- active linked users;
- inactive linked users if staff chooses to show history;
- relationship type;
- role;
- active login state;
- forced password-change state.

## 6. Service Ownership

Continue using existing service boundaries.

### Existing Services

`accounts.services.profile_service`

- Owns account profile creation and role assignment.
- Should continue to own `AccountProfile.role` updates.
- May gain read helpers for account detail display if they are profile-specific.

`accounts.services.link_service`

- Owns user-player link creation, activation, deactivation, lookup, and primary-link rules.
- Should be used by all link management views.

`accounts.services.password_service`

- Owns temporary-password generation, password setting, and password-change requirement state.
- Should gain staff reset helpers if needed.

`accounts.services.username_service`

- Owns username normalization and uniqueness.
- Should gain manual username validation/change helpers if needed.

`accounts.services.provisioning_service`

- Owns account provisioning from players/imports.
- Should not become the general staff account operations service unless the operation is provisioning-specific.

`accounts.services.auth_redirect_service`

- Owns authenticated landing URLs and account redirect constants.
- Account Operations should import shared route constants rather than hardcoding paths if constants already exist or are added.

`accounts.services.permissions`

- Owns account-operation permission helpers.
- Should distinguish staff-only operations from superuser-only operations.

### Recommended New Services

`accounts.services.account_query_service`

- Reusable user search and filtering.
- Account list queryset construction.
- Search by username, first name, last name, email, role, active status, staff status, and linked player.
- Should use `select_related("account_profile")` and prefetch links where practical.

`accounts.services.account_operations_service`

- Thin orchestration layer for staff account operations that touch multiple account services.
- Manual account creation.
- User activation/deactivation.
- Username changes.
- Role changes.
- Staff password reset orchestration.
- Should call the specialized services rather than duplicating their rules.

Do not place account operation business logic in views, Analytics services, or player services.

## 7. Permissions

Account operations must preserve the distinction between Django permissions and platform roles.

`AccountProfile.role` does not replace Django `User.is_staff` or `User.is_superuser`.

Recommended access rules:

### Regular Authenticated Users

May access:

- own profile page;
- own forced password-change page;
- normal authenticated app pages allowed by each subsystem.

May not access:

- account user list;
- account detail pages for other users;
- manual account creation;
- role changes;
- activation/deactivation;
- staff password resets;
- user-player link management.

### Staff Users

Definition:

- `User.is_staff=True` or `User.is_superuser=True`.

May access:

- Account Operations landing page;
- user list and search;
- user detail pages;
- parent, coach, player, and guest evaluator account creation where no staff/superuser flags are granted;
- user-player link management;
- non-privileged role changes;
- password reset for non-staff users;
- activation/deactivation for non-superuser accounts, subject to safety checks.

May not access unless also superuser:

- granting Django staff status;
- granting superuser status;
- creating staff users;
- assigning `admin` role if it is treated as privileged;
- deactivating superusers;
- deactivating the last active superuser.

### Superusers

May access:

- all staff operations;
- create staff accounts;
- grant or remove Django staff status;
- assign `admin` role;
- manage other staff accounts, subject to self-lockout protection.

Safety rules:

- No user should be able to deactivate themselves through Account Operations.
- No operation should remove the last active superuser.
- Permission helpers should be testable and reused by views.

## 8. UX Principles

- Keep views thin. Views should validate permissions, bind forms, call services, and redirect/render.
- Keep business logic in services.
- Keep templates presentation-only.
- Use confirmation pages for destructive or access-changing operations.
- Prefer deactivation over deletion.
- Preserve historical links and observations.
- Make idempotent operations safe to repeat.
- Avoid duplicate business rules in forms, views, and templates.
- Avoid exposing temporary passwords except at the moment a reset is intentionally performed.
- Make account state visible: active/inactive, role, staff flag, superuser flag, password-change requirement, and linked players.
- Display clear warnings when a role does not grant staff access.
- Display clear warnings when staff access is controlled by Django `is_staff` or `is_superuser`.
- Use server-rendered pages consistent with the rest of the platform.

## 9. Future Phases

Implementation should be split into small, independently testable phases.

### Phase A: Account Operations Foundation

Goals:

- Add account operation permission helpers.
- Add account search/query service.
- Add Account Operations landing page.
- Add user list and user detail pages.

Deliverables:

- staff-only `/accounts/`;
- staff-only `/accounts/users/`;
- staff-only `/accounts/users/<id>/`;
- search/filter forms;
- read-only linked player and profile summaries;
- tests for staff access, non-staff denial, search, filtering, and empty states.

### Phase B: Manual Account Creation

Goals:

- Allow staff to create coach, parent, player, and guest evaluator accounts.
- Allow superusers to create staff accounts.

Deliverables:

- `/accounts/users/create/`;
- service-backed manual account creation;
- role assignment through `profile_service`;
- temporary password setup through `password_service`;
- tests for duplicate username/email, role defaults, staff restrictions, and password-change requirement.

### Phase C: Link Management

Goals:

- Allow staff to manually link and unlink users and players.
- Provide player-centered linked-user view.

Deliverables:

- `/accounts/users/<id>/links/`;
- `/accounts/users/<id>/links/add/`;
- link activation/deactivation actions;
- `/accounts/players/<player_id>/users/`;
- tests for duplicate active links, primary self-link constraints, link history preservation, and permission checks.

### Phase D: Account State And Role Operations

Goals:

- Allow staff to manage active status and account roles safely.
- Allow superusers to manage privileged staff/admin state.

Deliverables:

- activate/deactivate confirmation pages;
- role change page;
- staff/superuser guardrails;
- self-lockout prevention;
- last-superuser protection;
- tests for all safety rules.

### Phase E: Password And Username Operations

Goals:

- Allow staff to reset passwords and change usernames through services.

Deliverables:

- password reset page;
- username change page;
- generated temporary password flow or approved birthdate reset flow;
- forced password-change after staff reset;
- username collision handling;
- tests proving no plaintext password persistence and correct password-change enforcement.

### Phase F: Bulk Operations And Polish

Goals:

- Add only low-risk bulk actions after single-user operations are stable.

Possible deliverables:

- bulk activate selected users;
- bulk deactivate selected users;
- bulk require password change;
- bulk role update only if safe and restricted;
- improved filters for imported accounts and linked/unlinked accounts;
- tests for partial failures and permission restrictions.

Bulk operations should be deferred if implementation pressure would weaken safety or clarity.

## 10. Risks

- Incorrect role assignment could make reporting and evaluator snapshots misleading.
- Confusing `AccountProfile.role` with Django `is_staff` / `is_superuser` could accidentally grant or deny operational access.
- Duplicate users may be created if search and creation do not check username and email carefully.
- Incorrect user-player links could expose player context to the wrong account.
- Deleting links instead of deactivating them would lose operational history.
- Deactivating users incorrectly could lock out staff or superusers.
- Password reset workflows could expose temporary passwords if summaries, logs, or metadata are not carefully controlled.
- Username changes could create collisions or make staff unable to find accounts.
- Imported player accounts may be active immediately, so staff need clear visibility into which accounts still require password changes.
- Bulk operations could cause large accidental access changes if not carefully confirmed and permission-guarded.
- Without audit logging, staff may have limited historical visibility into who performed account changes. Audit logging is out of scope for this plan unless separately approved.

## 11. Open Questions

- Should staff-created temporary passwords be random-only, or should birthdate-based temporary passwords remain available for player-linked accounts?
- Should parent accounts require email uniqueness, or can multiple accounts share a family email address?
- Should coach accounts be linked to specific players, teams, or both? The current model supports player links but does not model team assignments.
- Should account operations expose inactive link history by default or behind an explicit "show history" option?
- Should `AccountProfile.is_active` be kept synchronized with `User.is_active`, or treated as platform metadata only?
- Should assigning `AccountProfile.role=admin` require superuser even if it does not grant Django admin access?
- Should changing `User.is_staff` be included in this operational UI, or remain in Django admin for Platform V1?
- Should bulk operations be included in the initial implementation or deferred until after single-account workflows are proven in production?
- Should account-operation changes eventually produce audit records? This plan treats audit logging as out of scope, but production operations may require it later.

## Definition Of Done

This roadmap is ready for implementation when:

- each phase has a detailed implementation prompt or engineering plan;
- permission rules are confirmed;
- password reset behavior is confirmed;
- role/staff/superuser boundaries are confirmed;
- the first implementation phase can be built without introducing new architecture decisions.
