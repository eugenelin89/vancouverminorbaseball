**Must-Fix Before Phase 4**

1. Coach assessments can be created without an evaluator.  
   `create_coach_assessment_observation()` requires an `evaluator` parameter syntactically, but it accepts `None` at runtime. `_validate_unique_coach_assessment()` skips duplicate checks when evaluator is `None` in [analytics/services/observation_service.py](/Users/eugenelin/dev/vmba0/analytics/services/observation_service.py:59), and the DB constraint also only applies when evaluator is not null in [analytics/models.py](/Users/eugenelin/dev/vmba0/analytics/models.py:239).  
   This conflicts with the requirement to record who submitted the evaluation.

2. Submitted observations do not require required responses.  
   The default rating questions are marked required in [analytics/services/question_service.py](/Users/eugenelin/dev/vmba0/analytics/services/question_service.py:142), but `submit_observation()` only changes status and timestamp in [analytics/services/observation_service.py](/Users/eugenelin/dev/vmba0/analytics/services/observation_service.py:229). Phase 4 could accidentally submit empty or partial coach assessments.

**Should-Fix**

1. Validate that `question_set.observation_type` matches `observation_type`.  
   `create_observation()` accepts both independently in [analytics/services/observation_service.py](/Users/eugenelin/dev/vmba0/analytics/services/observation_service.py:106), but does not confirm they belong together. This could create a `coach_assessment` using the wrong question set.

2. Tighten rating validation.  
   `_coerce_rating()` allows any decimal between 1 and 5 in [analytics/services/observation_service.py](/Users/eugenelin/dev/vmba0/analytics/services/observation_service.py:73). If Version 1 rubric is strictly choices `1`, `2`, `3`, `4`, `5`, reject values like `3.5`, `NaN`, and infinity explicitly.

3. Make default setup less likely to overwrite edited questions.  
   `ensure_default_coach_assessment_setup()` uses `update_or_create()` for existing questions in [analytics/services/question_service.py](/Users/eugenelin/dev/vmba0/analytics/services/question_service.py:147). If staff later edits a V1 question in admin, rerunning setup may overwrite prompt/order/required flags. Safer default setup should create missing records and avoid destructive updates once questions exist.

4. Validate cycle question-set assignment.  
   `EvaluationCycle.coach_assessment_question_set` can point to any `ObservationQuestionSet`, including a future non-coach type. Add model/service validation before Phase 4 depends on it.

**Nice-To-Have**

1. Add convenience query helpers for Phase 4, such as “get or create draft coach assessment for evaluator/player/cycle” and “list active cycles for coach assessments.”

2. Add admin inlines for `ObservationResponse` under `ObservationAdmin` as read-only or mostly read-only for inspection.

3. Split `analytics/tests.py` before it grows further. It now contains both import UI tests and observation foundation tests.

**Recommended Fixes**

- In `create_coach_assessment_observation()`, require a non-null authenticated evaluator or at least non-null evaluator.
- Add `validate_required_responses(observation)` and call it from `submit_observation()` for `coach_assessment`.
- Validate `question_set.observation_type_id == observation_type.id` in `create_observation()`.
- Restrict `rating_1_5` responses to integer choices 1 through 5.
- Change default setup to avoid overwriting existing question text/order after creation, especially once responses exist.
- Add tests for evaluator-required creation, required-response submission blocking, question-set/type mismatch, decimal/NaN rating rejection, and setup not overwriting existing questions.

**Can Phase 4 Safely Begin?**

Not yet. The architecture boundary is clean and Phase 2 import UI appears unaffected, but Phase 4 will build directly on the observation service. Fix the evaluator requirement and required-response submission guard first; otherwise the coach assessment UI could create invalid submitted assessments.