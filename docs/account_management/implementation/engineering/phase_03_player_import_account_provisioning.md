# Account Management v1 Phase 3 Engineering Plan: Player Import Account Provisioning

## Phase Goal

Allow staff/admin player imports to optionally provision linked Django login accounts for committed `players.Player` records.

Player import remains primarily a player identity workflow:

```text
CSV
  -> players.services.import_service
      -> players.Player
      -> accounts.services.provisioning_service, only when provisioning is enabled
          -> Django User
          -> accounts.AccountProfile
          -> accounts.UserPlayerLink
```

Provisioning must be optional, deterministic, conservative, idempotent, and owned by `accounts` services. Phase 3 should not change Analytics evaluation behavior, login behavior, password-change enforcement, or portal access.

Running the same import or provisioning workflow repeatedly must never create duplicate `User`, `AccountProfile`, or `UserPlayerLink` records. Provisioning results should distinguish `created`, `linked_existing`, `already_linked`, `skipped`, and `conflict`.

## Strict Scope

- Add account-provisioning planning and execution services under `accounts/services/`.
- Add optional account-provisioning controls to the existing Analytics staff import UI.
- Allow `players.services.import_service.commit_import_batch()` to call `accounts` provisioning services after player identity rows are committed.
- Provision Django `User` records for eligible imported players when staff explicitly enables provisioning.
- Create/update `AccountProfile` records for provisioned users.
- Create/update `UserPlayerLink` records with relationship `self`.
- Store safe non-sensitive account-provisioning counts in `PlayerImportBatch.import_summary`.
- Add tests for services, import integration, UI controls, and regressions.

## Out Of Scope

- Login/logout views.
- Forced password-change middleware.
- Staff account-management UI.
- Email invitations.
- Password reset emails.
- Parent account provisioning.
- Coach account provisioning.
- Role assignment UI.
- Analytics evaluator snapshot integration.
- Player/parent portal.
- PDP migration or bridge behavior.
- Account audit logging.
- New import ownership in `analytics`.
- Storing or displaying plaintext temporary passwords.

## Current State

Phase 1 is complete:

- `accounts.AccountProfile`
- `accounts.AccountRole`
- `accounts/services/profile_service.py`
- `accounts/services/role_service.py`
- `accounts/services/permissions.py`

Phase 2 is complete:

- `accounts.UserPlayerRelationship`
- `accounts.UserPlayerLink`
- `accounts/services/link_service.py`
- link constraints and admin registration

Existing import flow:

- `analytics.forms.PlayerImportUploadForm` collects `csv_file` and `source`.
- `analytics.forms.PlayerImportMappingForm` maps player identity fields.
- `analytics.views.PlayerImportUploadView` creates a `PlayerImportBatch` through `players.services.import_service.create_import_batch()`.
- `analytics.views.PlayerImportPreviewView` refreshes mapping through `players.services.import_service.build_import_preview()`.
- `analytics.views.PlayerImportConflictView` collects row conflict resolutions.
- `analytics.views.PlayerImportConfirmView` calls `players.services.import_service.commit_import_batch()`.
- `players.services.import_service` owns CSV parsing, source detection, mapping, matching, conflict review, player commit, source identifiers, and source row provenance.
- `PlayerImportBatch.import_summary` currently stores `ImportCommitResult` as JSON.
- Current import preview rows include `identity`, `original_row`, `unmapped_fields`, row action, match status, candidate options, and field conflicts.
- Current mapping does not include account-specific fields such as email.

The existing Analytics import UI is a transitional integration point. Long-term ownership should become:

```text
players
    player import

accounts
    account provisioning

analytics
    reporting and evaluations only
```

Phase 3 should continue using the existing Analytics import UI to minimize disruption, but Analytics must remain a thin orchestration/presentation layer.

## User Account Provisioning Model

Do not add a new database model in Phase 3 unless implementation discovers a hard requirement. The existing models are sufficient:

