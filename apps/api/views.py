import json
from datetime import datetime

from django.http.response import HttpResponse, JsonResponse
from django.http.request import HttpRequest

from django.shortcuts import get_object_or_404
from apps.abstracts.views import BaseAPIView
from apps.abstracts.mixins import PaginatedMixin

from apps.db.models import JiraUser, Company, Task, Project  # noqa


class TaskListView(BaseAPIView, PaginatedMixin):

    def get(self, request: HttpRequest) -> HttpResponse:
        project_id = request.GET.get("project")
        assignee_id = request.GET.get("assignee")
        category = request.GET.get("category")
        overdue = request.GET.get("overdue")
        status = request.GET.get("status")

        queryset = Task.objects.filter()

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)
        if category:
            queryset = queryset.filter(category=category)

        task_list = list(queryset)

        if overdue == "true":
            task_list = [task for task in task_list if task.overdue]
        elif overdue == "false":
            task_list = [task for task in task_list if not task.overdue]

        if status == "open":
            task_list = [task for task in task_list if task.status == "open"]
        elif status == "closed":
            task_list = [task for task in task_list if task.status == "closed"]

        paginated_data = self.paginate_queryset_list(task_list)
        return JsonResponse(paginated_data)


class TaskCreateView(BaseAPIView):

    def post(self, request: HttpRequest) -> JsonResponse:
        data = json.loads(request.body)

        title = data.get("title")
        category = data.get("category")
        project_id = data.get("project_id")
        assignee_id = data.get("assignee_id")
        deadline = data.get("deadline")

        if not all([title, category, project_id]):
            return self.error_response("title, category и project_id required")

        project = get_object_or_404(Project, id=project_id)
        assignee = None
        if assignee_id:
            assignee = get_object_or_404(JiraUser, id=assignee_id)

        task = Task.objects.create(
            title=title,
            category=category,
            project=project,
            assignee=assignee,
            deadline=self.parse_date(deadline),
        )

        return self.json_response(task.to_json(), status=201)


class TaskDetailView(BaseAPIView):

    def get(self, request: HttpRequest, pk: int) -> JsonResponse:
        task = get_object_or_404(Task, id=pk)
        if task.is_deleted:
            return self.error_response("Task deleted", status=404)
        return self.json_response(task.to_json())


class TaskStatusUpdateView(BaseAPIView):

    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        task = get_object_or_404(Task, id=pk)

        data = json.loads(request.body)
        new_status = data.get("status")

        if new_status not in ["open", "closed"]:
            return self.error_response("status must be 'open' or 'closed'")

        if new_status == "closed":
            task.completed_at = datetime.now().date()
        else:
            task.completed_at = None

        task.save(update_fields=["completed_at"])
        return self.json_response(task.to_json())


class TaskSoftDeleteView(BaseAPIView):

    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        task = get_object_or_404(Task, id=pk)
        data = json.loads(request.body)
        action = data.get("action")

        if action == "delete":
            task.delete()
        elif action == "restore":
            task.restore_deleted()
        else:
            return self.error_response("action must be 'delete' or 'restore'")

        return self.json_response(task.to_json())
