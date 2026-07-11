# 10 Permissions

## Staff

Staff users can review all observations.

Staff/admin users can manage:

- imports
- player matching review
- player tags
- question sets
- reopened submitted observations when needed

## Coaches

Coaches can submit `coach_assessment` observations.

Authenticated coaches may evaluate any player they know well enough to assess.

Coaches may edit their own draft/unsubmitted observations. Staff/admin users control whether submitted observations can be reopened.

Coaches do not manage player tags unless future permissions allow it.

## Player Access

Authenticated player users can submit evaluations for active players. When evaluating their own active self-linked player record, the submission is labeled Self Evaluation. When evaluating another player, the submission is labeled Peer Evaluation.

Players can view submitted evaluations about their own active self-linked player records through the player-facing My Evaluations pages. Player-facing result pages hide evaluator names, usernames, emails, and account metadata for external evaluations.

## Future Parent Access

Future parent portals are supported by the long-term architecture but are not implemented in Version 1.

Future permissions may allow parents to view selected timeline entries, reports, or development feedback. Do not implement those surfaces in Version 1.

## Sensitive Data

Do not expose sensitive fields such as addresses, medical notes, phone numbers, emails, or guardian/contact details to ordinary coach assessment screens unless explicitly needed and permissioned.
