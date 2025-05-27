from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecurringTaskInfo:
    message: str
    data: dict
