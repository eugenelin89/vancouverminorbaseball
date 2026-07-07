Implement Phase 4 review fixes only. Do not start Phase 5 and do not change architecture docs except to record these review fixes if needed.

Apply these targeted fixes:

1. In `CoachAssessmentEditView.dispatch()`, use the existing `can_submit_coach_assessment()` permission helper before allowing a user to start/create/edit a coach assessment. If the user cannot submit, raise `PermissionDenied`.

2. In `StaffObservationReviewListView.get_queryset()`, replace the queryset union-style search:
   queryset.filter(...) | queryset.filter(...) | queryset.filter(...)
   with a single `.filter(Q(...) | Q(...) | Q(...))`.

3. In `CoachAssessmentDetailView`, pass a `can_edit` boolean into the template context using `can_edit_observation(request.user, observation)`. Update `assessment_detail.html` to use `{% if can_edit %}` instead of the long inline boolean expression.

4. Normalize/guard the `cycle` GET parameter before passing it to `get_active_coach_assessment_cycle()`. Invalid cycle IDs should not crash the page.

5. Fix the staff review detail UX so the Back link from staff review returns to `analytics:observation-review-list`, while the regular coach detail page still returns to `analytics:assessment-list`.

6. Add or update tests for the above where appropriate.

Run:
- `python manage.py test analytics`
- `python manage.py test players`
- `python manage.py test`

Report files changed and test results.