from typing import Any
from django.db import models
from django.utils import timezone as django_timezone


class AbstractSoftDeletableModel(models.Model):
    """Abstract base model with common fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Soft delete the object by setting deleted_at timestamp."""
        self.deleted_at = django_timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore_deleted(self) -> None:
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])


class Person(AbstractSoftDeletableModel):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    class Meta:
        abstract = True
