import re
import unicodedata

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()
USERNAME_ALLOWED_PATTERN = re.compile(r"[^a-z0-9._-]+")


def normalize_username_part(value: str) -> str:
    """Normalize a name part into a deterministic username-safe token."""
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    collapsed = " ".join(ascii_value.casefold().strip().split())
    safe = USERNAME_ALLOWED_PATTERN.sub("", collapsed.replace(" ", ""))
    return safe.strip("._-")


def base_username_for_player(player) -> str:
    """Return firstname.lastname username base for a player."""
    first = normalize_username_part(getattr(player, "first_name", ""))
    last = normalize_username_part(getattr(player, "last_name", ""))
    if not first or not last:
        raise ValidationError("Player first and last name are required to generate a username.")
    return f"{first}.{last}"


def username_for_player(player) -> str:
    """Return a unique deterministic username for a player."""
    base_username = base_username_for_player(player)
    username = base_username
    suffix = 2
    while User.objects.filter(username__iexact=username).exists():
        username = f"{base_username}{suffix}"
        suffix += 1
    return username
