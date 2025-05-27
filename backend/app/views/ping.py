import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


logger = logging.getLogger(__name__)
app_logger = logging.getLogger("app_logger")


@api_view(["GET"])
def ping(request):
    app_logger.info(f"ping from {request.user}")
    return Response({"ping": "pong"}, status=status.HTTP_200_OK)
