# Account Management v1 Engineering Plan

## Goals

Account Management v1 prepares the VCB baseball platform for production use by separating login identity from player identity while connecting them where needed.

The main goals are:

- Create a platform-owned account profile foundation around Django `User`.
- Define platform roles for analytics, permissions, and reporting.
- Link Django users to canonical `players.Player` records.
- Allow staff/admin player imports to provision login accounts for imported players.
- Force imported users with temporary passwords to change password on first login.
- Preserve Analytics v1 behavior: any authenticated user may evaluate any player.
- Snapshot evaluator role on submitted evaluations for historical reporting.
- Keep staff/admin surfaces restricted to staff/admin users.

## Non-Goals

Do not implement these in Account Management v1:

- A custom Django user model.
- Social login or SSO.
- Email delivery infrastructure.
- Password reset email integration unless already available.
- Public self-registration.
- Parent/player portals.
- Advanced role-based access control.
- Group/permission administration UI.
- Changes to Analytics observation, reporting, draft, or import architecture beyond account provisioning hooks.
- PDP migration.

## Current State

### Analytics

- Analytics v1 is complete.
- `players.Player` is the canonical player identity model.
- `analytics.Observation` references `players.Player`.
- `Observation.evaluator` references Django `User`.
- `Observation` stores evaluator role snapshots:
  - `evaluator_role`
  - `evaluator_role_key`
  - `evaluator_role_name`
- `analytics.services.permissions.can_submit_coach_assessment(user)` currently allows any authenticated user.
- Staff/admin Analytics views use `is_staff` or `is_superuser`.
- Player CSV import creates/updates `players.Player`, not Django users.
- Player import logic lives in `players.services.import_service`.
- Analytics import views are thin UI orchestration.

### Authentication

- The project uses Django's default auth `User`.
- There is no custom `AUTH_USER_MODEL`.
- `LOGIN_URL` currently points to `/pdp/login/`.
- `LOGIN_REDIRECT_URL` currently points to `/pdp/`.
- `pdp` provides login, logout, and password-change views.
- `pdp.middleware.FirstLoginPasswordChangeMiddleware` forces password change only for legacy `pdp.PlayerProfile.must_change_password`.
- `scholarships` has a separate applicant login/signup flow.
- There is no platform-wide account profile model.
- There is no Analytics-owned account or role model.
- There is no link between `players.Player` and Django `User`.

### Existing Auth / Account / Role Documentation Discovered

- `docs/analytics/architecture/10_permissions.md`
- `docs/analytics/architecture/03_analytics.md`
- `docs/analytics/architecture/04_imports.md`
- `docs/analytics/implementation/repository_assessment.md`
- `docs/pdp.md`
- `docs/prompts/pdp_prompt.md`
- `docs/prompts/scholarship.md`

These documents are useful context, but Account Management v1 should not depend on PDP because PDP is transitionary.

## Proposed App And Model Ownership

Create a new Django app:

```text
accounts/
```

Ownership:

- `accounts` owns login-account profile data, platform roles, password-change requirement state, account provisioning, user/player links, and account-management UI.
- `players` continues to own canonical player identity, imports, matching, source identifiers, source rows, and provenance.
- `analytics` continues to own observations, evaluations, evaluator role snapshots, metrics, reports, timelines, and comparisons.
- `drafts` continues to own draft workflow.

Account provisioning should be callable from `players.services.import_service`, but provisioning logic should live in `accounts.services.provisioning_service`.

Do not place account-management business logic in `analytics`.

## Proposed Models

### `accounts.AccountProfile`

One profile per Django user.

Suggested fields:

- `user`: `OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="account_profile")`
- `role`: `CharField(max_length=40, choices=AccountRole.choices, default=AccountRole.GUEST_EVALUATOR)`
- `must_change_password`: `BooleanField(default=False)`
- `created_from_import`: `BooleanField(default=False)`
- `import_batch`: nullable `ForeignKey("players.PlayerImportBatch", on_delete=models.SET_NULL, blank=True, null=True)`
- `is_active`: `BooleanField(default=True)`
- `activated_at`: nullable `DateTimeField`
- `deactivated_at`: nullable `DateTimeField`
- `created_at`
- `updated_at`
- `metadata`: `JSONField(default=dict, blank=True)`

