# Phase 3 Engineering Plan: Analytics Observation Foundation

## Overview

Phase 3 creates the Analytics observation foundation required for Version 1 coach assessments.

Phase 1 and Phase 2 are complete. The repository already has:

- `players.Player` as the canonical future player identity model.
- player matching/import/provenance owned by `players`.
- a minimal `analytics` app created for the Phase 2 import UI.

Phase 3 should extend the existing `analytics` app with models, admin, services, migrations, and tests for observations, questions, responses, evaluation cycles, sources, and evaluator roles.

Mandatory boundaries:

- Use `players.Player` as the canonical player reference.
- Do not duplicate player identity, matching, or import logic in Analytics.
- Do not implement coach-facing assessment UI yet.
- Do not implement staff review UI yet.
- Do not implement reporting, timelines, draft context, measurements, attachments, AI, provider integrations, or future observation workflows.
- Version 1 should support only the `coach_assessment` observation type, while keeping the model practical for future observation types.

## Files To Create

Analytics models and services:

- `analytics/models.py`
  - define the Phase 3 Analytics observation foundation models.
- `analytics/admin.py`
  - register all Phase 3 models for staff inspection/configuration.
- `analytics/services/__init__.py`
- `analytics/services/question_service.py`
  - seed/retrieve question configuration.
- `analytics/services/observation_service.py`
  - create observations and persist responses.
- `analytics/migrations/0001_initial.py`
  - initial Analytics model migration, unless current app migration numbering requires a different filename.
- `analytics/migrations/0002_seed_observation_defaults.py`
  - optional data migration for default lookup data and default coach assessment questions.

Testing:

- Prefer adding Phase 3 tests to existing `analytics/tests.py` to follow current repository convention.
- If `analytics/tests.py` becomes too large, defer splitting into a tests package unless explicitly approved.

## Files To Modify

Existing Analytics files:

- `analytics/apps.py`
  - no change expected unless app startup metadata is needed.
- `analytics/tests.py`
  - add model/service tests for the observation foundation.

Project settings:

- `vancouverminor/settings.py`
  - no change expected because `analytics` is already installed from Phase 2.

Documentation after implementation:

- `docs/analytics/implementation/STATUS.md`
- `docs/analytics/implementation/phase_03_analytics_observation_foundation.md`
- `docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md`

Do not modify architecture documents unless implementation discovers a genuine architectural issue.

## Proposed Analytics Models

Use app-local timestamp patterns consistent with `players`.

Recommended shared abstract base:

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

Keep this local to `analytics`. Do not introduce a project-wide base model in Phase 3.

### EvaluationCycle

Purpose:

- Groups observations by season, event, draft, tryout, or assessment window.
- Provides the context for which question set applies to coach assessments.

Fields:

