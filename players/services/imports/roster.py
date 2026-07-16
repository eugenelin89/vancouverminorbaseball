"""Seasonal roster integration for player imports."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from django.core.exceptions import ValidationError

from players.models import Player, PlayerImportBatch
from players.services.imports.parsing import clean_cell
from seasons.models import PlayerRosterMembership, RosterStatus, SeasonTeam
from seasons.services.membership_service import (
    create_membership,
    sync_player_current_team_fields,
    update_membership,
)
from seasons.services.team_service import (
    get_or_create_season_team,
    normalize_division_value,
    normalize_team_value,
)


def team_preview(roster: dict[str, Any], season) -> dict[str, Any]:
    team_name = roster.get("team_name", "")
    division = roster.get("division", "")
    if not team_name or not division:
        return {"action": "invalid_roster_context", "label": "Invalid Roster Context"}
    normalized_name = normalize_team_value(team_name)
    normalized_division = normalize_division_value(division)
    existing = SeasonTeam.objects.filter(
        season=season,
        normalized_name=normalized_name,
        normalized_division=normalized_division,
    ).first()
    return {
        "id": existing.id if existing else None,
        "name": existing.name if existing else team_name,
        "division": existing.division if existing else division,
        "action": "reuse" if existing else "create",
        "label": "Reuse Season Team" if existing else "Create Season Team",
    }


def membership_preview(
    player: Player | None,
    season_team_preview: dict[str, Any],
    season,
    roster: dict[str, Any],
) -> dict[str, Any]:
    if not player:
        return {
            "action": "create",
            "label": "Create Membership",
            "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE,
        }
    existing_same_team = None
    if season_team_preview.get("id"):
        existing_same_team = PlayerRosterMembership.objects.filter(
            player=player,
            season_team_id=season_team_preview["id"],
        ).first()
    if existing_same_team:
        return {
            "id": existing_same_team.id,
            "action": "update",
            "label": "Update Membership",
            "is_primary": existing_same_team.is_primary,
        }
    primary = (
        PlayerRosterMembership.objects.select_related("season_team")
        .filter(
            player=player,
            season_team__season=season,
            is_active=True,
            is_primary=True,
        )
        .first()
    )
    if primary:
        return {
            "id": None,
            "action": "review_team_change",
            "label": "Review Team Change",
            "is_primary": False,
            "existing_primary": str(primary.season_team),
        }
    return {
        "id": None,
        "action": "new_season_membership",
        "label": "New Season Membership",
        "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE,
    }


def parse_iso_date(value: str):
    cleaned = clean_cell(value)
    if not cleaned:
        return None
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Roster date is invalid.") from None


def membership_update_values(roster: dict[str, Any]) -> dict[str, Any]:
    values = {}
    if roster.get("roster_status"):
        values["status"] = roster["roster_status"]
        values["is_active"] = roster["roster_status"] in {
            RosterStatus.ACTIVE,
            RosterStatus.GUEST,
        }
        if not values["is_active"]:
            values["is_primary"] = False
    if roster.get("jersey_number"):
        values["jersey_number"] = roster["jersey_number"]
    if roster.get("starts_on"):
        values["starts_on"] = parse_iso_date(roster["starts_on"])
    if roster.get("ends_on"):
        values["ends_on"] = parse_iso_date(roster["ends_on"])
    if roster.get("roster_source_id"):
        values["source_identifier"] = roster["roster_source_id"]
    return values


def commit_membership(
    player: Player, import_batch: PlayerImportBatch, preview_row_data: dict[str, Any]
) -> tuple[str, bool]:
    if not import_batch.season_id:
        raise ValidationError(
            "Import batch requires a season before memberships can be committed."
        )
    roster = preview_row_data.get("roster", {})
    team_name = roster.get("team_name", "")
    division = roster.get("division", "")
    if not team_name or not division:
        raise ValidationError("Team and division are required for roster membership.")
    season_team, team_created = get_or_create_season_team(
        season=import_batch.season,
        name=team_name,
        division=division,
        external_source=import_batch.source if roster.get("roster_source_id") else "",
        external_identifier=roster.get("roster_source_id", ""),
        metadata={"import_batch_id": import_batch.id},
    )
    existing = (
        PlayerRosterMembership.objects.select_for_update()
        .filter(player=player, season_team=season_team)
        .first()
    )
    values = membership_update_values(roster)
    values.setdefault("source", import_batch.source)
    if existing:
        was_primary = existing.is_primary
        update_membership(existing, sync_player_fields=was_primary, **values)
        return "updated", team_created

    primary = (
        PlayerRosterMembership.objects.select_for_update()
        .filter(
            player=player,
            season_team__season=import_batch.season,
            is_active=True,
            is_primary=True,
        )
        .first()
    )
    if primary:
        raise ValidationError(
            "Player already has an active primary membership in this season."
        )
    status = values.pop("status", roster.get("roster_status") or RosterStatus.ACTIVE)
    is_active = values.pop(
        "is_active", status in {RosterStatus.ACTIVE, RosterStatus.GUEST}
    )
    membership = create_membership(
        player=player,
        season_team=season_team,
        status=status,
        is_primary=is_active,
        is_active=is_active,
        source=values.pop("source", import_batch.source),
        source_identifier=values.pop(
            "source_identifier", roster.get("roster_source_id", "")
        ),
        import_batch=import_batch,
        metadata={"row_number": preview_row_data["row_number"]},
        sync_player_fields=is_active,
        **values,
    )
    if membership.is_primary:
        sync_player_current_team_fields(player, import_batch.season)
    return "created", team_created
