# 07 Player Experience

## Player Profile And Timeline

Add a Player Profile page as the central player view in the analytics app.

The Player Profile page should become the central location for:

- player profile details
- current team
- draft context
- tags
- coach observations
- timeline
- imports
- reports

Future features can naturally extend this page, but Version 1 should keep it focused on imported player data, tags, coach assessments, draft context, and basic reports.

## Timeline Philosophy

Present the player timeline as part of the Player Profile page.

The Player Timeline is intended to become the primary historical view of a player.

The timeline should eventually show a player's development history over time, including:

- observations
- measurements
- draft events
- imports
- awards
- tryouts
- AI analyses
- attendance
- development milestones

For Version 1, include only:

- coach-assessment observations
- draft context
- imported player information

Future versions may introduce a `TimelineEvent` abstraction that aggregates observations, measurements, imports, awards, draft events, and other historical records into a unified player timeline.

Do not implement `TimelineEvent` in Version 1.

Do not build timeline UI for future observation types, AI analysis, third-party imports, objective metrics, or provider-specific data yet.

## Player Comparison

Add a simple server-rendered Player Comparison feature.

Version 1 should support comparing:

- average scores
- category scores
- coach notes
- evaluator count
- draft expectation vs actual draft
- team/division
- tags

Keep implementation simple and server-rendered. Do not build an advanced comparison dashboard in Version 1.

## Analytics Command Center

The Version 1 command center should include:

- Coach completion
- Observation counts
- Player search
- Imports
- Import errors and ambiguous matches
- Draft matching
- Player timeline links
- Reports
- Evaluation trends
- Assessment count by player
- Assessment count by evaluator role
- Average score by category
- Average score by evaluator role
- Coach-to-coach score variance by player/category
- Players whose coach-assessed expected round differs from actual draft selection
- Players with unmatched draft records
- Recently submitted observations

Use tables, summary cards, filters, and server-rendered pages. Do not add charts or JavaScript-heavy visualizations in Version 1.

## Player Search

Support simple player search and filtering.

Version 1 search/filter fields should include:

- name
- team
- division
- birth year
- draft status
- tags
- imported source
- evaluation completion

No advanced search UI is required. Simple server-rendered filters are sufficient.
