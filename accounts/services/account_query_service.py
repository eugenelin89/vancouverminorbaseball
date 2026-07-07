from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Q

from accounts.models import AccountRole, UserPlayerLink, UserPlayerRelationship
from players.models import Player


User = get_user_model()


@dataclass(frozen=True)
class AccountListFilters:
    search: str = ""
    role: str = ""
    active_status: str = ""
    staff_status: str = ""
    superuser_status: str = ""
    imported_status: str = ""
    must_change_password: str = ""
    linked_status: str = ""


def parse_account_list_filters(params) -> AccountListFilters:
    """Parse account list GET parameters into normalized filter values."""
    return AccountListFilters(
        search=str(params.get("q", "") or "").strip(),
        role=str(params.get("role", "") or "").strip(),
        active_status=str(params.get("active", "") or "").strip(),
        staff_status=str(params.get("staff", "") or "").strip(),
        superuser_status=str(params.get("superuser", "") or "").strip(),
        imported_status=str(params.get("imported", "") or "").strip(),
        must_change_password=str(params.get("must_change_password", "") or "").strip(),
        linked_status=str(params.get("linked", "") or "").strip(),
    )


def _truthy_filter_value(value: str) -> bool | None:
    if value in {"yes", "true", "1"}:
        return True
    if value in {"no", "false", "0"}:
        return False
    return None


def account_user_queryset():
    """Return the base queryset for account operation user lists."""
    active_link = UserPlayerLink.objects.filter(user=OuterRef("pk"), is_active=True)
    return (
        User.objects.select_related("account_profile", "account_profile__import_batch")
        .prefetch_related("player_links__player", "player_links__import_batch")
        .annotate(
            active_player_link_count=Count("player_links", filter=Q(player_links__is_active=True), distinct=True),
            has_active_player_link=Exists(active_link),
        )
        .order_by("username", "id")
    )


def filter_account_users(filters: AccountListFilters):
    """Apply account operation search and filters to users."""
    queryset = account_user_queryset()

    if filters.search:
        queryset = queryset.filter(
            Q(username__icontains=filters.search)
            | Q(email__icontains=filters.search)
            | Q(first_name__icontains=filters.search)
            | Q(last_name__icontains=filters.search)
        )

    if filters.role in {choice.value for choice in AccountRole}:
        queryset = queryset.filter(account_profile__role=filters.role)

    active = _truthy_filter_value(filters.active_status)
    if active is not None:
        queryset = queryset.filter(is_active=active)

    staff = _truthy_filter_value(filters.staff_status)
    if staff is not None:
        queryset = queryset.filter(is_staff=staff)

    superuser = _truthy_filter_value(filters.superuser_status)
    if superuser is not None:
        queryset = queryset.filter(is_superuser=superuser)

    imported = _truthy_filter_value(filters.imported_status)
    if imported is not None:
        queryset = queryset.filter(account_profile__created_from_import=imported)

    must_change = _truthy_filter_value(filters.must_change_password)
    if must_change is not None:
        queryset = queryset.filter(account_profile__must_change_password=must_change)

    if filters.linked_status == "linked":
        queryset = queryset.filter(has_active_player_link=True)
    elif filters.linked_status == "unlinked":
        queryset = queryset.filter(has_active_player_link=False)

    return queryset


def get_account_user(user_id: int):
    """Return one user with account-operation related data loaded."""
    return account_user_queryset().get(pk=user_id)


def count_players_without_self_link() -> int:
    """Return active players without an active primary self-linked user account."""
    self_link = UserPlayerLink.objects.filter(
        player=OuterRef("pk"),
        relationship=UserPlayerRelationship.SELF,
        is_active=True,
    )
    return Player.objects.filter(is_active=True).annotate(has_self_link=Exists(self_link)).filter(has_self_link=False).count()
