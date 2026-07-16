# VCB Platform User Manual

This manual explains how administrators, coordinators, staff, coaches, evaluators, and players use the VCB platform.

The platform helps Vancouver Community Baseball manage:

- player records
- account access
- player and coach imports
- season and roster operations
- evaluations
- player history
- draft preparation
- draft room workflows

This is a user manual, not a technical deployment guide. Deployment information lives in [docs/deployment/](deployment/README.md).

Season-aware roster operations now exist in the system. Staff can manage seasons, teams, player roster memberships, transfers, coach assignments, and season history without using Django admin. Player imports, coach imports, and evaluations are season-aware: staff choose an active season for imports, imported team/division information creates roster participation records or coach assignments, and submitted evaluations preserve the season/team/division context that existed when the evaluation was submitted.

## Start Here

### Sign In

Use:

```text
/accounts/login/
```

After signing in:

- staff and administrators usually land in Analytics;
- non-staff users land on their account profile;
- users who must change their password are sent to `/accounts/password/` first.

### Key Terms

User-facing pages use the word **evaluation**.

Some older pages and internal records may still use **assessment** or **observation**:

- an evaluation is the form a coach, player, staff member, or guest evaluator submits;
- a coach assessment is the current evaluation form and question set;
- an observation is the internal Analytics record created by an evaluation.

In normal use, think of these as evaluations.

### Access Levels

- **Players** can submit evaluations, view their own submitted drafts/final submissions, and view submitted evaluations about themselves when linked to their player record.
- **Coaches** can submit evaluations and review submitted evaluations.
- **Staff** can manage Analytics workflows, player imports, account operations, draft workflows, and staff review.
- **Administrators** have staff access plus responsibility for account permissions and operational oversight.

Platform roles such as `coach`, `player`, or `staff` describe the account. Staff-only page access depends on Django staff/superuser permissions, not the platform role alone.

## Administrator Quick Start

### Purpose

Use this section when you are responsible for account access, operational setup, or platform oversight.

### Where To Log In

```text
/accounts/login/
```

### Where To Begin

- Account Operations: `/accounts/`
- Analytics Command Center: `/analytics/`
- Django admin, if needed: `/admin/`

### Typical Daily Workflow

1. Open Account Operations.
2. Review accounts requiring password change and users without player links.
3. Create or update staff, coach, parent, guest evaluator, or player accounts.
4. Import coach accounts when onboarding a roster.
5. Open Season Operations to create seasons, teams, roster memberships, and coach assignments.
6. Confirm staff-only access is controlled by Django staff/superuser permissions.
7. Use Analytics to confirm imports, evaluations, and review workflows are healthy.

### Pages Normally Used

- `/accounts/`
- `/accounts/users/`
- `/accounts/create/`
- `/accounts/create/player/`
- `/accounts/imports/coaches/`
- `/seasons/`
- `/analytics/`
- `/admin/`

## Staff Quick Start

### Purpose

Use this section when you help run baseball operations, imports, evaluations, draft prep, or review workflows.

### Where To Log In

```text
/accounts/login/
```

### Where To Begin

Start at:

```text
/analytics/
```

### Typical Daily Workflow

1. Open the Analytics Command Center.
2. Review evaluation activity, import summaries, and completion status.
3. Search for players from `/analytics/players/`.
4. Import or update players from `/analytics/imports/`.
5. Use `/seasons/` to review or correct season teams, roster memberships, transfers, and coach assignments.
6. Review submitted evaluations from `/analytics/observations/review/`.
7. Compare players or review player profiles when preparing decisions.
8. Use Account Operations if users need access help.

### Pages Normally Used

- `/analytics/`
- `/analytics/players/`
- `/analytics/players/compare/`
- `/analytics/imports/`
- `/analytics/observations/review/`
- `/analytics/evaluation-review/`
- `/seasons/`
- `/accounts/`
- `/drafts/`

## Coach Quick Start

### Purpose

Use this section when you need to evaluate players or review submitted evaluations.

### Where To Log In

```text
/accounts/login/
```

If your account was imported or reset, you may need to change your password before continuing.

