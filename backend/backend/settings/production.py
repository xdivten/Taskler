from decouple import config

from .main import LOGGING


CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS").split(",")

CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS").split(",")

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "connect.smtp.bz"
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "tasklerpro@yahoo.com"
EMAIL_HOST_PASSWORD = "u4zwnT37sGVd"

DEFAULT_FROM_EMAIL = "info@taskler.pro"
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

EMAIL_SUBJECT_PREFIX = ["Verify email"]


LOGGING["loggers"].pop("django.db.backends")
LOGGING["handlers"].pop("db_file")
