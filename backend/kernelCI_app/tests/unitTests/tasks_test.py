from unittest.mock import patch

import pytest
from django.core.cache import caches
from django.test import SimpleTestCase, override_settings

from kernelCI_app.tasks import _lock_key, run_management_command

LOCMEM = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}
KEY = _lock_key("cmd", ("--x",))


@pytest.mark.unit
@override_settings(CACHES=LOCMEM)
@patch("kernelCI_app.tasks.call_command")
class TestRunManagementCommand(SimpleTestCase):
    def setUp(self):
        caches["default"].clear()

    def _run(self, task_id="t1"):
        return run_management_command.apply(task_id=task_id, args=("cmd", ["--x"]))

    def test_runs_and_releases_lock(self, call_command):
        result = self._run()
        assert result.get() == "ok"
        call_command.assert_called_once_with("cmd", "--x")
        assert caches["default"].get(KEY) is None

    def test_skips_when_another_run_holds_lock(self, call_command):
        caches["default"].set(KEY, "other-task")
        assert self._run().get() == "skipped"
        call_command.assert_not_called()
        assert caches["default"].get(KEY) == "other-task"

    def test_redelivery_with_same_id_takes_lock_back(self, call_command):
        caches["default"].set(KEY, "t1")
        assert self._run("t1").get() == "ok"
        call_command.assert_called_once()

    def test_failure_releases_lock_and_retries(self, call_command):
        call_command.side_effect = RuntimeError("boom")
        result = self._run()
        assert result.state == "FAILURE"
        assert call_command.call_count == 4  # first run + max_retries=3
        assert caches["default"].get(KEY) is None
