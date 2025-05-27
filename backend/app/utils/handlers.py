from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data["success"] = False
        if isinstance(exc, ValidationError):
            response.data["message"] = "Validation failed"
    if response.data.get("detail"):
        response.data["message"] = response.data["detail"]
        del response.data["detail"]
    return response
