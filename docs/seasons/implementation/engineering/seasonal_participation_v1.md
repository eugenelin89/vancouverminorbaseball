# Seasonal Participation V1 Engineering Plan

Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 is the next implementation phase.

Created: 2026-07-15.

## Verified Production State

Production counts were checked in the production environment on July 15, 2026:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

This means production currently has no Platform V1 player roster data, coach profile data, or Analytics evaluation data to migrate into seasonal records. Existing unrelated production data in legacy apps must remain untouched.

Migration planning for Seasonal Participation V1 should therefore be empty-state-first:

- no fake legacy season is required;
- no player roster backfill is required;
- no coach assignment backfill is required;
- no observation season/team backfill is required;
- new seasonal tables should be empty immediately after the schema migration in production.

## 1. Executive Summary

The platform currently treats `players.Player` as the permanent player identity, but it still stores `team_name` and `division` directly on that permanent record. That is workable for a first import workflow, but it is not safe for long-term player development because players and coaches can move teams, divisions, or rosters across seasons.

Seasonal Participation V1 should introduce season-aware roster context without recreating people. Permanent player identity remains stable in `players.Player`; permanent login identity remains stable in Django `User` and `accounts.AccountProfile`; evaluations remain owned by `analytics`. The new seasonal layer should record which players and coaches participated with which season-specific teams, and `analytics.Observation` should preserve the season/team/division context that existed when an evaluation was submitted.

Settled model direction:

- Add a new `seasons` app for the season/roster bounded context.
- Add `Season` and `SeasonTeam`.
- Add `PlayerRosterMembership` for player stints on season teams.
- Add `CoachSeasonAssignment` for coach assignments on season teams.
- Add durable evaluation-context fields or references on `analytics.Observation`.
- Keep `Player.team_name` and `Player.division` temporarily as compatibility/current-display fields during migration, then deprecate them after season-aware views and filters are proven.

## 2. Current Problem

Current `players.Player` records include:

- `division`
- `team_name`

Those fields describe a roster state, not permanent player identity. If staff import a player again next season with a new team or division, updating those fields rewrites the apparent current and historical context for every view that reads from `Player`.

Current submitted evaluations reference:

- `players.Player`
- `analytics.EvaluationCycle`
- evaluator `User`
- `EvaluatorRole`
- evaluator role snapshot fields
- evaluation perspective snapshot

They do not currently store the player's season, team, or division at submission time. Review services currently derive `player_team` and `player_division` from `Observation.player.team_name` and `Observation.player.division`, which means historical display can change when the player record changes.

Coach import currently creates or reuses coach accounts and stores `team` and `division` in profile metadata. It does not create season-specific coach assignments, and reused coaches currently receive a new temporary password during import. That is not safe for reimporting established coaches for a new season.

## 3. Goals

- Reuse permanent `players.Player` records across seasons.
- Reuse permanent coach `User` and `AccountProfile` records across seasons.
- Represent team/division participation as season-specific history.
- Preserve prior-season roster and coach assignment records.
- Preserve evaluation season/team/division context as it existed when each evaluation was submitted.
- Make player and coach imports deterministic when repeated.
- Support transfers and multi-team participation without overwriting history.
- Keep existing Platform V1 behavior stable during the migration.
- Keep subsystem ownership clear and avoid circular dependencies.
- Provide a safe production migration path that recognizes current production is empty for Platform V1 roster/evaluation data.

## 4. Non-Goals

Seasonal Participation V1 should not implement:

- new player identity rules;
- player merge or account merge;
- coach-to-player permission restrictions unless separately approved;
- roster-management dashboards beyond the planned implementation phases;
- scheduling, attendance, registration, payments, or league operations;
- parent portal changes;
- draft workflow changes except future read-only context integration;
- PDP migration;
- historical season reconstruction beyond what current data supports;
- deletion of existing `Player.team_name` or `Player.division` during the first implementation phase;
- legacy app data migration or cleanup.

