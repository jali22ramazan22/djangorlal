"""
Authentication serializers
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from apps.auths.models import CustomUser


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    Validates email and password
    """

    email = serializers.EmailField(max_length=CustomUser.EMAIL_MAX_LENGTH)
    password = serializers.CharField(
        max_length=CustomUser.PASSWORD_MAX_LENGTH, write_only=True
    )

    def validate_email(self, value):
        """Normalize email to lowercase"""
        return value.lower()

    def validate(self, attrs):
        """
        Validate credentials and authenticate user
        """
        email = attrs.get("email")
        password = attrs.get("password")

        # Check if user exists
        if not CustomUser.objects.filter(email=email).exists():
            raise ValidationError({"email": "User with this email does not exist"})

        # Authenticate user
        user = authenticate(username=email, password=password)

        if not user:
            raise ValidationError({"password": "Invalid credentials"})

        if not user.is_active:
            raise ValidationError({"email": "User account is disabled"})

        attrs["user"] = user
        return attrs


class UserLoginResponseSerializer(serializers.Serializer):
    """
    Serializer for successful login response
    Used for API documentation
    """

    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    access = serializers.CharField()
    refresh = serializers.CharField()


class UserPersonalInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for user's personal information
    """

    class Meta:
        model = CustomUser
        fields = ("id", "full_name", "email", "is_active", "created_at")
        read_only_fields = ("id", "email", "created_at")
