from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import AccountRole
from accounts.services.password_service import (
    generate_birthdate_password,
    mark_password_change_required,
    set_random_temporary_password,
)
from accounts.services.profile_service import (
    get_or_create_account_profile,
    set_account_role,
)
from accounts.services.provisioning_service import (
    STATUS_CREATED,
    provision_player_account,
)
from accounts.services.role_service import role_label
from accounts.services.username_service import validate_available_username
from players.models import Player

from .contracts import CreatedAccountResult
from .shared import validate_actor_can_create_role, validate_email_available

User = get_user_model()


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
    validate_actor_can_create_role(actor, role)
    username = validate_available_username(username)
    normalized_email = validate_email_available(email)
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
    validate_actor_can_create_role(actor, role)
    if role != AccountRole.PLAYER:
        raise ValidationError(
            "Player account creation must use the player role in Phase B."
        )
    normalized_email = validate_email_available(email)
    result = provision_player_account(
        player,
        actor=actor,
        email=normalized_email,
        activate_user=bool(is_active),
        username=username,
    )
    if result.status != STATUS_CREATED or not result.user_id:
        message = (
            "; ".join(result.messages)
            if result.messages
            else "Player account could not be created."
        )
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
