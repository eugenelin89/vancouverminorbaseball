from django.urls import path

from seasons.views import (
    CoachAssignmentCreateView,
    CoachAssignmentEditView,
    CoachAssignmentEndView,
    CoachAssignmentListView,
    CoachSeasonHistoryView,
    PlayerMembershipCreateView,
    PlayerMembershipEditView,
    PlayerMembershipEndView,
    PlayerMembershipListView,
    PlayerMembershipTransferView,
    PlayerSeasonHistoryView,
    SeasonCreateView,
    SeasonDetailView,
    SeasonEditView,
    SeasonListView,
    SeasonSetCurrentView,
    SeasonTeamCreateView,
    SeasonTeamEditView,
    SeasonTeamListView,
)


app_name = "seasons"

urlpatterns = [
    path("", SeasonListView.as_view(), name="season-list"),
    path("new/", SeasonCreateView.as_view(), name="season-new"),
    path("<int:season_id>/", SeasonDetailView.as_view(), name="season-detail"),
    path("<int:season_id>/edit/", SeasonEditView.as_view(), name="season-edit"),
    path("<int:season_id>/set-current/", SeasonSetCurrentView.as_view(), name="season-set-current"),
    path("teams/", SeasonTeamListView.as_view(), name="team-list"),
    path("teams/new/", SeasonTeamCreateView.as_view(), name="team-new"),
    path("<int:season_id>/teams/new/", SeasonTeamCreateView.as_view(), name="season-team-new"),
    path("teams/<int:team_id>/edit/", SeasonTeamEditView.as_view(), name="team-edit"),
    path("memberships/", PlayerMembershipListView.as_view(), name="membership-list"),
    path("memberships/new/", PlayerMembershipCreateView.as_view(), name="membership-new"),
    path("memberships/<int:membership_id>/edit/", PlayerMembershipEditView.as_view(), name="membership-edit"),
    path("memberships/<int:membership_id>/end/", PlayerMembershipEndView.as_view(), name="membership-end"),
    path("memberships/<int:membership_id>/transfer/", PlayerMembershipTransferView.as_view(), name="membership-transfer"),
    path("players/<int:player_id>/history/", PlayerSeasonHistoryView.as_view(), name="player-history"),
    path("coach-assignments/", CoachAssignmentListView.as_view(), name="coach-assignment-list"),
    path("coach-assignments/new/", CoachAssignmentCreateView.as_view(), name="coach-assignment-new"),
    path("coach-assignments/<int:assignment_id>/edit/", CoachAssignmentEditView.as_view(), name="coach-assignment-edit"),
    path("coach-assignments/<int:assignment_id>/end/", CoachAssignmentEndView.as_view(), name="coach-assignment-end"),
    path("coaches/<int:user_id>/history/", CoachSeasonHistoryView.as_view(), name="coach-history"),
]
