from players.tests.helpers import (
    IntegrityError,
    Player,
    PlayerAlias,
    PlayerSourceIdentifier,
    PlayerSourceRow,
    PlayerTag,
    TestCase,
    transaction,
)


class PlayerModelTests(TestCase):
    def test_player_full_name_and_display_name(self):
        player = Player.objects.create(
            first_name="Eugene", last_name="Lin", preferred_name="Gene"
        )

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
        alias = PlayerAlias.objects.create(
            player=player, alias="  Gene   LIN  ", source="manual"
        )

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
