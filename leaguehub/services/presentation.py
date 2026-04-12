from datetime import timedelta

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from leaguehub.forms import UrlChoiceForm
from leaguehub.models import Game, GameStatus, GameVerificationStatus, LeagueSeason, Team
from leaguehub.services.permissions import (
    can_contribute_team_content,
    can_edit_verified_game,
    can_submit_score,
    can_verify_score,
    is_league_admin,
)
from leaguehub.services.standings import calculate_official_standings


def get_verification_presentation(game):
    if game.verification_status == GameVerificationStatus.VERIFIED_FINAL:
        return {
            "label": "Verified Final",
            "badge_class": "leaguehub-status leaguehub-status--verified",
            "card_class": "leaguehub-game-card leaguehub-game-card--verified",
        }
    if game.verification_status == GameVerificationStatus.AWAITING_AWAY_VERIFICATION:
        return {
            "label": "Awaiting Away Verification",
            "badge_class": "leaguehub-status leaguehub-status--awaiting",
            "card_class": "leaguehub-game-card leaguehub-game-card--awaiting",
        }
    return {
        "label": "Scheduled",
        "badge_class": "leaguehub-status leaguehub-status--scheduled",
        "card_class": "leaguehub-game-card",
    }


def serialize_game_for_display(game, user=None):
    verification = get_verification_presentation(game)
    scoreline = (
        f"{game.away_team.name} {game.away_score} at {game.home_team.name} {game.home_score}"
        if game.has_valid_score
        else f"{game.away_team.name} at {game.home_team.name}"
    )
    return {
        "id": game.id,
        "detail_url": reverse("leaguehub:game-detail", kwargs={"pk": game.pk}),
        "game_date": game.game_date,
        "scheduled_start_time": game.scheduled_start_time,
        "location": game.location,
        "home_team": game.home_team,
        "away_team": game.away_team,
        "home_score": game.home_score,
        "away_score": game.away_score,
        "scoreline": scoreline,
        "status": game.status,
        "status_label": game.get_status_display(),
        "verification_status": game.verification_status,
        "verification_label": verification["label"],
        "verification_badge_class": verification["badge_class"],
        "card_class": verification["card_class"],
        "is_verified": game.verification_status == GameVerificationStatus.VERIFIED_FINAL,
        "is_awaiting_verification": game.verification_status == GameVerificationStatus.AWAITING_AWAY_VERIFICATION,
        "can_submit_score": bool(user and can_submit_score(user, game)),
        "can_verify_score": bool(user and can_verify_score(user, game)),
        "can_edit_verified_game": bool(user and can_edit_verified_game(user, game)),
        "can_submit_home_story": bool(user and can_contribute_team_content(user, game, game.home_team)),
        "can_submit_away_story": bool(user and can_contribute_team_content(user, game, game.away_team)),
        "home_team_url": reverse(
            "leaguehub:team-detail",
            kwargs={
                "league_slug": game.league_season.league.slug,
                "season_slug": game.league_season.season.slug,
                "team_slug": game.home_team.slug,
            },
        ),
        "away_team_url": reverse(
            "leaguehub:team-detail",
            kwargs={
                "league_slug": game.league_season.league.slug,
                "season_slug": game.league_season.season.slug,
                "team_slug": game.away_team.slug,
            },
        ),
        "home_story": game.stories.filter(team=game.home_team).first(),
        "away_story": game.stories.filter(team=game.away_team).first(),
        "home_photo": game.photos.filter(team=game.home_team).first(),
        "away_photo": game.photos.filter(team=game.away_team).first(),
    }


def get_dashboard_context(*, league_season: LeagueSeason, user=None):
    today = timezone.localdate()
    recent_cutoff = today - timedelta(days=7)
    standings = serialize_standings_for_display(league_season=league_season)
    recent_games = (
        Game.objects.filter(league_season=league_season, game_date__gte=recent_cutoff, is_archived=False)
        .exclude(status=GameStatus.CANCELED)
        .select_related("home_team", "away_team")
        .prefetch_related("stories", "photos")
        .order_by("-game_date", "-id")
    )
    all_games = list(
        Game.objects.filter(league_season=league_season, is_archived=False)
        .exclude(status=GameStatus.CANCELED)
        .select_related("home_team", "away_team")
        .prefetch_related("stories", "photos")
        .order_by("-game_date", "-id")
    )
    return {
        "league_season": league_season,
        "standings": standings,
        "standings_count": len(standings),
        "recent_games": [serialize_game_for_display(game, user=user) for game in recent_games[:6]],
        "featured_games": [serialize_game_for_display(game, user=user) for game in all_games[:3]],
        "verified_final_count": sum(1 for game in all_games if game.verification_status == GameVerificationStatus.VERIFIED_FINAL),
        "total_team_count": league_season.teams.filter(is_active=True).count(),
    }


