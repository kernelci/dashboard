# Notifications

The backend sends email reports from KCIDB results through the `notifications`
Django management command. Cron jobs run the scheduled reports. The notification
system is independent of the frontend.

Entry point: [notifications.py](../backend/kernelCI_app/management/commands/notifications.py).
Subscriptions live in [backend/data/notifications/subscriptions/](../backend/data/notifications/subscriptions/).

## Data flow

1. The command selects an action and loads its subscriptions, where applicable.
2. Queries read checkouts, builds, tests, issues, and incidents from PostgreSQL.
3. The action renders a plain-text report with a Jinja template from
   [management/commands/templates/](../backend/kernelCI_app/management/commands/templates/).
4. The shared email helper prints the report in a dry run, or resolves recipients
   and sends it through Django's email backend.
5. Actions that track notifications use the separate `notifications` SQLite
   database. This stores discovered issues and sent-report metadata.

`new_issues`, `summary`, `hardware_summary`, and `metrics_summary` return without
running on staging. They can run in production and development.

## Running the command

Run from `backend/` with the backend environment configured:

```bash
poetry run python manage.py notifications --action=summary --summary-origins=maestro
```

Without `--send`, the command prints the subject and body. With `--send`, it asks
for confirmation unless `--yes` is also present. A dry run of `new_issues` still
stores newly discovered issues, so it changes what a later run considers new.

For an existing development stack, run the same command inside the backend
container:

```bash
docker compose -f docker-compose.dev.yml exec backend \
  poetry run python manage.py notifications --action=summary --summary-origins=maestro
```

Run Compose commands from the repository root. See
[dev-environment.md](dev-environment.md) for database and environment setup.

## Actions

| Action | Behavior |
| ------ | -------- |
| `new_issues` | Looks for recent issues, records newly discovered issue ID/version pairs, and emails a summary. Also generates individual reports for new Maestro build issues. |
| `issue_report` | Generates a regression report for `--id`, or processes pending build issues with `--all`. The bulk mode asks whether to ignore each issue for that run. |
| `test_report` | Generates a boot or test regression report for a test `--id`, with up to ten history entries and the most recent passing commit from that history. |
| `summary` | Generates checkout status reports for subscribed branches and origins. Sends only when test history changes, unless `always: true` is set. |
| `hardware_summary` | Reports the last seven days of results for subscribed hardware, filtered by its configured labs. |
| `metrics_summary` | Reports activity for the previous seven complete UTC days and compares it with the preceding seven days. Includes tree, checkout, build, test, issue, and lab activity data. |
| `fake_report` | Exercises the email path with a fixed test subject and body. |

### Checkout summaries

For each subscribed repository and branch, the query selects the latest checkout
in the window from 29 hours ago to 5 hours ago. It gathers build, boot, and test
status counts and associated build issues for the selected revision.

The command then evaluates test history over the last seven days:

- Match the subscription's origin, repository URL, branch, and optional test path
  patterns. Exclude the `kubernetes` platform.
- Group tests by platform, build configuration, architecture, compiler, and path.
- Read up to five results per group, newest first. Keep groups whose latest
  result belongs to the selected revision.
- Skip groups with only one distinct status. Classify the remaining histories as
  regressions, fixes, or unstable tests.

A latest `FAIL` preceded by `PASS` is a regression. A latest `PASS` preceded by
`FAIL` is a fix. A history that switches back again, or includes an inconclusive
status, is unstable. Histories with one repeated status do not trigger a report,
including repeated failures.

Unless the subscription sets `always: true`, the command skips the report when
all three groups are empty. Build failures or build issue records alone do not
trigger a checkout summary. `always: true` bypasses this change check, but still
requires a checkout in the selection window.

The CIP subscription omits `always` on all its branches in this branch. CIP
therefore receives summaries only when the test-history check finds changes.

### Issue reports

`new_issues` searches a one-hour window, selects the highest recent version of
each issue, and excludes issues with older incidents. It compares the results
with the issue ID/version pairs already stored in SQLite before rendering the
summary. Test-linked issues enter this discovery path as boot issues.

For each new Maestro build issue, it enables community mailing lists and storage
updates before generating an individual report. Boot issues do not get an
automatic individual report through this path.

`issue_report --id` fetches the latest issue version and its incidents. It looks
for passing builds or tests without the issue over an 18-day window to provide
regression context. `issue_report --all` only processes stored, unsent build
issues. Ignoring an already stored issue does not persist a separate ignored
state, so it can appear again on a later run.

## Subscriptions

### Trees

Add or edit a YAML file in the subscriptions directory. The top-level tree name
should follow the Dashboard's tree name. The repository URL, branch, and origin
identify the checkout summary subscription. Report labels are descriptive; the
loader reads the fields inside each report.

```yaml
example:
  url: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
  default_recipients:
    - maintainer@example.com
  reports:
    - default:
      branch: master
      origin: maestro
      always: true
    - rt_tests:
      branch: master
      path: [rt-tests%]
      recipients:
        - tests@example.com
      options:
        - ignore_default_recipients
```

| Field | Behavior |
| ----- | -------- |
| `origin` | Defaults to `maestro`. `--summary-origins` limits which origins run. |
| `always` | Defaults to false. Set true to generate a summary even without test-history changes. |
| `path` | List of SQL `LIKE` patterns for the test-history check. For example, `rt-tests%` matches paths with that prefix. Omit it to consider all paths. It does not filter the overall status counts. |
| `default_recipients` | Tree-level recipients, added to Cc. Individual issue and test reports find these by repository URL. |
| `recipients` | Additional recipients for this checkout report, added to Cc. |
| `options: [ignore_default_recipients]` | Use only the report-specific recipients for this checkout report. |

