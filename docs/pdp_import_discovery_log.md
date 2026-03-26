# PDP Import Discovery Log

## 2026-03-26

### Workbook Reviewed

`/Users/eugenelin/Desktop/VCB2026/VCB House - 13u PeeWee Assessment.xlsx`

### Discovery

The workbook is a valid `.xlsx` file with four worksheets:

- `Ranking `
- `Pitcher Ranking `
- `Assessment Data`
- `Pitching Data `

The current PDP importer can parse the workbook container and read the sheets, but it is **not safe to fully import this workbook yet**.

Reason:

- the current `.xlsx` parser assumes the first non-empty row in each sheet is the header row
- `Pitcher Ranking ` and `Pitching Data ` follow that rule
- `Ranking ` and `Assessment Data` do **not** follow that rule
- those two sheets use row 1 as a title/grouping row and row 2 as the actual field headers

Examples observed:

- `Ranking ` row 1 contains a title: `VCB House 13 U - PeeWee Assessment - Performance Scores`
- `Ranking ` row 2 contains the actual headers such as `Name`, `Speed Ranking`, `Power Ranking`
- `Assessment Data` row 1 contains grouped section labels such as `Athleticism Evaluation`
- `Assessment Data` row 2 contains the actual headers such as `Name`, `Home to 1st`, `Broad Jump`, `Bat Speed`

### Recommendation

Do not import this workbook with the current importer as-is.

Recommended next change:

1. Add per-sheet header row selection to the import flow.
2. Support skipping title rows above the actual headers.
3. Preserve grouped heading rows as optional sheet metadata instead of treating them as data headers.
4. Re-test this workbook after the parser change before using it for production imports.

### Practical Impact

Current status by sheet:

- `Pitcher Ranking `: likely importable
- `Pitching Data `: likely importable
- `Ranking `: not safe with current parser
- `Assessment Data`: not safe with current parser

Overall status:

- This workbook should be treated as **not fully import-compatible** until header-row selection is added.
