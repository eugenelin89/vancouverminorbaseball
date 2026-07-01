# Analytics App Prompt

Create a new Django app named `analytics` for the Vancouver Community Baseball (VCB) project.

The analytics app should start by replacing the current Google Sheet-based coach player assessment workflow, but it should be designed as the foundation of a broader VCB Baseball Intelligence / Player Development Platform.

The first delivered workflow is practical and narrow: coaches submit structured observations for players using the existing 1-5 questionnaire. The architecture should be broader than that first workflow. Coach assessments should be one type of player observation, not the entire domain model.

## Version 1 Guardrail

Version 1 should implement only the `coach_assessment` workflow. The Observation/ObservationResponse architecture should make future observation types possible, but the first implementation should not build UI, workflows, or admin experiences for other observation types yet.

Future-ready architecture is required, but future product surfaces are not. Keep Version 1 focused on coach assessments, CSV roster imports, player search, player timeline, staff review, and draft context display.

Although the architecture anticipates significant future expansion, Version 1 intentionally delivers only the smallest practical workflow that replaces the existing spreadsheet-based coach assessment process. Future capabilities should build on this foundation incrementally rather than being implemented prematurely.

## Decision Support

The Analytics platform exists to organize observations, measurements, historical context, and reports in order to support better decision-making.

It does not replace the judgment of coaches, evaluators, coordinators, or administrators.

Final baseball decisions, including player placement, draft selections, coaching assignments, player development plans, and roster decisions, remain the responsibility of people, not software.

## Goals

- Give admins and staff a first version of an Analytics Command Center for player observations, imports, draft context, and evaluation trends.
- Give coaches a simple form for evaluating players they know using the current 1-5 scoring rubric.
- Preserve the existing coach assessment categories from the spreadsheet in normalized, queryable data.
- Model coach assessments as observations so future observation types can be added later without redesigning the app.
- Allow questions, categories, scoring methods, and response types to evolve over time without implementing non-coach-assessment workflows in Version 1.
- Pull draft round, selected round, team, and pick context from the existing `drafts` app where possible.
- Support CSV imports for player/member/roster data with conservative matching and merge review.
- Introduce a separate `players` app with `players.Player` as the canonical player identity model for imports, coach assessments, search, timelines, draft matching, reporting, and future expansion.
- Reuse existing models and service-layer patterns.
- Avoid duplicating business logic from existing apps.
- Keep the UI server-rendered with Django templates.
- Do not introduce frontend build tooling.

## Design Principles

This platform is intentionally designed using several architectural principles:

- Build only the smallest useful Version 1.
- Favor explicit, readable Django code over clever abstractions.
- Separate player identity from baseball observations.
- Treat observations as historical records that should rarely be modified.
- Prefer configuration over hard-coded baseball rules.
- Keep business logic in service modules.
- Design for incremental expansion rather than predicting every future requirement.
- Support coaches and staff through better information rather than automation of baseball decisions.

## Observation Architecture

Use a flexible observation model instead of a narrow assessment-only model.

An observation is any structured or semi-structured record about a player's baseball development, performance, evaluation, or context.

Initial observation type:

- `coach_assessment`

Use a lightweight `ObservationType` model or equivalent controlled lookup table instead of assuming observation type will always be a freeform string. Version 1 only needs one record: `coach_assessment`.

Future observation types may include the following, but Version 1 should not build UI, workflows, or admin management for them:

- evaluator tryout score
- camp evaluation
- AI video analysis
- bullpen evaluation
- player self-evaluation
- skills testing
- imported third-party data
- seasonal stats snapshot
- attendance note
- development note

Future `ObservationType` records may include:

- tryout
- game
- practice
- bullpen
- video
- AI
- attendance
- development_note

Each observation should include:

- Player reference.
- Evaluation cycle.
- Observation type.
- Observation source/provider.
- Evaluator/user who submitted or imported the observation, when applicable.
- Evaluator role at the time of submission, such as coach, assistant coach, evaluator, staff, admin, player, AI, import, or future roles.
- Status, timestamps, submitted timestamp, and optional internal notes.
- Responses to configured questions or fields.
- Raw/source metadata where useful for auditability.

