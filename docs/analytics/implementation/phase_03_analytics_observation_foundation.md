# Phase 03: Analytics Observation Foundation

## Purpose

Create the Analytics observation, question, response, source, role, and evaluation-cycle foundation required for Version 1 coach assessments.

## Architecture References

- [03 Analytics](../architecture/03_analytics.md)
- [05 Coach Assessments](../architecture/05_coach_assessments.md)
- [09 Services](../architecture/09_services.md)
- [10 Permissions](../architecture/10_permissions.md)

## Scope

- Create the `analytics` app.
- Add evaluation cycles.
- Add observation types with only `coach_assessment` needed for Version 1.
- Add observation sources for Version 1.
- Add evaluator roles.
- Add question sets/questions.
- Add observation/response models.
- Seed the default coach assessment question set.
- Add core observation/question services.

## Out of Scope

- Coach-facing form UI.
- Staff review UI.
- Import UI.
- Timeline UI.
- Reporting dashboard.
- Non-`coach_assessment` observation workflows.
- Measurements.
- Attachments.
- Provider integrations.
- AI.

## Deliverables

- `analytics` app added to `INSTALLED_APPS`.
- `EvaluationCycle`.
- `ObservationType`.
- `ObservationSource`.
- `EvaluatorRole`.
- `ObservationQuestionSet`.
- `ObservationQuestion`.
- `Observation`.
- `ObservationResponse` with `payload` JSON field.
- Default `coach_assessment` observation type.
- Default Version 1 observation sources.
- Default evaluator roles.
- Default coach assessment question set seed/setup helper.
- Core services and tests.

## Models

- `EvaluationCycle`.
- `ObservationType`.
- `ObservationSource`.
- `EvaluatorRole`.
- `ObservationQuestionSet`.
- `ObservationQuestion`.
- `Observation` referencing `players.Player`.
- `ObservationResponse`.

## Services

- `analytics/services/question_service.py`
  - create/load default question set
  - retrieve active questions for a cycle/type
  - preserve question-set versioning
- `analytics/services/observation_service.py`
  - create draft/submitted observations
  - validate duplicate evaluator/player/cycle/type constraints
  - save responses
  - retrieve observation details

## Views

- Minimal admin or setup-only views if needed.
- No coach-facing or staff review views in this phase unless needed for smoke testing.

## Templates

- None required beyond admin/setup unless implementation needs simple internal scaffolding.

## URLs

- No user-facing URLs required in this phase.

## Admin

- Register evaluation cycles.
- Register observation types.
- Register observation sources.
- Register evaluator roles.
- Register question sets/questions.
- Register observations/responses for staff inspection.

## Migrations

- Initial `analytics` migration for observation foundation models.
- Data migration or setup helper for defaults.

## Tests

- Default `coach_assessment` type exists or can be seeded.
- Default question set can be seeded.
- Question retrieval for cycle/type.
- Observation creation referencing `players.Player`.
- ObservationResponse numeric/text storage.
- ObservationResponse payload field exists and can store JSON.
- Duplicate `coach_assessment` prevention for same evaluator/player/cycle.
- Multiple evaluators can assess the same player/cycle.
- Evaluator role snapshot persists.

## Acceptance Criteria

- Analytics app exists and is installed.
- Observation foundation models are migrated.
- Default coach assessment configuration is available.
- Observation services support creation and response persistence.
- Version 1 supports only `coach_assessment` workflows.
- Tests for this phase pass.

## Risks / Open Questions

- Question-set versioning should remain simple but sufficient for historical interpretability.
- Data seeding strategy should fit the repo's existing migration/test patterns.
- Avoid adding UI for future observation types.

## Implementation Notes


## Phase Review

