import pytest
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Task
from .factories import TaskDataForBatchUpdateFactory, TaskFactory


@pytest.mark.django_db
class TestTaskAPI:
    def test_week_task_create_success(self, authenticated_client: APIClient):
        task = TaskFactory.build(task_type="week")
        data = {
            "name": task.name,
            "date": task.date,
            "task_type": task.task_type,
            "order_id": task.order_id,
        }
        response = authenticated_client.post("/task/", data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.count() == 1
        created_task = Task.objects.first()
        assert created_task.name == data["name"]
        assert created_task.task_type == data["task_type"]

    def test_fixed_task_create_success(self, authenticated_client: APIClient):
        task = TaskFactory.build(task_type="fixed")
        data = {
            "name": task.name,
            "date": task.date,
            "task_type": task.task_type,
            "order_id": task.order_id,
            "column_id": task.column_id,
        }
        response = authenticated_client.post("/task/", data=data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.count() == 1
        created_task = Task.objects.first()
        assert created_task.name == data["name"]
        assert created_task.task_type == data["task_type"]

    def test_task_create_error(self, authenticated_client: APIClient):
        data = {"name": "test task", "date": "2024-12-19", "task_type": "fixed", "order_id": 1}
        response = authenticated_client.post("/task/", data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_task_update_success(self, authenticated_client: APIClient):
        task = TaskFactory()
        data = {"name": "new name"}
        response = authenticated_client.patch(f"/task/{task.id}/", data=data)

        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert response.data["success"]
        assert "message" in response.data
        assert "data" in response.data
        assert task.name == response.data["data"]["name"]

    def test_task_update_not_found(self, authenticated_client: APIClient):
        data = {"name": "new name"}
        expected_message = "Task not found"
        response = authenticated_client.patch("/task/1/", data=data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert not response.data["success"]
        assert response.data["message"] == expected_message

    def test_task_delete_success(self, authenticated_client: APIClient):
        task = TaskFactory()
        response = authenticated_client.delete(f"/task/{task.id}/")
        expected = {"detail": "Task archived"}

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data == expected
        task.refresh_from_db()
        assert task.is_deleted

    def test_task_delete_not_found(self, authenticated_client: APIClient):
        expected = {"detail": "Task not found"}
        response = authenticated_client.delete("/task/1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == expected

    def test_task_bulk_update_success(self, authenticated_client: APIClient):
        batch = 3
        data = TaskDataForBatchUpdateFactory.create_batch(batch)
        data = [task.__dict__ for task in data]
        tasks = TaskFactory.create_batch(batch + 1)
        for task_data, task in zip(data, tasks):
            task_data["task_id"] = task.id

        data.append({"task_id": tasks[batch].id})  # test continue if not update_data

        response = authenticated_client.post("/task_bulk_update/", data=data)

        assert response.status_code == status.HTTP_200_OK

        for task in tasks:
            task.refresh_from_db()
        for i in range(batch):
            assert data[i]["task_type"] == tasks[i].task_type
            assert data[i]["order_id"] == tasks[i].order_id
            assert data[i]["date"] == tasks[i].date.strftime("%Y-%m-%d")
            if "column_id" in data[i]:
                assert data[i]["column_id"] == tasks[i].column_id
