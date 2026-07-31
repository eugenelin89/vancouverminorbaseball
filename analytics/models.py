from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

OBSERVATION_TYPE_COACH_ASSESSMENT = "coach_assessment"

RESPONSE_TYPE_RATING_1_5 = "rating_1_5"
RESPONSE_TYPE_TEXT = "text"
RESPONSE_TYPE_BOOLEAN = "boolean"
RESPONSE_TYPE_MULTIPLE_CHOICE = "multiple_choice"
RESPONSE_TYPE_VELOCITY = "velocity"
RESPONSE_TYPE_TIME = "time"
RESPONSE_TYPE_DISTANCE = "distance"

RESPONSE_TYPE_CHOICES = [
    (RESPONSE_TYPE_RATING_1_5, "1-5 Rating"),
    (RESPONSE_TYPE_TEXT, "Text"),
    (RESPONSE_TYPE_BOOLEAN, "Boolean"),
    (RESPONSE_TYPE_MULTIPLE_CHOICE, "Multiple Choice"),
    (RESPONSE_TYPE_VELOCITY, "Velocity"),
    (RESPONSE_TYPE_TIME, "Time"),
    (RESPONSE_TYPE_DISTANCE, "Distance"),
]

OBSERVATION_STATUS_DRAFT = "draft"
OBSERVATION_STATUS_SUBMITTED = "submitted"
OBSERVATION_STATUS_REOPENED = "reopened"
OBSERVATION_STATUS_ARCHIVED = "archived"

OBSERVATION_STATUS_CHOICES = [
    (OBSERVATION_STATUS_DRAFT, "Draft"),
    (OBSERVATION_STATUS_SUBMITTED, "Submitted"),
    (OBSERVATION_STATUS_REOPENED, "Reopened"),
    (OBSERVATION_STATUS_ARCHIVED, "Archived"),
]

EVALUATION_PERSPECTIVE_SELF = "self"
EVALUATION_PERSPECTIVE_PEER = "peer"
EVALUATION_PERSPECTIVE_COACH = "coach"
EVALUATION_PERSPECTIVE_STAFF = "staff"
EVALUATION_PERSPECTIVE_GUEST = "guest"

EVALUATION_PERSPECTIVE_CHOICES = [
    (EVALUATION_PERSPECTIVE_SELF, "Self Evaluation"),
    (EVALUATION_PERSPECTIVE_PEER, "Peer Evaluation"),
    (EVALUATION_PERSPECTIVE_COACH, "Coach Evaluation"),
    (EVALUATION_PERSPECTIVE_STAFF, "Staff Evaluation"),
    (EVALUATION_PERSPECTIVE_GUEST, "Guest Evaluation"),
]

EVALUATION_PERSPECTIVE_LABELS = dict(EVALUATION_PERSPECTIVE_CHOICES)

ASSESSMENT_VALUE_TYPE_NUMBER = "number"
ASSESSMENT_VALUE_TYPE_RATING = "rating"
ASSESSMENT_VALUE_TYPE_TEXT = "text"
ASSESSMENT_VALUE_TYPE_CHOICE = "choice"

ASSESSMENT_VALUE_TYPE_CHOICES = [
    (ASSESSMENT_VALUE_TYPE_NUMBER, "Number"),
    (ASSESSMENT_VALUE_TYPE_RATING, "Rating"),
    (ASSESSMENT_VALUE_TYPE_TEXT, "Text"),
    (ASSESSMENT_VALUE_TYPE_CHOICE, "Choice"),
]

ASSESSMENT_DIRECTION_HIGHER = "higher"
ASSESSMENT_DIRECTION_LOWER = "lower"
ASSESSMENT_DIRECTION_NEUTRAL = "neutral"

ASSESSMENT_DIRECTION_CHOICES = [
    (ASSESSMENT_DIRECTION_HIGHER, "Higher is better"),
    (ASSESSMENT_DIRECTION_LOWER, "Lower is better"),
    (ASSESSMENT_DIRECTION_NEUTRAL, "Neutral"),
]

ASSESSMENT_STATUS_DRAFT = "draft"
ASSESSMENT_STATUS_COMMITTED = "committed"

ASSESSMENT_STATUS_CHOICES = [
    (ASSESSMENT_STATUS_DRAFT, "Draft"),
    (ASSESSMENT_STATUS_COMMITTED, "Committed"),
]

