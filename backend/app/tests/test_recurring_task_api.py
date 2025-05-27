import logging
from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from ..models import RecurringTask
from ..services.task_list_generator import TaskListGenerator
from .factories import RecurringTaskFactory, TaskFactory


logger = logging.getLogger("my_logger")


@pytest.fixture
def setup_tasks_for_test(db, date_range_for_week, user):
    from_date, to_date = date_range_for_week
    recurring_task = RecurringTaskFactory(
        user=user, repeat_type=RecurringTask.RepeatType.DAILY, interval=1, start_date=from_date
    )
    generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)
    tasks, _ = generator.generate()

    assert len(tasks) > 0
    return recurring_task, tasks


@pytest.mark.django_db
class TestRecciringTaskAPI:

    @pytest.mark.parametrize(
        "repeat_type, interval, days_of_week, days_of_month",
        [
            ("daily", 1, None, None),
            ("weekly", 1, [0, 3], None),
            ("monthly", 1, None, [date.today().strftime("%Y-%m-%d")]),
        ],
    )
    def test_reccuring_task_create_success(
        self, authenticated_client: APIClient, repeat_type, interval, days_of_week, days_of_month
    ):
        recurring_task = RecurringTaskFactory.build(
            repeat_type=repeat_type,
            interval=interval,
            days_of_week=days_of_week,
            days_of_month=days_of_month,
        )
        data = {
            "name": recurring_task.name,
            "repeat_type": recurring_task.repeat_type,
            "start_date": recurring_task.start_date,
            "end_date": recurring_task.end_date,
            "interval": recurring_task.interval,
            "days_of_week": recurring_task.days_of_week,
            "days_of_month": recurring_task.days_of_month,
        }
        response = authenticated_client.post("/repeat_task/", data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"]
        assert response.data["message"] == "Recurring task created succesfully"
        assert RecurringTask.objects.count() == 1
        created_repeat_task = RecurringTask.objects.first()
        assert created_repeat_task.name == data["name"]
        assert created_repeat_task.repeat_type == data["repeat_type"]

    @pytest.mark.parametrize(
        "start_date, repeat_type, interval, expected_error",
        [
            (date.today().strftime("%Y-%m-%d"), "daily", None, "Interval not provided"),
            (None, "weekly", None, None),
        ],
    )
    def test_recurring_task_create_with_invalid_data(
        self, authenticated_client: APIClient, start_date, repeat_type, interval, expected_error
    ):
        data = {
            "name": "task name",
            "repeat_type": repeat_type,
            "start_date": start_date,
            "interval": interval,
        }
        response = authenticated_client.post("/repeat_task/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not response.data["success"]
        assert response.data["message"] == "Validation failed"

        if start_date is None:
            assert "start_date" in response.data["errors"]
        if expected_error is not None:
            assert response.data["errors"]["detail"][0] == expected_error

    def test_recurring_task_update_date(self, authenticated_client: APIClient):
        recurring_task = RecurringTaskFactory()
        task = TaskFactory(parent=recurring_task)
        data = {"date": (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")}
        response = authenticated_client.patch(f"/task/{task.id}/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not response.data["success"]
        assert response.data["message"] == "it is impossible to change the date for repeat task"

    @pytest.mark.parametrize(
        "strategy, field, value",
        [
            ("single", "name", "New name"),
            ("single", "color", "#0123ab"),
            ("all", "name", "New name"),
            ("all", "color", "#1234ab"),
        ],
    )
    def test_recurring_task_update_success(
        self, setup_tasks_for_test, authenticated_client: APIClient, strategy, field, value
    ):
        recurring_task, tasks = setup_tasks_for_test

        data = {field: value, "strategy": strategy}
        response = authenticated_client.patch(f"/task/{tasks[0].id}/", data=data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert response.data["success"]
        assert response.data.get("id") is not None

        for task in tasks:
            task.refresh_from_db()
        recurring_task.refresh_from_db()

        if strategy == "single":
            assert response.data["message"] == "Single repeat task updated"
            if field == "name":
                assert recurring_task.name != data[field]
                assert tasks[0].name == data[field]
                assert tasks[1].name != data[field]
            elif field == "color":
                assert recurring_task.color != data[field]
                assert tasks[0].color == data[field]
                assert tasks[1].color != data[field]
        elif strategy == "all":
            assert response.data["message"] == "All repeat tasks updated"
            if field == "name":
                assert recurring_task.name == data[field]
                assert tasks[0].name == data[field]
                assert tasks[1].name == data[field]
            elif field == "color":
                assert recurring_task.color == data[field]
                assert tasks[0].color == data[field]
                assert tasks[1].color == data[field]

    @pytest.mark.parametrize("name, strategy", [(None, "all"), ("New name", None), ("New name", "not all")])
    def test_recurring_task_update_name_invalid_data(
        self, setup_tasks_for_test, authenticated_client: APIClient, name, strategy
    ):
        recurring_task, tasks = setup_tasks_for_test

        data = {"name": name, "strategy": strategy}
        response = authenticated_client.patch(f"/task/{tasks[0].id}/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["message"] == "Validation failed"
        assert not response.data["success"]

        if name is None:
            assert "name" in response.data["errors"]
            assert response.data["errors"]["name"][0] == "This field may not be null."
        if strategy is None or strategy not in ["all", "single"]:
            assert "strategy" in response.data["errors"]

    @pytest.mark.parametrize("color, strategy", [(None, "all"), ("#2a", "all"), ("#1green", "all"), ("red", "all")])
    def test_recurring_task_update_color_invalid_data(
        self, setup_tasks_for_test, authenticated_client: APIClient, color, strategy
    ):
        recurring_task, tasks = setup_tasks_for_test

        data = {"color": color, "strategy": strategy}
        response = authenticated_client.patch(f"/task/{tasks[0].id}/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data
        assert not response.data["success"]

        if color is None:
            assert response.data["errors"]["color"][0] == "This field may not be null."
        else:
            assert response.data["errors"]["color"][0] == "Wrong color hex code"

    @pytest.mark.parametrize("strategy", ["single", "all", None])
    def test_recurring_task_delete(self, setup_tasks_for_test, authenticated_client: APIClient, strategy):
        recurring_task, tasks = setup_tasks_for_test
        data = {"strategy": strategy}
        response = authenticated_client.delete(f"/task/{tasks[0].id}/", data=data)

        for task in tasks:
            task.refresh_from_db()
        recurring_task.refresh_from_db()

        if strategy == "single":
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert "detail" in response.data
            assert response.data["detail"] == "Single repeat task archived"
            assert not recurring_task.is_deleted
            assert tasks[0].is_deleted
            assert not tasks[1].is_deleted
        if strategy == "all":
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert "detail" in response.data
            assert response.data["detail"] == "Repeat task archived"
            assert recurring_task.is_deleted
            assert tasks[0].is_deleted
            assert tasks[1].is_deleted
        if strategy is None:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "strategy" in response.data
            assert not recurring_task.is_deleted
            assert not tasks[0].is_deleted
            assert not tasks[1].is_deleted
