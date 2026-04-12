from django.urls import path

from leaguehub.views import (
    CoachAssignmentCreateView,
    CoachUserCreateView,
    GameDetailView,
    GamePhotoSubmitView,
    GameCreateView,
    GameScoreSubmitView,
    GameScoreVerifyView,
    GameStorySubmitView,
    LeagueCreateView,
    LeagueHubIndexView,
    LeagueHubManageView,
    LeagueSeasonCreateView,
    LeagueSeasonDashboardView,
    ResultsListView,
    SeasonCreateView,
    StandingsView,
    TeamDetailView,
    TeamCreateView,
)


app_name = "leaguehub"

urlpatterns = [
    path("", LeagueHubIndexView.as_view(), name="index"),
    path("manage/", LeagueHubManageView.as_view(), name="manage"),
    path("manage/seasons/create/", SeasonCreateView.as_view(), name="manage-season-create"),
    path("manage/leagues/create/", LeagueCreateView.as_view(), name="manage-league-create"),
    path("manage/league-seasons/create/", LeagueSeasonCreateView.as_view(), name="manage-league-season-create"),
    path("manage/teams/create/", TeamCreateView.as_view(), name="manage-team-create"),
    path("manage/coaches/create/", CoachUserCreateView.as_view(), name="manage-coach-create"),
    path("manage/assignments/create/", CoachAssignmentCreateView.as_view(), name="manage-assignment-create"),
    path("manage/games/create/", GameCreateView.as_view(), name="manage-game-create"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game-detail"),
    path("games/<int:pk>/submit-score/", GameScoreSubmitView.as_view(), name="submit-score"),
    path("games/<int:pk>/verify-score/", GameScoreVerifyView.as_view(), name="verify-score"),
    path("games/<int:pk>/story/<int:team_id>/", GameStorySubmitView.as_view(), name="submit-story"),
    path("games/<int:pk>/photo/<int:team_id>/", GamePhotoSubmitView.as_view(), name="submit-photo"),
    path("<slug:league_slug>/<slug:season_slug>/", LeagueSeasonDashboardView.as_view(), name="dashboard"),
    path("<slug:league_slug>/<slug:season_slug>/standings/", StandingsView.as_view(), name="standings"),
    path("<slug:league_slug>/<slug:season_slug>/results/", ResultsListView.as_view(), name="results"),
    path("<slug:league_slug>/<slug:season_slug>/teams/<slug:team_slug>/", TeamDetailView.as_view(), name="team-detail"),
]
