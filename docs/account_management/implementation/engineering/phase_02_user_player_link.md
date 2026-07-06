# Account Management v1 Phase 2 Engineering Plan: User Player Linking

## Phase Goal

Create the foundation for linking Django `User` accounts to canonical `players.Player` records.

Phase 2 introduces:

```text
User
  -> accounts.UserPlayerLink
      -> players.Player
```

This phase should establish the data model, service boundary, admin registration, and test coverage needed for future account provisioning and portals. It must not change player import behavior, Analytics evaluation behavior, login behavior, or password-change behavior.

## Strict Scope

- Add `accounts.UserPlayerLink`.
- Add relationship choices for user/player links.
- Add database constraints and indexes for active links and primary self links.
- Add `accounts/services/link_service.py`.
- Add admin registration for `UserPlayerLink`.
- Add tests for model constraints, service behavior, admin registration, and ownership boundaries.
- Preserve explicit service-based behavior. Do not use signals.

## Out Of Scope

- Player import account provisioning.
- Automatic link creation during import.
- Login/logout views.
- Password-change views.
- Middleware.
- Account activation workflow.
- Username generation.
- Temporary passwords.
- Analytics evaluator snapshot changes.
- Staff account-management UI.
- Parent/player portal.
- Coach portal.
- PDP migration or bridge behavior.
- Any changes to `players.Player`, player import behavior, Analytics observation behavior, or draft behavior.

## Current State

Account Management v1 Phase 1 is complete:

- `accounts` app exists.
- `accounts.AccountProfile` exists.
- `accounts.AccountRole` choices exist.
- `accounts/services/profile_service.py` exists.
- `accounts/services/role_service.py` exists.
- `accounts/services/permissions.py` exists.
- Explicit profile creation is used.
- No signals are used.
- No `UserPlayerLink` exists yet.
- No provisioning exists yet.
- No login/password-change changes exist yet.

Related existing app boundaries:

- `players` owns canonical player identity, imports, matching, aliases, source identifiers, source rows, and tags.
- `analytics` owns observations, evaluator snapshots, reports, metrics, timelines, comparisons, and Analytics UI.
- `drafts` owns draft workflows.
- `accounts` owns account profiles, roles, permissions, and user/player account relationships.

## Model Design

Create `accounts.UserPlayerLink`.

Suggested fields:

- `user`: `ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="player_links")`
- `player`: `ForeignKey("players.Player", on_delete=models.CASCADE, related_name="user_links")`
- `relationship`: `CharField(max_length=40, choices=UserPlayerRelationship.choices)`
- `is_primary`: `BooleanField(default=False)`
- `is_active`: `BooleanField(default=True)`
- `created_from_import`: `BooleanField(default=False)`
- `import_batch`: nullable `ForeignKey("players.PlayerImportBatch", on_delete=models.SET_NULL, blank=True, null=True, related_name="user_player_links")`
- `metadata`: `JSONField(default=dict, blank=True)`
- `created_at`: inherited from the existing `accounts.TimeStampedModel`
- `updated_at`: inherited from the existing `accounts.TimeStampedModel`

Add `UserPlayerRelationship(models.TextChoices)` in `accounts/models.py`:

- `SELF = "self", "Self"`
- `PARENT = "parent", "Parent"`
- `GUARDIAN = "guardian", "Guardian"`
- `COACH = "coach", "Coach"`
- `STAFF = "staff", "Staff"`

Recommended model metadata:

- `ordering = ["user__username", "relationship", "player__last_name", "player__first_name", "id"]`
- Indexes:
  - `["user", "is_active"]`
  - `["player", "is_active"]`
  - `["relationship", "is_active"]`
  - `["created_from_import"]`
  - `["import_batch"]`

`__str__` should include the user, relationship, player, and inactive state when applicable.

## Relationship Choices

Relationship values describe why a login account is linked to a player:

- `self`: the user is the player.
- `parent`: the user is a parent of the player.
- `guardian`: the user is a guardian of the player.
- `coach`: the user has a coaching relationship with the player.
- `staff`: the user has a staff relationship with the player.

