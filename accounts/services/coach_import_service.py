from __future__ import annotations

import csv
from dataclasses import dataclass, field, replace
from datetime import datetime
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import AccountRole
from accounts.services.email_service import find_existing_email_user, normalize_email
from accounts.services.password_service import set_random_temporary_password
from accounts.services.permissions import can_manage_accounts
from accounts.services.profile_service import get_or_create_account_profile, set_account_role
from accounts.services.username_service import validate_available_username, username_for_person
from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, Season, SeasonTeam
from seasons.services.coach_assignment_service import create_assignment, get_primary_assignment, update_assignment
from seasons.services.team_service import get_or_create_season_team, normalize_division_value, normalize_team_value


User = get_user_model()

REQUIRED_COLUMNS = {"first_name", "last_name", "email"}
OPTIONAL_COLUMNS = {
    "username",
    "team",
    "division",
    "is_active",
    "notes",
    "source_id",
    "season",
    "assignment_role",
    "assignment_start_date",
    "assignment_end_date",
    "assignment_source_id",
}
SUPPORTED_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS

STATUS_READY = "ready"
STATUS_REUSE = "reuse"
STATUS_CONFLICT = "conflict"
STATUS_ERROR = "error"

RESULT_CREATED = "created"
RESULT_REUSED = "reused"
RESULT_CONFLICT = "conflict"
RESULT_ERROR = "error"
RESULT_SKIPPED = "skipped"


@dataclass(frozen=True)
class CoachImportRowPreview:
    row_number: int
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    username: str = ""
    generated_username: str = ""
    team: str = ""
    division: str = ""
    is_active: bool = True
    notes: str = ""
    source_id: str = ""
    assignment_role: str = CoachAssignmentRole.ASSISTANT_COACH
    assignment_role_label: str = CoachAssignmentRole.ASSISTANT_COACH.label
    assignment_start_date: str = ""
    assignment_end_date: str = ""
    assignment_source_id: str = ""
    season_team_action: str = ""
    season_team_label: str = ""
    assignment_action: str = ""
    assignment_label: str = ""
    account_action: str = ""
    account_label: str = ""
    password_behavior: str = ""
    status: str = STATUS_READY
    messages: list[str] = field(default_factory=list)
    existing_user_id: int | None = None

    @property
    def final_username(self) -> str:
        return self.username or self.generated_username

    @property
    def can_commit(self) -> bool:
        return self.status in {STATUS_READY, STATUS_REUSE}


@dataclass(frozen=True)
class CoachImportPreview:
    rows: list[CoachImportRowPreview]
    headers: list[str]
    row_errors: list[str]
    season_id: int | None = None
    season_name: str = ""

    @property
    def rows_processed(self) -> int:
        return len(self.rows)

    @property
    def ready_count(self) -> int:
        return sum(1 for row in self.rows if row.status == STATUS_READY)

    @property
    def reuse_count(self) -> int:
        return sum(1 for row in self.rows if row.status == STATUS_REUSE)

    @property
    def conflict_count(self) -> int:
        return sum(1 for row in self.rows if row.status == STATUS_CONFLICT)

    @property
    def error_count(self) -> int:
        return len(self.row_errors) + sum(1 for row in self.rows if row.status == STATUS_ERROR)

    @property
    def can_confirm(self) -> bool:
        return any(row.can_commit for row in self.rows)

    @property
    def season_teams_create(self) -> int:
        return sum(1 for row in self.rows if row.season_team_action == "create")

    @property
    def season_teams_reuse(self) -> int:
        return sum(1 for row in self.rows if row.season_team_action == "reuse")

    @property
    def assignments_create(self) -> int:
        return sum(1 for row in self.rows if row.assignment_action == "create")

    @property
    def assignments_update(self) -> int:
        return sum(1 for row in self.rows if row.assignment_action in {"update", "reuse"})


