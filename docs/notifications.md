# Notifications Management Command

## Overview

The `notifications` management command provides a flexible tool for generating and sending various types of email notifications related to issue reporting and summaries. It supports multiple actions and offers extensive configuration options.


## Command Syntax

```bash
poetry run ./manage.py notifications --action=<action> [options]
```

If you are running the project in a docker container, you should add a `docker compose run --rm backend` to get a container of the backend running separately in order to use environment variables and existing connections to the database and be able to send notifications.


## Actions

The command supports four primary actions:

1. `new_issues`
    * Generates a summary of new issues.
1. `issue_report`
    * Creates issue reports with multiple execution modes:
        * Report for a specific issue
        * Report for all pending issues
1. `summary`
    * Runs a checkout summary report for trees listed in the [subscriptions folder](../backend/data/notifications/subscriptions/).
1. `hardware_summary`
    * Generate weekly hardware reports for hardware listed in the [subscriptions folder](../backend/data/notifications/subscriptions/).
1.  `fake_report`
    * Generates a fake report (for  testing email send).


### Email Management Options

These options are available for all actions and are always optional:

| Option | Description | Type | Default |
|--------|-------------|------|---------|
| `--add-mailing-lists` | Include community mailing lists in recipients | Flag | False |
| `--ignore-recipients` | Bypass the recipients in the subscription file | Flag | False |
| `--send` | Send email after generating report | Flag | False |
| `--to` | Specify direct recipient email | String | None |
| `--cc` | Specify CC recipient emails as "email1, email2" list | String | None |
| `--yes` | Send email without confirmation | Flag | False |
| `--in-reply-to` | Message-ID to reply to (sets In-Reply-To header) | String | None |

### Action-Specific Options

| Option | Applies to | Required/Optional | Description |
|--------|------------|-------------------|-------------|
| `--id` | `issue_report`, `test_report` | **Required** for `test_report`; **Required** for `issue_report` unless `--all` is used | Issue ID or Test ID in Dashboard/KCIDB |
| `--all` | `issue_report` | **Alternative** to `--id` | Create reports for all issues not sent or not ignored |
| `--update-storage` / `-u` | `issue_report` | Optional | Update JSON storage while generating/sending reports |
| `--summary-signup-folder` | `summary` | Optional | Alternative signup folder under `/backend/data` |
| `--summary-origins` | `summary` | Optional | Comma-separated list to limit to specific origins |
| `--issue-report-origins` | `new_issues` | Optional | Comma-separated origins for the automatic regression report. Default: `maestro` |
| `--issue-report-types` | `new_issues` | Optional | Comma-separated issue types (`build`, `boot`, `test`) for the automatic regression report. Default: `build` |
| `--skip-sent-reports` | `summary` | Optional | Skip reports that have already been sent |
| `--hardware-origins` | `hardware_summary` | Optional | Comma-separated list to limit to specific origins |
| `--tree` | `fake_report` | Optional | Add recipients for the given tree name |


## Email Configuration

The notification system uses Django's SMTP backend to send emails. Configure the following environment variables:

### SMTP Settings

```bash
# Email backend configuration
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER="bot@kernelci.org"
export EMAIL_HOST_PASSWORD="your-app-password"
```

Only `EMAIL_HOST_PASSWORD` is a required parameter. All the others
are optional and already set in settings.py.

### Gmail Configuration

For Gmail SMTP:
1. Use an app-specific password (not your regular Gmail password)
2. Enable 2-factor authentication on your Google account
3. Generate an app password at https://myaccount.google.com/apppasswords
4. Use the generated password in `EMAIL_HOST_PASSWORD`

### Testing Configuration

Test your email configuration with:

```bash
poetry run python manage.py notifications \
  --action fake_report \
  --to your-email@example.com \
  --send \
  --yes
```


## Adding yourself to recipients

Edit the corresponding tree file in the [subscriptions folder](../backend/data/notifications/subscriptions) and send a PR to the dashboard.