Relationship values are not authorization by themselves. They are identity/context links that future views and services may use when deciding access.

## Database Constraints

Use database constraints where practical, backed by service-level validation for clearer errors.

Recommended constraints:

1. Prevent duplicate active relationships for the same user/player/relationship.

   Intended Django implementation:

   ```python
   models.UniqueConstraint(
       fields=["user", "player", "relationship"],
       condition=models.Q(is_active=True),
       name="accounts_unique_active_user_player_relationship",
   )
   ```

   Deactivated historical links may remain in the database. A new active link for the same user/player/relationship can be created after the prior one is inactive.

2. Enforce at most one active primary `self` link per user.

   Intended Django implementation:

   ```python
   models.UniqueConstraint(
       fields=["user"],
       condition=models.Q(is_active=True, is_primary=True, relationship="self"),
       name="accounts_unique_primary_self_link_per_user",
   )
   ```

   This supports one user linked to many players, while keeping only one primary player identity for the user.

3. Consider at most one active primary `self` link per player.

   Recommended Phase 2 decision: include this constraint unless implementation or product review identifies a strong reason not to.

   Intended Django implementation:

   ```python
   models.UniqueConstraint(
       fields=["player"],
       condition=models.Q(is_active=True, is_primary=True, relationship="self"),
       name="accounts_unique_primary_self_link_per_player",
   )
   ```

   Rationale: a canonical player should normally have only one primary login identity. Parent, guardian, coach, and staff links can still be many-to-many.

4. Do not globally enforce only one primary link per user across all relationship types.

   Parents and guardians may later need a primary child context, but that is separate from the `self` identity rule and should not be assumed in Phase 2.

5. Deactivated links should not participate in active uniqueness constraints.

   Deactivation preserves history while allowing staff to correct links without deleting data.

Partial unique indexes are supported by Django on the project database target used for development. If deployment database support differs, keep service-level validation and document the database limitation before implementation.

## Service Functions

Create:

```text
accounts/services/link_service.py
```

Business rules should live in this service. Views, admin actions, future provisioning, and future account-management UI should call this service rather than writing link rules directly.

### `link_user_to_player(...)`

Signature:

```python
def link_user_to_player(
    user,
    player,
    relationship="self",
    is_primary=True,
    created_from_import=False,
    import_batch=None,
    metadata=None,
):
    ...
```

Responsibilities:

- Validate `user` is an authenticated Django user instance.
- Validate `player` is a `players.Player`.
- Validate `relationship` is one of `UserPlayerRelationship`.
- Validate `import_batch`, when supplied, is a `players.PlayerImportBatch`.
- Normalize `metadata` to `{}` when omitted.
- Use `transaction.atomic()`.
- Reuse an existing active link for the same user/player/relationship when possible.
- Update simple mutable fields on an existing active link if needed:
  - `is_primary`
  - `created_from_import`
  - `import_batch`
  - `metadata`
- Enforce primary `self` rules before saving.
- Raise `ValidationError` with descriptive messages for invalid or conflicting requests.

Primary behavior:

- Default `is_primary=True` is appropriate for `relationship="self"`.
- For non-`self` relationships, callers should normally pass `is_primary=False`.
- If a caller passes `is_primary=True` for non-`self`, Phase 2 should either:
  - reject it with `ValidationError`, or
  - allow it only if a documented future use case exists.

Recommended Phase 2 decision: reject primary non-`self` links to keep semantics clean.

### `deactivate_link(link, actor=None)`

Responsibilities:

- Validate `link` is a `UserPlayerLink`.
- Use `transaction.atomic()`.
- If already inactive, return it unchanged.
- Set `is_active=False`.
- Set `is_primary=False` to prevent inactive primary confusion.
- Save `updated_at`.
- Do not delete the row.
- Do not require `actor` in Phase 2. It is reserved for future audit behavior.

### `activate_link(link, actor=None)`

Responsibilities:

