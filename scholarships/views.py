from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView, UpdateView

from home.views import base_context
from scholarships.forms import ApplicantLoginForm, ApplicantSignupForm, ScholarshipApplicationForm, StaffApplicationFilterForm
from scholarships.models import ScholarshipApplication, ScholarshipApplicationStatus, ScholarshipCycle


def current_cycle():
    return (
        ScholarshipCycle.objects.filter(status="open")
        .order_by("application_deadline", "-year")
        .first()
        or ScholarshipCycle.objects.order_by("-year").first()
    )


class ScholarshipOverviewView(TemplateView):
    template_name = "scholarships/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        cycle = current_cycle()
        context.update(
            {
                "cycle": cycle,
                "eligibility_points": [
                    "Graduating 18U player in good standing with Vancouver Community Baseball",
                    "Participated in VCB programs during the 18U season",
                    "Pursuing post-secondary education, trade school, or a recognized training or development program",
                    "Completed the season without unresolved disciplinary issues",
                ],
                "selection_points": [
                    "On-field excellence",
                    "Leadership and sportsmanship",
                    "Academic and personal commitment",
                    "Community involvement and service",
                    "Character and values alignment",
                ],
                "has_scholarship_profile": hasattr(self.request.user, "scholarship_profile"),
            }
        )
        return context


