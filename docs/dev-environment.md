# Local Development Environment

This document explains how to run the KernelCI Dashboard locally with live reload for both the backend and the frontend.

## Overview

`docker-compose.dev.yml` is a self-contained Compose file designed for contributors. It is separate from the production `docker-compose.yml` so it can be used without any changes to the production config.

**What live reload means in practice:**

- **Backend** — edit any `.py` file and Django's development server (`manage.py runserver`) restarts automatically. No container rebuild needed.
- **Frontend** — edit any file under `dashboard/src/` or `dashboard/public/` and Vite's Hot Module Replacement (HMR) pushes the change to the browser instantly, without a full page reload.

## Services

| Service | Image / Build | Port | Purpose |
|---|---|---|---|
| `backend` | `./backend` (Dockerfile) | 8000 | Django dev server with live reload |
| `dashboard_db` | `postgres:17` | 5434 → 5432 | PostgreSQL database |
| `redis` | `redis:8.0-M04-alpine` | — | Cache / message broker |
| `dashboard_dev` | `./dashboard/Dockerfile.dev` | 5173 | Vite dev server with HMR |
| `proxy` | `./proxy` (Dockerfile) | 9000 | Nginx — routes `/api` → backend, `/` → Vite |

## Setup

### 1. Copy environment files

```bash
cp .env.example .env
cd dashboard && cp .env.example .env && cd ..
```

### 2. Configure `.env`

Open `.env` and set the required values:

```
DB_PASSWORD=<choose a password>
DJANGO_SECRET_KEY=<any long random string>
```

For a fully local setup leave `DB_HOST=dashboard_db` (the default). The `CORS_ALLOWED_ORIGINS`, `PROXY_TARGET`, and `DB_PORT_PUBLISHED` values can stay at their defaults.

### 3. Start the stack

```bash
docker compose -f docker-compose.dev.yml up -d
```

> The first run builds the images automatically — this takes a few minutes while base images are downloaded and dependencies installed. Subsequent starts are fast because layers are cached.

### 4. Verify

```bash
# Backend API
curl http://localhost:8000/api/schema/

# Frontend via proxy (same URL as production)
curl http://localhost:9000/
```

Both should return HTTP 200.

## Accessing the app

| URL | What you get |
|---|---|
| `http://localhost:9000` | Full app through Nginx (backend + frontend, same as production) |
| `http://localhost:5173` | Vite dev server directly (HMR WebSocket always available) |
| `http://localhost:8000` | Django dev server directly |
| `http://localhost:8000/api/schema/swagger-ui/` | Swagger UI — interactive API docs |
| `http://localhost:8000/api/schema/redoc/` | ReDoc — alternative API docs viewer |

## Connecting a database client (DBeaver, TablePlus, etc.)

The `dashboard_db` service exposes PostgreSQL on the host at port `5434` by default to avoid conflicts with a local PostgreSQL install. Override `DB_PORT_PUBLISHED` in `.env` if you need a different host port.

| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `5434` (or `$DB_PORT_PUBLISHED` from `.env`) |
| Database | `dashboard` (or `$DB_NAME` from `.env`) |
| User | `admin` (or `$DB_USER` from `.env`) |
| Password | value of `DB_PASSWORD` in `.env` |

## Live reload in practice

### Backend

Any change to a `.py` file inside `backend/` is picked up automatically. Django's `StatReloader` polls for mtime changes every second and restarts the inner worker process when a change is detected. You will see a new `Starting development server` line in the logs:

```bash
docker compose -f docker-compose.dev.yml logs -f backend
```

### Frontend

Any change to a file inside `dashboard/src/` or `dashboard/public/` is picked up by Vite. The browser updates without a manual refresh. Vite logs each update:

```
[vite] hmr update /src/components/MyComponent.tsx
```

CSS-only changes are injected into the page without touching JavaScript at all.

If you introduce a syntax error, Vite surfaces it in the browser overlay and in the terminal — fix the file and it recovers automatically.

