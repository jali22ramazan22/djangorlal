from django.db import models
from django.contrib.auth.models import User

from apps.abstracts.models import AbstractSoftDeletableModel
from apps.abstracts.mixins import JSONSerializerInstanceMixin

from datetime import datetime


class Company(AbstractSoftDeletableModel):
    company_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.company_name} - instance"


class JiraUser(User, JSONSerializerInstanceMixin):
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)

    def __str__(self):
        return f"Jira User with name {self.username}"

    def to_json(self) -> dict:
        data = super().to_json()

        if self.company_id:
            data["company"] = {
                "id": self.company_id.id,
                "name": self.company_id.company_name,
            }

        data.pop("password", None)
        data.pop("is_superuser", None)
        data.pop("company_id", None)

        return data


class Project(JSONSerializerInstanceMixin, AbstractSoftDeletableModel):
    project_name = models.CharField(max_length=100)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"Project {self.project_name}"

    def to_json(self):
        data = super().to_json()

        data.pop("company_id", None)

        data["company"] = {
            "company": {
                "id": self.company_id.id,
                "name": self.company_id.company_name,
            },
        }
        return data


class Task(AbstractSoftDeletableModel, JSONSerializerInstanceMixin):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignee = models.ForeignKey(
        JiraUser, on_delete=models.CASCADE, blank=True, null=True
    )
    deadline = models.DateField(blank=True, null=True)
    completed_at = models.DateField(blank=True, null=True)
    created_at = models.DateField(default=datetime.now())

    def __str__(self):
        return f"Task {self.title}-{self.category}-{self.project}-{self.deadline}"

    @property
    def status(self):
        if not self.completed_at:
            return "open"
        return "closed"

    @property
    def overdue(self):
        if self.deadline and not self.completed_at:
            return self.deadline < datetime.now().date()
        return False

    def to_json(self):
        data = super().to_json()
        data["project"] = {
            "id": self.project.id,
            "name": self.project.project_name,
            "company": {
                "id": self.project.company_id.id,
                "name": self.project.company_id.company_name,
            },
        }

        if self.assignee:
            data["assignee"] = {
                "id": self.assignee.id,
                "username": self.assignee.username,
                "role": self.assignee.role,
                "company": {
                    "id": self.assignee.company_id.id,
                    "name": self.assignee.company_id.company_name,
                },
            }
        else:
            data["assignee"] = None

        data["status"] = self.status
        data["overdue"] = self.overdue

        return data


class TaskFilter:
    @staticmethod
    def apply(
            queryset,
            *,
            project_id=None,
            assignee_id=None,
            category=None,
            overdue=None,
            status=None,
    ):
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)
        if category:
            queryset = queryset.filter(category=category)

        tasks = list(queryset)
        tasks = TaskFilter.filter_by_overdue(tasks, overdue)
        tasks = TaskFilter.filter_by_status(tasks, status)
        return tasks

    @staticmethod
    def filter_by_priority(task_list, priority):
        if not priority:
            return task_list
        return [t for t in task_list if getattr(t, "priority", None) == priority]

    @staticmethod
    def filter_by_overdue(task_list, overdue):
        if overdue == "true":
            return [t for t in task_list if t.overdue]
        if overdue == "false":
            return [t for t in task_list if not t.overdue]
        return task_list

    @staticmethod
    def filter_by_status(task_list, status):
        if status == "open":
            return [t for t in task_list if t.status == "open"]
        if status == "closed":
            return [t for t in task_list if t.status == "closed"]
        return task_list

    @staticmethod
    def sort(task_list, sort_by=None):
        if not sort_by:
            return task_list
        reverse = sort_by.startswith("-")
        key = sort_by.lstrip("-")
        try:
            return sorted(task_list, key=lambda t: getattr(t, key), reverse=reverse)
        except Exception:
            return task_list
