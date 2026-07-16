from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from seasons.models import Season, SeasonTeam, normalize_lookup_value


def normalize_team_value(value: str) -> str:
    return normalize_lookup_value(value)


def normalize_division_value(value: str) -> str:
    return normalize_lookup_value(value)


@transaction.atomic
def get_or_create_season_team(
    *,
    season: Season,
    name: str,
    division: str,
    external_source: str = "",
    external_identifier: str = "",
    metadata: dict | None = None,
) -> tuple[SeasonTeam, bool]:
    """Create or reuse a season-specific team."""
    normalized_name = normalize_team_value(name)
    normalized_division = normalize_division_value(division)
    if not normalized_name:
        raise ValidationError("Team name is required.")
    if not normalized_division:
        raise ValidationError("Division is required.")

    normalized_source = normalize_lookup_value(external_source).replace(" ", "_")
    normalized_identifier = normalize_lookup_value(external_identifier)
    if normalized_source and normalized_identifier:
        existing_by_external = SeasonTeam.objects.select_for_update().filter(
            season=season,
            external_source=normalized_source,
            external_identifier=normalized_identifier,
        ).first()
        if existing_by_external:
            if (
                existing_by_external.normalized_name != normalized_name
                or existing_by_external.normalized_division != normalized_division
            ):
                raise ValidationError("External team identifier points to a different season team.")
            return existing_by_external, False

    team = SeasonTeam.objects.select_for_update().filter(
        season=season,
        normalized_name=normalized_name,
        normalized_division=normalized_division,
    ).first()
    if team:
        return team, False

    team = SeasonTeam(
        season=season,
        name=name,
        division=division,
        external_source=external_source,
        external_identifier=external_identifier,
        metadata=metadata or {},
    )
    team.save()
    return team, True


@transaction.atomic
def update_season_team(team: SeasonTeam, **updates) -> SeasonTeam:
    for field, value in updates.items():
        setattr(team, field, value)
    team.save()
    return team

