from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import AccountProfile
from accounts.services.role_service import default_role_for_user, role_for_user, validate_role


def _validate_user(user) -> None:
    if not user or not getattr(user, "is_authenticated", False):
        raise ValidationError("An authenticated user is required.")


@transaction.atomic
def get_or_create_account_profile(user) -> AccountProfile:
    """Explicitly create or return the account profile for an authenticated user."""
    _validate_user(user)
    profile, _ = AccountProfile.objects.get_or_create(
        user=user,
        defaults={"role": default_role_for_user(user)},
    )
    return profile


@transaction.atomic
def set_account_role(user, role: str, actor=None) -> AccountProfile:
    """Set a user's account role without changing Django staff/superuser flags."""
    _validate_user(user)
    validated_role = validate_role(role)
    profile = get_or_create_account_profile(user)
    if profile.role != validated_role:
        profile.role = validated_role
        profile.save(update_fields=["role", "updated_at"])
    return profile


def get_account_role(user) -> str:
    """Return the user's current account role key."""
    return role_for_user(user)