- Django `User` stores login credentials and email.
- `accounts.AccountProfile` stores role, import provenance, and `must_change_password`.
- `accounts.UserPlayerLink` stores the relationship between login identity and canonical player identity.
- `players.PlayerImportBatch.import_summary` stores safe aggregate provisioning counts.
- `players.PlayerSourceRow` remains player identity provenance only and should not store account secrets.

Use dataclasses/read models in `accounts.services.provisioning_service` for execution results:

- `ProvisioningOptions`
- `ProvisioningResult`
- `ProvisioningSummary`

Recommended `ProvisioningOptions` fields:

- `enabled: bool`
- `activate_users: bool = True`
- `email_column: str = ""`

Recommended `ProvisioningResult` fields:

- `player_id`
- `row_number`
- `status`: `created`, `linked_existing`, `already_linked`, `skipped`, `conflict`
- `username`
- `user_id`
- `messages`

Do not include plaintext passwords in any result object that may be serialized.

Provisioning user resolution order:

1. Existing active `UserPlayerLink` with `relationship=self` for the player.
2. Existing email user only when that user is already safely self-linked to the same player.
3. Create a new user.

Never silently associate an unrelated existing user or email address with a different player.

## Username Generation Strategy

Default username format:

```text
firstname.lastname
firstname.lastname2
firstname.lastname3
firstname.lastname4
```

Rules:

- Lowercase.
- Strip leading/trailing spaces.
- Collapse repeated whitespace.
- Normalize Unicode accents, for example `José García` becomes `jose.garcia`.
- Remove unsafe username characters.
- Keep letters, numbers, dots, underscores, and hyphens.
- Build the base username from player first and last name.
- Do not use random suffixes.
- Use deterministic numeric suffixes starting at `2`.
- Check against existing Django `User.username` values case-insensitively.

Missing name handling:

- Player import already requires first and last name for committed rows.
- If first or last name is unexpectedly missing at provisioning time, return a row-level provisioning conflict rather than inventing an unrelated username.

Create:

```text
accounts/services/username_service.py
```

Recommended service functions:

```python
normalize_username_part(value: str) -> str
base_username_for_player(player: Player) -> str
username_for_player(player: Player) -> str
```

Implementation should keep username generation in `accounts.services.username_service`, because username strategy is account behavior, not player identity behavior. `accounts.services.provisioning_service` should call `username_service` rather than implementing username normalization directly.

## Temporary Password Strategy

Temporary password rule:

```text
player.birthdate -> YYYYMMDD
```

Example:

```text
2012-05-01 -> 20120501
```

Use Django `User.set_password()` to persist the hash.

Create:

```text
accounts/services/password_service.py
```

Recommended functions:

```python
temporary_password_for_player(player) -> str
set_temporary_password(user, player) -> None
mark_must_change_password(user, value=True) -> AccountProfile
```

Security rules:

- Never store plaintext temporary passwords.
- Never log plaintext temporary passwords.
- Never include plaintext passwords in `metadata`, `import_summary`, `preview_snapshot`, `row_errors`, source rows, messages, or tests that assert serialized output.
- Phase 4 will enforce password change on first login. Phase 3 only sets `AccountProfile.must_change_password=True`.

## Birthdate Handling

Birthdate is already part of `players.Player` and import mapping:

- `players.Player.birthdate`
- `PlayerImportMappingForm.birthdate`
- `players.services.import_service.HEADER_ALIASES["birthdate"]`

Provisioning should use the committed `players.Player.birthdate`, not raw CSV values. This keeps the password decision tied to canonical player identity after matching/conflict resolution.

Rows that update an existing player should provision only after the player identity commit has applied accepted birthdate updates.

## Missing Birthdate Fallback

Default Phase 3 behavior:

- Do not create a login account automatically when `player.birthdate` is missing.
- Mark the provisioning row as `skipped` or `conflict` with a safe message such as `Missing birthdate; account not provisioned.`
- Do not invent passwords from name, team, birth year, registration ID, or source identifiers.
- Do not create active accounts with unusable passwords in the default flow.

