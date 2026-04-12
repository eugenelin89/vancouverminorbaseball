You are working inside an existing Django project for vancouverminor.com.

Your task is to design and implement a league standings and scores platform for baseball seasons, with an ESPN-style season dashboard page.

This must fit the existing repo architecture and visual language.

Important repo context:

- This project uses Django templates, Django models, Django admin, and plain CSS.
- Do not introduce React, Tailwind, Vite, webpack, or any frontend build tooling.
- Reuse the established visual direction already present in the repo:
  - navy / blue / gold palette
  - premium rounded cards
  - polished spacing
  - strong hero sections
  - Barlow and Source Sans 3 typography
  - existing premium dashboard language from the `drafts` and `pdp` apps
- The new feature must feel native to this codebase, not like a separate product.

Before creating models, inspect the existing project structure and reuse existing core entities where appropriate.

Requirements:

- reuse existing `Team`, `Season`, and `User` models if suitable ones already exist
- do NOT duplicate core entities unnecessarily
- if an existing model is not sufficient, extend or relate to it cleanly instead of creating overlapping duplicates without justification

Primary product goal:

Build a baseball league/season scoreboard and standings system where:

- admins manage leagues, seasons, teams, and coaches
- home team coaches enter scores
- away team coaches verify scores
- unverified scores are still visible but clearly marked as unverified
- verified scores are visually distinct
- standings are calculated automatically from submitted game results
- a given season + league has a premium ESPN-style dashboard
- coaches from either team can add a short game story/summary
- each team can upload one photo per game
- those stories and photos appear in an editorial, sports-media-style presentation

Core requirements:

1. League and Season Management

Admins must be able to create and manage:

- leagues
- seasons
- teams
- coach assignments

The status/dashboard page is always scoped to:

- one specific league
- one specific season

Admins must be able to:

- create new leagues
- create new seasons
- create new teams
- assign coaches to teams
- enter scores on behalf of coaches
- confirm scores
- edit scores

2. Team and Coach Management

Each team belongs to a league and season context in a clean, maintainable way.

Each coach should have at minimum:

- first_name
- last_name
- email

Head coaches should be able to add assistant coaches to their team if practical.

The architecture should cleanly support:

- head coach
- assistant coach
- admin

3. Game / Score Entry Workflow

Use a single `Game` model as the source of truth for schedule, score, and verification workflow.

Include on `Game`:

- `home_score`
- `away_score`
- `status`
- `verification_status`

Do NOT create a separate `GameResult` model unless absolutely necessary and strongly justified.

Game verification must follow a clear state machine represented as a field on `Game`.

Required states:

- `scheduled`
- `score_submitted_by_home`
- `awaiting_away_verification`
- `verified_final`

All state transitions must be controlled through service-layer functions, not ad hoc in views or templates.
Ensure that a game cannot transition to `verified_final` unless a valid score has been submitted.
Enforce this through model validation or database constraints where practical.
Ensure a game cannot be verified more than once or re-verified without an explicit admin override.

The system must also support non-final game statuses such as:

- postponed
- canceled

If practical, include game presentation/status support for:

- Scheduled
- Live
- Final

If practical, include inning / partial-game scaffolding for future expansion, even if the first version does not implement full live scoring.

Track score-change history.

At minimum, retain:

- previous values
- who edited
- timestamp

Use either:

- a dedicated history model
- or `django-simple-history`

Rules:

- only the home team coach can initially enter the score
- the away team coach can verify the score
- admin can enter, verify, or edit any score
- once the score is entered by the home team coach, it should appear publicly
- while awaiting away-team verification, the UI must clearly show that the result is not verified
- once the away team coach verifies it, the UI must show a clearly different verified state

Model the workflow cleanly so transitions are explicit and enforceable.

Score submission and verification operations should be wrapped in database transactions to prevent inconsistent state.
Score submission operations should be idempotent where possible to prevent duplicate or conflicting updates.
Once a game is `verified_final`, prevent further score edits unless performed by an admin.
Admin edits to verified games should automatically create an audit entry and may require the game to re-enter a re-verification flow if appropriate.

The verification state must be obvious at a glance.

Examples:

- unverified score uses a warning/accent treatment and label such as “Awaiting Away Verification”
- verified score uses a more confident/complete treatment and label such as “Verified Final”

4. Standings Logic

Standings must be calculated automatically from accumulated game results.

Points system:

- win = 2 points
- tie = 1 point
- loss = 0 points

Important constraint:

- standings must NOT be stored as source-of-truth data
- standings must be derived from game results
- standings must be computed dynamically or via cache/materialized summary
- standings must be recalculated whenever scores change
- if caching is used, implement a clear rebuild / refresh mechanism
- standings recalculation must be idempotent and deterministic
- repeated recalculations over the same game data must produce the same result

Postponed and canceled games must be handled explicitly and must not incorrectly affect standings.

Standings should show at minimum:

- team name
- games played
- wins
- losses
- ties
- points
- runs for
- runs against
- run differential

If practical, include:

- streak
- last 5
- verified games count

Design the standings calculation so future tie-breakers can be added without redesigning the system.

Important future-ready requirement:

