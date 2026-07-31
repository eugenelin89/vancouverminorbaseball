from django.core.management.base import BaseCommand

from analytics.services.assessment_import_service import (
    ensure_2026_13u_assessment_configuration,
)


class Command(BaseCommand):
    help = "Create assessment configuration for the 2026 VCB House 13U workbook."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the configuration plan without writing database records.",
        )

    def handle(self, *args, **options):
        plan = ensure_2026_13u_assessment_configuration(
            dry_run=options.get("dry_run", False)
        )
        mode = "Dry run" if options.get("dry_run", False) else "Configured"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode} 2026 13U assessment template with {len(plan['metrics'])} metrics."
            )
        )
