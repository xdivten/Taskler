import logging
from typing import Literal

from django.db import connection, transaction

from ..models import Task
from ..serializers import RecurringTaskActionSerializer, RecurringTaskSerializer, TaskSerializer
from ..utils.types import RecurringTaskInfo
from .general import is_valid_serializer, log_and_handle_errors


app_logger = logging.getLogger("app_logger")


@log_and_handle_errors
def create_recurring_task(request, pk):
    context = {"request": request}
    serializer = RecurringTaskSerializer(data=request.data, context=context)
    is_valid_serializer(serializer)
    if pk is None:
        recurring_task = serializer.save()
        app_logger.info(f"Recurring task created successfully: {recurring_task.id}")
        return serializer.data
    with transaction.atomic():
        task = get_task(pk)
        task.is_deleted = True
        task.save()
        recurring_task = serializer.save()
        app_logger.info(f"Recurring task created by {pk=} successfully: {recurring_task.id}")
        return serializer.data


@log_and_handle_errors
def update_recurring_task(request, task) -> RecurringTaskInfo:
    context = {"request": request}
    serializer = RecurringTaskActionSerializer(data=request.data, context=context)
    is_valid_serializer(serializer)
    strategy = serializer.data.get("strategy")
    app_logger.info(f"Recurring task strategy: {strategy}")
    data = serializer.data.copy()
    data["id"] = task.id
    if strategy == "single":
        _update_single_recurring_task(task, request)
        app_logger.info(f"Single recurring task {task.id} updated")
        return RecurringTaskInfo(message="Single repeat task updated", data=data)
    if strategy == "all":
        _update_all_recurring_tasks(serializer.validated_data, task.parent_id)
        app_logger.info(f"All recurring tasks updated for parent ID {task.parent_id}")
        return RecurringTaskInfo(message="All repeat tasks updated", data=data)


def _update_all_recurring_tasks(data, parent_id):
    sql1 = _get_raw_sql_for_update_all_tasks_from_parent(data)
    sql2 = _get_raw_sql_for_update_recurring_task_from_id(data)
    params = _get_params_for_update_tasks(data, parent_id)
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(sql=sql1, params=params)
            cursor.execute(sql=sql2, params=params)


def _update_single_recurring_task(task, request):
    context = {"request": request}
    serializer = TaskSerializer(task, data=request.data, context=context, partial=True)
    is_valid_serializer(serializer)
    serializer.save()


def _generate_update_raw_sql(table_name: Literal["app_task", "app_recurringtask"], data: dict):
    allowed_data = ["name", "color", "time"]
    field_from_table = {"app_task": "parent_id", "app_recurringtask": "id"}
    data_to_update = [f"{item} = %s" for item in allowed_data if item in data]
    sets = ", ".join(data_to_update)
    sql = f"update {table_name} set {sets} where {field_from_table[table_name]}=%s"
    return sql


def _get_params_for_update_tasks(data, parent_id):
    allowed_data = ["name", "color", "time"]
    params = [data[item] for item in allowed_data if item in data]
    params.append(parent_id)
    return params


def _get_raw_sql_for_update_all_tasks_from_parent(data):
    return _generate_update_raw_sql("app_task", data)


def _get_raw_sql_for_update_recurring_task_from_id(data):
    return _generate_update_raw_sql("app_recurringtask", data)


def get_task(pk):
    app_logger.info(f"Fetching task with ID {pk}")
    return Task.objects.get(id=pk)
