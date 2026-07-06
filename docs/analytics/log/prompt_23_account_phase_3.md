You are continuing Account Management v1.

Do NOT implement application code.

Your task is to create the engineering plan for:

Account Management v1 Phase 3 — Player Import Account Provisioning

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

Analytics v1 is complete.

Current boundary:
- `players.Player` is canonical player identity.
- Django `User` is login identity.
- `accounts` owns account profiles, roles, and user/player links.
- `players.services.import_service` owns player import parsing/matching/commit.
- Analytics import views are thin UI orchestration.
- No account provisioning exists yet.

==================================================
Before Writing
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md
- docs/account_management/implementation/engineering/phase_02_user_player_link.md

Inspect:

- accounts/
- players/services/import_service.py
- players/models.py
- analytics/views.py
- analytics/forms.py
- analytics/templates/analytics/import_*.html
- analytics/tests.py
- players/tests.py
- accounts/tests.py

==================================================
Task
==================================================

Create:

docs/account_management/implementation/engineering/phase_03_player_import_account_provisioning.md

Do NOT implement code.

Do NOT create migrations.

Do NOT modify application behavior.

==================================================
Phase 3 Goal
==================================================

Define how player imports can optionally provision linked Django user accounts for imported `players.Player` records.

The import should still primarily create/update player identity records.

Account provisioning should be optional and owned by `accounts` services.

==================================================
Required Plan Sections
==================================================

Include:

1. Phase goal
2. Strict scope
3. Out of scope
4. Current state
5. User account provisioning model
6. Username generation strategy
7. Temporary password strategy
8. Birthdate handling
9. Missing birthdate fallback
10. Duplicate username/email handling
11. Import UI changes
12. Import service integration
13. Account provisioning services
14. UserPlayerLink behavior
15. AccountProfile behavior
16. Import summary/provenance
17. Security considerations
18. Tests to write
19. Implementation sequence
20. Risks/open questions
21. Definition of Done

==================================================
Important Product Requirements
==================================================

When player import provisioning is enabled:

- Imported player records may create linked Django users.
- Default account role should be `player`.
- Link relationship should be `self`.
- Created accounts should have `AccountProfile.created_from_import=True`.
- Created links should have `UserPlayerLink.created_from_import=True`.
- Created users should have `must_change_password=True`.

Username strategy:

- Default username format should be:

  firstname.lastname

- If already taken:

  firstname.lastname2
  firstname.lastname3
  firstname.lastname4

- Use deterministic suffixes.
- Do NOT use random suffixes.
- Normalize names safely:
  - lowercase
  - strip spaces
  - remove unsafe username characters
  - handle missing first/last name predictably

Temporary password strategy:

- If player birthdate exists:
  - temporary password = YYYYMMDD
- Example:
  - 2012-05-01 -> 20120501
- Use Django `set_password`.
- Do NOT store plaintext password.
- Do NOT log plaintext password.
- Do NOT include plaintext password in import summaries, source rows, preview snapshots, row errors, metadata, or logs.

Missing birthdate fallback:

- Recommended behavior:
  - do not create active login account automatically
  - mark account provisioning as skipped or needing staff review
  - do not invent weak passwords from name/team/etc.

Activation:

- Recommend imported accounts be inactive by default for v1 unless staff explicitly chooses activation.
- Plan should define the exact default.
- If active/inactive behavior is deferred, document it clearly.

Email:

- Email should be optional.
- If email exists and is unique, store it on User.email.
- If email conflicts with an existing unrelated user, mark provisioning conflict/review.
- Do not silently link an existing email to a different player.

==================================================
Service Boundary
==================================================

Create planned services in:

accounts/services/provisioning_service.py
accounts/services/password_service.py

Provisioning service should own:

- username generation
- user creation/update
- profile creation/update
- user/player link creation/update
- import provisioning orchestration

Password service should own:

- birthdate temporary-password generation
- password state helpers
- must_change_password handling

players.services.import_service may call accounts provisioning services after player identity commit, but must not own account logic.

analytics views should remain thin.

==================================================
Out Of Scope
==================================================

Explicitly exclude:

- login/logout views
- forced password-change middleware
- staff account management UI
- email invitations
- password reset emails
- parent account provisioning
- coach account provisioning
- role assignment UI
- Analytics evaluator snapshot integration
- player/parent portal
- PDP migration

==================================================
Security Requirements
==================================================

Address:

- birthdate passwords are weak and temporary only
- force password change will be implemented in Phase 4
- no plaintext password storage
- no plaintext password logging
- no plaintext passwords in JSON fields
- duplicate email/username safety
- inactive-by-default recommendation
- transaction safety with import commit
- rollback behavior if account provisioning fails

==================================================
Tests To Plan
==================================================

Include tests for:

- username generation
- username collision suffixes
- temporary password from birthdate
- missing birthdate behavior
- account provisioning creates User
- creates AccountProfile
- role defaults to player
- sets must_change_password=True
- creates UserPlayerLink relationship self
- duplicate existing linked user is reused safely
- duplicate unrelated email becomes conflict/review
- import without provisioning remains unchanged
- import with provisioning creates eligible accounts
- no plaintext password stored in metadata/import summaries/logs
- analytics/import regression tests still pass

==================================================
Final Report
==================================================

Report:

- files created
- files modified
- key decisions
- open questions
- confirmation that no application code was implemented