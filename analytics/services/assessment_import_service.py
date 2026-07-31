from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from analytics.models import (
    ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
    ASSESSMENT_IMPORT_ROW_COMMITTED,
    ASSESSMENT_IMPORT_ROW_INVALID,
    ASSESSMENT_IMPORT_ROW_MATCHED,
    ASSESSMENT_IMPORT_ROW_SKIPPED,
    ASSESSMENT_IMPORT_ROW_UNMATCHED,
    ASSESSMENT_IMPORT_STATUS_COMMITTED,
    ASSESSMENT_IMPORT_STATUS_FAILED,
    ASSESSMENT_IMPORT_STATUS_PREVIEWED,
    ASSESSMENT_STATUS_COMMITTED,
    ASSESSMENT_VALUE_SOURCE_IMPORTED,
    ASSESSMENT_VALUE_TYPE_NUMBER,
    ASSESSMENT_VALUE_TYPE_RATING,
    AssessmentImportBatch,
    AssessmentImportRow,
    AssessmentImportTemplate,
    AssessmentMetricDefinition,
    AssessmentScoringProfile,
    AssessmentTemplate,
    AssessmentTemplateMetric,
    AssessmentValue,
    PlayerAssessment,
)
from analytics.services.assessment_matching_service import (
    MATCH_AMBIGUOUS,
    MATCH_UNMATCHED,
    match_player_for_assessment,
    normalize_assessment_name,
)
from players.models import Player

BOOTSTRAP_2026_13U_ASSESSMENT_KEY = "2026-13u-house-assessment"
BOOTSTRAP_2026_13U_IMPORT_KEY = "2026-13u-house-assessment-xlsx"


DEFAULT_2026_13U_DATA_SHEETS = [
    {
        "name": "Assessment Data",
        "header_row": 2,
        "identity_column": "Name",
        "category_row": 1,
        "metrics": [
            {
                "header": "Home to 1st",
                "key": "home_to_1st",
                "category": "Athleticism Evaluation",
                "unit": "seconds",
                "direction": "lower",
            },
            {
                "header": "Broad Jump",
                "key": "broad_jump",
                "category": "Athleticism Evaluation",
                "unit": "inches",
                "direction": "higher",
            },
            {
                "header": "Lateral Jump",
                "key": "lateral_jump",
                "category": "Athleticism Evaluation",
                "unit": "inches",
                "direction": "higher",
            },
            {
                "header": "Shotput",
                "key": "shotput",
                "category": "Athleticism Evaluation",
                "unit": "feet",
                "direction": "higher",
            },
            {
                "header": "Bat Speed",
                "key": "bat_speed",
                "category": "Hitting Objective Evaluation",
                "unit": "mph",
                "direction": "higher",
            },
            {
                "header": "Time 2 Contact",
                "key": "time_to_contact",
                "category": "Hitting Objective Evaluation",
                "unit": "seconds",
                "direction": "lower",
            },
            {
                "header": "Exit Velocity Avg.",
                "key": "exit_velocity_avg",
                "category": "Hitting Objective Evaluation",
                "unit": "mph",
                "direction": "higher",
            },
            {
                "header": "Exit Velocity Max",
                "key": "exit_velocity_max",
                "category": "Hitting Objective Evaluation",
                "unit": "mph",
                "direction": "higher",
            },
            {
                "header": "Athletic Stance",
                "key": "athletic_stance",
                "category": "Hitting Subjective Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Balance Stride",
                "key": "balance_stride",
                "category": "Hitting Subjective Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Barrel Level",
                "key": "barrel_level",
                "category": "Hitting Subjective Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Launch Position",
                "key": "launch_position",
                "category": "Hitting Subjective Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Follow Through",
                "key": "follow_through",
                "category": "Hitting Subjective Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Readiness",
                "key": "fielding_readiness",
                "category": "Fielding and Throwing Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Footwork",
                "key": "fielding_footwork",
                "category": "Fielding and Throwing Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Glovework",
                "key": "fielding_glovework",
                "category": "Fielding and Throwing Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Athleticism",
                "key": "fielding_athleticism",
                "category": "Fielding and Throwing Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Fundamental Throwing",
                "key": "fundamental_throwing",
                "category": "Fielding and Throwing Evaluation",
                "value_type": "rating",
                "direction": "higher",
            },
        ],
    },
    {
        "name": "Pitching Data",
        "header_row": 2,
        "identity_column": "Name",
        "metrics": [
            {
                "header": "Velocity Avg.",
                "key": "pitching_velocity_avg",
                "category": "Pitching Data",
                "unit": "mph",
                "direction": "higher",
            },
            {
                "header": "Velocity Max",
                "key": "pitching_velocity_max",
                "category": "Pitching Data",
                "unit": "mph",
                "direction": "higher",
            },
            {
                "header": "Pitch 1",
                "key": "pitch_1",
                "category": "Pitching Data",
                "value_type": "text",
            },
            {
                "header": "Pitch 2",
                "key": "pitch_2",
                "category": "Pitching Data",
                "value_type": "text",
            },
            {
                "header": "Pitch 3",
                "key": "pitch_3",
                "category": "Pitching Data",
                "value_type": "text",
            },
            {
                "header": "Pitch 4",
                "key": "pitch_4",
                "category": "Pitching Data",
                "value_type": "text",
            },
            {
                "header": "Athletic Movement",
                "key": "pitching_athletic_movement",
                "category": "Pitching Data",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Body Control",
                "key": "pitching_body_control",
                "category": "Pitching Data",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Direction",
                "key": "pitching_direction",
                "category": "Pitching Data",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Repeatability",
                "key": "pitching_repeatability",
                "category": "Pitching Data",
                "value_type": "rating",
                "direction": "higher",
            },
            {
                "header": "Command2",
                "key": "pitching_command",
                "category": "Pitching Data",
                "value_type": "rating",
                "direction": "higher",
            },
        ],
    },
]

