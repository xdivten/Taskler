from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import RecurringTask, Task


class TaskSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    sub_title = serializers.CharField(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"

    def validate(self, data):
        if data.get("task_type") == "fixed" and data.get("column_id") is None:
            raise ValidationError({"detail": "Column_id not provided"})
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation["sub_title"] is None:
            del representation["sub_title"]
        return representation


class CurTaskDatesSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()


class RecurringTaskSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = RecurringTask
        fields = "__all__"

    def validate(self, data):
        if data.get("repeat_type") == RecurringTask.RepeatType.DAILY and data.get("interval") is None:
            raise ValidationError({"repeat_type": "daily", "detail": "Interval not provided"})
        if data.get("repeat_type") == RecurringTask.RepeatType.WEEKLY and (
            data.get("interval") is None or data.get("days_of_week") is None
        ):
            raise ValidationError({"repeat_type": "weekly", "detail": "Interval or days of week not provided"})
        if data.get("repeat_type") == RecurringTask.RepeatType.MONTHLY and (
            data.get("interval") is None or data.get("days_of_month") is None
        ):
            raise ValidationError({"repeat_type": "monthly", "detail": "Interval or days of month not provided"})
        return data


class RecurringTaskActionSerializer(serializers.Serializer):

    strategy = serializers.ChoiceField(choices=["single", "all"])
    name = serializers.CharField(max_length=200, required=False)
    color = serializers.CharField(
        required=False,
        max_length=7,
        validators=[
            RegexValidator(
                regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Wrong color hex code",
            )
        ],
    )
    time = serializers.TimeField(required=False)

    def validate(self, data):
        if self.context["request"].method == "PATCH":
            if not data.get("name") and not data.get("color"):
                raise ValidationError("Name or color must be provided.")
        return data
