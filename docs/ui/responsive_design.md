# Responsive UI Guide

This guide documents the responsive layout conventions used by the VCB platform.
It is intended for developers and maintainers who add or update Django templates.

## Purpose

The platform is used on phones, tablets, laptops, and desktops. Staff workflows
often include dense tables, but key user journeys must remain readable and usable
on narrow screens.

Responsive work should preserve existing server-rendered behavior. Do not add
JavaScript solely to make a table usable on mobile unless a workflow explicitly
requires it.

## Breakpoints

- Mobile: up to `640px`.
- Tablet and narrow desktop: existing app layouts use intermediate breakpoints
  around `760px`, `820px`, `900px`, `960px`, and `1180px`.
- Desktop: layouts should continue to use the existing table and grid patterns.

When testing manually, check at least:

- `320px`
- `375px`
- `390px`
- `430px`
- tablet portrait
- desktop

## Responsive Tables

Most user-facing tables should use the table-to-card pattern on mobile.

Use:

```html
<div class="table-wrap table-wrap--cards">
  <table class="pdp-table" data-responsive="cards">
    <thead>...</thead>
    <tbody>
      <tr>
        <td data-label="Player">...</td>
        <td data-label="Team">...</td>
      </tr>
    </tbody>
  </table>
</div>
```

For non-PDP tables, the same `data-responsive="cards"` pattern is supported for:

- `.draft-table`
- `.team-table`
- `.scholarship-table`
- `.tryout-table`

Each mobile card cell must include a concise `data-label` matching the column
meaning. Empty-state rows may omit `data-label`.

## Form Layouts

Use the existing form containers and field patterns. Forms should stack naturally
on mobile, with full-width inputs and buttons where practical.

The PDP-style form utility `.pdp-form` uses a responsive grid so labels and
controls remain readable on mobile without fixed widths.

## Pages Converted To Mobile Cards

The responsive card pattern is used across representative high-traffic workflows:

- Account operations dashboard, user list, user detail, user links, coach import
  preview, and coach import result.
- Analytics player imports, coach assessments, evaluation submission, submitted
  evaluation review, staff review, player search, player profile context,
  comparison, and My Evaluations.
- Season operations lists and detail tables for seasons, teams, memberships,
  coach assignments, player history, and coach history.
- Draft list and draft import previews.
- Public registration, tryouts, scholarship staff review, LeagueHub summary
  tables, and legacy PDP data tables.

## Intentionally Scrollable Tables

Some dense operational tables remain horizontally scrollable instead of becoming
cards:

- Draft command center roster/player-pool tables.
- Public live draft board tables.
- Analytics command center summary/matrix tables.

These pages are dense comparison or live-operation surfaces where preserving
side-by-side columns is more useful than stacking every cell into cards. If these
surfaces become primary mobile workflows, redesign them as dedicated mobile
views rather than forcing the same desktop matrix into cards.

## Accessibility Notes

- Do not duplicate table content for mobile.
- Keep the original `<table>` structure in the template.
- Use CSS display changes for the mobile card layout.
- Ensure every meaningful cell has a `data-label`.
- Keep action links and buttons keyboard accessible.

## QA Checklist

Before finishing a template change:

- The page has no unreadable fixed-width table on mobile.
- Table card labels are clear and not duplicated in confusing ways.
- Actions remain reachable without horizontal scrolling.
- Empty states still read correctly.
- Desktop table layout is unchanged.
- `git diff --check` passes.
- Existing page/view tests still pass.
