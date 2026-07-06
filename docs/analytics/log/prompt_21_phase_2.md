You are continuing Account Management v1.

Do NOT implement application code.

Your task is to create the engineering plan for:

Account Management v1 Phase 2 — User ↔ Player Linking

==================================================
Context
==================================================

Account Management v1 Phase 1 is complete.

Existing Phase 1 implementation:

- `accounts` app exists.
- `AccountProfile` model exists.
- `AccountRole` choices exist.
- `profile_service.py` exists.
- `role_service.py` exists.
- `permissions.py` exists.
- Explicit profile creation is used.
- No signals are used.
- No `UserPlayerLink` exists yet.
- No provisioning exists yet.
- No login/password-change changes exist yet.

Account Management v1 master plan:

- docs/account_management/implementation/account_management_v1.md

==================================================
Before Writing
==================================================

Read:

- docs/account_management/implementation/account_management_v1.md

Inspect:

- accounts/
- players/
- analytics/
- drafts/

Review the existing Phase 1 implementation before creating the Phase 2 plan.

==================================================
Task
==================================================

Create:

docs/account_management/implementation/engineering/phase_02_user_player_link.md

If the directory does not exist, create it.

The plan should define Phase 2 only.

Do NOT implement code.

Do NOT create migrations.

Do NOT modify application behavior.

==================================================
Phase 2 Goal
==================================================

Define the foundation for linking Django `User` accounts to canonical `players.Player` records.

This phase should introduce:

User
↓
UserPlayerLink
↓
Player

without changing player import, Analytics evaluation behavior, login behavior, or password-change behavior.

==================================================
Required Plan Sections
==================================================

Include:

1. Phase goal
2. Strict scope
3. Out of scope
4. Current state
5. Model design
6. Relationship choices
7. Database constraints
8. Service functions
9. Admin integration
10. Permission considerations
11. How this phase preserves ownership boundaries
12. Tests to write
13. Implementation sequence
14. Risks / open questions
15. Definition of Done

==================================================
Model Design Requirements
==================================================

Plan a new model:

`accounts.UserPlayerLink`

Suggested fields:

- `user`
- `player`
- `relationship`
- `is_primary`
- `is_active`
- `created_from_import`
- `import_batch`
- `metadata`
- `created_at`
- `updated_at`

Relationship choices:

- `self`
- `parent`
- `guardian`
- `coach`
- `staff`

Ownership:

- `UserPlayerLink` belongs in `accounts`.
- Do NOT add `user` field to `players.Player`.
- Do NOT put account logic in `players`.
- Do NOT put linking logic in `analytics`.

==================================================
Constraint Planning
==================================================

Define database constraints carefully.

Recommended constraints:

- Prevent duplicate active relationships for the same user/player/relationship.
- Allow a user to be linked to multiple players.
- Allow a player to have multiple linked users.
- Allow parents/guardians to link to multiple children.
- Allow multiple parents/guardians per player.
- Enforce at most one active primary `self` link per user.
- Consider whether at most one active primary `self` link per player should also be enforced.
- Clarify what happens when links are deactivated.

If a constraint is tricky because of database limitations or partial unique indexes, document the intended Django implementation.

==================================================
Service Planning
==================================================

Plan:

accounts/services/link_service.py

Include functions:

- `link_user_to_player(user, player, relationship="self", is_primary=True, created_from_import=False, import_batch=None, metadata=None)`
- `deactivate_link(link, actor=None)`
- `activate_link(link, actor=None)`
- `unlink_user_from_player(user, player, relationship=None, actor=None)`
- `get_players_for_user(user, active_only=True)`
- `get_users_for_player(player, active_only=True)`
- `get_primary_player(user)`
- `get_primary_user(player)`
- `is_player_self(user, player)`

Business rules should live in the service.

Do not use signals.

==================================================
Admin Planning
==================================================

Plan admin registration for:

`UserPlayerLink`

Admin should show:

- user
- player
- relationship
- is_primary
- is_active
- created_from_import
- import_batch
- created_at
- updated_at

Do not expose metadata by default.

==================================================
Out Of Scope
==================================================

Explicitly exclude:

- player import account provisioning
- automatic link creation
- login/logout views
- password-change views
- middleware
- account activation workflow
- username generation
- temporary passwords
- Analytics evaluator snapshot changes
- staff account-management UI
- parent/player portal
- coach portal

==================================================
Security / Privacy Notes
==================================================

Include notes that:

- links may later control access to player/parent portals
- do not expose sensitive player data merely because a link exists
- permissions must be checked by service/view layer
- deactivated links should not grant access

==================================================
Final Report
==================================================

Report:

- files created
- files modified
- key decisions
- constraints proposed
- open questions
- confirmation that no application code was implemented