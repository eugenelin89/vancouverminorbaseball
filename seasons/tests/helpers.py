from datetime import date

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountRole
from accounts.services.profile_service import (
    get_or_create_account_profile,
    set_account_role,
)
from analytics.models import (
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    EvaluationCycle,
)
from analytics.services.observation_service import (
    create_coach_assessment_observation,
    submit_observation,
)
from analytics.services.question_service import ensure_default_coach_assessment_setup
from players.models import Player
from seasons.models import (
    CoachAssignmentRole,
    CoachSeasonAssignment,
    PlayerRosterMembership,
    RosterStatus,
    Season,
    SeasonTeam,
)
from seasons.services.coach_assignment_service import (
    assignments_for_team,
    assignments_for_user,
    create_assignment,
    deactivate_assignment,
    get_primary_assignment,
    set_primary_assignment,
    update_assignment,
)
from seasons.services.membership_service import (
    create_membership,
    current_team_division,
    deactivate_membership,
    get_current_membership,
    get_primary_membership,
    memberships_for_player,
    sync_player_current_team_fields,
    transfer_player,
    update_membership,
)
from seasons.services.season_service import (
    create_season,
    deactivate_season,
    get_current_season,
    set_current_season,
)
from seasons.services.team_service import get_or_create_season_team, update_season_team

User = get_user_model()

__all__ = (
    "AccountRole",
    "CoachAssignmentRole",
    "CoachSeasonAssignment",
    "EvaluationCycle",
    "Player",
    "PlayerRosterMembership",
    "RESPONSE_TYPE_RATING_1_5",
    "RESPONSE_TYPE_TEXT",
    "RosterStatus",
    "Season",
    "SeasonTeam",
    "TestCase",
    "User",
    "ValidationError",
    "admin",
    "apps",
    "assignments_for_team",
    "assignments_for_user",
    "create_assignment",
    "create_coach_assessment_observation",
    "create_membership",
    "create_season",
    "current_team_division",
    "date",
    "deactivate_assignment",
    "deactivate_membership",
    "deactivate_season",
    "ensure_default_coach_assessment_setup",
    "get_current_membership",
    "get_current_season",
    "get_or_create_account_profile",
    "get_or_create_season_team",
    "get_primary_assignment",
    "get_primary_membership",
    "memberships_for_player",
    "reverse",
    "set_account_role",
    "set_current_season",
    "set_primary_assignment",
    "submit_observation",
    "sync_player_current_team_fields",
    "transaction",
    "transfer_player",
    "update_assignment",
    "update_membership",
    "update_season_team",
)
