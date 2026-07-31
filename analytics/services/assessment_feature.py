from django.conf import settings


def assessments_enabled() -> bool:
    """Return whether the versioned assessment subsystem is enabled."""
    return bool(getattr(settings, "ANALYTICS_ASSESSMENTS_ENABLED", False))
