# Python modules
from typing import Any

# Django modules
from django.shortcuts import render
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated, AllowAny

# App modules
from apps.education.models import Course
from apps.education.serializers import CourseSerializer, LessonSerializer


# Create your views here.
class CourseViewSet(ViewSet):
    """ViewSet for managng Courses"""

    permission_classes = (IsAuthenticated,)

    def list(self, request: Request) -> Response:

        courses = Course.objects.all()

        is_active = request.query_params.get("is_active")
        if not is_active:
            courses = courses.filter(is_active=is_active.lower() == "true")

        courses = courses.annotate(lessons_count=Count("lessons"))
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    # def create(self, )
