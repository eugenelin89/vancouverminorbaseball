"""Commit orchestration for staff coach imports."""

from __future__ import annotations

from dataclasses import replace

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import AccountRole
from accounts.services.coach_import.assignment import (
    commit_assignment,
    metadata_for_row,
    profile_metadata,
)
from accounts.services.coach_import.constants import (
    RESULT_CONFLICT,
    RESULT_CREATED,
    RESULT_ERROR,
    RESULT_REUSED,
    STATUS_CONFLICT,
    STATUS_READY,
    STATUS_REUSE,
)
from accounts.services.coach_import.matching import role_for_user
from accounts.services.coach_import.preview import preview_coach_import
from accounts.services.coach_import.result_models import (
    CoachImportResult,
    CoachImportResultRow,
    CoachImportRowPreview,
)
from accounts.services.email_service import find_existing_email_user
from accounts.services.password_service import set_random_temporary_password
from accounts.services.permissions import can_manage_accounts
from accounts.services.profile_service import (
    get_or_create_account_profile,
    set_account_role,
)
from seasons.models import Season

User = get_user_model()


def validate_actor(actor) -> None:
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can import coaches.")


@transaction.atomic
def reuse_existing_coach(
    row: CoachImportRowPreview, season: Season
) -> CoachImportResultRow:
    user = (
        User.objects.select_for_update()
        .select_related("account_profile")
        .get(pk=row.existing_user_id)
    )
    profile = get_or_create_account_profile(user)
    if profile.role != AccountRole.COACH:
        raise ValidationError("Existing account is not a coach.")
    metadata = {**profile_metadata(profile), **metadata_for_row(row)}
    profile.metadata = metadata
    profile.save(update_fields=["metadata", "updated_at"])
    user.first_name = user.first_name or row.first_name
    user.last_name = user.last_name or row.last_name
    user.email = user.email or row.email
    user.save(update_fields=["first_name", "last_name", "email"])
    assignment_action, team_created = commit_assignment(user, row, season)
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
def create_coach(row: CoachImportRowPreview, season: Season) -> CoachImportResultRow:
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
    profile.metadata = {**profile_metadata(profile), **metadata_for_row(row)}
    profile.save(update_fields=["must_change_password", "metadata", "updated_at"])
    assignment_action, team_created = commit_assignment(user, row, season)
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


def commit_coach_import(
    actor, csv_text: str, season: Season | None = None
) -> CoachImportResult:
    """Create or reuse coach accounts from CSV text and return one-time passwords."""
    validate_actor(actor)
    preview = preview_coach_import(csv_text, season=season)
    result_rows = []

    for error in preview.row_errors:
        result_rows.append(
            CoachImportResultRow(row_number=0, status=RESULT_ERROR, messages=[error])
        )

    for row in preview.rows:
        if row.status == STATUS_READY:
            try:
                existing_user = find_existing_email_user(row.email)
                if existing_user and role_for_user(existing_user) == AccountRole.COACH:
                    result_rows.append(
                        reuse_existing_coach(
                            replace(row, existing_user_id=existing_user.id), season
                        )
                    )
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
                            messages=[
                                "Email belongs to an existing non-coach account."
                            ],
                        )
                    )
                else:
                    result_rows.append(create_coach(row, season))
            except ValidationError as exc:
                result_rows.append(
                    CoachImportResultRow(
                        row_number=row.row_number,
                        status=RESULT_ERROR,
                        messages=list(exc.messages),
                    )
                )
        elif row.status == STATUS_REUSE:
            try:
                result_rows.append(reuse_existing_coach(row, season))
            except ValidationError as exc:
                result_rows.append(
                    CoachImportResultRow(
                        row_number=row.row_number,
                        status=RESULT_ERROR,
                        messages=list(exc.messages),
                    )
                )
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

    return CoachImportResult(
        rows=result_rows,
        season_id=season.id if season else None,
        season_name=season.name if season else "",
    )
