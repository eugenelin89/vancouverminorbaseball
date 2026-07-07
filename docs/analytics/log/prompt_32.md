The platform now has multiple completed Version 1 subsystems.

Do NOT implement application code.

Do NOT modify Python files.

Do NOT modify models, services, views, URLs, middleware, templates, or tests.

Your task is to create the top-level architecture index for the entire project.

==================================================
Goal
==================================================

Create the canonical architecture entry point that every engineer should read before working on the repository.

This document should explain:

- what the overall platform is
- how the major subsystems fit together
- ownership boundaries
- dependency direction
- current implementation status
- where future development belongs

This is an architectural overview.

It is NOT a changelog.

It is NOT an implementation guide.

==================================================
Before Writing
==================================================

Review the repository structure.

Read the major architecture and summary documents including:

- docs/account_management/V1_SUMMARY.md
- docs/analytics/V1_SUMMARY.md (or equivalent Analytics summary document if named differently)
- docs/analytics/architecture/
- docs/account_management/
- docs/

Review the major applications:

- players
- analytics
- accounts
- drafts
- pdp

Review current implementation status documents where appropriate.

==================================================
Create
==================================================

Create:

docs/ARCHITECTURE.md

==================================================
Document Structure
==================================================

Use the following structure.

# VCB Platform Architecture

Short introduction.

Explain the purpose of the platform.

Explain that the architecture is intentionally modular and organized around subsystem ownership.

==================================================
Platform Vision
==================================================

Briefly explain:

The platform is intended to become the central baseball operations system.

Examples of capabilities:

- player management
- evaluations
- analytics
- drafts
- recruiting
- account management
- future portals
- future LeagueHub
- future video analysis

==================================================
Core Design Principles
==================================================

Explain the long-lived architectural principles.

Examples:

- canonical ownership
- modular subsystems
- service-oriented architecture
- thin views
- explicit services instead of signals
- authentication separated from player identity
- business rules live in services
- idempotent workflows
- conservative security
- future features should extend existing boundaries rather than bypass them

==================================================
Subsystem Overview
==================================================

Describe every major subsystem.

--------------------------------------------------
Players
--------------------------------------------------

Purpose

Responsibilities

What it owns

What it must not own

Current status

Link to Players documentation if available.

--------------------------------------------------
Analytics
--------------------------------------------------

Purpose

Responsibilities

What it owns

What it must not own

Current status

Reference Analytics V1 summary.

--------------------------------------------------
Account Management
--------------------------------------------------

Purpose

Responsibilities

What it owns

What it must not own

Current status

Reference Account Management V1 summary.

--------------------------------------------------
Drafts
--------------------------------------------------

Describe current scope.

Mention that this subsystem is still evolving.

--------------------------------------------------
PDP (Legacy)
--------------------------------------------------

Explain:

legacy subsystem

temporary coexistence

migration direction

future retirement

==================================================
Ownership Matrix
==================================================

Include a table similar to:

| Capability | Owner |
|------------|-------|
| Player identity | Players |
| Authentication | Accounts |
| User-player relationships | Accounts |
| Player imports | Players |
| Evaluations | Analytics |
| Reports | Analytics |
| Draft workflow | Drafts |
| Login | Accounts |
| Password management | Accounts |
| Timeline | Analytics |
| Comparisons | Analytics |

Add additional rows where appropriate.

==================================================
Dependency Direction
==================================================

Include a dependency diagram.

For example:

Players
    ▲
    │
Accounts

Analytics ─────► Players
Analytics ─────► Accounts

Drafts ─────► Players

PDP (legacy)

Explain:

Cross-subsystem business rules should normally be consumed through services rather than directly manipulating another subsystem's models.

==================================================
Version Status
==================================================

Include a table.

Example:

| Subsystem | Version | Status |
|-----------|---------|--------|
| Players | V1 | Complete |
| Analytics | V1 | Complete / Frozen |
| Account Management | V1 | Complete / Frozen |
| Drafts | Active Development |
| LeagueHub | Planned |
| Video | Planned |

==================================================
Current Platform State
==================================================

Summarize what already exists.

Examples:

- production-ready player identity
- production-ready analytics
- production-ready authentication
- import pipeline
- draft foundation

==================================================
Future Roadmap
==================================================

High-level roadmap only.

Do NOT invent implementation details.

Examples:

Account Management V2

Analytics V2

Drafts expansion

LeagueHub

Video

Player portal

Parent portal

Coach portal

Audit system

==================================================
Documentation Index
==================================================

Provide links to major documentation.

Examples:

Account Management V1

Analytics V1

Analytics Architecture

Implementation Roadmaps

Future subsystem documentation

==================================================
Engineering Expectations
==================================================

Document expectations for future contributors.

Examples:

- respect subsystem ownership
- avoid bypassing service boundaries
- keep views thin
- preserve architectural consistency
- avoid cross-subsystem coupling
- document new subsystem versions
- perform implementation review before freezing a subsystem

==================================================
Writing Style
==================================================

Write for engineers.

Be concise.

Explain architecture rather than implementation.

Use diagrams and tables where appropriate.

Avoid duplicating the subsystem summary documents.

Instead, explain how they fit together.

==================================================
Final Report
==================================================

Report:

- files created

- files modified

- summary of the architecture document

- confirmation that no application code was changed

- confirmation that subsystem implementation remains unchanged