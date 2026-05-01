from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ScholarshipCycleStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"
    ARCHIVED = "archived", "Archived"


class ScholarshipApplicationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under review"
    AWARDED = "awarded", "Awarded"
    NOT_SELECTED = "not_selected", "Not selected"
    WITHDRAWN = "withdrawn", "Withdrawn"


class ScholarshipCycle(TimeStampedModel):
    title = models.CharField(max_length=160)
    year = models.PositiveIntegerField(unique=True)
    slug = models.SlugField(max_length=180, unique=True)
    status = models.CharField(max_length=20, choices=ScholarshipCycleStatus.choices, default=ScholarshipCycleStatus.DRAFT)
    application_open_date = models.DateField()
    application_deadline = models.DateField()
    public_announcement = models.TextField(blank=True)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-year", "-application_deadline"]

    def __str__(self):
        return f"{self.title} ({self.year})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or f"scholarship-{self.year}"
            slug = base_slug
            counter = 2
            while ScholarshipCycle.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def clean(self):
        if self.application_deadline < self.application_open_date:
            raise ValidationError("Application deadline must be on or after the open date.")

    @property
    def is_accepting_applications(self):
        today = timezone.localdate()
        return (
            self.status == ScholarshipCycleStatus.OPEN
            and self.application_open_date <= today <= self.application_deadline
        )

    def get_absolute_url(self):
        return reverse("scholarships:overview")


class ScholarshipApplicantProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scholarship_profile",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=220, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["last_name", "first_name", "id"]

    def __str__(self):
        return self.full_name or self.email

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        self.email = self.email.strip().lower()
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)


class ScholarshipApplication(TimeStampedModel):
    applicant = models.ForeignKey(
        ScholarshipApplicantProfile,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    cycle = models.ForeignKey(
        ScholarshipCycle,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=20,
        choices=ScholarshipApplicationStatus.choices,
        default=ScholarshipApplicationStatus.DRAFT,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)

    player_full_name = models.CharField(max_length=220)
    date_of_birth = models.DateField()
    vcb_team_or_program = models.CharField(max_length=180)
    primary_positions = models.CharField(max_length=180)
    years_participated_in_vcb_programs = models.CharField(max_length=120)

    pathway_college_university = models.BooleanField(default=False)
    pathway_trade_vocational_training = models.BooleanField(default=False)
    pathway_recognized_training_program = models.BooleanField(default=False)
    pathway_undecided = models.BooleanField(default=False)
    institution_or_program_name = models.CharField(max_length=220, blank=True)
    intended_field_of_study_or_training = models.CharField(max_length=220, blank=True)

    nomination_statement = models.TextField()

    confirm_information_is_accurate = models.BooleanField(default=False)
    confirm_good_standing = models.BooleanField(default=False)
    confirm_decisions_are_final = models.BooleanField(default=False)
    consent_to_reference_checks = models.BooleanField(default=False)
    nominator_signature = models.CharField(max_length=220)
    signature_date = models.DateField()

    transcript_or_report_card = models.FileField(
        upload_to="scholarships/transcripts/",
        blank=True,
    )
    supporting_documents = models.FileField(
        upload_to="scholarships/supporting/",
        blank=True,
    )

    internal_review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at", "-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["applicant", "cycle"], name="unique_scholarship_application_per_cycle")
        ]

    def __str__(self):
        return f"{self.player_full_name} - {self.cycle.year}"

    def clean(self):
        if not any(
            [
                self.pathway_college_university,
                self.pathway_trade_vocational_training,
                self.pathway_recognized_training_program,
                self.pathway_undecided,
            ]
        ):
            raise ValidationError("Select at least one post-graduation pathway.")

    @property
    def can_edit(self):
        if self.status != ScholarshipApplicationStatus.DRAFT:
            return False
        return self.cycle.is_accepting_applications

    @property
    def word_count(self):
        return len([word for word in self.nomination_statement.split() if word.strip()])

    def get_absolute_url(self):
        return reverse("scholarships:application-detail", kwargs={"pk": self.pk})


class ScholarshipReference(TimeStampedModel):
    application = models.ForeignKey(
        ScholarshipApplication,
        on_delete=models.CASCADE,
        related_name="references",
    )
    display_order = models.PositiveSmallIntegerField(default=1)
    name = models.CharField(max_length=180)
    role_relationship = models.CharField(max_length=180)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.application.player_full_name} reference {self.display_order}"

