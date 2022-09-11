from decouple import config

from .base import *  # noqa: F401, F403

ALLOWED_HOSTS = [
    "localhost",
    "165.22.90.173",
    "api.converter-x.com",
    "converter-x.com"
]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:9000",
    "http://165.22.90.173:8000",
)

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME", "templates_x"),
        "USER": config("DB_USER", "root"),
        "PASSWORD": config("DB_PASSWORD", ""),
        "HOST": config("DB_HOST", "localhost"),
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
}

# CELERY
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CACHE_MIDDLEWARE_ALIAS = "default"  # which cache alias to use
CACHE_MIDDLEWARE_KEY_PREFIX = ""

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "hybrid_x_",
    }
}
