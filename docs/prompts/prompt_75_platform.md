# Prompt 75 - Platform

App/subsystem: platform

Work commit: `e3a770989f759ccfef8e18c0a9b675d89d8236c6`

Terminal state: `PASS`

## User Prompt

```text
Implement Seasonal Participation V1 Phase 2 only: Season-Aware Player Import.

Use continuous loop engineering.

Continue until the Phase 2 scope is production-ready, fully reviewed, documented, tested, committed, pushed, and the working tree is clean.

Do not start Phase 3 or later work.

==================================================
Current State
=============

Seasonal Participation V1 Phase 1 is complete.

The repository now contains:

* `seasons.Season`
* `seasons.SeasonTeam`
* `seasons.PlayerRosterMembership`
* `seasons.CoachSeasonAssignment`
* transactional season/team/membership/assignment services
* current-season handling
* player compatibility helpers
* schema-only migration
* admin registration
* comprehensive tests

Phase 1 did not change player import, coach import, or evaluation workflows.

Verified production state before Phase 1 deployment planning:

```text
Players: 0
Coach profiles: 0
Observations: 0
```

No historical player roster data needs reconstruction.

==================================================
Phase 2 Objective
=================

Make the existing player CSV import season-aware.

Staff should continue importing normal player CSV files, but every import must be associated with a selected season.

For each valid row, the import must:

1. match or create the permanent `players.Player`;
2. resolve or create the row’s `SeasonTeam`;
3. create or update `PlayerRosterMembership`;
4. preserve previous-season memberships;
5. avoid recreating permanent players;
6. preserve current provenance and conflict-review behavior;
7. update compatibility `Player.team_name` and `Player.division` only through explicit seasonal membership services.

Do not implement coach seasonal import or evaluation seasonal context yet.

==================================================
Terminal States
===============

Every loop must end in exactly one state:

CONTINUE

Concrete Phase 2 implementation, review, documentation, or verification work remains.

PASS

All acceptance criteria are satisfied, verification passes, commits are pushed, and the working tree is clean.

BLOCKED

A necessary decision requires unresolved product direction, destructive migration, external infrastructure, or architecture expansion outside Phase 2.

NO_PROGRESS

Two consecutive complete loops fail to make meaningful progress toward an unsatisfied acceptance criterion.

Do not continue through speculative or cosmetic refactoring.

==================================================
Established Loop Workflow
=========================

Every loop must complete the full repository workflow.

Each loop must:

1. Reconcile the current committed state.
2. Read `AGENTS.md`, the seasonal plan, and prior prompt archives.
3. Confirm the working tree is clean.
4. Inspect the complete player import workflow.
5. Identify concrete incomplete criteria or verified defects.
6. Create the next prompt archive before implementation according to `AGENTS.md`.
7. Implement only selected Phase 2 work.
8. Add or update focused tests.
9. Run focused verification.
10. Perform senior-engineer self-review.
11. Fix every verified issue.
12. Update relevant documentation.
13. Run the complete verification suite.
14. Commit implementation, tests, migrations, and documentation.
15. Finalize the prompt archive with commit hash, review findings, verification results, and terminal state.
16. Commit the prompt archive separately.
17. Push both commits.
18. Re-read the committed diff.
19. Confirm the working tree is clean.
20. Reassess every acceptance criterion.
21. Choose CONTINUE, PASS, BLOCKED, or NO_PROGRESS.
22. If CONTINUE, begin the next loop without asking for confirmation.

Each loop must create:

1. one implementation/review/documentation commit;
2. one prompt archive commit.

==================================================
Required Repository Review
==========================

Before implementation, read:

* `AGENTS.md`
* `README.md`
* `docs/ARCHITECTURE.md`
* `docs/USER_MANUAL.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* relevant player import documentation
* prompt archives for player import, account provisioning, and Seasons Phase 1

Inspect:

* `players/models.py`
* `players/forms.py`
* `players/views.py`
* `players/urls.py`
* `players/services/import_service.py`
* player matching and merge services
* account-provisioning integration
* player import templates
* `players/tests.py`
* `seasons/models.py`
* `seasons/services/team_service.py`
* `seasons/services/membership_service.py`
* current player-import migrations and provenance models
* all current player-import routes and form/session state

==================================================
Season Selection
================

Every new player import batch must be associated with one selected `Season`.

Preferred UX:

* staff selects the season on the upload page;
* only active seasons should normally be selectable;
* current season should be the default when one exists;
* staff may explicitly select another active season;
* season selection must persist through:

  * upload;
  * column mapping;
  * preview;
  * conflict review;
  * confirmation;
  * result display.

Do not trust a client-submitted raw season identifier without server validation.

The selected season must be stored durably with the import batch if the current model supports extending `PlayerImportBatch`.

Recommended change:

* add nullable `season` FK to `PlayerImportBatch`;
* existing batches remain valid;
* all new confirmed season-aware imports require a season.

A migration is authorized.

Do not create a default season automatically.

==================================================
CSV Fields
==========

Continue supporting all current identity and player fields.

Season-aware roster fields should include:

* `team_name`
* `division`
* optional `jersey_number`
* optional `roster_status`
* optional `membership_start_date`
* optional `membership_end_date`
* optional `roster_source_id`

Use names consistent with current mapping conventions.

Minimum identity requirements remain unchanged:

* full name;
* or first name plus last name.

Season is selected at the import level and does not need to exist in every row.

If a CSV also contains a season column:

* either validate it matches the selected season;
* or ignore it with clear preview messaging;
* do not silently create mixed-season imports.

Recommended V1 rule:

> One import batch belongs to exactly one selected season.

==================================================
Team And Division Requirements
==============================

A roster membership requires:

* team;
* division;
* selected season.

Rows missing team or division should not create a seasonal membership.

Decide and implement one clear behavior:

Preferred behavior:

* permanent player data may still be previewed;
* confirmation blocks the row as invalid for season-aware import;
* report the missing roster context clearly;
* do not create a player without its required membership during a normal season-aware roster import.

Do not create blank or placeholder `SeasonTeam` records.

Normalize team and division using the existing `seasons` team services.

==================================================
Import Batch And Provenance
===========================

Extend current import provenance without replacing it.

The import batch should record:

* selected season;
* original filename;
* source type;
* uploader;
* import status;
* counts;
* timestamps;
* existing metadata.

Each created membership should retain:

* import batch;
* source;
* source identifier where available;
* relevant row metadata.

Permanent player source identifiers and source rows must continue working as before.

Do not duplicate raw CSV rows inside membership metadata when existing provenance already stores them.

==================================================
Permanent Player Matching
=========================

Keep existing player matching rules.

Season/team data is context, not permanent identity.

Do not treat a different team or division as proof that a person is a different player.

Matching priority should continue to rely on:

* source identifiers;
* registration/registrant identifiers;
* name;
* birthdate/birth year;
* existing player matching safeguards.

Team and division may assist conflict review but must not override strong permanent identity matches.

==================================================
SeasonTeam Resolution
=====================

For every valid row:

* use the selected season;
* normalize team and division;
* find or create `SeasonTeam` through `seasons` services;
* reuse the same `SeasonTeam` across rows with equivalent normalized values;
* preserve human-friendly display values;
* preserve optional external team identifiers when safely available.

Preview must distinguish:

* existing season team;
* new season team;
* ambiguous external identifier conflict;
* invalid missing team/division.

Do not create teams directly in views or templates.

==================================================
Membership Behavior
===================

For every matched or created permanent player, resolve the appropriate membership action.

## Same Player, Same Season, Same Team

Reuse or update the existing membership.

Do not create duplicates.

Update only roster-specific fields that were supplied.

Preserve prior provenance appropriately.

## Same Player, Different Season

Create a new membership for the selected season.

Preserve all prior-season memberships.

## Same Player, Same Season, Different Team

Do not automatically overwrite the old membership.

Classify the row as one of:

* concurrent membership;
* transfer/new stint;
* conflict requiring review.

Because the CSV does not yet have a fully established transfer workflow, use a conservative V1 rule.

Recommended behavior:

* if no active primary membership exists, create the new membership as primary;
* if an active primary membership exists on another team, flag the row for review;
* staff must explicitly confirm whether the new row is:

  * a transfer;
  * an additional non-primary membership;
  * a correction.

Do not guess.

If the existing import conflict UI cannot safely support this choice within Phase 2, block the ambiguous row and document manual resolution through admin or a later workflow.

## Primary Membership

For normal roster imports:

* first valid active membership for player/season becomes primary;
* same-team reimport preserves primary state;
* additional same-season membership must not silently demote or replace the existing primary membership;
* compatibility fields synchronize only from the active primary membership.

==================================================
Roster Status
=============

Support current controlled statuses:

* Active
* Inactive
* Transferred
* Guest
* Removed

CSV values must map through a strict normalization function.

Blank status should default to Active.

Unknown values must produce a row validation error.

Do not allow arbitrary status text.

An inactive membership must not be primary.

==================================================
Dates And Jersey Number
=======================

Optional membership fields:

* jersey number;
* starts_on;
* ends_on.

Validation:

* end date cannot precede start date;
* invalid dates produce row errors;
* jersey number remains text;
* blank values should not erase existing values during reimport unless an explicit clear behavior already exists.

Document the update semantics.

==================================================
Account Provisioning
====================

Preserve current optional player-account provisioning.

Player import may still:

* create or reuse a player account;
* create a self `UserPlayerLink`;
* require initial password change;
* display temporary passwords according to current security rules.

Season-aware roster creation must not change account identity behavior.

Do not create one account per season.

The same player account must be reused across future seasonal imports.

Account provisioning failures should continue to use current partial-failure behavior.

==================================================
Preview UX
==========

Update the preview to clearly show:

* selected season;
* matched/new player;
* team;
* division;
* season-team action;
* membership action;
* account-provisioning action;
* conflicts;
* errors.

Use friendly membership action labels such as:

* Create Membership
* Update Membership
* Reuse Membership
* New Season Membership
* Review Team Change
* Invalid Roster Context

Do not expose internal IDs unnecessarily.

The selected season must be visible on every import step.

==================================================
Confirmation
============

Confirmation must use server-side session/batch state established during preview.

Do not trust hidden form fields for:

* season;
* team action;
* membership action;
* player match;
* primary status.

Revalidate before writing.

Use transactions consistent with current import behavior.

Ensure:

* permanent player;
* SeasonTeam;
* PlayerRosterMembership;
* source row;
* source identifiers;
* optional account provisioning

remain internally consistent if one step fails.

