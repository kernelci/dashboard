# Background tasks: POCs

Celery and Procrastinate POCs below. Same job, same scenarios.

Issue: [#2253](https://github.com/kernelci/dashboard/issues/2253). Status: POCs, nothing is wired into production. `CRONJOBS` is unchanged.

## Job inventory (current cron)

All 14 entries live in `CRONJOBS` (`backend/kernelCI/settings.py`), registered by django-crontab and run by `crond` inside the backend container.

| Job | Schedule (UTC) | Healthcheck ping |
| --- | --- | --- |
| `notifications` new_issues | `59 * * * *` | yes |
| `notifications` summary (microsoft) | `30 14 * * *` | yes |
| `notifications` summary (maestro) | `30 2 * * *` | yes |
| `notifications` hardware_summary | `33 3 * * 1` | yes |
| `notifications` metrics_summary | `0 0 * * 6` | yes |
| `delete_unused_hardware_status` | `0 0 * * 1` | yes |
| `publish_visitor_requests` | `15 0 * * *` | yes |
| `warm_metrics_cache` | `10 0 * * 6` | no |
| `update_hardware_registry` | `0 3 * * *` | no |
| `recompute_hardware_daily` (15d / 1d) | `0 */6 * * *` / `50 * * * *` | no |
| `recompute_lab_daily` (30d / 1d) | `10 */6 * * *` / `20 * * * *` | no |
| `prune_db` | `0 4 * * 0` | no |

Cron behavior today:

- **Retries:** none. A failed run waits for the next schedule.
- **Overlap:** nothing prevents it. `recompute_*` runs hourly and every 6h, so the two can overlap.
- **Failure detection:** only the 7 jobs with a monitoring id. The rest are visible only in container logs.
- **Deployment:** a job killed by a container restart is lost until its next slot.
- **Missed runs:** if the container is down at the scheduled minute, the run is skipped.

## Celery POC

### What the POC does

- `backend/kernelCI/celery.py` is the Celery app. It reads `CELERY_*` Django settings.
- `kernelCI_app.tasks.run_management_command(command, args)` runs any management command with `call_command`. It adds:
  - a Redis lock per `command + args`, so two copies never run at once. The lock value is the task id, so a redelivered task takes its own lock back;
  - `acks_late` + `reject_on_worker_lost`, so a task lost with its worker is delivered again;
  - up to 3 retries with exponential backoff.
- `CELERY_BEAT_SCHEDULE` has one entry: `delete_unused_hardware_status`, same schedule as in `CRONJOBS`.
- Healthcheck.io pings keep working because they live inside the management command (`--monitoring-id`).
- Broker uses the existing Redis, DB 1. Results use DB 2 (expire after 1 day). The Django cache stays on DB 0.

### Run it

```bash
docker compose -f docker-compose.dev.yml --profile celery up -d --build backend celery_worker celery_beat
# demo: fire the job every 30s instead of Monday 00:00 UTC
CELERY_POC_INTERVAL_SECONDS=30 docker compose -f docker-compose.dev.yml --profile celery up -d celery_beat
# run once by hand
docker compose -f docker-compose.dev.yml --profile celery exec celery_worker poetry run celery -A kernelCI call \
  kernelCI_app.tasks.run_management_command --args='["delete_unused_hardware_status", ["--dry-run"]]'
docker compose -f docker-compose.dev.yml --profile celery logs -f celery_worker celery_beat
```

Tunables: `CELERY_POC_INTERVAL_SECONDS`, `CELERY_VISIBILITY_TIMEOUT` (seconds, default 7200).

### Celery evidence

Everything below ran on the dev compose stack (Celery 5.6.3, Redis 8 from `docker-compose.dev.yml`).

| Scenario | Result |
| --- | --- |
| Scheduled execution (30s interval) | beat logs `Scheduler: Sending due task ...` every 30s, worker receives each one. |
| Failure | A failing command is retried 3 times with backoff, then the task ends in `FAILURE` with the traceback (`celery result <id>`). Lock is released. The healthcheck `fail` ping fires on every attempt. |
| Overlap | Same job sent twice at once: the second returns `skipped` in 1ms, the side effect ran once. |
| Graceful deploy (`docker stop -t 90`) | Worker waits for the running task, side effect completes once, message acked. |
| Hard kill mid-run (default `visibility_timeout`, 2h) | Task is **not** redelivered and the lock stays until its TTL (61 min). The job is effectively lost for up to 2h, worse than cron. |
| Hard kill mid-run (`visibility_timeout`=30s) | Task redelivered about 100s after the kill with the same task id, takes the lock back and finishes. Side effect log: `START` twice, `END` once. |

Takeaways:

- Retry and "run again after a crash" only produce clean results for **idempotent** jobs. `notifications` sends email, so a redelivery after a partial send can duplicate it. Those jobs need their own dedup before they use retries.
- `visibility_timeout` must be longer than the longest job, otherwise Redis redelivers a task that is still running (the lock then turns it into `skipped`). That is the trade-off for recovery speed after a hard kill.
- Celery does not stop duplicates by itself. The lock in `tasks.py` is the part that does.

#### Findings from the POC run

- `kombu 5.7` (pulled by `celery 5.6`) needs `redis-py>=6.1`. `pyproject.toml` moved from `redis<6` to `redis>=6.1,<7`. The Django `RedisCache` backend works on 6.4 (unit tests are unchanged by the bump).
- `delete_unused_hardware_status` without `--dry-run` fails today against the dev database with Postgres `stack depth limit exceeded`. The same error happens when the command is run directly, so this is not Celery. The batched `pk__in` over composite keys is the likely cause. Not fixed here.

## Comparison (cron vs Celery)

| | cron (current) | Celery + beat |
| --- | --- | --- |
| Scheduling | `CRONJOBS`, one crontab per container | `CELERY_BEAT_SCHEDULE`, one beat process (must stay a singleton) |
| Retries | none | built in |
| Overlap | none | needs a lock (small, in `tasks.py`) |
| Failure visibility | healthcheck.io for 7 jobs, logs | result backend, task states, optional Flower, healthcheck.io unchanged |
| Hard kill / deploy | job lost until next slot | graceful: fine. Hard kill: lost until `visibility_timeout` |
| Deployment overhead | none | 2 more processes (worker about 195 MiB, beat about 110 MiB), `celery` + `redis>=6.1` deps, Redis DBs 1 and 2 |
| Reuses existing Redis | n/a | yes, no new service |

See the three-way table after the Procrastinate section.

## Procrastinate POC

[Procrastinate](https://procrastinate.readthedocs.io) keeps jobs in Postgres. No Redis, no broker, no separate scheduler: the worker also runs the periodic tasks.

### What the POC does

- `procrastinate.contrib.django` is an installed app. Its 47 migrations create the `procrastinate_*` tables in the `default` database (the router allows it).
- `kernelCI_app/procrastinate_tasks.py`:
  - `delete_unused_hardware_status`: `@app.periodic(cron="0 0 * * 1")`, `lock` + `queueing_lock`, up to 3 retries with exponential backoff.
  - `run_management_command`: manual entry point for demos.
  - `retry_stalled_jobs`: runs every minute and retries jobs of workers that stopped sending heartbeats. Procrastinate detects stalled jobs but does not rerun them by itself.
- Worker: `manage.py procrastinate worker --wait --concurrency=2`, heartbeat every 10s, worker considered dead after 30s.
- Job history, attempts and events are SQL tables (`procrastinate_jobs`, `procrastinate_events`).

### Run it

```bash
docker compose -f docker-compose.dev.yml --profile procrastinate up -d --build backend procrastinate_worker
# the worker restarts until the backend finishes migrating
docker compose -f docker-compose.dev.yml --profile procrastinate exec procrastinate_worker \
  poetry run python manage.py shell -c "from kernelCI_app.procrastinate_tasks import run_management_command as t; t.defer(command='delete_unused_hardware_status', args=['--dry-run'])"
docker compose -f docker-compose.dev.yml exec dashboard_db psql -U admin -d dashboard \
  -c "select id, task_name, status, attempts from procrastinate_jobs order by id desc limit 5"
```

`PROCRASTINATE_RETRY_BASE_SECONDS` (default 60) sets the backoff base.

### Procrastinate evidence

Procrastinate 3.12.0, same dev stack. A temporary `poc_sleep` command wrote START/END lines to a file to count side effects.

| Scenario | Result |
| --- | --- |
| Scheduled execution | The periodic `retry_stalled_jobs` was deferred and ran every minute, no beat process. |
| Failure | Unknown command: retried after 3s, 9s, 27s (backoff base 3), then `failed`. Every attempt is a row in `procrastinate_events`. |
| Overlap (`lock` + `queueing_lock`) | 3 defers at once: the 2nd is rejected (`AlreadyEnqueued`) while the 1st is still waiting. The 3rd is accepted and runs after the 1st ends. Runs are serial, never concurrent. Unlike the Celery lock, a late run is queued, not skipped. |
| Graceful deploy (`docker stop -t 90`) | The worker waits for the running job. It finished and was marked `succeeded`. |
| Hard kill mid-run | The job stayed `doing`. About 60s later (30s heartbeat timeout + the next minute tick of `retry_stalled_jobs`) it was retried and finished. Side effect log: `START` twice, `END` once. |
| Memory | The worker used about 85 MiB. |

Notes:

- `RetryStrategy(max_attempts=N)` allows N retries, so N+1 runs. The task uses `max_attempts=3`.
- Recovery after a crash needs `retry_stalled_jobs`. Without it the job stays `doing` forever.
- Same rule as Celery: rerunning a job restarts it from the beginning. Only idempotent jobs are safe to rerun (not `notifications`).
- Cost: 47 migrations and write traffic in the main `default` database. The queue is durable with the database, so a host crash does not lose it.

## Three-way comparison

| | cron (current) | Celery + beat | Procrastinate |
| --- | --- | --- | --- |
| Extra processes | none | worker + beat | 1 worker |
| Memory (measured, dev) | n/a | about 195 + 110 MiB | about 85 MiB |
| Needs | nothing | Redis, `celery`, `redis>=6.1` | Postgres (already used), `procrastinate`, `psycopg-pool`, `croniter` |
| Scheduling | `CRONJOBS` | beat (singleton) | built in the worker, safe with several workers |
| Retries | none | built in | built in |
| Overlap | none | custom Redis lock (skip) | `lock` (serialise) + `queueing_lock` |
| Failure visibility | healthcheck.io for 7 jobs | result backend | SQL tables, healthcheck.io unchanged |
| Hard kill | job lost until next slot | lost until `visibility_timeout`, unless tuned | retried in about 1 min with `retry_stalled_jobs` |
| Durability | none | Redis persistence | Postgres |
| Main risk | no retry, no overlap guard | `redis` major bump, 2 processes | schema in the main DB, jobs share DB load |

## Preliminary assessment

- Jobs that would gain the most: `recompute_*` (overlap protection, idempotent, retries are safe), `delete_unused_hardware_status`, `prune_db`, `update_hardware_registry`.
- Jobs to leave on cron until they are made idempotent: `notifications`.
- Final recommendation, rollout and rollback steps wait for the decision between the options above.
