Create the Phase 6 engineering plan only.

Do NOT implement code.

Use the repository discovery findings from the previous run:

- Current incomplete phase: Phase 6 - Player Experience
- Missing file: docs/analytics/implementation/engineering/phase_06_player_experience.md
- Phase 6 tracking doc exists: docs/analytics/implementation/phase_06_player_experience.md
- Relevant architecture docs exist:
  - docs/analytics/architecture/07_player_experience.md
  - docs/analytics/architecture/08_reporting.md
  - docs/analytics/architecture/09_services.md
  - docs/analytics/architecture/90_implementation_roadmap.md

Task:

Create:

docs/analytics/implementation/engineering/phase_06_player_experience.md

The engineering plan should resolve the missing/underspecified Phase 6 details without implementing code.

Include:

1. Phase goal
2. Strict scope
3. Out-of-scope items
4. Files to create
5. Files to modify
6. URL names and paths
7. View classes
8. Service functions and dataclasses
9. Player search/filter semantics
10. Draft status filter semantics
11. Evaluation completion filter semantics
12. Player profile layout
13. Timeline item shape
14. Timeline ordering rules
15. Comparison page behavior
16. Draft context lookup from canonical players.Player
17. Permission model
18. Empty states
19. Tests to write
20. Implementation sequence
21. Risks/open questions
22. Definition of done

Important constraints:

- Phase 6 is staff-only.
- Do not implement Phase 7.
- Do not add dashboards, charts, exports, AI summaries, reporting engine, or timeline database models.
- Use dataclasses/read models only.
- Reuse existing Phase 5 draft context service where possible.
- Keep business logic in services.
- Keep views thin.
- Keep templates presentation-only.
- Do not modify code except creating/updating documentation for the Phase 6 engineering plan.

Also update docs/analytics/implementation/STATUS.md only if needed to clarify that Phase 6 is the next phase to implement, but do not mark Phase 6 complete.

Final report:
- files created
- files modified
- summary of decisions made
- confirmation no code was implemented