### Where To Begin

- Submit evaluations: `/analytics/evaluations/`
- Review submitted evaluations: `/analytics/evaluation-review/`

### Typical Daily Workflow

1. Open the evaluation list.
2. Search or filter for a player.
3. Open the player evaluation.
4. Enter ratings and notes.
5. Save a draft if you are not finished.
6. Submit when complete.
7. Use evaluation review to read submitted evaluations when needed.

### Pages Normally Used

- `/analytics/evaluations/`
- `/analytics/evaluation-review/`
- `/accounts/profile/`
- `/accounts/password/`

## Player Quick Start

### Purpose

Use this section when you have a player account and need to submit peer or self evaluations, or view evaluations about yourself.

### Where To Log In

```text
/accounts/login/
```

If this is your first login, change your temporary password when prompted.

### Where To Begin

- Submit evaluations: `/analytics/evaluations/`
- View your evaluations: `/analytics/my/evaluations/`
- View your account: `/accounts/profile/`

### Typical Daily Workflow

1. Sign in.
2. Change your password if required.
3. Submit evaluations for players you know, including yourself when appropriate.
4. View submitted evaluations about yourself from My Evaluations.
5. Sign out when finished.

### Pages Normally Used

- `/analytics/evaluations/`
- `/analytics/my/evaluations/`
- `/accounts/profile/`
- `/accounts/password/`

Player self-evaluations are allowed and are clearly labeled as Self Evaluation.

## Account Access

### Purpose

Account access controls who can sign in and what each user can do.

### Who Uses It

- all users sign in and manage their own password;
- staff and administrators manage other users through Account Operations.

### Typical Workflow

1. Sign in at `/accounts/login/`.
2. Change password if required.
3. Use the landing page for your role.
4. Staff use Account Operations for user support.

### Related Pages

- `/accounts/login/`
- `/accounts/logout/`
- `/accounts/password/`
- `/accounts/profile/`
- `/accounts/`

### First Login And Password Changes

Some accounts are created by staff or through imports. These users must change their password before using normal platform pages.

The password-change page is:

```text
/accounts/password/
```

Temporary passwords are shown only once when staff creates, imports, or resets an account. If the temporary password is lost, staff must reset it.

### Account Profile

The account profile page is:

```text
/accounts/profile/
```

It shows basic account information:

- username
- email, if available
- account role
- linked players, if any

This page is intentionally simple. It is not a full player, parent, or coach portal.

## Account Operations

### Purpose

Account Operations lets staff manage user accounts without using Django admin for routine work.

### Who Uses It

Staff and administrators with Django staff/superuser access.

### Typical Workflow

1. Open `/accounts/`.
2. Review summary cards and issue lists.
3. Search users from `/accounts/users/`.
4. Create accounts or player accounts.
5. Edit usernames, emails, roles, and active status.
6. Manage player links.
7. Reset passwords when needed.

### Related Pages

- `/accounts/`
- `/accounts/users/`
- `/accounts/create/`
- `/accounts/create/player/`
- `/accounts/imports/coaches/`
- `/accounts/users/<id>/`
- `/accounts/users/<id>/edit/`
- `/accounts/users/<id>/links/`
- `/accounts/users/<id>/password/`

### What Staff Can Do

Staff Account Operations includes:

- account search, list, and detail pages;
- account-only creation for coaches, parents, guest evaluators, staff-role metadata users, and other non-player accounts;
- player account creation from an existing player record;
- coach account import from CSV;
- account activation and deactivation;
- username, email, and platform role editing;
- user-player link management;
- operational password reset;
- low-risk bulk account actions.

Account Operations does not create player identity records. Player accounts are created by finding an existing player, creating a login account, and linking that user to the player.

### Coach Import

Staff can import coach accounts from:

```text
/accounts/imports/coaches/
```

Required CSV columns:

- `first_name`
- `last_name`
- `email`

Optional CSV columns:

- `username`
- `team`
- `division`
- `is_active`
- `notes`
- `source_id`
- `assignment_role`
- `assignment_start_date`
- `assignment_end_date`
- `assignment_source_id`

