# Prompt 106 - Platform

## User Prompt

```text
You are working in the Django project located at:

/Users/eugenelin/dev/vmba0

The production site is:

https://vancouverminor.com/

## Objective

Redesign the submitted evaluation review experience so it looks polished, modern, and intentionally designed on both desktop browsers and mobile devices.

The current evaluation detail page is functional, but visually underdeveloped. On desktop, the content is left-heavy with large amounts of empty space, the metadata reads like a plain definition list, and the evaluation answers do not have enough visual hierarchy. On mobile, the page should remain compact, readable, and easy to scan without feeling cramped.

This is not a broad site-wide redesign. Focus specifically on the submitted evaluation review/detail experience and any shared components that directly support it.

The main route is similar to:

/analytics/evaluation-review/<observation_id>/

Also inspect closely related submitted/read-only evaluation pages, such as:

- staff evaluation review detail
- observation review detail
- “My Evaluations” detail
- coach assessment detail
- any shared read-only evaluation partials

Use the project’s URL configuration and templates to identify the exact routes and shared components.

## Current visual problems

The current desktop page has several issues:

1. The evaluation metadata is presented as a narrow vertical list on the left side of a very wide card.
2. Most of the card width is empty.
3. The metadata lacks visual grouping and hierarchy.
4. The player, evaluator, season, cycle, and submission information are all treated with nearly equal emphasis.
5. Evaluation answers appear as large pale boxes, but the question, category, score, and answer hierarchy is weak.
6. Numeric ratings are visually easy to miss.
7. The page is long but not especially easy to scan.
8. The desktop layout does not make good use of available horizontal space.
9. The mobile layout should remain elegant and not simply collapse into an endless stack of oversized blocks.
10. The visual treatment should feel consistent with the existing VCB branding and responsive card system.

## Desired result

The submitted evaluation detail should feel like a professional player development report.

A user should be able to understand, at a glance:

- who was evaluated
- what kind of evaluation it was
- who submitted it
- when it was submitted
- season, team, division, and cycle context
- category-by-category results
- individual question scores and comments
- whether a question was unanswered
- available actions such as back, reopen, edit, or print, depending on permissions

The finished page should feel balanced, polished, and easy to scan on desktop, tablet, and phone.

## Design direction

Use a responsive report-style layout.

### Header / summary area

Create a strong summary section near the top of the page.

The most important information should be visually prominent:

- player name
- evaluation type
- evaluator name
- submitted date

Secondary context should be grouped clearly:

- season
- team
- division
- evaluation cycle
- evaluator role

Consider a summary card or report header with:

- a prominent player name
- a badge or label for “Peer Evaluation”, “Self Evaluation”, “Coach Evaluation”, etc.
- a status badge such as “Submitted”
- a concise metadata grid
- optional small icons only if the project already uses them or they can be added without introducing a new icon framework

Do not make the page overly decorative. The design should feel clean, trustworthy, and appropriate for a youth baseball development platform.

### Desktop layout

On desktop, use the available width effectively.

A good structure may be:

- a full-width report summary at the top
- a two-column layout below, where appropriate:
  - main column: evaluation categories and answers
  - secondary column: compact metadata, score summary, navigation, or review actions
- or a full-width layout with a multi-column metadata grid and well-spaced evaluation sections

Do not leave a large empty area inside the main card.

The content width should remain comfortable for reading. Avoid stretching long text across the entire screen.

### Mobile layout

On mobile:

- stack content naturally
- keep the player name and evaluation type prominent
- use a compact metadata grid or stacked key/value layout
- avoid oversized padding
- keep score and answer text readable
- ensure buttons are full-width or easy to tap
- avoid horizontal scrolling
- prevent long names, usernames, and cycle names from overflowing
- keep the report visually cohesive rather than looking like unrelated cards stacked endlessly

Test at:

- 320 px
- 375 px
- 390 px
- 430 px

## Evaluation answer design

Redesign the read-only answer sections.

Each category should have a clear section heading.

For each question, show:

- question text
- rating or score, if applicable
- text answer or comment, if present
- “Not answered” when appropriate
- optional/required status only if useful in the read-only view

For numeric ratings:

- make the score visually prominent
- show the scale where available, for example “2 / 5”
- do not rely on the number alone without context
- consider a compact rating badge, score pill, progress bar, or segmented scale
- ensure the design remains accessible and understandable without colour

For text answers:

- distinguish the question from the response
- preserve line breaks
- handle long comments gracefully
- avoid excessive empty vertical space

For unanswered questions:

- display a muted “Not answered” state
- do not show a misleading zero
- keep the unanswered state visually distinct from an actual low score

## Category summaries

If the existing data supports it without changing business logic, add useful category-level summaries such as:

- average rating for the category
- answered question count
- total rated questions

Do not invent or persist new scores. Use only values already available or safely computed in the presentation/read-model layer.

If category averages are not already available, determine whether they can be computed in the view/service layer without changing evaluation semantics.

Do not add database fields or migrations for visual summaries.

## Overall score summary

If the current evaluation data supports a meaningful overall average, consider showing:

- overall average rating
- number of rated questions
- a clear note that text-only or unanswered questions are excluded

Only do this if it accurately reflects the existing scoring model.

Do not create an overall score if the evaluation system intentionally avoids one or if categories use incompatible scales.

## Navigation and actions

Review the page-level actions.

Potential actions may include:

- Back to submitted evaluations
- Back to My Evaluations
- Reopen
- Edit
- Print
- Download
- Return to player profile

Only show actions supported by existing permissions and routes.

Requirements:

- primary and secondary actions should be visually distinct
- destructive or workflow-changing actions such as “Reopen” should not look identical to ordinary navigation
- mobile actions should stack cleanly
- desktop actions should align neatly
- action labels should not wrap awkwardly

Do not change permissions or workflow rules.

## Printability

Make the evaluation detail reasonably printable.

Add print CSS if appropriate so that:

- navigation and irrelevant buttons are hidden
- the report uses the page width well
- cards do not split awkwardly where avoidable
- text remains high contrast
- background-heavy decorative effects are reduced
- the player name, evaluation type, evaluator, and submission date remain visible
- category sections print cleanly

Do not build PDF generation unless it already exists.

## Shared components

Prefer reusable components and classes.

Potential shared patterns:

- `.evaluation-report`
- `.evaluation-report__header`
- `.evaluation-summary-grid`
- `.evaluation-meta-item`
- `.evaluation-category`
- `.evaluation-question`
- `.evaluation-score`
- `.evaluation-answer`
- `.evaluation-empty-answer`
- `.evaluation-actions`

Names may differ if the project already has established conventions.

Avoid large amounts of inline CSS.

Reuse existing:

- colour variables
- card styles
- badges
- buttons
- typography
- responsive breakpoints

Do not introduce a new CSS framework or JavaScript framework.

## Accessibility

Maintain or improve:

- semantic heading hierarchy
- readable contrast
- visible focus states
- logical reading order
- proper link and button semantics
- clear labels for scores
- accessible status text
- no colour-only meaning
- meaningful print output
- keyboard usability

If using visual rating bars or score pills, include text that communicates the same information.

## Scope control

Do not alter:

- evaluation business logic
- permissions
- account roles
- submission or reopen rules
- database models
- URL names
- scoring semantics
- import behavior
- authentication behavior

No migration should be required.

Do not expose private metadata, passwords, or internal identifiers.

## Audit process

Before implementing:

1. Inspect the exact URL, view, template, service/read model, and partials used by submitted evaluation detail pages.
2. Identify whether multiple detail pages share the same rendering structure.
3. Inspect existing CSS in:
   - `static/css/pdp.css`
   - `static/css/styles.css`
   - any analytics-specific stylesheet
4. Review current mobile breakpoints and responsive conventions.
5. Determine which changes can be shared across all read-only evaluation detail pages.
6. Preserve unrelated page behavior.

## Testing

Add or update focused tests for representative evaluation detail pages.

Tests should verify important structural markup, for example:

- report wrapper class
- summary section
- metadata items
- category section markup
- score display
- “Not answered” state
- action links where permissions allow

Do not write brittle tests that assert exact CSS rendering or every class name unnecessarily.

Run at least:

DJANGO_SECRET_KEY=test python manage.py check
DJANGO_SECRET_KEY=test python manage.py makemigrations --check
DJANGO_SECRET_KEY=test python manage.py test analytics
git diff --check

Also run the project’s Ruff and Black checks for changed Python files.

Run the full test suite if practical.

## Manual QA

Inspect representative evaluation detail pages at:

- 390 × 844
- 375 × 667
- 768 × 1024
- 1440 × 900

Test cases should include:

- player with a long name
- evaluator with a long name or username
- long cycle name
- peer evaluation
- self evaluation
- coach evaluation
- numeric ratings
- text comments
- optional unanswered question
- many categories
- category with only one question
- long text response
- user with and without staff actions

Confirm:

- no horizontal scrolling
- no large unexplained empty areas
- metadata uses desktop space effectively
- mobile spacing is compact but readable
- rating values are obvious
- unanswered questions are clear
- buttons remain accessible
- print preview is readable

## Documentation

Update:

docs/ui/responsive_design.md

Add a section describing the submitted evaluation report pattern, including:

- summary/header structure
- metadata grid
- question and answer hierarchy
- score presentation
- mobile behavior
- print behavior
- guidance for future read-only evaluation pages

Update the user manual only if the visible workflow or action placement changes materially.

## Git discipline

- Inspect the working tree first.
- Do not include unrelated changes.
- Preserve the existing unrelated uncommitted file:
  `/Users/eugenelin/dev/vmba0/docs/qa/platform_e2e/test_coaches_import.csv`
- Make focused commits with clear messages.
- Push to the current branch.
- Archive this prompt using the project’s normal prompt numbering and naming convention.
- Commit the prompt archive separately if that matches the existing project convention.

## Deliverables

When finished, provide:

1. A summary of the visual problems found.
2. The routes and templates reviewed.
3. The final layout approach.
4. Templates, CSS files, views, services, and tests changed.
5. Any shared components introduced.
6. How numeric, text, and unanswered questions are displayed.
7. Whether category or overall summaries were added and how they are calculated.
8. Desktop, tablet, mobile, and print behavior.
9. Tests and verification commands run.
10. Confirmation that no migration is required.
11. Deployment instructions, including whether `collectstatic` is required.
12. Commit hashes.
13. Any remaining limitations.

## Final standard

The completed submitted evaluation experience should look like a polished player development report, not a raw database detail page.

On desktop, it should use space intelligently, have clear hierarchy, and be easy to scan.

On mobile, it should feel compact, elegant, and natural to use without zooming, sideways scrolling, or deciphering dense blocks of text.
```

