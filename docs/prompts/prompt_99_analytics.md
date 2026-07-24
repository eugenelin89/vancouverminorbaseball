# Prompt 99 - Analytics

## User Prompt

```text
# Codex Prompt — Support Optional Evaluation Questions

Review the current evaluation-question and evaluation-submission implementation in:

```text
/Users/eugenelin/dev/vmba0
```

Implement support for optional evaluation questions.

This is an incremental feature change.

Do not redesign the evaluation system.

Do not hard-code pitching, catching, or any other position name into the evaluation form logic.

The goal is to allow individual evaluation questions to be configured as required or optional.

Examples of questions that may need to be optional:

* pitching questions, because not every player pitches;
* catching questions, because not every player catches;
* other position-specific questions added in the future.

General evaluation questions should continue to be required unless explicitly configured otherwise.

---

# 1. Inspect the Current Implementation

Before making changes, inspect the current evaluation architecture.

At minimum, identify:

* the model representing evaluation or observation questions;
* the model storing evaluation answers;
* the services or builders that generate dynamic evaluation forms;
* coach evaluation forms;
* player self-evaluation forms;
* player peer-evaluation forms;
* draft-save behavior;
* final submission validation;
* review/detail templates;
* question administration screens;
* imports, fixtures, or seed data used to create questions;
* existing tests for evaluations and dynamic questions.

Likely relevant concepts may include:

```text
ObservationQuestion
Observation
ObservationAnswer
evaluation forms
dynamic forms
question groups
perspectives
evaluation cycles
```

Use the actual project terminology and structure.

Do not assume model or field names without inspecting the code.

---

# 2. Add a Required/Optional Setting to Questions

Add a field to the question model representing whether an answer is required.

Preferred behavior:

```python
is_required = models.BooleanField(default=True)
```

Use the project’s existing naming conventions if another field name fits better.

Requirements:

* existing questions must remain required after migration;
* new questions should default to required;
* administrators must be able to mark individual questions optional;
* optional status must apply consistently to coach, self, and peer evaluations where that question is shown;
* no position-specific business logic should be embedded in form validation.

Create the required database migration.

The migration must preserve existing behavior by giving existing rows a required value of `True`.

---

# 3. Update Question Administration

Expose the required/optional setting wherever questions are currently managed.

This may include:

* Django Admin;
* a custom question-management page;
* question creation forms;
* question-edit forms;
* question import or seed configuration.

An administrator should be able to:

1. create a required question;
2. create an optional question;
3. change an existing question from required to optional;
4. change an optional question back to required.

Where practical, show the required status in question lists.

Example:

```text
Question: Pitching command
Required: No
```

Do not add a second separate workflow just for optional questions.

---

# 4. Update Dynamic Form Generation

Update the dynamic evaluation-form builder so each generated form field uses the question’s required setting.

Conceptually:

```python
form_field.required = question.is_required
```

or set the correct `required` value when the field is constructed.

Verify this works for all supported question/input types, including any existing types such as:

* numeric scores;
* choices;
* text;
* textarea;
* boolean;
* rating scales;
* comments.

Do not make every question optional.

Do not rely only on HTML attributes.

Server-side validation must enforce required questions and permit blank optional questions.

---

# 5. Submission Behavior

Required questions:

* must still block final submission when unanswered;
* must display a clear validation error;
* must retain the user’s other entered answers after validation fails.

Optional questions:

* may be left unanswered;
* must not block final submission;
* must not produce a validation error;
* must not create an invalid placeholder answer merely to satisfy a database constraint.

Draft behavior should remain unchanged:

* drafts may continue to contain incomplete answers according to current behavior;
* changing a question to optional must not break reopening an existing draft.

---

# 6. Answer Persistence

Inspect how blank answers are currently stored.

Choose the implementation that best fits the existing data model.

Acceptable approaches may include:

* do not create an answer record for an unanswered optional question;
* preserve an existing blank-answer representation if the application already uses one consistently.

Requirements:

* do not store misleading zero values for unanswered optional score questions;
* do not interpret an unanswered optional question as a score of zero;
* analytics must distinguish “not answered” from an actual zero score;
* review pages must not imply that a blank answer is a negative rating.

Do not change historical answers unnecessarily.

---

# 7. Evaluation Display

Update evaluation forms so optional questions are visibly identifiable.

Use clear, understated wording such as:

```text
Optional
```

Possible display:

```text
Pitching Command (Optional)
```

or a small optional label beside the question.

Required questions may continue using the existing presentation.

Do not add an asterisk to optional questions.

If required questions currently use an asterisk, preserve that convention.

---

# 8. Review and Detail Pages

Update submitted-evaluation review/detail displays so unanswered optional questions are handled clearly.

Preferred display:

```text
Not answered
```

or:

```text
Not applicable / not answered
```

Use wording consistent with the application.

Do not display:

* `0`;
* `None`;
* an empty table cell with no explanation;
* a fabricated answer.

If unanswered optional questions are currently omitted entirely from review pages, determine whether omission or a “Not answered” label is clearer and more consistent with the existing interface.

Document the choice in the completion report.

---

# 9. Analytics and Scoring

Inspect all analytics and score-calculation code that consumes evaluation answers.

This includes, where applicable:

* average scores;
* question averages;
* player comparison;
* player timeline;
* Command Center metrics;
* reporting summaries;
* completion calculations;
* variance calculations;
* exports.

Unanswered optional questions must be excluded from score denominators.

Example:

Answers:

```text
5
4
blank optional question
```

Correct average:

```text
(5 + 4) / 2 = 4.5
```

Incorrect average:

```text
(5 + 4 + 0) / 3 = 3.0
```

Requirements:

* blank optional answers must not count as zero;
* blank optional answers must not reduce an average;
* existing required-question calculations must remain unchanged;
* views must not crash when all questions in a subgroup are unanswered;
* where no applicable answers exist, return the project’s normal empty state rather than dividing by zero.

Do not silently alter unrelated analytics behavior.

---

# 10. Completion and Progress Metrics

Inspect whether an evaluation’s completion percentage currently assumes every displayed question must be answered.

Update completion logic so:

* required questions determine submission completeness;
* optional unanswered questions do not make a submitted evaluation appear incomplete;
* optional answered questions may still be counted in informational completion displays if appropriate, but must not prevent 100% required completion.

Preferred conceptual distinction:

```text
Required completion: 100%
Optional answered: 2 of 5
```

Do not add a complicated new UI unless needed.

At minimum, ensure submitted evaluations with blank optional questions are not reported as incomplete.

---

# 11. Existing Data and Compatibility

Preserve all existing evaluation data.

Requirements:

* existing questions become required by default;
* existing answers remain unchanged;
* existing submitted evaluations remain valid;
* existing drafts still open;
* existing forms continue behaving as before until a question is explicitly made optional;
* no question should accidentally become optional through migration defaults.

Do not require rebuilding existing evaluation cycles or observations.

---

# 12. Automated Tests

Add or update tests covering the full behavior.

At minimum, test:

## Model and administration

* new questions default to required;
* an optional question can be created;
* the required flag can be changed;
* existing-question migration behavior is safe where practical to test.

## Dynamic form behavior

* required question fields are generated with `required=True`;
* optional question fields are generated with `required=False`;
* this applies across supported evaluation perspectives;
* this applies across relevant question types.

## Final submission

* missing required answer blocks submission;
* missing optional answer allows submission;
* required validation errors are displayed;
* other entered answers survive validation failure;
* optional blank score does not become zero.

## Drafts

* a draft can be saved with optional questions blank;
* reopening the draft works;
* the draft can later be submitted while optional questions remain blank;
* a required question still must be answered before submission.

## Review display

* answered optional questions display normally;
* unanswered optional questions display as the chosen empty-state wording or are intentionally omitted;
* they are never displayed as zero.

## Analytics

* optional blank answers are excluded from averages;
* optional answered questions are included normally;
* all-blank optional subgroups do not cause division-by-zero errors;
* player timeline and comparison continue to render;
* submitted evaluations with blank optional questions are treated as complete.

## Duplicate and lifecycle behavior

* optional questions do not affect evaluation uniqueness;
* reopen and resubmit continue to reuse the same evaluation;
* changing answers to optional questions does not create duplicate observations.

Use existing test factories, fixtures, and conventions.

Do not create an unrelated testing framework.

---

# 13. QA Documentation

Update relevant QA documentation under:

```text
docs/qa/platform_e2e/
```

Add a practical manual test scenario for optional questions.

Include a scenario similar to:

```text
1. Mark one pitching question optional.
2. Leave that question blank.
3. Complete all required questions.
4. Submit the evaluation.
5. Confirm submission succeeds.
6. Confirm review shows the optional question as unanswered.
7. Confirm analytics do not treat it as zero.
8. Change the same question back to required.
9. Start a new evaluation.
10. Leave it blank.
11. Confirm final submission is blocked.
```

Update feature traceability if the existing requirement-ID convention requires it.

Prefer adding or updating an evaluation requirement rather than creating excessive new IDs.

Possible choices:

```text
EVL-008 Optional evaluation questions
```

or expand an existing question-validation requirement if one already clearly covers this behavior.

Do not renumber existing requirement IDs.

Update the QA changelog.

---

# 14. Validation

Run the appropriate project validations.

At minimum:

```bash
DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
DJANGO_SECRET_KEY=test python manage.py test
git diff --check
```

If the full test suite is unusually large, run:

1. focused evaluation tests;
2. analytics tests affected by blank answers;
3. the full suite if practical.

Report exact commands and results.

Also verify manually or through tests that:

* a required question blocks submission;
* an optional question does not block submission;
* unanswered optional score questions are not stored or calculated as zero;
* existing questions remain required after migration;
* analytics render without errors.

---

# 15. Scope Restrictions

Do not:

* hard-code pitching or catching question names;
* infer optionality from question text;
* infer optionality from player position;
* automatically hide position-specific questions;
* redesign the evaluation-cycle system;
* change evaluation uniqueness rules;
* remove existing required validation;
* change historical answers;
* modify production data;
* run production imports;
* push changes unless explicitly instructed.

The question configuration—not the player’s roster position—should determine whether an answer is required.

A future feature may conditionally show questions based on player positions, but that is outside this task.

---

# 16. Completion Report

At completion, report:

1. Files modified.
2. Files added.
3. Model and migration changes.
4. Administration changes.
5. Dynamic-form validation changes.
6. Draft and submission behavior.
7. How blank optional answers are persisted.
8. Review-page behavior.
9. Analytics and denominator handling.
10. Completion-metric behavior.
11. Tests added or updated.
12. QA documentation changes.
13. Validation commands and results.
14. Any unresolved product decisions.
15. Confirmation that no production data was changed.

Commit with a clear message such as:

```text
Support optional evaluation questions
```

Do not push unless explicitly instructed.
```

