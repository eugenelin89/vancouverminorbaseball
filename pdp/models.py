from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Season(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    year = models.PositiveIntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-year", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or f"season-{self.year}"
            slug = base_slug
            counter = 2
            while Season.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class AccessRole(models.TextChoices):
    PLAYER = "player", "Player"
    PARENT = "parent", "Parent"
    COACH = "coach", "Coach"
    ADMIN = "admin", "Admin"


class PlayerProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="player_profile",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=220, blank=True)
    email = models.EmailField(blank=True)
    external_player_id = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    primary_position = models.CharField(max_length=100, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    level = models.CharField(max_length=100, blank=True)
    throws = models.CharField(max_length=20, blank=True)
    bats = models.CharField(max_length=20, blank=True)
    must_change_password = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["last_name", "first_name", "id"]

    def __str__(self):
        return self.full_name or f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("pdp:player-dashboard", kwargs={"player_id": self.pk})


class CoachAssignment(TimeStampedModel):
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coached_players",
    )
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="coach_assignments")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True, related_name="coach_assignments")
    role = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("coach", "player", "season")]
        ordering = ["player__last_name", "player__first_name"]

    def __str__(self):
        return f"{self.coach} -> {self.player}"


class ParentChildAccess(TimeStampedModel):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="child_access_links",
    )
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="parent_links")
    relationship_label = models.CharField(max_length=80, blank=True)
    can_view_private_notes = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("parent", "player")]
        ordering = ["player__last_name", "player__first_name"]

    def __str__(self):
        return f"{self.parent} -> {self.player}"


class ImportStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PREVIEWED = "previewed", "Previewed"
    IMPORTED = "imported", "Imported"
    PARTIAL = "partial", "Partial"
    FAILED = "failed", "Failed"


class EvaluationImportTemplate(TimeStampedModel):
    name = models.CharField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    configuration = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_import_templates",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class EvaluationImport(TimeStampedModel):
    template = models.ForeignKey(
        EvaluationImportTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imports",
    )
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="imports")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluation_imports",
    )
    file_name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=40, default="workbook")
    status = models.CharField(max_length=20, choices=ImportStatus.choices, default=ImportStatus.DRAFT)
    workbook_metadata = models.JSONField(default=dict, blank=True)
    mapping_config = models.JSONField(default=dict, blank=True)
    preview_snapshot = models.JSONField(default=dict, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)
    row_errors = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_name} ({self.get_status_display()})"


class EvaluationEventType(models.TextChoices):
    TRYOUT = "tryout", "Tryout"
    BASELINE = "baseline", "Baseline"
    MID_SEASON = "mid_season", "Mid-season"
    END_SEASON = "end_season", "End of season"
    OFFSEASON = "offseason", "Offseason"
    CUSTOM = "custom", "Custom"


class EvaluationEvent(TimeStampedModel):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="evaluation_events")
    name = models.CharField(max_length=140)
    event_type = models.CharField(max_length=30, choices=EvaluationEventType.choices, default=EvaluationEventType.CUSTOM)
    description = models.TextField(blank=True)
    evaluated_on = models.DateField()
    source_import = models.ForeignKey(
        EvaluationImport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluation_events",
    )
    is_published = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-evaluated_on", "-id"]
        unique_together = [("season", "name", "evaluated_on")]

    def __str__(self):
        return f"{self.name} ({self.evaluated_on})"


class PlayerEvaluation(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="evaluations")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="player_evaluations")
    evaluation_event = models.ForeignKey(EvaluationEvent, on_delete=models.CASCADE, related_name="player_evaluations")
    import_record = models.ForeignKey(
        EvaluationImport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="player_evaluations",
    )
    source_sheet = models.CharField(max_length=140, blank=True)
    source_row_number = models.PositiveIntegerField(null=True, blank=True)
    summary_text = models.TextField(blank=True)
    raw_row_data = models.JSONField(default=dict, blank=True)
    unmapped_data = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-evaluation_event__evaluated_on", "-id"]
        unique_together = [("player", "evaluation_event")]

    def __str__(self):
        return f"{self.player} - {self.evaluation_event}"


class MetricType(models.TextChoices):
    NUMBER = "number", "Number"
    TEXT = "text", "Text"
    RATING = "rating", "Rating"
    BOOLEAN = "boolean", "Boolean"


class PlayerMetric(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="metrics")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="metrics")
    evaluation_event = models.ForeignKey(EvaluationEvent, on_delete=models.CASCADE, related_name="metrics")
    player_evaluation = models.ForeignKey(PlayerEvaluation, on_delete=models.CASCADE, related_name="metrics")
    metric_key = models.SlugField(max_length=120)
    display_name = models.CharField(max_length=140)
    category = models.CharField(max_length=100, blank=True)
    metric_type = models.CharField(max_length=20, choices=MetricType.choices, default=MetricType.NUMBER)
    numeric_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    text_value = models.CharField(max_length=255, blank=True)
    rating_value = models.CharField(max_length=60, blank=True)
    raw_value = models.CharField(max_length=255, blank=True)
    unit = models.CharField(max_length=30, blank=True)
    ranking_label = models.CharField(max_length=80, blank=True)
    source_sheet = models.CharField(max_length=140, blank=True)
    source_column = models.CharField(max_length=140, blank=True)
    measured_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["category", "display_name", "evaluation_event__evaluated_on"]
        indexes = [
            models.Index(fields=["player", "metric_key"]),
            models.Index(fields=["season", "metric_key"]),
        ]

    def __str__(self):
        return f"{self.player} - {self.display_name}"


