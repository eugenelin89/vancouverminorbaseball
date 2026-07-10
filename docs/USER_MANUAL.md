# VCB Platform User Manual

This manual explains how the VCB platform is used by coaches, evaluators, players, and administrators.

The platform helps Vancouver Community Baseball manage player information, coach assessments, analytics, draft preparation, and account access.

## Who This Manual Is For

This manual is for:

- coaches
- evaluators
- coordinators
- administrators
- players with platform accounts

It is not a technical setup guide.

## What The Platform Does

The current platform supports:

- player records
- player CSV imports
- coach assessment forms
- staff review of submitted assessments
- player search
- player profile pages
- player timelines
- simple player comparison
- Analytics Command Center summaries
- draft context from submitted assessments
- draft room workflows
- account login and password change
- staff Account Operations for managing user accounts

Some future features are not available yet, including full player portals, parent portals, coach portals, email invitations, and password reset emails.

## User Types

### Administrators And Staff

Administrators and staff can access staff-only areas such as Analytics, imports, player search, review pages, reporting summaries, draft workflows, and Account Operations.

Staff/admin access is controlled by Django account permissions. Staff-only Account Operations pages require `User.is_staff` or `User.is_superuser`.

The platform account role is separate from Django staff access. For example, `AccountProfile.role = staff` is metadata and does not grant staff-only page access by itself. If you cannot access a staff page, ask a site administrator to check your Django staff or superuser permissions.

### Coaches And Evaluators

Authenticated coaches, players, staff, and guest evaluators can submit assessments for players they know.

The system records:

- who submitted the assessment
- the evaluator role stored on the account
- the player being evaluated
- the assessment cycle
- the submitted ratings and notes

A player can be evaluated by multiple coaches or evaluators.

### Players

Players may have login accounts, especially when accounts are provisioned from player imports.

In the current version, players have a basic account profile page. A full player portal is not available yet.

## Signing In

Use the account login page:

```text
/accounts/login/
```

After signing in:

- staff/admin users are sent to Analytics
- non-staff users are sent to their account profile page
- users who must change their password are sent to the password-change page first

## First Login And Password Change

Some accounts are created from player imports.

When a player account is created from an import:

- the account is activated immediately
- the temporary password is based on the player's birthdate, if available
- the user must change the password before using normal platform pages

The password-change page is:

```text
/accounts/password/
```

After the password is changed, the user can continue to the appropriate landing page.

## Account Profile

The basic account profile page is:

```text
/accounts/profile/
```

It shows basic account information such as:

- username
- email, if available
- account role
- linked players, if any

This page is intentionally simple. It is not a player portal.

## Account Operations

Staff can manage platform user accounts from Account Operations:

```text
/accounts/
```

The Account Operations dashboard gives staff a production view of account status, including account totals, active and inactive accounts, imported accounts, accounts requiring password changes, players without accounts, and users without player links.

Staff Account Operations includes:

- account search, list, and detail pages
- account-only creation for coaches, parents, guest evaluators, staff-role metadata users, and other non-player accounts
- player account creation from an existing player record
- coach account import from CSV
- account activation and deactivation
- username, email, and platform role editing
- user-player link management
- operational password reset
- bulk account operations for low-risk actions

Account Operations does not create new player identity records. Player accounts are created by finding an existing player, creating a login account, and linking the user to that player.

### Creating Accounts

Staff can create account-only users from:

```text
/accounts/create/
```

Use this for coaches, parents, guest evaluators, staff-role metadata users, or other users who do not need a new player identity.

Staff can create a player login account from an existing player record at:

```text
/accounts/create/player/
```

Use this only when the player already exists in the player database.

Temporary passwords are shown once immediately after account creation. They are not shown again on the account detail page.

### Importing Coach Accounts

Staff can import coach accounts from:

```text
/accounts/imports/coaches/
```

Coach import uses a preview and confirm workflow:

1. Upload a coach CSV file.
2. Review the preview for rows to create, existing coach accounts to reuse, conflicts, and row errors.
3. Confirm the import.
4. Copy temporary passwords from the result page immediately.

Required CSV columns:

- first_name
- last_name
- email

Optional CSV columns:

- username
- team
- division
- is_active
- notes
- source_id

If an imported row uses the email address of an existing coach account, the system reuses that coach account. Confirming the import resets that coach's temporary password, and the coach must change the password on next login.