Notes:

- `AccountProfile.is_active` should not replace `User.is_active`. Use it for platform-level account state if needed.
- `User.is_active=False` should block login.
- Imported player accounts may start active or inactive depending on the final security decision.

### `accounts.AccountRole`

Use `models.TextChoices` rather than a database lookup for v1 unless implementation reveals a strong need for staff-managed role records.

Required choices:

- `admin`
- `staff`
- `coach`
- `player`
- `parent`
- `guest_evaluator`

Role meanings:

- `admin`: platform administrator role; should generally align with `is_superuser` or designated staff.
- `staff`: staff/admin workflow access when paired with Django `is_staff=True`, or used for reporting.
- `coach`: authenticated evaluator/coach role.
- `player`: imported player account default.
- `parent`: future parent/guardian account role.
- `guest_evaluator`: authenticated evaluator without a stronger role assignment.

### `accounts.UserPlayerLink`

Links Django users to canonical players.

Suggested fields:

- `user`: `ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="player_links")`
- `player`: `ForeignKey("players.Player", on_delete=models.CASCADE, related_name="user_links")`
- `relationship`: `CharField(max_length=40, choices=UserPlayerRelationship.choices)`
- `is_primary`: `BooleanField(default=False)`
- `is_active`: `BooleanField(default=True)`
- `created_from_import`: `BooleanField(default=False)`
- `import_batch`: nullable `ForeignKey("players.PlayerImportBatch", on_delete=models.SET_NULL, blank=True, null=True)`
- `created_at`
- `updated_at`
- `metadata`: `JSONField(default=dict, blank=True)`

Suggested relationships:

- `self`
- `parent`
- `guardian`
- `coach`
- `staff`

Constraints:

- Unique active relationship per `(user, player, relationship)` if practical.
- At most one active primary `self` link per user.
- A player may have multiple linked users over time.

## Role Definitions

Role is a platform/account concept, not a replacement for Django admin flags.

Rules:

- `User.is_staff` and `User.is_superuser` continue to control Django admin and staff/admin views unless explicitly changed later.
- `AccountProfile.role` is used for evaluator-role snapshots, reporting, and non-admin permission checks.
- `player` role does not imply staff access.
- `parent` role does not imply staff access.
- `coach` role does not automatically imply staff access.
- `admin` role should not grant Django admin access unless `User.is_staff` or `User.is_superuser` is also set.

Recommended default mapping:

| User State | Account Role |
| --- | --- |
| `is_superuser=True` | `admin` |
| `is_staff=True` and not superuser | `staff` |
| Imported player account | `player` |
| Authenticated account without explicit role | `guest_evaluator` |

## Phase 1 - User Profile And Role Foundation

Purpose:

- Introduce the platform account profile model and role definitions.

Scope:

- Create `accounts` app.
- Add `AccountProfile`.
- Add role choices.
- Add account profile service helpers.
- Add admin registration.
- Add tests for profile creation and role defaults.

Out of scope:

- User/player links.
- Import provisioning.
- Login/password-change behavior.
- Staff UI beyond admin registration.

Key services:

- `accounts.services.profile_service.get_or_create_account_profile(user)`
- `accounts.services.profile_service.role_for_user(user)`
- `accounts.services.profile_service.set_account_role(user, role, actor=None)`

Open question:

- Whether to auto-create profiles with a signal or create them lazily through services. Recommendation: use explicit service creation first; consider a signal only if repeated missing-profile handling becomes noisy.

## Phase 2 - Player/User Linking

Purpose:

- Link login users to canonical `players.Player` records without making `players.Player` depend on auth.

Scope:

- Add `UserPlayerLink`.
- Add relationship choices.
- Add service helpers to create/update/deactivate links.
- Add admin registration.
- Add tests for linking constraints and lookups.

Out of scope:

- Import provisioning.
- Parent portal behavior.
- Player profile pages for logged-in players.

Recommended services:

- `accounts.services.link_service.link_user_to_player(user, player, relationship="self", is_primary=True, created_from_import=False, import_batch=None)`
- `accounts.services.link_service.get_players_for_user(user)`
- `accounts.services.link_service.get_users_for_player(player)`
- `accounts.services.link_service.deactivate_link(link, actor=None)`