DEFAULT_2026_13U_RANKING_SHEETS = ["Ranking", "Pitcher Ranking"]


@dataclass(frozen=True)
class AssessmentPreviewSummary:
    rows: int
    matched: int
    unmatched: int
    ambiguous: int
    invalid: int
    skipped: int
    checksum_seen_before: bool

    @property
    def can_commit(self) -> bool:
        return self.unmatched == 0 and self.ambiguous == 0 and self.invalid == 0


@dataclass(frozen=True)
class AssessmentCommitResult:
    processed: int
    created: int
    updated: int
    skipped: int


def normalize_sheet_name(value: str) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def normalize_header(value: str) -> str:
    return normalize_sheet_name(value).replace(".", "").replace(" ", "_")


def _workbook_bytes(file_obj: BinaryIO) -> bytes:
    position = file_obj.tell() if hasattr(file_obj, "tell") else None
    content = file_obj.read()
    if position is not None and hasattr(file_obj, "seek"):
        file_obj.seek(position)
    return content


def workbook_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _load_workbook_from_bytes(content: bytes):
    return load_workbook(BytesIO(content), read_only=True, data_only=True)


def _worksheet_by_name(workbook, configured_name: str):
    normalized = normalize_sheet_name(configured_name)
    for sheet_name in workbook.sheetnames:
        if normalize_sheet_name(sheet_name) == normalized:
            return workbook[sheet_name]
    return None


def _row_values(row) -> list:
    return [cell for cell in row]


def _header_map(row_values: list) -> dict[str, int]:
    mapping = {}
    for index, value in enumerate(row_values):
        if value not in (None, ""):
            mapping[normalize_header(value)] = index
    return mapping


def _decimal_or_none(value) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


def _snapshot_value(
    metric_config: dict,
    raw_value,
    *,
    sheet_name: str,
    row_number: int,
    column_index: int,
) -> dict | None:
    if raw_value in (None, ""):
        return None
    value_type = metric_config.get("value_type") or ASSESSMENT_VALUE_TYPE_NUMBER
    raw_text = str(raw_value).strip()
    snapshot = {
        "metric_key": metric_config["key"],
        "header": metric_config["header"],
        "value_type": value_type,
        "unit": metric_config.get("unit", ""),
        "raw_value": raw_text,
        "source_sheet": sheet_name,
        "source_row": row_number,
        "source_column": get_column_letter(column_index + 1),
    }
    if value_type in {ASSESSMENT_VALUE_TYPE_NUMBER, ASSESSMENT_VALUE_TYPE_RATING}:
        decimal_value = _decimal_or_none(raw_value)
        if decimal_value is None:
            snapshot["error"] = f"{metric_config['header']} is not numeric."
        else:
            snapshot["numeric_value"] = str(decimal_value)
    else:
        snapshot["text_value"] = raw_text
    return snapshot


def parse_assessment_workbook(
    content: bytes, import_template: AssessmentImportTemplate
) -> dict:
    """Parse configured workbook sheets into sanitized row/value snapshots."""
    workbook = _load_workbook_from_bytes(content)
    config = import_template.config
    parsed_rows: dict[str, dict] = {}
    workbook_errors = []
    for sheet_config in config.get("sheets", []):
        worksheet = _worksheet_by_name(workbook, sheet_config["name"])
        if worksheet is None:
            if sheet_config.get("required", True):
                workbook_errors.append(f"Missing worksheet: {sheet_config['name']}.")
            continue
        rows = list(worksheet.iter_rows(values_only=True))
        header_index = int(sheet_config.get("header_row", 1)) - 1
        if header_index >= len(rows):
            workbook_errors.append(
                f"Missing header row for worksheet: {worksheet.title}."
            )
            continue
        headers = _header_map(_row_values(rows[header_index]))
        identity_key = normalize_header(sheet_config.get("identity_column", "Name"))
        identity_index = headers.get(identity_key)
        if identity_index is None:
            workbook_errors.append(
                f"Missing identity column in worksheet: {worksheet.title}."
            )
            continue
        metric_indexes = []
        for metric_config in sheet_config.get("metrics", []):
            metric_index = headers.get(normalize_header(metric_config["header"]))
            if metric_index is not None:
                metric_indexes.append((metric_config, metric_index))
        for zero_based_index, row in enumerate(
            rows[header_index + 1 :], start=header_index + 2
        ):
            row_values = _row_values(row)
            raw_name = (
                row_values[identity_index] if identity_index < len(row_values) else ""
            )
            if raw_name in (None, ""):
                continue
            row_key = (
                slugify(normalize_assessment_name(raw_name))
                or f"row-{zero_based_index}"
            )
            parsed_row = parsed_rows.setdefault(
                row_key,
                {
                    "row_key": row_key,
                    "raw_identity": str(raw_name).strip(),
                    "source_rows": [],
                    "values": [],
                    "errors": [],
                },
            )
            parsed_row["source_rows"].append(
                {"sheet": worksheet.title, "row": zero_based_index}
            )
            raw_row = {}
            for metric_config, metric_index in metric_indexes:
                value = (
                    row_values[metric_index] if metric_index < len(row_values) else None
                )
                raw_row[metric_config["header"]] = "" if value is None else str(value)
                snapshot = _snapshot_value(
                    metric_config,
                    value,
                    sheet_name=worksheet.title,
                    row_number=zero_based_index,
                    column_index=metric_index,
                )
                if snapshot is None:
                    continue
                if snapshot.get("error"):
                    parsed_row["errors"].append(snapshot["error"])
                parsed_row["values"].append(snapshot)
            parsed_row.setdefault("raw_rows", []).append(
                {"sheet": worksheet.title, "row": zero_based_index, "values": raw_row}
            )
    return {
        "rows": list(parsed_rows.values()),
        "errors": workbook_errors,
        "ranking_sheets": config.get("ranking_sheets", []),
    }


def _preview_summary(batch: AssessmentImportBatch) -> AssessmentPreviewSummary:
    rows = list(batch.rows.all())
    return AssessmentPreviewSummary(
        rows=len(rows),
        matched=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_MATCHED),
        unmatched=sum(
            1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_UNMATCHED
        ),
        ambiguous=sum(
            1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_AMBIGUOUS
        ),
        invalid=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_INVALID),
        skipped=sum(1 for row in rows if row.status == ASSESSMENT_IMPORT_ROW_SKIPPED),
        checksum_seen_before=bool(batch.preview_snapshot.get("checksum_seen_before")),
    )


def summarize_import_batch(batch: AssessmentImportBatch) -> AssessmentPreviewSummary:
    """Return a read model summary for an assessment import batch."""
    return _preview_summary(batch)


@transaction.atomic
def create_assessment_import_batch(
    *, file_obj, event, import_template, uploaded_by
) -> AssessmentImportBatch:
    """Create a persisted preview batch without committing assessment values."""
    filename = Path(file_obj.name).name
    if not filename.lower().endswith(".xlsx"):
        raise ValidationError("Upload an .xlsx workbook.")
    content = _workbook_bytes(file_obj)
    checksum = workbook_sha256(content)
    checksum_seen_before = AssessmentImportBatch.objects.filter(
        event=event,
        workbook_sha256=checksum,
        status=ASSESSMENT_IMPORT_STATUS_COMMITTED,
    ).exists()
    batch = AssessmentImportBatch.objects.create(
        event=event,
        import_template=import_template,
        uploaded_by=uploaded_by,
        original_filename=filename,
        workbook_sha256=checksum,
        config_snapshot=json.loads(json.dumps(import_template.config)),
        preview_snapshot={"checksum_seen_before": checksum_seen_before},
    )
    try:
        parsed = parse_assessment_workbook(content, import_template)
        build_assessment_import_preview(batch=batch, parsed=parsed)
    except Exception as exc:
        batch.status = ASSESSMENT_IMPORT_STATUS_FAILED
        batch.import_summary = {"errors": [str(exc)]}
        batch.save(update_fields=["status", "import_summary", "updated_at"])
        raise
    return batch


