from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q

from accounts.models import UserPlayerLink, UserPlayerRelationship
from players.models import Player, PlayerImportBatch


User = get_user_model()


def _validate_user(user) -> None:
    if not isinstance(user, User) or not getattr(user, "is_authenticated", False):
        raise ValidationError("An authenticated user is required.")


def _validate_player(player) -> None:
    if not isinstance(player, Player):
        raise ValidationError("A valid player is required.")


def _validate_import_batch(import_batch) -> None:
    if import_batch is not None and not isinstance(import_batch, PlayerImportBatch):
        raise ValidationError("A valid player import batch is required.")


def _validate_relationship(relationship: str) -> str:
    valid_relationships = {choice.value for choice in UserPlayerRelationship}
    if relationship not in valid_relationships:
        raise ValidationError(f"Unsupported user/player relationship: {relationship}.")
    return relationship


def _validate_primary_relationship(relationship: str, is_primary: bool) -> None:
    if is_primary and relationship != UserPlayerRelationship.SELF:
        raise ValidationError("Only self links can be primary.")


def _validate_primary_self_conflicts(user, player, exclude_link_id=None) -> None:
    user_conflicts = UserPlayerLink.objects.filter(
        user=user,
        relationship=UserPlayerRelationship.SELF,
        is_primary=True,
        is_active=True,
    )
    player_conflicts = UserPlayerLink.objects.filter(
        player=player,
        relationship=UserPlayerRelationship.SELF,
        is_primary=True,
        is_active=True,
    )
    if exclude_link_id:
        user_conflicts = user_conflicts.exclude(pk=exclude_link_id)
        player_conflicts = player_conflicts.exclude(pk=exclude_link_id)
    if user_conflicts.exists():
        raise ValidationError("This user already has an active primary self player link.")
    if player_conflicts.exists():
        raise ValidationError("This player already has an active primary self user link.")


def validate_no_active_relationship_conflict(user, player, relationship: str, exclude_link_id=None) -> None:
    """Validate that no active link exists for this user, player, and relationship."""
    _validate_user(user)
    _validate_player(player)
    relationship = _validate_relationship(relationship)
    conflicts = UserPlayerLink.objects.filter(
        user=user,
        player=player,
        relationship=relationship,
        is_active=True,
    )
    if exclude_link_id:
        conflicts = conflicts.exclude(pk=exclude_link_id)
    if conflicts.exists():
        raise ValidationError("An active link already exists for this user, player, and relationship.")


def _validate_active_relationship_conflict(link) -> None:
    validate_no_active_relationship_conflict(link.user, link.player, link.relationship, exclude_link_id=link.pk)


@transaction.atomic
def link_user_to_player(
    user,
    player,
    relationship=UserPlayerRelationship.SELF,
    is_primary=True,
    created_from_import=False,
    import_batch=None,
    metadata=None,
) -> UserPlayerLink:
    """Create or update an active relationship between a Django user and player."""
    _validate_user(user)
    _validate_player(player)
    relationship = _validate_relationship(relationship)
    _validate_import_batch(import_batch)
    _validate_primary_relationship(relationship, is_primary)

    existing_link = (
        UserPlayerLink.objects.select_for_update()
        .filter(user=user, player=player, relationship=relationship, is_active=True)
        .first()
    )
    if is_primary and relationship == UserPlayerRelationship.SELF:
        _validate_primary_self_conflicts(user, player, exclude_link_id=getattr(existing_link, "pk", None))

    link_metadata = {} if metadata is None else metadata
    if not isinstance(link_metadata, dict):
        raise ValidationError("Link metadata must be a dictionary.")

    if existing_link:
        existing_link.is_primary = is_primary
        existing_link.created_from_import = created_from_import
        existing_link.import_batch = import_batch
        existing_link.metadata = link_metadata
        existing_link.save(
            update_fields=[
                "is_primary",
                "created_from_import",
                "import_batch",
                "metadata",
                "updated_at",
            ]
        )
        return existing_link

    link = UserPlayerLink(
        user=user,
        player=player,
        relationship=relationship,
        is_primary=is_primary,
        is_active=True,
        created_from_import=created_from_import,
        import_batch=import_batch,
        metadata=link_metadata,
    )
    try:
        link.save()
    except IntegrityError as exc:
        raise ValidationError("This user/player link conflicts with an existing active link.") from exc
    return link


