from django.conf import settings
from django.db import models


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