class DevelopmentLogType(models.TextChoices):
    PRACTICE = "practice", "Practice"
    GAME = "game", "Game"
    BULLPEN = "bullpen", "Bullpen"
    HITTING = "hitting", "Hitting"
    FIELDING = "fielding", "Fielding"
    PITCHING = "pitching", "Pitching"
    STRENGTH = "strength", "Strength"
    REFLECTION = "reflection", "Reflection"
    GENERAL = "general", "General"


class VisibilityLevel(models.TextChoices):
    PLAYER = "player", "Player and family"
    COACH = "coach", "Coach only"
    STAFF = "staff", "Staff only"


class PlayerDevelopmentLog(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="development_logs")
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="development_logs")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="player_development_logs",
    )
    log_type = models.CharField(max_length=20, choices=DevelopmentLogType.choices, default=DevelopmentLogType.GENERAL)
    title = models.CharField(max_length=140)
    note = models.TextField()
    skill_tags = models.CharField(max_length=255, blank=True)
    visibility = models.CharField(max_length=20, choices=VisibilityLevel.choices, default=VisibilityLevel.PLAYER)
    occurred_at = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-occurred_at", "-id"]

    def __str__(self):
        return f"{self.player} - {self.title}"


class GoalStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    ON_HOLD = "on_hold", "On hold"
    ARCHIVED = "archived", "Archived"


class DevelopmentGoal(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="goals")
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="goals")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="development_goals",
    )
    title = models.CharField(max_length=140)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=GoalStatus.choices, default=GoalStatus.ACTIVE)
    target_metric_key = models.CharField(max_length=120, blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_unit = models.CharField(max_length=30, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    progress_notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["status", "due_date", "title"]

    def __str__(self):
        return f"{self.player} - {self.title}"


class AnalysisRunStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class GeneratedByType(models.TextChoices):
    SYSTEM = "system", "System"
    AI = "ai", "AI"
    COACH = "coach", "Coach"


class AIAnalysisRun(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, null=True, blank=True, related_name="analysis_runs")
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="analysis_runs")
    evaluation_event = models.ForeignKey(
        EvaluationEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analysis_runs",
    )
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_ai_runs",
    )
    analysis_type = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=AnalysisRunStatus.choices, default=AnalysisRunStatus.PENDING)
    provider = models.CharField(max_length=80, blank=True)
    model_name = models.CharField(max_length=120, blank=True)
    input_snapshot = models.JSONField(default=dict, blank=True)
    output_payload = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.analysis_type} ({self.get_status_display()})"


class InsightType(models.TextChoices):
    SUMMARY = "summary", "Summary"
    OPPORTUNITY = "opportunity", "Opportunity"
    TREND = "trend", "Trend"
    ROADMAP = "roadmap", "Roadmap"
    REPORT = "report", "Report"


class InsightAudience(models.TextChoices):
    PLAYER = "player", "Player"
    COACH = "coach", "Coach"
    PARENT = "parent", "Parent"


class PlayerInsight(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="insights")
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="insights")
    evaluation_event = models.ForeignKey(
        EvaluationEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="insights",
    )
    analysis_run = models.ForeignKey(
        AIAnalysisRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="insights",
    )
    insight_type = models.CharField(max_length=30, choices=InsightType.choices, default=InsightType.SUMMARY)
    audience = models.CharField(max_length=20, choices=InsightAudience.choices, default=InsightAudience.PLAYER)
    title = models.CharField(max_length=140)
    summary = models.TextField()
    strengths = models.TextField(blank=True)
    development_opportunities = models.TextField(blank=True)
    recommended_actions = models.TextField(blank=True)
    generated_by_type = models.CharField(max_length=20, choices=GeneratedByType.choices, default=GeneratedByType.SYSTEM)
    is_current = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.player} - {self.title}"


class ReportTemplate(TimeStampedModel):
    name = models.CharField(max_length=140)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True, related_name="report_templates")
    division = models.CharField(max_length=80, blank=True)
    categories = models.JSONField(default=list, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        unique_together = [("name", "season", "division")]

    def __str__(self):
        return self.name


class EndOfSeasonReport(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="season_reports")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="season_reports")
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coached_reports",
    )
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
    )
    summary = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    development_opportunities = models.TextField(blank=True)
    offseason_focus = models.TextField(blank=True)
    overall_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overall_comments = models.TextField(blank=True)
    printable_summary = models.TextField(blank=True)
    is_final = models.BooleanField(default=False)

    class Meta:
        ordering = ["-season__year", "player__last_name"]
        unique_together = [("player", "season")]

    def __str__(self):
        return f"{self.player} - {self.season}"


