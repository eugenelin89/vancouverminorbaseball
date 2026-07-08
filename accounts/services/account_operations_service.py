from __future__ import annotations

from dataclasses import dataclass, field

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from accounts.models import AccountRole, UserPlayerLink, UserPlayerRelationship
from accounts.services import account_query_service
from accounts.services.account_query_service import AccountListFilters
from accounts.services.email_service import find_existing_email_user, normalize_email
from accounts.services.link_service import (
    activate_link,
    deactivate_link,
    link_user_to_player,
    set_primary_self_link,
    validate_no_active_relationship_conflict,
)
from accounts.services.password_service import (
    generate_birthdate_password,
    mark_password_change_required,
    set_random_temporary_password,
    set_temporary_password,
)
from accounts.services.permissions import can_manage_accounts, can_manage_privileged_accounts
from accounts.services.profile_service import get_or_create_account_profile, set_account_role
from accounts.services.provisioning_service import STATUS_CREATED, provision_player_account
from accounts.services.role_service import role_label
from accounts.services.username_service import validate_available_username, validate_available_username_for_user
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


def _validate_actor_can_create_role(actor, role: str) -> None:
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can manage accounts.")
    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
        raise ValidationError("Only superusers can create admin accounts.")


def _validate_actor_can_assign_role(actor, role: str) -> None:
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can manage accounts.")
    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
        raise ValidationError("Only superusers can assign admin role.")


def _validate_actor_can_manage_target(actor, user: User) -> None:
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can manage accounts.")
    if (user.is_staff or user.is_superuser) and not can_manage_privileged_accounts(actor):
        raise ValidationError("Only superusers can manage staff or superuser accounts.")


def _validate_account_deactivation_allowed(actor, user: User) -> None:
    if actor and getattr(actor, "id", None) == user.id:
        raise ValidationError("You cannot deactivate your own account.")
    if user.is_superuser and user.is_active:
        other_active_superusers = User.objects.filter(is_superuser=True, is_active=True).exclude(pk=user.pk).exists()
        if not other_active_superusers:
            raise ValidationError("You cannot deactivate the last active superuser account.")


def _validate_email_available(email: str) -> str:
    normalized = normalize_email(email)
    if normalized and find_existing_email_user(normalized):
        raise ValidationError("Email is already in use.")
    return normalized


def _validate_email_available_for_user(user: User, email: str) -> str:
    normalized = normalize_email(email)
    if normalized:
        existing_user = find_existing_email_user(normalized)
        if existing_user and existing_user.pk != user.pk:
            raise ValidationError("Email is already in use.")
    return normalized


def _role_for_user(user: User) -> str:
    profile = getattr(user, "account_profile", None)
    if profile:
        return profile.role
    if user.is_superuser:
        return AccountRole.ADMIN
    if user.is_staff:
        return AccountRole.STAFF
    return AccountRole.GUEST_EVALUATOR


def _list_row(user: User) -> AccountListRow:
    role = _role_for_user(user)
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


def _linked_player_row(link: UserPlayerLink) -> LinkedPlayerRow:
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


def _updated_account_result(user: User) -> UpdatedAccountResult:
    role = _role_for_user(user)
    return UpdatedAccountResult(
        user=user,
        username=user.username,
        role=role,
        role_label=role_label(role),
        is_active=user.is_active,
    )


def _updated_link_result(link: UserPlayerLink) -> UpdatedLinkResult:
    return UpdatedLinkResult(
        link=link,
        user=link.user,
        player=link.player,
        relationship=link.relationship,
        is_primary=link.is_primary,
        is_active=link.is_active,
    )


def _get_user_for_update(user_id: int) -> User:
    return User.objects.select_for_update().select_related("account_profile").get(pk=user_id)


def _get_link_for_user(user: User, link_id: int) -> UserPlayerLink:
    return UserPlayerLink.objects.select_for_update().select_related("user", "player").get(pk=link_id, user=user)


def _player_for_password_reset(user: User) -> Player | None:
    link = (
        UserPlayerLink.objects.select_related("player")
        .filter(user=user, relationship=UserPlayerRelationship.SELF, is_active=True)
        .order_by("-is_primary", "id")
        .first()
    )
    return link.player if link else None