ASSESSMENT_IMPORT_STATUS_UPLOADED = "uploaded"
ASSESSMENT_IMPORT_STATUS_PREVIEWED = "previewed"
ASSESSMENT_IMPORT_STATUS_COMMITTED = "committed"
ASSESSMENT_IMPORT_STATUS_FAILED = "failed"

ASSESSMENT_IMPORT_STATUS_CHOICES = [
    (ASSESSMENT_IMPORT_STATUS_UPLOADED, "Uploaded"),
    (ASSESSMENT_IMPORT_STATUS_PREVIEWED, "Previewed"),
    (ASSESSMENT_IMPORT_STATUS_COMMITTED, "Committed"),
    (ASSESSMENT_IMPORT_STATUS_FAILED, "Failed"),
]

ASSESSMENT_IMPORT_ROW_MATCHED = "matched"
ASSESSMENT_IMPORT_ROW_UNMATCHED = "unmatched"
ASSESSMENT_IMPORT_ROW_AMBIGUOUS = "ambiguous"
ASSESSMENT_IMPORT_ROW_INVALID = "invalid"
ASSESSMENT_IMPORT_ROW_SKIPPED = "skipped"
ASSESSMENT_IMPORT_ROW_COMMITTED = "committed"

ASSESSMENT_IMPORT_ROW_STATUS_CHOICES = [
    (ASSESSMENT_IMPORT_ROW_MATCHED, "Matched"),
    (ASSESSMENT_IMPORT_ROW_UNMATCHED, "Unmatched"),
    (ASSESSMENT_IMPORT_ROW_AMBIGUOUS, "Ambiguous"),
    (ASSESSMENT_IMPORT_ROW_INVALID, "Invalid"),
    (ASSESSMENT_IMPORT_ROW_SKIPPED, "Skipped"),
    (ASSESSMENT_IMPORT_ROW_COMMITTED, "Committed"),
]

ASSESSMENT_VALUE_SOURCE_IMPORTED = "imported"
ASSESSMENT_VALUE_SOURCE_MANUAL = "manual"
ASSESSMENT_VALUE_SOURCE_MANUAL_CORRECTED = "manual_corrected"

ASSESSMENT_VALUE_SOURCE_CHOICES = [
    (ASSESSMENT_VALUE_SOURCE_IMPORTED, "Imported"),
    (ASSESSMENT_VALUE_SOURCE_MANUAL, "Manual"),
    (ASSESSMENT_VALUE_SOURCE_MANUAL_CORRECTED, "Manual Correction"),
]


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def unique_slug_for_model(
    instance, source_value: str, slug_field: str = "slug", max_length: int = 180
) -> str:
    base_slug = slugify(source_value) or "item"
    slug = base_slug[:max_length]
    counter = 2
    model = instance.__class__
    while model.objects.exclude(pk=instance.pk).filter(**{slug_field: slug}).exists():
        suffix = f"-{counter}"
        slug = f"{base_slug[:max_length - len(suffix)]}{suffix}"
        counter += 1
    return slug


class ObservationType(TimeStampedModel):
    key = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["key"]
        indexes = [
            models.Index(fields=["is_active", "key"]),
        ]

    def __str__(self) -> str:
        return self.name


class ObservationSource(TimeStampedModel):
    key = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["key"]
        indexes = [
            models.Index(fields=["is_active", "key"]),
        ]

    def __str__(self) -> str:
        return self.name


class EvaluatorRole(TimeStampedModel):
    key = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["key"]
        indexes = [
            models.Index(fields=["is_active", "key"]),
        ]

    def __str__(self) -> str:
        return self.name


