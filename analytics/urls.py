from django.urls import path

from analytics.views import (
    AnalyticsCommandCenterView,
    CoachAssessmentDetailView,
    CoachAssessmentEditView,
    CoachAssessmentListView,
    PlayerComparisonView,
    PlayerProfileView,
    PlayerImportConfirmView,
    PlayerImportConflictView,
    PlayerImportDetailView,
    PlayerImportListView,
    PlayerImportPreviewView,
    PlayerImportUploadView,
    PlayerSearchView,
    StaffObservationReviewDetailView,
    StaffObservationReviewListView,
)


app_name = "analytics"

urlpatterns = [
    path("", AnalyticsCommandCenterView.as_view(), name="command-center"),
    path("players/", PlayerSearchView.as_view(), name="player-search"),
    path("players/compare/", PlayerComparisonView.as_view(), name="player-compare"),
    path("players/<int:player_id>/", PlayerProfileView.as_view(), name="player-profile"),
    path("assessments/", CoachAssessmentListView.as_view(), name="assessment-list"),
    path("assessments/players/<int:player_id>/", CoachAssessmentEditView.as_view(), name="assessment-player"),
    path("assessments/<int:observation_id>/", CoachAssessmentDetailView.as_view(), name="assessment-detail"),
    path("assessments/<int:observation_id>/edit/", CoachAssessmentEditView.as_view(), name="assessment-edit"),
    path("observations/review/", StaffObservationReviewListView.as_view(), name="observation-review-list"),
    path("observations/<int:observation_id>/review/", StaffObservationReviewDetailView.as_view(), name="observation-review-detail"),
    path("imports/", PlayerImportListView.as_view(), name="import-list"),
    path("imports/new/", PlayerImportUploadView.as_view(), name="import-new"),
    path("imports/<int:pk>/preview/", PlayerImportPreviewView.as_view(), name="import-preview"),
    path("imports/<int:pk>/conflicts/", PlayerImportConflictView.as_view(), name="import-conflicts"),
    path("imports/<int:pk>/confirm/", PlayerImportConfirmView.as_view(), name="import-confirm"),
    path("imports/<int:pk>/", PlayerImportDetailView.as_view(), name="import-detail"),
]
