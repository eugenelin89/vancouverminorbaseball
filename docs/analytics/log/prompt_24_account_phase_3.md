You are implementing Account Management v1.

Implement Phase 3 only:

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

Add these refinements:

1. Idempotency requirement

Provisioning must be idempotent.

Re-running the same import should not create duplicate users, profiles, or links.

The service should safely reuse existing linked accounts where possible and return statuses such as:

- created
- linked_existing
- already_linked
- skipped
- conflict

2. Reuse-before-create workflow

Provisioning should resolve users in this order:

- existing active/inactive self-linked user for the player
- safe existing user by email only if already linked to the same player
- otherwise create a new user

Do not silently link an unrelated existing email user to a different player.

3. Username normalization

Username generation must normalize Unicode consistently.

Example:

José García

should become:

jose.garcia

Username strategy:

firstname.lastname
firstname.lastname2
firstname.lastname3

Use deterministic suffixes only.

Do not use random suffixes.

4. Import summary

Include `already_linked` as a provisioning count in the safe import summary.

5. Service split

Create a dedicated:

accounts/services/username_service.py

Username generation belongs there, not inside provisioning_service.

Provisioning service should call username_service.

Recommended service responsibilities:

username_service.py
- normalize_username_part()
- base_username_for_player()
- username_for_player()

password_service.py
- temporary password generation
- setting temporary password
- must-change-password helpers

provisioning_service.py
- orchestration
- user creation/reuse
- profile updates
- UserPlayerLink creation/reuse
- import batch provisioning

==================================================
Phase 3 Scope
==================================================

Implement optional player import account provisioning.

Expected implementation includes:

- accounts/services/username_service.py
- accounts/services/password_service.py
- accounts/services/provisioning_service.py
- provisioning dataclasses/read models
- optional provisioning fields in import forms
- optional account_email mapping
- safe provisioning summary in PlayerImportBatch.import_summary
- integration from player import commit flow
- template updates for import upload/preview/detail
- service, import, UI, and regression tests

==================================================
Architecture Rules
==================================================

accounts
- owns account provisioning
- owns username generation
- owns temporary password handling
- owns profile/link orchestration

players
- continues to own player import parsing, matching, conflict resolution, player commit, and source-row provenance
- may call accounts provisioning services after player rows are committed
- must NOT implement username or password logic directly

analytics
- remains thin UI orchestration only
- must NOT own account provisioning logic

drafts
- unchanged

==================================================
Provisioning Rules
==================================================

Provisioning is optional.

If provisioning is disabled, player import behavior must remain unchanged.

If provisioning is enabled:

- create/reuse Django User
- create/update AccountProfile
- create/reuse UserPlayerLink relationship self
- role defaults to AccountRole.PLAYER for newly provisioned player accounts
- must_change_password=True
- created_from_import=True
- link created_from_import=True
- import_batch is recorded where appropriate

New users default to:

User.is_active=False

unless staff explicitly selects activation during import.

Do not downgrade existing staff/admin users to player.

==================================================
Username Rules
==================================================

Use:

firstname.lastname

If unavailable:

firstname.lastname2
firstname.lastname3
firstname.lastname4

Rules:

- lowercase
- trim spaces
- collapse repeated whitespace
- normalize Unicode accents
- remove unsafe username characters
- keep letters, numbers, dots, underscores, hyphens
- deterministic suffixes only
- check User.username case-insensitively
- do not use random values

If first or last name is missing unexpectedly, provisioning should skip/conflict safely rather than inventing an unrelated username.

==================================================
Password Rules
==================================================

If player.birthdate exists:

temporary password = YYYYMMDD

Use Django set_password.

Never store plaintext passwords.

Never log plaintext passwords.

Never serialize plaintext passwords into:

- import_summary
- preview_snapshot
- row_errors
- conflict_summary
- PlayerSourceRow
- AccountProfile.metadata
- UserPlayerLink.metadata
- test fixtures asserting serialized output

