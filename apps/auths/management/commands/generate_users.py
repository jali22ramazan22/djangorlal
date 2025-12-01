"""
Management command to generate test users with realistic fake data
"""

from django.core.management.base import BaseCommand
from apps.auths.models import CustomUser
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = "Generate test users with fake data for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of users to create (default: 10)",
        )
        parser.add_argument(
            "--admin", action="store_true", help="Also create an admin user"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear non-admin users before generating",
        )

    def handle(self, *args, **options):
        count = options["count"]
        create_admin = options["admin"]
        clear = options["clear"]

        if clear:
            self.stdout.write(
                self.style.WARNING("⚠ Clearing existing non-admin users...")
            )
            deleted = CustomUser.objects.filter(
                is_superuser=False, is_staff=False
            ).delete()[0]
            self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted} users"))

        self.stdout.write(f"Generating {count} test users...")

        created_count = 0
        skipped_count = 0

        # Create admin if requested
        if create_admin:
            admin, created = CustomUser.objects.get_or_create(
                email="admin@example.com",
                defaults={
                    "full_name": "Admin User",
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                },
            )
            if created:
                admin.set_password("admin123")
                admin.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created admin: {admin.email} (password: admin123)"
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"○ Admin already exists: {admin.email}")
                )

        # Generate fake users
        for i in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
            full_name = f"{first_name} {last_name}"

            # Check if email already exists
            if CustomUser.objects.filter(email=email).exists():
                skipped_count += 1
                continue

            try:
                user = CustomUser.objects.create_user(
                    email=email,
                    password="testpass123",
                    full_name=full_name,
                    is_active=True,
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created user: {user.email} ({user.full_name})"
                    )
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Failed to create user: {e}"))

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"✓ Created {created_count} users"))
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f"○ Skipped {skipped_count} (already exist)")
            )

        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(
            is_active=True, deleted_at__isnull=True
        ).count()
        self.stdout.write(
            self.style.SUCCESS(f"✓ Total users: {total_users} ({active_users} active)")
        )

        # Helpful info
        self.stdout.write("")
        self.stdout.write(
            self.style.HTTP_INFO("ℹ Default password for all test users: testpass123")
        )
