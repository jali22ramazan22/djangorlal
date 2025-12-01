"""Admin configuration for CustomUser"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.auths.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin panel configuration for CustomUser"""

    list_display = ("email", "full_name", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("email", "full_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("full_name",)}),
        ("Permission", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        None,
        {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2"),
        },
    )

    readonly_fields = ("created_at", "updated_at", "last_login")
