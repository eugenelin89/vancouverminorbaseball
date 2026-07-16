from seasons.views.assignments import (
    CoachAssignmentCreateView,
    CoachAssignmentEditView,
    CoachAssignmentEndView,
    CoachAssignmentListView,
    CoachSeasonHistoryView,
)
from seasons.views.memberships import (
    PlayerMembershipCreateView,
    PlayerMembershipEditView,
    PlayerMembershipEndView,
    PlayerMembershipListView,
    PlayerMembershipTransferView,
    PlayerSeasonHistoryView,
)
from seasons.views.seasons import (
    SeasonCreateView,
    SeasonDetailView,
    SeasonEditView,
    SeasonListView,
    SeasonSetCurrentView,
)
from seasons.views.teams import (
    SeasonTeamCreateView,
    SeasonTeamEditView,
    SeasonTeamListView,
)

__all__ = [
    "CoachAssignmentCreateView",
    "CoachAssignmentEditView",
    "CoachAssignmentEndView",
    "CoachAssignmentListView",
    "CoachSeasonHistoryView",
    "PlayerMembershipCreateView",
    "PlayerMembershipEditView",
    "PlayerMembershipEndView",
    "PlayerMembershipListView",
    "PlayerMembershipTransferView",
    "PlayerSeasonHistoryView",
    "SeasonCreateView",
    "SeasonDetailView",
    "SeasonEditView",
    "SeasonListView",
    "SeasonSetCurrentView",
    "SeasonTeamCreateView",
    "SeasonTeamEditView",
    "SeasonTeamListView",
]
