"""
Custom permissions for API views
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRFRequest
from rest_framework.viewsets import ViewSet
from apps.db.models import Project, Task


class IsUserInProject(BasePermission):
    """
    Permission to check if user is a member of the project
    Checks if user is in project.users ManyToMany field
    """

    message = "Forbidden! You are not a member of this project."

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Project | int
    ) -> bool:
        """
        Check if request user is in project's team members
        """
        # Handle both Project objects and project_id integers
        project_id = obj.id if isinstance(obj, Project) else obj

        if not isinstance(project_id, int):
            return False

        # Check if user is in project
        return Project.objects.filter(users__id=request.user.id, id=project_id).exists()


class IsTaskAssignee(BasePermission):
    """
    Permission to check if user is assigned to the task
    Checks if user is in task.assignees ManyToMany field
    """

    message = "Forbidden! You are not assigned to this task."

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Task
    ) -> bool:
        """
        Check if request user is assigned to the task
        """
        return obj.assignees.filter(id=request.user.id).exists()


class IsProjectAuthor(BasePermission):
    """
    Permission to check if user is the author of the project
    Only author can delete/update certain fields
    """

    message = "Forbidden! Only project author can perform this action."

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Project
    ) -> bool:
        """
        Check if request user is the project author
        """
        return obj.author == request.user


class IsTaskAssigneeOrProjectMember(BasePermission):
    """
    Permission that allows:
    - Task assignees can view and edit their tasks
    - Project members can view tasks
    - Only assignees can edit tasks
    """

    message = "Forbidden! You must be assigned to this task or be a project member."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        """
        Allow authenticated users to list tasks, but filter by project membership
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Task
    ) -> bool:
        """
        Check permissions based on action:
        - GET: Project members can view
        - POST/PUT/PATCH/DELETE: Only assignees can edit
        """
        # Check if user is project member
        is_project_member = obj.project.users.filter(id=request.user.id).exists()

        # For read operations, project membership is enough
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return is_project_member

        # For write operations, must be assignee
        is_assignee = obj.assignees.filter(id=request.user.id).exists()
        return is_assignee or obj.project.author == request.user


class IsProjectAuthorOrReadOnly(BasePermission):
    """
    Permission that allows:
    - Project author can edit/delete project
    - Project members can view project and create tasks
    """

    message = "Forbidden! Only project author can modify this project."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        """
        Allow authenticated users to list projects
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Project
    ) -> bool:
        """
        Check permissions:
        - GET: Project members can view
        - POST (create_task action): Project members can create
        - PUT/PATCH/DELETE: Only author
        """
        is_project_member = obj.users.filter(id=request.user.id).exists()
        is_author = obj.author == request.user

        # For read operations
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return is_project_member or is_author

        # For create_task action, allow project members
        if (
            request.method == "POST"
            and hasattr(view, "action")
            and view.action == "create_task"
        ):
            return is_project_member or is_author

        # For write operations on project itself, only author
        return is_author


class IsCompanyMemberOrReadOnly(BasePermission):
    """
    Permission that allows:
    - Anyone can read companies (for browsing)
    - Only admin users can edit companies
    """

    message = "Forbidden! Only administrators can modify companies."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        """
        Allow authenticated users to list companies
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # For read operations, allow any authenticated user
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # For write operations, only staff/admin
        return request.user.is_staff or request.user.is_superuser

    def has_object_permission(self, request: DRFRequest, view: ViewSet, obj) -> bool:
        """
        Object-level check (same as has_permission logic)
        """
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        return request.user.is_staff or request.user.is_superuser
