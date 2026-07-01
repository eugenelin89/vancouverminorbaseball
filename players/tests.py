from datetime import date

from django.apps import apps
from django.contrib import admin
from django.db import IntegrityError, transaction
from django.test import TestCase

from players.models import Player, PlayerAlias, PlayerSourceIdentifier, PlayerSourceRow, PlayerTag
from players.services import import_service
from players.services.identity_service import add_source_identifier, create_player
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
        for model in [Player, PlayerAlias, PlayerSourceIdentifier, PlayerSourceRow, PlayerTag]:
            self.assertIn(model, admin.site._registry)