Recommended status:

- Use `skipped` when the row is otherwise valid but missing birthdate.
- Use `conflict` when the row has duplicate identity/email/user ownership issues.

## Duplicate Username/Email Handling

### Username

If `firstname.lastname` exists, try deterministic suffixes:

```text
firstname.lastname2
firstname.lastname3
firstname.lastname4
```

Keep incrementing until a unique username is found. Do not reuse usernames from inactive users.

### Email

Email should be optional.

Create:

```text
accounts/services/email_service.py
```

Recommended functions:

```python
normalize_email(value: str) -> str
emails_equal(left: str, right: str) -> bool
find_existing_email_user(email: str)
```

Phase 3 should add an optional account email mapping control without adding email to `players.Player`.

Recommended UI behavior:

- Add optional `account_email` mapping to `PlayerImportMappingForm`.
- Do not store `account_email` in player identity fields.
- Use the mapped email only for account provisioning.
- Preserve raw email only as part of the existing import raw row provenance; do not duplicate it into account metadata unless there is a clear reason.

Email rules:

- If email is blank, create the user without email.
- If email is present and no user has that email, set `User.email`.
- If email is present and belongs to the same user already linked to the player, reuse/update safely.
- If email is present and belongs to a user already self-linked to the same player, treat as `already_linked` or `linked_existing`.
- If email is present and belongs to an unrelated user, mark the provisioning row as conflict/review.
- Do not silently link an existing email to a different player.
- Email comparisons should be case-insensitive.

## Import UI Changes

The existing Analytics import UI may expose the optional provisioning workflow because staff already uses it to import player CSVs. The UI must remain thin.

Update `PlayerImportUploadForm`:

- Add `provision_player_accounts = BooleanField(required=False, initial=False)`.
- Add `activate_player_accounts = BooleanField(required=False, initial=False)`.
- Keep activation default `False`.

Update `PlayerImportMappingForm`:

- Add optional `account_email = ChoiceField(required=False)`.
- Include it in mapping config but ensure `players.services.import_service` does not treat it as a player identity field.

Update templates:

- `analytics/templates/analytics/import_upload.html`
  - Show provisioning checkbox.
  - Show activation checkbox only as an explicit option.
- `analytics/templates/analytics/import_preview.html`
  - Display account provisioning intent and readiness summary if enabled.
  - Continue to route player identity conflicts through existing review flow.
- `analytics/templates/analytics/import_conflicts.html`
  - Keep player identity conflict resolution unchanged.
  - Do not add account conflict resolution UI in Phase 3 unless required for duplicate email handling. Duplicate email rows should be skipped/conflicted in provisioning results.
- `analytics/templates/analytics/import_detail.html`
  - Show safe provisioning counts only:
    - users created
    - existing users linked
    - already linked
    - accounts skipped
    - account conflicts

Do not display temporary passwords.

## Import Service Integration

`players.services.import_service` remains the owner of player identity import.

Recommended changes:

- Extend `create_import_batch()` to accept optional `provisioning_options=None` or keep options in `PlayerImportBatch.mapping_config` during upload.
- Extend `commit_import_batch()` to accept optional `provisioning_options=None`.
- After a player row is created/updated and `PlayerSourceRow` is recorded, collect committed row context:
  - `player`
  - `row_number`
  - `original_row`
  - `mapping_config`
  - `import_batch`
- After all player identity rows are processed, if provisioning is enabled, call `accounts.services.provisioning_service.provision_accounts_for_import(...)`.

Recommended transaction behavior:

- Keep `commit_import_batch()` atomic for player identity commit and account provisioning together.
- If account provisioning raises an unexpected exception, roll back the entire import commit.
- Expected row-level provisioning issues, such as missing birthdate or duplicate unrelated email, should be returned as row results and should not roll back player identity commit.
- Do not mark a batch failed solely because some account rows were skipped for expected provisioning reasons.

