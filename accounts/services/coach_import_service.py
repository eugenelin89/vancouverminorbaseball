from __future__ import annotations

import csv
from dataclasses import dataclass, field, replace
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


User = get_user_model()

REQUIRED_COLUMNS = {"first_name", "last_name", "email"}
OPTIONAL_COLUMNS = {"username", "team", "division", "is_active", "notes", "source_id"}
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


@dataclass(frozen=True)
class CoachImportResultRow:
    row_number: int
    status: str
    username: str = ""
    user_id: int | None = None
    temporary_password: str = field(default="", repr=False)
    messages: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CoachImportResult:
    rows: list[CoachImportResultRow]

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
        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and "inactive" not in row.messages)

    @property
    def inactive_accounts(self) -> int:
        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED} and "inactive" in row.messages)

    @property
    def password_change_required(self) -> int:
        return sum(1 for row in self.rows if row.status in {RESULT_CREATED, RESULT_REUSED})


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


def _preview_row(row_number: int, row: dict[str, str]) -> CoachImportRowPreview:
    messages = []
    first_name = row.get("first_name", "").strip()
    last_name = row.get("last_name", "").strip()
    email = normalize_email(row.get("email", ""))
    explicit_username = row.get("username", "").strip()
    team = row.get("team", "").strip()
    division = row.get("division", "").strip()
    notes = row.get("notes", "").strip()
    source_id = row.get("source_id", "").strip()

    try:
        is_active = _parse_bool(row.get("is_active", ""), default=True)
    except ValidationError as exc:
        return CoachImportRowPreview(row_number=row_number, status=STATUS_ERROR, messages=list(exc.messages))

    missing_fields = [label for label, value in [("first_name", first_name), ("last_name", last_name), ("email", email)] if not value]
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
            status=STATUS_ERROR,
            messages=[f"Missing required field(s): {', '.join(missing_fields)}."],
        )

    existing_email_user = find_existing_email_user(email)
    if existing_email_user:
        existing_role = _role_for_user(existing_email_user)
        if existing_role == AccountRole.COACH:
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
                status=STATUS_REUSE,
                messages=["Existing coach account will be reused."],
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
        status=STATUS_READY,
        messages=messages,
    )


def preview_coach_import(csv_text: str) -> CoachImportPreview:
    """Return a non-persistent preview for a coach CSV import."""
    try:
        headers, rows = _read_csv(csv_text)
    except ValidationError as exc:
        return CoachImportPreview(rows=[], headers=[], row_errors=list(exc.messages))

    preview_rows = []
    seen_emails = set()
    seen_usernames = set()
    for index, row in enumerate(rows, start=2):
        preview_row = _preview_row(index, row)
        if preview_row.email:
            if preview_row.email in seen_emails:
                preview_row = replace(
                    preview_row,
                    status=STATUS_CONFLICT,
                    messages=[*preview_row.messages, "Email appears more than once in this CSV."],
                )
            seen_emails.add(preview_row.email)
        final_username = preview_row.final_username
        if preview_row.status == STATUS_READY and final_username:
            if final_username in seen_usernames:
                preview_row = replace(
                    preview_row,
                    status=STATUS_CONFLICT,
                    messages=[*preview_row.messages, "Username appears more than once in this CSV."],
                )
            seen_usernames.add(final_username)
        preview_rows.append(preview_row)
    return CoachImportPreview(rows=preview_rows, headers=headers, row_errors=[])


def preview_coach_import_file(uploaded_file) -> CoachImportPreview:
    """Read an uploaded CSV file and return a coach import preview."""
    return preview_coach_import(_decode_csv_file(uploaded_file))


def _metadata_for_row(row: CoachImportRowPreview) -> dict[str, str]:
    return {
        key: value
        for key, value in {
            "team": row.team,
            "division": row.division,
            "notes": row.notes,
            "source_id": row.source_id,
            "source": "coach_roster",
        }.items()
        if value
    }


@transaction.atomic
def _reuse_existing_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
    user = User.objects.select_for_update().select_related("account_profile").get(pk=row.existing_user_id)
    profile = set_account_role(user, AccountRole.COACH)
    metadata = {**profile.metadata, **_metadata_for_row(row)}
    profile.metadata = metadata
    profile.must_change_password = True
    profile.save(update_fields=["metadata", "must_change_password", "updated_at"])
    user.first_name = user.first_name or row.first_name
    user.last_name = user.last_name or row.last_name
    user.email = user.email or row.email
    user.is_active = row.is_active
    user.save(update_fields=["first_name", "last_name", "email", "is_active"])
    temporary_password = set_random_temporary_password(user)
    status_message = "inactive" if not user.is_active else "active"
    return CoachImportResultRow(
        row_number=row.row_number,
        status=RESULT_REUSED,
        username=user.username,
        user_id=user.id,
        temporary_password=temporary_password,
        messages=[status_message],
    )


@transaction.atomic
def _create_coach(row: CoachImportRowPreview) -> CoachImportResultRow:
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
    profile.metadata = {**profile.metadata, **_metadata_for_row(row)}
    profile.save(update_fields=["must_change_password", "metadata", "updated_at"])
    status_message = "inactive" if not user.is_active else "active"
    return CoachImportResultRow(
        row_number=row.row_number,
        status=RESULT_CREATED,
        username=user.username,
        user_id=user.id,
        temporary_password=temporary_password,
        messages=[status_message],
    )


def commit_coach_import(actor, csv_text: str) -> CoachImportResult:
    """Create or reuse coach accounts from CSV text and return one-time passwords."""
    _validate_actor(actor)
    preview = preview_coach_import(csv_text)
    result_rows = []

    for error in preview.row_errors:
        result_rows.append(CoachImportResultRow(row_number=0, status=RESULT_ERROR, messages=[error]))

    for row in preview.rows:
        if row.status == STATUS_READY:
            try:
                result_rows.append(_create_coach(row))
            except ValidationError as exc:
                result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
        elif row.status == STATUS_REUSE:
            try:
                result_rows.append(_reuse_existing_coach(row))
            except ValidationError as exc:
                result_rows.append(CoachImportResultRow(row_number=row.row_number, status=RESULT_ERROR, messages=list(exc.messages)))
        elif row.status == STATUS_CONFLICT:
            result_rows.append(
                CoachImportResultRow(
                    row_number=row.row_number,
                    status=RESULT_CONFLICT,
                    username=row.final_username,
                    user_id=row.existing_user_id,
                    messages=row.messages,
                )
            )
        else:
            result_rows.append(
                CoachImportResultRow(
                    row_number=row.row_number,
                    status=RESULT_ERROR,
                    username=row.final_username,
                    messages=row.messages,
                )
            )

    return CoachImportResult(rows=result_rows)
