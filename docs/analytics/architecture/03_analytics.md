# 03 Analytics

## Observation Architecture

Use a flexible observation model instead of a narrow assessment-only model.

An observation is any structured or semi-structured record about a player's baseball development, performance, evaluation, or context.

Version 1 implements only one observation type:

- `coach_assessment`

Use a lightweight `ObservationType` model or equivalent controlled lookup table instead of assuming observation type will always be a freeform string. Version 1 only needs one record: `coach_assessment`.

Future `ObservationType` records may include:

- tryout
- game
- practice
- bullpen
- video
- AI
- attendance
- development_note

Do not build UI, workflows, or admin management for future observation types in Version 1.

Each observation should include:

- player reference to `players.Player`
- evaluation cycle
- observation type
- observation source/provider
- evaluator/user who submitted or imported the observation, when applicable
- evaluator role at the time of submission
- status and timestamps
- responses to configured questions or fields
- raw/source metadata where useful for auditability

Store evaluator role as a snapshot on the observation record because user roles may change over time. Reports must be able to filter observations by evaluator role.

## Evaluation Cycles

Use `EvaluationCycle` to represent the time window, event, season, draft, or program context that groups related observations.

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

## Questions And Responses

Use `ObservationQuestionSet` and `ObservationQuestion` or equivalent names.

Questions must not be hard-coded into templates. Staff/admin users should be able to add, remove, deactivate, reorder, or revise coach assessment questions over time.

Historical observations must remain interpretable after questions change. Prefer versioning, effective dates, retired dates, deactivation, and question-set snapshots over destructive deletion once a question has responses.

Version 1 only needs:

- 1-5 numeric rating responses
- freeform notes/text responses

The response model should remain future-ready for additional response types, including:

- boolean
- multiple choice
- velocity
- time
- distance

Do not fully implement future response-type UI or workflows unless required by the coach assessment workflow.

## ObservationResponse

`ObservationResponse` should include:

- observation
- question
- response type
- numeric value
- text value
- boolean value
- selected choice
- raw value
- unit
- payload
- metadata

Use `payload` as a JSON field for future structured responses, including possible AI-generated response details. Version 1 does not need UI for payload values.

## Observation Sources

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

Do not overbuild provider infrastructure in Version 1. Do not implement GameChanger, Pocket Radar, Rapsodo, TrackMan, AI, or other future integrations.

## Future Measurements

Observations and measurements are different concepts.

Observations represent evaluator opinions, notes, or structured feedback. Examples:

- "Throws accurately"
- "Shows leadership"

Measurements represent objective values. Examples:

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

Future architecture may introduce models such as:

- `MeasurementDefinition`
- `PlayerMeasurement`
- `MeasurementRecord`

Future versions may correlate observations and measurements.

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

Do not implement attachment workflows in Version 1.