If birthdate is missing:

- do not create active login account automatically
- skip account provisioning for that row with a safe message

==================================================
Email Rules
==================================================

Email is optional.

Add optional `account_email` mapping for import.

Do NOT add email to players.Player.

If email exists and is unique:

- store it on User.email

If email belongs to an existing user:

- reuse only if safely linked to the same player
- otherwise mark provisioning conflict/review

Do not silently link an existing email to a different player.

Email matching should be case-insensitive.

==================================================
Import Integration
==================================================

Keep player identity import behavior in players.services.import_service.

After committed player rows are created/updated, call accounts.services.provisioning_service only if provisioning is enabled.

Expected row-level provisioning problems should not roll back player import:

- missing birthdate
- duplicate unrelated email
- already linked

Unexpected provisioning exceptions should roll back the import transaction.

Safe account provisioning counts should be nested under:

import_summary["account_provisioning"]

Include:

- enabled
- activate_users
- users_created
- users_linked
- already_linked
- skipped
- conflicts
- messages

No plaintext passwords.

==================================================
UI Requirements
==================================================

Update staff import UI only.

Upload form:

- provision_player_accounts checkbox
- activate_player_accounts checkbox, default false

Mapping form:

- optional account_email mapping

Preview/detail templates:

- show provisioning intent
- show safe provisioning status/counts
- never show passwords

Do not add account conflict resolution UI in Phase 3.

==================================================
Do NOT Implement
==================================================

Do NOT implement:

Phase 4

login/logout views

forced password-change middleware

password-change UI

staff account management UI

email invitations

password reset emails

parent account provisioning

coach account provisioning

role assignment UI

Analytics evaluator snapshot integration

player portal

parent portal

PDP migration

audit logging

new database models unless absolutely necessary

==================================================
Testing
==================================================

Implement tests for:

username_service

- firstname.lastname generation
- deterministic suffixes
- Unicode normalization
- unsafe character removal
- missing name behavior

password_service

- birthdate temporary password as YYYYMMDD
- set_temporary_password uses hashing
- plaintext is not stored in User.password
- must_change_password is set

provisioning_service

- missing birthdate skipped
- creates User
- creates AccountProfile
- role player
- must_change_password true
- new users inactive by default
- activation option creates active users
- creates UserPlayerLink self
- created_from_import flags set
- existing linked user reused
- repeated provisioning is idempotent
- duplicate unrelated email becomes conflict
- existing staff/admin linked user is not downgraded
- no plaintext password in result dicts/messages

import integration

- import without provisioning unchanged
- import with provisioning creates eligible accounts
- missing birthdate does not block player import
- duplicate unrelated email is reported safely
- existing linked player account is not duplicated
- import summary includes safe account_provisioning counts
- import summary includes already_linked
- import summary does not include plaintext passwords
- unexpected provisioning exception rolls back import transaction

analytics import UI

- upload page shows provisioning controls
- mapping supports account_email
- preview/detail show safe provisioning status
- existing conflict review remains unchanged

regressions

- players.Player still has no user field
- players import service does not own username/password logic
- Analytics evaluator behavior unchanged
- Phase 4 login/password middleware not introduced

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

Before finishing, verify:

- no plaintext passwords are stored, logged, or serialized
- provisioning is idempotent
- username generation is deterministic
- player import without provisioning remains unchanged
- accounts owns provisioning logic
- players does not contain username/password logic
- analytics views remain thin
- no Phase 4 behavior was implemented
- no unused imports
- no TODO/FIXME placeholders
- no architecture violations

==================================================
Final Report
==================================================

Report:

- implementation summary
- engineering plan updates made
- files created
- files modified
- migrations added, if any
- services implemented
- import/UI integration changes
- safe import summary structure
- tests added
- test results
- implementation decisions
- deviations from engineering plan
- technical debt
- self-review findings
- confirmation that Phase 4 was NOT started