See [example-subscription.yaml](../backend/data/notifications/example-subscription.yaml).
Changes to subscriptions go through the repository's normal contribution process.

### Hardware

Hardware subscription filenames must end in `_hardware.yaml` or `_hardware.yml`.
The top-level key is the hardware platform name. Each entry supplies an origin,
lab names and URLs, and default recipients:

```yaml
example-board:
  origin: maestro
  labs:
    example-lab: https://lab.example.com
  default_recipients:
    - maintainer@example.com
```

The origin defaults to `maestro`. `--hardware-origins` limits which origins run.
The configured lab names filter the report data. See
[example-hardware-subscription.yaml](../backend/data/notifications/example-hardware-subscription.yaml).

## Recipients and email options

Emails use `KernelCI bot <bot@kernelci.org>` as the sender.

| Option | Behavior |
| ------ | -------- |
| `--send` | Send the report instead of printing a dry run. |
| `--yes` | Skip the send confirmation. Does not skip the bulk issue ignore prompt. |
| `--to` | Set the direct To address. |
| `--cc` | Add comma-separated Cc addresses. |
| `--add-mailing-lists` | Set To to `kernelci-results@groups.io` and Reply-To to `kernelci@lists.linux.dev`. Overrides `--to`. |
| `--ignore-recipients` | Exclude subscription recipients. Explicit `--cc` and community mailing lists still apply. |
| `--in-reply-to` | Set the `In-Reply-To` header to an existing Message-ID. |
| `--summary-signup-folder` | Override the subscription directory, relative to `backend/data/`. The command also passes this directory to issue, test, and hardware reports. |
| `--update-storage`, `-u` | Record sent issue or checkout reports in SQLite when the send helper returns a Message-ID. |
| `--monitoring-id` | Select a configured Healthchecks monitor for command execution. See [monitoring.md](monitoring.md). |

When community mailing lists are enabled, regression reports for `mainline`,
`next`, and `stable` also Cc `regressions@lists.linux.dev`. Their templates include
regzbot directives and a lore link using the email's own Message-ID.

`--tree` is accepted for `fake_report`, but currently does not resolve tree
subscription recipients. Use `--to` for the test email.

## Storage and repeat reports

Django's `notifications` database alias points to
`notifications.sqlite3` under `BACKEND_VOLUME_DIR`. Apply its migrations with:

```bash
poetry run python manage.py migrate --database=notifications
```

`notifications_issue` stores discovered issue ID/version pairs, their type, and
optional sent timestamps and Message-IDs. Discovery writes these records even
without `--send`. Individual issue reports update their sent metadata with
`--update-storage`; the automatic Maestro build report path enables that option
itself. `test_report` does not record sent notifications.

`notifications_checkout` stores sent checkout metadata when `--update-storage`
is enabled. The repeat-report query checks repository URL, branch, origin, and
path against a 12-hour window. A match removes the whole branch/URL/origin key
from the current run, including its other configured reports.

The current `--skip-sent-reports` flag behaves opposite to its help text. With
the flag present, the command bypasses the repeat-report check. Omit it to run
the check. Scheduled summary jobs omit both this flag and `--update-storage`,
so they consult existing records but do not record their own sends.

## Scheduled reports

The schedule is defined in [settings.py](../backend/kernelCI/settings.py) through
`django-crontab`. These are cron expressions in the cron environment's timezone.

| Schedule | Action | Delivery |
| -------- | ------ | -------- |
| `59 * * * *` | `new_issues` | Summary to `kernelci-results@groups.io`; individual Maestro build reports use community mailing lists and tree recipients. |
| `30 14 * * *` | `summary`, Microsoft | To `kernelcialerts@microsoft.com`, Cc `kernelci-results@groups.io`, ignoring subscription recipients. |
| `30 2 * * *` | `summary`, Maestro | Community mailing lists and subscription recipients. |
| `33 3 * * 1` | `hardware_summary` | Subscription recipients and Cc `kernelci-results@groups.io`. |
| `0 0 * * 6` | `metrics_summary` | To `kernelci@lists.linux.dev`, Cc `kernelci-results@groups.io`. |

All scheduled email jobs pass `--send --yes` and a monitoring ID. Metrics cache
warming runs separately at `10 0 * * 6` for the seven-day and fourteen-day
periods. The backend container entrypoint installs the crontab and starts cron.
Set `SKIP_CRONJOBS=True` to leave the configured job list empty during development.
See the [backend README](../backend/README.md#cron-jobs) for manual cron setup.

## Email configuration and testing

The default Django email backend is SMTP, using `smtp.gmail.com`, port `587`,
TLS, and the account `bot@kernelci.org`. Set `EMAIL_HOST_PASSWORD` for that
account. The settings also read `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`,
`EMAIL_USE_TLS`, and `EMAIL_HOST_USER` from the environment.

To inspect a test report without sending:

```bash
poetry run python manage.py notifications --action=fake_report
```

To test delivery to your own address:

```bash
poetry run python manage.py notifications \
  --action=fake_report --to=your-email@example.com --send
```

To preview a report using real data:

```bash
poetry run python manage.py notifications --action=test_report --id='<test-id>'
poetry run python manage.py notifications --action=issue_report --id='<issue-id>'
```

SMTP errors propagate from the send helper. Subscription and query logic lives
in [helpers/summary.py](../backend/kernelCI_app/management/commands/helpers/summary.py)
and [queries/notifications.py](../backend/kernelCI_app/queries/notifications.py).
Recipient resolution lives in
[helpers/common.py](../backend/kernelCI_app/management/commands/helpers/common.py),
and delivery lives in [helpers/email.py](../backend/kernelCI_app/helpers/email.py).