Store evaluator role as a snapshot on the observation record, not only indirectly through current user permissions, because a user's role may change over time. Reports must be able to filter observations by evaluator role, for example showing only observations submitted by coaches.

In Version 1, only create and manage observations needed for the coach assessment workflow, staff/manual entry where required for review, CSV import audit context, and draft matching context.

## Evaluation Cycles

Use `EvaluationCycle` instead of `AssessmentCycle`.

An evaluation cycle is the time window, event, season, draft, or program context that groups related observations.

Example cycle types:

- House Draft
- AAA Tryout
- Mid-Season Evaluation
- End-Season Evaluation
- Winter Camp
- Coach Assessment
- Futures Tryout

Examples:

- `2026 13U House Draft`
- `2026 15U Spring Coach Assessment`
- `2026 AAA Tryout`
- `2026 Winter Camp`

The cycle should define which observation question set is used for coach assessments. The cycle model may include minimal fields that make future structured observation types possible, but Version 1 should not implement workflows for those future types.

## Shared Player App

Introduce a separate Django app named `players`.

The `players` app should own the core player identity model used across the project.

Use:

- App: `players`
- Main model: `Player`

Avoid naming the app `player_profiles`, because the player entity will eventually be used by many systems, not just profile pages.

Avoid putting the canonical player model inside `analytics`, because future apps such as analytics, drafts, PDP, video, attendance, recruiting, awards, and parent/player portals will all need to reference the same player identity.

Analytics should reference `players.Player`.

Example:

```python
class Observation(models.Model):
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE)
```

`players.Player` should support:

- CSV imports
- coach assessments
- player search
- Player Profile pages
- player timeline display
- draft matching
- reporting
- future expansion

The player model should stand on its own in the `players` app. It should be reusable by analytics and future project apps.

`players.Player` should support the fields needed for Version 1 imports, coach assessments, player search, timeline display, and draft matching:

- First name
- Last name
- Preferred/nickname when available
- Birthdate or birth year when available
- Gender when available
- Team/division context
- Source identifiers such as registration ID, registrant ID, team ID, or draft player ID
- Safe reporting fields
- Source metadata

Do not expose sensitive fields such as addresses, medical notes, phone numbers, emails, or guardian/contact details to ordinary coach assessment screens unless explicitly needed and permissioned.

## App Responsibility Boundaries

Keep app ownership clear so future modules can reuse shared concepts without duplicating them.

`players` owns:

- canonical player identity
- aliases
- source identifiers
- player matching
- player tags
- player imports
- player identity provenance

`analytics` owns:

- observations
- evaluations
- reports
- metrics
- timelines
- comparisons

`drafts` owns:

- draft process
- draft selections
- draft actions

Future `pdp` may own:

- development plans
- goals
- milestones

Future `video` may own:

- media
- AI analysis

Future `recruiting` may own:

- recruiting history
- recruiting reports

## Player Tags

Add a lightweight tagging system so staff can organize and search players using baseball-specific labels.

Create `PlayerTag` with a many-to-many relationship to `players.Player`.

Example tags:

- Strong Arm
- Potential Catcher
- Future AAA
- Development Priority
- Leader
- High Baseball IQ
- Two-Way Player
- Pitcher Only
- Speed
- Power
- Injury Recovery
- Needs Confidence

Version 1 requirements:

- staff/admin users can manage tags
- tags appear on the player profile page
- tags appear on the player timeline
- tags are searchable/filterable
- coaches do not manage tags unless future permissions allow it

Keep tagging intentionally simple.

## Watch Lists

Future versions may add lightweight Watch Lists to help staff organize players they want to monitor.

Example watch lists:

- Future AAA
- Strong Prospect
- Follow Up
- Potential Catcher
- Interesting Pitcher

Watch Lists are different from Player Tags. Tags describe a player. Watch Lists help staff organize players they want to monitor.

Do not implement Watch Lists in Version 1.

## Coach Assessment Workflow

Build the first workflow around coach-submitted observations with:

```text
Observation.observation_type = "coach_assessment"
```