- Validate `link`.
- Use `transaction.atomic()`.
- Enforce duplicate active relationship and primary `self` constraints before activation.
- Set `is_active=True`.
- Preserve `is_primary` only if it remains valid.
- Save `updated_at`.

If reactivation would violate an active-link constraint, raise `ValidationError`.

### `unlink_user_from_player(user, player, relationship=None, actor=None)`

Responsibilities:

- Validate `user` and `player`.
- Find active links for the user/player pair.
- If `relationship` is provided, only deactivate that active relationship.
- If `relationship` is omitted, deactivate all active links between that user and player.
- Return the number of links deactivated or the affected link queryset/list.
- Do not delete rows.

### `get_players_for_user(user, active_only=True)`

Responsibilities:

- Return a queryset of `players.Player` linked to the user.
- Default to active links only.
- Use `distinct()`.
- Use ordering from `players.Player`.
- Avoid returning players through inactive links when `active_only=True`.

### `get_users_for_player(player, active_only=True)`

Responsibilities:

- Return a queryset of Django users linked to the player.
- Default to active links only.
- Use `distinct()`.
- Use stable ordering by username/id.
- Avoid returning users through inactive links when `active_only=True`.

### `get_primary_player(user)`

Responsibilities:

- Return the player from the active primary `self` link for the user.
- Return `None` if no active primary `self` link exists.
- Use `select_related("player")`.

### `get_primary_user(player)`

Responsibilities:

- Return the user from the active primary `self` link for the player.
- Return `None` if no active primary `self` link exists.
- Use `select_related("user")`.

### `is_player_self(user, player)`

Responsibilities:

- Return `True` when an active `self` link exists between the user and player.
- Return `False` for anonymous users, inactive links, non-`self` links, and missing players.

## Admin Integration

Register `UserPlayerLink` in `accounts/admin.py`.

Admin should show:

- `user`
- `player`
- `relationship`
- `is_primary`
- `is_active`
- `created_from_import`
- `import_batch`
- `created_at`
- `updated_at`

Recommended configuration:

- `list_display`: fields above, except `updated_at` can be omitted if the list gets too wide.
- `list_filter`: `relationship`, `is_primary`, `is_active`, `created_from_import`, `import_batch`.
- `search_fields`: `user__username`, `user__email`, `user__first_name`, `user__last_name`, `player__first_name`, `player__last_name`, `player__preferred_name`.
- `autocomplete_fields`: `user`, `player`, `import_batch`.
- `readonly_fields`: `created_at`, `updated_at`.
- `exclude`: `metadata`.

Do not expose metadata by default because future imports or provisioning may store operational context there.

## Permission Considerations

Phase 2 should not grant access based only on a link.

Security and privacy rules:

- Links may later control access to player/parent portals.
- A link should not expose sensitive player data unless a view/service explicitly checks permission.
- Permission checks must happen in service/view layers.
- Deactivated links must not grant access.
- `parent`, `guardian`, `coach`, and `staff` relationship values are context, not automatic authorization.
- Analytics v1 behavior remains unchanged: any authenticated user can evaluate any player.
- Staff/admin checks remain based on `User.is_staff` or `User.is_superuser` unless a later phase explicitly changes that.

Recommended Phase 2 permission helper additions are optional and should remain narrow if implemented:

- `can_view_user_player_link(user, link)`
- `can_manage_user_player_links(user)`

If added, staff/admin should be the only users allowed to manage links in Phase 2. No self-service link management should be introduced.

## How This Phase Preserves Ownership Boundaries

- `accounts` owns `UserPlayerLink` because it connects authentication identity to player identity.
- `players.Player` remains canonical player identity and should not gain a `user` field.
- `players` should not import account services for Phase 2.
- `analytics` should not own linking logic.
- `analytics` should not change evaluator permissions or observation creation in Phase 2.
- `drafts` should not change.
- Future account provisioning may call `link_service`, but provisioning is not part of Phase 2.

## Tests To Write

### Model Tests

