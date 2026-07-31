from django.core.exceptions import ValidationError
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
        try:
            plan = ensure_2026_13u_assessment_configuration(
                dry_run=options.get("dry_run", False)
            )
        except ValidationError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            raise
        mode = "Dry run" if options.get("dry_run", False) else "Configured"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode} 2026 13U assessment template with {len(plan['metrics'])} metrics."
            )
        )
        self.stdout.write(
            f"Required sheets: {', '.join(plan['required_sheets'])}; "
            f"optional sheets: {', '.join(plan['optional_sheets']) or 'none'}"
        )
        for sheet in plan["sheets"]:
            self.stdout.write(
                f"- {sheet['name']}: header row={sheet['header_row']}; "
                f"identity={sheet['identity_column']}; required headers="
                f"{', '.join(sheet['required_headers'])}"
            )
        self.stdout.write(
            "Import mapping: "
            f"{plan['import_template']['key']} v{plan['import_template']['version']} "
            f"({plan['import_template']['config_checksum']})"
        )
        self.stdout.write(
            "Scoring profile: "
            f"{plan['scoring_profile']['key']} v{plan['scoring_profile']['version']}"
        )
        for state in plan.get("states", []):
            self.stdout.write(
                f"{state['object']}: {state['state']}"
                f"{' (locked)' if state['locked'] else ''}"
            )
            for field_name, conflict in state.get("conflicts", {}).items():
                self.stdout.write(
                    self.style.WARNING(
                        f"  conflict {field_name}: actual={conflict['actual']!r}; "
                        f"expected={conflict['expected']!r}"
                    )
                )
        for metric in plan["metrics"]:
            scale = metric["rating_scale"] or "n/a"
            unit = metric["unit"] or "not configured"
            self.stdout.write(
                f"- {metric['key']}: type={metric['value_type']}; scale={scale}; "
                f"unit={unit}; unit_status={metric['unit_status']}; "
                f"zero={metric['zero_policy']}; blank={metric['blank_policy']}"
            )
