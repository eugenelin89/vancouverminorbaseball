"""Commit orchestration for player import batches."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from players.models import (
    Player,
    PlayerImportBatch,
    PlayerImportStatus,
    PlayerSourceIdentifier,
    PlayerSourceRow,
)
from players.services.imports.constants import (
    ACTION_ERROR,
    ACTION_NEEDS_REVIEW,
    ACTION_SKIP,
    MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS,
    MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS,
    RESOLUTION_ACTION_COMMIT,
    RESOLUTION_ACTION_CREATE_NEW,
    RESOLUTION_ACTION_USE_CANDIDATE,
    RESOLUTION_USE_IMPORTED,
)
from players.services.imports.mapping import (
    identity_for_model,
    parsed_to_snapshot,
)
from players.services.imports.parsing import (
    detect_source_from_filename,
    normalize_header,
    normalize_source,
    parse_player_csv,
    suggest_mapping,
)
from players.services.imports.preview import build_import_preview, current_preview
from players.services.imports.result_models import ImportCommitResult
from players.services.imports.roster import commit_membership
from players.services.matching_service import MATCH_AMBIGUOUS


def ensure_staff(actor):
    if (
        not actor
        or not actor.is_authenticated
        or not (actor.is_staff or actor.is_superuser)
    ):
        raise PermissionDenied("Only staff/admin users can run player imports.")


@transaction.atomic
def create_import_batch(
    *,
    file_obj,
    source: str,
    uploaded_by,
    season=None,
    provision_player_accounts: bool = False,
    activate_player_accounts: bool = True,
) -> PlayerImportBatch:
    """Create a persisted player import batch from a CSV upload."""
    ensure_staff(uploaded_by)
    if season is None:
        raise ValidationError("Select an active season for this player import.")
    if not getattr(season, "is_active", False):
        raise ValidationError("Select an active season for this player import.")
    parsed = parse_player_csv(file_obj)
    normalized_source = normalize_source(
        source or detect_source_from_filename(parsed.file_name)
    )
    mapping_config = suggest_mapping(parsed.headers, source=normalized_source)
    mapping_config[MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS] = bool(
        provision_player_accounts
    )
    mapping_config[MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS] = bool(
        provision_player_accounts
    ) and bool(activate_player_accounts)
    batch = PlayerImportBatch.objects.create(
        source=normalized_source,
        original_filename=parsed.file_name,
        uploaded_by=uploaded_by,
        season=season,
        status=PlayerImportStatus.UPLOADED,
        mapping_config=mapping_config,
        preview_snapshot={"parsed_csv": parsed_to_snapshot(parsed)},
        rows_processed=len(parsed.rows),
    )
    build_import_preview(import_batch=batch, mapping_config=mapping_config)
    return batch


def create_player_from_import(identity: dict[str, Any]) -> Player:
    """Create a canonical player from import identity fields."""
    return Player.objects.create(**identity_for_model(identity))


def apply_player_updates(
    player: Player,
    identity: dict[str, Any],
    field_resolutions: dict[str, str] | None = None,
) -> Player:
    """Fill blank player fields and apply explicit conflict resolutions."""
    field_resolutions = field_resolutions or {}
    model_identity = identity_for_model(identity)
    changed_fields = []
    for field_name, imported_value in model_identity.items():
        existing_value = getattr(player, field_name)
        should_update = (
            existing_value in {"", None}
            or field_resolutions.get(field_name) == RESOLUTION_USE_IMPORTED
        )
        if (
            should_update
            and imported_value not in {"", None}
            and existing_value != imported_value
        ):
            setattr(player, field_name, imported_value)
            changed_fields.append(field_name)
    if changed_fields:
        changed_fields.append("updated_at")
        player.save(update_fields=changed_fields)
    return player


def attach_source_identifiers(
    player: Player,
    identifiers: list[dict[str, str]],
    metadata: dict[str, Any] | None = None,
):
    """Attach source identifiers, reporting duplicate ownership conflicts as errors."""
    errors = []
    for identifier in identifiers:
        source = normalize_source(identifier["source"])
        identifier_type = normalize_header(identifier["identifier_type"]).replace(
            " ", "_"
        )
        identifier_value = normalize_header(identifier["identifier_value"])
        existing = (
            PlayerSourceIdentifier.objects.filter(
                source=source,
                identifier_type=identifier_type,
                identifier_value=identifier_value,
            )
            .select_related("player")
            .first()
        )
        if existing:
            if existing.player_id != player.id:
                errors.append(
                    f"Identifier {source}:{identifier_type}:{identifier_value} "
                    f"already belongs to {existing.player.display_name}."
                )
            continue
        try:
            PlayerSourceIdentifier.objects.create(
                player=player,
                source=source,
                identifier_type=identifier_type,
                identifier_value=identifier_value,
                metadata=metadata or {},
            )
        except IntegrityError:
            errors.append(
                f"Identifier {source}:{identifier_type}:{identifier_value} could not be attached."
            )
    return errors


def record_import_source_row(
    player: Player, import_batch: PlayerImportBatch, preview: dict[str, Any], actor
) -> PlayerSourceRow:
    """Record row-level provenance for a committed player import row."""
    return PlayerSourceRow.objects.create(
        player=player,
        import_batch=import_batch,
        source=import_batch.source,
        source_filename=import_batch.original_filename,
        row_number=preview["row_number"],
        original_row=preview["original_row"],
        unmapped_fields=preview["unmapped_fields"],
        imported_by=actor,
    )


def resolutions_for_row(
    resolutions: dict[str, Any], row_number: int
) -> tuple[str, dict[str, str]]:
    row_key = str(row_number)
    row_resolution = resolutions.get(row_key, {}) if resolutions else {}
    return row_resolution.get("action", RESOLUTION_ACTION_COMMIT), row_resolution.get(
        "fields", {}
    )


def candidate_id_for_row(resolutions: dict[str, Any], row_number: int) -> int | None:
    row_key = str(row_number)
    row_resolution = resolutions.get(row_key, {}) if resolutions else {}
    candidate_id = row_resolution.get("candidate_id")
    if not candidate_id:
        return None
    try:
        return int(candidate_id)
    except (TypeError, ValueError):
        return None


def unresolved_review_messages(
    preview: dict[str, Any], resolutions: dict[str, Any]
) -> list[str]:
    messages = []
    for preview_row_data in preview.get("rows", []):
        row_number = preview_row_data["row_number"]
        row_action, field_resolutions = resolutions_for_row(resolutions, row_number)
        if row_action == ACTION_SKIP:
            continue
        if preview_row_data["action"] == ACTION_ERROR:
            messages.append(
                f"Row {row_number}: fix mapping/data errors or explicitly skip the row."
            )
            continue
        if preview_row_data["match_status"] == MATCH_AMBIGUOUS:
            candidate_id = candidate_id_for_row(resolutions, row_number)
            if row_action == RESOLUTION_ACTION_CREATE_NEW:
                continue
            if (
                row_action == RESOLUTION_ACTION_USE_CANDIDATE
                and candidate_id in preview_row_data.get("candidate_ids", [])
            ):
                continue
            messages.append(
                f"Row {row_number}: choose an existing candidate, create a new player, "
                "or skip the row."
            )
            continue
        if preview_row_data["action"] == ACTION_NEEDS_REVIEW:
            conflict_fields = {
                conflict["field_name"]
                for conflict in preview_row_data.get("field_conflicts", [])
            }
            resolved_fields = set(field_resolutions)
            if conflict_fields and conflict_fields.issubset(resolved_fields):
                continue
            messages.append(
                f"Row {row_number}: resolve all field conflicts or explicitly skip the row."
            )
    return messages


@transaction.atomic
def commit_import_batch(
    *,
    import_batch: PlayerImportBatch,
    actor,
    resolutions: dict[str, Any] | None = None,
) -> ImportCommitResult:
    """Commit a previewed import batch to canonical player records."""
    ensure_staff(actor)
    resolutions = resolutions or {}
    locked_batch = PlayerImportBatch.objects.select_for_update().get(pk=import_batch.pk)
    if locked_batch.status == PlayerImportStatus.COMMITTED:
        raise ValidationError("This import batch has already been committed.")
    if not locked_batch.season_id:
        raise ValidationError(
            "Select an active season before committing this player import."
        )

    preview = current_preview(locked_batch)
    if not preview:
        preview = build_import_preview(import_batch=locked_batch)

    unresolved_messages = unresolved_review_messages(preview, resolutions)
    if unresolved_messages:
        locked_batch.status = PlayerImportStatus.NEEDS_REVIEW
        locked_batch.row_errors = unresolved_messages
        locked_batch.save(update_fields=["status", "row_errors", "updated_at"])
        raise ValidationError(
            "Resolve or explicitly skip review rows before committing this import."
        )

    result = ImportCommitResult(rows_processed=len(preview.get("rows", [])))
    committed_rows = []
    for preview_row_data in preview.get("rows", []):
        row_number = preview_row_data["row_number"]
        row_action, field_resolutions = resolutions_for_row(resolutions, row_number)
        if row_action == ACTION_SKIP:
            result.skipped += 1
            continue
        if preview_row_data["action"] == ACTION_ERROR:
            result.skipped += 1
            result.errors.append(
                f"Row {row_number}: {'; '.join(preview_row_data['errors'])}"
            )
            continue

        player = None
        if preview_row_data["match_status"] == MATCH_AMBIGUOUS:
            if row_action == RESOLUTION_ACTION_CREATE_NEW:
                player = create_player_from_import(preview_row_data["identity"])
                result.created += 1
            else:
                candidate_id = candidate_id_for_row(resolutions, row_number)
                player = Player.objects.select_for_update().get(pk=candidate_id)
                apply_player_updates(player, preview_row_data["identity"])
                result.updated += 1
        elif preview_row_data["matched_player_id"]:
            player = Player.objects.select_for_update().get(
                pk=preview_row_data["matched_player_id"]
            )
            apply_player_updates(
                player,
                preview_row_data["identity"],
                field_resolutions=field_resolutions,
            )
            result.updated += 1
        else:
            player = create_player_from_import(preview_row_data["identity"])
            result.created += 1

        identifier_errors = attach_source_identifiers(
            player,
            preview_row_data.get("source_identifiers", []),
            metadata={"import_batch_id": locked_batch.id, "row_number": row_number},
        )
        result.errors.extend(
            [f"Row {row_number}: {error}" for error in identifier_errors]
        )
        record_import_source_row(player, locked_batch, preview_row_data, actor)
        membership_action, team_created = commit_membership(
            player, locked_batch, preview_row_data
        )
        if team_created:
            result.season_teams_created += 1
        else:
            result.season_teams_reused += 1
        if membership_action == "created":
            result.memberships_created += 1
        else:
            result.memberships_updated += 1
        committed_rows.append(
            {
                "player": player,
                "row_number": row_number,
                "original_row": preview_row_data.get("original_row", {}),
            }
        )

    if locked_batch.mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS):
        from accounts.services.provisioning_service import (
            ProvisioningOptions,
            provision_accounts_for_import,
        )

        provisioning_summary = provision_accounts_for_import(
            locked_batch,
            committed_rows,
            actor=actor,
            options=ProvisioningOptions(
                enabled=True,
                activate_users=True,
                email_column=locked_batch.mapping_config.get("account_email", ""),
            ),
        )
        result.account_provisioning = provisioning_summary.to_dict()
        result.warnings.extend(provisioning_summary.warnings)

    locked_batch.status = PlayerImportStatus.COMMITTED
    locked_batch.rows_created = result.created
    locked_batch.rows_updated = result.updated
    locked_batch.rows_skipped = result.skipped
    locked_batch.rows_conflicted = result.conflicts
    locked_batch.import_summary = asdict(result)
    locked_batch.row_errors = result.errors
    locked_batch.committed_at = timezone.now()
    locked_batch.save(
        update_fields=[
            "status",
            "rows_created",
            "rows_updated",
            "rows_skipped",
            "rows_conflicted",
            "import_summary",
            "row_errors",
            "committed_at",
            "updated_at",
        ]
    )
    return result
