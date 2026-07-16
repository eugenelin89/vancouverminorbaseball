from __future__ import annotations

from dataclasses import dataclass, field

from django.contrib.auth import get_user_model

from accounts.models import UserPlayerLink
from accounts.services.account_query_service import AccountListFilters
from players.models import Player

User = get_user_model()


@dataclass(frozen=True)
class AccountSummaryCard:
    label: str
    value: int
    help_text: str = ""
    url: str = ""


@dataclass(frozen=True)
class AccountListRow:
    user: User
    role: str
    role_label: str
    linked_player_count: int
    detail_url: str


@dataclass(frozen=True)
class LinkedPlayerRow:
    link: UserPlayerLink
    player: object
    relationship: str
    is_primary: bool
    is_active: bool
    created_from_import: bool
    import_label: str


@dataclass(frozen=True)
class AccountOperationsDashboard:
    summary_cards: list[AccountSummaryCard]
    users_requiring_password_change: list[AccountListRow]
    unlinked_users: list[AccountListRow]
    players_without_self_link_count: int
    generated_at: object


@dataclass(frozen=True)
class AccountListContext:
    filters: AccountListFilters
    rows: list[AccountListRow]
    role_choices: tuple
    total_count: int


@dataclass(frozen=True)
class AccountDetailContext:
    user: User
    role: str
    role_label: str
    linked_players: list[LinkedPlayerRow]


@dataclass(frozen=True)
class CreatedAccountResult:
    user: User
    username: str
    temporary_password: str = field(repr=False)
    role: str
    role_label: str
    player: Player | None = None


@dataclass(frozen=True)
class UpdatedAccountResult:
    user: User
    username: str
    role: str
    role_label: str
    is_active: bool


@dataclass(frozen=True)
class UpdatedLinkResult:
    link: UserPlayerLink
    user: User
    player: Player
    relationship: str
    is_primary: bool
    is_active: bool


@dataclass(frozen=True)
class PasswordResetResult:
    user: User
    username: str
    temporary_password: str = field(repr=False)


BULK_ACTION_ACTIVATE = "activate"
BULK_ACTION_DEACTIVATE = "deactivate"
BULK_ACTION_REQUIRE_PASSWORD_CHANGE = "require_password_change"
BULK_ACTION_CLEAR_PASSWORD_CHANGE = "clear_password_change"
BULK_ACCOUNT_ACTIONS = {
    BULK_ACTION_ACTIVATE,
    BULK_ACTION_DEACTIVATE,
    BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
}


@dataclass(frozen=True)
class BulkOperationError:
    username: str
    message: str


@dataclass(frozen=True)
class BulkOperationResult:
    processed: int
    successful: int
    failed: int
    errors: list[BulkOperationError] = field(default_factory=list, repr=False)
