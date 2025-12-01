"""Custom User Model with email authentication"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError

from apps.abstracts.models import AbstractBaseModel
from apps.auths.managers import CustomUserManager


# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """
    Custom User Model with email username field
    Inherits from AbstractBaseUser for authentication and PermissionsMixin
    """

    EMAIL_MAX_LENGTH: int = 150
    PASSWORD_MAX_LENGTH: int = 150
    FULLNAME_MAX_LENGTH: int = 150

    email = models.EmailField(
        verbose_name="Email address",
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True,
        help_text="User's email address (used for login)",
    )
    full_name = models.CharField(
        verbose_name="Full name",
        max_length=FULLNAME_MAX_LENGTH,
        help_text="User's full name",
    )
    is_staff = models.BooleanField(
        verbose_name="Staff status",
        default=False,
        help_text="Designates whether the user can log into the admin site",
    )
    is_active = models.BooleanField(
        verbose_name="Active",
        default=True,
        help_text="Designates whether the user should be threated as active",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "custom_users"

    def __str__(self) -> str:
        return f"{self.email} - {self.full_name}"

    def __repr__(self) -> str:
        return f"<CustomUser(id={self.id}, email={self.email})>"

    def clean(self) -> None:
        """Validate that email is not contained in full_name"""

        if self.email and self.full_name:
            if self.email.lower() in self.full_name.lower():
                raise ValidationError(
                    {"full_name": "Full name should not contain email address"}
                )
        return super().clean()
