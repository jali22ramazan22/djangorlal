# Project modules
from decouple import config
from datetime import timedelta

# ----------------------------------------------
# Env id
#
ENV_POSSIBLE_OPTIONS = (
    "local",
    "prod",
)
ENV_ID = config("DJANGORLAR_ENV_ID", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)

# ----------------------------------------------
# REST Framework Configuration
#
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # For development
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ----------------------------------------------
# Simple JWT Configuration
#
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ----------------------------------------------
# DRF Spectacular (OpenAPI/Swagger) Configuration
#
SPECTACULAR_SETTINGS = {
    "TITLE": "Jira Clone API",
    "DESCRIPTION": "Task management system - Jira clone with Django REST Framework",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# ----------------------------------------------
# Debug Toolbar Configuration
#
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: config("DJANGO_DEBUG", default=False, cast=bool),
}

# ----------------------------------------------
# Shell Plus Configuration (django-extensions)
#
SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000
SHELL_PLUS = "ipython"
SHELL_PLUS_PRE_IMPORTS = [
    ("django.db", ("connection", "reset_queries", "connections")),
    ("datetime", ("datetime", "timedelta", "date")),
    ("json", ("loads", "dumps")),
]
