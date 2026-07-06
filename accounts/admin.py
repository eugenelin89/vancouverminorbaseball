from django.contrib import admin

from accounts.models import AccountProfile, UserPlayerLink


class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


@admin.register(AccountProfile)
class AccountProfileAdmin(TimeStampedAdmin):
    list_display = (
        "user",
        "role",
        "must_change_password",
        "created_from_import",
        "activated_at",
        "deactivated_at",
    )
    list_filter = ("role", "must_change_password", "created_from_import", "activated_at", "deactivated_at")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    readonly_fields = TimeStampedAdmin.readonly_fields
    exclude = ("metadata",)


@admin.register(UserPlayerLink)
class UserPlayerLinkAdmin(TimeStampedAdmin):
    list_display = (
        "user",
        "player",
        "relationship",
        "is_primary",
        "is_active",
        "created_from_import",
        "import_batch",
        "created_at",
        "updated_at",
    )
    list_filter = ("relationship", "is_primary", "is_active", "created_from_import", "import_batch")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "player__first_name",
        "player__last_name",
        "player__preferred_name",
    )
    autocomplete_fields = ("user", "player", "import_batch")
    readonly_fields = TimeStampedAdmin.readonly_fields
    exclude = ("metadata",)
