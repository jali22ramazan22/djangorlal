"""
Management command to generate test companies
"""

from django.core.management.base import BaseCommand
from apps.db.models import Company


class Command(BaseCommand):
    help = "Generate test companies for development"

    def handle(self, *args, **options):
        self.stdout.write("Generating test companies...")

        test_companies = [
            {"company_name": "TechCorp Solutions"},
            {"company_name": "InnovateLab Inc"},
            {"company_name": "Digital Dynamics"},
            {"company_name": "CloudWorks Ltd"},
            {"company_name": "DataDriven Systems"},
        ]

        created_count = 0
        existing_count = 0

        for company_data in test_companies:
            company, created = Company.objects.get_or_create(
                company_name=company_data["company_name"], defaults=company_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created company: {company.company_name}")
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"○ Company already exists: {company.company_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Created {created_count} companies, {existing_count} already existed"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Total companies: {Company.objects.filter(deleted_at__isnull=True).count()}"
            )
        )
