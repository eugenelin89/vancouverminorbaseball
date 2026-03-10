from django.urls import path

from .views import (
    DraftAssignPlayerView,
    DraftCommandCenterView,
    DraftCreateView,
    DraftExportView,
    DraftImportView,
    DraftListView,
    DraftMovePlayerView,
    DraftRemovePlayerView,
    DraftStatusUpdateView,
    DraftTradeView,
    DraftUndoView,
    PublicDraftLiveView,
)

app_name = "drafts"

urlpatterns = [
    path("", DraftListView.as_view(), name="list"),
    path("new/", DraftCreateView.as_view(), name="create"),
    path("live/<slug:slug>/", PublicDraftLiveView.as_view(), name="public-live"),
    path("<slug:slug>/", DraftCommandCenterView.as_view(), name="command-center"),
    path("<slug:slug>/import/", DraftImportView.as_view(), name="import"),
    path("<slug:slug>/trade/", DraftTradeView.as_view(), name="trade"),
    path("<slug:slug>/export/", DraftExportView.as_view(), name="export"),
    path("<slug:slug>/assign/", DraftAssignPlayerView.as_view(), name="assign-player"),
    path("<slug:slug>/move/", DraftMovePlayerView.as_view(), name="move-player"),
    path("<slug:slug>/remove/", DraftRemovePlayerView.as_view(), name="remove-player"),
    path("<slug:slug>/undo/", DraftUndoView.as_view(), name="undo-action"),
    path("<slug:slug>/status/", DraftStatusUpdateView.as_view(), name="status-update"),
]