def _row_status_for_match(match, row_errors: list[str]) -> str:
    if row_errors:
        return ASSESSMENT_IMPORT_ROW_INVALID
    if match.status == MATCH_AMBIGUOUS:
        return ASSESSMENT_IMPORT_ROW_AMBIGUOUS
    if match.status == MATCH_UNMATCHED:
        return ASSESSMENT_IMPORT_ROW_UNMATCHED
    if match.player:
        return ASSESSMENT_IMPORT_ROW_MATCHED
    return ASSESSMENT_IMPORT_ROW_UNMATCHED


@transaction.atomic
def build_assessment_import_preview(
    *, batch: AssessmentImportBatch, parsed: dict
) -> AssessmentPreviewSummary:
    """Refresh import preview rows and conservative player matches."""
    if batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
        raise ValidationError("Committed assessment imports cannot be previewed again.")
    batch.rows.all().delete()
    workbook_errors = parsed.get("errors", [])
    for parsed_row in parsed.get("rows", []):
        match = match_player_for_assessment(
            raw_name=parsed_row["raw_identity"],
            event=batch.event,
        )
        errors = list(parsed_row.get("errors", []))
        if workbook_errors:
            errors.extend(workbook_errors)
        status = _row_status_for_match(match, errors)
        action = "skip"
        if status == ASSESSMENT_IMPORT_ROW_MATCHED:
            action = "create_or_update"
        elif status in {
            ASSESSMENT_IMPORT_ROW_AMBIGUOUS,
            ASSESSMENT_IMPORT_ROW_UNMATCHED,
        }:
            action = "needs_review"
        AssessmentImportRow.objects.create(
            batch=batch,
            row_key=parsed_row["row_key"],
            source_sheet=(parsed_row.get("source_rows") or [{}])[0].get("sheet", ""),
            source_row=(parsed_row.get("source_rows") or [{}])[0].get("row", 0) or 0,
            raw_identity=parsed_row["raw_identity"],
            player=match.player,
            roster_membership=match.roster_membership,
            action=action,
            status=status,
            errors=errors,
            values_snapshot=parsed_row.get("values", []),
            raw_row={
                "source_rows": parsed_row.get("source_rows", []),
                "raw_rows": parsed_row.get("raw_rows", []),
            },
            metadata={
                "match_reason": match.reason,
                "candidate_ids": [candidate.pk for candidate in match.candidates],
            },
        )
    batch.status = ASSESSMENT_IMPORT_STATUS_PREVIEWED
    summary = _preview_summary(batch)
    batch.preview_snapshot = {
        "checksum_seen_before": batch.preview_snapshot.get(
            "checksum_seen_before", False
        ),
        "ranking_sheets": parsed.get("ranking_sheets", []),
        "summary": summary.__dict__,
    }
    batch.import_summary = summary.__dict__
    batch.save(
        update_fields=["status", "preview_snapshot", "import_summary", "updated_at"]
    )
    return summary


@transaction.atomic
def resolve_assessment_import_row(
    *, row: AssessmentImportRow, player: Player | None, skip: bool = False
):
    """Resolve an unmatched/ambiguous preview row before commit."""
    if row.batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
        raise ValidationError("Committed assessment import rows cannot be changed.")
    if skip:
        row.player = None
        row.roster_membership = None
        row.status = ASSESSMENT_IMPORT_ROW_SKIPPED
        row.action = "skip"
    elif player is None:
        raise ValidationError("Choose a player or skip the row.")
    else:
        row.player = player
        row.roster_membership = (
            player.roster_memberships.select_related("season_team")
            .filter(season_team__season=row.batch.event.season, is_active=True)
            .order_by("-is_primary", "id")
            .first()
        )
        row.status = ASSESSMENT_IMPORT_ROW_MATCHED
        row.action = "create_or_update"
    row.save(
        update_fields=["player", "roster_membership", "status", "action", "updated_at"]
    )
    summary = _preview_summary(row.batch)
    row.batch.import_summary = summary.__dict__
    row.batch.save(update_fields=["import_summary", "updated_at"])
    return row


