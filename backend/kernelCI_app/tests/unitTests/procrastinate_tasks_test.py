import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kernelCI_app import procrastinate_tasks as tasks


@pytest.mark.unit
@patch("kernelCI_app.procrastinate_tasks.call_command")
def test_delete_unused_hardware_status_runs_the_command(call_command):
    tasks.delete_unused_hardware_status(timestamp=0)
    call_command.assert_called_once_with(
        "delete_unused_hardware_status",
        "--monitoring-id=delete_unused_hardware_status",
    )


@pytest.mark.unit
def test_retry_stalled_jobs_retries_every_stalled_job():
    job = MagicMock(id=1, task_name="x")
    manager = MagicMock(
        get_stalled_jobs=AsyncMock(return_value=[job]), retry_job=AsyncMock()
    )
    with patch.object(tasks.app, "job_manager", manager, create=True):
        asyncio.run(tasks.retry_stalled_jobs(timestamp=0))
    manager.retry_job.assert_awaited_once_with(job)
