from __future__ import annotations

from django.db import transaction

from .contracts import UpdatedAccountResult
from .shared import (
    get_user_for_update,
    updated_account_result,
    validate_account_deactivation_allowed,
    validate_actor_can_manage_target,
)


@transaction.atomic
def activate_account(*, actor, user_id: int) -> UpdatedAccountResult:
    """Activate an existing account without changing profile or link history."""
    user = get_user_for_update(user_id)
    validate_actor_can_manage_target(actor, user)
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=["is_active"])
    return updated_account_result(user)


@transaction.atomic
def deactivate_account(*, actor, user_id: int) -> UpdatedAccountResult:
    """Deactivate an existing account without deleting account data or links."""
    user = get_user_for_update(user_id)
    if user.is_active:
        validate_account_deactivation_allowed(actor, user)
        validate_actor_can_manage_target(actor, user)
        user.is_active = False
        user.save(update_fields=["is_active"])
    return updated_account_result(user)
