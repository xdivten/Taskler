from django.contrib import admin

from .models import RecurringTask, Subscriptions, Task, User


admin.site.register([Task, User, Subscriptions, RecurringTask])
