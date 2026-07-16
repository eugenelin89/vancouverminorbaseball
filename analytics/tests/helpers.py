from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import AccountRole, UserPlayerRelationship
from accounts.services.link_service import (
    activate_link,
    deactivate_link,
    link_user_to_player,
)
from accounts.services.profile_service import set_account_role
from analytics.assessment_forms import CoachAssessmentForm
from analytics.models import (
    EVALUATION_PERSPECTIVE_COACH,
    EVALUATION_PERSPECTIVE_GUEST,
    EVALUATION_PERSPECTIVE_PEER,
    EVALUATION_PERSPECTIVE_SELF,
    EVALUATION_PERSPECTIVE_STAFF,
    OBSERVATION_STATUS_DRAFT,
    OBSERVATION_STATUS_REOPENED,
    OBSERVATION_STATUS_SUBMITTED,
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    EvaluationCycle,
    EvaluatorRole,
    Observation,
    ObservationQuestion,
    ObservationQuestionSet,
    ObservationResponse,
    ObservationSource,
    ObservationType,
)
from analytics.services.comparison_service import (
    get_player_comparison,
    get_player_score_summary,
)
from analytics.services.draft_service import (
    get_draft_context_for_draft_player,
    get_draft_contexts_for_draft,
)
from analytics.services.evaluation_access_service import (
    get_my_evaluation_detail,
    get_my_evaluations,
)
from analytics.services.metrics_service import (
    completion_metrics,
    draft_matching_metrics,
    import_metrics,
    observation_metrics,
    recent_submitted_observations,
)
from analytics.services.observation_service import (
    create_coach_assessment_observation,
    create_observation,
    default_coach_assessment_question_set,
    get_observation_detail,
    save_observation_responses,
    submit_observation,
    validate_required_responses,
)
from analytics.services.permissions import (
    can_evaluate_player,
    can_submit_evaluation,
    can_view_own_evaluation_draft,
    evaluation_perspective_for_user,
    evaluator_role_for_user,
)
from analytics.services.player_service import (
    DRAFT_STATUS_AVAILABLE,
    DRAFT_STATUS_DRAFTED,
    DRAFT_STATUS_NO_CONTEXT,
    EVALUATION_HAS_ANY,
    EVALUATION_HAS_SUBMITTED,
    EVALUATION_NO_SUBMITTED,
    EVALUATION_NOT_STARTED,
    active_player_ids,
    parse_player_search_filters,
    search_players,
)
from analytics.services.question_service import (
    COACH_ASSESSMENT_RUBRIC,
    DEFAULT_COACH_ASSESSMENT_QUESTIONS,
    DEFAULT_EVALUATOR_ROLES,
    DEFAULT_OBSERVATION_SOURCES,
    ROLE_ADMIN,
    ROLE_COACH,
    ROLE_GUEST_EVALUATOR,
    ROLE_PLAYER,
    ROLE_STAFF,
    SOURCE_COACH,
    ensure_default_coach_assessment_setup,
    get_active_questions,
    get_question_set_for_cycle,
)
from analytics.services.reporting_service import get_command_center_context
from analytics.services.timeline_service import get_player_timeline
from drafts.models import Draft, DraftAction, DraftActionType, DraftPlayer, DraftTeam
from players.models import (
    Player,
    PlayerImportBatch,
    PlayerImportStatus,
    PlayerSourceRow,
    PlayerTag,
)
from players.services.import_service import SOURCE_MEMBER_LIST
from players.services.tag_service import assign_tag
from seasons.services.coach_assignment_service import create_assignment
from seasons.services.membership_service import create_membership
from seasons.services.season_service import create_season
from seasons.services.team_service import get_or_create_season_team

User = get_user_model()


def attach_player_to_season(
    player, season, *, team_name=None, division=None, is_primary=True
):
    season_team, _ = get_or_create_season_team(
        season=season,
        name=team_name or player.team_name or "Expos",
        division=division or player.division or "13U",
    )
    return create_membership(
        player=player, season_team=season_team, is_primary=is_primary, is_active=True
    )


__all__ = (
    "AccountRole",
    "COACH_ASSESSMENT_RUBRIC",
    "CoachAssessmentForm",
    "DEFAULT_COACH_ASSESSMENT_QUESTIONS",
    "DEFAULT_EVALUATOR_ROLES",
    "DEFAULT_OBSERVATION_SOURCES",
    "DRAFT_STATUS_AVAILABLE",
    "DRAFT_STATUS_DRAFTED",
    "DRAFT_STATUS_NO_CONTEXT",
    "Decimal",
    "Draft",
    "DraftAction",
    "DraftActionType",
    "DraftPlayer",
    "DraftTeam",
    "EVALUATION_HAS_ANY",
    "EVALUATION_HAS_SUBMITTED",
    "EVALUATION_NOT_STARTED",
    "EVALUATION_NO_SUBMITTED",
    "EVALUATION_PERSPECTIVE_COACH",
    "EVALUATION_PERSPECTIVE_GUEST",
    "EVALUATION_PERSPECTIVE_PEER",
    "EVALUATION_PERSPECTIVE_SELF",
    "EVALUATION_PERSPECTIVE_STAFF",
    "EvaluationCycle",
    "EvaluatorRole",
    "IntegrityError",
    "OBSERVATION_STATUS_DRAFT",
    "OBSERVATION_STATUS_REOPENED",
    "OBSERVATION_STATUS_SUBMITTED",
    "OBSERVATION_TYPE_COACH_ASSESSMENT",
    "Observation",
    "ObservationQuestion",
    "ObservationQuestionSet",
    "ObservationResponse",
    "ObservationSource",
    "ObservationType",
    "Player",
    "PlayerImportBatch",
    "PlayerImportStatus",
    "PlayerSourceRow",
    "PlayerTag",
    "RESPONSE_TYPE_RATING_1_5",
    "RESPONSE_TYPE_TEXT",
    "ROLE_ADMIN",
    "ROLE_COACH",
    "ROLE_GUEST_EVALUATOR",
    "ROLE_PLAYER",
    "ROLE_STAFF",
    "SOURCE_COACH",
    "SOURCE_MEMBER_LIST",
    "SimpleUploadedFile",
    "TestCase",
    "User",
    "UserPlayerRelationship",
    "ValidationError",
    "activate_link",
    "active_player_ids",
    "admin",
    "assign_tag",
    "attach_player_to_season",
    "can_evaluate_player",
    "can_submit_evaluation",
    "can_view_own_evaluation_draft",
    "completion_metrics",
    "create_assignment",
    "create_coach_assessment_observation",
    "create_membership",
    "create_observation",
    "create_season",
    "deactivate_link",
    "default_coach_assessment_question_set",
    "draft_matching_metrics",
    "ensure_default_coach_assessment_setup",
    "evaluation_perspective_for_user",
    "evaluator_role_for_user",
    "get_active_questions",
    "get_command_center_context",
    "get_draft_context_for_draft_player",
    "get_draft_contexts_for_draft",
    "get_my_evaluation_detail",
    "get_my_evaluations",
    "get_observation_detail",
    "get_or_create_season_team",
    "get_player_comparison",
    "get_player_score_summary",
    "get_player_timeline",
    "get_question_set_for_cycle",
    "import_metrics",
    "link_user_to_player",
    "observation_metrics",
    "parse_player_search_filters",
    "patch",
    "recent_submitted_observations",
    "reverse",
    "save_observation_responses",
    "search_players",
    "set_account_role",
    "submit_observation",
    "timedelta",
    "timezone",
    "transaction",
    "validate_required_responses",
)
