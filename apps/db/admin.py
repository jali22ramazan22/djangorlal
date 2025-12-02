# Django modules
from django.contrib import admin
from unfold.admin import ModelAdmin

# Project modules
from apps.db.models import Company, Project, Task, UserTask


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ("company_name", "created_at", "updated_at")
    search_fields = ("company_name",)
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ("name", "company", "author", "created_at", "updated_at")
    search_fields = ("name", "company__company_name", "author__email")
    list_filter = ("company", "created_at", "updated_at")
    ordering = ("-created_at",)
    raw_id_fields = ("company", "author", "users")
    filter_horizontal = ("users",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = (
        "title",
        "project",
        "category",
        "status",
        "deadline",
        "is_completed",
        "is_overdue",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "description", "category", "project__name")
    list_filter = (
        "status",
        "project",
        "category",
        "deadline",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    raw_id_fields = ("project", "parent", "assignees")
    readonly_fields = ("created_at", "updated_at")

    def is_completed(self, obj):
        return obj.is_completed

    is_completed.boolean = True
    is_completed.short_description = "Completed"

    def is_overdue(self, obj):
        return obj.is_overdue

    is_overdue.boolean = True
    is_overdue.short_description = "Overdue"


@admin.register(UserTask)
class UserTaskAdmin(ModelAdmin):
    list_display = ("user", "task", "assigned_at")
    search_fields = ("user__email", "user__username", "task__title")
    list_filter = ("assigned_at",)
    ordering = ("-assigned_at",)
    raw_id_fields = ("user", "task")
    readonly_fields = ("assigned_at",)
