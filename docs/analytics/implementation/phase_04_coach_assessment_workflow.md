# Phase 04: Coach Assessment Workflow

## Purpose

Replace the spreadsheet coach assessment workflow with server-rendered Django pages for coach assessment submission and staff review.

## Architecture References

- [03 Analytics](../architecture/03_analytics.md)
- [05 Coach Assessments](../architecture/05_coach_assessments.md)
- [09 Services](../architecture/09_services.md)
- [10 Permissions](../architecture/10_permissions.md)

## Existing Project Integration

Before implementing this phase, inspect relevant existing project conventions, including:

- authentication and permission patterns
- class-based view patterns
- form validation patterns
- messages and redirect conventions
- template/layout conventions
- service-layer patterns for workflow actions
- test organization for view and permission tests

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

- [x] Coach assessment list page.
- [x] Coach assessment form.
- [x] Staff observation detail/review page.
- [x] Services for submission and response validation.
- [x] Permission checks for coach/staff behavior.
- [x] Tests for workflow and permissions.

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

## Definition of Done

This phase is complete when:

- [x] All deliverables are complete.
- [x] Acceptance criteria are satisfied.
- [x] Tests for the phase pass.
- [x] Documentation is updated if implementation details changed.
- [x] Phase Review is completed.
- [x] `docs/analytics/implementation/STATUS.md` is updated.

## Risks / Open Questions

- Exact authentication/coach-role source may need to align with existing users/groups.
- Draft vs submitted edit rules should stay simple.
- UI should remain usable for many questions without adding frontend build tooling.

## Implementation Notes

Implemented on 2026-07-03.

Created a dynamic coach assessment workflow on top of the Phase 3 observation foundation. Questions are loaded from `ObservationQuestionSet` / `ObservationQuestion` through `question_service`; templates do not hard-code question text.

Created:

- `analytics/assessment_forms.py`
- `analytics/services/coach_assessment_service.py`
- `analytics/services/permissions.py`
- `analytics/templates/analytics/assessment_list.html`
- `analytics/templates/analytics/assessment_form.html`
- `analytics/templates/analytics/assessment_detail.html`
- `analytics/templates/analytics/assessment_review.html`
- `analytics/templates/analytics/observation_review_list.html`
- `analytics/templates/analytics/_assessment_question.html`
- `analytics/templates/analytics/_assessment_status_badge.html`

Updated:

- `analytics/views.py`
- `analytics/urls.py`
- `analytics/tests.py`

Verification completed:

- `python manage.py makemigrations analytics --check`
- `python manage.py test analytics`
- `python manage.py test players`
- `python manage.py test`

## Phase Review

### What went well

The dynamic form worked cleanly with the Phase 3 question and observation services.

The existing Phase 2 import UI remained intact while the assessment workflow was added to the same Analytics app.

The workflow uses `players.Player` directly and does not duplicate player identity or import logic.

### Challenges

There is no dedicated coach role model yet, so Phase 4 follows the architecture guidance that authenticated users may submit coach assessments while staff/admin users can review all observations.

Draft save and submit use the same dynamic form with different required-field behavior, so the view must instantiate the form based on the POST action.

### Technical debt

The coach assessment list uses a simple active-cycle selection and basic filters. A richer cycle picker can be added later if needed.

The staff review workflow is intentionally basic and does not include reporting, comparison, exports, or timelines.

### Architecture changes

None.

### Recommendations for the next phase

Phase 5 should consume submitted observations as read-only context and should not add reporting/timeline behavior unless that phase explicitly calls for it.
