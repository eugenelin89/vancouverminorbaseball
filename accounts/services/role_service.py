from django.core.exceptions import ValidationError

from accounts.models import AccountProfile, AccountRole


def default_role_for_user(user) -> str:
    """Return the default account role for a user without an explicit profile."""
    if user and getattr(user, "is_superuser", False):
        return AccountRole.ADMIN
    if user and getattr(user, "is_staff", False):
        return AccountRole.STAFF
    return AccountRole.GUEST_EVALUATOR


def validate_role(role: str) -> str:
    """Validate and return a supported account role key."""
    valid_roles = {choice.value for choice in AccountRole}
    if role not in valid_roles:
        raise ValidationError(f"Unsupported account role: {role}.")
    return role


def role_for_user(user) -> str:
    """Return a user's account role, falling back to Django staff flags when needed."""
    if not user or not getattr(user, "is_authenticated", False):
        return AccountRole.GUEST_EVALUATOR
    try:
        return user.account_profile.role
    except AccountProfile.DoesNotExist:
        return default_role_for_user(user)


def role_label(role: str) -> str:
    """Return the display label for an account role."""
    validate_role(role)
    return AccountRole(role).label
