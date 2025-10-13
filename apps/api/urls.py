# apps/api/urls.py
from django.urls import path
from apps.api.views import (
    # Tasks
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskStatusUpdateView,
    TaskSoftDeleteView,
    # Users
    JiraUserView,  # /users/<id>/tasks/
    JiraUserProfileView,  # /users/<id>/profile/
    UserChangePasswordView,  # /users/<id>/password/
    JiraUserSoftDeleteView,  # /users/<id>/soft/
)

urlpatterns = [
    # Task endpoints
    path("tasks/", TaskListView.as_view(), name="task_list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path(
        "tasks/<int:pk>/status/",
        TaskStatusUpdateView.as_view(),
        name="task_status_update",
    ),
    path("tasks/<int:pk>/soft/", TaskSoftDeleteView.as_view(), name="task_soft_delete"),
    # User endpoints
    path("users/<int:user_id>/tasks/", JiraUserView.as_view(), name="user_tasks"),
    path(
        "users/<int:user_id>/profile/",
        JiraUserProfileView.as_view(),
        name="user_profile",
    ),
    path(
        "users/<int:user_id>/password/",
        UserChangePasswordView.as_view(),
        name="user_change_password",
    ),
    path(
        "users/<int:user_id>/soft/",
        JiraUserSoftDeleteView.as_view(),
        name="user_soft_delete",
    ),
]
