from django.contrib.auth import get_user_model


User = get_user_model()


def normalize_email(value: str) -> str:
    """Normalize an email for account provisioning comparisons."""
    return str(value or "").strip().casefold()


def emails_equal(left: str, right: str) -> bool:
    return normalize_email(left) == normalize_email(right)


def find_existing_email_user(email: str):
    """Return the first user with the normalized email, if any."""
    normalized = normalize_email(email)
    if not normalized:
        return None
    return User.objects.filter(email__iexact=normalized).order_by("id").first()
