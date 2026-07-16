from __future__ import annotations

from django.db import transaction

from accounts.services.link_service import (
    activate_link,
    deactivate_link,
    link_user_to_player,
    set_primary_self_link,
    validate_no_active_relationship_conflict,
)
from players.models import Player

from .contracts import UpdatedLinkResult
from .shared import (
    get_link_for_user,
    get_user_for_update,
    updated_link_result,
    validate_actor_can_manage_target,
)


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
    user = get_user_for_update(user_id)
    validate_actor_can_manage_target(actor, user)
    validate_no_active_relationship_conflict(user, player, relationship)
    link = link_user_to_player(
        user, player, relationship=relationship, is_primary=is_primary
    )
    return updated_link_result(link)


@transaction.atomic
def deactivate_user_player_link(
    *, actor, user_id: int, link_id: int
) -> UpdatedLinkResult:
    """Deactivate a user/player link without deleting its history."""
    user = get_user_for_update(user_id)
    validate_actor_can_manage_target(actor, user)
    link = get_link_for_user(user, link_id)
    return updated_link_result(deactivate_link(link, actor=actor))


@transaction.atomic
def reactivate_user_player_link(
    *, actor, user_id: int, link_id: int
) -> UpdatedLinkResult:
    """Reactivate an existing inactive user/player link when constraints allow it."""
    user = get_user_for_update(user_id)
    validate_actor_can_manage_target(actor, user)
    link = get_link_for_user(user, link_id)
    return updated_link_result(activate_link(link, actor=actor))


@transaction.atomic
def set_primary_user_player_link(
    *, actor, user_id: int, link_id: int
) -> UpdatedLinkResult:
    """Set an existing self link as the active primary player link."""
    user = get_user_for_update(user_id)
    validate_actor_can_manage_target(actor, user)
    link = get_link_for_user(user, link_id)
    return updated_link_result(set_primary_self_link(link, actor=actor))
