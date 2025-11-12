"""
Settings for performance tests.

Inherits from test_settings but enables migrations for proper database setup.
"""

from kernelCI.test_settings import *  # noqa: F403, F401

# Enable migrations for kernelCI_app, but keep kernelCI_cache migrations disabled
# to avoid issues with migrations that access the notifications database
MIGRATION_MODULES = {
    "kernelCI_cache": None,
}
