# Account Management v1 Phase 4 Engineering Plan: Authentication and Forced Password Change

## Phase Goal

Define the platform-forward authentication flow for Account Management v1 and enforce password changes for users with `accounts.AccountProfile.must_change_password=True`.

Phase 4 prepares imported player accounts for safer login by ensuring temporary birthdate passwords cannot be used for normal app access without first being changed.

## Strict Scope

- Add platform account auth routes under `/accounts/`.
- Add login, logout, password-change, and simple account-home/profile views.
- Add simple account auth templates.
- Add middleware that redirects authenticated users with `AccountProfile.must_change_password=True` to `/accounts/password/`.
- Add redirect/landing helpers in an account auth service.
- Update project URL routing to include `accounts.urls`.
- Decide whether to update `LOGIN_URL` and `LOGIN_REDIRECT_URL`.
- Add tests for auth views, middleware, redirects, inactive users, PDP coexistence, and regressions.

## Out Of Scope

- Staff account management UI.
- Account activation UI.
- Email invitations.
- Password reset email flow.
- Parent/player portal.
- Coach portal.
- Evaluator role snapshot integration.
- Import provisioning changes.
- PDP migration/removal.
- Social login/SSO.
- Custom user model.
- Advanced role-based access control.

## Current State

Completed Account Management phases:

- Phase 1: `AccountProfile`, `AccountRole`, profile/role/permission services.
- Phase 2: `UserPlayerLink`, `UserPlayerRelationship`, `link_service`.
- Phase 3: optional player import account provisioning, username/email/password/provisioning services, imported users activated immediately, hashed temporary birthdate passwords, `AccountProfile.must_change_password=True`.

Current project auth state:

- The project uses Django default `User`.
- There is no custom `AUTH_USER_MODEL`.
- `accounts` has models/services/admin/tests but no URLs, views, middleware, or templates.
- `LOGIN_URL = "/pdp/login/"`.
- `LOGIN_REDIRECT_URL = "/pdp/"`.
- Project URLs include `pdp/` but not `accounts/`.
- PDP has `PDPLoginView`, `PDPLogoutView`, and `PDPPasswordChangeView`.
- PDP password change clears `pdp.PlayerProfile.must_change_password`, not `accounts.AccountProfile.must_change_password`.
- PDP middleware `pdp.middleware.FirstLoginPasswordChangeMiddleware` redirects users with legacy `pdp.PlayerProfile.must_change_password=True`.
- `pdp.middleware.FirstLoginPasswordChangeMiddleware` is currently installed after Django `AuthenticationMiddleware`.
- Analytics staff/admin views use `is_staff` / `is_superuser`.
- Analytics coach assessment submission still allows any authenticated user.

## URL Design

Create:

```text
accounts/urls.py
```

Routes:

```text
/accounts/login/       -> accounts:login
/accounts/logout/      -> accounts:logout
/accounts/password/    -> accounts:password-change
/accounts/profile/     -> accounts:profile
```

Recommended URL names:

- `accounts:login`
- `accounts:logout`
- `accounts:password-change`
- `accounts:profile`

Project URL change:

```python
path("accounts/", include("accounts.urls"))
```

Do not remove PDP URLs.

## View Design

Use Django auth views where practical:

- `LoginView`
- `LogoutView`
- `PasswordChangeView`

Create:

```text
accounts/views.py
```

Recommended views:

- `AccountLoginView(LoginView)`
- `AccountLogoutView(LogoutView)`
- `AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView)`
- `AccountProfileView(LoginRequiredMixin, TemplateView)`

`AccountLoginView`:

- Renders `accounts/login.html`.
- Allows anonymous users.
- Uses Django authentication.
- Uses safe `next` handling from Django `LoginView`.
- On successful login, users with `must_change_password=True` should land on `/accounts/password/`.
- Users without forced password change should land on `next` when safe, otherwise role-based landing URL.

`AccountLogoutView`:

- Uses Django `LogoutView`.
- Redirects to `accounts:login`.

`AccountPasswordChangeView`:

- Requires login.
- Renders `accounts/password_change.html`.
- On valid form:
  - saves the new password through Django `PasswordChangeView`.
  - sets `AccountProfile.must_change_password=False`.
  - calls `update_session_auth_hash`.
  - redirects to role-based landing URL.

`AccountProfileView`:

- Minimal safe landing page for non-staff users.
- Shows basic account information only:
  - username
  - name/email if available
  - account role
  - linked players summary if simple and already available through `link_service`
- No player/parent portal features.

## Template Design

Create:

```text
accounts/templates/accounts/login.html
accounts/templates/accounts/password_change.html
accounts/templates/accounts/profile.html
```

Templates should be simple and can reuse existing project styling conventions from PDP/Analytics templates.

`login.html`:

