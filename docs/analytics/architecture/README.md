# Analytics Architecture Handbook

## Purpose

This folder contains the authoritative architecture specification for the Analytics subsystem.

Implementation prompts should reference these documents instead of embedding architecture into every Codex prompt. These documents are organized by business domain so future work can load only the context needed for the current implementation task.

## Reading Order

Recommended reading order:

1. [00 Overview](00_overview.md)
2. [01 Design Principles](01_design_principles.md)
3. [02 Players](02_players.md)
4. [03 Analytics](03_analytics.md)
5. [04 Imports](04_imports.md)
6. [05 Coach Assessments](05_coach_assessments.md)
7. [06 Draft Integration](06_draft_integration.md)
8. [07 Player Experience](07_player_experience.md)
9. [08 Reporting](08_reporting.md)
10. [09 Services](09_services.md)
11. [10 Permissions](10_permissions.md)
12. [90 Implementation Roadmap](90_implementation_roadmap.md)

Use [GLOSSARY.md](GLOSSARY.md) as the canonical vocabulary reference.

## Using These Documents With Codex

For implementation tasks:

1. Read this README.
2. Read [90_implementation_roadmap.md](90_implementation_roadmap.md).
3. Read only the architecture documents relevant to the current implementation phase.

Do not load every document unless making cross-cutting architectural changes.

## Phase Context Sets

### Phase 1: Players Foundation

- [02 Players](02_players.md)
- [04 Imports](04_imports.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Phase 2: Player Import Workflow

- [02 Players](02_players.md)
- [04 Imports](04_imports.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Phase 3: Analytics Observation Foundation

- [03 Analytics](03_analytics.md)
- [05 Coach Assessments](05_coach_assessments.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Phase 4: Coach Assessment Workflow

- [03 Analytics](03_analytics.md)
- [05 Coach Assessments](05_coach_assessments.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Phase 5: Draft Context

- [06 Draft Integration](06_draft_integration.md)
- [09 Services](09_services.md)

### Phase 6: Player Experience

- [07 Player Experience](07_player_experience.md)
- [08 Reporting](08_reporting.md)
- [09 Services](09_services.md)

### Phase 7: Command Center and Reporting

- [07 Player Experience](07_player_experience.md)
- [08 Reporting](08_reporting.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

Implementation prompts should reference only the architecture documents needed for the current task.