def _metric_by_key(event) -> dict[str, AssessmentTemplateMetric]:
    return {
        template_metric.metric.key: template_metric
        for template_metric in event.template.template_metrics.select_related("metric")
    }


def _apply_snapshot_value(
    *,
    player_assessment: PlayerAssessment,
    template_metric: AssessmentTemplateMetric,
    import_row: AssessmentImportRow,
    snapshot: dict,
):
    existing = AssessmentValue.objects.filter(
        player_assessment=player_assessment,
        template_metric=template_metric,
    ).first()
    if existing and existing.is_manual_override:
        raise ValidationError(
            f"Manual override exists for {player_assessment.player} / {template_metric.display_name}."
        )
    defaults = {
        "raw_value": snapshot.get("raw_value", ""),
        "normalized_value": snapshot.get("numeric_value")
        or snapshot.get("text_value", ""),
        "unit": snapshot.get("unit", ""),
        "source_sheet": snapshot.get("source_sheet", ""),
        "source_row": snapshot.get("source_row"),
        "source_column": snapshot.get("source_column", ""),
        "source_header": snapshot.get("header", ""),
        "source_kind": ASSESSMENT_VALUE_SOURCE_IMPORTED,
        "is_imported": True,
        "import_row": import_row,
    }
    value_type = snapshot.get("value_type")
    if value_type == ASSESSMENT_VALUE_TYPE_RATING:
        defaults["rating_value"] = Decimal(snapshot["numeric_value"])
        defaults["rating_scale_min"] = template_metric.rating_scale_min
        defaults["rating_scale_max"] = template_metric.rating_scale_max
    elif value_type == ASSESSMENT_VALUE_TYPE_NUMBER:
        defaults["numeric_value"] = Decimal(snapshot["numeric_value"])
    else:
        defaults["text_value"] = snapshot.get(
            "text_value", snapshot.get("raw_value", "")
        )
    AssessmentValue.objects.update_or_create(
        player_assessment=player_assessment,
        template_metric=template_metric,
        defaults=defaults,
    )


