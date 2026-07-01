# 00 Overview

## Vision

The Analytics subsystem is the first module of VCB's Baseball Intelligence and long-term Player Development Platform.

Version 1 replaces the current Google Sheet-based coach player assessment workflow. The architecture should support future observations, measurements, reporting, timelines, draft context, and player development analytics without increasing Version 1 complexity.

## Version 1 Guardrail

Version 1 should implement only the `coach_assessment` workflow.

The Observation/ObservationResponse architecture should make future observation types possible, but the first implementation should not build UI, workflows, or admin experiences for other observation types yet.

Future-ready architecture is required, but future product surfaces are not. Keep Version 1 focused on:

- coach assessments
- CSV roster imports
- player search
- Player Profile page and timeline
- staff review
- simple Player Comparison
- draft context display

Although the architecture anticipates significant future expansion, Version 1 intentionally delivers only the smallest practical workflow that replaces the existing spreadsheet-based coach assessment process. Future capabilities should build on this foundation incrementally rather than being implemented prematurely.

## Goals

- Give admins and staff a first version of an Analytics Command Center for player observations, imports, draft context, and evaluation trends.
- Give coaches a simple form for evaluating players they know using the current 1-5 scoring rubric.
- Preserve the existing coach assessment categories from the spreadsheet in normalized, queryable data.
- Model coach assessments as observations so future observation types can be added later without redesigning the app.
- Allow questions, categories, scoring methods, and response types to evolve over time without implementing non-coach-assessment workflows in Version 1.
- Pull draft round, selected round, team, and pick context from the existing `drafts` app where possible.
- Support CSV imports for player/member/roster data with conservative matching and merge review.
- Introduce a separate `players` app with `players.Player` as the canonical player identity model for imports, coach assessments, search, timelines, draft matching, reporting, and future expansion.
- Keep the UI server-rendered with Django templates.
- Do not introduce frontend build tooling.

## Decision Support

The Analytics platform exists to organize observations, measurements, historical context, and reports in order to support better decision-making.

It does not replace the judgment of coaches, evaluators, coordinators, or administrators.

Final baseball decisions, including player placement, draft selections, coaching assignments, player development plans, and roster decisions, remain the responsibility of people, not software.

## Long-Term Direction

The architecture should not block future capabilities, but these are not implemented in Version 1.

Future capabilities may include:

- AI-assisted video analysis
- objective metrics
- velocity tracking
- exit velocity tracking
- practice attendance
- workload tracking
- provider integrations
- parent portal
- player portal
- advanced reporting

Future capabilities should build on the service boundaries and models described in this handbook, especially [02 Players](02_players.md), [03 Analytics](03_analytics.md), [07 Player Experience](07_player_experience.md), and [09 Services](09_services.md).