Temporary passwords are shown only once on the immediate result page. They are not stored on the account detail page or in account metadata.

Coach import creates or reuses coach login accounts only. It does not create player records and does not create coach-to-player links.

### Editing Accounts

Staff can open an account detail page from the account list:

```text
/accounts/users/
```

From account detail, staff can edit:

- username
- email
- platform role
- active/inactive status

Changing `AccountProfile.role` does not change Django `User.is_staff` or `User.is_superuser`. Platform roles help describe account purpose; Django staff/superuser flags control operational access.

### User-Player Links

Staff can manage user-player links from an account detail page.

Supported link relationships include:

- self
- parent
- guardian
- coach
- staff

A parent or guardian account may be linked to multiple players. A player may also be linked to multiple parents or guardians.

Normal unlinking deactivates the link instead of deleting it, so staff can preserve history and reactivate links when needed.

### Password Reset And Forced Password Change

Staff can perform operational password resets from an account detail page.

When a password is reset:

- a temporary password is shown once
- the user is required to change the password at next login
- the temporary password is not stored in account summaries, import data, or account detail pages

Users who must change their password are sent to:

```text
/accounts/password/
```

They cannot use normal platform pages until the password change is complete.

### Bulk Account Operations

Staff can perform selected low-risk bulk actions from the account list, such as:

- activate selected accounts
- deactivate selected accounts
- require selected users to change passwords
- clear password-change requirement for selected users

Bulk operations are intended for routine account maintenance. Staff should review selected accounts carefully before applying a bulk action.

## Analytics Command Center

The Analytics Command Center is the staff starting point:

```text
/analytics/
```

It provides staff with a summary of the Analytics system, including items such as:

- assessment activity
- completion summaries
- import summaries
- draft context summaries
- links to common Analytics workflows

Analytics V1 is staff-only. Coaches or players who are not staff may not be able to access the Command Center.

## Player Search

Staff can search for players from the Analytics player search page:

```text
/analytics/players/
```

Player search is used to find player profiles, review player history, and compare players.

Search and filters may include player details such as:

- name
- division
- team
- draft status
- assessment completion status

## Player Profile

Each player has a staff-facing player profile page.

The player profile is intended to become the main historical view of a player. In the current version it may show:

- player identity details
- imported player context
- submitted coach assessments
- draft context
- player timeline entries

Future versions may add more timeline entries such as measurements, awards, attendance, development milestones, and video analysis.

## Player Timeline

The player timeline gives staff a chronological view of known player history.

In the current version, timeline information focuses on:

- coach assessments
- imported player context
- draft context

The timeline is read-only.

## Player Comparison

Staff can compare selected players:

```text
/analytics/players/compare/
```

The comparison page helps staff view player summaries side by side.

It is intended for decision support only. It does not make final baseball decisions.

## Coach Assessments

Coach assessments replace the earlier spreadsheet-based assessment process.

Assessment pages are available under:

```text
/analytics/assessments/
```

Evaluation submission pages are available under:

```text
/analytics/evaluations/
```

The assessment form uses the active question set for the current assessment cycle. Questions are not hard-coded into the page, so they can evolve over time.

Assessments may include:

- 1-5 ratings
- written notes

When submitting an assessment:

- choose or open the player evaluation
- enter ratings and notes
- save a draft if more work is needed
- submit when finished

Submitted assessments become part of the player's Analytics record.

Players, coaches, staff, and guest evaluators use the evaluation pages to submit evaluations. Staff-only review pages and player result pages are separate workflows.
After submitting, an evaluator can view their own submission.

## Player My Evaluations

Players with an active linked self player record can view submitted evaluations about themselves:

```text
/analytics/my/evaluations/
```

Player-facing evaluation results show evaluator role/category, submitted date, cycle, ratings, and notes. Evaluator names, usernames, and email addresses are hidden from players.

Draft and reopened evaluations are not shown as final feedback. Inactive player links and inactive player records are not shown in normal My Evaluations lists.

## Coach Evaluation Review

Coaches can review submitted evaluations:

```text
/analytics/evaluation-review/
```

Coach review is read-only. It shows submitted evaluations only and does not allow coaches to reopen, edit, or delete submitted evaluations.

Coaches can filter submitted evaluations by:

