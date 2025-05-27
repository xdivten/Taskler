from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Subscriptions(models.Model):

    class SubscriptionType(models.TextChoices):
        one_month = "one_month", _("One month")
        three_months = "three_month", _("Three months")
        six_months = "six_month", _("Six months")
        one_year = "one_year", _("One month")

    paid_date = models.DateTimeField(null=False, blank=False)
    subscription_type = models.CharField(null=False, blank=False, choices=SubscriptionType)


class User(AbstractUser):

    first_name = None
    last_name = None
    subscription = models.OneToOneField(Subscriptions, null=True, blank=True, on_delete=models.SET_NULL)
    timezone = models.SmallIntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        default=0,
    )
    move_uncomplite_task = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return f"{self.username}"


class RecurringTask(models.Model):
    class RepeatType(models.TextChoices):
        DAILY = "daily"
        WEEKLY = "weekly"
        MONTHLY = "monthly"
        WEEKDAYS = "weekdays"
        WEEKENDS = "weekends"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=False, blank=False)
    repeat_type = models.CharField(max_length=20, choices=RepeatType.choices)
    color = models.CharField(
        null=False,
        blank=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Wrong color hex code",
            )
        ],
        default="#FFFFFF",
    )
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True, help_text="Дата завершения повторений.")
    interval = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Интервал между повторениями (например, каждые 3 дня).",
    )
    days_of_week = ArrayField(
        models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(6)]),
        null=True,
        blank=True,
        help_text="Дни недели для повторений (0 = Понедельник, 6 = Воскресенье).",
    )
    days_of_month = ArrayField(
        models.DateField(null=False, blank=False),
        null=True,
        blank=True,
        help_text="Числа месяца",
    )
    time = models.TimeField(null=True, blank=True, default=None)
    is_deleted = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return f"{self.user_id} user, {self.name} task"


class Task(models.Model):

    class TaskType(models.TextChoices):
        week = "week"
        fixed = "fixed"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(db_index=True, null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(null=True, blank=True, max_length=200)
    color = models.CharField(
        null=False,
        blank=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Wrong color hex code",
            )
        ],
        default="#FFFFFF",
    )
    subtask = ArrayField(models.CharField(max_length=200), null=True, blank=True)
    done = models.BooleanField(null=False, blank=False, default=False)
    order_id = models.SmallIntegerField(null=False, blank=False)
    task_type = models.CharField(null=False, blank=False, choices=TaskType.choices)
    column_id = models.SmallIntegerField(null=True, blank=True)
    parent = models.ForeignKey(RecurringTask, null=True, blank=True, on_delete=models.CASCADE)
    time = models.TimeField(null=True, blank=True, default=None)
    is_deleted = models.BooleanField(null=False, blank=False, default=False)
    sub_title = None

    def __str__(self):
        return f"{self.user_id} user, {self.name} task"
