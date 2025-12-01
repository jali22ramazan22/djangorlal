"""
Project serializers for API
"""

from rest_framework import serializers
from apps.db.models import Project
from apps.api.serializers.user import CustomUserForeignSerializer
from apps.api.serializers.company import CompanySerializer


class ProjectBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for project - minimal fields
    Used in nested representations
    """

    class Meta:
        model = Project
        fields = ("id", "name", "created_at")
        read_only_fields = ("created_at",)


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Serializer for project list view
    Includes company, author, and team member count
    """

    company = CompanySerializer(read_only=True)
    author = CustomUserForeignSerializer(read_only=True)
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "company",
            "author",
            "users_count",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def get_users_count(self, obj):
        """Get count of team members"""
        return obj.users.count()


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a project
    Accepts company_id and author_id as integers
    """

    company_id = serializers.IntegerField(write_only=True)
    author_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Project
        fields = ("name", "company_id", "author_id")

    def create(self, validated_data):
        """
        Create project with company and author
        """
        from apps.db.models import Company
        from django.conf import settings

        User = settings.AUTH_USER_MODEL

        company_id = validated_data.pop("company_id")
        author_id = validated_data.pop("author_id")

        company = Company.objects.get(id=company_id)
        author = User.objects.get(id=author_id)

        project = Project.objects.create(
            company=company, author=author, **validated_data
        )

        return project


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a project
    Only name can be updated
    """

    class Meta:
        model = Project
        fields = ("name",)


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single project view
    Includes company, author, team members, and tasks
    """

    company = CompanySerializer(read_only=True)
    author = CustomUserForeignSerializer(read_only=True)
    users = CustomUserForeignSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "company",
            "author",
            "users",
            "tasks_count",
            "tasks",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_tasks(self, obj):
        """Get project's active tasks"""
        from apps.api.serializers.task import TaskListSerializer

        tasks = obj.tasks.filter(deleted_at__isnull=True)
        return TaskListSerializer(tasks, many=True).data

    def get_tasks_count(self, obj):
        """Get count of active tasks"""
        return obj.tasks.filter(deleted_at__isnull=True).count()
