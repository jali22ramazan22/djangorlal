"""
Management command to generate test tasks with realistic fake data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.db.models import Project, Task
from apps.auths.models import CustomUser
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):
    help = "Generate test tasks with fake data for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of tasks to create (default: 20)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing tasks before generating",
        )

    def handle(self, *args, **options):
        count = options["count"]
        clear = options["clear"]

        if clear:
            self.stdout.write(self.style.WARNING("⚠ Clearing existing tasks..."))
            deleted = Task.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted} tasks"))

        self.stdout.write(f"Generating {count} test tasks...")

        # Get necessary data
        projects = list(Project.objects.filter(deleted_at__isnull=True))
        if not projects:
            self.stdout.write(
                self.style.ERROR(
                    "✗ No projects found. Run: python manage.py generate_projects"
                )
            )
            return

        users = list(CustomUser.objects.filter(is_active=True))
        if not users:
            self.stdout.write(
                self.style.ERROR(
                    "✗ No users found. Run: python manage.py generate_users"
                )
            )
            return

        # Categories for realistic tasks
        categories = [
            "Backend",
            "Frontend",
            "DevOps",
            "Testing",
            "Documentation",
            "Design",
            "Security",
            "Database",
        ]

        # Task action verbs
        actions = [
            "Implement",
            "Create",
            "Build",
            "Design",
            "Setup",
            "Configure",
            "Write",
            "Test",
            "Fix",
            "Optimize",
        ]

        created_count = 0
        existing_count = 0

        for i in range(count):
            # Generate realistic task data
            action = random.choice(actions)
            category = random.choice(categories)
            title = f"{action} {fake.catch_phrase()}"
            description = fake.paragraph(nb_sentences=3)

            # Random project and status
            project = random.choice(projects)
            status = random.choice([Task.TODO, Task.IN_PROGRESS, Task.DONE])

            # Random deadline (past for DONE, future for others)
            if status == Task.DONE:
                deadline_days = random.randint(-30, -1)
            else:
                deadline_days = random.randint(1, 30)

            deadline = timezone.now().date() + timedelta(days=deadline_days)

            task, created = Task.objects.get_or_create(
                title=title,
                project=project,
                defaults={
                    "description": description,
                    "category": category,
                    "status": status,
                    "deadline": deadline,
                },
            )

            if created:
                # Assign random users (1-3 users)
                num_assignees = min(random.randint(1, 3), len(users))
                task.assignees.set(random.sample(users, num_assignees))

                created_count += 1
                status_display = dict(Task.STATUS_CHOICES).get(task.status)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created task: {task.title[:50]}... ({status_display}, {category})"
                    )
                )
            else:
                existing_count += 1

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} tasks"))
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f"○ {existing_count} already existed"))

        # Statistics
        total_tasks = Task.objects.filter(deleted_at__isnull=True).count()
        todo_count = Task.objects.filter(
            status=Task.TODO, deleted_at__isnull=True
        ).count()
        in_progress_count = Task.objects.filter(
            status=Task.IN_PROGRESS, deleted_at__isnull=True
        ).count()
        done_count = Task.objects.filter(
            status=Task.DONE, deleted_at__isnull=True
        ).count()

        self.stdout.write(self.style.SUCCESS(f"✓ Total tasks: {total_tasks}"))
        self.stdout.write(f"  - TODO: {todo_count}")
        self.stdout.write(f"  - IN PROGRESS: {in_progress_count}")
        self.stdout.write(f"  - DONE: {done_count}")
