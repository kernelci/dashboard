# Running in development

- Install the packager manager [pnpm](https://pnpm.io/installation)

- Install all dependencies with:

```sh
pnpm install
```

Create a .env.development file (Do not forget to check and set the variables and their values)

```sh
 cp .env.example .env.development
```

After establishing the connection with Google Cloud and running `backend`, run the `dashboard` dev server with

```sh
pnpm dev
```

## Running unit tests

The frontend includes unit tests covering some parts of the source code. To run the tests, use the following command:

```sh
pnpm test
```

## Running end-to-end (e2e) tests

The project includes Playwright-based end-to-end tests. To run the tests, first set the test environment URL in your .env file:

```sh
# Copy the example file
cp .env.example .env

# Edit the .env file to set PLAYWRIGHT_TEST_BASE_URL to your desired environment
# Available environments:
# - Staging: https://staging.dashboard.kernelci.org:9000 (default)
# - Production: https://dashboard.kernelci.org
# - Local: http://localhost:5173

# Install Playwright browsers if you don't have them yet
pnpm exec playwright install
```

Then run the e2e tests:

```sh
# Run all e2e tests
pnpm run e2e

# Run e2e tests with UI mode for debugging
pnpm run e2e-ui
```

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
- `VITE_FEATURE_FLAG_TREE_LISTING_VERSION` - Controls which tree listing version to display. Set to `"v1"` for the old version or `"v2"` for the new version (string, default: `"v1"`)
- `VITE_FEATURE_FLAG_HARDWARE_LISTING_VERSION` - Controls which hardware listing version to display. Set to `"v1"` for the old version or `"v2"` for the new version (string, default: `"v1"`)
