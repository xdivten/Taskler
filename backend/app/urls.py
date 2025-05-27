from django.urls import include, path

from .views.auth import get_csrf
from .views.ping import ping
from .views.tasks import CurrTaskAPI, RecurringTaskCreateAPI, TaskBulkUpdateAPI, TaskCreateAPI, TaskUpdateDeleteAPI


# ping_views
urlpatterns = [
    path("ping/", ping, name="ping"),
]


# task_views
urlpatterns += [
    path(
        "task/<int:pk>/",
        TaskUpdateDeleteAPI.as_view(),
        name="delete_or_update_task",
    ),
    path("task/", TaskCreateAPI.as_view(), name="create_task"),
    path("tasks/", CurrTaskAPI.as_view(), name="get_current_task"),
    path(
        "task_bulk_update/",
        TaskBulkUpdateAPI.as_view(),
        name="bulk_update_task",
    ),
    path("repeat_task/<int:pk>/", RecurringTaskCreateAPI.as_view(), name="create_repeat_task"),
    path("repeat_task/", RecurringTaskCreateAPI.as_view(), name="create_repeat_task"),
]

urlpatterns += [
    path("csrf/", get_csrf, name="csrf"),
    path("_allauth/", include("allauth.headless.urls")),
]
