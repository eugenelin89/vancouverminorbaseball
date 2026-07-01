# Analytics Implementation Handbook

## Purpose

This folder contains the implementation planning documents for the Analytics subsystem.

These documents are used to plan, track, review, and document implementation progress. Unlike the Architecture Handbook, the implementation documents are expected to evolve during development as tasks are completed, lessons are learned, and phase reviews are written.

## Relationship To Architecture

The Architecture Handbook is the source of truth for system design:

- [Analytics Architecture Handbook](../architecture/README.md)

Implementation documents should never redefine architecture. They should translate the approved architecture into actionable engineering work.

If implementation discovers an architectural issue, update the Architecture Handbook first before continuing. After the architecture is corrected, update the relevant implementation phase document to match.

## Implementation Workflow

1. Review architecture.
2. Expand the phase plan.
3. Implement only that phase.
4. Review implementation against architecture.
5. Apply approved fixes.
6. Mark the phase complete.
7. Continue to the next phase.

Never implement multiple phases in a single Codex task unless explicitly instructed.

## Phase Documents

- [Phase 01: Players Foundation](phase_01_players_foundation.md)
- [Phase 02: Player Import Workflow](phase_02_player_import_workflow.md)
- [Phase 03: Analytics Observation Foundation](phase_03_analytics_observation_foundation.md)
- [Phase 04: Coach Assessment Workflow](phase_04_coach_assessment_workflow.md)
- [Phase 05: Draft Context](phase_05_draft_context.md)
- [Phase 06: Player Experience](phase_06_player_experience.md)
- [Phase 07: Command Center and Reporting](phase_07_command_center_reporting.md)

## Phase Completion

A phase is complete only when:

- all in-scope deliverables are implemented
- tests for the phase pass
- the implementation has been reviewed against the relevant architecture documents
- out-of-scope items remain deferred
- the Phase Review section is filled in
