from django.conf import settings
from django.contrib import admin
from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import (
    AccountProfile,
    AccountRole,
    UserPlayerLink,
    UserPlayerRelationship,
)
from accounts.services.account_operations_service import (
    activate_account,
    bulk_account_operation,
    create_account_only,
    create_player_account,
    create_user_player_link,
    deactivate_account,
    deactivate_user_player_link,
    get_account_detail,
    get_account_list,
    get_account_operations_dashboard,
    reactivate_user_player_link,
    reset_account_password,
    set_primary_user_player_link,
    update_account,
)
from accounts.services.account_query_service import (
    AccountListFilters,
    count_players_without_self_link,
    filter_account_users,
)
from accounts.services.auth_redirect_service import (
    ACCOUNT_LOGIN_PATH,
    ACCOUNT_LOGOUT_PATH,
    ACCOUNT_PASSWORD_PATH,
    ACCOUNT_PROFILE_PATH,
    ANALYTICS_HOME_PATH,
    is_password_change_allowed_path,
    landing_url_for_user,
    should_force_password_change,
)
from accounts.services.coach_import_service import (
    RESULT_CONFLICT,
    RESULT_CREATED,
    RESULT_REUSED,
    commit_coach_import,
    preview_coach_import,
)
from accounts.services.email_service import (
    emails_equal,
    find_existing_email_user,
    normalize_email,
)
from accounts.services.link_service import (
    activate_link,
    deactivate_link,
    get_players_for_user,
    get_primary_player,
    get_primary_user,
    get_users_for_player,
    is_player_self,
    link_user_to_player,
    set_primary_self_link,
    unlink_user_from_player,
)
from accounts.services.password_service import (
    generate_birthdate_password,
    generate_random_temporary_password,
    mark_password_change_required,
    set_temporary_password,
)
from accounts.services.permissions import (
    can_access_account_operations,
    can_change_account_role,
    can_manage_accounts,
    can_manage_privileged_accounts,
    can_submit_evaluations,
    can_view_account_detail,
    can_view_account_list,
    can_view_account_operations_dashboard,
    can_view_account_profile,
)
from accounts.services.profile_service import (
    get_account_role,
    get_or_create_account_profile,
    set_account_role,
)
from accounts.services.provisioning_service import (
    STATUS_ALREADY_LINKED,
    STATUS_CONFLICT,
    STATUS_CREATED,
    STATUS_SKIPPED,
    ProvisioningOptions,
    ProvisioningSummary,
    provision_accounts_for_import,
    provision_player_account,
)
from accounts.services.role_service import (
    default_role_for_user,
    role_for_user,
    role_label,
    validate_role,
)
from accounts.services.username_service import (
    base_username_for_person,
    base_username_for_player,
    normalize_username_part,
    username_for_person,
    username_for_player,
    validate_available_username,
    validate_available_username_for_user,
)
from analytics.services.permissions import can_submit_coach_assessment
from players.models import Player, PlayerImportBatch
from seasons.models import CoachAssignmentRole, CoachSeasonAssignment, SeasonTeam
from seasons.services.season_service import create_season

User = get_user_model()

__all__ = (
    "ACCOUNT_LOGIN_PATH",
    "ACCOUNT_LOGOUT_PATH",
    "ACCOUNT_PASSWORD_PATH",
    "ACCOUNT_PROFILE_PATH",
    "ANALYTICS_HOME_PATH",
    "AccountListFilters",
    "AccountProfile",
    "AccountRole",
    "CoachAssignmentRole",
    "CoachSeasonAssignment",
    "IntegrityError",
    "Player",
    "PlayerImportBatch",
    "ProvisioningOptions",
    "ProvisioningSummary",
    "RESULT_CONFLICT",
    "RESULT_CREATED",
    "RESULT_REUSED",
    "SESSION_KEY",
    "STATUS_ALREADY_LINKED",
    "STATUS_CONFLICT",
    "STATUS_CREATED",
    "STATUS_SKIPPED",
    "SeasonTeam",
    "SimpleUploadedFile",
    "TestCase",
    "User",
    "UserPlayerLink",
    "UserPlayerRelationship",
    "ValidationError",
    "activate_account",
    "activate_link",
    "admin",
    "base_username_for_person",
    "base_username_for_player",
    "bulk_account_operation",
    "can_access_account_operations",
    "can_change_account_role",
    "can_manage_accounts",
    "can_manage_privileged_accounts",
    "can_submit_coach_assessment",
    "can_submit_evaluations",
    "can_view_account_detail",
    "can_view_account_list",
    "can_view_account_operations_dashboard",
    "can_view_account_profile",
    "commit_coach_import",
    "count_players_without_self_link",
    "create_account_only",
    "create_player_account",
    "create_season",
    "create_user_player_link",
    "deactivate_account",
    "deactivate_link",
    "deactivate_user_player_link",
    "default_role_for_user",
    "emails_equal",
    "filter_account_users",
    "find_existing_email_user",
    "generate_birthdate_password",
    "generate_random_temporary_password",
    "get_account_detail",
    "get_account_list",
    "get_account_operations_dashboard",
    "get_account_role",
    "get_messages",
    "get_or_create_account_profile",
    "get_players_for_user",
    "get_primary_player",
    "get_primary_user",
    "get_users_for_player",
    "is_password_change_allowed_path",
    "is_player_self",
    "landing_url_for_user",
    "link_user_to_player",
    "mark_password_change_required",
    "normalize_email",
    "normalize_username_part",
    "preview_coach_import",
    "provision_accounts_for_import",
    "provision_player_account",
    "reactivate_user_player_link",
    "reset_account_password",
    "reverse",
    "role_for_user",
    "role_label",
    "set_account_role",
    "set_primary_self_link",
    "set_primary_user_player_link",
    "set_temporary_password",
    "settings",
    "should_force_password_change",
    "transaction",
    "unlink_user_from_player",
    "update_account",
    "username_for_person",
    "username_for_player",
    "validate_available_username",
    "validate_available_username_for_user",
    "validate_role",
)
