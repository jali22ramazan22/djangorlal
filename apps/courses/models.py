# Django modules
from django.db.models import (
    CharField,
    BooleanField,
    TextField,
    ForeignKey,
    DecimalField,
    PositiveSmallIntegerField,
    CASCADE,
)

# Project modules
from apps.abstracts.models import AbstractBaseModel
from apps.auths.models import CustomUser


# Create your models here.
class Course(AbstractBaseModel):
    """
    Model is a course in a learning site
    """

    title = CharField(max_length=128)
    is_active = BooleanField(default=True)
    description = TextField(blank=True, null=True)
    owner = ForeignKey(CustomUser, on_delete=CASCADE, related_name="owned_courses")


class Lesson(AbstractBaseModel):
    """Model is a lesson in a course"""

    title = CharField(max_length=128)
    content = TextField()
    order = DecimalField(max_digits=5, decimal_places=2)
    indentation = PositiveSmallIntegerField(max_length=5)
    is_published = BooleanField(default=False)
    course = ForeignKey(Course, on_delete=CASCADE, related_name="lessons")
