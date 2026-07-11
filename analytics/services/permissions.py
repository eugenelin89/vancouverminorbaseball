from django.core.exceptions import ValidationError

from accounts.models import AccountRole
from accounts.services.link_service import get_self_linked_players, has_self_link, is_player_self
from accounts.services.role_service import role_for_user, role_label
from analytics.models import (
    EVALUATION_PERSPECTIVE_COACH,
    EVALUATION_PERSPECTIVE_GUEST,
    EVALUATION_PERSPECTIVE_PEER,
    EVALUATION_PERSPECTIVE_SELF,
    EVALUATION_PERSPECTIVE_STAFF,
    OBSERVATION_STATUS_DRAFT,
    OBSERVATION_STATUS_REOPENED,
    OBSERVATION_STATUS_SUBMITTED,
    EvaluatorRole,
)


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
    if target_player is not None and not getattr(target_player, "is_active", False):
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True

    account_role = role_for_user(user)
    if account_role not in EVALUATION_SUBMITTER_ROLES:
        return False
    return True


def can_evaluate_player(user, target_player) -> bool:
    if not target_player or not can_submit_evaluation(user, target_player=target_player):
        return False
    if role_for_user(user) == AccountRole.PLAYER and not is_player_self(user, target_player):
        return not has_self_link(user, target_player, active_only=False)
    return True


def evaluation_perspective_for_user(user, target_player) -> str:
    """Return the server-derived evaluation perspective for this submission."""
    if not can_submit_evaluation(user, target_player=target_player):
        raise ValidationError("This account cannot submit an evaluation for this player.")
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return EVALUATION_PERSPECTIVE_STAFF

    account_role = role_for_user(user)
    if account_role == AccountRole.PLAYER:
        if is_player_self(user, target_player):
            return EVALUATION_PERSPECTIVE_SELF
        if has_self_link(user, target_player, active_only=False):
            raise ValidationError("An active self player link is required to submit a self evaluation.")
        return EVALUATION_PERSPECTIVE_PEER
    if account_role == AccountRole.COACH:
        return EVALUATION_PERSPECTIVE_COACH
    if account_role == AccountRole.STAFF or account_role == AccountRole.ADMIN:
        return EVALUATION_PERSPECTIVE_STAFF
    if account_role == AccountRole.GUEST_EVALUATOR:
        return EVALUATION_PERSPECTIVE_GUEST
    raise ValidationError("This account role cannot submit evaluations.")


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


def can_review_submitted_evaluations(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return role_for_user(user) in {AccountRole.COACH, AccountRole.STAFF, AccountRole.ADMIN}


def can_view_evaluation_review_detail(user, observation) -> bool:
    return bool(
        observation
        and observation.status == OBSERVATION_STATUS_SUBMITTED
        and can_review_submitted_evaluations(user)
    )


def can_view_observation(user, observation) -> bool:
    if can_review_observations(user):
        return True
    return bool(user and user.is_authenticated and observation.evaluator_id == user.id)


def can_view_my_evaluations(user, player=None) -> bool:
    if not user or not user.is_authenticated:
        return False
    if player is not None:
        if not getattr(player, "is_active", False):
            return False
        return is_player_self(user, player)
    return get_self_linked_players(user).filter(is_active=True).exists()


def can_view_my_evaluation_detail(user, observation) -> bool:
    if not observation or observation.status != OBSERVATION_STATUS_SUBMITTED:
        return False
    return can_view_my_evaluations(user, player=observation.player)


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
