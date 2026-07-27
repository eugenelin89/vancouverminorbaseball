from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Protocol


class EvaluationReportResponseLike(Protocol):
    category: str
    numeric_value: object
    text_value: str


@dataclass(frozen=True)
class EvaluationReportCategorySummary:
    name: str
    responses: list[EvaluationReportResponseLike]
    average_rating: Decimal | None
    answered_count: int
    rated_count: int
    question_count: int


@dataclass(frozen=True)
class EvaluationReportOverallSummary:
    average_rating: Decimal | None
    answered_count: int
    rated_count: int
    question_count: int


def _numeric_rating(value) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _has_answer(response: EvaluationReportResponseLike) -> bool:
    return _numeric_rating(response.numeric_value) is not None or bool(
        (response.text_value or "").strip()
    )


def _average(values: list[Decimal]) -> Decimal | None:
    if not values:
        return None
    return sum(values, Decimal("0")) / Decimal(len(values))


def build_category_summaries(
    responses: Iterable[EvaluationReportResponseLike],
) -> list[EvaluationReportCategorySummary]:
    """Group consecutive report responses by category without changing display order."""
    grouped: list[tuple[str, list[EvaluationReportResponseLike]]] = []
    for response in responses:
        category = response.category or "Questions"
        if not grouped or grouped[-1][0] != category:
            grouped.append((category, []))
        grouped[-1][1].append(response)

    summaries = []
    for category, category_responses in grouped:
        ratings = [
            rating
            for rating in (
                _numeric_rating(response.numeric_value)
                for response in category_responses
            )
            if rating is not None
        ]
        summaries.append(
            EvaluationReportCategorySummary(
                name=category,
                responses=category_responses,
                average_rating=_average(ratings),
                answered_count=sum(
                    1 for response in category_responses if _has_answer(response)
                ),
                rated_count=len(ratings),
                question_count=len(category_responses),
            )
        )
    return summaries


def build_overall_summary(
    category_summaries: Iterable[EvaluationReportCategorySummary],
) -> EvaluationReportOverallSummary:
    """Return an overall read-model summary from category summaries."""
    summaries = list(category_summaries)
    ratings = [
        rating
        for summary in summaries
        for rating in (
            _numeric_rating(response.numeric_value) for response in summary.responses
        )
        if rating is not None
    ]
    return EvaluationReportOverallSummary(
        average_rating=_average(ratings),
        answered_count=sum(summary.answered_count for summary in summaries),
        rated_count=len(ratings),
        question_count=sum(summary.question_count for summary in summaries),
    )
