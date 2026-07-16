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

Current limitations:

- evaluations do not yet store season/team/membership context;
- there are no first-class roster-management pages yet.

Next phase:

- Phase 4 - Evaluation Context.

No evaluation workflow changes were made in Phase 3.
