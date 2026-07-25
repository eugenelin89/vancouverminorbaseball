"""Data contracts for player import parsing, preview, and commit results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from players.services.imports.constants import ACTION_CREATE, RESOLUTION_KEEP_EXISTING


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


@dataclass
class ParsedCsvFile:
    file_name: str
    headers: list[str]
    normalized_headers: dict[str, str]
    rows: list[dict[str, Any]]
    duplicate_headers: list[str] = field(default_factory=list)


@dataclass
class FieldConflict:
    field_name: str
    existing_value: str
    imported_value: str
    resolution: str = RESOLUTION_KEEP_EXISTING


@dataclass
class ImportPreviewRow:
    row_number: int
    identity: dict[str, Any]
    original_row: dict[str, Any]
    unmapped_fields: dict[str, Any]
    source_identifiers: list[dict[str, str]]
    match_status: str
    matched_player_id: int | None = None
    matched_player_name: str = ""
    candidate_ids: list[int] = field(default_factory=list)
    candidate_names: list[str] = field(default_factory=list)
    candidate_options: list[dict[str, Any]] = field(default_factory=list)
    field_conflicts: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    action: str = ACTION_CREATE
    roster: dict[str, Any] = field(default_factory=dict)
    season_team: dict[str, Any] = field(default_factory=dict)
    membership: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportCommitResult:
    rows_processed: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    conflicts: int = 0
    season_teams_created: int = 0
    season_teams_reused: int = 0
    memberships_created: int = 0
    memberships_updated: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    account_provisioning: dict[str, Any] = field(default_factory=dict)
