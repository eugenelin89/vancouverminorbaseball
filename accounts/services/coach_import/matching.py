"""Account matching helpers for coach imports."""

from accounts.services.profile_service import get_or_create_account_profile


def role_for_user(user) -> str:
    profile = getattr(user, "account_profile", None)
    if profile:
        return profile.role
    return get_or_create_account_profile(user).role
