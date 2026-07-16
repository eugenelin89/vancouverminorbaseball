from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from accounts.services.permissions import can_manage_accounts

from .contracts import (
    BULK_ACCOUNT_ACTIONS,
    BULK_ACTION_ACTIVATE,
    BULK_ACTION_CLEAR_PASSWORD_CHANGE,
    BULK_ACTION_DEACTIVATE,
    BULK_ACTION_REQUIRE_PASSWORD_CHANGE,
    BulkOperationError,
    BulkOperationResult,
)
from .lifecycle import activate_account, deactivate_account
from .passwords import set_account_password_change_required

User = get_user_model()


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
        username = (
            User.objects.filter(pk=user_id).values_list("username", flat=True).first()
        )
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
            errors.append(
                BulkOperationError(username=username, message="Account not found.")
            )
            continue
        try:
            if action == BULK_ACTION_ACTIVATE:
                activate_account(actor=actor, user_id=user_id)
            elif action == BULK_ACTION_DEACTIVATE:
                deactivate_account(actor=actor, user_id=user_id)
            elif action == BULK_ACTION_REQUIRE_PASSWORD_CHANGE:
                set_account_password_change_required(
                    actor=actor, user_id=user_id, required=True
                )
            elif action == BULK_ACTION_CLEAR_PASSWORD_CHANGE:
                set_account_password_change_required(
                    actor=actor, user_id=user_id, required=False
                )
        except User.DoesNotExist:
            errors.append(
                BulkOperationError(username=username, message="Account not found.")
            )
        except ValidationError as exc:
            errors.append(
                BulkOperationError(username=username, message=_validation_message(exc))
            )
        else:
            successful += 1

    return BulkOperationResult(
        processed=len(clean_user_ids),
        successful=successful,
        failed=len(errors),
        errors=errors,
    )
