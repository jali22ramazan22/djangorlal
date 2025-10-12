from django.contrib import admin

from apps.books.models import *

admin.site.register(BookAuthor)  # noqa
admin.site.register(Book)  # noqa