Multiple coaches can evaluate the same player in the same evaluation cycle.

Each evaluator should be able to submit at most one coach-assessment observation for the same player in the same evaluation cycle, but a player may have observations from many evaluators.

Players are most likely to be evaluated by their own coaches, but the app should allow any authenticated coach to evaluate any player if they know the player well enough to provide useful feedback.

The initial coach assessment should use this 1-5 scoring rubric. Version 1 only needs numeric 1-5 rating responses plus freeform notes/text responses.

- `1`: 0/5 times, Never
- `2`: 1-2/5 times, Infrequently
- `3`: 2.5/5 times, Half the time
- `4`: 4/5 times, Frequently
- `5`: 5/5 times, Always

Each coach-assessment observation should include:

- Player identity/reference.
- Evaluator/user who submitted the observation.
- Evaluator role snapshot.
- Evaluation cycle.
- Observation status.
- A set of configured question responses.
- Freeform notes.

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
- Do not duplicate draft selection logic; query existing draft models and actions.

## Player and Roster Imports

The project should be able to import CSV files that describe the same player population with different levels of detail.

Player identity import is part of the `players` bounded context. The `players` app should own player imports, matching, duplicate merging, aliases, source identifiers, and provenance. The analytics app may provide an "Import Players" page in the Analytics Command Center for Version 1, but the underlying import logic should call `players.services.import_service` and related `players` services.

Example source files include:

- A member-list CSV with fields such as first name, last name, role, age, gender, and team.
- A roster-detail CSV with fields such as first name, last name, player/non-player status, address, city, birthdate, jersey number, position, email, phone number, gender, contacts/guardians, team ID, team, division, registration fields, baseball history, positions, throwing, batting, medical notes, availability, volunteering, sponsorship, and comments.

Import requirements:

- Support CSV upload through a staff/admin-only import workflow exposed from the Analytics Command Center.
- Provide a preview step before committing imported data.
- Allow staff to map source columns to `players.Player` fields.
- Normalize common header variants, for example `First Name` and `First` should both map to first name.
- Use `players.services.import_service` to import player identity data.
- Use `players.services.matching_service` to match players conservatively.
- Merge files that refer to the same players instead of creating duplicates.
- Match players conservatively using reusable player-matching logic from `players.services.matching_service`, using a combination of first name, last name, birthdate, team, division, email, registration ID, registrant ID, team ID, or other stable identifiers when available.
- Flag ambiguous matches for staff review instead of automatically merging risky records.
- If an imported player already exists with a high-confidence match, enrich the existing `players.Player` record instead of creating a duplicate.
- For high-confidence matches, fill missing fields from the new import and attach the new source row to the existing player through `players.PlayerSourceRow`.
- Do not silently overwrite important existing player fields when the new import conflicts with stored data.
- Record field-level conflicts during import preview and allow staff/admin users to choose whether to keep the existing value, use the imported value, or store the imported value only as source-row metadata.
- If one imported row matches multiple possible existing players, mark it as ambiguous and require staff review before merge.
- If one existing player appears in multiple imported files, keep one player record and attach each source row/import record to that player.
- If no existing player can be matched confidently, create a new `players.Player`.
- Preserve source filename, import timestamp, imported-by user, row number, original row data, and unmapped extra fields in `players` provenance models for audit/debugging.
- Support importing multiple CSVs for the same evaluation cycle, because different exports may contain different details about the same members.
- Make imported player records available for coach assessment even when they are not linked to draft data.

Responsibility split:

- `players` imports player identity.
- `players` performs matching.
- `players` merges duplicates.
- `players` owns aliases, source identifiers, source rows, and provenance.
- `analytics` consumes imported players.
- `analytics` displays imported context.
- `analytics` uses player matching services.
- `analytics` links observations to players.

## Questions And Responses

Create a reusable, configurable question set matching the initial spreadsheet structure.

Questions must not be hard-coded into templates. Staff/admin users should be able to add, remove, deactivate, reorder, or revise coach assessment questions over time. Historical observations must remain interpretable after questions change, so prefer versioning, effective dates, retired dates, deactivation, and question-set snapshots over destructive deletion once a question has responses.