Staff must select an active season when uploading the coach CSV. Team and division are required for the seasonal coach assignment.

Coach import creates or reuses coach login accounts. It does not create player records and does not create coach-to-player links.

New imported coach accounts are active by default and must change password on first login. Returning coach accounts are reused without changing their password or activation status.

### User-Player Links

Staff can link users to players from an account detail page.

Supported relationships:

- self
- parent
- guardian
- coach
- staff

A parent or guardian may link to multiple players. A player may have multiple parents or guardians. Normal unlinking deactivates the link instead of deleting it so history is preserved.

## Season Operations

### Purpose

Season Operations lets staff manage season-aware roster context without using Django admin.

### Who Uses It

Staff and administrators with Django staff/superuser access.

Seasonal assignments do not grant access by themselves. A coach assignment records baseball context for a season and team; it does not make the user a Django staff member or superuser.

### Typical Workflow

1. Open `/seasons/`.
2. Create or edit the season.
3. Set the current season explicitly when the organization is ready.
4. Create season-specific teams.
5. Create or correct player roster memberships.
6. Use transfer/additional-membership actions when a player changes teams or plays on multiple teams.
7. Review player season history.
8. Create or correct coach season assignments.
9. Review coach season history.

### Related Pages

- `/seasons/`
- `/seasons/new/`
- `/seasons/<season_id>/`
- `/seasons/teams/`
- `/seasons/memberships/`
- `/seasons/players/<player_id>/history/`
- `/seasons/coach-assignments/`
- `/seasons/coaches/<user_id>/history/`

### Seasons And Current Season

Staff can create and edit seasons. One season can be marked current at a time. Setting the current season is an explicit confirmation action so staff do not accidentally change import and evaluation defaults.

Inactive seasons remain visible for history. Normal operations preserve history instead of deleting records.

### Teams

Teams are scoped to a season. The same team name can exist in different seasons without being treated as the same roster record.

### Player Memberships

Player memberships record a player's roster stint on a season team. Staff can:

- create memberships;
- edit status, dates, jersey number, source, and primary membership;
- end memberships without deleting history;
- transfer a player to another team in the same season;
- add an additional non-primary membership for multi-team participation;
- view the player's season-by-season history.

A player may have multiple memberships in a season, but only one active primary membership per season. Transfers preserve the prior membership as historical context.

### Coach Assignments

Coach assignments record a coach user's season-specific team assignment. Staff can:

- create assignments;
- edit assignment role, dates, primary flag, source, and active state;
- end assignments without deleting history;
- view the coach's season-by-season assignment history.

Coach assignment changes do not reset passwords, change account activation, change platform role, or grant Django staff/superuser access.

## Evaluations

### Purpose

Evaluations collect structured baseball feedback from coaches, players, staff, and guest evaluators.

### Who Uses It

- coaches
- players
- staff
- guest evaluators

Parent accounts do not submit evaluations unless staff gives that user an evaluator role.

### Typical Workflow

1. Open `/analytics/evaluations/`.
2. Search or filter for a player.
3. Open the player's evaluation form.
4. Enter 1-5 ratings and notes.
5. Save a draft if needed.
6. Submit when complete.

### Related Pages

- `/analytics/evaluations/`
- `/analytics/evaluations/players/<player_id>/`
- `/analytics/assessments/`
- `/analytics/assessments/<observation_id>/`

### Evaluation Rules

- Authenticated coaches, players, staff, and guest evaluators can evaluate players they know.
- The player does not need to be on the evaluator's own team.
- Players can evaluate themselves when their account is actively linked to their own player record.
- Self evaluations are labeled Self Evaluation.
- The system records who submitted the evaluation.
- The evaluator's role/category and evaluation type are recorded for reporting and historical context.
- The evaluation cycle determines the season for new evaluations when the cycle has a season.
- The player list uses roster membership for that evaluation season.
- Submitted evaluations preserve the season, team, and division at the time of submission.
- Submitted evaluations become part of the player's Analytics record.

### Ratings And Notes

The current evaluation form uses:

- 1-5 rating questions
- written notes

The active question set can change over time. Questions are not hard-coded into the page.

