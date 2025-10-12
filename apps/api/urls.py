from django.urls import path
from apps.api.views import get_companies, get_users


urlpatterns = [path("companies/", get_companies), path("users/", get_users)]
