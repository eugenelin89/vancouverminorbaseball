import csv
import io
import json
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, Prefetch

from .models import Draft, DraftAction, DraftActionType, DraftPlayer, DraftStatus, DraftTeam


REQUIRED_PLAYER_HEADERS = {"first", "last"}


@dataclass
class ImportRowResult:
    row_number: int
    imported: bool
    errors: list[str]
    cleaned_row: dict


def _normalize_header(header):
    return " ".join((header or "").strip().split()).lower()


def _clean_cell(value):
    return "" if value is None else str(value).strip()


def parse_player_csv(file_obj):
    raw_data = file_obj.read()
    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode("utf-8-sig")
    file_obj.seek(0)
    csv_stream = io.StringIO(raw_data)
    reader = csv.DictReader(csv_stream)
    if not reader.fieldnames:
        raise ValidationError("The uploaded CSV does not contain a header row.")

    normalized_headers = {}
    duplicate_headers = []
    stripped_headers = []
    for header in reader.fieldnames:
        stripped = (header or "").strip()
        if not stripped:
            duplicate_headers.append("<blank header>")
            continue
        normalized = _normalize_header(header)
        if normalized in normalized_headers:
            duplicate_headers.append(stripped)
        normalized_headers[normalized] = stripped
        stripped_headers.append(stripped)

    if duplicate_headers:
        raise ValidationError(
            "Duplicate or blank column headers were found: " + ", ".join(sorted(set(duplicate_headers)))
        )

    missing = [name.title() for name in REQUIRED_PLAYER_HEADERS if name not in normalized_headers]
    if missing:
        raise ValidationError("Missing required column(s): " + ", ".join(missing))

    preview_rows = []
    for index, row in enumerate(reader, start=2):
        original_row = {}
        cleaned_row = {}
        for original_header in reader.fieldnames:
            value = row.get(original_header, "")
            original_row[original_header] = value
            cleaned_row[(original_header or "").strip()] = _clean_cell(value)

        first_name = cleaned_row.get(normalized_headers["first"], "")
        last_name = cleaned_row.get(normalized_headers["last"], "")
        errors = []
        if not first_name:
            errors.append("Missing First")
        if not last_name:
            errors.append("Missing Last")

        preview_rows.append(
            ImportRowResult(
                row_number=index,
                imported=not errors,
                errors=errors,
                cleaned_row={
                    "first_name": first_name,
                    "last_name": last_name,
                    "extra_data": {
                        key: value
                        for key, value in cleaned_row.items()
                        if key and _normalize_header(key) not in REQUIRED_PLAYER_HEADERS and value != ""
                    },
                    "imported_row": original_row,
                },
            )
        )

    return {
        "headers": stripped_headers,
        "rows": preview_rows,
        "normalized_headers": normalized_headers,
    }


def serialize_import_preview(preview):
    return json.dumps(
        {
            "headers": preview["headers"],
            "rows": [
                {
                    "row_number": row.row_number,
                    "imported": row.imported,
                    "errors": row.errors,
                    "cleaned_row": row.cleaned_row,
                }
                for row in preview["rows"]
            ],
        }
    )


def deserialize_import_preview(payload):
    data = json.loads(payload)
    data["rows"] = [ImportRowResult(**row) for row in data["rows"]]
    return data


@transaction.atomic
def create_draft(*, name, year, division, description, created_by, teams):
    draft = Draft.objects.create(
        name=name,
        year=year,
        division=division,
        description=description,
        created_by=created_by,
    )
    for index, team_data in enumerate(teams, start=1):
        team = DraftTeam.objects.create(
            draft=draft,
            name=team_data["name"],
            color=team_data.get("color", ""),
            display_order=index,
        )
        DraftAction.objects.create(
            draft=draft,
            action_type=DraftActionType.TEAM_CREATED,
            to_team=team,
            actor=created_by,
            metadata={"team_name": team.name, "display_order": team.display_order, "color": team.color},
        )
    return draft


@transaction.atomic
def import_players(*, draft, rows, actor):
    results = {"rows_processed": len(rows), "rows_imported": 0, "rows_rejected": 0, "errors": []}
    existing_names = {
        (player.first_name.casefold(), player.last_name.casefold()): player.id
        for player in draft.players.only("id", "first_name", "last_name")
    }

    for row in rows:
        first_name = row.cleaned_row["first_name"]
        last_name = row.cleaned_row["last_name"]
        if row.errors:
            results["rows_rejected"] += 1
            results["errors"].append(f"Row {row.row_number}: {'; '.join(row.errors)}")
            continue

        name_key = (first_name.casefold(), last_name.casefold())
        if name_key in existing_names:
            results["rows_rejected"] += 1
            results["errors"].append(f"Row {row.row_number}: duplicate player '{first_name} {last_name}'")
            continue

        player = DraftPlayer.objects.create(
            draft=draft,
            first_name=first_name,
            last_name=last_name,
            full_name=f"{first_name} {last_name}",
            extra_data=row.cleaned_row["extra_data"],
            imported_row=row.cleaned_row["imported_row"],
        )
        existing_names[name_key] = player.id
        DraftAction.objects.create(
            draft=draft,
            action_type=DraftActionType.PLAYER_IMPORTED,
            player=player,
            actor=actor,
            metadata={"row_number": row.row_number, "extra_keys": sorted(player.extra_data.keys())},
        )
        results["rows_imported"] += 1

    results["rows_rejected"] = results["rows_processed"] - results["rows_imported"]
    return results


