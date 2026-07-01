from __future__ import annotations

from typing import Any

from django.db import transaction

from players.models import Player, PlayerAlias, PlayerSourceIdentifier, PlayerSourceRow, normalize_lookup_value


def normalize_name(value: str) -> str:
    """Normalize a player name for matching and duplicate checks."""
    return normalize_lookup_value(value)


def normalize_identifier(value: str) -> str:
    """Normalize a source identifier for deterministic lookup."""
    return normalize_lookup_value(value)


def build_display_name(player: Player) -> str:
    """Return the display name used for player-facing and staff-facing summaries."""
    return player.display_name


def create_player(**fields: Any) -> Player:
    """Create a canonical player identity record."""
    return Player.objects.create(**fields)


def update_player_identity(player: Player, **fields: Any) -> Player:
    """Update basic canonical player identity fields."""
    for field_name, value in fields.items():
        setattr(player, field_name, value)
    update_fields = list(fields.keys())
    if update_fields:
        update_fields.append("updated_at")
        player.save(update_fields=update_fields)
    return player


def create_alias(player: Player, alias: str, source: str = "", context: str = "") -> PlayerAlias:
    """Create an alternate name for a player."""
    return PlayerAlias.objects.create(player=player, alias=alias, source=source, context=context)


def add_source_identifier(
    player: Player,
    source: str,
    identifier_type: str,
    identifier_value: str,
    metadata: dict[str, Any] | None = None,
) -> PlayerSourceIdentifier:
    """Attach a normalized source identifier to a player."""
    return PlayerSourceIdentifier.objects.create(
        player=player,
        source=source,
        identifier_type=identifier_type,
        identifier_value=identifier_value,
        metadata=metadata or {},
    )


@transaction.atomic
def record_source_row(
    player: Player,
    source: str,
    source_filename: str = "",
    row_number: int | None = None,
    original_row: dict[str, Any] | None = None,
    unmapped_fields: dict[str, Any] | None = None,
    imported_by=None,
) -> PlayerSourceRow:
    """Record import provenance for a player source row."""
    return PlayerSourceRow.objects.create(
        player=player,
        source=source,
        source_filename=source_filename,
        row_number=row_number,
        original_row=original_row or {},
        unmapped_fields=unmapped_fields or {},
        imported_by=imported_by,
    )