## 5. Current Architecture Findings

`players` currently owns:

- `Player`
- `PlayerAlias`
- `PlayerSourceIdentifier`
- `PlayerImportBatch`
- `PlayerSourceRow`
- `PlayerTag`
- player import parsing, preview, matching, conflict handling, provenance, and optional account provisioning.

`accounts` currently owns:

- `AccountProfile`
- `UserPlayerLink`
- account roles
- username, email, password, provisioning, account operations, link management, and coach import.

`analytics` currently owns:

- `Observation`
- `ObservationResponse`
- `EvaluationCycle`
- observation types, sources, evaluator roles, questions, question sets, services, review filters, metrics, timeline, comparison, command center, and player-facing/coach-facing evaluation access.

Important current coupling:

- Player import maps `team_name` and `division` into `Player`.
- Player matching can use `division` as context.
- Analytics player search, metrics, review, and command center filters read `Player.team_name` and `Player.division`.
- Coach import accepts `team` and `division` but persists them as metadata only.
- `EvaluationCycle` has no season link.

## 6. Recommended Domain Model

Use the following domain concepts.

### Season

Represents an organizational/roster period, such as `2026 Spring`, `2026 Summer`, or `2026`.

Fields to consider:

- `key`: stable slug or identifier, unique.
- `name`: display name.
- `starts_on`: nullable date.
- `ends_on`: nullable date.
- `is_active`: whether the season is available for current workflows.
- `is_current`: optional single-current flag if needed for default UI.
- `metadata`: JSON for import/source-specific context.
- timestamps.

Settled uniqueness and current-season behavior:

- unique `key`.
- allow exactly one current season.
- use a conditional database constraint for `is_current=True` if it is safe on SQLite; otherwise enforce the rule through a transactional service and tests.

Season naming:

- `key` should be stable and unique, using values such as `2026-spring`, `2026-summer`, or `2027-spring`.
- `name` should be human-friendly, using values such as `2026 Spring`, `2026 Summer`, or `2027 Spring`.
- Do not hard-code a fixed list of season types.

Archive behavior:

- Do not delete seasons that have memberships, assignments, imports, cycles, or observations.
- Mark inactive rather than deleting.

### SeasonTeam

Represents a team within one season.

Fields to consider:

- `season`: FK to `Season`.
- `name`: team display name.
- `division`: division/program label for that season team.
- `normalized_name`: normalized team name for imports.
- `normalized_division`: normalized division for imports.
- `external_source`: optional source name.
- `external_identifier`: optional source ID.
- `is_active`.
- `metadata`.
- timestamps.

Recommended uniqueness:

- unique `(season, normalized_name, normalized_division)`.
- optional unique `(season, external_source, external_identifier)` when both source fields are present.

Recommendation:

Use season-specific teams only for V1. Avoid a separate permanent `Team` model until the organization needs long-lived team brands independent of season.

### PlayerRosterMembership

Represents one player's roster stint on one season team.

Fields to consider:

- `player`: FK to `players.Player`.
- `season_team`: FK to `SeasonTeam`.
- `status`: active, inactive, transferred, removed, injured, guest, or equivalent controlled values.
- `jersey_number`: optional string.
- `roster_role`: optional label if needed later.
- `is_primary`: primary roster assignment for current display/filter defaults.
- `starts_on`: nullable date.
- `ends_on`: nullable date.
- `source`: import/manual source label.
- `source_identifier`: optional source row/team/player membership ID.
- `import_batch`: nullable FK to `players.PlayerImportBatch` if player import remains the provenance batch.
- `source_row`: nullable FK to `players.PlayerSourceRow` if a direct row link is useful.
- `metadata`.
- timestamps.

Recommended uniqueness:

- prevent exact duplicate active memberships for the same `(player, season_team, source_identifier)` when source identifier exists.
- prevent exact duplicate active memberships for the same `(player, season_team, starts_on, ends_on)` when dates are supplied.
- allow multiple memberships in one season because transfers and multi-team participation are real.
- enforce only one active primary membership per `(player, season)` where practical.

Current team derivation:

- Current team should be derived from active primary membership in the current season.
- If no primary exists, derive from the latest active membership in the current season.
- If no current-season membership exists, return blank or a clear no-current-roster state.

### CoachSeasonAssignment

Represents one coach/user assignment to one season team.

Fields to consider:

- `user`: FK to Django `User`.
- `season_team`: FK to `SeasonTeam`.
- `assignment_role`: head coach, assistant coach, coordinator, evaluator, manager, or text/title.
- `is_primary`.
- `is_active`.
- `starts_on`.
- `ends_on`.
- `source`.
- `source_identifier`.
- `metadata`.
- timestamps.

Recommended uniqueness:

- prevent duplicate active assignment for the same `(user, season_team, assignment_role)`.
- allow one coach to be assigned to multiple teams in a season.
- allow one team to have multiple coaches.
- optionally enforce one active primary assignment per `(user, season)` where practical.

Important distinction:

`AccountProfile.role` remains permanent platform metadata. `CoachSeasonAssignment.assignment_role` is seasonal team context. Changing a seasonal assignment must not grant Django staff/superuser access and must not rewrite the permanent account role except through existing account services when staff intentionally changes the account role.

## 7. Model Ownership

Settled ownership:

- New `seasons` app owns `Season`, `SeasonTeam`, `PlayerRosterMembership`, and `CoachSeasonAssignment`.
- `players` continues to own `Player`, player matching, source identifiers, source rows, and player import orchestration.
- `accounts` continues to own `User`, `AccountProfile`, `UserPlayerLink`, account provisioning, passwords, roles, and coach account creation/reuse.
- `analytics` owns evaluation cycles and observations, including submitted evaluation context snapshots.

Why the new `seasons` app is used:

- Seasonal participation is shared by players, accounts, analytics, and future roster/attendance/video work.
- Putting coach assignments in `accounts` would couple account identity to roster history.
- Putting player memberships in `players` would make player identity responsible for team operations.
- Putting season teams in `analytics` would make evaluations own roster structure.

Allowed dependencies:

- `seasons` may reference `players.Player` and Django `User`.
- `players` import services may call `seasons` services to create/update season/team/membership records.
- `accounts` coach import services may call `seasons` services to create/update coach assignments.
- `analytics` may reference or snapshot `seasons` records when observations are submitted.

Avoid:

- `seasons` calling analytics services.
- views directly creating roster memberships or assignments.
- templates inferring current team from historical memberships.

## 8. Season And Team Design

Season and evaluation cycle should be related but distinct:

- Season = roster/organizational period.
- Evaluation cycle = feedback window within a season.

Recommended `EvaluationCycle` change:

- Add nullable FK `season` to `Season`.
- Keep `starts_on` and `ends_on` on `EvaluationCycle`.
- Allow cycles without a season during compatibility migration.
- Require a season in the application workflow for newly created production cycles once the seasonal foundation is implemented.

SeasonTeam should be season-specific, not permanent:

- `13U Expos` in 2026 and `13U Expos` in 2027 are separate `SeasonTeam` rows.
- This prevents future imports from accidentally rewriting prior-year rosters.
- If the organization later needs long-lived team lineage, add a separate permanent team concept in a future plan.

## 9. Player Roster Membership Design

Settled behavior: a player may have multiple memberships in one season.

Supported cases:

- transfer from one team to another;
- call-up or affiliate/guest participation;
- concurrent development roster plus game roster;
- corrected import with same membership.

Primary rules:

- A player may have multiple memberships in one season.
- A player should have at most one active primary membership per season.
- A non-primary membership may be active at the same time.
- Setting a new active primary membership should demote or end the prior active primary membership through a service, not direct model saves.

