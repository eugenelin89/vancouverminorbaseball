# Phase 03: Analytics Observation Foundation

## Purpose

Create the Analytics observation, question, response, source, role, and evaluation-cycle foundation required for Version 1 coach assessments.

## Architecture References

- [03 Analytics](../architecture/03_analytics.md)
- [05 Coach Assessments](../architecture/05_coach_assessments.md)
- [09 Services](../architecture/09_services.md)
- [10 Permissions](../architecture/10_permissions.md)

## Existing Project Integration

Before implementing this phase, inspect relevant existing project conventions, including:

- model conventions
- timestamp and status-field patterns
- seed/setup helper or data migration patterns
- admin configuration patterns
- service-layer patterns
- test organization and fixtures

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

- [x] `analytics` app added to `INSTALLED_APPS`.
- [x] `EvaluationCycle`.
- [x] `ObservationType`.
- [x] `ObservationSource`.
- [x] `EvaluatorRole`.
- [x] `ObservationQuestionSet`.
- [x] `ObservationQuestion`.
- [x] `Observation`.
- [x] `ObservationResponse` with `payload` JSON field.
- [x] Default `coach_assessment` observation type.
- [x] Default Version 1 observation sources.
- [x] Default evaluator roles.
- [x] Default coach assessment question set seed/setup helper.
- [x] Core services and tests.

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

## Definition of Done

This phase is complete when:

- [x] All deliverables are complete.
- [x] Acceptance criteria are satisfied.
- [x] Tests for the phase pass.
- [x] Documentation is updated if implementation details changed.
- [x] Phase Review is completed.
- [x] `docs/analytics/implementation/STATUS.md` is updated.

## Risks / Open Questions

- Question-set versioning should remain simple but sufficient for historical interpretability.
- Data seeding strategy should fit the repo's existing migration/test patterns.
- Avoid adding UI for future observation types.

## Implementation Notes

Implemented on 2026-07-02.

Phase 3 extended the existing Phase 2 `analytics` app rather than creating a second app. The app was already installed and continued to serve the Phase 2 import UI unchanged.

Created the Analytics observation foundation models:

- `EvaluationCycle`
- `ObservationType`
- `ObservationSource`
- `EvaluatorRole`
- `ObservationQuestionSet`
- `ObservationQuestion`
- `Observation`
- `ObservationResponse`

Created admin registration for all Phase 3 models.

Created:

- `analytics/services/question_service.py`
- `analytics/services/observation_service.py`

Created migrations:

- `analytics/migrations/0001_initial.py`
- `analytics/migrations/0002_seed_observation_defaults.py`

Verification completed:

- `python manage.py makemigrations analytics`
- `python manage.py migrate`
- `python manage.py test analytics`
- `python manage.py test players`
- `python manage.py test`

Review fixes applied on 2026-07-02:

- Required an evaluator when creating coach assessment observations.
- Added `validate_required_responses(observation)` and blocked submitted coach assessments when required active questions are unanswered.
- Validated that observation question sets belong to the selected observation type.
- Tightened `rating_1_5` validation to accept only integer values 1, 2, 3, 4, or 5.
- Made default question setup non-destructive for existing default questions.
- Validated that `EvaluationCycle.coach_assessment_question_set` points to a coach-assessment question set.
- Added a read-only `ObservationResponse` inline under `ObservationAdmin`.

Review-fix verification completed:

- `python manage.py makemigrations analytics --check`
- `python manage.py test analytics`
- `python manage.py test players`
- `python manage.py test`

## Phase Review

### What went well

The observation foundation fit cleanly into the existing minimal Analytics app from Phase 2. No changes were needed to the Phase 2 import views, templates, forms, or URL patterns.

The `players.Player` boundary stayed intact: observations reference `players.Player` directly and no player identity, matching, or import behavior was duplicated in Analytics.

Default coach assessment setup is available both through a migration and through an idempotent question service.

### Challenges

The duplicate coach-assessment constraint needed an `observation_type_key` snapshot because Django conditional unique constraints cannot filter through a related `ObservationType.key`.

The default seed migration intentionally mirrors the setup service with migration-safe model access instead of importing runtime service code.

The review fixes added service-level validation for the Phase 4 submission path without requiring schema changes.

### Technical debt

Question-set lifecycle management is intentionally minimal. Future phases may need explicit workflows for creating a new question-set version, retiring an old version, and assigning a version to an evaluation cycle.

The coach/staff permission model is still future work for Phase 4. Phase 3 stores evaluator role snapshots but does not introduce a full role-permission system.

Default seed data is intentionally duplicated between migration and service code. This keeps migrations safe, but future question changes should be handled as explicit versioned changes rather than edits in both places.

### Architecture changes

None.

### Recommendations for the next phase

Phase 4 should build coach-facing forms on top of `analytics.services.question_service` and `analytics.services.observation_service` rather than hard-coding coach assessment questions.

Phase 4 should define the user-facing edit/submit/reopen rules for draft and submitted observations.
