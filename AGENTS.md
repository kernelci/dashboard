# Agent notes — KernelCI Dashboard

Monorepo: React/TypeScript UI (`dashboard/`) plus Django REST API (`backend/`) over the KernelCI/KCIDB results database.

Human onboarding and contribution process live in [docs/Onboarding.md](docs/Onboarding.md) and [CONTRIBUTING.md](CONTRIBUTING.md). Do not copy those here.

## Where to look

| Need | Path |
| --- | --- |
| Layout of the DB | [backend/docs/database-logic.md](backend/docs/database-logic.md) |
| Adding or changing a filter | [docs/filters.md](docs/filters.md) |
| API request/response contract | `backend/schema.yml` — regenerate with [backend/generate-schema.sh](backend/generate-schema.sh) |
| URL ↔ endpoint map | [backend/kernelCI_app/urls.py](backend/kernelCI_app/urls.py) |
| Frontend request layer | `dashboard/src/api/` |
| User-visible strings | `dashboard/src/locales/messages/index.ts` |
| Integration tests | [docs/IntegrationTests.md](docs/IntegrationTests.md) |

Also: `docs/` (ops), `k6/` (load), `monitoring/`, `proxy/` (nginx). Backend settings are `backend/kernelCI/`; cache app is `backend/kernelCI_cache/`. App code and tests: `backend/kernelCI_app/`. UI: `dashboard/src/` (colocated `*.test.ts(x)`); Playwright: `dashboard/e2e/`.

## Commands (repo root)

- `make setup` — copy missing env templates, `pnpm` + Poetry install.
- `make dev` / `make dev-build` / `make dev-down` — Docker Compose via `docker-compose.dev.yml`.
- `make fix` — ESLint/Prettier (frontend) and Ruff fix/format (backend). Prefer this over hand-formatting.
- `make test` — frontend Vitest and **backend unit** (`pytest -m unit`). Not integration.
- `make build` — frontend production build (includes typecheck).
- `make ci` — lint + build + unit + Docker-backed integration (`docker-compose.test.yml`).

Caveats:

- `make check-lint` runs `pnpm lint-staged` on the frontend (staged files only), plus Ruff check/format on the backend. For a full frontend lint, `cd dashboard && pnpm lint`.
- Frontend package manager is **pnpm**. Backend is **Poetry** from `backend/`.
- Frontend-only: `pnpm dev` inside `dashboard/`. Backend needs Redis; see the backend README.
- Playwright: `pnpm e2e` in `dashboard/` with the app up; `PLAYWRIGHT_TEST_BASE_URL` as needed. Prefer `data-test-id` selectors.
- Without a local API, point `VITE_API_BASE_URL` at staging (`https://staging.dashboard.kernelci.org`).

## Running the app

Do not start a stack for logic-only work. Prefer `make test`, schema, and code. Full install/run details: [docs/dev-environment.md](docs/dev-environment.md).

Need a browser or a local API? Check terminals and ports first; reuse what is already up.

- **Full local stack:** `make setup` once if env files are missing, then `make dev` (Compose `--wait`). Docker needs an unsandboxed shell. First build is slow.
- **Frontend only:** `pnpm dev` in `dashboard/` with `VITE_API_BASE_URL=https://staging.dashboard.kernelci.org`.
- **URLs:** http://localhost:9000 (nginx, prod-like), http://localhost:5173 (Vite HMR), http://localhost:8000 (Django). Ready check: `curl` 9000 and `/api/schema/` on 8000.
- **UI changes:** exercise the flow in the browser (click, navigate, shared routes). A screenshot is not enough. Stop with `make dev-down` only if you started the stack.

## Local Postgres

Query via Compose, not host `psql` (avoids leaking `.env` into the chat):

```bash
docker compose -f docker-compose.dev.yml exec -T dashboard_db \
  psql -U "${DB_USER:-admin}" -d "${DB_NAME:-dashboard}" -c '…'
```

Docker socket needs an unsandboxed shell. Schema/meaning: [backend/docs/database-logic.md](backend/docs/database-logic.md) and `backend/kernelCI_app/models.py` (`db_table`). Prefer `reltuples` for size estimates; `COUNT(*)` is fine on `tests` (~1M). Do not write/DDL without asking.

Host clients (DBeaver, etc.): `docs/dev-environment.md` — hostname `dashboard_db` is in-network only; published port is `DB_PORT_PUBLISHED` (default 5434).

## Invariants

- **Shareable links.** UI state belongs in the URL (TanStack Router). File-based routes: only files whose names start with `~`.
- **Filters:** same category = OR, different categories = AND. A new filter needs backend `FilterParams` (plus summary/commitHistory, tests, schema) **and** frontend types, modal, `zFilter*` in `dashboard/src/types/general.ts`, `mapFilterToReq` (`dashboard/src/components/Tabs/Filters.tsx`), and the short name in `dashboard/src/utils/search.ts`. Listing `diffFilter` keys must still apply on details.
- Copy goes in `messages/index.ts`, not hardcoded in components.
- **Redis** for caching queries.

## Git

Conventional Commits with a scope, e.g. `fix(tree-compare): restore drawer navigation`. One concern per commit/PR. PR titles match; describe why, how, trade-offs, tests; link issues; screenshots/GIFs for UI. CI green before asking for review. Commit with "Signed-off-by".

Refer to related issues in commit footers, e.g. `Part of #issue-number` and `Closes #issue-number`.

Keep credentials, DB passwords, and webhook URLs out of commits. Use the supplied `.env.example` files.

## Pull requests quality

For any changes that affects the frontend, attach visual evidence to the pull requests via `gh pr comment --attach`. NEVER commit evidence files to the repository. 

Add clear and reproducible test instructions to the pull requests so the reviewers can test themselves and validate the implementation.

Describe in the pull request body what was changed, use the `unslop` skill to write. Add references to the related issues.

Prefer using git fixups when addressing something implemented in the same pull request. Push the fixups as is in order to make easier to another devs to review only what changed. The fixups should be squashed before merge.

