"""
Tests for project endpoints
"""

import pytest
from django.urls import reverse
from rest_framework import status
from apps.db.models import Project


@pytest.mark.django_db
class TestProjectEndpoints:
    """Test project API endpoints"""

    def test_list_projects(self, api_client, project):
        """Test listing all projects"""
        url = reverse("project-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(p["name"] == "Test Project" for p in response.data)

    def test_create_project(self, api_client, company, admin_user):
        """Test creating a new project"""
        url = reverse("project-list")
        data = {
            "name": "New Project",
            "company_id": company.id,
            "author_id": admin_user.id,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Project"
        assert response.data["company"]["id"] == company.id
        assert response.data["author"]["id"] == admin_user.id

    def test_create_project_invalid_data(self, api_client):
        """Test creating a project with invalid data"""
        url = reverse("project-list")
        data = {
            "name": "",  # Empty name
            "company_id": 99999,  # Nonexistent company
            "author_id": 99999,  # Nonexistent author
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_project(self, api_client, project):
        """Test retrieving a single project"""
        url = reverse("project-detail", kwargs={"pk": project.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Project"
        assert response.data["id"] == project.id
        assert "company" in response.data
        assert "author" in response.data

    def test_update_project(self, admin_client, project):
        """Test updating a project (only author can update)"""
        url = reverse("project-detail", kwargs={"pk": project.id})
        data = {
            "name": "Updated Project Name",
            "company_id": project.company.id,
            "author_id": project.author.id,
        }

        response = admin_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Project Name"

        # Verify in database
        project.refresh_from_db()
        assert project.name == "Updated Project Name"

    def test_partial_update_project(self, admin_client, project):
        """Test partial update of a project (only author can update)"""
        url = reverse("project-detail", kwargs={"pk": project.id})
        data = {"name": "Partially Updated"}

        response = admin_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Partially Updated"

    def test_delete_project(self, admin_client, project):
        """Test soft deleting a project (only author can delete)"""
        url = reverse("project-detail", kwargs={"pk": project.id})

        response = admin_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete
        project.refresh_from_db()
        assert project.deleted_at is not None

    def test_get_project_tasks(self, api_client, project, task):
        """Test retrieving all tasks for a project"""
        url = reverse("project-get-tasks", kwargs={"pk": project.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(t["title"] == "Test Task" for t in response.data)

    def test_get_project_tasks_with_filters(
        self, api_client, project, task, completed_task
    ):
        """Test filtering tasks by status"""
        url = reverse("project-get-tasks", kwargs={"pk": project.id})

        # Filter by status=2 (Done)
        response = api_client.get(url, {"status": 2})

        assert response.status_code == status.HTTP_200_OK
        # Should only return completed tasks
        for task_data in response.data:
            assert task_data["status"]["value"] == 2

    def test_create_task_in_project(self, api_client, project, regular_user):
        """Test creating a task within a project"""
        url = reverse("project-create-task", kwargs={"pk": project.id})
        data = {
            "title": "New Task in Project",
            "description": "Task description",
            "category": "Backend",
            "assignee_ids": [regular_user.id],
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Task in Project"
        assert response.data["project"]["id"] == project.id
