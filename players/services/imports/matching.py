"""Player matching adapter used by the import preview."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from players.models import Player
from players.services.imports.constants import CONFLICT_FIELDS
from players.services.imports.mapping import date_to_string, identity_for_model
from players.services.imports.result_models import FieldConflict
from players.services.matching_service import (
    MATCH_AMBIGUOUS,
    MATCH_EXACT,
    PlayerMatchResult,
    find_player_match,
    match_by_identifier,
)


def match_identity(identity: dict[str, Any], source_identifiers: list[dict[str, str]]):
    model_identity = identity_for_model(identity)
    match_data = {
        "first_name": model_identity.get("first_name", ""),
        "last_name": model_identity.get("last_name", ""),
        "birthdate": model_identity.get("birthdate"),
        "birth_year": model_identity.get("birth_year"),
        "division": identity.get("division", ""),
    }
    if source_identifiers:
        exact_matches = []
        exact_score = None
        seen_player_ids = set()
        for identifier in source_identifiers:
            identifier_result = match_by_identifier(
                identifier.get("source", ""),
                identifier.get("identifier_type", ""),
                identifier.get("identifier_value", ""),
            )
            if identifier_result.status == MATCH_EXACT and identifier_result.player:
                if identifier_result.player.id not in seen_player_ids:
                    exact_matches.append(identifier_result.player)
                    exact_score = identifier_result.score
                    seen_player_ids.add(identifier_result.player.id)
        if len(exact_matches) == 1:
            return PlayerMatchResult(
                status=MATCH_EXACT,
                player=exact_matches[0],
                candidates=exact_matches,
                reason="Matched by source identifier.",
                score=exact_score,
            )
        if len(exact_matches) > 1:
            return PlayerMatchResult(
                status=MATCH_AMBIGUOUS,
                candidates=exact_matches,
                reason="Multiple source identifiers matched different players.",
            )
    return find_player_match(match_data)


def field_conflicts(
    player: Player | None, identity: dict[str, Any]
) -> list[dict[str, str]]:
    if not player:
        return []
    model_identity = identity_for_model(identity)
    conflicts = []
    for field_name in CONFLICT_FIELDS:
        imported = model_identity.get(field_name)
        existing = getattr(player, field_name, None)
        if existing in {"", None} or imported in {"", None}:
            continue
        existing_value = date_to_string(existing)
        imported_value = date_to_string(imported)
        if existing_value != imported_value:
            conflicts.append(
                asdict(
                    FieldConflict(
                        field_name=field_name,
                        existing_value=existing_value,
                        imported_value=imported_value,
                    )
                )
            )
    return conflicts
