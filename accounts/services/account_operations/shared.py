from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from accounts.models import AccountRole, UserPlayerLink
from accounts.services.email_service import find_existing_email_user, normalize_email
from accounts.services.permissions import (
    can_manage_accounts,
    can_manage_privileged_accounts,
)
from accounts.services.role_service import role_label
from accounts.services.username_service import validate_available_username_for_user

from .contracts import UpdatedAccountResult, UpdatedLinkResult

User = get_user_model()


def validate_actor_can_create_role(actor, role: str) -> None:
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can manage accounts.")
    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
        raise ValidationError("Only superusers can create admin accounts.")


def validate_actor_can_assign_role(actor, role: str) -> None:
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can manage accounts.")
    if role == AccountRole.ADMIN and not getattr(actor, "is_superuser", False):
        raise ValidationError("Only superusers can assign admin role.")


def validate_actor_can_manage_target(actor, user: User) -> None:
    if not can_manage_accounts(actor):
        raise ValidationError("Only staff users can manage accounts.")
    if (user.is_staff or user.is_superuser) and not can_manage_privileged_accounts(
        actor
    ):
        raise ValidationError("Only superusers can manage staff or superuser accounts.")


def validate_account_deactivation_allowed(actor, user: User) -> None:
    if actor and getattr(actor, "id", None) == user.id:
        raise ValidationError("You cannot deactivate your own account.")
    if user.is_superuser and user.is_active:
        other_active_superusers = (
            User.objects.filter(is_superuser=True, is_active=True)
            .exclude(pk=user.pk)
            .exists()
        )
        if not other_active_superusers:
            raise ValidationError(
                "You cannot deactivate the last active superuser account."
            )


def validate_email_available(email: str) -> str:
    normalized = normalize_email(email)
    if normalized and find_existing_email_user(normalized):
        raise ValidationError("Email is already in use.")
    return normalized


def validate_email_available_for_user(user: User, email: str) -> str:
    normalized = normalize_email(email)
    if normalized:
        existing_user = find_existing_email_user(normalized)
        if existing_user and existing_user.pk != user.pk:
            raise ValidationError("Email is already in use.")
    return normalized


def role_for_user(user: User) -> str:
    profile = getattr(user, "account_profile", None)
    if profile:
        return profile.role
    if user.is_superuser:
        return AccountRole.ADMIN
    if user.is_staff:
        return AccountRole.STAFF
    return AccountRole.GUEST_EVALUATOR


def updated_account_result(user: User) -> UpdatedAccountResult:
    role = role_for_user(user)
    return UpdatedAccountResult(
        user=user,
        username=user.username,
        role=role,
        role_label=role_label(role),
        is_active=user.is_active,
    )


def updated_link_result(link: UserPlayerLink) -> UpdatedLinkResult:
    return UpdatedLinkResult(
        link=link,
        user=link.user,
        player=link.player,
        relationship=link.relationship,
        is_primary=link.is_primary,
        is_active=link.is_active,
    )


def get_user_for_update(user_id: int) -> User:
    return (
        User.objects.select_for_update()
        .select_related("account_profile")
        .get(pk=user_id)
    )


def get_link_for_user(user: User, link_id: int) -> UserPlayerLink:
    return (
        UserPlayerLink.objects.select_for_update()
        .select_related("user", "player")
        .get(pk=link_id, user=user)
    )


def normalize_available_username_for_user(user: User, username: str) -> str:
    return validate_available_username_for_user(user, username)
