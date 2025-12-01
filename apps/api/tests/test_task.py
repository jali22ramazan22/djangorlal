"""
Tests for task endpoints
"""

import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from apps.db.models import Task, Project


@pytest.mark.django_db
class TestTaskEndpoints:
    """Test task API endpoints"""

    def test_list_tasks(self, api_client, task):
        """Test listing all tasks"""
        url = reverse("task-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert any(t["title"] == "Test Task" for t in response.data)

    def test_list_tasks_filter_by_project(self, api_client, project, task):
        """Test filtering tasks by project"""
        url = reverse("task-list")

        response = api_client.get(url, {"project": project.id})

        assert response.status_code == status.HTTP_200_OK
        for task_data in response.data:
            assert task_data["project"]["id"] == project.id

    def test_list_tasks_filter_by_status(self, api_client, task, completed_task):
        """Test filtering tasks by status"""
        url = reverse("task-list")

        # Filter by TODO status
        response = api_client.get(url, {"status": Task.TODO})
        assert response.status_code == status.HTTP_200_OK
        for task_data in response.data:
            assert task_data["status"]["value"] == Task.TODO

        # Filter by DONE status
        response = api_client.get(url, {"status": Task.DONE})
        assert response.status_code == status.HTTP_200_OK
        for task_data in response.data:
            assert task_data["status"]["value"] == Task.DONE

    def test_list_tasks_filter_by_assignee(self, api_client, task, regular_user):
        """Test filtering tasks by assignee"""
        url = reverse("task-list")

        response = api_client.get(url, {"assignee": regular_user.id})

        assert response.status_code == status.HTTP_200_OK
        # Verify all returned tasks have the assignee
        for task_data in response.data:
            assignee_ids = [a["id"] for a in task_data["assignees"]]
            assert regular_user.id in assignee_ids

    def test_list_tasks_filter_by_category(self, api_client, task):
        """Test filtering tasks by category"""
        url = reverse("task-list")

        response = api_client.get(url, {"category": "Backend"})

        assert response.status_code == status.HTTP_200_OK
        for task_data in response.data:
            assert task_data["category"].lower() == "backend"

    def test_create_task(self, api_client, project, regular_user):
        """Test creating a new task"""
        url = reverse("task-list")
        data = {
            "title": "New Test Task",
            "description": "Task description here",
            "category": "Frontend",
            "project_id": project.id,
            "assignee_ids": [regular_user.id],
            "deadline": (timezone.now().date() + timedelta(days=7)).isoformat(),
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Test Task"
        assert response.data["category"] == "Frontend"
        assert response.data["project"]["id"] == project.id

    def test_create_task_missing_required_fields(self, api_client):
        """Test creating a task without required fields"""
        url = reverse("task-list")
        data = {"description": "Missing title and project"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_task(self, api_client, task):
        """Test retrieving a single task"""
        url = reverse("task-detail", kwargs={"pk": task.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Task"
        assert response.data["id"] == task.id
        assert "project" in response.data
        assert "assignees" in response.data

    def test_update_task(self, api_client, task):
        """Test updating a task"""
        url = reverse("task-detail", kwargs={"pk": task.id})
        data = {
            "title": "Updated Task Title",
            "description": task.description,
            "category": task.category,
            "project_id": task.project.id,
            "status": Task.IN_PROGRESS,
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Task Title"
        assert response.data["status"]["value"] == Task.IN_PROGRESS

    def test_partial_update_task(self, api_client, task):
        """Test partial update of a task"""
        url = reverse("task-detail", kwargs={"pk": task.id})
        data = {"status": Task.DONE}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"]["value"] == Task.DONE
        assert response.data["title"] == task.title  # Unchanged

    def test_delete_task(self, api_client, task):
        """Test soft deleting a task"""
        url = reverse("task-detail", kwargs={"pk": task.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft delete
        task.refresh_from_db()
        assert task.deleted_at is not None

    def test_update_task_status(self, api_client, task):
        """Test updating task status via dedicated endpoint"""
        url = reverse("task-update-status", kwargs={"pk": task.id})
        data = {"status": Task.DONE}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"]["value"] == Task.DONE

        # Verify in database
        task.refresh_from_db()
        assert task.status == Task.DONE

    def test_update_task_status_invalid(self, api_client, task):
        """Test updating task status with invalid value"""
        url = reverse("task-update-status", kwargs={"pk": task.id})
        data = {"status": 999}  # Invalid status

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_task_is_overdue_property(self, api_client, task):
        """Test task is_overdue computed property"""
        # Set deadline in the past
        task.deadline = timezone.now().date() - timedelta(days=1)
        task.status = Task.TODO
        task.save()

        url = reverse("task-detail", kwargs={"pk": task.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_overdue"] is True

    def test_task_is_completed_property(self, api_client, completed_task):
        """Test task is_completed computed property"""
        url = reverse("task-detail", kwargs={"pk": completed_task.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_completed"] is True
        assert response.data["status"]["value"] == Task.DONE

    def test_list_tasks_filter_by_overdue(self, api_client, task):
        """Test filtering tasks by overdue status"""
        # Create an overdue task
        overdue_task = Task.objects.create(
            title="Overdue Task",
            description="This task is overdue",
            category="Backend",
            status=Task.TODO,
            project=task.project,
            deadline=timezone.now().date() - timedelta(days=2),
        )

        url = reverse("task-list")

        # Filter overdue tasks
        response = api_client.get(url, {"overdue": "true"})
        assert response.status_code == status.HTTP_200_OK
        # Should include overdue task
        overdue_ids = [t["id"] for t in response.data if t.get("is_overdue")]
        assert overdue_task.id in overdue_ids

    def test_create_task_with_multiple_assignees(
        self, api_client, project, regular_user, another_user
    ):
        """Test creating a task with multiple assignees"""
        url = reverse("task-list")
        data = {
            "title": "Multi-Assignee Task",
            "description": "Task with multiple assignees",
            "category": "Backend",
            "project_id": project.id,
            "assignee_ids": [regular_user.id, another_user.id],
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["assignees"]) == 2
        assignee_ids = [a["id"] for a in response.data["assignees"]]
        assert regular_user.id in assignee_ids
        assert another_user.id in assignee_ids

    def test_create_subtask_with_parent(self, api_client, task):
        """Test creating a subtask with parent task"""
        url = reverse("task-list")
        data = {
            "title": "Subtask",
            "description": "This is a subtask",
            "category": "Backend",
            "project_id": task.project.id,
            "parent": task.id,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["parent"] is not None
        assert response.data["parent"]["id"] == task.id

    def test_retrieve_task_with_subtasks(self, api_client, task):
        """Test that task detail includes subtasks"""
        # Create subtasks
        subtask1 = Task.objects.create(
            title="Subtask 1", category="Backend", project=task.project, parent=task
        )
        subtask2 = Task.objects.create(
            title="Subtask 2", category="Frontend", project=task.project, parent=task
        )

        url = reverse("task-detail", kwargs={"pk": task.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "subtasks" in response.data
        assert len(response.data["subtasks"]) == 2
        subtask_ids = [s["id"] for s in response.data["subtasks"]]
        assert subtask1.id in subtask_ids
        assert subtask2.id in subtask_ids

    def test_update_task_assignees(self, api_client, task, another_user):
        """Test updating task assignees"""
        url = reverse("task-detail", kwargs={"pk": task.id})

        # Get current assignees count
        initial_assignees = list(task.assignees.all())

        # Update with new assignee
        data = {
            "title": task.title,
            "category": task.category,
            "project_id": task.project.id,
            "assignee_ids": [another_user.id],
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["assignees"]) == 1
        assert response.data["assignees"][0]["id"] == another_user.id

        # Verify in database
        task.refresh_from_db()
        assert list(task.assignees.all()) == [another_user]

    def test_partial_update_task_add_deadline(self, api_client, task):
        """Test adding deadline via partial update"""
        # Task initially has no deadline set to None
        task.deadline = None
        task.save()

        url = reverse("task-detail", kwargs={"pk": task.id})
        new_deadline = (timezone.now().date() + timedelta(days=14)).isoformat()
        data = {"deadline": new_deadline}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["deadline"] == new_deadline

    def test_task_soft_delete_excludes_from_list(self, api_client, task):
        """Test that soft-deleted tasks are excluded from list"""
        task_id = task.id

        # Soft delete
        task.delete()

        url = reverse("task-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        task_ids = [t["id"] for t in response.data]
        assert task_id not in task_ids

    def test_cannot_create_task_with_nonexistent_project(self, api_client):
        """Test creating task with non-existent project fails"""
        url = reverse("task-list")
        data = {
            "title": "Invalid Task",
            "category": "Backend",
            "project_id": 99999,  # Non-existent
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_create_task_with_nonexistent_assignee(self, api_client, project):
        """Test creating task with non-existent assignee fails gracefully"""
        url = reverse("task-list")
        data = {
            "title": "Task with Bad Assignee",
            "category": "Backend",
            "project_id": project.id,
            "assignee_ids": [99999],  # Non-existent user
        }

        response = api_client.post(url, data, format="json")
        # Should create task but with no assignees
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["assignees"]) == 0

    def test_update_status_to_in_progress(self, api_client, task):
        """Test updating task status to IN_PROGRESS"""
        url = reverse("task-update-status", kwargs={"pk": task.id})
        data = {"status": Task.IN_PROGRESS}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"]["value"] == Task.IN_PROGRESS

    def test_completed_task_not_overdue(self, api_client):
        """Test that completed tasks are never overdue even with past deadline"""
        project = Project.objects.first()
        if not project:
            pytest.skip("No project available")

        task = Task.objects.create(
            title="Completed Past Deadline",
            category="Backend",
            project=project,
            status=Task.DONE,
            deadline=timezone.now().date() - timedelta(days=5),
        )

        url = reverse("task-detail", kwargs={"pk": task.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_overdue"] is False
        assert response.data["is_completed"] is True

    def test_list_tasks_combined_filters(self, api_client, project, regular_user):
        """Test combining multiple filters"""
        # Create various tasks
        Task.objects.create(
            title="Backend TODO", category="Backend", status=Task.TODO, project=project
        )
        backend_done = Task.objects.create(
            title="Backend DONE", category="Backend", status=Task.DONE, project=project
        )

        url = reverse("task-list")

        # Filter by category AND status
        response = api_client.get(url, {"category": "Backend", "status": Task.DONE})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        for task_data in response.data:
            assert task_data["category"].lower() == "backend"
            assert task_data["status"]["value"] == Task.DONE
