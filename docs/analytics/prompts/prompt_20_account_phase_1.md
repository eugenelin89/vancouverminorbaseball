You are implementing Account Management v1.

Implement **Phase 1 only**.

Do NOT implement Phases 2–6.

==================================================
Before Coding
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md

Review existing code:

- players/
- analytics/
- drafts/
- pdp/
- project settings
- authentication configuration

Implement only what belongs to Phase 1.

==================================================
Phase 1 Scope
==================================================

Implement the Account Management foundation.

Create a new Django app:

accounts

Implement:

1. AccountProfile model

Fields:

- user (OneToOne to Django User)
- role
- must_change_password
- created_from_import
- import_batch (nullable)
- activated_at
- deactivated_at
- metadata
- created_at
- updated_at

Do NOT duplicate Django User fields.

Use Django User for:

- username
- password
- email
- first_name
- last_name
- is_active
- is_staff
- is_superuser

==================================================
Account Roles
==================================================

Use TextChoices.

Roles:

- admin
- staff
- coach
- player
- parent
- guest_evaluator

Role is NOT a replacement for:

- is_staff
- is_superuser

Those remain authoritative for admin/staff access.

==================================================
Services
==================================================

Create:

accounts/services/

profile_service.py

role_service.py

permissions.py

Implement service functions described in the engineering plan.

Business logic belongs in services.

Do not place business logic inside models or views.

==================================================
Authentication Boundary
==================================================

Although this is a single Django app, keep authentication and account management logically separated.

Authentication responsibilities:

- login
- logout
- password
- middleware

Account responsibilities:

- profiles
- roles
- provisioning (future)
- user/player links (future)
- permissions

No login views should be implemented yet.

==================================================
Admin
==================================================

Register:

AccountProfile

Admin should display:

- user
- role
- must_change_password
- created_from_import
- activated_at
- deactivated_at

Do not expose metadata by default.

==================================================
Profile Creation
==================================================

Use explicit service creation.

Do NOT use Django signals.

Implement:

get_or_create_account_profile(user)

through profile_service.

Signals can be considered in a future version if necessary.

==================================================
Status
==================================================

Do NOT introduce an AccountStatus model or enum yet.

Continue using:

- User.is_active
- must_change_password

Document in code comments that a richer lifecycle may be introduced in a future version.

==================================================
Username Strategy
==================================================

Do NOT implement provisioning yet.

However, document inside provisioning-related TODO comments (where appropriate) that the future username generation strategy will be:

firstname.lastname

If already exists:

firstname.lastname2
firstname.lastname3
...

Use deterministic suffixes.

Do NOT use random values.

Email may eventually become the preferred username when available, but v1 provisioning will default to deterministic usernames if email is unavailable.

==================================================
Testing
==================================================

Implement tests for:

AccountProfile creation

Role defaults

Role helper functions

Permission helper functions

Admin registration

Regression tests

==================================================
Quality
==================================================

Maintain existing architecture.

Keep:

- thin views
- service-oriented design
- presentation-only templates

No unnecessary abstractions.

No speculative optimization.

==================================================
Do NOT Implement
==================================================

Do NOT implement:

Phase 2

UserPlayerLink

Provisioning

Import integration

Login views

Logout views

Password change

Middleware

Analytics changes

Evaluator snapshots

Staff account management UI

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

python manage.py test

git diff --check

==================================================
Self Review
==================================================

Before finishing, verify:

- service boundaries are clean
- no duplicated logic
- no unnecessary model fields
- no unused imports
- no TODO/FIXME placeholders except for documented future provisioning notes
- no architecture violations

==================================================
Final Report
==================================================

Report:

- summary
- files created
- files modified
- migrations
- tests
- implementation decisions
- deviations from engineering plan
- technical debt
- confirmation that Phase 2 was NOT started