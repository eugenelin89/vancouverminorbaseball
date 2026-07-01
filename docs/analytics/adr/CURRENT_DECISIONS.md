# Current Analytics Architecture Decisions

This file is a quick index of accepted/current architecture decisions for the Analytics subsystem.

Individual ADR files can be created later for decisions that need deeper context, alternatives, and consequences.

## Player Identity App

Decision: Player identity lives in the `players` app.

Status: Accepted

Related architecture document: [02 Players](../architecture/02_players.md)

## Analytics Player References

Decision: Analytics stores observations, not canonical player identity.

Status: Accepted

Related architecture document: [03 Analytics](../architecture/03_analytics.md)

## Coach Assessments As Observations

Decision: Coach assessments are implemented as `coach_assessment` observations.

Status: Accepted

Related architecture document: [05 Coach Assessments](../architecture/05_coach_assessments.md)

## Version 1 Scope

Decision: Version 1 is intentionally limited to coach assessments, imports, player search/profile/timeline, staff review, simple comparison, draft context, and command center summaries.

Status: Accepted

Related architecture document: [00 Overview](../architecture/00_overview.md)

## Human Decision-Making

Decision: Final baseball decisions remain with people, not software.

Status: Accepted

Related architecture document: [00 Overview](../architecture/00_overview.md)