Use the git tree name reported by the
Web Dashboard.

Every address in `default_recipients` is Cc on the mail that file already sends. A tree file sends the `[STATUS]` checkout summary, one per entry under `reports`, and the `[REGRESSION]` mail, one message per new build issue on that git URL. A `*_hardware.yaml` file sends the Monday `hardware <board> summary`. The hourly `new issues summary` still goes to `kernelci-results@groups.io` with every new build and boot issue. A `new_issues` block on a recipient adds a second copy for that address.

An entry is either an address string, including `Name <email>`, or a mapping with `email` and an optional `issues` list. `issues` names the issue kinds that address is notified about on the mails above: `build`, `boot`, or `test`. It does not subscribe anyone to the hourly summary.

```yaml
broonie-sound:
  url: https://git.kernel.org/pub/scm/linux/kernel/git/broonie/sound.git
  default_recipients:
    - email: someone-else@kernel.org
      issues: [build]
    - email: broonie@kernel.org
      issues: [build, boot, test]
```

`build` is the kind with a `[REGRESSION]` sender today. Every tree file lists `[build]` on each address, which states the mail those addresses already receive. Adding `boot` or `test` to `issues` records a request that the regression mail does not cover yet. Full regression reports prefer `build` when a checkout has both build and test incidents.

### Hourly new-issues summary

The summary runs once an hour, the same run as the community mail. There is no per-address schedule.

Add `new_issues` to opt an address into a filtered copy. `issue_types` is `build`, `boot`, `test`, or a combination. The copy contains only issues of those types in that file's scope:

- a tree file matches `git_repository_url`
- a hardware file matches the platform and its `origin` (`maestro` when omitted)

An issue is tied to its first incident, the same row the community summary prints. The copy is skipped when nothing matches. Someone on `kernelci-results@groups.io` who also has a block may get two mails. `--ignore-recipients` skips the copies. With `--send` left off, the command prints `To` and the issue ids for the community mail and for each copy.

```yaml
default_recipients:
  - someone-else@kernel.org
  - email: broonie@kernel.org
    issues: [build]
    new_issues:
      issue_types: [boot]
```

`test` issues are not part of the community mail. They are included only in copies whose `issue_types` list `test`.

The same run can also send a `[REGRESSION]` report. Without `--issue-report-origins` or `--issue-report-types`, that report stays limited to build issues from `maestro`. Boot issues and other origins are sent only when a flag lists them. The flags do not change who is on To or Cc: the list stays on To, the tree's `default_recipients` stay on Cc, and `regressions@lists.linux.dev` plus regzbot stay on mainline, next, and stable.

Hardware files keep plain address strings. Those addresses receive the Monday board summary and no issue mail, so there is no kind to list:

```yaml
qcs6490-rb3gen2:
  origin: maestro
  labs:
    lava-kci-qualcomm: https://lava-oss.qualcomm.com
  default_recipients:
    - Trilok Soni <tsoni@quicinc.com>
    - Shiraz Hashim <shashim@qti.qualcomm.com>
```

A hardware recipient can add the same `new_issues` block. The copy is limited to that platform.

Editing a file in that folder runs these checks in CI. A malformed file, an unknown issue kind, an unknown `issue_types` value, or an address without a single `@` fails with the file name and the field.

## Metrics rules

`backend/data/notifications/metrics/` holds one YAML file per rule group. A rule name is the top-level key. `hardware` and `trees` name keys in the subscriptions folder. `period_days` is a positive integer. Two rules that share a recipient and a hardware or tree name are rejected. These files are validated only; they do not send mail.

```yaml
qualcomm-weekly:
  recipients:
    - tsoni@quicinc.com
  hardware: [qcs6490-rb3gen2]
  origins: [maestro]
  period_days: 7
```


## Signup tree for checkout summary

Add a new file in the [subscriptions folder](../backend/data/notifications/subscriptions/) and send a PR to the dashboard.

Use the git tree name reported by the
Web Dashboard.
