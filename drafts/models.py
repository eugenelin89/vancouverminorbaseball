from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class DraftStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"


class DraftActionType(models.TextChoices):
    PLAYER_IMPORTED = "player_imported", "Player imported"
    PLAYER_DRAFTED = "player_drafted", "Player drafted"
    DRAFT_PICK_REVERTED = "draft_pick_reverted", "Draft pick reverted"
    PLAYER_TRADED = "player_traded", "Player traded"
    PLAYER_MOVED = "player_moved", "Player moved"
    PLAYER_REMOVED = "player_removed", "Player removed"
    TEAM_CREATED = "team_created", "Team created"
    DRAFT_OPENED = "draft_opened", "Draft opened"
    DRAFT_CLOSED = "draft_closed", "Draft closed"
    DRAFT_REOPENED = "draft_reopened", "Draft reopened"


class Draft(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    year = models.PositiveIntegerField()
    division = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=DraftStatus.choices, default=DraftStatus.DRAFT)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_drafts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-year", "division", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or f"draft-{self.year}"
            slug = base_slug
            counter = 2
            while Draft.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("drafts:command-center", kwargs={"slug": self.slug})

    @property
    def is_open_for_moves(self):
        return self.status == DraftStatus.OPEN

    @property
    def available_player_count(self):
        return self.players.filter(current_team__isnull=True).count()

    @property
    def drafted_player_count(self):
        return self.players.filter(current_team__isnull=False).count()

    @property
    def total_player_count(self):
        return self.players.count()

    @property
    def next_pick_number(self):
        last_pick = self.actions.filter(action_type=DraftActionType.PLAYER_DRAFTED).aggregate(
            models.Max("pick_number")
        )["pick_number__max"]
        return (last_pick or 0) + 1


class DraftTeam(models.Model):
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=255)
    display_order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        unique_together = [("draft", "name"), ("draft", "display_order")]

    def __str__(self):
        return f"{self.draft.name}: {self.name}"

    @property
    def roster_count(self):
        prefetched = getattr(self, "_prefetched_objects_cache", {}).get("players")
        if prefetched is not None:
            return len(prefetched)
        return self.players.count()


class DraftPlayer(models.Model):
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, related_name="players")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255)
    current_team = models.ForeignKey(
        DraftTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="players",
    )
    extra_data = models.JSONField(default=dict, blank=True)
    imported_row = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name", "id"]
        unique_together = [("draft", "first_name", "last_name")]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)


class DraftAction(models.Model):
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=40, choices=DraftActionType.choices)
    player = models.ForeignKey(
        DraftPlayer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions",
    )
    from_team = models.ForeignKey(
        DraftTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions_from",
    )
    to_team = models.ForeignKey(
        DraftTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions_to",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="draft_actions",
    )
    metadata = models.JSONField(default=dict, blank=True)
    pick_number = models.PositiveIntegerField(null=True, blank=True)
    is_reverted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.get_action_type_display()} ({self.draft.name})"

    @property
    def can_revert(self):
        return not self.is_reverted and self.action_type in {
            DraftActionType.PLAYER_DRAFTED,
            DraftActionType.PLAYER_MOVED,
            DraftActionType.PLAYER_REMOVED,
            DraftActionType.PLAYER_TRADED,
            DraftActionType.DRAFT_OPENED,
            DraftActionType.DRAFT_CLOSED,
            DraftActionType.DRAFT_REOPENED,
        }
