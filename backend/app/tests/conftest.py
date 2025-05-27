from datetime import date, timedelta

import pytest
from allauth.account.models import EmailAddress
from rest_framework.test import APIClient, APIRequestFactory

from .factories import UserFactory


@pytest.fixture(scope="session", autouse=True)
def drf_api_logger_settings():
    from django.conf import settings

    settings.DRF_API_LOGGER_DATABASE = False


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def authenticated_client(db, user):
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def request_with_user(user):
    api_factory = APIRequestFactory()
    request = api_factory.get("/")
    request.user = user
    return request


@pytest.fixture
def date_range_for_week(request):
    multiplier = getattr(request, "param", 0)
    cur_date = date.today()
    from_date = date.today() + timedelta(days=7 * multiplier - cur_date.weekday())
    to_date = from_date + timedelta(days=6)
    return from_date, to_date
