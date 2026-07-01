# 04 Imports

## Ownership

Player identity import is part of the `players` bounded context.

The `players` app owns:

- player imports
- player matching
- duplicate merging
- aliases
- source identifiers
- source rows
- provenance

The analytics app may provide an "Import Players" page in the Analytics Command Center for Version 1, but the underlying import logic should call `players.services.import_service` and related `players` services.

## Source Files

The project should import CSV files that describe the same player population with different levels of detail.

Example source files include:

- A member-list CSV with fields such as first name, last name, role, age, gender, and team.
- A roster-detail CSV with fields such as first name, last name, player/non-player status, address, city, birthdate, jersey number, position, email, phone number, gender, contacts/guardians, team ID, team, division, registration fields, baseball history, positions, throwing, batting, medical notes, availability, volunteering, sponsorship, and comments.

## Import Workflow

Version 1 should support CSV upload through a staff/admin-only import workflow exposed from the Analytics Command Center.

Requirements:

- Provide a preview step before committing imported data.
- Allow staff to map source columns to `players.Player` fields.
- Normalize common header variants, for example `First Name` and `First` should both map to first name.
- Use `players.services.import_service` to import player identity data.
- Use `players.services.matching_service` to match players conservatively.
- Merge files that refer to the same players instead of creating duplicates.
- Flag ambiguous matches for staff review instead of automatically merging risky records.
- Record field-level conflicts during import preview.
- Allow staff/admin users to choose whether to keep the existing value, use the imported value, or store the imported value only as source-row metadata.
- Support importing multiple CSVs for the same evaluation cycle.

## Matching And Merge Strategy

Match players conservatively using reusable player-matching logic from `players.services.matching_service`, using a combination of:

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

If an imported player already exists with a high-confidence match, enrich the existing `players.Player` record instead of creating a duplicate.

For high-confidence matches, fill missing fields from the new import and attach the new source row to the existing player through `players.PlayerSourceRow`.

Do not silently overwrite important existing player fields when the new import conflicts with stored data.

If one imported row matches multiple possible existing players, mark it as ambiguous and require staff review before merge.

If one existing player appears in multiple imported files, keep one player record and attach each source row/import record to that player.

If no existing player can be matched confidently, create a new `players.Player`.

## Provenance

Preserve source filename, import timestamp, imported-by user, row number, original row data, and unmapped extra fields in `players` provenance models for audit/debugging.

Analytics consumes imported players, displays imported context, uses player matching services, and links observations to players.
