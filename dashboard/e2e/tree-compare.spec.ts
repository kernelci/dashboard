import { expect, test } from '@playwright/test';

const FULL_HASH_LENGTH = 40;
const HASH_A = 'a'.repeat(FULL_HASH_LENGTH);
const HASH_B = 'b'.repeat(FULL_HASH_LENGTH);

test('loads comparison data and opens a side-by-side details drawer', async ({
  page,
}) => {
  await page.route('**/api/tree/linux/master/commits?**', route =>
    route.fulfill({
      json: [
        {
          git_commit_hash: HASH_A,
          last_checkout: '2026-07-14T10:00:00Z',
        },
        {
          git_commit_hash: HASH_B,
          last_checkout: '2026-07-13T10:00:00Z',
        },
      ],
    }),
  );

  await page.route('**/api/tree/linux/master/compare/builds?**', route =>
    route.fulfill({
      json: [
        {
          config_name: 'defconfig+allmodconfig',
          architecture: 'arm64',
          compiler: 'clang-17',
          status_a: 'PASS',
          status_b: 'FAIL',
          id_a: 'build-a',
          id_b: 'build-b',
        },
      ],
    }),
  );

  await page.route('**/api/tree/linux/master/compare/boots?**', route =>
    route.fulfill({ json: [] }),
  );

  await page.route('**/api/tree/linux/master/compare/tests?**', route =>
    route.fulfill({
      json: [
        {
          path: 'kselftest.sgx',
          config_name: 'defconfig-a',
          architecture: 'x86_64',
          platform: 'kubernetes',
          status_a: 'PASS',
          status_b: 'FAIL',
        },
      ],
    }),
  );

  await page.route('**/api/tree/linux/master/compare?**', route =>
    route.fulfill({
      json: {
        treeName: 'linux',
        branch: 'master',
        gitUrl: 'https://git.kernel.org/linux.git',
        summary: {
          builds: {
            sideA: { pass: 42, fail: 1, inconclusive: 0 },
            sideB: { pass: 40, fail: 3, inconclusive: 0 },
            delta: { pass: -2, fail: 2 },
            changes: {
              regression: 2,
              fixed: 0,
              newFailure: 0,
              stillFailing: 0,
              newPass: 0,
            },
          },
          boots: {
            sideA: { pass: 20, fail: 0, inconclusive: 1 },
            sideB: { pass: 18, fail: 2, inconclusive: 1 },
            delta: { pass: -2, fail: 2 },
            changes: {
              regression: 2,
              fixed: 0,
              newFailure: 0,
              stillFailing: 0,
              newPass: 0,
            },
          },
          tests: {
            sideA: { pass: 100, fail: 5, inconclusive: 2 },
            sideB: { pass: 95, fail: 10, inconclusive: 2 },
            delta: { pass: -5, fail: 5 },
            changes: {
              regression: 5,
              fixed: 0,
              newFailure: 0,
              stillFailing: 0,
              newPass: 0,
            },
          },
        },
      },
    }),
  );

  await page.route('**/api/build/build-a**', route =>
    route.fulfill({
      json: {
        id: 'build-a',
        status: 'PASS',
        build_origin: 'maestro',
        timestamp: '2026-07-14T10:00:00Z',
        log_excerpt: 'side A build log',
        architecture: 'arm64',
        git_commit_hash: HASH_A,
        tree_name: 'linux',
        git_repository_branch: 'master',
      },
    }),
  );

  await page.route('**/api/build/build-b**', route =>
    route.fulfill({
      json: {
        id: 'build-b',
        status: 'FAIL',
        build_origin: 'maestro',
        timestamp: '2026-07-13T10:00:00Z',
        log_excerpt: 'side B build log',
        architecture: 'arm64',
        git_commit_hash: HASH_B,
        tree_name: 'linux',
        git_repository_branch: 'master',
      },
    }),
  );

  await page.goto(
    `/tree/linux/master/compare?hashA=${HASH_A}&hashB=${HASH_B}&origin=maestro`,
  );

  await expect(page.getByText('Tree summary')).toBeVisible();
  await expect(page.getByText('Changed results')).toBeVisible();
  await expect(page.getByRole('combobox', { name: 'From' })).toBeVisible();
  await expect(page.getByRole('combobox', { name: 'To' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Regressions' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add' })).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Remove PASS to FAIL filter' }),
  ).toBeVisible();
  await expect(page.getByText('defconfig+allmodconfig')).toBeVisible();
  await expect(page.getByText('Regression', { exact: true })).toBeVisible();

  await expect(
    page.getByRole('button', { name: 'CLI command' }),
  ).toBeInViewport();
  await page.getByRole('button', { name: 'CLI command' }).click();
  const command = page.getByLabel('Tree comparison: Human-readable', {
    exact: true,
  });
  await expect(command).toContainText('--giturl');
  await expect(command).not.toContainText('--git-url');
  await expect(command).toContainText('--origin maestro');
  await expect(command).toContainText('--branch master');
  await expect(command).toContainText(`${HASH_A} ${HASH_B}`);

  await page.getByRole('tab', { name: /Tests/i }).click();
  await expect(
    page.getByRole('columnheader', { name: 'Config' }),
  ).toBeVisible();
  await expect(page.getByText('kselftest.sgx')).toBeVisible();
  await expect(page.getByText('defconfig-a')).toBeVisible();

  await page.getByRole('tab', { name: /Builds/i }).click();
  await page.getByText('defconfig+allmodconfig').click();

  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByText('Log Viewer')).toBeVisible();
  await expect(page.getByText('side A build log')).toBeVisible();
  await expect(page.getByText('side B build log')).toBeVisible();
});

