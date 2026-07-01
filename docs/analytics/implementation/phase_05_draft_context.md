# Phase 05: Draft Context

## Purpose

Display draft context from the existing `drafts` app without asking coaches to manually enter draft selection information.

## Architecture References

- [06 Draft Integration](../architecture/06_draft_integration.md)
- [09 Services](../architecture/09_services.md)

## Existing Project Integration

Before implementing this phase, inspect relevant existing project conventions, including:

- existing `drafts` models and service-layer patterns
- URL and template conventions for cross-app links
- permission patterns for staff/coach views
- query optimization patterns
- test organization for cross-app behavior

## Scope

- Match `players.Player` records to existing draft data.
- Display draft context where available.
- Show unmatched/missing draft context clearly.
- Support expected draft round vs actual draft comparison inputs/results from coach assessments.

## Out of Scope

- Changing `drafts` app behavior.
- Duplicating draft selection logic.
- Draft management UI.
- Draft import changes.
- Public draft pages.
- Advanced draft analytics beyond Version 1 context display.

## Deliverables

- [ ] `analytics/services/draft_service.py`.
- [ ] Draft matching helper functions.
- [ ] Draft context summary objects for templates/services.
- [ ] Basic draft-context display on relevant assessment/profile views.
- [ ] Tests for draft matching and unmatched states.

## Models

- No new models expected.
- Use existing `drafts` models/actions.
- Use existing analytics observation responses for subjective expected draft round responses.

## Services

- `analytics/services/draft_service.py`
  - find draft player matches for `players.Player`
  - derive draft room/team/pick/round context
  - expose unmatched status
  - compare expected vs actual draft context

## Views

- Integrate draft context into existing assessment review and player profile views.
- No standalone draft management view required.

## Templates

- Draft context partial for reuse.
- Unmatched/missing draft context display.

## URLs

- No new URLs required unless implementation chooses a staff-only draft matching review page within Version 1 scope.

## Admin

- No new admin required.

## Migrations

- None expected.

## Tests

- Draft context is derived from existing draft models/actions.
- Coaches are not asked to type actual draft selection data.
- Unmatched player shows missing/unmatched context.
- Expected vs actual draft comparison can be computed when data exists.
- Existing `drafts` behavior remains unchanged.

## Acceptance Criteria

- Draft context displays where available.
- Draft context is read from `drafts`, not duplicated.
- Missing/unmatched context is clear to staff/coaches.
- Tests for this phase pass.

## Definition of Done

This phase is complete when:

- [ ] All deliverables are complete.
- [ ] Acceptance criteria are satisfied.
- [ ] Tests for the phase pass.
- [ ] Documentation is updated if implementation details changed.
- [ ] Phase Review is completed.
- [ ] `docs/analytics/implementation/STATUS.md` is updated.

## Risks / Open Questions

- Existing draft data may not have enough stable identifiers for reliable matching.
- Round calculation may need a clear rule if drafts only store pick order.
- Name-only matching may be ambiguous and should remain conservative.

## Implementation Notes


## Phase Review

### What went well

### Challenges

### Technical debt

### Architecture changes

### Recommendations for the next phase
