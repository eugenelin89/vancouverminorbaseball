You are continuing Account Management v1.

Do NOT implement application code.

Your task is to create the engineering plan for:

Account Management v1 Phase 4 — Authentication & Forced Password Change

==================================================
Context
==================================================

Account Management v1 Phase 1 is complete:
- `accounts.AccountProfile`
- `AccountRole`
- profile/role/permission services

Account Management v1 Phase 2 is complete:
- `accounts.UserPlayerLink`
- `UserPlayerRelationship`
- `accounts/services/link_service.py`

Account Management v1 Phase 3 is complete:
- optional player import account provisioning
- username_service
- email_service
- password_service
- provisioning_service
- imported users default inactive unless explicitly activated
- temporary birthdate passwords are hashed and not serialized
- `AccountProfile.must_change_password=True` for provisioned accounts

Current known auth state:
- Django default `User` is used.
- No custom `AUTH_USER_MODEL`.
- Existing `LOGIN_URL` currently points to `/pdp/login/`.
- PDP has legacy login/logout/password-change views.
- PDP has legacy first-login password-change middleware tied to `pdp.PlayerProfile`.
- Account Management should not depend on PDP long term.

==================================================
Before Writing
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md

Inspect:

- accounts/
- pdp/
- project settings
- project urls
- existing login/logout/password-change views/templates
- existing middleware
- analytics permissions/views
- players import flow

==================================================
Task
==================================================

Create:

docs/account_management/implementation/engineering/phase_04_authentication_forced_password_change.md

Do NOT implement code.

Do NOT create migrations.

Do NOT modify application behavior.

==================================================
Phase 4 Goal
==================================================

Define the platform account authentication flow and forced password-change behavior for accounts created by Account Management.

This phase should prepare imported player accounts for safe login by enforcing password change before normal app access.

==================================================
Required Plan Sections
==================================================

Include:

1. Phase goal
2. Strict scope
3. Out of scope
4. Current state
5. URL design
6. View design
7. Template design
8. Middleware design
9. Redirect behavior
10. Password-change behavior
11. Interaction with inactive imported accounts
12. Interaction with PDP legacy auth
13. Permission/security considerations
14. Services to create/update
15. Settings changes
16. Tests to write
17. Implementation sequence
18. Risks/open questions
19. Definition of Done

==================================================
Required Behavior
==================================================

Create platform account auth routes:

- `/accounts/login/`
- `/accounts/logout/`
- `/accounts/password/`

Use Django auth views where practical.

Login behavior:
- Anonymous users can access login page.
- Successful login redirects based on role or next parameter.
- Users with `must_change_password=True` must be redirected to `/accounts/password/`.

Forced password-change behavior:
- If authenticated user has `AccountProfile.must_change_password=True`, they cannot access normal app pages.
- They must be redirected to `/accounts/password/`.
- Allowed paths while forced password change is required:
  - `/accounts/password/`
  - `/accounts/logout/`
  - `/accounts/login/`
  - static/media paths if needed
  - Django admin paths only for superusers if appropriate
- After successful password change:
  - set `must_change_password=False`
  - call `update_session_auth_hash`
  - redirect to appropriate landing page

Landing behavior:
- Staff/admin users should land at `/analytics/`.
- Player/parent/coach/guest users currently have no portal.
- For non-staff users, define a minimal safe landing page such as `/accounts/profile/` or a simple account home page.
- Do not build a player/parent portal in Phase 4.

Inactive users:
- `User.is_active=False` users cannot log in through Django authentication.
- Phase 4 should not auto-activate imported accounts.
- Activation remains future staff account management scope.

==================================================
PDP Legacy Auth
==================================================

Plan how Phase 4 coexists with PDP.

Important:
- Do not break PDP unexpectedly.
- Do not remove PDP middleware unless explicitly planned.
- Account Management auth should become the platform-forward path.
- Update `LOGIN_URL` only if safe.
- Document coexistence with `pdp.middleware.FirstLoginPasswordChangeMiddleware`.

The plan should decide whether:
- to add new account middleware before/after PDP middleware
- to keep PDP routes available
- to update global settings now or defer

==================================================
Services / Middleware
==================================================

Plan services such as:

accounts/services/auth_redirect_service.py

Possible responsibilities:
- landing_url_for_user(user)
- should_force_password_change(user)
- is_password_change_allowed_path(path, user)

Plan middleware:

accounts.middleware.AccountPasswordChangeRequiredMiddleware

Responsibilities:
- check authenticated users
- use `AccountProfile.must_change_password`
- avoid infinite redirects
- allow logout/password/admin/static paths
- redirect to `/accounts/password/` when required

Do not use signals.

==================================================
Templates
==================================================

Plan templates:

- `accounts/login.html`
- `accounts/password_change.html`
- `accounts/account_home.html` or `accounts/profile.html`

Keep templates simple.

No portal features.

==================================================
Security Requirements
==================================================

Address:

- temporary birthdate passwords are weak
- forced password change required
- inactive accounts cannot login
- no plaintext password display
- CSRF protection
- session authentication hash update
- avoiding redirect loops
- respecting next parameter safely
- staff/admin access remains controlled by `is_staff` / `is_superuser`

==================================================
Tests To Plan
==================================================

Include tests for:

Authentication views:
- login page renders
- logout works
- password page renders for authenticated users
- successful password change clears `must_change_password`
- `update_session_auth_hash` behavior keeps user logged in
- inactive user cannot login

Middleware:
- user with `must_change_password=True` is redirected from normal pages
- allowed paths do not redirect
- no redirect loop
- user without `must_change_password` not redirected
- missing AccountProfile behavior is safe

Redirects:
- staff/admin lands at `/analytics/`
- non-staff lands at account home/profile
- next parameter respected safely where appropriate

Regression:
- Analytics staff views still require staff
- any authenticated user can still submit evaluations
- Phase 3 provisioning remains unchanged
- PDP legacy auth is not broken unintentionally

==================================================
Out Of Scope
==================================================

Explicitly exclude:

- staff account management UI
- account activation UI
- email invitations
- password reset email flow
- parent/player portal
- coach portal
- evaluator role snapshot integration
- import provisioning changes
- PDP migration/removal
- social login/SSO
- custom user model

==================================================
Final Report
==================================================

Report:

- files created
- files modified
- key architectural decisions
- PDP coexistence decision
- open questions
- confirmation that no application code was implemented