## Implementation Commit

```text
e52bf1a2c4c75e952ad083a85a37a7fd704dbadd
```

## Commit Diff

```diff
diff --git a/analytics/admin.py b/analytics/admin.py
index fe1f86b..bcaade0 100644
--- a/analytics/admin.py
+++ b/analytics/admin.py
@@ -18,7 +18,15 @@ class TimeStampedAdmin(admin.ModelAdmin):
 
 @admin.register(EvaluationCycle)
 class EvaluationCycleAdmin(TimeStampedAdmin):
-    list_display = ("name", "cycle_type", "season", "is_active", "starts_on", "ends_on", "coach_assessment_question_set")
+    list_display = (
+        "name",
+        "cycle_type",
+        "season",
+        "is_active",
+        "starts_on",
+        "ends_on",
+        "coach_assessment_question_set",
+    )
     list_filter = ("is_active", "cycle_type", "season")
     search_fields = ("name", "slug")
     prepopulated_fields = {"slug": ("name",)}
@@ -48,19 +56,48 @@ class EvaluatorRoleAdmin(TimeStampedAdmin):
 class ObservationQuestionInline(admin.TabularInline):
     model = ObservationQuestion
     extra = 0
-    fields = ("display_order", "category", "key", "prompt", "response_type", "is_required", "is_active")
+    fields = (
+        "display_order",
+        "category",
+        "key",
+        "prompt",
+        "response_type",
+        "is_required",
+        "is_active",
+    )
 
 
 @admin.register(ObservationQuestion)
 class ObservationQuestionAdmin(TimeStampedAdmin):
-    list_display = ("prompt", "question_set", "category", "response_type", "display_order", "is_active")
-    list_filter = ("question_set", "category", "response_type", "is_active")
+    list_display = (
+        "prompt",
+        "question_set",
+        "category",
+        "response_type",
+        "display_order",
+        "is_required",
+        "is_active",
+    )
+    list_filter = (
+        "question_set",
+        "category",
+        "response_type",
+        "is_required",
+        "is_active",
+    )
     search_fields = ("prompt", "key", "question_set__name")
 
 
 @admin.register(ObservationQuestionSet)
 class ObservationQuestionSetAdmin(TimeStampedAdmin):
-    list_display = ("name", "observation_type", "version", "is_active", "effective_from", "retired_on")
+    list_display = (
+        "name",
+        "observation_type",
+        "version",
+        "is_active",
+        "effective_from",
+        "retired_on",
+    )
     list_filter = ("observation_type", "is_active")
     search_fields = ("name", "observation_type__key")
     inlines = [ObservationQuestionInline]
@@ -103,8 +140,21 @@ class ObservationAdmin(TimeStampedAdmin):
         "evaluation_perspective",
         "submitted_at",
     )
-    list_filter = ("status", "season", "observation_type", "evaluation_cycle", "evaluator_role_key", "evaluation_perspective", "source")
-    search_fields = ("player__first_name", "player__last_name", "evaluator__username", "evaluator__email")
+    list_filter = (
+        "status",
+        "season",
+        "observation_type",
+        "evaluation_cycle",
+        "evaluator_role_key",
+        "evaluation_perspective",
+        "source",
+    )
+    search_fields = (
+        "player__first_name",
+        "player__last_name",
+        "evaluator__username",
+        "evaluator__email",
+    )
     readonly_fields = TimeStampedAdmin.readonly_fields + (
         "submitted_at",
         "observation_type_key",
@@ -124,6 +174,17 @@ class ObservationAdmin(TimeStampedAdmin):
 
 @admin.register(ObservationResponse)
 class ObservationResponseAdmin(TimeStampedAdmin):
-    list_display = ("observation", "question", "response_type", "numeric_value", "text_preview")
+    list_display = (
+        "observation",
+        "question",
+        "response_type",
+        "numeric_value",
+        "text_preview",
+    )
     list_filter = ("response_type", "question__category")
-    search_fields = ("observation__player__first_name", "observation__player__last_name", "question__prompt", "text_value")
+    search_fields = (
+        "observation__player__first_name",
+        "observation__player__last_name",
+        "question__prompt",
+        "text_value",
+    )
diff --git a/analytics/assessment_forms.py b/analytics/assessment_forms.py
index e7bcf57..d0aa829 100644
--- a/analytics/assessment_forms.py
+++ b/analytics/assessment_forms.py
@@ -6,7 +6,9 @@ from analytics.services.question_service import get_active_questions
 
 
 class CoachAssessmentForm(forms.Form):
-    def __init__(self, *args, question_set, observation=None, require_required=False, **kwargs):
+    def __init__(
+        self, *args, question_set, observation=None, require_required=False, **kwargs
+    ):
         super().__init__(*args, **kwargs)
         self.question_set = question_set
         self.observation = observation
@@ -18,29 +20,40 @@ class CoachAssessmentForm(forms.Form):
         for question in self.questions:
             field_name = self.field_name(question)
             required = question.is_required if require_required else False
-            initial = self.initial_for_question(question, existing_responses.get(question.id))
+            field_label = (
+                question.prompt
+                if question.is_required
+                else f"{question.prompt} (Optional)"
+            )
+            initial = self.initial_for_question(
+                question, existing_responses.get(question.id)
+            )
             if question.response_type == RESPONSE_TYPE_RATING_1_5:
                 choices = [("", "---------")]
                 for value in range(1, 6):
-                    label = rubric_labels.get(str(value), str(value))
-                    choices.append((value, f"{value} - {label}"))
+                    choice_label = rubric_labels.get(str(value), str(value))
+                    choices.append((value, f"{value} - {choice_label}"))
                 self.fields[field_name] = forms.TypedChoiceField(
                     choices=choices,
                     coerce=int,
                     empty_value=None,
                     required=required,
-                    label=question.prompt,
+                    label=field_label,
                     help_text=question.help_text,
                 )
             elif question.response_type == RESPONSE_TYPE_TEXT:
                 self.fields[field_name] = forms.CharField(
                     required=required,
-                    label=question.prompt,
+                    label=field_label,
                     help_text=question.help_text,
                     widget=forms.Textarea(attrs={"rows": 4}),
                 )
             else:
-                self.fields[field_name] = forms.CharField(required=False, label=question.prompt, disabled=True)
+                self.fields[field_name] = forms.CharField(
+                    required=False,
+                    label=field_label,
+                    disabled=True,
+                )
             self.fields[field_name].initial = initial
 
     @staticmethod
@@ -52,7 +65,11 @@ class CoachAssessmentForm(forms.Form):
         if not response:
             return None
         if question.response_type == RESPONSE_TYPE_RATING_1_5:
-            return int(response.numeric_value) if response.numeric_value is not None else None
+            return (
+                int(response.numeric_value)
+                if response.numeric_value is not None
+                else None
+            )
         if question.response_type == RESPONSE_TYPE_TEXT:
             return response.text_value
         return response.raw_value
@@ -61,8 +78,6 @@ class CoachAssessmentForm(forms.Form):
         payload = []
         for question in self.questions:
             value = self.cleaned_data.get(self.field_name(question))
-            if value in {"", None}:
-                continue
             payload.append({"question": question, "value": value})
         return payload
 
diff --git a/analytics/migrations/0005_alter_observationquestion_is_required.py b/analytics/migrations/0005_alter_observationquestion_is_required.py
new file mode 100644
index 0000000..2679565
--- /dev/null
+++ b/analytics/migrations/0005_alter_observationquestion_is_required.py
@@ -0,0 +1,18 @@
+# Generated by Django 4.2.30 on 2026-07-24 02:21
+
+from django.db import migrations, models
+
+
+class Migration(migrations.Migration):
+
+    dependencies = [
+        ("analytics", "0004_evaluationcycle_season_and_more"),
+    ]
+
+    operations = [
+        migrations.AlterField(
+            model_name="observationquestion",
+            name="is_required",
+            field=models.BooleanField(default=True),
+        ),
+    ]
diff --git a/analytics/models.py b/analytics/models.py
index 27de1f4..485dfd8 100644
--- a/analytics/models.py
+++ b/analytics/models.py
@@ -9,7 +9,6 @@ from django.db.models import Q
 from django.utils import timezone
 from django.utils.text import slugify
 
-
 OBSERVATION_TYPE_COACH_ASSESSMENT = "coach_assessment"
 
 RESPONSE_TYPE_RATING_1_5 = "rating_1_5"
@@ -67,7 +66,9 @@ class TimeStampedModel(models.Model):
         abstract = True
 
 
-def unique_slug_for_model(instance, source_value: str, slug_field: str = "slug", max_length: int = 180) -> str:
+def unique_slug_for_model(
+    instance, source_value: str, slug_field: str = "slug", max_length: int = 180
+) -> str:
     base_slug = slugify(source_value) or "item"
     slug = base_slug[:max_length]
     counter = 2
@@ -131,7 +132,9 @@ class EvaluatorRole(TimeStampedModel):
 
 
 class ObservationQuestionSet(TimeStampedModel):
-    observation_type = models.ForeignKey(ObservationType, on_delete=models.PROTECT, related_name="question_sets")
+    observation_type = models.ForeignKey(
+        ObservationType, on_delete=models.PROTECT, related_name="question_sets"
+    )
     name = models.CharField(max_length=160)
     version = models.PositiveIntegerField(default=1)
     description = models.TextField(blank=True)
@@ -144,7 +147,10 @@ class ObservationQuestionSet(TimeStampedModel):
     class Meta:
         ordering = ["observation_type__key", "-version"]
         constraints = [
-            models.UniqueConstraint(fields=["observation_type", "version"], name="analytics_unique_question_set_version"),
+            models.UniqueConstraint(
+                fields=["observation_type", "version"],
+                name="analytics_unique_question_set_version",
+            ),
         ]
         indexes = [
             models.Index(fields=["observation_type", "is_active"]),
@@ -198,10 +204,13 @@ class EvaluationCycle(TimeStampedModel):
     def clean(self):
         if (
             self.coach_assessment_question_set_id
-            and self.coach_assessment_question_set.observation_type.key != OBSERVATION_TYPE_COACH_ASSESSMENT
+            and self.coach_assessment_question_set.observation_type.key
+            != OBSERVATION_TYPE_COACH_ASSESSMENT
         ):
             raise ValidationError(
-                {"coach_assessment_question_set": "Coach assessment cycles must use a coach-assessment question set."}
+                {
+                    "coach_assessment_question_set": "Coach assessment cycles must use a coach-assessment question set."
+                }
             )
 
     def __str__(self) -> str:
@@ -209,24 +218,33 @@ class EvaluationCycle(TimeStampedModel):
 
 
 class ObservationQuestion(TimeStampedModel):
-    question_set = models.ForeignKey(ObservationQuestionSet, on_delete=models.CASCADE, related_name="questions")
+    question_set = models.ForeignKey(
+        ObservationQuestionSet, on_delete=models.CASCADE, related_name="questions"
+    )
     key = models.SlugField(max_length=120)
     prompt = models.CharField(max_length=255)
     help_text = models.TextField(blank=True)
     category = models.CharField(max_length=80, blank=True)
     response_type = models.CharField(max_length=40, choices=RESPONSE_TYPE_CHOICES)
     display_order = models.PositiveIntegerField(default=0)
-    is_required = models.BooleanField(default=False)
+    is_required = models.BooleanField(default=True)
     is_active = models.BooleanField(default=True)
-    min_numeric_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
-    max_numeric_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
+    min_numeric_value = models.DecimalField(
+        max_digits=6, decimal_places=2, null=True, blank=True
+    )
+    max_numeric_value = models.DecimalField(
+        max_digits=6, decimal_places=2, null=True, blank=True
+    )
     choices = models.JSONField(default=list, blank=True)
     metadata = models.JSONField(default=dict, blank=True)
 
     class Meta:
         ordering = ["question_set", "display_order", "id"]
         constraints = [
-            models.UniqueConstraint(fields=["question_set", "key"], name="analytics_unique_question_key_per_set"),
+            models.UniqueConstraint(
+                fields=["question_set", "key"],
+                name="analytics_unique_question_key_per_set",
+            ),
         ]
         indexes = [
             models.Index(fields=["question_set", "display_order"]),
@@ -239,8 +257,12 @@ class ObservationQuestion(TimeStampedModel):
 
 
 class Observation(TimeStampedModel):
-    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="observations")
-    evaluation_cycle = models.ForeignKey(EvaluationCycle, on_delete=models.PROTECT, related_name="observations")
+    player = models.ForeignKey(
+        "players.Player", on_delete=models.CASCADE, related_name="observations"
+    )
+    evaluation_cycle = models.ForeignKey(
+        EvaluationCycle, on_delete=models.PROTECT, related_name="observations"
+    )
     season = models.ForeignKey(
         "seasons.Season",
         null=True,
@@ -262,10 +284,16 @@ class Observation(TimeStampedModel):
         on_delete=models.PROTECT,
         related_name="observations",
     )
-    observation_type = models.ForeignKey(ObservationType, on_delete=models.PROTECT, related_name="observations")
+    observation_type = models.ForeignKey(
+        ObservationType, on_delete=models.PROTECT, related_name="observations"
+    )
     observation_type_key = models.CharField(max_length=80, editable=False)
-    question_set = models.ForeignKey(ObservationQuestionSet, on_delete=models.PROTECT, related_name="observations")
-    source = models.ForeignKey(ObservationSource, on_delete=models.PROTECT, related_name="observations")
+    question_set = models.ForeignKey(
+        ObservationQuestionSet, on_delete=models.PROTECT, related_name="observations"
+    )
+    source = models.ForeignKey(
+        ObservationSource, on_delete=models.PROTECT, related_name="observations"
+    )
     evaluator = models.ForeignKey(
         settings.AUTH_USER_MODEL,
         null=True,
@@ -287,15 +315,29 @@ class Observation(TimeStampedModel):
         choices=EVALUATION_PERSPECTIVE_CHOICES,
         default=EVALUATION_PERSPECTIVE_GUEST,
     )
-    status = models.CharField(max_length=40, choices=OBSERVATION_STATUS_CHOICES, default=OBSERVATION_STATUS_DRAFT)
+    status = models.CharField(
+        max_length=40,
+        choices=OBSERVATION_STATUS_CHOICES,
+        default=OBSERVATION_STATUS_DRAFT,
+    )
     submitted_at = models.DateTimeField(null=True, blank=True)
     season_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
     season_key_snapshot = models.CharField(max_length=80, blank=True, editable=False)
-    player_team_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
-    player_division_snapshot = models.CharField(max_length=80, blank=True, editable=False)
-    evaluator_team_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
-    evaluator_division_snapshot = models.CharField(max_length=80, blank=True, editable=False)
-    evaluator_assignment_role_snapshot = models.CharField(max_length=80, blank=True, editable=False)
+    player_team_name_snapshot = models.CharField(
+        max_length=120, blank=True, editable=False
+    )
+    player_division_snapshot = models.CharField(
+        max_length=80, blank=True, editable=False
+    )
+    evaluator_team_name_snapshot = models.CharField(
+        max_length=120, blank=True, editable=False
+    )
+    evaluator_division_snapshot = models.CharField(
+        max_length=80, blank=True, editable=False
+    )
+    evaluator_assignment_role_snapshot = models.CharField(
+        max_length=80, blank=True, editable=False
+    )
     notes = models.TextField(blank=True)
     source_metadata = models.JSONField(default=dict, blank=True)
     metadata = models.JSONField(default=dict, blank=True)
@@ -304,12 +346,26 @@ class Observation(TimeStampedModel):
         ordering = ["-submitted_at", "-created_at", "-id"]
         constraints = [
             models.UniqueConstraint(
-                fields=["player", "evaluation_cycle", "observation_type_key", "evaluator", "evaluation_perspective"],
-                condition=Q(observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT, evaluator__isnull=False),
+                fields=[
+                    "player",
+                    "evaluation_cycle",
+                    "observation_type_key",
+                    "evaluator",
+                    "evaluation_perspective",
+                ],
+                condition=Q(
+                    observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
+                    evaluator__isnull=False,
+                ),
                 name="analytics_unique_coach_assessment_per_perspective",
             ),
             models.UniqueConstraint(
-                fields=["player", "evaluation_cycle", "observation_type_key", "evaluation_perspective"],
+                fields=[
+                    "player",
+                    "evaluation_cycle",
+                    "observation_type_key",
+                    "evaluation_perspective",
+                ],
                 condition=Q(
                     observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
                     evaluation_perspective=EVALUATION_PERSPECTIVE_SELF,
@@ -332,19 +388,42 @@ class Observation(TimeStampedModel):
 
     def clean(self):
         errors = {}
-        if self.evaluation_cycle_id and self.season_id and self.evaluation_cycle.season_id:
+        if (
+            self.evaluation_cycle_id
+            and self.season_id
+            and self.evaluation_cycle.season_id
+        ):
             if self.evaluation_cycle.season_id != self.season_id:
-                errors["season"] = "Observation season must match the evaluation cycle season."
+                errors["season"] = (
+                    "Observation season must match the evaluation cycle season."
+                )
         if self.player_roster_membership_id:
             if self.player_roster_membership.player_id != self.player_id:
-                errors["player_roster_membership"] = "Player roster membership must belong to the observation player."
-            if self.season_id and self.player_roster_membership.season.id != self.season_id:
-                errors["player_roster_membership"] = "Player roster membership must belong to the observation season."
+                errors["player_roster_membership"] = (
+                    "Player roster membership must belong to the observation player."
+                )
+            if (
+                self.season_id
+                and self.player_roster_membership.season.id != self.season_id
+            ):
+                errors["player_roster_membership"] = (
+                    "Player roster membership must belong to the observation season."
+                )
         if self.evaluator_coach_assignment_id:
-            if self.evaluator_id and self.evaluator_coach_assignment.user_id != self.evaluator_id:
-                errors["evaluator_coach_assignment"] = "Evaluator coach assignment must belong to the evaluator."
-            if self.season_id and self.evaluator_coach_assignment.season.id != self.season_id:
-                errors["evaluator_coach_assignment"] = "Evaluator coach assignment must belong to the observation season."
+            if (
+                self.evaluator_id
+                and self.evaluator_coach_assignment.user_id != self.evaluator_id
+            ):
+                errors["evaluator_coach_assignment"] = (
+                    "Evaluator coach assignment must belong to the evaluator."
+                )
+            if (
+                self.season_id
+                and self.evaluator_coach_assignment.season.id != self.season_id
+            ):
+                errors["evaluator_coach_assignment"] = (
+                    "Evaluator coach assignment must belong to the observation season."
+                )
         if errors:
             raise ValidationError(errors)
 
@@ -363,14 +442,22 @@ class Observation(TimeStampedModel):
 
     @property
     def evaluation_perspective_label(self) -> str:
-        return EVALUATION_PERSPECTIVE_LABELS.get(self.evaluation_perspective, "Evaluation")
+        return EVALUATION_PERSPECTIVE_LABELS.get(
+            self.evaluation_perspective, "Evaluation"
+        )
 
 
 class ObservationResponse(TimeStampedModel):
-    observation = models.ForeignKey(Observation, on_delete=models.CASCADE, related_name="responses")
-    question = models.ForeignKey(ObservationQuestion, on_delete=models.PROTECT, related_name="responses")
+    observation = models.ForeignKey(
+        Observation, on_delete=models.CASCADE, related_name="responses"
+    )
+    question = models.ForeignKey(
+        ObservationQuestion, on_delete=models.PROTECT, related_name="responses"
+    )
     response_type = models.CharField(max_length=40, choices=RESPONSE_TYPE_CHOICES)
-    numeric_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
+    numeric_value = models.DecimalField(
+        max_digits=8, decimal_places=2, null=True, blank=True
+    )
     text_value = models.TextField(blank=True)
     boolean_value = models.BooleanField(null=True, blank=True)
     selected_choice = models.CharField(max_length=120, blank=True)
@@ -382,7 +469,10 @@ class ObservationResponse(TimeStampedModel):
     class Meta:
         ordering = ["question__display_order", "id"]
         constraints = [
-            models.UniqueConstraint(fields=["observation", "question"], name="analytics_unique_response_per_question"),
+            models.UniqueConstraint(
+                fields=["observation", "question"],
+                name="analytics_unique_response_per_question",
+            ),
         ]
         indexes = [
             models.Index(fields=["observation", "question"]),
@@ -393,14 +483,20 @@ class ObservationResponse(TimeStampedModel):
     def clean(self):
         if self.response_type == RESPONSE_TYPE_RATING_1_5:
             if self.numeric_value is None:
-                raise ValidationError({"numeric_value": "A 1-5 rating response requires a numeric value."})
+                raise ValidationError(
+                    {"numeric_value": "A 1-5 rating response requires a numeric value."}
+                )
             if (
                 not self.numeric_value.is_finite()
                 or self.numeric_value != self.numeric_value.to_integral_value()
                 or self.numeric_value < Decimal("1")
                 or self.numeric_value > Decimal("5")
             ):
-                raise ValidationError({"numeric_value": "Rating responses must be one of 1, 2, 3, 4, or 5."})
+                raise ValidationError(
+                    {
+                        "numeric_value": "Rating responses must be one of 1, 2, 3, 4, or 5."
+                    }
+                )
 
     def save(self, *args, **kwargs):
         if not self.response_type and self.question_id:
diff --git a/analytics/services/evaluation_access_service.py b/analytics/services/evaluation_access_service.py
index 2e7c34b..11fd4de 100644
--- a/analytics/services/evaluation_access_service.py
+++ b/analytics/services/evaluation_access_service.py
@@ -63,6 +63,7 @@ class MyEvaluationSummary:
 class MyEvaluationQuestionResponse:
     question_prompt: str
     category: str
+    is_required: bool
     numeric_value: object = None
     text_value: str = ""
 
@@ -88,15 +89,22 @@ def get_evaluation_target_list(user, params) -> EvaluationTargetList:
     division = (params.get("division") or "").strip()
     team = (params.get("team") or "").strip()
     if not cycle:
-        return EvaluationTargetList(cycle=None, player_statuses=[], query=query, division=division, team=team)
+        return EvaluationTargetList(
+            cycle=None, player_statuses=[], query=query, division=division, team=team
+        )
 
-    targets = list(list_memberships_for_assessment(cycle, query=query, division=division, team=team))
+    targets = list(
+        list_memberships_for_assessment(
+            cycle, query=query, division=division, team=team
+        )
+    )
     player_statuses = [
         EvaluationTargetStatus(
             player=item.player,
             observation=item.observation,
             status=item.status,
-            can_evaluate=item.status != "unavailable" and can_evaluate_player(user, item.player),
+            can_evaluate=item.status != "unavailable"
+            and can_evaluate_player(user, item.player),
             player_roster_membership=item.player_roster_membership,
             player_team=item.player_team,
             player_division=item.player_division,
@@ -113,20 +121,26 @@ def get_evaluation_target_list(user, params) -> EvaluationTargetList:
     )
 
 
-def get_existing_evaluation_for_player(user, player: Player, cycle: EvaluationCycle) -> Observation | None:
+def get_existing_evaluation_for_player(
+    user, player: Player, cycle: EvaluationCycle
+) -> Observation | None:
     """Return the evaluator's existing coach-assessment observation for a target player and cycle."""
     return get_existing_coach_assessment(player, cycle, user)
 
 
 @transaction.atomic
-def get_or_create_evaluation_for_player(user, player: Player, cycle: EvaluationCycle, player_roster_membership=None) -> Observation:
+def get_or_create_evaluation_for_player(
+    user, player: Player, cycle: EvaluationCycle, player_roster_membership=None
+) -> Observation:
     """Return or create the evaluator's draft evaluation for a target player."""
     if not can_evaluate_player(user, player):
         raise PermissionDenied("You cannot evaluate this player.")
     existing = get_existing_evaluation_for_player(user, player, cycle)
     if existing and existing.status == OBSERVATION_STATUS_SUBMITTED:
         return existing
-    return get_or_create_draft_coach_assessment(player, cycle, user, player_roster_membership=player_roster_membership)
+    return get_or_create_draft_coach_assessment(
+        player, cycle, user, player_roster_membership=player_roster_membership
+    )
 
 
 def active_evaluation_cycle() -> EvaluationCycle | None:
@@ -139,7 +153,9 @@ def self_linked_players_for_user(user) -> list[Player]:
     return list(get_self_linked_players(user).filter(is_active=True))
 
 
-def get_my_evaluations(user, player: Player | None = None) -> tuple[list[Player], list[MyEvaluationSummary]]:
+def get_my_evaluations(
+    user, player: Player | None = None
+) -> tuple[list[Player], list[MyEvaluationSummary]]:
     """Return submitted evaluations about the current user's self-linked player records."""
     if player is not None and not can_view_my_evaluations(user, player=player):
         raise PermissionDenied("You cannot view evaluations for this player.")
@@ -147,7 +163,9 @@ def get_my_evaluations(user, player: Player | None = None) -> tuple[list[Player]
     if not players:
         return [], []
     observations = (
-        Observation.objects.select_related("player", "evaluation_cycle", "evaluator_role")
+        Observation.objects.select_related(
+            "player", "evaluation_cycle", "evaluator_role"
+        )
         .filter(
             player__in=players,
             observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
@@ -172,23 +190,36 @@ def get_my_evaluations(user, player: Player | None = None) -> tuple[list[Player]
 def get_my_evaluation_detail(user, observation_id: int) -> MyEvaluationDetail:
     """Return a player-safe submitted evaluation detail view."""
     observation = (
-        Observation.objects.select_related("player", "evaluation_cycle", "evaluator_role")
+        Observation.objects.select_related(
+            "player", "evaluation_cycle", "evaluator_role", "question_set"
+        )
+        .prefetch_related("responses__question")
         .get(pk=observation_id)
     )
     if not can_view_my_evaluation_detail(user, observation):
         raise PermissionDenied("You cannot view this evaluation.")
+    responses_by_question = {
+        response.question_id: response for response in observation.responses.all()
+    }
     responses = [
         MyEvaluationQuestionResponse(
-            question_prompt=response.question.prompt,
-            category=response.question.category or "Questions",
-            numeric_value=response.numeric_value,
-            text_value=response.text_value,
-        )
-        for response in observation.responses.select_related("question").order_by(
-            "question__display_order",
-            "question_id",
-            "id",
+            question_prompt=question.prompt,
+            category=question.category or "Questions",
+            is_required=question.is_required,
+            numeric_value=(
+                responses_by_question[question.id].numeric_value
+                if question.id in responses_by_question
+                else None
+            ),
+            text_value=(
+                responses_by_question[question.id].text_value
+                if question.id in responses_by_question
+                else ""
+            ),
         )
+        for question in observation.question_set.questions.filter(
+            is_active=True
+        ).order_by("display_order", "id")
     ]
     return MyEvaluationDetail(
         observation_id=observation.id,
diff --git a/analytics/services/evaluation_review_service.py b/analytics/services/evaluation_review_service.py
index 17fba2c..b29d8f4 100644
--- a/analytics/services/evaluation_review_service.py
+++ b/analytics/services/evaluation_review_service.py
@@ -14,7 +14,10 @@ from analytics.models import (
     EvaluatorRole,
     Observation,
 )
-from analytics.services.permissions import can_review_submitted_evaluations, can_view_evaluation_review_detail
+from analytics.services.permissions import (
+    can_review_submitted_evaluations,
+    can_view_evaluation_review_detail,
+)
 from seasons.models import Season
 
 
@@ -51,6 +54,7 @@ class EvaluationReviewRow:
 class EvaluationReviewQuestionResponse:
     question_prompt: str
     category: str
+    is_required: bool
     numeric_value: object = None
     text_value: str = ""
 
@@ -105,7 +109,9 @@ def _display_user(user) -> str:
 
 def submitted_evaluation_queryset(filters: EvaluationReviewFilters | None = None):
     queryset = (
-        Observation.objects.select_related("player", "evaluation_cycle", "season", "evaluator", "evaluator_role")
+        Observation.objects.select_related(
+            "player", "evaluation_cycle", "season", "evaluator", "evaluator_role"
+        )
         .filter(
             observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
             status=OBSERVATION_STATUS_SUBMITTED,
@@ -134,13 +140,22 @@ def submitted_evaluation_queryset(filters: EvaluationReviewFilters | None = None
         queryset = queryset.filter(evaluation_perspective=filters.perspective)
     if filters.team:
         queryset = queryset.filter(
-            Q(player_team_name_snapshot__gt="", player_team_name_snapshot__icontains=filters.team)
+            Q(
+                player_team_name_snapshot__gt="",
+                player_team_name_snapshot__icontains=filters.team,
+            )
             | Q(player_team_name_snapshot="", player__team_name__icontains=filters.team)
         )
     if filters.division:
         queryset = queryset.filter(
-            Q(player_division_snapshot__gt="", player_division_snapshot__icontains=filters.division)
-            | Q(player_division_snapshot="", player__division__icontains=filters.division)
+            Q(
+                player_division_snapshot__gt="",
+                player_division_snapshot__icontains=filters.division,
+            )
+            | Q(
+                player_division_snapshot="",
+                player__division__icontains=filters.division,
+            )
         )
     if filters.season.isdigit():
         queryset = queryset.filter(season_id=int(filters.season))
@@ -166,9 +181,16 @@ def get_evaluation_review_list(user, params) -> EvaluationReviewList:
         EvaluationReviewRow(
             observation_id=observation.id,
             player_name=observation.player.display_name,
-            season_name=observation.season_name_snapshot or (observation.season.name if observation.season_id else "Legacy / No Season"),
-            player_team=observation.player_team_name_snapshot or observation.player.team_name,
-            player_division=observation.player_division_snapshot or observation.player.division,
+            season_name=observation.season_name_snapshot
+            or (
+                observation.season.name
+                if observation.season_id
+                else "Legacy / No Season"
+            ),
+            player_team=observation.player_team_name_snapshot
+            or observation.player.team_name,
+            player_division=observation.player_division_snapshot
+            or observation.player.division,
             evaluator_name=_display_user(observation.evaluator),
             evaluator_role_name=observation.evaluator_role_name or "Evaluator",
             evaluation_perspective_label=observation.evaluation_perspective_label,
@@ -181,36 +203,58 @@ def get_evaluation_review_list(user, params) -> EvaluationReviewList:
         filters=filters,
         rows=rows,
         total_count=len(rows),
-        seasons=Season.objects.filter(is_active=True).order_by("-is_current", "-starts_on", "name"),
-        cycles=EvaluationCycle.objects.filter(is_active=True).order_by("-starts_on", "-created_at", "name"),
+        seasons=Season.objects.filter(is_active=True).order_by(
+            "-is_current", "-starts_on", "name"
+        ),
+        cycles=EvaluationCycle.objects.filter(is_active=True).order_by(
+            "-starts_on", "-created_at", "name"
+        ),
         evaluator_roles=EvaluatorRole.objects.filter(is_active=True).order_by("name"),
         perspective_choices=EVALUATION_PERSPECTIVE_CHOICES,
     )
 
 
 def get_evaluation_review_detail(user, observation_id: int) -> EvaluationReviewDetail:
-    observation = submitted_evaluation_queryset().get(pk=observation_id)
+    observation = (
+        submitted_evaluation_queryset()
+        .select_related("question_set")
+        .prefetch_related("responses__question")
+        .get(pk=observation_id)
+    )
     if not can_view_evaluation_review_detail(user, observation):
         raise PermissionDenied("You cannot review this evaluation.")
+    responses_by_question = {
+        response.question_id: response for response in observation.responses.all()
+    }
     responses = [
         EvaluationReviewQuestionResponse(
-            question_prompt=response.question.prompt,
-            category=response.question.category or "Questions",
-            numeric_value=response.numeric_value,
-            text_value=response.text_value,
-        )
-        for response in observation.responses.select_related("question").order_by(
-            "question__display_order",
-            "question_id",
-            "id",
+            question_prompt=question.prompt,
+            category=question.category or "Questions",
+            is_required=question.is_required,
+            numeric_value=(
+                responses_by_question[question.id].numeric_value
+                if question.id in responses_by_question
+                else None
+            ),
+            text_value=(
+                responses_by_question[question.id].text_value
+                if question.id in responses_by_question
+                else ""
+            ),
         )
+        for question in observation.question_set.questions.filter(
+            is_active=True
+        ).order_by("display_order", "id")
     ]
     return EvaluationReviewDetail(
         observation_id=observation.id,
         player_name=observation.player.display_name,
-        season_name=observation.season_name_snapshot or (observation.season.name if observation.season_id else "Legacy / No Season"),
-        player_team=observation.player_team_name_snapshot or observation.player.team_name,
-        player_division=observation.player_division_snapshot or observation.player.division,
+        season_name=observation.season_name_snapshot
+        or (observation.season.name if observation.season_id else "Legacy / No Season"),
+        player_team=observation.player_team_name_snapshot
+        or observation.player.team_name,
+        player_division=observation.player_division_snapshot
+        or observation.player.division,
         evaluator_name=_display_user(observation.evaluator),
         evaluator_role_name=observation.evaluator_role_name or "Evaluator",
         evaluation_perspective_label=observation.evaluation_perspective_label,
diff --git a/analytics/services/observation_service.py b/analytics/services/observation_service.py
index 3b33362..9687e94 100644
--- a/analytics/services/observation_service.py
+++ b/analytics/services/observation_service.py
@@ -25,6 +25,15 @@ from analytics.models import (
     ObservationSource,
     ObservationType,
 )
+from analytics.services.evaluation_context_service import (
+    apply_evaluation_context,
+    resolve_evaluation_context,
+)
+from analytics.services.permissions import (
+    can_evaluate_player,
+    evaluation_perspective_for_user,
+    evaluator_role_for_user,
+)
 from analytics.services.question_service import (
     SOURCE_COACH,
     get_active_questions,
@@ -32,10 +41,8 @@ from analytics.services.question_service import (
     get_default_coach_assessment_question_set,
     get_question_set_for_cycle,
 )
-from analytics.services.permissions import can_evaluate_player, evaluation_perspective_for_user, evaluator_role_for_user
 from players.models import Player
 from seasons.models import CoachSeasonAssignment, PlayerRosterMembership
-from analytics.services.evaluation_context_service import apply_evaluation_context, resolve_evaluation_context
 
 
 @dataclass
@@ -45,7 +52,9 @@ class ObservationCreateResult:
     responses_updated: int = 0
 
 
-def _snapshot_role(observation: Observation, evaluator_role: EvaluatorRole | None) -> None:
+def _snapshot_role(
+    observation: Observation, evaluator_role: EvaluatorRole | None
+) -> None:
     if evaluator_role:
         observation.evaluator_role = evaluator_role
         observation.evaluator_role_key = evaluator_role.key
@@ -73,7 +82,9 @@ def _validate_unique_coach_assessment(
     if exclude_observation:
         queryset = queryset.exclude(pk=exclude_observation.pk)
     if queryset.exists():
-        raise ValidationError("This evaluator already has a coach assessment for this player and evaluation cycle.")
+        raise ValidationError(
+            "This evaluator already has a coach assessment for this player and evaluation cycle."
+        )
     if evaluation_perspective == EVALUATION_PERSPECTIVE_SELF:
         self_queryset = Observation.objects.filter(
             player=player,
@@ -84,7 +95,9 @@ def _validate_unique_coach_assessment(
         if exclude_observation:
             self_queryset = self_queryset.exclude(pk=exclude_observation.pk)
         if self_queryset.exists():
-            raise ValidationError("This player already has a self evaluation for this evaluation cycle.")
+            raise ValidationError(
+                "This player already has a self evaluation for this evaluation cycle."
+            )
 
 
 def _coerce_rating(value) -> Decimal:
@@ -102,12 +115,18 @@ def _coerce_rating(value) -> Decimal:
     return numeric
 
 
-def _validate_question_set_for_type(question_set: ObservationQuestionSet, observation_type: ObservationType) -> None:
+def _validate_question_set_for_type(
+    question_set: ObservationQuestionSet, observation_type: ObservationType
+) -> None:
     if question_set.observation_type_id != observation_type.id:
-        raise ValidationError("Question set must belong to the selected observation type.")
+        raise ValidationError(
+            "Question set must belong to the selected observation type."
+        )
 
 
-def _response_defaults(question: ObservationQuestion, value, extra: dict[str, Any] | None = None) -> dict[str, Any]:
+def _response_defaults(
+    question: ObservationQuestion, value, extra: dict[str, Any] | None = None
+) -> dict[str, Any]:
     extra = extra or {}
     defaults = {
         "response_type": question.response_type,
@@ -125,10 +144,28 @@ def _response_defaults(question: ObservationQuestion, value, extra: dict[str, An
     elif question.response_type == RESPONSE_TYPE_TEXT:
         defaults["text_value"] = "" if value is None else str(value)
     else:
-        raise ValidationError(f"Response type {question.response_type} is not implemented in Version 1.")
+        raise ValidationError(
+            f"Response type {question.response_type} is not implemented in Version 1."
+        )
     return defaults
 
 
+def _is_blank_response_value(value) -> bool:
+    return value is None or (isinstance(value, str) and value.strip() == "")
+
+
+def _response_has_value(response: ObservationResponse) -> bool:
+    if response.response_type == RESPONSE_TYPE_RATING_1_5:
+        return response.numeric_value is not None
+    if response.response_type == RESPONSE_TYPE_TEXT:
+        return bool(response.text_value.strip())
+    return bool(
+        response.raw_value.strip()
+        or response.selected_choice
+        or response.boolean_value is not None
+    )
+
+
 @transaction.atomic
 def create_observation(
     *,
@@ -153,7 +190,9 @@ def create_observation(
         if not can_evaluate_player(evaluator, player):
             raise ValidationError("This evaluator cannot evaluate this player.")
         evaluator_role = evaluator_role or evaluator_role_for_user(evaluator)
-        evaluation_perspective = evaluation_perspective or evaluation_perspective_for_user(evaluator, player)
+        evaluation_perspective = (
+            evaluation_perspective or evaluation_perspective_for_user(evaluator, player)
+        )
     else:
         evaluation_perspective = evaluation_perspective or EVALUATION_PERSPECTIVE_GUEST
     _validate_unique_coach_assessment(
@@ -193,7 +232,9 @@ def create_observation(
     try:
         observation.save()
     except IntegrityError as exc:
-        raise ValidationError("This observation would duplicate an existing coach assessment.") from exc
+        raise ValidationError(
+            "This observation would duplicate an existing coach assessment."
+        ) from exc
     return observation
 
 
@@ -219,10 +260,14 @@ def create_coach_assessment_observation(
     if evaluator is None:
         raise ValidationError("Coach assessments require an evaluator.")
     observation_type = get_coach_assessment_type()
-    question_set = question_set or get_question_set_for_cycle(evaluation_cycle, observation_type)
+    question_set = question_set or get_question_set_for_cycle(
+        evaluation_cycle, observation_type
+    )
     source = source or ObservationSource.objects.get(key=SOURCE_COACH)
     evaluator_role = evaluator_role or evaluator_role_for_user(evaluator)
-    evaluation_perspective = evaluation_perspective or evaluation_perspective_for_user(evaluator, player)
+    evaluation_perspective = evaluation_perspective or evaluation_perspective_for_user(
+        evaluator, player
+    )
     observation = create_observation(
         player=player,
         evaluation_cycle=evaluation_cycle,
@@ -247,33 +292,56 @@ def create_coach_assessment_observation(
     return result
 
 
-def _question_for_response(observation: Observation, question_ref) -> ObservationQuestion:
+def _question_for_response(
+    observation: Observation, question_ref
+) -> ObservationQuestion:
     if isinstance(question_ref, ObservationQuestion):
         question = question_ref
     elif isinstance(question_ref, int):
         question = ObservationQuestion.objects.get(pk=question_ref)
     else:
-        question = ObservationQuestion.objects.get(question_set=observation.question_set, key=str(question_ref))
+        question = ObservationQuestion.objects.get(
+            question_set=observation.question_set, key=str(question_ref)
+        )
     if question.question_set_id != observation.question_set_id:
-        raise ValidationError("Responses can only be saved for questions in the observation question set.")
+        raise ValidationError(
+            "Responses can only be saved for questions in the observation question set."
+        )
     return question
 
 
 @transaction.atomic
-def save_observation_responses(observation: Observation, responses: dict[Any, Any] | list[dict[str, Any]]) -> tuple[int, int]:
+def save_observation_responses(
+    observation: Observation, responses: dict[Any, Any] | list[dict[str, Any]]
+) -> tuple[int, int]:
     """Create or update responses for an observation."""
     locked_observation = Observation.objects.select_for_update().get(pk=observation.pk)
     created_count = 0
     updated_count = 0
 
     if isinstance(responses, dict):
-        response_items = [{"question": question_ref, "value": value} for question_ref, value in responses.items()]
+        response_items = [
+            {"question": question_ref, "value": value}
+            for question_ref, value in responses.items()
+        ]
     else:
         response_items = responses
 
     for response_input in response_items:
-        question = _question_for_response(locked_observation, response_input["question"])
-        defaults = _response_defaults(question, response_input.get("value"), extra=response_input)
+        question = _question_for_response(
+            locked_observation, response_input["question"]
+        )
+        value = response_input.get("value")
+        if _is_blank_response_value(value):
+            deleted_count, _ = ObservationResponse.objects.filter(
+                observation=locked_observation,
+                question=question,
+            ).delete()
+            updated_count += int(bool(deleted_count))
+            continue
+        defaults = _response_defaults(
+            question, response_input.get("value"), extra=response_input
+        )
         _, created = ObservationResponse.objects.update_or_create(
             observation=locked_observation,
             question=question,
@@ -290,12 +358,22 @@ def validate_required_responses(observation: Observation) -> None:
     if observation.observation_type_key != OBSERVATION_TYPE_COACH_ASSESSMENT:
         return
     required_question_ids = set(
-        observation.question_set.questions.filter(is_active=True, is_required=True).values_list("id", flat=True)
+        observation.question_set.questions.filter(
+            is_active=True, is_required=True
+        ).values_list("id", flat=True)
     )
-    answered_question_ids = set(observation.responses.filter(question_id__in=required_question_ids).values_list("question_id", flat=True))
+    answered_question_ids = {
+        response.question_id
+        for response in observation.responses.filter(
+            question_id__in=required_question_ids
+        )
+        if _response_has_value(response)
+    }
     missing_count = len(required_question_ids - answered_question_ids)
     if missing_count:
-        raise ValidationError(f"Coach assessment is missing {missing_count} required response(s).")
+        raise ValidationError(
+            f"Coach assessment is missing {missing_count} required response(s)."
+        )
 
 
 @transaction.atomic
diff --git a/analytics/templates/analytics/_assessment_question.html b/analytics/templates/analytics/_assessment_question.html
index c91a886..384d1c8 100644
--- a/analytics/templates/analytics/_assessment_question.html
+++ b/analytics/templates/analytics/_assessment_question.html
@@ -1,5 +1,6 @@
 <label>
     {{ field.label }}
+    {% if not question.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
     {{ field }}
     {% if field.help_text %}<span class="helptext">{{ field.help_text }}</span>{% endif %}
     {% for error in field.errors %}<span class="errorlist">{{ error }}</span>{% endfor %}
diff --git a/analytics/templates/analytics/assessment_detail.html b/analytics/templates/analytics/assessment_detail.html
index 032a869..8eccba8 100644
--- a/analytics/templates/analytics/assessment_detail.html
+++ b/analytics/templates/analytics/assessment_detail.html
@@ -20,6 +20,7 @@
             {% for item in group.questions %}
                 <div>
                     <strong>{{ item.question.prompt }}</strong>
+                    {% if not item.question.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
                     {% if item.response %}
                         {% if item.response.numeric_value %}
                             <span>{{ item.response.numeric_value|floatformat:0 }}</span>
diff --git a/analytics/templates/analytics/evaluation_review_detail.html b/analytics/templates/analytics/evaluation_review_detail.html
index d0d3849..b67afd7 100644
--- a/analytics/templates/analytics/evaluation_review_detail.html
+++ b/analytics/templates/analytics/evaluation_review_detail.html
@@ -31,6 +31,7 @@
             <h3>{{ response.category }}</h3>
             <div>
                 <strong>{{ response.question_prompt }}</strong>
+                {% if not response.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
                 {% if response.numeric_value %}
                     <span>{{ response.numeric_value|floatformat:0 }}</span>
                 {% elif response.text_value %}
diff --git a/analytics/templates/analytics/my_evaluation_detail.html b/analytics/templates/analytics/my_evaluation_detail.html
index cfbb502..b125db2 100644
--- a/analytics/templates/analytics/my_evaluation_detail.html
+++ b/analytics/templates/analytics/my_evaluation_detail.html
@@ -21,6 +21,7 @@
             <h3>{{ response.category }}</h3>
             <div>
                 <strong>{{ response.question_prompt }}</strong>
+                {% if not response.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
                 {% if response.numeric_value %}
                     <span>{{ response.numeric_value|floatformat:0 }}</span>
                 {% elif response.text_value %}
diff --git a/analytics/tests/test_coach_assessments.py b/analytics/tests/test_coach_assessments.py
index c9aac3d..e247374 100644
--- a/analytics/tests/test_coach_assessments.py
+++ b/analytics/tests/test_coach_assessments.py
@@ -8,6 +8,7 @@ from analytics.tests.helpers import (
     Decimal,
     EvaluationCycle,
     Observation,
+    ObservationResponse,
     Player,
     TestCase,
     User,
@@ -15,6 +16,8 @@ from analytics.tests.helpers import (
     create_coach_assessment_observation,
     create_season,
     ensure_default_coach_assessment_setup,
+    get_player_score_summary,
+    observation_metrics,
     patch,
     reverse,
     submit_observation,
@@ -73,6 +76,32 @@ class CoachAssessmentWorkflowTests(TestCase):
             form.fields[f"question_{question.id}"].label, "Edited dynamic question"
         )
 
+    def test_dynamic_form_marks_optional_questions_not_required(self):
+        optional_question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        optional_question.is_required = False
+        optional_question.save(update_fields=["is_required", "updated_at"])
+        required_question = (
+            self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5,
+                is_required=True,
+            )
+            .exclude(id=optional_question.id)
+            .first()
+        )
+
+        form = CoachAssessmentForm(
+            question_set=self.setup_result.question_set, require_required=True
+        )
+
+        self.assertFalse(form.fields[f"question_{optional_question.id}"].required)
+        self.assertTrue(form.fields[f"question_{required_question.id}"].required)
+        self.assertEqual(
+            form.fields[f"question_{optional_question.id}"].label,
+            f"{optional_question.prompt} (Optional)",
+        )
+
     def test_assessment_list_requires_login_and_lists_players(self):
         response = self.client.get(reverse("analytics:assessment-list"))
         self.assertEqual(response.status_code, 302)
@@ -187,6 +216,103 @@ class CoachAssessmentWorkflowTests(TestCase):
         self.assertIsNotNone(observation.submitted_at)
         self.assertEqual(observation.responses.count(), len(self.response_payload()))
 
+    def test_coach_can_submit_with_optional_question_blank(self):
+        optional_question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        optional_question.is_required = False
+        optional_question.save(update_fields=["is_required", "updated_at"])
+        self.client.force_login(self.coach)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+        data[f"question_{optional_question.id}"] = ""
+
+        response = self.client.post(
+            reverse(
+                "analytics:assessment-player", kwargs={"player_id": self.player.id}
+            ),
+            data,
+        )
+
+        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
+        score_summary = get_player_score_summary(self.player)
+        metrics = observation_metrics(cycle=self.cycle)
+        expected_rating_count = (
+            self.setup_result.question_set.questions.filter(
+                response_type=RESPONSE_TYPE_RATING_1_5
+            ).count()
+            - 1
+        )
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
+        self.assertFalse(
+            ObservationResponse.objects.filter(
+                observation=observation, question=optional_question
+            ).exists()
+        )
+        self.assertEqual(score_summary.rating_count, expected_rating_count)
+        self.assertEqual(
+            sum(row.count for row in metrics.by_category_average),
+            expected_rating_count,
+        )
+
+    def test_clearing_optional_draft_answer_removes_response(self):
+        optional_question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        optional_question.is_required = False
+        optional_question.save(update_fields=["is_required", "updated_at"])
+        self.client.force_login(self.coach)
+
+        self.client.post(
+            reverse(
+                "analytics:assessment-player", kwargs={"player_id": self.player.id}
+            ),
+            {"action": "save_draft", f"question_{optional_question.id}": "3"},
+        )
+        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
+        self.client.post(
+            reverse(
+                "analytics:assessment-edit", kwargs={"observation_id": observation.id}
+            ),
+            {"action": "save_draft", f"question_{optional_question.id}": ""},
+        )
+
+        self.assertFalse(
+            ObservationResponse.objects.filter(
+                observation=observation, question=optional_question
+            ).exists()
+        )
+
+    def test_assessment_detail_shows_unanswered_optional_question(self):
+        optional_question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        optional_question.is_required = False
+        optional_question.save(update_fields=["is_required", "updated_at"])
+        self.client.force_login(self.coach)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+        data[f"question_{optional_question.id}"] = ""
+        self.client.post(
+            reverse(
+                "analytics:assessment-player", kwargs={"player_id": self.player.id}
+            ),
+            data,
+        )
+        observation = Observation.objects.get(player=self.player, evaluator=self.coach)
+
+        response = self.client.get(
+            reverse(
+                "analytics:assessment-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+
+        self.assertContains(response, optional_question.prompt)
+        self.assertContains(response, "Optional")
+        self.assertContains(response, "Not answered")
+
     def test_submitted_assessment_redirects_instead_of_creating_duplicate(self):
         self.client.force_login(self.coach)
         data = {"action": "submit"}
diff --git a/analytics/tests/test_evaluation_review.py b/analytics/tests/test_evaluation_review.py
index 77f4749..c225163 100644
--- a/analytics/tests/test_evaluation_review.py
+++ b/analytics/tests/test_evaluation_review.py
@@ -177,6 +177,26 @@ class EvaluationReviewViewTests(TestCase):
         )
         self.assertNotContains(response, self.coach.email)
 
+    def test_review_detail_shows_unanswered_optional_questions(self):
+        optional_question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        optional_question.is_required = False
+        optional_question.save(update_fields=["is_required", "updated_at"])
+        observation = self.submitted_observation(note="Required answers only.")
+        self.client.force_login(self.coach)
+
+        response = self.client.get(
+            reverse(
+                "analytics:evaluation-review-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+
+        self.assertContains(response, optional_question.prompt)
+        self.assertContains(response, "Optional")
+        self.assertContains(response, "Not answered")
+
     def test_coach_review_access_rules(self):
         self.submitted_observation()
         for user in [self.player_user, self.parent, self.guest]:
diff --git a/analytics/tests/test_evaluation_submission.py b/analytics/tests/test_evaluation_submission.py
index c7fcd0d..916b203 100644
--- a/analytics/tests/test_evaluation_submission.py
+++ b/analytics/tests/test_evaluation_submission.py
@@ -259,6 +259,34 @@ class EvaluationAccessSubmissionViewTests(TestCase):
             observation.evaluation_perspective, EVALUATION_PERSPECTIVE_PEER
         )
 
+    def test_player_can_submit_with_optional_question_blank(self):
+        optional_question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        optional_question.is_required = False
+        optional_question.save(update_fields=["is_required", "updated_at"])
+        self.client.force_login(self.player_user)
+        data = {"action": "submit"}
+        data.update(self.response_payload())
+        data[f"question_{optional_question.id}"] = ""
+
+        response = self.client.post(
+            reverse(
+                "analytics:evaluation-player",
+                kwargs={"player_id": self.target_player.id},
+            ),
+            data,
+        )
+
+        observation = Observation.objects.get(
+            player=self.target_player, evaluator=self.player_user
+        )
+        self.assertEqual(response.status_code, 302)
+        self.assertEqual(observation.status, OBSERVATION_STATUS_SUBMITTED)
+        self.assertFalse(
+            observation.responses.filter(question=optional_question).exists()
+        )
+
     def test_player_self_evaluation_draft_resumes_and_submitted_duplicate_redirects(
         self,
     ):
diff --git a/analytics/tests/test_my_evaluations.py b/analytics/tests/test_my_evaluations.py
index 7269006..16a3f55 100644
--- a/analytics/tests/test_my_evaluations.py
+++ b/analytics/tests/test_my_evaluations.py
@@ -183,6 +183,34 @@ class MyEvaluationsViewTests(TestCase):
         self.assertEqual(detail.observation_id, observation.id)
         self.assertFalse(hasattr(detail, "observation"))
 
+    def test_my_evaluation_detail_shows_unanswered_optional_questions(self):
+        optional_question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        optional_question.is_required = False
+        optional_question.save(update_fields=["is_required", "updated_at"])
+        observation = self.submitted_observation(note="Required answers only.")
+        self.client.force_login(self.player_user)
+
+        response = self.client.get(
+            reverse(
+                "analytics:my-evaluation-detail",
+                kwargs={"observation_id": observation.id},
+            )
+        )
+        detail = get_my_evaluation_detail(self.player_user, observation.id)
+        optional_response = next(
+            item
+            for item in detail.responses
+            if item.question_prompt == optional_question.prompt
+        )
+
+        self.assertContains(response, optional_question.prompt)
+        self.assertContains(response, "Optional")
+        self.assertContains(response, "Not answered")
+        self.assertFalse(optional_response.is_required)
+        self.assertIsNone(optional_response.numeric_value)
+
     def test_my_evaluations_show_self_label_without_external_identity(self):
         self_observation = self.submitted_observation(
             player=self.player, evaluator=self.player_user, note="My reflection."
diff --git a/analytics/tests/test_observation_foundation.py b/analytics/tests/test_observation_foundation.py
index 280946c..4519a91 100644
--- a/analytics/tests/test_observation_foundation.py
+++ b/analytics/tests/test_observation_foundation.py
@@ -148,6 +148,16 @@ class AnalyticsObservationFoundationTests(TestCase):
         self.assertEqual(question.display_order, 99)
         self.assertFalse(question.is_required)
 
+    def test_new_questions_default_to_required(self):
+        question = ObservationQuestion.objects.create(
+            question_set=self.setup_result.question_set,
+            key="new_required_default",
+            prompt="New required default",
+            response_type=RESPONSE_TYPE_RATING_1_5,
+        )
+
+        self.assertTrue(question.is_required)
+
     def test_cycle_slug_generation_creates_unique_slugs(self):
         second_cycle = EvaluationCycle.objects.create(
             name=self.cycle.name, cycle_type="Coach Assessment"
@@ -465,6 +475,31 @@ class AnalyticsObservationFoundationTests(TestCase):
         self.assertEqual(updated, 1)
         self.assertEqual(response.numeric_value, Decimal("5.00"))
 
+    def test_blank_optional_response_deletes_existing_response(self):
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+        ).observation
+        question = self.setup_result.question_set.questions.filter(
+            response_type=RESPONSE_TYPE_RATING_1_5
+        ).first()
+        question.is_required = False
+        question.save(update_fields=["is_required", "updated_at"])
+
+        save_observation_responses(observation, {question: 3})
+        created, updated = save_observation_responses(
+            observation, [{"question": question, "value": ""}]
+        )
+
+        self.assertEqual(created, 0)
+        self.assertEqual(updated, 1)
+        self.assertFalse(
+            ObservationResponse.objects.filter(
+                observation=observation, question=question
+            ).exists()
+        )
+
     def test_invalid_rating_is_rejected(self):
         observation = create_coach_assessment_observation(
             player=self.player,
@@ -667,6 +702,28 @@ class AnalyticsObservationFoundationTests(TestCase):
         with self.assertRaises(ValidationError):
             submit_observation(observation, actor=self.evaluator)
 
+    def test_blank_required_text_response_does_not_count_as_answered(self):
+        text_question = self.setup_result.question_set.questions.get(
+            response_type=RESPONSE_TYPE_TEXT
+        )
+        text_question.is_required = True
+        text_question.save(update_fields=["is_required", "updated_at"])
+        observation = create_coach_assessment_observation(
+            player=self.player,
+            evaluation_cycle=self.cycle,
+            evaluator=self.evaluator,
+            responses=self.required_response_payload(),
+        ).observation
+        ObservationResponse.objects.create(
+            observation=observation,
+            question=text_question,
+            response_type=RESPONSE_TYPE_TEXT,
+            text_value="  ",
+        )
+
+        with self.assertRaises(ValidationError):
+            validate_required_responses(observation)
+
     def test_default_question_set_wrapper(self):
         self.assertEqual(
             default_coach_assessment_question_set(), self.setup_result.question_set
diff --git a/docs/qa/platform_e2e/CHANGELOG.md b/docs/qa/platform_e2e/CHANGELOG.md
index 81cff6c..35832a4 100644
--- a/docs/qa/platform_e2e/CHANGELOG.md
+++ b/docs/qa/platform_e2e/CHANGELOG.md
@@ -11,6 +11,7 @@
 - Release-pipeline guidance.
 - Change-impact guidance for selecting QA scope.
 - Lightweight maintenance conventions for future traceability changes.
+- Optional evaluation question traceability and regression coverage.
 
 ## Previous Milestones
 
diff --git a/docs/qa/platform_e2e/feature_traceability.md b/docs/qa/platform_e2e/feature_traceability.md
index 8e3f782..204139d 100644
--- a/docs/qa/platform_e2e/feature_traceability.md
+++ b/docs/qa/platform_e2e/feature_traceability.md
@@ -72,6 +72,7 @@ Current prefixes:
 | `EVL-005` | Evaluation uniqueness and duplicate prevention | Critical | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Duplicate Evaluation and Repeat Submission Tests |
 | `EVL-006` | Evaluation-cycle isolation | Critical | No | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Evaluation Cycle Isolation Tests |
 | `EVL-007` | Imported/manual workflow consistency | High | Partial | No | Yes | No | Semi-automatable | `platform_e2e_test_script.md` - Cross-Workflow Consistency Tests |
+| `EVL-008` | Optional evaluation questions | High | Partial | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Optional Evaluation Question Tests |
 | `REV-001` | Evaluation review | High | Yes | Yes | Yes | Partial | Semi-automatable | `platform_e2e_test_script.md` - Review Workflow |
 | `REV-002` | Reopen and resubmit | High | Yes | Yes | Yes | Yes | Fully automatable | `platform_e2e_test_script.md` - Review Workflow |
 | `REV-003` | Evaluation metadata and attribution | High | Partial | Yes | Yes | Partial | Fully automatable | `platform_e2e_test_script.md` - Review Workflow |
diff --git a/docs/qa/platform_e2e/platform_e2e_test_script.md b/docs/qa/platform_e2e/platform_e2e_test_script.md
index 42ea06d..0ece02a 100644
--- a/docs/qa/platform_e2e/platform_e2e_test_script.md
+++ b/docs/qa/platform_e2e/platform_e2e_test_script.md
@@ -26,6 +26,7 @@ These tests must pass before a production release is accepted:
 - [ ] coach evaluation submission (`EVL-001`)
 - [ ] player self-evaluation submission (`EVL-002`)
 - [ ] player peer-evaluation submission (`EVL-003`)
+- [ ] optional evaluation question handling (`EVL-008`)
 - [ ] evaluation review (`REV-001`, `REV-003`)
 - [ ] direct URL permissions (`SEC-001` to `SEC-004`)
 - [ ] forced password change (`ACC-006`)
@@ -71,6 +72,7 @@ Critical and High tests should be prioritized when release time is limited. Medi
 | Historical assignment preservation | `ASN-003` | High |
 | Core evaluation workflows | `EVL-001` to `EVL-006` | Critical |
 | Imported/manual workflow consistency | `EVL-007` | High |
+| Optional evaluation questions | `EVL-008` | High |
 | Review and attribution | `REV-001` to `REV-003` | High |
 | Permissions | `SEC-001` to `SEC-004` | Critical |
 | Command Center and reporting | `ANA-001` to `ANA-005` | High |
@@ -492,7 +494,78 @@ Result:
 Notes:
 ```
 
