from analytics.models import OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED, OBSERVATION_STATUS_SUBMITTED


def can_submit_coach_assessment(user) -> bool:
    return bool(user and user.is_authenticated)


def can_review_observations(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def can_view_observation(user, observation) -> bool:
    if can_review_observations(user):
        return True
    return bool(user and user.is_authenticated and observation.evaluator_id == user.id)


def can_edit_observation(user, observation) -> bool:
    if not user or not user.is_authenticated or observation.evaluator_id != user.id:
        return False
    return observation.status in {OBSERVATION_STATUS_DRAFT, OBSERVATION_STATUS_REOPENED}


def can_reopen_observation(user, observation) -> bool:
    return can_review_observations(user) and observation.status == OBSERVATION_STATUS_SUBMITTED