## My Evaluations

### Purpose

My Evaluations lets players view submitted evaluations about themselves.

### Who Uses It

Players with an active account link to their own player record.

### Typical Workflow

1. Open `/analytics/my/evaluations/`.
2. Choose a linked player if more than one is available.
3. Open an evaluation detail.
4. Review ratings, notes, evaluator role/category, submitted date, and cycle.

### Related Pages

- `/analytics/my/evaluations/`
- `/analytics/my/evaluations/players/<player_id>/`
- `/analytics/my/evaluations/<observation_id>/`

### Privacy Rules

Players can see submitted evaluations about themselves only.

Players do not see evaluator names, usernames, email addresses, or account details. They may see evaluator role/category.

Draft and reopened evaluations are not shown as final feedback.

## Coach Evaluation Review

### Purpose

Coach Evaluation Review lets coaches and staff review submitted evaluations.

### Who Uses It

- coaches
- staff
- administrators

Players, parents, and guest evaluators cannot access the review page.

### Typical Workflow

1. Open `/analytics/evaluation-review/`.
2. Filter by player, evaluator, evaluator role, evaluation type, team, division, cycle, or date.
3. Open an evaluation detail.
4. Use the information for discussion and decision support.

### Related Pages

- `/analytics/evaluation-review/`
- `/analytics/evaluation-review/<observation_id>/`

Coach review is read-only. It shows submitted evaluations only. Coaches cannot reopen, edit, or delete submitted evaluations from this page.

Coach review shows evaluator names, role/category, and evaluation type. It does not show evaluator email addresses, passwords, import metadata, or unrelated account details.

Coach review displays the saved season/team/division from the submitted evaluation. Later roster changes do not rewrite historical evaluation context.

## Staff Analytics

### Purpose

Staff Analytics helps coordinators and administrators manage player records, imports, evaluations, timelines, comparisons, and decision-support summaries.

### Who Uses It

Staff and administrators with Django staff/superuser access.

### Typical Workflow

1. Start at the Analytics Command Center.
2. Review summaries and quick links.
3. Search for players.
4. Open player profiles and timelines.
5. Review imports and submitted evaluations.
6. Compare players when preparing baseball decisions.

### Related Pages

- `/analytics/`
- `/analytics/players/`
- `/analytics/players/<player_id>/`
- `/analytics/players/compare/`
- `/analytics/imports/`
- `/analytics/observations/review/`

### Analytics Command Center

The staff starting point is:

```text
/analytics/
```

It summarizes:

- evaluation activity
- completion status
- import status
- draft context
- common Analytics workflows

### Player Search

Staff can search players from:

```text
/analytics/players/
```

Search and filters may include:

- name
- division
- team
- draft status
- evaluation completion status
- tags or source context where available

### Player Profile And Timeline

Player profile pages are staff-facing.

They may show:

- player identity details
- imported player context
- submitted evaluations
- draft context
- timeline entries

The timeline is read-only.

### Player Comparison

Staff can compare selected players from:

```text
/analytics/players/compare/
```

Comparison is for decision support. It does not make final baseball decisions.

### Staff Review

Staff can review submitted evaluations from:

```text
/analytics/observations/review/
```

This page still uses `observations` in the URL because that is the internal Analytics record name. Staff review is used to inspect submitted evaluations and reopen them if corrections are needed.

Staff review shows saved season and roster context for submitted evaluations. Older legacy records without season context may display as `Legacy / No Season`.

## Player Imports

### Purpose

Player imports let staff create or update canonical player records from CSV files.

### Who Uses It

Staff and administrators.

### Typical Workflow

1. Open `/analytics/imports/`.
2. Upload a CSV file.
3. Choose the active season and source information.
4. Map CSV columns to player fields.
5. Preview the import.
6. Review conflicts or ambiguous matches.
7. Resolve rows by choosing an existing player, creating a new player, or skipping the row.
8. Confirm the import.
9. Review the import result.

### Related Pages

