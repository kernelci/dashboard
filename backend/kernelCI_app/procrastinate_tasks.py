import os

from django.core.management import call_command
from procrastinate import RetryStrategy
from procrastinate.contrib.django import app

from kernelCI_app.helpers.logger import log_message

RETRY_BASE_SECONDS = int(os.environ.get("PROCRASTINATE_RETRY_BASE_SECONDS", 60))
RETRY = RetryStrategy(max_attempts=3, exponential_wait=RETRY_BASE_SECONDS)
STALLED_AFTER_SECONDS = 30


# `lock` makes jobs with the same lock run one at a time (the later one waits).
# `queueing_lock` allows at most one waiting job, so a slow run cannot pile up.
@app.periodic(cron="0 0 * * 1")
@app.task(
    name="delete_unused_hardware_status",
    lock="delete_unused_hardware_status",
    queueing_lock="delete_unused_hardware_status",
    retry=RETRY,
)
def delete_unused_hardware_status(timestamp: int):
    call_command(
        "delete_unused_hardware_status",
        "--monitoring-id=delete_unused_hardware_status",
    )


@app.task(name="run_management_command", retry=RETRY)
def run_management_command(command: str, args: list[str] | None = None):
    """Manual entry point, used for demos and tests. Same retry and lock rules as the job."""
    call_command(command, *(args or []))


# Procrastinate marks jobs of dead workers as stalled but does not rerun them.
@app.periodic(cron="* * * * *")
@app.task(name="retry_stalled_jobs", queueing_lock="retry_stalled_jobs")
async def retry_stalled_jobs(timestamp: int):
    for job in await app.job_manager.get_stalled_jobs(
        seconds_since_heartbeat=STALLED_AFTER_SECONDS
    ):
        log_message(f"Retrying stalled job {job.id} ({job.task_name})")
        await app.job_manager.retry_job(job)
