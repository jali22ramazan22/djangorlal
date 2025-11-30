from django.contrib.admin import ModelAdmin, register
from apps.courses.models import Lesson, Course


# Register your models here.
@register(Lesson)
class LessonAdmin(ModelAdmin):
    """Admin model for Lesson"""

    ...


@register(Course)
class CourseAdmin(ModelAdmin):
    """Admin model for Course"""

    ...
