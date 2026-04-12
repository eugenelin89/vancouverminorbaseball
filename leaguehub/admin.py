from django.contrib import admin

from leaguehub.models import (
    Game,
    GamePhoto,
    GameScoreAuditEntry,
    GameStory,
    League,
    LeagueSeason,
    Team,
    TeamCoachAssignment,
)


class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


@admin.register(League)
class LeagueAdmin(TimeStampedAdmin):
    list_display = ("name", "slug", "is_active")
    search_fields = ("name", "slug")


@admin.register(LeagueSeason)
class LeagueSeasonAdmin(TimeStampedAdmin):
    list_display = ("title", "league", "season", "is_active")
    list_filter = ("league", "season", "is_active")
    search_fields = ("title", "slug", "league__name", "season__name")


@admin.register(Team)
class TeamAdmin(TimeStampedAdmin):
    list_display = ("name", "league_season", "short_name", "is_active")
    list_filter = ("league_season", "is_active")
    search_fields = ("name", "short_name", "league_season__title")


@admin.register(TeamCoachAssignment)
class TeamCoachAssignmentAdmin(TimeStampedAdmin):
    list_display = ("team", "user", "role", "is_active")
    list_filter = ("role", "is_active", "team__league_season")
    search_fields = ("team__name", "user__username", "user__first_name", "user__last_name", "user__email")


@admin.register(Game)
class GameAdmin(TimeStampedAdmin):
    list_display = (
        "__str__",
        "league_season",
        "game_date",
        "status",
        "verification_status",
        "home_score",
        "away_score",
        "is_archived",
    )
    list_filter = ("league_season", "status", "verification_status", "is_archived")
    search_fields = ("home_team__name", "away_team__name", "location", "league_season__title")


@admin.register(GameStory)
class GameStoryAdmin(TimeStampedAdmin):
    list_display = ("game", "team", "author", "headline")
    list_filter = ("team__league_season",)
    search_fields = ("game__home_team__name", "game__away_team__name", "team__name", "headline", "story")


@admin.register(GamePhoto)
class GamePhotoAdmin(TimeStampedAdmin):
    list_display = ("game", "team", "uploaded_by", "caption")
    list_filter = ("team__league_season",)
    search_fields = ("game__home_team__name", "game__away_team__name", "team__name", "caption")


@admin.register(GameScoreAuditEntry)
class GameScoreAuditEntryAdmin(TimeStampedAdmin):
    list_display = ("game", "edited_by", "previous_home_score", "new_home_score", "requires_reverification", "created_at")
    list_filter = ("requires_reverification", "game__league_season")
    search_fields = ("game__home_team__name", "game__away_team__name", "edited_by__username", "note")
