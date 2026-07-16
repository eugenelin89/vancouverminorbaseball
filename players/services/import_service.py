from __future__ import annotations

import csv
import io
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
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
from players.services.matching_service import (
    MATCH_AMBIGUOUS,
    MATCH_EXACT,
    MATCH_HIGH_CONFIDENCE,
    MATCH_NO_MATCH,
    PlayerMatchResult,
    find_player_match,
    match_by_identifier,
)
from seasons.models import PlayerRosterMembership, RosterStatus, SeasonTeam
from seasons.services.membership_service import create_membership, sync_player_current_team_fields, update_membership
from seasons.services.team_service import get_or_create_season_team, normalize_division_value, normalize_team_value


SOURCE_MEMBER_LIST = "vcb_member_list_csv"
SOURCE_ROSTER_DETAIL = "vcb_roster_detail_csv"
SOURCE_MANUAL_STAFF = "manual_staff_csv"

SOURCE_CHOICES = [
    (SOURCE_MEMBER_LIST, "VCB member list CSV"),
    (SOURCE_ROSTER_DETAIL, "VCB roster detail CSV"),
    (SOURCE_MANUAL_STAFF, "Manual staff CSV"),
]

MAX_CSV_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_CSV_ROWS = 5000

MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS = "_provision_player_accounts"
MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS = "_activate_player_accounts"

ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_NEEDS_REVIEW = "needs_review"
ACTION_SKIP = "skip"
ACTION_ERROR = "error"

RESOLUTION_ACTION_COMMIT = "commit"
RESOLUTION_ACTION_CREATE_NEW = "create_new"
RESOLUTION_ACTION_USE_CANDIDATE = "use_candidate"
RESOLUTION_KEEP_EXISTING = "keep_existing"
RESOLUTION_USE_IMPORTED = "use_imported"
RESOLUTION_METADATA_ONLY = "metadata_only"

PLAYER_FIELD_KEYS = [
    "first_name",
    "last_name",
    "preferred_name",
    "birthdate",
    "birth_year",
    "gender",
    "division",
    "team_name",
    "primary_positions",
    "bats",
    "throws",
    "school",
    "graduation_year",
]

PERMANENT_PLAYER_FIELD_KEYS = [
    "first_name",
    "last_name",
    "preferred_name",
    "birthdate",
    "birth_year",
    "gender",
    "primary_positions",
    "bats",
    "throws",
    "school",
    "graduation_year",
]

CONFLICT_FIELDS = [
    "first_name",
    "last_name",
    "preferred_name",
    "birthdate",
    "birth_year",
    "gender",
    "primary_positions",
    "bats",
    "throws",
    "school",
    "graduation_year",
]

IDENTIFIER_FIELD_TYPES = {
    "registration_id": "registration_id",
    "registrant_id": "registrant_id",
    "team_id": "team_id",
    "source_player_id": "source_player_id",
}

HEADER_ALIASES = {
    "first_name": {"first", "first name", "firstname", "given name", "player first name"},
    "last_name": {"last", "last name", "lastname", "surname", "family name", "player last name"},
    "full_name": {"name", "full name", "player", "player name"},
    "preferred_name": {"preferred", "preferred name", "nickname", "nick name"},
    "birthdate": {"birthdate", "birth date", "date of birth", "dob"},
    "birth_year": {"birth year", "year of birth", "yob"},
    "gender": {"gender", "sex"},
    "division": {"division", "level", "program"},
    "team_name": {"team", "team name", "current team"},
    "roster_status": {"roster status", "status", "membership status"},
    "jersey_number": {"jersey", "jersey number", "number", "uniform number"},
    "membership_start_date": {"membership start date", "start date", "starts on", "roster start"},
    "membership_end_date": {"membership end date", "end date", "ends on", "roster end"},
    "roster_source_id": {"roster source id", "membership id", "roster id"},
    "primary_positions": {"position", "positions", "primary position", "primary positions"},
    "bats": {"bats", "batting", "hits"},
    "throws": {"throws", "throwing"},
    "school": {"school"},
    "graduation_year": {"graduation year", "grad year", "class year"},
    "registration_id": {"registration id", "registration", "reg id"},
    "registrant_id": {"registrant id", "member id", "participant id"},
    "team_id": {"team id", "teamid"},
    "source_player_id": {"player id", "source player id", "external player id"},
}


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
    account_provisioning: dict[str, Any] = field(default_factory=dict)


