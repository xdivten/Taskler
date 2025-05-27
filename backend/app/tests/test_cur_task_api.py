from datetime import date, timedelta

import pytest
from rest_framework import status

from .factories import RecurringTaskFactory, TaskFactory


@pytest.fixture
def setup_tasks_for_test_api(db, user):
    tasks = TaskFactory.create_batch(3, user=user, date=date.today())
    recurring_task = RecurringTaskFactory(user=user, start_date=date.today() - timedelta(days=date.today().weekday()))
    return tasks, recurring_task


@pytest.mark.django_db
class TestCurTaskAPI:

    def test_get_tasks_success(self, date_range_for_week, authenticated_client, setup_tasks_for_test_api):
        from_date, to_date = date_range_for_week
        tasks, _ = setup_tasks_for_test_api
        response = authenticated_client.get("/tasks/", {"from_date": from_date, "to_date": to_date})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"]
        assert "tasks" in response.data
        assert len(response.data["tasks"]) > len(tasks)

    def test_get_tasks_missing_date_range(self, authenticated_client):
        response = authenticated_client.get("/tasks/", {})

        assert response.status_code == 400
        assert not response.data["success"]
        assert "from_date" in response.data["errors"]
        assert "to_date" in response.data["errors"]

    def test_get_tasks_invalid_date_range(self, authenticated_client):
        response = authenticated_client.get("/tasks/", {"from_date": "invalid", "to_date": "invalid"})

        assert response.status_code == 400
        assert not response.data["success"]
        assert "from_date" in response.data["errors"]
        assert "to_date" in response.data["errors"]

    # def test_error_handling_in_generate_tasks(
    #     self, date_range_for_week, authenticated_client, mocker
    # ):
    #     mocker.patch(
    #         "backend.utils.task_list_generation.generate_tasks_for_week",
    #         side_effect=Exception("Test Error"),
    #     )
    #     from_date, to_date = date_range_for_week
    #     response = authenticated_client.get(
    #         "/tasks/", {"from_date": from_date, "to_date": to_date}
    #     )

    #     assert response.status_code == 400
    #     assert response.data["error"] == "Error generating tasks"
    #     assert response.data["detail"] == "Test Error"
