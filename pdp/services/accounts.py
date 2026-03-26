from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.db import transaction

from pdp.models import PlayerProfile


User = get_user_model()


@dataclass
class ProvisioningResult:
    player_id: int
    player_name: str
    username: str
    created: bool
    password_reset: bool
    user_id: int


def _base_username(first_name: str, last_name: str) -> str:
    return "".join(f"{first_name}{last_name}".lower().split())


def generate_unique_username(first_name: str, last_name: str) -> str:
    base = _base_username(first_name, last_name) or "player"
    existing = set(
        User.objects.filter(username__startswith=base).values_list("username", flat=True)
    )
    if base not in existing:
        return base
    counter = 2
    while f"{base}{counter}" in existing:
        counter += 1
    return f"{base}{counter}"


@transaction.atomic
def provision_player_account(player: PlayerProfile, *, reset_password: bool = False) -> ProvisioningResult:
    created = False
    password_reset = False

    if player.user_id:
        user = player.user
    else:
        username = generate_unique_username(player.first_name, player.last_name)
        user = User.objects.create(
            username=username,
            first_name=player.first_name,
            last_name=player.last_name,
            email=player.email,
        )
        user.set_password(username)
        user.save(update_fields=["password"])
        player.user = user
        player.must_change_password = True
        player.save(update_fields=["user", "must_change_password", "updated_at"])
        created = True
        password_reset = True
        return ProvisioningResult(
            player_id=player.id,
            player_name=player.full_name,
            username=user.username,
            created=created,
            password_reset=password_reset,
            user_id=user.id,
        )

    if reset_password:
        user.set_password(user.username)
        user.save(update_fields=["password"])
        player.must_change_password = True
        player.save(update_fields=["must_change_password", "updated_at"])
        password_reset = True

    return ProvisioningResult(
        player_id=player.id,
        player_name=player.full_name,
        username=user.username,
        created=created,
        password_reset=password_reset,
        user_id=user.id,
    )


def provision_accounts_for_players(players, *, reset_existing_passwords: bool = False):
    return [
        provision_player_account(player, reset_password=reset_existing_passwords)
        for player in players
    ]