Avoid circular ownership:

- `players.services.import_service` may import `accounts.services.provisioning_service` inside the function body to avoid module-level coupling.
- `accounts.services.provisioning_service` may call `accounts.services.link_service`.
- `accounts.services.provisioning_service` should not call player import internals.

## Account Provisioning Services

Create:

```text
accounts/services/provisioning_service.py
```

Recommended functions:

```python
provision_player_account(
    player,
    import_batch=None,
    actor=None,
    email="",
    activate_user=False,
    row_number=None,
) -> ProvisioningResult

provision_accounts_for_import(
    import_batch,
    committed_rows,
    actor=None,
    options=None,
) -> ProvisioningSummary
```

`committed_rows` should be a list of simple dictionaries or dataclasses created by `players.services.import_service`, not `PlayerSourceRow` querysets that require re-parsing raw JSON.

Recommended provisioning statuses:

- `created`
- `linked_existing`
- `already_linked`
- `skipped`
- `conflict`

Create specialized services and keep responsibilities separated:

```text
accounts/services/username_service.py
    normalize_username_part()
    base_username_for_player()
    username_for_player()

accounts/services/email_service.py
    normalize_email()
    emails_equal()
    find_existing_email_user()

accounts/services/password_service.py
    generate_birthdate_password()
    set_temporary_password()
    mark_password_change_required()

accounts/services/provisioning_service.py
    orchestration
    create/reuse User
    create/reuse AccountProfile
    create/reuse UserPlayerLink
    provisioning read models
    import orchestration
```

Provisioning service should coordinate the workflow. Specialized services should perform username, email, and password work.

`provision_player_account()` responsibilities:

- Validate player.
- If missing birthdate, return skipped result.
- Resolve optional email.
- Detect existing self-linked user for player.
- Detect duplicate unrelated email.
- Generate deterministic username if a new user is needed.
- Create user with `is_active=activate_user`.
- Set temporary password through `password_service`.
- Create/update `AccountProfile`.
- Create/update `UserPlayerLink`.
- Return a safe result without plaintext password.

`provision_accounts_for_import()` responsibilities:

- Iterate committed player rows only.
- Aggregate counts.
- Return safe batch result.
- Never include plaintext passwords in serialized summaries.

## UserPlayerLink Behavior

Provisioned player accounts should link as:

- `relationship = UserPlayerRelationship.SELF`
- `is_primary = True`
- `is_active = True`
- `created_from_import = True`
- `import_batch = current PlayerImportBatch`

Use:

```python
accounts.services.link_service.link_user_to_player(...)
```

Do not create `UserPlayerLink` directly in import code.

Existing link behavior:

- If the player already has an active primary self-linked user, provisioning should reuse it only when it is clearly the same account.
- If a different active primary self-linked user exists, mark provisioning conflict.
- If the same user/player self link already exists, return `already_linked` or update provenance safely.

## AccountProfile Behavior

Provisioned player users should have:

- `role = AccountRole.PLAYER`
- `created_from_import = True`
- `import_batch = current PlayerImportBatch`
- `must_change_password = True`

Use profile services where possible:

- `get_or_create_account_profile(user)`
- `set_account_role(user, AccountRole.PLAYER)`

If updating an existing linked user:

- Do not downgrade staff/admin users to player automatically.
- If an existing linked user has a non-player role, preserve the role and return a message in the provisioning result.
- Ensure `created_from_import` and `import_batch` are set only when appropriate and do not erase prior provenance.

Activation:

- Create provisioned imported users with `is_active=True`.
- `AccountProfile` does not currently have an `is_active` field; Django `User.is_active` remains authoritative.

## Import Summary / Provenance

Store safe aggregate account provisioning results in `PlayerImportBatch.import_summary`.

Recommended structure:

