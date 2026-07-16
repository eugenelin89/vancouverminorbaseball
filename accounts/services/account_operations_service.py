"""Public façade for staff Account Operations services.

Keep imports through this module stable for views, forms, tests, and future callers.
Implementation details live in ``accounts.services.account_operations``.
"""

from accounts.services.account_operations.bulk import bulk_account_operation
from accounts.services.account_operations.contracts import (
    BULK_ACCOUNT_ACTIONS,
    BULK_ACTION_ACTIVATE,
    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
    BULK_ACTION_DEACTIVATE,
    BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
    AccountDetailContext,
    AccountListContext,
    AccountListRow,
    AccountOperationsDashboard,
    AccountSummaryCard,
    BulkOperationError,
    BulkOperationResult,
    CreatedAccountResult,
    LinkedPlayerRow,
    PasswordResetResult,
    UpdatedAccountResult,
    UpdatedLinkResult,
)
from accounts.services.account_operations.creation import (
    create_account_only,
    create_player_account,
)
from accounts.services.account_operations.lifecycle import (
    activate_account,
    deactivate_account,
)
from accounts.services.account_operations.links import (
    create_user_player_link,
    deactivate_user_player_link,
    reactivate_user_player_link,
    set_primary_user_player_link,
)
from accounts.services.account_operations.passwords import (
    reset_account_password,
    set_account_password_change_required,
)
from accounts.services.account_operations.read_models import (
    get_account_detail,
    get_account_list,
    get_account_operations_dashboard,
)
from accounts.services.account_operations.updates import update_account

__all__ = [
    "BULK_ACCOUNT_ACTIONS",
    "BULK_ACTION_ACTIVATE",
    "BULK_ACTION_CLEAR_PASSWORD_CHANGE",
    "BULK_ACTION_DEACTIVATE",
    "BULK_ACTION_REQUIRE_PASSWORD_CHANGE",
    "AccountDetailContext",
    "AccountListContext",
    "AccountListRow",
    "AccountOperationsDashboard",
    "AccountSummaryCard",
    "BulkOperationError",
    "BulkOperationResult",
    "CreatedAccountResult",
    "LinkedPlayerRow",
    "PasswordResetResult",
    "UpdatedAccountResult",
    "UpdatedLinkResult",
    "activate_account",
    "bulk_account_operation",
    "create_account_only",
    "create_player_account",
    "create_user_player_link",
    "deactivate_account",
    "deactivate_user_player_link",
    "get_account_detail",
    "get_account_list",
    "get_account_operations_dashboard",
    "reactivate_user_player_link",
    "reset_account_password",
    "set_account_password_change_required",
    "set_primary_user_player_link",
    "update_account",
]
