# Phase 4 Engineering Plan: Coach Assessment Workflow

> Historical implementation record.
> This document preserves the plan and decisions used during implementation. For current behavior, use [../../../ARCHITECTURE.md](../../../ARCHITECTURE.md), [../../../USER_MANUAL.md](../../../USER_MANUAL.md), and the relevant subsystem summaries.

## Overview

Phase 4 implements the Version 1 coach assessment workflow on top of the completed Phase 3 observation foundation.

Phase 1, Phase 2, and Phase 3 are complete. Phase 4 should use:

- `players.Player` as the canonical player reference.
- `analytics.services.question_service` for configured question sets and ordered questions.
- `analytics.services.observation_service` for observation creation, response persistence, duplicate prevention, and submission validation.

Mandatory boundaries:

- Do not hard-code coach assessment questions in templates.
- Do not duplicate player identity, matching, or import logic.
- Do not implement reporting, timelines, draft context, measurements, attachments, AI, or future observation workflows.
- Do not migrate PDP workflows.
- Do not redesign Phase 3 models unless implementation discovers a small required workflow fix.

Phase 4 should produce server-rendered Django pages that replace the spreadsheet-based coach assessment process:

- Coaches can choose players and complete the Version 1 coach assessment questionnaire.
- Coaches can save drafts.
- Coaches can submit complete assessments.
- Staff can review submitted observations.

## Files To Create

Forms:

- `analytics/assessment_forms.py`
  - dynamic coach assessment form classes/helpers.
  - Keep separate from existing `analytics/forms.py` if useful to avoid mixing import forms and assessment forms.

Services:

- `analytics/services/coach_assessment_service.py`
  - thin workflow helpers for Phase 4 if needed.
  - Should call `question_service` and `observation_service`.
  - Must not own generic observation persistence already implemented in `observation_service`.

Templates:

- `analytics/templates/analytics/assessment_list.html`
- `analytics/templates/analytics/assessment_form.html`
- `analytics/templates/analytics/assessment_detail.html`
- `analytics/templates/analytics/assessment_review.html`
- Optional partials:
  - `analytics/templates/analytics/_assessment_question.html`
  - `analytics/templates/analytics/_assessment_status_badge.html`

Tests:

- Continue using `analytics/tests.py` unless implementation decides the file has become too large.
- A later cleanup can split import tests, observation foundation tests, and workflow tests into a package.

## Files To Modify

Existing Analytics files:

- `analytics/views.py`
  - add coach assessment list/form/detail/review views.
  - Preserve existing import views.
- `analytics/urls.py`
  - add Phase 4 routes while preserving Phase 2 import routes.
- `analytics/templates/analytics/base.html`
  - optional navigation additions only if useful and consistent with existing PDP shell.
- `analytics/tests.py`
  - add workflow, form, and permission tests.

Existing services:

- `analytics/services/observation_service.py`
  - add small helpers only if Phase 4 needs them, such as get/create draft or reopen.
  - Keep existing validation behavior.
- `analytics/services/question_service.py`
  - add query helpers only if needed, such as active coach assessment cycles/questions.

Documentation after implementation:

- `docs/analytics/implementation/STATUS.md`
- `docs/analytics/implementation/phase_04_coach_assessment_workflow.md`
- `docs/analytics/implementation/engineering/phase_04_coach_assessment_workflow.md`

Do not modify architecture documents unless implementation discovers a genuine architecture issue.

## Coach-Facing Workflow

### Entry Point

Route:

- `/analytics/assessments/`

Purpose:

- Shows authenticated coach/staff users the list of active players they may assess.
- Version 1 allows authenticated coaches to evaluate any player they know.

Recommended page content:

- Current active evaluation cycle selector or default active coach assessment cycle.
- Search/filter players by name, division, team.
- Player list with assessment status for the current evaluator/cycle:
  - Not started
  - Draft
  - Submitted
  - Reopened, if used
- Action links:
  - Start assessment
  - Continue draft
  - View submitted assessment

Player source:

- Query `players.Player.objects.filter(is_active=True)`.
- Do not use `pdp.PlayerProfile`.
- Do not implement team assignment restrictions in Phase 4 unless explicitly required later.

Evaluation cycle source:

- Use existing `EvaluationCycle` records.
- If no active coach assessment cycle exists, staff/admin should create one in admin for Phase 4.
- Phase 4 may include a simple fallback that uses the latest active `EvaluationCycle(cycle_type="Coach Assessment")`, but should not create a full cycle management UI.