Use `ObservationQuestionSet` and `ObservationQuestion` or equivalent names.

The Version 1 implementation only needs:

- 1-5 numeric rating responses
- freeform notes/text responses

The response model should remain future-ready for additional response types, including:

- boolean
- multiple choice
- velocity
- time
- distance

Do not fully implement future response-type UI or workflows unless required by the coach assessment workflow.

The initial coach assessment question set should use the current 1-5 rubric and include:

### Throw

- Throws accurately
- Throws with velocity
- Ability to throw from outfield to infield in the air or on one hop
- Can throw accurately across the diamond from 3rd to 1st

### Field

- Can catch routine balls at 1st base
- Can catch non-routine balls at 1st base
- Ability to catch a routine grounder
- Ability to catch a non-routine grounder
- Ability to catch a routine fly ball
- Ability to catch a non-routine fly ball

### Hitting

- Hits barrels
- Player can sacrifice bunt
- Player chooses strikes to swing at
- Gets on base
- Hits for power

### Pitching

- Throws strikes
- Can hold runners
- Has good velocity
- Has an off-speed pitch

### Catching

- Likes to catch
- Can throw to 2nd accurately
- Can block

### Hustle

- Always focused
- Checks in/attends regularly
- Listens to coach feedback

### Notes

- Freeform coach notes

## Observation Sources And Providers

Add a simple source/provider design so observations can record where they came from.

Version 1 only needs sources required for:

- coach
- staff
- manual entry
- imported CSV
- draft matching context

Future sources may include:

- evaluator
- GameChanger
- Pocket Radar
- Rapsodo
- TrackMan
- AI
- player self-entry

Do not overbuild provider infrastructure in Version 1. Do not implement GameChanger, Pocket Radar, Rapsodo, TrackMan, AI, or other future integrations. Design the model so these sources can be added later without changing the core observation model.

## Future Capabilities

The architecture should not block future capabilities, but these are not implemented in Version 1.

Future capabilities may include:

- AI-assisted video analysis
- objective metrics
- velocity tracking
- exit velocity tracking
- practice attendance
- workload tracking
- provider integrations
- parent portal
- player portal
- advanced reporting

Future AI modules should consume analytics data through service-layer APIs. AI should not be embedded inside analytics business logic.

Possible future AI capabilities include:

- player feedback
- video summaries
- trend detection
- development recommendations
- report generation

## Future Measurements

Observations and measurements are different concepts.

Observations represent evaluator opinions, notes, or structured feedback.

Measurements represent objective values.

Examples of observations:

- "Throws accurately"
- "Shows leadership"

Examples of measurements:

- fastball velocity
- exit velocity
- pop time
- sprint time
- height
- weight
- pitch count

Future measurements may include:

- fastball velocity
- exit velocity
- throwing velocity
- sprint time
- pop time
- height
- weight
- pitch count
- workload

Do not implement measurements in Version 1. Version 1 should continue using only observations.

Future versions may correlate observations and measurements.

Future architecture may introduce models such as:

- `MeasurementDefinition`
- `PlayerMeasurement`
- `MeasurementRecord`

## Future Observation Attachments

Future versions may allow observations to include attachments.

Possible future model:

- `ObservationAttachment`

Possible attachment types:

- video
- photo
- PDF
- CSV
- radar screenshot
- TrackMan export
- Rapsodo export

Do not implement attachment workflows in Version 1. Ensure the architecture does not prevent adding attachments later.

## Reporting

Do not implement a reporting engine in Version 1.

Report calculations should live in reusable services, such as `reporting_service.py` and `metrics_service.py`, so future reporting can build on the same logic.

Future reporting concepts may include:

- saved filters
- report definitions
- report runs

Version 1 reports should remain simple, server-rendered summaries and tables.

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

Present the player timeline as part of the Player Profile page.

The Player Timeline is intended to become the primary historical view of a player.

The timeline should eventually show a player's development history over time, including:

- coach observations
- tryout evaluations
- draft history
- imports
- seasonal stats
- velocity progression
- attendance
- development notes
- AI/video observations
- awards or milestones
- development milestones

For the first version, include:

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

