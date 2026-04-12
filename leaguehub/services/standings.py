from dataclasses import dataclass

from leaguehub.models import Game, GameStatus, GameVerificationStatus, LeagueSeason, Team


@dataclass(frozen=True)
class TeamStanding:
    team_id: int
    team_name: str
    games_played: int
    wins: int
    losses: int
    ties: int
    points: int
    runs_for: int
    runs_against: int
    run_differential: int


def official_games_for_league_season(league_season: LeagueSeason):
    return (
        Game.objects.filter(
            league_season=league_season,
            verification_status=GameVerificationStatus.VERIFIED_FINAL,
            is_archived=False,
        )
        .exclude(status__in=[GameStatus.POSTPONED, GameStatus.CANCELED])
        .select_related("home_team", "away_team")
        .order_by("game_date", "id")
    )


def calculate_official_standings(*, league_season: LeagueSeason):
    teams = list(Team.objects.filter(league_season=league_season, is_active=True).order_by("name"))
    standings = {
        team.id: {
            "team_id": team.id,
            "team_name": team.name,
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "points": 0,
            "runs_for": 0,
            "runs_against": 0,
        }
        for team in teams
    }

    for game in official_games_for_league_season(league_season):
        home = standings[game.home_team_id]
        away = standings[game.away_team_id]

        home["games_played"] += 1
        away["games_played"] += 1
        home["runs_for"] += game.home_score or 0
        home["runs_against"] += game.away_score or 0
        away["runs_for"] += game.away_score or 0
        away["runs_against"] += game.home_score or 0

        if game.home_score > game.away_score:
            home["wins"] += 1
            home["points"] += 2
            away["losses"] += 1
        elif game.home_score < game.away_score:
            away["wins"] += 1
            away["points"] += 2
            home["losses"] += 1
        else:
            home["ties"] += 1
            away["ties"] += 1
            home["points"] += 1
            away["points"] += 1

    result = []
    for item in standings.values():
        result.append(
            TeamStanding(
                team_id=item["team_id"],
                team_name=item["team_name"],
                games_played=item["games_played"],
                wins=item["wins"],
                losses=item["losses"],
                ties=item["ties"],
                points=item["points"],
                runs_for=item["runs_for"],
                runs_against=item["runs_against"],
                run_differential=item["runs_for"] - item["runs_against"],
            )
        )

    # Deterministic sort: points, run differential, runs for, then team name.
    return sorted(
        result,
        key=lambda row: (-row.points, -row.run_differential, -row.runs_for, row.team_name.lower(), row.team_id),
    )