Transfer rules:

- Transfers should create a new membership/stint rather than overwriting the old team.
- The previous membership can receive `ends_on` and status `transferred` or `inactive`.
- If dates are unknown, use the import date or leave dates null with metadata explaining the source.

## 10. Coach Assignment Design

Settled behavior: one coach may have multiple assignments in one season.

Supported cases:

- head coach of one team and assistant coach of another;
- coordinator across multiple teams;
- guest evaluator for a team;
- staff member also coaching.

Use this minimal controlled assignment-role list for V1:

- Head Coach
- Assistant Coach
- Manager
- Coordinator
- Evaluator

Future roles may be added through an explicit migration or controlled-choice update after confirming how they affect imports, filters, and permissions.

Assignment role should be separate from account role:

- `AccountProfile.role=coach` means the user is generally a coach in the platform.
- `CoachSeasonAssignment.assignment_role=head_coach` means the user has a season-team role.

Password behavior:

- Creating a new coach account should set a random temporary password and `must_change_password=True`.
- Reusing an established coach account for a new season must not reset the password by default.
- Reused accounts should only be forced to change password if they already require it or staff explicitly chooses a reset.

## 11. Evaluation Context Design

Historical evaluations must retain the context that existed when submitted.

Recommended future design:

- Add nullable FK `player_roster_membership` to `Observation`.
- Add nullable FK `season` to `Observation`.
- Add nullable FK `season_team` to `Observation`.
- Add snapshot fields on `Observation`:
  - `player_season_name`
  - `player_team_name`
  - `player_division`
- Consider evaluator context:
  - nullable FK `evaluator_coach_assignment` for coach/staff/guest evaluators when available;
  - snapshot fields `evaluator_team_name`, `evaluator_division`, `evaluator_assignment_role`.

Why FK plus snapshot is recommended:

- FK provides structured filtering and drill-down while the referenced records exist.
- Snapshot fields preserve display text if season/team names are later corrected.
- Existing observations in non-production environments can be backfilled with best-known current fields without pretending to reconstruct unsupported history.

Submission behavior:

- When an observation is submitted, resolve player context for the observation cycle's season.
- Prefer active primary roster membership for `(player, season)`.
- If none exists, prefer active non-primary membership.
- If multiple equally valid memberships exist, require staff/evaluator selection or record an unresolved/no-roster context.
- Snapshot season/team/division before saving submitted state.
- Do not recalculate snapshots after submission except through an explicit staff correction workflow.

Existing draft or reopened observations:

- Drafts may refresh context until submitted.
- Reopened observations should preserve the original submitted context unless staff explicitly resubmits with a correction policy.
- No production observation-context migration or backfill is required during the initial schema foundation because verified production has zero observations.

## 12. Player Import Design

Player import should remain staff-facing and owned by `players/services/import_service.py`, with seasonal participation delegated to season services.

CSV behavior:

- Staff must select a season before preview/confirm, or the CSV must include an accepted season column.
- `team`/`team_name` and `division` should map to `SeasonTeam`, not permanently overwrite player identity.
- Identity fields continue to match/create `Player`.
- Roster fields create/update `PlayerRosterMembership`.

Recommended source fields:

- Permanent player identity: name, preferred name, birthdate, birth year, gender, school, bats, throws, positions.
- Roster context: season, team, division, jersey number, roster status, starts_on, ends_on, source roster ID.
- Source identifiers: registration ID, registrant ID, source player ID.

Preview behavior:

- Show matched or new permanent player.
- Show season.
- Show season team to be created or reused.
- Show membership action: create, update, transfer/stint, skip, conflict.
- Show whether compatibility `Player.team_name` and `division` will be updated for current display.

Confirm behavior:

- Within one transaction per import batch or one safe transaction per row, depending on current service pattern.
- Create/reuse `Season`.
- Create/reuse `SeasonTeam`.
- Create/update `Player`.
- Create/update `PlayerRosterMembership`.
- Record `PlayerSourceRow`.
- Preserve prior memberships.