def get_account_operations_dashboard() -> AccountOperationsDashboard:
    """Return the read-only Account Operations dashboard context."""
    users = User.objects.select_related("account_profile")
    total_accounts = users.count()
    active_accounts = users.filter(is_active=True).count()
    inactive_accounts = users.filter(is_active=False).count()
    imported_accounts = users.filter(account_profile__created_from_import=True).count()
    password_change_accounts = users.filter(account_profile__must_change_password=True).count()
    unlinked_users_count = account_query_service.filter_account_users(
        AccountListFilters(linked_status="unlinked")
    ).count()
    players_without_self_link_count = account_query_service.count_players_without_self_link()

    summary_cards = [
        AccountSummaryCard("Total accounts", total_accounts, "All Django user accounts.", reverse("accounts:user-list")),
        AccountSummaryCard("Active accounts", active_accounts, "Accounts that can authenticate.", reverse("accounts:user-list") + "?active=yes"),
        AccountSummaryCard("Inactive accounts", inactive_accounts, "Accounts blocked from login.", reverse("accounts:user-list") + "?active=no"),
        AccountSummaryCard("Imported accounts", imported_accounts, "Accounts created from player imports.", reverse("accounts:user-list") + "?imported=yes"),
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
        _list_row(user)
        for user in account_query_service.filter_account_users(AccountListFilters(must_change_password="yes"))[:10]
    ]
    unlinked_rows = [
        _list_row(user)
        for user in account_query_service.filter_account_users(AccountListFilters(linked_status="unlinked"))[:10]
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
    rows = [_list_row(user) for user in queryset]
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
    role = _role_for_user(user)
    return AccountDetailContext(
        user=user,
        role=role,
        role_label=role_label(role),
        linked_players=[_linked_player_row(link) for link in links],
    )


@transaction.atomic
def update_account(
    *,
    actor,
    user_id: int,
    username: str,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
    role: str = AccountRole.GUEST_EVALUATOR,
    is_active: bool = True,
) -> UpdatedAccountResult:
    """Update lifecycle and profile fields for an existing account."""
    _validate_actor_can_assign_role(actor, role)
    user = _get_user_for_update(user_id)
    if user.is_active and not bool(is_active):
        _validate_account_deactivation_allowed(actor, user)
    _validate_actor_can_manage_target(actor, user)
    user.username = validate_available_username_for_user(user, username)
    user.first_name = str(first_name or "").strip()
    user.last_name = str(last_name or "").strip()
    user.email = _validate_email_available_for_user(user, email)
    user.is_active = bool(is_active)
    user.save(update_fields=["username", "first_name", "last_name", "email", "is_active"])
    set_account_role(user, role, actor=actor)
    user.refresh_from_db()
    return _updated_account_result(user)


@transaction.atomic
def activate_account(*, actor, user_id: int) -> UpdatedAccountResult:
    """Activate an existing account without changing profile or link history."""
    user = _get_user_for_update(user_id)
    _validate_actor_can_manage_target(actor, user)
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=["is_active"])
    return _updated_account_result(user)


@transaction.atomic
def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
    """Deactivate an existing account without deleting account data or links."""
    user = _get_user_for_update(user_id)
    if user.is_active:
        _validate_account_deactivation_allowed(actor, user)
        _validate_actor_can_manage_target(actor, user)
        user.is_active = False
        user.save(update_fields=["is_active"])
    return _updated_account_result(user)


@transaction.atomic
def create_user_player_link(
    *,
    actor,
    user_id: int,
    player: Player,
    relationship: str,
    is_primary: bool = False,
) -> UpdatedLinkResult:
    """Create an active user/player link through the account operations workflow."""
    user = _get_user_for_update(user_id)
    _validate_actor_can_manage_target(actor, user)
    validate_no_active_relationship_conflict(user, player, relationship)
    link = link_user_to_player(user, player, relationship=relationship, is_primary=is_primary)
    return _updated_link_result(link)


@transaction.atomic
def deactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
    """Deactivate a user/player link without deleting its history."""
    user = _get_user_for_update(user_id)
    _validate_actor_can_manage_target(actor, user)
    link = _get_link_for_user(user, link_id)
    return _updated_link_result(deactivate_link(link, actor=actor))


@transaction.atomic
def reactivate_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
    """Reactivate an existing inactive user/player link when constraints allow it."""
    user = _get_user_for_update(user_id)
    _validate_actor_can_manage_target(actor, user)
    link = _get_link_for_user(user, link_id)
    return _updated_link_result(activate_link(link, actor=actor))


@transaction.atomic
def set_primary_user_player_link(*, actor, user_id: int, link_id: int) -> UpdatedLinkResult:
    """Set an existing self link as the active primary player link."""
    user = _get_user_for_update(user_id)
    _validate_actor_can_manage_target(actor, user)
    link = _get_link_for_user(user, link_id)
    return _updated_link_result(set_primary_self_link(link, actor=actor))


@transaction.atomic
def reset_account_password(*, actor, user_id: int) -> PasswordResetResult:
    """Reset an existing account password and require password change on next login."""
    user = _get_user_for_update(user_id)
    _validate_actor_can_manage_target(actor, user)
    player = _player_for_password_reset(user)
    if player:
        temporary_password = generate_birthdate_password(player)
        set_temporary_password(user, player)
    else:
        temporary_password = set_random_temporary_password(user)
    mark_password_change_required(user, True)
    user.refresh_from_db()
    return PasswordResetResult(user=user, username=user.username, temporary_password=temporary_password)


