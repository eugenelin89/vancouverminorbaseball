from django.utils.text import slugify

from players.models import Player, PlayerTag


def create_tag(name: str, description: str = "") -> PlayerTag:
    """Create or return a player tag by slug."""
    slug = slugify(name) or "tag"
    tag, _created = PlayerTag.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "description": description},
    )
    return tag


def assign_tag(player: Player, tag_or_name) -> PlayerTag:
    """Assign a tag to a player idempotently."""
    tag = tag_or_name if isinstance(tag_or_name, PlayerTag) else create_tag(str(tag_or_name))
    tag.players.add(player)
    return tag


def remove_tag(player: Player, tag_or_name) -> None:
    """Remove a tag from a player if present."""
    if isinstance(tag_or_name, PlayerTag):
        tag = tag_or_name
    else:
        tag = PlayerTag.objects.filter(slug=slugify(str(tag_or_name))).first()
    if tag:
        tag.players.remove(player)


def players_with_tag(tag_or_slug):
    """Return active players assigned to a tag."""
    slug = tag_or_slug.slug if isinstance(tag_or_slug, PlayerTag) else slugify(str(tag_or_slug))
    return Player.objects.filter(tags__slug=slug, tags__is_active=True).distinct()


def active_tags():
    """Return active tags for staff/admin workflows."""
    return PlayerTag.objects.filter(is_active=True).order_by("name")
