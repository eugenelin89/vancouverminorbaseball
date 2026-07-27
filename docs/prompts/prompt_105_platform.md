# Prompt 105 - Platform

## User Prompt

```text
You are working in the Django project located at:

/Users/eugenelin/dev/vmba0

The production site is:

https://vancouverminor.com/

A recent responsive UI pass successfully converted wide tables into stacked mobile cards. The submitted-evaluations page is now usable on mobile, but the action rows need a small polish pass.

## Objective

Improve the mobile presentation of action cells in responsive table cards.

On the submitted-evaluations page, the “Review” button currently wraps onto two lines because the action cell uses the same two-column label/value grid as ordinary data fields.

The current mobile card layout shows something like:

ACTION        REV
              IEW

This should instead render as a clean action section:

ACTION

[ Review ]

The button should be full width or otherwise wide enough to prevent wrapping.

## Required changes

Update the shared responsive table-card CSS so cells with these labels receive special mobile treatment:

- `data-label="Action"`
- `data-label="Actions"`

At the mobile breakpoint:

1. Render action cells as a block rather than the standard two-column field grid.
2. Display the action label above the buttons.
3. Add sensible spacing between the label and the action controls.
4. Make action buttons easy to tap.
5. Prevent short action text such as “Review”, “Open”, “Edit”, “Profile”, and “Compare” from wrapping unnecessarily.
6. Allow multiple action buttons to wrap or stack cleanly.
7. Preserve the existing desktop table layout.
8. Apply the treatment consistently across all responsive table classes already supported by the mobile-card system, including:
   - `.pdp-table`
   - `.draft-table`
   - `.team-table`
   - `.scholarship-table`
   - `.tryout-table`
9. Avoid inline styles and page-specific hacks where a shared reusable rule is appropriate.

A suitable implementation may resemble:

```css
.pdp-table[data-responsive="cards"] td[data-label="Action"],
.pdp-table[data-responsive="cards"] td[data-label="Actions"] {
    display: block;
}

.pdp-table[data-responsive="cards"] td[data-label="Action"]::before,
.pdp-table[data-responsive="cards"] td[data-label="Actions"]::before {
    display: block;
    margin-bottom: 0.6rem;
}

.pdp-table[data-responsive="cards"] td[data-label="Action"] .button,
.pdp-table[data-responsive="cards"] td[data-label="Actions"] .button {
    width: 100%;
    white-space: nowrap;
}
```
```

## Implementation Commit Diff

```diff
diff --git a/static/css/pdp.css b/static/css/pdp.css
index afe6199..c983550 100644
--- a/static/css/pdp.css
+++ b/static/css/pdp.css
@@ -433,12 +433,41 @@
         content: none;
     }
 
+    .pdp-table[data-responsive="cards"] td[data-label="Action"],
+    .pdp-table[data-responsive="cards"] td[data-label="Actions"] {
+        display: flex;
+        align-items: stretch;
+        flex-direction: column;
+        gap: 0.65rem;
+    }
+
+    .pdp-table[data-responsive="cards"] td[data-label="Action"]::before,
+    .pdp-table[data-responsive="cards"] td[data-label="Actions"]::before {
+        display: block;
+        margin-bottom: 0;
+    }
+
     .pdp-table[data-responsive="cards"] td .button,
     .pdp-table[data-responsive="cards"] td button {
         width: 100%;
         justify-content: center;
     }
 
+    .pdp-table[data-responsive="cards"] td[data-label="Action"] .button,
+    .pdp-table[data-responsive="cards"] td[data-label="Action"] button,
+    .pdp-table[data-responsive="cards"] td[data-label="Action"] a,
+    .pdp-table[data-responsive="cards"] td[data-label="Actions"] .button,
+    .pdp-table[data-responsive="cards"] td[data-label="Actions"] button,
+    .pdp-table[data-responsive="cards"] td[data-label="Actions"] a {
+        display: flex;
+        align-items: center;
+        width: 100%;
+        min-height: 2.75rem;
+        justify-content: center;
+        text-align: center;
+        white-space: nowrap;
+    }
+
     .pdp-table th,
     .pdp-table td {
         padding: 0.72rem 0.65rem;
diff --git a/static/css/styles.css b/static/css/styles.css
index 023b804..09634da 100644
--- a/static/css/styles.css
+++ b/static/css/styles.css
@@ -2745,6 +2745,57 @@ table.tryout-table td:last-child {
     .tryout-table[data-responsive="cards"] td:not([data-label])::before {
         content: none;
     }
+
+    .draft-table[data-responsive="cards"] td[data-label="Action"],
+    .draft-table[data-responsive="cards"] td[data-label="Actions"],
+    .team-table[data-responsive="cards"] td[data-label="Action"],
+    .team-table[data-responsive="cards"] td[data-label="Actions"],
+    .scholarship-table[data-responsive="cards"] td[data-label="Action"],
+    .scholarship-table[data-responsive="cards"] td[data-label="Actions"],
+    .tryout-table[data-responsive="cards"] td[data-label="Action"],
+    .tryout-table[data-responsive="cards"] td[data-label="Actions"] {
+        display: flex;
+        align-items: stretch;
+        flex-direction: column;
+        gap: 0.65rem;
+    }
+
+    .draft-table[data-responsive="cards"] td[data-label="Action"]::before,
+    .draft-table[data-responsive="cards"] td[data-label="Actions"]::before,
+    .team-table[data-responsive="cards"] td[data-label="Action"]::before,
+    .team-table[data-responsive="cards"] td[data-label="Actions"]::before,
+    .scholarship-table[data-responsive="cards"] td[data-label="Action"]::before,
+    .scholarship-table[data-responsive="cards"] td[data-label="Actions"]::before,
+    .tryout-table[data-responsive="cards"] td[data-label="Action"]::before,
+    .tryout-table[data-responsive="cards"] td[data-label="Actions"]::before {
+        display: block;
+        margin-bottom: 0;
+    }
+
+    .draft-table[data-responsive="cards"] td[data-label="Action"] a,
+    .draft-table[data-responsive="cards"] td[data-label="Action"] button,
+    .draft-table[data-responsive="cards"] td[data-label="Actions"] a,
+    .draft-table[data-responsive="cards"] td[data-label="Actions"] button,
+    .team-table[data-responsive="cards"] td[data-label="Action"] a,
+    .team-table[data-responsive="cards"] td[data-label="Action"] button,
+    .team-table[data-responsive="cards"] td[data-label="Actions"] a,
+    .team-table[data-responsive="cards"] td[data-label="Actions"] button,
+    .scholarship-table[data-responsive="cards"] td[data-label="Action"] a,
+    .scholarship-table[data-responsive="cards"] td[data-label="Action"] button,
+    .scholarship-table[data-responsive="cards"] td[data-label="Actions"] a,
+    .scholarship-table[data-responsive="cards"] td[data-label="Actions"] button,
+    .tryout-table[data-responsive="cards"] td[data-label="Action"] a,
+    .tryout-table[data-responsive="cards"] td[data-label="Action"] button,
+    .tryout-table[data-responsive="cards"] td[data-label="Actions"] a,
+    .tryout-table[data-responsive="cards"] td[data-label="Actions"] button {
+        display: flex;
+        align-items: center;
+        width: 100%;
+        min-height: 2.75rem;
+        justify-content: center;
+        text-align: center;
+        white-space: nowrap;
+    }
 }
 
 @media (max-width: 380px) {
```