Ownership decision:

- The link belongs in `accounts` because it connects auth users to player identity.
- `players` should not own login-user concerns.
- `analytics` should consume links only when needed.

## Phase 3 - Player Import Account Provisioning

Purpose:

- Allow staff/admin player imports to optionally provision linked player login accounts.

Scope:

- Extend player import UI with an account-provisioning option.
- Keep parsing/matching/commit logic in `players.services.import_service`.
- Call account provisioning service from import commit flow when selected.
- Create/update user account.
- Create/update `AccountProfile`.
- Create/update `UserPlayerLink` with relationship `self`.
- Store account-provisioning summary in import result metadata without exposing raw passwords broadly.

Recommended services:

- `accounts.services.provisioning_service.provision_player_account(player, import_batch=None, actor=None)`
- `accounts.services.provisioning_service.username_for_player(player)`
- `accounts.services.provisioning_service.temporary_password_for_player(player)`
- `accounts.services.provisioning_service.provision_accounts_for_import(import_batch, players, actor=None)`

Default behavior:

- Imported users receive `AccountProfile.role = "player"`.
- Imported users receive `AccountProfile.created_from_import = True`.
- Imported user/player links use relationship `self`.
- `must_change_password=True`.

Temporary password rule:

- If `player.birthdate` exists, temporary password is `YYYYMMDD`.
- Example: birthdate `2012-05-01` -> `20120501`.

Missing birthdate fallback:

- Recommended v1 behavior: do not create an active login account automatically when birthdate is missing.
- Mark the row/account as requiring staff review.
- Optionally create the user inactive with an unusable password if staff explicitly chooses that flow.
- Do not invent weak passwords from names or teams.

Activation decision:

- Recommended v1 default: imported player accounts are inactive until staff activates them or confirms the onboarding batch.
- If operational simplicity is preferred, allow staff to select "activate immediately" during import, but keep default conservative.

Username behavior:

- Prefer email as username if a permissioned email field is mapped and unique.
- If no email is available, generate a username from first + last name.
- If username conflicts, append a numeric suffix.
- Username generation must be deterministic and testable.

Email behavior:

- Email should be optional for player accounts.
- If email exists and belongs to an existing user, do not silently attach it to a different player.
- Duplicate email should produce a staff-review conflict unless it resolves to the same linked player/user.

Password handling:

- Do not log plaintext passwords.
- Do not store plaintext passwords.
- Avoid displaying plaintext passwords except possibly a one-time staff-facing provisioning result if absolutely required.
- Long term, password setup/reset links are preferable.

Provenance:

- Record `created_from_import=True`.
- Record `import_batch`.
- Include non-sensitive provisioning counts in `PlayerImportBatch.import_summary`.
- Do not put plaintext passwords into `PlayerImportBatch.preview_snapshot`, `row_errors`, `conflict_summary`, or `import_summary`.

## Phase 4 - Login And Forced Password Change

Purpose:

- Provide platform account login/logout/password-change behavior independent of PDP.

Scope:

- Add account login/logout/password-change views or reuse Django auth views under `accounts`.
- Add account templates.
- Add first-login password-change middleware for `accounts.AccountProfile.must_change_password`.
- Update settings to use account login paths when ready.
- Add tests for redirect behavior and password-change completion.

Recommended URLs:

- `/accounts/login/`
- `/accounts/logout/`
- `/accounts/password/`

Recommended redirect behavior:

- Anonymous users are redirected to `/accounts/login/`.
- Authenticated users with `must_change_password=True` are redirected to `/accounts/password/`.
- Allowed paths while password change is required:
  - `/accounts/password/`
  - `/accounts/logout/`
  - `/accounts/login/`
  - possibly `/admin/` for superusers only
- After successful password change:
  - set `must_change_password=False`
  - call `update_session_auth_hash`
  - redirect based on role:
    - staff/admin -> `/analytics/`
    - coach/player/parent/guest evaluator -> first permitted landing page

Important:

- This should replace dependence on PDP login for new Account Management behavior.
- Do not remove PDP middleware until PDP decommissioning is explicitly planned.

## Phase 5 - Evaluator Role Snapshot

Purpose:

- Ensure submitted evaluations snapshot the evaluator's current account role.

Current behavior:

- Any authenticated user can evaluate any player.
- Coach assessment creation defaults evaluator role to Analytics `Coach`.
- Observation already stores role snapshots.

Required v1 behavior:

- Any authenticated user can submit evaluations.
- On creation/submission, determine role from `accounts.AccountProfile.role`.
- Map account roles to Analytics `EvaluatorRole` keys.
- Store:
  - `evaluator`
  - `evaluator_role`
  - `evaluator_role_key`
  - `evaluator_role_name`
- Historical observations must not change if a user's account role changes later.

Recommended role mapping:

| Account Role | Analytics EvaluatorRole |
| --- | --- |
| `admin` | `admin` |
| `staff` | `staff` |
| `coach` | `coach` |
| `player` | `player` |
| `parent` | `parent` |
| `guest_evaluator` | `guest_evaluator` |

Required Analytics setup change:

- Add missing Analytics evaluator roles:
  - `player`
  - `parent`
  - `guest_evaluator`

Keep existing evaluator roles:

- `coach`
- `assistant_coach`
- `head_coach`
- `coordinator`
- `staff`
- `admin`

Service boundary:

- `accounts.services.role_service.evaluator_role_for_user(user)` should return the Analytics role key/name or enough data for `analytics.services.observation_service` to snapshot.
- `analytics` should not own account-role lookup logic.
- `analytics` may call an account service at observation creation time.

## Phase 6 - Staff Account Management UI

Purpose:

- Give staff/admin users a small account-management surface for production operations.

Scope:

- Staff/admin list of accounts.
- Search/filter by name, username, email, role, active state, import-created state.
- Account detail page.
- Linked player display.
- Role update form.
- Activate/deactivate imported account.
- Reset temporary password or mark `must_change_password=True`.

Out of scope:

- Full audit dashboard.
- Bulk email invitations.
- Self-service registration.
- Parent portal management.
- Advanced permission matrix.

Recommended URLs:

- `/accounts/manage/`
- `/accounts/manage/<int:user_id>/`
- `/accounts/manage/<int:user_id>/role/`
- `/accounts/manage/<int:user_id>/activate/`
- `/accounts/manage/<int:user_id>/deactivate/`
- `/accounts/manage/<int:user_id>/reset-password/`

Permissions:

- Staff/admin only.
- Use `is_staff` or `is_superuser`.
- Role changes should not silently grant Django staff/admin access.

## Import Provisioning Workflow

Recommended staff workflow:

1. Staff uploads player CSV through existing Analytics import UI.
2. Staff maps player fields, including birthdate if available.
3. Staff selects whether to provision player accounts.
4. Import preview shows player identity actions and account-provisioning readiness:
   - ready to provision
   - missing birthdate
   - duplicate email/username
   - already linked
   - needs staff review
5. Staff resolves player identity conflicts first.
6. Staff confirms import.
7. Player import creates/updates `players.Player`.
8. Account provisioning service creates/updates users and links.
9. Import result shows counts:
   - users created
   - users linked
   - accounts skipped
   - account rows needing review
10. Staff manages unresolved accounts in Account Management UI.

Do not create user accounts before player identity conflicts are resolved.

## Password And Login Workflow

Temporary password:

- If birthdate exists, use `YYYYMMDD`.
- Set with Django `set_password`.
- Never store plaintext.
- Set `AccountProfile.must_change_password=True`.

Missing birthdate:

- Recommended default: do not provision active account automatically.
- Staff can later set/reset password through Account Management UI.

First login:

- User logs in.
- Middleware sees `AccountProfile.must_change_password=True`.
- User is redirected to password-change page.
- After successful password change, `must_change_password=False`.

## Evaluation Permission Behavior

Rules:

- Any authenticated user can submit evaluations.
- Anonymous users cannot submit evaluations.
- Staff/admin users can access staff/admin views.
- Player/parent/coach/guest evaluator roles do not grant staff/admin access.
- The same evaluator cannot submit duplicate `coach_assessment` observations for the same player/cycle.
- Multiple evaluators can evaluate the same player.
- The same evaluator can evaluate many players.

This preserves current Analytics v1 behavior.

## Evaluator Role Snapshot Behavior

