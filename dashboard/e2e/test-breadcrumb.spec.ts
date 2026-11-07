import { expect, test } from '@playwright/test';

const FULL_HASH_LENGTH = 40;
const hash = 'a'.repeat(FULL_HASH_LENGTH);
const testDetails = {
  id: 'breadcrumb-test',
  build_id: 'breadcrumb-build',
  path: 'boot',
  status: 'PASS',
  field_timestamp: '2026-07-16T17:00:00Z',
  start_time: '2026-07-16T17:00:00Z',
  tree_name: 'linux',
  git_repository_branch: 'master',
  git_repository_url: 'https://git.kernel.org/linux.git',
  git_commit_hash: hash,
  origin: 'ti',
  test_origin: 'different-test-origin',
};

test.beforeEach(async ({ page }) => {
  await page.route(
    url => url.pathname.startsWith('/api/'),
    route =>
      route.fulfill({
        status: 404,
        json: { error: 'Not in this test fixture' },
      }),
  );
  await page.route('**/api/test/breadcrumb-test', route =>
    route.fulfill({ json: testDetails }),
  );
  await page.route('**/api/test/breadcrumb-test/issues', route =>
    route.fulfill({ json: [] }),
  );
});

test('direct links show Trees breadcrumbs and navigate with the checkout origin', async ({
  page,
}) => {
  await page.addInitScript(() => {
    localStorage.setItem(
      'previousSearchParams',
      JSON.stringify({
        state: { previousSearch: { origin: 'stale-origin' } },
        version: 0,
      }),
    );
  });
  await page.goto('/test/breadcrumb-test');
  const breadcrumb = page.getByRole('navigation', { name: 'breadcrumb' });
  await expect(breadcrumb).toHaveText('TreesTrees DetailsTest Details');
  await page.reload();
  await expect(breadcrumb).toHaveText('TreesTrees DetailsTest Details');

  const request = page.waitForRequest(
    req =>
      new URL(req.url()).pathname === `/api/tree/linux/master/${hash}/summary`,
  );
  await breadcrumb
    .getByRole('link', { name: 'Trees Details', exact: true })
    .click();
  expect(new URL((await request).url()).searchParams.get('origin')).toBe('ti');
  await expect(page).toHaveURL(new RegExp(`/tree/linux/master/${hash}\\?`));

  await page.goBack();
  await expect(breadcrumb).toHaveText('TreesTrees DetailsTest Details');
  await breadcrumb.getByRole('link', { name: 'Trees', exact: true }).click();
  await expect(page).toHaveURL(
    url => url.pathname === '/tree' && url.searchParams.get('o') === 'ti',
  );
});

test('a commit without a tree name uses the hash route', async ({ page }) => {
  await page.route('**/api/test/breadcrumb-test', route =>
    route.fulfill({ json: { ...testDetails, tree_name: null } }),
  );
  await page.goto('/test/breadcrumb-test');
  const breadcrumb = page.getByRole('navigation', { name: 'breadcrumb' });
  const request = page.waitForRequest(
    req => new URL(req.url()).pathname === `/api/tree/${hash}/summary`,
  );
  await breadcrumb
    .getByRole('link', { name: 'Trees Details', exact: true })
    .click();
  const url = new URL((await request).url());
  expect(url.searchParams.get('origin')).toBe('ti');
  expect(url.searchParams.get('git_branch')).toBe('master');
  expect(url.searchParams.get('git_url')).toBe(testDetails.git_repository_url);
});

test('missing commit metadata does not create a broken details link', async ({
  page,
}) => {
  await page.route('**/api/test/breadcrumb-test', route =>
    route.fulfill({ json: { ...testDetails, git_commit_hash: null } }),
  );
  await page.goto('/test/breadcrumb-test');
  const breadcrumb = page.getByRole('navigation', { name: 'breadcrumb' });
  await expect(breadcrumb).toHaveText('TreesTrees DetailsTest Details');
  await expect(
    breadcrumb.getByRole('link', { name: 'Trees Details', exact: true }),
  ).toHaveCount(0);
  await expect(
    breadcrumb.getByRole('link', { name: 'Trees', exact: true }),
  ).toBeVisible();
});

for (const context of [
  { path: '/hardware/board-a', label: 'Hardware Details' },
  { path: `/tree/${'b'.repeat(FULL_HASH_LENGTH)}`, label: 'Trees Details' },
]) {
  test(`preserves existing ${context.label} context but supplies a fallback when shared`, async ({
    page,
    context: browserContext,
  }) => {
    await page.goto(`${context.path}/test/breadcrumb-test`);
    const breadcrumb = page.getByRole('navigation', { name: 'breadcrumb' });
    await expect(
      breadcrumb.getByRole('link', { name: context.label, exact: true }),
    ).toHaveAttribute('href', context.path);
    await expect(page).toHaveURL(
      url => url.pathname === '/test/breadcrumb-test',
    );

    const sharedPage = await browserContext.newPage();
    await sharedPage.route('**/api/test/breadcrumb-test', route =>
      route.fulfill({ json: testDetails }),
    );
    await sharedPage.route('**/api/test/breadcrumb-test/issues', route =>
      route.fulfill({ json: [] }),
    );
    await sharedPage.goto(page.url());
    const sharedBreadcrumb = sharedPage.getByRole('navigation', {
      name: 'breadcrumb',
    });
    await expect(sharedBreadcrumb).toHaveText('TreesTrees DetailsTest Details');
    await expect(
      sharedBreadcrumb.getByRole('link', {
        name: 'Trees Details',
        exact: true,
      }),
    ).toHaveAttribute('href', new RegExp(`/tree/linux/master/${hash}\\?`));
  });
}
