from __future__ import annotations

from django.db import transaction

from accounts.models import AccountRole
from accounts.services.profile_service import set_account_role

from .contracts import UpdatedAccountResult
from .shared import (
    get_user_for_update,
    normalize_available_username_for_user,
    updated_account_result,
    validate_account_deactivation_allowed,
    validate_actor_can_assign_role,
    validate_actor_can_manage_target,
    validate_email_available_for_user,
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
    validate_actor_can_assign_role(actor, role)
    user = get_user_for_update(user_id)
    if user.is_active and not bool(is_active):
        validate_account_deactivation_allowed(actor, user)
    validate_actor_can_manage_target(actor, user)
    user.username = normalize_available_username_for_user(user, username)
    user.first_name = str(first_name or "").strip()
    user.last_name = str(last_name or "").strip()
    user.email = validate_email_available_for_user(user, email)
    user.is_active = bool(is_active)
    user.save(
        update_fields=["username", "first_name", "last_name", "email", "is_active"]
    )
    set_account_role(user, role, actor=actor)
    user.refresh_from_db()
    return updated_account_result(user)