-## I. Review Workflow
+## I. Optional Evaluation Question Tests
+
+Requirements covered: `EVL-008`, `EVL-001`, `EVL-002`, `EVL-003`, `REV-001`, `ANA-002`
+
+Automation readiness: Fully automatable
+
+Setup:
+
+- [ ] In Django admin, open the active coach assessment question set.
+- [ ] Mark one rating question optional.
+- [ ] Leave at least one other rating question required.
+- [ ] Confirm the freeform notes question may also be optional if configured that way.
+
+Required-question behavior:
+
+- [ ] As a coach, open a new evaluation form.
+- [ ] Leave a required rating blank.
+- [ ] Fill any optional questions or leave them blank.
+- [ ] Click Submit.
+- [ ] Confirm the page blocks submission and shows a required-field error.
+- [ ] Confirm the evaluation remains draft.
+- [ ] Confirm entered answers remain visible after the validation error.
+
+Optional-question behavior:
+
+- [ ] As a coach, fill all required questions and leave the optional rating blank.
+- [ ] Click Submit.
+- [ ] Confirm submission succeeds.
+- [ ] Open the evaluation detail page.
+- [ ] Confirm the optional question is shown as `Optional`.
+- [ ] Confirm the optional unanswered question displays `Not answered`.
+- [ ] Confirm it is not displayed or counted as a `0`.
+
+Draft behavior:
+
+- [ ] Start another evaluation.
+- [ ] Answer only the optional question.
+- [ ] Save as draft.
+- [ ] Reopen the draft and clear the optional answer.
+- [ ] Save again.
+- [ ] Confirm the optional blank value is not retained as a zero or stale answer.
+- [ ] Complete only required questions and submit successfully.
+
+Player-submission behavior:
+
+- [ ] Repeat the optional blank submit path as a player self-evaluation.
+- [ ] Repeat the optional blank submit path as a player peer evaluation.
+- [ ] Confirm both submit successfully when required questions are complete.
+
+Review and analytics behavior:
+
+- [ ] Open player-facing `/analytics/my/evaluations/` detail for the submitted result.
+- [ ] Confirm evaluator names remain hidden.
+- [ ] Confirm the unanswered optional question is visible as `Not answered`.
+- [ ] Open coach/staff review detail.
+- [ ] Confirm the unanswered optional question is visible as `Not answered`.
+- [ ] Open Analytics Command Center and comparison views.
+- [ ] Confirm averages exclude blank optional answers.
+- [ ] Confirm completion metrics treat the submitted evaluation as complete because required questions were answered.
+
+Cleanup:
+
+- [ ] Restore the optional question setting to the desired production configuration.
+
+Pass / Fail:
+
+```text
+Result:
+Notes:
+```
+
+## J. Review Workflow
 
 Requirements covered: `REV-001`, `REV-002`, `REV-003`, `ANA-005`, `EVL-005`
```
