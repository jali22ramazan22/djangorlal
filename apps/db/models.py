from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from apps.abstracts.models import AbstractBaseModel


class Company(AbstractBaseModel):
    """Company model"""

    company_name = models.CharField(
        max_length=100, db_index=True, verbose_name="Company Name"
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["-created_at"]
        db_table = "companies"

    def __str__(self):
        return f"{self.company_name}"

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.company_name})>"


class Project(AbstractBaseModel):
    """Project model with author and team members"""

    name = models.CharField(max_length=100, db_index=True, verbose_name="Project name")

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Company",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_projects",
        verbose_name="Author",
    )

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        blank=True,
        verbose_name="Team Members",
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]
        db_table = "projects"

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"


class Task(AbstractBaseModel):
    """Task model with status tracking and assignees"""

    # Status choices
    TODO = 0
    IN_PROGRESS = 1
    DONE = 2

    STATUS_CHOICES = [
        (TODO, "To Do"),
        (IN_PROGRESS, "In Progress"),
        (DONE, "Done"),
    ]

    title = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Title",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
    )
    category = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Category",
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=TODO,
        verbose_name="Status",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Project",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subtasks",
        verbose_name="Parent Task",
    )

    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="UserTask",
        related_name="assigned_tasks",
        blank=True,
    )
    deadline = models.DateField(
        blank=True,
        null=True,
        verbose_name="Deadline",
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]
        db_table = "tasks"

    def __str__(self):
        return f"{self.title} - {self.project.name}"

    @property
    def is_completed(self) -> bool:
        """Check if tasks is completed"""
        return self.status == self.DONE

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.deadline and not self.is_completed:
            return self.deadline < date.today()
        return False


class UserTask(models.Model):
    """
    Intermediate model for User-Task many-to-many relationship
    Allows tracking when user was assigned to task
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User"
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Task")

    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Assigned At")

    class Meta:
        unique_together = ("user", "task")
        verbose_name = "User Task Assignment"
        verbose_name_plural = "User Task Assignments"
        ordering = ["-assigned_at"]
        db_table = "user_tasks"

    def __str__(self) -> str:
        return f"{self.user.email} -> {self.task.title}"

    def __repr__(self) -> str:
        return f"<UserTask(user_id={self.user.id}, task_id={self.task.id})>"
