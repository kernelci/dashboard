# KernelCI Dashboard

Our Web Dashboard to evaluate test results from the common results database([KCIDB](https://docs.kernelci.org/kcidb/)).
Available at [dashboard.kernelci.org](https://dashboard.kernelci.org).

The new KernelCI Web Dashboard is a web application created to provide access
to static checks, build logs, boot logs and test results related for the Linux kernel
CI/test ecosystem. All that data will be provided by [KCIDB](https://docs.kernelci.org/kcidb/)
system from the [KernelCI Foundation](https://kernelci.org/).

## Repository
What we have as a repository is a monorepo containing the *dashboard* (the web application) and a *backend*.

### Dashboard
 A web app built with [React](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/), to see more information check the dashboard [README](dashboard/README.md).

### Backend
A Python http server built with [Django](https://www.djangoproject.com/) + [DRF](https://www.django-rest-framework.org/), to see more information check the backend [README](backend/README.md).


## Quick run

To run pre-built images without rebuilding, use [docker-compose-next.yml](./docker-compose-next.yml). Copy [`.env.example`](.env.example) to `.env`, set required values, then start the stack. The proxy defaults to port **80**. See [DEPLOYMENT.md](./DEPLOYMENT.md) for details.

## Local development

Pick the workflow that fits how you want to work:

| Workflow | Guide |
|---|---|
| Docker with live reload (recommended) | [docs/dev-environment.md](docs/dev-environment.md) — `make dev` or `docker compose -f docker-compose.dev.yml up -d` |
| Manual backend + frontend on the host | [backend/README.md](backend/README.md) and [dashboard/README.md](dashboard/README.md) |
| Staging-like container run (no live reload) | [DEPLOYMENT.md](./DEPLOYMENT.md) §1 |
| Guided first-time setup | [docs/Onboarding.md](docs/Onboarding.md) |

**Env files:** Docker Compose reads root `.env` plus `dashboard/.env`. For manual backend runs, export variables from [`.env.backend.example`](.env.backend.example) (Django does not load that file automatically).

**Ports:** `docker-compose.dev.yml` and `docker-compose.yml` expose the app at `http://localhost:9000` by default. Running services on the host uses `5173` (frontend) and `8000` (backend). `docker-compose-next.yml` defaults to port **80**.

## Deploying to production

See [DEPLOYMENT.md](./DEPLOYMENT.md) for staging, production, and deployment scenarios.

To deploy to prod you need to push a tag in the `release/YYYYMMDD.N` format
like: `release/20240910.0`

### Publishing container images to GHCR

The workflow `.github/workflows/deploy-containers.yaml` publishes Docker images for the three services used by the dashboard stack:

- `dashboard-backend` (from `./backend`)
- `dashboard-frontend` (from `./dashboard/Dockerfile`)
- `dashboard-proxy` (from `./proxy`)

This workflow is triggered on pushes to main (on the original repository) and also manually (`workflow_dispatch`) and pushes images to GHCR under `ghcr.io/<owner>/<repo>` with two tags for each image:

- `latest`
- `${{ github.sha }}`

At the end of the run, the workflow writes an image digest summary in the GitHub Actions job summary.

## Test results email reports

See details about our new [notifications](docs/notifications.md) system.

## Manual environment checks

If you want to verify container/deployment environment settings before running services, use:

 - `docker compose run --rm backend poetry run python3 manage.py verify_env` for DB/Redis/Email + storage + env/secrets checks
- [docs/verify_env.md](docs/verify_env.md) for detailed examples, including test email sending to a specific destination
  - Destination is required with `--send-test-email` and `--to-email`.

## Contributing

Check out [CONTRIBUTING.md](./CONTRIBUTING.md) and the [onboarding guide](docs/Onboarding.md). Contributions are welcome!
