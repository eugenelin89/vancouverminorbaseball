Perform Platform V1 UI Hardening only: Mobile-First Responsive Design Review and Optimization.

Use continuous loop engineering.

Continue until the current Platform V1 interface is responsive, usable, accessible, and production-ready on common mobile and tablet screen sizes; all verified issues are fixed; tests and tooling pass; documentation is updated; commits are pushed; and the working tree is clean.

Do not implement Platform V2.

Do not add new product features.

Do not redesign the brand or replace the existing visual language.

Do not introduce a JavaScript framework or frontend build system.

==================================================
Current State
=============

Platform V1 is complete and frozen.

Current implemented areas include:

* public website;
* authentication and forced password change;
* account profile;
* Account Operations;
* player import;
* coach import;
* Season Operations;
* evaluation submission;
* My Evaluations;
* coach evaluation review;
* staff Analytics;
* draft workflows;
* PDP legacy pages;
* LeagueHub and Scholarships pages.

The interface is server-rendered using Django templates and shared CSS.

The current repository uses plain HTML and CSS without frontend build tooling.

The goal is to make every current production workflow work well on mobile devices without changing application behavior.

==================================================
Objective
=========

Review and optimize the complete current UI for:

* phones;
* tablets;
* narrow browser windows;
* touch interaction;
* readable typography;
* responsive navigation;
* usable forms;
* usable tables;
* safe destructive actions;
* accessible controls;
* long content;
* validation and error messages;
* import previews;
* review pages;
* empty states.

The result should remain visually consistent with the current platform.

This is a responsive-design and usability-hardening phase.

It is not a product redesign.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete responsive-design, usability, accessibility, testing, or documentation work remains.

PASS

All acceptance criteria are satisfied, verification passes, commits are pushed, and the working tree is clean.

BLOCKED

A material responsive-design issue requires a product redesign, external design decision, browser/device infrastructure, or architecture expansion outside this phase.

NO_PROGRESS

Two consecutive loops fail to make meaningful progress toward a verified unresolved issue.

Do not continue through cosmetic-only changes.

==================================================
Established Loop Workflow
=========================

Every loop must:

1. reconcile the committed repository state;
2. read `AGENTS.md`;
3. confirm the working tree is clean;
4. inspect current shared templates, app templates, and CSS;
5. inventory responsive issues by route/workflow;
6. classify issues by severity;
7. create the next prompt archive before implementation;
8. fix only verified responsive and accessibility issues;
9. add or update focused tests where useful;
10. run tooling on touched files only;
11. perform browser-oriented self-review;
12. fix every verified regression;
13. update documentation where user behavior or responsive conventions materially change;
14. run focused and full verification;
15. commit implementation, tests, and documentation;
16. finalize and separately commit the prompt archive;
17. push both commits;
18. re-read the committed diff;
19. confirm the working tree is clean;
20. reassess every acceptance criterion;
21. choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS;
22. if CONTINUE, immediately begin the next loop.

Each loop must produce:

1. one implementation/test/documentation commit;
2. one prompt archive commit.

==================================================
Required Repository Review
==========================

Read:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* current deployment documentation;
* current subsystem documentation;
* current production-readiness and final-audit documents.

Inspect:

* shared base templates;
* all shared navigation templates;
* `static/css/styles.css`;
* any app-specific CSS;
* all templates under:

  * `templates/`;
  * `home/templates/`;
  * `accounts/templates/`;
  * `players/templates/`;
  * `analytics/templates/`;
  * `seasons/templates/`;
  * `drafts/templates/`;
  * `pdp/templates/`;
  * `leaguehub/templates/`;
  * `scholarships/templates/`;
* form rendering patterns;
* pagination partials;
* table patterns;
* message/alert components;
* confirmation pages;
* import preview and result pages;
* current navigation and staff shells;
* current tests checking templates or rendered markup.

==================================================
Device Targets
==============

Optimize for at least these viewport widths:

```text
320px
360px
375px
390px
414px
768px
1024px
```

The interface should remain usable at:

* portrait phone;
* landscape phone;
* portrait tablet;
* landscape tablet;
* desktop.

Do not optimize for one device model only.

==================================================
Mobile-First Principles
=======================

Use mobile-first CSS where practical.

Prioritize:

* readable content before decorative layout;
* one-column layout on narrow screens;
* progressive enhancement for wider screens;
* touch-friendly controls;
* no horizontal page scrolling;
* clear hierarchy;
* safe spacing;
* reduced visual density;
* explicit labels;
* stable navigation;
* visible form errors.

Do not hide essential functions on mobile.

==================================================
Shared Layout Review
====================

Review all shared base layouts.

Ensure:

