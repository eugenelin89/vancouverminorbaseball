You are working on an existing Django project for vancouverminor.com.

Your task is to design and implement a reusable, production-quality Django app for a Player Development Platform (PDP) for youth baseball.

This app must live inside the existing Django project and must be designed for long-term extensibility.

IMPORTANT:
This is not a one-off spreadsheet importer. It is a long-term player development platform.

The system must support:
- multiple seasons
- multiple evaluations over time
- changing spreadsheet formats
- player / parent / coach access
- future sports-tech integrations
- future AI analysis features
- future mobile app support using the same backend

The goal is to help each player develop into the best baseball player he can become, ideally an elite player over time.

The platform should emphasize:
- player growth
- encouragement
- development opportunities
- long-term progress
- actionable next steps

Where possible:
- present weaknesses as development opportunities
- present strengths as assets to build on

This platform should feel like a premium athlete growth system that motivates players to improve, rather than a system that merely stores evaluation data.

The UI must be as beautiful as the draft app.
It may share a similar visual theme and design system.

AI-generated recommendations should be constructive, specific, age-appropriate, and framed as actionable development opportunities rather than harsh criticism.

------------------------------------------------
HIGH-LEVEL PRODUCT GOAL
------------------------------------------------

Build a Player Development Platform app that allows:

1. Admins to import player evaluation data from spreadsheets
2. Coaches to track player development over the season
3. Players to log in and review their own progress
4. Parents to log in and review their child’s progress
5. The system to track evaluations across multiple seasons
6. The system to track goals, feedback, logs, and growth over time
7. AI to be plugged in later for analysis and recommendations
8. If practical, the platform should already include scaffolding for periodic AI-generated player analysis
9. Coaches should be able to complete end-of-season evaluations and generate player report cards
10. The platform should generate progress snapshots and season comparison views
11. The platform should translate evaluations and logs into development roadmaps
12. The platform should support a drill and development resource library linked to player improvement opportunities

This system should help answer:

- How is this player improving over time?
- What are this player’s strengths?
- What are this player’s key development opportunities?
- What should this player work on next?
- How does this season compare with prior evaluations?
- What does the system suggest as the next improvement priority?
- Is this player progressing toward elite-level performance?
- How did this player develop across the entire season?
- What should appear on this player’s end-of-season report card?
- What should this player focus on this month, this season, and this offseason?
- Which drills or training resources should be assigned based on this player’s needs?

------------------------------------------------
CURRENT SOURCE DATA CONTEXT
------------------------------------------------

The attached workbook is an example of the type of evaluation data the platform must support.

Examples of metrics may include:

- Home to 1st
- Broad Jump
- Lateral Jump
- Shotput
- Bat Speed
- Time to Contact
- Exit Velocity Avg
- Exit Velocity Max
- Velocity Avg
- Velocity Max
- Athletic Stance
- Balance / Stride
- Barrel Level
- Launch Position
- Follow Through
- Readiness
- Athletic Movement
- Body Control
- Direction
- Repeatability
- Command

IMPORTANT:
Future evaluation spreadsheets may have different:

- sheet names
- column names
- categories
- ranking systems
- formats

Do NOT hardcode the system to a specific spreadsheet structure.

------------------------------------------------
CORE DESIGN PRINCIPLE
------------------------------------------------

Separate these concerns:

1. Player identity
2. Evaluation events
3. Flexible metrics
4. Development logs
5. Development goals
6. AI insights
7. End-of-season report cards
8. Progress snapshots
9. Development roadmaps
10. Drill / development resources
11. External performance integrations

------------------------------------------------
AUTHENTICATION REQUIREMENTS
------------------------------------------------

Each player must have an account.

Initial onboarding rules:

Username = lowercase(first_name + last_name)

Example:
Eugene Lin → eugenelin

Initial password = same as username.

Example:
password = eugenelin

If duplicates occur, append numbers.

