"""
Test-specific Django settings for integration tests with local database.
"""

# Override database configuration for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "kcidb_test",
        "USER": "test_user",
        "PASSWORD": "test_password",
        "HOST": "test_db",
        "PORT": "5432",
        "OPTIONS": {
            "connect_timeout": 5,
        },
    },
    "dashboard_db": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dashboard_test",
        "USER": "test_user",
        "PASSWORD": "test_password",
        "HOST": "test_db",
        "PORT": "5432",
        "OPTIONS": {
            "connect_timeout": 5,
        },
    },
    "cache": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "notifications": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Disable debug for tests
DEBUG = False
DEBUG_SQL_QUERY = False

# Use in-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# Disable CORS for tests
CORS_ALLOW_ALL_ORIGINS = True

# Shorter cache timeout for tests
CACHE_TIMEOUT = 60

# Disable security features for tests
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Disable cron jobs for tests
CRONJOBS = []

# Use test email backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable logging for tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}

TEST_BASE_URL = "http://localhost:8001/"
