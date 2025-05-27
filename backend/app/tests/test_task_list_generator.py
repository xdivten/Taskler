import datetime

import pytest

from ..models import RecurringTask, Task
from ..services.task_list_generator import TaskListGenerator
from .factories import RecurringTaskFactory, TaskFactory


_date = lambda month, day: datetime.date(2025, month, day)


@pytest.mark.django_db
class TestTaskListGenerator:

    def test_task_list_generator_initialization(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        assert generator.user == user
        assert generator.from_date == from_date
        assert generator.to_date == to_date
        assert len(generator.existing_tasks) == 0
        assert len(generator.recurring_tasks) == 0

    def test_should_skip_recurring_task_when_existing_dates(self, user, date_range_for_week, mocker):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)
        recurring_task = mocker.Mock()
        recurring_task.id = 1

        existing_task = mocker.Mock()
        existing_task.date = mocker.Mock()
        existing_task.parent_id = 1
        generator.existing_tasks = [existing_task]

        assert generator._should_skip_recurring_task(recurring_task)

    def test_should_skip_recurring_task_when_no_existing_dates(self, user, date_range_for_week, mocker):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)
        recurring_task = mocker.Mock()
        recurring_task.id = 1
        generator.existing_tasks = []

        assert not generator._should_skip_recurring_task(recurring_task)

    def test_date_range_offsets_full_week(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        offsets = generator._date_range_offsets()

        assert list(offsets) == [0, 1, 2, 3, 4, 5, 6]

    def test_is_date_in_recurrence_range_true(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        recurring_task = RecurringTaskFactory(
            user=user, start_date=from_date, end_date=to_date, repeat_type=RecurringTask.RepeatType.DAILY, interval=1
        )
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)
        current_date = from_date

        assert generator._is_date_in_recurrence_range(recurring_task, current_date)

        current_date = to_date

        assert generator._is_date_in_recurrence_range(recurring_task, current_date)

    def test_is_date_in_recurrence_range_false(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        recurring_task = RecurringTaskFactory(
            user=user, start_date=from_date, end_date=to_date, repeat_type=RecurringTask.RepeatType.DAILY, interval=1
        )
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)
        current_date = from_date - datetime.timedelta(days=1)

        assert not generator._is_date_in_recurrence_range(recurring_task, current_date)

        current_date = to_date + datetime.timedelta(days=1)

        assert not generator._is_date_in_recurrence_range(recurring_task, current_date)

    def test_validate_daily_with_interval_of_one_day(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)
        recurring_task = RecurringTaskFactory(
            user=user, start_date=from_date, repeat_type=RecurringTask.RepeatType.DAILY, interval=1
        )

        for i in range(7):
            current_date = from_date + datetime.timedelta(days=i)
            assert generator._validate_daily(recurring_task, current_date)

    @pytest.mark.parametrize("interval", [2, 3, 4, 5, 6, 10, 15, 20])
    def test_validate_daily_with_interval_of_not_one_day(self, user, date_range_for_week, interval):
        from_date, to_date = date_range_for_week
        recurring_task = RecurringTaskFactory(
            user=user,
            start_date=from_date,
            end_date=None,
            repeat_type=RecurringTask.RepeatType.DAILY,
            interval=interval,
        )
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        assert generator._validate_daily(recurring_task, from_date)

        for i in range(1, interval * 2 + 1):
            current_date = from_date + datetime.timedelta(days=i)
            if i % interval == 0:
                assert generator._validate_daily(recurring_task, current_date)
            else:
                assert not generator._validate_daily(recurring_task, current_date)

    @pytest.mark.parametrize("days_delta", range(7))
    def test_validate_weekdays(self, user, date_range_for_week, days_delta):
        from_date, to_date = date_range_for_week
        recurring_task = RecurringTaskFactory(
            user=user,
            start_date=from_date,
            repeat_type=RecurringTask.RepeatType.WEEKDAYS,
        )
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        current_date = from_date + datetime.timedelta(days=days_delta)
        if days_delta < 5:
            assert generator._validate_weekdays(recurring_task, current_date)
        else:
            assert not generator._validate_weekdays(recurring_task, current_date)

    @pytest.mark.parametrize("days_delta", range(7))
    def test_validate_weekends(self, user, date_range_for_week, days_delta):
        from_date, to_date = date_range_for_week
        recurring_task = RecurringTaskFactory(
            user=user,
            start_date=from_date,
            repeat_type=RecurringTask.RepeatType.WEEKENDS,
        )
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        current_date = from_date + datetime.timedelta(days=days_delta)
        if days_delta >= 5:
            assert generator._validate_weekends(recurring_task, current_date)
        else:
            assert not generator._validate_weekends(recurring_task, current_date)

    @pytest.mark.parametrize(
        "start_date, current_date, interval, days_of_week, expected_result",
        # fmt: off
        [
            (_date(2, 3), _date(2, 3), 1, [0], True),  # Monday, same week
            (_date(2, 3), _date(2, 5), 1, [0], False),  # Monday, not in days_of_week
            (_date(2, 3), _date(2, 10), 1, [0], True),  # Monday, next week
            (_date(2, 3), _date(2, 10), 2, [0], False),  # Monday, not in interval
            (_date(2, 3), _date(2, 17), 2, [0], True),  # Monday, two weeks later in interval
            (_date(2, 3), _date(2, 24), 3, [0], True),  # Monday, three weeks later in inteval
            (_date(2, 3), _date(2, 24), 4, [0], False),  # Monday, four weeks later (not matching interval)
            (_date(2, 3), _date(2, 8), 1, [5], True),  # Saturday, same week
            (_date(2, 3), _date(2, 9), 1, [6], True),  # Sunday, same week
        ],
        # fmt: on
    )
    def test_validate_weekly(self, user, start_date, current_date, interval, days_of_week, expected_result):
        recurring_task = RecurringTaskFactory(
            user=user,
            repeat_type=RecurringTask.RepeatType.WEEKLY,
            start_date=start_date,
            end_date=None,
            interval=interval,
            days_of_week=days_of_week,
        )
        generator = TaskListGenerator(user=user, from_date=start_date, to_date=start_date + datetime.timedelta(days=7))

        assert generator._validate_weekly(recurring_task, current_date) == expected_result

    @pytest.mark.parametrize(
        "start_date, interval, days_of_month, current_date, expected_result",
        # fmt: off
        [
            (_date(1, 1), 1, [_date(1, 15)], _date(1, 15), True),
            (_date(1, 1), 1, [_date(1, 15)], _date(2, 15), True),
            (_date(1, 1), 2, [_date(1, 15)], _date(3, 15), True),
            (_date(1, 1), 2, [_date(1, 15)], _date(2, 15), False),
            (_date(1, 1), 1, [_date(1, 15)], _date(1, 16), False),
            (_date(1, 1), 1, [_date(1, 31), _date(1, 15)], _date(1, 31), True),
            (_date(1, 1), 1, [_date(1, 31), _date(1, 28)], _date(2, 28), True),
            (_date(1, 1), 3, [_date(1, 30)], _date(3, 30), False),
            (_date(1, 1), 3, [_date(1, 30)], _date(4, 30), True),
        ],
        # fmt: on
    )
    def test_validate_monthly(self, user, start_date, current_date, interval, days_of_month, expected_result):
        recurring_task = RecurringTaskFactory(
            user=user,
            repeat_type=RecurringTask.RepeatType.MONTHLY,
            start_date=start_date,
            end_date=None,
            interval=interval,
            days_of_month=days_of_month,
        )
        generator = TaskListGenerator(user=user, from_date=start_date, to_date=start_date + datetime.timedelta(days=7))

        assert generator._validate_monthly(recurring_task, current_date) == expected_result

    def test_create_task_with_valid_input(self, user, date_range_for_week, mocker):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)
        recurring_task = RecurringTaskFactory(
            user=user,
            name="Test Task",
            color="#FF0000",
            time=datetime.time(9, 0),
        )

        current_date = from_date + datetime.timedelta(days=1)
        mocker.patch.object(generator, "_calculate_order_id_for_task", return_value=1)

        new_task = generator._create_task(recurring_task, current_date)

        assert new_task.user == user
        assert new_task.date == current_date
        assert new_task.name == "Test Task"
        assert new_task.order_id == 1
        assert new_task.task_type == Task.TaskType.week
        assert new_task.color == "#FF0000"
        assert new_task.parent == recurring_task
        assert new_task.time == datetime.time(9, 0)

    def test_calculate_order_id_for_task_no_existing_tasks(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        result = generator._calculate_order_id_for_task(from_date)

        assert result == 1

    def test_calculate_order_id_for_task_with_existing_tasks(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        for order_id in [1, 2, 3]:
            TaskFactory(user=user, date=from_date, order_id=order_id)
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        result = generator._calculate_order_id_for_task(from_date)

        assert result == 4

    def test_calculate_order_id_for_task_with_same_order_ids(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        TaskFactory.create_batch(3, user=user, date=from_date, order_id=1)
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        result = generator._calculate_order_id_for_task(from_date)

        assert result == 2

    def test_is_date_valid_for_recurring_with_invalid_date(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        recurring_task = RecurringTaskFactory(
            user=user,
            start_date=from_date,
            end_date=None,
            repeat_type=RecurringTask.RepeatType.DAILY,
        )
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        invalid_date = from_date - datetime.timedelta(days=5)

        assert not generator._is_date_valid_for_recurring(recurring_task, invalid_date)

    @pytest.mark.parametrize(
        "repeat_type, interval, days_of_week, days_of_month, current_date, expected_result",
        [
            (RecurringTask.RepeatType.DAILY, 1, None, None, _date(1, 1), True),
            (RecurringTask.RepeatType.DAILY, 2, None, None, _date(1, 2), False),
            (RecurringTask.RepeatType.WEEKDAYS, 1, None, None, _date(1, 2), True),
            (RecurringTask.RepeatType.WEEKDAYS, 1, None, None, _date(1, 4), False),
            (RecurringTask.RepeatType.WEEKENDS, 1, None, None, _date(1, 4), True),
            (RecurringTask.RepeatType.WEEKENDS, 1, None, None, _date(1, 2), False),
            (RecurringTask.RepeatType.WEEKLY, 1, [2], None, _date(1, 8), True),
            (RecurringTask.RepeatType.MONTHLY, 1, None, [_date(1, 1)], _date(2, 1), True),
        ],
    )
    def test_is_date_valid_for_recurring_with_valid_dates(
        self,
        user,
        date_range_for_week,
        repeat_type,
        interval,
        days_of_week,
        days_of_month,
        current_date,
        expected_result,
    ):
        from_date, to_date = date_range_for_week
        recurring_task = RecurringTaskFactory(
            user=user,
            start_date=_date(1, 1),
            end_date=None,
            interval=interval,
            repeat_type=repeat_type,
            days_of_week=days_of_week,
            days_of_month=days_of_month,
        )
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        result = generator._is_date_valid_for_recurring(recurring_task, current_date)

        assert result == expected_result

    def test_process_recurring_task_with_empty_list(self, user, date_range_for_week, mocker):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        mocker.patch.object(generator, "_date_range_offsets", return_value=[0, 1, 2])
        mocker.patch.object(generator, "_is_date_valid_for_recurring", return_value=False)
        mocker.patch.object(generator, "_create_task")

        recurring_task = RecurringTaskFactory(user=user)
        result = generator._process_recurring_task(recurring_task)

        assert len(result) == 0
        assert generator._create_task.call_count == 0

    def test_process_recurring_task_with_recurring_tasks(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        recurring_task1 = RecurringTaskFactory(user=user, start_date=from_date)
        recurring_task2 = RecurringTaskFactory(user=user, start_date=from_date + datetime.timedelta(days=2))
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        result1 = generator._process_recurring_task(recurring_task1)
        result2 = generator._process_recurring_task(recurring_task2)

        assert len(result1) >= 1
        assert len(result2) >= 1
        assert Task.objects.filter(parent=recurring_task1).count() >= 1
        assert Task.objects.filter(parent=recurring_task2).count() >= 1

    def test_combine_results_with_empty_lists(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)
        created_tasks = []

        result = generator._combine_results(created_tasks)

        assert result == []

    def test_combine_results_with_all_existing_tasks_deleted(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        deleted_tasks = TaskFactory.create_batch(3, user=user, date=from_date, is_deleted=True)
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        created_tasks = TaskFactory.create_batch(2, user=user, date=from_date)

        result = generator._combine_results(created_tasks)

        assert len(result) == 2
        assert all(task in created_tasks for task in result)
        assert all(task not in deleted_tasks for task in result)

    def test_generate_with_empty_recurring_tasks(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        result, recurring_tasks = generator.generate()

        assert len(result) == 0
        assert len(recurring_tasks) == 0

    def test_generate_with_recurring_tasks(self, user, date_range_for_week):
        from_date, to_date = date_range_for_week
        RecurringTaskFactory(user=user, start_date=from_date, interval=1, repeat_type=RecurringTask.RepeatType.DAILY)
        generator = TaskListGenerator(user=user, from_date=from_date, to_date=to_date)

        result, recurring_tasks = generator.generate()

        assert len(result) == 7
        assert len(recurring_tasks) == 1
