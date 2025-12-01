"""
Task serializers for API
"""

from rest_framework import serializers
from apps.db.models import Task, Project
from apps.api.serializers.user import CustomUserForeignSerializer
from apps.api.serializers.project import ProjectBaseSerializer
from apps.api.serializers.base import CurrentPKURLDefault


class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer for task list view
    """

    project = ProjectBaseSerializer(read_only=True)
    assignees = CustomUserForeignSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "category",
            "status",
            "project",
            "assignees",
            "deadline",
            "is_overdue",
            "is_completed",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def get_status(self, obj):
        """Get status as dictionary with value and label"""
        return obj.get_status_as_dict()


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a task
    Can automatically get project_id from URL context
    """

    project_id = serializers.IntegerField(default=CurrentPKURLDefault(), required=False)
    assignee_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "category",
            "project_id",
            "parent",
            "assignee_ids",
            "deadline",
        )

    def create(self, validated_data):
        """
        Create task with project and assignees
        """
        from django.conf import settings

        User = settings.AUTH_USER_MODEL

        assignee_ids = validated_data.pop("assignee_ids", [])
        project_id = validated_data.pop("project_id")

        # Get project
        project = Project.objects.get(id=project_id)

        # Create task
        task = Task.objects.create(project=project, **validated_data)

        # Assign users
        if assignee_ids:
            task.assignees.set(User.objects.filter(id__in=assignee_ids))

        return task


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a task
    """

    assignee_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "category",
            "status",
            "parent",
            "assignee_ids",
            "deadline",
        )

    def update(self, instance, validated_data):
        """
        Update task with assignees
        """
        from django.conf import settings

        User = settings.AUTH_USER_MODEL

        assignee_ids = validated_data.pop("assignee_ids", None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update assignees if provided
        if assignee_ids is not None:
            instance.assignees.set(User.objects.filter(id__in=assignee_ids))

        return instance


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for single task view
    Includes project, assignees, parent task, and subtasks
    """

    project = ProjectBaseSerializer(read_only=True)
    assignees = CustomUserForeignSerializer(many=True, read_only=True)
    parent = serializers.SerializerMethodField()
    subtasks = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "category",
            "status",
            "project",
            "parent",
            "subtasks",
            "assignees",
            "deadline",
            "is_overdue",
            "is_completed",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def get_status(self, obj):
        """Get status as dictionary"""
        return obj.get_status_as_dict()

    def get_parent(self, obj):
        """Get parent task if exists"""
        if obj.parent:
            return TaskListSerializer(obj.parent).data
        return None

    def get_subtasks(self, obj):
        """Get subtasks"""
        subtasks = obj.subtasks.filter(deleted_at__isnull=True)
        return TaskListSerializer(subtasks, many=True).data
