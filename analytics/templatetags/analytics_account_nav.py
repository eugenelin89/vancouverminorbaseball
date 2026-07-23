from django import template

from analytics.services.permissions import (
    can_review_submitted_evaluations,
    can_submit_evaluation,
    can_view_my_evaluations,
)

register = template.Library()


@register.inclusion_tag("analytics/includes/account_profile_actions.html")
def analytics_account_profile_actions(user):
    """Render Analytics-owned account profile navigation eligibility."""
    return {
        "can_submit_evaluations": can_submit_evaluation(user),
        "can_view_my_evaluations": can_view_my_evaluations(user),
        "can_review_submitted_evaluations": can_review_submitted_evaluations(user),
    }


@register.simple_tag
def analytics_can_submit_evaluation(user):
    """Return whether the user should see evaluation submission navigation."""
    return can_submit_evaluation(user)


@register.simple_tag
def analytics_can_view_my_evaluations(user):
    """Return whether the user should see player-facing evaluation navigation."""
    return can_view_my_evaluations(user)


@register.simple_tag
def analytics_can_review_evaluations(user):
    """Return whether the user should see evaluation review navigation."""
    return can_review_submitted_evaluations(user)
