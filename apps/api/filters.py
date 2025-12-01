"""
Django filters for API querysets
"""

import django_filters
from apps.db.models import Task


class TaskFilter(django_filters.FilterSet):
    """
    Filter for tasks with multiple criteria
    Supports filtering by project, assignee, category, status, overdue, completed
    """

    project = django_filters.NumberFilter(field_name="project_id")
    assignee = django_filters.NumberFilter(field_name="assignees__id")
    category = django_filters.CharFilter(field_name="category", lookup_expr="iexact")
    status = django_filters.ChoiceFilter(
        field_name="status", choices=Task.STATUS_CHOICES
    )
    overdue = django_filters.BooleanFilter(method="filter_overdue")
    completed = django_filters.BooleanFilter(method="filter_completed")

    class Meta:
        model = Task
        fields = ["project", "assignee", "category", "status", "overdue", "completed"]

    def filter_overdue(self, queryset, name, value):
        """
        Filter tasks that are overdue
        Overdue = deadline passed AND status is not DONE
        """
        if value:
            from datetime import date

            return queryset.filter(
                deadline__lt=date.today(), status__in=[Task.TODO, Task.IN_PROGRESS]
            )
        return queryset

    def filter_completed(self, queryset, name, value):
        """
        Filter completed/incomplete tasks
        Completed = status is DONE
        """
        if value:
            return queryset.filter(status=Task.DONE)
        else:
            return queryset.exclude(status=Task.DONE)
