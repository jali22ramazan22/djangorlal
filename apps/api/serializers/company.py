"""
Company serializers for API
"""

from rest_framework import serializers
from apps.db.models import Company


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for company list and basic operations
    """

    is_deleted = serializers.BooleanField(read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "company_name",
            "created_at",
            "updated_at",
            "is_deleted",
        )
        read_only_fields = ("created_at", "updated_at")


class CompanyDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for company with projects
    """

    projects = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "company_name",
            "projects_count",
            "projects",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_projects(self, obj):
        """Get company's active projects"""
        from apps.api.serializers.project import ProjectListSerializer

        projects = obj.projects.filter(deleted_at__isnull=True)
        return ProjectListSerializer(projects, many=True).data

    def get_projects_count(self, obj):
        """Get count of active projects"""
        return obj.projects.filter(deleted_at__isnull=True).count()
