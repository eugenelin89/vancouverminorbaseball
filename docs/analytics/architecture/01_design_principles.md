# 01 Design Principles

## Design Philosophy

The platform is intentionally designed using these principles:

- Build only the smallest useful Version 1.
- Favor explicit, readable Django code over clever abstractions.
- Separate player identity from baseball observations.
- Treat observations as historical records that should rarely be modified.
- Prefer configuration over hard-coded baseball rules.
- Keep business logic in service modules.
- Keep views thin and templates presentation-only.
- Design for incremental expansion rather than predicting every future requirement.
- Support coaches and staff through better information rather than automation of baseball decisions.

## Version 1 Philosophy

Version 1 is not a broad player development platform yet. It is a practical workflow replacement for spreadsheet-based coach assessments.

It should include only:

- Analytics Command Center
- CSV import workflow
- player search
- Player Profile page with timeline
- Player Comparison
- coach assessment list
- coach assessment form
- staff observation/assessment review
- basic draft-context display

## Deferred Capabilities

The following are supported by the architecture but not implemented in Version 1:

- non-`coach_assessment` observation workflows
- third-party integrations
- provider management UI
- future response-type UI beyond 1-5 ratings and notes
- measurements
- observation attachment workflows
- Watch Lists
- reporting engine
- advanced charts or JavaScript-heavy visualization
- AI workflows
- parent/player portal surfaces

## Responsibility Boundaries

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
