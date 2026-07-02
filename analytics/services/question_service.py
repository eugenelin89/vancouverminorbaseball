from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction
from django.utils.text import slugify

from analytics.models import (
    OBSERVATION_TYPE_COACH_ASSESSMENT,
    RESPONSE_TYPE_RATING_1_5,
    RESPONSE_TYPE_TEXT,
    EvaluationCycle,
    EvaluatorRole,
    ObservationQuestion,
    ObservationQuestionSet,
    ObservationSource,
    ObservationType,
)


SOURCE_COACH = "coach"
SOURCE_STAFF = "staff"
SOURCE_MANUAL_ENTRY = "manual_entry"
SOURCE_IMPORTED_CSV = "imported_csv"
SOURCE_DRAFT_CONTEXT = "draft_context"

ROLE_COACH = "coach"
ROLE_ASSISTANT_COACH = "assistant_coach"
ROLE_HEAD_COACH = "head_coach"
ROLE_COORDINATOR = "coordinator"
ROLE_STAFF = "staff"
ROLE_ADMIN = "admin"

COACH_ASSESSMENT_RUBRIC = {
    "scale": "1-5",
    "labels": {
        "1": "0/5 times, Never",
        "2": "1-2/5 times, Infrequently",
        "3": "2.5/5 times, Half the time",
        "4": "4/5 times, Frequently",
        "5": "5/5 times, Always",
    },
}

DEFAULT_OBSERVATION_SOURCES = [
    (SOURCE_COACH, "Coach"),
    (SOURCE_STAFF, "Staff"),
    (SOURCE_MANUAL_ENTRY, "Manual Entry"),
    (SOURCE_IMPORTED_CSV, "Imported CSV"),
    (SOURCE_DRAFT_CONTEXT, "Draft Context"),
]

DEFAULT_EVALUATOR_ROLES = [
    (ROLE_COACH, "Coach"),
    (ROLE_ASSISTANT_COACH, "Assistant Coach"),
    (ROLE_HEAD_COACH, "Head Coach"),
    (ROLE_COORDINATOR, "Coordinator"),
    (ROLE_STAFF, "Staff"),
    (ROLE_ADMIN, "Admin"),
]

DEFAULT_COACH_ASSESSMENT_QUESTIONS = [
    ("Throw", "Throws accurately", RESPONSE_TYPE_RATING_1_5),
    ("Throw", "Throws with velocity", RESPONSE_TYPE_RATING_1_5),
    ("Throw", "Ability to throw from outfield to infield in the air or on one hop", RESPONSE_TYPE_RATING_1_5),
    ("Throw", "Can throw accurately across the diamond from 3rd to 1st", RESPONSE_TYPE_RATING_1_5),
    ("Field", "Can catch routine balls at 1st base", RESPONSE_TYPE_RATING_1_5),
    ("Field", "Can catch non-routine balls at 1st base", RESPONSE_TYPE_RATING_1_5),
    ("Field", "Ability to catch a routine grounder", RESPONSE_TYPE_RATING_1_5),
    ("Field", "Ability to catch a non-routine grounder", RESPONSE_TYPE_RATING_1_5),
    ("Field", "Ability to catch a routine fly ball", RESPONSE_TYPE_RATING_1_5),
    ("Field", "Ability to catch a non-routine fly ball", RESPONSE_TYPE_RATING_1_5),
    ("Hitting", "Hits barrels", RESPONSE_TYPE_RATING_1_5),
    ("Hitting", "Player can sacrifice bunt", RESPONSE_TYPE_RATING_1_5),
    ("Hitting", "Player chooses strikes to swing at", RESPONSE_TYPE_RATING_1_5),
    ("Hitting", "Gets on base", RESPONSE_TYPE_RATING_1_5),
    ("Hitting", "Hits for power", RESPONSE_TYPE_RATING_1_5),
    ("Pitching", "Throws strikes", RESPONSE_TYPE_RATING_1_5),
    ("Pitching", "Can hold runners", RESPONSE_TYPE_RATING_1_5),
    ("Pitching", "Has good velocity", RESPONSE_TYPE_RATING_1_5),
    ("Pitching", "Has an off-speed pitch", RESPONSE_TYPE_RATING_1_5),
    ("Catching", "Likes to catch", RESPONSE_TYPE_RATING_1_5),
    ("Catching", "Can throw to 2nd accurately", RESPONSE_TYPE_RATING_1_5),
    ("Catching", "Can block", RESPONSE_TYPE_RATING_1_5),
    ("Hustle", "Always focused", RESPONSE_TYPE_RATING_1_5),
    ("Hustle", "Checks in/attends regularly", RESPONSE_TYPE_RATING_1_5),
    ("Hustle", "Listens to coach feedback", RESPONSE_TYPE_RATING_1_5),
    ("Notes", "Freeform coach notes", RESPONSE_TYPE_TEXT),
]


