"""Public façade for the staff coach import workflow.

Implementation lives in ``accounts.services.coach_import`` modules so callers
can keep using the stable coach-import service API while internals stay focused.
"""

from accounts.services.coach_import.commit import User, commit_coach_import
from accounts.services.coach_import.constants import (
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
    RESULT_CONFLICT,
    RESULT_CREATED,
    RESULT_ERROR,
    RESULT_REUSED,
    RESULT_SKIPPED,
    ROLE_ALIASES,
    STATUS_CONFLICT,
    STATUS_ERROR,
    STATUS_READY,
    STATUS_REUSE,
    SUPPORTED_COLUMNS,
)
from accounts.services.coach_import.preview import (
    preview_coach_import,
    preview_coach_import_file,
)
from accounts.services.coach_import.result_models import (
    CoachImportPreview,
    CoachImportResult,
    CoachImportResultRow,
    CoachImportRowPreview,
)

__all__ = [
    "CoachImportPreview",
    "CoachImportResult",
    "CoachImportResultRow",
    "CoachImportRowPreview",
    "OPTIONAL_COLUMNS",
    "REQUIRED_COLUMNS",
    "RESULT_CONFLICT",
    "RESULT_CREATED",
    "RESULT_ERROR",
    "RESULT_REUSED",
    "RESULT_SKIPPED",
    "ROLE_ALIASES",
    "STATUS_CONFLICT",
    "STATUS_ERROR",
    "STATUS_READY",
    "STATUS_REUSE",
    "SUPPORTED_COLUMNS",
    "User",
    "commit_coach_import",
    "preview_coach_import",
    "preview_coach_import_file",
]
