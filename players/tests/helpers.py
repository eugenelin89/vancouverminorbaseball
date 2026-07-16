from datetime import date

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import AccountProfile, UserPlayerLink
from players.models import (
    Player,
    PlayerAlias,
    PlayerImportBatch,
    PlayerImportStatus,
    PlayerSourceIdentifier,
    PlayerSourceRow,
    PlayerTag,
)
from players.services import import_service
from players.services.identity_service import add_source_identifier, create_player
from players.services.import_service import (
    ACTION_CREATE,
    ACTION_ERROR,
    ACTION_NEEDS_REVIEW,
    ACTION_SKIP,
    ACTION_UPDATE,
    MAX_CSV_ROWS,
    MAX_CSV_UPLOAD_BYTES,
    RESOLUTION_ACTION_CREATE_NEW,
    RESOLUTION_ACTION_USE_CANDIDATE,
    SOURCE_MEMBER_LIST,
    SOURCE_ROSTER_DETAIL,
    build_import_preview,
    commit_import_batch,
    create_import_batch,
    parse_player_csv,
    suggest_mapping,
)
from players.services.matching_service import (
    MATCH_AMBIGUOUS,
    MATCH_EXACT,
    MATCH_HIGH_CONFIDENCE,
    MATCH_NO_MATCH,
    find_player_match,
    match_by_identifier,
    match_by_name_and_birthdate,
)
from players.services.tag_service import (
    active_tags,
    assign_tag,
    players_with_tag,
    remove_tag,
)
from seasons.models import PlayerRosterMembership, SeasonTeam
from seasons.services.season_service import create_season

User = get_user_model()

__all__ = (
    "ACTION_CREATE",
    "ACTION_ERROR",
    "ACTION_NEEDS_REVIEW",
    "ACTION_SKIP",
    "ACTION_UPDATE",
    "AccountProfile",
    "IntegrityError",
    "MATCH_AMBIGUOUS",
    "MATCH_EXACT",
    "MATCH_HIGH_CONFIDENCE",
    "MATCH_NO_MATCH",
    "MAX_CSV_ROWS",
    "MAX_CSV_UPLOAD_BYTES",
    "PermissionDenied",
    "Player",
    "PlayerAlias",
    "PlayerImportBatch",
    "PlayerImportStatus",
    "PlayerRosterMembership",
    "PlayerSourceIdentifier",
    "PlayerSourceRow",
    "PlayerTag",
    "RESOLUTION_ACTION_CREATE_NEW",
    "RESOLUTION_ACTION_USE_CANDIDATE",
    "SOURCE_MEMBER_LIST",
    "SOURCE_ROSTER_DETAIL",
    "SeasonTeam",
    "SimpleUploadedFile",
    "TestCase",
    "User",
    "UserPlayerLink",
    "ValidationError",
    "active_tags",
    "add_source_identifier",
    "admin",
    "apps",
    "assign_tag",
    "build_import_preview",
    "commit_import_batch",
    "create_import_batch",
    "create_player",
    "create_season",
    "date",
    "find_player_match",
    "import_service",
    "match_by_identifier",
    "match_by_name_and_birthdate",
    "parse_player_csv",
    "players_with_tag",
    "remove_tag",
    "suggest_mapping",
    "transaction",
)
