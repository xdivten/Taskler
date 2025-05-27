import datetime
import logging

from dateutil.relativedelta import relativedelta
from django.db.models import Q, QuerySet

from ..models import RecurringTask, Task, User
from .general import log_and_handle_errors


app_logger = logging.getLogger("app_logger")


class TaskListGenerator:
    def __init__(self, user: User, from_date: datetime.date, to_date: datetime.date):
        self.user = user
        self.from_date = from_date
        self.to_date = to_date
        self._existing_tasks()
        self._recurring_tasks()
        app_logger.info(f"The task list generator in range {from_date}, {to_date} for the user {user} initialized")

    def _existing_tasks(self):
        tasks = self._fetch_existing_tasks_in_range()
        app_logger.info(f"Fetched {len(tasks)} tasks")
        self.existing_tasks = tasks

    def _recurring_tasks(self):
        recurring_tasks = self._fetch_recurring_tasks()
        app_logger.info(f"Fetched {len(recurring_tasks)} recurring tasks")
        self.recurring_tasks = recurring_tasks

    def generate(self):
        created_tasks = []

        for recurring_task in self.recurring_tasks:
            if self._should_skip_recurring_task(recurring_task):
                continue

            created_tasks.extend(self._process_recurring_task(recurring_task))

            app_logger.info(f"Generated {len(created_tasks)} tasks from parent {recurring_task.id}")
        return self._combine_results(created_tasks), self.recurring_tasks

    def _combine_results(self, created_tasks):
        non_deleted_tasks = [task for task in self.existing_tasks if not task.is_deleted]
        return non_deleted_tasks + created_tasks

    def _should_skip_recurring_task(self, recurring_task):
        existing_dates = {task.date for task in self.existing_tasks if task.parent_id == recurring_task.id}
        return bool(existing_dates)

    def _process_recurring_task(self, recurring_task):
        new_tasks = []
        for day_offset in self._date_range_offsets():
            current_date = self.from_date + datetime.timedelta(days=day_offset)

            if self._is_date_valid_for_recurring(recurring_task, current_date):
                new_task = self._create_task(recurring_task, current_date)
                new_tasks.append(new_task)
        return new_tasks

    def _date_range_offsets(self):
        return range((self.to_date - self.from_date).days + 1)

    def _is_date_valid_for_recurring(self, recurring_task, current_date):
        if not self._is_date_in_recurrence_range(recurring_task, current_date):
            return False
        date_validators = {
            RecurringTask.RepeatType.DAILY: self._validate_daily,
            RecurringTask.RepeatType.WEEKDAYS: self._validate_weekdays,
            RecurringTask.RepeatType.WEEKENDS: self._validate_weekends,
            RecurringTask.RepeatType.WEEKLY: self._validate_weekly,
            RecurringTask.RepeatType.MONTHLY: self._validate_monthly,
        }
        validator = date_validators.get(recurring_task.repeat_type)
        return validator(recurring_task, current_date) if validator else False

    def _is_date_in_recurrence_range(self, recurring_task, current_date):
        return current_date >= recurring_task.start_date and (
            not recurring_task.end_date or current_date <= recurring_task.end_date
        )

    def _validate_daily(self, recurring_task, current_date):
        days_difference = (current_date - recurring_task.start_date).days
        return days_difference % recurring_task.interval == 0

    def _validate_weekdays(self, _, current_date):
        return current_date.weekday() < 5

    def _validate_weekends(self, _, current_date):
        return current_date.weekday() >= 5

    def _validate_weekly(self, recurring_task, current_date):
        start_monday = recurring_task.start_date - datetime.timedelta(days=recurring_task.start_date.weekday())
        weeks_difference = (current_date - start_monday).days // 7
        return (
            current_date.weekday() in recurring_task.days_of_week and weeks_difference % recurring_task.interval == 0
        )

    def _validate_monthly(self, recurring_task, current_date):
        month_difference = relativedelta(current_date, recurring_task.start_date)
        total_months = month_difference.years * 12 + month_difference.months
        only_date_day_of_month = [date.day for date in recurring_task.days_of_month]
        return current_date.day in only_date_day_of_month and total_months % recurring_task.interval == 0

    def _create_task(self, recurring_task: RecurringTask, current_date: datetime.date) -> Task:
        order_id = self._calculate_order_id_for_task(current_date)
        new_task = Task(
            user=self.user,
            date=current_date,
            name=recurring_task.name,
            order_id=order_id,
            task_type=Task.TaskType.week,
            color=recurring_task.color,
            parent=recurring_task,
            time=recurring_task.time,
        )
        new_task.save()
        return new_task

    def _fetch_existing_tasks_in_range(self) -> QuerySet[Task]:
        app_logger.info("Fetching tasks for generator")
        return Task.objects.filter(
            Q(
                user=self.user,
                date__range=[self.from_date, self.to_date],
                task_type=Task.TaskType.week,
            )
            | Q(
                user=self.user,
                task_type=Task.TaskType.fixed,
                is_deleted=False,
            )
        )

    def _fetch_recurring_tasks(self) -> QuerySet[RecurringTask]:
        app_logger.info("Fetching recurring tasks for generator")
        return RecurringTask.objects.filter(user=self.user, is_deleted=False, start_date__lte=self.to_date).filter(
            Q(end_date__gte=self.from_date) | Q(end_date__isnull=True)
        )

    def _calculate_order_id_for_task(self, date: datetime.date) -> int:
        order_ids = [task.order_id for task in self.existing_tasks if task.date == date]
        return (max(order_ids, default=0)) + 1
