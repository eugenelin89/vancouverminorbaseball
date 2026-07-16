from django.contrib import admin

from seasons.models import CoachSeasonAssignment, PlayerRosterMembership, Season, SeasonTeam


class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


@admin.register(Season)
class SeasonAdmin(TimeStampedAdmin):
    list_display = ("name", "key", "starts_on", "ends_on", "is_current", "is_active", "updated_at")
    list_filter = ("is_current", "is_active", "starts_on")
    search_fields = ("key", "name")
    readonly_fields = TimeStampedAdmin.readonly_fields


@admin.register(SeasonTeam)
class SeasonTeamAdmin(TimeStampedAdmin):
    list_display = ("season", "division", "name", "external_source", "external_identifier", "is_active", "updated_at")
    list_filter = ("season", "division", "is_active")
    search_fields = ("name", "division", "normalized_name", "normalized_division", "external_identifier")
    autocomplete_fields = ("season",)
    readonly_fields = TimeStampedAdmin.readonly_fields + ("normalized_name", "normalized_division")
    exclude = ("metadata",)


@admin.register(PlayerRosterMembership)
class PlayerRosterMembershipAdmin(TimeStampedAdmin):
    list_display = ("player", "season_team", "status", "jersey_number", "is_primary", "is_active", "starts_on", "ends_on")
    list_filter = ("season_team__season", "season_team__division", "status", "is_primary", "is_active")
    search_fields = (
        "player__first_name",
        "player__last_name",
        "player__preferred_name",
        "season_team__name",
        "season_team__division",
        "source_identifier",
    )
    autocomplete_fields = ("player", "season_team", "import_batch")
    readonly_fields = TimeStampedAdmin.readonly_fields
    exclude = ("metadata",)


@admin.register(CoachSeasonAssignment)
class CoachSeasonAssignmentAdmin(TimeStampedAdmin):
    list_display = ("user", "season_team", "assignment_role", "is_primary", "is_active", "starts_on", "ends_on")
    list_filter = ("season_team__season", "season_team__division", "assignment_role", "is_primary", "is_active")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "season_team__name",
        "season_team__division",
        "source_identifier",
    )
    autocomplete_fields = ("user", "season_team")
    readonly_fields = TimeStampedAdmin.readonly_fields
    exclude = ("metadata",)

