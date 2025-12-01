"""Custom User Manager"""

from typing import Any
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """Manager for CustomUser model"""

    def create_user(
        self, email: str, password: str, full_name: str, **extra_fields: Any
    ) -> "CustomUser":  # noqa
        """Create and save a regular User with email and password"""

        if not email:
            raise ValueError("The Email field must be set")
        if not password:
            raise ValueError("The Password field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        full_name: str = "Admin",
        **extra_fields: Any  # noqa
    ) -> "CustomUser":  # noqa:
        """Create and save a SuperUser with email and password"""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, full_name, extra_fields)
