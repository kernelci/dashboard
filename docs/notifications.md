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
1.  `fake_report`
    * Generates a fake report (for  testing email send).


### Email Management Options

| Option | Description | Type | Default |
|--------|-------------|------|---------|
| `--add-mailing-lists` | Include community mailing lists in recipients | Flag | False |
| `--ignore-recipients` | Bypass the recipients in the subscription file | Flag | False |
| `--send` | Send email after generating report | Flag | False |
| `--to` | Specify direct recipient email | String | None |
| `--cc` | Specify CC recipient emails a "email1, email2" list  | String | None |
| `--yes` | Send email without confirmation | Flag | False |


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


## Signup tree for checkout summary

Add a new file in the [subscriptions folder](../backend/data/notifications/subscriptions/) and send a PR to the dashboard.

Use the git tree name reported by the
Web Dashboard.