## 13. Coach Import Design

Coach import should stay in `accounts/services/coach_import_service.py` for account provisioning, with season/team assignment delegated to season services.

CSV behavior:

- Required account fields remain `first_name`, `last_name`, `email`.
- Staff must select a season before preview/confirm, or the CSV must include an accepted season column.
- `team` and `division` create/reuse `SeasonTeam`.
- Assignment fields create/update `CoachSeasonAssignment`.

Recommended optional fields:

- username
- team
- division
- assignment_role
- is_active
- starts_on
- ends_on
- source_id
- notes

Account behavior:

- New coach account: create user, role `coach`, active by default unless CSV says inactive, random temporary password, `must_change_password=True`.
- Existing coach account: reuse account, update assignment, do not reset password by default.
- Existing non-coach account: conflict unless staff chooses a supported role update through account operations.
- Existing inactive coach: assignment may be created, but account activation should require explicit import option or account operation.

Result behavior:

- Report users created, coaches reused, assignments created, assignments updated, conflicts, skipped rows, active/inactive accounts.
- Temporary passwords are shown only for newly created accounts or explicit password reset actions.

## 14. Reimport And Duplicate Behavior

Player reimport should be deterministic:

- Same source identifier and same season team updates the existing membership/provenance.
- Same permanent player and same season team without source identifier should update the existing active membership if no conflicting dates/status exist.
- Different team in same season should create a new membership/stint unless staff chooses to transfer/end the prior primary membership.
- Different season should create a new season-team membership and preserve old membership.

Coach reimport should be deterministic:

- Same email and same season team/assignment role reuses the account and updates the assignment.
- Same email and different season creates or updates a different assignment.
- Existing coach password is not reset just because the row is reimported.
- Duplicate email rows in the same CSV should remain a conflict unless a deterministic merge rule is explicitly added.

Conflicts should block only unsafe rows where possible. Valid rows may continue if the current import workflow supports partial commits and clear result reporting.

## 15. Transfer And Multi-Team Behavior

Transfers:

- Do not edit the prior team out of history.
- Create a new membership/stint.
- Mark prior active primary membership inactive/transferred when staff confirms a transfer.
- Preserve original import provenance.

Multi-team participation:

- Allow concurrent non-primary memberships.
- Require one active primary membership for current-display defaults when practical.
- Show all memberships in season history views.

Ambiguous imports:

- If a player has multiple active memberships in the selected season and the CSV row lacks enough team/division information, mark the row for review.
- Do not guess which membership should receive roster-specific updates.

## 16. Production Migration Strategy

Production is empty for Platform V1 roster/evaluation data.

Verified production counts on July 15, 2026:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

Production migration should therefore:

1. Create schema only.
2. Do not create a legacy season.
3. Do not fabricate player roster memberships.
4. Do not fabricate coach assignments.
5. Do not backfill observations.
6. Leave all new seasonal tables empty after migration.
7. Preserve unrelated legacy app data untouched.

Production safety:

- Run deployment verification before migration to confirm production still has zero Platform V1 players, coach profiles, and observations.
- If unexpected Platform V1 rows exist in another environment, do not guess history. Use a defensive management command or explicit service-backed backfill plan that produces reviewable counts and metadata.
- Keep defensive checks in deployment verification and service/management-command logic rather than fabricating records in the schema migration.
- Back up the production database before applying migrations.
- Run the migration in staging or a production copy first.

## 17. Compatibility Strategy For Current Player Fields

`Player.team_name` and `Player.division` should not be deleted immediately.

Recommended staged approach:

