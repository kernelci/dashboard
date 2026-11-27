from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command

from kernelCI_app.helpers.logger import log_message


def _lock_key(command: str, args: tuple[str, ...]) -> str:
    return f"celery-lock:{command}:{' '.join(args)}"


@shared_task(
    bind=True,
    acks_late=True,
    reject_on_worker_lost=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_backoff_max=600,
    retry_kwargs={"max_retries": 3},
)
def run_management_command(self, command: str, args: list[str] | None = None) -> str:
    """Run a Django management command, never two copies of the same one at once.

    The lock value is the task id, so a redelivery after a worker crash
    (same id) takes the lock back instead of waiting for the TTL.
    Retries are safe only for idempotent commands.
    """
    args_tuple = tuple(args or [])
    key = _lock_key(command, args_tuple)
    task_id = self.request.id

    if not cache.add(key, task_id, timeout=settings.CELERY_TASK_LOCK_TTL):
        if cache.get(key) != task_id:
            log_message(f"Skipping {command}: another run holds the lock")
            return "skipped"
        cache.set(key, task_id, timeout=settings.CELERY_TASK_LOCK_TTL)

    try:
        call_command(command, *args_tuple)
    finally:
        if cache.get(key) == task_id:
            cache.delete(key)
    return "ok"