@transaction.atomic
def set_account_password_change_required(*, actor, user_id: int, required: bool) -> UpdatedAccountResult:
    """Set the password-change requirement for an existing account."""
    user = _get_user_for_update(user_id)
    _validate_actor_can_manage_target(actor, user)
    mark_password_change_required(user, bool(required))
    user.refresh_from_db()
    return _updated_account_result(user)


def _clean_bulk_user_ids(user_ids):
    clean_ids = []
    seen = set()
    for raw_user_id in user_ids or []:
        raw_value = str(raw_user_id or "").strip()
        if not raw_value or raw_value in seen:
            continue
        seen.add(raw_value)
        try:
            clean_ids.append(int(raw_value))
        except (TypeError, ValueError):
            clean_ids.append(raw_value)
    return clean_ids


def _bulk_error_username(user_id) -> str:
    if isinstance(user_id, int):
        username = User.objects.filter(pk=user_id).values_list("username", flat=True).first()
        if username:
            return username
    return "Unknown account"


def _validation_message(exc: ValidationError) -> str:
    if hasattr(exc, "messages"):
        return "; ".join(exc.messages)
    return str(exc)


def bulk_account_operation(*, actor, action: str, user_ids) -> BulkOperationResult:
    """Apply a safe account operation to selected users and collect per-account failures."""
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can manage accounts.")
    if action not in BULK_ACCOUNT_ACTIONS:
        raise ValidationError("Unsupported bulk action.")

    clean_user_ids = _clean_bulk_user_ids(user_ids)
    if not clean_user_ids:
        raise ValidationError("Select at least one account.")

    successful = 0
    errors = []
    for user_id in clean_user_ids:
        username = _bulk_error_username(user_id)
        if not isinstance(user_id, int):
            errors.append(BulkOperationError(username=username, message="Account not found."))
            continue
        try:
            if action == BULK_ACTION_ACTIVATE:
                activate_account(actor=actor, user_id=user_id)
            elif action == BULK_ACTION_DEACTIVATE:
                deactivate_account(actor=actor, user_id=user_id)
            elif action == BULK_ACTION_REQUIRE_PASSWORD_CHANGE:
                set_account_password_change_required(actor=actor, user_id=user_id, required=True)
            elif action == BULK_ACTION_CLEAR_PASSWORD_CHANGE:
                set_account_password_change_required(actor=actor, user_id=user_id, required=False)
        except User.DoesNotExist:
            errors.append(BulkOperationError(username=username, message="Account not found."))
        except ValidationError as exc:
            errors.append(BulkOperationError(username=username, message=_validation_message(exc)))
        else:
            successful += 1

    return BulkOperationResult(
        processed=len(clean_user_ids),
        successful=successful,
        failed=len(errors),
        errors=errors,
    )


@transaction.atomic
def create_account_only(
    *,
    actor,
    username: str,
    first_name: str = "",
    last_name: str = "",
    email: str = "",
    role: str = AccountRole.GUEST_EVALUATOR,
    is_active: bool = True,
) -> CreatedAccountResult:
    """Create a login account without creating or linking a player."""
    _validate_actor_can_create_role(actor, role)
    username = validate_available_username(username)
    normalized_email = _validate_email_available(email)
    user = User.objects.create(
        username=username,
        first_name=str(first_name or "").strip(),
        last_name=str(last_name or "").strip(),
        email=normalized_email,
        is_active=bool(is_active),
    )
    temporary_password = set_random_temporary_password(user)
    profile = get_or_create_account_profile(user)
    if profile.created_from_import or profile.import_batch_id:
        raise ValidationError("Manual accounts cannot use import provenance.")
    set_account_role(user, role, actor=actor)
    mark_password_change_required(user, True)
    user.refresh_from_db()
    return CreatedAccountResult(
        user=user,
        username=user.username,
        temporary_password=temporary_password,
        role=role,
        role_label=role_label(role),
    )


@transaction.atomic
def create_player_account(
    *,
    actor,
    player,
    username: str = "",
    email: str = "",
    role: str = AccountRole.PLAYER,
    is_active: bool = True,
) -> CreatedAccountResult:
    """Create a login account for an existing canonical player."""
    if not isinstance(player, Player):
        raise ValidationError("A valid existing player is required.")
    _validate_actor_can_create_role(actor, role)
    if role != AccountRole.PLAYER:
        raise ValidationError("Player account creation must use the player role in Phase B.")
    normalized_email = _validate_email_available(email)
    result = provision_player_account(
        player,
        actor=actor,
        email=normalized_email,
        activate_user=bool(is_active),
        username=username,
    )
    if result.status != STATUS_CREATED or not result.user_id:
        message = "; ".join(result.messages) if result.messages else "Player account could not be created."
        raise ValidationError(message)
    user = User.objects.get(pk=result.user_id)
    temporary_password = generate_birthdate_password(player)
    return CreatedAccountResult(
        user=user,
        username=user.username,
        temporary_password=temporary_password,
        role=role,
        role_label=role_label(role),
        player=player,
    )