Document whether transaction scope is per batch or per row.

Preserve existing partial-failure behavior only if errors are clearly reported.

==================================================
Result Page
===========

Report separate counts for:

* players created;
* players reused;
* season teams created;
* season teams reused;
* memberships created;
* memberships updated/reused;
* rows requiring review;
* account users created;
* account users reused;
* conflicts;
* errors.

If temporary passwords are displayed, preserve current one-time-display rules.

Do not expose temporary passwords on later page loads.

==================================================
Compatibility Fields
====================

`Player.team_name` and `Player.division` remain temporary compatibility fields.

After creating or updating an active primary membership:

* call the explicit compatibility synchronization service;
* update fields from the membership’s `SeasonTeam`;
* do not write these fields directly in import code.

If a row creates only a non-primary membership:

* do not change compatibility fields.

Document that these fields reflect current primary roster display only and are not historical.

==================================================
Import List And Detail
======================

Where current import pages show batch information, add the selected season.

Historical import batches with no season should display:

* Legacy / No Season

Do not fabricate a Season record for them.

==================================================
Permissions
===========

Keep current player-import authorization unchanged.

Only existing authorized staff users may access player import.

Do not grant access based on seasonal assignment.

Do not introduce team-scoped permissions.

==================================================
Migration
=========

A migration may:

* add nullable `season` FK to `PlayerImportBatch`;
* add any narrowly required roster import fields to existing provenance models.

Do not:

* backfill production players;
* create a default season;
* create memberships from existing player fields;
* modify Analytics observations;
* modify coach imports.

Migration must be additive and SQLite-safe.

==================================================
Phase 2 Non-Goals
=================

Do not implement:

* season-aware coach import;
* changes to existing coach password behavior;
* coach assignment creation from CSV;
* `EvaluationCycle.season`;
* observation season/team/membership fields;
* evaluation-context snapshots;
* team-based coach permissions;
* player peer-evaluation team scope;
* roster-management dashboards;
* manual transfer UI outside existing conflict review;
* player season-history pages;
* coach season pages;
* Platform V2 player summaries;
* APIs;
* JavaScript frameworks;
* notifications;
* exports;
* removal of `Player.team_name`;
* removal of `Player.division`;
* permanent Team model.

==================================================
Documentation
=============

Update:

* `docs/USER_MANUAL.md`
* `docs/ARCHITECTURE.md`
* `docs/seasons/README.md`
* `docs/seasons/implementation/engineering/seasonal_participation_v1.md`
* relevant player import documentation

Document:

* season selection requirement;
* supported roster columns;
* permanent player reuse;
* new-season behavior;
* same-season same-team reimport behavior;
* ambiguous team-change behavior;
* compatibility-field behavior;
* optional account provisioning;
* current limitations;
* Phase 2 completion;
* next phase: season-aware coach import.

Do not describe coach import or evaluation context as season-aware yet.

==================================================
Required Test Coverage
======================

## Season Selection

* current season defaults on upload form;
* staff can select another active season;
* inactive season rejected;
* missing season rejected;
* selected season persists through preview/confirm;
* manipulated season ID rejected;
* legacy batches without season still display safely.

## Team Resolution

* team created in selected season;
* equivalent normalized team reused;
* same team name in different season creates distinct team;
* missing team rejected;
* missing division rejected;
* external identifier reuse works safely;
* ambiguous external identifier conflicts.

## Permanent Player Reuse

* new player created once;
* same player reimported in same season is reused;
* same player imported in future season is reused;
* team change does not create another Player;
* existing matching/conflict rules remain intact.

## Membership Creation

* first season membership created;
* first active membership becomes primary;
* compatibility fields synchronized;
* future season creates new membership;
* prior membership preserved;
* same season/team reimport reuses or updates membership;
* duplicate membership not created;
* non-primary membership does not change compatibility fields.

## Ambiguous Team Change

* same player/same season/different team is detected;
* existing primary membership is preserved;
* row is blocked or marked for review according to chosen contract;
* no silent transfer;
* no silent duplicate primary membership.

## Roster Fields

* valid status mapping;
* blank status defaults active;
* invalid status rejected;
* valid dates accepted;
* invalid date range rejected;
* jersey number saved;
* blank optional fields preserve existing values according to contract.

## Account Provisioning Regressions

* player account creation still works;
* existing account reuse still works;
* self-link creation still works;
* password rules unchanged;
* one-time password display unchanged;
* future season import does not create duplicate account.

## Security

* non-staff denied;
* confirm cannot be replayed unsafely;
* season cannot be changed through hidden-field manipulation;
* player match cannot be changed through request manipulation;
* primary membership cannot be forged by client input;
* temporary passwords are not redisplayed.

## Result Reporting

* created/reused player counts;
* team counts;
* membership counts;
* conflict/error counts;
* season displayed correctly.

## Regression

* current player search and profiles still work;
* account operations unchanged;
* coach import unchanged;
* evaluations unchanged;
* draft and PDP tests remain passing.

==================================================
Focused Verification Per Loop
=============================

Run at minimum:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
git diff --check
```

==================================================
Full Verification Every Loop
============================

Every loop must run:

```bash
DJANGO_SECRET_KEY=test-only-not-production python manage.py check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations seasons --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations players --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations accounts --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py makemigrations analytics --check
DJANGO_SECRET_KEY=test-only-not-production python manage.py migrate --plan
DJANGO_SECRET_KEY=test-only-not-production python manage.py test seasons
DJANGO_SECRET_KEY=test-only-not-production python manage.py test players
DJANGO_SECRET_KEY=test-only-not-production python manage.py test accounts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test analytics
DJANGO_SECRET_KEY=test-only-not-production python manage.py test drafts
DJANGO_SECRET_KEY=test-only-not-production python manage.py test pdp
DJANGO_SECRET_KEY=test-only-not-production python manage.py test
git diff --check
```

All commands must pass before an implementation commit.

==================================================
Self-Review Every Loop
======================

Review each diff as a senior Django engineer.

Check:

* permanent identity versus seasonal context;
* model ownership;
* import transaction boundaries;
* session-state security;
* hidden-field manipulation;
* duplicate membership creation;
* primary-membership invariants;
* normalized team reuse;
* accidental player recreation;
* source/provenance integrity;
* partial-failure behavior;
* account-provisioning regressions;
* temporary password exposure;
* compatibility-field side effects;
* SQLite migration safety;
* stale docs;
* N+1 queries in preview/result pages;
* accidental Phase 3+ work.

Fix every verified issue before committing.

==================================================
Phase 2 Acceptance Criteria
===========================

Do not declare PASS until all criteria are satisfied.

A. Season Selection

* every new player import requires a valid active season;
* selected season persists securely through the workflow;
* current season defaults appropriately;
* legacy batches remain readable.

B. Permanent Identity

* permanent Player is reused across seasons;
* team/division changes do not create duplicate players;
* existing matching protections remain.

C. Season Teams

* teams are created/reused within selected season;
* normalization is deterministic;
* same team across seasons remains distinct;
* missing context is rejected.

D. Memberships

* membership created for valid imported row;
* future season creates new membership;
* same season/team reimport is deterministic;
* prior memberships remain historical;
* primary membership rules remain valid;
* ambiguous same-season team changes do not silently overwrite history.

E. Compatibility

* current primary membership updates compatibility fields through seasons services;
* non-primary membership does not overwrite them;
* import code does not directly write historical team semantics.

F. Provisioning

* optional account provisioning still works;
* accounts are permanent and reused;
* no duplicate seasonal accounts;
* password privacy remains intact.

G. Migration

* additive migration only;
* no default/legacy season;
* no roster backfill;
* SQLite plan reviewed.

H. UX

* selected season is visible throughout;
* preview shows membership actions clearly;
* results report teams and memberships;
* errors are understandable.

I. Tests

* focused and full suites pass;
* security manipulation cases covered;
* regressions covered.

J. Documentation

* user manual accurately explains season-aware player import;
* Phase 2 marked complete only after PASS;
* coach import and evaluations remain documented as not season-aware;
* next phase identified as Phase 3.

K. Git

* implementation commit exists;
* prompt archive commit exists;
* both pushed;
* working tree clean.

==================================================
Recommended Loop 1 Objective
============================

Loop 1 should normally:

1. add season to player import batch and forms;
2. preserve selected season through workflow state;
3. update preview/read models;
4. resolve SeasonTeam;
5. create/update PlayerRosterMembership;
6. synchronize compatibility fields;
7. preserve account provisioning;
8. add comprehensive tests;
9. update documentation;
10. run full verification;
11. commit, archive, push, and reassess.

If material issues remain, continue into further loops.

==================================================
No-Progress Rule
================

A loop counts as progress only if it:

* satisfies an unsatisfied acceptance criterion;
* fixes a verified data-integrity or authorization defect;
* prevents duplicate permanent players or memberships;
* strengthens transaction/provenance safety;
* adds missing regression proof;
* corrects material documentation drift.

Formatting-only work does not count.

If two consecutive loops make no meaningful progress and PASS cannot be reached, stop with NO_PROGRESS.

==================================================
Final PASS Review
=================

Before PASS, review from the perspectives of:

* registrar importing a new roster;
* registrar reimporting a corrected roster;
* player returning in a new season;
* player changing teams in the same season;
* administrator reviewing import provenance;
* security reviewer testing request manipulation;
* release engineer reviewing migrations.

Confirm:

* Phase 2 is usable for real player roster import;
* no duplicate permanent people are created;
* historical memberships are preserved;
* coach import remains unchanged;
* evaluation context remains unchanged;
* no Phase 3+ work was introduced.

==================================================
Git Workflow
============

For every loop:

1. create the next prompt archive before implementation;
2. commit implementation, migration, tests, and documentation;
3. update the prompt archive with:

   * implementation commit hash;
   * files changed;
   * migration summary;
   * issues found;
   * fixes applied;
   * verification results;
   * remaining criteria;
   * terminal state;
4. commit the prompt archive separately;
5. push both commits;
6. confirm the working tree is clean.

Suggested implementation commit message:

```text
Implement season-aware player import
```

==================================================
Final Report
============

Report:

* terminal state;
* loops completed;
* objective of each loop;
* files created;
* files modified;
* migration changes;
* season-selection behavior;
* player matching behavior;
* team resolution behavior;
* membership behavior;
* primary-membership behavior;
* ambiguous team-change behavior;
* compatibility-field behavior;
* account-provisioning behavior;
* preview/result UX;
* security protections;
* tests added;
* focused verification;
* full verification;
* documentation updates;
* deferred Phase 3+ work;
* commits;
* push results;
* confirmation that the working tree is clean.
```

