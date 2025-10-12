from typing import Any

from apps.abstracts.models import AbstractSoftDeletableModel, Person
from django.db import models
from django.core.exceptions import ValidationError


class BookAuthor(Person):

    bio = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.name} {self.surname}"


class Book(AbstractSoftDeletableModel):

    title = models.CharField(max_length=25)
    author = models.ForeignKey(
        BookAuthor,
        on_delete=models.CASCADE,
        related_name="books",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"],
                name="uq_book_author_title",
            )
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.author}"

    def clean(self) -> None:
        if getattr(self.author, "is_deleted", False):
            raise ValidationError({"author": _("Author is deleted.")})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)