Reframe the staff dashboard as the first version of an Analytics Command Center.

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

Do not add charts or JavaScript-heavy visualizations in the first version. Use tables, summary cards, filters, and server-rendered pages.

Do not build UI for future observation types, AI analysis, third-party imports, objective metrics, or provider management in Version 1.

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

## Service Organization

Use structured service packages instead of one large service module.

Because `players.Player` is the canonical player identity model, player-specific business logic belongs in the `players` app. The analytics app should consume these services instead of owning player identity, player matching, player imports, aliases, source identifiers, or player tag management.

Recommended `players` service modules:

```text
players/
    services/
        identity_service.py
        matching_service.py
        import_service.py
        tag_service.py
```

The `players` service package should own:

- player identity management
- player matching
- player imports
- player aliases
- player source identifiers
- player tag management

Player matching should be reusable infrastructure for future apps such as analytics, recruiting, attendance, video, and PDP.

Recommended `analytics` service modules:

```text
analytics/
    services/
        observation_service.py
        draft_service.py
        metrics_service.py
        timeline_service.py
        comparison_service.py
        question_service.py
        reporting_service.py
```

Analytics services should call `players.services.identity_service`, `players.services.matching_service`, `players.services.import_service`, and `players.services.tag_service` when they need player identity, player matching, player import, provenance, or tag behavior.

Business logic should live inside these service modules. Views should coordinate requests and responses. Templates should remain presentation only. Keep model methods limited to validation or simple helper methods.

## Initial Scope

The Version 1 UI should include only:

- Analytics Command Center
- CSV import workflow
- player search
- Player Profile page with timeline
- Player Comparison
- coach assessment list
- coach assessment form
- staff observation/assessment review
- basic draft-context display

1. Create an `/analytics/` section mounted from the root URL config.
2. Add an Analytics Command Center for staff/admin users.
3. Add staff/admin CSV import for player/member/roster data with preview, mapping, validation, conflict handling, and merge review.
4. Add player search, Player Profile, player timeline, and simple Player Comparison pages.
5. Add a coach-facing player list showing available players, the coach's own completion status, and already-submitted observations.
6. Add a coach-assessment observation form for one evaluator to score one player.
7. Add an observation detail/read-only view for staff review.
8. Add basic draft-context display and service logic to match `players.Player` records to existing draft data.
9. Seed the initial coach assessment question set.
10. Use Django ORM aggregation where possible.
11. Put analytics queries, draft matching, question handling, reporting calculations, timeline assembly, comparison logic, and observation creation in analytics service modules, not directly inside templates. Put player identity management, player matching, player imports, aliases, source identifiers, provenance, and tag management in `players/services/`.
12. Add focused tests for permission behavior, CSV parsing, import merging, ambiguous match handling, conflict handling, observation submission, response validation, evaluator-role filtering, question-set versioning, and draft-data matching.
13. Use templates and CSS consistent with the existing project style.

## Suggested Data Model

Prefer a normalized shape that supports the first coach-assessment workflow while remaining flexible for broader player intelligence. Future-facing fields should be simple and minimal in Version 1. Avoid abstraction-heavy design.

