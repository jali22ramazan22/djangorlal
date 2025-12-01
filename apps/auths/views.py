"""
Authentication views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema


from apps.auths.serializers import (
    UserLoginSerializer,
    UserLoginResponseSerializer,
    UserPersonalInfoSerializer,
)


class CustomUserViewSet(viewsets.GenericViewSet):
    """
    ViewSet for user authentication and profile
    Provides login and personal info endpoints
    """

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserLoginResponseSerializer},
        description="Login with email and password to receive JWT tokens",
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        """
        User login endpoint
        POST /api/v1/auth/users/login
        Body: {"email": "user@example.com", "password": "password"}
        Returns: JWT access and refresh tokens
        """
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: UserPersonalInfoSerializer},
        description="Get personal information of authenticated user",
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="personal-info",
    )
    def personal_info(self, request):
        """
        Get personal information of current user
        GET /api/v1/auth/users/personal-info
        Requires: JWT authentication
        """
        serializer = UserPersonalInfoSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
