from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from analytics.models import (
    EVALUATION_PERSPECTIVE_GUEST,
    EVALUATION_PERSPECTIVE_SELF,
    OBSERVATION_STATUS_DRAFT,
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
from analytics.services.question_service import (
    SOURCE_COACH,
    get_active_questions,
    get_coach_assessment_type,
    get_default_coach_assessment_question_set,
    get_question_set_for_cycle,
)
from analytics.services.permissions import can_evaluate_player, evaluation_perspective_for_user, evaluator_role_for_user
from players.models import Player
from seasons.models import CoachSeasonAssignment, PlayerRosterMembership
from analytics.services.evaluation_context_service import apply_evaluation_context, resolve_evaluation_context


@dataclass
class ObservationCreateResult:
    observation: Observation
    responses_created: int = 0
    responses_updated: int = 0


def _snapshot_role(observation: Observation, evaluator_role: EvaluatorRole | None) -> None:
    if evaluator_role:
        observation.evaluator_role = evaluator_role
        observation.evaluator_role_key = evaluator_role.key
        observation.evaluator_role_name = evaluator_role.name


def _validate_unique_coach_assessment(
    *,
    player: Player,
    evaluation_cycle: EvaluationCycle,
    observation_type: ObservationType,
    evaluator,
    evaluation_perspective: str,
    exclude_observation: Observation | None = None,
) -> None:
    if observation_type.key != OBSERVATION_TYPE_COACH_ASSESSMENT or evaluator is None:
        return
    queryset = Observation.objects.filter(
        player=player,
        evaluation_cycle=evaluation_cycle,
        observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
        evaluator=evaluator,
        evaluation_perspective=evaluation_perspective,
    )
    if exclude_observation:
        queryset = queryset.exclude(pk=exclude_observation.pk)
    if queryset.exists():
        raise ValidationError("This evaluator already has a coach assessment for this player and evaluation cycle.")
    if evaluation_perspective == EVALUATION_PERSPECTIVE_SELF:
        self_queryset = Observation.objects.filter(
            player=player,
            evaluation_cycle=evaluation_cycle,
            observation_type_key=OBSERVATION_TYPE_COACH_ASSESSMENT,
            evaluation_perspective=EVALUATION_PERSPECTIVE_SELF,
        )
        if exclude_observation:
            self_queryset = self_queryset.exclude(pk=exclude_observation.pk)
        if self_queryset.exists():
            raise ValidationError("This player already has a self evaluation for this evaluation cycle.")


def _coerce_rating(value) -> Decimal:
    try:
        numeric = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Rating responses must be numeric.") from None
    if (
        not numeric.is_finite()
        or numeric != numeric.to_integral_value()
        or numeric < Decimal("1")
        or numeric > Decimal("5")
    ):
        raise ValidationError("Rating responses must be one of 1, 2, 3, 4, or 5.")
    return numeric


def _validate_question_set_for_type(question_set: ObservationQuestionSet, observation_type: ObservationType) -> None:
    if question_set.observation_type_id != observation_type.id:
        raise ValidationError("Question set must belong to the selected observation type.")


def _response_defaults(question: ObservationQuestion, value, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    extra = extra or {}
    defaults = {
        "response_type": question.response_type,
        "numeric_value": None,
        "text_value": "",
        "boolean_value": None,
        "selected_choice": "",
        "raw_value": "" if value is None else str(value),
        "unit": extra.get("unit", ""),
        "payload": extra.get("payload", {}),
        "metadata": extra.get("metadata", {}),
    }
    if question.response_type == RESPONSE_TYPE_RATING_1_5:
        defaults["numeric_value"] = _coerce_rating(value)
    elif question.response_type == RESPONSE_TYPE_TEXT:
        defaults["text_value"] = "" if value is None else str(value)
    else:
        raise ValidationError(f"Response type {question.response_type} is not implemented in Version 1.")
    return defaults


@transaction.atomic
def create_observation(
    *,
    player: Player,
    evaluation_cycle: EvaluationCycle,
    observation_type: ObservationType,
    question_set: ObservationQuestionSet,
    source: ObservationSource,
    evaluator=None,
    evaluator_role: EvaluatorRole | None = None,
    evaluation_perspective: str | None = None,
    player_roster_membership: PlayerRosterMembership | None = None,
    evaluator_coach_assignment: CoachSeasonAssignment | None = None,
    status: str = OBSERVATION_STATUS_DRAFT,
    notes: str = "",
    source_metadata: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Observation:
    """Create an observation with role snapshot and duplicate validation."""
    _validate_question_set_for_type(question_set, observation_type)
    if evaluator is not None:
        if not can_evaluate_player(evaluator, player):
            raise ValidationError("This evaluator cannot evaluate this player.")
        evaluator_role = evaluator_role or evaluator_role_for_user(evaluator)
        evaluation_perspective = evaluation_perspective or evaluation_perspective_for_user(evaluator, player)
    else:
        evaluation_perspective = evaluation_perspective or EVALUATION_PERSPECTIVE_GUEST
    _validate_unique_coach_assessment(
        player=player,
        evaluation_cycle=evaluation_cycle,
        observation_type=observation_type,
        evaluator=evaluator,
        evaluation_perspective=evaluation_perspective,
    )
    context = resolve_evaluation_context(
        player=player,
        evaluation_cycle=evaluation_cycle,
        evaluator=evaluator,
        evaluation_perspective=evaluation_perspective,
        player_roster_membership=player_roster_membership,
        evaluator_coach_assignment=evaluator_coach_assignment,
        require_season=False,
    )
    observation = Observation(
        player=player,
        evaluation_cycle=evaluation_cycle,
        observation_type=observation_type,
        observation_type_key=observation_type.key,
        question_set=question_set,
        source=source,
        evaluator=evaluator,
        evaluation_perspective=evaluation_perspective,
        status=status,
        notes=notes,
        source_metadata=source_metadata or {},
        metadata=metadata or {},
    )
    _snapshot_role(observation, evaluator_role)
    apply_evaluation_context(observation, context, refresh_snapshots=True)
    if status == OBSERVATION_STATUS_SUBMITTED:
        observation.submitted_at = timezone.now()
    try:
        observation.save()
    except IntegrityError as exc:
        raise ValidationError("This observation would duplicate an existing coach assessment.") from exc
    return observation


@transaction.atomic
def create_coach_assessment_observation(
    *,
    player: Player,
    evaluation_cycle: EvaluationCycle,
    evaluator,
    evaluator_role: EvaluatorRole | None = None,
    evaluation_perspective: str | None = None,
    player_roster_membership: PlayerRosterMembership | None = None,
    evaluator_coach_assignment: CoachSeasonAssignment | None = None,
    source: ObservationSource | None = None,
    question_set: ObservationQuestionSet | None = None,
    status: str = OBSERVATION_STATUS_DRAFT,
    responses: dict[Any, Any] | None = None,
    notes: str = "",
    source_metadata: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ObservationCreateResult:
    """Create a coach assessment observation and optional responses."""
    if evaluator is None:
        raise ValidationError("Coach assessments require an evaluator.")
    observation_type = get_coach_assessment_type()
    question_set = question_set or get_question_set_for_cycle(evaluation_cycle, observation_type)
    source = source or ObservationSource.objects.get(key=SOURCE_COACH)
    evaluator_role = evaluator_role or evaluator_role_for_user(evaluator)
    evaluation_perspective = evaluation_perspective or evaluation_perspective_for_user(evaluator, player)
    observation = create_observation(
        player=player,
        evaluation_cycle=evaluation_cycle,
        observation_type=observation_type,
        question_set=question_set,
        source=source,
        evaluator=evaluator,
        evaluator_role=evaluator_role,
        evaluation_perspective=evaluation_perspective,
        player_roster_membership=player_roster_membership,
        evaluator_coach_assignment=evaluator_coach_assignment,
        status=status,
        notes=notes,
        source_metadata=source_metadata,
        metadata=metadata,
    )
    result = ObservationCreateResult(observation=observation)
    if responses:
        created, updated = save_observation_responses(observation, responses)
        result.responses_created = created
        result.responses_updated = updated
    return result


def _question_for_response(observation: Observation, question_ref) -> ObservationQuestion:
    if isinstance(question_ref, ObservationQuestion):
        question = question_ref
    elif isinstance(question_ref, int):
        question = ObservationQuestion.objects.get(pk=question_ref)
    else:
        question = ObservationQuestion.objects.get(question_set=observation.question_set, key=str(question_ref))
    if question.question_set_id != observation.question_set_id:
        raise ValidationError("Responses can only be saved for questions in the observation question set.")
    return question


@transaction.atomic
def save_observation_responses(observation: Observation, responses: dict[Any, Any] | list[dict[str, Any]]) -> tuple[int, int]:
    """Create or update responses for an observation."""
    locked_observation = Observation.objects.select_for_update().get(pk=observation.pk)
    created_count = 0
    updated_count = 0

    if isinstance(responses, dict):
        response_items = [{"question": question_ref, "value": value} for question_ref, value in responses.items()]
    else:
        response_items = responses

    for response_input in response_items:
        question = _question_for_response(locked_observation, response_input["question"])
        defaults = _response_defaults(question, response_input.get("value"), extra=response_input)
        _, created = ObservationResponse.objects.update_or_create(
            observation=locked_observation,
            question=question,
            defaults=defaults,
        )
        created_count += int(created)
        updated_count += int(not created)

    return created_count, updated_count


def validate_required_responses(observation: Observation) -> None:
    """Ensure submitted coach assessments include all active required question responses."""
    if observation.observation_type_key != OBSERVATION_TYPE_COACH_ASSESSMENT:
        return
    required_question_ids = set(
        observation.question_set.questions.filter(is_active=True, is_required=True).values_list("id", flat=True)
    )
    answered_question_ids = set(observation.responses.filter(question_id__in=required_question_ids).values_list("question_id", flat=True))
    missing_count = len(required_question_ids - answered_question_ids)
    if missing_count:
        raise ValidationError(f"Coach assessment is missing {missing_count} required response(s).")


@transaction.atomic
def submit_observation(observation: Observation, actor=None) -> Observation:
    """Mark an observation submitted."""
    locked_observation = (
        Observation.objects.select_for_update()
        .select_related("observation_type", "evaluation_cycle", "player", "evaluator")
        .get(pk=observation.pk)
    )
    if locked_observation.observation_type:
        _validate_unique_coach_assessment(
            player=locked_observation.player,
            evaluation_cycle=locked_observation.evaluation_cycle,
            observation_type=locked_observation.observation_type,
            evaluator=locked_observation.evaluator,
            evaluation_perspective=locked_observation.evaluation_perspective,
            exclude_observation=locked_observation,
        )
    validate_required_responses(locked_observation)
    context = resolve_evaluation_context(
        player=locked_observation.player,
        evaluation_cycle=locked_observation.evaluation_cycle,
        evaluator=locked_observation.evaluator,
        evaluation_perspective=locked_observation.evaluation_perspective,
        player_roster_membership=locked_observation.player_roster_membership,
        evaluator_coach_assignment=locked_observation.evaluator_coach_assignment,
        require_season=True,
    )
    apply_evaluation_context(locked_observation, context, refresh_snapshots=True)
    locked_observation.status = OBSERVATION_STATUS_SUBMITTED
    locked_observation.submitted_at = timezone.now()
    locked_observation.save(
        update_fields=[
            "season",
            "player_roster_membership",
            "evaluator_coach_assignment",
            "season_name_snapshot",
            "season_key_snapshot",
            "player_team_name_snapshot",
            "player_division_snapshot",
            "evaluator_team_name_snapshot",
            "evaluator_division_snapshot",
            "evaluator_assignment_role_snapshot",
            "status",
            "submitted_at",
            "updated_at",
        ]
    )
    return locked_observation


def get_observation_detail(observation_id: int) -> Observation:
    """Return an observation with related player, cycle, question set, and responses."""
    return (
        Observation.objects.select_related(
            "player",
            "evaluation_cycle",
            "season",
            "player_roster_membership",
            "player_roster_membership__season_team",
            "evaluator_coach_assignment",
            "evaluator_coach_assignment__season_team",
            "observation_type",
            "question_set",
            "source",
            "evaluator",
            "evaluator_role",
        )
        .prefetch_related("responses__question")
        .get(pk=observation_id)
    )


def active_questions_for_observation(observation: Observation):
    """Return active questions for an observation's question set."""
    return get_active_questions(observation.question_set)


def default_coach_assessment_question_set() -> ObservationQuestionSet:
    """Convenience wrapper for the default coach assessment question set."""
    return get_default_coach_assessment_question_set()
