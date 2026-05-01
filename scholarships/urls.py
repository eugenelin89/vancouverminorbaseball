from django.urls import path

from scholarships.views import (
    ApplicantDashboardView,
    ApplicantSignupView,
    ScholarshipApplicationCreateView,
    ScholarshipApplicationDetailView,
    ScholarshipApplicationUpdateView,
    ScholarshipLoginView,
    ScholarshipLogoutView,
    ScholarshipOverviewView,
    StaffApplicationDetailView,
    StaffApplicationDownloadView,
    StaffApplicationListView,
    StaffCycleDownloadView,
)


app_name = "scholarships"

urlpatterns = [
    path("", ScholarshipOverviewView.as_view(), name="overview"),
    path("signup/", ApplicantSignupView.as_view(), name="signup"),
    path("login/", ScholarshipLoginView.as_view(), name="login"),
    path("logout/", ScholarshipLogoutView.as_view(), name="logout"),
    path("dashboard/", ApplicantDashboardView.as_view(), name="dashboard"),
    path("apply/", ScholarshipApplicationCreateView.as_view(), name="apply"),
    path("application/<int:pk>/", ScholarshipApplicationDetailView.as_view(), name="application-detail"),
    path("application/<int:pk>/edit/", ScholarshipApplicationUpdateView.as_view(), name="application-edit"),
    path("staff/applications/", StaffApplicationListView.as_view(), name="staff-application-list"),
    path("staff/applications/<int:pk>/", StaffApplicationDetailView.as_view(), name="staff-application-detail"),
    path("staff/applications/<int:pk>/download/", StaffApplicationDownloadView.as_view(), name="staff-application-download"),
    path("staff/cycles/<slug:slug>/download/", StaffCycleDownloadView.as_view(), name="staff-cycle-download"),
]