## Implementation Notes

Implemented Seasonal Participation V1 Phase 2: Season-Aware Player Import.

- Added nullable `players.PlayerImportBatch.season` with an index for season/date import lookup.
- Required staff uploads to select an active season through the Analytics import UI.
- Preserved existing permanent player matching and provenance behavior while moving team/division handling into seasonal roster context.
- Added roster field mapping for status, jersey number, membership dates, and roster source identifiers.
- Created or reused `seasons.SeasonTeam` through season services.
- Created or updated `seasons.PlayerRosterMembership` through membership services.
- Blocked same-season active-primary team changes for manual review instead of silently transferring players.
- Preserved prior-season memberships when importing the same player into a future season.
- Kept optional player account provisioning behavior intact.
- Updated staff import preview, conflict review, list, and result displays with season/roster/membership context.
- Updated user and architecture documentation to show Seasonal Participation V1 Phase 2 complete and Phase 3 as the next seasonal phase.

## Verification

- `DJANGO_SECRET_KEY=test python manage.py check` - passed.
- `DJANGO_SECRET_KEY=test python manage.py makemigrations seasons --check` - passed.
- `DJANGO_SECRET_KEY=test python manage.py makemigrations players --check` - passed.
- `DJANGO_SECRET_KEY=test python manage.py makemigrations accounts --check` - passed.
- `DJANGO_SECRET_KEY=test python manage.py makemigrations analytics --check` - passed.
- `DJANGO_SECRET_KEY=test python manage.py migrate --plan` - completed; local plan includes existing unapplied migrations plus `players.0003_playerimportbatch_season_and_more`.
- `DJANGO_SECRET_KEY=test python manage.py test seasons` - passed, 32 tests.
- `DJANGO_SECRET_KEY=test python manage.py test players` - passed, 47 tests.
- `DJANGO_SECRET_KEY=test python manage.py test analytics` - passed, 127 tests.
- `DJANGO_SECRET_KEY=test python manage.py test accounts` - passed, 184 tests.
- `DJANGO_SECRET_KEY=test python manage.py test drafts` - passed, 8 tests.
- `DJANGO_SECRET_KEY=test python manage.py test pdp` - passed, 6 tests.
- `DJANGO_SECRET_KEY=test python manage.py test` - passed, 431 tests.
- `git diff --check` - passed.

## Implementation Commit Diff

