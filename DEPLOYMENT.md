# KernelCI Dashboard — Deployment Guide

This guide covers three deployment scenarios: **development**, **production**, and **staging**.

## Quick Reference

| Scenario | Compose File | Database | Profiles |
|----------|-------------|----------|----------|
| Development | `docker-compose.yml` | Local (always on) | `with_commands` for ingester |
| Production | `docker-compose-next.yml` | External PostgreSQL | none (or `with_commands`) |
| Staging | `docker-compose-next.yml` | Local via profile | `local-db` (+ `with_commands`) |

---

## 1. Development (`docker-compose.yml`)

The development setup builds images locally and uses per-service `.env` files.

### Setup

```bash
# Copy all example env files
cp .env.example .env
cp .env.backend.example .env.backend
cp .env.db.example .env.db
cp .env.proxy.example .env.proxy
cp .env.ingester.example .env.ingester
cp .env.pending_aggregations.example .env.pending_aggregations

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

### Frontend development

For active frontend work, run the Vite dev server directly:

```bash
cd dashboard
pnpm install
# Copy the example env file and verify VITE_API_BASE_URL
cp .env.example .env
pnpm dev
```

The frontend connects to the backend API via the `VITE_API_BASE_URL` defined in `dashboard/.env` (defaults to `http://localhost:8000`).

---

## 2. Production (`docker-compose-next.yml`, external PostgreSQL)

Uses pre-built images from GHCR and connects to an external PostgreSQL instance.

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

# 4. Verify
curl http://localhost/api/

# 5. Run database migrations (first deploy or after updates)
docker compose -f docker-compose-next.yml run --rm backend \
  sh -c "chmod +x ./migrate-app-db.sh && ./migrate-app-db.sh"
```

### With ingester and aggregation processor

```bash
# Set INGESTER_SPOOL_DIR in .env to the host path where submissions arrive
docker compose -f docker-compose-next.yml --profile=with_commands up -d
```

### Updating to a new version

```bash
# Pull latest images and restart
docker compose -f docker-compose-next.yml pull
docker compose -f docker-compose-next.yml up -d

# Run migrations if needed
docker compose -f docker-compose-next.yml run --rm backend \
  sh -c "chmod +x ./migrate-app-db.sh && ./migrate-app-db.sh"
```

---

## 3. Staging (`docker-compose-next.yml`, local PostgreSQL)

Uses pre-built images with a local PostgreSQL container via the `local-db` profile.

### Setup

```bash
# 1. Create .env from the template
cp .env.example .env

# 2. Edit .env — at minimum, set these:
#    DB_PASSWORD       → choose a password for the local postgres
#    DJANGO_SECRET_KEY → a random string (can be less strict for staging)
#    Keep DB_HOST=dashboard_db (the default)

# 3. Start the database first (wait for it to be ready)
docker compose -f docker-compose-next.yml --profile=local-db up -d dashboard_db
docker compose -f docker-compose-next.yml exec dashboard_db pg_isready -U admin

# 4. Start remaining services
docker compose -f docker-compose-next.yml --profile=local-db up -d

# 5. Verify
curl http://localhost:8000/api/
curl http://localhost/
```

### With all optional services

```bash
docker compose -f docker-compose-next.yml --profile=local-db --profile=with_commands up -d
```

### Tear down (including database volume)

```bash
docker compose -f docker-compose-next.yml --profile=local-db down -v
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

## Migration Notes

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

- [Monitoring Setup](docs/monitoring.md) — Prometheus metrics configuration
- [Notifications](docs/notifications.md) — Email and Discord notification setup
