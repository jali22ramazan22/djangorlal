"""
Management command to generate ALL test data (companies, users, projects, tasks)
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Generate all test data: companies, users, projects, and tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all existing data before generating",
        )
        parser.add_argument(
            "--companies",
            type=int,
            default=5,
            help="Number of companies to create (default: 5)",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=15,
            help="Number of users to create (default: 15)",
        )
        parser.add_argument(
            "--projects",
            type=int,
            default=10,
            help="Number of projects to create (default: 10)",
        )
        parser.add_argument(
            "--tasks",
            type=int,
            default=50,
            help="Number of tasks to create (default: 50)",
        )

    def handle(self, *args, **options):
        clear = options["clear"]
        companies_count = options["companies"]
        users_count = options["users"]
        projects_count = options["projects"]
        tasks_count = options["tasks"]

        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write(self.style.HTTP_INFO("  JIRA CLONE - FAKE DATA GENERATOR"))
        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write("")

        # Step 1: Generate Companies
        self.stdout.write(self.style.HTTP_INFO("📊 Step 1/4: Generating Companies..."))
        call_command(
            "generate_companies", count=companies_count, clear=clear, stdout=self.stdout
        )
        self.stdout.write("")

        # Step 2: Generate Users
        self.stdout.write(self.style.HTTP_INFO("👥 Step 2/4: Generating Users..."))
        call_command(
            "generate_users",
            count=users_count,
            admin=True,
            clear=clear,
            stdout=self.stdout,
        )
        self.stdout.write("")

        # Step 3: Generate Projects
        self.stdout.write(self.style.HTTP_INFO("📁 Step 3/4: Generating Projects..."))
        call_command(
            "generate_projects", count=projects_count, clear=clear, stdout=self.stdout
        )
        self.stdout.write("")

        # Step 4: Generate Tasks
        self.stdout.write(self.style.HTTP_INFO("✓ Step 4/4: Generating Tasks..."))
        call_command(
            "generate_tasks", count=tasks_count, clear=clear, stdout=self.stdout
        )
        self.stdout.write("")

        # Final Summary
        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write(self.style.SUCCESS("✓ ALL DATA GENERATED SUCCESSFULLY!"))
        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("📝 Quick Start:"))
        self.stdout.write("  1. Login: http://localhost:8000/api/v1/auth/users/login")
        self.stdout.write("     Email: admin@example.com | Password: admin123")
        self.stdout.write("")
        self.stdout.write("  2. API Docs: http://localhost:8000/api/v1/docs/")
        self.stdout.write("")
        self.stdout.write("  3. Explore:")
        self.stdout.write(f"     - Companies: {companies_count}")
        self.stdout.write(f"     - Users: {users_count} + 1 admin")
        self.stdout.write(f"     - Projects: {projects_count}")
        self.stdout.write(f"     - Tasks: {tasks_count}")
        self.stdout.write("")
