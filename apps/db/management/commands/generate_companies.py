"""
Management command to generate test companies with realistic fake data
"""

from django.core.management.base import BaseCommand
from apps.db.models import Company
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = "Generate test companies with fake data for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Number of companies to create (default: 5)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing companies before generating",
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]

        if clear:
            self.stdout.write(self.style.WARNING("⚠ Clearing existing companies..."))
            deleted = Company.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted} companies"))

        self.stdout.write(f"Generating {count} test companies...")

        created_count = 0
        existing_count = 0

        for i in range(count):
            # Generate realistic company name
            company_name = fake.company()

            company, created = Company.objects.get_or_create(
                company_name=company_name, defaults={"company_name": company_name}
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

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} companies"))
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f"○ {existing_count} already existed"))

        total_companies = Company.objects.filter(deleted_at__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f"✓ Total companies: {total_companies}"))
