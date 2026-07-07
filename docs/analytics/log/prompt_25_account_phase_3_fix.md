You are performing the Phase 3 review fixes only.

Do NOT implement Phase 4.

Do NOT add new features.

Do NOT redesign the architecture.

Only address architectural correctness, idempotency, maintainability, and minor performance issues discovered during review.

==================================================
Before Coding
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md

Review the current Phase 3 implementation.

==================================================
Required Review Fixes
==================================================

1. Idempotency must include inactive self links

The engineering plan specifies that provisioning should first resolve:

- existing active self-linked user
- existing inactive self-linked user
- existing safe email-linked user
- otherwise create a new user

Currently provisioning only checks active self links.

Update provisioning so inactive self links are also reused.

Do NOT create duplicate users when an inactive self link already exists.

If appropriate:

- reactivate the existing link through the existing service layer
- preserve existing user/profile
- preserve history

Do not bypass link_service.

==================================================
2. Centralize user lookup
==================================================

Avoid spreading user-resolution logic throughout
`provisioning_service.py`.

Introduce small private helper methods such as:

- _find_existing_self_link(...)
- _find_existing_player_user(...)
- _find_safe_email_user(...)

or equivalent.

The provisioning workflow should read clearly as:

player

↓

existing linked account?

↓

safe email reuse?

↓

create account

rather than mixing lookup and provisioning logic.

==================================================
3. Keep ProvisioningSummary authoritative
==================================================

Review whether ProvisioningSummary should remain the single source of truth.

Avoid constructing provisioning summary dictionaries manually anywhere else.

Any serialization should come from:

ProvisioningSummary.to_dict()

==================================================
4. Verify password safety
==================================================

Verify again that plaintext passwords never appear in:

- import_summary
- preview_snapshot
- row_errors
- metadata
- log messages
- ValidationError messages
- serialized dataclasses

If any accidental exposure exists, remove it.

==================================================
5. Minor query cleanup
==================================================

Review provisioning queries.

Use select_related() where it removes obvious N+1 lookups.

Do not over-optimize.

==================================================
6. Remove duplication
==================================================

If small helper methods reduce duplicated logic inside:

- provisioning_service
- username_service
- email_service

apply those refactors.

Do not change external behavior.

==================================================
7. Tests
==================================================

Add regression tests for:

- inactive self link is reused
- provisioning remains idempotent after link deactivation/reactivation
- no duplicate users created
- no duplicate AccountProfiles
- no duplicate UserPlayerLinks

==================================================
Do NOT Change
==================================================

Do NOT implement:

Phase 4

login

logout

password change

middleware

email invitations

staff account management

parent provisioning

coach provisioning

player portal

parent portal

Analytics evaluator behavior

PDP migration

==================================================
Verification
==================================================

Run:

python manage.py check

python manage.py makemigrations accounts --check

python manage.py makemigrations players --check

python manage.py test accounts

python manage.py test players

python manage.py test analytics

python manage.py test drafts

python manage.py test

git diff --check

==================================================
Self Review
==================================================

Verify:

- provisioning remains idempotent

- inactive self links are reused

- no duplicate users are created

- no duplicate AccountProfiles are created

- no duplicate UserPlayerLinks are created

- ProvisioningSummary remains authoritative

- no plaintext passwords are exposed

- players still owns player identity only

- accounts still owns provisioning

- analytics remains a thin integration layer

- no architecture violations

- no TODO/FIXME placeholders

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

- confirmation that Phase 4 was NOT started