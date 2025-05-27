import logging

from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view


logger = logging.getLogger(__name__)


@api_view(["GET"])
def get_csrf(request):

    csrf_token = get_token(request)
    response = JsonResponse({"message": "CSRF token set successfully"})
    response.set_cookie(
        "csrftoken",
        csrf_token,
        max_age=3600,
        httponly=False,
        secure=False,
        samesite="Strict",
    )
    return response


def email_confirm_redirect(request, key):
    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")


def password_reset_confirm_redirect(request, uidb64, token):
    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )
