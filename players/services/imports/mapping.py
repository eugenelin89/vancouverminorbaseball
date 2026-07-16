"""Column mapping and row normalization for player imports."""

from __future__ import annotations

from datetime import date
from typing import Any

from django.core.exceptions import ValidationError

from players.services.imports.constants import (
    IDENTIFIER_FIELD_TYPES,
    PERMANENT_PLAYER_FIELD_KEYS,
    PLAYER_FIELD_KEYS,
)
from players.services.imports.parsing import (
    clean_cell,
    normalize_source,
    parse_birth_year,
    parse_birthdate,
    parse_import_date,
    parse_roster_status,
    split_full_name,
)
from players.services.imports.result_models import ParsedCsvFile
from seasons.models import RosterStatus


def date_to_string(value) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return clean_cell(value)


def parse_identity_value(field_name: str, value):
    if field_name == "birthdate":
        return parse_birthdate(value) if not isinstance(value, date) else value
    if field_name in {"birth_year", "graduation_year"}:
        return parse_birth_year(value)
    return clean_cell(value)


def identity_for_storage(identity: dict[str, Any]) -> dict[str, Any]:
    stored = {}
    for key, value in identity.items():
        if isinstance(value, date):
            stored[key] = value.isoformat()
        else:
            stored[key] = value
    return stored


def identity_for_model(identity: dict[str, Any]) -> dict[str, Any]:
    model_identity = {}
    for field_name in PERMANENT_PLAYER_FIELD_KEYS:
        value = identity.get(field_name)
        if field_name == "birthdate" and value:
            value = parse_birthdate(value) if not isinstance(value, date) else value
        elif field_name in {"birth_year", "graduation_year"} and value:
            value = parse_birth_year(value)
        if value not in {"", None}:
            model_identity[field_name] = value
    return model_identity


def build_roster_payload(
    row: dict[str, Any], mapping: dict[str, str] | None = None
) -> dict[str, Any]:
    """Build season roster context from a source row and optional column mapping."""
    mapping = mapping or {}
    status_column = mapping.get("roster_status", "")
    starts_column = mapping.get("membership_start_date", "")
    ends_column = mapping.get("membership_end_date", "")
    try:
        roster_status = (
            parse_roster_status(row.get(status_column, ""))
            if status_column
            else RosterStatus.ACTIVE
        )
    except ValidationError as exc:
        roster_status = ""
        status_errors = list(exc.messages)
    else:
        status_errors = []

    starts_on = parse_import_date(row.get(starts_column, "")) if starts_column else None
    ends_on = parse_import_date(row.get(ends_column, "")) if ends_column else None
    errors = status_errors
    if starts_column and clean_cell(row.get(starts_column)) and starts_on is None:
        errors.append("Membership start date is invalid.")
    if ends_column and clean_cell(row.get(ends_column)) and ends_on is None:
        errors.append("Membership end date is invalid.")
    if starts_on and ends_on and ends_on < starts_on:
        errors.append("Membership end date cannot be before start date.")

    return {
        "team_name": clean_cell(row.get(mapping.get("team_name", "team_name"))),
        "division": clean_cell(row.get(mapping.get("division", "division"))),
        "roster_status": roster_status,
        "jersey_number": (
            clean_cell(row.get(mapping.get("jersey_number", "")))
            if mapping.get("jersey_number")
            else ""
        ),
        "starts_on": starts_on.isoformat() if starts_on else "",
        "ends_on": ends_on.isoformat() if ends_on else "",
        "roster_source_id": (
            clean_cell(row.get(mapping.get("roster_source_id", "")))
            if mapping.get("roster_source_id")
            else ""
        ),
        "errors": errors,
    }


def build_identity_payload(
    row: dict[str, Any], mapping: dict[str, str] | None = None
) -> dict[str, Any]:
    """Build a player identity payload from a source row and optional column mapping."""
    mapping = mapping or {}
    identity = {}
    full_name_column = mapping.get("full_name", "")
    full_name = clean_cell(row.get(full_name_column)) if full_name_column else ""
    for target_field in PLAYER_FIELD_KEYS:
        source_field = mapping.get(target_field, target_field)
        identity[target_field] = parse_identity_value(
            target_field, row.get(source_field)
        )
    if full_name and not (identity.get("first_name") and identity.get("last_name")):
        first_name, last_name = split_full_name(full_name)
        identity["first_name"] = identity.get("first_name") or first_name
        identity["last_name"] = identity.get("last_name") or last_name
    return identity_for_storage(identity)


def build_source_identifiers(
    row: dict[str, Any], mapping: dict[str, str] | None, source: str
) -> list[dict[str, str]]:
    """Build source identifiers from mapped CSV columns."""
    mapping = mapping or {}
    identifiers = []
    for field_name, identifier_type in IDENTIFIER_FIELD_TYPES.items():
        column = mapping.get(field_name, "")
        value = clean_cell(row.get(column)) if column else ""
        if value:
            identifiers.append(
                {
                    "source": normalize_source(source),
                    "identifier_type": identifier_type,
                    "identifier_value": value,
                }
            )
    return identifiers


def unmapped_fields(row: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    mapped_headers = {header for header in mapping.values() if header}
    return {
        key: value
        for key, value in row.items()
        if key not in mapped_headers and value not in {"", None}
    }


def parsed_to_snapshot(parsed: ParsedCsvFile) -> dict[str, Any]:
    return {
        "file_name": parsed.file_name,
        "headers": parsed.headers,
        "normalized_headers": parsed.normalized_headers,
        "rows": parsed.rows,
    }


def snapshot_to_parsed(snapshot: dict[str, Any]) -> ParsedCsvFile:
    parsed = snapshot.get("parsed_csv", snapshot)
    return ParsedCsvFile(
        file_name=parsed.get("file_name", ""),
        headers=parsed.get("headers", []),
        normalized_headers=parsed.get("normalized_headers", {}),
        rows=parsed.get("rows", []),
    )
