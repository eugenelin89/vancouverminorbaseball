"""Season team and coach-assignment integration for coach imports."""

from __future__ import annotations

from django.db import transaction

from accounts.services.coach_import.parsing import parse_import_date
from accounts.services.coach_import.result_models import CoachImportRowPreview
from seasons.models import CoachSeasonAssignment, Season
from seasons.services.coach_assignment_service import (
    create_assignment,
    get_primary_assignment,
    update_assignment,
)
from seasons.services.team_service import (
    get_or_create_season_team,
    normalize_division_value,
    normalize_team_value,
)


def season_team_preview(*, season: Season, team: str, division: str) -> tuple[str, str]:
    normalized_team = normalize_team_value(team)
    normalized_division = normalize_division_value(division)
    existing = season.teams.filter(
        normalized_name=normalized_team,
        normalized_division=normalized_division,
    ).first()
    if existing:
        return "reuse", "Reuse Season Team"
    return "create", "Create Season Team"


def assignment_preview(
    *,
    user,
    season: Season,
    team: str,
    division: str,
    assignment_role: str,
    is_active: bool,
) -> tuple[str, str]:
    if not user:
        return "create", "Create Assignment"
    normalized_team = normalize_team_value(team)
    normalized_division = normalize_division_value(division)
    existing = (
        CoachSeasonAssignment.objects.select_related("season_team")
        .filter(
            user=user,
            season_team__season=season,
            season_team__normalized_name=normalized_team,
            season_team__normalized_division=normalized_division,
            assignment_role=assignment_role,
        )
        .first()
    )
    if existing:
        return "update", (
            "Update Assignment" if is_active else "Update Inactive Assignment"
        )
    return "create", "Create Assignment"


def metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
    return {
        key: value
        for key, value in {
            "team": row.team,
            "division": row.division,
            "notes": row.notes,
            "source_id": row.source_id,
            "assignment_role": row.assignment_role,
            "source": "coach_roster",
        }.items()
        if value
    }


def profile_metadata(profile) -> dict:
    return profile.metadata if isinstance(profile.metadata, dict) else {}


@transaction.atomic
def commit_assignment(
    user, row: CoachImportRowPreview, season: Season
) -> tuple[str, bool]:
    season_team, team_created = get_or_create_season_team(
        season=season,
        name=row.team,
        division=row.division,
        metadata={"source": "coach_roster"},
    )
    assignment = (
        CoachSeasonAssignment.objects.select_for_update()
        .filter(
            user=user,
            season_team=season_team,
            assignment_role=row.assignment_role,
        )
        .first()
    )
    starts_on = parse_import_date(row.assignment_start_date)
    ends_on = parse_import_date(row.assignment_end_date)
    updates = {"is_active": row.is_active}
    if not row.is_active:
        updates["is_primary"] = False
    if starts_on:
        updates["starts_on"] = starts_on
    if ends_on:
        updates["ends_on"] = ends_on
    if row.assignment_source_id:
        updates["source_identifier"] = row.assignment_source_id
    updates["source"] = "coach_roster"
    updates["metadata"] = {
        key: value
        for key, value in {"notes": row.notes, "source_id": row.source_id}.items()
        if value
    }
    if assignment:
        update_assignment(assignment, **updates)
        return "updated", team_created
    is_primary = row.is_active and get_primary_assignment(user, season) is None
    create_assignment(
        user=user,
        season_team=season_team,
        assignment_role=row.assignment_role,
        is_primary=is_primary,
        is_active=row.is_active,
        starts_on=starts_on,
        ends_on=ends_on,
        source="coach_roster",
        source_identifier=row.assignment_source_id,
        metadata={
            key: value
            for key, value in {"notes": row.notes, "source_id": row.source_id}.items()
            if value
        },
    )
    return "created", team_created
