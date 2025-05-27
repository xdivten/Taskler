from rest_framework import status
from rest_framework.exceptions import APIException


class UnexpectedError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected error occurred. Please try again later."
    default_code = "unexpected_error"
