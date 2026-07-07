You are working inside an existing Django project named `vancouverminor`.

Current project constraints:
- Django 4.2
- Server-rendered templates
- Plain HTML/CSS, no frontend build step
- SQLite in development
- Existing apps follow standard Django patterns with `models.py`, `views.py`, `forms.py`, `urls.py`, app templates, and admin registration
- Use Django's built-in authentication system
- Keep implementation consistent with the current codebase structure and style

Your task is to design and implement a new Django app for:

Vancouver Community Baseball
18U Graduating Player Scholarship Program

This app should support an annual scholarship application process for graduating 18U players.

Core product requirements

1. Annual scholarship cycle
- The scholarship application happens annually.
- Create a model representing an annual application cycle, for example `ScholarshipCycle`.
- Each cycle should support:
  - title
  - year
  - slug
  - status (`draft`, `open`, `closed`, `archived`)
  - application open date
  - application deadline
  - optional review notes / admin notes
  - optional public announcement text
- Only open cycles should accept submissions.
- A player may submit only one application per cycle unless admins explicitly reopen/edit it.

2. Applicant accounts
- Applicants must be able to create their own account.
- Do not require email verification.
- Assume the email entered is correct.
- Use Django's built-in `User` model unless there is a strong reason not to.
- Provide:
  - sign up
  - login
  - logout
  - password reset can be omitted for now unless already easy to support
- On sign up:
  - collect email, password, first name, last name
  - create the account immediately
  - log the user in after registration if practical
- Email should be unique for applicant login purposes.

3. Scholarship application workflow
- Authenticated applicants should be able to:
  - view the currently open scholarship cycle
  - start an application
  - save as draft
  - return later to edit before deadline
  - submit final application
  - view submitted application in read-only form after submission unless the cycle is reopened by admin
- Admin/staff users should be able to:
  - create and manage annual cycles
  - view all applications
  - filter by cycle and submission status
  - review applications in Django admin at minimum
- Admin/staff users must be able to review applications easily without digging through raw records.
- Provide a clear admin workflow for browsing applications by year, by applicant, and by status.
- Admin/staff users must be able to download application records for each applicant and for each scholarship year.
- Prefer a professional export format such as print-friendly HTML and/or PDF-ready output. CSV export may be included as a secondary option, but the primary admin review/download format should preserve the application structure and readability.
- Build the app so future admin review screens can be added cleanly.

4. Data modeling
Implement a clean, extensible model structure. Suggested models:

- `ScholarshipCycle`
  - annual application cycle metadata

- `ScholarshipApplicantProfile`
  - one-to-one with Django `User`
  - first_name
  - last_name
  - full_name
  - email
  - phone optional
  - created_at / updated_at

- `ScholarshipApplication`
  - applicant
  - cycle
  - status (`draft`, `submitted`, `under_review`, `awarded`, `not_selected`, `withdrawn`)
  - submitted_at
  - locked_at
  - all application content fields
  - declarations / consent booleans
  - optional internal review fields
  - timestamps

- `ScholarshipReference`
  - application foreign key
  - display order
  - name
  - relationship / role
  - email
  - phone optional

- Optional future-ready models if useful but do not overbuild:
  - `ScholarshipAttachment`
  - `ScholarshipReview`

5. Exact application content
The application form must include the following sections and fields.

Section A: Applicant Information
- player_full_name
- date_of_birth
- vcb_team_or_program
- primary_positions
- years_participated_in_vcb_programs

Section B: Post-Graduation Plans
Checkboxes, multi-select:
- college_university
- trade_vocational_training
- recognized_training_or_development_program
- undecided

Additional fields:
- institution_or_program_name
- intended_field_of_study_or_training

Section C: Applicant Statement
A written statement, approximately 300–500 words, covering:
- experience in growth and development during time with VCB
- leadership, character, and sportsmanship
- commitment to athletics, academics, and/or personal development
- community involvement or service
- why the applicant exemplifies the values of Vancouver Community Baseball

Store as:
- nomination_statement

Section D: References
Allow one required reference and one optional second reference.
Both references must be non-family adults.

Reference 1 required:
- name
- role_relationship
- email
- phone optional

Reference 2 optional:
- name
- role_relationship
- email
- phone optional

Section E: Declarations & Consent
Required checkboxes:
- applicant confirms information is accurate
- applicant confirms they are a graduating 18U player in good standing with Vancouver Community Baseball
- applicant understands scholarship decisions are final and not subject to appeal

Also include:
- nominator_signature
- signature_date

Note:
Even though the original document says "nominator," this is an applicant-facing application flow. Preserve the field label if requested in the UI, but structure the product coherently for self-submission by the applicant.

6. Eligibility and program messaging
In the applicant-facing pages, reflect this program summary:

Program overview:
The Vancouver Community Baseball 18U Graduating Player Scholarship Program recognizes graduating 18U players who exemplify excellence both on and off the field. It is values-based and focused on impact, growth, leadership, character, commitment, and community involvement, not athletic statistics alone.

Eligibility:
Applicants must:
- be a graduating 18U player in good standing with Vancouver Community Baseball
- have participated in VCB programs during their 18U season
- be pursuing post-secondary education, trade school, or a recognized training or development program
- have completed the 18U season without unresolved disciplinary issues
- consent to reference checks by the selection committee

Selection criteria summary:
- on-field excellence
- leadership and sportsmanship
- academic and personal commitment
- community involvement and service
- character and values alignment

Scholarship structure:
- awarded annually
- one or more recipients may be selected
- award amounts may vary annually

7. Supporting documents
The additional program notes mention possible supporting documents such as:
- reference letters
- transcript or report card

