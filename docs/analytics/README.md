# Analytics Subsystem

The Analytics subsystem is VCB's first module for Baseball Intelligence and long-term player development analytics.

Version 1 remains intentionally focused on replacing the current spreadsheet-based coach assessment workflow while establishing a clean foundation for future analytics, player development, reporting, measurements, and integrations.

The authoritative architecture handbook lives in [architecture/README.md](architecture/README.md).

Local setup and smoke testing instructions live in [local_development.md](local_development.md).

Future implementation prompts should reference the relevant handbook documents instead of embedding or restating the full architecture.

## Reusable Prompts

Reusable Codex prompts for planning, implementing, reviewing, and fixing Analytics implementation phases should live in [prompts/](prompts/).

Prompts should reference the Architecture Handbook and the relevant Implementation Handbook phase document instead of restating architecture.

Recommended prompt workflow:

1. Plan phase.
2. Implement phase.
3. Review phase.
4. Apply approved fixes.
5. Update the phase review and [implementation/STATUS.md](implementation/STATUS.md).

Do not implement multiple phases from a single prompt unless explicitly instructed.
