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
