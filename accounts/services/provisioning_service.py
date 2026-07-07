from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import AccountRole, UserPlayerLink, UserPlayerRelationship
from accounts.services.email_service import find_existing_email_user, normalize_email
from accounts.services.link_service import activate_link, link_user_to_player
from accounts.services.password_service import mark_password_change_required, set_temporary_password
from accounts.services.profile_service import get_or_create_account_profile
from accounts.services.username_service import username_for_player
from players.models import Player, PlayerImportBatch


User = get_user_model()

STATUS_CREATED = "created"
STATUS_LINKED_EXISTING = "linked_existing"
STATUS_ALREADY_LINKED = "already_linked"
STATUS_SKIPPED = "skipped"
STATUS_CONFLICT = "conflict"


@dataclass
class ProvisioningOptions:
    enabled: bool = False
    activate_users: bool = False
    email_column: str = ""


@dataclass
class ProvisioningResult:
    player_id: int | None
    row_number: int | None
    status: str
    username: str = ""
    user_id: int | None = None
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProvisioningSummary:
    enabled: bool = False
    activate_users: bool = False
    users_created: int = 0
    users_linked: int = 0
    already_linked: int = 0
    skipped: int = 0
    conflicts: int = 0
    messages: list[str] = field(default_factory=list)
    results: list[ProvisioningResult] = field(default_factory=list)

    def add_result(self, result: ProvisioningResult) -> None:
        self.results.append(result)
        if result.status == STATUS_CREATED:
            self.users_created += 1
        elif result.status == STATUS_LINKED_EXISTING:
            self.users_linked += 1
        elif result.status == STATUS_ALREADY_LINKED:
            self.already_linked += 1
        elif result.status == STATUS_SKIPPED:
            self.skipped += 1
        elif result.status == STATUS_CONFLICT:
            self.conflicts += 1
        self.messages.extend(result.messages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "activate_users": self.activate_users,
            "users_created": self.users_created,
            "users_linked": self.users_linked,
            "already_linked": self.already_linked,
            "skipped": self.skipped,
            "conflicts": self.conflicts,
            "messages": list(self.messages),
        }


def _row_message(row_number: int | None, message: str) -> str:
    return f"Row {row_number}: {message}" if row_number else message


def _validate_player(player) -> None:
    if not isinstance(player, Player):
        raise ValidationError("A valid player is required for account provisioning.")


def _validate_import_batch(import_batch) -> None:
    if import_batch is not None and not isinstance(import_batch, PlayerImportBatch):
        raise ValidationError("A valid player import batch is required.")


def _find_existing_self_link(player: Player):
    return (
        UserPlayerLink.objects.select_related("user")
        .filter(player=player, relationship=UserPlayerRelationship.SELF)
        .order_by("-is_active", "-is_primary", "id")
        .first()
    )


def _find_safe_email_user(player: Player, email: str):
    email_user = find_existing_email_user(email)
    if not email_user:
        return None, None
    link = (
        UserPlayerLink.objects.select_related("user", "player")
        .filter(user=email_user, player=player, relationship=UserPlayerRelationship.SELF)
        .order_by("-is_active", "-is_primary", "id")
        .first()
    )
    return email_user, link


def _apply_import_profile_state(user, import_batch, *, set_player_role: bool, created_from_import: bool):
    profile = get_or_create_account_profile(user)
    update_fields = []
    if set_player_role and profile.role not in {AccountRole.ADMIN, AccountRole.STAFF}:
        profile.role = AccountRole.PLAYER
        update_fields.append("role")
    if created_from_import:
        if not profile.created_from_import:
            profile.created_from_import = True
            update_fields.append("created_from_import")
        if profile.import_batch_id != getattr(import_batch, "id", None):
            profile.import_batch = import_batch
            update_fields.append("import_batch")
    if update_fields:
        profile.save(update_fields=[*update_fields, "updated_at"])
    return profile


def _ensure_active_self_link(link, import_batch):
    if link.is_active:
        return link
    link.is_primary = True
    update_fields = ["is_primary"]
    if link.created_from_import and import_batch and not link.import_batch_id:
        link.import_batch = import_batch
        update_fields.append("import_batch")
    link.save(update_fields=[*update_fields, "updated_at"])
    return activate_link(link)


