"""
Settings for performance tests.

Inherits from test_settings but enables migrations for proper database setup.
"""

from kernelCI.test_settings import *  # noqa: F403, F401

# test_settings disables every migration. Perf tests need the real schema,
# including the notification tables on the default database.
MIGRATION_MODULES = {}
