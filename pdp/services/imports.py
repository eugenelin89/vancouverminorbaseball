import csv
import io
import json
import re
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from pdp.models import (
    EvaluationEvent,
    EvaluationEventType,
    EvaluationImport,
    ImportStatus,
    MetricType,
    PlayerEvaluation,
    PlayerMetric,
    PlayerProfile,
    Season,
)
from pdp.services.accounts import provision_player_account


EXCEL_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


@dataclass
class WorkbookSheet:
    name: str
    headers: list[str]
    rows: list[dict]


def _clean_value(value):
    return "" if value is None else str(value).strip()


def _normalize_header(value: str) -> str:
    return " ".join(_clean_value(value).lower().split())


def _split_name(full_name: str):
    parts = [part for part in full_name.split() if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _parse_decimal(value):
    cleaned = _clean_value(value).replace(",", "")
    if cleaned == "":
        return None
    cleaned = re.sub(r"[^\d.\-]", "", cleaned)
    if cleaned in {"", "-", ".", "-."}:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _column_index_from_ref(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    value = 0
    for char in letters:
        value = (value * 26) + ord(char.upper()) - 64
    return max(value - 1, 0)


def _xlsx_shared_strings(archive: zipfile.ZipFile):
    try:
        data = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ElementTree.fromstring(data)
    strings = []
    for node in root.findall("main:si", EXCEL_NS):
        strings.append("".join(text or "" for text in node.itertext()))
    return strings


def _xlsx_sheet_map(archive: zipfile.ZipFile):
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    rels = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall("pkgrel:Relationship", EXCEL_NS)
    }
    sheets = []
    for sheet in workbook.findall("main:sheets/main:sheet", EXCEL_NS):
        target = rel_targets.get(sheet.attrib.get(f"{{{EXCEL_NS['rel']}}}id"))
        if not target:
            continue
        normalized_target = target if target.startswith("worksheets/") else target.replace("../", "")
        sheets.append((sheet.attrib["name"], f"xl/{normalized_target}"))
    return sheets


def _parse_xlsx_sheet(archive: zipfile.ZipFile, path: str, shared_strings: list[str]) -> WorkbookSheet:
    root = ElementTree.fromstring(archive.read(path))
    rows = []
    max_columns = 0
    for row in root.findall(".//main:sheetData/main:row", EXCEL_NS):
        values = []
        for cell in row.findall("main:c", EXCEL_NS):
            index = _column_index_from_ref(cell.attrib.get("r", "A1"))
            while len(values) <= index:
                values.append("")
            cell_type = cell.attrib.get("t")
            value_node = cell.find("main:v", EXCEL_NS)
            inline_node = cell.find("main:is", EXCEL_NS)
            value = ""
            if inline_node is not None:
                value = "".join(inline_node.itertext())
            elif value_node is not None:
                value = value_node.text or ""
                if cell_type == "s":
                    try:
                        value = shared_strings[int(value)]
                    except (IndexError, ValueError):
                        pass
            values[index] = _clean_value(value)
        if any(values):
            rows.append(values)
            max_columns = max(max_columns, len(values))

    if not rows:
        return WorkbookSheet(name=path.rsplit("/", 1)[-1], headers=[], rows=[])

    headers = [
        _clean_value(rows[0][index]) if index < len(rows[0]) else f"Column {index + 1}"
        for index in range(max_columns)
    ]
    normalized_headers = []
    for index, header in enumerate(headers, start=1):
        normalized_headers.append(header or f"Column {index}")
    data_rows = []
    for values in rows[1:]:
        row = {}
        for index, header in enumerate(normalized_headers):
            row[header] = values[index] if index < len(values) else ""
        data_rows.append(row)
    return WorkbookSheet(name=path.rsplit("/", 1)[-1], headers=normalized_headers, rows=data_rows)


def _parse_csv_workbook(file_obj) -> list[WorkbookSheet]:
    raw_data = file_obj.read()
    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode("utf-8-sig")
    file_obj.seek(0)
    reader = csv.DictReader(io.StringIO(raw_data))
    if not reader.fieldnames:
        raise ValidationError("The uploaded file does not contain a header row.")
    headers = [_clean_value(header) for header in reader.fieldnames]
    rows = []
    for row in reader:
        rows.append({header: _clean_value(row.get(header)) for header in reader.fieldnames})
    return [WorkbookSheet(name="Sheet1", headers=headers, rows=rows)]


def _parse_xlsx_workbook(file_obj) -> list[WorkbookSheet]:
    workbook_bytes = file_obj.read()
    file_obj.seek(0)
    archive = zipfile.ZipFile(io.BytesIO(workbook_bytes))
    shared_strings = _xlsx_shared_strings(archive)
    sheets = []
    for sheet_name, path in _xlsx_sheet_map(archive):
        parsed = _parse_xlsx_sheet(archive, path, shared_strings)
        parsed.name = sheet_name
        sheets.append(parsed)
    return sheets


def parse_workbook(file_obj):
    name = getattr(file_obj, "name", "workbook").lower()
    if name.endswith(".csv"):
        sheets = _parse_csv_workbook(file_obj)
    elif name.endswith(".xlsx"):
        sheets = _parse_xlsx_workbook(file_obj)
    else:
        raise ValidationError("Upload a .csv or .xlsx workbook.")
    return {
        "file_name": getattr(file_obj, "name", "workbook"),
        "sheet_count": len(sheets),
        "sheets": [
            {
                "name": sheet.name,
                "headers": sheet.headers,
                "row_count": len(sheet.rows),
                "sample_rows": sheet.rows[:5],
            }
            for sheet in sheets
        ],
        "rows_by_sheet": {sheet.name: sheet.rows for sheet in sheets},
    }


def serialize_preview(preview: dict) -> str:
    return json.dumps(preview)


def deserialize_preview(payload: str) -> dict:
    return json.loads(payload)


def build_column_choices(preview: dict):
    choices = []
    for sheet in preview["sheets"]:
        for header in sheet["headers"]:
            key = f"{sheet['name']}::{header}"
            choices.append((key, f"{sheet['name']} / {header}"))
    return choices


def _value_from_key(sheet_name, row, key):
    if not key:
        return ""
    mapped_sheet, _, column = key.partition("::")
    if mapped_sheet != sheet_name:
        return ""
    return _clean_value(row.get(column))


def _infer_metric_type(raw_value: str) -> str:
    numeric = _parse_decimal(raw_value)
    if numeric is not None:
        return MetricType.NUMBER
    lowered = _clean_value(raw_value).lower()
    if lowered in {"yes", "no", "true", "false"}:
        return MetricType.BOOLEAN
    if lowered in {"1", "2", "3", "4", "5"}:
        return MetricType.RATING
    return MetricType.TEXT


def _default_category_from_name(name: str) -> str:
    lower = name.lower()
    if any(term in lower for term in ["velo", "speed", "jump", "shotput", "time"]):
        return "Athletic Performance"
    if any(term in lower for term in ["bat", "barrel", "launch", "contact", "exit"]):
        return "Hitting"
    if any(term in lower for term in ["command", "direction", "repeatability", "pitch"]):
        return "Pitching"
    if any(term in lower for term in ["stance", "balance", "movement", "body control"]):
        return "Movement"
    return "General"


def _match_player(*, first_name, last_name, full_name, email, external_player_id):
    queryset = PlayerProfile.objects.all()
    if external_player_id:
        exact = queryset.filter(external_player_id__iexact=external_player_id)
        count = exact.count()
        if count == 1:
            return exact.first(), None
        if count > 1:
            return None, "Ambiguous external player ID match."
    if email:
        exact = queryset.filter(email__iexact=email)
        count = exact.count()
        if count == 1:
            return exact.first(), None
        if count > 1:
            return None, "Ambiguous email match."
    if full_name:
        first_name, last_name = _split_name(full_name)
    if first_name and last_name:
        exact = queryset.filter(first_name__iexact=first_name, last_name__iexact=last_name)
        count = exact.count()
        if count == 1:
            return exact.first(), None
        if count > 1:
            return None, "Ambiguous name match."
    return None, None


def _ensure_player(*, first_name, last_name, full_name, email, external_player_id, create_missing_players):
    player, error = _match_player(
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        email=email,
        external_player_id=external_player_id,
    )
    if error:
        return None, error, False
    if player:
        return player, "", False
    if not create_missing_players:
        return None, "No matching player profile found.", False
    if full_name and not (first_name and last_name):
        first_name, last_name = _split_name(full_name)
    if not first_name or not last_name:
        return None, "Missing player name fields for new profile.", False
    player = PlayerProfile.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email or "",
        external_player_id=external_player_id or "",
    )
    return player, "", True


