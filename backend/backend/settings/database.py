from decouple import config

print("DB_HOST:", config("DB_HOST"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
        "CONN_HEALTH_CHECKS": True,
        "TEST": {
            "NAME": "testdatabase",
        },
    }
}
