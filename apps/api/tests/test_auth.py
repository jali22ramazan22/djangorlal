"""
Tests for authentication endpoints
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthEndpoints:
    """Test authentication API endpoints"""

    def test_user_login_success(self, api_client, regular_user):
        """Test successful user login"""
        url = reverse("user-login")
        data = {"email": "user@test.com", "password": "testpass123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["email"] == "user@test.com"
        assert response.data["full_name"] == "Regular Test User"

    def test_user_login_invalid_credentials(self, api_client, regular_user):
        """Test login with invalid credentials"""
        url = reverse("user-login")
        data = {"email": "user@test.com", "password": "wrongpassword"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_login_nonexistent_email(self, api_client):
        """Test login with nonexistent email"""
        url = reverse("user-login")
        data = {"email": "nonexistent@test.com", "password": "testpass123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_login_missing_fields(self, api_client):
        """Test login with missing required fields"""
        url = reverse("user-login")

        # Missing password
        response = api_client.post(url, {"email": "user@test.com"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Missing email
        response = api_client.post(url, {"password": "testpass123"}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_personal_info_authenticated(self, authenticated_client, regular_user):
        """Test retrieving personal info when authenticated"""
        url = reverse("user-personal-info")

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == regular_user.email
        assert response.data["full_name"] == regular_user.full_name
        assert "id" in response.data

    def test_personal_info_unauthenticated(self, unauthenticated_client):
        """Test retrieving personal info without authentication"""
        url = reverse("user-personal-info")

        response = unauthenticated_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
