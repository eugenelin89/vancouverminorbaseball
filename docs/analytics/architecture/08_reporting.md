# 08 Reporting

## Reporting Philosophy

Do not implement a reporting engine in Version 1.

Version 1 reports should remain simple, server-rendered summaries and tables.

Report calculations should live in reusable services, such as `analytics.services.reporting_service` and `analytics.services.metrics_service`, so future reporting can build on the same logic.

## Version 1 Metrics

Version 1 should support practical coach-assessment summaries such as:

- observation counts
- completion status by coach/evaluator
- assessment count by player
- assessment count by evaluator role
- average score by category
- average score by evaluator role
- coach-to-coach score variance by player/category
- players whose coach-assessed expected round differs from actual draft selection
- players with unmatched draft records

## Future Reporting Concepts

Future reporting concepts may include:

- saved filters
- report definitions
- report runs
- advanced reporting

These are not implemented in Version 1.

## Future AI

Future AI modules should consume analytics data through service-layer APIs. AI should not be embedded inside analytics business logic.

Possible future AI capabilities include:

- player feedback
- video summaries
- trend detection
- development recommendations
- report generation

Do not implement AI workflows in Version 1.
