You are implementing Account Management v1.

Implement **Phase 3 only**:

Account Management v1 Phase 3 — Player Import Account Provisioning

Do NOT implement Phases 4–6.

==================================================
Before Coding
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md

Review existing implementation:

- accounts/
- players/
- analytics/
- drafts/

Pay particular attention to:

- accounts.models.AccountProfile
- accounts.models.UserPlayerLink
- accounts.services.profile_service
- accounts.services.link_service
- players.services.import_service
- analytics import views/forms/templates

==================================================
Step 1 — Update Engineering Plan First
==================================================

Before implementing code, update:

docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md

Incorporate these architectural refinements.

--------------------------------------------------
1. Idempotency
--------------------------------------------------

Provisioning MUST be idempotent.

Running the same import repeatedly should never create duplicate:

- User
- AccountProfile
- UserPlayerLink

Provisioning should safely reuse existing resources whenever possible.

Provisioning status should distinguish:

- created
- linked_existing
- already_linked
- skipped
- conflict

--------------------------------------------------
2. Reuse Before Create
--------------------------------------------------

Provisioning should resolve users in this order:

1. Existing UserPlayerLink (relationship=self)
2. Existing email already safely linked to same player
3. Create new user

Never silently associate an unrelated existing user to a different player.

--------------------------------------------------
3. Username Normalization
--------------------------------------------------

Username generation must normalize Unicode.

Example:

José García

↓

jose.garcia

Username strategy:

firstname.lastname

firstname.lastname2

firstname.lastname3

...

Use deterministic numeric suffixes only.

Never generate random usernames.

--------------------------------------------------
4. Import Summary
--------------------------------------------------

Provisioning summary should include:

already_linked

as a separate count.

--------------------------------------------------
5. Service Boundaries
--------------------------------------------------

Introduce:

accounts/services/username_service.py

Username generation belongs here.

Provisioning service must call username_service.

Recommended responsibilities:

username_service.py

- normalize_username_part()
- base_username_for_player()
- username_for_player()

email_service.py

- normalize_email()
- emails_equal()
- find_existing_email_user()

password_service.py

- generate_birthdate_password()
- set_temporary_password()
- mark_password_change_required()

provisioning_service.py

- orchestration
- create/reuse User
- create/reuse AccountProfile
- create/reuse UserPlayerLink
- provisioning read models
- import orchestration

Provisioning should coordinate.

Specialized services should perform the work.

--------------------------------------------------
6. Transitional UI Ownership
--------------------------------------------------

Document that the existing Analytics import UI is a transitional integration point.

Long-term ownership should become:

players
    player import

accounts
    account provisioning

analytics
    reporting/evaluations only

Phase 3 should continue using the existing Analytics import UI to minimize disruption.

==================================================
Phase 3 Scope
==================================================

Implement optional player account provisioning.

Expected implementation:

- username_service.py
- email_service.py
- password_service.py
- provisioning_service.py

Implement provisioning dataclasses/read models.

Do NOT return loosely structured dictionaries from provisioning services.

Introduce read-model dataclasses such as:

ProvisioningResult

ProvisioningSummary

These become the authoritative objects used by import workflow and UI.

Update:

- player import services
- analytics import UI
- analytics import templates
- analytics import forms

Only as necessary.

==================================================
Architecture Rules
==================================================

accounts owns:

- provisioning
- username generation
- email normalization
- password generation
- profile creation
- link orchestration

players owns:

- player import
- CSV parsing
- matching
- player identity
- source rows

players may call provisioning services after player commit.

players must NOT implement:

- username generation
- password generation
- account creation

analytics:

Current Analytics import UI remains a temporary integration point.

Analytics must NOT own provisioning logic.

drafts unchanged.

==================================================
Provisioning Rules
==================================================

Provisioning is optional.

If disabled:

Player import behavior must remain unchanged.

If enabled:

Provisioning should:

- create/reuse User
- create/reuse AccountProfile
- create/reuse UserPlayerLink

Role defaults:

player

must_change_password=True

created_from_import=True

UserPlayerLink.created_from_import=True

AccountProfile.created_from_import=True

New users default:

User.is_active=False

unless explicitly activated during import.

Never downgrade existing staff/admin users.

==================================================
Username Rules
==================================================

Generate usernames:

firstname.lastname

firstname.lastname2

firstname.lastname3

Normalize:

- lowercase
- Unicode accents removed
- trim whitespace
- collapse repeated whitespace
- remove unsupported username characters
- deterministic suffixes only

Allow:

letters

numbers

dot

underscore

hyphen

Never use random suffixes.

Missing first/last name:

Skip provisioning safely.

==================================================
Email Rules
==================================================

Create:

email_service.py

Email optional.

Optional import mapping:

account_email

Store email only on Django User.

Never on players.Player.

Normalize emails.

Compare case-insensitively.

Reuse existing email ONLY if already safely linked to same player.

Otherwise:

conflict

==================================================
Password Rules
==================================================

Birthdate available:

temporary password:

YYYYMMDD

Use Django set_password().

Never store plaintext passwords.

Never log plaintext passwords.

Never serialize plaintext passwords.

If birthdate missing:

Skip provisioning.

Do not invent passwords.

==================================================
Provisioning Read Models
==================================================

Create dataclasses:

ProvisioningResult

ProvisioningSummary

PlayerImportBatch.import_summary should serialize from these dataclasses rather than constructing dictionaries throughout the codebase.

==================================================
Import Integration
==================================================

players.services.import_service

continues to own:

- parsing
- matching
- player creation

After player commit:

call

accounts.services.provisioning_service

Expected row issues:

- missing birthdate
- already linked
- duplicate unrelated email

must NOT rollback player import.

Unexpected exceptions:

Rollback transaction.

Provisioning summary:

import_summary["account_provisioning"]

Include:

enabled

activate_users

users_created

users_linked

already_linked

skipped

conflicts

messages

Never passwords.

==================================================
UI
==================================================

Reuse existing Analytics import UI.

Treat it as temporary.

Upload page:

provision_player_accounts

activate_player_accounts

Mapping:

account_email

Preview/detail:

safe provisioning summary

Never passwords.

==================================================
Do NOT Implement
==================================================

Do NOT implement:

Phase 4

login

logout

password change

middleware

email invitations

password reset emails

staff account management

player portal

parent portal

coach portal

Analytics evaluator snapshot changes

PDP migration

audit logging

==================================================
Testing
==================================================

Implement tests for:

username_service

email_service

password_service

provisioning_service

import integration

analytics import UI

ProvisioningResult

ProvisioningSummary

Idempotency

Repeated imports

Unicode usernames

Username suffixes

Email normalization

Missing birthdate

Existing linked users

Duplicate unrelated emails

Safe summaries

No plaintext password leakage

Regression tests

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

✓ provisioning is idempotent

✓ username generation deterministic

✓ no plaintext password stored anywhere

✓ import without provisioning unchanged

✓ provisioning uses read-model dataclasses

✓ provisioning orchestrates instead of duplicating logic

✓ username/email/password responsibilities remain separated

✓ players does not own account logic

✓ analytics remains a thin integration layer

✓ no Phase 4 work

✓ no unused imports

✓ no TODO/FIXME placeholders

✓ no architecture violations

==================================================
Final Report
==================================================

Report:

- implementation summary

- engineering plan updates

- files created

- files modified

- migrations

- services implemented

- dataclasses implemented

- import/UI changes

- provisioning summary format

- tests added

- test results

- implementation decisions

- deviations

- technical debt

- self-review

- confirmation that Phase 4 was NOT started