* viewport meta tag is present and correct;
* content does not overflow the viewport;
* fixed widths are removed or constrained;
* containers use responsive padding;
* long words, URLs, and email addresses wrap safely;
* images scale within their containers;
* headings wrap without clipping;
* cards stack cleanly;
* footer content remains readable;
* flash messages remain visible and dismissible if dismiss behavior exists;
* skip links and landmarks


==================================================
Implementation Commit Diff
==================================================

commit eff03793a076c36d065d6f457e0cb81a6a29a52b
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Fri Jul 17 00:16:26 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Fri Jul 17 00:16:26 2026 -0700

    Harden responsive UI styling
---
 static/css/leaguehub.css    |  33 ++++++++++
 static/css/pdp.css          | 104 ++++++++++++++++++++++++++++++++
 static/css/scholarships.css |  39 ++++++++++++
 static/css/styles.css       | 144 ++++++++++++++++++++++++++++++++++++++++++++
 4 files changed, 320 insertions(+)

diff --git a/static/css/leaguehub.css b/static/css/leaguehub.css
index f1ba078..21411e4 100644
--- a/static/css/leaguehub.css
+++ b/static/css/leaguehub.css
@@ -4,6 +4,7 @@
     gap: 1rem;
     grid-template-columns: minmax(0, 1fr) auto;
     margin-bottom: 1.5rem;
+    min-width: 0;
 }

 .leaguehub-toolbar__links,
@@ -43,6 +44,7 @@
     color: #09172f;
     font-family: "Source Sans 3", sans-serif;
     min-width: 220px;
+    min-height: 44px;
     padding: 0.7rem 2.75rem 0.7rem 0.95rem;
 }

@@ -120,6 +122,7 @@
     box-shadow: 0 28px 56px rgba(7, 20, 45, 0.2);
     color: #f7f2e8;
     padding: 1.75rem;
+    overflow-wrap: anywhere;
 }

 .leaguehub-scoreboard-hero {
@@ -243,6 +246,8 @@
     display: block;
     padding: 1.15rem 1.2rem;
     text-decoration: none;
+    min-width: 0;
+    overflow-wrap: anywhere;
 }

 .leaguehub-game-card--awaiting {
@@ -344,3 +349,31 @@
         justify-content: flex-start;
     }
 }
+
+@media (max-width: 640px) {
+    .leaguehub-toolbar__links,
+    .leaguehub-toolbar__selectors,
+    .leaguehub-season-card__actions {
+        align-items: stretch;
+        flex-direction: column;
+    }
+
+    .leaguehub-select,
+    .leaguehub-toolbar__selectors .button,
+    .leaguehub-season-card__actions .button {
+        width: 100%;
+    }
+
+    .leaguehub-scoreboard-hero,
+    .leaguehub-scoreboard {
+        padding: 1.15rem;
+        border-radius: 20px;
+    }
+
+    .leaguehub-scoreboard__row,
+    .leaguehub-game-card__team-row,
+    .leaguehub-game-card__teams {
+        align-items: flex-start;
+        flex-direction: column;
+    }
+}
diff --git a/static/css/pdp.css b/static/css/pdp.css
index 4e739d7..3077993 100644
--- a/static/css/pdp.css
+++ b/static/css/pdp.css
@@ -1,10 +1,12 @@
 .pdp-shell {
     padding: 0 1.5rem 4rem;
+    overflow-x: hidden;
 }

 .pdp-app {
     max-width: 1260px;
     margin: 0 auto;
+    min-width: 0;
 }

 .pdp-hero {
@@ -63,6 +65,8 @@
     color: #fff;
     font-weight: 700;
     text-decoration: none;
+    min-height: 44px;
+    overflow-wrap: anywhere;
 }

 .pdp-nav a:hover,
@@ -97,6 +101,8 @@
     padding: 1.5rem;
     box-shadow: 0 22px 60px rgba(16, 42, 67, 0.1);
     backdrop-filter: blur(8px);
+    min-width: 0;
+    overflow-wrap: anywhere;
 }

 .pdp-card--highlight {
@@ -140,6 +146,7 @@
     border-radius: 18px;
     background: rgba(240, 245, 255, 0.78);
     border: 1px solid rgba(16, 42, 67, 0.05);
+    min-width: 0;
 }

 .pdp-list__item--stack,
@@ -215,6 +222,7 @@
 .pdp-form select,
 .pdp-form textarea {
     width: 100%;
+    min-height: 44px;
     padding: 0.85rem 0.95rem;
     border-radius: 16px;
     border: 1px solid rgba(16, 42, 67, 0.16);
@@ -222,6 +230,24 @@
     background: #fff;
 }

