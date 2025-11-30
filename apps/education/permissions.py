from typing import Any
from rest_framework.permissions import BasePermission
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request


class IsOwner(BasePermission):
    """Custom Permission to only allow edit for owners only"""

    def has_object_permission(self, request: Request, view: ViewSet, obj: Any):
        return obj.owner == request.user
