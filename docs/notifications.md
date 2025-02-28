# Notifications Management Command

## Overview

The `notifications` management command provides a flexible tool for generating and sending various types of email notifications related to issue reporting and summaries. It supports multiple actions and offers extensive configuration options.

## Command Syntax

```bash
poetry run ./manage.py notifications --action=<action> [options]
```

## Actions

The command supports four primary actions:

1. `new_issues`
    * Generates a summary of new issues.
1. `issue_report`
    * Creates issue reports with multiple execution modes:
        * Report for a specific issue
        * Report for all pending issues
1. `summary`
    * Runs a checkout summary report for trees listed in [summary-signup.yaml](../backend/kernelCI_app/management/commands/data/summary-signup.yaml).
1.  `fake_report`
    * Generates a fake report (for  testing email send).


### Email Management Options

| Option | Description | Type | Default |
|--------|-------------|------|---------|
| `--add-mailing-lists` | Include community mailing lists in recipients | Flag | False |
| `--ignore-recipients` | Bypass [recipients.yaml](../backend/kernelCI_app/management/commands/data/recipients.yaml) file | Flag | False |
| `--send` | Send email after generating report | Flag | False |
| `--to` | Specify direct recipient email | String | None |
| `--cc` | Specify CC recipient emails a "email1, email2" list  | String | None |
| `--yes` | Send email without confirmation | Flag | False |
| `--credentials-file` | Path to Gmail API credentials file. You only need it to generate the gmail_api_token.json file | String | None |


## Adding yourself to recipients

Edit the [recipients.yaml](../backend/kernelCI_app/management/commands/data/recipients.yaml) and send a PR to the dashboard.

Use the git tree name reported by the
Web Dashboard.


## Signup tree for checkout summary

Edit the [summary-signup.yaml](../backend/kernelCI_app/management/commands/data/summary-signup.yaml) and send a PR to the dashboard.

Use the git tree name reported by the
Web Dashboard