class ApplicantSignupView(FormView):
    template_name = "scholarships/signup.html"
    form_class = ApplicantSignupForm
    success_url = reverse_lazy("scholarships:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        return context

    def form_valid(self, form):
        form.save(request=self.request)
        messages.success(self.request, "Account created. You can start your scholarship application now.")
        return super().form_valid(form)


class ScholarshipLoginView(LoginView):
    template_name = "scholarships/login.html"
    authentication_form = ApplicantLoginForm

    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse("scholarships:staff-application-list")
        return reverse("scholarships:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        return context


class ScholarshipLogoutView(LogoutView):
    next_page = reverse_lazy("scholarships:overview")


class ApplicantRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("scholarships:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if not hasattr(request.user, "scholarship_profile"):
            messages.error(
                request,
                "This account does not have a scholarship applicant profile yet. Create an applicant account to continue.",
            )
            return redirect("scholarships:signup")
        return super().dispatch(request, *args, **kwargs)


class ApplicantDashboardView(ApplicantRequiredMixin, TemplateView):
    template_name = "scholarships/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return redirect("scholarships:staff-application-list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        cycle = current_cycle()
        profile = getattr(self.request.user, "scholarship_profile", None)
        application = None
        if profile and cycle:
            application = ScholarshipApplication.objects.filter(applicant=profile, cycle=cycle).first()
        context.update(
            {
                "cycle": cycle,
                "application": application,
                "profile": profile,
            }
        )
        return context


class ApplicantApplicationMixin(ApplicantRequiredMixin):
    application = None

    def dispatch(self, request, *args, **kwargs):
        self.application = None
        pk = kwargs.get("pk")
        if pk is not None:
            self.application = get_object_or_404(
                ScholarshipApplication.objects.select_related("applicant", "cycle"),
                pk=pk,
                applicant=request.user.scholarship_profile,
            )
            hook_response = self.on_application_loaded(request)
            if hook_response is not None:
                return hook_response
        return super().dispatch(request, *args, **kwargs)

    def on_application_loaded(self, request):
        return None


class ScholarshipApplicationCreateView(ApplicantRequiredMixin, FormView):
    template_name = "scholarships/application_form.html"
    form_class = ScholarshipApplicationForm

    def dispatch(self, request, *args, **kwargs):
        self.cycle = current_cycle()
        if not self.cycle or not self.cycle.is_accepting_applications:
            messages.error(request, "Applications are not open right now.")
            return redirect("scholarships:dashboard")
        existing = ScholarshipApplication.objects.filter(
            applicant=request.user.scholarship_profile,
            cycle=self.cycle,
        ).first()
        if existing:
            return redirect("scholarships:application-detail", pk=existing.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["applicant"] = self.request.user.scholarship_profile
        kwargs["cycle"] = self.cycle
        return kwargs

    def form_valid(self, form):
        application = form.save()
        if application.status == ScholarshipApplicationStatus.SUBMITTED:
            messages.success(self.request, "Application submitted successfully.")
        else:
            messages.success(self.request, "Application draft saved.")
        return redirect("scholarships:application-detail", pk=application.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["cycle"] = self.cycle
        context["application"] = None
        return context


class ScholarshipApplicationUpdateView(ApplicantApplicationMixin, UpdateView):
    template_name = "scholarships/application_form.html"
    form_class = ScholarshipApplicationForm
    model = ScholarshipApplication

    def on_application_loaded(self, request):
        if not self.application.can_edit:
            messages.error(request, "This application can no longer be edited.")
            return redirect("scholarships:application-detail", pk=self.application.pk)
        return None

    def get_object(self, queryset=None):
        return self.application

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["applicant"] = self.request.user.scholarship_profile
        kwargs["cycle"] = self.application.cycle
        return kwargs

    def form_valid(self, form):
        application = form.save()
        if application.status == ScholarshipApplicationStatus.SUBMITTED:
            messages.success(self.request, "Application submitted successfully.")
        else:
            messages.success(self.request, "Application draft updated.")
        return redirect("scholarships:application-detail", pk=application.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["cycle"] = self.application.cycle
        context["application"] = self.application
        return context


class ScholarshipApplicationDetailView(ApplicantApplicationMixin, DetailView):
    template_name = "scholarships/application_detail.html"
    model = ScholarshipApplication

    def get_object(self, queryset=None):
        return self.application

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        return context


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy("scholarships:login")

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class StaffApplicationListView(StaffRequiredMixin, ListView):
    template_name = "scholarships/staff_application_list.html"
    model = ScholarshipApplication
    paginate_by = 50

    def get_filter_form(self):
        return StaffApplicationFilterForm(self.request.GET or None)

    def get_queryset(self):
        queryset = ScholarshipApplication.objects.select_related("applicant", "cycle").prefetch_related("references")
        form = self.get_filter_form()
        if form.is_valid():
            cycle = form.cleaned_data.get("cycle")
            status = form.cleaned_data.get("status")
            search = (form.cleaned_data.get("search") or "").strip()
            if cycle:
                queryset = queryset.filter(cycle=cycle)
            if status:
                queryset = queryset.filter(status=status)
            if search:
                queryset = queryset.filter(Q(player_full_name__icontains=search) | Q(applicant__email__icontains=search))
        return queryset.order_by("-cycle__year", "player_full_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        context["filter_form"] = self.get_filter_form()
        context["cycles"] = ScholarshipCycle.objects.order_by("-year")
        return context


class StaffApplicationDetailView(StaffRequiredMixin, DetailView):
    template_name = "scholarships/staff_application_detail.html"
    model = ScholarshipApplication
    queryset = ScholarshipApplication.objects.select_related("applicant", "cycle").prefetch_related("references")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        return context


class StaffApplicationDownloadView(StaffRequiredMixin, DetailView):
    model = ScholarshipApplication
    queryset = ScholarshipApplication.objects.select_related("applicant", "cycle").prefetch_related("references")

    def render_to_response(self, context, **response_kwargs):
        application = context["object"]
        response = TemplateResponse(self.request, "scholarships/download_application.html", context)
        filename = f"scholarship-application-{application.cycle.year}-{application.player_full_name.lower().replace(' ', '-')}.html"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class StaffCycleDownloadView(StaffRequiredMixin, TemplateView):
    template_name = "scholarships/download_cycle.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context())
        cycle = get_object_or_404(ScholarshipCycle, slug=kwargs["slug"])
        applications = ScholarshipApplication.objects.filter(cycle=cycle).select_related("applicant").prefetch_related("references")
        context.update({"cycle": cycle, "applications": applications})
        return context

    def render_to_response(self, context, **response_kwargs):
        response = TemplateResponse(self.request, self.template_name, context)
        cycle = context["cycle"]
        response["Content-Disposition"] = f'attachment; filename="scholarship-applications-{cycle.year}.html"'
        return response