- Phase 1: keep fields, add compatibility helpers, and do not populate production memberships from them because verified production has zero players.
- Phase 2: stop treating them as authoritative in new imports; write seasonal membership records first.
- Phase 2 compatibility: optionally update `Player.team_name` and `Player.division` from current active primary membership for existing UI compatibility.
- Phase 4/5: update analytics filters, player search, metrics, and review views to use seasonal context.
- Later: mark fields deprecated in code/docs.
- Future cleanup: remove fields only after all reads have moved to season services and production has passed a full release cycle.

Matching-service compatibility:

- `division` may remain a matching hint temporarily.
- New matching should prefer permanent identifiers/name/birthdate and use season/team only as context, not identity.

## 18. Evaluation-Cycle Relationship

Season and evaluation cycle are related but not identical.

Recommended rule:

- A season may have many evaluation cycles.
- An evaluation cycle may belong to one season.
- Evaluations should use their cycle's season as the first context lookup.

Examples:

- `2026 Spring` season may include `Preseason Evaluation`, `Midseason Check-In`, and `Year-End Evaluation` cycles.
- A winter clinic cycle may belong to a clinic season or have no season during compatibility migration.

If a cycle has no season:

- Submission should fall back to current player membership only during compatibility.
- The observation should clearly mark context source as fallback in metadata.

## 19. Permission Implications

Do not introduce team-restricted permissions in the first schema phase unless explicitly approved.

Future likely rules:

- Staff/admin can manage all seasons, rosters, assignments, and evaluations.
- Coaches may eventually evaluate players on assigned teams.
- Coaches may review evaluations according to assignment scope.
- Players may evaluate players in allowed peer scope, likely same season/team or approved cycle.
- Guest evaluators may be scoped by explicit assignment or staff-created access.

Dependencies before enforcing team scope:

- reliable `CoachSeasonAssignment` records;
- reliable player memberships;
- active season defaults;
- clear exception rules for guest evaluators and coordinators;
- privacy review for player peer-evaluation scope.

## 20. Security And Privacy

- Do not expose all roster history to players unless a player-facing policy approves it.
- Player-facing evaluations should continue to hide evaluator names unless policy changes.
- Coach review filters should not grant access to users without review permission.
- Account role metadata must not grant Django `is_staff` or `is_superuser`.
- Coach assignment role must not grant account permissions by itself.
- Temporary passwords must not be reset or displayed for reused coach accounts unless staff explicitly performs a password reset.
- Import provenance may contain sensitive source-row data and should remain staff/admin-only.
- Seasonal records should preserve history through inactive/end-dated rows rather than destructive deletion.

## 21. Performance And Indexing

Likely indexes:

- `Season`: `key`, `is_active`, `is_current`, `starts_on`, `ends_on`.
- `SeasonTeam`: `(season, normalized_division, normalized_name)`, `(season, division)`, `(is_active, season)`.
- `PlayerRosterMembership`: `(player, season_team)`, `(season_team, is_active)`, `(player, is_primary, is_active)`, `(starts_on, ends_on)`, optional source identifier fields.
- `CoachSeasonAssignment`: `(user, season_team)`, `(season_team, is_active)`, `(user, is_primary, is_active)`, assignment role.
- `Observation`: `season`, `season_team`, `player_roster_membership`, `(season, season_team, status)`, `(evaluation_cycle, season_team, status)`.
- `EvaluationCycle`: `season`, `(season, is_active)`.

Query patterns to optimize:

- current roster for season/team;
- player season history;
- coach assignments by season/team;
- evaluation review filters by season/team/division/cycle;
- command center metrics by season/team/division/cycle;
- import preview duplicate detection.

Use `select_related()` for season/team/membership references in evaluation review and timeline services.

## 22. Proposed Implementation Phases

### Phase 0 - Decisions And Compatibility

Status: complete.

Decisions recorded:

