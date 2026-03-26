from django.urls import path

from pdp.views import (
    AIInsightsView,
    CoachDashboardView,
    DevelopmentLogView,
    DrillLibraryView,
    EvaluationHistoryView,
    GoalView,
    ImportWorkbenchView,
    ParentDashboardView,
    PDPHomeView,
    PDPLoginView,
    PDPLogoutView,
    PDPPasswordChangeView,
    PlayerDashboardView,
    ReportCardView,
    RoadmapView,
    SnapshotView,
)


app_name = "pdp"

urlpatterns = [
    path("", PDPHomeView.as_view(), name="home"),
    path("login/", PDPLoginView.as_view(), name="login"),
    path("logout/", PDPLogoutView.as_view(), name="logout"),
    path("account/password/", PDPPasswordChangeView.as_view(), name="password-change"),
    path("coach/", CoachDashboardView.as_view(), name="coach-dashboard"),
    path("parent/", ParentDashboardView.as_view(), name="parent-dashboard"),
    path("import/", ImportWorkbenchView.as_view(), name="import-workbench"),
    path("drills/", DrillLibraryView.as_view(), name="drill-library"),
    path("players/<int:player_id>/", PlayerDashboardView.as_view(), name="player-dashboard"),
    path("players/<int:player_id>/evaluations/", EvaluationHistoryView.as_view(), name="evaluation-history"),
    path("players/<int:player_id>/logs/", DevelopmentLogView.as_view(), name="development-logs"),
    path("players/<int:player_id>/goals/", GoalView.as_view(), name="goals"),
    path("players/<int:player_id>/insights/", AIInsightsView.as_view(), name="ai-insights"),
    path("players/<int:player_id>/report-card/", ReportCardView.as_view(), name="report-card"),
    path("players/<int:player_id>/snapshots/", SnapshotView.as_view(), name="snapshots"),
    path("players/<int:player_id>/roadmap/", RoadmapView.as_view(), name="roadmap"),
]
