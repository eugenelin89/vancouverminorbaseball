# 05 Coach Assessments

## Workflow

Build the first workflow around coach-submitted observations with:

```text
Observation.observation_type = "coach_assessment"
```

Multiple coaches can evaluate the same player in the same evaluation cycle.

Each evaluator should be able to submit at most one coach-assessment observation for the same player in the same evaluation cycle, but a player may have observations from many evaluators.

Players are most likely to be evaluated by their own coaches, but the app should allow any authenticated coach to evaluate any player if they know the player well enough to provide useful feedback.

## Rubric

Version 1 uses this 1-5 scoring rubric:

- `1`: 0/5 times, Never
- `2`: 1-2/5 times, Infrequently
- `3`: 2.5/5 times, Half the time
- `4`: 4/5 times, Frequently
- `5`: 5/5 times, Always

Version 1 only needs numeric 1-5 rating responses plus freeform notes/text responses.

## Coach Assessment Observation Fields

Each coach-assessment observation should include:

- player reference
- evaluator/user who submitted the observation
- evaluator role snapshot
- evaluation cycle
- observation status
- configured question responses
- freeform notes

## Default Question Set

The initial coach assessment question set should use the current 1-5 rubric.

### Throw

- Throws accurately
- Throws with velocity
- Ability to throw from outfield to infield in the air or on one hop
- Can throw accurately across the diamond from 3rd to 1st

### Field

- Can catch routine balls at 1st base
- Can catch non-routine balls at 1st base
- Ability to catch a routine grounder
- Ability to catch a non-routine grounder
- Ability to catch a routine fly ball
- Ability to catch a non-routine fly ball

### Hitting

- Hits barrels
- Player can sacrifice bunt
- Player chooses strikes to swing at
- Gets on base
- Hits for power

### Pitching

- Throws strikes
- Can hold runners
- Has good velocity
- Has an off-speed pitch

### Catching

- Likes to catch
- Can throw to 2nd accurately
- Can block

### Hustle

- Always focused
- Checks in/attends regularly
- Listens to coach feedback

### Notes

- Freeform coach notes

## Review Workflow

Staff users can review all observations.

Coaches may edit their own draft/unsubmitted observations. Staff/admin users control whether submitted observations can be reopened.

## Question Versioning

Question configuration is canonical in [03 Analytics](03_analytics.md). Coach assessment implementation should consume question sets rather than hard-coding question text in templates.
