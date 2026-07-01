# Phase 04: Coach Assessment Workflow

## Purpose

Replace the spreadsheet coach assessment workflow with server-rendered Django pages for coach assessment submission and staff review.

## Architecture References

- [03 Analytics](../architecture/03_analytics.md)
- [05 Coach Assessments](../architecture/05_coach_assessments.md)
- [09 Services](../architecture/09_services.md)
- [10 Permissions](../architecture/10_permissions.md)

## Scope

- Coach-facing player list.
- Coach assessment form.
- Draft/unsubmitted save behavior if needed.
- Submit behavior.
- Staff observation/assessment review.
- Duplicate submission prevention.
- Response validation.
- 1-5 rubric and notes only.

## Out of Scope

- Non-coach-assessment observation types.
- Measurements.
- Attachments.
- AI/video analysis.
- Advanced reporting.
- Advanced comparison UI.
- Parent/player portals.

## Deliverables

- Coach assessment list page.
- Coach assessment form.
- Staff observation detail/review page.
- Services for submission and response validation.
- Permission checks for coach/staff behavior.
- Tests for workflow and permissions.

## Models

- Use Phase 3 analytics models.
- No new models expected unless implementation identifies a small workflow status field need already consistent with architecture.

## Services

- `analytics/services/observation_service.py`
  - create/update draft observation
  - submit observation
  - validate response values
  - enforce duplicate-submission rule
  - retrieve coach's completion status
- `analytics/services/question_service.py`
  - provide ordered coach assessment questions

## Views

- Coach assessment player list view.
- Coach assessment create/edit view.
- Coach assessment submit endpoint/view.
- Staff observation detail/review view.

## Templates

- Coach player list template.
- Coach assessment form template.
- Staff observation detail/review template.
- Shared question/response partials if useful.

## URLs

- `/analytics/assessments/`
- `/analytics/assessments/players/<player_id>/`
- `/analytics/assessments/<observation_id>/`
- `/analytics/observations/<observation_id>/review/`

Exact route names can follow project conventions.

## Admin

- Admin inspection of observations/responses.
- No advanced admin workflow for future observation types.

## Migrations

- None expected beyond Phase 3 unless minor status/field adjustments are required.

## Tests

- Coach can access assessment list.
- Coach can assess any player they know well enough to assess.
- Coach can submit valid 1-5 responses.
- Invalid response values are rejected.
- Freeform notes persist.
- Same evaluator cannot submit duplicate coach assessment for same player/cycle.
- Multiple evaluators can assess same player/cycle.
- Staff can review all observations.
- Non-staff cannot review all observations.

## Acceptance Criteria

- Coaches can complete the Version 1 questionnaire in Django.
- Staff can review submitted assessments.
- The workflow uses configured questions, not hard-coded template text.
- Duplicate-submission rules are enforced.
- Tests for this phase pass.

## Risks / Open Questions

- Exact authentication/coach-role source may need to align with existing users/groups.
- Draft vs submitted edit rules should stay simple.
- UI should remain usable for many questions without adding frontend build tooling.

## Implementation Notes


## Phase Review

