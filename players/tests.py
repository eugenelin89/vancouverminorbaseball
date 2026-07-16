from datetime import date

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import admin
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import AccountProfile, UserPlayerLink
from players.models import Player, PlayerAlias, PlayerImportBatch, PlayerImportStatus, PlayerSourceIdentifier, PlayerSourceRow, PlayerTag
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
from players.services.tag_service import active_tags, assign_tag, players_with_tag, remove_tag
from seasons.models import PlayerRosterMembership, SeasonTeam
from seasons.services.season_service import create_season


User = get_user_model()


class PlayerModelTests(TestCase):
    def test_player_full_name_and_display_name(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin", preferred_name="Gene")

        self.assertEqual(player.full_name, "Eugene Lin")
        self.assertEqual(player.display_name, "Gene Lin")
        self.assertEqual(str(player), "Gene Lin")

    def test_player_model_has_no_pdp_dependency(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        related_models = [
            field.remote_field.model
            for field in Player._meta.fields
            if getattr(field, "remote_field", None) and field.remote_field
        ]

        self.assertEqual(related_models, [])
        self.assertEqual(player.full_name, "Eugene Lin")

    def test_alias_saves_normalized_value(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        alias = PlayerAlias.objects.create(player=player, alias="  Gene   LIN  ", source="manual")

        self.assertEqual(alias.normalized_alias, "gene lin")

    def test_duplicate_alias_for_same_player_is_rejected(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        PlayerAlias.objects.create(player=player, alias="Gene Lin")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PlayerAlias.objects.create(player=player, alias=" gene   lin ")

    def test_same_alias_can_exist_for_different_players(self):
        player_one = Player.objects.create(first_name="Eugene", last_name="Lin")
        player_two = Player.objects.create(first_name="Gene", last_name="Lynn")

        PlayerAlias.objects.create(player=player_one, alias="Gene")
        PlayerAlias.objects.create(player=player_two, alias="Gene")

        self.assertEqual(PlayerAlias.objects.filter(normalized_alias="gene").count(), 2)

    def test_source_identifier_uniqueness_uses_source_type_and_value(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        PlayerSourceIdentifier.objects.create(
            player=player,
            source="Registration",
            identifier_type="Registrant ID",
            identifier_value=" ABC-123 ",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PlayerSourceIdentifier.objects.create(
                    player=player,
                    source="registration",
                    identifier_type="registrant id",
                    identifier_value="abc-123",
                )

    def test_source_row_preserves_provenance(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        row = PlayerSourceRow.objects.create(
            player=player,
            source="Roster Import",
            source_filename="roster.csv",
            row_number=4,
            original_row={"First": "Eugene", "Last": "Lin", "Extra": "Value"},
            unmapped_fields={"Extra": "Value"},
        )

        self.assertEqual(row.source, "roster import")
        self.assertEqual(row.original_row["First"], "Eugene")
        self.assertEqual(row.unmapped_fields, {"Extra": "Value"})

    def test_tag_assignment_and_removal(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        tag = PlayerTag.objects.create(name="Strong Arm")

        tag.players.add(player)
        self.assertEqual(list(player.tags.all()), [tag])

        tag.players.remove(player)
        self.assertFalse(player.tags.exists())


class PlayerServiceTests(TestCase):
    def test_create_player_service_creates_canonical_player(self):
        player = create_player(first_name="Eugene", last_name="Lin", division="13U")

        self.assertEqual(player.full_name, "Eugene Lin")
        self.assertEqual(player.division, "13U")

    def test_add_source_identifier_service_normalizes_values(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        identifier = add_source_identifier(
            player,
            source="Registration",
            identifier_type="Registrant ID",
            identifier_value=" ABC-123 ",
        )

        self.assertEqual(identifier.source, "registration")
        self.assertEqual(identifier.identifier_type, "registrant id")
        self.assertEqual(identifier.identifier_value, "abc-123")

    def test_match_by_identifier_returns_exact_match(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        add_source_identifier(player, "registration", "registrant_id", "abc-123")

        result = match_by_identifier("Registration", "Registrant_ID", " ABC-123 ")

        self.assertEqual(result.status, MATCH_EXACT)
        self.assertEqual(result.player, player)

    def test_name_and_birthdate_returns_high_confidence_match(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate=date(2012, 5, 1))

        result = match_by_name_and_birthdate("eugene", "lin", date(2012, 5, 1))

        self.assertEqual(result.status, MATCH_HIGH_CONFIDENCE)
        self.assertEqual(result.player, player)

    def test_duplicate_name_candidates_return_ambiguous(self):
        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")

        result = find_player_match(
            {
                "first_name": "Eugene",
                "last_name": "Lin",
                "birth_year": 2012,
                "division": "13U",
            }
        )

        self.assertEqual(result.status, MATCH_AMBIGUOUS)
        self.assertEqual(len(result.candidates), 2)

    def test_unknown_identity_returns_no_match(self):
        result = find_player_match({"first_name": "Unknown", "last_name": "Player"})

        self.assertEqual(result.status, MATCH_NO_MATCH)
        self.assertIsNone(result.player)

    def test_tag_service_assigns_removes_and_filters_tags(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")

        tag = assign_tag(player, "Strong Arm")

        self.assertEqual(tag.slug, "strong-arm")
        self.assertEqual(list(players_with_tag("strong-arm")), [player])
        self.assertEqual(list(active_tags()), [tag])

        remove_tag(player, "Strong Arm")
        self.assertFalse(players_with_tag("strong-arm").exists())

    def test_import_service_builds_identity_payload(self):
        row = {"First": " Eugene ", "Last": " Lin ", "Division": "13U", "Unused": "x"}
        payload = import_service.build_identity_payload(
            row,
            mapping={"first_name": "First", "last_name": "Last", "division": "Division"},
        )

        self.assertEqual(payload["first_name"], "Eugene")
        self.assertEqual(payload["last_name"], "Lin")
        self.assertEqual(payload["division"], "13U")
        self.assertEqual(import_service.normalize_header(" First   Name "), "first name")


class PlayerIntegrationTests(TestCase):
    def test_players_app_is_installed(self):
        self.assertTrue(apps.is_installed("players"))

    def test_player_models_are_registered_in_admin(self):
        for model in [Player, PlayerAlias, PlayerImportBatch, PlayerSourceIdentifier, PlayerSourceRow, PlayerTag]:
            self.assertIn(model, admin.site._registry)


class PlayerImportWorkflowTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="testpass", is_staff=True)
        self.user = User.objects.create_user(username="user", password="testpass")
        self.season = create_season(key="2026-spring", name="2026 Spring", is_current=True)

    def upload(self, name="member list for 13u house.csv", body=b"First,Last,Gender,Division,Team\nEugene,Lin,M,13U,Expos\n"):
        return SimpleUploadedFile(name, body, content_type="text/csv")

    def test_parse_csv_handles_bom_and_preserves_rows(self):
        parsed = parse_player_csv(self.upload(body="\ufeffFirst,Last,Extra\nEugene,Lin,Value\n".encode("utf-8")))

        self.assertEqual(parsed.headers, ["First", "Last", "Extra"])
        self.assertEqual(parsed.rows[0]["row_number"], 2)
        self.assertEqual(parsed.rows[0]["original_row"]["Extra"], "Value")

    def test_parse_csv_rejects_duplicate_and_blank_headers(self):
        with self.assertRaises(ValidationError):
            parse_player_csv(self.upload(body=b"First, first\nA,B\n"))
        with self.assertRaises(ValidationError):
            parse_player_csv(self.upload(body=b"First,\nA,B\n"))

    def test_parse_csv_rejects_oversized_uploads(self):
        with self.assertRaises(ValidationError):
            parse_player_csv(self.upload(body=b"First,Last\n" + (b"A,B\n" * ((MAX_CSV_UPLOAD_BYTES // 4) + 1))))

    def test_parse_csv_rejects_too_many_rows(self):
        rows = b"".join([b"A,B\n" for _ in range(MAX_CSV_ROWS + 1)])

        with self.assertRaises(ValidationError):
            parse_player_csv(self.upload(body=b"First,Last\n" + rows))

    def test_suggest_mapping_for_member_and_roster_headers(self):
        member_mapping = suggest_mapping(["First", "Last", "Gender", "Team"], source=SOURCE_MEMBER_LIST)
        roster_mapping = suggest_mapping(["First Name", "Last Name", "DOB", "Registration ID"], source=SOURCE_ROSTER_DETAIL)

        self.assertEqual(member_mapping["first_name"], "First")
        self.assertEqual(member_mapping["team_name"], "Team")
        self.assertEqual(roster_mapping["birthdate"], "DOB")
        self.assertEqual(roster_mapping["registration_id"], "Registration ID")

    def test_create_import_batch_requires_staff(self):
        with self.assertRaises(PermissionDenied):
            create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.user)

    def test_preview_classifies_new_player_as_create(self):
        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
        preview = batch.preview_snapshot["preview"]

        self.assertEqual(preview["rows"][0]["action"], ACTION_CREATE)
        self.assertEqual(preview["summary"]["rows_create"], 1)
        self.assertEqual(preview["season"]["name"], "2026 Spring")

    def test_create_import_batch_requires_active_season(self):
        inactive = create_season(key="2025-spring", name="2025 Spring", is_active=False)

        with self.assertRaises(ValidationError):
            create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff)
        with self.assertRaises(ValidationError):
            create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=inactive)

    def test_preview_classifies_source_identifier_match_as_update(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        add_source_identifier(player, SOURCE_ROSTER_DETAIL, "registration_id", "REG-1")
        batch = create_import_batch(
            file_obj=self.upload(
                name="roster detail for 13u house.csv",
                body=b"First Name,Last Name,Registration ID,Division,Team\nEugene,Lin,REG-1,13U,Expos\n",
            ),
            source=SOURCE_ROSTER_DETAIL,
            uploaded_by=self.staff,
            season=self.season,
        )

        row = batch.preview_snapshot["preview"]["rows"][0]
        self.assertEqual(row["action"], ACTION_UPDATE)
        self.assertEqual(row["matched_player_id"], player.id)

    def test_preview_tries_all_source_identifiers(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        add_source_identifier(player, SOURCE_ROSTER_DETAIL, "registrant_id", "MEM-1")
        batch = create_import_batch(
            file_obj=self.upload(
                name="roster detail for 13u house.csv",
                body=b"First Name,Last Name,Registration ID,Registrant ID,Division,Team\nEugene,Lin,NO-MATCH,MEM-1,13U,Expos\n",
            ),
            source=SOURCE_ROSTER_DETAIL,
            uploaded_by=self.staff,
            season=self.season,
        )

        row = batch.preview_snapshot["preview"]["rows"][0]
        self.assertEqual(row["action"], ACTION_UPDATE)
        self.assertEqual(row["matched_player_id"], player.id)

    def test_preview_marks_conflicting_source_identifiers_as_ambiguous(self):
        player_one = Player.objects.create(first_name="Eugene", last_name="Lin")
        player_two = Player.objects.create(first_name="Gene", last_name="Lynn")
        add_source_identifier(player_one, SOURCE_ROSTER_DETAIL, "registration_id", "REG-1")
        add_source_identifier(player_two, SOURCE_ROSTER_DETAIL, "registrant_id", "MEM-1")
        batch = create_import_batch(
            file_obj=self.upload(
                name="roster detail for 13u house.csv",
                body=b"First Name,Last Name,Registration ID,Registrant ID,Division,Team\nEugene,Lin,REG-1,MEM-1,13U,Expos\n",
            ),
            source=SOURCE_ROSTER_DETAIL,
            uploaded_by=self.staff,
            season=self.season,
        )

        row = batch.preview_snapshot["preview"]["rows"][0]
        self.assertEqual(row["action"], ACTION_NEEDS_REVIEW)
        self.assertEqual(row["match_status"], MATCH_AMBIGUOUS)
        self.assertCountEqual(row["candidate_ids"], [player_one.id, player_two.id])

    def test_preview_high_confidence_match_and_conflict(self):
        player = Player.objects.create(
            first_name="Eugene",
            last_name="Lin",
            birthdate="2012-05-01",
            preferred_name="Old",
            team_name="Existing Team",
        )
        batch = create_import_batch(
            file_obj=self.upload(
                name="roster detail for 13u house.csv",
                body=b"First Name,Last Name,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,Gene,13U,New Team\n",
            ),
            source=SOURCE_ROSTER_DETAIL,
            uploaded_by=self.staff,
            season=self.season,
        )

        row = batch.preview_snapshot["preview"]["rows"][0]
        self.assertEqual(row["action"], ACTION_NEEDS_REVIEW)
        self.assertEqual(row["matched_player_id"], player.id)
        self.assertEqual(row["field_conflicts"][0]["field_name"], "preferred_name")

    def test_preview_treats_name_difference_on_identifier_match_as_conflict(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin")
        add_source_identifier(player, SOURCE_ROSTER_DETAIL, "registration_id", "REG-1")
        batch = create_import_batch(
            file_obj=self.upload(
                name="roster detail for 13u house.csv",
                body=b"First Name,Last Name,Registration ID,Division,Team\nGene,Lin,REG-1,13U,Expos\n",
            ),
            source=SOURCE_ROSTER_DETAIL,
            uploaded_by=self.staff,
            season=self.season,
        )

        row = batch.preview_snapshot["preview"]["rows"][0]
        self.assertEqual(row["action"], ACTION_NEEDS_REVIEW)
        self.assertEqual(row["field_conflicts"][0]["field_name"], "first_name")

    def test_preview_ambiguous_match_and_missing_name_error(self):
        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n,Missing,2012,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )

        rows = batch.preview_snapshot["preview"]["rows"]
        self.assertEqual(rows[0]["action"], ACTION_NEEDS_REVIEW)
        self.assertEqual(rows[0]["match_status"], MATCH_AMBIGUOUS)
        self.assertEqual(rows[1]["action"], ACTION_ERROR)

    def test_commit_creates_player_and_source_row(self):
        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)

        result = commit_import_batch(import_batch=batch, actor=self.staff)

        player = Player.objects.get(first_name="Eugene", last_name="Lin")
        self.assertEqual(result.created, 1)
        self.assertEqual(PlayerSourceRow.objects.get(player=player).import_batch_id, batch.id)
        membership = PlayerRosterMembership.objects.select_related("season_team").get(player=player)
        self.assertEqual(membership.season_team.season, self.season)
        self.assertEqual(membership.season_team.name, "Expos")
        self.assertEqual(membership.season_team.division, "13U")
        self.assertTrue(membership.is_primary)
        self.assertEqual(result.season_teams_created, 1)
        self.assertEqual(result.memberships_created, 1)
        batch.refresh_from_db()
        self.assertEqual(batch.status, PlayerImportStatus.COMMITTED)

    def test_commit_reuses_same_team_membership_in_same_season(self):
        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
        commit_import_batch(import_batch=first_batch, actor=self.staff)
        player = Player.objects.get(first_name="Eugene", last_name="Lin")
        add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")
        second_batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team,Jersey\nEugene,Lin,MEM-1,13U,Expos,27\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )

        result = commit_import_batch(import_batch=second_batch, actor=self.staff)

        self.assertEqual(result.updated, 1)
        self.assertEqual(result.memberships_updated, 1)
        self.assertEqual(PlayerRosterMembership.objects.filter(player=player, season_team__season=self.season).count(), 1)
        self.assertEqual(PlayerRosterMembership.objects.get(player=player).jersey_number, "27")

    def test_commit_preserves_prior_season_and_creates_future_membership(self):
        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
        commit_import_batch(import_batch=first_batch, actor=self.staff)
        player = Player.objects.get(first_name="Eugene", last_name="Lin")
        add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")
        next_season = create_season(key="2027-spring", name="2027 Spring")
        next_batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team\nEugene,Lin,MEM-1,15U,Mounties\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=next_season,
        )

        commit_import_batch(import_batch=next_batch, actor=self.staff)

        self.assertEqual(PlayerRosterMembership.objects.filter(player=player).count(), 2)
        self.assertTrue(
            PlayerRosterMembership.objects.filter(player=player, season_team__season=self.season, season_team__name="Expos").exists()
        )
        self.assertTrue(
            PlayerRosterMembership.objects.filter(player=player, season_team__season=next_season, season_team__name="Mounties").exists()
        )

    def test_preview_blocks_same_season_team_change_for_active_primary(self):
        first_batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
        commit_import_batch(import_batch=first_batch, actor=self.staff)
        player = Player.objects.get(first_name="Eugene", last_name="Lin")
        add_source_identifier(player, SOURCE_MEMBER_LIST, "registrant_id", "MEM-1")

        change_batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,Registrant ID,Division,Team\nEugene,Lin,MEM-1,13U,Mounties\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )

        row = change_batch.preview_snapshot["preview"]["rows"][0]
        self.assertEqual(row["action"], ACTION_ERROR)
        self.assertIn("active primary membership", " ".join(row["errors"]))

    def test_commit_updates_blanks_without_overwriting_conflicts(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01")
        add_source_identifier(player, SOURCE_ROSTER_DETAIL, "registration_id", "REG-1")
        batch = create_import_batch(
            file_obj=self.upload(
                name="roster detail for 13u house.csv",
                body=b"First Name,Last Name,DOB,Registration ID,Division,Team\nEugene,Lin,2012-05-01,REG-1,13U,Expos\n",
            ),
            source=SOURCE_ROSTER_DETAIL,
            uploaded_by=self.staff,
            season=self.season,
        )

        result = commit_import_batch(import_batch=batch, actor=self.staff)

        player.refresh_from_db()
        self.assertEqual(result.updated, 1)
        self.assertEqual(player.team_name, "Expos")

    def test_commit_applies_use_imported_resolution(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )
        resolutions = {"2": {"action": "commit", "fields": {"preferred_name": "use_imported"}}}

        commit_import_batch(import_batch=batch, actor=self.staff, resolutions=resolutions)

        player.refresh_from_db()
        self.assertEqual(player.preferred_name, "New")

    def test_commit_rejects_unresolved_review_rows_without_mutating_player(self):
        player = Player.objects.create(first_name="Eugene", last_name="Lin", birthdate="2012-05-01", preferred_name="Old")
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,DOB,Preferred Name,Division,Team\nEugene,Lin,2012-05-01,New,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )

        with self.assertRaises(ValidationError):
            commit_import_batch(import_batch=batch, actor=self.staff)

        player.refresh_from_db()
        batch.refresh_from_db()
        self.assertEqual(player.preferred_name, "Old")
        self.assertEqual(batch.status, PlayerImportStatus.NEEDS_REVIEW)
        self.assertFalse(PlayerSourceRow.objects.exists())

    def test_commit_allows_error_rows_to_be_explicitly_skipped(self):
        batch = create_import_batch(
            file_obj=self.upload(body=b"Last\nMissingFirst\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )

        result = commit_import_batch(import_batch=batch, actor=self.staff, resolutions={"2": {"action": ACTION_SKIP}})

        batch.refresh_from_db()
        self.assertEqual(result.skipped, 1)
        self.assertEqual(batch.status, PlayerImportStatus.COMMITTED)
        self.assertFalse(Player.objects.exists())

    def test_commit_resolves_ambiguous_match_to_selected_candidate(self):
        player_one = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        player_two = Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )

        result = commit_import_batch(
            import_batch=batch,
            actor=self.staff,
            resolutions={"2": {"action": RESOLUTION_ACTION_USE_CANDIDATE, "candidate_id": str(player_two.id)}},
        )

        player_two.refresh_from_db()
        self.assertEqual(result.updated, 1)
        self.assertEqual(Player.objects.count(), 2)
        self.assertEqual(player_two.team_name, "Expos")
        self.assertEqual(PlayerSourceRow.objects.get().player, player_two)
        self.assertFalse(PlayerSourceRow.objects.filter(player=player_one).exists())

    def test_commit_can_create_new_player_from_ambiguous_row(self):
        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        Player.objects.create(first_name="Eugene", last_name="Lin", birth_year=2012, division="13U")
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,Birth Year,Division,Team\nEugene,Lin,2012,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )

        result = commit_import_batch(
            import_batch=batch,
            actor=self.staff,
            resolutions={"2": {"action": RESOLUTION_ACTION_CREATE_NEW}},
        )

        self.assertEqual(result.created, 1)
        self.assertEqual(Player.objects.count(), 3)

    def test_commit_prevents_double_commit(self):
        batch = create_import_batch(file_obj=self.upload(), source=SOURCE_MEMBER_LIST, uploaded_by=self.staff, season=self.season)
        commit_import_batch(import_batch=batch, actor=self.staff)

        with self.assertRaises(ValidationError):
            commit_import_batch(import_batch=batch, actor=self.staff)

    def test_commit_without_provisioning_leaves_account_models_unchanged(self):
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,DOB,Division,Team\nEugene,Lin,2012-05-01,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            season=self.season,
        )

        commit_import_batch(import_batch=batch, actor=self.staff)

        self.assertFalse(User.objects.filter(username="eugene.lin").exists())
        self.assertFalse(AccountProfile.objects.exists())
        self.assertFalse(UserPlayerLink.objects.exists())

    def test_commit_with_provisioning_creates_eligible_account_and_safe_summary(self):
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            provision_player_accounts=True,
            season=self.season,
        )
        mapping = dict(batch.mapping_config)
        mapping["account_email"] = "Email"
        build_import_preview(import_batch=batch, mapping_config=mapping)

        commit_import_batch(import_batch=batch, actor=self.staff)

        user = User.objects.get(username="eugene.lin")
        player = Player.objects.get(first_name="Eugene", last_name="Lin")
        batch.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, "eugene@example.com")
        self.assertTrue(user.check_password("20120501"))
        self.assertTrue(UserPlayerLink.objects.filter(user=user, player=player, relationship="self").exists())
        summary = batch.import_summary["account_provisioning"]
        self.assertEqual(summary["users_created"], 1)
        self.assertEqual(summary["already_linked"], 0)
        self.assertNotIn("20120501", str(batch.import_summary))

    def test_commit_with_provisioning_skips_missing_birthdate_without_rollback(self):
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,Division,Team\nEugene,Lin,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            provision_player_accounts=True,
            season=self.season,
        )

        commit_import_batch(import_batch=batch, actor=self.staff)

        batch.refresh_from_db()
        self.assertTrue(Player.objects.filter(first_name="Eugene", last_name="Lin").exists())
        self.assertFalse(User.objects.filter(username="eugene.lin").exists())
        self.assertEqual(batch.import_summary["account_provisioning"]["skipped"], 1)

    def test_commit_with_provisioning_reports_duplicate_unrelated_email_conflict(self):
        User.objects.create_user(username="existing", email="eugene@example.com")
        batch = create_import_batch(
            file_obj=self.upload(body=b"First,Last,DOB,Email,Division,Team\nEugene,Lin,2012-05-01,eugene@example.com,13U,Expos\n"),
            source=SOURCE_MEMBER_LIST,
            uploaded_by=self.staff,
            provision_player_accounts=True,
            season=self.season,
        )
        mapping = dict(batch.mapping_config)
        mapping["account_email"] = "Email"
        build_import_preview(import_batch=batch, mapping_config=mapping)

        commit_import_batch(import_batch=batch, actor=self.staff)

        batch.refresh_from_db()
        self.assertTrue(Player.objects.filter(first_name="Eugene", last_name="Lin").exists())
        self.assertFalse(User.objects.filter(username="eugene.lin").exists())
        self.assertEqual(batch.import_summary["account_provisioning"]["conflicts"], 1)
