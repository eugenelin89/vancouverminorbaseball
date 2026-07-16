from __future__ import annotations

from django.db import transaction

from accounts.models import UserPlayerRelationship
from accounts.services.password_service import (
    generate_birthdate_password,
    mark_password_change_required,
    set_random_temporary_password,
    set_temporary_password,
)

from .contracts import PasswordResetResult, UpdatedAccountResult
from .shared import (
    get_user_for_update,
    updated_account_result,
    validate_actor_can_manage_target,
)


def _player_for_password_reset(user):
    link = (
        user.player_links.select_related("player")
        .filter(relationship=UserPlayerRelationship.SELF, is_active=True)
        .order_by("-is_primary", "id")
        .first()
    )
    return link.player if link else None


@transaction.atomic
def reset_account_password(*, actor, user_id: int) -> PasswordResetResult:
    """Reset an existing account password and require password change on next login."""
    user = get_user_for_update(user_id)
    validate_actor_can_manage_target(actor, user)
    player = _player_for_password_reset(user)
    if player:
        temporary_password = generate_birthdate_password(player)
        set_temporary_password(user, player)
    else:
        temporary_password = set_random_temporary_password(user)
    mark_password_change_required(user, True)
    user.refresh_from_db()
    return PasswordResetResult(
        user=user, username=user.username, temporary_password=temporary_password
    )


@transaction.atomic
def set_account_password_change_required(
    *, actor, user_id: int, required: bool
) -> UpdatedAccountResult:
    """Set the password-change requirement for an existing account."""
    user = get_user_for_update(user_id)
    validate_actor_can_manage_target(actor, user)
    mark_password_change_required(user, bool(required))
    user.refresh_from_db()
    return updated_account_result(user)