For now:
- design the app so supporting documents can be added later cleanly
- if file upload is straightforward, include optional uploads now for:
  - transcript_or_report_card
  - supporting_documents
- if implemented, use Django file uploads and store under `MEDIA_ROOT`
- do not make uploads required unless explicitly needed

8. Validation rules
- Only authenticated users can create or edit applications.
- Only one application per applicant per cycle.
- Draft applications can be edited until the cycle deadline.
- Submitted applications become read-only by default.
- Required reference 1 must be complete.
- Reference 2 is optional, but if any field is entered, validate the required fields for that reference entry.
- Declarations must be checked before submission.
- Applicant statement should enforce reasonable length validation targeting the 300–500 word guidance. Prefer soft validation plus server-side minimum/maximum character or word-count validation.
- If the cycle is closed or deadline has passed, no new submissions or edits should be allowed except by admin.

9. Views and pages
Build a practical first version with server-rendered Django views and templates.

Suggested pages:
- public scholarship overview page
- sign up page
- login page
- applicant dashboard
- application create/edit page
- application detail / submission confirmation page
- staff/admin application list page
- staff/admin application detail page
- staff/admin year-based application review page if helpful

Applicant dashboard should show:
- current cycle
- application status
- deadline
- whether the application is still editable

Admin review experience should support:
- quick scanning of applicants
- filtering by scholarship year
- filtering by application status
- opening a clean, readable application detail view
- downloading a single applicant's application
- downloading all applications for a given scholarship year

10. URLs
Use a dedicated app namespace, for example `scholarships`.

Suggested routes:
- `/scholarships/`
- `/scholarships/signup/`
- `/scholarships/login/`
- `/scholarships/logout/`
- `/scholarships/dashboard/`
- `/scholarships/apply/`
- `/scholarships/application/<id>/`

Integrate the app into the project-level URL configuration cleanly.

11. Forms
Use Django forms / ModelForms.
Keep forms readable and maintainable.
Prefer server-side validation first.
Use HTML5 input types where useful:
- date
- email

12. Admin
Register the models in Django admin.
Admin should be able to:
- create scholarship cycles
- open/close cycles
- inspect applicant profiles
- review applications
- view references inline if practical
- access applications in a way that is easy to review operationally, not just technically
- download individual applications
- download year-based application sets or reports
Useful admin filters:
- cycle
- status
- submitted_at

If the built-in Django admin alone is not sufficient for a clean review workflow, add lightweight custom staff views inside the scholarship app for better operational usability.

13. UI expectations
Match the existing project style: clean, professional, lightweight, maintainable.
Do not introduce React or frontend tooling.
Keep templates straightforward and mobile-friendly.
This is a scholarship app for a community baseball organization, so it should feel credible, calm, and well-structured.
The UI must be beautiful and consistent with the overall site design language.
The application flow should feel polished, trustworthy, and professionally built.
Pay close attention to:
- typography
- spacing
- form layout
- section hierarchy
- dashboard clarity
- mobile responsiveness
- print/download readability for exported applications
Avoid a bare-bones or purely utilitarian admin/applicant experience.

14. Testing
Add focused tests for:
- signup flow
- application creation
- one-application-per-cycle rule
- deadline / closed-cycle restrictions
- required declarations
- draft vs submitted edit permissions

15. Implementation approach
Before coding, inspect the existing project and integrate with its conventions.
Prefer a new app rather than forcing scholarship logic into unrelated apps.
Keep code modular and future-friendly, but do not over-engineer.

16. Deliverable expectations
Implement:
- models
- forms
- views
- urls
- templates
- admin
- migrations
- tests

Also include a brief summary of:
- architecture decisions
- annual cycle logic
- how applicant authentication works without email verification
- how admin review and download workflows work
- any follow-up improvements that should come next

Use the following scholarship content as the source of truth for wording and requirements:

Vancouver Community Baseball
18U Graduating Player Scholarship Program

Application Form

Instructions
This form is used for 18U players applying for the Vancouver Community Baseball 18U Graduating Player Scholarship Program.
Please complete all required sections.
Application must be submitted by the published deadline.
Incomplete submissions may not be considered.

Section A: Applicant Information
Player Full Name
Date of Birth
VCB Team / Program
Primary Position(s)
Years Participated in VCB Programs

Section B: Post-Graduation Plans
What pathway does the nominee plan to pursue? (check all that apply)
- College / University
- Trade or Vocational Training
- Recognized Training or Development Program
- Undecided
Institution / Program Name (if known)
Intended Field of Study or Training (if applicable)

Section C: Applicant Statement
Please provide a written statement (approximately 300–500 words) addressing:
- the applicant's experience in growth and development during their time with VCB
- leadership, character, and sportsmanship
- commitment to athletics, academics, and/or personal development
- community involvement or service
- why the nominee exemplifies the values of Vancouver Community Baseball

Section D: References
Please provide one to two references who can speak to the nominee's character and involvement. References must be non-family adults.

Section E: Declarations & Consent
- I confirm that the information provided is accurate to the best of my knowledge.
- I confirm that the nominee is a graduating 18U player in good standing with Vancouver Community Baseball.
- I understand that scholarship decisions are final and not subject to appeal.
Nominator Signature
Date

Program summary:
- values-based scholarship
- not based on athletic statistics alone
- recognizes leadership, commitment, character, growth, and community involvement
- supports post-secondary, trade, vocational, and recognized development pathways
- awarded annually

Build a solid first version suitable for real internal review and iterative expansion.
The final result must feel professionally designed and professionally engineered, with an especially strong admin review experience for annual scholarship operations.