def _ensure_draft_open(draft):
    if draft.status != DraftStatus.OPEN:
        raise ValidationError("The draft must be open before players can be assigned or moved.")


def _lock_player_for_draft(draft, player_id):
    return (
        DraftPlayer.objects.select_for_update()
        .select_related("current_team", "draft")
        .get(draft=draft, pk=player_id)
    )


def _lock_team_for_draft(draft, team_id):
    return DraftTeam.objects.select_for_update().get(draft=draft, pk=team_id)


@transaction.atomic
def draft_player(*, draft, player_id, team_id, actor):
    _ensure_draft_open(draft)
    player = _lock_player_for_draft(draft, player_id)
    if player.current_team_id:
        raise ValidationError(f"{player.full_name} has already been drafted.")
    team = _lock_team_for_draft(draft, team_id)
    next_pick = (
        DraftAction.objects.select_for_update()
        .filter(draft=draft, action_type=DraftActionType.PLAYER_DRAFTED)
        .aggregate(max_pick=Max("pick_number"))
    )["max_pick"] or 0
    player.current_team = team
    player.save(update_fields=["current_team", "updated_at"])
    action = DraftAction.objects.create(
        draft=draft,
        action_type=DraftActionType.PLAYER_DRAFTED,
        player=player,
        from_team=None,
        to_team=team,
        actor=actor,
        pick_number=next_pick + 1,
        metadata={"player_name": player.full_name},
    )
    return action


@transaction.atomic
def move_player(*, draft, player_id, to_team_id, actor):
    _ensure_draft_open(draft)
    player = _lock_player_for_draft(draft, player_id)
    if not player.current_team_id:
        raise ValidationError(f"{player.full_name} is not currently assigned to a team.")
    from_team = player.current_team
    to_team = _lock_team_for_draft(draft, to_team_id)
    if from_team.id == to_team.id:
        raise ValidationError("Choose a different destination team.")
    player.current_team = to_team
    player.save(update_fields=["current_team", "updated_at"])
    return DraftAction.objects.create(
        draft=draft,
        action_type=DraftActionType.PLAYER_MOVED,
        player=player,
        from_team=from_team,
        to_team=to_team,
        actor=actor,
        metadata={"player_name": player.full_name},
    )


@transaction.atomic
def remove_player_from_team(*, draft, player_id, actor):
    _ensure_draft_open(draft)
    player = _lock_player_for_draft(draft, player_id)
    if not player.current_team_id:
        raise ValidationError(f"{player.full_name} is already in the available pool.")
    from_team = player.current_team
    player.current_team = None
    player.save(update_fields=["current_team", "updated_at"])
    return DraftAction.objects.create(
        draft=draft,
        action_type=DraftActionType.PLAYER_REMOVED,
        player=player,
        from_team=from_team,
        actor=actor,
        metadata={"player_name": player.full_name},
    )


@transaction.atomic
def trade_players(*, draft, team_one_id, team_two_id, team_one_player_ids, team_two_player_ids, actor):
    _ensure_draft_open(draft)
    if team_one_id == team_two_id:
        raise ValidationError("Trades require two different teams.")

    team_one = _lock_team_for_draft(draft, team_one_id)
    team_two = _lock_team_for_draft(draft, team_two_id)
    team_one_players = list(
        DraftPlayer.objects.select_for_update().filter(draft=draft, current_team=team_one, pk__in=team_one_player_ids)
    )
    team_two_players = list(
        DraftPlayer.objects.select_for_update().filter(draft=draft, current_team=team_two, pk__in=team_two_player_ids)
    )

    if not team_one_players or not team_two_players:
        raise ValidationError("Select at least one player from each team.")

    for player in team_one_players:
        player.current_team = team_two
        player.save(update_fields=["current_team", "updated_at"])
    for player in team_two_players:
        player.current_team = team_one
        player.save(update_fields=["current_team", "updated_at"])

    return DraftAction.objects.create(
        draft=draft,
        action_type=DraftActionType.PLAYER_TRADED,
        actor=actor,
        from_team=team_one,
        to_team=team_two,
        metadata={
            "team_one_id": team_one.id,
            "team_two_id": team_two.id,
            "team_one_player_ids": [player.id for player in team_one_players],
            "team_two_player_ids": [player.id for player in team_two_players],
            "team_one_players": [player.full_name for player in team_one_players],
            "team_two_players": [player.full_name for player in team_two_players],
        },
    )