```diff
commit e3a770989f759ccfef8e18c0a9b675d89d8236c6
Author:     Eugene Lin <eugenelin89@gmail.com>
AuthorDate: Wed Jul 15 22:11:54 2026 -0700
Commit:     Eugene Lin <eugenelin89@gmail.com>
CommitDate: Wed Jul 15 22:11:54 2026 -0700

    Implement season-aware player import

diff --git a/analytics/forms.py b/analytics/forms.py
index 7db49df..ea7f7e0 100644
--- a/analytics/forms.py
+++ b/analytics/forms.py
@@ -1,13 +1,23 @@
 from django import forms
 
 from players.services.import_service import SOURCE_CHOICES, build_column_choices
+from seasons.models import Season
+from seasons.services.season_service import get_current_season
 
 
 class PlayerImportUploadForm(forms.Form):
+    season = forms.ModelChoiceField(queryset=Season.objects.none(), help_text="Choose the season for this roster import.")
     csv_file = forms.FileField(help_text="Upload a player member-list or roster-detail CSV.")
     source = forms.ChoiceField(choices=SOURCE_CHOICES)
     provision_player_accounts = forms.BooleanField(required=False, initial=False)
 
+    def __init__(self, *args, **kwargs):
+        super().__init__(*args, **kwargs)
+        self.fields["season"].queryset = Season.objects.filter(is_active=True).order_by("-is_current", "-starts_on", "name")
+        current = get_current_season()
+        if current and current.is_active:
+            self.fields["season"].initial = current
+
     def clean_csv_file(self):
         csv_file = self.cleaned_data["csv_file"]
         if not csv_file.name.lower().endswith(".csv"):
@@ -35,6 +45,11 @@ class PlayerImportMappingForm(forms.Form):
     team_id = forms.ChoiceField(required=False)
     source_player_id = forms.ChoiceField(required=False)
     account_email = forms.ChoiceField(required=False)
+    roster_status = forms.ChoiceField(required=False)
+    jersey_number = forms.ChoiceField(required=False)
+    membership_start_date = forms.ChoiceField(required=False)
+    membership_end_date = forms.ChoiceField(required=False)
+    roster_source_id = forms.ChoiceField(required=False)
 
     def __init__(self, *args, parsed=None, **kwargs):
         super().__init__(*args, **kwargs)
diff --git a/analytics/templates/analytics/import_conflicts.html b/analytics/templates/analytics/import_conflicts.html
index 49f1998..832f3fb 100644
--- a/analytics/templates/analytics/import_conflicts.html
+++ b/analytics/templates/analytics/import_conflicts.html
@@ -11,6 +11,8 @@
         {% for row in review_rows %}
             <section class="pdp-list__item pdp-list__item--stack">
                 <h3>Row {{ row.row_number }} · {{ row.identity.first_name }} {{ row.identity.last_name }}</h3>
+                <p>Roster: {{ row.roster.division }} {{ row.roster.team_name }} · {{ row.membership.label }}</p>
+                {% if row.membership.existing_primary %}<p>Existing primary membership: {{ row.membership.existing_primary }}</p>{% endif %}
                 {% if row.candidate_names %}<p>Ambiguous candidates: {{ row.candidate_names|join:", " }}</p>{% endif %}
                 {% if row.errors %}<p>{{ row.errors|join:", " }}</p>{% endif %}
                 <label>
diff --git a/analytics/templates/analytics/import_detail.html b/analytics/templates/analytics/import_detail.html
index c51d2cd..18973c0 100644
--- a/analytics/templates/analytics/import_detail.html
+++ b/analytics/templates/analytics/import_detail.html
@@ -6,13 +6,16 @@
 {% block analytics_content %}
 <article class="pdp-card">
     <h2>{{ import_batch.original_filename }}</h2>
-    <p>{{ import_batch.source }} · {{ import_batch.get_status_display }}</p>
+    <p>{{ import_batch.source }} · {{ import_batch.get_status_display }} · Season: {% if import_batch.season %}{{ import_batch.season }}{% else %}Legacy / No Season{% endif %}</p>
     <div class="pdp-stat-grid">
         <div><strong>{{ import_batch.rows_processed }}</strong><span>Processed</span></div>
         <div><strong>{{ import_batch.rows_created }}</strong><span>Created</span></div>
         <div><strong>{{ import_batch.rows_updated }}</strong><span>Updated</span></div>
         <div><strong>{{ import_batch.rows_skipped }}</strong><span>Skipped</span></div>
         <div><strong>{{ import_batch.rows_conflicted }}</strong><span>Conflicts</span></div>
+        <div><strong>{{ import_batch.import_summary.season_teams_created|default:0 }}</strong><span>Teams Created</span></div>
+        <div><strong>{{ import_batch.import_summary.memberships_created|default:0 }}</strong><span>Memberships Created</span></div>
+        <div><strong>{{ import_batch.import_summary.memberships_updated|default:0 }}</strong><span>Memberships Updated</span></div>
     </div>
     {% if import_batch.row_errors %}
         <h3>Issues</h3>
diff --git a/analytics/templates/analytics/import_list.html b/analytics/templates/analytics/import_list.html
index 115ba8c..79562de 100644
--- a/analytics/templates/analytics/import_list.html
+++ b/analytics/templates/analytics/import_list.html
@@ -14,6 +14,7 @@
             <thead>
                 <tr>
                     <th>File</th>
+                    <th>Season</th>
                     <th>Source</th>
                     <th>Status</th>
                     <th>Rows</th>
@@ -25,6 +26,7 @@
                 {% for batch in import_batches %}
                     <tr>
                         <td><a href="{% url 'analytics:import-detail' pk=batch.pk %}">{{ batch.original_filename }}</a></td>
+                        <td>{% if batch.season %}{{ batch.season }}{% else %}Legacy / No Season{% endif %}</td>
                         <td>{{ batch.source }}</td>
                         <td>{{ batch.get_status_display }}</td>
                         <td>{{ batch.rows_processed }}</td>
@@ -32,7 +34,7 @@
                         <td>{{ batch.rows_updated }}</td>
                     </tr>
                 {% empty %}
-                    <tr><td colspan="6">No imports yet.</td></tr>
+                    <tr><td colspan="7">No imports yet.</td></tr>
                 {% endfor %}
             </tbody>
         </table>
diff --git a/analytics/templates/analytics/import_preview.html b/analytics/templates/analytics/import_preview.html
index 17af1aa..84c7ce5 100644
--- a/analytics/templates/analytics/import_preview.html
+++ b/analytics/templates/analytics/import_preview.html
@@ -15,7 +15,7 @@
 
 <article class="pdp-card">
     <h2>{{ import_batch.original_filename }}</h2>
-    <p>{{ import_batch.source }} · {{ import_batch.get_status_display }}</p>
+    <p>{{ import_batch.source }} · {{ import_batch.get_status_display }} · Season: {% if import_batch.season %}{{ import_batch.season }}{% else %}Legacy / No Season{% endif %}</p>
     {% if preview.account_provisioning.enabled %}
         <p>
             Account provisioning enabled; new accounts will be activated immediately and must change password on first login.
@@ -29,6 +29,10 @@
             <div><strong>{{ preview.summary.rows_update }}</strong><span>Update</span></div>
             <div><strong>{{ preview.summary.rows_needs_review }}</strong><span>Review</span></div>
             <div><strong>{{ preview.summary.rows_error }}</strong><span>Errors</span></div>
+            <div><strong>{{ preview.summary.season_teams_create }}</strong><span>Teams Create</span></div>
+            <div><strong>{{ preview.summary.season_teams_reuse }}</strong><span>Teams Reuse</span></div>
+            <div><strong>{{ preview.summary.memberships_create }}</strong><span>Memberships Create</span></div>
+            <div><strong>{{ preview.summary.memberships_update }}</strong><span>Memberships Update</span></div>
         </div>
     {% endif %}
     <div class="table-wrap">
@@ -37,7 +41,9 @@
                 <tr>
                     <th>Row</th>
                     <th>Player</th>
+                    <th>Roster</th>
                     <th>Action</th>
+                    <th>Membership</th>
                     <th>Match</th>
                     <th>Issues</th>
                 </tr>
@@ -47,7 +53,9 @@
                     <tr>
                         <td>{{ row.row_number }}</td>
                         <td>{{ row.identity.first_name }} {{ row.identity.last_name }}</td>
+                        <td>{{ row.roster.division }} {{ row.roster.team_name }}</td>
                         <td>{{ row.action }}</td>
+                        <td>{{ row.membership.label }}</td>
                         <td>{% if row.matched_player_name %}{{ row.matched_player_name }}{% else %}{{ row.match_status }}{% endif %}</td>
                         <td>
                             {% if row.errors %}{{ row.errors|join:", " }}{% endif %}
diff --git a/analytics/tests.py b/analytics/tests.py
index 6a43ddb..8ff8c20 100644
--- a/analytics/tests.py
+++ b/analytics/tests.py
@@ -98,6 +98,7 @@ from drafts.models import Draft, DraftAction, DraftActionType, DraftPlayer, Draf
 from players.models import Player, PlayerImportBatch, PlayerImportStatus, PlayerSourceRow, PlayerTag
 from players.services.import_service import SOURCE_MEMBER_LIST
 from players.services.tag_service import assign_tag
+from seasons.services.season_service import create_season
 
 
 User = get_user_model()
@@ -107,11 +108,12 @@ class AnalyticsImportViewTests(TestCase):
     def setUp(self):
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
         self.user = User.objects.create_user(username="user", password="testpass")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
 
     def upload(self):
         return SimpleUploadedFile(
             "member list for 13u house.csv",
-            b"First,Last,Gender,Team\nEugene,Lin,M,Expos\n",
+            b"First,Last,Gender,Division,Team\nEugene,Lin,M,13U,Expos\n",
             content_type="text/csv",
         )
 
@@ -136,7 +138,7 @@ class AnalyticsImportViewTests(TestCase):
 
         response = self.client.post(
             reverse("analytics:import-new"),
-            {"source": SOURCE_MEMBER_LIST, "csv_file": self.upload()},
+            {"season": str(self.season.pk), "source": SOURCE_MEMBER_LIST, "csv_file": self.upload()},
         )
 
         self.assertEqual(response.status_code, 302)
@@ -150,9 +152,10 @@ class AnalyticsImportViewTests(TestCase):
             reverse("analytics:import-new"),
             {
                 "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
                 "csv_file": SimpleUploadedFile(
                     "member.csv",
-                    b"First,Last,DOB,Email\nEugene,Lin,2012-05-01,eugene@example.com\n",
+                    b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n",
                     content_type="text/csv",
                 ),
                 "provision_player_accounts": "on",
@@ -170,17 +173,18 @@ class AnalyticsImportViewTests(TestCase):
             source=SOURCE_MEMBER_LIST,
             original_filename="member.csv",
             uploaded_by=self.staff,
+            season=self.season,
             mapping_config={"_provision_player_accounts": True, "_activate_player_accounts": False},
             preview_snapshot={
                 "parsed_csv": {
                     "file_name": "member.csv",
-                    "headers": ["First", "Last", "DOB", "Email"],
-                    "normalized_headers": {"first": "First", "last": "Last", "dob": "DOB", "email": "Email"},
+                    "headers": ["First", "Last", "DOB", "Email", "Division", "Team"],
+                    "normalized_headers": {"first": "First", "last": "Last", "dob": "DOB", "email": "Email", "division": "Division", "team": "Team"},
                     "rows": [
                         {
                             "row_number": 2,
-                            "original_row": {"First": "Eugene", "Last": "Lin", "DOB": "2012-05-01", "Email": "eugene@example.com"},
-                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "DOB": "2012-05-01", "Email": "eugene@example.com"},
+                            "original_row": {"First": "Eugene", "Last": "Lin", "DOB": "2012-05-01", "Email": "eugene@example.com", "Division": "13U", "Team": "Expos"},
+                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "DOB": "2012-05-01", "Email": "eugene@example.com", "Division": "13U", "Team": "Expos"},
                         }
                     ],
                 }
@@ -189,7 +193,7 @@ class AnalyticsImportViewTests(TestCase):
 
         response = self.client.post(
             reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
-            {"first_name": "First", "last_name": "Last", "birthdate": "DOB", "account_email": "Email"},
+            {"first_name": "First", "last_name": "Last", "birthdate": "DOB", "account_email": "Email", "division": "Division", "team_name": "Team"},
         )
 
         batch.refresh_from_db()
@@ -205,16 +209,17 @@ class AnalyticsImportViewTests(TestCase):
             source=SOURCE_MEMBER_LIST,
             original_filename="member.csv",
             uploaded_by=self.staff,
+            season=self.season,
             preview_snapshot={
                 "parsed_csv": {
                     "file_name": "member.csv",
-                    "headers": ["First", "Last", "Team"],
-                    "normalized_headers": {"first": "First", "last": "Last", "team": "Team"},
+                    "headers": ["First", "Last", "Division", "Team"],
+                    "normalized_headers": {"first": "First", "last": "Last", "division": "Division", "team": "Team"},
                     "rows": [
                         {
                             "row_number": 2,
-                            "original_row": {"First": "Eugene", "Last": "Lin", "Team": "Expos"},
-                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "Team": "Expos"},
+                            "original_row": {"First": "Eugene", "Last": "Lin", "Division": "13U", "Team": "Expos"},
+                            "cleaned_row": {"First": "Eugene", "Last": "Lin", "Division": "13U", "Team": "Expos"},
                         }
                     ],
                 }
@@ -223,7 +228,7 @@ class AnalyticsImportViewTests(TestCase):
 
         preview_response = self.client.post(
             reverse("analytics:import-preview", kwargs={"pk": batch.pk}),
-            {"first_name": "First", "last_name": "Last", "team_name": "Team"},
+            {"first_name": "First", "last_name": "Last", "division": "Division", "team_name": "Team"},
         )
         self.assertEqual(preview_response.status_code, 302)
 
@@ -239,9 +244,10 @@ class AnalyticsImportViewTests(TestCase):
             reverse("analytics:import-new"),
             {
                 "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
                 "csv_file": SimpleUploadedFile(
                     "member.csv",
-                    b"First,Last,DOB\nEugene,Lin,2012-05-01\n",
+                    b"First,Last,DOB,Division,Team\nEugene,Lin,2012-05-01,13U,Expos\n",
                     content_type="text/csv",
                 ),
                 "provision_player_accounts": "on",
@@ -258,14 +264,15 @@ class AnalyticsImportViewTests(TestCase):
 
     def test_conflict_page_displays_review_rows(self):
         self.client.force_login(self.staff)
-        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", team_name="Old")
+        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
         upload_response = self.client.post(
             reverse("analytics:import-new"),
             {
                 "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
                 "csv_file": SimpleUploadedFile(
                     "member.csv",
-                    b"First,Last,DOB,Team\nEugene,Lin,2012-05-01,New\n",
+                    b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n",
                     content_type="text/csv",
                 ),
             },
@@ -276,18 +283,19 @@ class AnalyticsImportViewTests(TestCase):
 
         self.assertEqual(upload_response.status_code, 302)
         self.assertContains(response, "Row 2")
-        self.assertContains(response, "team_name")
+        self.assertContains(response, "preferred_name")
 
     def test_preview_routes_review_rows_through_conflict_review(self):
         self.client.force_login(self.staff)
-        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", team_name="Old")
+        Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
         self.client.post(
             reverse("analytics:import-new"),
             {
                 "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
                 "csv_file": SimpleUploadedFile(
                     "member.csv",
-                    b"First,Last,DOB,Team\nEugene,Lin,2012-05-01,New\n",
+                    b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n",
                     content_type="text/csv",
                 ),
             },
@@ -307,6 +315,7 @@ class AnalyticsImportViewTests(TestCase):
             reverse("analytics:import-new"),
             {
                 "source": SOURCE_MEMBER_LIST,
+                "season": str(self.season.pk),
                 "csv_file": SimpleUploadedFile(
                     "member.csv",
                     b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n",
diff --git a/analytics/views.py b/analytics/views.py
index 11ae636..e0c123b 100644
--- a/analytics/views.py
+++ b/analytics/views.py
@@ -100,6 +100,9 @@ class PlayerImportListView(AnalyticsStaffRequiredMixin, ListView):
     context_object_name = "import_batches"
     paginate_by = 25
 
+    def get_queryset(self):
+        return PlayerImportBatch.objects.select_related("season", "uploaded_by")
+
 
 class PlayerImportUploadView(AnalyticsStaffRequiredMixin, FormView):
     template_name = "analytics/import_upload.html"
@@ -110,6 +113,7 @@ class PlayerImportUploadView(AnalyticsStaffRequiredMixin, FormView):
             file_obj=form.cleaned_data["csv_file"],
             source=form.cleaned_data["source"],
             uploaded_by=self.request.user,
+            season=form.cleaned_data["season"],
             provision_player_accounts=form.cleaned_data.get("provision_player_accounts", False),
         )
         messages.success(self.request, "CSV uploaded. Review the import preview before committing.")
diff --git a/docs/ARCHITECTURE.md b/docs/ARCHITECTURE.md
index 46133de..4a21fc2 100644
--- a/docs/ARCHITECTURE.md
+++ b/docs/ARCHITECTURE.md
@@ -202,7 +202,7 @@ What it must not own:
 
 Current status:
 
-Seasonal Participation V1 Phase 1 foundation is implemented. The schema, services, admin registration, and tests exist, but player imports, coach imports, and evaluations are not season-aware yet.
+Seasonal Participation V1 Phase 1 foundation and Phase 2 season-aware player import are implemented. The schema, services, admin registration, tests, and player import integration exist. Player imports now require a selected active season and create or update season teams and player roster memberships. Coach imports and evaluations are not season-aware yet.
 
 Documentation:
 
@@ -327,7 +327,7 @@ Dependency guidance:
 | Players | V1 | Complete |
 | Analytics | V1 | Complete |
 | Account Management | V1 | Complete / Frozen |
-| Seasons | V1 Phase 1 | Foundation complete |
+| Seasons | V1 Phase 2 | Player import integration complete |
 | Drafts | Active | Active development |
 | PDP | Legacy | Transitionary |
 | LeagueHub | Planned | Planned |
@@ -359,7 +359,7 @@ Likely future areas:
 
 - Account Management V2
 - Analytics V2
-- Seasonal Participation Phase 2
+- Seasonal Participation Phase 3
 - Drafts expansion
 - LeagueHub
 - Video
diff --git a/docs/USER_MANUAL.md b/docs/USER_MANUAL.md
index 4a1cc37..d000a40 100644
--- a/docs/USER_MANUAL.md
+++ b/docs/USER_MANUAL.md
@@ -15,7 +15,7 @@ The platform helps Vancouver Community Baseball manage:
 
 This is a user manual, not a technical deployment guide. Deployment information lives in [docs/deployment/](deployment/README.md).
 
-Season-aware roster foundations now exist in the system, but normal player import, coach import, and evaluation pages are not season-aware yet. Staff should continue using the current import and evaluation workflows until the next seasonal import phase is implemented.
+Season-aware roster foundations now exist in the system. Player imports are now season-aware: staff choose an active season, and imported team/division information creates roster participation records for that season. Coach import and evaluation pages are not season-aware yet, so staff should continue using the current coach import and evaluation workflows until those seasonal phases are implemented.
 
 ## Start Here
 
@@ -569,7 +569,7 @@ Staff and administrators.
 
 1. Open `/analytics/imports/`.
 2. Upload a CSV file.
-3. Choose source information.
+3. Choose the active season and source information.
 4. Map CSV columns to player fields.
 5. Preview the import.
 6. Review conflicts or ambiguous matches.
@@ -597,6 +597,9 @@ Player imports can include:
 - birth year
 - division
 - team
+- roster status
+- jersey number
+- roster start/end dates
 - positions
 - bats/throws
 - school
@@ -605,6 +608,8 @@ Player imports can include:
 
 Birthdate is supported and is important for player identity and account provisioning.
 
+Season, division, and team are required for the current player import workflow. Division and team are used as roster context for the selected season rather than as permanent player identity.
+
 ### Account Provisioning From Player Imports
 
 During a player import, staff may choose to provision player accounts.
diff --git a/docs/seasons/README.md b/docs/seasons/README.md
index 08e2251..59af133 100644
--- a/docs/seasons/README.md
+++ b/docs/seasons/README.md
@@ -21,6 +21,8 @@ Phase 0 planning decisions are complete.
 
 Phase 1 - Season And Roster Foundation is implemented.
 
+Phase 2 - Season-Aware Player Import is implemented.
+
 Verified production state on July 15, 2026:
 
 ```text
