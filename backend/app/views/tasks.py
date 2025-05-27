import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Task
from ..serializers import RecurringTaskActionSerializer, RecurringTaskSerializer, TaskSerializer
from ..services.curr_tasks import get_curr_tasks
from ..services.recurring_tasks import create_recurring_task, update_recurring_task
from ..utils.formatters import get_user_dict
from ..utils.validators import validate_task_update


logger = logging.getLogger(__name__)
app_logger = logging.getLogger("app_logger")


class CurrTaskAPI(APIView):

    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    @method_decorator(never_cache)
    def get(self, request):
        app_logger.info(
            f"Received request to get current tasks for user {request.user}",
            extra={"user_info": get_user_dict(request.user)},
        )
        tasks = get_curr_tasks(request)
        return Response(
            {"success": True, "message": "Tasks received successfully", "tasks": tasks}, status=status.HTTP_200_OK
        )


class TaskCreateAPI(APIView):

    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        app_logger.info(
            f"Received request to create task for user {request.user}",
            extra={"user_info": get_user_dict(request.user)},
        )
        context = {"request": self.request}
        serializer = TaskSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(user=request.user)
        app_logger.info(f"Task created successfully: {task.id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskUpdateDeleteAPI(APIView):

    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get_task(self, pk):
        app_logger.info(f"Fetching task with ID {pk}")
        return Task.objects.get(id=pk)

    def patch(self, request, pk):
        app_logger.info(f"Received request to update task {pk} by user {request.user}")
        try:
            task = self.get_task(pk)
            app_logger.info(f"Task {pk} fetched successfully")
            context = {"request": self.request}
            validate_task_update(task=task, update_data=request.data)

            if task.parent is None:
                serializer = TaskSerializer(task, data=request.data, context=context, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                app_logger.info(f"Task {pk} updated successfully")
                return Response(
                    {"success": True, "message": "Task updated", "data": serializer.data}, status=status.HTTP_200_OK
                )

            recurring_task_info = update_recurring_task(request=request, task=task)
            return Response(
                {"success": True, "message": recurring_task_info.message, "data": recurring_task_info.data},
                status=status.HTTP_200_OK,
            )
        except Task.DoesNotExist:
            app_logger.warning(f"Task {pk} not found")
            return Response({"success": False, "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        app_logger.info(f"Received request to delete task {pk} by user {request.user}")
        try:
            task = self.get_task(pk)
            context = {"request": self.request}
            if task.parent is None:
                task.is_deleted = True
                task.save()
                app_logger.info(f"Task {pk} archived successfully")
                return Response({"detail": "Task archived"}, status=status.HTTP_204_NO_CONTENT)
            serializer = RecurringTaskActionSerializer(data=request.data, context=context)
            serializer.is_valid(raise_exception=True)
            strategy = serializer.data.get("strategy")
            app_logger.info(f"Recurring task delete strategy: {strategy}")
            if strategy == "single":
                task.is_deleted = True
                task.save()
                app_logger.info(f"Single recurring task {pk} archived successfully")
                return Response({"detail": "Single repeat task archived"}, status=status.HTTP_204_NO_CONTENT)
            if strategy == "all":
                with connection.cursor() as cursor:
                    sql1 = "update app_task set is_deleted=%s where parent_id=%s"
                    cursor.execute(sql=sql1, params=[True, task.parent_id])
                    sql2 = "update app_recurringtask set is_deleted=%s where id=%s"
                    cursor.execute(sql=sql2, params=[True, task.parent_id])
                    app_logger.info(f"All recurring tasks archived for parent ID {task.parent_id}")
                    return Response({"detail": "Repeat task archived"}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            app_logger.warning(f"Task {pk} not found")
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


class TaskBulkUpdateAPI(APIView):

    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        app_logger.info(f"Received request to bulk update tasks by user {request.user}")
        tasks_list = request.data
        tasks_dict = {item["task_id"]: item for item in tasks_list}
        for task_data in tasks_dict.values():
            task_data.pop("task_id", None)
        ids = list(tasks_dict.keys())
        tasks = Task.objects.filter(id__in=ids)
        app_logger.info(f"Found {len(tasks)} tasks to update for user {request.user}")

        tasks_to_update = []
        for task in tasks:
            update_data = tasks_dict.get(task.id)
            if not update_data:
                app_logger.warning(f"No update data found for task ID {task.id}. Skipping.")
                continue
            validate_task_update(task=task, update_data=update_data)
            if (
                task.task_type != update_data.get("task_type", task.task_type)
                or task.order_id != update_data.get("order_id", task.order_id)
                or task.date != update_data.get("date", task.date)
                or task.column_id != update_data.get("column_id", task.column_id)
            ):
                task.task_type = update_data.get("task_type", task.task_type)
                task.order_id = update_data.get("order_id", task.order_id)
                task.date = update_data.get("date", task.date)
                task.column_id = update_data.get("column_id", task.column_id)
                tasks_to_update.append(task)

        Task.objects.bulk_update(tasks_to_update, ["task_type", "order_id", "date", "column_id"])
        app_logger.info(f"Successfully updated {len(tasks_to_update)} tasks for user {request.user}")
        return Response({"detail": "Tasks updated"}, status=status.HTTP_200_OK)


class RecurringTaskCreateAPI(APIView):

    serializer_class = RecurringTaskSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None):
        app_logger.info(f"Received request to create recurring task with {pk=} by user {request.user}")

        data = create_recurring_task(request, pk)
        return Response(
            {"success": True, "message": "Recurring task created succesfully", "data": data},
            status=status.HTTP_201_CREATED,
        )
