"""Constants for the staff coach import workflow."""

from seasons.models import CoachAssignmentRole

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
