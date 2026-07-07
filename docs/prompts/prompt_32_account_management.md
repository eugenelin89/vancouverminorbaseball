You are implementing Account Management v1.

Implement Phase 4 only:

Account Management v1 Phase 4 — Authentication & Forced Password Change

Do NOT implement Phase 5 or Phase 6.

The Phase 4 engineering plan has been reviewed and approved.

Implement exactly what is described in:

- docs/account_management/implementation/engineering/phase_04_authentication_forced_password_change.md

Do not redesign the architecture.

==================================================
Before Coding
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/phase_04_authentication_forced_password_change.md

Review existing implementation:

- accounts/
- pdp/
- analytics/
- players/
- project urls
- project settings
- existing middleware
- existing login/logout/password-change views/templates

==================================================
Scope
==================================================

Implement platform-forward account authentication under `/accounts/`.

Expected implementation includes:

- accounts/services/auth_redirect_service.py
- accounts/views.py
- accounts/urls.py
- accounts/middleware.py
- accounts login template
- accounts password-change template
- accounts profile/home template
- project URL include for accounts
- account forced-password middleware
- auth settings updates, if tests confirm safe coexistence
- tests for views, middleware, redirects, inactive users, PDP coexistence, and regressions

==================================================
Architecture Rules
==================================================

accounts owns:

- account login routes
- account logout routes
- account password-change route
- account profile/home route
- account forced-password middleware
- account redirect/landing helpers

pdp:

- remains available
- keeps existing PDP auth routes
- keeps existing PDP middleware
- should not be migrated or removed in Phase 4

analytics:

- unchanged except for regression coverage
- staff/admin views still controlled by is_staff / is_superuser

players:

- unchanged

drafts:

- unchanged

==================================================
Required Routes
==================================================

Create:

/accounts/login/       -> accounts:login
/accounts/logout/      -> accounts:logout
/accounts/password/    -> accounts:password-change
/accounts/profile/     -> accounts:profile

Add:

path("accounts/", include("accounts.urls"))

to the project URL config.

Do not remove PDP URLs.

==================================================
Views
==================================================

Use Django auth views where practical.

Implement:

AccountLoginView

- subclass LoginView
- renders accounts/login.html
- anonymous users can access it
- successful login redirects based on role/next
- users with AccountProfile.must_change_password=True go to /accounts/password/

AccountLogoutView

- subclass LogoutView
- redirects to accounts login

AccountPasswordChangeView

- subclass LoginRequiredMixin + PasswordChangeView
- renders accounts/password_change.html
- on successful password change:
  - set AccountProfile.must_change_password=False
  - save updated_at
  - call update_session_auth_hash
  - redirect to landing_url_for_user(user)

AccountProfileView

- subclass LoginRequiredMixin + TemplateView
- renders accounts/profile.html
- minimal safe landing page
- show basic account info only:
  - username
  - first name / last name / email if available
  - role
  - simple linked-player summary if easy via link_service
- do NOT build player/parent/coach portal features

==================================================
Services
==================================================

Create:

accounts/services/auth_redirect_service.py

Implement:

landing_url_for_user(user)

Rules:
- anonymous -> /accounts/login/
- staff/superuser -> /analytics/
- non-staff -> /accounts/profile/

should_force_password_change(user)

Rules:
- True only for authenticated users with AccountProfile.must_change_password=True
- Missing AccountProfile should be safe and return False
- Inactive users should not matter because they cannot authenticate

is_password_change_allowed_path(path, user)

Allowed while forced password change is required:
- /accounts/password/
- /accounts/logout/
- /accounts/login/
- static paths
- media paths if configured
- /admin/ only for superusers

==================================================
Middleware
==================================================

Create:

accounts.middleware.AccountPasswordChangeRequiredMiddleware

Responsibilities:

- run after AuthenticationMiddleware
- inspect authenticated users
- if should_force_password_change(user) is True:
  - allow only allowed paths
  - otherwise redirect to /accounts/password/
- avoid infinite redirects
- missing AccountProfile must not crash
- do not redirect anonymous users

Middleware order:

- keep existing PDP middleware installed
- add account middleware after PDP first-login/password-change middleware

Do not remove PDP middleware.

==================================================
Settings
==================================================

After account auth routes and tests are in place, update global settings if safe:

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/profile/"

Do not change AUTH_USER_MODEL.

Do not remove PDP settings/routes.

==================================================
Templates
==================================================

Create:

accounts/templates/accounts/login.html
accounts/templates/accounts/password_change.html
accounts/templates/accounts/profile.html

Keep templates simple.

Use CSRF protection.

Do not display temporary passwords.

Do not add portal features.

==================================================
Password Change Behavior
==================================================

When AccountProfile.must_change_password=True:

- user cannot access normal app pages
- user is redirected to /accounts/password/
- user can access password page
- user can logout
- user can access login path without redirect loop

After password change:

- AccountProfile.must_change_password=False
- session remains authenticated through update_session_auth_hash
- user redirects to role-based landing page

==================================================
Inactive Users
==================================================

User.is_active=False users cannot log in.

Do NOT auto-activate imported users.

Activation remains Phase 6 scope.

==================================================
PDP Coexistence
==================================================

Do NOT break PDP.

Required:

- PDP routes remain available
- PDP middleware remains installed
- PDP login route still renders
- PDP password-change behavior is not intentionally removed
- account middleware coexists with PDP middleware

If a user has both PDP and AccountProfile forced-password flags, keep the middleware order recommended in the plan:
- PDP middleware first
- account middleware second

==================================================
Do NOT Implement
==================================================

Do NOT implement:

Phase 5

evaluator role snapshot integration

Phase 6

staff account management UI

account activation UI

email invitations

password reset emails

parent/player portal

coach portal

PDP migration/removal

social login

SSO

custom user model

advanced role-based access control

import provisioning changes

==================================================
Testing
==================================================

Add tests for:

auth redirect service:

- anonymous landing URL
- staff landing URL
- non-staff landing URL
- should_force_password_change true/false
- missing AccountProfile safe
- allowed path behavior

auth views:

- login page renders
- logout works
- password page renders for authenticated users
- password change clears must_change_password
- password change keeps user logged in
- inactive user cannot login
- staff login lands at /analytics/
- non-staff login lands at /accounts/profile/
- safe next parameter respected when no forced password change
- forced password change overrides next

middleware:

- forced-password user redirected from normal app pages
- /accounts/password/ allowed
- /accounts/logout/ allowed
- /accounts/login/ allowed
- static/media paths allowed
- superuser admin path allowed if implemented
- no redirect loop
- user without must_change_password is not redirected
- missing AccountProfile is safe

PDP coexistence:

- PDP login route still renders
- PDP routes remain registered
- PDP middleware remains installed

regressions:

- Analytics staff views still require staff
- any authenticated user can still submit evaluations
- Phase 3 provisioning remains unchanged
- no Phase 5 evaluator snapshot behavior introduced
- no Phase 6 staff account UI introduced

==================================================
Verification
==================================================

Run:

python manage.py check

python manage.py makemigrations accounts --check

python manage.py test accounts

python manage.py test analytics

python manage.py test players

python manage.py test drafts

python manage.py test pdp

python manage.py test

git diff --check

==================================================
Self Review
==================================================

Before finishing, verify:

- no Phase 5 work was started
- no Phase 6 work was started
- PDP routes remain available
- PDP middleware remains installed
- forced password-change middleware avoids redirect loops
- inactive users cannot login
- update_session_auth_hash is used
- no plaintext temporary passwords displayed
- account roles do not grant staff/admin access
- LOGIN_URL / LOGIN_REDIRECT_URL changes are safe
- no unused imports
- no TODO/FIXME placeholders
- no architecture violations

==================================================
Final Report
==================================================

Report:

- implementation summary
- files created
- files modified
- migrations added, if any
- services implemented
- views/urls/templates implemented
- middleware implemented
- settings changes
- PDP coexistence behavior
- tests added
- test results
- implementation decisions
- deviations from engineering plan
- technical debt
- self-review findings
- confirmation that Phase 5 and Phase 6 were NOT started