Examples:
eugenelin
eugenelin2

Players must be able to change password after login.

If practical, prompt users to change password on first login.

Passwords must always use Django’s password hashing.

Never store plaintext passwords.

Provide an admin onboarding report listing:
- player
- generated username
- account creation status
- whether password was reset

For username/password bootstrapping, create a dedicated account provisioning service so the logic is deterministic, testable, and reusable for future imports and onboarding flows.

If duplicate first_name+last_name usernames exist, generate deterministic unique usernames while keeping the result simple for admins to manage.

------------------------------------------------
SUGGESTED DATA MODEL
------------------------------------------------

Use this as a starting point, but inspect the existing project structure first and integrate cleanly with any existing player/user/team/coach models.

Core models should include:

PlayerProfile
Season
EvaluationEvent
EvaluationImport
PlayerEvaluation
PlayerMetric
PlayerDevelopmentLog
DevelopmentGoal
PlayerInsight
AIAnalysisRun
ExternalPerformanceSource
EndOfSeasonReport
EndOfSeasonReportItem
ProgressSnapshot
DevelopmentRoadmap
DevelopmentRoadmapItem
DrillResource
PlayerDrillAssignment

Suggested concepts:

### PlayerProfile
Persistent player identity across seasons

### Season
One baseball season or training period

### EvaluationEvent
Represents one evaluation or assessment event

### EvaluationImport
Tracks workbook upload/import metadata

### PlayerEvaluation
One player’s record for one evaluation event

### PlayerMetric
Flexible metric storage with:
- metric_key
- display_name
- category
- metric_type
- numeric_value
- text_value
- raw_value
- unit
- source_sheet
- source_column

### PlayerDevelopmentLog
In-season notes, feedback, reflections, sessions

### DevelopmentGoal
Tracks goals, target metrics, target outcomes, due dates

### PlayerInsight
Stores AI-generated or system-generated insights

### AIAnalysisRun
Tracks manual or scheduled analysis jobs

### ExternalPerformanceSource
Future-facing external source integrations

------------------------------------------------
END OF SEASON REPORT CARD SYSTEM
------------------------------------------------

At the end of each season, coaches should be able to evaluate each player and generate an end-of-season report card.

Requirements:

Coaches must only evaluate players they are authorized to coach.

The report card must support:
- structured categories
- numeric scores
- rubric ratings
- written feedback

Categories may include:
- hitting
- fielding
- throwing
- pitching
- athleticism
- baseball IQ
- teamwork
- coachability
- effort
- attitude
- leadership
- overall development

Each report card should include:
- player strengths
- development opportunities
- recommended offseason focus
- overall coach comments

Report cards should be linked to:
- player
- season
- coach
- creation date
- update date

Players and parents must be able to view the report card when permissions allow.

The system should support:
- printable report cards
- potential PDF export later
- player-friendly summary view
- parent-friendly report view

Recommended models:

### EndOfSeasonReport
- player
- season
- coach
- summary
- strengths
- development_opportunities
- offseason_focus
- overall_rating
- is_final
- created_at
- updated_at

### EndOfSeasonReportItem
- report
- category
- rating_value
- text_feedback
- display_order

This system must allow future customization of report card templates by season, division, or program.

The end-of-season report card should integrate naturally with:
- evaluation history
- development logs
- goals
- AI insights
so the final report reflects the full season of development.

------------------------------------------------
PROGRESS SNAPSHOTS AND SEASON COMPARISON
------------------------------------------------

Add a Progress Snapshot and Season Comparison system.

This feature should automatically generate clear summary cards showing:
- what improved
- what stayed flat
- what regressed if relevant
- what should be prioritized next
- best historical values
- latest values
- change since previous evaluation
- season-over-season comparison when possible

Examples of snapshot moments:
- Start of Season
- Mid-Season
- End of Season
- Year-over-Year