def clean_cell(value) -> str:
    """Return a stripped string suitable for import processing."""
    return "" if value is None else str(value).strip()


def normalize_header(value) -> str:
    """Normalize an import header for matching mapped columns."""
    return " ".join(clean_cell(value).casefold().split())


def _normalize_source(value: str) -> str:
    normalized = normalize_header(value).replace(" ", "_")
    return normalized or SOURCE_MANUAL_STAFF


def _ensure_staff(actor):
    if not actor or not actor.is_authenticated or not (actor.is_staff or actor.is_superuser):
        raise PermissionDenied("Only staff/admin users can run player imports.")


def _json_preview_row(row: ImportPreviewRow) -> dict[str, Any]:
    return asdict(row)


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
    raw_size = len(raw_data.encode("utf-8")) if isinstance(raw_data, str) else len(raw_data)
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
        raise ValidationError("Duplicate or blank column headers were found: " + ", ".join(sorted(set(duplicate_headers))))

    rows = []
    for row_number, row in enumerate(reader, start=2):
        if len(rows) >= MAX_CSV_ROWS:
            raise ValidationError(f"CSV uploads are limited to {MAX_CSV_ROWS} data rows.")
        original_row = {}
        cleaned_row = {}
        for header in reader.fieldnames:
            stripped = clean_cell(header)
            original_value = row.get(header, "")
            original_row[stripped] = original_value
            cleaned_row[stripped] = clean_cell(original_value)
        rows.append({"row_number": row_number, "original_row": original_row, "cleaned_row": cleaned_row})

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
    headers = parsed.headers if isinstance(parsed, ParsedCsvFile) else parsed.get("headers", [])
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


def _date_to_string(value) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return clean_cell(value)


def _parse_identity_value(field_name: str, value):
    if field_name == "birthdate":
        return parse_birthdate(value) if not isinstance(value, date) else value
    if field_name in {"birth_year", "graduation_year"}:
        return parse_birth_year(value)
    return clean_cell(value)


def _identity_for_storage(identity: dict[str, Any]) -> dict[str, Any]:
    stored = {}
    for key, value in identity.items():
        if isinstance(value, date):
            stored[key] = value.isoformat()
        else:
            stored[key] = value
    return stored


def _identity_for_model(identity: dict[str, Any]) -> dict[str, Any]:
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


def build_roster_payload(row: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
    """Build season roster context from a source row and optional column mapping."""
    mapping = mapping or {}
    status_column = mapping.get("roster_status", "")
    starts_column = mapping.get("membership_start_date", "")
    ends_column = mapping.get("membership_end_date", "")
    try:
        roster_status = parse_roster_status(row.get(status_column, "")) if status_column else RosterStatus.ACTIVE
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
        "jersey_number": clean_cell(row.get(mapping.get("jersey_number", ""))) if mapping.get("jersey_number") else "",
        "starts_on": starts_on.isoformat() if starts_on else "",
        "ends_on": ends_on.isoformat() if ends_on else "",
        "roster_source_id": clean_cell(row.get(mapping.get("roster_source_id", ""))) if mapping.get("roster_source_id") else "",
        "errors": errors,
    }


