from django.db.models import QuerySet

from ..models import RecurringTask


class RepeatSubTitlesGenerator:
    default_map = {
        RecurringTask.RepeatType.DAILY: "Daily",
        RecurringTask.RepeatType.WEEKLY: "Weekly on {}",
        RecurringTask.RepeatType.MONTHLY: "Monthly on {}",
        RecurringTask.RepeatType.WEEKDAYS: "On weekdays",
        RecurringTask.RepeatType.WEEKENDS: "On weekends",
    }
    multiple_map = {
        RecurringTask.RepeatType.DAILY: "Every {} days",
        RecurringTask.RepeatType.WEEKLY: "Every {} weeks on {}",
        RecurringTask.RepeatType.MONTHLY: "Every {} months on {}",
    }
    days_of_week = {
        0: "Mo",
        1: "Tu",
        2: "We",
        3: "Th",
        4: "Fr",
        5: "Sa",
        6: "Su",
    }
    days_of_month = {
        1: "st",
        2: "nd",
        3: "rd",
        21: "st",
        22: "nd",
        23: "rd",
        31: "st",
    }

    def __init__(self, recurring_tasks: QuerySet[RecurringTask]):
        self.recurring_tasks = recurring_tasks

    def generate_sub_titles(self):
        sub_titles = {}
        for recurring_task in self.recurring_tasks:
            if self._is_type_weekdays_or_weekends(recurring_task):
                sub_titles[recurring_task.id] = self._sub_title_for_weekdays_or_weekends(recurring_task)
            elif recurring_task.repeat_type == RecurringTask.RepeatType.DAILY:
                sub_titles[recurring_task.id] = self._sub_title_for_daily(recurring_task)
            elif recurring_task.repeat_type == RecurringTask.RepeatType.WEEKLY:
                sub_titles[recurring_task.id] = self._sub_title_for_weekly(recurring_task)
            elif recurring_task.repeat_type == RecurringTask.RepeatType.MONTHLY:
                sub_titles[recurring_task.id] = self._sub_title_for_monthly(recurring_task)
        return sub_titles

    def _is_type_weekdays_or_weekends(self, recurring_task):
        return recurring_task.repeat_type in [
            RecurringTask.RepeatType.WEEKDAYS,
            RecurringTask.RepeatType.WEEKENDS,
        ]

    def _sub_title_for_weekdays_or_weekends(self, recurring_task):
        return self.default_map.get(recurring_task.repeat_type)

    def _sub_title_for_daily(self, recurring_task):
        if recurring_task.interval == 1:
            return self.default_map.get(recurring_task.repeat_type)
        return self.multiple_map.get(recurring_task.repeat_type).format(recurring_task.interval)

    def _sub_title_for_weekly(self, recurring_task):
        days_of_week = ", ".join([self.days_of_week.get(day) for day in recurring_task.days_of_week])
        if recurring_task.interval == 1:
            return self.default_map.get(recurring_task.repeat_type).format(days_of_week)
        return self.multiple_map.get(recurring_task.repeat_type).format(recurring_task.interval, days_of_week)

    def _sub_title_for_monthly(self, recurring_task):
        days_of_month = ", ".join(
            [f"{date.day}{self.days_of_month.get(date.day, 'th')}" for date in recurring_task.days_of_month]
        )
        if recurring_task.interval == 1:
            return self.default_map.get(recurring_task.repeat_type).format(days_of_month)
        return self.multiple_map.get(recurring_task.repeat_type).format(recurring_task.interval, days_of_month)
