# 02 Players

## Shared Player App

Introduce a separate Django app named `players`.

The `players` app owns the core player identity model used across the project.

Use:

- App: `players`
- Main model: `Player`

`players.Player` is the canonical future player identity model. It must not be designed as a dependent extension of the legacy `pdp.PlayerProfile` model.

`pdp.PlayerProfile` is transitionary and should only be considered for coexistence, migration planning, or temporary bridge logic if required. Do not migrate PDP workflows in Version 1 unless explicitly instructed.

Avoid naming the app `player_profiles`, because the player entity will eventually be used by many systems, not just profile pages.

Avoid putting the canonical player model inside `analytics`, because future apps such as analytics, drafts, PDP, video, attendance, recruiting, awards, and parent/player portals will all need to reference the same player identity.

Analytics should reference `players.Player`.

```python
class Observation(models.Model):
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE)
```

## Player Model

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

Version 1 fields should support:

- first name
- last name
- preferred/nickname when available
- birthdate or birth year when available
- gender when available
- team/division context
- source identifiers such as registration ID, registrant ID, team ID, or draft player ID
- safe reporting fields
- source metadata

Do not expose sensitive fields such as addresses, medical notes, phone numbers, emails, or guardian/contact details to ordinary coach assessment screens unless explicitly needed and permissioned.

## Player Aliases

`players.PlayerAlias` should support alternate names and aliases for player matching and display.

Examples:

- preferred names
- nicknames
- imported spelling variants
- names with punctuation or quote differences

## Source Identifiers

`players.PlayerSourceIdentifier` should store external/source identifiers such as:

- registration ID
- registrant ID
- team ID
- draft player ID
- imported source keys

## Provenance

`players.PlayerSourceRow` should store original source row data and unmapped fields linked to a `players.Player` record for auditability and provenance.

Preserve:

- source filename
- import timestamp
- imported-by user
- row number
- original row data
- unmapped fields

## Player Tags

Add a lightweight tagging system so staff can organize and search players using baseball-specific labels.

Create `players.PlayerTag` with a many-to-many relationship to `players.Player`.

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
- tags appear on the Player Profile page
- tags appear on the player timeline
- tags are searchable/filterable
- coaches do not manage tags unless future permissions allow it

Keep tagging intentionally simple.

## Player Matching

Player matching belongs in `players.services.matching_service`.

Use conservative matching based on combinations of:

- first name
- last name
- birthdate
- team
- division
- email where permissioned
- registration ID
- registrant ID
- team ID
- other stable identifiers

Ambiguous matches should require staff review instead of risky automatic merging.

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
