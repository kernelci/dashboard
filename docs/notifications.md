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
| `--ignore-recipients` | Bypass the recipients in the subscription, `regression/`, and `new_issues/` files | Flag | False |
| `--send` | Send email after generating report | Flag | False |
| `--to` | Specify direct recipient email. Overrides `new_issues/default.yaml` on the community summary | String | None |
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

Edit the file for your tree and send a PR to the dashboard. Use the git tree
name reported by the Web Dashboard.

- `[STATUS]` checkout summaries: `default_recipients` in the
  [subscriptions folder](../backend/data/notifications/subscriptions).
- `[REGRESSION]` issue reports: the
  [regression folder](../backend/data/notifications/regression). The report
  body names the file it took the Cc from.
- New-issues summary copies: the
  [new issues folder](../backend/data/notifications/new_issues). The community
  mail still goes to the `to` address in `default.yaml`. A copy names the
  files its rows came from.

### Regression recipients

Each `regression/<tree>.yaml` has a top-level key that must be a tree key
from `subscriptions/`. The tree's `url` decides which issues the file applies
to. Each entry Cc's its `recipients` when every scope key it sets matches:

```yaml
stable:
  - recipients: [list@example.org]          # no scope keys: every build issue on this tree's URL
  - branch: [linux-6.12.y, linux-6.6.y]
    architecture: [arm64]
    recipients: [maintainer@example.com]
```

| Key | Values | Matched against |
|---|---|---|
| `recipients` | addresses, at least one, sent as written | |
| `issues` | `build` only | the issue kind |
| `branch` | string or list | the branch printed in the report |
| `architecture`, `config_name`, `compiler` | string or list | any build where the issue occurred |

The Cc is the union of the matching entries, with repeated addresses dropped.
Any other key, including `platform` and `origin`, fails `pytest -m unit` with
the file, entry index, and key.

`test_report` only uses entries without scope keys.

With `--add-mailing-lists`, regression reports are sent to the `to` address in
[`regression/default.yaml`](../backend/data/notifications/regression/default.yaml).
`[STATUS]` summaries keep the address in `common.py`.

### New-issues recipients

[`new_issues/default.yaml`](../backend/data/notifications/new_issues/default.yaml)
replaces `--to` on the hourly summary. `--to` still overrides it. `issues`
lists the kinds in that community mail.

Other files are optional. A tree file's key must be a tree key in
`subscriptions/`, and the entry matches that tree's `url`. A
`*_hardware.yaml` key must be a platform in `subscriptions/`, and the entry
matches that platform. Each address with at least one matching issue gets one
mail for the run, combining every matching entry and file. No match sends
nothing. The community mail is still sent, including to an address that also
gets a copy.

```yaml
broonie-sound:
  - issues: [boot, test]
    recipients: [maintainer@example.com]
```

```yaml
qcs6490-rb3gen2:
  - issues: [boot]
    recipients: [board-owner@example.com]  # origin comes from that platform's *_hardware.yaml
```

| Key | Values | Matched against |
|---|---|---|
| `recipients` | addresses, at least one, sent as written | |
| `issues` | `build`, `boot`, `test` | the row kind |
| `branch`, `origin` | string or list | the first incident's row |
| `platform` | string or list | that row's platform. Build rows have none and never match |

An omitted `origin` on a hardware entry uses the platform's `origin` in
`subscriptions/*_hardware.yaml`, or `maestro` when that file omits it.
`architecture`, `config_name`, and `compiler` fail `pytest -m unit` with the
file, entry index, and key.

A copy goes to that address alone. Its body starts with `Copy from:
new_issues/<file>` for each file that contributed a row. The community mail
has no such line.


## Signup tree for checkout summary

Add a new file in the [subscriptions folder](../backend/data/notifications/subscriptions/) and send a PR to the dashboard.

Use the git tree name reported by the
Web Dashboard.
