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


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def unique_slug_for_model(instance, source_value: str, slug_field: str = "slug", max_length: int = 180) -> str:
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
    observation_type = models.ForeignKey(ObservationType, on_delete=models.PROTECT, related_name="question_sets")
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
            models.UniqueConstraint(fields=["observation_type", "version"], name="analytics_unique_question_set_version"),
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
            and self.coach_assessment_question_set.observation_type.key != OBSERVATION_TYPE_COACH_ASSESSMENT
        ):
            raise ValidationError(
                {"coach_assessment_question_set": "Coach assessment cycles must use a coach-assessment question set."}
            )

    def __str__(self) -> str:
        return self.name


class ObservationQuestion(TimeStampedModel):
    question_set = models.ForeignKey(ObservationQuestionSet, on_delete=models.CASCADE, related_name="questions")
    key = models.SlugField(max_length=120)
    prompt = models.CharField(max_length=255)
    help_text = models.TextField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    response_type = models.CharField(max_length=40, choices=RESPONSE_TYPE_CHOICES)
    display_order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    min_numeric_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    max_numeric_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    choices = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["question_set", "display_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["question_set", "key"], name="analytics_unique_question_key_per_set"),
        ]
        indexes = [
            models.Index(fields=["question_set", "display_order"]),
            models.Index(fields=["question_set", "is_active"]),
            models.Index(fields=["category", "display_order"]),
        ]

    def __str__(self) -> str:
        return self.prompt


class Observation(TimeStampedModel):
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="observations")
    evaluation_cycle = models.ForeignKey(EvaluationCycle, on_delete=models.PROTECT, related_name="observations")
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
    observation_type = models.ForeignKey(ObservationType, on_delete=models.PROTECT, related_name="observations")
    observation_type_key = models.CharField(max_length=80, editable=False)
    question_set = models.ForeignKey(ObservationQuestionSet, on_delete=models.PROTECT, related_name="observations")
    source = models.ForeignKey(ObservationSource, on_delete=models.PROTECT, related_name="observations")
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
    status = models.CharField(max_length=40, choices=OBSERVATION_STATUS_CHOICES, default=OBSERVATION_STATUS_DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    season_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
    season_key_snapshot = models.CharField(max_length=80, blank=True, editable=False)
    player_team_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
    player_division_snapshot = models.CharField(max_length=80, blank=True, editable=False)
    evaluator_team_name_snapshot = models.CharField(max_length=120, blank=True, editable=False)
    evaluator_division_snapshot = models.CharField(max_length=80, blank=True, editable=False)
    evaluator_assignment_role_snapshot = models.CharField(max_length=80, blank=True, editable=False)
    notes = models.TextField(blank=True)
    source_metadata = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-submitted_at", "-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "evaluation_cycle", "observation_type_key", "evaluator", "evaluation_perspective"],
                condition=Q(observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT, evaluator__isnull=False),
                name="analytics_unique_coach_assessment_per_perspective",
            ),
            models.UniqueConstraint(
                fields=["player", "evaluation_cycle", "observation_type_key", "evaluation_perspective"],
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
        if self.evaluation_cycle_id and self.season_id and self.evaluation_cycle.season_id:
            if self.evaluation_cycle.season_id != self.season_id:
                errors["season"] = "Observation season must match the evaluation cycle season."
        if self.player_roster_membership_id:
            if self.player_roster_membership.player_id != self.player_id:
                errors["player_roster_membership"] = "Player roster membership must belong to the observation player."
            if self.season_id and self.player_roster_membership.season.id != self.season_id:
                errors["player_roster_membership"] = "Player roster membership must belong to the observation season."
        if self.evaluator_coach_assignment_id:
            if self.evaluator_id and self.evaluator_coach_assignment.user_id != self.evaluator_id:
                errors["evaluator_coach_assignment"] = "Evaluator coach assignment must belong to the evaluator."
            if self.season_id and self.evaluator_coach_assignment.season.id != self.season_id:
                errors["evaluator_coach_assignment"] = "Evaluator coach assignment must belong to the observation season."
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
        return EVALUATION_PERSPECTIVE_LABELS.get(self.evaluation_perspective, "Evaluation")


class ObservationResponse(TimeStampedModel):
    observation = models.ForeignKey(Observation, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(ObservationQuestion, on_delete=models.PROTECT, related_name="responses")
    response_type = models.CharField(max_length=40, choices=RESPONSE_TYPE_CHOICES)
    numeric_value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
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
            models.UniqueConstraint(fields=["observation", "question"], name="analytics_unique_response_per_question"),
        ]
        indexes = [
            models.Index(fields=["observation", "question"]),
            models.Index(fields=["question", "numeric_value"]),
            models.Index(fields=["response_type"]),
        ]

    def clean(self):
        if self.response_type == RESPONSE_TYPE_RATING_1_5:
            if self.numeric_value is None:
                raise ValidationError({"numeric_value": "A 1-5 rating response requires a numeric value."})
            if (
                not self.numeric_value.is_finite()
                or self.numeric_value != self.numeric_value.to_integral_value()
                or self.numeric_value < Decimal("1")
                or self.numeric_value > Decimal("5")
            ):
                raise ValidationError({"numeric_value": "Rating responses must be one of 1, 2, 3, 4, or 5."})

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
