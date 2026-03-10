from django.contrib import admin

from .models import Draft, DraftAction, DraftPlayer, DraftTeam


class DraftTeamInline(admin.TabularInline):
    model = DraftTeam
    extra = 0


@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "division", "status", "created_by", "updated_at")
    list_filter = ("status", "year", "division")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "division", "description")
    inlines = [DraftTeamInline]


@admin.register(DraftTeam)
class DraftTeamAdmin(admin.ModelAdmin):
    list_display = ("name", "draft", "display_order", "color", "created_at")
    list_filter = ("draft",)
    search_fields = ("name", "draft__name")


@admin.register(DraftPlayer)
class DraftPlayerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "draft", "current_team", "updated_at")
    list_filter = ("draft", "current_team")
    search_fields = ("full_name", "first_name", "last_name")


@admin.register(DraftAction)
class DraftActionAdmin(admin.ModelAdmin):
    list_display = ("action_type", "draft", "player", "from_team", "to_team", "pick_number", "actor", "created_at")
    list_filter = ("action_type", "draft")
    search_fields = ("draft__name", "player__full_name", "from_team__name", "to_team__name")
    ordering = ("-created_at", "-id")