@transaction.atomic
def change_draft_status(*, draft, new_status, actor):
    if new_status not in DraftStatus.values:
        raise ValidationError("Invalid draft status.")
    previous_status = draft.status
    if previous_status == new_status:
        raise ValidationError("The draft is already in that state.")
    draft.status = new_status
    draft.save(update_fields=["status", "updated_at"])
    action_map = {
        DraftStatus.OPEN: DraftActionType.DRAFT_OPENED if previous_status == DraftStatus.DRAFT else DraftActionType.DRAFT_REOPENED,
        DraftStatus.CLOSED: DraftActionType.DRAFT_CLOSED,
    }
    action_type = action_map.get(new_status)
    if action_type:
        DraftAction.objects.create(
            draft=draft,
            action_type=action_type,
            actor=actor,
            metadata={"previous_status": previous_status, "new_status": new_status},
        )
    return draft


@transaction.atomic
def revert_action(*, action, actor):
    action = DraftAction.objects.select_for_update().select_related("draft", "player", "from_team", "to_team").get(pk=action.pk)
    if action.is_reverted:
        raise ValidationError("This action has already been reverted.")
    latest_revertable = DraftAction.objects.filter(
        draft=action.draft,
        is_reverted=False,
        action_type__in=[
            DraftActionType.PLAYER_DRAFTED,
            DraftActionType.PLAYER_MOVED,
            DraftActionType.PLAYER_REMOVED,
            DraftActionType.PLAYER_TRADED,
            DraftActionType.DRAFT_OPENED,
            DraftActionType.DRAFT_CLOSED,
            DraftActionType.DRAFT_REOPENED,
        ],
    ).order_by("-created_at", "-id").first()
    if not latest_revertable or latest_revertable.id != action.id:
        raise ValidationError("Only the most recent reversible action can be undone safely.")
    draft = Draft.objects.select_for_update().get(pk=action.draft_id)
    if action.action_type in {DraftActionType.PLAYER_DRAFTED, DraftActionType.PLAYER_MOVED, DraftActionType.PLAYER_REMOVED}:
        player = _lock_player_for_draft(draft, action.player_id)
        player.current_team = action.from_team
        player.save(update_fields=["current_team", "updated_at"])
    elif action.action_type == DraftActionType.PLAYER_TRADED:
        team_one = _lock_team_for_draft(draft, action.metadata["team_one_id"])
        team_two = _lock_team_for_draft(draft, action.metadata["team_two_id"])
        team_one_players = DraftPlayer.objects.select_for_update().filter(
            draft=draft, pk__in=action.metadata.get("team_one_player_ids", [])
        )
        team_two_players = DraftPlayer.objects.select_for_update().filter(
            draft=draft, pk__in=action.metadata.get("team_two_player_ids", [])
        )
        for player in team_one_players:
            player.current_team = team_one
            player.save(update_fields=["current_team", "updated_at"])
        for player in team_two_players:
            player.current_team = team_two
            player.save(update_fields=["current_team", "updated_at"])
    elif action.action_type in {
        DraftActionType.DRAFT_OPENED,
        DraftActionType.DRAFT_CLOSED,
        DraftActionType.DRAFT_REOPENED,
    }:
        draft.status = action.metadata["previous_status"]
        draft.save(update_fields=["status", "updated_at"])
    else:
        raise ValidationError("This action cannot be reverted.")

    action.is_reverted = True
    action.save(update_fields=["is_reverted"])
    return DraftAction.objects.create(
        draft=draft,
        action_type=DraftActionType.DRAFT_PICK_REVERTED,
        actor=actor,
        player=action.player,
        from_team=action.to_team,
        to_team=action.from_team,
        metadata={"reverted_action_id": action.id, "reverted_action_type": action.action_type},
    )


def get_command_center_data(*, draft, search="", team_filter="", sort="name", extra_columns=None):
    extra_columns = extra_columns or []
    teams = list(
        draft.teams.prefetch_related(
            Prefetch("players", queryset=DraftPlayer.objects.order_by("last_name", "first_name"))
        )
    )
    players = list(draft.players.select_related("current_team"))
    available_players = [player for player in players if player.current_team_id is None]

    if search:
        term = search.casefold()
        available_players = [
            player
            for player in available_players
            if term in player.full_name.casefold()
            or any(term in str(value).casefold() for value in player.extra_data.values())
        ]

    if team_filter:
        available_players = [player for player in available_players if str(player.current_team_id or "") == team_filter]

    available_extra_keys = sorted(
        {
            key
            for player in players
            for key in player.extra_data.keys()
        }
    )
    if sort == "name":
        available_players.sort(key=lambda player: (player.last_name.casefold(), player.first_name.casefold()))
    elif sort in available_extra_keys:
        available_players.sort(key=lambda player: str(player.extra_data.get(sort, "")).casefold())

    timeline = list(draft.actions.select_related("player", "from_team", "to_team", "actor")[:30])
    draft_history = list(
        draft.actions.filter(action_type=DraftActionType.PLAYER_DRAFTED)
        .select_related("player", "to_team", "actor")[:50]
    )
    return {
        "teams": teams,
        "available_players": available_players,
        "timeline": timeline,
        "draft_history": draft_history,
        "available_extra_keys": available_extra_keys,
        "selected_extra_columns": [column for column in extra_columns if column in available_extra_keys],
    }
