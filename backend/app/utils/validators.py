import logging

from rest_framework.exceptions import ValidationError

from ..models import Task


app_logger = logging.getLogger("app_logger")


def validate_task_update(task, update_data):
    if task.parent is None:
        return
    date = update_data.get("date")
    if date is None or len(date) == 0:
        return
    if task.date.strftime("%Y-%m-%d") != date:
        app_logger.warning(f"Validation failed for task with ID {task.id}")
        raise ValidationError(
            {
                "detail": "it is impossible to change the date for repeat task",
                "data": {
                    "id": task.id,
                },
            }
        )
    task_type = update_data.get("task_type")
    if task_type is None:
        return
    if task_type != Task.TaskType.week:
        app_logger.warning(f"Validation failed for task with ID {task.id}")
        raise ValidationError(
            {
                "detail": "it is impossible to change the task type for repeat task",
                "data": {
                    "id": task.id,
                },
            }
        )
