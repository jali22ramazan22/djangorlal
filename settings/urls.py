from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from settings.base import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT, STATIC_URL


urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns += static(prefix=STATIC_URL, document_root=STATIC_ROOT)
urlpatterns += static(prefix=MEDIA_URL, document_root=MEDIA_ROOT)