def _safe_linked_user_result(player, link, import_batch, email: str, row_number: int | None) -> ProvisioningResult:
    normalized_email = normalize_email(email)
    existing_email_user = find_existing_email_user(normalized_email)
    if existing_email_user and existing_email_user.id != link.user_id:
        return ProvisioningResult(
            player_id=player.id,
            row_number=row_number,
            status=STATUS_CONFLICT,
            username=link.user.username,
            user_id=link.user_id,
            messages=[_row_message(row_number, "Email belongs to a different existing user; account not provisioned.")],
        )
    try:
        link = _ensure_active_self_link(link, import_batch)
    except ValidationError as exc:
        return ProvisioningResult(
            player_id=player.id,
            row_number=row_number,
            status=STATUS_CONFLICT,
            username=link.user.username,
            user_id=link.user_id,
            messages=[_row_message(row_number, "; ".join(exc.messages))],
        )
    if normalized_email and not link.user.email:
        link.user.email = normalized_email
        link.user.save(update_fields=["email"])
    _apply_import_profile_state(link.user, import_batch, set_player_role=False, created_from_import=False)
    return ProvisioningResult(
        player_id=player.id,
        row_number=row_number,
        status=STATUS_ALREADY_LINKED,
        username=link.user.username,
        user_id=link.user_id,
        messages=[_row_message(row_number, "Player already has a linked user account.")],
    )


@transaction.atomic
def provision_player_account(
    player,
    import_batch=None,
    actor=None,
    email="",
    activate_user=False,
    row_number=None,
) -> ProvisioningResult:
    """Create or reuse an imported player login account without exposing passwords."""
    _validate_player(player)
    _validate_import_batch(import_batch)
    normalized_email = normalize_email(email)

    existing_link = _find_existing_self_link(player)
    if existing_link:
        return _safe_linked_user_result(player, existing_link, import_batch, normalized_email, row_number)

    email_user, same_player_link = _find_safe_email_user(player, normalized_email)
    if email_user:
        if same_player_link:
            try:
                _ensure_active_self_link(same_player_link, import_batch)
            except ValidationError as exc:
                return ProvisioningResult(
                    player_id=player.id,
                    row_number=row_number,
                    status=STATUS_CONFLICT,
                    username=email_user.username,
                    user_id=email_user.id,
                    messages=[_row_message(row_number, "; ".join(exc.messages))],
                )
            _apply_import_profile_state(email_user, import_batch, set_player_role=False, created_from_import=False)
            return ProvisioningResult(
                player_id=player.id,
                row_number=row_number,
                status=STATUS_LINKED_EXISTING,
                username=email_user.username,
                user_id=email_user.id,
                messages=[_row_message(row_number, "Existing linked email user reused.")],
            )
        return ProvisioningResult(
            player_id=player.id,
            row_number=row_number,
            status=STATUS_CONFLICT,
            username=email_user.username,
            user_id=email_user.id,
            messages=[_row_message(row_number, "Email belongs to an unrelated existing user; account not provisioned.")],
        )

    if not player.birthdate:
        return ProvisioningResult(
            player_id=player.id,
            row_number=row_number,
            status=STATUS_SKIPPED,
            messages=[_row_message(row_number, "Missing birthdate; account not provisioned.")],
        )

    try:
        username = username_for_player(player)
    except ValidationError as exc:
        return ProvisioningResult(
            player_id=player.id,
            row_number=row_number,
            status=STATUS_SKIPPED,
            messages=[_row_message(row_number, "; ".join(exc.messages))],
        )

    user = User.objects.create(username=username, email=normalized_email, is_active=activate_user)
    set_temporary_password(user, player)
    profile = _apply_import_profile_state(user, import_batch, set_player_role=True, created_from_import=True)
    if not profile.must_change_password:
        mark_password_change_required(user, True)
    link_user_to_player(
        user,
        player,
        relationship=UserPlayerRelationship.SELF,
        is_primary=True,
        created_from_import=True,
        import_batch=import_batch,
    )
    return ProvisioningResult(
        player_id=player.id,
        row_number=row_number,
        status=STATUS_CREATED,
        username=user.username,
        user_id=user.id,
        messages=[_row_message(row_number, "Player account provisioned.")],
    )


def _email_for_committed_row(row: dict[str, Any], options: ProvisioningOptions) -> str:
    if not options.email_column:
        return ""
    original_row = row.get("original_row") or {}
    return original_row.get(options.email_column, "")


@transaction.atomic
def provision_accounts_for_import(
    import_batch,
    committed_rows,
    actor=None,
    options: ProvisioningOptions | None = None,
) -> ProvisioningSummary:
    """Provision accounts for committed player import rows."""
    _validate_import_batch(import_batch)
    options = options or ProvisioningOptions()
    summary = ProvisioningSummary(enabled=options.enabled, activate_users=options.activate_users)
    if not options.enabled:
        return summary

    for row in committed_rows:
        result = provision_player_account(
            row.get("player"),
            import_batch=import_batch,
            actor=actor,
            email=_email_for_committed_row(row, options),
            activate_user=options.activate_users,
            row_number=row.get("row_number"),
        )
        summary.add_result(result)
    return summary
