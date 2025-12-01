"""
DRF ViewSets for API endpoints
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from apps.db.models import Company, Project, Task
from apps.api.serializers import (
    CompanySerializer,
    CompanyDetailSerializer,
    ProjectListSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectDetailSerializer,
    TaskListSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskDetailSerializer,
)
from apps.api.filters import TaskFilter
from apps.api.permissions import IsUserInProject


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for companies (read-only)
    Provides list and retrieve actions
    """

    queryset = Company.objects.filter(deleted_at__isnull=True)
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "retrieve":
            return CompanyDetailSerializer
        return CompanySerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for projects with full CRUD operations
    Includes custom actions for tasks
    """

    queryset = (
        Project.objects.filter(deleted_at__isnull=True)
        .select_related("company", "author")
        .prefetch_related("users")
    )
    permission_classes = [AllowAny]  # TODO: Add IsAuthenticated for production

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return ProjectListSerializer
        elif self.action == "create":
            return ProjectCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ProjectUpdateSerializer
        return ProjectDetailSerializer

    @action(detail=True, methods=["get"], url_path="tasks")
    def get_tasks(self, request, pk=None):
        """
        Get all tasks for a project with filtering
        GET /api/v1/projects/{id}/tasks?status=0&overdue=true
        """
        project = self.get_object()
        tasks = project.tasks.filter(deleted_at__isnull=True)

        # Apply filters
        filterset = TaskFilter(request.GET, queryset=tasks)
        filtered_tasks = filterset.qs

        # Paginate
        page = self.paginate_queryset(filtered_tasks)
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskListSerializer(filtered_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="tasks/create")
    def create_task(self, request, pk=None):
        """
        Create a task within a project
        POST /api/v1/projects/{id}/tasks/create
        """
        project = self.get_object()
        serializer = TaskCreateSerializer(
            data=request.data, context={"view": self, "request": request}
        )

        if serializer.is_valid():
            task = serializer.save(project_id=project.id)
            return Response(
                TaskDetailSerializer(task).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        """
        Soft delete or restore a project
        POST /api/v1/projects/{id}/soft-delete
        Body: {"action": "delete" | "restore"}
        """
        project = self.get_object()
        action_type = request.data.get("action")

        if action_type == "delete":
            project.delete()  # Soft delete from AbstractBaseModel
            return Response({"message": "Project soft deleted successfully"})
        elif action_type == "restore":
            project.restore_deleted()
            return Response({"message": "Project restored successfully"})
        else:
            return Response(
                {"error": "action must be 'delete' or 'restore'"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tasks with full CRUD operations
    Includes filtering, status updates, and soft delete
    """

    queryset = (
        Task.objects.filter(deleted_at__isnull=True)
        .select_related("project", "project__company", "parent")
        .prefetch_related("assignees", "subtasks")
    )
    permission_classes = [AllowAny]  # TODO: Add IsAuthenticated for production
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return TaskListSerializer
        elif self.action == "create":
            return TaskCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TaskUpdateSerializer
        return TaskDetailSerializer

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """
        Update task status
        POST /api/v1/tasks/{id}/update-status
        Body: {"status": 0 | 1 | 2}
        """
        task = self.get_object()
        new_status = request.data.get("status")

        # Validate status
        valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Choose from: {Task.STATUS_CHOICES}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task.status = new_status
        task.save(update_fields=["status"])

        return Response(TaskDetailSerializer(task).data)

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request, pk=None):
        """
        Soft delete or restore a task
        POST /api/v1/tasks/{id}/soft-delete
        Body: {"action": "delete" | "restore"}
        """
        task = self.get_object()
        action_type = request.data.get("action")

        if action_type == "delete":
            task.delete()  # Soft delete from AbstractBaseModel
            return Response({"message": "Task soft deleted successfully"})
        elif action_type == "restore":
            task.restore_deleted()
            return Response({"message": "Task restored successfully"})
        else:
            return Response(
                {"error": "action must be 'delete' or 'restore'"},
                status=status.HTTP_400_BAD_REQUEST,
            )