- Form rendering.
- CSRF token.
- No account provisioning details.

`password_change.html`:

- Password change form.
- CSRF token.
- No plaintext temporary password display.

`profile.html`:

- Minimal account home/profile page.
- No player portal, parent portal, coach dashboard, or staff management features.

## Middleware Design

Create:

```text
accounts/middleware.py
```

Middleware:

```python
AccountPasswordChangeRequiredMiddleware
```

Responsibilities:

- Inspect authenticated users.
- Use `accounts.AccountProfile.must_change_password`.
- If missing `AccountProfile`, treat as no forced password change.
- Redirect to `/accounts/password/` when password change is required and path is not allowed.
- Avoid infinite redirect loops.
- Allow logout/login/password paths.
- Allow static/media paths.
- Allow Django admin paths for superusers if appropriate.

Allowed paths while forced password change is required:

- `/accounts/password/`
- `/accounts/logout/`
- `/accounts/login/`
- static paths from `settings.STATIC_URL`
- media paths from `settings.MEDIA_URL`, if needed
- `/admin/` only for superusers

Middleware order:

- Must run after `django.contrib.auth.middleware.AuthenticationMiddleware`.
- Recommended placement: immediately after existing PDP password-change middleware during coexistence.
- This allows legacy PDP password enforcement to continue for `pdp.PlayerProfile` users while account-management enforcement applies to `AccountProfile` users.

## Redirect Behavior

Create:

```text
accounts/services/auth_redirect_service.py
```

Recommended functions:

```python
landing_url_for_user(user) -> str
should_force_password_change(user) -> bool
is_password_change_allowed_path(path, user) -> bool
```

Landing rules:

- Staff/admin users: `/analytics/`
- Non-staff users: `/accounts/profile/`
- Anonymous users: `/accounts/login/`

Staff/admin means Django `is_staff` or `is_superuser`, not `AccountProfile.role` alone.

`next` parameter:

- Respect safe `next` values when Django auth view deems them safe.
- Forced password change takes precedence over `next`.
- After password change, redirect to role-based landing page rather than the originally requested protected page unless implementation has a safe stored-next design.

## Password-Change Behavior

When `AccountProfile.must_change_password=True`:

- User cannot access normal app pages.
- User is redirected to `/accounts/password/`.
- User can access logout.
- User can access login but authenticated users should normally be redirected by Django or middleware flow.

After successful password change:

- Set `AccountProfile.must_change_password=False`.
- Save `updated_at`.
- Call `update_session_auth_hash(request, user)`.
- Redirect to `landing_url_for_user(user)`.

Do not display, log, or store plaintext temporary passwords.

## Interaction With Imported Account Activation

Phase 3 creates imported users with `User.is_active=True` when account provisioning is enabled.

Phase 4 rules:

- `User.is_active=False` users cannot log in through Django authentication.
- Imported users with temporary passwords must change password before normal platform access.
- Phase 4 must not bypass forced password change.
- Tests should prove inactive users cannot authenticate.

## Interaction With PDP Legacy Auth

PDP is legacy/transitionary but still installed.

Coexistence decision:

- Keep PDP routes available.
- Keep PDP middleware installed.
- Do not remove or migrate PDP auth behavior in Phase 4.
- Add account auth as the platform-forward path under `/accounts/`.
- Add account password-change middleware alongside PDP middleware.

Settings decision:

- Recommended: update `LOGIN_URL` to `/accounts/login/` in Phase 4 once account login views are implemented and tested.
- Recommended: update `LOGIN_REDIRECT_URL` to `/accounts/profile/` or a platform-aware redirect endpoint only if the new login view handles staff redirect to `/analytics/`.
- Safer implementation option: use `AccountLoginView.get_success_url()` for landing behavior and set global `LOGIN_REDIRECT_URL = "/accounts/profile/"`.

PDP impact:

- PDP login/logout/password URLs remain available.
- PDP middleware still handles `pdp.PlayerProfile.must_change_password`.
- Account middleware handles `accounts.AccountProfile.must_change_password`.
- If a user has both PDP and AccountProfile forced password flags, middleware order determines first redirect. Recommended order keeps PDP middleware first to avoid changing PDP behavior unexpectedly.

## Permission / Security Considerations

- Temporary birthdate passwords are weak and must be changed before normal access.
- CSRF protection is required on login/password forms.
- Password change must use Django password validators.
- `update_session_auth_hash` must be called after password change.
- Redirect loops must be prevented.
- Safe `next` handling should use Django auth view behavior and not manually trust arbitrary URLs.
- Staff/admin surfaces remain controlled by `is_staff` / `is_superuser`.
- Account roles do not grant Django admin/staff access.
- Missing `AccountProfile` should not crash middleware.
- Do not use signals.
- Do not add portal access based on `UserPlayerLink`.

