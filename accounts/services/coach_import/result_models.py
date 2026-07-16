"""Data contracts for coach import preview and commit results."""

from __future__ import annotations

from dataclasses import dataclass, field

from accounts.services.coach_import.constants import (
    RESULT_CONFLICT,
    RESULT_CREATED,
    RESULT_ERROR,
    RESULT_REUSED,
    RESULT_SKIPPED,
    STATUS_CONFLICT,
    STATUS_ERROR,
    STATUS_READY,
    STATUS_REUSE,
)
from seasons.models import CoachAssignmentRole


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
        return len(self.row_errors) + sum(
            1 for row in self.rows if row.status == STATUS_ERROR
        )

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
        return sum(
            1 for row in self.rows if row.assignment_action in {"update", "reuse"}
        )


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
        return sum(
            1
            for row in self.rows
            if row.status in {RESULT_CREATED, RESULT_REUSED} and row.is_active
        )

    @property
    def inactive_accounts(self) -> int:
        return sum(
            1
            for row in self.rows
            if row.status in {RESULT_CREATED, RESULT_REUSED} and not row.is_active
        )

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
        return sum(
            1 for row in self.rows if row.assignment_status in {"updated", "reused"}
        )