```json
{
  "rows_processed": 10,
  "created": 8,
  "updated": 2,
  "skipped": 0,
  "conflicts": 0,
  "errors": [],
  "account_provisioning": {
    "enabled": true,
    "activate_users": false,
    "users_created": 7,
    "users_linked": 1,
    "already_linked": 0,
    "skipped": 2,
    "conflicts": 0,
    "messages": [
      "Row 4: Missing birthdate; account not provisioned."
    ]
  }
}
```

Rules:

- Do not store plaintext passwords.
- Do not store generated password hints.
- Do not store sensitive raw row data beyond existing import provenance.
- Do not store account email conflict details beyond safe staff-readable messages.
- Do not put plaintext passwords into `preview_snapshot`, `row_errors`, `conflict_summary`, `PlayerSourceRow.original_row`, `PlayerSourceRow.unmapped_fields`, `AccountProfile.metadata`, or `UserPlayerLink.metadata`.

## Security Considerations

- Birthdate passwords are weak and temporary only.
- Phase 4 must enforce password change before these accounts are allowed normal use.
- New imported users should be active immediately when account provisioning is enabled.
- No plaintext password storage.
- No plaintext password logging.
- No plaintext passwords in JSON fields.
- Duplicate email must be conservative and should not silently link unrelated accounts.
- Duplicate username handling must be deterministic and should not leak whether a person exists beyond staff-only import surfaces.
- Deactivated `UserPlayerLink` rows must not grant access.
- Phase 3 links do not create portal access.
- Account provisioning should run inside the import commit transaction for consistency.
- Expected provisioning skips/conflicts should not roll back player imports; unexpected provisioning exceptions should roll back the full commit.

## Tests To Write

### Password Service Tests

- `temporary_password_for_player()` returns `YYYYMMDD` from birthdate.
- Missing birthdate raises `ValidationError` or returns a clear missing-birthdate result, depending on final implementation.
- `set_temporary_password()` uses Django password hashing.
- Plaintext password is not stored on `User.password`.
- `mark_must_change_password()` sets `AccountProfile.must_change_password=True`.

### Provisioning Service Tests

- Username generation returns `firstname.lastname`.
- Username collision suffixes are deterministic: `firstname.lastname2`, `firstname.lastname3`.
- Unicode names are normalized, for example `José García` becomes `jose.garcia`.
- Unsafe username characters are removed.
- Missing first/last name produces a conflict/skipped result.
- Missing birthdate skips provisioning.
- Provisioning creates Django `User`.
- Provisioning creates `AccountProfile`.
- `AccountProfile.role` defaults to `player`.
- `AccountProfile.created_from_import=True`.
- `AccountProfile.must_change_password=True`.
- New users default to `is_active=False`.
- Explicit activation option creates active users.
- Provisioning creates `UserPlayerLink` with relationship `self`.
- `UserPlayerLink.created_from_import=True`.
- Existing linked user is reused safely.
- Duplicate unrelated email becomes conflict/review.
- Existing staff/admin linked user is not downgraded to player.
- No plaintext password appears in result dataclasses or serialized dictionaries.

### Import Service Tests

- Import without provisioning remains unchanged.
- Import with provisioning creates eligible accounts after player identity commit.
- Missing birthdate rows are skipped for account provisioning but player import can still commit.
- Duplicate unrelated email is reported as account provisioning conflict.
- Existing linked player account is not duplicated.
- Import summary includes safe account provisioning counts.
- Import summary does not include plaintext passwords.
- Unexpected provisioning exception rolls back the import transaction.

### Analytics Import View Tests

- Upload page displays optional provisioning controls to staff.
- Provisioning options are passed through thin Analytics views without account business logic.
- Preview/detail pages show safe provisioning status/counts only.
- Staff-only access remains unchanged.
- Existing import conflict review behavior remains unchanged.

### Regression Tests

- `players.Player` still has no direct user field.
- `players.services.import_service` does not implement username/email/password logic directly.
- Analytics evaluator permissions remain unchanged.
- Phase 4 login/password middleware is not introduced.
- Full `accounts`, `players`, and `analytics` test suites pass.

