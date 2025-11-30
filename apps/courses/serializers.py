from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    SerializerMethodField,
    PrimaryKeyRelatedField,
    IntegerField,
    BooleanField,
)

from apps.auths.serializers import UserRelatedSerializer
from apps.courses.models import Course


class CourseSerializer(ModelSerializer):
    """Serializer for course model"""

    id = CharField(read_only=True)
    title = CharField(required=True, max_length=255)
    description = CharField(required=True)
    author = UserRelatedSerializer(read_only=True)
    lessons_count = SerializerMethodField()

    class Meta:
        model = Course
        fields = ("id", "title", "description", "author", "lessons_count")

    def get_lessons_count(self, obj: Course) -> int:
        return obj.lessons.filter(deleted_at__isnull=True).count()


class LessonSerializer(ModelSerializer):
    "Serializer for lesson Model"

    id = CharField(read_only=True)
    course = PrimaryKeyRelatedField(queryset=Course.objects.all(), required=True)
    title = CharField(required=True, max_length=255)
    content = CharField(required=True)
    order = IntegerField(required=True)
    is_published = BooleanField(required=True)
    indentation = IntegerField(required=True)
