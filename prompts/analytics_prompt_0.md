# Analytics App Prompt

Create a new Django app named `analytics` for the Vancouver Community Baseball (VCB) project.

The analytics app should start by replacing the current Google Sheet-based coach player assessment workflow, but it should be designed as the foundation of a broader VCB Baseball Intelligence / Player Development Platform.

The first delivered workflow is practical and narrow: coaches submit structured observations for players using the existing 1-5 questionnaire. The architecture should be broader than that first workflow. Coach assessments should be one type of player observation, not the entire domain model.

## Version 1 Guardrail

Version 1 should implement only the `coach_assessment` workflow. The Observation/ObservationResponse architecture should make future observation types possible, but the first implementation should not build UI, workflows, or admin experiences for other observation types yet.

Future-ready architecture is required, but future product surfaces are not. Keep Version 1 focused on coach assessments, CSV roster imports, player search, player timeline, staff review, and draft context display.

## Goals

- Give admins and staff a first version of an Analytics Command Center for player observations, imports, draft context, and evaluation trends.
- Give coaches a simple form for evaluating players they know using the current 1-5 scoring rubric.
- Preserve the existing coach assessment categories from the spreadsheet in normalized, queryable data.
- Model coach assessments as observations so future observation types can be added later without redesigning the app.
- Allow questions, categories, scoring methods, and response types to evolve over time without implementing non-coach-assessment workflows in Version 1.
- Pull draft round, selected round, team, and pick context from the existing `drafts` app where possible.
- Support CSV imports for player/member/roster data with conservative matching and merge review.
- Keep the design ready to link or migrate to a future shared player model such as `PlayerProfile` or `pdp.Player`.
- Reuse existing models and service-layer patterns.
- Avoid duplicating business logic from existing apps.
- Keep the UI server-rendered with Django templates.
- Do not introduce frontend build tooling.

## Observation Architecture

Use a flexible observation model instead of a narrow assessment-only model.

An observation is any structured or semi-structured record about a player's baseball development, performance, evaluation, or context.

Initial observation type:

- `coach_assessment`

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

Each observation should include:

- Player reference or temporary player identity.
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

## Player Identity

The analytics app may temporarily store player identity for imports and observations, but it should not be designed as the permanent source of truth for player identity.

Use a model such as `PlayerIdentity` or temporary `AnalyticsPlayer` to support the first version. Keep the model intentionally migration-friendly so it can later link or migrate to a shared player model such as `PlayerProfile` or `pdp.Player`.

Player identity should support the fields needed for Version 1 imports, coach assessments, player search, timeline display, and draft matching:

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

- Birth year should come from the player identity record or imported draft/player data when available.
- Actual draft selection data should come from the existing `drafts` app.
- Draft room, team, selected round, pick number, and selection order should be derived from `Draft`, `DraftTeam`, `DraftPlayer`, and `DraftAction`.
- Coaches may answer subjective observation questions, including where the player should have been drafted based on performance and peers.
- If a player cannot be matched to draft data, show the draft context as missing or unmatched rather than asking the coach to type it in.
- Do not duplicate draft selection logic; query existing draft models and actions.

## Player and Roster Imports

The analytics app should be able to import CSV files that describe the same player population with different levels of detail.

Example source files include:

- A member-list CSV with fields such as first name, last name, role, age, gender, and team.
- A roster-detail CSV with fields such as first name, last name, player/non-player status, address, city, birthdate, jersey number, position, email, phone number, gender, contacts/guardians, team ID, team, division, registration fields, baseball history, positions, throwing, batting, medical notes, availability, volunteering, sponsorship, and comments.

Import requirements:

- Support CSV upload through a staff/admin-only import workflow.
- Provide a preview step before committing imported data.
- Allow staff to map source columns to player identity fields.
- Normalize common header variants, for example `First Name` and `First` should both map to first name.
- Merge files that refer to the same players instead of creating duplicates.
- Match players conservatively using a combination of first name, last name, birthdate, team, division, email, registration ID, registrant ID, team ID, or other stable identifiers when available.
- Flag ambiguous matches for staff review instead of automatically merging risky records.
- If an imported player already exists with a high-confidence match, enrich the existing player identity record instead of creating a duplicate.
- For high-confidence matches, fill missing fields from the new import and attach the new source row to the existing player.
- Do not silently overwrite important existing player fields when the new import conflicts with stored data.
- Record field-level conflicts during import preview and allow staff/admin users to choose whether to keep the existing value, use the imported value, or store the imported value only as source-row metadata.
- If one imported row matches multiple possible existing players, mark it as ambiguous and require staff review before merge.
- If one existing player appears in multiple imported files, keep one player record and attach each source row/import record to that player.
- If no existing player can be matched confidently, create a new temporary player identity record.
- Preserve source filename, import timestamp, imported-by user, row number, original row data, and unmapped extra fields for audit/debugging.
- Support importing multiple CSVs for the same evaluation cycle, because different exports may contain different details about the same members.
- Make imported player records available for coach assessment even when they are not linked to draft data.

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