@transaction.atomic
def execute_import(
    *,
    import_record: EvaluationImport,
    preview: dict,
    mapping_config: dict,
    provision_accounts: bool = False,
):
    season = Season.objects.get(pk=mapping_config["season_id"])
    event, _ = EvaluationEvent.objects.get_or_create(
        season=season,
        name=mapping_config["event_name"],
        evaluated_on=date.fromisoformat(mapping_config["evaluated_on"]),
        defaults={
            "event_type": mapping_config.get("event_type", EvaluationEventType.CUSTOM),
            "source_import": import_record,
        },
    )
    import_record.season = season
    import_record.mapping_config = mapping_config
    import_record.preview_snapshot = preview

    results = {
        "created_profiles": 0,
        "evaluations_processed": 0,
        "metrics_created": 0,
        "accounts_provisioned": 0,
        "errors": [],
        "onboarding_report": [],
    }

    identity = mapping_config["identity"]
    metric_columns = mapping_config.get("metric_columns", [])
    summary_columns = mapping_config.get("summary_columns", [])
    ranking_columns = set(mapping_config.get("ranking_columns", []))
    category_column = mapping_config.get("category_column", "")

    grouped_rows = preview["rows_by_sheet"]
    evaluation_cache = {}

    for sheet_name, rows in grouped_rows.items():
        for row_index, row in enumerate(rows, start=2):
            full_name = _value_from_key(sheet_name, row, identity.get("full_name_column"))
            first_name = _value_from_key(sheet_name, row, identity.get("first_name_column"))
            last_name = _value_from_key(sheet_name, row, identity.get("last_name_column"))
            email = _value_from_key(sheet_name, row, identity.get("email_column"))
            external_player_id = _value_from_key(sheet_name, row, identity.get("external_id_column"))
            player, error, created_profile = _ensure_player(
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                email=email,
                external_player_id=external_player_id,
                create_missing_players=mapping_config.get("create_missing_players", True),
            )
            if error or not player:
                results["errors"].append(f"{sheet_name} row {row_index}: {error}")
                continue
            if created_profile:
                results["created_profiles"] += 1

            cache_key = (player.id, event.id)
            if cache_key in evaluation_cache:
                player_evaluation = evaluation_cache[cache_key]
            else:
                player_evaluation, _ = PlayerEvaluation.objects.get_or_create(
                    player=player,
                    evaluation_event=event,
                    defaults={
                        "season": season,
                        "import_record": import_record,
                        "source_sheet": sheet_name,
                        "source_row_number": row_index,
                        "raw_row_data": row,
                    },
                )
                evaluation_cache[cache_key] = player_evaluation
                results["evaluations_processed"] += 1

            summary_parts = []
            for summary_key in summary_columns:
                value = _value_from_key(sheet_name, row, summary_key)
                if value:
                    summary_parts.append(value)
            if summary_parts:
                player_evaluation.summary_text = "\n".join(summary_parts)
                player_evaluation.save(update_fields=["summary_text", "updated_at"])

            category_value = _value_from_key(sheet_name, row, category_column)
            for metric_key in metric_columns:
                raw_value = _value_from_key(sheet_name, row, metric_key)
                if raw_value == "":
                    continue
                mapped_sheet, _, source_column = metric_key.partition("::")
                if mapped_sheet != sheet_name:
                    continue
                display_name = source_column
                metric_slug = slugify(display_name)[:120] or f"metric-{row_index}"
                metric_type = _infer_metric_type(raw_value)
                numeric_value = _parse_decimal(raw_value) if metric_type == MetricType.NUMBER else None
                PlayerMetric.objects.create(
                    player=player,
                    season=season,
                    evaluation_event=event,
                    player_evaluation=player_evaluation,
                    metric_key=metric_slug,
                    display_name=display_name,
                    category=category_value or _default_category_from_name(display_name),
                    metric_type=metric_type,
                    numeric_value=numeric_value,
                    text_value=raw_value if metric_type == MetricType.TEXT else "",
                    rating_value=raw_value if metric_key in ranking_columns or metric_type == MetricType.RATING else "",
                    raw_value=raw_value,
                    source_sheet=sheet_name,
                    source_column=source_column,
                )
                results["metrics_created"] += 1

            mapped_columns = set()
            for group in [metric_columns, summary_columns, [category_column]]:
                mapped_columns.update(value for value in group if value)
            mapped_columns.update(value for value in identity.values() if value)
            unmapped = {}
            for column, value in row.items():
                prefixed = f"{sheet_name}::{column}"
                if prefixed not in mapped_columns and value not in ("", None):
                    unmapped[column] = value
            if unmapped:
                player_evaluation.unmapped_data = {**player_evaluation.unmapped_data, **unmapped}
                player_evaluation.save(update_fields=["unmapped_data", "updated_at"])

            if provision_accounts and not player.user_id:
                onboarding = provision_player_account(player)
                results["accounts_provisioned"] += 1
                results["onboarding_report"].append(onboarding)

    import_record.status = ImportStatus.IMPORTED if not results["errors"] else ImportStatus.PARTIAL
    import_record.row_errors = results["errors"]
    import_record.workbook_metadata = {
        "sheet_count": preview["sheet_count"],
        "event_id": event.id,
    }
    import_record.save()
    return results, event
