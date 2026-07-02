from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView, TemplateView, View

from analytics.forms import PlayerImportMappingForm, PlayerImportUploadForm, parse_conflict_resolutions
from players.models import PlayerImportBatch
from players.services.import_service import (
    build_import_preview,
    commit_import_batch,
    create_import_batch,
    current_preview,
)


class AnalyticsStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class PlayerImportListView(AnalyticsStaffRequiredMixin, ListView):
    model = PlayerImportBatch
    template_name = "analytics/import_list.html"
    context_object_name = "import_batches"
    paginate_by = 25


class PlayerImportUploadView(AnalyticsStaffRequiredMixin, FormView):
    template_name = "analytics/import_upload.html"
    form_class = PlayerImportUploadForm

    def form_valid(self, form):
        batch = create_import_batch(
            file_obj=form.cleaned_data["csv_file"],
            source=form.cleaned_data["source"],
            uploaded_by=self.request.user,
        )
        messages.success(self.request, "CSV uploaded. Review the import preview before committing.")
        return redirect("analytics:import-preview", pk=batch.pk)


class ImportBatchMixin(AnalyticsStaffRequiredMixin):
    import_batch = None

    def dispatch(self, request, *args, **kwargs):
        self.import_batch = get_object_or_404(PlayerImportBatch, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["import_batch"] = self.import_batch
        context["preview"] = current_preview(self.import_batch)
        return context


class PlayerImportPreviewView(ImportBatchMixin, TemplateView):
    template_name = "analytics/import_preview.html"

    def get_mapping_form(self, data=None):
        parsed = self.import_batch.preview_snapshot.get("parsed_csv", {})
        initial = self.import_batch.mapping_config
        return PlayerImportMappingForm(data=data, parsed=parsed, initial=initial)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mapping_form"] = kwargs.get("mapping_form") or self.get_mapping_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_mapping_form(data=request.POST)
        if form.is_valid():
            build_import_preview(import_batch=self.import_batch, mapping_config=form.mapping_config())
            messages.success(request, "Import preview refreshed.")
            return redirect("analytics:import-preview", pk=self.import_batch.pk)
        return self.render_to_response(self.get_context_data(mapping_form=form))


class PlayerImportConflictView(ImportBatchMixin, TemplateView):
    template_name = "analytics/import_conflicts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preview = context.get("preview") or {}
        context["review_rows"] = [
            row for row in preview.get("rows", []) if row.get("action") == "needs_review" or row.get("errors")
        ]
        return context


class PlayerImportConfirmView(ImportBatchMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            result = commit_import_batch(
                import_batch=self.import_batch,
                actor=request.user,
                resolutions=parse_conflict_resolutions(request.POST),
            )
        except (PermissionDenied, ValidationError) as exc:
            messages.error(request, str(exc))
            return redirect("analytics:import-preview", pk=self.import_batch.pk)

        messages.success(
            request,
            f"Import committed. Created {result.created}, updated {result.updated}, skipped {result.skipped}.",
        )
        if result.errors:
            messages.warning(request, f"{len(result.errors)} row issue(s) were recorded.")
        return redirect("analytics:import-detail", pk=self.import_batch.pk)


class PlayerImportDetailView(ImportBatchMixin, TemplateView):
    template_name = "analytics/import_detail.html"
