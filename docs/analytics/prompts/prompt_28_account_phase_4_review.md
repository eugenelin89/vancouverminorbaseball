You are performing the Phase 4 review fixes only.

Do NOT implement Phase 5.

Do NOT implement new features.

Do NOT redesign the architecture.

Only address architectural correctness, maintainability, authentication correctness, and minor cleanup issues discovered during review.

==================================================
Before Coding
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/phase_04_authentication_forced_password_change.md

Review the current Phase 4 implementation.

==================================================
Required Review Fixes
==================================================

1. Make password-change completion explicit

Currently AccountPasswordChangeView relies on the ordering of
PasswordChangeView.form_valid().

Refactor AccountPasswordChangeView so the password-change flow is explicit.

Recommended sequence:

1. form.save()
2. clear_password_change_required(user)
3. update_session_auth_hash(...)
4. add success message
5. redirect to landing_url_for_user()

Do not rely on implicit parent implementation ordering.

The resulting code should clearly document the intended sequence.

==================================================
2. Verify middleware behavior after successful password change

Ensure middleware does not immediately redirect the user back to
/accounts/password/

after a successful password change.

The sequence should be:

password updated

↓

must_change_password=False

↓

middleware no longer redirects

↓

redirect to landing page

==================================================
3. Centralize redirect constants

Review URL/path constants.

Avoid hardcoding account URLs throughout the implementation.

If multiple modules reference the same account paths, keep the constants
owned by:

accounts.services.auth_redirect_service

Other modules should import those constants rather than redefining them.

==================================================
4. Middleware readability

Review AccountPasswordChangeRequiredMiddleware.

If small helper methods improve readability, extract them.

Example:

_should_redirect(request)

or equivalent.

Do not change behavior.

==================================================
5. Landing page logic

Verify landing_url_for_user() remains the single authority for deciding
where authenticated users land.

Avoid duplicating landing logic inside views.

==================================================
6. Minor cleanup

Review:

- auth_redirect_service.py
- middleware.py
- views.py

Remove duplicated logic.

Remove unused imports.

Keep service boundaries clean.

==================================================
7. Additional Regression Tests

Add tests covering:

Password change:

- user with must_change_password=True successfully changes password
- must_change_password becomes False before redirect
- middleware does not redirect after successful password change
- session remains authenticated
- redirected to correct landing page

Middleware:

- password page POST is never blocked
- password page GET is never blocked
- middleware never creates redirect loop

Redirect service:

- landing_url_for_user remains single source of truth

==================================================
Do NOT Change
==================================================

Do NOT implement:

Phase 5

Phase 6

staff account management

player portal

parent portal

coach portal

email invitations

password reset emails

account activation

Analytics evaluator changes

PDP migration

social login

SSO

custom user model

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

Verify:

✓ password-change flow is explicit

✓ middleware never redirects after successful password change

✓ landing_url_for_user remains authoritative

✓ middleware remains simple and readable

✓ no redirect loops

✓ session stays authenticated

✓ no duplicated redirect logic

✓ no unused imports

✓ no TODO/FIXME placeholders

✓ PDP remains intact

✓ no Phase 5 work

✓ no architecture violations

==================================================
Final Report
==================================================

Report:

- files modified

- implementation summary

- review fixes applied

- tests added

- test results

- implementation decisions

- remaining technical debt

- self-review findings

- confirmation that Phase 5 was NOT started