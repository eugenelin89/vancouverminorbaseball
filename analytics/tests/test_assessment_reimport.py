from copy import deepcopy
from decimal import Decimal

from django.core.exceptions import ValidationError

from analytics.models import AssessmentValue, PlayerAssessment
from analytics.services.assessment_import_service import (
    acknowledge_assessment_import_warnings,
    commit_assessment_import_batch,
    correct_assessment_value,
    create_assessment_import_batch,
    preserve_manual_override_conflicts,
)
from analytics.tests.assessment_test_helpers import (
    AssessmentTestMixin,
    assessment_row,
    pitching_row,
    uploaded_workbook,
    workbook_bytes,
)
from analytics.tests.helpers import TestCase


class AssessmentReimportTests(AssessmentTestMixin, TestCase):
    def import_rows(self, *, assessment_overrides=None, pitching_overrides=None):
        batch = create_assessment_import_batch(
            file_obj=uploaded_workbook(
                workbook_bytes(
                    assessment_rows=[assessment_row(**(assessment_overrides or {}))],
                    pitching_rows=[pitching_row(**(pitching_overrides or {}))],
                )
            ),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )
        batch.refresh_from_db()
        if batch.required_warning_codes:
            acknowledge_assessment_import_warnings(
                batch=batch,
                actor=self.staff,
                token=batch.acknowledgement_token,
            )
        return batch, commit_assessment_import_batch(batch=batch, actor=self.staff)

    def preview_rows(self, *, assessment_overrides=None, pitching_overrides=None):
        batch = create_assessment_import_batch(
            file_obj=uploaded_workbook(
                workbook_bytes(
                    assessment_rows=[assessment_row(**(assessment_overrides or {}))],
                    pitching_rows=[pitching_row(**(pitching_overrides or {}))],
                )
            ),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )
        return batch

    def metric_change(self, batch, metric_key):
        return next(
            change
            for change in batch.rows.get().metric_changes
            if change["metric_key"] == metric_key
        )

    def test_identical_reimport_is_unchanged_without_value_timestamp_churn(self):
        _, first = self.import_rows()
        self.assertEqual(first.created, 1)
        value = AssessmentValue.objects.get(
            player_assessment__player=self.player,
            template_metric__metric__key="home_to_1st",
        )
        original_updated_at = value.updated_at

        batch = self.preview_rows()
        self.assertEqual(
            self.metric_change(batch, "home_to_1st")["action"], "unchanged"
        )
        batch = self.acknowledge(batch)
        result = commit_assessment_import_batch(batch=batch, actor=self.staff)

        value.refresh_from_db()
        self.assertEqual(result.unchanged, 1)
        self.assertEqual(value.updated_at, original_updated_at)
        self.assertEqual(PlayerAssessment.objects.count(), 1)

    def test_duplicate_workbook_checksum_requires_acknowledgement(self):
        self.import_rows()
        batch = self.preview_rows()
        batch.refresh_from_db()

        self.assertTrue(batch.preview_snapshot["checksum_seen_before"])
        self.assertIn("duplicate_workbook_checksum", batch.required_warning_codes)
        with self.assertRaises(ValidationError):
            commit_assessment_import_batch(batch=batch, actor=self.staff)

    def test_changed_value_updates_and_blank_clear_removes_imported_value(self):
        self.import_rows()
        changed = self.preview_rows(assessment_overrides={"Home to 1st": 4.2})
        self.assertEqual(self.metric_change(changed, "home_to_1st")["action"], "update")
        commit_assessment_import_batch(
            batch=self.acknowledge(changed), actor=self.staff
        )
        value = AssessmentValue.objects.get(
            player_assessment__player=self.player,
            template_metric__metric__key="home_to_1st",
        )
        self.assertEqual(value.numeric_value, Decimal("4.2"))

        blank = self.preview_rows(assessment_overrides={"Home to 1st": None})
        self.assertEqual(self.metric_change(blank, "home_to_1st")["action"], "clear")
        commit_assessment_import_batch(batch=self.acknowledge(blank), actor=self.staff)
        self.assertFalse(
            AssessmentValue.objects.filter(
                player_assessment__player=self.player,
                template_metric__metric__key="home_to_1st",
            ).exists()
        )

    def test_removed_mapping_metric_does_not_delete_historical_value(self):
        self.import_rows()
        config = deepcopy(self.import_template.config)
        config["sheets"][0]["metrics"] = [
            metric
            for metric in config["sheets"][0]["metrics"]
            if metric["key"] != "home_to_1st"
        ]
        mapping = self.custom_import_template(config, version=101)
        headers = [
            header
            for header in self.import_template.config["sheets"][0]["metrics"]
            if header["key"] != "home_to_1st"
        ]
        source_headers = ["Name", *[metric["header"] for metric in headers]]
        source_values = assessment_row()[2:]
        batch = create_assessment_import_batch(
            file_obj=uploaded_workbook(
                workbook_bytes(
                    assessment_headers=source_headers,
                    assessment_rows=[["Alex Example", *source_values]],
                    pitching_rows=[pitching_row()],
                )
            ),
            event=self.event,
            import_template=mapping,
            uploaded_by=self.staff,
        )
        commit_assessment_import_batch(batch=self.acknowledge(batch), actor=self.staff)
        self.assertTrue(
            AssessmentValue.objects.filter(
                player_assessment__player=self.player,
                template_metric__metric__key="home_to_1st",
            ).exists()
        )

    def test_frozen_mapping_is_used_after_live_mapping_changes(self):
        batch = self.preview_rows()
        frozen_checksum = batch.config_checksum
        live = batch.import_template
        live.config = {"mapping_version": 999, "sheets": []}
        live.save()
        batch.refresh_from_db()
        self.assertEqual(batch.config_checksum, frozen_checksum)
        self.assertTrue(batch.config_snapshot["sheets"])
        commit_assessment_import_batch(batch=self.acknowledge(batch), actor=self.staff)
        self.assertTrue(PlayerAssessment.objects.filter(player=self.player).exists())

    def test_manual_override_identical_is_protected_without_conflict(self):
        self.import_rows()
        value = AssessmentValue.objects.get(
            player_assessment__player=self.player,
            template_metric__metric__key="home_to_1st",
        )
        correct_assessment_value(
            assessment_value=value,
            actor=self.staff,
            reason="Confirmed existing value",
            new_value="4.1",
        )
        batch = self.preview_rows()
        change = self.metric_change(batch, "home_to_1st")
        self.assertEqual(change["action"], "protected_manual")
        self.assertEqual(batch.rows.get().conflict_status, "none")

    def test_manual_override_difference_and_blank_require_preserve_resolution(self):
        self.import_rows()
        value = AssessmentValue.objects.get(
            player_assessment__player=self.player,
            template_metric__metric__key="home_to_1st",
        )
        correct_assessment_value(
            assessment_value=value,
            actor=self.staff,
            reason="Timing video review",
            new_value="4.3",
        )
        for incoming in [4.2, None]:
            batch = self.preview_rows(assessment_overrides={"Home to 1st": incoming})
            row = batch.rows.get()
            self.assertEqual(row.conflict_status, "unresolved")
            self.assertEqual(
                self.metric_change(batch, "home_to_1st")["action"], "conflict"
            )
            with self.assertRaises(ValidationError):
                commit_assessment_import_batch(batch=batch, actor=self.staff)
            preserve_manual_override_conflicts(row=row, actor=self.staff)
            batch = self.acknowledge(batch)
            commit_assessment_import_batch(batch=batch, actor=self.staff)
            value.refresh_from_db()
            self.assertEqual(value.numeric_value, Decimal("4.3"))
