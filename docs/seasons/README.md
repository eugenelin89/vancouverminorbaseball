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

Planning only. No application code, models, migrations, services, views, templates, or tests have been implemented for Seasonal Participation V1.

