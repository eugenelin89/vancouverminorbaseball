# Drafts App

`drafts` is a reusable Django app for running live player drafts across seasons and divisions.

## Workflow

1. Create a draft room with a year, division, and team list.
2. Import players from CSV. Only `First` and `Last` are required.
3. Preview the import results and confirm.
4. Open the draft when the room is ready.
5. Use the command center to assign players, move players, undo mistakes, and review the audit timeline.
6. Use the trade desk for roster swaps.
7. Close the draft to lock player movement.
8. Export final rosters when complete.

## CSV Import Rules

- Required columns: `First`, `Last`
- Additional columns are accepted automatically and stored in `DraftPlayer.extra_data`
- Original rows are preserved in `DraftPlayer.imported_row`
- Headers are normalized for required-field matching
- Rows missing `First` or `Last` are rejected
- Duplicate players within the same draft are rejected during import

## Service Layer

Business logic lives in `drafts/services.py`:

- `create_draft`
- `import_players`
- `draft_player`
- `move_player`
- `remove_player_from_team`
- `trade_players`
- `revert_action`
- `change_draft_status`

All roster-changing operations run inside database transactions and write a `DraftAction` audit record.
