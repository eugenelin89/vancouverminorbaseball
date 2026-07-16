from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


def normalize_lookup_value(value: str) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def normalize_slug_value(value: str) -> str:
    normalized = normalize_lookup_value(value)
    return slugify(normalized)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Season(TimeStampedModel):
    key = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-starts_on", "name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_current"],
                condition=Q(is_current=True),
                name="seasons_unique_current_season",
            ),
        ]
        indexes = [
            models.Index(fields=["key"]),
            models.Index(fields=["is_active", "starts_on"]),
            models.Index(fields=["is_current"]),
        ]

    def clean(self):
        self.key = normalize_slug_value(self.key)
        self.name = str(self.name or "").strip()
        if not self.key:
            raise ValidationError({"key": "Season key is required."})
        if not self.name:
            raise ValidationError({"name": "Season name is required."})
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": "Season end date cannot be before the start date."})

    def save(self, *args, **kwargs):
        self.key = normalize_slug_value(self.key)
        self.name = str(self.name or "").strip()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class SeasonTeam(TimeStampedModel):
    season = models.ForeignKey(Season, on_delete=models.PROTECT, related_name="teams")
    name = models.CharField(max_length=120)
    division = models.CharField(max_length=80)
    normalized_name = models.CharField(max_length=120, editable=False)
    normalized_division = models.CharField(max_length=80, editable=False)
    external_source = models.CharField(max_length=80, blank=True)
    external_identifier = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["season__name", "normalized_division", "normalized_name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["season", "normalized_division", "normalized_name"],
                name="seasons_unique_team_per_season_division",
            ),
            models.UniqueConstraint(
                fields=["season", "external_source", "external_identifier"],
                condition=~Q(external_source="") & ~Q(external_identifier=""),
                name="seasons_unique_team_external_identifier",
            ),
        ]
        indexes = [
            models.Index(fields=["season", "normalized_division", "normalized_name"]),
            models.Index(fields=["season", "division"]),
            models.Index(fields=["season", "is_active"]),
            models.Index(fields=["external_source", "external_identifier"]),
        ]

    def clean(self):
        self.name = str(self.name or "").strip()
        self.division = str(self.division or "").strip()
        self.normalized_name = normalize_lookup_value(self.name)
        self.normalized_division = normalize_lookup_value(self.division)
        self.external_source = normalize_lookup_value(self.external_source).replace(" ", "_")
        self.external_identifier = normalize_lookup_value(self.external_identifier)
        if not self.name:
            raise ValidationError({"name": "Team name is required."})
        if not self.division:
            raise ValidationError({"division": "Division is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.season} / {self.division} {self.name}"


class RosterStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    TRANSFERRED = "transferred", "Transferred"
    GUEST = "guest", "Guest"
    REMOVED = "removed", "Removed"


class PlayerRosterMembership(TimeStampedModel):
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="roster_memberships")
    season_team = models.ForeignKey(SeasonTeam, on_delete=models.PROTECT, related_name="player_memberships")
    status = models.CharField(max_length=40, choices=RosterStatus.choices, default=RosterStatus.ACTIVE)
    jersey_number = models.CharField(max_length=20, blank=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=80, blank=True)
    source_identifier = models.CharField(max_length=160, blank=True)
    import_batch = models.ForeignKey(
        "players.PlayerImportBatch",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roster_memberships",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["season_team__season__name", "player__last_name", "player__first_name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["player", "season_team", "source", "source_identifier"],
                condition=~Q(source="") & ~Q(source_identifier=""),
                name="seasons_unique_player_membership_source",
            ),
        ]
        indexes = [
            models.Index(fields=["player", "is_active"]),
            models.Index(fields=["season_team", "is_active"]),
            models.Index(fields=["player", "is_primary", "is_active"]),
            models.Index(fields=["starts_on", "ends_on"]),
            models.Index(fields=["source", "source_identifier"]),
            models.Index(fields=["import_batch"]),
        ]

    @property
    def season(self) -> Season:
        return self.season_team.season

    def clean(self):
        self.source = normalize_lookup_value(self.source).replace(" ", "_")
        self.source_identifier = normalize_lookup_value(self.source_identifier)
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": "Membership end date cannot be before the start date."})
        if self.is_primary and not self.is_active:
            raise ValidationError({"is_primary": "Only active memberships can be primary."})
        if self.is_primary and self.is_active and self.player_id and self.season_team_id:
            queryset = PlayerRosterMembership.objects.filter(
                player_id=self.player_id,
                season_team__season_id=self.season_team.season_id,
                is_active=True,
                is_primary=True,
            )
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError({"is_primary": "This player already has an active primary membership for this season."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.player} - {self.season_team}"


class CoachAssignmentRole(models.TextChoices):
    HEAD_COACH = "head_coach", "Head Coach"
    ASSISTANT_COACH = "assistant_coach", "Assistant Coach"
    MANAGER = "manager", "Manager"
    COORDINATOR = "coordinator", "Coordinator"
    EVALUATOR = "evaluator", "Evaluator"


class CoachSeasonAssignment(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="season_assignments")
    season_team = models.ForeignKey(SeasonTeam, on_delete=models.PROTECT, related_name="coach_assignments")
    assignment_role = models.CharField(max_length=40, choices=CoachAssignmentRole.choices)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=80, blank=True)
    source_identifier = models.CharField(max_length=160, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["season_team__season__name", "user__username", "assignment_role", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "season_team", "assignment_role"],
                condition=Q(is_active=True),
                name="seasons_unique_active_coach_assignment",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["season_team", "is_active"]),
            models.Index(fields=["user", "is_primary", "is_active"]),
            models.Index(fields=["assignment_role", "is_active"]),
            models.Index(fields=["source", "source_identifier"]),
        ]

    @property
    def season(self) -> Season:
        return self.season_team.season

    def clean(self):
        self.source = normalize_lookup_value(self.source).replace(" ", "_")
        self.source_identifier = normalize_lookup_value(self.source_identifier)
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": "Assignment end date cannot be before the start date."})
        if self.is_primary and not self.is_active:
            raise ValidationError({"is_primary": "Only active assignments can be primary."})
        if self.is_primary and self.is_active and self.user_id and self.season_team_id:
            queryset = CoachSeasonAssignment.objects.filter(
                user_id=self.user_id,
                season_team__season_id=self.season_team.season_id,
                is_active=True,
                is_primary=True,
            )
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError({"is_primary": "This user already has an active primary assignment for this season."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user} - {self.get_assignment_role_display()} - {self.season_team}"
