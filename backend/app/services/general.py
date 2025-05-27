import functools
import logging

from django.db import DatabaseError
from rest_framework.exceptions import ValidationError

from ..utils.exceptions import UnexpectedError


app_logger = logging.getLogger("app_logger")


def log_and_handle_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            request = next((arg for arg in args if hasattr(arg, "user")), None)
            if not request and "request" in kwargs:
                request = kwargs["request"]

            # Получение информации о пользователе
            if request and hasattr(request, "user"):
                user = request.user
                user_info = {
                    "user_id": user.id if user.is_authenticated else None,
                    "username": user.username if user.is_authenticated else None,
                    "user_is_authenticated": user.is_authenticated,
                }
            return func(*args, **kwargs)
        except ValidationError as e:
            app_logger.warning(
                "Validation failed",
                extra={"function": func.__name__, "error_type": "ValidationError", "details": e.detail, **user_info},
            )
            raise
        except DatabaseError as e:
            app_logger.error(
                "Database error occurred",
                extra={"function": func.__name__, "error_type": "DatabaseError", "error_message": str(e), **user_info},
                exc_info=True,
            )
            raise UnexpectedError()
        except Exception as e:
            app_logger.error(
                "Unexpected error occurred",
                extra={
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    **user_info,
                },
                exc_info=True,
            )
            raise UnexpectedError()

    return wrapper


def is_valid_serializer(serializer):
    if not serializer.is_valid():
        raise ValidationError({"errors": serializer.errors})
