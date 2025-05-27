from typing import NoReturn

import pytest
from django.core.handlers.wsgi import WSGIRequest

from ..serializers import TaskSerializer
from .factories import TaskFactory


@pytest.mark.django_db
class TestTaskSerializer:

    def test_task_serializer(self, user: NoReturn):
        task = TaskFactory(user=user)
        serializer = TaskSerializer(task)
        data = serializer.data

        assert task.user == user
        assert str(task.date) == data["date"]
        assert task.name == data["name"]
        assert task.description == data["description"]
        assert task.color == data["color"]
        assert task.subtask == data["subtask"]
        assert task.done == data["done"]
        assert task.order_id == data["order_id"]
        assert task.task_type == data["task_type"]
        assert task.column_id == data["column_id"]
        assert task.parent == data["parent"]
        assert task.is_deleted == data["is_deleted"]

    def test_task_serializer_deserialization(self, request_with_user: WSGIRequest):
        data = TaskFactory.build().__dict__
        serializer = TaskSerializer(data=data, context={"request": request_with_user})

        assert serializer.is_valid()

        task = serializer.save()

        assert task.user == request_with_user.user
        assert task.name == data["name"]

    def test_task_serializer_with_invalid_column_id(self, request_with_user: WSGIRequest):
        data = TaskFactory.build(task_type="fixed", column_id=None).__dict__
        serializer = TaskSerializer(data=data, context={"request": request_with_user})

        assert not serializer.is_valid()
        assert "detail" in serializer.errors
        assert serializer.errors["detail"][0] == "Column_id not provided"
