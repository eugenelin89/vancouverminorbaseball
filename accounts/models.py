from django.conf import settings
from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AccountRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    COACH = "coach", "Coach"
    PLAYER = "player", "Player"
    PARENT = "parent", "Parent"
    GUEST_EVALUATOR = "guest_evaluator", "Guest Evaluator"


class UserPlayerRelationship(models.TextChoices):
    SELF = "self", "Self"
    PARENT = "parent", "Parent"
    GUARDIAN = "guardian", "Guardian"
    COACH = "coach", "Coach"
    STAFF = "staff", "Staff"


class AccountProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_profile",
    )
    role = models.CharField(max_length=40, choices=AccountRole.choices, default=AccountRole.GUEST_EVALUATOR)
    must_change_password = models.BooleanField(default=False)
    created_from_import = models.BooleanField(default=False)
    import_batch = models.ForeignKey(
        "players.PlayerImportBatch",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="account_profiles",
    )
    # Account lifecycle remains intentionally simple in Phase 1. Django User.is_active
    # is still authoritative; richer account states can be introduced later.
    activated_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["user__username", "id"]
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["created_from_import"]),
            models.Index(fields=["must_change_password"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} ({self.get_role_display()})"


class UserPlayerLink(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="player_links",
    )
    player = models.ForeignKey(
        "players.Player",
        on_delete=models.CASCADE,
        related_name="user_links",
    )
    relationship = models.CharField(max_length=40, choices=UserPlayerRelationship.choices)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_from_import = models.BooleanField(default=False)
    import_batch = models.ForeignKey(
        "players.PlayerImportBatch",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_player_links",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["user__username", "relationship", "player__last_name", "player__first_name", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "player", "relationship"],
                condition=Q(is_active=True),
                name="accounts_unique_active_user_player_relationship",
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_active=True, is_primary=True, relationship=UserPlayerRelationship.SELF),
                name="accounts_unique_primary_self_link_per_user",
            ),
            models.UniqueConstraint(
                fields=["player"],
                condition=Q(is_active=True, is_primary=True, relationship=UserPlayerRelationship.SELF),
                name="accounts_unique_primary_self_link_per_player",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["player", "is_active"]),
            models.Index(fields=["relationship", "is_active"]),
            models.Index(fields=["created_from_import"]),
            models.Index(fields=["import_batch"]),
        ]

    def __str__(self) -> str:
        inactive = " inactive" if not self.is_active else ""
        return f"{self.user} {self.get_relationship_display()} -> {self.player}{inactive}"