## Services To Create / Update

Create:

```text
accounts/services/auth_redirect_service.py
```

Functions:

- `landing_url_for_user(user)`
- `should_force_password_change(user)`
- `is_password_change_allowed_path(path, user)`

Possibly update:

- `accounts/services/password_service.py`
  - add or reuse helper to clear `must_change_password`
  - keep password state logic centralized

Do not update provisioning behavior in Phase 4 except through existing password state expectations.

## Settings Changes

Project URLs:

- Add `path("accounts/", include("accounts.urls"))`.

Middleware:

- Add `accounts.middleware.AccountPasswordChangeRequiredMiddleware` after `pdp.middleware.FirstLoginPasswordChangeMiddleware`.

Authentication settings:

- Recommended after implementation tests pass:
  - `LOGIN_URL = "/accounts/login/"`
  - `LOGIN_REDIRECT_URL = "/accounts/profile/"`

Do not change `AUTH_USER_MODEL`.

## Tests To Write

### Authentication Views

- Login page renders.
- Logout works and redirects to account login.
- Password-change page renders for authenticated users.
- Successful password change clears `AccountProfile.must_change_password`.
- Successful password change calls/achieves session auth hash update so user remains logged in.
- Inactive user cannot log in.

### Middleware

- User with `must_change_password=True` is redirected from normal pages.
- `/accounts/password/` is allowed.
- `/accounts/logout/` is allowed.
- `/accounts/login/` is allowed.
- Static/media paths are allowed.
- Superuser admin path is allowed if implemented.
- No redirect loop occurs.
- User without `must_change_password` is not redirected.
- Missing `AccountProfile` is safe and does not redirect.

### Redirects

- Staff/admin login lands at `/analytics/`.
- Non-staff login lands at `/accounts/profile/`.
- Safe `next` parameter is respected when no forced password change is required.
- Forced password change overrides `next`.
- After password change, user lands at the role-based landing page.

### Regression

- Analytics staff views still require staff.
- Any authenticated user can still submit evaluations.
- Phase 3 provisioning remains unchanged.
- PDP login route still renders.
- PDP password-change middleware behavior is not intentionally removed.
- PDP routes remain registered.

## Implementation Sequence

1. Create `accounts/services/auth_redirect_service.py`.
2. Add service tests for landing URLs, force-password state, and allowed paths.
3. Create `accounts/views.py`.
4. Create `accounts/urls.py`.
5. Create account auth/profile templates.
6. Create `accounts/middleware.py`.
7. Add project URL include for `accounts/`.
8. Add account middleware after PDP middleware.
9. Update `LOGIN_URL` and `LOGIN_REDIRECT_URL` if tests confirm safe coexistence.
10. Add view and middleware tests.
11. Add PDP coexistence regression tests.
12. Run:
    - `python manage.py check`
    - `python manage.py makemigrations accounts --check`
    - `python manage.py test accounts`
    - `python manage.py test analytics`
    - `python manage.py test players`
    - `python manage.py test pdp`
    - `python manage.py test`
    - `git diff --check`

## Risks / Open Questions

- Updating global `LOGIN_URL` from PDP to accounts may change unauthenticated redirects across the project. Recommendation: do it in Phase 4 only after account login tests cover Analytics and PDP coexistence.
- PDP and account forced-password middleware can both apply to users with both profile types. Recommendation: keep PDP middleware first for now.
- Non-staff users do not yet have a portal. Recommendation: add minimal `/accounts/profile/` only.
- Imported accounts are activated immediately from Phase 3. Staff account-management UI remains unavailable until a future phase.
- If the project needs PDP users to continue landing in PDP after PDP login, PDP-specific login view can keep its own success URL even if global `LOGIN_URL` changes.

## Definition of Done

- [ ] `/accounts/login/` exists.
- [ ] `/accounts/logout/` exists.
- [ ] `/accounts/password/` exists.
- [ ] `/accounts/profile/` or equivalent safe account landing page exists.
- [ ] Account login uses Django auth.
- [ ] Account password change clears `AccountProfile.must_change_password`.
- [ ] Account password change calls `update_session_auth_hash`.
- [ ] Middleware redirects forced-password users away from normal app pages.
- [ ] Middleware avoids redirect loops and allows password/logout/login/static paths.
- [ ] Inactive users cannot log in.
- [ ] Staff/admin landing goes to `/analytics/`.
- [ ] Non-staff landing goes to account profile/home.
- [ ] PDP routes remain available.
- [ ] PDP middleware is not removed.
- [ ] No Phase 5 evaluator snapshot work is implemented.
- [ ] No Phase 6 staff account-management UI is implemented.
- [ ] Tests cover auth views, middleware, redirects, security, PDP coexistence, and regressions.
