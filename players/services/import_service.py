from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ImportIdentityRow:
    row_number: int | None
    identity: dict[str, Any]
    original_row: dict[str, Any] = field(default_factory=dict)
    unmapped_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportRowResult:
    row_number: int | None
    imported: bool
    errors: list[str] = field(default_factory=list)
    identity: dict[str, Any] = field(default_factory=dict)


def clean_cell(value) -> str:
    """Return a stripped string suitable for import processing."""
    return "" if value is None else str(value).strip()


def normalize_header(value) -> str:
    """Normalize an import header for matching mapped columns."""
    return " ".join(clean_cell(value).casefold().split())


def build_identity_payload(row: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
    """Build a player identity payload from a source row and optional column mapping."""
    mapping = mapping or {}
    payload = {}
    for target_field in [
        "first_name",
        "last_name",
        "preferred_name",
        "birthdate",
        "birth_year",
        "gender",
        "division",
        "team_name",
        "source",
        "identifier_type",
        "identifier_value",
    ]:
        source_field = mapping.get(target_field, target_field)
        payload[target_field] = clean_cell(row.get(source_field))
    return payload
