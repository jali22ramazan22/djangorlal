# Django modules
from django.urls import include, path

# Django Rest Framework modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.auths.views import CustomUserViewSet
from apps.education.views import CourseViewSet

router: DefaultRouter = DefaultRouter(trailing_slash=False)
router.register(prefix="courses", viewset=CourseViewSet, basename="courses")

urlpatterns = [
    path("v1/", include(router.urls)),
]
