# 90 Implementation Roadmap

This roadmap is the canonical implementation order for Version 1. It preserves the Version 1 guardrail: build the smallest practical workflow that replaces the current coach assessment spreadsheet.

## Phase 1: Players Foundation

### Goal

Create the shared player identity foundation used by Analytics and future apps.

### Scope

- `players` app
- `players.Player`
- aliases
- source identifiers
- source rows/provenance
- player tags
- player services

### Major Deliverables

- `players` Django app
- `players.Player`
- `players.PlayerAlias`
- `players.PlayerSourceIdentifier`
- `players.PlayerSourceRow`
- `players.PlayerTag`
- `players/services/identity_service.py`
- `players/services/matching_service.py`
- `players/services/import_service.py`
- `players/services/tag_service.py`

### Dependencies

None beyond existing Django project structure.

### Relevant Architecture Documents

- [02 Players](02_players.md)
- [04 Imports](04_imports.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Acceptance Criteria

- Player records can be created and searched.
- Tags can be managed by staff/admin users.
- Source identifiers and source rows preserve imported provenance.
- Matching service can identify exact, high-confidence, ambiguous, and no-match cases.

## Phase 2: Player Import Workflow

### Goal

Import roster/member CSVs into shared player records using conservative matching and merge review.

### Scope

- Staff/admin CSV upload
- Preview
- Mapping
- Conflict handling
- Merge review
- Provenance preservation

### Major Deliverables

- Import Players page in Analytics Command Center
- Import orchestration that calls `players.services.import_service`
- Import preview and row-level errors
- Conflict review workflow

### Dependencies

- Phase 1

### Relevant Architecture Documents

- [02 Players](02_players.md)
- [04 Imports](04_imports.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Acceptance Criteria

- Member-list and roster-detail CSV files can be previewed.
- Matching uses `players.services.matching_service`.
- High-confidence matches enrich existing players.
- Ambiguous matches require staff review.
- Source rows are preserved for auditability.

## Phase 3: Analytics Observation Foundation

### Goal

Create the Analytics observation model and question configuration foundation.

### Scope

- `analytics` app
- Evaluation cycles
- Observation types
- Observation sources
- Evaluator roles
- Question sets and questions
- Observation responses

### Major Deliverables

- `analytics` Django app
- `EvaluationCycle`
- `ObservationType`
- `ObservationSource`
- `EvaluatorRole`
- `ObservationQuestionSet`
- `ObservationQuestion`
- `Observation`
- `ObservationResponse`
- default coach assessment question seed/setup helper

### Dependencies

- Phase 1

### Relevant Architecture Documents

- [03 Analytics](03_analytics.md)
- [05 Coach Assessments](05_coach_assessments.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Acceptance Criteria

- Version 1 supports only `coach_assessment` observations.
- Questions are data-driven, not hard-coded in templates.
- Historical question/response data remains interpretable.
- ObservationResponse supports numeric/text values and future JSON payloads.

## Phase 4: Coach Assessment Workflow

### Goal

Replace the spreadsheet coach questionnaire with a server-rendered Django workflow.

### Scope

- Coach assessment list
- Coach assessment form
- Staff review
- Duplicate-submission prevention

### Major Deliverables

- Coach-facing player list
- Coach-assessment observation form
- Staff review/detail views
- Observation submission service
- Response validation

### Dependencies

- Phase 1
- Phase 3

### Relevant Architecture Documents

- [03 Analytics](03_analytics.md)
- [05 Coach Assessments](05_coach_assessments.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Acceptance Criteria

- Coaches can assess any player they know well enough to assess.
- Multiple coaches can assess the same player in the same cycle.
- The same evaluator cannot submit duplicate `coach_assessment` observations for the same player/cycle.
- Staff can review all submitted observations.

## Phase 5: Draft Context

### Goal

Show draft context without asking coaches to manually enter draft data.

### Scope

- Draft matching
- Draft context display
- Expected vs actual draft comparison

### Major Deliverables

- `analytics.services.draft_service`
- Basic draft-context display on assessment/profile views
- Draft matching summaries

### Dependencies

- Phase 1
- Phase 3
- Existing `drafts` app

### Relevant Architecture Documents

- [06 Draft Integration](06_draft_integration.md)
- [09 Services](09_services.md)

### Acceptance Criteria

- Draft selection data comes from existing `drafts` models/actions.
- Coaches are not asked to type draft selection data.
- Unmatched draft context is shown as missing/unmatched.

## Phase 6: Player Experience

### Goal

Create the practical staff-facing player experience for Version 1.

### Scope

- Player search
- Player Profile page
- Timeline
- Player Comparison

### Major Deliverables

- Player search and filters
- Player Profile page with timeline
- Simple Player Comparison view
- Timeline assembly service
- Comparison service

### Dependencies

- Phase 1
- Phase 3
- Phase 4
- Phase 5

### Relevant Architecture Documents

- [07 Player Experience](07_player_experience.md)
- [08 Reporting](08_reporting.md)
- [09 Services](09_services.md)

### Acceptance Criteria

- Staff can search/filter players.
- Player Profile displays imported context, tags, coach assessments, draft context, and timeline.
- Timeline includes coach assessments, imported player context, and draft context.
- Comparison supports average scores, category scores, coach notes, evaluator count, draft expectation vs actual draft, team/division, and tags.

## Phase 7: Analytics Command Center And Reporting Summaries

### Goal

Provide staff/admin users with the Version 1 Analytics Command Center.

### Scope

- Completion tracking
- Observation summaries
- Import summaries
- Draft matching summaries
- Basic reports

### Major Deliverables

- Analytics Command Center
- Metrics service
- Reporting service summaries
- Server-rendered cards/tables/filters

### Dependencies

- Phases 1-6

### Relevant Architecture Documents

- [07 Player Experience](07_player_experience.md)
- [08 Reporting](08_reporting.md)
- [09 Services](09_services.md)
- [10 Permissions](10_permissions.md)

### Acceptance Criteria

- Staff can view coach completion.
- Staff can view observation counts and recent observations.
- Staff can view import errors/ambiguous matches.
- Staff can navigate to player profiles/timelines.
- Reports remain simple server-rendered summaries and tables.
