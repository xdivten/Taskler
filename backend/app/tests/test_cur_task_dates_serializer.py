import pytest

from ..serializers import CurTaskDatesSerializer
from .factories import CurTaskDatesFactory


@pytest.mark.django_db
class TestCurTaskDatesSerializer:

    def test_cur_dates_serializer(self):
        data = CurTaskDatesFactory().__dict__
        serializer = CurTaskDatesSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data == data

    def test_cur_dates_serializer_with_invalid_data(self):
        data = CurTaskDatesFactory(to_date=None).__dict__
        serializer = CurTaskDatesSerializer(data=data)

        assert not serializer.is_valid()
        assert "to_date" in serializer.errors

    def test_cur_dates_serializer_with_invalid_date_format(self):
        data = CurTaskDatesFactory(to_date="2024/12/31").__dict__
        serializer = CurTaskDatesSerializer(data=data)

        assert not serializer.is_valid()
        assert "to_date" in serializer.errors