@@ -42,15 +44,25 @@ Implemented foundation:
 - schema-only migration
 - tests for current-season, roster membership, coach assignment, compatibility, and admin behavior
 
+Implemented player import integration:
+
+- player imports require a selected active season;
+- import batches store the selected season;
+- imported rows require team and division roster context;
+- player identity matching remains permanent-player based;
+- season teams are created or reused through `seasons` services;
+- player roster memberships are created or updated through `seasons` services;
+- same-season active primary team changes are blocked for manual review;
+- prior-season memberships are preserved.
+
 Current limitations:
 
-- player import does not require or create seasonal memberships yet;
 - coach import does not require or create seasonal assignments yet;
 - evaluations do not yet store season/team/membership context;
 - there are no first-class roster-management pages yet.
 
 Next phase:
 
-- Phase 2 - Season-Aware Player Import.
+- Phase 3 - Season-Aware Coach Import.
 
-No user-facing import or evaluation workflow changes were made in Phase 1.
+No coach import or evaluation workflow changes were made in Phase 2.
diff --git a/docs/seasons/implementation/engineering/seasonal_participation_v1.md b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
index baab82b..04d9e39 100644
--- a/docs/seasons/implementation/engineering/seasonal_participation_v1.md
+++ b/docs/seasons/implementation/engineering/seasonal_participation_v1.md
@@ -1,6 +1,6 @@
 # Seasonal Participation V1 Engineering Plan
 
-Status: Phase 1 foundation complete. Phase 2 is the next implementation phase.
+Status: Phase 1 foundation complete. Phase 2 season-aware player import complete. Phase 3 is the next implementation phase.
 
 Created: 2026-07-15.
 
@@ -678,6 +678,8 @@ Phase 1 must not:
 
 ### Phase 2 - Season-Aware Player Import
 
+Status: complete.
+
 - Add season selection to player import.
 - Map team/division to `SeasonTeam`.
 - Create/update `PlayerRosterMembership`.
@@ -811,13 +813,13 @@ Rollback considerations:
 - Should the exact one-current-season rule be database-enforced on SQLite, service-enforced, or both?
 - Should compatibility writes to `Player.team_name` and `Player.division` happen automatically when primary membership changes, or only during import/service workflows?
 
-## 27. Recommended First Implementation Phase
+## 27. Recommended Next Implementation Phase
 
-Start with Phase 2 - Season-Aware Player Import.
+Start with Phase 3 - Coach Seasonal Assignment.
 
-Phase 1 decisions and implementation are complete. Phase 2 should update player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services.
+Phase 1 decisions and implementation are complete. Phase 2 updated player import to require a selected season, create or reuse `SeasonTeam`, and create/update `PlayerRosterMembership` through `seasons` services.
 
-Before implementing Phase 2, verify that Phase 1 production migration completed with empty seasonal tables and no fabricated history.
+Before implementing Phase 3, verify that Phase 2 production migration completed successfully and that imported player rows are creating expected season teams and roster memberships.
 
 ## 28. Acceptance Criteria
 
diff --git a/players/admin.py b/players/admin.py
index d8604ed..1889490 100644
--- a/players/admin.py
+++ b/players/admin.py
@@ -60,6 +60,7 @@ class PlayerImportBatchAdmin(TimeStampedAdmin):
     list_display = (
         "original_filename",
         "source",
+        "season",
         "status",
         "uploaded_by",
         "rows_processed",
@@ -68,8 +69,9 @@ class PlayerImportBatchAdmin(TimeStampedAdmin):
         "rows_conflicted",
         "created_at",
     )
-    list_filter = ("status", "source", "created_at")
+    list_filter = ("status", "source", "season", "created_at")
     search_fields = ("original_filename", "uploaded_by__username", "uploaded_by__email")
+    autocomplete_fields = ("season", "uploaded_by")
     readonly_fields = TimeStampedAdmin.readonly_fields + (
         "committed_at",
         "preview_snapshot",
diff --git a/players/migrations/0003_playerimportbatch_season_and_more.py b/players/migrations/0003_playerimportbatch_season_and_more.py
new file mode 100644
index 0000000..e878f88
--- /dev/null
+++ b/players/migrations/0003_playerimportbatch_season_and_more.py
@@ -0,0 +1,24 @@
+# Generated by Django 4.2.25 on 2026-07-16 04:56
+
+from django.db import migrations, models
+import django.db.models.deletion
+
+
+class Migration(migrations.Migration):
+
+    dependencies = [
+        ('seasons', '0001_initial'),
+        ('players', '0002_playerimportbatch_and_more'),
+    ]
+
+    operations = [
+        migrations.AddField(
+            model_name='playerimportbatch',
+            name='season',
+            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='player_import_batches', to='seasons.season'),
+        ),
+        migrations.AddIndex(
+            model_name='playerimportbatch',
+            index=models.Index(fields=['season', '-created_at'], name='players_pla_season__4fcae7_idx'),
+        ),
+    ]
diff --git a/players/models.py b/players/models.py
index d328025..c1d2454 100644
--- a/players/models.py
+++ b/players/models.py
@@ -130,6 +130,13 @@ class PlayerImportBatch(TimeStampedModel):
         on_delete=models.SET_NULL,
         related_name="player_import_batches",
     )
+    season = models.ForeignKey(
+        "seasons.Season",
+        null=True,
+        blank=True,
+        on_delete=models.PROTECT,
+        related_name="player_import_batches",
+    )
     status = models.CharField(max_length=40, choices=PlayerImportStatus.choices, default=PlayerImportStatus.UPLOADED)
     mapping_config = models.JSONField(default=dict, blank=True)
     preview_snapshot = models.JSONField(default=dict, blank=True)
@@ -149,6 +156,7 @@ class PlayerImportBatch(TimeStampedModel):
             models.Index(fields=["status", "-created_at"]),
             models.Index(fields=["source", "-created_at"]),
             models.Index(fields=["uploaded_by", "-created_at"]),
+            models.Index(fields=["season", "-created_at"]),
         ]
 
     def save(self, *args, **kwargs):
diff --git a/players/services/import_service.py b/players/services/import_service.py
index ba1970c..a139e14 100644
--- a/players/services/import_service.py
+++ b/players/services/import_service.py
@@ -26,6 +26,9 @@ from players.services.matching_service import (
     find_player_match,
     match_by_identifier,
 )
+from seasons.models import PlayerRosterMembership, RosterStatus, SeasonTeam
+from seasons.services.membership_service import create_membership, sync_player_current_team_fields, update_membership
+from seasons.services.team_service import get_or_create_season_team, normalize_division_value, normalize_team_value
 
 
 SOURCE_MEMBER_LIST = "vcb_member_list_csv"
@@ -73,6 +76,20 @@ PLAYER_FIELD_KEYS = [
     "graduation_year",
 ]
 
