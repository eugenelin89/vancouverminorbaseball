You are continuing development on the VCB baseball platform.

Do NOT implement code yet.

Your task is to create an engineering plan for the next major epic:

Account Management v1

This epic is required before production use because imported player records currently do not create login accounts.

==================================================
Context
==================================================

Analytics v1 is complete.

Important current boundary:

- `players.Player` represents canonical player identity.
- Django `User` represents login identity.
- Analytics currently imports player records only.
- Imported players do NOT automatically get user accounts.
- Evaluators are currently existing Django users.
- Player records and login users are separate.

Desired future behavior:

- When importing players, the system should be able to create linked Django user accounts.
- If player birthdate is available, the temporary/default password should be `YYYYMMDD`.
- Users created this way must be forced to change password after first login.
- Imported users should receive the `player` role by default.
- Any authenticated user should be allowed to evaluate any player.
- When an evaluation is submitted, the evaluator’s user and role should be recorded/snapshotted for later analysis.
- Staff/admin users should still be the only users who can access staff/admin views.

==================================================
Repository Discovery
==================================================

Before planning, inspect the repository.

Read:

- docs/analytics/implementation/STATUS.md
- docs/analytics/architecture/
- docs/analytics/implementation/
- existing players app
- existing analytics app
- existing drafts app
- existing authentication/user-related code, if any
- existing settings/urls/templates related to login/logout/password change

List any existing docs related to users, auth, permissions, roles, accounts, registration, or onboarding.

Do not assume such docs exist.

==================================================
Planning Goal
==================================================

Create an engineering plan for:

docs/account_management/implementation/account_management_v1.md

If the directory does not exist, create it.

The plan should define Account Management v1 in phases.

Recommended phases:

Phase 1 — User Profile and Role Foundation
- Add user profile or account profile model if no equivalent exists.
- Define user role choices:
  - admin
  - staff
  - coach
  - player
  - parent
  - guest_evaluator
- Define `must_change_password`.
- Define `created_from_import`.
- Define how roles relate to Django `is_staff` and `is_superuser`.

Phase 2 — Player/User Linking
- Define a link between Django User and `players.Player`.
- Recommended model:
  - user
  - player
  - relationship: self / parent / guardian / coach / staff
- Clarify whether this belongs in `players`, `accounts`, or a new app.
- Avoid putting account logic inside `analytics`.

Phase 3 — Player Import Account Provisioning
- Extend player import workflow so imported players can create/update linked user accounts.
- Default role should be `player`.
- If birthdate exists, temporary password should be `YYYYMMDD`.
- If birthdate is missing, define safe fallback behavior.
- Set `must_change_password=True`.
- Decide whether imported users are active immediately or require staff activation.
- Define duplicate email/username behavior.
- Define provenance fields and audit behavior.

Phase 4 — Login and Forced Password Change
- Add or reuse login/logout/password-change views.
- Force users with `must_change_password=True` to change password after login.
- Ensure they cannot continue using the app until password is changed.
- Define redirect behavior.
- Define tests.

Phase 5 — Evaluator Role Snapshot
- Update coach assessment submission so any authenticated user can evaluate any player.
- Store evaluator user.
- Snapshot evaluator role at submission time:
  - evaluator_role_key
  - evaluator_role_name
- Ensure role changes later do not alter historical evaluations.
- Preserve existing analytics behavior.

Phase 6 — Staff Account Management UI
- Staff/admin page for viewing users/profiles/linked players.
- Staff can activate/deactivate imported accounts.
- Staff can reset temporary password or trigger password reset flow.
- Staff can update roles.
- Do not overbuild.

==================================================
Important Design Rules
==================================================

The plan must preserve current app ownership:

- `players` owns player identity.
- `analytics` owns observations/evaluations/reporting.
- account/user management should not be embedded inside analytics.
- import parsing logic should remain in `players.services.import_service`.
- account provisioning can be called from import services but should live in account/user services.

Prefer a new app if appropriate, likely:

- `accounts`

But inspect the repo first before deciding.

==================================================
Security Requirements
==================================================

Address these explicitly:

- Birthdate password is weak and must be temporary only.
- Force password change on first login.
- Consider whether imported accounts should be inactive by default.
- Avoid exposing passwords after creation.
- Do not log plaintext passwords.
- Do not show raw password except possibly one-time staff-facing import result, if absolutely required.
- Password setup/reset link may be preferable long term.
- Email uniqueness and username uniqueness must be handled.
- Parent/player privacy should be considered.

==================================================
Permission Requirements
==================================================

Define clear rules:

- Any authenticated user can submit evaluations.
- Staff/admin can access staff/admin views.
- Players should not automatically get staff access.
- Parents should not automatically get staff access.
- Role is used for analytics and permission checks.
- Django `is_staff` / `is_superuser` still control admin/staff access unless explicitly changed.

==================================================
Deliverables
==================================================

The engineering plan should include:

1. Goals
2. Non-goals
3. Current state
4. Proposed app/model ownership
5. Proposed models
6. Role definitions
7. Import provisioning workflow
8. Password and login workflow
9. Evaluation permission behavior
10. Evaluator role snapshot behavior
11. Staff account management workflow
12. Services to create
13. Views/templates to create or reuse
14. URL paths
15. Admin integration
16. Data migration considerations
17. Security considerations
18. Tests to write
19. Implementation sequence
20. Risks/open questions
21. Definition of Done

==================================================
Constraints
==================================================

Do NOT implement code.

Do NOT create migrations.

Do NOT modify existing application behavior.

Do NOT start Account Management implementation.

Only create the engineering plan documentation.

==================================================
Final Report
==================================================

Report:

- files created
- files modified
- existing auth/account/role code discovered
- major architectural decisions
- open questions
- confirmation that no application code was implemented