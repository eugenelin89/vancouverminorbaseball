# Glossary

## Player

The canonical player identity record owned by the `players` app as `players.Player`. Future apps should reference this shared model instead of creating their own player identity models.

## Player Profile

A page/view in the Analytics experience that presents player details, tags, draft context, coach observations, timeline, imports, and simple reports. It is not the core model name.

## Observation

A structured or semi-structured record about a player's baseball development, performance, evaluation, or context. Version 1 implements only `coach_assessment` observations.

## Observation Type

A controlled lookup describing the kind of observation. Version 1 only needs `coach_assessment`. Future values may include tryout, game, practice, bullpen, video, AI, attendance, and development notes.

## Observation Response

A response to a configured observation question. Version 1 needs 1-5 numeric rating responses and freeform notes/text. The model should also include a JSON `payload` for future structured responses.

## Evaluation Cycle

A time window, event, season, draft, or program context that groups related observations. Examples include House Draft, AAA Tryout, Winter Camp, and Coach Assessment.

## Measurement

An objective value about a player, such as fastball velocity, exit velocity, pop time, sprint time, height, weight, pitch count, or workload. Measurements are future work and are not implemented in Version 1.

## Timeline

The historical view of a player, presented as part of the Player Profile page. Version 1 includes coach assessments, imported player context, and draft context.

## Player Tag

A staff-managed label attached to a player, such as Strong Arm, Future AAA, Development Priority, Leader, or Needs Confidence. Tags describe a player and are searchable/filterable.

## Watch List

A future feature for staff-curated lists of players to monitor, such as Future AAA, Strong Prospect, Follow Up, Potential Catcher, or Interesting Pitcher. Watch Lists are not implemented in Version 1.

## Analytics Command Center

The staff/admin landing page for Analytics. Version 1 includes coach completion, observation counts, player search, imports, draft matching, timeline links, reports, trends, and recent observations.

## Draft Context

Draft-related information derived from the existing `drafts` app, including draft room, team, selected round, pick number, and selection order.

## Player Comparison

A simple server-rendered view for comparing players by average scores, category scores, coach notes, evaluator count, draft expectation vs actual draft, team/division, and tags.

## Source Identifier

An external or imported identifier associated with a player, such as registration ID, registrant ID, team ID, draft player ID, or source-system key.

## Provenance

Source/audit context explaining where player identity data came from, including source filename, imported row data, import timestamp, imported-by user, row number, and unmapped fields.
