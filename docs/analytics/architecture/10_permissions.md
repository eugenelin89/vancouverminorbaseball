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

## Future Player And Parent Access

Future player and parent portals are supported by the long-term architecture but are not implemented in Version 1.

Future permissions may allow players or parents to view selected timeline entries, reports, or development feedback. Do not implement those surfaces in Version 1.

## Sensitive Data

Do not expose sensitive fields such as addresses, medical notes, phone numbers, emails, or guardian/contact details to ordinary coach assessment screens unless explicitly needed and permissioned.
