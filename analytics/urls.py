from django.urls import path

from analytics.views import (
    PlayerImportConfirmView,
    PlayerImportConflictView,
    PlayerImportDetailView,
    PlayerImportListView,
    PlayerImportPreviewView,
    PlayerImportUploadView,
)


app_name = "analytics"

urlpatterns = [
    path("imports/", PlayerImportListView.as_view(), name="import-list"),
    path("imports/new/", PlayerImportUploadView.as_view(), name="import-new"),
    path("imports/<int:pk>/preview/", PlayerImportPreviewView.as_view(), name="import-preview"),
    path("imports/<int:pk>/conflicts/", PlayerImportConflictView.as_view(), name="import-conflicts"),
    path("imports/<int:pk>/confirm/", PlayerImportConfirmView.as_view(), name="import-confirm"),
    path("imports/<int:pk>/", PlayerImportDetailView.as_view(), name="import-detail"),
]
