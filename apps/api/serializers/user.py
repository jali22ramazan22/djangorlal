"""
User serializers for API
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserForeignSerializer(serializers.ModelSerializer):
    """
    Serializer for nested user representations
    Used in ForeignKey and ManyToMany relations
    """

    class Meta:
        model = User
        fields = ("id", "email", "full_name")


class CustomUserListSerializer(serializers.ModelSerializer):
    """
    Serializer for user list view
    """

    class Meta:
        model = User
        fields = ("id", "email", "full_name", "is_active", "created_at")
        read_only_fields = ("created_at",)


class CustomUserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single user view
    Includes related projects
    """

    projects = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "is_active",
            "is_staff",
            "projects",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_projects(self, obj):
        """Get user's projects (avoiding circular import)"""
        from apps.api.serializers.project import ProjectListSerializer

        projects = obj.projects.filter(deleted_at__isnull=True)
        return ProjectListSerializer(projects, many=True).data
