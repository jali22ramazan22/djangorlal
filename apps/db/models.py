from django.db import models

from apps.abstracts.models import AbstractSoftDeletableModel
from django.contrib.auth.models import User


class Company(AbstractSoftDeletableModel):
    company_name = models.CharField(max_length=100)


class JiraUser(User):
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)


class Project(AbstractSoftDeletableModel):
    project_name = models.CharField(max_length=100)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)


class Task(AbstractSoftDeletableModel):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignee = models.ForeignKey(JiraUser, on_delete=models.CASCADE)
    deadline = models.DateField()
    completed_at = models.DateField()
    created_at = models.DateField()