## Running database migrations

The backend container runs migrations automatically on startup through `backend/utils/docker/backend_entrypoint.sh`. That entrypoint calls `backend/migrate-app-db.sh` for the default PostgreSQL database and `backend/migrate-cache-db.sh` for the SQLite cache / notifications databases.

When you need to create or apply migrations manually, run the commands inside the running backend container so they target the live development databases:

```bash
# Create a new migration after editing models.py
docker compose -f docker-compose.dev.yml exec backend poetry run python manage.py makemigrations

# Apply pending migrations
docker compose -f docker-compose.dev.yml exec backend poetry run python manage.py migrate

# Roll back to a specific migration
docker compose -f docker-compose.dev.yml exec backend poetry run python manage.py migrate kernelCI_app 0016
```

## Regenerating the OpenAPI schema

After adding or modifying endpoints, regenerate `schema.yml` so Swagger UI reflects your changes:

```bash
docker compose -f docker-compose.dev.yml exec backend sh generate-schema.sh
```

Then open http://localhost:8000/api/schema/swagger-ui/ to validate your endpoint appears with the correct request/response types.

## Loading a database dump for local testing

Sample SQL dumps are distributed separately (download and extract a zip you received — the folder and file names may vary). Once you have the `.sql` files, load each one by piping it into `psql` inside the `dashboard_db` container:

```bash
docker compose -f docker-compose.dev.yml exec -T dashboard_db \
  psql -U ${DB_USER:-admin} -d ${DB_NAME:-dashboard} \
  < /path/to/dump.sql
```

> The `-T` flag disables pseudo-TTY allocation, which is required when piping stdin.

If you want to start from a clean slate before loading:

```bash
# 1. Wipe the database volume
docker compose -f docker-compose.dev.yml down -v

# 2. Start the stack (runs migrations automatically via the entrypoint)
docker compose -f docker-compose.dev.yml up -d

# 3. Load each dump file
docker compose -f docker-compose.dev.yml exec -T dashboard_db \
  psql -U ${DB_USER:-admin} -d ${DB_NAME:-dashboard} \
  < /path/to/dump.sql
```

## Stopping and cleaning up

```bash
# Stop without removing data
docker compose -f docker-compose.dev.yml down

# Stop and remove all volumes (wipes the database)
docker compose -f docker-compose.dev.yml down -v
```

**What does `-v` do?** By default, everything inside a container is thrown away when the container is removed, but data you want to keep (like the database) is stored in a *volume* — a piece of storage that lives outside the container and survives restarts and rebuilds. The `dashboard_db` service uses a volume to persist the PostgreSQL data files, which is why your database survives a normal `down` + `up` cycle.

The `-v` flag tells Compose to delete those volumes along with the containers, permanently wiping the database. Use it when you want a completely clean slate. It is the Docker equivalent of dropping and recreating the database.

> `--build` only rebuilds images — it never touches volumes. Your database data is safe when you rebuild. To get a clean database you must use `down -v` explicitly.

## Rebuilding after dependency changes

Normal source code changes never require a rebuild — they are picked up via volume mounts or live reload. A rebuild is only needed when something baked into the image changes: a `Dockerfile`, `pyproject.toml`, or `pnpm-lock.yaml`.

The `--build` flag forces Compose to rebuild images even if they already exist locally. Without it, `docker compose up` reuses whatever is cached.

If you change `pyproject.toml` or `pnpm-lock.yaml`, restart the affected service with `--build`:

```bash
# Backend only
docker compose -f docker-compose.dev.yml up -d --build backend

# Frontend only
docker compose -f docker-compose.dev.yml up -d --build dashboard_dev

# Both
docker compose -f docker-compose.dev.yml up -d --build backend dashboard_dev
```

If you want Compose to recreate containers without stopping the whole stack first, add `--force-recreate`:

