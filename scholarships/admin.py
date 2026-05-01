from django.contrib import admin

from scholarships.models import (
    ScholarshipApplicantProfile,
    ScholarshipApplication,
    ScholarshipCycle,
    ScholarshipReference,
)


class ScholarshipReferenceInline(admin.TabularInline):
    model = ScholarshipReference
    extra = 0


@admin.register(ScholarshipCycle)
class ScholarshipCycleAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "status", "application_open_date", "application_deadline")
    list_filter = ("status", "year")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "year")


@admin.register(ScholarshipApplicantProfile)
class ScholarshipApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "created_at")
    search_fields = ("full_name", "email")


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ("player_full_name", "cycle", "status", "submitted_at", "updated_at")
    list_filter = ("cycle", "status", "submitted_at")
    search_fields = ("player_full_name", "vcb_team_or_program", "applicant__full_name", "applicant__email")
    readonly_fields = ("submitted_at", "locked_at", "created_at", "updated_at")
    inlines = [ScholarshipReferenceInline]


@admin.register(ScholarshipReference)
class ScholarshipReferenceAdmin(admin.ModelAdmin):
    list_display = ("application", "display_order", "name", "email")
    search_fields = ("name", "email", "application__player_full_name")

