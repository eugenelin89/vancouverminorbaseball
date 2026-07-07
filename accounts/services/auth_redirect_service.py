from django.conf import settings

from accounts.models import AccountProfile


ACCOUNT_LOGIN_PATH = "/accounts/login/"
ACCOUNT_LOGOUT_PATH = "/accounts/logout/"
ACCOUNT_PASSWORD_PATH = "/accounts/password/"
ACCOUNT_PROFILE_PATH = "/accounts/profile/"
ANALYTICS_HOME_PATH = "/analytics/"
ACCOUNT_PASSWORD_ALLOWED_PATHS = {
    ACCOUNT_LOGIN_PATH,
    ACCOUNT_LOGOUT_PATH,
    ACCOUNT_PASSWORD_PATH,
}


def landing_url_for_user(user) -> str:
    """Return the post-auth landing URL for a user."""
    if not user or not getattr(user, "is_authenticated", False):
        return ACCOUNT_LOGIN_PATH
    if user.is_staff or user.is_superuser:
        return ANALYTICS_HOME_PATH
    return ACCOUNT_PROFILE_PATH


def should_force_password_change(user) -> bool:
    """Return whether an authenticated user must change their account password."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    try:
        return bool(user.account_profile.must_change_password)
    except AccountProfile.DoesNotExist:
        return False


def is_password_change_allowed_path(path: str, user) -> bool:
    """Return whether a path is allowed while password change is required."""
    if path in ACCOUNT_PASSWORD_ALLOWED_PATHS:
        return True
    static_url = getattr(settings, "STATIC_URL", "")
    media_url = getattr(settings, "MEDIA_URL", "")
    if static_url and path.startswith(static_url if static_url.startswith("/") else f"/{static_url}"):
        return True
    if media_url and path.startswith(media_url):
        return True
    return bool(path.startswith("/admin/") and user and getattr(user, "is_superuser", False))