+.pdp-form input[type="checkbox"],
+.pdp-form input[type="radio"] {
+    width: auto;
+    min-height: 0;
+}
+
+.pdp-actions {
+    display: flex;
+    flex-wrap: wrap;
+    gap: 0.75rem;
+    align-items: center;
+}
+
+.pdp-actions .button,
+.pdp-form .button {
+    min-height: 44px;
+}
+
 .pdp-form ul {
     list-style: none;
     padding: 0;
@@ -232,11 +258,15 @@

 .table-wrap {
     overflow-x: auto;
+    -webkit-overflow-scrolling: touch;
+    max-width: 100%;
+    border-radius: 18px;
 }

 .pdp-table {
     width: 100%;
     border-collapse: collapse;
+    min-width: 640px;
 }

 .pdp-table th,
@@ -245,6 +275,7 @@
     border-bottom: 1px solid rgba(16, 42, 67, 0.08);
     text-align: left;
     vertical-align: top;
+    overflow-wrap: anywhere;
 }

 .empty-state {
@@ -265,3 +296,76 @@
         justify-content: flex-start;
     }
 }
+
+@media (max-width: 640px) {
+    .pdp-shell {
+        padding: 0 0.75rem 2.5rem;
+    }
+
+    .pdp-hero {
+        gap: 1.25rem;
+        margin: 0.75rem 0 1rem;
+        padding: 1.25rem;
+        border-radius: 22px;
+    }
+
+    .pdp-hero h1 {
+        line-height: 1.08;
+    }
+
+    .pdp-subtitle {
+        font-size: 1rem;
+    }
+
+    .pdp-nav {
+        gap: 0.5rem;
+    }
+
+    .pdp-nav a {
+        flex: 1 1 calc(50% - 0.5rem);
+        justify-content: center;
+        text-align: center;
+    }
+
+    .pdp-card {
+        padding: 1rem;
+        border-radius: 18px;
+    }
+
+    .section-heading,
+    .toolbar-inline,
+    .pdp-list__item,
+    .pdp-actions {
+        align-items: stretch;
+        flex-direction: column;
+    }
+
+    .pdp-actions .button,
+    .pdp-form .button {
+        width: 100%;
+    }
+
+    .pdp-table {
+        min-width: 560px;
+    }
+
+    .pdp-table th,
+    .pdp-table td {
+        padding: 0.72rem 0.65rem;
+    }
+}
+
+@media (max-width: 380px) {
+    .pdp-shell {
+        padding-inline: 0.5rem;
+    }
+
+    .pdp-hero,
+    .pdp-card {
+        border-radius: 16px;
+    }
+
+    .pdp-nav a {
+        flex-basis: 100%;
+    }
+}
diff --git a/static/css/scholarships.css b/static/css/scholarships.css
index e3cc304..360bca3 100644
--- a/static/css/scholarships.css
+++ b/static/css/scholarships.css
@@ -9,6 +9,7 @@
     max-width: var(--max-width);
     margin: 0 auto;
     padding: 0 1.5rem 1rem;
+    min-width: 0;
 }

 .scholarship-message-stack {
@@ -109,6 +110,8 @@
     padding: 1.65rem 1.75rem;
     border-radius: 28px;
     background: rgba(255, 255, 255, 0.94);
+    min-width: 0;
+    overflow-wrap: anywhere;
 }

 .scholarship-panel--feature {
@@ -272,6 +275,7 @@
 .scholarship-filter-bar input,
 .scholarship-filter-bar select {
     width: 100%;
+    min-height: 44px;
     padding: 0.9rem 1rem;
     border-radius: 16px;
     border: 1px solid rgba(16, 42, 67, 0.14);
@@ -360,11 +364,15 @@

 .table-shell {
     overflow-x: auto;
+    -webkit-overflow-scrolling: touch;
+    max-width: 100%;
+    border-radius: 18px;
 }

 .scholarship-table {
     width: 100%;
     border-collapse: collapse;
+    min-width: 640px;
 }

 .scholarship-table th,
@@ -373,6 +381,7 @@
     border-bottom: 1px solid rgba(16, 42, 67, 0.08);
     text-align: left;
     vertical-align: top;
+    overflow-wrap: anywhere;
 }

 .scholarship-table th {
@@ -453,4 +462,34 @@
         align-items: start;
         flex-direction: column;
     }
+
+    .scholarship-actions,
+    .scholarship-actions--split {
+        align-items: stretch;
+        flex-direction: column;
+    }
+
+    .scholarship-actions .button,
+    .scholarship-form .button,
+    .scholarship-filter-bar .button {
+        width: 100%;
+    }
+
+    .scholarship-table {
+        min-width: 560px;
+    }
+}
+
+@media (max-width: 380px) {
+    .scholarship-app {
+        padding-inline: 0.75rem;
+    }
+
+    .scholarship-hero__content,
+    .scholarship-cycle-card,
+    .scholarship-panel,
+    .scholarship-dashboard-hero {
+        padding: 1rem;
+        border-radius: 18px;
+    }
 }
