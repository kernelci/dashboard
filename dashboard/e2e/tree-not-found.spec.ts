import { test, expect } from '@playwright/test';

test.use({ testIdAttribute: 'data-test-id' });

const hash = '29c6cdaac04a6989a7ed4ae4275ce4244e617f58';

const status = {
  PASS: 1,
  FAIL: 0,
  ERROR: 0,
  SKIP: 0,
  MISS: 0,
  DONE: 0,
  NULL: 0,
};
const builds = {
  status,
  origins: {},
  architectures: {},
  configs: {},
  labs: {},
  issues: [],
  unknown_issues: 0,
};
const tests = {
  ...builds,
  architectures: [],
  fail_reasons: {},
  failed_platforms: [],
};
const filters = { issues: [], origins: [], has_unknown_issue: false, labs: [] };
const summary = {
  common: {
    hardware: [],
    tree_url: 'https://example.org/linux.git',
    git_commit_tags: ['v6.1'],
  },
  summary: { builds, boots: tests, tests },
  filters: {
    all: { configs: [], architectures: [], compilers: [] },
    builds: filters,
    boots: filters,
    tests: filters,
  },
};

test('client navigation to a missing branch does not reuse valid checkout details', async ({
  page,
}) => {
  const invalidPath = `/tree/stable/linux-5.925.y/${hash}`;
  let releaseMissing: () => void = () => {};
  const missingResponse = new Promise<void>(resolve => {
    releaseMissing = resolve;
  });
  const requests: string[] = [];
  await page.route('**/api/tree/**', async route => {
    const path = new URL(route.request().url()).pathname;
    requests.push(path);
    if (path.includes('linux-5.925.y')) {
      await missingResponse;
      return route.fulfill({
        status: 404,
        json: { error: 'Branch not found', resource: 'branch' },
      });
    }
    return route.fulfill({
      json: path.endsWith('/summary') ? summary : { builds: [] },
    });
  });
  await page.goto(`/tree/stable/linux-6.1.y/${hash}`);
  await expect(
    page.getByText('Compare revisions', { exact: true }),
  ).toBeVisible();
  await page.evaluate(path => {
    // Exercise SPA navigation while retaining the mounted query observer and cache.
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  }, invalidPath);
  await expect
    .poll(() => requests.includes(`/api${invalidPath}/summary`))
    .toBe(true);
  await expect(
    page.getByText('Compare revisions', { exact: true }),
  ).toHaveCount(0);
  await expect(page.getByRole('tab')).toHaveCount(0);
  releaseMissing();
  await expect(
    page.getByRole('heading', { name: 'Branch not found' }),
  ).toBeVisible();
  expect(requests.filter(path => path.includes('linux-5.925.y'))).toEqual([
    `/api${invalidPath}/summary`,
  ]);
});

for (const resource of ['tree', 'branch', 'commit'] as const) {
  test(`missing ${resource} replaces details and stops dependent loading`, async ({
    page,
  }) => {
    const requests: string[] = [];
    await page.route('**/api/tree/**', async route => {
      const path = new URL(route.request().url()).pathname;
      requests.push(path);
      await route.fulfill({
        status: 404,
        json: { error: `${resource} not found`, resource },
      });
    });
    await page.goto(`/tree/stable/linux-5.925.y/${hash}?df%7Cbs%7CFAIL=true`);
    const error = page.getByTestId('tree-query-error');
    await expect(error.getByRole('heading')).toHaveText(
      `${resource.charAt(0).toUpperCase()}${resource.slice(1)} not found`,
    );
    await expect(page.getByText('Loading...', { exact: true })).toHaveCount(0);
    await expect(
      page.getByText('Compare revisions', { exact: true }),
    ).toHaveCount(0);
    await expect(page.getByRole('tab')).toHaveCount(0);
    expect(requests).toEqual([
      `/api/tree/stable/linux-5.925.y/${hash}/summary`,
    ]);
    await error.getByRole('link', { name: 'Back to Trees' }).click();
    await expect(page).toHaveURL(/\/tree(?:\?|$)/);
  });
}

test('existing checkout without results shows a settled empty state', async ({
  page,
}) => {
  await page.route('**/api/tree/**', route =>
    route.fulfill({
      json: { error: 'No results available for this tree/branch/commit' },
    }),
  );
  await page.goto(`/tree/stable/linux-6.1.y/${hash}`);
  await expect(page.getByTestId('tree-query-error')).toContainText(
    'No results available for this tree/branch/commit',
  );
  await expect(page.getByText('404', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Loading...', { exact: true })).toHaveCount(0);
});

test('unknown tree shortcut reports a missing tree', async ({ page }) => {
  await page.route('**/api/tree/unknown/master*', route =>
    route.fulfill({
      status: 404,
      json: { error: 'Tree not found', resource: 'tree' },
    }),
  );
  await page.goto('/tree/unknown/master');
  await expect(
    page.getByRole('heading', { name: 'Tree not found' }),
  ).toBeVisible();
  await expect(page.getByText('Loading...', { exact: true })).toHaveCount(0);
});