- `name`: `CharField(max_length=160)`
- `slug`: `SlugField(max_length=180, unique=True)`
- `cycle_type`: `CharField(max_length=80)`
- `description`: `TextField(blank=True)`
- `starts_on`: `DateField(null=True, blank=True)`
- `ends_on`: `DateField(null=True, blank=True)`
- `is_active`: `BooleanField(default=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- timestamps

Recommended behavior:

- Generate a unique slug from `name` if blank.
- Keep cycle type as a simple controlled string in Phase 3, not a separate model.
- Do not connect to a PDP season model or draft model in Phase 3.

Indexes:

- `["is_active", "starts_on"]`
- `["cycle_type", "is_active"]`
- `["slug"]`

Ordering:

- `["-starts_on", "-created_at", "name"]`

### ObservationType

Purpose:

- Controlled lookup for observation types.
- Version 1 only needs `coach_assessment`.

Fields:

- `key`: `SlugField(max_length=80, unique=True)`
- `name`: `CharField(max_length=120)`
- `description`: `TextField(blank=True)`
- `is_active`: `BooleanField(default=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- timestamps

Default record:

- `key="coach_assessment"`
- `name="Coach Assessment"`

Indexes:

- `["is_active", "key"]`

Ordering:

- `["key"]`

### ObservationSource

Purpose:

- Records where an observation came from without overbuilding provider infrastructure.

Fields:

- `key`: `SlugField(max_length=80, unique=True)`
- `name`: `CharField(max_length=120)`
- `description`: `TextField(blank=True)`
- `is_active`: `BooleanField(default=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- timestamps

Version 1 default records:

- `coach`
- `staff`
- `manual_entry`
- `imported_csv`
- `draft_context`

Do not implement provider credentials, third-party configuration, sync jobs, or provider admin workflows.

Indexes:

- `["is_active", "key"]`

Ordering:

- `["key"]`

### EvaluatorRole

Purpose:

- Controlled lookup for evaluator role snapshots.
- Reports may later filter observations by evaluator role.

Fields:

- `key`: `SlugField(max_length=80, unique=True)`
- `name`: `CharField(max_length=120)`
- `description`: `TextField(blank=True)`
- `is_active`: `BooleanField(default=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- timestamps

Recommended default records:

- `coach`
- `assistant_coach`
- `head_coach`
- `coordinator`
- `staff`
- `admin`

Keep this separate from Django auth groups. Phase 3 should snapshot the selected role on each observation and should not introduce a full role-permission system.

Indexes:

- `["is_active", "key"]`

Ordering:

- `["key"]`

### ObservationQuestionSet

Purpose:

- Defines a versioned set of questions for an observation type.
- Allows questions to evolve while old observations remain interpretable.

Fields:

- `observation_type`: `ForeignKey("analytics.ObservationType", on_delete=models.PROTECT, related_name="question_sets")`
- `name`: `CharField(max_length=160)`
- `version`: `PositiveIntegerField(default=1)`
- `description`: `TextField(blank=True)`
- `rubric`: `JSONField(default=dict, blank=True)`
- `effective_from`: `DateField(null=True, blank=True)`
- `retired_on`: `DateField(null=True, blank=True)`
- `is_active`: `BooleanField(default=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- timestamps

Recommended constraints:

- Unique `["observation_type", "version"]`.

Indexes:

- `["observation_type", "is_active"]`
- `["observation_type", "version"]`
- `["effective_from", "retired_on"]`

Ordering:

- `["observation_type__key", "-version"]`

### ObservationQuestion

Purpose:

- Stores one question within a question set.
- Questions are configurable and ordered, not hard-coded in templates.

Fields:

- `question_set`: `ForeignKey("analytics.ObservationQuestionSet", on_delete=models.CASCADE, related_name="questions")`
- `key`: `SlugField(max_length=120)`
- `prompt`: `CharField(max_length=255)`
- `help_text`: `TextField(blank=True)`
- `category`: `CharField(max_length=80, blank=True)`
- `response_type`: `CharField(max_length=40)`
- `display_order`: `PositiveIntegerField(default=0)`
- `is_required`: `BooleanField(default=False)`
- `is_active`: `BooleanField(default=True)`
- `min_numeric_value`: `DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)`
- `max_numeric_value`: `DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)`
- `choices`: `JSONField(default=list, blank=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- timestamps

Recommended response type constants:

- `rating_1_5`
- `text`

Future-ready constants may exist in code as choices, but Phase 3 tests and seed data should only require `rating_1_5` and `text`.

Recommended constraints:

- Unique `["question_set", "key"]`.
- Unique `["question_set", "display_order"]` if the implementation wants strict ordering. If this makes resequencing awkward, skip the uniqueness and rely on ordering only.

Indexes:

- `["question_set", "display_order"]`
- `["question_set", "is_active"]`
- `["category", "display_order"]`

Ordering:

- `["question_set", "display_order", "id"]`

### Observation

Purpose:

- Represents one structured/semi-structured observation about a `players.Player`.
- Version 1 uses this for coach assessments.

Fields:

- `player`: `ForeignKey("players.Player", on_delete=models.CASCADE, related_name="observations")`
- `evaluation_cycle`: `ForeignKey("analytics.EvaluationCycle", on_delete=models.PROTECT, related_name="observations")`
- `observation_type`: `ForeignKey("analytics.ObservationType", on_delete=models.PROTECT, related_name="observations")`
- `question_set`: `ForeignKey("analytics.ObservationQuestionSet", on_delete=models.PROTECT, related_name="observations")`
- `source`: `ForeignKey("analytics.ObservationSource", on_delete=models.PROTECT, related_name="observations")`
- `evaluator`: `ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="analytics_observations")`
- `evaluator_role`: `ForeignKey("analytics.EvaluatorRole", null=True, blank=True, on_delete=models.PROTECT, related_name="observations")`
- `evaluator_role_key`: `CharField(max_length=80, blank=True)`
- `evaluator_role_name`: `CharField(max_length=120, blank=True)`
- `status`: `CharField(max_length=40)`
- `submitted_at`: `DateTimeField(null=True, blank=True)`
- `notes`: `TextField(blank=True)`
- `source_metadata`: `JSONField(default=dict, blank=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- timestamps

Recommended status constants:

- `draft`
- `submitted`
- `reopened`
- `archived`

Phase 3 should support creating draft and submitted observations through services. It should not implement the coach-facing form UI that edits them.

Evaluator role snapshot:

- On creation/submission, copy `evaluator_role.key` to `evaluator_role_key`.
- Copy `evaluator_role.name` to `evaluator_role_name`.
- This keeps observations reportable by role even if the role display name changes later.

Recommended constraints:

- Unique coach assessment per evaluator/player/cycle/type:
  - `UniqueConstraint(fields=["player", "evaluation_cycle", "observation_type", "evaluator"], condition=Q(observation_type__key="coach_assessment")...)` is not valid in Django because conditional constraints cannot join on related fields.
  - Practical Phase 3 option: add a nullable/simple snapshot field `observation_type_key` on `Observation` and enforce a conditional unique constraint on `["player", "evaluation_cycle", "observation_type_key", "evaluator"]` where `observation_type_key="coach_assessment"` and `evaluator IS NOT NULL`.

Recommended additional field for constraints:

- `observation_type_key`: `CharField(max_length=80, editable=False)`

Set `observation_type_key` from `observation_type.key` in `save()` and in services before validation.

Constraint:

- Unique `["player", "evaluation_cycle", "observation_type_key", "evaluator"]` when `observation_type_key="coach_assessment"` and `evaluator__isnull=False`.

Indexes:

- `["player", "-created_at"]`
- `["evaluation_cycle", "observation_type", "status"]`
- `["evaluator", "evaluation_cycle"]`
- `["evaluator_role_key", "evaluation_cycle"]`
- `["observation_type_key", "status"]`
- `["submitted_at"]`

Ordering:

- `["-submitted_at", "-created_at", "-id"]`

### ObservationResponse

Purpose:

- Stores one answer/value for one question on one observation.

Fields:

- `observation`: `ForeignKey("analytics.Observation", on_delete=models.CASCADE, related_name="responses")`
- `question`: `ForeignKey("analytics.ObservationQuestion", on_delete=models.PROTECT, related_name="responses")`
- `response_type`: `CharField(max_length=40)`
- `numeric_value`: `DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)`
- `text_value`: `TextField(blank=True)`
- `boolean_value`: `BooleanField(null=True, blank=True)`
- `selected_choice`: `CharField(max_length=120, blank=True)`
- `raw_value`: `TextField(blank=True)`
- `unit`: `CharField(max_length=40, blank=True)`
- `payload`: `JSONField(default=dict, blank=True)`
- `metadata`: `JSONField(default=dict, blank=True)`
- timestamps

Version 1 only needs:

- `rating_1_5` stored in `numeric_value`.
- `text` stored in `text_value`.

Recommended constraints:

- Unique `["observation", "question"]`.

Indexes:

- `["observation", "question"]`
- `["question", "numeric_value"]`
- `["response_type"]`

Ordering:

- `["question__display_order", "id"]`

Validation:

- If `response_type="rating_1_5"`, require numeric value between 1 and 5.
- If `response_type="text"`, store text in `text_value`.
- Phase 3 may implement validation in `observation_service` and/or model `clean()`. Prefer service validation for response payload assembly and model validation for invariant checks.

## Constraints And Indexes

Use explicit constraints where they protect user-facing workflow assumptions:

- `ObservationQuestionSet`: one version number per observation type.
- `ObservationQuestion`: one question key per question set.
- `Observation`: one `coach_assessment` per evaluator/player/cycle/type.
- `ObservationResponse`: one response per observation/question.

Use indexes for likely Phase 4 and Phase 6 access patterns:

- player profile/detail pages need observations by player and recent date.
- coach workflow needs observations by evaluator and cycle.
- staff review needs observations by cycle, type, status, and evaluator role.
- response analysis needs numeric responses by question.

Avoid adding speculative indexes for future measurements, attachments, AI, third-party integrations, or reporting not implemented in Version 1.

## Question-Set And Versioning Strategy

Keep versioning practical:

- Question sets are versioned by `ObservationQuestionSet.version`.
- Questions belong to one question set.
- Do not mutate question text destructively after responses exist.
- To change questions later, create a new question set version and attach future cycles/observations to that version.
- Preserve old question sets and questions so historical observations remain interpretable.

Phase 3 should provide service helpers to:

- get or create `coach_assessment` observation type.
- get the active/default coach assessment question set.
- create a new question set from a structured list of default question definitions.
- retrieve active questions in display order.

Do not build admin workflows for version branching in Phase 3. The Django admin can inspect and manually adjust question sets, but service helpers should seed the default configuration safely.

Cycle/question-set relationship:

- Prefer adding `coach_assessment_question_set` on `EvaluationCycle` as a nullable FK to `ObservationQuestionSet`.
- This makes Phase 4 straightforward: choose the cycle, then load the cycle's configured coach assessment questions.
- If blank, `question_service.get_question_set_for_cycle()` can fall back to the active default coach assessment question set.

Recommended additional `EvaluationCycle` field:

- `coach_assessment_question_set`: nullable `ForeignKey("analytics.ObservationQuestionSet", on_delete=models.PROTECT, blank=True, null=True, related_name="evaluation_cycles")`

## Default Coach Assessment Seed / Setup Strategy

Seed the default configuration through an idempotent service function and optionally call it from a data migration.

Recommended service function:

```python
ensure_default_coach_assessment_setup() -> dict
```

Responsibilities:

- Create/update `ObservationType(key="coach_assessment")`.
- Create/update Version 1 `ObservationSource` records:
  - `coach`
  - `staff`
  - `manual_entry`
  - `imported_csv`
  - `draft_context`
- Create/update default `EvaluatorRole` records:
  - `coach`
  - `assistant_coach`
  - `head_coach`
  - `coordinator`
  - `staff`
  - `admin`
- Create the default `ObservationQuestionSet` for `coach_assessment`, version `1`, if it does not exist.
- Create default questions if missing.
- Do not delete or rewrite existing questions with responses.

Default rubric:

```python
{
    "scale": "1-5",
    "labels": {
        "1": "0/5 times, Never",
        "2": "1-2/5 times, Infrequently",
        "3": "2.5/5 times, Half the time",
        "4": "4/5 times, Frequently",
        "5": "5/5 times, Always",
    },
}
```

Default questions:

- Throw
  - Throws accurately
  - Throws with velocity
  - Ability to throw from outfield to infield in the air or on one hop
  - Can throw accurately across the diamond from 3rd to 1st
- Field
  - Can catch routine balls at 1st base
  - Can catch non-routine balls at 1st base
  - Ability to catch a routine grounder
  - Ability to catch a non-routine grounder
  - Ability to catch a routine fly ball
  - Ability to catch a non-routine fly ball
- Hitting
  - Hits barrels
  - Player can sacrifice bunt
  - Player chooses strikes to swing at
  - Gets on base
  - Hits for power
- Pitching
  - Throws strikes
  - Can hold runners
  - Has good velocity
  - Has an off-speed pitch
- Catching
  - Likes to catch
  - Can throw to 2nd accurately
  - Can block
- Hustle
  - Always focused
  - Checks in/attends regularly
  - Listens to coach feedback
- Notes
  - Freeform coach notes

Response type mapping:

- All rubric questions use `rating_1_5`.
- Freeform coach notes uses `text`.

Question keys:

- Generate stable slugs from category and prompt, for example:
  - `throw_throws_accurately`
  - `hitting_hits_barrels`
  - `notes_freeform_coach_notes`
- Keep keys stable once seeded.

Data migration recommendation:

- Add a small data migration that calls the idempotent setup logic or mirrors it with migration-safe model access.
- If importing the runtime service from a migration feels too brittle, implement the data migration with `apps.get_model()` and keep service tests verifying the same defaults.
- The setup service should still exist for tests, local repair, and future setup commands.

Do not create a management command in Phase 3 unless the implementation discovers a strong repository convention requiring one.

## Observation Service Design

Location:

- `analytics/services/observation_service.py`

Recommended constants:

- `STATUS_DRAFT = "draft"`
- `STATUS_SUBMITTED = "submitted"`
- `STATUS_REOPENED = "reopened"`
- `STATUS_ARCHIVED = "archived"`

Recommended dataclasses:

- `ResponseInput`
  - `question`
  - `value`
  - optional explicit response fields if useful.
- `ObservationCreateResult`
  - `observation`
  - `responses_created`
  - `responses_updated`

Core functions:

- `create_observation(...)`
  - Creates an observation without necessarily creating responses.
  - Requires `players.Player`, `EvaluationCycle`, `ObservationType`, `ObservationSource`, evaluator, and evaluator role where appropriate.
  - Sets `observation_type_key`.
  - Snapshots evaluator role key/name.
  - Enforces duplicate coach assessment rule.
- `create_coach_assessment_observation(...)`
  - Convenience wrapper for `coach_assessment`.
  - Loads the cycle/default question set.
  - Uses source `coach` by default.
  - Can create draft or submitted observations.
- `save_observation_responses(observation, responses)`
  - Validates questions belong to `observation.question_set`.
  - Upserts `ObservationResponse` rows.
  - Validates `rating_1_5` numeric values are between 1 and 5.
  - Stores text responses in `text_value`.
  - Does not implement future boolean/multiple-choice/measurement UI.
- `submit_observation(observation, actor=None)`
  - Changes status to `submitted`.
  - Sets `submitted_at`.
  - Keeps role snapshot unchanged unless explicitly provided.
- `get_observation_detail(observation_id)`
  - Returns observation with select/prefetch related data for future Phase 4/6 use.

Transaction rules:

- Wrap create/save/submit operations in `transaction.atomic`.
- Use `select_for_update()` when updating an existing observation and responses.
- Let database constraints protect duplicate submitted/draft creation, but raise clear `ValidationError` from services before relying only on `IntegrityError`.

Permission rules:

- Phase 3 service functions should not assume UI permissions are complete.
- For creation helpers, accept an evaluator user and role.
- Do not build a full coach permission system in Phase 3.
- Phase 4 will decide how authenticated coaches access these services.

## Question Service Design

Location:

- `analytics/services/question_service.py`

Recommended constants:

- `OBSERVATION_TYPE_COACH_ASSESSMENT = "coach_assessment"`
- `RESPONSE_TYPE_RATING_1_5 = "rating_1_5"`
- `RESPONSE_TYPE_TEXT = "text"`

Core functions:

- `ensure_default_coach_assessment_setup()`
  - Idempotently creates default type/source/roles/question set/questions.
- `get_coach_assessment_type()`
  - Returns `ObservationType` for `coach_assessment`.
- `get_default_coach_assessment_question_set()`
  - Returns active version 1 question set or latest active coach assessment question set.
- `get_question_set_for_cycle(cycle, observation_type=None)`
  - Returns `cycle.coach_assessment_question_set` when present.
  - Falls back to default active coach assessment question set.
- `get_active_questions(question_set)`
  - Returns active questions ordered by `display_order`.
- `create_question_set_version(...)`
  - Optional helper in Phase 3 if simple; otherwise defer until a real versioning workflow exists.

Keep question service focused on configuration and retrieval. Observation creation belongs in `observation_service`.

## Admin Configuration

Register all Phase 3 models in `analytics/admin.py`.

Recommended admin setup:

### EvaluationCycleAdmin

- `list_display`: `name`, `cycle_type`, `is_active`, `starts_on`, `ends_on`, `coach_assessment_question_set`
- `list_filter`: `is_active`, `cycle_type`
- `search_fields`: `name`, `slug`
- `prepopulated_fields`: `{"slug": ("name",)}`
- `readonly_fields`: `created_at`, `updated_at`

### ObservationTypeAdmin

- `list_display`: `key`, `name`, `is_active`
- `list_filter`: `is_active`
- `search_fields`: `key`, `name`
- `readonly_fields`: timestamps

### ObservationSourceAdmin

- `list_display`: `key`, `name`, `is_active`
- `list_filter`: `is_active`
- `search_fields`: `key`, `name`
- `readonly_fields`: timestamps

### EvaluatorRoleAdmin

- `list_display`: `key`, `name`, `is_active`
- `list_filter`: `is_active`
- `search_fields`: `key`, `name`
- `readonly_fields`: timestamps

### ObservationQuestionInline

- Inline questions under `ObservationQuestionSet`.
- Use tabular inline.
- Fields: `display_order`, `category`, `key`, `prompt`, `response_type`, `is_required`, `is_active`.
- Avoid making response data editable inline.

### ObservationQuestionSetAdmin

- `list_display`: `name`, `observation_type`, `version`, `is_active`, `effective_from`, `retired_on`
- `list_filter`: `observation_type`, `is_active`
- `search_fields`: `name`, `observation_type__key`
- inline `ObservationQuestionInline`
- `readonly_fields`: timestamps

### ObservationAdmin

- `list_display`: `player`, `evaluation_cycle`, `observation_type`, `status`, `evaluator`, `evaluator_role_name`, `submitted_at`
- `list_filter`: `status`, `observation_type`, `evaluation_cycle`, `evaluator_role_key`, `source`
- `search_fields`: `player__first_name`, `player__last_name`, `evaluator__username`, `evaluator__email`
- `readonly_fields`: timestamps, `submitted_at`, `observation_type_key`, `evaluator_role_key`, `evaluator_role_name`
- Do not expose raw sensitive import provenance here.

### ObservationResponseAdmin

- `list_display`: `observation`, `question`, `response_type`, `numeric_value`, `text_preview`
- `list_filter`: `response_type`, `question__category`
- `search_fields`: `observation__player__first_name`, `observation__player__last_name`, `question__prompt`, `text_value`
- `readonly_fields`: timestamps

Admin is for staff inspection/configuration only. Do not build user-facing coach assessment screens in Phase 3.

## Tests To Write

Follow current app-level `tests.py` convention.

### Model tests

- Analytics app has Phase 3 models importable.
- `EvaluationCycle` slug generation creates stable unique slugs.
- `ObservationType`, `ObservationSource`, and `EvaluatorRole` keys are unique.
- `ObservationQuestionSet` enforces unique version per observation type.
- `ObservationQuestion` enforces unique key per question set.
- `Observation` references `players.Player`, not `pdp.PlayerProfile`.
- `Observation` snapshots evaluator role key/name.
- `ObservationResponse` stores `payload` JSON.
- `ObservationResponse` enforces one response per observation/question.

### Question service tests

- `ensure_default_coach_assessment_setup()` creates `coach_assessment`.
- Default Version 1 sources are created.
- Default evaluator roles are created.
- Default coach assessment question set is created.
- Default question count matches architecture.
- Rubric is stored on the question set.
- Rating questions use `rating_1_5`.
- Notes question uses `text`.
- Re-running setup is idempotent and does not duplicate defaults.
- `get_active_questions()` returns active questions in display order.
- `get_question_set_for_cycle()` returns the cycle question set when assigned and the default otherwise.

### Observation service tests

- Can create a draft coach assessment observation for a `players.Player`.
- Can create a submitted coach assessment observation and set `submitted_at`.
- Can persist numeric 1-5 responses.
- Can persist freeform text responses.
- Can store JSON payload on a response.
- Rejects rating values below 1 or above 5.
- Rejects responses for questions outside the observation's question set.
- Prevents duplicate coach assessment for the same evaluator/player/cycle/type.
- Allows multiple evaluators to assess the same player/cycle.
- Allows the same evaluator to assess different players in the same cycle.
- Allows the same evaluator to assess the same player in different cycles.

### Admin tests

- All Phase 3 models are registered in Django admin.
- Admin configuration includes practical list/search/filter fields.

### Regression tests

- `python manage.py test analytics` passes.
- `python manage.py test players` passes.
- `python manage.py test` passes.
- No test should require PDP workflow migration.

## Migration Strategy

Expected migrations:

1. `analytics` initial model migration for:
   - `EvaluationCycle`
   - `ObservationType`
   - `ObservationSource`
   - `EvaluatorRole`
   - `ObservationQuestionSet`
   - `ObservationQuestion`
   - `Observation`
   - `ObservationResponse`
2. Optional data migration seeding:
   - default `coach_assessment` observation type
   - Version 1 observation sources
   - Version 1 evaluator roles
   - default coach assessment question set and questions

Migration constraints:

- Do not alter `players` models unless Phase 3 implementation proves a missing relationship is absolutely required.
- Do not alter `pdp` models.
- Do not alter `drafts` models.
- Do not add measurement, attachment, timeline, reporting, or draft-context tables.
- Use `settings.AUTH_USER_MODEL` for evaluator FK.
- Reference `players.Player` directly.

Required commands during implementation:

- `python manage.py makemigrations analytics`
- `python manage.py migrate`
- `python manage.py test analytics`
- `python manage.py test players`
- `python manage.py test`

If using a data migration, verify that re-running tests creates defaults deterministically and does not depend on production database state.

## Risks / Ambiguities

- The repository has no shared season model. `EvaluationCycle` should remain independent in Phase 3.
- The existing `analytics` app currently owns Phase 2 import UI. Phase 3 must add observation foundation without entangling import UI and observation logic.
- Django conditional unique constraints cannot reference related fields, so duplicate coach assessment protection needs an `observation_type_key` snapshot or service-only validation. The recommended plan uses a snapshot plus service validation.
- Question-set versioning can become overbuilt. Phase 3 should support versioned question sets and historical interpretability without implementing a full question-set lifecycle UI.
- Role snapshots are required, but there is no project-wide coach/staff role system. Phase 3 should use `EvaluatorRole` as an Analytics lookup and avoid changing auth/group behavior.
- Default seed strategy must balance repeatability with migration safety. A data migration is useful, but service-level idempotent setup should also exist.
- Future Phase 4 may need draft/dynamic forms. Phase 3 should expose clean services and query helpers so Phase 4 does not hard-code questions.
- Numeric responses use `DecimalField`; UI form conversion and display formatting will be Phase 4 concerns.

## Open Questions

- Should default lookup/question data be seeded only through a data migration, or should implementation also add a management command for repair/setup? Recommendation: service plus data migration only in Phase 3.
- Should `EvaluationCycle` require date ranges? Recommendation: allow blank dates because some assessment cycles may be event-based or created before schedules are finalized.
- Should staff-created manual assessments use source `staff` or `manual_entry`? Recommendation: use `coach` for coach workflow, `staff` for staff-entered assessment records, and reserve `manual_entry` as a broader source lookup.
- Should `Observation.notes` duplicate the freeform notes question? Recommendation: keep `Observation.notes` for administrative/general observation notes, while the coach-facing freeform notes should be stored as an `ObservationResponse`.
- Should submitted observations be immutable in Phase 3? Recommendation: service should support submitted status but not implement reopen/edit policy until Phase 4.

## Recommended Implementation Sequence

1. Re-read architecture docs for Analytics, Coach Assessments, Services, and Permissions.
2. Inspect current `analytics` app from Phase 2 so new models/services do not disrupt import UI.
3. Create `analytics/models.py` with timestamp base, constants, models, constraints, indexes, and minimal validation.
4. Create `analytics/services/question_service.py` with default setup constants and idempotent seed helpers.
5. Create `analytics/services/observation_service.py` with transaction-wrapped observation/response creation helpers.
6. Register Phase 3 models in `analytics/admin.py`.
7. Generate `analytics` migrations.
8. Add a migration-safe default data migration if approved by implementation.
9. Add Analytics model/service/admin tests.
10. Run `python manage.py makemigrations analytics` and confirm no unexpected model churn.
11. Run `python manage.py migrate`.
12. Run `python manage.py test analytics`.
13. Run `python manage.py test players`.
14. Run `python manage.py test`.
15. Update `STATUS.md`, the Phase 3 tracker, and this engineering plan with implementation decisions and phase review.

## Implementation Decisions

- Extended the existing Phase 2 `analytics` app instead of creating a new app. This preserved the Phase 2 import UI and avoided duplicate app configuration.
- Added a local `TimeStampedModel` in `analytics.models`, consistent with the app-local timestamp pattern already used elsewhere in the repository.
- Added `Observation.observation_type_key` as a snapshot field so the database can enforce one `coach_assessment` per evaluator/player/evaluation cycle without joining through `ObservationType`.
- Stored evaluator role snapshots on `Observation` with `evaluator_role_key` and `evaluator_role_name` so future reporting can filter by the role at submission time even if role records change later.
- Added `EvaluationCycle.coach_assessment_question_set` as the Phase 3 link between a cycle and the active coach assessment question set.
- Implemented default coach assessment setup in both an idempotent runtime service and a migration-safe data migration. The migration mirrors the service data rather than importing runtime service code.
- Kept Version 1 response handling limited to `rating_1_5` and `text` in `observation_service`, while the model remains future-ready with fields such as boolean, selected choice, raw value, unit, payload, and metadata.
- Registered `ObservationQuestion` both inline under `ObservationQuestionSet` and directly in admin because the Phase 3 tracker explicitly calls for registering questions.
- Did not add any Phase 3 views, templates, URLs, reporting, timeline, draft integration, measurements, attachments, AI, or coach-facing UI.

## Implementation Notes

Implemented on 2026-07-02.

Files created:

- `analytics/models.py`
- `analytics/admin.py`
- `analytics/services/__init__.py`
- `analytics/services/question_service.py`
- `analytics/services/observation_service.py`
- `analytics/migrations/0001_initial.py`
- `analytics/migrations/0002_seed_observation_defaults.py`

Files updated:

- `analytics/tests.py`
- `docs/analytics/implementation/STATUS.md`
- `docs/analytics/implementation/phase_03_analytics_observation_foundation.md`
- `docs/analytics/implementation/engineering/phase_03_analytics_observation_foundation.md`

Verification completed:

- `python manage.py makemigrations analytics`
- `python manage.py migrate`
- `python manage.py test analytics`
- `python manage.py test players`
- `python manage.py test`

Test results:

- `analytics`: 25 tests passing.
- `players`: 39 tests passing.
- full suite: 98 tests passing.

## Phase Review

### What went well

The observation model, question setup, and response persistence fit cleanly into the existing app and service patterns.

The Phase 2 import UI remained untouched and continued passing through the Analytics test suite.

The `players.Player` boundary remained clean: Analytics references players but does not own player identity, matching, or import behavior.

### Challenges

Django cannot enforce a conditional unique constraint through `ObservationType.key`, so `Observation.observation_type_key` is required for the database-level coach assessment duplicate rule.

The default seed data is duplicated between the runtime setup service and the migration to keep the migration safe and historical.

### Technical debt

Question-set version lifecycle operations are intentionally minimal. Phase 4 or a later staff admin phase may need explicit workflows for copying, retiring, and assigning question sets.

Observation editing/reopen rules are not implemented yet. Phase 4 should define the user-facing policy.

### Architecture changes

None.

### Recommendations for the next phase

Build Phase 4 coach assessment forms from `ObservationQuestionSet` and `ObservationQuestion`, not hard-coded question lists.

Use `analytics.services.observation_service` for draft/submitted observation creation and response persistence.