@dataclass(frozen=True)
class CoachImportResultRow:
    row_number: int
    status: str
    username: str = ""
    user_id: int | None = None
    is_active: bool = False
    temporary_password: str = field(default="", repr=False)
    season_name: str = ""
    team: str = ""
    division: str = ""
    assignment_role_label: str = ""
    assignment_status: str = ""
    password_behavior: str = ""
    messages: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CoachImportResult:
    rows: list[CoachImportResultRow]
    season_id: int | None = None
    season_name: str = ""

    @property
    def rows_processed(self) -> int:
        return len(self.rows)

    @property
    def users_created(self) -> int:
        return sum(1 for row in self.rows if row.status == RESULT_CREATED)

    @property
    def existing_coaches_reused(self) -> int:
        return sum(1 for row in self.rows if row.status == RESULT_REUSED)

    @property
    def conflicts(self) -> int:
        return sum(1 for row in self.rows if row.status == RESULT_CONFLICT)

    @property
    def errors(self) -> int:
        return sum(1 for row in self.rows if row.status == RESULT_ERROR)

    @property
    def skipped_rows(self) -> int:
        return sum(1 for row in self.rows if row.status == RESULT_SKIPPED)

    @property
    def active_accounts(self) -> int:
        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and row.is_active)

    @property
    def inactive_accounts(self) -> int:
        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and not row.is_active)

    @property
    def password_change_required(self) -> int:
        return sum(1 for row in self.rows if row.status == RESULT_CREATED)

    @property
    def season_teams_created(self) -> int:
        return sum(1 for row in self.rows if "season team created" in row.messages)

    @property
    def season_teams_reused(self) -> int:
        return sum(1 for row in self.rows if "season team reused" in row.messages)

    @property
    def assignments_created(self) -> int:
        return sum(1 for row in self.rows if row.assignment_status == "created")

    @property
    def assignments_updated(self) -> int:
        return sum(1 for row in self.rows if row.assignment_status in {"updated", "reused"})


def _validate_actor(actor) -> None:
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can import coaches.")


def _parse_bool(value, default=True) -> bool:
    text = str(value or "").strip().casefold()
    if not text:
        return default
    if text in {"1", "true", "yes", "y", "active"}:
        return True
    if text in {"0", "false", "no", "n", "inactive"}:
        return False
    raise ValidationError("is_active must be true or false.")


ROLE_ALIASES = {
    "": CoachAssignmentRole.ASSISTANT_COACH,
    "assistant": CoachAssignmentRole.ASSISTANT_COACH,
    "assistant coach": CoachAssignmentRole.ASSISTANT_COACH,
    "assistant_coach": CoachAssignmentRole.ASSISTANT_COACH,
    "head": CoachAssignmentRole.HEAD_COACH,
    "head coach": CoachAssignmentRole.HEAD_COACH,
    "head_coach": CoachAssignmentRole.HEAD_COACH,
    "manager": CoachAssignmentRole.MANAGER,
    "coordinator": CoachAssignmentRole.COORDINATOR,
    "evaluator": CoachAssignmentRole.EVALUATOR,
}


def _parse_assignment_role(value: str) -> str:
    normalized = _normalize_header(value).replace("_", " ")
    if normalized in ROLE_ALIASES:
        return ROLE_ALIASES[normalized]
    raise ValidationError(f"Unknown assignment role '{str(value or '').strip()}'.")


def _assignment_role_label(value: str) -> str:
    return CoachAssignmentRole(value).label


def _parse_import_date(value: str):
    cleaned = str(value or "").strip()
    if not cleaned:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    raise ValidationError("Assignment date is invalid.")


def _decode_csv_file(uploaded_file) -> str:
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    if isinstance(raw, str):
        return raw
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError("Coach import CSV must be UTF-8 encoded.") from exc


def _normalize_header(header: str) -> str:
    return str(header or "").strip().casefold().replace(" ", "_")