- head-to-head comparison should be addable later as a tie-breaker
- do not hard-code the standings logic in a way that makes future tie-breaker expansion difficult

Standings must be scoped to the selected season and league.

5. Dashboard Page

Build an ESPN-style dashboard page for a given season and league.

This is the signature page.

It should feel like a premium baseball media / scoreboard hub, not an admin CRUD view.

The page should include:

- strong season/league hero
- standings table
- recent scores from the past week
- ability to navigate to view all scores
- featured recent game cards
- verification status badges
- editorial-style game stories
- team-submitted photos
- compact scoreboard presentation
- mobile-friendly layout

The page must feel energetic, sports-forward, and editorial while still matching the existing site theme.

Do not copy ESPN branding literally.
Do adopt an ESPN-style information hierarchy and sports presentation style.

6. Scores and Results Pages

Include:

- recent scores for the past week on the main dashboard
- a separate “all scores” or full results view
- filters or navigation by season/league if practical

Each game result card/page should support:

- home team
- away team
- final score
- verification state
- game date
- story/report from home coach
- story/report from away coach
- one photo upload per team per game

7. Stories and Photos

Both the home team coach and away team coach must be able to write a short story, report, or summary for the game.

Both team sides should have permission to contribute.

Each team may upload one photo per game.

Enforce the one-photo-per-team-per-game rule at the model and/or validation level, not only in the UI.

Those stories and photos should appear in an editorial sports-style presentation similar to a baseball news/results page.

The UI should make game content feel alive:

- score first
- story second
- image support where available

8. Permissions

Implement clear, correct permissions.

At minimum:

Admin:

- manage leagues
- manage seasons
- manage teams
- manage coaches
- manage games
- enter scores
- verify scores
- edit scores

Home team coach:

- enter initial score for home games
- add game story/report
- upload one team photo for that game

Away team coach:

- verify submitted score
- add game story/report
- upload one team photo for that game

Assistant coaches:

- if included, define clearly whether they can enter scores, verify scores, add stories, and upload photos
- default to a conservative, explicit permission model

9. Data Model Expectations

Design clean, reusable models.

Suggested entities:

- League
- Season
- Team
- TeamSeason or LeagueSeason relationship model if needed
- CoachProfile or coach/team assignment model
- Game
- GameStory
- GamePhoto

You may adjust the exact model design, but it must remain extensible and production-quality.

Important modeling constraint:

- `Game` should be the authoritative record for scheduled matchup and score state
- score fields should live directly on `Game`
- verification state should live directly on `Game` unless there is a very strong reason otherwise
- do not split core score state into a separate result table without strong justification
- do NOT create a separate `GameVerification` model unless there is a very strong and justified reason

Ensure appropriate uniqueness and integrity constraints at the model level.

Ensure relational consistency:

- `home_team` and `away_team` must belong to the same league and season context as the `Game`
- enforce this through validation so cross-league or cross-season mismatches are prevented
- `home_team` and `away_team` cannot be the same team

Examples:

- one `Game` per `home_team`, `away_team`, and date, or another clearly defined and justified uniqueness rule
- one photo per team per game

Add appropriate database indexes for expected query patterns.

At minimum, consider indexes for:

- `Game` by season, league, and date
- team relationship lookups
- frequently queried standings-related fields and filters

Support soft deletion or archival of games instead of hard deletion so historical integrity is preserved.

10. UI / UX Requirements

The dashboard and results pages must be beautiful.

Use the current repo’s theme, but elevate it into a sports-media presentation:

- bold scoreboard header
- high-contrast result cards
- refined status badges
- strong table styling
- editorial story modules
- premium card composition
- subtle gradients and shadows
- responsive layout for desktop, tablet, and mobile

The page should feel like:

- a standings hub
- a schedule/results center
- a baseball season media page

11. Technical Requirements

Use Django best practices.

Include:

- models
- migrations
- admin integration
- views
- forms
- urls
- templates
- services
- tests
- documentation

Keep business logic out of templates.
Keep business logic out of views.

Design views so they can later be converted cleanly into Django REST Framework endpoints.

Structure the feature so:

- business rules live in services
- views stay thin
- data access patterns are reusable
- future serializers/API views can reuse the same core logic

Use services where appropriate for:

- standings calculation
- score submission
- score verification
- permission helpers
- game story/photo handling
- score history / audit handling

Critical workflow operations such as score submission, verification, and admin score edits should use transactions.

Do not persist standings rows as authoritative league-state records unless they are explicitly treated as cache only.

12. Deliverables

Provide:

1. architecture proposal first
2. do NOT generate code yet
3. do NOT generate migrations yet
4. do NOT implement models, views, templates, or CSS yet
5. wait until the architecture proposal is reviewed before implementation begins

The first response should be architecture proposal only.

Design and implementation guidance:

- build this as a reusable Django app or a cleanly isolated feature area inside the existing project
- make the dashboard page the visual centerpiece
- use realistic baseball terminology
- ensure score verification is very obvious in the UI
- ensure standings update from submitted scores
- ensure all score/story/photo permissions are correct
- prefer long-term maintainability over quick hacks

Do not build a throwaway prototype.

Build a maintainable baseball league season dashboard and standings system that feels like a polished ESPN-style season hub inside this Django repo.
