from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, F
from django.utils.text import slugify

from pdp.models import Season


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class League(TimeStampedModel):
    name = models.CharField(max_length=140, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "league"
            slug = base_slug
            counter = 2
            while League.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class LeagueSeason(TimeStampedModel):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="league_seasons")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="league_seasons")
    slug = models.SlugField(max_length=180, unique=True)
    title = models.CharField(max_length=180, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-season__year", "league__name"]
        constraints = [
            models.UniqueConstraint(fields=["league", "season"], name="leaguehub_unique_league_season"),
        ]
        indexes = [
            models.Index(fields=["league", "season"]),
        ]

    def __str__(self):
        return self.title or f"{self.league.name} - {self.season.name}"

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"{self.league.name} - {self.season.name}"
        if not self.slug:
            base_slug = slugify(self.title) or f"league-season-{self.season.year}"
            slug = base_slug
            counter = 2
            while LeagueSeason.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Team(TimeStampedModel):
    league_season = models.ForeignKey(LeagueSeason, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160)
    short_name = models.CharField(max_length=60, blank=True)
    color = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["league_season", "name"], name="leaguehub_unique_team_name_per_season"),
            models.UniqueConstraint(fields=["league_season", "slug"], name="leaguehub_unique_team_slug_per_season"),
        ]
        indexes = [
            models.Index(fields=["league_season", "name"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.short_name or self.name)[:160] or "team"
        super().save(*args, **kwargs)


class CoachRole(models.TextChoices):
    HEAD_COACH = "head_coach", "Head coach"
    ASSISTANT_COACH = "assistant_coach", "Assistant coach"


class TeamCoachAssignment(TimeStampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="coach_assignments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team_assignments")
    role = models.CharField(max_length=20, choices=CoachRole.choices, default=CoachRole.HEAD_COACH)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["team__name", "role", "user__last_name", "user__first_name"]
        constraints = [
            models.UniqueConstraint(fields=["team", "user"], name="leaguehub_unique_coach_assignment"),
        ]
        indexes = [
            models.Index(fields=["team", "role", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.team}"

    def clean(self):
        missing = []
        if not self.user.first_name:
            missing.append("first_name")
        if not self.user.last_name:
            missing.append("last_name")
        if not self.user.email:
            missing.append("email")
        if missing:
            raise ValidationError(
                {"user": f"Coach user must include: {', '.join(missing)}."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class GameStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    LIVE = "live", "Live"
    FINAL = "final", "Final"
    POSTPONED = "postponed", "Postponed"
    CANCELED = "canceled", "Canceled"


class GameVerificationStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    AWAITING_AWAY_VERIFICATION = "awaiting_away_verification", "Awaiting away verification"
    VERIFIED_FINAL = "verified_final", "Verified final"


class Game(TimeStampedModel):
    league_season = models.ForeignKey(LeagueSeason, on_delete=models.CASCADE, related_name="games")
    game_date = models.DateField()
    scheduled_start_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=180, blank=True)
    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="home_games")
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="away_games")
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=GameStatus.choices, default=GameStatus.SCHEDULED)
    verification_status = models.CharField(
        max_length=30,
        choices=GameVerificationStatus.choices,
        default=GameVerificationStatus.SCHEDULED,
    )
    inning_label = models.CharField(max_length=40, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_games",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_games",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["-game_date", "-scheduled_start_time", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["home_team", "away_team", "game_date"],
                name="leaguehub_unique_game_matchup_date",
            ),
            models.CheckConstraint(check=~Q(home_team=F("away_team")), name="leaguehub_home_away_must_differ"),
        ]
        indexes = [
            models.Index(fields=["league_season", "game_date"]),
            models.Index(fields=["league_season", "status", "game_date"]),
            models.Index(fields=["league_season", "verification_status", "game_date"]),
            models.Index(fields=["league_season", "is_archived", "game_date"]),
            models.Index(fields=["home_team", "game_date"]),
            models.Index(fields=["away_team", "game_date"]),
        ]

    def __str__(self):
        return f"{self.away_team} at {self.home_team} ({self.game_date})"

    @property
    def has_valid_score(self):
        return self.home_score is not None and self.away_score is not None

    def clean(self):
        errors = {}
        if self.home_team_id and self.away_team_id and self.home_team_id == self.away_team_id:
            errors["away_team"] = "Home and away teams must be different."

        if self.league_season_id and self.home_team_id and self.home_team.league_season_id != self.league_season_id:
            errors["home_team"] = "Home team must belong to the same league season as the game."

        if self.league_season_id and self.away_team_id and self.away_team.league_season_id != self.league_season_id:
            errors["away_team"] = "Away team must belong to the same league season as the game."

        if self.verification_status == GameVerificationStatus.VERIFIED_FINAL and not self.has_valid_score:
            errors["verification_status"] = "A game cannot be verified final without a valid score."

        if self.status in {GameStatus.POSTPONED, GameStatus.CANCELED} and self.verification_status == GameVerificationStatus.VERIFIED_FINAL:
            errors["status"] = "Postponed or canceled games cannot be verified final."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class GameStory(TimeStampedModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="stories")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="game_stories")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="game_stories",
    )
    headline = models.CharField(max_length=180, blank=True)
    story = models.TextField()

    class Meta:
        ordering = ["game__game_date", "team__name"]
        constraints = [
            models.UniqueConstraint(fields=["game", "team"], name="leaguehub_unique_story_per_team_per_game"),
        ]
        indexes = [
            models.Index(fields=["game", "team"]),
        ]

    def __str__(self):
        return f"{self.team} story for {self.game}"

    def clean(self):
        if self.game_id and self.team_id and self.team_id not in {self.game.home_team_id, self.game.away_team_id}:
            raise ValidationError({"team": "Story team must be either the home or away team for the game."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class GamePhoto(TimeStampedModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="photos")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="game_photos")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="game_photos",
    )
    image = models.ImageField(upload_to="leaguehub/game_photos/")
    caption = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["game__game_date", "team__name"]
        constraints = [
            models.UniqueConstraint(fields=["game", "team"], name="leaguehub_unique_photo_per_team_per_game"),
        ]
        indexes = [
            models.Index(fields=["game", "team"]),
        ]

    def __str__(self):
        return f"{self.team} photo for {self.game}"

    def clean(self):
        if self.game_id and self.team_id and self.team_id not in {self.game.home_team_id, self.game.away_team_id}:
            raise ValidationError({"team": "Photo team must be either the home or away team for the game."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class GameScoreAuditEntry(TimeStampedModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="score_audit_entries")
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="game_score_audits",
    )
    previous_home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    previous_away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    new_home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    new_away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    previous_status = models.CharField(max_length=20, choices=GameStatus.choices, blank=True)
    new_status = models.CharField(max_length=20, choices=GameStatus.choices, blank=True)
    previous_verification_status = models.CharField(
        max_length=30,
        choices=GameVerificationStatus.choices,
        blank=True,
    )
    new_verification_status = models.CharField(
        max_length=30,
        choices=GameVerificationStatus.choices,
        blank=True,
    )
    note = models.TextField(blank=True)
    requires_reverification = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["game", "-created_at"]),
            models.Index(fields=["edited_by", "-created_at"]),
        ]

    def __str__(self):
        return f"Score audit for {self.game} at {self.created_at}"
