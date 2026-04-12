from leaguehub.models import CoachRole, TeamCoachAssignment


def is_league_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def active_assignments_for_user(user):
    if not user or not user.is_authenticated:
        return TeamCoachAssignment.objects.none()
    return TeamCoachAssignment.objects.filter(user=user, is_active=True).select_related("team", "team__league_season")


def coach_assignment_for_team(user, team):
    if not user or not user.is_authenticated or not team:
        return None
    return active_assignments_for_user(user).filter(team=team).first()


def is_head_coach_for_team(user, team) -> bool:
    assignment = coach_assignment_for_team(user, team)
    return bool(assignment and assignment.role == CoachRole.HEAD_COACH)


def is_assistant_coach_for_team(user, team) -> bool:
    assignment = coach_assignment_for_team(user, team)
    return bool(assignment and assignment.role == CoachRole.ASSISTANT_COACH)


def can_submit_score(user, game) -> bool:
    if is_league_admin(user):
        return True
    return is_head_coach_for_team(user, game.home_team)


def can_verify_score(user, game) -> bool:
    if is_league_admin(user):
        return True
    return is_head_coach_for_team(user, game.away_team)


def can_edit_verified_game(user, game) -> bool:
    return is_league_admin(user)


def can_contribute_team_content(user, game, team) -> bool:
    if is_league_admin(user):
        return True
    if team not in {game.home_team, game.away_team}:
        return False
    return coach_assignment_for_team(user, team) is not None