Each snapshot should summarize:
- top strengths
- biggest gains
- biggest remaining opportunities
- key metrics changed
- coach summary
- AI summary if enabled

Recommended model:

### ProgressSnapshot
- player
- season nullable
- evaluation_event nullable
- snapshot_type
    - start_of_season
    - mid_season
    - end_of_season
    - year_over_year
    - custom
- title
- summary
- strengths
- improvement_areas
- metric_summary_data (JSONField)
- source_data_snapshot (JSONField)
- generated_by_type
    - system
    - ai
    - coach
- created_at
- updated_at

This feature should be visible on player dashboards and season summary views.

------------------------------------------------
DEVELOPMENT ROADMAP ENGINE
------------------------------------------------

Add a Development Roadmap feature that translates evaluations, logs, goals, report cards, and AI insights into an actionable improvement plan.

The roadmap should identify:
- current strengths
- top development priorities
- short-term focus
- medium-term focus
- offseason focus
- recommended next steps
- linked goals
- linked drills/resources

The roadmap should feel like a structured player improvement plan, not just notes.

Examples:
- top 3 development priorities
- recommended monthly focus
- seasonal milestones
- offseason action plan

Recommended models:

### DevelopmentRoadmap
- player
- season nullable
- generated_by_type
    - system
    - ai
    - coach
- title
- summary
- is_current
- created_at
- updated_at

### DevelopmentRoadmapItem
- roadmap
- priority_level
- category
- title
- description
- target_metric_key nullable
- target_value nullable
- timeframe
    - short_term
    - mid_term
    - long_term
    - offseason
- linked_goal nullable
- linked_drill_resource nullable
- created_at
- updated_at

This roadmap should appear on the player dashboard and coach dashboard.

------------------------------------------------
DRILL AND DEVELOPMENT RESOURCE LIBRARY
------------------------------------------------

Add a Drill and Development Resource Library.

This library should store:
- drills
- exercises
- routines
- cues
- coaching notes
- development resources
- optional video links later
- skill tags

Resources should be linkable to:
- development goals
- roadmap items
- weaknesses
- report card recommendations
- AI improvement opportunities

Examples:
- throwing accuracy drill
- bat speed routine
- mobility exercise
- balance drill
- pitching direction cue

Recommended models:

### DrillResource
- title
- category
- skill_tags
- description
- coaching_points
- recommended_for
- difficulty_level
- media_url nullable
- is_active
- created_at
- updated_at

### PlayerDrillAssignment
- player
- season nullable
- drill_resource
- assigned_by
- source_type
    - coach
    - ai
    - roadmap
    - report_card
- notes
- status
- created_at
- updated_at

The UI should let coaches connect drills/resources directly to player goals and roadmap items.

------------------------------------------------
IMPORT ARCHITECTURE REQUIREMENTS
------------------------------------------------

The import system must be flexible.

Future spreadsheets may differ in:
- sheet names
- column names
- number of columns
- data types
- categories
- ranking structures

Build a flexible import layer with:
1. upload workbook
2. detect sheets
3. preview columns
4. allow mapping columns to:
   - player identity fields
   - metric fields
   - category labels
   - summary fields
   - ranking fields
5. preserve raw row data
6. import into flexible normalized structures

Support:
- .xlsx import
- multi-sheet workbooks
- merging metrics from multiple sheets into one evaluation event
- partially mapped imports
- unmapped field preservation in JSON
- row-level error reporting
- reusable mapping templates for future spreadsheet formats

Use a service/adaptor architecture:
- workbook parser
- sheet parser
- row normalizer
- player matcher
- metric inference helper
- import mapping config
- import execution service

Do NOT require every metric to be predefined in code.

------------------------------------------------
PLAYER MATCHING REQUIREMENTS
------------------------------------------------

Be careful with player matching.

Support safe matching to an existing player profile using:
- full name
- email if available
- internal player ID if available later
- manual review if ambiguous

Do not silently merge the wrong player.