## Player Timeline

Add a player timeline as a major reporting concept.

The timeline should eventually show a player's development history over time, including:

- coach observations
- tryout evaluations
- draft history
- seasonal stats
- velocity progression
- attendance
- development notes
- AI/video observations
- awards or milestones

For the first version, include:

- coach-assessment observations
- draft context
- imported player information

Do not build timeline UI for future observation types, AI analysis, third-party imports, objective metrics, or provider-specific data yet.

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

## Initial Scope

The Version 1 UI should include only:

- Analytics Command Center
- CSV import workflow
- player search
- player timeline
- coach assessment list
- coach assessment form
- staff observation/assessment review
- basic draft-context display

1. Create an `/analytics/` section mounted from the root URL config.
2. Add an Analytics Command Center for staff/admin users.
3. Add staff/admin CSV import for player/member/roster data with preview, mapping, validation, conflict handling, and merge review.
4. Add player search and player timeline pages.
5. Add a coach-facing player list showing available players, the coach's own completion status, and already-submitted observations.
6. Add a coach-assessment observation form for one evaluator to score one player.
7. Add an observation detail/read-only view for staff review.
8. Add basic draft-context display and service logic to match player identity records to existing draft data.
9. Seed the initial coach assessment question set.
10. Use Django ORM aggregation where possible.
11. Put analytics queries, CSV import, player matching, draft matching, question handling, and observation creation in service modules, not directly inside templates.
12. Add focused tests for permission behavior, CSV parsing, import merging, ambiguous match handling, conflict handling, observation submission, response validation, evaluator-role filtering, question-set versioning, and draft-data matching.
13. Use templates and CSS consistent with the existing project style.

## Suggested Data Model

Prefer a normalized shape that supports the first coach-assessment workflow while remaining flexible for broader player intelligence. Future-facing fields should be simple and minimal in Version 1. Avoid abstraction-heavy design.

- `EvaluationCycle`: time window/event/season/draft/program context for observations.
- `ImportedRosterFile`: uploaded file metadata, source type, uploaded-by user, status, preview snapshot, row errors, conflict summary, and import summary.
- `PlayerIdentity` or temporary `AnalyticsPlayer`: imported/player identity record for observations, with stable identity fields, team/division context, source identifiers, and a clear migration path to a future shared player model.
- `PlayerSourceRow`: original source row data and unmapped fields linked to a player identity for auditability.
- `ObservationQuestionSet`: reusable collection/version of active questions assigned to a cycle and observation type.
- `ObservationQuestion`: category, prompt text, display order, active flag, response type, scoring/evaluation configuration, effective dates, retired date, and version metadata. Version 1 only needs 1-5 numeric ratings and freeform notes/text.
- `ObservationSource`: minimal source/provider metadata for coach, staff/manual entry, imported CSV, and draft matching context. Keep future sources such as AI or third-party systems possible, but do not build provider management infrastructure in Version 1.
- `EvaluatorRole`: role key and display label for the evaluator's role at submission time.
- `Observation`: evaluation cycle, player identity/reference, optional linked `drafts.DraftPlayer`, observation type, observation source, evaluator/user, evaluator role snapshot, status, submitted timestamp, notes, and source metadata.
- `ObservationResponse`: observation, question, response type, numeric value, text value, boolean value, selected choice, raw value, unit, and metadata.

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
- Do not add charts or JavaScript-heavy visualizations in the first version.
- Staff users can review all observations.
- Coaches can submit coach-assessment observations.
- Authenticated coaches may evaluate any player they know well enough to assess.
- Coaches may edit their own draft/unsubmitted observations, but staff/admin users control whether submitted observations can be reopened.
- Use service modules for analytics queries, CSV import, player matching, draft matching, question handling, and observation workflows.
- Prefer conservative, readable implementation over abstraction-heavy design.

## Deliverables

- `analytics` Django app
- URL routing
- Analytics Command Center
- Staff/admin CSV import workflow
- Player search
- Player timeline view
- Coach assessment observation list, form, and detail views
- Basic draft-context display
- Service functions for metrics
- Service functions for importing CSVs and merging player identity records
- Service functions for matching player identity records to draft data
- Models and migrations for evaluation cycles, player identity, imports, observation sources, question sets, questions, observations, responses, and evaluator roles
- Initial seed data or setup helper for the default coach assessment question set
- Dashboard, import, player timeline, and observation templates
- Minimal CSS if needed
- Tests
- Updated root URL config and settings
