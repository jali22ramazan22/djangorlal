"""
DRF ViewSets using ViewSet base class (not ModelViewSet)
Following DRF best practices with explicit method definitions
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
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
from apps.api.permissions import (
    IsTaskAssigneeOrProjectMember,
    IsProjectAuthorOrReadOnly,
    IsCompanyMemberOrReadOnly,
)


class CompanyViewSet(viewsets.ViewSet):
    """
    ViewSet for companies with explicit methods
    Permissions: Anyone authenticated can read, only admins can modify
    """

    permission_classes = [IsCompanyMemberOrReadOnly]

    def list(self, request):
        """List all companies"""
        queryset = Company.objects.filter(deleted_at__isnull=True)

        # Pagination
        page = (
            self.paginate_queryset(queryset)
            if hasattr(self, "paginate_queryset")
            else None
        )
        if page is not None:
            serializer = CompanySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CompanySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Retrieve a single company"""
        queryset = Company.objects.filter(deleted_at__isnull=True)
        company = get_object_or_404(queryset, pk=pk)
        serializer = CompanyDetailSerializer(company)
        return Response(serializer.data)


class ProjectViewSet(viewsets.ViewSet):
    """
    ViewSet for projects with full CRUD operations
    Permissions: Project members can read, only author can modify
    """

    permission_classes = [IsProjectAuthorOrReadOnly]

    def list(self, request):
        """List all projects - only projects the user is a member of"""
        queryset = (
            Project.objects.filter(deleted_at__isnull=True, users=request.user)
            .select_related("company", "author")
            .prefetch_related("users")
        )

        page = (
            self.paginate_queryset(queryset)
            if hasattr(self, "paginate_queryset")
            else None
        )
        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new project"""
        serializer = ProjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectDetailSerializer(project).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Retrieve a single project"""
        queryset = (
            Project.objects.filter(deleted_at__isnull=True)
            .select_related("company", "author")
            .prefetch_related("users")
        )
        project = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, project)
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Full update of a project"""
        queryset = Project.objects.filter(deleted_at__isnull=True)
        project = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, project)
        serializer = ProjectUpdateSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(ProjectDetailSerializer(project).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """Partial update of a project"""
        queryset = Project.objects.filter(deleted_at__isnull=True)
        project = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, project)
        serializer = ProjectUpdateSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ProjectDetailSerializer(project).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Soft delete a project"""
        queryset = Project.objects.filter(deleted_at__isnull=True)
        project = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, project)
        project.delete()  # Soft delete from AbstractBaseModel
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="tasks")
    def get_tasks(self, request, pk=None):
        """Get all tasks for a project"""
        project = get_object_or_404(
            Project.objects.filter(deleted_at__isnull=True), pk=pk
        )
        self.check_object_permissions(request, project)
        tasks = project.tasks.filter(deleted_at__isnull=True)

        # Apply filters from query params
        status_filter = request.GET.get("status")
        category = request.GET.get("category")
        assignee = request.GET.get("assignee")

        if status_filter is not None:
            tasks = tasks.filter(status=status_filter)
        if category:
            tasks = tasks.filter(category__iexact=category)
        if assignee:
            tasks = tasks.filter(assignees__id=assignee)

        page = (
            self.paginate_queryset(tasks)
            if hasattr(self, "paginate_queryset")
            else None
        )
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="tasks/create")
    def create_task(self, request, pk=None):
        """Create a task within a project"""
        project = get_object_or_404(
            Project.objects.filter(deleted_at__isnull=True), pk=pk
        )
        self.check_object_permissions(request, project)
        serializer = TaskCreateSerializer(
            data=request.data, context={"view": self, "request": request}
        )

        if serializer.is_valid():
            task = serializer.save(project_id=project.id)
            return Response(
                TaskDetailSerializer(task).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskViewSet(viewsets.ViewSet):
    """
    ViewSet for tasks with full CRUD operations
    Permissions: Only project members can view tasks, only assignees can edit
    """

    permission_classes = [IsTaskAssigneeOrProjectMember]

    def list(self, request):
        """List all tasks with filtering - only tasks from user's projects"""
        # Filter tasks to only those from projects the user is a member of
        user_projects = Project.objects.filter(
            users=request.user, deleted_at__isnull=True
        )

        queryset = (
            Task.objects.filter(deleted_at__isnull=True, project__in=user_projects)
            .select_related("project", "project__company", "parent")
            .prefetch_related("assignees", "subtasks")
        )

        # Apply filters
        project = request.GET.get("project")
        assignee = request.GET.get("assignee")
        category = request.GET.get("category")
        status_filter = request.GET.get("status")

        if project:
            queryset = queryset.filter(project_id=project)
        if assignee:
            queryset = queryset.filter(assignees__id=assignee)
        if category:
            queryset = queryset.filter(category__iexact=category)
        if status_filter is not None:
            queryset = queryset.filter(status=status_filter)

        page = (
            self.paginate_queryset(queryset)
            if hasattr(self, "paginate_queryset")
            else None
        )
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Create a new task"""
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(
                TaskDetailSerializer(task).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Retrieve a single task"""
        queryset = (
            Task.objects.filter(deleted_at__isnull=True)
            .select_related("project", "project__company", "parent")
            .prefetch_related("assignees", "subtasks")
        )
        task = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, task)
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Full update of a task"""
        queryset = Task.objects.filter(deleted_at__isnull=True)
        task = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, task)
        serializer = TaskUpdateSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(TaskDetailSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """Partial update of a task"""
        queryset = Task.objects.filter(deleted_at__isnull=True)
        task = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, task)
        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(TaskDetailSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Soft delete a task"""
        queryset = Task.objects.filter(deleted_at__isnull=True)
        task = get_object_or_404(queryset, pk=pk)
        self.check_object_permissions(request, task)
        task.delete()  # Soft delete from AbstractBaseModel
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """Update task status"""
        task = get_object_or_404(Task.objects.filter(deleted_at__isnull=True), pk=pk)
        self.check_object_permissions(request, task)
        new_status = request.data.get("status")

        valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Choose from: {Task.STATUS_CHOICES}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task.status = new_status
        task.save(update_fields=["status"])

        return Response(TaskDetailSerializer(task).data)