## Implementation Sequence

1. Add `accounts/services/username_service.py`.
2. Add `accounts/services/email_service.py`.
3. Add `accounts/services/password_service.py`.
4. Add username, email, and password service tests.
5. Add `accounts/services/provisioning_service.py` with `ProvisioningResult` and `ProvisioningSummary` dataclasses/read models.
6. Add provisioning service tests for idempotency, username, birthdate, duplicate email, profile, and link behavior.
7. Add optional provisioning fields to `PlayerImportUploadForm`.
8. Add optional `account_email` mapping to `PlayerImportMappingForm`.
9. Update import upload/preview/detail templates with thin display-only controls.
10. Extend `players.services.import_service.commit_import_batch()` to accept/pass provisioning options and call `accounts.services.provisioning_service` after player rows commit.
11. Store safe provisioning counts under `PlayerImportBatch.import_summary["account_provisioning"]`.
12. Add import integration tests in `players/tests.py`.
13. Add Analytics import view tests in `analytics/tests.py`.
14. Run:
    - `python manage.py check`
    - `python manage.py makemigrations accounts --check`
    - `python manage.py makemigrations players --check`
    - `python manage.py test accounts`
    - `python manage.py test players`
    - `python manage.py test analytics`
    - `python manage.py test drafts`
    - `python manage.py test`
    - `git diff --check`

## Risks / Open Questions

- Current `PlayerImportBatch` has no dedicated account-provisioning options field. Recommendation: store options in `mapping_config` or pass them explicitly through confirm POST rather than adding a model field in Phase 3.
- Current `ImportCommitResult` does not include account provisioning counts. Recommendation: keep player import counts unchanged and nest provisioning counts under `import_summary["account_provisioning"]`.
- Current import mapping has no account email field. Recommendation: add optional `account_email` mapping without adding email to `players.Player`.
- Existing raw source rows may contain email if the CSV contains it. This is already part of import provenance; Phase 3 should avoid duplicating email into account metadata unless needed.
- Inactive-by-default accounts may require staff activation later. This is intentional for Phase 3; Phase 6 can add staff account-management UI.
- Phase 4 password-change enforcement is now in place. Imported accounts are active immediately, but users with temporary passwords are forced to change password before normal access.
- There is no email invitation/reset infrastructure. Phase 3 should not attempt to notify users.
- Reusing existing users requires conservative matching. Email alone should not link to a different player.

## Definition of Done

- [ ] Account provisioning is optional during player import.
- [ ] Provisioning business logic lives in `accounts.services.provisioning_service`.
- [ ] Password temporary-state logic lives in `accounts.services.password_service`.
- [ ] Username generation lives in `accounts.services.username_service`.
- [ ] Email normalization lives in `accounts.services.email_service`.
- [ ] Provisioning uses `ProvisioningResult` and `ProvisioningSummary` read-model dataclasses.
- [ ] Provisioning is idempotent and does not create duplicate users, profiles, or links.
- [ ] Player import business logic remains in `players.services.import_service`.
- [ ] Analytics import views remain thin.
- [ ] New users receive deterministic usernames.
- [ ] New users receive hashed temporary birthdate passwords when birthdate exists.
- [ ] Missing birthdate does not create active login accounts automatically.
- [ ] New imported accounts are active immediately when account provisioning is enabled.
- [ ] `AccountProfile.role=player` for created player accounts.
- [ ] `AccountProfile.must_change_password=True`.
- [ ] `UserPlayerLink.relationship=self`.
- [ ] Safe provisioning counts are included in import summary.
- [ ] `already_linked` is tracked separately in provisioning summary.
- [ ] No plaintext passwords are stored or logged.
- [ ] Import without provisioning remains unchanged.
- [ ] Analytics evaluator behavior remains unchanged.
- [ ] Login/password-change behavior remains unchanged.
- [ ] Tests cover services, import integration, UI controls, and regressions.
