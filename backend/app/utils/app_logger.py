import logging

from systemdlogging.toolbox import SystemdFormatter, SystemdHandler


class CustomSystemdFormatter(SystemdFormatter):
    SEVERITY_MAP = {
        "DEBUG": "debug",
        "INFO": "info",
        "WARNING": "warn",
        "ERROR": "error",
        "CRITICAL": "fatal",
    }

    def format(self, record):
        record.context = getattr(record, "context", {})
        record.context["SEVERITY"] = self.SEVERITY_MAP.get(record.levelname, "unknown")
        return super().format(record)


handler = SystemdHandler()
handler.syslog_id = ""
handler.setFormatter(CustomSystemdFormatter())

app_logger = logging.getLogger("app_logger")
app_logger.addHandler(handler)