class ObservationQuestionSet(TimeStampedModel):
    observation_type = models.ForeignKey(
        ObservationType, on_delete=models.PROTECT, related_name="question_sets"
    )
    name = models.CharField(max_length=160)
    version = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    rubric = models.JSONField(default=dict, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    retired_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["observation_type__key", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["observation_type", "version"],
                name="analytics_unique_question_set_version",
            ),
        ]
        indexes = [
            models.Index(fields=["observation_type", "is_active"]),
            models.Index(fields=["observation_type", "version"]),
            models.Index(fields=["effective_from", "retired_on"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class EvaluationCycle(TimeStampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    cycle_type = models.CharField(max_length=80)
    season = models.ForeignKey(
        "seasons.Season",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="evaluation_cycles",
    )
    description = models.TextField(blank=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    coach_assessment_question_set = models.ForeignKey(
        ObservationQuestionSet,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="evaluation_cycles",
    )
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-starts_on", "-created_at", "name"]
        indexes = [
            models.Index(fields=["is_active", "starts_on"]),
            models.Index(fields=["season", "is_active"]),
            models.Index(fields=["cycle_type", "is_active"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_for_model(self, self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if (
            self.coach_assessment_question_set_id
            and self.coach_assessment_question_set.observation_type.key
            != OBSERVATION_TYPE_COACH_ASSESSMENT
        ):
            raise ValidationError(
                {
                    "coach_assessment_question_set": "Coach assessment cycles must use a coach-assessment question set."
                }
            )

    def __str__(self) -> str:
        return self.name


class ObservationQuestion(TimeStampedModel):
    question_set = models.ForeignKey(
        ObservationQuestionSet, on_delete=models.CASCADE, related_name="questions"
    )
    key = models.SlugField(max_length=120)
    prompt = models.CharField(max_length=255)
    help_text = models.TextField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    response_type = models.CharField(max_length=40, choices=RESPONSE_TYPE_CHOICES)
    display_order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    min_numeric_value = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    max_numeric_value = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    choices = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["question_set", "display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["question_set", "key"],
                name="analytics_unique_question_key_per_set",
            ),
        ]
        indexes = [
            models.Index(fields=["question_set", "display_order"]),
            models.Index(fields=["question_set", "is_active"]),
            models.Index(fields=["category", "display_order"]),
        ]

    def __str__(self) -> str:
        return self.prompt


class Observation(TimeStampedModel):
    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="observations"
    )
    evaluation_cycle = models.ForeignKey(
        EvaluationCycle, on_delete=models.PROTECT, related_name="observations"
    )
    season = models.ForeignKey(
        "seasons.Season",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="observations",
    )
    player_roster_membership = models.ForeignKey(
        "seasons.PlayerRosterMembership",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="observations",
    )
    evaluator_coach_assignment = models.ForeignKey(
        "seasons.CoachSeasonAssignment",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="observations",
    )
    observation_type = models.ForeignKey(
        ObservationType, on_delete=models.PROTECT, related_name="observations"
    )
    observation_type_key = models.CharField(max_length=80, editable=False)
    question_set = models.ForeignKey(
        ObservationQuestionSet, on_delete=models.PROTECT, related_name="observations"
    )
    source = models.ForeignKey(
        ObservationSource, on_delete=models.PROTECT, related_name="observations"
    )
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="analytics_observations",
    )
    evaluator_role = models.ForeignKey(
        EvaluatorRole,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="observations",
    )
    evaluator_role_key = models.CharField(max_length=80, blank=True)
    evaluator_role_name = models.CharField(max_length=120, blank=True)
    evaluation_perspective = models.CharField(
        max_length=40,
        choices=EVALUATION_PERSPECTIVE_CHOICES,
        default=EVALUATION_PERSPECTIVE_GUEST,
    )
    status = models.CharField(
        max_length=40,
        choices=OBSERVATION_STATUS_CHOICES,
        default=OBSERVATION_STATUS_DRAFT,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    season_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
    season_key_snapshot = models.CharField(max_length=80, blank=True, editable=False)
    player_team_name_snapshot = models.CharField(
        max_length=120, blank=True, editable=False
    )
    player_division_snapshot = models.CharField(
        max_length=80, blank=True, editable=False
    )
    evaluator_team_name_snapshot = models.CharField(
        max_length=120, blank=True, editable=False
    )
    evaluator_division_snapshot = models.CharField(
        max_length=80, blank=True, editable=False
    )
    evaluator_assignment_role_snapshot = models.CharField(
        max_length=80, blank=True, editable=False
    )
    notes = models.TextField(blank=True)
    source_metadata = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-submitted_at", "-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "player",
                    "evaluation_cycle",
                    "observation_type_key",
                    "evaluator",
                    "evaluation_perspective",
                ],
                condition=Q(
                    observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
                    evaluator__isnull=False,
                ),
                name="analytics_unique_coach_assessment_per_perspective",
            ),
            models.UniqueConstraint(
                fields=[
                    "player",
                    "evaluation_cycle",
                    "observation_type_key",
                    "evaluation_perspective",
                ],
                condition=Q(
                    observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
                    evaluation_perspective=EVALUATION_PERSPECTIVE_SELF,
                ),
                name="analytics_unique_self_assessment_per_player",
            ),
        ]
        indexes = [
            models.Index(fields=["player", "-created_at"]),
            models.Index(fields=["evaluation_cycle", "observation_type", "status"]),
            models.Index(fields=["season", "status"]),
            models.Index(fields=["season", "player_roster_membership", "status"]),
            models.Index(fields=["evaluator_coach_assignment", "status"]),
            models.Index(fields=["evaluator", "evaluation_cycle"]),
            models.Index(fields=["evaluator_role_key", "evaluation_cycle"]),
            models.Index(fields=["evaluation_perspective", "evaluation_cycle"]),
            models.Index(fields=["observation_type_key", "status"]),
            models.Index(fields=["submitted_at"]),
        ]

    def clean(self):
        errors = {}
        if (
            self.evaluation_cycle_id
            and self.season_id
            and self.evaluation_cycle.season_id
        ):
            if self.evaluation_cycle.season_id != self.season_id:
                errors["season"] = (
                    "Observation season must match the evaluation cycle season."
                )
        if self.player_roster_membership_id:
            if self.player_roster_membership.player_id != self.player_id:
                errors["player_roster_membership"] = (
                    "Player roster membership must belong to the observation player."
                )
            if (
                self.season_id
                and self.player_roster_membership.season.id != self.season_id
            ):
                errors["player_roster_membership"] = (
                    "Player roster membership must belong to the observation season."
                )
        if self.evaluator_coach_assignment_id:
            if (
                self.evaluator_id
                and self.evaluator_coach_assignment.user_id != self.evaluator_id
            ):
                errors["evaluator_coach_assignment"] = (
                    "Evaluator coach assignment must belong to the evaluator."
                )
            if (
                self.season_id
                and self.evaluator_coach_assignment.season.id != self.season_id
            ):
                errors["evaluator_coach_assignment"] = (
                    "Evaluator coach assignment must belong to the observation season."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.observation_type_id:
            self.observation_type_key = self.observation_type.key
        if self.evaluator_role_id:
            self.evaluator_role_key = self.evaluator_role.key
            self.evaluator_role_name = self.evaluator_role.name
        if self.status == OBSERVATION_STATUS_SUBMITTED and self.submitted_at is None:
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.observation_type_key} for {self.player}"

    @property
    def evaluation_perspective_label(self) -> str:
        return EVALUATION_PERSPECTIVE_LABELS.get(
            self.evaluation_perspective, "Evaluation"
        )


class ObservationResponse(TimeStampedModel):
    observation = models.ForeignKey(
        Observation, on_delete=models.CASCADE, related_name="responses"
    )
    question = models.ForeignKey(
        ObservationQuestion, on_delete=models.PROTECT, related_name="responses"
    )
    response_type = models.CharField(max_length=40, choices=RESPONSE_TYPE_CHOICES)
    numeric_value = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    text_value = models.TextField(blank=True)
    boolean_value = models.BooleanField(null=True, blank=True)
    selected_choice = models.CharField(max_length=120, blank=True)
    raw_value = models.TextField(blank=True)
    unit = models.CharField(max_length=40, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["question__display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["observation", "question"],
                name="analytics_unique_response_per_question",
            ),
        ]
        indexes = [
            models.Index(fields=["observation", "question"]),
            models.Index(fields=["question", "numeric_value"]),
            models.Index(fields=["response_type"]),
        ]

    def clean(self):
        if self.response_type == RESPONSE_TYPE_RATING_1_5:
            if self.numeric_value is None:
                raise ValidationError(
                    {"numeric_value": "A 1-5 rating response requires a numeric value."}
                )
            if (
                not self.numeric_value.is_finite()
                or self.numeric_value != self.numeric_value.to_integral_value()
                or self.numeric_value < Decimal("1")
                or self.numeric_value > Decimal("5")
            ):
                raise ValidationError(
                    {
                        "numeric_value": "Rating responses must be one of 1, 2, 3, 4, or 5."
                    }
                )

    def save(self, *args, **kwargs):
        if not self.response_type and self.question_id:
            self.response_type = self.question.response_type
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def text_preview(self) -> str:
        return self.text_value[:80]

    def __str__(self) -> str:
        return f"{self.question} response"


class AssessmentMetricDefinition(TimeStampedModel):
    key = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    default_value_type = models.CharField(
        max_length=40,
        choices=ASSESSMENT_VALUE_TYPE_CHOICES,
        default=ASSESSMENT_VALUE_TYPE_NUMBER,
    )
    default_unit = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["key"]
        indexes = [
            models.Index(fields=["is_active", "key"]),
        ]

    def __str__(self) -> str:
        return self.name


class AssessmentTemplate(TimeStampedModel):
    key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    version = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    effective_from = models.DateField(null=True, blank=True)
    retired_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["key", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["key", "version"],
                name="analytics_unique_assessment_template_version",
            ),
        ]
        indexes = [
            models.Index(fields=["key", "version"]),
            models.Index(fields=["is_active", "key"]),
        ]

    def has_committed_assessments(self) -> bool:
        if not self.pk:
            return False
        return PlayerAssessment.objects.filter(
            event__template_id=self.pk,
            status=ASSESSMENT_STATUS_COMMITTED,
        ).exists()

    def save(self, *args, **kwargs):
        if self.pk and self.has_committed_assessments():
            original = AssessmentTemplate.objects.get(pk=self.pk)
            locked_fields = ["key", "version"]
            for field_name in locked_fields:
                if getattr(original, field_name) != getattr(self, field_name):
                    raise ValidationError(
                        {field_name: "Template identity cannot change after use."}
                    )
            self.is_locked = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class AssessmentTemplateMetric(TimeStampedModel):
    template = models.ForeignKey(
        AssessmentTemplate, on_delete=models.CASCADE, related_name="template_metrics"
    )
    metric = models.ForeignKey(
        AssessmentMetricDefinition,
        on_delete=models.PROTECT,
        related_name="template_metrics",
    )
    category = models.CharField(max_length=120, blank=True)
    display_name = models.CharField(max_length=160)
    display_order = models.PositiveIntegerField(default=0)
    value_type = models.CharField(
        max_length=40,
        choices=ASSESSMENT_VALUE_TYPE_CHOICES,
        default=ASSESSMENT_VALUE_TYPE_NUMBER,
    )
    unit = models.CharField(max_length=40, blank=True)
    is_required = models.BooleanField(default=False)
    min_value = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    max_value = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    rating_scale_min = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    rating_scale_max = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    direction = models.CharField(
        max_length=20,
        choices=ASSESSMENT_DIRECTION_CHOICES,
        default=ASSESSMENT_DIRECTION_NEUTRAL,
    )
    help_text = models.TextField(blank=True)
    rubric = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["template", "display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["template", "metric"],
                name="analytics_unique_metric_per_assessment_template",
            ),
        ]
        indexes = [
            models.Index(fields=["template", "display_order"]),
            models.Index(fields=["category", "display_order"]),
            models.Index(fields=["metric", "template"]),
        ]

    def clean(self):
        errors = {}
        if self.min_value is not None and self.max_value is not None:
            if self.max_value < self.min_value:
                errors["max_value"] = "Maximum value cannot be less than minimum value."
        if self.rating_scale_min is not None and self.rating_scale_max is not None:
            if self.rating_scale_max < self.rating_scale_min:
                errors["rating_scale_max"] = (
                    "Rating scale maximum cannot be less than the minimum."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pk and self.template.has_committed_assessments():
            original = AssessmentTemplateMetric.objects.get(pk=self.pk)
            locked_fields = [
                "metric_id",
                "category",
                "display_name",
                "display_order",
                "value_type",
                "unit",
                "is_required",
                "min_value",
                "max_value",
                "rating_scale_min",
                "rating_scale_max",
                "direction",
                "rubric",
            ]
            for field_name in locked_fields:
                if getattr(original, field_name) != getattr(self, field_name):
                    raise ValidationError(
                        {field_name: "Template metrics cannot change after use."}
                    )
            self.template.is_locked = True
            self.template.save(update_fields=["is_locked", "updated_at"])
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.display_name


class AssessmentScoringProfile(TimeStampedModel):
    key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    version = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["key", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["key", "version"],
                name="analytics_unique_assessment_scoring_profile_version",
            ),
        ]
        indexes = [
            models.Index(fields=["key", "version"]),
            models.Index(fields=["is_active", "key"]),
        ]

    def has_committed_assessments(self) -> bool:
        if not self.pk:
            return False
        return PlayerAssessment.objects.filter(
            event__scoring_profile_id=self.pk,
            status=ASSESSMENT_STATUS_COMMITTED,
        ).exists()

    def save(self, *args, **kwargs):
        if self.pk and self.has_committed_assessments():
            original = AssessmentScoringProfile.objects.get(pk=self.pk)
            for field_name in ["key", "version", "config"]:
                if getattr(original, field_name) != getattr(self, field_name):
                    raise ValidationError(
                        {field_name: "Scoring profile cannot change after use."}
                    )
            self.is_locked = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class AssessmentImportTemplate(TimeStampedModel):
    key = models.SlugField(max_length=120)
    name = models.CharField(max_length=160)
    version = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["key", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["key", "version"],
                name="analytics_unique_assessment_import_template_version",
            ),
        ]
        indexes = [
            models.Index(fields=["key", "version"]),
            models.Index(fields=["is_active", "key"]),
        ]

    def has_committed_imports(self) -> bool:
        if not self.pk:
            return False
        return self.import_batches.filter(
            status=ASSESSMENT_IMPORT_STATUS_COMMITTED
        ).exists()

    def save(self, *args, **kwargs):
        if self.pk and self.has_committed_imports():
            original = AssessmentImportTemplate.objects.get(pk=self.pk)
            for field_name in ["key", "version", "config"]:
                if getattr(original, field_name) != getattr(self, field_name):
                    raise ValidationError(
                        {field_name: "Import template cannot change after use."}
                    )
            self.is_locked = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class AssessmentEvent(TimeStampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    season = models.ForeignKey(
        "seasons.Season", on_delete=models.PROTECT, related_name="assessment_events"
    )
    division = models.CharField(max_length=80, blank=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    template = models.ForeignKey(
        AssessmentTemplate, on_delete=models.PROTECT, related_name="events"
    )
    scoring_profile = models.ForeignKey(
        AssessmentScoringProfile,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="events",
    )
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-starts_on", "name"]
        indexes = [
            models.Index(fields=["season", "is_active"]),
            models.Index(fields=["division", "is_active"]),
            models.Index(fields=["slug"]),
        ]

    def clean(self):
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError(
                {"ends_on": "Assessment event end date cannot be before start date."}
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_for_model(self, self.name)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class AssessmentImportBatch(TimeStampedModel):
    event = models.ForeignKey(
        AssessmentEvent, on_delete=models.PROTECT, related_name="import_batches"
    )
    import_template = models.ForeignKey(
        AssessmentImportTemplate,
        on_delete=models.PROTECT,
        related_name="import_batches",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assessment_import_batches",
    )
    original_filename = models.CharField(max_length=255)
    workbook_sha256 = models.CharField(max_length=64)
    status = models.CharField(
        max_length=40,
        choices=ASSESSMENT_IMPORT_STATUS_CHOICES,
        default=ASSESSMENT_IMPORT_STATUS_UPLOADED,
    )
    preview_snapshot = models.JSONField(default=dict, blank=True)
    config_snapshot = models.JSONField(default=dict, blank=True)
    import_summary = models.JSONField(default=dict, blank=True)
    committed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["event", "status"]),
            models.Index(fields=["workbook_sha256"]),
            models.Index(fields=["uploaded_by", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.original_filename


class PlayerAssessment(TimeStampedModel):
    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="assessment_records"
    )
    event = models.ForeignKey(
        AssessmentEvent, on_delete=models.PROTECT, related_name="player_assessments"
    )
    roster_membership = models.ForeignKey(
        "seasons.PlayerRosterMembership",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="assessment_records",
    )
    import_batch = models.ForeignKey(
        AssessmentImportBatch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_assessments",
    )
    source_row_key = models.CharField(max_length=180, blank=True)
    status = models.CharField(
        max_length=40,
        choices=ASSESSMENT_STATUS_CHOICES,
        default=ASSESSMENT_STATUS_DRAFT,
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["event", "player__last_name", "player__first_name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "event"],
                name="analytics_unique_player_assessment_per_event",
            ),
        ]
        indexes = [
            models.Index(fields=["player", "event"]),
            models.Index(fields=["event", "status"]),
            models.Index(fields=["import_batch"]),
        ]

    def clean(self):
        errors = {}
        if self.roster_membership_id:
            if self.roster_membership.player_id != self.player_id:
                errors["roster_membership"] = (
                    "Roster membership must belong to the assessed player."
                )
            if (
                self.event_id
                and self.roster_membership.season.id != self.event.season_id
            ):
                errors["roster_membership"] = (
                    "Roster membership season must match the assessment event season."
                )
        if self.import_batch_id and self.event_id:
            if self.import_batch.event_id != self.event_id:
                errors["import_batch"] = (
                    "Import batch must belong to the same assessment event."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.event}: {self.player}"


class AssessmentImportRow(TimeStampedModel):
    batch = models.ForeignKey(
        AssessmentImportBatch, on_delete=models.CASCADE, related_name="rows"
    )
    row_key = models.CharField(max_length=180)
    source_sheet = models.CharField(max_length=120)
    source_row = models.PositiveIntegerField()
    raw_identity = models.CharField(max_length=180, blank=True)
    player = models.ForeignKey(
        "players.Player",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assessment_import_rows",
    )
    roster_membership = models.ForeignKey(
        "seasons.PlayerRosterMembership",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assessment_import_rows",
    )
    action = models.CharField(max_length=40, blank=True)
    status = models.CharField(
        max_length=40,
        choices=ASSESSMENT_IMPORT_ROW_STATUS_CHOICES,
        default=ASSESSMENT_IMPORT_ROW_UNMATCHED,
    )
    errors = models.JSONField(default=list, blank=True)
    values_snapshot = models.JSONField(default=list, blank=True)
    raw_row = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["batch", "source_sheet", "source_row", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "row_key"],
                name="analytics_unique_assessment_import_row_key",
            ),
        ]
        indexes = [
            models.Index(fields=["batch", "status"]),
            models.Index(fields=["player", "batch"]),
            models.Index(fields=["source_sheet", "source_row"]),
        ]

    def __str__(self) -> str:
        return f"{self.batch} row {self.source_row}"


class AssessmentValue(TimeStampedModel):
    player_assessment = models.ForeignKey(
        PlayerAssessment, on_delete=models.CASCADE, related_name="values"
    )
    template_metric = models.ForeignKey(
        AssessmentTemplateMetric,
        on_delete=models.PROTECT,
        related_name="assessment_values",
    )
    numeric_value = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    rating_value = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    rating_scale_min = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    rating_scale_max = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    text_value = models.TextField(blank=True)
    choice_value = models.CharField(max_length=160, blank=True)
    raw_value = models.TextField(blank=True)
    normalized_value = models.TextField(blank=True)
    unit = models.CharField(max_length=40, blank=True)
    source_sheet = models.CharField(max_length=120, blank=True)
    source_row = models.PositiveIntegerField(null=True, blank=True)
    source_column = models.CharField(max_length=20, blank=True)
    source_header = models.CharField(max_length=160, blank=True)
    source_kind = models.CharField(
        max_length=40,
        choices=ASSESSMENT_VALUE_SOURCE_CHOICES,
        default=ASSESSMENT_VALUE_SOURCE_IMPORTED,
    )
    is_imported = models.BooleanField(default=True)
    is_manual_override = models.BooleanField(default=False)
    import_row = models.ForeignKey(
        AssessmentImportRow,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assessment_values",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["template_metric__display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["player_assessment", "template_metric"],
                name="analytics_unique_assessment_value_per_metric",
            ),
        ]
        indexes = [
            models.Index(fields=["player_assessment", "template_metric"]),
            models.Index(fields=["template_metric", "numeric_value"]),
            models.Index(fields=["source_sheet", "source_row"]),
            models.Index(fields=["is_manual_override"]),
        ]

    def clean(self):
        errors = {}
        if self.player_assessment_id and self.template_metric_id:
            if (
                self.template_metric.template_id
                != self.player_assessment.event.template_id
            ):
                errors["template_metric"] = (
                    "Assessment value metric must belong to the event template."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.player_assessment} - {self.template_metric}"
