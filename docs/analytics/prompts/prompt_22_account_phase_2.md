You are implementing Account Management v1.

Implement **Phase 2 only**.

Do NOT implement Phases 3–6.

The Phase 2 engineering plan has been reviewed and approved.

Implement exactly what is described in:

- docs/account_management/implementation/engineering/phase_02_user_player_link.md

Do not redesign the architecture.

==================================================
Before Coding
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/phase_02_user_player_link.md

Review existing implementation:

- accounts/
- players/
- analytics/
- drafts/

Pay particular attention to the existing Phase 1 implementation.

==================================================
Scope
==================================================

Implement only Phase 2.

Expected implementation includes:

- UserPlayerRelationship TextChoices
- UserPlayerLink model
- database constraints
- migration
- accounts/services/link_service.py
- admin registration
- tests

Nothing else.

==================================================
Architecture Rules
==================================================

Maintain these ownership boundaries.

accounts
- owns UserPlayerLink
- owns account relationships
- owns linking services

players
- owns canonical player identity
- MUST NOT gain a user field
- MUST NOT contain account logic

analytics
- MUST NOT own linking logic
- MUST NOT change evaluator behavior
- MUST NOT change permissions

drafts
- unchanged

==================================================
Model Rules
==================================================

Implement UserPlayerLink exactly as defined in the engineering plan.

Relationship choices:

- self
- parent
- guardian
- coach
- staff

Fields:

- user
- player
- relationship
- is_primary
- is_active
- created_from_import
- import_batch
- metadata
- created_at
- updated_at

==================================================
Database Constraints
==================================================

Implement the documented constraints.

Use conditional UniqueConstraint where supported.

Required:

- unique active (user, player, relationship)

- unique active primary self per user

- unique active primary self per player

Historical inactive rows must remain valid.

==================================================
Business Logic
==================================================

Business rules belong in:

accounts/services/link_service.py

Do NOT place relationship validation inside model clean() unless required by Django itself.

Views and future provisioning should call the service layer.

==================================================
Implement Services
==================================================

Implement:

link_user_to_player()

unlink_user_from_player()

activate_link()

deactivate_link()

get_players_for_user()

get_users_for_player()

get_primary_player()

get_primary_user()

is_player_self()

Use transaction.atomic() where appropriate.

Use select_related()/prefetch_related() where obvious.

Raise ValidationError with clear messages.

==================================================
Admin
==================================================

Register UserPlayerLink.

Hide metadata.

Show:

- user
- player
- relationship
- is_primary
- is_active
- created_from_import
- import_batch
- timestamps

==================================================
Do NOT Implement
==================================================

Do NOT implement:

Phase 3

automatic provisioning

player import integration

username generation

temporary passwords

login/logout

password change

middleware

player portal

parent portal

coach portal

analytics evaluator snapshot

staff account UI

audit logging

==================================================
Testing
==================================================

Implement every test described in the engineering plan.

Include:

- model tests
- constraint tests
- service tests
- admin tests
- boundary regression tests

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

- service boundaries remain clean

- Player model was NOT modified

- Analytics behavior is unchanged

- no duplicated relationship logic

- no unnecessary queries

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

- migrations added

- database constraints implemented

- services implemented

- tests added

- test results

- implementation decisions

- deviations from engineering plan

- technical debt

- self-review findings

- confirmation that Phase 3 was NOT started