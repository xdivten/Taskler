from rest_framework import status
from rest_framework.test import APIClient


def test_get_csrf(authenticated_client: APIClient):
    response = authenticated_client.get("/csrf/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "CSRF token set successfully"}

    csrf_token = response.cookies.get("csrftoken")
    assert csrf_token is not None
