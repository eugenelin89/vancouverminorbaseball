from copy import deepcopy
from io import BytesIO

from django.core.exceptions import ValidationError
from django.test import override_settings
from openpyxl import Workbook

from analytics.models import ASSESSMENT_IMPORT_STATUS_FAILED
from analytics.services.assessment_import_service import (
    create_assessment_import_batch,
    parse_assessment_workbook,
    resolve_assessment_import_row,
    summarize_import_batch,
)
from analytics.tests.assessment_test_helpers import (
    ASSESSMENT_HEADERS,
    AssessmentTestMixin,
    assessment_row,
    minimal_config,
    minimal_workbook,
    uploaded_workbook,
    workbook_bytes,
)
from analytics.tests.helpers import TestCase


def issue_codes(issues):
    return {issue["code"] for issue in issues}


class WorkbookStructureTests(AssessmentTestMixin, TestCase):
    def create_batch(self, content, *, import_template=None, name="assessment.xlsx"):
        return create_assessment_import_batch(
            file_obj=uploaded_workbook(content, name=name),
            event=self.event,
            import_template=import_template or self.import_template,
            uploaded_by=self.staff,
        )

    def test_empty_workbook_and_no_player_rows_are_not_committable(self):
        empty = Workbook()
        output = BytesIO()
        empty.save(output)
        batch = self.create_batch(output.getvalue())
        self.assertIn("required_sheet_missing", issue_codes(batch.validation_errors))
        self.assertIn("no_valid_player_rows", issue_codes(batch.validation_errors))
        self.assertFalse(summarize_import_batch(batch).can_commit)

        no_rows = self.create_batch(
            workbook_bytes(assessment_rows=[], pitching_rows=[])
        )
        self.assertIn("no_player_rows", issue_codes(no_rows.validation_errors))
        self.assertFalse(summarize_import_batch(no_rows).can_commit)

    def test_missing_required_sheet_blocks_and_missing_optional_sheet_warns(self):
        missing_required = self.create_batch(
            workbook_bytes(
                include_assessment=False,
                pitching_rows=[],
            )
        )
        self.assertIn(
            "required_sheet_missing", issue_codes(missing_required.validation_errors)
        )

        missing_optional = self.create_batch(
            workbook_bytes(
                assessment_rows=[assessment_row()],
                include_pitching=False,
            )
        )
        self.assertIn(
            "optional_sheet_missing", issue_codes(missing_optional.validation_warnings)
        )

    def test_missing_header_row_identity_and_metric_header_block(self):
        missing_header_row = self.create_batch(
            workbook_bytes(
                assessment_rows=[assessment_row()],
                include_pitching=False,
                assessment_header_row=2,
            ),
            import_template=self.custom_import_template(
                {
                    **deepcopy(self.import_template.config),
                    "sheets": [
                        {
                            **deepcopy(self.import_template.config["sheets"][0]),
                            "header_row": 99,
                        }
                    ],
                },
                version=100,
            ),
        )
        self.assertIn(
            "header_row_missing", issue_codes(missing_header_row.validation_errors)
        )

        headers_without_identity = ["Player", *ASSESSMENT_HEADERS[1:]]
        missing_identity = self.create_batch(
            workbook_bytes(
                assessment_rows=[assessment_row()],
                assessment_headers=headers_without_identity,
                include_pitching=False,
            )
        )
        self.assertIn(
            "identity_header_missing", issue_codes(missing_identity.validation_errors)
        )

        missing_metric = self.create_batch(
            workbook_bytes(
                assessment_rows=[assessment_row()[:-1]],
                assessment_headers=ASSESSMENT_HEADERS[:-1],
                include_pitching=False,
            )
        )
        self.assertIn(
            "required_metric_header_missing",
            issue_codes(missing_metric.validation_errors),
        )

    def test_unexpected_column_warns_and_header_alias_supports_new_mapping_version(
        self,
    ):
        unexpected = self.create_batch(
            workbook_bytes(
                assessment_rows=[assessment_row()],
                pitching_rows=[],
                extra_assessment_headers=["Operator Note"],
            )
        )
        self.assertIn("unexpected_column", issue_codes(unexpected.validation_warnings))

        config = minimal_config(header="Time", header_aliases=["Sprint Time"])
        parsed = parse_assessment_workbook(
            minimal_workbook([["Synthetic Player", 4.2]], header="  SPRINT   TIME. "),
            config,
        )
        self.assertFalse(parsed["errors"])
        self.assertEqual(parsed["rows"][0]["values"][0]["numeric_value"], "4.2")

    def test_malformed_workbook_persists_failed_batch_without_player_data(self):
        batch = self.create_batch(b"not a workbook")
        self.assertEqual(batch.status, ASSESSMENT_IMPORT_STATUS_FAILED)
        self.assertIn("workbook_parse_failed", issue_codes(batch.validation_errors))
        self.assertFalse(batch.rows.exists())

    def test_wrong_extension_and_upload_size_are_rejected(self):
        with self.assertRaises(ValidationError):
            self.create_batch(b"data", name="assessment.csv")
        with override_settings(ANALYTICS_ASSESSMENT_MAX_UPLOAD_BYTES=10):
            with self.assertRaises(ValidationError):
                self.create_batch(workbook_bytes(assessment_rows=[], pitching_rows=[]))

        with override_settings(ANALYTICS_ASSESSMENT_MAX_UNCOMPRESSED_BYTES=100):
            batch = self.create_batch(
                workbook_bytes(
                    assessment_rows=[assessment_row()],
                    pitching_rows=[],
                )
            )
        self.assertEqual(batch.status, ASSESSMENT_IMPORT_STATUS_FAILED)

    def test_row_and_column_limits_block_preview(self):
        row_config = minimal_config()
        row_config["sheets"][0]["max_rows"] = 2
        parsed = parse_assessment_workbook(
            minimal_workbook([["One", 1], ["Two", 2]]), row_config
        )
        self.assertIn("worksheet_row_limit", issue_codes(parsed["errors"]))

        column_config = minimal_config()
        column_config["sheets"][0]["max_columns"] = 2
        parsed = parse_assessment_workbook(
            minimal_workbook([["One", 1]], extra_headers=["Extra"]), column_config
        )
        self.assertIn("worksheet_column_limit", issue_codes(parsed["errors"]))

    def test_worksheet_and_cell_text_limits_block_preview(self):
        worksheet_config = minimal_config()
        worksheet_config["limits"]["max_worksheets"] = 1
        parsed_batch = self.create_batch(
            workbook_bytes(assessment_rows=[assessment_row()], pitching_rows=[]),
            import_template=self.custom_import_template(
                worksheet_config,
                version=102,
            ),
        )
        self.assertEqual(parsed_batch.status, ASSESSMENT_IMPORT_STATUS_FAILED)

        cell_config = minimal_config(value_type="text")
        cell_config["limits"]["max_cell_text_length"] = 5
        parsed = parse_assessment_workbook(
            minimal_workbook([["Synthetic Player", "too long"]]),
            cell_config,
        )
        row_codes = {
            issue["code"] for row in parsed["rows"] for issue in row.get("errors", [])
        }
        self.assertIn("cell_text_too_long", row_codes)

    def test_assigning_player_does_not_clear_numeric_validation_errors(self):
        content = workbook_bytes(
            assessment_rows=[assessment_row(**{"Athletic Stance": 4})],
            pitching_rows=[],
        )
        batch = self.create_batch(content)
        row = batch.rows.get()
        self.assertEqual(row.validation_status, "invalid")

        with self.assertRaises(ValidationError):
            resolve_assessment_import_row(row=row, player=self.player)

        row.refresh_from_db()
        self.assertEqual(row.validation_status, "invalid")
        self.assertFalse(summarize_import_batch(batch).can_commit)


