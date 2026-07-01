from django.contrib import admin

from players.models import Player, PlayerAlias, PlayerSourceIdentifier, PlayerSourceRow, PlayerTag


class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


class PlayerAliasInline(admin.TabularInline):
    model = PlayerAlias
    extra = 0
    readonly_fields = ("created_at", "updated_at")


class PlayerSourceIdentifierInline(admin.TabularInline):
    model = PlayerSourceIdentifier
    extra = 0
    readonly_fields = ("created_at", "updated_at")


@admin.register(Player)
class PlayerAdmin(TimeStampedAdmin):
    list_display = ("display_name", "last_name", "first_name", "division", "team_name", "is_active", "updated_at")
    list_filter = ("is_active", "division", "team_name", "gender")
    search_fields = (
        "first_name",
        "last_name",
        "preferred_name",
        "aliases__alias",
        "source_identifiers__identifier_value",
    )
    inlines = [PlayerAliasInline, PlayerSourceIdentifierInline]


@admin.register(PlayerAlias)
class PlayerAliasAdmin(TimeStampedAdmin):
    list_display = ("alias", "player", "source", "context", "created_at")
    list_filter = ("source",)
    search_fields = ("alias", "normalized_alias", "player__first_name", "player__last_name")


@admin.register(PlayerSourceIdentifier)
class PlayerSourceIdentifierAdmin(TimeStampedAdmin):
    list_display = ("player", "source", "identifier_type", "identifier_value", "created_at")
    list_filter = ("source", "identifier_type")
    search_fields = ("identifier_value", "player__first_name", "player__last_name")


@admin.register(PlayerSourceRow)
class PlayerSourceRowAdmin(TimeStampedAdmin):
    list_display = ("player", "source", "source_filename", "row_number", "imported_by", "imported_at")
    list_filter = ("source", "imported_at")
    search_fields = ("player__first_name", "player__last_name", "source_filename")


@admin.register(PlayerTag)
class PlayerTagAdmin(TimeStampedAdmin):
    list_display = ("name", "slug", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
