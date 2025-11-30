# Python modules
from typing import Any

# Django modules
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

# App modules
from apps.education.models import Course, Lesson
from apps.education.serializers import CourseSerializer, LessonSerializer
from apps.education.permissions import IsOwner


# Create your views here.
class CourseViewSet(ViewSet):
    """ViewSet for managing Courses"""

    permission_classes = (IsAuthenticated,)

    def list(self, request: Request) -> Response:

        courses = Course.objects.all()

        is_active = request.query_params.get("is_active")
        if not is_active:
            courses = courses.filter(is_active=is_active.lower() == "true")

        courses = courses.annotate(lessons_count=Count("lessons"))
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def create(self, request: Request) -> Response:
        serializer = CourseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer.save(author=request.user)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def retrieve(self, request: Request, pk: int) -> Response:
        course = get_object_or_404(Course, pk=pk)
        return Response(CourseSerializer(course).data, status=HTTP_200_OK)

    def update(self, request: Request, pk: int) -> Response:
        course = get_object_or_404(Course, pk=pk)
        self.check_object_permissions(request, course)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer.save(author=request.user)
        return Response(serializer.data, status=HTTP_200_OK)

    def delete(self, request: Request, pk: int) -> Response:
        course = get_object_or_404(Course, pk=pk)

        self.check_object_permissions(request, course)
        course.delete()
        return Response(status=HTTP_200_OK)

    def _change_activity(self, value: bool, request: Request, course: Course):
        self.check_object_permissions(request, course)
        course.is_active = value
        course.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=[IsAuthenticated, IsOwner],  # noqa
    )
    def activate(self, request: Request, pk: int):
        course = get_object_or_404(Course, pk=pk)
        return self._change_activity(True, request, course)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=[IsAuthenticated, IsOwner],  # noqa
    )
    def deactivate(self, request: Request, pk: int) -> Response:
        course = get_object_or_404(Course, pk=pk)
        return self._change_activity(False, request, course)

    @action(methods=["get"], detail=True, permission_classes=[AllowAny])
    def lessons(self, request: Request, pk: int) -> Response:
        course = get_object_or_404(Course, pk=pk)
        lessons = Lesson.objects.filter(course=course)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class ListViewSet(ViewSet):

    def create(self, request: Request) -> Response:
        course_id = request.data.get("course")
        course = get_object_or_404(Course, id=course_id)

        self.check_object_permissions(request, course)

        first = Lesson.objects.filter(course=course).order_by("order").first()
        order = first.order - 1 if first else 1

        serializer = LessonSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        serializer.save(course=course, order=order)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(methods=["put"], detail=True)
    def move(self, request: Request, pk: int) -> Response:
        lesson = get_object_or_404(Lesson, pk=pk)
        self.check_object_permissions(request, lesson.course)

        before_id = request.data.get("before_lesson_id")

        if before_id:
            before = Lesson.objects.filter(pk=before_id).first()
            if before:
                lesson.order = before.order - 1
        else:
            last = (
                Lesson.objects.filter(course=lesson.course).order_by("-order").first()
            )
            lesson.order = (last.order + 1) if last else 1

        lesson.save()
        serializer = LessonSerializer(lesson)
        return Response(
            {"detail": {"new_order": lesson.order, "lesson": serializer.data}},
            status=HTTP_200_OK,
        )

    def delete(self, request: Request, pk: int) -> Response:
        lesson = get_object_or_404(Lesson, pk=pk)

        self.check_object_permissions(request, lesson.course)

        lesson.delete()
        return Response(status=HTTP_200_OK)

    @action(methods=["post"], permission_classes=[AllowAny], detail=True)
    def publish(self, request: Request, pk: int) -> Response:
        lesson = get_object_or_404(Lesson, pk=pk)
        self.check_object_permissions(request, lesson.course)

        lesson.is_published = True
        lesson.save()
        serializer = LessonSerializer(lesson)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=["post"], permission_classes=[AllowAny], detail=True)
    def unpublish(self, request: Request, pk: int) -> Response:
        lesson = get_object_or_404(Lesson, pk=pk)
        self.check_object_permissions(request, lesson.course)

        lesson.is_published = False
        lesson.save()
        serializer = LessonSerializer(lesson)

        return Response(serializer.data, status=HTTP_200_OK)