- `/analytics/imports/`
- `/analytics/imports/new/`
- `/analytics/imports/<id>/preview/`
- `/analytics/imports/<id>/conflicts/`
- `/analytics/imports/<id>/confirm/`
- `/analytics/imports/<id>/`

### Supported Player Data

Player imports can include:

- first name
- last name
- preferred name
- birthdate
- birth year
- division
- team
- roster status
- jersey number
- roster start/end dates
- positions
- bats/throws
- school
- graduation year
- source identifiers

Birthdate is supported and is important for player identity and account provisioning.

Season, division, and team are required for the current player import workflow. Division and team are used as roster context for the selected season rather than as permanent player identity.

### Account Provisioning From Player Imports

During a player import, staff may choose to provision player accounts.

When account provisioning is enabled:

- eligible imported players can receive login accounts;
- player accounts are linked to matching player records;
- users are assigned the player role by default;
- accounts are activated immediately;
- users must change temporary passwords after first login.

Accounts are not created when required information is missing, such as birthdate for the temporary-password rule.

## Draft Workflows

### Purpose

Draft workflows help staff run live player drafts.

### Who Uses It

Staff and administrators.

### Typical Workflow

1. Open `/drafts/`.
2. Create or open a draft room.
3. Import draft players from CSV.
4. Preview and confirm the import.
5. Open the draft room.
6. Assign players to teams.
7. Move players or use the trade desk when needed.
8. Review the action timeline.
9. Close the draft when complete.

### Related Pages

- `/drafts/`
- `/drafts/new/`
- `/drafts/<slug>/`
- `/drafts/<slug>/import/`
- `/drafts/<slug>/trade/`
- `/drafts/live/<slug>/`

Draft actions are recorded so staff can review what happened. Analytics may show read-only draft context, but the draft workflow itself belongs to the Drafts app.

## Privacy And Good Use

### Purpose

The platform contains youth player information and should be used carefully.

### Who Uses It

Everyone.

### Typical Workflow

1. Use only your own account.
2. Keep passwords private.
3. Enter accurate information.
4. Write notes professionally.
5. Avoid unnecessary sensitive information in freeform notes.
6. Report incorrect player records to staff.

### Related Pages

- `/accounts/profile/`
- `/analytics/evaluations/`
- `/analytics/my/evaluations/`

Staff should review imports carefully before confirming them.

## Decision Support

The platform organizes player records, evaluations, draft context, reports, and historical information.

It does not replace the judgment of coaches, evaluators, coordinators, or administrators.

Final baseball decisions remain the responsibility of people.

## What Is Not Available Yet

The following are not part of the current version:

- full player portal
- parent portal
- coach portal dashboard
- public self-registration
- email invitations
- password reset emails
- audit dashboard
- video analysis
- AI-generated summaries
- advanced measurement tracking

## FAQ

### Where do I sign in?

Use:

```text
/accounts/login/
```

### I was sent to the password page. What should I do?

Change your temporary password at:

```text
/accounts/password/
```

You must complete this before using normal platform pages.

### Can more than one person evaluate the same player?

Yes. Multiple evaluators can submit evaluations for the same player.

### Can I evaluate a player who is not on my team?

Yes, if your account can submit evaluations and you know the player well enough to provide useful feedback.

### Can I evaluate myself?

Yes. If you have an active player account linked to your own player record, your own submission is labeled Self Evaluation.

### Is my role recorded when I submit an evaluation?

Yes. The system records your evaluator identity, role/category, and evaluation type for reporting and historical context.

### Can players see who evaluated them?

No. Player-facing My Evaluations pages hide evaluator names, usernames, emails, and account details for external evaluations. Players may see evaluator role/category and evaluation type.

### Can coaches see all submitted evaluations?

Coaches can use the read-only coach review page for submitted evaluations:

```text
/analytics/evaluation-review/
```

### Can parents use the platform?

Parent accounts can exist and can be linked to players, but a full parent portal is not available yet.

### What should staff use first?

Staff should usually begin at:

```text
/analytics/
```

### What should administrators use first?

Administrators should usually begin with Account Operations:

```text
/accounts/
```

### Where is deployment or server configuration documented?

Deployment documentation is in:

```text
docs/deployment/
```
