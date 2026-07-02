from decimal import Decimal

from django.db import migrations
from django.utils.text import slugify


OBSERVATION_TYPE_COACH_ASSESSMENT = "coach_assessment"
RESPONSE_TYPE_RATING_1_5 = "rating_1_5"
RESPONSE_TYPE_TEXT = "text"

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
    ("coach", "Coach"),
    ("staff", "Staff"),
    ("manual_entry", "Manual Entry"),
    ("imported_csv", "Imported CSV"),
    ("draft_context", "Draft Context"),
]

DEFAULT_EVALUATOR_ROLES = [
    ("coach", "Coach"),
    ("assistant_coach", "Assistant Coach"),
    ("head_coach", "Head Coach"),
    ("coordinator", "Coordinator"),
    ("staff", "Staff"),
    ("admin", "Admin"),
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


def question_key(category, prompt):
    return f"{slugify(category).replace('-', '_')}_{slugify(prompt).replace('-', '_')}"[:120]


def seed_defaults(apps, schema_editor):
    ObservationType = apps.get_model("analytics", "ObservationType")
    ObservationSource = apps.get_model("analytics", "ObservationSource")
    EvaluatorRole = apps.get_model("analytics", "EvaluatorRole")
    ObservationQuestionSet = apps.get_model("analytics", "ObservationQuestionSet")
    ObservationQuestion = apps.get_model("analytics", "ObservationQuestion")

    observation_type, _ = ObservationType.objects.update_or_create(
        key=OBSERVATION_TYPE_COACH_ASSESSMENT,
        defaults={"name": "Coach Assessment", "is_active": True},
    )

    for key, name in DEFAULT_OBSERVATION_SOURCES:
        ObservationSource.objects.update_or_create(key=key, defaults={"name": name, "is_active": True})

    for key, name in DEFAULT_EVALUATOR_ROLES:
        EvaluatorRole.objects.update_or_create(key=key, defaults={"name": name, "is_active": True})

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

    for display_order, (category, prompt, response_type) in enumerate(DEFAULT_COACH_ASSESSMENT_QUESTIONS, start=1):
        ObservationQuestion.objects.update_or_create(
            question_set=question_set,
            key=question_key(category, prompt),
            defaults={
                "prompt": prompt,
                "category": category,
                "response_type": response_type,
                "display_order": display_order,
                "is_required": response_type == RESPONSE_TYPE_RATING_1_5,
                "is_active": True,
                "min_numeric_value": Decimal("1") if response_type == RESPONSE_TYPE_RATING_1_5 else None,
                "max_numeric_value": Decimal("5") if response_type == RESPONSE_TYPE_RATING_1_5 else None,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_defaults, migrations.RunPython.noop),
    ]