- `EvaluationCycle`: time window/event/season/draft/program context for observations.
- `players.Player`: canonical player identity record owned by the separate `players` app and referenced by analytics.
- `players.PlayerAlias`: alternate names and aliases for player matching and display.
- `players.PlayerSourceIdentifier`: external/source identifiers such as registration ID, registrant ID, team ID, or imported source keys.
- `players.PlayerSourceRow`: original source row data and unmapped fields linked to a `players.Player` record for auditability and provenance.
- `players.PlayerTag`: lightweight staff-managed tags with a many-to-many relationship to `players.Player`.
- `ImportedRosterFile`: uploaded file metadata, source type, uploaded-by user, status, preview snapshot, row errors, conflict summary, and import summary. This should live with the player import/provenance workflow in `players` unless there is a strong reason to keep upload metadata in analytics.
- `ObservationType`: lightweight controlled lookup table for observation types. Version 1 only needs `coach_assessment`.
- `ObservationQuestionSet`: reusable collection/version of active questions assigned to a cycle and observation type.
- `ObservationQuestion`: category, prompt text, display order, active flag, response type, scoring/evaluation configuration, effective dates, retired date, and version metadata. Version 1 only needs 1-5 numeric ratings and freeform notes/text.
- `ObservationSource`: minimal source/provider metadata for coach, staff/manual entry, imported CSV, and draft matching context. Keep future sources such as AI or third-party systems possible, but do not build provider management infrastructure in Version 1.
- `EvaluatorRole`: role key and display label for the evaluator's role at submission time.
- `Observation`: evaluation cycle, `players.Player`, optional linked `drafts.DraftPlayer`, observation type, observation source, evaluator/user, evaluator role snapshot, status, submitted timestamp, notes, and source metadata.
- `ObservationResponse`: observation, question, response type, numeric value, text value, boolean value, selected choice, raw value, unit, payload, and metadata. Use `payload` as a JSON field for future structured responses, including possible AI-generated response details. Version 1 does not need UI for payload values.

Represent the initial coach workflow as:

```text
Observation.observation_type = "coach_assessment"
```

Add a uniqueness rule so the same evaluator cannot submit duplicate `coach_assessment` observations for the same player in the same evaluation cycle. Do not make player plus cycle unique, because multiple evaluators must be able to evaluate the same player.

Do not hard-code the long-term question list in templates or views. A short seed function, data migration, fixture, or admin setup helper can create the initial default questions from this prompt, but the runtime app should read questions from data.

Historical observations must remain interpretable even after questions change. Store enough question/response metadata or snapshots to render old observations accurately.

## Constraints

- Do not change existing app behavior.
- Do not modify existing `drafts`, `leaguehub`, or `scholarships` models unless absolutely required.
- Do not ask coaches to manually enter draft selection data already available from the `drafts` app.
- Do not duplicate draft selection logic; query existing draft models and actions.
- Do not overbuild the first version.
- Do not add third-party integrations in the first version.
- Do not build UI, workflows, or admin experiences for non-`coach_assessment` observation types in Version 1.
- Do not build provider management UI in Version 1.
- Do not fully implement future response types unless required by coach assessments.
- Do not implement a reporting engine in Version 1.
- Do not implement measurements in Version 1.
- Do not implement observation attachment workflows in Version 1.
- Do not implement Watch Lists in Version 1.
- Do not add charts or JavaScript-heavy visualizations in the first version.
- Staff users can review all observations.
- Coaches can submit coach-assessment observations.
- Authenticated coaches may evaluate any player they know well enough to assess.
- Coaches may edit their own draft/unsubmitted observations, but staff/admin users control whether submitted observations can be reopened.
- Use structured service packages. `players/services/` owns player identity management, player matching, player imports, aliases, source identifiers, provenance, and player tag management. `analytics/services/` owns observations, questions, reports, metrics, timelines, comparisons, draft analytics, and observation workflows.
- Prefer conservative, readable implementation over abstraction-heavy design.

## Deliverables

- `analytics` Django app
- `players` Django app
- Canonical `players.Player` model
- URL routing
- Analytics Command Center
- Staff/admin CSV import workflow
- Player search
- Player Profile page with timeline
- Simple Player Comparison view
- Coach assessment observation list, form, and detail views
- Basic draft-context display
- Structured `analytics/services/` package
- Structured `players/services/` package for identity, matching, imports, aliases, source identifiers, provenance, and tags
- Service functions for metrics
- Service functions in `players` for importing CSVs and merging `players.Player` records
- Service functions for matching `players.Player` records to draft data
- Service functions for timeline, comparison, question, observation, and reporting calculations
- Models and migrations for `players.Player`, `players.PlayerAlias`, `players.PlayerSourceIdentifier`, `players.PlayerSourceRow`, `players.PlayerTag`, evaluation cycles, observation types, imports, observation sources, question sets, questions, observations, responses, and evaluator roles
- Initial seed data or setup helper for the default coach assessment question set
- Dashboard, import, Player Profile/timeline, comparison, and observation templates
- Minimal CSS if needed
- Tests
- Updated root URL config and settings
