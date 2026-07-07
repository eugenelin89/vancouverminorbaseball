def is_staff_or_admin(user) -> bool:
    """Return whether the Django user can access staff/admin account surfaces."""
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def can_manage_accounts(user) -> bool:
    return is_staff_or_admin(user)


def can_access_account_operations(user) -> bool:
    return is_staff_or_admin(user)


def can_view_account_operations_dashboard(user) -> bool:
    return can_access_account_operations(user)


def can_view_account_list(user) -> bool:
    return can_access_account_operations(user)


def can_view_account_detail(user, target_user) -> bool:
    return bool(target_user and can_access_account_operations(user))


def can_manage_privileged_accounts(user) -> bool:
    return bool(user and user.is_authenticated and user.is_superuser)


def can_view_account_profile(user, profile) -> bool:
    if is_staff_or_admin(user):
        return True
    return bool(user and user.is_authenticated and profile and profile.user_id == user.id)


def can_change_account_role(user) -> bool:
    return is_staff_or_admin(user)


def can_submit_evaluations(user) -> bool:
    """Account roles do not restrict evaluation submission in Account Management v1."""
    return bool(user and user.is_authenticated)