@transaction.atomic
def deactivate_link(link, actor=None) -> UserPlayerLink:
    """Deactivate a user/player link without deleting its history."""
    if not isinstance(link, UserPlayerLink):
        raise ValidationError("A valid user/player link is required.")
    if not link.is_active and not link.is_primary:
        return link
    link.is_active = False
    link.is_primary = False
    link.save(update_fields=["is_active", "is_primary", "updated_at"])
    return link


@transaction.atomic
def activate_link(link, actor=None) -> UserPlayerLink:
    """Reactivate a user/player link when doing so does not conflict."""
    if not isinstance(link, UserPlayerLink):
        raise ValidationError("A valid user/player link is required.")
    _validate_primary_relationship(link.relationship, link.is_primary)
    _validate_active_relationship_conflict(link)
    if link.is_primary and link.relationship == UserPlayerRelationship.SELF:
        _validate_primary_self_conflicts(link.user, link.player, exclude_link_id=link.pk)
    if link.is_active:
        return link
    link.is_active = True
    try:
        link.save(update_fields=["is_active", "updated_at"])
    except IntegrityError as exc:
        raise ValidationError("This user/player link conflicts with an existing active link.") from exc
    return link


@transaction.atomic
def set_primary_self_link(link, actor=None) -> UserPlayerLink:
    """Make a self link the active primary link for its user and player."""
    if not isinstance(link, UserPlayerLink):
        raise ValidationError("A valid user/player link is required.")
    if link.relationship != UserPlayerRelationship.SELF:
        raise ValidationError("Only self links can be primary.")

    UserPlayerLink.objects.select_for_update().filter(
        Q(user=link.user) | Q(player=link.player),
        relationship=UserPlayerRelationship.SELF,
        is_active=True,
        is_primary=True,
    ).exclude(pk=link.pk).update(is_primary=False)

    link.is_active = True
    link.is_primary = True
    try:
        link.save(update_fields=["is_active", "is_primary", "updated_at"])
    except IntegrityError as exc:
        raise ValidationError("This primary self link conflicts with an existing active link.") from exc
    return link


@transaction.atomic
def unlink_user_from_player(user, player, relationship=None, actor=None) -> int:
    """Deactivate active links between a user and player, optionally for one relationship."""
    _validate_user(user)
    _validate_player(player)
    queryset = UserPlayerLink.objects.select_for_update().filter(user=user, player=player, is_active=True)
    if relationship is not None:
        queryset = queryset.filter(relationship=_validate_relationship(relationship))

    count = 0
    for link in queryset:
        deactivate_link(link, actor=actor)
        count += 1
    return count


def get_players_for_user(user, active_only=True):
    """Return players linked to a user."""
    _validate_user(user)
    filters = {"user_links__user": user}
    if active_only:
        filters["user_links__is_active"] = True
    return Player.objects.filter(**filters).distinct()


def get_users_for_player(player, active_only=True):
    """Return users linked to a player."""
    _validate_player(player)
    filters = {"player_links__player": player}
    if active_only:
        filters["player_links__is_active"] = True
    return User.objects.filter(**filters).distinct().order_by("username", "id")


def get_primary_player(user):
    """Return the user's active primary self-linked player, if present."""
    _validate_user(user)
    link = (
        UserPlayerLink.objects.select_related("player")
        .filter(
            user=user,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
            is_active=True,
        )
        .first()
    )
    return link.player if link else None


def get_primary_user(player):
    """Return the player's active primary self-linked user, if present."""
    _validate_player(player)
    link = (
        UserPlayerLink.objects.select_related("user")
        .filter(
            player=player,
            relationship=UserPlayerRelationship.SELF,
            is_primary=True,
            is_active=True,
        )
        .first()
    )
    return link.user if link else None


def is_player_self(user, player) -> bool:
    """Return whether the user is actively self-linked to the player."""
    if not isinstance(user, User) or not getattr(user, "is_authenticated", False):
        return False
    if not isinstance(player, Player):
        return False
    return UserPlayerLink.objects.filter(
        user=user,
        player=player,
        relationship=UserPlayerRelationship.SELF,
        is_active=True,
    ).exists()
