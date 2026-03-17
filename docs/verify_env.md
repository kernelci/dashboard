# Environment verification helpers

This project has a manual-only management command to validate local/container environment settings.

Command: `verify_env`

## What it validates

- Database connectivity (by default on Django `default` alias; additional aliases can be passed)
- Redis connectivity (`redis` service)
- Email backend configuration and SMTP connectability
- Required filesystem paths and mounted volumes writable check
- Environment variable/secrets presence sanity checks
- Optional real test email send

## Run inside Docker (manual)

```bash
# Run default non-destructive checks (db + redis + email + storage + env/secrets)
docker compose run --rm backend poetry run python3 manage.py verify_env

# Check only DB aliases and skip redis + email

docker compose run --rm backend poetry run python3 manage.py verify_env \
  --check-db --database-alias default,notifications

# Check redis endpoint only

docker compose run --rm backend poetry run python3 manage.py verify_env --check-redis

# Validate email backend only

docker compose run --rm backend poetry run python3 manage.py verify_env --check-email

# Validate storage permissions only

docker compose run --rm backend poetry run python3 manage.py verify_env --check-storage

# Validate env/secrets sanity only

docker compose run --rm backend poetry run python3 manage.py verify_env --check-env
```

## Send a test email

Use `--send-test-email` together with `--to-email`.

```bash
docker compose run --rm backend poetry run python3 manage.py verify_env \
  --send-test-email \
  --to-email your-email@example.com
```

Optional email overrides:

- `--subject "KernelCI env smoke"`
- `--body "Custom message"`
- `--cc recipient1@example.com,recipient2@example.com`

## Notes

- The command uses settings from `kernelCI/settings.py` plus the environment values in `.env.backend`.
- Non-sending checks are read-only and safe for routine manual execution.
- Use send mode with a mailbox you control, so you can confirm deliverability and final headers.