diff --git a/static/css/styles.css b/static/css/styles.css
index 1613872..d65902e 100644
--- a/static/css/styles.css
+++ b/static/css/styles.css
@@ -33,6 +33,7 @@ body {
     color: var(--color-text);
     line-height: 1.6;
     font-family: inherit;
+    overflow-x: hidden;
 }

 .skip-link {
@@ -55,6 +56,7 @@ body {
 a {
     color: inherit;
     text-decoration: none;
+    overflow-wrap: anywhere;
 }

 a:hover,
@@ -74,6 +76,8 @@ a:focus {
     text-transform: uppercase;
     letter-spacing: 0.05em;
     cursor: pointer;
+    min-height: 44px;
+    text-align: center;
     transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, color 0.2s ease;
     text-decoration: none;
 }
@@ -149,6 +153,7 @@ main {
     max-width: var(--max-width);
     margin: 0 auto;
     padding: 0 1.5rem;
+    min-width: 0;
 }

 .site-header {
@@ -160,6 +165,7 @@ main {
     max-width: var(--max-width);
     margin: 2rem auto 2.5rem;
     overflow: hidden;
+    width: calc(100% - 2rem);
 }

 .header-top {
@@ -399,6 +405,7 @@ main {
     border-radius: 28px;
     overflow: hidden;
     box-shadow: var(--shadow-lg);
+    width: calc(100% - 2rem);
 }

 .hero-media {
@@ -519,6 +526,7 @@ main {
     margin: 0;
     line-height: 1.15;
     text-shadow: 0 18px 40px rgba(16, 42, 67, 0.42);
+    overflow-wrap: anywhere;
 }

 .hero-eyebrow {
@@ -2513,3 +2521,139 @@ table.tryout-table td:last-child {
         grid-template-columns: 1fr;
     }
 }
+
+@media (max-width: 640px) {
+    :root {
+        --section-spacing: 2.5rem;
+        --radius-lg: 20px;
+    }
+
+    main {
+        padding-bottom: 2.5rem;
+    }
+
+    .container,
+    .programs-sections,
+    .info-sections,
+    .tryout-section,
+    .contact-callout {
+        padding-inline: 1rem;
+    }
+
+    .site-header,
+    .hero {
+        border-radius: 20px;
+        margin: 0.5rem 1rem 1.5rem;
+        width: auto;
+    }
+
+    .header-top {
+        align-items: flex-start;
+        flex-direction: column;
+        gap: 1rem;
+        padding: 1rem;
+    }
+
+    .logo img {
+        width: 88px;
+    }
+
+    .branding h2 {
+        font-size: 1.35rem;
+    }
+
+    .branding-highlights,
+    .social-links,
+    .hero-actions,
+    .schedule-cta,
+    .contact-actions,
+    .cta-banner-actions {
+        align-items: stretch;
+        flex-direction: column;
+    }
+
+    .hero-media {
+        min-height: 520px;
+    }
+
+    .hero-content {
+        justify-content: flex-start;
+        padding: 1.25rem;
+    }
+
+    .home-hero,
+    .programs-hero,
+    .registration-hero {
+        padding-top: 1.25rem;
+    }
+
+    .hero-message,
+    .hero-message--compact {
+        max-width: 100%;
+    }
+
+    .hero-highlights li {
+        border-radius: 14px;
+    }
+
+    .button,
+    .hero-actions .button,
+    .schedule-cta .button,
+    .contact-actions .button,
+    .cta-banner-actions .button {
+        width: 100%;
+    }
+
+    .about-grid,
+    .expectations .container,
+    .info-card,
+    .programs-card,
+    .division-card,
+    .contact-card {
+        padding: 1.35rem;
+        border-radius: 18px;
+    }
+
+    .expectations-grid,
+    .programs-grid,
+    .info-grid,
+    .tryout-grid,
+    .division-grid,
+    .schedule-grid {
+        grid-template-columns: minmax(0, 1fr);
+    }
+
+    .division-header {
+        align-items: flex-start;
+        flex-direction: column;
+    }
+
+    .tryout-table {
+        min-width: 620px;
+    }
+}
+
+@media (max-width: 380px) {
+    .container,
+    .programs-sections,
+    .info-sections,
+    .tryout-section,
+    .contact-callout {
+        padding-inline: 0.75rem;
+    }
+
+    .site-header,
+    .hero {
+        border-radius: 16px;
+        margin-inline: 0.5rem;
+    }
+
+    .hero-content {
+        padding: 1rem;
+    }
+
+    .hero-eyebrow {
+        border-radius: 12px;
+        letter-spacing: 0.12em;
+    }
+}
