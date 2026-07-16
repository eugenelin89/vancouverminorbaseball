# Platform V2 Product Planning

Platform V2 is the next product phase for the VCB Platform.

Status:

```text
Phase 0 planning complete.
No Platform V2 application code has been implemented.
```

## Product Direction

Platform V2 is centered on Player Development Intelligence:

> Help players, coaches, and staff understand development over time and turn evaluations into clear, evidence-based next steps.

Platform V2 should build on the completed Platform V1 foundations:

- canonical player identity in `players`;
- account identity and user-player links in `accounts`;
- season-aware rosters and coach assignments in `seasons`;
- submitted evaluations, perspectives, snapshots, timelines, comparisons, and review surfaces in `analytics`;
- legacy PDP coexistence without making PDP the dependency target for new work.

## Phase 0 Decision Summary

- The first implementation phase should be Player Development Summary V1.
- The first implementation should be deterministic and non-AI.
- Summaries should be computed read models at first, not persisted summary records.
- A future `development` Django app is recommended as the Platform V2 bounded context.
- The `development` app should consume `analytics`, `players`, `accounts`, and `seasons` services rather than duplicating their rules.
- PDP should remain legacy/transitionary. Platform V2 should not depend on `pdp.PlayerProfile` or PDP development models.
- Parent access, AI-generated summaries, report exports, rankings, and development-plan persistence are deferred.

## Phase 1A Decision Summary

- Player Development Summary V1 engineering planning is complete.
- Implementation has not started.
- Future implementation should create a `development` app with no models and no migrations.
- Summary output should use submitted, season-scoped `coach_assessment` observations only.
- Category averages may display from one valid rating, but strength/opportunity labels require at least two valid ratings.
- Player-safe summaries hide evaluator identity and peer free-text comments.
- Coach access reuses current broad coach-review access; strict team scoping remains deferred.

## Planning Documents

- [Platform V2 Roadmap](../PLATFORM_V2_ROADMAP.md)
- [Phase 0 Engineering Plan](implementation/engineering/platform_v2_phase_0_plan.md)
- [Player Development Summary V1 Engineering Plan](implementation/engineering/player_development_summary_v1.md)

## Implementation Rule

Do not implement Platform V2 from the roadmap alone. Create or update an approved phase-specific engineering plan before writing application code.
