"""CSV and primitive parsing helpers for player imports."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime

from django.core.exceptions import ValidationError

from players.services.imports.constants import (
    HEADER_ALIASES,
    MAX_CSV_ROWS,
    MAX_CSV_UPLOAD_BYTES,
    SOURCE_MANUAL_STAFF,
    SOURCE_MEMBER_LIST,
    SOURCE_ROSTER_DETAIL,
)
from players.services.imports.result_models import ParsedCsvFile
from seasons.models import RosterStatus


def clean_cell(value) -> str:
    """Return a stripped string suitable for import processing."""
    return "" if value is None else str(value).strip()


def normalize_header(value) -> str:
    """Normalize an import header for matching mapped columns."""
    return " ".join(clean_cell(value).casefold().split())


def normalize_source(value: str) -> str:
    normalized = normalize_header(value).replace(" ", "_")
    return normalized or SOURCE_MANUAL_STAFF


def detect_source_from_filename(filename: str) -> str:
    """Infer a stable source name from a CSV filename."""
    lowered = normalize_header(filename)
    if "roster" in lowered and "detail" in lowered:
        return SOURCE_ROSTER_DETAIL
    if "member" in lowered:
        return SOURCE_MEMBER_LIST
    return SOURCE_MANUAL_STAFF


def parse_player_csv(file_obj) -> ParsedCsvFile:
    """Parse a player CSV upload and preserve original row values."""
    file_name = getattr(file_obj, "name", "players.csv")
    if not file_name.lower().endswith(".csv"):
        raise ValidationError("Upload a .csv file.")
    file_size = getattr(file_obj, "size", None)
    if file_size is not None and file_size > MAX_CSV_UPLOAD_BYTES:
        raise ValidationError("CSV uploads are limited to 5 MB.")

    raw_data = file_obj.read()
    raw_size = (
        len(raw_data.encode("utf-8")) if isinstance(raw_data, str) else len(raw_data)
    )
    if raw_size > MAX_CSV_UPLOAD_BYTES:
        raise ValidationError("CSV uploads are limited to 5 MB.")
    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode("utf-8-sig")
    file_obj.seek(0)

    reader = csv.DictReader(io.StringIO(raw_data))
    if not reader.fieldnames:
        raise ValidationError("The uploaded CSV does not contain a header row.")

    headers = []
    normalized_headers = {}
    duplicate_headers = []
    for header in reader.fieldnames:
        stripped = clean_cell(header)
        if not stripped:
            duplicate_headers.append("<blank header>")
            continue
        normalized = normalize_header(stripped)
        if normalized in normalized_headers:
            duplicate_headers.append(stripped)
        normalized_headers[normalized] = stripped
        headers.append(stripped)

    if duplicate_headers:
        raise ValidationError(
            "Duplicate or blank column headers were found: "
            + ", ".join(sorted(set(duplicate_headers)))
        )

    rows = []
    for row_number, row in enumerate(reader, start=2):
        if len(rows) >= MAX_CSV_ROWS:
            raise ValidationError(
                f"CSV uploads are limited to {MAX_CSV_ROWS} data rows."
            )
        original_row = {}
        cleaned_row = {}
        for header in reader.fieldnames:
            stripped = clean_cell(header)
            original_value = row.get(header, "")
            original_row[stripped] = original_value
            cleaned_row[stripped] = clean_cell(original_value)
        rows.append(
            {
                "row_number": row_number,
                "original_row": original_row,
                "cleaned_row": cleaned_row,
            }
        )

    return ParsedCsvFile(
        file_name=file_name,
        headers=headers,
        normalized_headers=normalized_headers,
        rows=rows,
        duplicate_headers=duplicate_headers,
    )


def serialize_preview(preview: dict) -> dict:
    """Return a JSON-ready preview payload."""
    return preview


def deserialize_preview(payload: dict) -> dict:
    """Return a preview payload from JSON data."""
    return payload or {}


def build_column_choices(parsed: ParsedCsvFile | dict) -> list[tuple[str, str]]:
    """Build form choices for parsed CSV headers."""
    headers = (
        parsed.headers
        if isinstance(parsed, ParsedCsvFile)
        else parsed.get("headers", [])
    )
    return [(header, header) for header in headers]


def suggest_mapping(headers: list[str], source: str = "") -> dict[str, str]:
    """Suggest canonical player field mappings from CSV headers."""
    mapping = {}
    normalized_to_header = {normalize_header(header): header for header in headers}
    for target, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            if alias in normalized_to_header:
                mapping[target] = normalized_to_header[alias]
                break
    return mapping


def split_full_name(full_name: str) -> tuple[str, str]:
    """Split a full name into first and last name for import matching."""
    parts = [part for part in clean_cell(full_name).split() if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def parse_birthdate(value: str):
    """Parse common ISO-style birthdate values."""
    cleaned = clean_cell(value)
    if not cleaned:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def parse_import_date(value: str):
    """Parse optional roster date values from CSV input."""
    return parse_birthdate(value)


ROSTER_STATUS_ALIASES = {
    "": RosterStatus.ACTIVE,
    "active": RosterStatus.ACTIVE,
    "inactive": RosterStatus.INACTIVE,
    "transferred": RosterStatus.TRANSFERRED,
    "transfer": RosterStatus.TRANSFERRED,
    "guest": RosterStatus.GUEST,
    "removed": RosterStatus.REMOVED,
    "remove": RosterStatus.REMOVED,
}


def parse_roster_status(value: str) -> str:
    cleaned = normalize_header(value)
    if cleaned in ROSTER_STATUS_ALIASES:
        return ROSTER_STATUS_ALIASES[cleaned]
    raise ValidationError(f"Unknown roster status '{clean_cell(value)}'.")


def parse_birth_year(value: str):
    """Parse a birth year from a string."""
    cleaned = clean_cell(value)
    if not cleaned:
        return None
    try:
        year = int(cleaned)
    except ValueError:
        return None
    if 1900 <= year <= date.today().year:
        return year
    return None
