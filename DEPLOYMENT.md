# KernelCI Dashboard — Deployment Guide

This guide covers three deployment scenarios: [containerized staging-like local run](#1-containerized-staging-like-local-run), [production](#2-production), and [staging](#3-staging).

For contributor live reload, see [docs/dev-environment.md](docs/dev-environment.md) instead.

## Quick Reference

| Scenario | Compose File | Database | Profiles |
|----------|-------------|----------|----------|
| Contributor live reload | `docker-compose.dev.yml` | Local | — |
| Staging-like local run | `docker-compose.yml` | Local (`dashboard_db`) | `with_commands` (for ingester) |
| Production | `docker-compose-next.yml` | External PostgreSQL | none (or `with_commands`) |
| Staging | `docker-compose.yml` | External PostgreSQL (shared with production) | none (or `with_commands`) |

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Containerized staging-like local run](#1-containerized-staging-like-local-run)
- [2. Production](#2-production)
- [3. Staging](#3-staging)
- [Profile Reference](#profile-reference)
- [Docker Secrets Support](#docker-secrets-support)
- [Migration Guide](#migration-guide-legacy)
- [Related Documentation](#related-documentation)

## Prerequisites

### Required Tools

| Tool           | Version | Homepage                         |
|------          |---------| ---                              |
| Docker         | ≥ 20.10 | https://www.docker.com/          |
| Docker Compose | ≥ 2.0   | https://docs.docker.com/compose/ |
| Git            | ≥ 2.0   | https://git-scm.com/             |

### Development Tools

| Tool   | Homepage                   |
| ----   | --------                   |
| pnpm   | https://pnpm.io/           |
| poetry | https://python-poetry.org/ |

### Optional Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| PostgreSQL | Local database for staging/dev | [postgresql.org](https://www.postgresql.org/download/) |
| pnpm | Frontend package management | `npm install -g pnpm` |
| Poetry | Backend package management | `python3 -m pip install poetry` | 

### Accessing production database

See [Onboarding Task 0](docs/Onboarding.md#task-0-check-your-ssh-and-database-access) for SSH tunnel and credential setup.

## 1. Containerized staging-like local run

> For contributor live reload (Django + Vite HMR), use [docs/dev-environment.md](docs/dev-environment.md) (`docker-compose.dev.yml`) instead.

This section covers a staging-like stack built from source with Gunicorn and a production-style frontend image. Images are built locally and use root `.env`. The proxy defaults to port **9000**.

### Setup

```bash
# Copy all example env files
cp .env.example .env

# Edit the env variables
# DB_PASSWORD and DJANGO_SECRET_KEY

# Start all core services (builds images from source)
docker compose up --build -d

# Include ingester and aggregation processor
docker compose --profile=with_commands up --build -d
```

### Rebuilding after code changes

```bash
# Rebuild and restart just the backend
docker compose up --build -d backend

# Rebuild everything
docker compose up --build -d
```

### Host-based development

For hot reload on the host machine, see [dashboard/README.md](dashboard/README.md) (frontend) and [backend/README.md](backend/README.md) (backend). Point `VITE_API_BASE_URL` in `dashboard/.env` at your backend (default `http://localhost:8000`).

---

## 2. Production

Unlike the development deployment, our production environment connects to a
pre-existing external PostgreSQL instance and use pre-built docker images
stored in the GitHub Container Registry (GHCR).

Production images are built on every push to main and when [deploy-containers.yaml](.github/workflows/deploy-containers.yaml) is triggered manually (`workflow_dispatch`).

The GitHub workflow for production is defined at: [deploy-production](.github/workflows/deploy-production.yaml)

> [!WARNING]
> It is important to point out that the backend entrypoint in Docker container
> will run database migrations.
> Changes that involve alterations in database schema should be previously communicated
> via [Discord channel](https://discord.com/channels/1245820301053530313/1301896040349433957).

### Setup

```bash
# 1. Create .env from the template
cp .env.example .env

# 2. Edit .env — at minimum, set these:
#    DB_HOST       → your PostgreSQL host
#    DB_PORT       → your PostgreSQL port (default: 5432)
#    DB_PASSWORD   → your PostgreSQL password
#    DJANGO_SECRET_KEY → a strong random string
#    ALLOWED_HOSTS → e.g. ["backend", "your-domain.com"]
#    CORS_ALLOWED_ORIGINS → e.g. ["https://your-domain.com"]

# 3. Start services
docker compose -f docker-compose-next.yml up -d

# 4. Verify frontend
curl http://localhost/api/

# 5. Verify backend
curl http://localhost/api # (via proxy)
curl http://localhost:8000/api/ # (direct access)

```

### (Optional) Run with ingester and aggregation processor

```bash
# Set INGESTER_SPOOL_DIR in .env to the host path where submissions arrive
docker compose -f docker-compose-next.yml --profile=with_commands up -d
```

### Updating to a new version

```bash
# Pull latest images and restart
docker compose -f docker-compose-next.yml pull
docker compose -f docker-compose-next.yml up -d
```

---

## 3. Staging

The current staging version of the KernelCI Dashboard is deployed similarly
to [production](#2-production), with the exception that staging deployment
does not pull docker images from the GHCR registry;
instead docker images are built locally.

However, it important to point that despite being in a different environment,
the staging still shares the PostgreSQL database with production.
Which demands extra caution for changes that require migrations or
significantly impact the database.

A GitHub workflow for staging is defined at [deploy-staging](.github/workflows/deploy-staging.yaml)

> [!WARNING]
> Migrations are automatically executed in the backend entrypoint
> when the docker container is executed.
> And as the staging environment is shared with production, the same precautions should follow.
> Changes that involve alterations in database schema should be previously communicated
> via [Discord channel](https://discord.com/channels/1245820301053530313/1301896040349433957).

---

## Profile Reference

| Command | Services |
|---------|----------|
| `docker compose -f docker-compose-next.yml up -d` | redis, backend, dashboard, proxy |
| `... --profile=local-db up -d` | + dashboard_db |
| `... --profile=with_commands up -d` | + ingester, pending_aggregations_processor |
| `... --profile=local-db --profile=with_commands up -d` | All services |

---

## Docker Secrets Support

The backend entrypoint supports Docker secrets for `DB_PASSWORD`. Instead of setting the password directly in `.env`, you can use:

```bash
# Create a secrets file
echo "my-secret-password" > backend/runtime/secrets/postgres_password_secret

# Set in .env or environment:
DB_PASSWORD_FILE=/run/secrets/postgres_password_secret
```

The entrypoint's `file_env` function reads the file and exports `DB_PASSWORD`. You cannot set both `DB_PASSWORD` and `DB_PASSWORD_FILE` — the entrypoint will error if both are present.

---
## Migration Guide (legacy)

### From `DB_DEFAULT_*` to `DB_*` variables

Previous versions used `DB_DEFAULT_*` prefixed variables (e.g., `DB_DEFAULT_PASSWORD`, `DB_DEFAULT_HOST`). These have been replaced with `DB_*` variables (e.g., `DB_PASSWORD`, `DB_HOST`).

**If upgrading from a previous deployment:**

1. Rename variables in your `.env` / environment:
   - `DB_DEFAULT_PASSWORD` → `DB_PASSWORD`
   - `DB_DEFAULT_HOST` → `DB_HOST`
   - `DB_DEFAULT_PORT` → `DB_PORT`
   - `DB_DEFAULT_NAME` → `DB_NAME`
   - `DB_DEFAULT_USER` → `DB_USER`
   - `DB_DEFAULT_ENGINE` → `DB_ENGINE`

2. If using Docker secrets: rename `DB_DEFAULT_PASSWORD_FILE` → `DB_PASSWORD_FILE`.

3. The `DB_DEFAULT` JSON blob environment variable is no longer generated — `settings.py` reads individual `DB_*` variables directly.

---

## Related Documentation

- [README](./README.md) - Project overview and local development
- [CONTRIBUTING](./CONTRIBUTING.md) - How to contribute to the project
- [Monitoring Setup](./docs/monitoring.md) — Prometheus metrics configuration
- [Notifications](./docs/notifications.md) — Email and Discord notification setup
- [Performance Tests](./docs/performanceTests.md) - k6 load test setup (`docker-compose.k6.yml`)
