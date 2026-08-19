import { expect, test } from '@playwright/test';

const FULL_HASH_LENGTH = 40;
const HASH_A = 'a'.repeat(FULL_HASH_LENGTH);
const HASH_B = 'b'.repeat(FULL_HASH_LENGTH);

test('loads revisions and comparison data from the API', async ({ page }) => {
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

  await page.goto(
    `/tree/linux/master/compare?hashA=${HASH_A}&hashB=${HASH_B}&origin=maestro`,
  );

  await expect(page.getByText('Tree summary')).toBeVisible();
  await expect(page.getByText('Changed results')).toBeVisible();
  await expect(page.getByText('defconfig+allmodconfig')).toBeVisible();
  await expect(page.getByText('Regression')).toBeVisible();
});