def build_identity_payload(row: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
    """Build a player identity payload from a source row and optional column mapping."""
    mapping = mapping or {}
    identity = {}
    full_name_column = mapping.get("full_name", "")
    full_name = clean_cell(row.get(full_name_column)) if full_name_column else ""
    for target_field in PLAYER_FIELD_KEYS:
        source_field = mapping.get(target_field, target_field)
        identity[target_field] = _parse_identity_value(target_field, row.get(source_field))
    if full_name and not (identity.get("first_name") and identity.get("last_name")):
        first_name, last_name = split_full_name(full_name)
        identity["first_name"] = identity.get("first_name") or first_name
        identity["last_name"] = identity.get("last_name") or last_name
    return _identity_for_storage(identity)


def build_source_identifiers(row: dict[str, Any], mapping: dict[str, str] | None, source: str) -> list[dict[str, str]]:
    """Build source identifiers from mapped CSV columns."""
    mapping = mapping or {}
    identifiers = []
    for field_name, identifier_type in IDENTIFIER_FIELD_TYPES.items():
        column = mapping.get(field_name, "")
        value = clean_cell(row.get(column)) if column else ""
        if value:
            identifiers.append({"source": _normalize_source(source), "identifier_type": identifier_type, "identifier_value": value})
    return identifiers


def _unmapped_fields(row: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    mapped_headers = {header for header in mapping.values() if header}
    return {key: value for key, value in row.items() if key not in mapped_headers and value not in {"", None}}


def _parsed_to_snapshot(parsed: ParsedCsvFile) -> dict[str, Any]:
    return {
        "file_name": parsed.file_name,
        "headers": parsed.headers,
        "normalized_headers": parsed.normalized_headers,
        "rows": parsed.rows,
    }


def _snapshot_to_parsed(snapshot: dict[str, Any]) -> ParsedCsvFile:
    parsed = snapshot.get("parsed_csv", snapshot)
    return ParsedCsvFile(
        file_name=parsed.get("file_name", ""),
        headers=parsed.get("headers", []),
        normalized_headers=parsed.get("normalized_headers", {}),
        rows=parsed.get("rows", []),
    )


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
    _ensure_staff(uploaded_by)
    if season is None:
        raise ValidationError("Select an active season for this player import.")
    if not getattr(season, "is_active", False):
        raise ValidationError("Select an active season for this player import.")
    parsed = parse_player_csv(file_obj)
    normalized_source = _normalize_source(source or detect_source_from_filename(parsed.file_name))
    mapping_config = suggest_mapping(parsed.headers, source=normalized_source)
    mapping_config[MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS] = bool(provision_player_accounts)
    mapping_config[MAPPING_KEY_ACTIVATE_PLAYER_ACCOUNTS] = bool(provision_player_accounts) and bool(activate_player_accounts)
    batch = PlayerImportBatch.objects.create(
        source=normalized_source,
        original_filename=parsed.file_name,
        uploaded_by=uploaded_by,
        season=season,
        status=PlayerImportStatus.UPLOADED,
        mapping_config=mapping_config,
        preview_snapshot={"parsed_csv": _parsed_to_snapshot(parsed)},
        rows_processed=len(parsed.rows),
    )
    build_import_preview(import_batch=batch, mapping_config=mapping_config)
    return batch


def _match_identity(identity: dict[str, Any], source_identifiers: list[dict[str, str]]):
    model_identity = _identity_for_model(identity)
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


def _field_conflicts(player: Player | None, identity: dict[str, Any]) -> list[dict[str, str]]:
    if not player:
        return []
    model_identity = _identity_for_model(identity)
    conflicts = []
    for field_name in CONFLICT_FIELDS:
        imported = model_identity.get(field_name)
        existing = getattr(player, field_name, None)
        if existing in {"", None} or imported in {"", None}:
            continue
        existing_value = _date_to_string(existing)
        imported_value = _date_to_string(imported)
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


def _team_preview(roster: dict[str, Any], season) -> dict[str, Any]:
    team_name = roster.get("team_name", "")
    division = roster.get("division", "")
    if not team_name or not division:
        return {"action": "invalid_roster_context", "label": "Invalid Roster Context"}
    normalized_name = normalize_team_value(team_name)
    normalized_division = normalize_division_value(division)
    existing = SeasonTeam.objects.filter(
        season=season,
        normalized_name=normalized_name,
        normalized_division=normalized_division,
    ).first()
    return {
        "id": existing.id if existing else None,
        "name": existing.name if existing else team_name,
        "division": existing.division if existing else division,
        "action": "reuse" if existing else "create",
        "label": "Reuse Season Team" if existing else "Create Season Team",
    }


def _membership_preview(player: Player | None, season_team_preview: dict[str, Any], season, roster: dict[str, Any]) -> dict[str, Any]:
    if not player:
        return {"action": "create", "label": "Create Membership", "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE}
    existing_same_team = None
    if season_team_preview.get("id"):
        existing_same_team = PlayerRosterMembership.objects.filter(
            player=player,
            season_team_id=season_team_preview["id"],
        ).first()
    if existing_same_team:
        return {
            "id": existing_same_team.id,
            "action": "update",
            "label": "Update Membership",
            "is_primary": existing_same_team.is_primary,
        }
    primary = PlayerRosterMembership.objects.select_related("season_team").filter(
        player=player,
        season_team__season=season,
        is_active=True,
        is_primary=True,
    ).first()
    if primary:
        return {
            "id": None,
            "action": "review_team_change",
            "label": "Review Team Change",
            "is_primary": False,
            "existing_primary": str(primary.season_team),
        }
    return {"id": None, "action": "new_season_membership", "label": "New Season Membership", "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE}


def preview_row(*, row: dict[str, Any], mapping_config: dict[str, str], source: str, season=None) -> ImportPreviewRow:
    """Build preview data for a single CSV row."""
    cleaned_row = row["cleaned_row"]
    identity = build_identity_payload(cleaned_row, mapping_config)
    roster = build_roster_payload(cleaned_row, mapping_config)
    source_identifiers = build_source_identifiers(cleaned_row, mapping_config, source)
    errors = list(roster.get("errors", []))
    if not (identity.get("first_name") and identity.get("last_name")):
        errors.append("Map either a full name column or both first and last name columns.")
    if not season:
        errors.append("Select an active season for this import.")
    if not roster.get("team_name"):
        errors.append("Team is required for season-aware player import.")
    if not roster.get("division"):
        errors.append("Division is required for season-aware player import.")
    match_result = _match_identity(identity, source_identifiers) if not errors else None
    field_conflicts = _field_conflicts(getattr(match_result, "player", None), identity) if match_result else []
    season_team_preview = _team_preview(roster, season) if season and not (not roster.get("team_name") or not roster.get("division")) else {
        "action": "invalid_roster_context",
        "label": "Invalid Roster Context",
    }
    matched_player = getattr(match_result, "player", None) if match_result else None
    membership_preview = _membership_preview(matched_player, season_team_preview, season, roster) if season and not errors else {
        "action": "invalid_roster_context",
        "label": "Invalid Roster Context",
        "is_primary": False,
    }
    if membership_preview.get("action") == "review_team_change":
        errors.append(
            "Player already has an active primary membership in this season. Resolve the team change manually or skip this row."
        )

    if errors:
        action = ACTION_ERROR
        match_status = MATCH_NO_MATCH
    elif match_result.status == MATCH_EXACT:
        action = ACTION_NEEDS_REVIEW if field_conflicts else ACTION_UPDATE
        match_status = match_result.status
    elif match_result.status == MATCH_HIGH_CONFIDENCE:
        action = ACTION_NEEDS_REVIEW if field_conflicts else ACTION_UPDATE
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
        unmapped_fields=_unmapped_fields(cleaned_row, mapping_config),
        source_identifiers=source_identifiers,
        match_status=match_status,
        matched_player_id=getattr(matched_player, "id", None),
        matched_player_name=getattr(matched_player, "display_name", ""),
        candidate_ids=[candidate.id for candidate in candidates],
        candidate_names=[candidate.display_name for candidate in candidates],
        candidate_options=[{"id": candidate.id, "name": candidate.display_name} for candidate in candidates],
        field_conflicts=field_conflicts,
        errors=errors,
        action=action,
        roster={key: value for key, value in roster.items() if key != "errors"},
        season_team=season_team_preview,
        membership=membership_preview,
    )


@transaction.atomic
def build_import_preview(*, import_batch: PlayerImportBatch, mapping_config: dict[str, str] | None = None) -> dict[str, Any]:
    """Build and persist an import preview for a batch."""
    parsed = _snapshot_to_parsed(import_batch.preview_snapshot)
    mapping_config = mapping_config or import_batch.mapping_config or suggest_mapping(parsed.headers, source=import_batch.source)
    rows = [
        _json_preview_row(preview_row(row=row, mapping_config=mapping_config, source=import_batch.source, season=import_batch.season))
        for row in parsed.rows
    ]
    row_errors = [row for row in rows if row["errors"]]
    conflicted_rows = [row for row in rows if row["action"] == ACTION_NEEDS_REVIEW]
    preview = {
        "file_name": parsed.file_name,
        "source": import_batch.source,
        "season": {
            "id": import_batch.season_id,
            "name": import_batch.season.name if import_batch.season_id else "Legacy / No Season",
        },
        "headers": parsed.headers,
        "mapping_config": mapping_config,
        "account_provisioning": {
            "enabled": bool(mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS)),
            "activate_users": bool(mapping_config.get(MAPPING_KEY_PROVISION_PLAYER_ACCOUNTS)),
            "email_column": mapping_config.get("account_email", ""),
        },
        "rows": rows,
        "summary": {
            "rows_processed": len(rows),
            "rows_create": sum(1 for row in rows if row["action"] == ACTION_CREATE),
            "rows_update": sum(1 for row in rows if row["action"] == ACTION_UPDATE),
            "rows_needs_review": len(conflicted_rows),
            "rows_error": len(row_errors),
            "season_teams_create": sum(1 for row in rows if row.get("season_team", {}).get("action") == "create"),
            "season_teams_reuse": sum(1 for row in rows if row.get("season_team", {}).get("action") == "reuse"),
            "memberships_create": sum(1 for row in rows if row.get("membership", {}).get("action") in {"create", "new_season_membership"}),
            "memberships_update": sum(1 for row in rows if row.get("membership", {}).get("action") == "update"),
        },
    }
    import_batch.mapping_config = mapping_config
    import_batch.preview_snapshot = {"parsed_csv": _parsed_to_snapshot(parsed), "preview": preview}
    import_batch.row_errors = row_errors
    import_batch.conflict_summary = {
        "rows_conflicted": len(conflicted_rows),
        "row_numbers": [row["row_number"] for row in conflicted_rows],
    }
    import_batch.rows_processed = len(rows)
    import_batch.rows_conflicted = len(conflicted_rows)
    import_batch.status = PlayerImportStatus.NEEDS_REVIEW if conflicted_rows or row_errors else PlayerImportStatus.PREVIEWED
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


def create_player_from_import(identity: dict[str, Any]) -> Player:
    """Create a canonical player from import identity fields."""
    return Player.objects.create(**_identity_for_model(identity))


def apply_player_updates(player: Player, identity: dict[str, Any], field_resolutions: dict[str, str] | None = None) -> Player:
    """Fill blank player fields and apply explicit conflict resolutions."""
    field_resolutions = field_resolutions or {}
    model_identity = _identity_for_model(identity)
    changed_fields = []
    for field_name, imported_value in model_identity.items():
        existing_value = getattr(player, field_name)
        should_update = existing_value in {"", None} or field_resolutions.get(field_name) == RESOLUTION_USE_IMPORTED
        if should_update and imported_value not in {"", None} and existing_value != imported_value:
            setattr(player, field_name, imported_value)
            changed_fields.append(field_name)
    if changed_fields:
        changed_fields.append("updated_at")
        player.save(update_fields=changed_fields)
    return player


def attach_source_identifiers(player: Player, identifiers: list[dict[str, str]], metadata: dict[str, Any] | None = None):
    """Attach source identifiers, reporting duplicate ownership conflicts as errors."""
    errors = []
    for identifier in identifiers:
        source = _normalize_source(identifier["source"])
        identifier_type = normalize_header(identifier["identifier_type"]).replace(" ", "_")
        identifier_value = normalize_header(identifier["identifier_value"])
        existing = PlayerSourceIdentifier.objects.filter(
            source=source,
            identifier_type=identifier_type,
            identifier_value=identifier_value,
        ).select_related("player").first()
        if existing:
            if existing.player_id != player.id:
                errors.append(
                    f"Identifier {source}:{identifier_type}:{identifier_value} already belongs to {existing.player.display_name}."
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
            errors.append(f"Identifier {source}:{identifier_type}:{identifier_value} could not be attached.")
    return errors


def record_import_source_row(player: Player, import_batch: PlayerImportBatch, preview: dict[str, Any], actor) -> PlayerSourceRow:
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


def _parse_iso_date(value: str):
    cleaned = clean_cell(value)
    if not cleaned:
        return None
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Roster date is invalid.") from None


def _membership_update_values(roster: dict[str, Any]) -> dict[str, Any]:
    values = {}
    if roster.get("roster_status"):
        values["status"] = roster["roster_status"]
        values["is_active"] = roster["roster_status"] in {RosterStatus.ACTIVE, RosterStatus.GUEST}
        if not values["is_active"]:
            values["is_primary"] = False
    if roster.get("jersey_number"):
        values["jersey_number"] = roster["jersey_number"]
    if roster.get("starts_on"):
        values["starts_on"] = _parse_iso_date(roster["starts_on"])
    if roster.get("ends_on"):
        values["ends_on"] = _parse_iso_date(roster["ends_on"])
    if roster.get("roster_source_id"):
        values["source_identifier"] = roster["roster_source_id"]
    return values


def _commit_membership(player: Player, import_batch: PlayerImportBatch, preview_row_data: dict[str, Any]) -> tuple[str, bool]:
    if not import_batch.season_id:
        raise ValidationError("Import batch requires a season before memberships can be committed.")
    roster = preview_row_data.get("roster", {})
    team_name = roster.get("team_name", "")
    division = roster.get("division", "")
    if not team_name or not division:
        raise ValidationError("Team and division are required for roster membership.")
    season_team, team_created = get_or_create_season_team(
        season=import_batch.season,
        name=team_name,
        division=division,
        external_source=import_batch.source if roster.get("roster_source_id") else "",
        external_identifier=roster.get("roster_source_id", ""),
        metadata={"import_batch_id": import_batch.id},
    )
    existing = PlayerRosterMembership.objects.select_for_update().filter(player=player, season_team=season_team).first()
    values = _membership_update_values(roster)
    values.setdefault("source", import_batch.source)
    if existing:
        was_primary = existing.is_primary
        update_membership(existing, sync_player_fields=was_primary, **values)
        return "updated", team_created

    primary = PlayerRosterMembership.objects.select_for_update().filter(
        player=player,
        season_team__season=import_batch.season,
        is_active=True,
        is_primary=True,
    ).first()
    if primary:
        raise ValidationError("Player already has an active primary membership in this season.")
    status = values.pop("status", roster.get("roster_status") or RosterStatus.ACTIVE)
    is_active = values.pop("is_active", status in {RosterStatus.ACTIVE, RosterStatus.GUEST})
    membership = create_membership(
        player=player,
        season_team=season_team,
        status=status,
        is_primary=is_active,
        is_active=is_active,
        source=values.pop("source", import_batch.source),
        source_identifier=values.pop("source_identifier", roster.get("roster_source_id", "")),
        import_batch=import_batch,
        metadata={"row_number": preview_row_data["row_number"]},
        sync_player_fields=is_active,
        **values,
    )
    if membership.is_primary:
        sync_player_current_team_fields(player, import_batch.season)
    return "created", team_created


def _resolutions_for_row(resolutions: dict[str, Any], row_number: int) -> tuple[str, dict[str, str]]:
    row_key = str(row_number)
    row_resolution = resolutions.get(row_key, {}) if resolutions else {}
    return row_resolution.get("action", RESOLUTION_ACTION_COMMIT), row_resolution.get("fields", {})


def _candidate_id_for_row(resolutions: dict[str, Any], row_number: int) -> int | None:
    row_key = str(row_number)
    row_resolution = resolutions.get(row_key, {}) if resolutions else {}
    candidate_id = row_resolution.get("candidate_id")
    if not candidate_id:
        return None
    try:
        return int(candidate_id)
    except (TypeError, ValueError):
        return None


def _unresolved_review_messages(preview: dict[str, Any], resolutions: dict[str, Any]) -> list[str]:
    messages = []
    for preview_row_data in preview.get("rows", []):
        row_number = preview_row_data["row_number"]
        row_action, field_resolutions = _resolutions_for_row(resolutions, row_number)
        if row_action == ACTION_SKIP:
            continue
        if preview_row_data["action"] == ACTION_ERROR:
            messages.append(f"Row {row_number}: fix mapping/data errors or explicitly skip the row.")
            continue
        if preview_row_data["match_status"] == MATCH_AMBIGUOUS:
            candidate_id = _candidate_id_for_row(resolutions, row_number)
            if row_action == RESOLUTION_ACTION_CREATE_NEW:
                continue
            if row_action == RESOLUTION_ACTION_USE_CANDIDATE and candidate_id in preview_row_data.get("candidate_ids", []):
                continue
            messages.append(f"Row {row_number}: choose an existing candidate, create a new player, or skip the row.")
            continue
        if preview_row_data["action"] == ACTION_NEEDS_REVIEW:
            conflict_fields = {conflict["field_name"] for conflict in preview_row_data.get("field_conflicts", [])}
            resolved_fields = set(field_resolutions)
            if conflict_fields and conflict_fields.issubset(resolved_fields):
                continue
            messages.append(f"Row {row_number}: resolve all field conflicts or explicitly skip the row.")
    return messages


@transaction.atomic
def commit_import_batch(*, import_batch: PlayerImportBatch, actor, resolutions: dict[str, Any] | None = None) -> ImportCommitResult:
    """Commit a previewed import batch to canonical player records."""
    _ensure_staff(actor)
    resolutions = resolutions or {}
    locked_batch = PlayerImportBatch.objects.select_for_update().get(pk=import_batch.pk)
    if locked_batch.status == PlayerImportStatus.COMMITTED:
        raise ValidationError("This import batch has already been committed.")
    if not locked_batch.season_id:
        raise ValidationError("Select an active season before committing this player import.")

    preview = current_preview(locked_batch)
    if not preview:
        preview = build_import_preview(import_batch=locked_batch)

    unresolved_messages = _unresolved_review_messages(preview, resolutions)
    if unresolved_messages:
        locked_batch.status = PlayerImportStatus.NEEDS_REVIEW
        locked_batch.row_errors = unresolved_messages
        locked_batch.save(update_fields=["status", "row_errors", "updated_at"])
        raise ValidationError("Resolve or explicitly skip review rows before committing this import.")

    result = ImportCommitResult(rows_processed=len(preview.get("rows", [])))
    committed_rows = []
    for preview_row_data in preview.get("rows", []):
        row_number = preview_row_data["row_number"]
        row_action, field_resolutions = _resolutions_for_row(resolutions, row_number)
        if row_action == ACTION_SKIP:
            result.skipped += 1
            continue
        if preview_row_data["action"] == ACTION_ERROR:
            result.skipped += 1
            result.errors.append(f"Row {row_number}: {'; '.join(preview_row_data['errors'])}")
            continue

        player = None
        if preview_row_data["match_status"] == MATCH_AMBIGUOUS:
            if row_action == RESOLUTION_ACTION_CREATE_NEW:
                player = create_player_from_import(preview_row_data["identity"])
                result.created += 1
            else:
                candidate_id = _candidate_id_for_row(resolutions, row_number)
                player = Player.objects.select_for_update().get(pk=candidate_id)
                apply_player_updates(player, preview_row_data["identity"])
                result.updated += 1
        elif preview_row_data["matched_player_id"]:
            player = Player.objects.select_for_update().get(pk=preview_row_data["matched_player_id"])
            apply_player_updates(player, preview_row_data["identity"], field_resolutions=field_resolutions)
            result.updated += 1
        else:
            player = create_player_from_import(preview_row_data["identity"])
            result.created += 1

        identifier_errors = attach_source_identifiers(
            player,
            preview_row_data.get("source_identifiers", []),
            metadata={"import_batch_id": locked_batch.id, "row_number": row_number},
        )
        result.errors.extend([f"Row {row_number}: {error}" for error in identifier_errors])
        record_import_source_row(player, locked_batch, preview_row_data, actor)
        membership_action, team_created = _commit_membership(player, locked_batch, preview_row_data)
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
        from accounts.services.provisioning_service import ProvisioningOptions, provision_accounts_for_import

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
