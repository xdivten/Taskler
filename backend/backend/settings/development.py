from decouple import config

from .main import *


SERVER = config("SERVER", cast=bool)

CORS_ALLOW_CREDENTIALS = True

if SERVER:
    
    CSRF_COOKIE_DOMAIN = config("CSRF_COOKIE_DOMAIN")
    CSRF_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS").split(",")

    CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS").split(",")
    
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

    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"

else:

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True

    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    CSRF_COOKIE_HTTPONLY = False
    CSRF_COOKIE_SECURE = False
