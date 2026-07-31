from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from analytics.models import (
    AssessmentImportBatch,
    AssessmentMetricDefinition,
    AssessmentTemplate,
    AssessmentTemplateMetric,
    AssessmentValue,
    PlayerAssessment,
)
from analytics.services.assessment_import_service import (
    commit_assessment_import_batch,
    create_assessment_import_batch,
)
from analytics.tests.assessment_test_helpers import AssessmentTestMixin
from analytics.tests.helpers import Player, TestCase, create_season


class AssessmentImmutabilityTests(AssessmentTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        batch = create_assessment_import_batch(
            file_obj=self.valid_upload(),
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
        )
        self.batch = self.acknowledge(batch)
        commit_assessment_import_batch(batch=self.batch, actor=self.staff)
        self.assessment = PlayerAssessment.objects.get(
            player=self.player, event=self.event
        )
        self.value = self.assessment.values.get(
            template_metric__metric__key="home_to_1st"
        )

    def assert_validation_error(self, callback):
        with self.assertRaises(ValidationError):
            callback()

    def test_used_template_cannot_change_or_receive_metric(self):
        self.template.name = "Reinterpreted Template"
        self.assert_validation_error(self.template.save)

        metric = AssessmentMetricDefinition.objects.create(
            key="new_metric", name="New Metric"
        )
        new_template_metric = AssessmentTemplateMetric(
            template=self.template,
            metric=metric,
            display_name="New Metric",
        )
        self.assert_validation_error(new_template_metric.save)

    def test_used_template_metric_cannot_change_or_delete(self):
        template_metric = self.value.template_metric
        template_metric.display_name = "Changed Meaning"
        self.assert_validation_error(template_metric.save)
        template_metric.refresh_from_db()
        self.assert_validation_error(template_metric.delete)

        unlocked_template = AssessmentTemplate.objects.create(
            key="future-template",
            name="Future Template",
            version=1,
        )
        template_metric.template = unlocked_template
        self.assert_validation_error(template_metric.save)

    def test_used_import_template_and_scoring_profile_cannot_change_or_delete(self):
        self.import_template.config = {"changed": True}
        self.assert_validation_error(self.import_template.save)
        self.import_template.refresh_from_db()
        self.assert_validation_error(self.import_template.delete)

        self.scoring_profile.config = {"changed": True}
        self.assert_validation_error(self.scoring_profile.save)
        self.scoring_profile.refresh_from_db()
        self.assert_validation_error(self.scoring_profile.delete)

    def test_used_event_cannot_change_template_season_or_dates(self):
        other_season = create_season(name="Fall 2026", key="fall-2026")
        self.event.season = other_season
        self.assert_validation_error(self.event.save)
        self.event.refresh_from_db()
        self.event.starts_on = other_season.starts_on
        self.event.name = "Changed Event Identity"
        self.assert_validation_error(self.event.save)
        self.event.refresh_from_db()
        self.assert_validation_error(self.event.delete)

    def test_committed_player_assessment_cannot_be_reassigned_or_deleted(self):
        other = Player.objects.create(first_name="Other", last_name="Player")
        self.assessment.player = other
        self.assert_validation_error(self.assessment.save)
        self.assessment.refresh_from_db()
        self.assessment.status = "draft"
        self.assert_validation_error(self.assessment.save)
        self.assessment.refresh_from_db()
        self.assert_validation_error(self.assessment.delete)
        with self.assertRaises(ProtectedError):
            self.player.delete()

    def test_committed_value_cannot_be_edited_deleted_or_added_directly(self):
        self.value.numeric_value = 9
        self.assert_validation_error(self.value.save)
        self.value.refresh_from_db()
        self.assert_validation_error(self.value.delete)

        draft_assessment = PlayerAssessment.objects.create(
            player=Player.objects.create(first_name="Draft", last_name="Player"),
            event=self.event,
        )
        self.value.player_assessment = draft_assessment
        self.assert_validation_error(self.value.save)

        other_metric = self.template.template_metrics.get(metric__key="pitch_3")
        direct = AssessmentValue(
            player_assessment=self.assessment,
            template_metric=other_metric,
            numeric_value=1,
        )
        self.assert_validation_error(direct.save)

    def test_metric_definition_with_historical_use_is_locked(self):
        metric = self.value.template_metric.metric
        metric.default_value_type = "text"
        self.assert_validation_error(metric.save)
        metric.refresh_from_db()
        self.assert_validation_error(metric.delete)

    def test_committed_batch_and_rows_are_immutable(self):
        self.batch.original_filename = "different.xlsx"
        self.assert_validation_error(self.batch.save)
        self.batch.refresh_from_db()
        self.assert_validation_error(self.batch.delete)

        row = self.batch.rows.first()
        row.raw_identity = "Changed"
        self.assert_validation_error(row.save)
        row.refresh_from_db()
        self.assert_validation_error(row.delete)

        other_batch = AssessmentImportBatch.objects.create(
            event=self.event,
            import_template=self.import_template,
            uploaded_by=self.staff,
            original_filename="other.xlsx",
            workbook_sha256="0" * 64,
            config_snapshot=self.import_template.config,
        )
        row.batch = other_batch
        self.assert_validation_error(row.save)

        with self.assertRaises(ProtectedError):
            self.batch.rows.all().delete()

    def test_safe_lifecycle_deactivation_remains_available(self):
        self.template.is_active = False
        self.template.save()
        self.event.is_active = False
        self.event.save()
        self.template.refresh_from_db()
        self.event.refresh_from_db()
        self.assertFalse(self.template.is_active)
        self.assertFalse(self.event.is_active)