When creating or submitting an observation:

1. Resolve evaluator role from `accounts.AccountProfile`.
2. Resolve matching `analytics.EvaluatorRole`.
3. Set `Observation.evaluator_role`.
4. Copy key/name to:
   - `Observation.evaluator_role_key`
   - `Observation.evaluator_role_name`
5. Do not recompute these fields later unless explicitly resnapshotting is requested.

Reports should use the snapshot fields, not live account role.

## Services To Create

```text
accounts/
    services/
        profile_service.py
        role_service.py
        link_service.py
        provisioning_service.py
        password_service.py
        permissions.py
```

Suggested responsibilities:

- `profile_service.py`
  - create/get account profile
  - set role
  - active/inactive state helpers
- `role_service.py`
  - role constants
  - role labels
  - map account role to Analytics evaluator role
- `link_service.py`
  - create/deactivate user-player links
  - find linked players/users
- `provisioning_service.py`
  - create user accounts for players
  - username generation
  - import-account provisioning orchestration
- `password_service.py`
  - birthdate temporary-password generation
  - mark must-change-password
  - reset temporary password
- `permissions.py`
  - staff/admin account-management access
  - account self-access helpers

## Views And Templates To Create Or Reuse

Use Django auth views where practical:

- `LoginView`
- `LogoutView`
- `PasswordChangeView`

Create account templates:

- `accounts/login.html`
- `accounts/password_change.html`
- `accounts/account_list.html`
- `accounts/account_detail.html`
- `accounts/account_role_form.html`

Import UI changes:

- Add account-provisioning option to existing Analytics import upload/preview flow.
- Keep import UI thin.
- Keep account provisioning behavior in `accounts` services.

## URL Paths

Recommended:

```text
/accounts/login/
/accounts/logout/
/accounts/password/
/accounts/manage/
/accounts/manage/<int:user_id>/
/accounts/manage/<int:user_id>/role/
/accounts/manage/<int:user_id>/activate/
/accounts/manage/<int:user_id>/deactivate/
/accounts/manage/<int:user_id>/reset-password/
```

Project URL change:

- Add `path("accounts/", include("accounts.urls"))`.
- Eventually update `LOGIN_URL` to `/accounts/login/`.
- Eventually update `LOGIN_REDIRECT_URL` to a platform-aware redirect endpoint.

## Admin Integration

Register:

- `AccountProfile`
- `UserPlayerLink`

Admin should show:

- user
- role
- must-change-password
- created-from-import
- active state
- linked player
- relationship
- import batch
- timestamps

Sensitive fields:

- Do not display plaintext passwords.
- Do not store plaintext passwords.

## Data Migration Considerations

Account Management v1 will require migrations when implemented:

- Create `accounts.AccountProfile`.
- Create `accounts.UserPlayerLink`.
- Optionally backfill profiles for existing users.
- Optionally infer role from `is_staff` / `is_superuser`.
- Do not migrate legacy PDP account/profile data unless explicitly planned.

Recommended initial data migration:

- For every existing `User`, create `AccountProfile`.
- If `is_superuser`, role `admin`.
- Else if `is_staff`, role `staff`.
- Else role `guest_evaluator`.

Do not create player links automatically without an explicit matching/migration plan.

## Security Considerations

- Birthdate passwords are weak and must be temporary only.
- Force password change on first login.
- Consider imported accounts inactive by default.
- Do not expose temporary passwords after creation.
- Do not log plaintext passwords.
- Do not store plaintext passwords in JSON metadata, import summaries, source rows, sessions, or logs.
- Prefer password setup/reset links long term.
- Handle duplicate emails and usernames conservatively.
- Do not silently link an existing user to a different player based only on email.
- Protect parent/player privacy when displaying linked accounts.
- Staff account-management UI must not expose sensitive import JSON by default.
- Account provisioning should be transaction-safe with player import commits.

## Tests To Write

### Model Tests

- Account profile creates for users.
- Role choices validate.
- User-player link uniqueness rules work.
- User-player link supports multiple users per player.
- User-player link supports one user linked to multiple players where relationship allows it.

### Service Tests

