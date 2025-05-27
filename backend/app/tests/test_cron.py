from datetime import timedelta

import pytest
from django.utils.timezone import now

from ..cron import get_timezone_to_update, move_task_on_next_day
from .factories import TaskFactory, UserFactory


@pytest.mark.django_db
class TestCron:

    # @pytest.mark.parametrize("tm_hour, expected", [(6, 18), (0, 0), (24, 0)])
    # def test_get_timezone_to_update(self, mocker, tm_hour, expected):
    #     mocker.patch(
    #         "app.cron.datetime.now", return_value=type("MockTime", (object,), {"hour": tm_hour})
    #     )
    #     assert get_timezone_to_update() == expected

    def test_move_task_on_next_day(self, mocker):
        timezone_to_update = 3
        mocker.patch("app.cron.get_timezone_to_update", return_value=timezone_to_update)
        user = UserFactory(
            timezone=timezone_to_update,
            move_uncomplite_task=True,
        )
        task = TaskFactory(user=user, date=now().date() - timedelta(days=2), task_type="week", parent=None)
        move_task_on_next_day()
        task.refresh_from_db()

        assert task.date == now().date()