## Implementation Commit Diff

```diff
diff --git a/analytics/services/evaluation_access_service.py b/analytics/services/evaluation_access_service.py
index 11fd4de..a77a8b7 100644
--- a/analytics/services/evaluation_access_service.py
+++ b/analytics/services/evaluation_access_service.py
@@ -25,6 +25,12 @@ from analytics.services.permissions import (
     can_view_my_evaluation_detail,
     can_view_my_evaluations,
 )
+from analytics.services.evaluation_report_service import (
+    EvaluationReportCategorySummary,
+    EvaluationReportOverallSummary,
+    build_category_summaries,
+    build_overall_summary,
+)
 from players.models import Player
 
 
@@ -77,6 +83,8 @@ class MyEvaluationDetail:
     submitted_at: object
     cycle_name: str
     responses: list[MyEvaluationQuestionResponse]
+    category_summaries: list[EvaluationReportCategorySummary]
+    overall_summary: EvaluationReportOverallSummary
 
 
 def get_evaluation_target_list(user, params) -> EvaluationTargetList:
@@ -221,6 +229,7 @@ def get_my_evaluation_detail(user, observation_id: int) -> MyEvaluationDetail:
             is_active=True
         ).order_by("display_order", "id")
     ]
+    category_summaries = build_category_summaries(responses)
     return MyEvaluationDetail(
         observation_id=observation.id,
         player=observation.player,
@@ -229,4 +238,6 @@ def get_my_evaluation_detail(user, observation_id: int) -> MyEvaluationDetail:
         submitted_at=observation.submitted_at,
         cycle_name=observation.evaluation_cycle.name,
         responses=responses,
+        category_summaries=category_summaries,
+        overall_summary=build_overall_summary(category_summaries),
     )
diff --git a/analytics/services/evaluation_report_service.py b/analytics/services/evaluation_report_service.py
new file mode 100644
index 0000000..c9b64b6
--- /dev/null
+++ b/analytics/services/evaluation_report_service.py
@@ -0,0 +1,109 @@
+from __future__ import annotations
+
+from dataclasses import dataclass
+from decimal import Decimal
+from typing import Iterable, Protocol
+
+
+class EvaluationReportResponseLike(Protocol):
+    category: str
+    numeric_value: object
+    text_value: str
+
+
+@dataclass(frozen=True)
+class EvaluationReportCategorySummary:
+    name: str
+    responses: list[EvaluationReportResponseLike]
+    average_rating: Decimal | None
+    answered_count: int
+    rated_count: int
+    question_count: int
+
+
+@dataclass(frozen=True)
+class EvaluationReportOverallSummary:
+    average_rating: Decimal | None
+    answered_count: int
+    rated_count: int
+    question_count: int
+
+
+def _numeric_rating(value) -> Decimal | None:
+    if value is None:
+        return None
+    if isinstance(value, Decimal):
+        return value
+    try:
+        return Decimal(str(value))
+    except Exception:
+        return None
+
+
+def _has_answer(response: EvaluationReportResponseLike) -> bool:
+    return _numeric_rating(response.numeric_value) is not None or bool(
+        (response.text_value or "").strip()
+    )
+
+
+def _average(values: list[Decimal]) -> Decimal | None:
+    if not values:
+        return None
+    return sum(values, Decimal("0")) / Decimal(len(values))
+
+
+def build_category_summaries(
+    responses: Iterable[EvaluationReportResponseLike],
+) -> list[EvaluationReportCategorySummary]:
+    """Group consecutive report responses by category without changing display order."""
+    grouped: list[tuple[str, list[EvaluationReportResponseLike]]] = []
+    for response in responses:
+        category = response.category or "Questions"
+        if not grouped or grouped[-1][0] != category:
+            grouped.append((category, []))
+        grouped[-1][1].append(response)
+
+    summaries = []
+    for category, category_responses in grouped:
+        ratings = [
+            rating
+            for rating in (
+                _numeric_rating(response.numeric_value)
+                for response in category_responses
+            )
+            if rating is not None
+        ]
+        summaries.append(
+            EvaluationReportCategorySummary(
+                name=category,
+                responses=category_responses,
+                average_rating=_average(ratings),
+                answered_count=sum(
+                    1 for response in category_responses if _has_answer(response)
+                ),
+                rated_count=len(ratings),
+                question_count=len(category_responses),
+            )
+        )
+    return summaries
+
+
+def build_overall_summary(
+    category_summaries: Iterable[EvaluationReportCategorySummary],
+) -> EvaluationReportOverallSummary:
+    """Return an overall read-model summary from category summaries."""
+    summaries = list(category_summaries)
+    ratings = [
+        rating
+        for summary in summaries
+        for rating in (
+            _numeric_rating(response.numeric_value) for response in summary.responses
+        )
+        if rating is not None
+    ]
+    return EvaluationReportOverallSummary(
+        average_rating=_average(ratings),
+        answered_count=sum(summary.answered_count for summary in summaries),
+        rated_count=len(ratings),
+        question_count=sum(summary.question_count for summary in summaries),
+    )
diff --git a/analytics/services/evaluation_review_service.py b/analytics/services/evaluation_review_service.py
index b29d8f4..b91698d 100644
--- a/analytics/services/evaluation_review_service.py
+++ b/analytics/services/evaluation_review_service.py
@@ -18,6 +18,12 @@ from analytics.services.permissions import (
     can_review_submitted_evaluations,
     can_view_evaluation_review_detail,
 )
+from analytics.services.evaluation_report_service import (
+    EvaluationReportCategorySummary,
+    EvaluationReportOverallSummary,
+    build_category_summaries,
+    build_overall_summary,
+)
 from seasons.models import Season
 
 
@@ -72,6 +78,8 @@ class EvaluationReviewDetail:
     cycle_name: str
     submitted_at: object
     responses: list[EvaluationReviewQuestionResponse]
+    category_summaries: list[EvaluationReportCategorySummary]
+    overall_summary: EvaluationReportOverallSummary
 
 
 @dataclass(frozen=True)
@@ -246,6 +254,7 @@ def get_evaluation_review_detail(user, observation_id: int) -> EvaluationReviewD
             is_active=True
         ).order_by("display_order", "id")
     ]
+    category_summaries = build_category_summaries(responses)
     return EvaluationReviewDetail(
         observation_id=observation.id,
         player_name=observation.player.display_name,
@@ -261,4 +270,6 @@ def get_evaluation_review_detail(user, observation_id: int) -> EvaluationReviewD
         cycle_name=observation.evaluation_cycle.name,
         submitted_at=observation.submitted_at,
         responses=responses,
+        category_summaries=category_summaries,
+        overall_summary=build_overall_summary(category_summaries),
     )
diff --git a/analytics/templates/analytics/_evaluation_report.html b/analytics/templates/analytics/_evaluation_report.html
new file mode 100644
index 0000000..333a3b2
--- /dev/null
+++ b/analytics/templates/analytics/_evaluation_report.html
@@ -0,0 +1,125 @@
+<article class="evaluation-report">
+    <header class="evaluation-report__header">
+        <div class="evaluation-report__headline">
+            <p class="evaluation-report__eyebrow">{{ report_eyebrow|default:"Submitted Evaluation" }}</p>
+            <h2>{{ player_name }}</h2>
+            <div class="evaluation-report__badges" aria-label="Evaluation status">
+                <span class="evaluation-report__badge">{{ evaluation_type }}</span>
+                <span class="evaluation-report__badge evaluation-report__badge--submitted">Submitted</span>
+            </div>
+        </div>
+        <div class="evaluation-report__score-card">
+            <span class="evaluation-report__score-label">Overall rating</span>
+            {% if overall_summary.average_rating %}
+                <strong>{{ overall_summary.average_rating|floatformat:1 }} / 5</strong>
+                <span>{{ overall_summary.rated_count }} rated question{{ overall_summary.rated_count|pluralize }}</span>
+            {% else %}
+                <strong>Not rated</strong>
+                <span>No numeric ratings submitted</span>
+            {% endif %}
+        </div>
+    </header>
+
+    <section class="evaluation-report__meta-grid" aria-label="Evaluation context">
+        {% if evaluator_name %}
+            <div class="evaluation-report__meta-item">
+                <span>Evaluator</span>
+                <strong>{{ evaluator_name }}</strong>
+            </div>
+        {% endif %}
+        <div class="evaluation-report__meta-item">
+            <span>Evaluator Role</span>
+            <strong>{{ evaluator_role_name }}</strong>
+        </div>
+        <div class="evaluation-report__meta-item">
+            <span>Submitted</span>
+            <strong>{% if submitted_at %}{{ submitted_at|date:"M j, Y" }}{% else %}Not submitted{% endif %}</strong>
+        </div>
+        {% if season_name %}
+            <div class="evaluation-report__meta-item">
+                <span>Season</span>
+                <strong>{{ season_name }}</strong>
+            </div>
+        {% endif %}
+        {% if player_team %}
+            <div class="evaluation-report__meta-item">
+                <span>Team</span>
+                <strong>{{ player_team }}</strong>
+            </div>
+        {% endif %}
+        {% if player_division %}
+            <div class="evaluation-report__meta-item">
+                <span>Division</span>
+                <strong>{{ player_division }}</strong>
+            </div>
+        {% endif %}
+        <div class="evaluation-report__meta-item evaluation-report__meta-item--wide">
+            <span>Cycle</span>
+            <strong>{{ cycle_name }}</strong>
+        </div>
+    </section>
+
+    <section class="evaluation-report__summary-strip" aria-label="Evaluation answer summary">
+        <div>
+            <span>Questions answered</span>
+            <strong>{{ overall_summary.answered_count }} / {{ overall_summary.question_count }}</strong>
+        </div>
+        <div>
+            <span>Rated questions</span>
+            <strong>{{ overall_summary.rated_count }}</strong>
+        </div>
+        <p>Overall and category ratings average numeric answers only. Text-only and unanswered questions are excluded.</p>
+    </section>
+
+    <section class="evaluation-report__body" aria-label="Evaluation answers">
+        {% for category in category_summaries %}
+            <section class="evaluation-category">
+                <header class="evaluation-category__header">
+                    <div>
+                        <p class="evaluation-report__eyebrow">Category</p>
+                        <h3>{{ category.name }}</h3>
+                    </div>
+                    <div class="evaluation-category__summary">
+                        {% if category.average_rating %}
+                            <strong>{{ category.average_rating|floatformat:1 }} / 5</strong>
+                            <span>{{ category.rated_count }} rated · {{ category.answered_count }} / {{ category.question_count }} answered</span>
+                        {% else %}
+                            <strong>No rating</strong>
+                            <span>{{ category.answered_count }} / {{ category.question_count }} answered</span>
+                        {% endif %}
+                    </div>
+                </header>
+                <div class="evaluation-question-list">
+                    {% for response in category.responses %}
+                        <article class="evaluation-question">
+                            <div class="evaluation-question__prompt">
+                                <h4>{{ response.question_prompt }}</h4>
+                                {% if not response.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
+                            </div>
+                            {% if response.numeric_value %}
+                                <div class="evaluation-question__score" aria-label="Rating {{ response.numeric_value|floatformat:0 }} out of 5">
+                                    <strong>{{ response.numeric_value|floatformat:0 }}</strong>
+                                    <span>/ 5</span>
+                                </div>
+                            {% elif response.text_value %}
+                                <div class="evaluation-question__answer">
+                                    <span>Comment</span>
+                                    <p>{{ response.text_value|linebreaksbr }}</p>
+                                </div>
+                            {% else %}
+                                <div class="evaluation-question__empty">Not answered</div>
+                            {% endif %}
+                        </article>
+                    {% endfor %}
+                </div>
+            </section>
+        {% empty %}
+            <div class="evaluation-report__empty">No responses are available.</div>
+        {% endfor %}
+    </section>
+
+    <footer class="evaluation-actions">
+        <a class="button button--ghost" href="{{ back_url }}">{{ back_label|default:"Back" }}</a>
+        <button class="button button--secondary evaluation-actions__print" type="button" onclick="window.print()">Print</button>
+    </footer>
+</article>
diff --git a/analytics/templates/analytics/assessment_detail.html b/analytics/templates/analytics/assessment_detail.html
index 8eccba8..6e3d573 100644
--- a/analytics/templates/analytics/assessment_detail.html
+++ b/analytics/templates/analytics/assessment_detail.html
@@ -4,39 +4,96 @@
 {% block analytics_subtitle %}{{ observation.evaluation_cycle.name }} · {{ observation.get_status_display }}{% endblock %}
 
 {% block analytics_content %}
-<article class="pdp-card">
-    <h2>Assessment</h2>
-    <p>Type: {{ observation.evaluation_perspective_label }}</p>
-    <p>Season: {{ observation.season_name_snapshot|default:"Legacy / No Season" }}</p>
-    <p>Roster: {{ observation.player_division_snapshot|default:observation.player.division }} {{ observation.player_team_name_snapshot|default:observation.player.team_name }}</p>
-    {% if observation.evaluator_team_name_snapshot %}
-        <p>Evaluator Assignment: {{ observation.evaluator_assignment_role_snapshot }} · {{ observation.evaluator_division_snapshot }} {{ observation.evaluator_team_name_snapshot }}</p>
-    {% endif %}
-    <p>Evaluator: {{ observation.evaluator }} · Role: {{ observation.evaluator_role_name }}</p>
-    {% if observation.submitted_at %}<p>Submitted: {{ observation.submitted_at }}</p>{% endif %}
-    {% for group in question_groups %}
-        <section class="pdp-list__item pdp-list__item--stack">
-            <h3>{{ group.category }}</h3>
-            {% for item in group.questions %}
-                <div>
-                    <strong>{{ item.question.prompt }}</strong>
-                    {% if not item.question.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
-                    {% if item.response %}
-                        {% if item.response.numeric_value %}
-                            <span>{{ item.response.numeric_value|floatformat:0 }}</span>
-                        {% else %}
-                            <p>{{ item.response.text_value }}</p>
-                        {% endif %}
-                    {% else %}
-                        <span>Not answered</span>
-                    {% endif %}
+<article class="evaluation-report">
+    <header class="evaluation-report__header">
+        <div class="evaluation-report__headline">
+            <p class="evaluation-report__eyebrow">Evaluation Detail</p>
+            <h2>{{ observation.player.display_name }}</h2>
+            <div class="evaluation-report__badges" aria-label="Evaluation status">
+                <span class="evaluation-report__badge">{{ observation.evaluation_perspective_label }}</span>
+                <span class="evaluation-report__badge{% if observation.status == 'submitted' %} evaluation-report__badge--submitted{% endif %}">{{ observation.get_status_display }}</span>
+            </div>
+        </div>
+        <div class="evaluation-report__score-card">
+            <span class="evaluation-report__score-label">Workflow status</span>
+            <strong>{{ observation.get_status_display }}</strong>
+            <span>{{ observation.evaluation_cycle.name }}</span>
+        </div>
+    </header>
+
+    <section class="evaluation-report__meta-grid" aria-label="Evaluation context">
+        <div class="evaluation-report__meta-item">
+            <span>Evaluator</span>
+            <strong>{{ observation.evaluator }}</strong>
+        </div>
+        <div class="evaluation-report__meta-item">
+            <span>Evaluator role</span>
+            <strong>{{ observation.evaluator_role_name }}</strong>
+        </div>
+        <div class="evaluation-report__meta-item">
+            <span>Season</span>
+            <strong>{{ observation.season_name_snapshot|default:"Legacy / No Season" }}</strong>
+        </div>
+        <div class="evaluation-report__meta-item">
+            <span>Roster</span>
+            <strong>{{ observation.player_division_snapshot|default:observation.player.division }} {{ observation.player_team_name_snapshot|default:observation.player.team_name }}</strong>
+        </div>
+        {% if observation.evaluator_team_name_snapshot %}
+            <div class="evaluation-report__meta-item evaluation-report__meta-item--wide">
+                <span>Evaluator assignment</span>
+                <strong>{{ observation.evaluator_assignment_role_snapshot }} · {{ observation.evaluator_division_snapshot }} {{ observation.evaluator_team_name_snapshot }}</strong>
+            </div>
+        {% endif %}
+        <div class="evaluation-report__meta-item evaluation-report__meta-item--wide">
+            <span>Submitted</span>
+            <strong>{% if observation.submitted_at %}{{ observation.submitted_at|date:"M j, Y" }}{% else %}Not submitted{% endif %}</strong>
+        </div>
+    </section>
+
+    <section class="evaluation-report__body" aria-label="Evaluation answers">
+        {% for group in question_groups %}
+            <section class="evaluation-category">
+                <header class="evaluation-category__header">
+                    <div>
+                        <p class="evaluation-report__eyebrow">Category</p>
+                        <h3>{{ group.category }}</h3>
+                    </div>
+                </header>
+                <div class="evaluation-question-list">
+                    {% for item in group.questions %}
+                        <article class="evaluation-question">
+                            <div class="evaluation-question__prompt">
+                                <h4>{{ item.question.prompt }}</h4>
+                                {% if not item.question.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
+                            </div>
+                            {% if item.response %}
+                                {% if item.response.numeric_value %}
+                                    <div class="evaluation-question__score" aria-label="Rating {{ item.response.numeric_value|floatformat:0 }} out of 5">
+                                        <strong>{{ item.response.numeric_value|floatformat:0 }}</strong>
+                                        <span>/ 5</span>
+                                    </div>
+                                {% else %}
+                                    <div class="evaluation-question__answer">
+                                        <span>Comment</span>
+                                        <p>{{ item.response.text_value|linebreaksbr }}</p>
+                                    </div>
+                                {% endif %}
+                            {% else %}
+                                <div class="evaluation-question__empty">Not answered</div>
+                            {% endif %}
+                        </article>
+                    {% endfor %}
                 </div>
-            {% endfor %}
-        </section>
-    {% endfor %}
-    {% if can_edit %}
-        <a class="button button--primary" href="{% url 'analytics:assessment-edit' observation_id=observation.id %}">Edit</a>
-    {% endif %}
-    <a class="button button--ghost" href="{{ back_url }}">Back</a>
+            </section>
+        {% endfor %}
+    </section>
+
+    <footer class="evaluation-actions">
+        {% if can_edit %}
+            <a class="button button--primary" href="{% url 'analytics:assessment-edit' observation_id=observation.id %}">Edit</a>
+        {% endif %}
+        <a class="button button--ghost" href="{{ back_url }}">Back</a>
+        <button class="button button--ghost evaluation-actions__print" type="button" onclick="window.print()">Print</button>
+    </footer>
 </article>
 {% endblock %}
diff --git a/analytics/templates/analytics/evaluation_review_detail.html b/analytics/templates/analytics/evaluation_review_detail.html
index b67afd7..281cdd2 100644
--- a/analytics/templates/analytics/evaluation_review_detail.html
+++ b/analytics/templates/analytics/evaluation_review_detail.html
@@ -4,46 +4,6 @@
 {% block analytics_subtitle %}{{ detail.player_name }} · {{ detail.cycle_name }}{% endblock %}
 
 {% block analytics_content %}
-<article class="pdp-card">
-    <h2>Submitted Evaluation</h2>
-    <dl class="pdp-definition-list">
-        <dt>Player</dt>
-        <dd>{{ detail.player_name }}</dd>
-        <dt>Season</dt>
-        <dd>{{ detail.season_name }}</dd>
-        <dt>Team</dt>
-        <dd>{{ detail.player_team }}</dd>
-        <dt>Division</dt>
-        <dd>{{ detail.player_division }}</dd>
-        <dt>Evaluator</dt>
-        <dd>{{ detail.evaluator_name }}</dd>
-        <dt>Evaluator Role</dt>
-        <dd>{{ detail.evaluator_role_name }}</dd>
-        <dt>Type</dt>
-        <dd>{{ detail.evaluation_perspective_label }}</dd>
-        <dt>Cycle</dt>
-        <dd>{{ detail.cycle_name }}</dd>
-        <dt>Submitted</dt>
-        <dd>{{ detail.submitted_at|date:"M j, Y" }}</dd>
-    </dl>
-    {% for response in detail.responses %}
-        <section class="pdp-list__item pdp-list__item--stack">
-            <h3>{{ response.category }}</h3>
-            <div>
-                <strong>{{ response.question_prompt }}</strong>
-                {% if not response.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
-                {% if response.numeric_value %}
-                    <span>{{ response.numeric_value|floatformat:0 }}</span>
-                {% elif response.text_value %}
-                    <p>{{ response.text_value }}</p>
-                {% else %}
-                    <span>Not answered</span>
-                {% endif %}
-            </div>
-        </section>
-    {% empty %}
-        <p>No responses are available.</p>
-    {% endfor %}
-    <a class="button button--ghost" href="{% url 'analytics:evaluation-review-list' %}">Back</a>
-</article>
+{% url 'analytics:evaluation-review-list' as evaluation_review_list_url %}
+{% include "analytics/_evaluation_report.html" with report_eyebrow="Evaluation Review" player_name=detail.player_name evaluation_type=detail.evaluation_perspective_label evaluator_name=detail.evaluator_name evaluator_role_name=detail.evaluator_role_name submitted_at=detail.submitted_at season_name=detail.season_name player_team=detail.player_team player_division=detail.player_division cycle_name=detail.cycle_name category_summaries=detail.category_summaries overall_summary=detail.overall_summary back_url=evaluation_review_list_url back_label="Back to submitted evaluations" %}
 {% endblock %}
diff --git a/analytics/templates/analytics/my_evaluation_detail.html b/analytics/templates/analytics/my_evaluation_detail.html
index b125db2..c06032f 100644
--- a/analytics/templates/analytics/my_evaluation_detail.html
+++ b/analytics/templates/analytics/my_evaluation_detail.html
@@ -4,36 +4,6 @@
 {% block analytics_subtitle %}{{ detail.cycle_name }} · Submitted evaluation{% endblock %}
 
 {% block analytics_content %}
-<article class="pdp-card">
-    <h2>Evaluation</h2>
-    <dl class="pdp-definition-list">
-        <dt>Player</dt>
-        <dd>{{ detail.player.display_name }}</dd>
-        <dt>Type</dt>
-        <dd>{{ detail.evaluation_perspective_label }}</dd>
-        <dt>Evaluator Role</dt>
-        <dd>{{ detail.evaluator_role_name }}</dd>
-        <dt>Submitted</dt>
-        <dd>{{ detail.submitted_at|date:"M j, Y" }}</dd>
-    </dl>
-    {% for response in detail.responses %}
-        <section class="pdp-list__item pdp-list__item--stack">
-            <h3>{{ response.category }}</h3>
-            <div>
-                <strong>{{ response.question_prompt }}</strong>
-                {% if not response.is_required %}<span class="pdp-badge pdp-badge--muted">Optional</span>{% endif %}
-                {% if response.numeric_value %}
-                    <span>{{ response.numeric_value|floatformat:0 }}</span>
-                {% elif response.text_value %}
-                    <p>{{ response.text_value }}</p>
-                {% else %}
-                    <span>Not answered</span>
-                {% endif %}
-            </div>
-        </section>
-    {% empty %}
-        <p>No responses are available.</p>
-    {% endfor %}
-    <a class="button button--ghost" href="{% url 'analytics:my-evaluations' %}">Back</a>
-</article>
+{% url 'analytics:my-evaluations' as my_evaluations_url %}
+{% include "analytics/_evaluation_report.html" with report_eyebrow="My Evaluation" player_name=detail.player.display_name evaluation_type=detail.evaluation_perspective_label evaluator_role_name=detail.evaluator_role_name submitted_at=detail.submitted_at cycle_name=detail.cycle_name category_summaries=detail.category_summaries overall_summary=detail.overall_summary back_url=my_evaluations_url back_label="Back to My Evaluations" %}
 {% endblock %}
diff --git a/analytics/tests/test_coach_assessments.py b/analytics/tests/test_coach_assessments.py
index e247374..7ee1fbc 100644
--- a/analytics/tests/test_coach_assessments.py
+++ b/analytics/tests/test_coach_assessments.py
@@ -409,6 +409,9 @@ class CoachAssessmentWorkflowTests(TestCase):
         )
 
         self.assertEqual(response.status_code, 200)
+        self.assertContains(response, 'class="evaluation-report"')
+        self.assertContains(response, "Workflow status")
+        self.assertContains(response, 'class="evaluation-question"')
         self.assertContains(
             response,
             reverse(
diff --git a/analytics/tests/test_evaluation_review.py b/analytics/tests/test_evaluation_review.py
index 41c596c..3345b14 100644
--- a/analytics/tests/test_evaluation_review.py
+++ b/analytics/tests/test_evaluation_review.py
@@ -199,6 +199,12 @@ class EvaluationReviewViewTests(TestCase):
         self.assertContains(response, optional_question.prompt)
         self.assertContains(response, "Optional")
         self.assertContains(response, "Not answered")
+        self.assertContains(response, 'class="evaluation-report"')
+        self.assertContains(response, "Overall rating")
+        self.assertContains(response, "Questions answered")
+        self.assertContains(response, "numeric answers only")
+        self.assertContains(response, 'class="evaluation-category"')
+        self.assertContains(response, 'class="evaluation-question__empty"')
 
     def test_coach_review_access_rules(self):
         self.submitted_observation()
@@ -365,6 +371,7 @@ class EvaluationReviewViewTests(TestCase):
         self.assertContains(response, "Casey Coach")
         self.assertContains(response, "Coach")
         self.assertContains(response, "Review detail note.")
+        self.assertContains(response, 'class="evaluation-report__meta-grid"')
         self.assertNotContains(response, self.coach.email)
         self.assertNotContains(response, "Reopen")
         self.assertEqual(post_response.status_code, 405)
diff --git a/analytics/tests/test_my_evaluations.py b/analytics/tests/test_my_evaluations.py
index 16a3f55..677c631 100644
--- a/analytics/tests/test_my_evaluations.py
+++ b/analytics/tests/test_my_evaluations.py
@@ -208,6 +208,9 @@ class MyEvaluationsViewTests(TestCase):
         self.assertContains(response, optional_question.prompt)
         self.assertContains(response, "Optional")
         self.assertContains(response, "Not answered")
+        self.assertContains(response, 'class="evaluation-report"')
+        self.assertContains(response, "Overall rating")
+        self.assertContains(response, 'class="evaluation-question__empty"')
         self.assertFalse(optional_response.is_required)
         self.assertIsNone(optional_response.numeric_value)
 
diff --git a/docs/ui/responsive_design.md b/docs/ui/responsive_design.md
index bd7b078..c016352 100644
--- a/docs/ui/responsive_design.md
+++ b/docs/ui/responsive_design.md
@@ -67,6 +67,53 @@ on mobile, with full-width inputs and buttons where practical.
 The PDP-style form utility `.pdp-form` uses a responsive grid so labels and
 controls remain readable on mobile without fixed widths.
 
+## Evaluation Report Detail Pages
+
+Submitted/read-only evaluation detail pages should use the report pattern rather
+than a plain definition list. This pattern is intended for:
+
+- submitted evaluation review
+- My Evaluations detail
+- coach assessment detail
+- staff observation review detail
+
+Use the shared `.evaluation-report` structure when rendering read-only
+evaluation results.
+
+The report should include:
+
+- a strong header with player name, evaluation type, and submitted/status badge
+- a compact metadata grid for evaluator, role, season, team, division, cycle, and
+  submitted date
+- an optional score summary that averages numeric rating answers only
+- category sections with category-level summaries when numeric data exists
+- question cards where the question text is visually distinct from the score or
+  text answer
+- a muted `Not answered` state for unanswered questions
+- actions grouped in `.evaluation-actions`
+
+Score presentation:
+
+- show numeric ratings as `N / 5`
+- never display unanswered ratings as zero
+- explain that averages exclude text-only and unanswered questions
+- keep score text understandable without relying on colour
+
+Mobile behavior:
+
+- the header, metadata grid, category summaries, and question cards stack below
+  `640px`
+- action buttons should be full width on mobile
+- long player names, evaluator names, usernames, and cycle names must wrap safely
+- no horizontal scrolling should be required
+
+Print behavior:
+
+- hide navigation and report actions
+- reduce decorative backgrounds and shadows
+- keep the player name, evaluation type, context, and answers visible
+- avoid splitting category and question cards where practical
+
 ## Pages Converted To Mobile Cards
 
 The responsive card pattern is used across representative high-traffic workflows:
diff --git a/static/css/pdp.css b/static/css/pdp.css
index c983550..30a1078 100644
--- a/static/css/pdp.css
+++ b/static/css/pdp.css
@@ -266,6 +266,299 @@
     gap: 0.45rem;
 }
 
+.evaluation-report {
+    display: grid;
+    gap: 1.25rem;
+    max-width: 1120px;
+    margin: 0 auto;
+    padding: 1.25rem;
+    border: 1px solid rgba(16, 42, 67, 0.08);
+    border-radius: 30px;
+    background:
+        linear-gradient(180deg, rgba(237, 244, 255, 0.96), rgba(255, 255, 255, 0.98)),
+        #fff;
+    box-shadow: 0 24px 70px rgba(16, 42, 67, 0.12);
+}
+
+.evaluation-report__header {
+    display: grid;
+    grid-template-columns: minmax(0, 1fr) minmax(13rem, 0.28fr);
+    gap: 1rem;
+    align-items: stretch;
+}
+
+.evaluation-report__headline,
+.evaluation-report__score-card,
+.evaluation-report__meta-grid,
+.evaluation-report__summary-strip,
+.evaluation-category {
+    border: 1px solid rgba(16, 42, 67, 0.08);
+    background: rgba(255, 255, 255, 0.9);
+}
+
+.evaluation-report__headline {
+    display: grid;
+    align-content: center;
+    gap: 0.8rem;
+    padding: 1.45rem;
+    border-radius: 24px;
+}
+
+.evaluation-report__eyebrow {
+    margin: 0;
+    font-size: 0.74rem;
+    font-weight: 800;
+    letter-spacing: 0.12em;
+    text-transform: uppercase;
+    color: var(--color-text-muted);
+}
+
+.evaluation-report__headline h2 {
+    margin: 0;
+    max-width: 48rem;
+    color: var(--color-navy);
+    font-size: clamp(2rem, 4vw, 3.25rem);
+    line-height: 1;
+    overflow-wrap: anywhere;
+}
+
+.evaluation-report__badges {
+    display: flex;
+    flex-wrap: wrap;
+    gap: 0.5rem;
+}
+
+.evaluation-report__badge {
+    display: inline-flex;
+    align-items: center;
+    min-height: 2rem;
+    padding: 0.38rem 0.72rem;
+    border-radius: 999px;
+    background: rgba(47, 111, 235, 0.1);
+    color: var(--color-navy);
+    font-weight: 800;
+    line-height: 1.1;
+}
+
+.evaluation-report__badge--submitted {
+    background: rgba(42, 157, 94, 0.12);
+    color: #17613a;
+}
+
+.evaluation-report__score-card {
+    display: grid;
+    align-content: center;
+    gap: 0.35rem;
+    padding: 1.25rem;
+    border-radius: 24px;
+}
+
+.evaluation-report__score-label,
+.evaluation-report__score-card span,
+.evaluation-category__summary span,
+.evaluation-report__summary-strip span,
+.evaluation-report__meta-item span,
+.evaluation-question__answer span {
+    color: var(--color-text-muted);
+    font-size: 0.8rem;
+    font-weight: 800;
+    letter-spacing: 0.08em;
+    text-transform: uppercase;
+}
+
+.evaluation-report__score-card strong {
+    color: var(--color-navy);
+    font-size: clamp(2rem, 4vw, 3rem);
+    line-height: 1;
+}
+
+.evaluation-report__meta-grid {
+    display: grid;
+    grid-template-columns: repeat(4, minmax(0, 1fr));
+    gap: 0.75rem;
+    padding: 1rem;
+    border-radius: 24px;
+}
+
+.evaluation-report__meta-item {
+    display: grid;
+    gap: 0.25rem;
+    min-width: 0;
+    padding: 0.85rem;
+    border-radius: 18px;
+    background: rgba(240, 245, 255, 0.82);
+}
+
+.evaluation-report__meta-item--wide {
+    grid-column: span 2;
+}
+
+.evaluation-report__meta-item strong {
+    color: var(--color-navy);
+    line-height: 1.25;
+    overflow-wrap: anywhere;
+}
+
+.evaluation-report__summary-strip {
+    display: grid;
+    grid-template-columns: minmax(9rem, auto) minmax(8rem, auto) minmax(0, 1fr);
+    gap: 1rem;
+    align-items: center;
+    padding: 1rem;
+    border-radius: 22px;
+}
+
+.evaluation-report__summary-strip div {
+    display: grid;
+    gap: 0.2rem;
+}
+
+.evaluation-report__summary-strip strong {
+    color: var(--color-navy);
+    font-size: 1.25rem;
+}
+
+.evaluation-report__summary-strip p {
+    margin: 0;
+    color: var(--color-text-muted);
+}
+
+.evaluation-report__body {
+    display: grid;
+    gap: 1rem;
+}
+
+.evaluation-category {
+    display: grid;
+    gap: 1rem;
+    padding: 1rem;
+    border-radius: 24px;
+}
+
+.evaluation-category__header {
+    display: flex;
+    align-items: center;
+    justify-content: space-between;
+    gap: 1rem;
+    padding-bottom: 0.85rem;
+    border-bottom: 1px solid rgba(16, 42, 67, 0.08);
+}
+
+.evaluation-category__header h3 {
+    margin: 0.15rem 0 0;
+    color: var(--color-navy);
+    font-size: 1.35rem;
+}
+
+.evaluation-category__summary {
+    display: grid;
+    justify-items: end;
+    gap: 0.2rem;
+    text-align: right;
+}
+
+.evaluation-category__summary strong {
+    color: var(--color-navy);
+    font-size: 1.35rem;
+}
+
+.evaluation-question-list {
+    display: grid;
+    gap: 0.75rem;
+}
+
+.evaluation-question {
+    display: grid;
+    grid-template-columns: minmax(0, 1fr) minmax(6.5rem, auto);
+    gap: 1rem;
+    align-items: center;
+    padding: 1rem;
+    border: 1px solid rgba(16, 42, 67, 0.07);
+    border-radius: 18px;
+    background: rgba(255, 255, 255, 0.88);
+}
+
+.evaluation-question__prompt {
+    display: flex;
+    flex-wrap: wrap;
+    gap: 0.45rem 0.6rem;
+    align-items: center;
+    min-width: 0;
+}
+
+.evaluation-question__prompt h4 {
+    flex-basis: 100%;
+    margin: 0;
+    color: var(--color-navy);
+    font-size: 1rem;
+    line-height: 1.35;
+    overflow-wrap: anywhere;
+}
+
+.evaluation-question__score {
+    display: inline-flex;
+    align-items: baseline;
+    justify-content: center;
+    gap: 0.2rem;
+    min-width: 5.25rem;
+    padding: 0.7rem 0.85rem;
+    border-radius: 18px;
+    background: linear-gradient(180deg, rgba(47, 111, 235, 0.16), rgba(47, 111, 235, 0.08));
+    color: var(--color-navy);
+    font-weight: 800;
+    white-space: nowrap;
+}
+
+.evaluation-question__score strong {
+    font-size: 1.7rem;
+    line-height: 1;
+}
+
+.evaluation-question__answer {
+    display: grid;
+    grid-column: 1 / -1;
+    gap: 0.35rem;
+    padding: 0.9rem;
+    border-radius: 16px;
+    background: rgba(240, 245, 255, 0.72);
+}
+
+.evaluation-question__answer p {
+    margin: 0;
+    color: var(--color-text);
+    line-height: 1.55;
+    overflow-wrap: anywhere;
+}
+
+.evaluation-question__empty {
+    justify-self: end;
+    padding: 0.55rem 0.75rem;
+    border-radius: 999px;
+    background: rgba(16, 42, 67, 0.06);
+    color: var(--color-text-muted);
+    font-weight: 800;
+    white-space: nowrap;
+}
+
+.evaluation-report__empty {
+    padding: 1rem;
+    border-radius: 18px;
+    background: rgba(255, 255, 255, 0.9);
+    color: var(--color-text-muted);
+    font-weight: 700;
+}
+
+.evaluation-actions {
+    display: flex;
+    flex-wrap: wrap;
+    gap: 0.75rem;
+    justify-content: flex-end;
+}
+
+.evaluation-actions .button {
+    min-height: 44px;
+}
+
 .table-wrap {
     overflow-x: auto;
     -webkit-overflow-scrolling: touch;
@@ -309,6 +602,15 @@
     .pdp-nav {
         justify-content: flex-start;
     }
+
+    .evaluation-report__header,
+    .evaluation-report__summary-strip {
+        grid-template-columns: minmax(0, 1fr);
+    }
+
+    .evaluation-report__meta-grid {
+        grid-template-columns: repeat(2, minmax(0, 1fr));
+    }
 }
 
 @media (max-width: 640px) {
@@ -359,6 +661,67 @@
         width: 100%;
     }
 
+    .evaluation-report {
+        gap: 1rem;
+        padding: 0.8rem;
+        border-radius: 22px;
+    }
+
+    .evaluation-report__headline,
+    .evaluation-report__score-card,
+    .evaluation-report__meta-grid,
+    .evaluation-report__summary-strip,
+    .evaluation-category {
+        border-radius: 18px;
+    }
+
+    .evaluation-report__headline,
+    .evaluation-report__score-card,
+    .evaluation-category {
+        padding: 1rem;
+    }
+
+    .evaluation-report__meta-grid {
+        grid-template-columns: minmax(0, 1fr);
+        gap: 0.6rem;
+        padding: 0.75rem;
+    }
+
+    .evaluation-report__meta-item--wide {
+        grid-column: auto;
+    }
+
+    .evaluation-category__header {
+        align-items: stretch;
+        flex-direction: column;
+    }
+
+    .evaluation-category__summary {
+        justify-items: start;
+        text-align: left;
+    }
+
+    .evaluation-question {
+        grid-template-columns: minmax(0, 1fr);
+        gap: 0.75rem;
+        padding: 0.85rem;
+    }
+
+    .evaluation-question__score,
+    .evaluation-question__empty {
+        justify-self: stretch;
+    }
+
+    .evaluation-actions {
+        align-items: stretch;
+        flex-direction: column;
+    }
+
+    .evaluation-actions .button {
+        width: 100%;
+        justify-content: center;
+    }
+
     .table-wrap--cards {
         border-radius: 0;
     }
@@ -488,3 +851,39 @@
         flex-basis: 100%;
     }
 }
+
+@media print {
+    .pdp-hero,
+    .pdp-nav,
+    .evaluation-actions {
+        display: none !important;
+    }
+
+    .pdp-shell,
+    .pdp-app {
+        max-width: none;
+        padding: 0;
+    }
+
+    .evaluation-report,
+    .evaluation-report__headline,
+    .evaluation-report__score-card,
+    .evaluation-report__meta-grid,
+    .evaluation-report__summary-strip,
+    .evaluation-category,
+    .evaluation-question {
+        border-color: #b8c3cf;
+        background: #fff;
+        box-shadow: none;
+    }
+
+    .evaluation-report {
+        max-width: none;
+        padding: 0;
+    }
+
+    .evaluation-category,
+    .evaluation-question {
+        break-inside: avoid;
+    }
+}
```
