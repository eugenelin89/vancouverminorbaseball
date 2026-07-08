# VCB Platform Architecture

The VCB platform is a modular Django system for baseball operations. It is organized around subsystem ownership so player identity, account identity, analytics, drafts, and future operational tools can evolve without collapsing into one tightly coupled application.

This document is the top-level architecture entry point. Engineers should read it before changing subsystem behavior, adding new workflows, or introducing cross-app dependencies.

## Platform Vision

The platform is intended to become the central baseball operations system for Vancouver Community Baseball.

Long-term capabilities may include:

- player management
- player imports and identity matching
- evaluations and coach assessments
- analytics, reporting, timelines, and comparisons
- draft preparation and draft execution
- account management and user-player relationships
- recruiting history and reports
- player, parent, and coach portals
- LeagueHub operations
- video and future AI-assisted analysis

The architecture should support that expansion by keeping each subsystem's ownership clear.

## Core Design Principles

- Canonical ownership matters. Each core concept has one owning subsystem.
- Subsystems are modular. Apps should collaborate through service boundaries rather than owning each other's rules.
- Business rules live in services. Views, templates, middleware, and forms should remain thin.
- Explicit services are preferred over signals for account, import, linking, and workflow behavior.
- Authentication is separate from player identity. Django `User` belongs to account identity; `players.Player` belongs to baseball identity.
- Workflows should be idempotent where retries are expected, especially imports and provisioning.
- Security defaults should be conservative, especially for authentication and account provisioning.
- Future features should extend existing boundaries rather than bypass them.
- New subsystem versions should be documented before or alongside implementation.

## Subsystem Overview

### Players

Purpose:

`players` owns canonical player identity for the platform.

Responsibilities:

- canonical `players.Player` records
- player aliases
- source identifiers
- player source rows and provenance
- player tags
- player imports, matching, conflict resolution, and merge/update behavior

What it owns:

- player identity data
- player import business logic
- reusable player matching infrastructure

What it must not own:

- Django login users
- account roles
- user-player auth relationships
- Analytics observations
- draft workflow

Current status:

V1 complete as part of the Analytics foundation.

Documentation:

- [Analytics Architecture: Players](analytics/architecture/02_players.md)
- [Analytics Architecture: Imports](analytics/architecture/04_imports.md)

### Analytics

Purpose:

`analytics` owns baseball intelligence workflows: observations, coach assessments, staff review, player experience, draft context, command center summaries, metrics, timelines, comparisons, and reporting surfaces.

Responsibilities:

- observation architecture
- coach assessment workflow
- staff observation review
- player search and profile views
- player timeline read models
- player comparison read models
- draft context read models
- command center metrics and reporting read models

What it owns:

- observations and responses
- evaluation cycles
- question sets and questions
- evaluator snapshots
- analytics metrics, timelines, comparisons, and reports

What it must not own:

- canonical player identity
- player import business logic
- account provisioning
- account roles
- draft selection workflow

Current status:

V1 complete. Implementation status records Phases 1-7 as complete.

Documentation:

- [Analytics README](analytics/README.md)
- [Analytics Architecture Handbook](analytics/architecture/README.md)
- [Analytics Implementation Status](analytics/implementation/STATUS.md)

### Account Management

Purpose:

`accounts` owns platform login-account identity and account metadata.

Responsibilities:

- `AccountProfile`
- account roles
- user-player links
- account permission helpers
- username, email, and password account services
- account provisioning from committed player imports
- platform login/logout/password-change routes
- forced password-change middleware
- account landing URL behavior
- staff Account Operations dashboard/list/detail
- manual account creation and player-account creation
- account lifecycle, link management, operational password reset, and safe bulk account actions

What it owns:

- authentication-facing account metadata
- user-player relationship records
- account provisioning rules
- account auth redirects and forced password-change enforcement

What it must not own:

- canonical player identity
- player import parsing/matching
- Analytics observations
- draft workflows
- PDP migration behavior

Current status:

V1 complete and frozen, including Platform V1 Account Operations Phase F production hardening/freeze review.

Documentation:

- [Account Management V1 Summary](account_management/V1_SUMMARY.md)
- [Account Management V1 Engineering Plan](account_management/implementation/account_management_v1.md)

### Drafts

Purpose:

`drafts` owns live player draft workflows across seasons and divisions.

Current scope:

- draft room creation
- player import into draft rooms
- draft command center
- player assignment and movement
- trade desk
- undo/revert actions
- draft status changes
- draft action audit records

Current status:

Active. The app exists and has a service layer, but it is still evolving relative to the completed V1 subsystem freezes.

Documentation:

- [Drafts README](../drafts/README.md)

### PDP (Legacy)

Purpose:

`pdp` is the legacy player development subsystem.

Current role:

- remains installed
- keeps existing PDP routes, middleware, views, and behavior available
- coexists temporarily with the platform-forward `players`, `analytics`, and `accounts` architecture

Migration direction:

New architecture should not depend on `pdp.PlayerProfile` as canonical player identity. Future PDP work should migrate toward `players.Player` and Account Management boundaries.

Future retirement:

PDP retirement requires a dedicated migration and regression plan. Do not remove or bypass PDP behavior casually.

Documentation:

- [PDP Notes](pdp.md)

## Ownership Matrix

| Capability | Owner |
| --- | --- |
| Player identity | Players |
| Player aliases | Players |
| Player source identifiers | Players |
| Player imports | Players |
| Player matching | Players |
| Authentication | Accounts |
| Login/logout/password change | Accounts |
| Account metadata | Accounts |
| Account roles | Accounts |
| User-player relationships | Accounts |
| Account provisioning | Accounts |
| Evaluations | Analytics |
| Coach assessments | Analytics |
| Observations and responses | Analytics |
| Evaluator snapshots | Analytics |
| Reports and metrics | Analytics |
| Player timeline | Analytics |
| Player comparison | Analytics |
| Draft context read models | Analytics |
| Draft workflow | Drafts |
| Draft selections/actions | Drafts |
| Legacy PDP workflows | PDP |

## Dependency Direction

```text
        Players
          ▲
          │
      Accounts

Analytics ─────► Players
Analytics ─────► Accounts

Drafts ────────► Players

PDP (legacy, transitionary)
```

Dependency guidance:

- Cross-subsystem business rules should normally be consumed through services.
- Do not directly manipulate another subsystem's models when an owning service exists.
- `players` owns player identity and imports.
- `accounts` owns account identity and user-player relationships.
- `analytics` may consume `players` and `accounts`, but must not own their business rules.
- `drafts` may reference player identity, but draft workflow remains in `drafts`.
- PDP is legacy and should not become the dependency target for new platform work.

## Version Status

| Subsystem | Version | Status |
| --- | --- | --- |
| Players | V1 | Complete |
| Analytics | V1 | Complete |
| Account Management | V1 | Complete / Frozen |
| Drafts | Active | Active development |
| PDP | Legacy | Transitionary |
| LeagueHub | Planned | Planned |
| Video | Planned | Planned |

## Current Platform State

The platform currently has:

- production-ready canonical player identity foundation
- production-ready player import and matching workflow
- production-ready Analytics V1 workflow
- production-ready Account Management V1 foundation
- production-ready staff-facing Account Operations
- account provisioning from player imports
- forced password-change account flow
- staff-only Analytics command center and reporting tables
- player search, profile, timeline, and comparison surfaces
- read-only draft context from submitted observations
- an active draft workflow app
- legacy PDP coexistence

## Future Roadmap

High-level future work should be added through documented subsystem versions. Do not invent cross-cutting implementation details without updating the relevant architecture documents.

Likely future areas:

- Account Management V2
- Analytics V2
- Drafts expansion
- LeagueHub
- Video
- player portal
- parent portal
- coach portal
- audit system
- PDP retirement and migration planning

## Documentation Index

Start here:

- [Platform Architecture](ARCHITECTURE.md)

Account Management:

- [Account Management V1 Summary](account_management/V1_SUMMARY.md)
- [Account Management V1 Engineering Plan](account_management/implementation/account_management_v1.md)
- [Account Management Engineering Plans](account_management/implementation/engineering/)

Analytics:

- [Analytics README](analytics/README.md)
- [Analytics Architecture Handbook](analytics/architecture/README.md)
- [Analytics Implementation Handbook](analytics/implementation/README.md)
- [Analytics Implementation Status](analytics/implementation/STATUS.md)
- [Analytics Local Development](analytics/local_development.md)

Prompts and archives:

- [Prompt Archive](prompts/README.md)
- [Archived Legacy Prompts](archive/prompts/README.md)

Drafts:

- [Drafts README](../drafts/README.md)

PDP:

- [PDP Notes](pdp.md)
- [PDP Import Discovery Log](pdp_import_discovery_log.md)

Future documentation areas:

- LeagueHub architecture
- Video architecture
- portal architecture
- audit architecture

## Engineering Expectations

Future contributors should:

- respect subsystem ownership
- avoid bypassing service boundaries
- keep views thin and templates presentational
- keep business logic in owning services
- avoid cross-subsystem model manipulation when services exist
- preserve conservative security defaults
- document new subsystem versions before or alongside implementation
- update the relevant architecture handbook when significant decisions change
- perform implementation review before freezing a subsystem version
- keep legacy PDP coexistence stable until a dedicated retirement plan exists
