"""
Django settings for kernelCI project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from utils.validation import is_boolean_or_string_true
import os
import json


def get_json_env_var(name, default):
    var = os.environ.get(name)
    if not var:
        return default
    try:
        return json.loads(var)
    except json.JSONDecodeError:
        if isinstance(default, str) or isinstance(default, bool):
            return var
        raise


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Path of data directory
BACKEND_DATA_DIR = os.path.join(BASE_DIR, "data")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_json_env_var(
    "DJANGO_SECRET_KEY", "django-insecure--!70an0r@i00)oqf!3uq_)9dx2^%)"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ENV_DEBUG = get_json_env_var("DEBUG", False)

if is_boolean_or_string_true(ENV_DEBUG):
    DEBUG = True

DEBUG_SQL_QUERY = False

ENV_DEBUG_SQL_QUERY = get_json_env_var("DEBUG_SQL_QUERY", False)

if is_boolean_or_string_true(ENV_DEBUG_SQL_QUERY) and DEBUG:
    DEBUG_SQL_QUERY = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 31536000


ALLOWED_HOSTS = get_json_env_var(
    "ALLOWED_HOSTS",
    ["localhost"],
)

# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "kernelCI_app",
    "kernelCI_cache",
    "rest_framework",
    "drf_spectacular",
    "django_crontab",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "kernelCI_app.middleware.logServerErrorMiddleware.LogServerErrorMiddleware",
]

ROOT_URLCONF = "kernelCI.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "kernelCI.wsgi.application"

REST_FRAMEWORK = {
    # YOUR SETTINGS
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "KernelCI Dashboard API",
    "DESCRIPTION": "API for the KernelCI dashboard",
    "VERSION": "0.9.0",
}

# To run cronjobs locally, execute
# poetry run ./manage.py crontab arg
# where "arg" is add, remove or show
CRONJOBS = [
    ("0 * * * *", "kernelCI_app.tasks.update_checkout_cache"),
    ("0 0 * * 0", "django.core.management.call_command", ["treeproof"]),
    (
        "59 * * * *",
        "django.core.management.call_command",
        [
            "notifications",
            "--action=new_issues",
            "--cc=gus@collabora.com",
            "--send",
            "--yes",
        ],
    ),
    (
        "30 14 * * *",
        "django.core.management.call_command",
        [
            "notifications",
            "--action=summary",
            "--to=Johnson.George@microsoft.com",
            "--cc=gus@collabora.com",
            "--ignore-recipients",
            "--send",
            "--yes",
            "--summary-signup-file=data/summary-signup-microsoft.yaml",
        ],
    ),
    (
        "30 2 * * *",
        "django.core.management.call_command",
        [
            "notifications",
            "--action=summary",
            "--add-mailing-lists",
            "--cc=gus@collabora.com",
            "--send",
            "--yes",
        ],
    ),
]

GMAIL_API_TOKEN = get_json_env_var("GMAIL_API_TOKEN", "")

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASE_ROUTERS = ["kernelCI_app.routers.disableMigrateRouter.DisableMigrateRouter"]

DATABASES = {
    "default": get_json_env_var(
        "DB_DEFAULT",
        {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "kernelci",
            "USER": "kernelci",
            "PASSWORD": "kernelci-db-password",
            "HOST": "127.0.0.1",
            "OPTIONS": {
                "connect_timeout": 5,
            },
        },
    ),
    "cache": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BACKEND_DATA_DIR, "cache.sqlite3"),
    },
}

if DEBUG:
    print("DEBUG: DEFAULT DATABASE:", DATABASES)


REDIS_HOST = get_json_env_var("REDIS_HOST", "127.0.0.1")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:6379",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MIGRATION_MODULES = {
    "kernelCI_app": None,
    "kernelCI_cache": "kernelCI_cache.migrations",
}

CORS_ALLOW_ALL_ORIGINS = False

CACHE_TIMEOUT = int(get_json_env_var("CACHE_TIMEOUT", "180"))

if DEBUG:
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http://localhost",  # dashboard dev server
    ]
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 3600
    CACHE_TIMEOUT = 0

if DEBUG_SQL_QUERY:
    LOGGING = {
        "disable_existing_loggers": False,
        "version": 1,
        "handlers": {
            "console": {
                # logging handler that outputs log messages to terminal
                "class": "logging.StreamHandler",
                "level": "DEBUG",  # message level to be written to console
            },
        },
        "loggers": {
            "": {
                # this sets root level logger to log debug and higher level
                # logs to console. All other loggers inherit settings from
                # root level logger.
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,  # this tells logger to send logging message
                # to its parent (will send if set to True)
            },
            "django.db": {
                # django also has database level logging
                "level": "DEBUG"
            },
        },
    }