```bash
docker compose -f docker-compose.dev.yml up -d --force-recreate backend dashboard_dev
```

## Edge cases and known limitations

The following scenarios were tested against the live dev stack. Each one documents what actually happens and how to handle it.

### Backend edge cases

#### Syntax error or ImportError in a Python file

Django's `StatReloader` detects the file change and attempts to restart the inner server process. If the error prevents Django from starting (syntax error, missing import, etc.), the inner process exits with code 1. The outer autoreloader process then also exits, and the container stops.

**What you see:**

```
SyntaxError: invalid syntax
...
[Container exits]
```

The server is **not** available while the error is present (`Connection refused`). The container does not automatically recover — it exits rather than looping.

**How to recover:**

1. Fix the file.
2. Restart the container:

```bash
docker compose -f docker-compose.dev.yml up -d backend
```

No rebuild is needed; the fixed source is picked up immediately on start.

> Note: this differs from Vite's behaviour. Vite stays running and shows an error overlay in the browser; Django's dev server exits entirely.

#### Changes to `settings.py`

`settings.py` is in `sys.modules` and is watched like any other Python file. Changes trigger a normal auto-reload. The server stays up and the new settings take effect immediately.

#### Rapid successive changes (multiple saves within one second)

Django's `StatReloader` polls every second and takes a snapshot at each tick. If you save a file five times in quick succession, only **one reload** is triggered — whichever mtime is current when the next poll runs. This is safe; no intermediate broken states are applied.

#### Deleting a file that has already been imported

The running server process has the module in `sys.modules` and keeps serving from memory. The deletion is **not immediately detected** because `StatReloader` watches mtimes of existing files — a deletion does not change any watched mtime.

The crash surfaces on the **next reload** (when another watched file changes), because Django then tries to re-import everything from scratch and finds the file missing. At that point the container exits.

**How to handle:** restore the file before making any other change, or immediately run `docker compose up -d backend` after restoring it.

If a `.pyc` file for the deleted module still exists in `__pycache__/`, Python will silently load from it even after the source is gone. Remove the stale `.pyc` to force the error to surface earlier:

```bash
rm backend/kernelCI_app/__pycache__/<module>.cpython-312.pyc
```

#### Stale `.pyc` files masking source changes

If a `.pyc` in `__pycache__/` has a newer mtime than its `.py` source, Python skips recompiling the source and loads the cached bytecode. This can hide a change you just made.

Remove the stale `.pyc` and the next reload will pick up the current source:

```bash
# Remove all pyc files for the app
find backend/kernelCI_app/__pycache__ -name "*.pyc" -delete
```

Or trigger a forced reload by touching the source file:

```bash
touch backend/kernelCI_app/utils.py
```

### Frontend edge cases

#### Syntax / parse error in a `.tsx` or `.ts` file

Vite catches the error during its transform step and:

1. Logs `Pre-transform error: <file>: <message> (<line>:<col>)` to the terminal.
2. Sends an error overlay to the browser.
3. **Does not crash** — the Vite server keeps running.

When you fix the file, Vite sends an HMR update and the browser clears the overlay automatically. No manual action needed.

#### Editing `vite.config.ts`

Vite watches its own config file. Any change triggers an automatic **full Vite server restart** (not HMR):

```
[vite] vite.config.ts changed, restarting server...
[vite] server restarted.
```

This takes ~2 seconds and requires no manual intervention.

#### Adding or removing packages (`package.json` / `pnpm-lock.yaml`)

Vite does **not** watch `package.json` or `pnpm-lock.yaml`. Changes to these files are completely ignored by the running dev server.

After adding or removing a dependency, rebuild the image:

```bash
docker compose -f docker-compose.dev.yml build dashboard_dev
docker compose -f docker-compose.dev.yml up -d dashboard_dev
```

#### Circular imports between components

Vite resolves circular imports without crashing and without any warning. The browser receives a module that may have `undefined` references on first evaluation, which can cause silent runtime bugs (e.g., a component that renders nothing, or a `TypeError` in the console).

