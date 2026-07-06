from django.contrib import admin

from accounts.models import AccountProfile


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
