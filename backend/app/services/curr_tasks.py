import logging

from ..serializers import CurTaskDatesSerializer, TaskSerializer
from .general import is_valid_serializer, log_and_handle_errors
from .repeat_sub_title_generator import RepeatSubTitlesGenerator
from .task_list_generator import TaskListGenerator


app_logger = logging.getLogger("app_logger")


@log_and_handle_errors
def get_curr_tasks(request):
    context = {"request": request}
    serializer = CurTaskDatesSerializer(data=request.GET)
    is_valid_serializer(serializer)
    tasks = _genetate_tasks(request, serializer.validated_data)
    serializer = TaskSerializer(tasks, context=context, many=True)
    return serializer.data


def _genetate_tasks(request, data):
    from_date, to_date = _get_dates(data)
    task_list_generator = TaskListGenerator(request.user, from_date, to_date)
    tasks, repeat_tasks = task_list_generator.generate()
    app_logger.info(f"List of {len(tasks)} tasks successfully generated")
    if not repeat_tasks:
        return tasks
    _merge_sub_titles_in_tasks(tasks, repeat_tasks)
    return tasks


def _merge_sub_titles_in_tasks(tasks, repeat_tasks):
    repeat_sub_titles_generator = RepeatSubTitlesGenerator(repeat_tasks)
    sub_titles = repeat_sub_titles_generator.generate_sub_titles()
    for task in tasks:
        if sub_titles.get(task.parent_id):
            task.sub_title = sub_titles[task.parent_id]


def _get_dates(data):
    from_date = data.get("from_date")
    to_date = data.get("to_date")
    return from_date, to_date
