import calendar
import random
from datetime import date, datetime, timedelta

import pytz
from factory import Factory, Faker, LazyFunction, Sequence, SubFactory, lazy_attribute
from factory.django import DjangoModelFactory, Password

from ..models import RecurringTask, Subscriptions, Task, User


class SubscriptionsFactory(DjangoModelFactory):

    class Meta:
        model = Subscriptions

    paid_date = LazyFunction(lambda: datetime.now(tz=pytz.UTC) - timedelta(days=random.randint(0, 30)))
    subscription_type = LazyFunction(lambda: random.choice(Subscriptions.SubscriptionType.values))


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    username = Faker("user_name")
    email = Faker("email")
    password = Password("password")
    timezone = Faker("random_int", min=0, max=23)
    move_uncomplite_task = Faker("boolean")
    subscription = SubFactory(SubscriptionsFactory)


class RecurringTaskFactory(DjangoModelFactory):

    class Meta:
        model = RecurringTask

    user = SubFactory(UserFactory)
    name = Faker("sentence", nb_words=3)
    repeat_type = LazyFunction(lambda: random.choice(RecurringTask.RepeatType.values))
    start_date = LazyFunction(lambda: date.today() - timedelta(days=date.today().weekday()))
    interval = LazyFunction(lambda: 1 if random.random() < 0.9 else random.randint(2, 5))

    @lazy_attribute
    def end_date(self):
        if random.random() < 0.7:
            return None
        return self.start_date + timedelta(days=random.randint(10, 30))

    @lazy_attribute
    def days_of_week(self):
        if self.repeat_type != RecurringTask.RepeatType.WEEKLY:
            return None
        if random.random() < 0.8:
            return [self.start_date.weekday()]
        return sorted(random.sample(range(7), random.randint(1, 7)))

    @lazy_attribute
    def days_of_month(self):
        if self.repeat_type != RecurringTask.RepeatType.MONTHLY:
            return None
        if random.random() < 0.9:
            return [self.start_date]
        days_in_month = calendar.monthrange(self.start_date.year, self.start_date.month)[1]
        random_days = random.sample(range(1, days_in_month + 1), random.randint(1, 3))
        return sorted([date(self.start_date.year, self.start_date.month, day) for day in random_days])


class TaskFactory(DjangoModelFactory):

    class Meta:
        model = Task

    user = SubFactory(UserFactory)
    date = LazyFunction(lambda: date.today())
    name = Faker("sentence", nb_words=3)
    description = Faker("sentence", nb_words=3)
    color = Faker("color")
    order_id = Sequence(int)
    task_type = LazyFunction(lambda: random.choice(Task.TaskType.values))
    is_deleted = False
    parent = None

    @lazy_attribute
    def column_id(self):
        if self.task_type == Task.TaskType.fixed:
            return random.randint(1, 5)
        return None


class CurTaskDates:

    def __init__(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date


class CurTaskDatesFactory(Factory):

    class Meta:
        model = CurTaskDates

    from_date = LazyFunction(lambda: date.today())

    @lazy_attribute
    def to_date(self):
        return self.from_date + timedelta(days=7)


class TaskDataForBatch:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, (date, datetime)):
                value = value.strftime("%Y-%m-%d")
            if value is not None:
                setattr(self, key, value)


class TaskDataForBatchUpdateFactory(Factory):

    class Meta:
        model = TaskDataForBatch

    date = Faker("date_this_month")
    task_type = LazyFunction(lambda: random.choice(Task.TaskType.values))
    order_id = LazyFunction(lambda: random.randint(1, 10))

    @lazy_attribute
    def column_id(self):
        if self.task_type == Task.TaskType.week:
            return None
        return random.randint(1, 3)
