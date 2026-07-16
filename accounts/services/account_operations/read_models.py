from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from accounts.models import AccountRole, UserPlayerLink
from accounts.services import account_query_service
from accounts.services.account_query_service import AccountListFilters
from accounts.services.role_service import role_label

from .contracts import (
    AccountDetailContext,
    AccountListContext,
    AccountListRow,
    AccountOperationsDashboard,
    AccountSummaryCard,
    LinkedPlayerRow,
)
from .shared import role_for_user

User = get_user_model()


def list_row(user: User) -> AccountListRow:
    role = role_for_user(user)
    linked_count = getattr(user, "active_player_link_count", None)
    if linked_count is None:
        linked_count = user.player_links.filter(is_active=True).count()
    return AccountListRow(
        user=user,
        role=role,
        role_label=role_label(role),
        linked_player_count=linked_count,
        detail_url=reverse("accounts:user-detail", kwargs={"user_id": user.id}),
    )


def linked_player_row(link: UserPlayerLink) -> LinkedPlayerRow:
    import_label = ""
    if link.import_batch_id:
        import_label = link.import_batch.original_filename
    return LinkedPlayerRow(
        link=link,
        player=link.player,
        relationship=link.get_relationship_display(),
        is_primary=link.is_primary,
        is_active=link.is_active,
        created_from_import=link.created_from_import,
        import_label=import_label,
    )


def get_account_operations_dashboard() -> AccountOperationsDashboard:
    """Return the read-only Account Operations dashboard context."""
    users = User.objects.select_related("account_profile")
    total_accounts = users.count()
    active_accounts = users.filter(is_active=True).count()
    inactive_accounts = users.filter(is_active=False).count()
    imported_accounts = users.filter(account_profile__created_from_import=True).count()
    password_change_accounts = users.filter(
        account_profile__must_change_password=True
    ).count()
    unlinked_users_count = account_query_service.filter_account_users(
        AccountListFilters(linked_status="unlinked")
    ).count()
    players_without_self_link_count = (
        account_query_service.count_players_without_self_link()
    )

    summary_cards = [
        AccountSummaryCard(
            "Total accounts",
            total_accounts,
            "All Django user accounts.",
            reverse("accounts:user-list"),
        ),
        AccountSummaryCard(
            "Active accounts",
            active_accounts,
            "Accounts that can authenticate.",
            reverse("accounts:user-list") + "?active=yes",
        ),
        AccountSummaryCard(
            "Inactive accounts",
            inactive_accounts,
            "Accounts blocked from login.",
            reverse("accounts:user-list") + "?active=no",
        ),
        AccountSummaryCard(
            "Imported accounts",
            imported_accounts,
            "Accounts created from player imports.",
            reverse("accounts:user-list") + "?imported=yes",
        ),
        AccountSummaryCard(
            "Password change required",
            password_change_accounts,
            "Users who must change a temporary password.",
            reverse("accounts:user-list") + "?must_change_password=yes",
        ),
        AccountSummaryCard(
            "Users without player links",
            unlinked_users_count,
            "Accounts with no active player links.",
            reverse("accounts:user-list") + "?linked=unlinked",
        ),
        AccountSummaryCard(
            "Players without self-linked accounts",
            players_without_self_link_count,
            "Active players without an active self-linked user account.",
        ),
    ]

    password_rows = [
        list_row(user)
        for user in account_query_service.filter_account_users(
            AccountListFilters(must_change_password="yes")
        )[:10]
    ]
    unlinked_rows = [
        list_row(user)
        for user in account_query_service.filter_account_users(
            AccountListFilters(linked_status="unlinked")
        )[:10]
    ]
    return AccountOperationsDashboard(
        summary_cards=summary_cards,
        users_requiring_password_change=password_rows,
        unlinked_users=unlinked_rows,
        players_without_self_link_count=players_without_self_link_count,
        generated_at=timezone.now(),
    )


def get_account_list(filters: AccountListFilters) -> AccountListContext:
    """Return read-only account list rows for staff account operations."""
    queryset = account_query_service.filter_account_users(filters)
    rows = [list_row(user) for user in queryset]
    return AccountListContext(
        filters=filters,
        rows=rows,
        role_choices=AccountRole.choices,
        total_count=len(rows),
    )


def get_account_detail(user_id: int) -> AccountDetailContext:
    """Return read-only detail context for one account."""
    user = account_query_service.get_account_user(user_id)
    links = user.player_links.select_related("player", "import_batch").order_by(
        "-is_active",
        "relationship",
        "player__last_name",
        "player__first_name",
        "id",
    )
    role = role_for_user(user)
    return AccountDetailContext(
        user=user,
        role=role,
        role_label=role_label(role),
        linked_players=[linked_player_row(link) for link in links],
    )
