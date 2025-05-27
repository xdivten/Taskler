from datetime import date

import pytest

from ..serializers import RecurringTaskSerializer
from .factories import RecurringTaskFactory


@pytest.mark.django_db
class TestRecurringTaskSetializer:

    @pytest.mark.parametrize(
        "repeat_type, interval, days_of_week, days_of_month",
        [
            ("daily", 1, None, None),
            ("weekly", 1, [0, 3], None),
            ("monthly", 1, None, [date.today().strftime("%Y-%m-%d")]),
        ],
    )
    def test_recurring_task_serializer(
        self, user, repeat_type, interval, days_of_week, days_of_month
    ):
        task = RecurringTaskFactory(
            user=user,
            repeat_type=repeat_type,
            interval=interval,
            days_of_week=days_of_week,
            days_of_month=days_of_month,
        )
        serializer = RecurringTaskSerializer(task)
        data = serializer.data

        assert task.user == user
        assert task.name == data["name"]
        assert task.repeat_type == data["repeat_type"]
        assert str(task.start_date) == data["start_date"]
        if task.end_date is None:
            assert data["end_date"] is None
        else:
            assert str(task.end_date) == data["end_date"]
        assert task.interval == data["interval"]
        assert task.days_of_week == data["days_of_week"]
        assert task.days_of_month == data["days_of_month"]
        assert task.is_deleted == data["is_deleted"]

    def test_recurring_task_serializer_deserialization(self, user, request_with_user):
        data = RecurringTaskFactory.build().__dict__
        serializer = RecurringTaskSerializer(data=data, context={"request": request_with_user})

        assert serializer.is_valid(), serializer.errors

        task = serializer.save()

        assert task.user == user
        assert task.name == data["name"]

    @pytest.mark.parametrize(
        "repeat_type, interval, days_of_week, days_of_month, expected_error",
        [
            ("daily", None, None, None, "Interval not provided"),
            ("weekly", None, None, None, "Interval or days of week not provided"),
            ("monthly", None, None, None, "Interval or days of month not provided"),
        ],
    )
    def test_recurring_task_serializer_with_invalid_data(
        self, request_with_user, repeat_type, interval, days_of_week, days_of_month, expected_error
    ):
        data = RecurringTaskFactory.build(
            repeat_type=repeat_type,
            interval=interval,
            days_of_week=days_of_week,
            days_of_month=days_of_month,
        ).__dict__
        serializer = RecurringTaskSerializer(data=data, context={"request": request_with_user})

        assert not serializer.is_valid()
        assert "detail" in serializer.errors
        assert serializer.errors["detail"][0] == expected_error
