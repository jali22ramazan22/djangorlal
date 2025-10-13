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
    # Companies & Projects
    CompanyListView,
    CompanyDetailView,
    ProjectListView,
    ProjectDetailView,
    # Dashboard
    DashboardView,
)

urlpatterns = [
    # -------------------- TASKS --------------------
    path("tasks/", TaskListView.as_view(), name="task_list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path(
        "tasks/<int:pk>/status/",
        TaskStatusUpdateView.as_view(),
        name="task_status_update",
    ),
    path("tasks/<int:pk>/soft/", TaskSoftDeleteView.as_view(), name="task_soft_delete"),
    # -------------------- USERS --------------------
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
    # -------------------- COMPANIES --------------------
    path("companies/", CompanyListView.as_view(), name="company_list"),
    path("companies/<int:pk>/", CompanyDetailView.as_view(), name="company_detail"),
    # -------------------- PROJECTS --------------------
    path("projects/", ProjectListView.as_view(), name="project_list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project_detail"),
    # -------------------- DASHBOARD --------------------
    path("dashboard/<int:user_id>", DashboardView.as_view(), name="dashboard"),
]
