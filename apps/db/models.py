from django.db import models

from apps.abstracts.models import AbstractSoftDeletableModel
from django.contrib.auth.models import User


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
    assignee = models.ForeignKey(JiraUser, on_delete=models.CASCADE)
    deadline = models.DateField()
    completed_at = models.DateField()
    created_at = models.DateField()

    def __str__(self):
        return f"Task {self.title}-{self.category}-{self.project}-{self.deadline}"
