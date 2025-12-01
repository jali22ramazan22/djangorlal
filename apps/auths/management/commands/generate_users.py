"""
Management command to generate test users
"""

from django.core.management.base import BaseCommand
from apps.auths.models import CustomUser


class Command(BaseCommand):
    help = "Generate test users for development"

    def handle(self, *args, **options):
        self.stdout.write("Generating test users...")

        # Create admin user
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
            self.stdout.write(self.style.SUCCESS(f"✓ Created admin: {admin.email}"))
        else:
            self.stdout.write(
                self.style.WARNING(f"○ Admin already exists: {admin.email}")
            )

        # Create test users
        test_users = [
            {
                "email": "developer@techcorp.com",
                "full_name": "John Developer",
                "password": "dev123",
            },
            {
                "email": "designer@techcorp.com",
                "full_name": "Sarah Designer",
                "password": "design123",
            },
            {
                "email": "manager@techcorp.com",
                "full_name": "Mike Manager",
                "password": "manager123",
            },
            {
                "email": "qa@techcorp.com",
                "full_name": "Lisa QA",
                "password": "qa123",
            },
        ]

        for user_data in test_users:
            user, created = CustomUser.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "full_name": user_data["full_name"],
                    "is_active": True,
                },
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✓ Created user: {user.email}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"○ User already exists: {user.email}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Total users in database: {CustomUser.objects.count()}"
            )
        )