- Use a new `seasons` app.
- Keep `players.Player` as permanent player identity.
- Keep Django `User` and `accounts.AccountProfile` as permanent coach/account identity.
- Use stable season keys such as `2026-spring` and display names such as `2026 Spring`.
- Allow exactly one current season.
- Use season-specific teams only for V1; do not add a permanent `Team` model.
- Allow multiple player memberships in one season.
- Allow only one active primary membership per player per season.
- Represent transfers as new memberships/stints rather than overwriting old memberships.
- Allow one coach to have multiple assignments in one season.
- Keep seasonal coach assignment role separate from permanent account role.
- Use V1 assignment roles: Head Coach, Assistant Coach, Manager, Coordinator, Evaluator.
- Treat `Season` and `EvaluationCycle` as distinct; a season has many evaluation cycles.
- New production evaluation cycles should require a season once the foundation exists.
- Keep `Player.team_name` and `Player.division` temporarily as compatibility/current-display fields.
- Use an empty-production migration strategy because verified production has zero players, zero coach profiles, and zero observations.

### Phase 1 - Season And Roster Foundation

Status: complete.

Completed:

- Added `seasons` app and models.
- Added `Season`.
- Added `SeasonTeam`.
- Added `PlayerRosterMembership`.
- Added `CoachSeasonAssignment`.
- Added transactional domain services for season lookup, team lookup, player membership creation/update, coach assignment creation/update, current season handling, and current team/division compatibility.
- Added admin configuration.
- Added schema-only migration.
- Added comprehensive tests.
- Added compatibility helpers for current team/division.
- Registered the app in settings.
- Updated architecture, seasonal, user/admin, and deployment documentation as needed.
- Kept existing import/UI behavior unchanged except compatibility helpers.

Phase 1 must not:

- change player import UI;
- change coach import UI;
- attach evaluation context;
- enforce team-based permissions;
- add roster-management dashboards;
- remove `Player.team_name` or `Player.division`;
- implement Platform V2 summaries.

### Phase 2 - Season-Aware Player Import

Status: complete.

- Add season selection to player import.
- Map team/division to `SeasonTeam`.
- Create/update `PlayerRosterMembership`.
- Preserve `PlayerSourceRow` provenance.
- Maintain compatibility fields from current primary membership if approved.
- Update import preview, conflict review, confirm, and tests.

### Phase 3 - Coach Seasonal Assignment

- Add season selection to coach import.
- Map team/division to `SeasonTeam`.
- Create/update `CoachSeasonAssignment`.
- Reuse existing coach accounts without password reset by default.
- Report assignment results separately from account creation/reuse.
- Add tests for existing-account password preservation.

### Phase 4 - Evaluation Context

- Add `EvaluationCycle.season`.
- Add observation season/team/membership references and snapshot fields.
- Do not backfill production observations unless new observations exist by then and a separate reviewed migration plan is approved.
- Update observation creation/submission services to snapshot context at submission.
- Update player-facing, coach-facing, and staff review read models to use snapshots.
- Preserve submitted snapshots across later roster changes.

### Phase 5 - Read Models And UI

- Add staff roster history views if needed.
- Update player profile/timeline to show season history.
- Update player search, command center, coach review, and metrics filters to use season-aware services.
- Add safe empty states for no current roster.
- Keep templates presentation-only.

### Phase 6 - Production Review And Freeze

- Architecture review.
- Migration review on production copy.
- Security/privacy review.
- Performance review for season/team filters.
- User manual and deployment documentation reconciliation.
- Production readiness and rollback plan.

## 23. Test Strategy

Model/service tests:

- season uniqueness and current/active behavior;
- season-team uniqueness within season;
- player may have memberships in multiple seasons;
- player may have multiple memberships in one season;
- primary membership constraints;
- transfers preserve old membership;
- coach may have multiple assignments;
- coach assignment role does not change account permissions;
- current membership derivation.

Import tests:

- player import creates/reuses season and season team;
- player import creates permanent player once across seasons;
- reimport updates membership deterministically;
- import with new season preserves previous membership;
- transfer import creates new stint;
- ambiguous multi-team import requires review;
- coach import creates assignment;
- coach reimport reuses account and assignment;
- existing coach password is not reset on seasonal reimport.

