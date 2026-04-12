from django.core.exceptions import PermissionDenied
from django.db import transaction

from leaguehub.models import GamePhoto, GameStory
from leaguehub.services.permissions import can_contribute_team_content


@transaction.atomic
def save_game_story(*, game, team, actor, headline="", story_text=""):
    if not can_contribute_team_content(actor, game, team):
        raise PermissionDenied("You do not have permission to submit a story for this team.")
    story, _ = GameStory.objects.update_or_create(
        game=game,
        team=team,
        defaults={
            "author": actor,
            "headline": headline,
            "story": story_text,
        },
    )
    return story


@transaction.atomic
def save_game_photo(*, game, team, actor, image, caption=""):
    if not can_contribute_team_content(actor, game, team):
        raise PermissionDenied("You do not have permission to upload a photo for this team.")
    photo, _ = GamePhoto.objects.update_or_create(
        game=game,
        team=team,
        defaults={
            "uploaded_by": actor,
            "image": image,
            "caption": caption,
        },
    )
    return photo
