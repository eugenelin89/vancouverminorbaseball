Adjust the Phase 7 engineering plan only.

Do NOT implement application code.

File to update:
- docs/analytics/implementation/engineering/phase_07_command_center.md

Also inspect:
- docs/analytics/implementation/
- docs/analytics/implementation/STATUS.md

Make these documentation-only adjustments:

1. Add a dedicated player service boundary

Add `analytics/services/player_service.py` to the Phase 7 plan as the owner of reusable player search/filter logic.

Clarify:
- player search/filtering should move out of `comparison_service`
- Player Search, Player Profile, Comparison, and Reporting should reuse `player_service`
- `comparison_service` should focus only on comparison/score summaries
- reporting should not duplicate player search/filtering logic

2. Clarify metrics/reporting separation

Update the plan so:
- `metrics_service.py` computes counts, averages, summaries, and metric rows
- `reporting_service.py` only assembles command center read models/cards/navigation from metrics service results
- reporting_service should not contain raw aggregation logic

3. Clarify draft matching responsibility

Update the plan so:
- `metrics_service.py` may call `draft_service` for `DraftContext` read models
- `metrics_service.py` must not duplicate draft matching rules
- draft matching remains owned by `analytics.services.draft_service`

4. Keep CommandCenterContext structured

Clarify that `CommandCenterContext` should remain a small top-level object containing grouped dataclasses:
- summary_cards
- completion_summary
- observation_summary
- import_summary
- draft_summary
- recent_observations
- navigation_links
- generated_at

Do not add many flat fields to `CommandCenterContext`.

5. Fix Phase 7 tracking document filename references

The engineering plan currently references:
- docs/analytics/implementation/phase_07_command_center_reporting.md

Inspect the actual files under docs/analytics/implementation/.

If the actual Phase 7 tracking document has a different name, update all references in the engineering plan to match the real filename.

If no Phase 7 tracking document exists, explicitly state in the engineering plan that it is missing and should be created before implementation.

6. Final report

Report:
- files modified
- what documentation decisions changed
- whether the Phase 7 tracking document exists
- confirmation that no application code was implemented