Analytics tests:

- submitted observation snapshots player season/team/division;
- later roster change does not change old evaluation display;
- evaluation cycle season drives context lookup;
- no roster context is handled safely;
- coach review filters by season/team/division;
- player My Evaluations keeps privacy rules;
- metrics use season-aware filters without changing access rules.

Migration tests:

- schema migration leaves new seasonal tables empty in an empty production-equivalent database;
- defensive verification detects unexpected existing Platform V1 rows before any optional backfill path;
- blank legacy fields do not produce fabricated teams if a non-production backfill helper is later used;
- migration and verification steps are idempotent where practical.

Regression tests:

- existing player import still works during compatibility phase;
- existing coach import still works during compatibility phase;
- account operations unchanged;
- existing evaluation submission/review permissions unchanged unless a phase explicitly changes them.

## 24. Deployment And Rollback Considerations

Deployment should be staged:

1. Deploy schema-only season foundation with compatibility reads intact.
2. Verify production still has zero Platform V1 players, coach profiles, and observations before applying schema.
3. Confirm new seasonal tables are empty after migration.
4. Deploy player import changes after foundation is stable.
5. Deploy coach assignment changes after player seasonal model is proven.
6. Deploy evaluation context changes with snapshot behavior for new submissions.
7. Update UI/read models after data is available.

Rollback considerations:

- Do not remove `Player.team_name` or `Player.division` during early phases.
- Do not make new non-null FKs on existing observations in the first migration.
- Use nullable references and snapshot fields while context behavior is validated.
- Keep compatibility display paths until a full production cycle has passed.
- Back up the database before data migrations.
- Avoid irreversible destructive migrations.

## 25. Risks

- Another environment may contain Platform V1 data even though production is empty; any optional backfill path must be explicit and reviewable.
- Future production data could be created between planning and Phase 1 deployment; pre-migration verification must re-check counts.
- Primary membership constraints can be difficult to enforce perfectly on all databases with nullable dates.
- Coach import currently resets reused coach passwords; this must change before season-aware reimports.
- Existing analytics filters and metrics currently read from `Player.team_name` and `Player.division`.
- Introducing team-scoped permissions too early could block valid evaluators.
- A new `seasons` app creates a shared dependency that needs clear service boundaries.
- Transfer handling requires staff UX decisions, not just schema.

## 26. Open Questions

- What roster statuses are needed for V1?
- Should staff be able to manually edit memberships and assignments in admin only, or through first-class UI?
- How should imported transfer rows explicitly signal transfer versus concurrent membership?
- Should player peer-evaluation scope eventually be limited to same season/team?
- Should the exact one-current-season rule be database-enforced on SQLite, service-enforced, or both?
- Should compatibility writes to `Player.team_name` and `Player.division` happen automatically when primary membership changes, or only during import/service workflows?

## 27. Recommended Next Implementation Phase

Start with Phase 3 - Coach Seasonal Assignment.

Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services.

Before implementing Phase 3, verify that Phase 2 production migration completed successfully and that imported player rows are creating expected season teams and roster memberships.

## 28. Acceptance Criteria

The Seasonal Participation V1 plan is acceptable when:

- permanent players are reused across seasons;
- permanent coach accounts are reused across seasons;
- seasonal team history is preserved;
- future imports do not recreate people unnecessarily;
- historical evaluations retain season/team/division context;
- reimports are deterministic;
- transfers and multi-team cases are handled;
- password behavior for existing coaches is safe;
- existing production data has a migration strategy;
- current `Player.team_name` and `division` have a compatibility plan;
- evaluation cycles and seasons have a defined relationship;
- subsystem ownership is clear;
- migration phases are safe and reversible where practical;
- tests and deployment steps are defined;
- no application code changed during this planning task.