def _read_csv(csv_text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(StringIO(csv_text))
    headers = [_normalize_header(header) for header in (reader.fieldnames or [])]
    missing = sorted(REQUIRED_COLUMNS - set(headers))
    if missing:
        raise ValidationError(f"Missing required column(s): {', '.join(missing)}.")

    rows = []
    for raw_row in reader:
        normalized_row = {}
        for header, value in raw_row.items():
            normalized_header = _normalize_header(header)
            if normalized_header in SUPPORTED_COLUMNS:
                normalized_row[normalized_header] = str(value or "").strip()
        rows.append(normalized_row)
    return headers, rows


def _role_for_user(user) -> str:
    profile = getattr(user, "account_profile", None)
    if profile:
        return profile.role
    return get_or_create_account_profile(user).role


def _season_matches(row_value: str, season: Season) -> bool:
    normalized = str(row_value or "").strip().casefold()
    return normalized in {season.key.casefold(), season.name.casefold()}


def _season_team_preview(*, season: Season, team: str, division: str) -> tuple[str, str]:
    normalized_team = normalize_team_value(team)
    normalized_division = normalize_division_value(division)
    existing = SeasonTeam.objects.filter(
        season=season,
        normalized_name=normalized_team,
        normalized_division=normalized_division,
    ).first()
    if existing:
        return "reuse", "Reuse Season Team"
    return "create", "Create Season Team"


def _assignment_preview(*, user, season: Season, team: str, division: str, assignment_role: str, is_active: bool) -> tuple[str, str]:
    if not user:
        return "create", "Create Assignment"
    normalized_team = normalize_team_value(team)
    normalized_division = normalize_division_value(division)
    existing = CoachSeasonAssignment.objects.select_related("season_team").filter(
        user=user,
        season_team__season=season,
        season_team__normalized_name=normalized_team,
        season_team__normalized_division=normalized_division,
        assignment_role=assignment_role,
    ).first()
    if existing:
        return "update", "Update Assignment" if is_active else "Update Inactive Assignment"
    return "create", "Create Assignment"


def _preview_row(row_number: int, row: dict[str, str], season: Season) -> CoachImportRowPreview:
    messages = []
    first_name = row.get("first_name", "").strip()
    last_name = row.get("last_name", "").strip()
    email = normalize_email(row.get("email", ""))
    explicit_username = row.get("username", "").strip()
    team = row.get("team", "").strip()
    division = row.get("division", "").strip()
    notes = row.get("notes", "").strip()
    source_id = row.get("source_id", "").strip()
    assignment_source_id = row.get("assignment_source_id", "").strip() or source_id
    starts_raw = row.get("assignment_start_date", "").strip()
    ends_raw = row.get("assignment_end_date", "").strip()

    try:
        is_active = _parse_bool(row.get("is_active", ""), default=True)
        assignment_role = _parse_assignment_role(row.get("assignment_role", ""))
        starts_on = _parse_import_date(starts_raw)
        ends_on = _parse_import_date(ends_raw)
    except ValidationError as exc:
        return CoachImportRowPreview(row_number=row_number, status=STATUS_ERROR, messages=list(exc.messages))
    if starts_on and ends_on and ends_on < starts_on:
        return CoachImportRowPreview(row_number=row_number, status=STATUS_ERROR, messages=["Assignment end date cannot be before start date."])

    season_value = row.get("season", "").strip()
    if season_value and not _season_matches(season_value, season):
        return CoachImportRowPreview(
            row_number=row_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=explicit_username,
            team=team,
            division=division,
            is_active=is_active,
            notes=notes,
            source_id=source_id,
            assignment_role=assignment_role,
            assignment_role_label=_assignment_role_label(assignment_role),
            assignment_start_date=starts_raw,
            assignment_end_date=ends_raw,
            assignment_source_id=assignment_source_id,
            status=STATUS_ERROR,
            messages=["CSV season does not match the selected import season."],
        )

    missing_fields = [
        label
        for label, value in [
            ("first_name", first_name),
            ("last_name", last_name),
            ("email", email),
            ("team", team),
            ("division", division),
        ]
        if not value
    ]
    if missing_fields:
        return CoachImportRowPreview(
            row_number=row_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=explicit_username,
            team=team,
            division=division,
            is_active=is_active,
            notes=notes,
            source_id=source_id,
            assignment_role=assignment_role,
            assignment_role_label=_assignment_role_label(assignment_role),
            assignment_start_date=starts_raw,
            assignment_end_date=ends_raw,
            assignment_source_id=assignment_source_id,
            status=STATUS_ERROR,
            messages=[f"Missing required field(s): {', '.join(missing_fields)}."],
        )

    existing_email_user = find_existing_email_user(email)
    season_team_action, season_team_label = _season_team_preview(season=season, team=team, division=division)
    if existing_email_user:
        existing_role = _role_for_user(existing_email_user)
        if existing_role == AccountRole.COACH:
            assignment_action, assignment_label = _assignment_preview(
                user=existing_email_user,
                season=season,
                team=team,
                division=division,
                assignment_role=assignment_role,
                is_active=is_active,
            )
            return CoachImportRowPreview(
                row_number=row_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=existing_email_user.username,
                team=team,
                division=division,
                is_active=is_active,
                notes=notes,
                source_id=source_id,
                assignment_role=assignment_role,
                assignment_role_label=_assignment_role_label(assignment_role),
                assignment_start_date=starts_raw,
                assignment_end_date=ends_raw,
                assignment_source_id=assignment_source_id,
                season_team_action=season_team_action,
                season_team_label=season_team_label,
                assignment_action=assignment_action,
                assignment_label=assignment_label,
                account_action="reuse",
                account_label="Reuse Coach Account",
                password_behavior="Password unchanged",
                status=STATUS_REUSE,
                messages=["Existing coach account will be reused.", "Password unchanged."],
                existing_user_id=existing_email_user.id,
            )
        return CoachImportRowPreview(
            row_number=row_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=existing_email_user.username,
            team=team,
            division=division,
            is_active=is_active,
            notes=notes,
            source_id=source_id,
            assignment_role=assignment_role,
            assignment_role_label=_assignment_role_label(assignment_role),
            assignment_start_date=starts_raw,
            assignment_end_date=ends_raw,
            assignment_source_id=assignment_source_id,
            season_team_action=season_team_action,
            season_team_label=season_team_label,
            account_action="conflict",
            account_label="Account Role Conflict",
            password_behavior="Password unchanged",
            status=STATUS_CONFLICT,
            messages=["Email belongs to an existing non-coach account."],
            existing_user_id=existing_email_user.id,
        )

    try:
        username = validate_available_username(explicit_username) if explicit_username else ""
        generated_username = "" if username else username_for_person(first_name, last_name)
    except ValidationError as exc:
        return CoachImportRowPreview(
            row_number=row_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=explicit_username,
            team=team,
            division=division,
            is_active=is_active,
            notes=notes,
            source_id=source_id,
            assignment_role=assignment_role,
            assignment_role_label=_assignment_role_label(assignment_role),
            assignment_start_date=starts_raw,
            assignment_end_date=ends_raw,
            assignment_source_id=assignment_source_id,
            season_team_action=season_team_action,
            season_team_label=season_team_label,
            status=STATUS_CONFLICT,
            messages=list(exc.messages),
        )

    return CoachImportRowPreview(
        row_number=row_number,
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=username,
        generated_username=generated_username,
        team=team,
        division=division,
        is_active=is_active,
        notes=notes,
        source_id=source_id,
        assignment_role=assignment_role,
        assignment_role_label=_assignment_role_label(assignment_role),
        assignment_start_date=starts_raw,
        assignment_end_date=ends_raw,
        assignment_source_id=assignment_source_id,
        season_team_action=season_team_action,
        season_team_label=season_team_label,
        assignment_action="create",
        assignment_label="Create Assignment",
        account_action="create",
        account_label="Create Coach Account",
        password_behavior="Temporary password will be generated",
        status=STATUS_READY,
        messages=messages,
    )


def preview_coach_import(csv_text: str, season: Season | None = None) -> CoachImportPreview:
    """Return a non-persistent preview for a coach CSV import."""
    if season is None:
        return CoachImportPreview(rows=[], headers=[], row_errors=["Select an active season for this coach import."])
    if not season.is_active:
        return CoachImportPreview(rows=[], headers=[], row_errors=["Select an active season for this coach import."])
    try:
        headers, rows = _read_csv(csv_text)
    except ValidationError as exc:
        return CoachImportPreview(rows=[], headers=[], row_errors=list(exc.messages), season_id=season.id, season_name=season.name)

    preview_rows = []
    seen_emails = set()
    username_owner_email = {}
    for index, row in enumerate(rows, start=2):
        preview_row = _preview_row(index, row, season)
        if preview_row.email:
            if preview_row.email in seen_emails and preview_row.status == STATUS_CONFLICT:
                preview_row = replace(
                    preview_row,
                    status=STATUS_CONFLICT,
                    messages=[*preview_row.messages, "Email appears more than once in this CSV."],
                )
            seen_emails.add(preview_row.email)
        final_username = preview_row.final_username
        if preview_row.status == STATUS_READY and final_username:
            owner_email = username_owner_email.get(final_username)
            if owner_email and owner_email != preview_row.email:
                preview_row = replace(
                    preview_row,
                    status=STATUS_CONFLICT,
                    messages=[*preview_row.messages, "Username appears more than once in this CSV."],
                )
            username_owner_email[final_username] = preview_row.email
        preview_rows.append(preview_row)
    return CoachImportPreview(rows=preview_rows, headers=headers, row_errors=[], season_id=season.id, season_name=season.name)


def preview_coach_import_file(uploaded_file, season: Season | None = None) -> CoachImportPreview:
    """Read an uploaded CSV file and return a coach import preview."""
    return preview_coach_import(_decode_csv_file(uploaded_file), season=season)


def _metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
    return {
        key: value
        for key, value in {
            "team": row.team,
            "division": row.division,
            "notes": row.notes,
            "source_id": row.source_id,
            "assignment_role": row.assignment_role,
            "source": "coach_roster",
        }.items()
        if value
    }


def _profile_metadata(profile) -> dict:
    return profile.metadata if isinstance(profile.metadata, dict) else {}


@transaction.atomic
def _commit_assignment(user, row: CoachImportRowPreview, season: Season) -> tuple[str, bool]:
    season_team, team_created = get_or_create_season_team(
        season=season,
        name=row.team,
        division=row.division,
        metadata={"source": "coach_roster"},
    )
    assignment = CoachSeasonAssignment.objects.select_for_update().filter(
        user=user,
        season_team=season_team,
        assignment_role=row.assignment_role,
    ).first()
    starts_on = _parse_import_date(row.assignment_start_date)
    ends_on = _parse_import_date(row.assignment_end_date)
    updates = {"is_active": row.is_active}
    if not row.is_active:
        updates["is_primary"] = False
    if starts_on:
        updates["starts_on"] = starts_on
    if ends_on:
        updates["ends_on"] = ends_on
    if row.assignment_source_id:
        updates["source_identifier"] = row.assignment_source_id
    updates["source"] = "coach_roster"
    updates["metadata"] = {key: value for key, value in {"notes": row.notes, "source_id": row.source_id}.items() if value}
    if assignment:
        update_assignment(assignment, **updates)
        return "updated", team_created
    is_primary = row.is_active and get_primary_assignment(user, season) is None
    create_assignment(
        user=user,
        season_team=season_team,
        assignment_role=row.assignment_role,
        is_primary=is_primary,
        is_active=row.is_active,
        starts_on=starts_on,
        ends_on=ends_on,
        source="coach_roster",
        source_identifier=row.assignment_source_id,
        metadata={key: value for key, value in {"notes": row.notes, "source_id": row.source_id}.items() if value},
    )
    return "created", team_created


@transaction.atomic
def _reuse_existing_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResultRow:
    user = User.objects.select_for_update().select_related("account_profile").get(pk=row.existing_user_id)
    profile = get_or_create_account_profile(user)
    if profile.role != AccountRole.COACH:
        raise ValidationError("Existing account is not a coach.")
    metadata = {**_profile_metadata(profile), **_metadata_for_row(row)}
    profile.metadata = metadata
    profile.save(update_fields=["metadata", "updated_at"])
    user.first_name = user.first_name or row.first_name
    user.last_name = user.last_name or row.last_name
    user.email = user.email or row.email
    user.save(update_fields=["first_name", "last_name", "email"])
    assignment_action, team_created = _commit_assignment(user, row, season)
    status_message = "inactive" if not user.is_active else "active"
    return CoachImportResultRow(
        row_number=row.row_number,
        status=RESULT_REUSED,
        username=user.username,
        user_id=user.id,
        is_active=user.is_active,
        season_name=season.name,
        team=row.team,
        division=row.division,
        assignment_role_label=row.assignment_role_label,
        assignment_status=assignment_action,
        password_behavior="Password unchanged",
        messages=[
            status_message,
            "password unchanged",
            "season team created" if team_created else "season team reused",
            f"assignment {assignment_action}",
        ],
    )


@transaction.atomic
def _create_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResultRow:
    user = User.objects.create(
        username=row.final_username,
        first_name=row.first_name,
        last_name=row.last_name,
        email=row.email,
        is_active=row.is_active,
    )
    temporary_password = set_random_temporary_password(user)
    profile = set_account_role(user, AccountRole.COACH)
    profile.must_change_password = True
    profile.metadata = {**_profile_metadata(profile), **_metadata_for_row(row)}
    profile.save(update_fields=["must_change_password", "metadata", "updated_at"])
    assignment_action, team_created = _commit_assignment(user, row, season)
    status_message = "inactive" if not user.is_active else "active"
    return CoachImportResultRow(
        row_number=row.row_number,
        status=RESULT_CREATED,
        username=user.username,
        user_id=user.id,
        is_active=user.is_active,
        temporary_password=temporary_password,
        season_name=season.name,
        team=row.team,
        division=row.division,
        assignment_role_label=row.assignment_role_label,
        assignment_status=assignment_action,
        password_behavior="Temporary password generated",
        messages=[
            status_message,
            "temporary password generated",
            "season team created" if team_created else "season team reused",
            f"assignment {assignment_action}",
        ],
    )


def commit_coach_import(actor, csv_text: str, season: Season | None = None) -> CoachImportResult:
    """Create or reuse coach accounts from CSV text and return one-time passwords."""
    _validate_actor(actor)
    preview = preview_coach_import(csv_text, season=season)
    result_rows = []

    for error in preview.row_errors:
        result_rows.append(CoachImportResultRow(row_number=0, status=RESULT_ERROR, messages=[error]))

    for row in preview.rows:
        if row.status == STATUS_READY:
            try:
                existing_user = find_existing_email_user(row.email)
                if existing_user and _role_for_user(existing_user) == AccountRole.COACH:
                    result_rows.append(_reuse_existing_coach(replace(row, existing_user_id=existing_user.id), season))
                elif existing_user:
                    result_rows.append(
                        CoachImportResultRow(
                            row_number=row.row_number,
                            status=RESULT_CONFLICT,
                            username=row.final_username,
                            user_id=existing_user.id,
                            season_name=season.name,
                            team=row.team,
                            division=row.division,
                            assignment_role_label=row.assignment_role_label,
                            password_behavior="Password unchanged",
                            messages=["Email belongs to an existing non-coach account."],
                        )
                    )
                else:
                    result_rows.append(_create_coach(row, season))
            except ValidationError as exc:
                result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
        elif row.status == STATUS_REUSE:
            try:
                result_rows.append(_reuse_existing_coach(row, season))
            except ValidationError as exc:
                result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
        elif row.status == STATUS_CONFLICT:
            result_rows.append(
                CoachImportResultRow(
                    row_number=row.row_number,
                    status=RESULT_CONFLICT,
                    username=row.final_username,
                    user_id=row.existing_user_id,
                    season_name=season.name if season else "",
                    team=row.team,
                    division=row.division,
                    assignment_role_label=row.assignment_role_label,
                    password_behavior="Password unchanged",
                    messages=row.messages,
                )
            )
        else:
            result_rows.append(
                CoachImportResultRow(
                    row_number=row.row_number,
                    status=RESULT_ERROR,
                    username=row.final_username,
                    season_name=season.name if season else "",
                    team=row.team,
                    division=row.division,
                    assignment_role_label=row.assignment_role_label,
                    messages=row.messages,
                )
            )

    return CoachImportResult(rows=result_rows, season_id=season.id if season else None, season_name=season.name if season else "")
