import secrets
from datetime import date

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.services.profile_service import get_or_create_account_profile

COACH_IMPORT_DEFAULT_PASSWORD_SETTING = "COACH_IMPORT_DEFAULT_PASSWORD"


def generate_birthdate_password(player) -> str:
    """Return the temporary birthdate password for player-account provisioning only."""
    birthdate = getattr(player, "birthdate", None)
    if not birthdate:
        raise ValidationError("Player birthdate is required for account provisioning.")
    if isinstance(birthdate, str):
        try:
            birthdate = date.fromisoformat(birthdate)
        except ValueError as exc:
            raise ValidationError("Player birthdate must be a valid date.") from exc
    return birthdate.strftime("%Y%m%d")


def set_temporary_password(user, player) -> None:
    """Set a hashed temporary password without returning or storing plaintext."""
    user.set_password(generate_birthdate_password(player))
    user.save(update_fields=["password"])


def generate_random_temporary_password(length: int = 18) -> str:
    """Return a secure random temporary password for non-player accounts."""
    if length < 12:
        raise ValidationError(
            "Temporary password length must be at least 12 characters."
        )
    return secrets.token_urlsafe(length)[:length]


def set_random_temporary_password(user, length: int = 18) -> str:
    """Set and return a one-time random temporary password."""
    password = generate_random_temporary_password(length=length)
    user.set_password(password)
    user.save(update_fields=["password"])
    return password


def get_coach_import_default_password() -> str:
    """Return the configured shared coach-import password or fail safely."""
    password = getattr(settings, COACH_IMPORT_DEFAULT_PASSWORD_SETTING, "")
    password = "" if password is None else str(password).strip()
    if not password:
        raise ValidationError(
            f"{COACH_IMPORT_DEFAULT_PASSWORD_SETTING} must be configured before creating coach accounts."
        )
    return password


def validate_coach_import_default_password(users=None) -> str:
    """Validate the configured coach-import password without exposing it."""
    password = get_coach_import_default_password()
    validation_users = list(users or [None])
    for user in validation_users:
        validate_password(password, user=user)
    return password


def set_coach_import_default_password(user) -> None:
    """Set a hashed shared default password for a newly imported coach account."""
    password = validate_coach_import_default_password(users=[user])
    user.set_password(password)
    user.save(update_fields=["password"])


@transaction.atomic
def mark_password_change_required(user, value=True):
    """Set the account profile password-change requirement."""
    profile = get_or_create_account_profile(user)
    profile.must_change_password = value
    profile.save(update_fields=["must_change_password", "updated_at"])
    return profile


def clear_password_change_required(user):
    """Clear the account profile password-change requirement."""
    return mark_password_change_required(user, False)
