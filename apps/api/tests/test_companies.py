"""
Tests for company endpoints
"""

import pytest
from django.urls import reverse
from rest_framework import status
from apps.db.models import Company


@pytest.mark.django_db
class TestCompanyEndpoints:
    """Test company API endpoints"""

    def test_list_companies(self, api_client, company):
        """Test listing all companies"""
        url = reverse("company-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(c["company_name"] == "Test Company" for c in response.data)

    def test_retrieve_company(self, api_client, company):
        """Test retrieving a single company"""
        url = reverse("company-detail", kwargs={"pk": company.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["company_name"] == "Test Company"
        assert response.data["id"] == company.id

    def test_retrieve_nonexistent_company(self, api_client):
        """Test retrieving a company that doesn't exist"""
        url = reverse("company-detail", kwargs={"pk": 99999})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_companies_excludes_soft_deleted(self, api_client, company):
        """Test that soft-deleted companies are not returned"""
        # Soft delete the company
        company.delete()

        url = reverse("company-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        company_ids = [c["id"] for c in response.data]
        assert company.id not in company_ids