If a component renders unexpectedly blank or you see `undefined is not a function` in the browser console, check for circular imports between your files.

#### Changes to files in `public/`

Files under `dashboard/public/` are served as static assets. Vite watches the `public/` directory and triggers a **full page reload** (not HMR) when any file there changes:

```
[vite] (client) page reload public/robots.txt
```

The browser re-fetches the new asset automatically. No manual action needed.

#### Files outside `src/` and `public/` mounts

Only `dashboard/src/` and `dashboard/public/` are mounted as volumes. Files like `tsconfig.json`, `tailwind.config.ts`, and `eslint.config.js` live in the image layer (baked in at build time). Changes to these files from the host are **not seen by the running container**.

To apply changes to any file outside the two mounted directories:

```bash
docker compose -f docker-compose.dev.yml build dashboard_dev
docker compose -f docker-compose.dev.yml up -d dashboard_dev
```

---

## Known caveat: Docker Desktop on macOS and Linux (inode issue)

**TL;DR** — if file changes are not picked up by the container, use native Docker Engine instead of Docker Desktop.

This affects **all Docker Desktop installations** — macOS and Linux alike. It does not affect native Docker Engine on Linux.

### What happens

Most code editors (VS Code, Neovim with swap files, etc.) write files atomically:

1. Write new content to a temporary file (new inode).
2. Rename the temporary file over the original filename.

On **native Docker Engine** (Linux), the container and host share the same kernel and filesystem. Renaming a file updates the directory entry immediately — both host and container see the new inode.

On **Docker Desktop** (macOS or Linux), the containers run inside a lightweight VM (Apple Hypervisor / VirtioFS on macOS, QEMU/KVM on Linux). The VM's bind mount driver tracks the original inode. When the host atomically renames a file, the directory entry on the host updates to the new inode but the container still serves the old one via the stale inode reference.

| Setup | Live reload works? |
|---|---|
| Native Docker Engine (Linux) | ✅ No issue |
| Docker Desktop (Linux) | ❌ Inode issue |
| Docker Desktop (macOS) | ❌ Inode issue |
| Docker Desktop (Windows + WSL2) | ⚠️ Works if files are edited from inside WSL2; editing from Windows Explorer has the same issue |

### Symptoms

- You save a file in your editor; the container still loads the old version.
- `ls -i file` on the host and inside the container shows **different inode numbers** for the same path.

### Verifying

```bash
# On the host
ls -i backend/kernelCI_app/models.py

# Inside the container
docker compose -f docker-compose.dev.yml exec backend ls -i /backend/kernelCI_app/models.py
```

If the inode numbers differ, atomic writes are the cause.

### Workarounds

**Option A — Use native Docker Engine (Linux, recommended)**

Install the Docker Engine package directly (not Docker Desktop). On Fedora/RHEL:

```bash
sudo dnf install docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
```

On Ubuntu/Debian:

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
```

With native Docker Engine the inode issue does not exist.

**Option A (macOS) — Use OrbStack instead of Docker Desktop**

[OrbStack](https://orbstack.dev) is a Docker Desktop alternative for macOS that uses a more efficient VM layer with better filesystem event propagation. It resolves the inode issue in most cases and is a drop-in replacement (`docker` and `docker compose` commands work identically).

**Option B — Write files from inside the container**

Editing through the container preserves the original inode because the write happens on the VM's filesystem view:

```bash
docker compose -f docker-compose.dev.yml exec backend \
  node -e "const fs=require('fs'); let f='/backend/kernelCI_app/models.py'; fs.writeFileSync(f, fs.readFileSync(f,'utf8').replace('old','new'));"
```

This is inconvenient for normal development — Option A is the practical solution.

**Option C — Restart the container after saving**

```bash
docker compose -f docker-compose.dev.yml restart backend
```

This is instant (no rebuild), but you lose live reload.
