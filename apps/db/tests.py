# from django.db.models.expressions import result

from django.test import TestCase
from django.utils import timezone
from apps.db.models import Company, JiraUser, Project, Task, TaskFilter


class JiraModelsAndFiltersTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(company_name="Test Company")
        self.user = JiraUser.objects.create_user(
            username="test.user",
            company_id=self.company.id,
            role="Engineer",
        )
        self.project = Project.objects.create(
            project_name="Test Project",
            company_id=self.company
        )
        self.task_open = Task.objects.create(
            title="Implement feature",
            category= "Backend",
            project=self.project,
            assignee= self.user,
            deadline= timezone.now().date(),
        )
        self.task_closed = Task.objects.create(
            title="Fix bag",
            category= "QA",
            project=self.project,
            assignee= self.user,
            completed_at= timezone.now().date(),
            deadline= timezone.now().date(),
        )
    def test_compony_str(self):
        self.assertIn("Test Company", str(self.company))

    def test_project_str(self):
        self.assertIn("Test Project", str(self.project))

    def test_user_str(self):
        self.assertIn("test.user", str(self.user))

    def test_task_str(self):
        self.assertIn("Implement feature", str(self.task_open))

    def test_task_status_open(self):
        self.assertEqual(self.task_open.status, "open")

    def test_task_status_closed(self):
        self.assertEqual(self.task_closed.status, "closed")

    def test_task_overdue_property(self):
        task = Task.objects.create(
            title = "Overdue check",
            category= "QA",
            project=self.project,
            deadline= timezone.now().date(),
        )
        self.assertIn(task.status, [True, False])

    def test_to_json_includes_expected_fields(self):
        data = self.task_open.to_json()
        for key in ["status", "overdue", "project", "assignee"]:
            self.assertIn(key, data)

    def test_filter_by_status_open(self):
        tasks = [self.task_open, self.task_closed]
        result = TaskFilter.filter_by_status(tasks, "open")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, "open")

    def test_filter_by_status_closed(self):
        tasks = [self.task_open, self.task_closed]
        result = TaskFilter.filter_by_status(tasks, "closed")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, "closed")

    def test_filter_by_overdue_false(self):
        tasks = [self.task_open]
        result = TaskFilter.filter_by_overdue(tasks, "false")
        self.assertEqual(result, tasks)

    def test_taskfilter_apply_combined(self):
        queryset = Task.objects.all()
        result = TaskFilter.apply(
            queryset,
            project_id= self.project.id,
            assignee_id=self.user.id,
            status="open",
        )
        self.assertTrue(all(t.status == "open" for t in result))
