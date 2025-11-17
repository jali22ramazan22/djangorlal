from typing import Any
from django.db.models import Model, DateTimeField
from datetime import timezone


class AbstractBaseModel(Model):
    """
    Abstract base model for all models in the application
    """

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    deleted_at = DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __delete__(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        self.deleted_at = timezone.now()
        self.save()