- player name or player ID
- evaluator
- evaluator role/category
- team
- division
- evaluation cycle
- submitted date range

Coach review shows evaluator names and role/category so coaches can understand who submitted each evaluation. It does not show evaluator email addresses, account metadata, passwords, import metadata, or unrelated account details.

Players, parents, and guest evaluators cannot access the coach review page. Staff review remains a separate workflow.

## Who Can Evaluate A Player

Authenticated coaches, players, staff, and guest evaluators can evaluate any player if they know the player.

The player does not need to be on the evaluator's own team.

This is intentional. It allows coaches, coordinators, staff, and other approved evaluators to contribute observations when they have useful knowledge of a player.

Players cannot evaluate themselves in Evaluation Access V1. Parent accounts do not submit evaluations unless staff gives the user a separate evaluator role.

## Staff Review Of Assessments

Staff can review submitted observations:

```text
/analytics/observations/review/
```

Staff review is used to inspect submitted assessments and reopen them if corrections are needed.

Assessments should not be edited casually after submission. If a correction is needed, staff should use the review workflow.

## Importing Players

Staff can import player records from CSV files:

```text
/analytics/imports/
```

The import workflow is:

1. Upload a CSV file.
2. Choose the source type.
3. Map CSV columns to player fields.
4. Preview the import.
5. Review conflicts or ambiguous matches.
6. Resolve rows by choosing an existing player, creating a new player, or skipping the row.
7. Confirm the import.
8. Review the import result.

The system tries to match imported rows to existing players using identifiers and player details. Staff should carefully review conflicts before confirming.

## Player Import Data

Player imports can include information such as:

- first name
- last name
- preferred name
- birthdate
- birth year
- division
- team
- positions
- bats/throws
- school
- graduation year
- source identifiers

Birthdate is supported and is important for player identity and account provisioning.

## Account Provisioning From Imports

During a player import, staff may choose to provision player accounts.

When account provisioning is enabled:

- eligible imported players can receive Django user accounts
- player accounts are linked to the matching player record
- users are assigned the player role by default
- accounts are activated immediately
- users must change temporary passwords after first login

Accounts are not created when required information is missing, such as birthdate for the temporary-password rule.

## Draft Workflows

The Drafts app is used for live player drafts.

Typical draft workflow:

1. Create a draft room with a year, division, and team list.
2. Import draft players from CSV.
3. Preview and confirm the import.
4. Open the draft room.
5. Assign players to teams.
6. Move players or use the trade desk when needed.
7. Review the audit timeline.
8. Close the draft when complete.

Draft actions are recorded so staff can review what happened.

Analytics can provide read-only draft context from submitted coach assessments, but the draft workflow itself belongs to the Drafts app.

## Decision Support

The platform is a decision-support system.

It helps organize:

- player records
- coach assessments
- observations
- draft context
- reports
- historical player information

It does not replace the judgment of coaches, evaluators, coordinators, or administrators.

Final baseball decisions remain the responsibility of people.

## Privacy And Care With Player Information

The platform contains youth player information.

Users should:

- use only their own account
- avoid sharing passwords
- enter accurate assessment information
- write notes professionally
- avoid including unnecessary sensitive information in freeform notes
- report incorrect player records to staff

Staff should review imports carefully before confirming them.

## What Is Not Available Yet

The following are not part of the current version:

- full player portal
- parent portal
- coach portal
- public self-registration
- email invitations
- password reset emails
- audit dashboard
- video analysis
- AI-generated summaries
- advanced measurement tracking

These may be added in future versions.

## Common Questions

### Can more than one coach evaluate the same player?

Yes. Multiple evaluators can submit assessments for the same player.

### Can I evaluate a player who is not on my team?

Yes, if your account has an evaluator role and you know the player well enough to provide a useful evaluation. Players cannot evaluate themselves.

### Is my role recorded when I submit an evaluation?

Yes. The system records the evaluator and role information for reporting and historical context.

### Can players log in?

Players can have accounts, especially if staff provisions accounts from imports. The current player-facing experience is limited to basic account access.

### Can players see their full Analytics profile?

Not yet. The player portal is a future feature.

### Where should staff begin?

Staff should usually begin at:

```text
/analytics/
```

### Where should users sign in?

Users should sign in at:

```text
/accounts/login/
```
