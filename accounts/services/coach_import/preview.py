"""Preview construction for staff coach imports."""

from __future__ import annotations

from dataclasses import replace

from django.core.exceptions import ValidationError

from accounts.models import AccountRole
from accounts.services.coach_import.assignment import (
    assignment_preview,
    season_team_preview,
)
from accounts.services.coach_import.constants import (
    STATUS_CONFLICT,
    STATUS_ERROR,
    STATUS_READY,
    STATUS_REUSE,
)
from accounts.services.coach_import.matching import role_for_user
from accounts.services.coach_import.parsing import (
    assignment_role_label,
    decode_csv_file,
    parse_assignment_role,
    parse_bool,
    parse_import_date,
    read_csv,
    season_matches,
)
from accounts.services.coach_import.result_models import (
    CoachImportPreview,
    CoachImportRowPreview,
)
from accounts.services.email_service import find_existing_email_user, normalize_email
from accounts.services.username_service import (
    username_for_person,
    validate_available_username,
)
from seasons.models import Season


def preview_row(
    row_number: int, row: dict[str, str], season: Season
) -> CoachImportRowPreview:
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
        is_active = parse_bool(row.get("is_active", ""), default=True)
        assignment_role = parse_assignment_role(row.get("assignment_role", ""))
        starts_on = parse_import_date(starts_raw)
        ends_on = parse_import_date(ends_raw)
    except ValidationError as exc:
        return CoachImportRowPreview(
            row_number=row_number, status=STATUS_ERROR, messages=list(exc.messages)
        )
    if starts_on and ends_on and ends_on < starts_on:
        return CoachImportRowPreview(
            row_number=row_number,
            status=STATUS_ERROR,
            messages=["Assignment end date cannot be before start date."],
        )

    season_value = row.get("season", "").strip()
    if season_value and not season_matches(season_value, season):
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
            assignment_role_label=assignment_role_label(assignment_role),
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
            assignment_role_label=assignment_role_label(assignment_role),
            assignment_start_date=starts_raw,
            assignment_end_date=ends_raw,
            assignment_source_id=assignment_source_id,
            status=STATUS_ERROR,
            messages=[f"Missing required field(s): {', '.join(missing_fields)}."],
        )

    existing_email_user = find_existing_email_user(email)
    season_team_action, season_team_label = season_team_preview(
        season=season, team=team, division=division
    )
    if existing_email_user:
        existing_role = role_for_user(existing_email_user)
        if existing_role == AccountRole.COACH:
            assignment_action, assignment_label = assignment_preview(
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
                assignment_role_label=assignment_role_label(assignment_role),
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
                messages=[
                    "Existing coach account will be reused.",
                    "Password unchanged.",
                ],
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
            assignment_role_label=assignment_role_label(assignment_role),
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
        username = (
            validate_available_username(explicit_username) if explicit_username else ""
        )
        generated_username = (
            "" if username else username_for_person(first_name, last_name)
        )
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
            assignment_role_label=assignment_role_label(assignment_role),
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
        assignment_role_label=assignment_role_label(assignment_role),
        assignment_start_date=starts_raw,
        assignment_end_date=ends_raw,
        assignment_source_id=assignment_source_id,
        season_team_action=season_team_action,
        season_team_label=season_team_label,
        assignment_action="create",
        assignment_label="Create Assignment",
        account_action="create",
        account_label="Create Coach Account",
        password_behavior="Configured default password; change required",
        status=STATUS_READY,
        messages=messages,
    )


def preview_coach_import(
    csv_text: str, season: Season | None = None
) -> CoachImportPreview:
    """Return a non-persistent preview for a coach CSV import."""
    if season is None:
        return CoachImportPreview(
            rows=[],
            headers=[],
            row_errors=["Select an active season for this coach import."],
        )
    if not season.is_active:
        return CoachImportPreview(
            rows=[],
            headers=[],
            row_errors=["Select an active season for this coach import."],
        )
    try:
        headers, rows = read_csv(csv_text)
    except ValidationError as exc:
        return CoachImportPreview(
            rows=[],
            headers=[],
            row_errors=list(exc.messages),
            season_id=season.id,
            season_name=season.name,
        )

    preview_rows = []
    seen_emails = set()
    username_owner_email = {}
    for index, row in enumerate(rows, start=2):
        row_preview = preview_row(index, row, season)
        if row_preview.email:
            if (
                row_preview.email in seen_emails
                and row_preview.status == STATUS_CONFLICT
            ):
                row_preview = replace(
                    row_preview,
                    status=STATUS_CONFLICT,
                    messages=[
                        *row_preview.messages,
                        "Email appears more than once in this CSV.",
                    ],
                )
            seen_emails.add(row_preview.email)
        final_username = row_preview.final_username
        if row_preview.status == STATUS_READY and final_username:
            owner_email = username_owner_email.get(final_username)
            if owner_email and owner_email != row_preview.email:
                row_preview = replace(
                    row_preview,
                    status=STATUS_CONFLICT,
                    messages=[
                        *row_preview.messages,
                        "Username appears more than once in this CSV.",
                    ],
                )
            username_owner_email[final_username] = row_preview.email
        preview_rows.append(row_preview)
    return CoachImportPreview(
        rows=preview_rows,
        headers=headers,
        row_errors=[],
        season_id=season.id,
        season_name=season.name,
    )


def preview_coach_import_file(
    uploaded_file, season: Season | None = None
) -> CoachImportPreview:
    """Read an uploaded CSV file and return a coach import preview."""
    return preview_coach_import(decode_csv_file(uploaded_file), season=season)