### Assessment Form

Routes:

- `/analytics/assessments/players/<int:player_id>/`
- Optional edit route: `/analytics/assessments/<int:observation_id>/`

Purpose:

- Render dynamic questions from the configured `ObservationQuestionSet`.
- Allow draft save.
- Allow submit when required responses are complete.

Behavior:

1. Authenticated evaluator opens a player assessment.
2. View resolves the current coach assessment cycle and question set.
3. View loads an existing draft/reopened observation for the evaluator/player/cycle if one exists.
4. If no observation exists, view creates or prepares a draft observation.
5. Form renders active questions grouped by category.
6. Coach can save draft.
7. Coach can submit when required rating questions are answered.
8. On submit, use `observation_service.submit_observation()` so required-response validation is centralized.

Submitted observations:

- Coaches should view their submitted observation but should not edit it by default.
- Staff/admin may reopen submitted observations if Phase 4 implements reopen.
- Reopen may be implemented as status change to `reopened`; keep it staff-only and simple.

## Staff Review Workflow

### Staff Observation List

Route:

- `/analytics/observations/review/`

Purpose:

- Allows staff/admin users to review submitted coach assessments.

Recommended filters:

- Evaluation cycle.
- Player search.
- Evaluator search.
- Evaluator role.
- Status.

Keep the list practical:

- Use pagination.
- Use `select_related` for player, evaluator, cycle, source, type.
- Do not build reporting, charts, summaries, comparison, or timeline features.

### Staff Observation Detail

Route:

- `/analytics/observations/<int:observation_id>/review/`

Purpose:

- Staff can inspect one observation and its responses.

Recommended detail content:

- Player name.
- Evaluation cycle.
- Evaluator.
- Evaluator role snapshot.
- Status/submitted timestamp.
- Questions and responses grouped by category.
- Freeform notes response.

Staff actions:

- Optional Phase 4 action: reopen submitted observation.
- Do not implement approval workflow, scoring reports, exports, comparison, or analytics dashboards.

## Forms Design

### Dynamic CoachAssessmentForm

Recommended location:

- `analytics/assessment_forms.py`

Constructor inputs:

- `question_set`
- optional `observation`
- optional `data`

Behavior:

- Load active questions from `question_service.get_active_questions(question_set)`.
- Create one form field per active question.
- Field names should use stable question keys or IDs.

Recommended field naming:

- `question_<question.id>`

Reason:

- Question keys are stable, but IDs make response lookup unambiguous for the exact question set version.

Rating fields:

- Use `forms.TypedChoiceField`.
- Choices:
  - `("", "---------")` for optional only.
  - `1`, `2`, `3`, `4`, `5` with rubric labels.
- Coerce to `int`.
- Required based on `ObservationQuestion.is_required`.

Text fields:

- Use `forms.CharField(widget=forms.Textarea, required=question.is_required)`.

Initial values:

- If editing an observation, prefill existing `ObservationResponse` values.
- Rating responses read from `numeric_value`.
- Text responses read from `text_value`.

Validation:

- Let the form validate field presence and value type.
- Let `observation_service.save_observation_responses()` remain the source of truth for response persistence/validation.
- Submit action should call `submit_observation()` to enforce required response completeness again.

Output:

- Provide a method such as `response_payload()` returning:

```python
[
    {"question": question, "value": cleaned_value}
]
```

Avoid storing raw form-specific structures in services.

### Cycle Selection Form

If needed:

- Small GET form with `cycle` choice.
- Choices limited to active coach assessment cycles.

Keep this optional in Phase 4. Do not build cycle management UI.

## Dynamic Question Rendering Strategy

Templates must not hard-code question text.

Recommended context:

- `question_groups`: ordered list of category groups.
- Each group contains:
  - category name.
  - ordered question/form-field pairs.

View/form responsibility:

- Build `question_groups` from `form.questions` or a helper.
- Template loops groups and fields.

Example rendering shape:

```django
{% for group in question_groups %}
  <section>
    <h2>{{ group.category }}</h2>
    {% for item in group.questions %}
      {% include "analytics/_assessment_question.html" with question=item.question field=item.field %}
    {% endfor %}
  </section>
{% endfor %}
```

Rubric display:

- Pull labels from `question_set.rubric`.
- Display once near the form header or as compact helper text near rating fields.

