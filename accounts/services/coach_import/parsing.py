"""CSV and primitive parsing helpers for coach imports."""

from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO

from django.core.exceptions import ValidationError

from accounts.services.coach_import.constants import (
    REQUIRED_COLUMNS,
    ROLE_ALIASES,
    SUPPORTED_COLUMNS,
)
from seasons.models import CoachAssignmentRole


def parse_bool(value, default=True) -> bool:
    text = str(value or "").strip().casefold()
    if not text:
        return default
    if text in {"1", "true", "yes", "y", "active"}:
        return True
    if text in {"0", "false", "no", "n", "inactive"}:
        return False
    raise ValidationError("is_active must be true or false.")


def normalize_header(header: str) -> str:
    return str(header or "").strip().casefold().replace(" ", "_")


def parse_assignment_role(value: str) -> str:
    normalized = normalize_header(value).replace("_", " ")
    if normalized in ROLE_ALIASES:
        return ROLE_ALIASES[normalized]
    raise ValidationError(f"Unknown assignment role '{str(value or '').strip()}'.")


def assignment_role_label(value: str) -> str:
    return CoachAssignmentRole(value).label


def parse_import_date(value: str):
    cleaned = str(value or "").strip()
    if not cleaned:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    raise ValidationError("Assignment date is invalid.")


def decode_csv_file(uploaded_file) -> str:
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    if isinstance(raw, str):
        return raw
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError("Coach import CSV must be UTF-8 encoded.") from exc


def read_csv(csv_text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(StringIO(csv_text))
    headers = [normalize_header(header) for header in (reader.fieldnames or [])]
    missing = sorted(REQUIRED_COLUMNS - set(headers))
    if missing:
        raise ValidationError(f"Missing required column(s): {', '.join(missing)}.")

    rows = []
    for raw_row in reader:
        normalized_row = {}
        for header, value in raw_row.items():
            normalized_header = normalize_header(header)
            if normalized_header in SUPPORTED_COLUMNS:
                normalized_row[normalized_header] = str(value or "").strip()
        rows.append(normalized_row)
    return headers, rows


def season_matches(row_value: str, season) -> bool:
    normalized = str(row_value or "").strip().casefold()
    return normalized in {season.key.casefold(), season.name.casefold()}
