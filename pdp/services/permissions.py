from django.db.models import Q

from pdp.models import ParentChildAccess, PlayerDevelopmentLog, PlayerProfile


def is_platform_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def get_accessible_players(user):
    if not user or not user.is_authenticated:
        return PlayerProfile.objects.none()
    if is_platform_admin(user):
        return PlayerProfile.objects.all()
    query = Q()
    if hasattr(user, "player_profile"):
        query |= Q(user=user)
    query |= Q(coach_assignments__coach=user, coach_assignments__is_active=True)
    query |= Q(parent_links__parent=user, parent_links__is_active=True)
    return PlayerProfile.objects.filter(query).distinct()


def can_view_player(user, player: PlayerProfile) -> bool:
    return get_accessible_players(user).filter(pk=player.pk).exists()


def can_manage_player(user, player: PlayerProfile) -> bool:
    if is_platform_admin(user):
        return True
    return player.coach_assignments.filter(coach=user, is_active=True).exists()


def can_manage_imports(user) -> bool:
    return is_platform_admin(user)


def can_view_log(user, log: PlayerDevelopmentLog) -> bool:
    if is_platform_admin(user):
        return True
    if hasattr(user, "player_profile") and log.player_id == user.player_profile.id:
        return log.visibility == "player"
    if log.player.parent_links.filter(parent=user, is_active=True).exists():
        if log.visibility == "staff":
            return ParentChildAccess.objects.filter(
                parent=user,
                player=log.player,
                is_active=True,
                can_view_private_notes=True,
            ).exists()
        return log.visibility == "player"
    if log.player.coach_assignments.filter(coach=user, is_active=True).exists():
        return log.visibility in {"player", "coach"}
    return False


def visible_logs_for_user(user, queryset=None):
    queryset = queryset or PlayerDevelopmentLog.objects.select_related("player", "season", "author")
    if is_platform_admin(user):
        return queryset
    allowed_player_ids = get_accessible_players(user).values_list("id", flat=True)
    if hasattr(user, "player_profile"):
        return queryset.filter(player=user.player_profile, visibility="player")
    if ParentChildAccess.objects.filter(parent=user, is_active=True, can_view_private_notes=True).exists():
        return queryset.filter(player_id__in=allowed_player_ids).exclude(visibility="staff")
    if user.is_authenticated:
        return queryset.filter(player_id__in=allowed_player_ids).exclude(visibility__in=["coach", "staff"])
    return queryset.none()