Do not hard-code the current 26 questions in templates.

## Draft / Submitted / Edit / Reopen Rules

### Draft

- Coaches can create one draft coach assessment per player/cycle.
- Coaches can edit their own draft.
- Drafts may be saved with incomplete required responses.
- Draft save should not call `submit_observation()`.

### Submitted

- Coaches can submit only when required active questions are answered.
- Submitted observations get `submitted_at`.
- Coaches can view their own submitted observations.
- Coaches cannot edit submitted observations by default.

### Duplicate Prevention

- Use Phase 3 uniqueness and service validation.
- Existing rule: one `coach_assessment` per evaluator/player/cycle/type.
- Multiple evaluators can assess the same player/cycle.

Implementation detail:

- A coach opening a submitted assessment should be routed to detail/read-only view.
- A coach opening an existing draft should edit the draft.
- A coach trying to create a second assessment should be redirected to the existing observation.

### Reopen

Staff/admin may reopen a submitted observation if Phase 4 includes this action.

Recommended simple rule:

- Staff-only POST action sets status to `reopened`.
- Reopened observations are editable by the original evaluator.
- Resubmitting sets status back to `submitted` and updates `submitted_at`.

If this creates too much complexity, defer reopen implementation but make submitted read-only.

## Permissions

Follow repository patterns:

- Use `LoginRequiredMixin`.
- Use `UserPassesTestMixin` for staff-only views.
- Use service/helper functions for reusable permission checks if useful.

Recommended helpers:

- `analytics/services/permissions.py`
  - `can_submit_coach_assessment(user)`.
  - `can_edit_observation(user, observation)`.
  - `can_review_observations(user)`.
  - `can_reopen_observation(user, observation)`.

Version 1 rules:

- Any authenticated non-staff coach/user can access coach assessment list and assess any active player.
- Staff/admin can also submit assessments if needed.
- Staff/admin can review all observations.
- Non-staff users cannot access staff review pages.
- Coaches can view/edit their own draft/reopened observations.
- Coaches can view their own submitted observations.
- Coaches cannot view or edit another evaluator's observation.

Authentication ambiguity:

- There is no dedicated coach role model in the current repo.
- For Phase 4, treat authenticated users as allowed coach assessment submitters unless a more specific existing permission pattern is identified during implementation.
- Do not create a full role/group system in Phase 4.

Sensitive data:

- Do not display source-row raw import data, addresses, guardian/contact data, medical notes, phone numbers, or emails on coach assessment screens.
- Player list should show only player name and basic baseball context such as division/team if needed.

## Views

Recommended class-based views in `analytics/views.py`.

### CoachAssessmentListView

Route:

- `/analytics/assessments/`

Access:

- authenticated users.

Responsibilities:

- Resolve selected/current evaluation cycle.
- List active `players.Player` records.
- Annotate or attach current user's observation status per player for the selected cycle.
- Render player search/filter UI if simple.

### CoachAssessmentEditView

Route:

- `/analytics/assessments/players/<int:player_id>/`
- Optional: `/analytics/assessments/<int:observation_id>/edit/`

Access:

- authenticated users for own draft/reopened observations.

Responsibilities:

- Resolve player, cycle, observation type, question set.
- Get or create draft observation through service helper.
- Instantiate dynamic `CoachAssessmentForm`.
- Save draft or submit based on POST action.
- Redirect with messages.

POST actions:

- `save_draft`
- `submit`

### CoachAssessmentDetailView

Route:

- `/analytics/assessments/<int:observation_id>/`

Access:

- owner evaluator or staff/admin.

Responsibilities:

- Display a read-only assessment.
- Useful after submit.

### StaffObservationReviewListView

Route:

- `/analytics/observations/review/`

Access:

- staff/admin only.

Responsibilities:

- List observations for staff review.
- Filter by cycle/status/player/evaluator if simple.

### StaffObservationReviewDetailView

Route:

- `/analytics/observations/<int:observation_id>/review/`

Access:

- staff/admin only.

Responsibilities:

- Show one observation and responses grouped by question category.
- Optional staff-only reopen POST action.

## Templates

Use `analytics/base.html`, which already extends the PDP shell.

Templates:

- `assessment_list.html`
  - player list/search/status/actions.
- `assessment_form.html`
  - dynamic grouped questions, rubric, draft/submit buttons.
- `assessment_detail.html`
  - read-only coach view of submitted/draft observation.
