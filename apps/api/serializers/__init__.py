"""
API Serializers Package
Exports all serializers for easy importing
"""

from .user import (
    CustomUserForeignSerializer,
    CustomUserListSerializer,
    CustomUserDetailSerializer,
)
from .company import CompanySerializer, CompanyDetailSerializer
from .project import (
    ProjectBaseSerializer,
    ProjectListSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectDetailSerializer,
)
from .task import (
    TaskListSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskDetailSerializer,
)

__all__ = [
    # User serializers
    "CustomUserForeignSerializer",
    "CustomUserListSerializer",
    "CustomUserDetailSerializer",
    # Company serializers
    "CompanySerializer",
    "CompanyDetailSerializer",
    # Project serializers
    "ProjectBaseSerializer",
    "ProjectListSerializer",
    "ProjectCreateSerializer",
    "ProjectUpdateSerializer",
    "ProjectDetailSerializer",
    # Task serializers
    "TaskListSerializer",
    "TaskCreateSerializer",
    "TaskUpdateSerializer",
    "TaskDetailSerializer",
]