test('drawer next stays on searched rows', async ({ page }) => {
  await page.route('**/api/tree/linux/master/commits?**', route =>
    route.fulfill({
      json: [
        {
          git_commit_hash: HASH_A,
          last_checkout: '2026-07-14T10:00:00Z',
        },
        {
          git_commit_hash: HASH_B,
          last_checkout: '2026-07-13T10:00:00Z',
        },
      ],
    }),
  );

  await page.route('**/api/tree/linux/master/compare/builds?**', route =>
    route.fulfill({
      json: [
        {
          config_name: 'keep-one',
          architecture: 'arm64',
          compiler: 'gcc',
          status_a: 'PASS',
          status_b: 'FAIL',
          id_a: 'build-keep-a',
          id_b: 'build-keep-b',
        },
        {
          config_name: 'hidden-row',
          architecture: 'arm64',
          compiler: 'gcc',
          status_a: 'PASS',
          status_b: 'FAIL',
          id_a: 'build-hidden-a',
          id_b: 'build-hidden-b',
        },
        {
          config_name: 'keep-two',
          architecture: 'arm64',
          compiler: 'gcc',
          status_a: 'PASS',
          status_b: 'FAIL',
          id_a: 'build-keep2-a',
          id_b: 'build-keep2-b',
        },
      ],
    }),
  );

  await page.route('**/api/tree/linux/master/compare/boots?**', route =>
    route.fulfill({ json: [] }),
  );
  await page.route('**/api/tree/linux/master/compare/tests?**', route =>
    route.fulfill({ json: [] }),
  );
  await page.route('**/api/tree/linux/master/compare?**', route =>
    route.fulfill({
      json: {
        treeName: 'linux',
        branch: 'master',
        gitUrl: 'https://git.kernel.org/linux.git',
        summary: {
          builds: {
            sideA: { pass: 1, fail: 0, inconclusive: 0 },
            sideB: { pass: 0, fail: 1, inconclusive: 0 },
            delta: { pass: -1, fail: 1 },
            changes: {
              regression: 3,
              fixed: 0,
              newFailure: 0,
              stillFailing: 0,
              newPass: 0,
            },
          },
          boots: {
            sideA: { pass: 0, fail: 0, inconclusive: 0 },
            sideB: { pass: 0, fail: 0, inconclusive: 0 },
            delta: { pass: 0, fail: 0 },
            changes: {
              regression: 0,
              fixed: 0,
              newFailure: 0,
              stillFailing: 0,
              newPass: 0,
            },
          },
          tests: {
            sideA: { pass: 0, fail: 0, inconclusive: 0 },
            sideB: { pass: 0, fail: 0, inconclusive: 0 },
            delta: { pass: 0, fail: 0 },
            changes: {
              regression: 0,
              fixed: 0,
              newFailure: 0,
              stillFailing: 0,
              newPass: 0,
            },
          },
        },
      },
    }),
  );

  await page.route('**/api/build/**', route =>
    route.fulfill({
      json: {
        id: 'build',
        status: 'FAIL',
        log_excerpt: 'log',
        architecture: 'arm64',
        git_commit_hash: HASH_A,
        tree_name: 'linux',
        git_repository_branch: 'master',
      },
    }),
  );

  await page.goto(
    `/tree/linux/master/compare?hashA=${HASH_A}&hashB=${HASH_B}&origin=maestro`,
  );

  await page.getByPlaceholder('Search').fill('keep-');
  await expect(page.getByText('hidden-row')).toHaveCount(0);
  await page.getByText('keep-one').click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.getByRole('button', { name: 'Next' }).click();
  await expect(page.getByRole('dialog').getByText('keep-two')).toBeVisible();
  await expect(page.getByRole('dialog').getByText('hidden-row')).toHaveCount(0);
});