class EndOfSeasonReportItem(TimeStampedModel):
    report = models.ForeignKey(EndOfSeasonReport, on_delete=models.CASCADE, related_name="items")
    category = models.CharField(max_length=100)
    rating_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rubric_rating = models.CharField(max_length=80, blank=True)
    text_feedback = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.report} - {self.category}"


class SnapshotType(models.TextChoices):
    START_OF_SEASON = "start_of_season", "Start of season"
    MID_SEASON = "mid_season", "Mid-season"
    END_OF_SEASON = "end_of_season", "End of season"
    YEAR_OVER_YEAR = "year_over_year", "Year over year"
    CUSTOM = "custom", "Custom"


class ProgressSnapshot(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="snapshots")
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="snapshots")
    evaluation_event = models.ForeignKey(
        EvaluationEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="snapshots",
    )
    snapshot_type = models.CharField(max_length=30, choices=SnapshotType.choices, default=SnapshotType.CUSTOM)
    title = models.CharField(max_length=140)
    summary = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    improvement_areas = models.TextField(blank=True)
    next_priorities = models.TextField(blank=True)
    metric_summary_data = models.JSONField(default=dict, blank=True)
    source_data_snapshot = models.JSONField(default=dict, blank=True)
    generated_by_type = models.CharField(max_length=20, choices=GeneratedByType.choices, default=GeneratedByType.SYSTEM)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.player} - {self.title}"


class DevelopmentRoadmap(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="roadmaps")
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="roadmaps")
    generated_by_type = models.CharField(max_length=20, choices=GeneratedByType.choices, default=GeneratedByType.SYSTEM)
    title = models.CharField(max_length=140)
    summary = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    short_term_focus = models.TextField(blank=True)
    medium_term_focus = models.TextField(blank=True)
    offseason_focus = models.TextField(blank=True)
    source_snapshot = models.JSONField(default=dict, blank=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.player} - {self.title}"


class RoadmapTimeframe(models.TextChoices):
    SHORT_TERM = "short_term", "Short-term"
    MID_TERM = "mid_term", "Mid-term"
    LONG_TERM = "long_term", "Long-term"
    OFFSEASON = "offseason", "Offseason"


class AssignmentStatus(models.TextChoices):
    ASSIGNED = "assigned", "Assigned"
    IN_PROGRESS = "in_progress", "In progress"
    COMPLETED = "completed", "Completed"
    ARCHIVED = "archived", "Archived"


class DrillDifficulty(models.TextChoices):
    FOUNDATIONAL = "foundational", "Foundational"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"


class DrillResource(TimeStampedModel):
    title = models.CharField(max_length=140)
    category = models.CharField(max_length=100)
    skill_tags = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    coaching_points = models.TextField(blank=True)
    recommended_for = models.TextField(blank=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=DrillDifficulty.choices,
        default=DrillDifficulty.FOUNDATIONAL,
    )
    media_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self):
        return self.title


class DevelopmentRoadmapItem(TimeStampedModel):
    roadmap = models.ForeignKey(DevelopmentRoadmap, on_delete=models.CASCADE, related_name="items")
    priority_level = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=140)
    description = models.TextField()
    target_metric_key = models.CharField(max_length=120, blank=True)
    target_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target_unit = models.CharField(max_length=30, blank=True)
    timeframe = models.CharField(max_length=20, choices=RoadmapTimeframe.choices, default=RoadmapTimeframe.SHORT_TERM)
    linked_goal = models.ForeignKey(
        DevelopmentGoal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roadmap_items",
    )
    linked_drill_resource = models.ForeignKey(
        DrillResource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roadmap_items",
    )
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.ASSIGNED)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["priority_level", "display_order", "id"]

    def __str__(self):
        return f"{self.roadmap} - {self.title}"


class AssignmentSourceType(models.TextChoices):
    COACH = "coach", "Coach"
    AI = "ai", "AI"
    ROADMAP = "roadmap", "Roadmap"
    REPORT_CARD = "report_card", "Report card"


class PlayerDrillAssignment(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="drill_assignments")
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="drill_assignments")
    drill_resource = models.ForeignKey(DrillResource, on_delete=models.CASCADE, related_name="assignments")
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drill_assignments",
    )
    source_type = models.CharField(max_length=20, choices=AssignmentSourceType.choices, default=AssignmentSourceType.COACH)
    roadmap_item = models.ForeignKey(
        DevelopmentRoadmapItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drill_assignments",
    )
    goal = models.ForeignKey(
        DevelopmentGoal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drill_assignments",
    )
    report = models.ForeignKey(
        EndOfSeasonReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drill_assignments",
    )
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.ASSIGNED)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["status", "due_date", "drill_resource__title"]

    def __str__(self):
        return f"{self.player} - {self.drill_resource}"


class ExternalPerformanceSource(TimeStampedModel):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="external_sources")
    provider_name = models.CharField(max_length=120)
    source_type = models.CharField(max_length=80)
    external_identifier = models.CharField(max_length=140)
    measurement_timestamp = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["provider_name", "source_type"]
        unique_together = [("player", "provider_name", "external_identifier")]

    def __str__(self):
        return f"{self.provider_name} - {self.player}"