def get_index_context(*, user=None):
    league_seasons = (
        LeagueSeason.objects.select_related("league", "season")
        .filter(is_active=True, league__is_active=True)
        .order_by("-season__year", "league__name", "title")
    )
    serialized = []
    for league_season in league_seasons:
        standings = calculate_official_standings(league_season=league_season)
        next_game = (
            Game.objects.filter(
                league_season=league_season,
                is_archived=False,
                game_date__gte=timezone.localdate(),
            )
            .exclude(status=GameStatus.CANCELED)
            .select_related("home_team", "away_team")
            .order_by("game_date", "scheduled_start_time", "id")
            .first()
        )
        serialized.append(
            {
                "title": league_season.title,
                "league_name": league_season.league.name,
                "season_name": league_season.season.name,
                "team_count": league_season.teams.filter(is_active=True).count(),
                "official_games": sum(row.games_played for row in standings) // 2,
                "dashboard_url": reverse(
                    "leaguehub:dashboard",
                    kwargs={
                        "league_slug": league_season.league.slug,
                        "season_slug": league_season.season.slug,
                    },
                ),
                "standings_url": reverse(
                    "leaguehub:standings",
                    kwargs={
                        "league_slug": league_season.league.slug,
                        "season_slug": league_season.season.slug,
                    },
                ),
                "next_game": serialize_game_for_display(next_game, user=user) if next_game else None,
            }
        )
    return {"league_seasons": serialized}


def get_navigation_context(*, current_league_season=None, current_team=None):
    active_league_seasons = (
        LeagueSeason.objects.select_related("league", "season")
        .filter(is_active=True, league__is_active=True)
        .order_by("-season__year", "league__name", "title")
    )
    season_choices = [
        (
            reverse(
                "leaguehub:dashboard",
                kwargs={"league_slug": item.league.slug, "season_slug": item.season.slug},
            ),
            item.title,
        )
        for item in active_league_seasons
    ]
    season_form = UrlChoiceForm(
        choices=season_choices,
        label="League season",
        field_name="season_destination",
        initial={
            "season_destination": reverse(
                "leaguehub:dashboard",
                kwargs={
                    "league_slug": current_league_season.league.slug,
                    "season_slug": current_league_season.season.slug,
                },
            )
            if current_league_season
            else ""
        },
    )

    team_form = None
    if current_league_season:
        team_choices = [
            (
                reverse(
                    "leaguehub:team-detail",
                    kwargs={
                        "league_slug": current_league_season.league.slug,
                        "season_slug": current_league_season.season.slug,
                        "team_slug": team.slug,
                    },
                ),
                team.name,
            )
            for team in current_league_season.teams.filter(is_active=True).order_by("name")
        ]
        team_form = UrlChoiceForm(
            choices=team_choices,
            label="Team",
            field_name="team_destination",
            initial={
                "team_destination": reverse(
                    "leaguehub:team-detail",
                    kwargs={
                        "league_slug": current_league_season.league.slug,
                        "season_slug": current_league_season.season.slug,
                        "team_slug": current_team.slug,
                    },
                )
                if current_team
                else ""
            },
        )

    return {
        "leaguehub_season_form": season_form,
        "leaguehub_team_form": team_form,
        "leaguehub_dashboard_url": (
            reverse(
                "leaguehub:dashboard",
                kwargs={
                    "league_slug": current_league_season.league.slug,
                    "season_slug": current_league_season.season.slug,
                },
            )
            if current_league_season
            else None
        ),
        "leaguehub_standings_url": (
            reverse(
                "leaguehub:standings",
                kwargs={
                    "league_slug": current_league_season.league.slug,
                    "season_slug": current_league_season.season.slug,
                },
            )
            if current_league_season
            else None
        ),
        "leaguehub_results_url": (
            reverse(
                "leaguehub:results",
                kwargs={
                    "league_slug": current_league_season.league.slug,
                    "season_slug": current_league_season.season.slug,
                },
            )
            if current_league_season
            else None
        ),
    }


def serialize_standings_for_display(*, league_season: LeagueSeason):
    team_slugs = {
        team.id: team.slug
        for team in league_season.teams.filter(is_active=True).only("id", "slug")
    }
    rows = []
    for standing in calculate_official_standings(league_season=league_season):
        rows.append(
            {
                "rank": len(rows) + 1,
                "team_id": standing.team_id,
                "team_name": standing.team_name,
                "games_played": standing.games_played,
                "wins": standing.wins,
                "losses": standing.losses,
                "ties": standing.ties,
                "points": standing.points,
                "runs_for": standing.runs_for,
                "runs_against": standing.runs_against,
                "run_differential": standing.run_differential,
                "team_url": reverse(
                    "leaguehub:team-detail",
                    kwargs={
                        "league_slug": league_season.league.slug,
                        "season_slug": league_season.season.slug,
                        "team_slug": team_slugs[standing.team_id],
                    },
                ),
            }
        )
    return rows


def get_team_context(*, team: Team, user=None):
    league_season = team.league_season
    standings = serialize_standings_for_display(league_season=league_season)
    standing_row = next((row for row in standings if row["team_id"] == team.id), None)
    games = (
        Game.objects.filter(league_season=league_season, is_archived=False)
        .filter(Q(home_team=team) | Q(away_team=team))
        .exclude(status=GameStatus.CANCELED)
        .select_related("home_team", "away_team", "league_season", "league_season__league", "league_season__season")
        .prefetch_related("stories", "photos")
        .order_by("-game_date", "-id")
    )
    return {
        "team": team,
        "league_season": league_season,
        "team_standing": standing_row,
        "games": [serialize_game_for_display(game, user=user) for game in games],
    }


def get_results_context(*, league_season: LeagueSeason, user=None):
    games = (
        Game.objects.filter(league_season=league_season, is_archived=False)
        .exclude(status=GameStatus.CANCELED)
        .select_related("home_team", "away_team")
        .prefetch_related("stories", "photos")
        .order_by("-game_date", "-id")
    )
    return {
        "league_season": league_season,
        "games": [serialize_game_for_display(game, user=user) for game in games],
    }
