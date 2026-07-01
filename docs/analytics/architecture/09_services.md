# 09 Services

## Service Philosophy

Use structured service packages instead of one large service module.

Business logic should live inside service modules. Views should coordinate requests and responses. Templates should remain presentation only. Keep model methods limited to validation or simple helper methods.

## Players Services

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

The `players` service package owns:

- player identity management
- player matching
- player imports
- player aliases
- player source identifiers
- player tag management
- player identity provenance

Player matching should be reusable infrastructure for future apps such as analytics, recruiting, attendance, video, and PDP.

## Analytics Services

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

The `analytics` service package owns:

- observations
- questions
- reports
- metrics
- timelines
- comparisons
- draft analytics
- observation workflows

Analytics services should call `players.services.identity_service`, `players.services.matching_service`, `players.services.import_service`, and `players.services.tag_service` when they need player identity, player matching, player import, provenance, or tag behavior.

## Service Boundaries

Version 1 implementation should put analytics queries, draft matching, question handling, reporting calculations, timeline assembly, comparison logic, and observation creation in analytics service modules.

Version 1 implementation should put player identity management, player matching, player imports, aliases, source identifiers, provenance, and tag management in `players/services/`.
