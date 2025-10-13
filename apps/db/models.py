from django.db import models

from apps.abstracts.models import AbstractSoftDeletableModel
from django.contrib.auth.models import User

from datetime import datetime


class Company(AbstractSoftDeletableModel):
    company_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.company_name} - instance"


class JiraUser(User):
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)

    def __str__(self):
        return f"Jira User with name {self.username}"


class Project(AbstractSoftDeletableModel):
    project_name = models.CharField(max_length=100)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"Project {self.project_name}"


class Task(AbstractSoftDeletableModel):
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
        return self.deadline > datetime.now().date()
