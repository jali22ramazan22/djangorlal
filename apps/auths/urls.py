"""API URls configuration with DRF Router"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.auths.views import CustomUserViewSet

# Create router with trailing_slash=False (like the origin our repo)
router = DefaultRouter(trailing_slash=False)


router.register(r"users", CustomUserViewSet, basename="user")

urlpatterns = [
    # Including all router urls
    path("", include(router.urls))
]