- `role_for_user` maps superuser/staff/imported/default roles correctly.
- `temporary_password_for_player` returns `YYYYMMDD` when birthdate exists.
- Missing birthdate prevents automatic active account provisioning.
- Username generation avoids collisions.
- Duplicate email is flagged for review.
- Provisioning creates User, AccountProfile, and UserPlayerLink.
- Provisioning sets role `player`.
- Provisioning sets `must_change_password=True`.
- Provisioning does not log/store plaintext passwords.

### Import Tests

- Player import can run without account provisioning.
- Player import with provisioning creates accounts for eligible players.
- Missing birthdate rows are skipped or marked review for account provisioning.
- Existing linked player account is not duplicated.
- Existing unrelated user email creates a conflict/review condition.
- Import summary includes safe account-provisioning counts.

### Login / Password Tests

- User with `must_change_password=True` is redirected to password change.
- Password-change page is accessible.
- Logout/login paths are accessible.
- Password change clears `must_change_password`.
- Session remains authenticated after password change.
- User without `must_change_password` is not redirected.

### Permission Tests

- Any authenticated user can open/submit an assessment.
- Anonymous user cannot submit assessment.
- Player role cannot access staff-only Analytics views.
- Parent role cannot access staff-only Analytics views.
- Staff/admin can access staff-only Analytics views.
- Staff/admin can access account-management UI.
- Non-staff cannot access account-management UI.

### Evaluator Snapshot Tests

- Player role evaluator snapshots as `player`.
- Coach role evaluator snapshots as `coach`.
- Parent role evaluator snapshots as `parent`.
- Role changes after submission do not change historical observation snapshot.
- Reports group by snapshot role, not live role.

## Implementation Sequence

1. Create `accounts` app and add it to `INSTALLED_APPS`.
2. Add `AccountProfile`, role choices, and admin.
3. Add profile/role services and tests.
4. Add `UserPlayerLink`, relationship choices, link services, and tests.
5. Add account login/logout/password-change views/templates.
6. Add account password-change middleware.
7. Update project login settings once account login is ready.
8. Add account provisioning services.
9. Extend player import workflow with optional account provisioning.
10. Add safe import summaries for account provisioning.
11. Add evaluator-role mapping service.
12. Update Analytics coach assessment creation to snapshot account role.
13. Add staff account-management UI.
14. Run full test suite.
15. Update documentation and status docs.

Do not implement multiple phases in one Codex task unless explicitly instructed.

## Risks / Open Questions

- Should imported player accounts be active immediately or require staff activation? Recommendation: inactive by default.
- Should email be required for login accounts? Recommendation: no for v1, but prefer email username when available and unique.
- Should staff see a one-time temporary password report? Recommendation: avoid if possible; use staff reset/setup workflow instead.
- What should the default landing page be for player/parent accounts before portals exist?
- Should `guest_evaluator` users be allowed to log in only for evaluations, or can they access player search/profile pages? Recommendation: evaluations only unless staff.
- How should parent/guardian account imports be handled when source rows contain guardian contact data? Recommendation: defer to a later parent-account phase.
- Should account roles be `TextChoices` or database-managed roles? Recommendation: `TextChoices` for v1.
- Should `AccountProfile` be auto-created by signal? Recommendation: explicit service plus optional management command/backfill.
- How should legacy PDP middleware coexist during transition? Recommendation: add account middleware without removing PDP behavior until PDP is formally phased out.

## Definition Of Done

Account Management v1 is complete when:

- `accounts` app exists.
- Every Django user can have an `AccountProfile`.
- Account roles are defined and tested.
- Users can be linked to canonical `players.Player` records.
- Player import can optionally provision linked player login accounts.
- Imported player accounts default to role `player`.
- Birthdate-based temporary passwords use `YYYYMMDD`.
- Users with temporary passwords are forced to change password on first login.
- Staff/admin views remain staff/admin-only.
- Any authenticated user can still evaluate any player.
- Evaluator role snapshots come from account role and remain historical.
- Staff/admin users can manage account role, activation state, and password reset state.
- No plaintext passwords are stored or logged.
- Required tests pass:
  - `python manage.py check`
  - `python manage.py makemigrations accounts --check`
  - `python manage.py test accounts`
  - `python manage.py test players`
  - `python manage.py test analytics`
  - `python manage.py test`