- `assessment_review.html`
  - staff review detail.
- Optional partials:
  - `_assessment_question.html`
  - `_assessment_status_badge.html`

UI constraints:

- Keep it server-rendered.
- Do not introduce frontend build tooling.
- Keep the form usable for the current question count.
- Avoid showing sensitive import/source-row data.

## URLs

Modify `analytics/urls.py`.

Recommended route names:

- `analytics:assessment-list`
- `analytics:assessment-player`
- `analytics:assessment-detail`
- `analytics:assessment-edit`
- `analytics:observation-review-list`
- `analytics:observation-review-detail`

Recommended paths:

```python
path("assessments/", CoachAssessmentListView.as_view(), name="assessment-list")
path("assessments/players/<int:player_id>/", CoachAssessmentEditView.as_view(), name="assessment-player")
path("assessments/<int:observation_id>/", CoachAssessmentDetailView.as_view(), name="assessment-detail")
path("assessments/<int:observation_id>/edit/", CoachAssessmentEditView.as_view(), name="assessment-edit")
path("observations/review/", StaffObservationReviewListView.as_view(), name="observation-review-list")
path("observations/<int:observation_id>/review/", StaffObservationReviewDetailView.as_view(), name="observation-review-detail")
```

Preserve existing import URLs.

## Services Needed

Prefer small additions rather than broad new abstractions.

### `analytics/services/coach_assessment_service.py`

Useful helper functions:

- `get_active_coach_assessment_cycle()`
- `list_players_for_assessment(query=None, division=None, team=None)`
- `get_existing_coach_assessment(player, cycle, evaluator)`
- `get_or_create_draft_coach_assessment(player, cycle, evaluator)`
- `assessment_status_for_players(players, cycle, evaluator)`
- `responses_by_question(observation)`
- `group_questions_for_display(question_set)`

These helpers should call:

- `question_service.get_question_set_for_cycle()`
- `question_service.get_active_questions()`
- `observation_service.create_coach_assessment_observation()`
- `observation_service.save_observation_responses()`
- `observation_service.submit_observation()`

Do not duplicate generic observation validation in this service.

### `analytics/services/permissions.py`

If useful, add simple permission helpers:

- `can_submit_coach_assessment(user)`
- `can_view_observation(user, observation)`
- `can_edit_observation(user, observation)`
- `can_review_observations(user)`
- `can_reopen_observation(user, observation)`

Keep these functions small and aligned with Phase 4 rules.

### Existing services

`observation_service.py` may need:

- `get_or_create_draft_observation(...)`
- `reopen_observation(observation, actor)`

Add only if needed.

## Migration Strategy

No migrations are expected.

Phase 4 should use existing Phase 3 models and fields.

Run during implementation:

- `python manage.py makemigrations analytics --check`

Create a migration only if implementation discovers a small, necessary field/constraint change that is consistent with the architecture. If a larger model change is needed, stop and reassess before implementation continues.

## Tests To Write

Follow current app-level `analytics/tests.py` convention unless the file becomes impractical.

### Form tests

- Dynamic form renders one field per active question.
- Rating questions render 1-5 choices from configured questions.
- Text question renders textarea field.
- Existing responses prefill form initial values.
- Invalid rating values are rejected.
- Required rating questions are required on submit.
- Draft save can persist partial responses if implementation supports partial save.

### Coach workflow tests

- Authenticated user can access assessment list.
- Unauthenticated user is redirected to login.
- Player list uses `players.Player`.
- Coach can open assessment form for any active player.
- Questions come from `ObservationQuestion`, not hard-coded template text.
- Coach can save draft.
- Coach can reopen/continue own draft.
- Coach can submit complete assessment.
- Submitted assessment records evaluator, evaluator role snapshot, cycle, source, and responses.
- Missing required responses block submit.
- Same evaluator cannot create duplicate assessment for same player/cycle.
- Multiple evaluators can assess same player/cycle.
- Coach cannot edit submitted observation unless reopened.
- Coach cannot view/edit another evaluator's observation.

### Staff review tests

- Staff can access observation review list.
- Non-staff cannot access staff review list.
- Staff can view submitted observation detail.
- Staff review displays grouped questions and responses.
- Staff can reopen submitted observation if reopen is implemented.
- Reopened observation becomes editable by original evaluator if reopen is implemented.

### Regression tests

