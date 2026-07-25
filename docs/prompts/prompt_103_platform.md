# Prompt 103 - Platform

## User Prompt

```text
Document the import process, including the mappings, in the project. this is an official prompt. using correct workflow.
```

## Implementation Commit

```text
8da0cf1 Document player import workflow
```

## Commit Diff

```diff
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 1068665..1c81d34 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -341,6 +341,8 @@ Optional CSV columns:
 
 Staff must select an active season when uploading the coach CSV. Team and division are required for the seasonal coach assignment.
 
+If the CSV includes a `season` column, each row must match the season selected on the upload page. If the CSV does not include a `season` column, the selected upload season is used.
+
 Coach import creates or reuses coach login accounts. It does not create player records and does not create coach-to-player links.
 
 New imported coach accounts are active by default and must change password on first login. Returning coach accounts are reused without changing their password or activation status.
@@ -696,6 +698,79 @@ Birthdate is supported and is important for player identity and account provisio
 
 Season, division, and team are required for the current player import workflow. Division and team are used as roster context for the selected season rather than as permanent player identity.
 
+### Player Import Source
+
+The source field describes where the CSV came from. It is saved with the import for provenance and future troubleshooting.
+
+Use:
+
+- `Manual staff CSV` for staff-prepared files, including team-by-team files derived from a master spreadsheet.
+- `VCB member list CSV` only for files exported directly from the member-list source.
+- `VCB roster detail CSV` only for files exported directly from the roster-detail source.
+
+For the current Spring 2026 team-by-team import files, use `Manual staff CSV` because the files were manually prepared for import.
+
+### Player Import Column Mapping
+
+After upload, the mapping page asks which CSV column should feed each platform field. The preview table shown after refreshing is not the mapping table; it is the result of applying the mapping.
+
+For the current roster import CSV format, use this mapping:
+
+| Platform field | CSV column to choose | Required? | Notes |
+| --- | --- | --- | --- |
+| First name | `first_name` | Yes | Required unless `full_name` is mapped instead. |
+| Last name | `last_name` | Yes | Required unless `full_name` is mapped instead. |
+| Full name | Leave blank | No | Use only when the CSV has one full-name column instead of separate names. |
+| Preferred name | Leave blank unless present | No | Use for nicknames only when staff intentionally want them imported. |
+| Birthdate | `birthdate` | Strongly recommended | Required for player account provisioning with the birthdate password rule. |
+| Birth year | `birth_year` | Optional | Useful for matching and review when available. |
+| Gender | `gender` | Optional | Import if available. |
+| Division | `division` | Yes for roster imports | Used to create or reuse the seasonal team context. |
+| Team name | `team_name` | Yes for roster imports | Used to create or reuse the seasonal team context. |
+| Primary positions | Leave blank unless present | Optional | Import only if the CSV contains maintained position data. |
+| Bats | `bats` | Optional | Import if available. |
+| Throws | `throws` | Optional | Import if available. |
+| School | `school` | Optional | Import if available. |
+| Graduation year | Leave blank unless present | Optional | Import only if the CSV has a graduation/class year. |
+| Registration id | Leave blank unless present | Optional | Source identifier only. |
+| Registrant id | Leave blank unless present | Optional | Source identifier only. |
+| Team id | Leave blank unless present | Optional | Source identifier only. |
+| Source player id | `source_player_id` | Recommended | Helps future imports match the same player. |
+| Player login email | Leave blank by default | Optional | Map only when the email belongs to the player's own login account. Do not map parent, guardian, registration, or family contact emails. |
+| Roster status | `roster_status` | Optional | Defaults are handled by the import when blank. |
+| Jersey number | Leave blank unless present | Optional | Import only if the CSV has jersey numbers. |
+| Membership start date | `membership_start_date` | Recommended | Used as the start date for the seasonal roster membership. |
+| Membership end date | Leave blank unless present | Optional | Use only when importing ended memberships. |
+| Roster source id | `roster_source_id` | Recommended | Helps future imports match the same roster membership. |
+
+Do not map every field just because it appears on the page. Map only fields that exist in the CSV and are meaningful for this import.
+
+### Reading The Player Import Preview
+
+After clicking **Refresh Preview**, review the preview table before confirming.
+
+The preview columns mean:
+
+- **Row**: the row number from the CSV file.
+- **Player**: the player identity parsed from the mapped columns.
+- **Roster**: the season roster context, usually division plus team.
+- **Action**: whether the player will be created, updated, skipped, or sent to review.
+- **Membership**: whether the season roster membership will be created or updated.
+- **Match**: how the import matched the row to an existing player. `no_match` is expected for a brand-new roster.
+- **Issues**: row errors, warnings, conflicts, or review notes.
+
+For a brand-new team import, it is normal to see `create`, `Create Membership`, and `no_match` for every row, with no issues.
+
+Do not click **Confirm Import** until:
+
+- the row count matches the CSV;
+- required player names are shown correctly;
+- the roster column shows the expected division and team;
+- the issue column is blank or contains only warnings staff have reviewed;
+- rows needing review have been resolved or skipped.
+
+If the preview shows unmapped required fields, go back to the mapping section, choose the missing CSV columns, and click **Refresh Preview** again.
+
 ### Account Provisioning From Player Imports
 
 During a player import, staff may choose to provision player accounts.
@@ -710,6 +785,24 @@ When account provisioning is enabled:
 
 Accounts are not created when required information is missing, such as birthdate for the temporary-password rule.
 
+Player account usernames are generated from the player name, normally `firstname.lastname`, with a suffix added if needed to avoid a username collision. The temporary password uses the player's birthdate in `YYYYMMDD` format. For example, a player born on April 1, 2013 receives the temporary password `20130401`.
+
+Player login email is optional. If it is blank, the player account is still created with a blank email. If a mapped player login email is already used by another account, the import still creates the player account with a blank email and reports a warning. Shared family contact emails should not be mapped as player login emails.
+
+### Player Import Troubleshooting
+
+If preview fails or the page does not show the expected mappings, check:
+
+- the CSV has a header row;
+- the header names match the columns you intend to map;
+- the file is saved as CSV, not an Excel workbook;
+- the file is not empty and is below the upload size limit;
+- required mappings include either `first_name` and `last_name`, or `full_name`;
+- `division` and `team_name` are mapped for roster imports;
+- parent, guardian, or registration contact emails are not mapped to `Player login email`.
+
+If the import result succeeds, the result page shows how many players, teams, roster memberships, and player accounts were created or updated.
+
 ## Draft Workflows
 
 ### Purpose
```
