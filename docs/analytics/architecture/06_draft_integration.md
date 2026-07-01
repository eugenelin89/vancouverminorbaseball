# 06 Draft Integration

## Draft Context

Do not ask coaches to enter draft selection information manually.

The current spreadsheet includes draft context rows such as:

- Birth year
- 2026 draft round
- Ranked by assessment/coaches
- Selected, meaning when the player was taken
- Based on performance and peers, what round the player should have been in

In the app:

- Birth year should come from the `players.Player` record or imported draft/player data when available.
- Actual draft selection data should come from the existing `drafts` app.
- Draft room, team, selected round, pick number, and selection order should be derived from `Draft`, `DraftTeam`, `DraftPlayer`, and `DraftAction`.
- Coaches may answer subjective observation questions, including where the player should have been drafted based on performance and peers.
- If a player cannot be matched to draft data, show the draft context as missing or unmatched rather than asking the coach to type it in.

## Boundaries

`drafts` owns:

- draft process
- draft selections
- draft actions

`analytics` owns:

- draft context display
- draft matching summaries
- draft expectation vs actual draft comparisons
- links between observations and draft context

Do not duplicate draft selection logic. Query existing draft models and actions.

## Services

Draft matching and draft analytics logic belongs in `analytics.services.draft_service`.

Player identity matching should use `players.services.matching_service` where relevant.