class NumericPolicyTests(TestCase):
    def parse_value(self, value, **config_options):
        parsed = parse_assessment_workbook(
            minimal_workbook([["Synthetic Player", value]]),
            minimal_config(**config_options),
        )
        return parsed["rows"][0]["values"][0]

    def test_rating_accepts_only_integers_one_to_three(self):
        valid = self.parse_value(2, value_type="rating")
        self.assertFalse(valid["errors"])
        for invalid in [0, 1.5, 4, "not numeric"]:
            snapshot = self.parse_value(invalid, value_type="rating")
            self.assertTrue(snapshot["errors"], invalid)
            self.assertEqual(snapshot["raw_value"], str(invalid))

    def test_numeric_minimum_maximum_and_invalid_text(self):
        self.assertIn(
            "value_below_minimum",
            issue_codes(self.parse_value(2, min_value=3)["errors"]),
        )
        self.assertIn(
            "value_above_maximum",
            issue_codes(self.parse_value(8, max_value=7)["errors"]),
        )
        self.assertIn(
            "invalid_numeric_value",
            issue_codes(self.parse_value("bad")["errors"]),
        )

    def test_all_zero_policies(self):
        allowed = self.parse_value(0, zero_policy="allow")
        self.assertEqual(allowed["numeric_value"], "0")

        missing = self.parse_value(0, zero_policy="treat_as_missing")
        self.assertTrue(missing["is_blank"])
        self.assertIn("zero_treated_as_missing", issue_codes(missing["warnings"]))
        self.assertTrue(missing["transformations"])

        warning = self.parse_value(0, zero_policy="warning")
        self.assertEqual(warning["numeric_value"], "0")
        self.assertIn("zero_requires_review", issue_codes(warning["warnings"]))

        error = self.parse_value(0, zero_policy="error")
        self.assertIn("zero_not_allowed", issue_codes(error["errors"]))

    def test_blank_policies_and_required_blank(self):
        for policy in [
            "preserve_existing",
            "clear_existing_imported_value",
            "ignore_on_create",
        ]:
            snapshot = self.parse_value(None, blank_policy=policy)
            self.assertTrue(snapshot["is_blank"])
            self.assertFalse(snapshot["errors"])
        required = self.parse_value(None, blank_policy="error_if_required")
        self.assertIn("required_value_missing", issue_codes(required["errors"]))
