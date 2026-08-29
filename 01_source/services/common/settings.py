"""Small settings factory shared by the three independently deployed services."""

import os
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def build_settings(service_name, app_config, root_urlconf, wsgi_application, db_env):
    use_sqlite = env_bool("SERVICE_USE_SQLITE", False)
    if use_sqlite:
        database = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.environ.get("SERVICE_SQLITE_PATH", ":memory:"),
        }
    else:
        database = {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get(db_env, service_name.replace("-service", "_db")),
            "USER": os.environ.get("SERVICE_DB_USER", "foodapp"),
            "PASSWORD": os.environ.get(
                "SERVICE_DB_PASSWORD",
                os.environ.get("FOOD_DELIVER_DB_PASSWORD", "changeme"),
            ),
            "HOST": os.environ.get("SERVICE_DB_HOST", "localhost"),
            "PORT": os.environ.get("SERVICE_DB_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }

    return {
        "SERVICE_NAME": service_name,
        "BASE_DIR": SOURCE_ROOT,
        "SECRET_KEY": os.environ.get(
            "DJANGO_SECRET_KEY", "service-development-key-not-for-production"
        ),
        "DEBUG": env_bool("DJANGO_DEBUG", False),
        "ALLOWED_HOSTS": [
            item.strip()
            for item in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
            if item.strip()
        ],
        "ROOT_URLCONF": root_urlconf,
        "WSGI_APPLICATION": wsgi_application,
        "INSTALLED_APPS": [app_config],
        "MIDDLEWARE": [
            "django.middleware.security.SecurityMiddleware",
            "django.middleware.common.CommonMiddleware",
        ],
        "DATABASES": {"default": database},
        "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
        "USE_TZ": True,
        "TIME_ZONE": "Asia/Shanghai",
        "LANGUAGE_CODE": "zh-hans",
        "APPEND_SLASH": False,
        "LOGGING": {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {"console": {"class": "logging.StreamHandler"}},
            "root": {"handlers": ["console"], "level": "INFO"},
        },
    }