@transaction.atomic
def commit_assessment_import_batch(
    *, batch: AssessmentImportBatch, actor
) -> AssessmentCommitResult:
    """Commit a fully resolved preview batch into PlayerAssessment records."""
    if not actor.is_staff and not actor.is_superuser:
        raise PermissionDenied("Only staff can commit assessment imports.")
    batch = AssessmentImportBatch.objects.select_for_update().get(pk=batch.pk)
    if batch.status == ASSESSMENT_IMPORT_STATUS_COMMITTED:
        raise ValidationError("This assessment import has already been committed.")
    unresolved = batch.rows.exclude(
        status__in=[ASSESSMENT_IMPORT_ROW_MATCHED, ASSESSMENT_IMPORT_ROW_SKIPPED]
    )
    if unresolved.exists():
        raise ValidationError(
            "Resolve or skip all unmatched, ambiguous, or invalid rows before committing."
        )
    metrics = _metric_by_key(batch.event)
    created = 0
    updated = 0
    skipped = 0
    for row in batch.rows.select_related("player", "roster_membership"):
        if row.status == ASSESSMENT_IMPORT_ROW_SKIPPED:
            skipped += 1
            continue
        if not row.player_id:
            raise ValidationError("Resolved assessment import rows require a player.")
        player_assessment, was_created = PlayerAssessment.objects.get_or_create(
            player=row.player,
            event=batch.event,
            defaults={
                "roster_membership": row.roster_membership,
                "import_batch": batch,
                "source_row_key": row.row_key,
                "status": ASSESSMENT_STATUS_COMMITTED,
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1
            player_assessment.roster_membership = (
                row.roster_membership or player_assessment.roster_membership
            )
            player_assessment.import_batch = batch
            player_assessment.source_row_key = row.row_key
            player_assessment.status = ASSESSMENT_STATUS_COMMITTED
            player_assessment.save()
        for snapshot in row.values_snapshot:
            template_metric = metrics.get(snapshot.get("metric_key"))
            if template_metric is None:
                raise ValidationError(
                    f"Unknown assessment metric: {snapshot.get('metric_key')}."
                )
            _apply_snapshot_value(
                player_assessment=player_assessment,
                template_metric=template_metric,
                import_row=row,
                snapshot=snapshot,
            )
        row.status = ASSESSMENT_IMPORT_ROW_COMMITTED
        row.save(update_fields=["status", "updated_at"])
    batch.status = ASSESSMENT_IMPORT_STATUS_COMMITTED
    batch.committed_at = timezone.now()
    result = AssessmentCommitResult(
        processed=created + updated + skipped,
        created=created,
        updated=updated,
        skipped=skipped,
    )
    batch.import_summary = result.__dict__
    batch.save(update_fields=["status", "committed_at", "import_summary", "updated_at"])
    batch.event.template.is_locked = True
    batch.event.template.save(update_fields=["is_locked", "updated_at"])
    batch.import_template.is_locked = True
    batch.import_template.save(update_fields=["is_locked", "updated_at"])
    if batch.event.scoring_profile_id:
        batch.event.scoring_profile.is_locked = True
        batch.event.scoring_profile.save(update_fields=["is_locked", "updated_at"])
    return result


def default_2026_13u_config() -> dict:
    """Return configuration derived from the supplied 2026 13U workbook headers."""
    return {
        "sheets": DEFAULT_2026_13U_DATA_SHEETS,
        "ranking_sheets": DEFAULT_2026_13U_RANKING_SHEETS,
        "notes": "Ranking sheets are provenance/QA only and are not imported as player metrics.",
    }


@transaction.atomic
def ensure_2026_13u_assessment_configuration(*, dry_run: bool = False) -> dict:
    """Create idempotent assessment/import templates for the 2026 13U workbook."""
    config = default_2026_13u_config()
    plan = {
        "metrics": [],
        "template": BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
        "import_template": BOOTSTRAP_2026_13U_IMPORT_KEY,
    }
    if dry_run:
        for sheet_config in config["sheets"]:
            for metric_config in sheet_config["metrics"]:
                plan["metrics"].append(metric_config["key"])
        return plan
    template, _ = AssessmentTemplate.objects.get_or_create(
        key=BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
        version=1,
        defaults={"name": "2026 VCB House 13U PeeWee Assessment"},
    )
    AssessmentScoringProfile.objects.get_or_create(
        key=BOOTSTRAP_2026_13U_ASSESSMENT_KEY,
        version=1,
        defaults={
            "name": "2026 VCB House 13U PeeWee Assessment Scoring",
            "config": {"source": "spreadsheet-derived", "computed_scores": []},
        },
    )
    AssessmentImportTemplate.objects.get_or_create(
        key=BOOTSTRAP_2026_13U_IMPORT_KEY,
        version=1,
        defaults={
            "name": "2026 VCB House 13U PeeWee Assessment Workbook",
            "config": config,
        },
    )
    display_order = 0
    for sheet_config in config["sheets"]:
        for metric_config in sheet_config["metrics"]:
            display_order += 10
            value_type = metric_config.get("value_type") or ASSESSMENT_VALUE_TYPE_NUMBER
            metric, _ = AssessmentMetricDefinition.objects.get_or_create(
                key=metric_config["key"],
                defaults={
                    "name": metric_config["header"].strip(),
                    "default_value_type": value_type,
                    "default_unit": metric_config.get("unit", ""),
                },
            )
            AssessmentTemplateMetric.objects.get_or_create(
                template=template,
                metric=metric,
                defaults={
                    "category": metric_config.get("category", sheet_config["name"]),
                    "display_name": metric_config["header"].strip(),
                    "display_order": display_order,
                    "value_type": value_type,
                    "unit": metric_config.get("unit", ""),
                    "direction": metric_config.get("direction", "neutral"),
                    "rating_scale_min": (
                        Decimal("1")
                        if value_type == ASSESSMENT_VALUE_TYPE_RATING
                        else None
                    ),
                    "rating_scale_max": (
                        Decimal("5")
                        if value_type == ASSESSMENT_VALUE_TYPE_RATING
                        else None
                    ),
                    "metadata": {"source_sheet": sheet_config["name"]},
                },
            )
            plan["metrics"].append(metric_config["key"])
    return plan


def assessment_records_for_player(player: Player):
    """Return staff-visible workbook assessment records for a player profile."""
    return (
        PlayerAssessment.objects.filter(player=player)
        .select_related("event", "event__season")
        .prefetch_related("values__template_metric")
        .order_by("-event__starts_on", "-created_at")
    )
