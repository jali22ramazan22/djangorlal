# Python modules
from typing import Any

# Django modules
from django.db.models import (
    EmailField,
    CharField,
    BooleanField,
    DateField,
    IntegerField,
    Choices,
)
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Project modules
from apps.abstracts.models import AbstractBaseModel
from apps.auths.validators import (
    validate_email_domain,
    validate_email_payload_not_in_full_name,
    validate_phone,
)


class CustomUserManager(BaseUserManager):
    """Custom User Manager to make database requests."""

    def __obtain_user_instance(
        self,
        email: str,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        **kwargs: dict[str, Any],
    ) -> "CustomUser":
        """Get user instance."""
        if not email:
            raise ValidationError(message="Email field is required", code="email_empty")
        if not username:
            raise ValidationError("The username is empty", code="username_empty")
        if not password:
            raise ValidationError("The password is empty", code="password_empty")
        if not first_name:
            raise ValidationError("The first name is empty", code="first_name_empty")
        if not last_name:
            raise ValidationError("The last name is empty", code="last_name_empty")

        new_user: "CustomUser" = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            **kwargs,
        )
        return new_user

    def create_user(
        self,
        email: str,
        username: str,
        first_name: str,
        last_name: str,
        password: str,
        **kwargs: dict[str, Any],
    ) -> "CustomUser":
        """Create Custom user. TODO where is this used?"""
        new_user: "CustomUser" = self.__obtain_user_instance(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            **kwargs,
        )
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user

    def create_superuser(
        self,
        email: str,
        username: str,
        first_name: str,
        last_name: str,
        password: str,
        **kwargs: dict[str, Any],
    ) -> "CustomUser":
        """Create super user. Used by manage.py createsuperuser."""
        new_user: "CustomUser" = self.__obtain_user_instance(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_staff=True,
            is_superuser=True,
            **kwargs,
        )
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user


class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """
    Custom user model extending AbstractBaseModel.
    """

    EMAIL_MAX_LENGTH = 150
    NAMES_MAX_LENGTH = 75
    PASSWORD_MAX_LENGTH = 254

    DEPARTMENT_CHOICES = (
        ("HR", "HR"),
        ("IT", "IT"),
        ("Sales", "Sales"),
        ("Finance", "Finance"),
    )

    ROLES_CHOICES = (
        ("Admin", "Admin"),
        ("Manager", "Manager"),
        ("Employee", "Employee"),
    )

    email = EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True,
        validators=[validate_email_domain],
        verbose_name="Email address",
        help_text="User's email address",
    )
    username = CharField(max_length=NAMES_MAX_LENGTH, unique=True)
    first_name = CharField(max_length=NAMES_MAX_LENGTH, blank=True)
    last_name = CharField(max_length=NAMES_MAX_LENGTH, blank=True)
    phone = CharField(max_length=15, blank=True, validators=[validate_phone])
    city = CharField(max_length=30, blank=True)
    country = CharField(max_length=30, blank=True)
    department = CharField(max_length=30, blank=True, choices=DEPARTMENT_CHOICES)
    role = CharField(max_length=30, blank=True, choices=ROLES_CHOICES)
    birth_date = DateField(null=True)
    salary = IntegerField(null=True)

    password = CharField(
        max_length=PASSWORD_MAX_LENGTH,
        validators=[validate_password],
        verbose_name="Password",
        help_text="User's hash representation of the password",
    )
    # True iff the user is part of the corporoom team, allowing them to access the admin panel
    is_staff = BooleanField(
        default=False,
        verbose_name="Staff status",
        help_text="True if the user is an admin and has an access to the admin panel",
    )
    # True iff the user can make requests to the backend (include in company)
    is_active = BooleanField(
        default=True,
        verbose_name="Active status",
        help_text="True if the user is active and has an access to request data",
    )
    date_joined = DateField(auto_now_add=True)
    last_login = DateField(null=True, blank=True)

    REQUIRED_FIELDS = ["first_name", "last_name", "email"]
    USERNAME_FIELD = "username"
    objects = CustomUserManager()

    class Meta:
        """Meta options for CustomUser model."""

        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"
        ordering = ["-created_at"]

    def clean(self) -> None:
        """Validate the model instance before saving."""
        validate_email_payload_not_in_full_name(
            email=self.email,
            full_name=self.full_name,
        )
        return super().clean()
