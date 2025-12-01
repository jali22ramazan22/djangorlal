"""
Pytest configuration and fixtures
"""

import pytest
from rest_framework.test import APIClient
from apps.auths.models import CustomUser
from apps.db.models import Company, Project, Task
from django.utils import timezone
from datetime import timedelta


@pytest.fixture
def unauthenticated_client():
    """
    Provide an unauthenticated API client
    """
    return APIClient()


@pytest.fixture
def api_client(regular_user):
    """
    Provide an authenticated API client (authenticated as regular_user)
    """
    client = APIClient()
    client.force_authenticate(user=regular_user)
    return client


@pytest.fixture
def admin_user(db):
    """
    Create an admin user
    """
    user = CustomUser.objects.create_user(
        email="admin@test.com",
        password="testpass123",
        full_name="Admin Test User",
        is_staff=True,
        is_superuser=True,
    )
    return user


@pytest.fixture
def regular_user(db):
    """
    Create a regular user
    """
    user = CustomUser.objects.create_user(
        email="user@test.com", password="testpass123", full_name="Regular Test User"
    )
    return user


@pytest.fixture
def another_user(db):
    """
    Create another regular user
    """
    user = CustomUser.objects.create_user(
        email="another@test.com", password="testpass123", full_name="Another Test User"
    )
    return user


@pytest.fixture
def authenticated_client(api_client, regular_user):
    """
    Provide an authenticated API client
    """
    api_client.force_authenticate(user=regular_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    Provide an admin authenticated API client
    """
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def company(db):
    """
    Create a test company
    """
    return Company.objects.create(company_name="Test Company")


@pytest.fixture
def project(db, company, admin_user, regular_user):
    """
    Create a test project with regular_user as a member
    """
    project = Project.objects.create(
        name="Test Project", company=company, author=admin_user
    )
    # Add users to the project so they have access
    project.users.add(admin_user, regular_user)
    return project


@pytest.fixture
def task(db, project, regular_user):
    """
    Create a test task
    """
    task = Task.objects.create(
        title="Test Task",
        description="Test task description",
        category="Backend",
        status=Task.TODO,
        project=project,
        deadline=timezone.now().date() + timedelta(days=7),
    )
    task.assignees.add(regular_user)
    return task


@pytest.fixture
def completed_task(db, project, regular_user):
    """
    Create a completed test task
    """
    task = Task.objects.create(
        title="Completed Task",
        description="This task is done",
        category="Frontend",
        status=Task.DONE,
        project=project,
        deadline=timezone.now().date() - timedelta(days=1),
    )
    task.assignees.add(regular_user)
    return task
