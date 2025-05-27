from decouple import config


DEBUG = config("DEBUG", cast=bool)


if DEBUG:
    from .development import *
else:
    from .production import *
