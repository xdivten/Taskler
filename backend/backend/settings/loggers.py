import logging
import os
from pathlib import Path

from decouple import config
from systemdlogging.toolbox import SystemdFormatter


BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_LOG_FILENAME = os.path.join(BASE_DIR, "log", "app.log")
ERROR_LOG_FILENAME = os.path.join(BASE_DIR, "log", "error.log")
DB_LOG_FILENAME = os.path.join(BASE_DIR, "log", "db.log")
SECURITY_LOG_FILENAME = os.path.join(BASE_DIR, "log", "security.log")


class ExcludeDRFFromDBLogFilter(logging.Filter):
    def filter(self, record):
        if record.name == "django.db.backends":
            if "drf_api_logs" in record.getMessage():
                return False
        return True


SERVER = config("SERVER", cast=bool)

if SERVER:

    class CustomSystemdFormatter(SystemdFormatter):
        SEVERITY_MAP = {
            "DEBUG": "debug",
            "INFO": "info",
            "WARNING": "warn",
            "ERROR": "error",
            "CRITICAL": "fatal",
        }

        def format(self, record: logging.LogRecord):
            record.context = getattr(record, "context", {})
            context_ = getattr(record, "context", {})

            context_["SEVERITY"] = self.SEVERITY_MAP.get(record.levelname, "unknown")

            if hasattr(record, "user_info"):
                for key, value in record.user_info.items():
                    context_[key] = str(value)

            record.context.update(context_)
            return super().format(record)

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "systemd": {
                "()": CustomSystemdFormatter,
            },
            "verbose": {
                "format": "{levelname} {asctime} {name} {process:d} {thread:d} {message}",
                "style": "{",
            },
        },
        "filters": {
            "exclude_drf_from_db_log": {
                "()": ExcludeDRFFromDBLogFilter,
            },
        },
        "handlers": {
            "error_file": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "formatter": "verbose",
                "filename": ERROR_LOG_FILENAME,
            },
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "verbose",
                "filename": APP_LOG_FILENAME,
            },
            "security_file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "formatter": "verbose",
                "filename": SECURITY_LOG_FILENAME,
            },
            "systemd": {"level": "INFO", "class": "systemdlogging.toolbox.SystemdHandler", "formatter": "systemd"},
        },
        "loggers": {
            "django": {
                "handlers": ["file", "systemd"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": ["systemd"],
                "level": "INFO",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["systemd"],
                "level": "INFO",
                "propagate": False,
            },
            "cron": {
                "handlers": ["file", "systemd"],
                "level": "INFO",
                "propagate": False,
            },
            "app_logger": {
                "handlers": ["file", "systemd"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }

else:

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {name} {process:d} {thread:d} {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname} {name} {message}",
                "style": "{",
            },
        },
        "filters": {
            "exclude_drf_from_db_log": {
                "()": ExcludeDRFFromDBLogFilter,  # Добавляем фильтр
            },
        },
        "handlers": {
            "error_file": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "formatter": "verbose",
                "filename": ERROR_LOG_FILENAME,
            },
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "verbose",
                "filename": APP_LOG_FILENAME,
            },
            "db_file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "formatter": "simple",
                "filename": DB_LOG_FILENAME,
                "filters": ["exclude_drf_from_db_log"],
            },
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "security_file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "formatter": "verbose",
                "filename": SECURITY_LOG_FILENAME,
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": ["console", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["db_file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["console", "security_file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "cron": {
                "handlers": ["file"],
                "level": "INFO",
                "propagate": False,
            },
            "app_logger": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }


DRF_API_LOGGER_DATABASE = True

SPECTACULAR_SETTINGS = {
    "TITLE": "Backend Swagger",
    "DESCRIPTION": "Backend API description",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
