Read:
- docs/analytics/architecture/03_analytics.md
- docs/analytics/architecture/05_coach_assessments.md
- docs/analytics/implementation/phase_03_analytics_observation_foundation.md
- docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md

Apply Phase 3 review fixes only.

Do not start Phase 4.

Fix these issues:

1. Require evaluator for coach assessments.
- `create_coach_assessment_observation()` must reject missing evaluator.
- Add tests.

2. Require required responses before submission.
- Add `validate_required_responses(observation)`.
- `submit_observation()` must block submitted coach assessments missing required active questions.
- Add tests.

3. Validate question set belongs to observation type.
- `create_observation()` must reject mismatched `question_set.observation_type`.
- Add tests.

4. Tighten `rating_1_5` validation.
- Accept only integer choices 1, 2, 3, 4, 5.
- Reject decimals like 3.5.
- Reject NaN/infinity.
- Add tests.

5. Make default setup non-destructive.
- `ensure_default_coach_assessment_setup()` should create missing default questions but avoid overwriting existing question prompt/order/required flags after creation.
- Add test proving existing edited questions are not overwritten.

6. Validate `EvaluationCycle.coach_assessment_question_set`.
- It should only point to a coach-assessment question set.
- Add model or service validation and tests.

Nice-to-have if straightforward:
- Add read-only `ObservationResponse` inline under `ObservationAdmin`.
- Add simple Phase 4 query helpers only if they do not expand scope.

Do not change architecture documents unless required.

After fixes:
- run `python manage.py test analytics`
- run `python manage.py test players`
- run `python manage.py test`
- update the Phase 3 implementation/engineering docs with review-fix decisions and notes
- summarize files changed and test results