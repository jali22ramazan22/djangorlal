from django.urls import path
from apps.api.views import (
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskStatusUpdateView,
    TaskSoftDeleteView,
)

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="task_list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path(
        "tasks/<int:pk>/status/",
        TaskStatusUpdateView.as_view(),
        name="task_status_update",
    ),
    path("tasks/<int:pk>/soft/", TaskSoftDeleteView.as_view(), name="task_soft_delete"),
]
