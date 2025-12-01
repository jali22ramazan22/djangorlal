"""
Management command to generate test tasks
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.db.models import Project, Task
from apps.auths.models import CustomUser


class Command(BaseCommand):
    help = "Generate test tasks for development"

    def handle(self, *args, **options):
        self.stdout.write("Generating test tasks...")

        # Get necessary data
        try:
            project = Project.objects.filter(deleted_at__isnull=True).first()
            if not project:
                self.stdout.write(
                    self.style.ERROR(
                        "✗ No projects found. Run generate_projects first."
                    )
                )
                return

            users = list(CustomUser.objects.all()[:3])
            if not users:
                self.stdout.write(
                    self.style.ERROR("✗ No users found. Run generate_users first.")
                )
                return

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {e}"))
            return

        # Task constants from model
        TODO = 0
        IN_PROGRESS = 1
        DONE = 2

        test_tasks = [
            {
                "title": "Setup Project Infrastructure",
                "description": "Initialize Django project with DRF and configure settings",
                "category": "Backend",
                "status": DONE,
                "project": project,
                "deadline": timezone.now().date() - timedelta(days=7),
            },
            {
                "title": "Design Database Schema",
                "description": "Create ERD and define models for the application",
                "category": "Backend",
                "status": DONE,
                "project": project,
                "deadline": timezone.now().date() - timedelta(days=5),
            },
            {
                "title": "Implement Authentication API",
                "description": "Create JWT authentication endpoints with login/logout",
                "category": "Backend",
                "status": IN_PROGRESS,
                "project": project,
                "deadline": timezone.now().date() + timedelta(days=3),
            },
            {
                "title": "Build Task Management API",
                "description": "CRUD operations for tasks with filtering and pagination",
                "category": "Backend",
                "status": IN_PROGRESS,
                "project": project,
                "deadline": timezone.now().date() + timedelta(days=5),
            },
            {
                "title": "Create Frontend UI Components",
                "description": "Build reusable React components for task board",
                "category": "Frontend",
                "status": TODO,
                "project": project,
                "deadline": timezone.now().date() + timedelta(days=10),
            },
            {
                "title": "Write API Documentation",
                "description": "Document all endpoints using OpenAPI/Swagger",
                "category": "Documentation",
                "status": IN_PROGRESS,
                "project": project,
                "deadline": timezone.now().date() + timedelta(days=7),
            },
            {
                "title": "Setup CI/CD Pipeline",
                "description": "Configure GitHub Actions for automated testing and deployment",
                "category": "DevOps",
                "status": TODO,
                "project": project,
                "deadline": timezone.now().date() + timedelta(days=14),
            },
            {
                "title": "Write Unit Tests",
                "description": "Achieve 80% code coverage with pytest",
                "category": "Testing",
                "status": TODO,
                "project": project,
                "deadline": timezone.now().date() + timedelta(days=12),
            },
            {
                "title": "Performance Optimization",
                "description": "Optimize database queries and add caching",
                "category": "Backend",
                "status": TODO,
                "project": project,
                "deadline": timezone.now().date() + timedelta(days=20),
            },
            {
                "title": "Security Audit",
                "description": "Review code for security vulnerabilities",
                "category": "Security",
                "status": TODO,
                "project": project,
                "deadline": timezone.now().date() + timedelta(days=15),
            },
        ]

        created_count = 0
        existing_count = 0

        for task_data in test_tasks:
            task, created = Task.objects.get_or_create(
                title=task_data["title"],
                project=task_data["project"],
                defaults=task_data,
            )
            if created:
                # Assign users to task
                task.assignees.set(users[:2])  # Assign first 2 users
                created_count += 1
                status_display = dict(Task.STATUS_CHOICES).get(task.status)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created task: {task.title} ({status_display})"
                    )
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f"○ Task already exists: {task.title}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Created {created_count} tasks, {existing_count} already existed"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Total tasks: {Task.objects.filter(deleted_at__isnull=True).count()}"
            )
        )
