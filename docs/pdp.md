# Player Development Platform

## Architecture Proposal

The PDP app is implemented as a standalone Django app named `pdp` inside the existing project. The design separates long-lived player identity from seasonal evaluations, flexible metrics, development planning, reporting, and future AI/integration concerns.

Core architectural decisions:

- `PlayerProfile` is the durable player identity record across seasons and can link to a Django auth user.
- `Season`, `EvaluationEvent`, `PlayerEvaluation`, and `PlayerMetric` separate event-level assessments from flexible metric storage.
- `EvaluationImport` and `EvaluationImportTemplate` store workbook metadata, reusable mapping configuration, raw previews, and row-level import errors.
- `CoachAssignment` and `ParentChildAccess` handle role-scoped access without coupling permissions to one-off assumptions.
- `PlayerDevelopmentLog`, `DevelopmentGoal`, `ProgressSnapshot`, `DevelopmentRoadmap`, `EndOfSeasonReport`, `DrillResource`, and `PlayerInsight` form the player-development layer.
- `AIAnalysisRun` and `ExternalPerformanceSource` are scaffolding for provider changes, scheduled analyses, and sports-tech integrations.
- Business logic is in services, not templates or model methods, so future API/mobile surfaces can reuse the same backend rules.

## Model Design

Main models:

- `Season`
- `PlayerProfile`
- `CoachAssignment`
- `ParentChildAccess`
- `EvaluationImportTemplate`
- `EvaluationImport`
- `EvaluationEvent`
- `PlayerEvaluation`
- `PlayerMetric`
- `PlayerDevelopmentLog`
- `DevelopmentGoal`
- `AIAnalysisRun`
- `PlayerInsight`
- `ReportTemplate`
- `EndOfSeasonReport`
- `EndOfSeasonReportItem`
- `ProgressSnapshot`
- `DevelopmentRoadmap`
- `DevelopmentRoadmapItem`
- `DrillResource`
- `PlayerDrillAssignment`
- `ExternalPerformanceSource`

This shape keeps the data model extensible:

- new metrics do not require code changes
- imports can evolve by template
- AI output is persisted separately from coach-authored content
- roadmaps, snapshots, and report cards can be regenerated over time
- external sports-tech payloads can be attached without redesigning core evaluation records

## Import Strategy

The import flow lives at `/pdp/import/` and follows a preview-then-map pattern:

1. Upload `.csv` or `.xlsx`
2. Parse workbook into sheet previews and raw row snapshots
3. Map identity fields, metric columns, summary columns, ranking columns, and optional category columns
4. Save optional mapping templates for later reuse
5. Execute import into normalized models while preserving unmapped row data
6. Return onboarding results and row-level errors

Implementation notes:

- `.xlsx` support is implemented without a third-party parser so the app runs with the current dependency set.
- multiple sheets are supported
- metric columns are selected dynamically from the workbook preview
- unmapped fields are preserved on `PlayerEvaluation.unmapped_data`
- player matching checks external ID, email, and full name, and refuses ambiguous merges

## Account Provisioning Strategy

The account provisioning service lives in `pdp/services/accounts.py`.

Rules:

- base username is `lowercase(first_name + last_name)`
- duplicates append a deterministic numeric suffix: `eugenelin`, `eugenelin2`, `eugenelin3`
- initial password is the same string as the generated username
- passwords are always hashed by Django
- `PlayerProfile.must_change_password` forces a first-login password update via middleware
- the import tool can optionally provision accounts during import
- an onboarding report shows player, username, account creation status, and password reset status

## AI Integration Strategy

The AI service layer lives in `pdp/services/ai.py`.

Current implementation:

- `collect_player_analysis_context()`
- `generate_player_summary()`
- `persist_generated_insight()`
- `run_player_ai_analysis()`

This is intentionally provider-agnostic. Today it stores scaffolded constructive summaries so the UI and persistence model are already in place. A future OpenAI or other provider integration can replace the generation function without changing views, templates, or database design.

## Key Pages

- `/pdp/` role-aware entry point
- `/pdp/coach/`
- `/pdp/parent/`
- `/pdp/import/`
- `/pdp/drills/`
- `/pdp/players/<id>/`
- `/pdp/players/<id>/evaluations/`
- `/pdp/players/<id>/logs/`
- `/pdp/players/<id>/goals/`
- `/pdp/players/<id>/insights/`
- `/pdp/players/<id>/report-card/`
- `/pdp/players/<id>/snapshots/`
- `/pdp/players/<id>/roadmap/`

## Setup

1. Run `python manage.py migrate`
2. Create seasons, player profiles, coaches, and parent access records in admin
3. Visit `/pdp/import/` to import evaluations
4. Use `/pdp/coach/` to manage players and `/pdp/drills/` to assign resources

## Tests

Covered areas:

- deterministic username generation and hashed password bootstrapping
- CSV and XLSX workbook parsing
- role-based log visibility rules
- snapshot and roadmap generation

Run with:

```bash
python manage.py test pdp
```

## Extension Points

- replace scaffold AI generation with a real provider
- add API views/serializers for mobile clients
- expand workbook mapping UI with per-column type metadata
- add charting/HTMX fragments for richer trend exploration
- add PDF export for report cards and progress summaries
