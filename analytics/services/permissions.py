from django.core.exceptions import ValidationError

from accounts.models import AccountRole
from accounts.services.link_service import is_player_self
from accounts.services.role_service import role_for_user, role_label
from analytics.models import OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED, OBSERVATION_STATUS_SUBMITTED, EvaluatorRole


ACCOUNT_ROLE_TO_EVALUATOR_ROLE = {
    AccountRole.COACH: "coach",
    AccountRole.PLAYER: "player",
    AccountRole.STAFF: "staff",
    AccountRole.ADMIN: "admin",
    AccountRole.GUEST_EVALUATOR: "guest_evaluator",
}

EVALUATION_SUBMITTER_ROLES = set(ACCOUNT_ROLE_TO_EVALUATOR_ROLE)


def can_submit_coach_assessment(user) -> bool:
    return can_submit_evaluation(user)


def can_submit_evaluation(user, target_player=None) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return not (target_player is not None and is_player_self(user, target_player))

    account_role = role_for_user(user)
    if account_role not in EVALUATION_SUBMITTER_ROLES:
        return False
    if target_player is not None and is_player_self(user, target_player):
        return False
    return True


def can_evaluate_player(user, target_player) -> bool:
    return bool(target_player and can_submit_evaluation(user, target_player=target_player))


def evaluator_role_for_user(user) -> EvaluatorRole:
    if not user or not user.is_authenticated:
        raise ValidationError("An authenticated evaluator is required.")
    account_role = role_for_user(user)
    evaluator_role_key = ACCOUNT_ROLE_TO_EVALUATOR_ROLE.get(account_role)
    if not evaluator_role_key:
        raise ValidationError("This account role cannot submit evaluations.")
    evaluator_role, _ = EvaluatorRole.objects.get_or_create(
        key=evaluator_role_key,
        defaults={"name": role_label(account_role), "is_active": True},
    )
    return evaluator_role


def can_review_observations(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def can_view_observation(user, observation) -> bool:
    if can_review_observations(user):
        return True
    return bool(user and user.is_authenticated and observation.evaluator_id == user.id)


def can_edit_observation(user, observation) -> bool:
    return can_edit_own_evaluation_draft(user, observation)


def can_view_own_evaluation_draft(user, observation) -> bool:
    if not user or not user.is_authenticated or observation.evaluator_id != user.id:
        return False
    return observation.status in {OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED}


def can_edit_own_evaluation_draft(user, observation) -> bool:
    if not user or not user.is_authenticated or observation.evaluator_id != user.id:
        return False
    return observation.status in {OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED}


def can_reopen_observation(user, observation) -> bool:
    return can_review_observations(user) and observation.status == OBSERVATION_STATUS_SUBMITTED
