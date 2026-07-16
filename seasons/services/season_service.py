from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from seasons.models import Season


def create_season(
    *,
    key: str,
    name: str,
    starts_on=None,
    ends_on=None,
    is_active: bool = True,
    is_current: bool = False,
    metadata: dict | None = None,
) -> Season:
    """Create a season, using the current-season service when needed."""
    if is_current:
        season = Season(
            key=key,
            name=name,
            starts_on=starts_on,
            ends_on=ends_on,
            is_active=is_active,
            is_current=False,
            metadata=metadata or {},
        )
        season.save()
        return set_current_season(season)
    season = Season(
        key=key,
        name=name,
        starts_on=starts_on,
        ends_on=ends_on,
        is_active=is_active,
        metadata=metadata or {},
    )
    season.save()
    return season


@transaction.atomic
def update_season(season: Season, **updates) -> Season:
    """Update season fields with model validation."""
    requested_current = updates.pop("is_current", None)
    if requested_current is True and not season.is_current:
        for field, value in updates.items():
            setattr(season, field, value)
        season.save()
        return set_current_season(season)
    if requested_current is not None:
        season.is_current = requested_current
    for field, value in updates.items():
        setattr(season, field, value)
    if season.is_current and not season.is_active:
        season.is_current = False
    season.save()
    return season


def get_current_season() -> Season | None:
    """Return the current season, or None before initial setup."""
    return Season.objects.filter(is_current=True).order_by("id").first()


@transaction.atomic
def set_current_season(season: Season) -> Season:
    """Atomically mark one season current and clear all others."""
    locked = list(Season.objects.select_for_update().all())
    if season.pk is None:
        raise ValidationError("Save the season before making it current.")
    Season.objects.exclude(pk=season.pk).filter(is_current=True).update(is_current=False)
    if season not in locked:
        season = Season.objects.select_for_update().get(pk=season.pk)
    season.is_current = True
    season.save(update_fields=["is_current", "updated_at"])
    return season


def activate_season(season: Season) -> Season:
    season.is_active = True
    season.save(update_fields=["is_active", "updated_at"])
    return season


def deactivate_season(season: Season) -> Season:
    season.is_active = False
    if season.is_current:
        season.is_current = False
        season.save(update_fields=["is_active", "is_current", "updated_at"])
    else:
        season.save(update_fields=["is_active", "updated_at"])
    return season
