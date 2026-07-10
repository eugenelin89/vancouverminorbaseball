from django.urls import path

from analytics.views import (
    AnalyticsCommandCenterView,
    CoachAssessmentDetailView,
    CoachAssessmentEditView,
    CoachAssessmentListView,
    EvaluationListView,
    EvaluationPlayerView,
    MyEvaluationDetailView,
    MyEvaluationsPlayerView,
    MyEvaluationsView,
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
    path("evaluations/", EvaluationListView.as_view(), name="evaluation-list"),
    path("evaluations/players/<int:player_id>/", EvaluationPlayerView.as_view(), name="evaluation-player"),
    path("my/evaluations/", MyEvaluationsView.as_view(), name="my-evaluations"),
    path("my/evaluations/players/<int:player_id>/", MyEvaluationsPlayerView.as_view(), name="my-evaluations-player"),
    path("my/evaluations/<int:observation_id>/", MyEvaluationDetailView.as_view(), name="my-evaluation-detail"),
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
