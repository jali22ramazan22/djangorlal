"""
Management command to generate test projects with realistic fake data
"""

from django.core.management.base import BaseCommand
from apps.db.models import Company, Project
from apps.auths.models import CustomUser
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):
    help = "Generate test projects with fake data for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Number of projects to create (default: 5)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing projects before generating",
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]

        if clear:
            self.stdout.write(self.style.WARNING("⚠ Clearing existing projects..."))
            deleted = Project.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted} projects"))

        self.stdout.write(f"Generating {count} test projects...")

        # Get necessary data
        companies = list(Company.objects.filter(deleted_at__isnull=True))
        if not companies:
            self.stdout.write(
                self.style.ERROR(
                    "✗ No companies found. Run: python manage.py generate_companies"
                )
            )
            return

        authors = list(CustomUser.objects.filter(is_active=True))
        if not authors:
            self.stdout.write(
                self.style.ERROR(
                    "✗ No users found. Run: python manage.py generate_users --admin"
                )
            )
            return

        users = list(CustomUser.objects.filter(is_active=True))

        created_count = 0
        existing_count = 0

        # Project types for realistic names
        project_types = [
            "Website",
            "Mobile App",
            "Dashboard",
            "API",
            "Platform",
            "System",
            "Portal",
            "Application",
        ]

        for i in range(count):
            # Generate realistic project name
            project_type = random.choice(project_types)
            project_name = f"{fake.catch_phrase()} {project_type}"

            company = random.choice(companies)
            author = random.choice(authors)

            project, created = Project.objects.get_or_create(
                name=project_name, company=company, defaults={"author": author}
            )

            if created:
                # Add random users to project (2-5 users)
                num_users = min(random.randint(2, 5), len(users))
                project.users.set(random.sample(users, num_users))
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created project: {project.name} ({company.company_name})"
                    )
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f"○ Project already exists: {project.name}")
                )

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} projects"))
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f"○ {existing_count} already existed"))

        total_projects = Project.objects.filter(deleted_at__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f"✓ Total projects: {total_projects}"))
