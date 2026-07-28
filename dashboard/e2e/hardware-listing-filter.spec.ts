import { test, expect, type Page } from '@playwright/test';

import { COMMON_SELECTORS, HARDWARE_LISTING_SELECTORS } from './e2e-selectors';

const FILTER_LOAD_TIMEOUT = 15000;

const openFilterDrawer = async (page: Page): Promise<void> => {
  await page.getByRole('button', { name: /filters/i }).click();
  await expect(
    page.locator(HARDWARE_LISTING_SELECTORS.filterSelector('checkoutOrigin')),
  ).toBeVisible({ timeout: FILTER_LOAD_TIMEOUT });
};

test.describe('Hardware Listing Filter Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/hardware');
    await expect(page.locator(HARDWARE_LISTING_SELECTORS.table)).toBeVisible({
      timeout: FILTER_LOAD_TIMEOUT,
    });
  });

  test('the five filters replace the omni origin selector', async ({
    page,
  }) => {
    await expect(page.locator(COMMON_SELECTORS.originDropdown)).toBeHidden();

    await openFilterDrawer(page);

    // KCI takes maestro checkouts and builds as the baseline, and leaves the test
    // side open until the user narrows it
    for (const [filter, value] of [
      ['checkoutOrigin', 'maestro'],
      ['buildOrigin', 'maestro'],
      ['buildLab', 'Any'],
      ['testOrigin', 'Any'],
      ['testLab', 'Any'],
    ] as const) {
      await expect(
        page.locator(HARDWARE_LISTING_SELECTORS.filterSelector(filter)),
      ).toContainText(value);
    }
  });

  test('picking a test lab narrows the listing to that lab', async ({
    page,
  }) => {
    await openFilterDrawer(page);

    const testLab = page.locator(
      HARDWARE_LISTING_SELECTORS.filterSelector('testLab'),
    );
    await testLab.click();

    const options = page
      .locator('[role="dialog"][data-state="open"]')
      .getByRole('option');
    await expect(options.first()).toBeVisible();

    const labCount = await options.count();
    test.skip(labCount < 2, 'Deployment has no test labs to filter by');

    // The first option is the "Any" choice
    const lab = options.nth(1);
    const labName = (await lab.textContent())?.trim() ?? '';
    await lab.click();
    await expect(testLab).toContainText(labName);

    await page.getByRole('button', { name: /^filter$/i }).click();

    await expect(page).toHaveURL(
      new RegExp(`[?&]tl=${encodeURIComponent(labName)}`),
    );
  });

  test('the filters survive a reload', async ({ page }) => {
    await page.goto('/hardware?tl=lava-collabora&to=maestro');
    await expect(page.locator(HARDWARE_LISTING_SELECTORS.table)).toBeVisible({
      timeout: FILTER_LOAD_TIMEOUT,
    });

    await openFilterDrawer(page);

    await expect(
      page.locator(HARDWARE_LISTING_SELECTORS.filterSelector('testLab')),
    ).toContainText('lava-collabora');
    await expect(
      page.locator(HARDWARE_LISTING_SELECTORS.filterSelector('testOrigin')),
    ).toContainText('maestro');
  });
});
