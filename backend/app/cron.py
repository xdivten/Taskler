import logging
from datetime import datetime, timedelta

from django.db import transaction

from .models import Task


logger = logging.getLogger("cron")


def get_timezone_to_update():
    utc_hour = datetime.utcnow().hour
    current_timezone = 24 - utc_hour
    return current_timezone if current_timezone != 24 else 0


def move_task_on_next_day():
    logger.info("Cron job started")
    try:
        timezone = get_timezone_to_update()
        user_local_date = (datetime.utcnow() + timedelta(hours=timezone)).date()
        with transaction.atomic():
            Task.objects.select_for_update().filter(
                user__timezone=timezone,
                user__move_uncomplite_task=True,
                date__lt=user_local_date,
                task_type=Task.TaskType.week,
                parent=None,
                done=False,
                is_deleted=False,
            ).update(date=user_local_date)
        logger.info(f"Timezone {timezone} updated to {user_local_date}")
    except Exception as e:
        logger.error(f"Error during cron job: {e}")