+PERMANENT_PLAYER_FIELD_KEYS = [
+    "first_name",
+    "last_name",
+    "preferred_name",
+    "birthdate",
+    "birth_year",
+    "gender",
+    "primary_positions",
+    "bats",
+    "throws",
+    "school",
+    "graduation_year",
+]
+
 CONFLICT_FIELDS = [
     "first_name",
     "last_name",
@@ -80,8 +97,6 @@ CONFLICT_FIELDS = [
     "birthdate",
     "birth_year",
     "gender",
-    "division",
-    "team_name",
     "primary_positions",
     "bats",
     "throws",
@@ -106,6 +121,11 @@ HEADER_ALIASES = {
     "gender": {"gender", "sex"},
     "division": {"division", "level", "program"},
     "team_name": {"team", "team name", "current team"},
+    "roster_status": {"roster status", "status", "membership status"},
+    "jersey_number": {"jersey", "jersey number", "number", "uniform number"},
+    "membership_start_date": {"membership start date", "start date", "starts on", "roster start"},
+    "membership_end_date": {"membership end date", "end date", "ends on", "roster end"},
+    "roster_source_id": {"roster source id", "membership id", "roster id"},
     "primary_positions": {"position", "positions", "primary position", "primary positions"},
     "bats": {"bats", "batting", "hits"},
     "throws": {"throws", "throwing"},
@@ -167,6 +187,9 @@ class ImportPreviewRow:
     field_conflicts: list[dict[str, str]] = field(default_factory=list)
     errors: list[str] = field(default_factory=list)
     action: str = ACTION_CREATE
+    roster: dict[str, Any] = field(default_factory=dict)
+    season_team: dict[str, Any] = field(default_factory=dict)
+    membership: dict[str, Any] = field(default_factory=dict)
 
 
 @dataclass
@@ -176,6 +199,10 @@ class ImportCommitResult:
     updated: int = 0
     skipped: int = 0
     conflicts: int = 0
+    season_teams_created: int = 0
+    season_teams_reused: int = 0
+    memberships_created: int = 0
+    memberships_updated: int = 0
     errors: list[str] = field(default_factory=list)
     account_provisioning: dict[str, Any] = field(default_factory=dict)
 
@@ -325,6 +352,30 @@ def parse_birthdate(value: str):
     return None
 
 
+def parse_import_date(value: str):
+    """Parse optional roster date values from CSV input."""
+    return parse_birthdate(value)
+
+
+ROSTER_STATUS_ALIASES = {
+    "": RosterStatus.ACTIVE,
+    "active": RosterStatus.ACTIVE,
+    "inactive": RosterStatus.INACTIVE,
+    "transferred": RosterStatus.TRANSFERRED,
+    "transfer": RosterStatus.TRANSFERRED,
+    "guest": RosterStatus.GUEST,
+    "removed": RosterStatus.REMOVED,
+    "remove": RosterStatus.REMOVED,
+}
+
+
+def parse_roster_status(value: str) -> str:
+    cleaned = normalize_header(value)
+    if cleaned in ROSTER_STATUS_ALIASES:
+        return ROSTER_STATUS_ALIASES[cleaned]
+    raise ValidationError(f"Unknown roster status '{clean_cell(value)}'.")
+
+
 def parse_birth_year(value: str):
     """Parse a birth year from a string."""
     cleaned = clean_cell(value)
@@ -365,7 +416,7 @@ def _identity_for_storage(identity: dict[str, Any]) -> dict[str, Any]:
 
 def _identity_for_model(identity: dict[str, Any]) -> dict[str, Any]:
     model_identity = {}
-    for field_name in PLAYER_FIELD_KEYS:
+    for field_name in PERMANENT_PLAYER_FIELD_KEYS:
         value = identity.get(field_name)
         if field_name == "birthdate" and value:
             value = parse_birthdate(value) if not isinstance(value, date) else value
@@ -376,6 +427,42 @@ def _identity_for_model(identity: dict[str, Any]) -> dict[str, Any]:
     return model_identity
 
 
+def build_roster_payload(row: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
+    """Build season roster context from a source row and optional column mapping."""
+    mapping = mapping or {}
+    status_column = mapping.get("roster_status", "")
+    starts_column = mapping.get("membership_start_date", "")
+    ends_column = mapping.get("membership_end_date", "")
+    try:
+        roster_status = parse_roster_status(row.get(status_column, "")) if status_column else RosterStatus.ACTIVE
+    except ValidationError as exc:
+        roster_status = ""
+        status_errors = list(exc.messages)
+    else:
+        status_errors = []
+
+    starts_on = parse_import_date(row.get(starts_column, "")) if starts_column else None
+    ends_on = parse_import_date(row.get(ends_column, "")) if ends_column else None
+    errors = status_errors
+    if starts_column and clean_cell(row.get(starts_column)) and starts_on is None:
+        errors.append("Membership start date is invalid.")
+    if ends_column and clean_cell(row.get(ends_column)) and ends_on is None:
+        errors.append("Membership end date is invalid.")
+    if starts_on and ends_on and ends_on < starts_on:
+        errors.append("Membership end date cannot be before start date.")
+
+    return {
+        "team_name": clean_cell(row.get(mapping.get("team_name", "team_name"))),
+        "division": clean_cell(row.get(mapping.get("division", "division"))),
+        "roster_status": roster_status,
+        "jersey_number": clean_cell(row.get(mapping.get("jersey_number", ""))) if mapping.get("jersey_number") else "",
+        "starts_on": starts_on.isoformat() if starts_on else "",
+        "ends_on": ends_on.isoformat() if ends_on else "",
+        "roster_source_id": clean_cell(row.get(mapping.get("roster_source_id", ""))) if mapping.get("roster_source_id") else "",
+        "errors": errors,
+    }
+
+
 def build_identity_payload(row: dict[str, Any], mapping: dict[str, str] | None = None) -> dict[str, Any]:
     """Build a player identity payload from a source row and optional column mapping."""
     mapping = mapping or {}
@@ -434,11 +521,16 @@ def create_import_batch(
     file_obj,
     source: str,
     uploaded_by,
+    season=None,
     provision_player_accounts: bool = False,
     activate_player_accounts: bool = True,
 ) -> PlayerImportBatch:
     """Create a persisted player import batch from a CSV upload."""
     _ensure_staff(uploaded_by)
+    if season is None:
+        raise ValidationError("Select an active season for this player import.")
+    if not getattr(season, "is_active", False):
+        raise ValidationError("Select an active season for this player import.")
     parsed = parse_player_csv(file_obj)
     normalized_source = _normalize_source(source or detect_source_from_filename(parsed.file_name))
     mapping_config = suggest_mapping(parsed.headers, source=normalized_source)
@@ -448,6 +540,7 @@ def create_import_batch(
         source=normalized_source,
         original_filename=parsed.file_name,
         uploaded_by=uploaded_by,
+        season=season,
         status=PlayerImportStatus.UPLOADED,
         mapping_config=mapping_config,
         preview_snapshot={"parsed_csv": _parsed_to_snapshot(parsed)},
@@ -464,7 +557,7 @@ def _match_identity(identity: dict[str, Any], source_identifiers: list[dict[str,
         "last_name": model_identity.get("last_name", ""),
         "birthdate": model_identity.get("birthdate"),
         "birth_year": model_identity.get("birth_year"),
-        "division": model_identity.get("division", ""),
+        "division": identity.get("division", ""),
     }
     if source_identifiers:
         exact_matches = []
@@ -523,16 +616,91 @@ def _field_conflicts(player: Player | None, identity: dict[str, Any]) -> list[di
     return conflicts
 
 
-def preview_row(*, row: dict[str, Any], mapping_config: dict[str, str], source: str) -> ImportPreviewRow:
+def _team_preview(roster: dict[str, Any], season) -> dict[str, Any]:
+    team_name = roster.get("team_name", "")
+    division = roster.get("division", "")
+    if not team_name or not division:
+        return {"action": "invalid_roster_context", "label": "Invalid Roster Context"}
+    normalized_name = normalize_team_value(team_name)
+    normalized_division = normalize_division_value(division)
+    existing = SeasonTeam.objects.filter(
+        season=season,
+        normalized_name=normalized_name,
+        normalized_division=normalized_division,
+    ).first()
+    return {
+        "id": existing.id if existing else None,
+        "name": existing.name if existing else team_name,
+        "division": existing.division if existing else division,
+        "action": "reuse" if existing else "create",
+        "label": "Reuse Season Team" if existing else "Create Season Team",
+    }
+
+
+def _membership_preview(player: Player | None, season_team_preview: dict[str, Any], season, roster: dict[str, Any]) -> dict[str, Any]:
+    if not player:
+        return {"action": "create", "label": "Create Membership", "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE}
+    existing_same_team = None
+    if season_team_preview.get("id"):
+        existing_same_team = PlayerRosterMembership.objects.filter(
+            player=player,
+            season_team_id=season_team_preview["id"],
+        ).first()
+    if existing_same_team:
+        return {
+            "id": existing_same_team.id,
+            "action": "update",
+            "label": "Update Membership",
+            "is_primary": existing_same_team.is_primary,
+        }
+    primary = PlayerRosterMembership.objects.select_related("season_team").filter(
+        player=player,
+        season_team__season=season,
+        is_active=True,
+        is_primary=True,
+    ).first()
+    if primary:
+        return {
+            "id": None,
+            "action": "review_team_change",
+            "label": "Review Team Change",
+            "is_primary": False,
+            "existing_primary": str(primary.season_team),
+        }
+    return {"id": None, "action": "new_season_membership", "label": "New Season Membership", "is_primary": roster.get("roster_status") == RosterStatus.ACTIVE}
+
+
+def preview_row(*, row: dict[str, Any], mapping_config: dict[str, str], source: str, season=None) -> ImportPreviewRow:
     """Build preview data for a single CSV row."""
     cleaned_row = row["cleaned_row"]
     identity = build_identity_payload(cleaned_row, mapping_config)
+    roster = build_roster_payload(cleaned_row, mapping_config)
     source_identifiers = build_source_identifiers(cleaned_row, mapping_config, source)
-    errors = []
+    errors = list(roster.get("errors", []))
     if not (identity.get("first_name") and identity.get("last_name")):
         errors.append("Map either a full name column or both first and last name columns.")
+    if not season:
+        errors.append("Select an active season for this import.")
+    if not roster.get("team_name"):
+        errors.append("Team is required for season-aware player import.")
+    if not roster.get("division"):
+        errors.append("Division is required for season-aware player import.")
     match_result = _match_identity(identity, source_identifiers) if not errors else None
     field_conflicts = _field_conflicts(getattr(match_result, "player", None), identity) if match_result else []
+    season_team_preview = _team_preview(roster, season) if season and not (not roster.get("team_name") or not roster.get("division")) else {
+        "action": "invalid_roster_context",
+        "label": "Invalid Roster Context",
+    }
+    matched_player = getattr(match_result, "player", None) if match_result else None
+    membership_preview = _membership_preview(matched_player, season_team_preview, season, roster) if season and not errors else {
+        "action": "invalid_roster_context",
+        "label": "Invalid Roster Context",
+        "is_primary": False,
+    }
+    if membership_preview.get("action") == "review_team_change":
+        errors.append(
+            "Player already has an active primary membership in this season. Resolve the team change manually or skip this row."
+        )
 
     if errors:
         action = ACTION_ERROR
@@ -551,7 +719,6 @@ def preview_row(*, row: dict[str, Any], mapping_config: dict[str, str], source:
         match_status = MATCH_NO_MATCH
 
     candidates = getattr(match_result, "candidates", []) if match_result else []
-    matched_player = getattr(match_result, "player", None) if match_result else None
     return ImportPreviewRow(
         row_number=row["row_number"],
         identity=identity,
@@ -567,6 +734,9 @@ def preview_row(*, row: dict[str, Any], mapping_config: dict[str, str], source:
         field_conflicts=field_conflicts,
         errors=errors,
         action=action,
+        roster={key: value for key, value in roster.items() if key != "errors"},
+        season_team=season_team_preview,
+        membership=membership_preview,
     )
 
 
@@ -575,12 +745,19 @@ def build_import_preview(*, import_batch: PlayerImportBatch, mapping_config: dic
     """Build and persist an import preview for a batch."""
     parsed = _snapshot_to_parsed(import_batch.preview_snapshot)
     mapping_config = mapping_config or import_batch.mapping_config or suggest_mapping(parsed.headers, source=import_batch.source)
-    rows = [_json_preview_row(preview_row(row=row, mapping_config=mapping_config, source=import_batch.source)) for row in parsed.rows]
+    rows = [
+        _json_preview_row(preview_row(row=row, mapping_config=mapping_config, source=import_batch.source, season=import_batch.season))
+        for row in parsed.rows
+    ]
     row_errors = [row for row in rows if row["errors"]]
     conflicted_rows = [row for row in rows if row["action"] == ACTION_NEEDS_REVIEW]
     preview = {
         "file_name": parsed.file_name,
         "source": import_batch.source,
+        "season": {
+            "id": import_batch.season_id,
+            "name": import_batch.season.name if import_batch.season_id else "Legacy / No Season",
+        },
         "headers": parsed.headers,
         "mapping_config": mapping_config,
         "account_provisioning": {
@@ -595,6 +772,10 @@ def build_import_preview(*, import_batch: PlayerImportBatch, mapping_config: dic
             "rows_update": sum(1 for row in rows if row["action"] == ACTION_UPDATE),
             "rows_needs_review": len(conflicted_rows),
             "rows_error": len(row_errors),
+            "season_teams_create": sum(1 for row in rows if row.get("season_team", {}).get("action") == "create"),
+            "season_teams_reuse": sum(1 for row in rows if row.get("season_team", {}).get("action") == "reuse"),
+            "memberships_create": sum(1 for row in rows if row.get("membership", {}).get("action") in {"create", "new_season_membership"}),
+            "memberships_update": sum(1 for row in rows if row.get("membership", {}).get("action") == "update"),
         },
     }
     import_batch.mapping_config = mapping_config
@@ -694,6 +875,86 @@ def record_import_source_row(player: Player, import_batch: PlayerImportBatch, pr
     )
 
 
+def _parse_iso_date(value: str):
+    cleaned = clean_cell(value)
+    if not cleaned:
+        return None
+    try:
+        return datetime.strptime(cleaned, "%Y-%m-%d").date()
+    except ValueError:
+        raise ValidationError("Roster date is invalid.") from None
+
+
+def _membership_update_values(roster: dict[str, Any]) -> dict[str, Any]:
+    values = {}
+    if roster.get("roster_status"):
+        values["status"] = roster["roster_status"]
+        values["is_active"] = roster["roster_status"] in {RosterStatus.ACTIVE, RosterStatus.GUEST}
+        if not values["is_active"]:
+            values["is_primary"] = False
+    if roster.get("jersey_number"):
+        values["jersey_number"] = roster["jersey_number"]
+    if roster.get("starts_on"):
+        values["starts_on"] = _parse_iso_date(roster["starts_on"])
+    if roster.get("ends_on"):
+        values["ends_on"] = _parse_iso_date(roster["ends_on"])
+    if roster.get("roster_source_id"):
+        values["source_identifier"] = roster["roster_source_id"]
+    return values
+
+
+def _commit_membership(player: Player, import_batch: PlayerImportBatch, preview_row_data: dict[str, Any]) -> tuple[str, bool]:
+    if not import_batch.season_id:
+        raise ValidationError("Import batch requires a season before memberships can be committed.")
+    roster = preview_row_data.get("roster", {})
+    team_name = roster.get("team_name", "")
+    division = roster.get("division", "")
+    if not team_name or not division:
+        raise ValidationError("Team and division are required for roster membership.")
+    season_team, team_created = get_or_create_season_team(
+        season=import_batch.season,
+        name=team_name,
+        division=division,
+        external_source=import_batch.source if roster.get("roster_source_id") else "",
+        external_identifier=roster.get("roster_source_id", ""),
+        metadata={"import_batch_id": import_batch.id},
+    )
+    existing = PlayerRosterMembership.objects.select_for_update().filter(player=player, season_team=season_team).first()
+    values = _membership_update_values(roster)
+    values.setdefault("source", import_batch.source)
+    if existing:
+        was_primary = existing.is_primary
+        update_membership(existing, sync_player_fields=was_primary, **values)
+        return "updated", team_created
+
+    primary = PlayerRosterMembership.objects.select_for_update().filter(
+        player=player,
+        season_team__season=import_batch.season,
+        is_active=True,
+        is_primary=True,
+    ).first()
+    if primary:
+        raise ValidationError("Player already has an active primary membership in this season.")
+    status = values.pop("status", roster.get("roster_status") or RosterStatus.ACTIVE)
+    is_active = values.pop("is_active", status in {RosterStatus.ACTIVE, RosterStatus.GUEST})
+    membership = create_membership(
+        player=player,
+        season_team=season_team,
+        status=status,
+        is_primary=is_active,
+        is_active=is_active,
+        source=values.pop("source", import_batch.source),
+        source_identifier=values.pop("source_identifier", roster.get("roster_source_id", "")),
+        import_batch=import_batch,
+        metadata={"row_number": preview_row_data["row_number"]},
+        sync_player_fields=is_active,
+        **values,
+    )
+    if membership.is_primary:
+        sync_player_current_team_fields(player, import_batch.season)
+    return "created", team_created
+
+
 def _resolutions_for_row(resolutions: dict[str, Any], row_number: int) -> tuple[str, dict[str, str]]:
     row_key = str(row_number)
     row_resolution = resolutions.get(row_key, {}) if resolutions else {}
@@ -747,6 +1008,8 @@ def commit_import_batch(*, import_batch: PlayerImportBatch, actor, resolutions:
     locked_batch = PlayerImportBatch.objects.select_for_update().get(pk=import_batch.pk)
     if locked_batch.status == PlayerImportStatus.COMMITTED:
         raise ValidationError("This import batch has already been committed.")
+    if not locked_batch.season_id:
+        raise ValidationError("Select an active season before committing this player import.")
 
     preview = current_preview(locked_batch)
     if not preview:
@@ -797,6 +1060,15 @@ def commit_import_batch(*, import_batch: PlayerImportBatch, actor, resolutions:
         )
         result.errors.extend([f"Row {row_number}: {error}" for error in identifier_errors])
         record_import_source_row(player, locked_batch, preview_row_data, actor)
+        membership_action, team_created = _commit_membership(player, locked_batch, preview_row_data)
+        if team_created:
+            result.season_teams_created += 1
+        else:
+            result.season_teams_reused += 1
+        if membership_action == "created":
+            result.memberships_created += 1
+        else:
+            result.memberships_updated += 1
         committed_rows.append(
             {
                 "player": player,
diff --git a/players/tests.py b/players/tests.py
index b4db580..89bc2b9 100644
--- a/players/tests.py
+++ b/players/tests.py
@@ -40,6 +40,8 @@ from players.services.matching_service import (
     match_by_name_and_birthdate,
 )
 from players.services.tag_service import active_tags, assign_tag, players_with_tag, remove_tag
+from seasons.models import PlayerRosterMembership, SeasonTeam
+from seasons.services.season_service import create_season
 
 
 User = get_user_model()
@@ -228,8 +230,9 @@ class PlayerImportWorkflowTests(TestCase):
     def setUp(self):
         self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
         self.user = User.objects.create_user(username="user", password="testpass")
+        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)
 
-    def upload(self, name="member list for 13u house.csv", body=b"First,Last,Gender,Team\nEugene,Lin,M,Expos\n"):
+    def upload(self, name="member list for 13u house.csv", body=b"First,Last,Gender,Division,Team\nEugene,Lin,M,13U,Expos\n"):
         return SimpleUploadedFile(name, body, content_type="text/csv")
 
     def test_parse_csv_handles_bom_and_preserves_rows(self):
@@ -269,11 +272,20 @@ class PlayerImportWorkflowTests(TestCase):
             create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.user)
 
     def test_preview_classifies_new_player_as_create(self):
-        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff)
+        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
         preview = batch.preview_snapshot["preview"]
 
         self.assertEqual(preview["rows"][0]["action"], ACTION_CREATE)
         self.assertEqual(preview["summary"]["rows_create"], 1)
+        self.assertEqual(preview["season"]["name"], "2026 Spring")
+
+    def test_create_import_batch_requires_active_season(self):
+        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)
+
+        with self.assertRaises(ValidationError):
+            create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff)
+        with self.assertRaises(ValidationError):
+            create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=inactive)
 
     def test_preview_classifies_source_identifier_match_as_update(self):
         player = Player.objects.create(first_name="Eugene", last_name="Lin")
@@ -281,10 +293,11 @@ class PlayerImportWorkflowTests(TestCase):
         batch = create_import_batch(
             file_obj=self.upload(
                 name="roster detail for 13u house.csv",
-                body=b"First Name,Last Name,Registration ID,Team\nEugene,Lin,REG-1,Expos\n",
+                body=b"First Name,Last Name,Registration ID,Division,Team\nEugene,Lin,REG-1,13U,Expos\n",
             ),
             source=SOURCE_ROSTER_DETAIL,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         row = batch.preview_snapshot["preview"]["rows"][0]
@@ -297,10 +310,11 @@ class PlayerImportWorkflowTests(TestCase):
         batch = create_import_batch(
             file_obj=self.upload(
                 name="roster detail for 13u house.csv",
-                body=b"First Name,Last Name,Registration ID,Registrant ID\nEugene,Lin,NO-MATCH,MEM-1\n",
+                body=b"First Name,Last Name,Registration ID,Registrant ID,Division,Team\nEugene,Lin,NO-MATCH,MEM-1,13U,Expos\n",
             ),
             source=SOURCE_ROSTER_DETAIL,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         row = batch.preview_snapshot["preview"]["rows"][0]
@@ -315,10 +329,11 @@ class PlayerImportWorkflowTests(TestCase):
         batch = create_import_batch(
             file_obj=self.upload(
                 name="roster detail for 13u house.csv",
-                body=b"First Name,Last Name,Registration ID,Registrant ID\nEugene,Lin,REG-1,MEM-1\n",
+                body=b"First Name,Last Name,Registration ID,Registrant ID,Division,Team\nEugene,Lin,REG-1,MEM-1,13U,Expos\n",
             ),
             source=SOURCE_ROSTER_DETAIL,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         row = batch.preview_snapshot["preview"]["rows"][0]
@@ -331,21 +346,23 @@ class PlayerImportWorkflowTests(TestCase):
             first_name="Eugene",
             last_name="Lin",
             birthdate="2012-05-01",
+            preferred_name="Old",
             team_name="Existing Team",
         )
         batch = create_import_batch(
             file_obj=self.upload(
                 name="roster detail for 13u house.csv",
-                body=b"First Name,Last Name,DOB,Team\nEugene,Lin,2012-05-01,New Team\n",
+                body=b"First Name,Last Name,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,Gene,13U,New Team\n",
             ),
             source=SOURCE_ROSTER_DETAIL,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         row = batch.preview_snapshot["preview"]["rows"][0]
         self.assertEqual(row["action"], ACTION_NEEDS_REVIEW)
         self.assertEqual(row["matched_player_id"], player.id)
-        self.assertEqual(row["field_conflicts"][0]["field_name"], "team_name")
+        self.assertEqual(row["field_conflicts"][0]["field_name"], "preferred_name")
 
     def test_preview_treats_name_difference_on_identifier_match_as_conflict(self):
         player = Player.objects.create(first_name="Eugene", last_name="Lin")
@@ -353,10 +370,11 @@ class PlayerImportWorkflowTests(TestCase):
         batch = create_import_batch(
             file_obj=self.upload(
                 name="roster detail for 13u house.csv",
-                body=b"First Name,Last Name,Registration ID\nGene,Lin,REG-1\n",
+                body=b"First Name,Last Name,Registration ID,Division,Team\nGene,Lin,REG-1,13U,Expos\n",
             ),
             source=SOURCE_ROSTER_DETAIL,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         row = batch.preview_snapshot["preview"]["rows"][0]
@@ -367,9 +385,10 @@ class PlayerImportWorkflowTests(TestCase):
         Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
         Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Birth Year,Division\nEugene,Lin,2012,13U\n,Missing,2012,13U\n"),
+            file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n,Missing,2012,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         rows = batch.preview_snapshot["preview"]["rows"]
@@ -378,26 +397,93 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(rows[1]["action"], ACTION_ERROR)
 
     def test_commit_creates_player_and_source_row(self):
-        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff)
+        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
 
         result = commit_import_batch(import_batch=batch, actor=self.staff)
 
         player = Player.objects.get(first_name="Eugene", last_name="Lin")
         self.assertEqual(result.created, 1)
         self.assertEqual(PlayerSourceRow.objects.get(player=player).import_batch_id, batch.id)
+        membership = PlayerRosterMembership.objects.select_related("season_team").get(player=player)
+        self.assertEqual(membership.season_team.season, self.season)
+        self.assertEqual(membership.season_team.name, "Expos")
+        self.assertEqual(membership.season_team.division, "13U")
+        self.assertTrue(membership.is_primary)
+        self.assertEqual(result.season_teams_created, 1)
+        self.assertEqual(result.memberships_created, 1)
         batch.refresh_from_db()
         self.assertEqual(batch.status, PlayerImportStatus.COMMITTED)
 
+    def test_commit_reuses_same_team_membership_in_same_season(self):
+        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        commit_import_batch(import_batch=first_batch, actor=self.staff)
+        player = Player.objects.get(first_name="Eugene", last_name="Lin")
+        add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")
+        second_batch = create_import_batch(
+            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team,Jersey\nEugene,Lin,MEM-1,13U,Expos,27\n"),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=self.season,
+        )
+
+        result = commit_import_batch(import_batch=second_batch, actor=self.staff)
+
+        self.assertEqual(result.updated, 1)
+        self.assertEqual(result.memberships_updated, 1)
+        self.assertEqual(PlayerRosterMembership.objects.filter(player=player, season_team__season=self.season).count(), 1)
+        self.assertEqual(PlayerRosterMembership.objects.get(player=player).jersey_number, "27")
+
+    def test_commit_preserves_prior_season_and_creates_future_membership(self):
+        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        commit_import_batch(import_batch=first_batch, actor=self.staff)
+        player = Player.objects.get(first_name="Eugene", last_name="Lin")
+        add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")
+        next_season = create_season(key="2027-spring", name="2027 Spring")
+        next_batch = create_import_batch(
+            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team\nEugene,Lin,MEM-1,15U,Mounties\n"),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=next_season,
+        )
+
+        commit_import_batch(import_batch=next_batch, actor=self.staff)
+
+        self.assertEqual(PlayerRosterMembership.objects.filter(player=player).count(), 2)
+        self.assertTrue(
+            PlayerRosterMembership.objects.filter(player=player, season_team__season=self.season, season_team__name="Expos").exists()
+        )
+        self.assertTrue(
+            PlayerRosterMembership.objects.filter(player=player, season_team__season=next_season, season_team__name="Mounties").exists()
+        )
+
+    def test_preview_blocks_same_season_team_change_for_active_primary(self):
+        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
+        commit_import_batch(import_batch=first_batch, actor=self.staff)
+        player = Player.objects.get(first_name="Eugene", last_name="Lin")
+        add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")
+
+        change_batch = create_import_batch(
+            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team\nEugene,Lin,MEM-1,13U,Mounties\n"),
+            source=SOURCE_MEMBER_LIST,
+            uploaded_by=self.staff,
+            season=self.season,
+        )
+
+        row = change_batch.preview_snapshot["preview"]["rows"][0]
+        self.assertEqual(row["action"], ACTION_ERROR)
+        self.assertIn("active primary membership", " ".join(row["errors"]))
+
     def test_commit_updates_blanks_without_overwriting_conflicts(self):
         player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01")
         add_source_identifier(player, SOURCE_ROSTER_DETAIL, "registration_id", "REG-1")
         batch = create_import_batch(
             file_obj=self.upload(
                 name="roster detail for 13u house.csv",
-                body=b"First Name,Last Name,DOB,Registration ID,Team\nEugene,Lin,2012-05-01,REG-1,Expos\n",
+                body=b"First Name,Last Name,DOB,Registration ID,Division,Team\nEugene,Lin,2012-05-01,REG-1,13U,Expos\n",
             ),
             source=SOURCE_ROSTER_DETAIL,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         result = commit_import_batch(import_batch=batch, actor=self.staff)
@@ -407,25 +493,27 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(player.team_name, "Expos")
 
     def test_commit_applies_use_imported_resolution(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", team_name="Old")
+        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Team\nEugene,Lin,2012-05-01,New\n"),
+            file_obj=self.upload(body=b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
+            season=self.season,
         )
-        resolutions = {"2": {"action": "commit", "fields": {"team_name": "use_imported"}}}
+        resolutions = {"2": {"action": "commit", "fields": {"preferred_name": "use_imported"}}}
 
         commit_import_batch(import_batch=batch, actor=self.staff, resolutions=resolutions)
 
         player.refresh_from_db()
-        self.assertEqual(player.team_name, "New")
+        self.assertEqual(player.preferred_name, "New")
 
     def test_commit_rejects_unresolved_review_rows_without_mutating_player(self):
-        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", team_name="Old")
+        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Team\nEugene,Lin,2012-05-01,New\n"),
+            file_obj=self.upload(body=b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         with self.assertRaises(ValidationError):
@@ -433,7 +521,7 @@ class PlayerImportWorkflowTests(TestCase):
 
         player.refresh_from_db()
         batch.refresh_from_db()
-        self.assertEqual(player.team_name, "Old")
+        self.assertEqual(player.preferred_name, "Old")
         self.assertEqual(batch.status, PlayerImportStatus.NEEDS_REVIEW)
         self.assertFalse(PlayerSourceRow.objects.exists())
 
@@ -442,6 +530,7 @@ class PlayerImportWorkflowTests(TestCase):
             file_obj=self.upload(body=b"Last\nMissingFirst\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         result = commit_import_batch(import_batch=batch, actor=self.staff, resolutions={"2": {"action": ACTION_SKIP}})
@@ -458,6 +547,7 @@ class PlayerImportWorkflowTests(TestCase):
             file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         result = commit_import_batch(
@@ -477,9 +567,10 @@ class PlayerImportWorkflowTests(TestCase):
         Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
         Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,Birth Year,Division\nEugene,Lin,2012,13U\n"),
+            file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         result = commit_import_batch(
@@ -492,7 +583,7 @@ class PlayerImportWorkflowTests(TestCase):
         self.assertEqual(Player.objects.count(), 3)
 
     def test_commit_prevents_double_commit(self):
-        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff)
+        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
         commit_import_batch(import_batch=batch, actor=self.staff)
 
         with self.assertRaises(ValidationError):
@@ -500,9 +591,10 @@ class PlayerImportWorkflowTests(TestCase):
 
     def test_commit_without_provisioning_leaves_account_models_unchanged(self):
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB\nEugene,Lin,2012-05-01\n"),
+            file_obj=self.upload(body=b"First,Last,DOB,Division,Team\nEugene,Lin,2012-05-01,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
+            season=self.season,
         )
 
         commit_import_batch(import_batch=batch, actor=self.staff)
@@ -513,10 +605,11 @@ class PlayerImportWorkflowTests(TestCase):
 
     def test_commit_with_provisioning_creates_eligible_account_and_safe_summary(self):
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Email\nEugene,Lin,2012-05-01,eugene@example.com\n"),
+            file_obj=self.upload(body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             provision_player_accounts=True,
+            season=self.season,
         )
         mapping = dict(batch.mapping_config)
         mapping["account_email"] = "Email"
@@ -538,10 +631,11 @@ class PlayerImportWorkflowTests(TestCase):
 
     def test_commit_with_provisioning_skips_missing_birthdate_without_rollback(self):
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last\nEugene,Lin\n"),
+            file_obj=self.upload(body=b"First,Last,Division,Team\nEugene,Lin,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             provision_player_accounts=True,
+            season=self.season,
         )
 
         commit_import_batch(import_batch=batch, actor=self.staff)
@@ -554,10 +648,11 @@ class PlayerImportWorkflowTests(TestCase):
     def test_commit_with_provisioning_reports_duplicate_unrelated_email_conflict(self):
         User.objects.create_user(username="existing", email="eugene@example.com")
         batch = create_import_batch(
-            file_obj=self.upload(body=b"First,Last,DOB,Email\nEugene,Lin,2012-05-01,eugene@example.com\n"),
+            file_obj=self.upload(body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"),
             source=SOURCE_MEMBER_LIST,
             uploaded_by=self.staff,
             provision_player_accounts=True,
+            season=self.season,
         )
         mapping = dict(batch.mapping_config)
         mapping["account_email"] = "Email"

```