Provide an unmatched / ambiguous review workflow.

------------------------------------------------
SEASONAL DEVELOPMENT FEATURES
------------------------------------------------

During the season the platform should support:
- practice notes
- game feedback
- bullpen notes
- hitting development logs
- fielding logs
- pitching logs
- strength training notes
- player reflections
- development goals
- parent notes if enabled
- end-of-season evaluations
- final report cards
- offseason development recommendations

The system should make it easy to see:
- latest development notes
- active goals
- completed goals
- evaluation history
- recent improvements
- ongoing development opportunities
- trend charts
- AI-generated recommendations if enabled
- current roadmap items
- assigned drills/resources

------------------------------------------------
AI INTEGRATION
------------------------------------------------

The architecture must allow AI to plug in easily.

AI should be able to:
- summarize evaluations
- identify strengths
- identify improvement opportunities
- compare seasons
- generate development recommendations
- generate encouraging summaries
- generate offseason focus suggestions
- help create progress snapshots
- help generate roadmap items
- help draft coach-facing or player-facing summaries
- assist with end-of-season report language if enabled

AI integration should use a service layer so the provider can change later.

Example services:
- collect_player_analysis_context()
- generate_player_summary()
- generate_improvement_opportunities()
- generate_trend_analysis()
- generate_progress_snapshot()
- generate_development_roadmap()
- persist_generated_insights()

AI output should be stored in database records.

If practical, include scaffolding for:
- post-import analysis
- periodic scheduled analysis
- manual “Generate AI Insight” action
- player-facing improvement opportunity cards

The AI integration must be optional.
The system should work even before a real AI provider is connected.

------------------------------------------------
PLAYER EXPERIENCE
------------------------------------------------

Players should be able to log in and view:
- their development dashboard
- evaluation history
- strengths
- improvement opportunities
- development logs
- goals
- coach feedback
- end-of-season report cards
- progress snapshots
- current development roadmap
- assigned drills/resources
- AI recommendations if enabled

The experience should feel motivating and constructive.

The language should be player-friendly and encouraging.

------------------------------------------------
USER ROLES
------------------------------------------------

### Admin
- manage imports
- manage seasons
- manage evaluations
- manage report cards
- manage drill library
- run AI analysis
- manage permissions

### Coach
- view players they coach
- add development logs
- create goals
- complete report cards
- assign drills/resources
- review snapshots
- update roadmap items if allowed

### Player
- view their progress
- view report cards
- view goals
- view coach feedback
- view roadmap
- view assigned drills/resources
- view snapshots
- change password after login

### Parent
- view their child’s progress
- view report cards
- view goals
- view roadmap
- view snapshots
- view assigned development resources if allowed

------------------------------------------------
KEY PAGES
------------------------------------------------

Build polished, premium UI pages for:

1. Player Development Dashboard
   - player header
   - current season summary
   - strengths
   - development opportunities
   - active goals
   - recent coach notes
   - AI insights
   - current roadmap
   - assigned drills/resources
   - recent snapshots

2. Evaluation History Page
   - grouped metrics by category
   - compare evaluations over time
   - raw and normalized values where appropriate

3. Development Log Timeline
   - filter by type
   - add new entries
   - visibility controls

4. Goals Page
   - active goals
   - completed goals
   - progress status
   - target dates

5. Coach Dashboard
   - players coached
   - players needing follow-up
   - missing report cards
   - players with new evaluations
   - flagged development priorities

6. Parent View
   - child overview
   - goals
   - evaluations
   - snapshots
   - report cards

7. Admin Import Tool
   - upload workbook
   - sheet preview
   - mapping
   - import results
   - unmatched player review
   - saved templates

8. AI Insights Panel
   - summaries
   - recommendations
   - analysis history

9. End-of-Season Report Card Page
   - coach form
   - completed report view
   - printable version

10. Progress Snapshot Page
   - snapshot cards
   - comparison cards
   - year-over-year summaries

