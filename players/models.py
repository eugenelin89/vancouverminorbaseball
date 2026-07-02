from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def normalize_lookup_value(value: str) -> str:
    return " ".join(str(value or "").strip().casefold().split())


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Player(TimeStampedModel):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    preferred_name = models.CharField(max_length=80, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    birth_year = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=40, blank=True)
    division = models.CharField(max_length=80, blank=True)
    team_name = models.CharField(max_length=120, blank=True)
    school = models.CharField(max_length=160, blank=True)
    graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)
    bats = models.CharField(max_length=20, blank=True)
    throws = models.CharField(max_length=20, blank=True)
    primary_positions = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["last_name", "first_name", "id"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["division", "team_name"]),
            models.Index(fields=["is_active", "last_name"]),
            models.Index(fields=["birthdate"]),
            models.Index(fields=["birth_year"]),
        ]

    @property
    def full_name(self) -> str:
        return " ".join(part for part in [self.first_name, self.last_name] if part).strip()

    @property
    def display_name(self) -> str:
        if self.preferred_name:
            return " ".join(part for part in [self.preferred_name, self.last_name] if part).strip()
        return self.full_name

    def __str__(self) -> str:
        return self.display_name


class PlayerAlias(TimeStampedModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="aliases")
    alias = models.CharField(max_length=160)
    normalized_alias = models.CharField(max_length=160, editable=False)
    source = models.CharField(max_length=120, blank=True)
    context = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["normalized_alias", "id"]
        constraints = [
            models.UniqueConstraint(fields=["player", "normalized_alias"], name="players_unique_alias_per_player"),
        ]
        indexes = [
            models.Index(fields=["normalized_alias"]),
        ]

    def save(self, *args, **kwargs):
        self.normalized_alias = normalize_lookup_value(self.alias)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.alias


class PlayerSourceIdentifier(TimeStampedModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="source_identifiers")
    source = models.CharField(max_length=80)
    identifier_type = models.CharField(max_length=80)
    identifier_value = models.CharField(max_length=160)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["source", "identifier_type", "identifier_value"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "identifier_type", "identifier_value"],
                name="players_unique_source_identifier",
            ),
        ]
        indexes = [
            models.Index(fields=["source", "identifier_type"]),
            models.Index(fields=["identifier_value"]),
        ]

    def save(self, *args, **kwargs):
        self.source = normalize_lookup_value(self.source)
        self.identifier_type = normalize_lookup_value(self.identifier_type)
        self.identifier_value = normalize_lookup_value(self.identifier_value)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.source}:{self.identifier_type}:{self.identifier_value}"


class PlayerImportStatus(models.TextChoices):
    UPLOADED = "uploaded", "Uploaded"
    PREVIEWED = "previewed", "Previewed"
    NEEDS_REVIEW = "needs_review", "Needs Review"
    COMMITTED = "committed", "Committed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class PlayerImportBatch(TimeStampedModel):
    source = models.CharField(max_length=80)
    original_filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_import_batches",
    )
    status = models.CharField(max_length=40, choices=PlayerImportStatus.choices, default=PlayerImportStatus.UPLOADED)
    mapping_config = models.JSONField(default=dict, blank=True)
    preview_snapshot = models.JSONField(default=dict, blank=True)
    row_errors = models.JSONField(default=list, blank=True)
    conflict_summary = models.JSONField(default=dict, blank=True)
    import_summary = models.JSONField(default=dict, blank=True)
    rows_processed = models.PositiveIntegerField(default=0)
    rows_created = models.PositiveIntegerField(default=0)
    rows_updated = models.PositiveIntegerField(default=0)
    rows_skipped = models.PositiveIntegerField(default=0)
    rows_conflicted = models.PositiveIntegerField(default=0)
    committed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["source", "-created_at"]),
            models.Index(fields=["uploaded_by", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        self.source = normalize_lookup_value(self.source).replace(" ", "_")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.original_filename


class PlayerSourceRow(TimeStampedModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="source_rows")
    import_batch = models.ForeignKey(
        PlayerImportBatch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="source_rows",
    )
    source = models.CharField(max_length=80)
    source_filename = models.CharField(max_length=255, blank=True)
    row_number = models.PositiveIntegerField(null=True, blank=True)
    original_row = models.JSONField(default=dict, blank=True)
    unmapped_fields = models.JSONField(default=dict, blank=True)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="imported_player_source_rows",
    )
    imported_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-imported_at", "-id"]
        indexes = [
            models.Index(fields=["source", "source_filename"]),
            models.Index(fields=["player", "source"]),
            models.Index(fields=["imported_at"]),
            models.Index(fields=["import_batch", "row_number"]),
        ]

    def save(self, *args, **kwargs):
        self.source = normalize_lookup_value(self.source)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        row = f" row {self.row_number}" if self.row_number else ""
        return f"{self.source}{row} for {self.player}"


class PlayerTag(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    players = models.ManyToManyField(Player, related_name="tags", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "tag"
            slug = base_slug[:100]
            counter = 2
            while PlayerTag.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                suffix = f"-{counter}"
                slug = f"{base_slug[:100 - len(suffix)]}{suffix}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
