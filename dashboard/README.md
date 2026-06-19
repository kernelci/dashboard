# Running in development

Install [pnpm](https://pnpm.io/installation), then from the `dashboard` directory:

```sh
cp .env.example .env   # set VITE_API_BASE_URL and other variables
pnpm install
pnpm dev
```

Set `VITE_API_BASE_URL=http://localhost:8000` when the backend runs on the host. With [dev-environment.md](../docs/dev-environment.md) (`docker-compose.dev.yml`), use the proxy at `http://localhost:9000` or Vite directly at `http://localhost:5173`.

## Running unit tests

```sh
pnpm test
```

## Running end-to-end (e2e) tests

Set `PLAYWRIGHT_TEST_BASE_URL` in `.env` (defaults to staging). Install browsers once with `pnpm exec playwright install`, then:

```sh
pnpm run e2e        # all tests
pnpm run e2e-ui     # UI mode for debugging
```

Available base URLs: staging (`https://staging.dashboard.kernelci.org`), production (`https://dashboard.kernelci.org`), local Vite (`http://localhost:5173`), local proxy (`http://localhost:9000`).

## E2E Test Selectors

To avoid complex css selectors, you can add a data-test-id attribute to elements that you want to target in your e2e tests. That way you don't need to fight with complex selectors.

# Routing and State Management

A big part of this project is to have shareable links
So we should use the URL to manage state as much as possible.

Also, we are using file based routing in the tanstack router, only files that starts with ~ are read by the Vite plugin.

# Feature Flags

They are used when we want to hide a feature for some users, without having to do branch manipulation.

Available feature flags:

- `VITE_FEATURE_FLAG_SHOW_DEV` - Controls visibility of dev-only features (boolean, default: `false`)