11. Development Roadmap Page
   - top priorities
   - linked goals
   - linked drills/resources
   - current and previous roadmap versions

12. Drill / Resource Library
   - searchable library
   - category filter
   - tags
   - assign to player

------------------------------------------------
VISUALIZATION
------------------------------------------------

Charts should support metric trends such as:
- velocity over time
- exit velocity over time
- bat speed over time
- home-to-first time

Display:
- latest value
- previous value
- change
- best historical value
- trend direction
- season summary

The UI should make it easy to understand progress at a glance.

------------------------------------------------
FUTURE INTEGRATIONS
------------------------------------------------

Architecture must support:
- radar guns
- biomechanics sensors
- motion capture
- video analysis
- mobile apps
- external APIs

Create clean extension points for:
- source tracking
- payload storage
- measurement timestamps
- source-specific services

------------------------------------------------
MOBILE / API READINESS
------------------------------------------------

Design the system so future mobile app features can use the same backend.

Where practical:
- keep business logic in services
- keep models clean
- structure views so future API support is straightforward
- do not tightly couple core logic to templates only

------------------------------------------------
UI / UX REQUIREMENTS
------------------------------------------------

The UI must be as beautiful as the draft app.

Use a premium sports-performance aesthetic:
- elegant cards
- polished spacing
- clean typography
- subtle shadows
- tasteful charts
- clear status badges
- motivating athlete dashboard feel

This should look like a top-tier athlete development platform, not a spreadsheet portal.

Works well on:
- desktop
- tablet
- mobile

------------------------------------------------
TECHNICAL REQUIREMENTS
------------------------------------------------

Use Django best practices.

Include:
- models
- migrations
- admin integration
- views
- forms
- urls
- templates
- services
- tests
- documentation

Keep business logic out of templates.

Use service-layer logic for:
- workbook import
- player matching
- account provisioning
- username generation
- initial password bootstrapping
- evaluation creation
- metric normalization
- development summary generation
- progress snapshot generation
- roadmap generation
- drill assignment
- report card generation
- AI insight generation
- permission helpers

Use HTMX or lightweight JavaScript where it improves UX, but do not overengineer the frontend.

------------------------------------------------
IMPLEMENTATION PRIORITIES
------------------------------------------------

Build the full system in one implementation pass, but structure it cleanly.

Priority order:
1. core models
2. flexible spreadsheet importer
3. account provisioning
4. permissions
5. evaluation history and dashboards
6. development logs and goals
7. end-of-season report cards
8. progress snapshots
9. development roadmap engine
10. drill/resource library
11. AI insight scaffolding

------------------------------------------------
DELIVERABLES
------------------------------------------------

Provide:
1. architecture proposal first
2. model design
3. import strategy
4. account provisioning strategy
5. AI integration strategy
6. full implementation
7. all files created/modified
8. migrations
9. templates
10. views
11. forms
12. services
13. tests
14. documentation for setup and use

------------------------------------------------
NICE-TO-HAVE FEATURES
------------------------------------------------

If feasible, also include:
- trend arrows
- printable player report
- exportable player progress report
- season-over-season comparison
- mapping templates for future spreadsheet imports
- goal completion workflow
- coach comment tagging by skill area
- category color coding
- manual “Generate AI Insight” button
- scheduled AI insight generation hooks
- dashboard cards for top development opportunities
- ability for player to acknowledge or reflect on improvement suggestions
- first-login password change prompt
- admin onboarding credentials export/report
- customizable end-of-season report card templates
- AI-assisted first draft of coach report comments

------------------------------------------------
CONSTRAINTS
------------------------------------------------

Do not build a throwaway prototype.

Build a reusable, extensible platform for long-term player development.

Prioritize:
- flexibility
- maintainability
- correct permissions
- strong import architecture
- motivating user experience
- beautiful UI
- future AI extensibility
- future sports-tech extensibility