- `UserPlayerLink` can link a user to a player with relationship `self`.
- A user can be linked to multiple players.
- A player can have multiple linked users.
- Multiple parent/guardian links can exist for one player.
- Duplicate active user/player/relationship links are blocked.
- Deactivated duplicate historical links are allowed.
- Only one active primary `self` link is allowed per user.
- Only one active primary `self` link is allowed per player, if the recommended constraint is implemented.
- Non-`self` primary links are rejected if the recommended service rule is implemented.
- `created_from_import`, `import_batch`, and `metadata` persist correctly.

### Service Tests

- `link_user_to_player()` creates an active link.
- `link_user_to_player()` reuses or updates an existing active link instead of creating a duplicate.
- `link_user_to_player()` rejects anonymous or missing users.
- `link_user_to_player()` rejects invalid players.
- `link_user_to_player()` rejects unsupported relationships.
- `link_user_to_player()` rejects invalid primary `self` conflicts.
- `deactivate_link()` marks a link inactive and clears `is_primary`.
- `activate_link()` reactivates a valid inactive link.
- `activate_link()` rejects reactivation when it would conflict with an active link.
- `unlink_user_from_player()` deactivates matching links.
- `get_players_for_user()` returns only active linked players by default.
- `get_players_for_user(active_only=False)` includes inactive historical links.
- `get_users_for_player()` returns only active linked users by default.
- `get_primary_player()` returns the primary self-linked player.
- `get_primary_user()` returns the primary self-linked user.
- `is_player_self()` returns true only for active `self` links.

### Admin Tests

- `UserPlayerLink` is registered in admin.
- Admin excludes `metadata`.
- Admin has expected list display, filters, search fields, and readonly timestamp fields.

### Boundary Regression Tests

- `players.Player` does not have a direct `user` field.
- Player import can still run without account link creation.
- Analytics coach assessment permission remains any authenticated user.
- No signal auto-creates links.

## Implementation Sequence

1. Add `UserPlayerRelationship` choices to `accounts/models.py`.
2. Add `UserPlayerLink` model to `accounts/models.py`.
3. Add constraints and indexes.
4. Generate a migration for `accounts`.
5. Register `UserPlayerLink` in `accounts/admin.py`.
6. Create `accounts/services/link_service.py`.
7. Add model, service, admin, and boundary tests.
8. Run:
   - `python manage.py makemigrations accounts`
   - `python manage.py migrate`
   - `python manage.py test accounts`
   - `python manage.py test analytics`
   - `python manage.py test players`
   - `python manage.py test drafts`
   - `python manage.py test`
9. Confirm no Analytics, player import, login, password, or draft behavior changed.

## Risks / Open Questions

- Whether to enforce at most one active primary `self` link per player in the database. Recommendation: enforce it for Phase 2 unless product needs shared primary logins.
- Whether `is_primary=True` should be valid for parent/guardian links. Recommendation: reject in Phase 2 and revisit when parent/player portals are designed.
- Whether deactivated links should keep `is_primary=True` for historical accuracy. Recommendation: clear `is_primary` on deactivation because active primary lookup is operational, not historical.
- Whether `link_user_to_player()` should reuse inactive links instead of creating new rows. Recommendation: create a new active row or explicitly reactivate through `activate_link()` so history is clearer.
- Whether import provenance in `metadata` may become sensitive. Recommendation: keep metadata hidden in admin by default.
- Whether future audit requirements need actor/timestamp fields for link changes. Phase 2 accepts `actor` arguments in services but should not add audit models yet.

## Definition of Done

- [ ] `accounts.UserPlayerLink` exists with relationship choices.
- [ ] Database constraints protect duplicate active relationships.
- [ ] Primary active `self` link rules are enforced.
- [ ] `accounts/services/link_service.py` exists with the planned service functions.
- [ ] Admin registration exists and hides metadata by default.
- [ ] Tests cover model constraints, services, admin registration, and ownership boundaries.
- [ ] Player import behavior is unchanged.
- [ ] Analytics evaluation behavior is unchanged.
- [ ] Login/password-change behavior is unchanged.
- [ ] No provisioning behavior is implemented.
- [ ] No PDP migration or bridge behavior is implemented.
- [ ] Full relevant test suite passes.