- Existing Phase 2 import UI tests still pass.
- Existing Phase 3 observation foundation tests still pass.
- `python manage.py test analytics` passes.
- `python manage.py test players` passes.
- `python manage.py test` passes.

## Risks / Open Questions

- There is no dedicated coach role source. The recommended Phase 4 rule treats authenticated users as coach assessment submitters and staff/admin as reviewers.
- Evaluation cycle selection may need user-friendly behavior if no active cycle exists. Recommendation: show a clear staff-facing message and do not auto-create cycles from the coach UI.
- Draft saving partial required responses needs careful form handling because submitted validation must remain strict.
- Reopen rules can expand scope. Implement only a small staff-only reopen action if straightforward; otherwise defer and keep submitted observations read-only.
- The existing `analytics/tests.py` may become large. Splitting tests is a cleanup decision, not required for Phase 4.
- The UI must remain usable for many questions without adding frontend tooling.

## Recommended Implementation Sequence

1. Re-read Phase 4 architecture docs, permissions, Phase 3 engineering notes, and existing Analytics views/templates.
2. Inspect `analytics.services.question_service` and `analytics.services.observation_service` to confirm available helper functions.
3. Add small permission helpers if useful.
4. Add `analytics/assessment_forms.py` with dynamic `CoachAssessmentForm`.
5. Add small coach assessment workflow helpers if needed.
6. Add coach assessment URLs while preserving import URLs.
7. Add coach assessment list/edit/detail views.
8. Add staff review list/detail views.
9. Add templates and optional partials using dynamic question groups.
10. Add tests for forms, coach workflow, staff review, permissions, and regressions.
11. Run `python manage.py makemigrations analytics --check`.
12. Run `python manage.py test analytics`.
13. Run `python manage.py test players`.
14. Run `python manage.py test`.
15. Update `STATUS.md`, the Phase 4 tracker, and this engineering plan with implementation decisions and phase review.

## Implementation Decisions

- Added `analytics/assessment_forms.py` with a dynamic `CoachAssessmentForm` that builds fields from active `ObservationQuestion` records.
- Kept question text out of templates. Templates render grouped question/form-field pairs supplied by the form/view layer.
- Added `analytics/services/coach_assessment_service.py` for Phase 4 workflow helpers such as active cycle lookup, player assessment status, draft get/create, display grouping, and staff reopen.
- Added `analytics/services/permissions.py` for small coach/staff observation permission checks.
- Treated authenticated users as coach assessment submitters because the repository does not yet have a dedicated coach role source.
- Preserved the Phase 2 import UI routes and templates while adding assessment and staff review routes.
- Implemented staff reopen as a simple status change from `submitted` to `reopened`; reopened observations are editable by the original evaluator.
- Did not add migrations, reporting, timelines, draft context, measurements, attachments, AI, PDP migration work, or future observation workflows.

## Implementation Notes

Implemented on 2026-07-03.

Files created:

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

Files updated:

- `analytics/views.py`
- `analytics/urls.py`
- `analytics/tests.py`
- `docs/analytics/implementation/STATUS.md`
- `docs/analytics/implementation/phase_04_coach_assessment_workflow.md`
- `docs/analytics/implementation/engineering/phase_04_coach_assessment_workflow.md`

Verification completed:

- `python manage.py makemigrations analytics --check`
- `python manage.py test analytics`
- `python manage.py test players`
- `python manage.py test`

Test results:

- `analytics`: 42 tests passing.
- `players`: 39 tests passing.
- full suite: 115 tests passing.

## Phase Review

### What went well

The Phase 3 observation and question services were sufficient for Phase 4. The workflow did not need model changes.

Dynamic question rendering worked without hard-coding question text in templates.

The Phase 2 import UI remained intact and continued passing through the Analytics regression tests.

### Challenges

The project does not yet have a dedicated coach role source. Phase 4 uses authenticated-user access for coach assessment submission and staff/superuser checks for review.

The assessment list and staff review filters are intentionally simple to avoid drifting into reporting or dashboard functionality.

### Technical debt

The active cycle picker is basic. Future work may need a clearer cycle selection and staff cycle management workflow.

`analytics/tests.py` now contains import, foundation, and workflow tests. A future cleanup could split it into a tests package.

### Architecture changes

None.

### Recommendations for the next phase

Keep Phase 5 focused on draft context. Do not turn the staff review list into reporting, comparison, or timeline functionality.
