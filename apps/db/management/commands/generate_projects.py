"""
Management command to generate test projects
"""

from django.core.management.base import BaseCommand
from apps.db.models import Company, Project
from apps.auths.models import CustomUser


class Command(BaseCommand):
    help = "Generate test projects for development"

    def handle(self, *args, **options):
        self.stdout.write("Generating test projects...")

        # Get or create necessary data
        try:
            company = Company.objects.filter(deleted_at__isnull=True).first()
            if not company:
                self.stdout.write(
                    self.style.ERROR(
                        "✗ No companies found. Run generate_companies first."
                    )
                )
                return

            author = CustomUser.objects.filter(is_staff=True).first()
            if not author:
                self.stdout.write(
                    self.style.ERROR(
                        "✗ No admin users found. Run generate_users first."
                    )
                )
                return

            users = list(CustomUser.objects.all()[:3])

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {e}"))
            return

        test_projects = [
            {
                "name": "E-commerce Platform",
                "company": company,
                "author": author,
            },
            {
                "name": "Mobile App Development",
                "company": company,
                "author": author,
            },
            {
                "name": "Internal Dashboard",
                "company": company,
                "author": author,
            },
            {
                "name": "API Integration",
                "company": company,
                "author": author,
            },
        ]

        created_count = 0
        existing_count = 0

        for project_data in test_projects:
            project, created = Project.objects.get_or_create(
                name=project_data["name"],
                company=project_data["company"],
                defaults=project_data,
            )
            if created:
                # Add users to project
                project.users.set(users)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created project: {project.name}")
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f"○ Project already exists: {project.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Created {created_count} projects, {existing_count} already existed"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Total projects: {Project.objects.filter(deleted_at__isnull=True).count()}"
            )
        )
