# KernelCI Dashboard — Deployment Guide

This guide covers three deployment scenarios: [development](#1-development), [production](#2-production), and [staging](#3-staging).

## Quick Reference

| Scenario | Compose File | Database | Profiles |
|----------|-------------|----------|----------|
| Development | `docker-compose.yml` | Local (always on) | `with_commands` (for ingester) |
| Production | `docker-compose-next.yml` | External PostgreSQL | none (or `with_commands`) |
| Staging | `docker-compose.yml` | External PostgreSQL (shared with production) | none (or `with_commands`) |

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Development](#1-development)
- [2. Production](#2-production)
  - [Production deploy checklist](#production-deploy-checklist)
  - [Tagging a release](#tagging-a-release)
- [3. Staging](#3-staging)
- [Profile Reference](#profile-reference)
- [Docker Secrets Support](#docker-secrets-support)
- [Database schema changes](#database-schema-changes)
- [Ingester deployment](#ingester-deployment)
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

### Bot protection

The standard Compose deployments place
[Anubis](https://anubis.techaro.lol/) between the public NGINX listener and
the dashboard. Its policy is stored in `anubis/botPolicy.yaml`. Requests whose
user agent starts with `curl`, `wget`, `python-requests`, or `kci-dev` are
explicitly allowed without a challenge; other traffic uses Anubis's default
policy.

Anubis uses secure cookies by default in `docker-compose-next.yml`. Set
`ANUBIS_COOKIE_SECURE=false` only when the public dashboard is intentionally
served over plain HTTP. `docker-compose.yml` defaults this setting to `false`
for local development.

### Accessing production database

If direct access to the production database is required,
whether for local debugging or validating critical feature development,
you must request permissions for the SSH connection and database user.

1. Connect to the Azure database SSH bridge:
    - Create a new SSH key and add it to your SSH agent.
    - Share the public SSH key to the database maintainer, to be granted access
    to the SSH tunnel.
    - Connect to the database via SSH tunnel with the provided URL.
2. Request credentials: Obtain a new username and password for the database access.
3. Connect: Once you have your credentials, connect to the database via `psql`, `pgAdmin`,
`DBeaver`, or any other PostgreSQL manager.

## Database schema changes

The backend Docker entrypoint runs Django migrations on startup. Staging and production
use the same PostgreSQL database, so schema changes affect both environments once deployed.

> [!WARNING]
> Before merging or deploying database schema changes, coordinate with the team in the
> [KernelCI dashboard Discord channel](https://discord.com/channels/1245820301053530313/1301896040349433957).
>
> Migrations that **create a new table** must be called out explicitly there and
> **Denys Fedoryshchenko** must be notified. New tables need **manual grants** for
> database permissions; migrations do not apply those grants.

## 1. Development

This is the minimal guide for development using
the fully containerized (Docker Compose) alternative.
Images are built locally and use a global `.env` file.

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

### Local Frontend development

When implementing frontend features, a fast "hot reload" workflow
is usually preferred. In these scenarios, it is recommended to
run a local frontend server on the host machine.

For active frontend work, we can run the Vite dev server directly:

```bash
cd dashboard
pnpm install
# Copy the example env file and verify VITE_API_BASE_URL
cp .env.example .env
pnpm dev
```

The frontend connects to the backend API via the `VITE_API_BASE_URL`
defined in `dashboard/.env` (defaults to `http://localhost:8000`).

### Local Backend development
To implement backend features with hot reloading,
you can also start a local Django instance.

```bash
cd backend
poetry install

# Copy the env file and edit the DB_* to match your local database instance.
# Also set DEBUG=True to allow CORS connections and stack traces.
poetry run python3 manage.py runserver
```

The backend connects to a PostgreSQL instance using the environment variables:
`DB_NAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_ENGINE`, `DB_OPTIONS_CONNECT_TIMEOUT`.

---

## 2. Production

Unlike the development deployment, our production environment connects to a
pre-existing external PostgreSQL instance and use pre-built docker images
stored in the GitHub Container Registry (GHCR).

Production images are automatically built via GitHub Workflow,
to every new commit in the main branch, or when
the `Publish GHCR Images` workflow is triggered manually. After CI passes on
`main`, the dashboard is also deployed to staging
([deploy-staging](.github/workflows/deploy-staging.yaml)). Production is deployed
manually via [deploy-production](.github/workflows/deploy-production.yaml) (see
the [Production deploy checklist](#production-deploy-checklist) and
[Tagging a release](#tagging-a-release)).

> [!IMPORTANT]
> The **ingester** on `db.kernelci.org` is **not** updated by these dashboard
> GitHub Actions workflows. Deploy it via [Ingester deployment](#ingester-deployment).

> [!WARNING]
> It is important to point out that the backend entrypoint in Docker container
> will run database migrations.
> Changes that involve alterations in database schema should be previously communicated
> via [Discord channel](https://discord.com/channels/1245820301053530313/1301896040349433957).
> See also [Database schema changes](#database-schema-changes) (new tables require notifying
> Denys Fedoryshchenko for manual permission grants).

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

### Production deploy checklist

Read [Tagging a release](#tagging-a-release) when onboarding. After that, this list is
the path to follow so a step is not skipped. Production is never deployed by merging.

- Pre-deploy
  - Confirm the commit is on `origin/main`, with CI and staging e2e green
  - Diff migrations vs the previous release tag; if any, follow
    [Database schema changes](#database-schema-changes) (new tables: wait for Denys)
  - Create the `release/YYYYMMDD.N` tag on that commit
  - Push the tag
  - Run **Publish GHCR Images** on that `main` commit; wait for backend, frontend, and proxy
  - Run **Deploy production Dashboard** from `main` with `tag` set to the new release
    (only after the publish finished)

- Post-deploy
  - Open <https://dashboard.kernelci.org> in a browser and confirm the new release tag
    at the bottom of the left side panel
  - Check the GitHub Actions job summary for container state and health
    ([Post-deployment status](#post-deployment-status))
  - Check Dozzle for container health and init logs
  - If the release had migrations, ping Denys Fedoryshchenko for permission grants
  - Write a changelog and send it to the KernelCI mailing list
  - Ingester / `pending_aggregations_processor` are not updated here; use
    [Ingester deployment](#ingester-deployment) when those need a rollout

### Tagging a release

Production is never deployed by merging. Pushes to `main` run [ci.yaml](.github/workflows/ci.yaml),
deploy staging, and publish GHCR images; production is always triggered manually.

Every production deployment must be preceded by a release tag.
The dashboard displays its version (`git describe --tags`) at the bottom of the
side menu, so an untagged deployment shows a string like
`release/<old release>-N-g<sha>`, making it hard to tell which release is live.

#### Before deploying

- Deploy a commit that is already on `main`, with CI and the staging e2e tests green.
- Check whether the release carries migrations:

    ```bash
    git fetch origin main --tags
    git diff --name-only "$(git describe --abbrev=0 --tags)" origin/main -- '**/migrations/*.py'
    ```

    If the list is not empty, follow [Database schema changes](#database-schema-changes)
    before deploying. New tables require notifying Denys Fedoryshchenko and waiting
    for his acknowledgement, because the permission grants are applied manually.

#### Steps

1. Tag the `main` commit being released, following the `release/YYYYMMDD.N`
convention (`N` starts at `0` and increments for further releases on the same day):

    ```bash
    git fetch --tags
    git tag -l "release/$(date +%Y%m%d).*"  # pick the next N
    git tag release/20260729.0 <commit>
    git push origin release/20260729.0
    ```

2. Manually trigger the `Publish GHCR Images` workflow. Images built by the
earlier push to `main` were baked before the tag existed, so they still carry the
previous version string. Wait for the backend, frontend, and proxy jobs to finish.
3. Trigger the `Deploy production Dashboard` workflow with the new tag, from `main`
while `main` still points at the tagged commit.
4. Open <https://dashboard.kernelci.org> in a browser and confirm the new release
tag at the bottom of the left side panel.
5. If the release contained migrations, tell Denys Fedoryshchenko on Discord, so he
can apply the permission grants the migrations do not cover.

The same steps from the command line:

```bash
gh workflow run "Publish GHCR Images" --repo kernelci/dashboard --ref main
gh run watch <run-id> --repo kernelci/dashboard

gh workflow run "Deploy production Dashboard" --repo kernelci/dashboard --ref main \
    -f tag=release/20260729.0
gh run watch <run-id> --repo kernelci/dashboard
```

#### Things that are easy to get wrong

- The `tag` input does not select the images. It only sets `DASHBOARD_VERSION` (side menu)
and the Discord messages. Production pulls `:latest` unless the host `.env` sets
`IMAGE_TAG`. Do not start step 3 until step 2 has finished.
- Run the deploy workflow from `main` while `main` is still the tagged commit, so the
compose files on the host match that release. The host clone is `--depth 1 --branch main`.
- The **ingester** and `pending_aggregations_processor` are not started by this workflow
(the `with_commands` profile is not used), and `--remove-orphans` stops them if they are
already running on the host. See [Ingester deployment](#ingester-deployment).
- [staging-db.yaml](.github/workflows/staging-db.yaml) deploys the kcidb-ng stack on the
database host, which is a different deployment from the one described here.

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

A GitHub workflow for staging is defined at [deploy-staging](.github/workflows/deploy-staging.yaml).
It runs automatically on pushes to `main` after the checks in
[ci.yaml](.github/workflows/ci.yaml) succeed.

> [!IMPORTANT]
> The **ingester** on `db.kernelci.org` is **not** deployed by this workflow.
> See [Ingester deployment](#ingester-deployment).

> [!WARNING]
> Migrations are automatically executed in the backend entrypoint
> when the docker container is executed.
> And as the staging environment is shared with production, the same precautions should follow.
> Changes that involve alterations in database schema should be previously communicated
> via [Discord channel](https://discord.com/channels/1245820301053530313/1301896040349433957).
> See also [Database schema changes](#database-schema-changes) (new tables require notifying
> Denys Fedoryshchenko for manual permission grants).

## Post-deployment status

Staging and production workflows add a service table to the GitHub Actions job
summary after deployment. It reports each container's state, health, restart
count, and running image. The same table is included in deployment failure
notifications.

The backend health check requests `http://localhost:8000/health/` with the
`backend` host header, so `ALLOWED_HOSTS` must contain `backend`.

To inspect the same information on a deployment host:

```bash
sh .github/scripts/deploy_collect_compose_status.sh docker-compose.yml
sh .github/scripts/deploy_collect_compose_status.sh docker-compose-next.yml
```

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

## Ingester deployment

The ingester on `db.kernelci.org` is defined in the
[kcidb-ng](https://github.com/kernelci/kcidb-ng) `docker-compose.yaml` (it uses the
`dashboard-backend` image and the `monitor_submissions` command).

Rolling out ingester changes to that host is **not** done through this repository's
dashboard deployment workflows (`Deploy production Dashboard`, `Deploy staging`, and
the like). Use the [**Build and Deploy**](https://github.com/kernelci/kcidb-ng/actions/workflows/deploy.yml)
GitHub Actions workflow in **kernelci/kcidb-ng** (on pushes to `main` or via
**workflow_dispatch**). That workflow builds the kcidb-ng services and redeploys the
Compose stack on the database server, including the ingester and
`pending_aggregations_processor` containers.

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

- [README](./README.md) - Project overview and build instructions
- [CONTRIBUTING](./CONTRIBUTING.md) - How to contribute to the project
- [Monitoring Setup](./docs/monitoring.md) — Prometheus metrics configuration
- [Notifications](./docs/notifications.md) — Email and Discord notification setup
- [Performance Tests](./docs/performanceTests.md) - k6 load test setup (`docker-compose.k6.yml`)
