# Seasons And Roster Participation

This folder contains planning and architecture notes for season-aware player and coach participation.

The VCB platform already has permanent player identity, account identity, evaluations, imports, and account operations. The next production-readiness gap is seasonal participation: the same player or coach can belong to different teams across seasons, while historical evaluations must preserve the team, division, and season context that existed when they were submitted.

## Current Planning Document

- [Seasonal Participation V1 Engineering Plan](implementation/engineering/seasonal_participation_v1.md)

## Ownership Summary

- `players` continues to own permanent player identity, matching, and player import orchestration.
- `accounts` continues to own Django users, account profiles, account roles, provisioning, and login identity.
- Seasonal roster and team concepts should live in a dedicated season/roster bounded context unless implementation discovery proves a smaller existing owner is safer.
- `analytics` should snapshot or link to seasonal context when evaluations are submitted.

## Current Status

Phase 0 planning decisions are complete.

Phase 1 - Season And Roster Foundation is implemented.

Phase 2 - Season-Aware Player Import is implemented.

Phase 3 - Season-Aware Coach Import is implemented.

Phase 4 - Season-Aware Evaluation Context is implemented.

Phase 5 - Season And Roster Operations UI is implemented.

Phase 6 - Production Review And Freeze is complete.

Seasonal Participation V1 status:

```text
Feature Complete
Production Ready
Frozen
```

Verified production state on July 15, 2026:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

Because production is empty for Platform V1 roster/evaluation data, the migration strategy is schema-only first. No fake legacy season, player roster backfill, coach assignment backfill, or observation context backfill is planned for production.

Implemented foundation:

- `Season`
- `SeasonTeam`
- `PlayerRosterMembership`
- `CoachSeasonAssignment`
- transactional domain services
- Django admin registration
- schema-only migration
- tests for current-season, roster membership, coach assignment, compatibility, and admin behavior

Implemented player import integration:

- player imports require a selected active season;
- import batches store the selected season;
- imported rows require team and division roster context;
- player identity matching remains permanent-player based;
- season teams are created or reused through `seasons` services;
- player roster memberships are created or updated through `seasons` services;
- same-season active primary team changes are blocked for manual review;
- prior-season memberships are preserved.

Implemented coach import integration:

- coach imports require a selected active season;
- imported rows require team, division, and an assignment role;
- new coach accounts receive one-time temporary passwords and must change them on first login;
- existing coach accounts are reused without password reset or activation changes;
- existing non-coach accounts remain conflicts;
- season teams are created or reused through `seasons` services;
- coach season assignments are created or updated through `seasons` services;
- prior-season assignments are preserved;
- coaches may have multiple teams and roles in the same season.

Implemented evaluation context:

- evaluation cycles can reference a season;
- new evaluations created against a season-linked cycle resolve the player's roster membership for that season;
- coach evaluations resolve a coach season assignment when one can be determined safely;
- submitted evaluations preserve season, team, division, and coach-assignment snapshots;
- review pages display submitted snapshots instead of live player team fields;
- legacy observations without season context remain readable as `Legacy / No Season`.

Implemented season operations UI:

- staff can list, create, edit, and explicitly set current seasons;
- staff can list, create, and edit season teams;
- staff can list, create, edit, end, transfer, and add additional player roster memberships;
- staff can view player season history;
- staff can list, create, edit, and end coach season assignments;
- staff can view coach season history;
- seasonal assignment changes do not reset passwords, change activation, change platform roles, or grant Django staff/superuser access;
- state-changing operations use staff-only POST workflows and preserve historical records.

Current limitations:

- stricter team-scoped coach permissions and peer team restrictions are deferred.
- dashboards, charts, exports, reports, and strict team-scoped permissions remain deferred.

Frozen status:

- no new V1 features should be added;
- defect fixes, security fixes, production-operability fixes, and documentation corrections are allowed;
- structural changes require a new reviewed phase;
- Platform V2 work must not be mixed into V1 maintenance.

Seasonal operations UI was added in Phase 5 without adding dashboards, reports, exports, APIs, bulk editing, or stricter team-based authorization.