@dataclass
class DefaultCoachAssessmentSetup:
    observation_type: ObservationType
    question_set: ObservationQuestionSet
    sources_created: int = 0
    roles_created: int = 0
    questions_created: int = 0


def question_key(category: str, prompt: str) -> str:
    """Return a stable key for a question within a question set."""
    return f"{slugify(category).replace('-', '_')}_{slugify(prompt).replace('-', '_')}"[:120]


@transaction.atomic
def ensure_default_coach_assessment_setup() -> DefaultCoachAssessmentSetup:
    """Create the default Version 1 coach assessment configuration if missing."""
    observation_type, _ = ObservationType.objects.update_or_create(
        key=OBSERVATION_TYPE_COACH_ASSESSMENT,
        defaults={"name": "Coach Assessment", "is_active": True},
    )

    sources_created = 0
    for key, name in DEFAULT_OBSERVATION_SOURCES:
        _, created = ObservationSource.objects.update_or_create(key=key, defaults={"name": name, "is_active": True})
        sources_created += int(created)

    roles_created = 0
    for key, name in DEFAULT_EVALUATOR_ROLES:
        _, created = EvaluatorRole.objects.update_or_create(key=key, defaults={"name": name, "is_active": True})
        roles_created += int(created)

    question_set, _ = ObservationQuestionSet.objects.update_or_create(
        observation_type=observation_type,
        version=1,
        defaults={
            "name": "Coach Assessment V1",
            "description": "Default Version 1 coach assessment question set.",
            "rubric": COACH_ASSESSMENT_RUBRIC,
            "is_active": True,
        },
    )

    questions_created = 0
    for display_order, (category, prompt, response_type) in enumerate(DEFAULT_COACH_ASSESSMENT_QUESTIONS, start=1):
        defaults = {
            "prompt": prompt,
            "category": category,
            "response_type": response_type,
            "display_order": display_order,
            "is_required": response_type == RESPONSE_TYPE_RATING_1_5,
            "is_active": True,
            "min_numeric_value": 1 if response_type == RESPONSE_TYPE_RATING_1_5 else None,
            "max_numeric_value": 5 if response_type == RESPONSE_TYPE_RATING_1_5 else None,
        }
        _, created = ObservationQuestion.objects.update_or_create(
            question_set=question_set,
            key=question_key(category, prompt),
            defaults=defaults,
        )
        questions_created += int(created)

    return DefaultCoachAssessmentSetup(
        observation_type=observation_type,
        question_set=question_set,
        sources_created=sources_created,
        roles_created=roles_created,
        questions_created=questions_created,
    )


def get_coach_assessment_type() -> ObservationType:
    """Return the configured coach assessment observation type."""
    return ObservationType.objects.get(key=OBSERVATION_TYPE_COACH_ASSESSMENT)


def get_default_coach_assessment_question_set() -> ObservationQuestionSet:
    """Return the latest active coach assessment question set."""
    return (
        ObservationQuestionSet.objects.select_related("observation_type")
        .filter(observation_type__key=OBSERVATION_TYPE_COACH_ASSESSMENT, is_active=True)
        .order_by("-version")
        .get()
    )


def get_question_set_for_cycle(cycle: EvaluationCycle, observation_type: ObservationType | None = None) -> ObservationQuestionSet:
    """Return the cycle-specific question set or the active default for the observation type."""
    if cycle.coach_assessment_question_set_id:
        return cycle.coach_assessment_question_set
    if observation_type and observation_type.key != OBSERVATION_TYPE_COACH_ASSESSMENT:
        return (
            ObservationQuestionSet.objects.filter(observation_type=observation_type, is_active=True)
            .order_by("-version")
            .get()
        )
    return get_default_coach_assessment_question_set()


def get_active_questions(question_set: ObservationQuestionSet):
    """Return active questions for a question set in display order."""
    return question_set.questions.filter(is_active=True).order_by("display_order", "id")
