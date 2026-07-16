"""Preview construction for player import batches."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from django.db import transaction

from players.models import PlayerImportBatch, PlayerImportStatus
from players.services.imports.constants import (
    ACTION_CREATE,
    ACTION_ERROR,
    ACTION_NEEDS_REVIEW,
    ACTION_UPDATE,
    MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
)
from players.services.imports.mapping import (
    build_identity_payload,
    build_roster_payload,
    build_source_identifiers,
    parsed_to_snapshot,
    snapshot_to_parsed,
    unmapped_fields,
)
from players.services.imports.matching import field_conflicts, match_identity
from players.services.imports.parsing import suggest_mapping
from players.services.imports.result_models import ImportPreviewRow
from players.services.imports.roster import (
    membership_preview as build_membership_preview,
)
from players.services.imports.roster import (
    team_preview,
)
from players.services.matching_service import (
    MATCH_AMBIGUOUS,
    MATCH_EXACT,
    MATCH_HIGH_CONFIDENCE,
    MATCH_NO_MATCH,
)


def json_preview_row(row: ImportPreviewRow) -> dict[str, Any]:
    return asdict(row)


def preview_row(
    *, row: dict[str, Any], mapping_config: dict[str, str], source: str, season=None
) -> ImportPreviewRow:
    """Build preview data for a single CSV row."""
    cleaned_row = row["cleaned_row"]
    identity = build_identity_payload(cleaned_row, mapping_config)
    roster = build_roster_payload(cleaned_row, mapping_config)
    source_identifiers = build_source_identifiers(cleaned_row, mapping_config, source)
    errors = list(roster.get("errors", []))
    if not (identity.get("first_name") and identity.get("last_name")):
        errors.append(
            "Map either a full name column or both first and last name columns."
        )
    if not season:
        errors.append("Select an active season for this import.")
    if not roster.get("team_name"):
        errors.append("Team is required for season-aware player import.")
    if not roster.get("division"):
        errors.append("Division is required for season-aware player import.")
    match_result = match_identity(identity, source_identifiers) if not errors else None
    field_conflict_rows = (
        field_conflicts(getattr(match_result, "player", None), identity)
        if match_result
        else []
    )
    season_team_preview = (
        team_preview(roster, season)
        if season and not (not roster.get("team_name") or not roster.get("division"))
        else {
            "action": "invalid_roster_context",
            "label": "Invalid Roster Context",
        }
    )
    matched_player = getattr(match_result, "player", None) if match_result else None
    membership_preview_data = (
        build_membership_preview(matched_player, season_team_preview, season, roster)
        if season and not errors
        else {
            "action": "invalid_roster_context",
            "label": "Invalid Roster Context",
            "is_primary": False,
        }
    )
    if membership_preview_data.get("action") == "review_team_change":
        errors.append(
            "Player already has an active primary membership in this season. "
            "Resolve the team change manually or skip this row."
        )

    if errors:
        action = ACTION_ERROR
        match_status = MATCH_NO_MATCH
    elif match_result.status == MATCH_EXACT:
        action = ACTION_NEEDS_REVIEW if field_conflict_rows else ACTION_UPDATE
        match_status = match_result.status
    elif match_result.status == MATCH_HIGH_CONFIDENCE:
        action = ACTION_NEEDS_REVIEW if field_conflict_rows else ACTION_UPDATE
        match_status = match_result.status
    elif match_result.status == MATCH_AMBIGUOUS:
        action = ACTION_NEEDS_REVIEW
        match_status = match_result.status
    else:
        action = ACTION_CREATE
        match_status = MATCH_NO_MATCH

    candidates = getattr(match_result, "candidates", []) if match_result else []
    return ImportPreviewRow(
        row_number=row["row_number"],
        identity=identity,
        original_row=row["original_row"],
        unmapped_fields=unmapped_fields(cleaned_row, mapping_config),
        source_identifiers=source_identifiers,
        match_status=match_status,
        matched_player_id=getattr(matched_player, "id", None),
        matched_player_name=getattr(matched_player, "display_name", ""),
        candidate_ids=[candidate.id for candidate in candidates],
        candidate_names=[candidate.display_name for candidate in candidates],
        candidate_options=[
            {"id": candidate.id, "name": candidate.display_name}
            for candidate in candidates
        ],
        field_conflicts=field_conflict_rows,
        errors=errors,
        action=action,
        roster={key: value for key, value in roster.items() if key != "errors"},
        season_team=season_team_preview,
        membership=membership_preview_data,
    )


@transaction.atomic
def build_import_preview(
    *, import_batch: PlayerImportBatch, mapping_config: dict[str, str] | None = None
) -> dict[str, Any]:
    """Build and persist an import preview for a batch."""
    parsed = snapshot_to_parsed(import_batch.preview_snapshot)
    mapping_config = (
        mapping_config
        or import_batch.mapping_config
        or suggest_mapping(parsed.headers, source=import_batch.source)
    )
    rows = [
        json_preview_row(
            preview_row(
                row=row,
                mapping_config=mapping_config,
                source=import_batch.source,
                season=import_batch.season,
            )
        )
        for row in parsed.rows
    ]
    row_errors = [row for row in rows if row["errors"]]
    conflicted_rows = [row for row in rows if row["action"] == ACTION_NEEDS_REVIEW]
    preview = {
        "file_name": parsed.file_name,
        "source": import_batch.source,
        "season": {
            "id": import_batch.season_id,
            "name": (
                import_batch.season.name
                if import_batch.season_id
                else "Legacy / No Season"
            ),
        },
        "headers": parsed.headers,
        "mapping_config": mapping_config,
        "account_provisioning": {
            "enabled": bool(mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS)),
            "activate_users": bool(
                mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS)
            ),
            "email_column": mapping_config.get("account_email", ""),
        },
        "rows": rows,
        "summary": {
            "rows_processed": len(rows),
            "rows_create": sum(1 for row in rows if row["action"] == ACTION_CREATE),
            "rows_update": sum(1 for row in rows if row["action"] == ACTION_UPDATE),
            "rows_needs_review": len(conflicted_rows),
            "rows_error": len(row_errors),
            "season_teams_create": sum(
                1
                for row in rows
                if row.get("season_team", {}).get("action") == "create"
            ),
            "season_teams_reuse": sum(
                1 for row in rows if row.get("season_team", {}).get("action") == "reuse"
            ),
            "memberships_create": sum(
                1
                for row in rows
                if row.get("membership", {}).get("action")
                in {"create", "new_season_membership"}
            ),
            "memberships_update": sum(
                1 for row in rows if row.get("membership", {}).get("action") == "update"
            ),
        },
    }
    import_batch.mapping_config = mapping_config
    import_batch.preview_snapshot = {
        "parsed_csv": parsed_to_snapshot(parsed),
        "preview": preview,
    }
    import_batch.row_errors = row_errors
    import_batch.conflict_summary = {
        "rows_conflicted": len(conflicted_rows),
        "row_numbers": [row["row_number"] for row in conflicted_rows],
    }
    import_batch.rows_processed = len(rows)
    import_batch.rows_conflicted = len(conflicted_rows)
    import_batch.status = (
        PlayerImportStatus.NEEDS_REVIEW
        if conflicted_rows or row_errors
        else PlayerImportStatus.PREVIEWED
    )
    import_batch.save(
        update_fields=[
            "mapping_config",
            "preview_snapshot",
            "row_errors",
            "conflict_summary",
            "rows_processed",
            "rows_conflicted",
            "status",
            "updated_at",
        ]
    )
    return preview


def current_preview(import_batch: PlayerImportBatch) -> dict[str, Any]:
    """Return the current persisted preview for a batch."""
    return import_batch.preview_snapshot.get("preview", {})
