import { test, expect } from '@playwright/test';

import { TREE_LISTING_SELECTORS, COMMON_SELECTORS } from './e2e-selectors';

const PAGE_LOAD_TIMEOUT = 5000;
const DEFAULT_ACTION_TIMEOUT = 1000;
const SEARCH_UPDATE_TIMEOUT = 2000;
const NAVIGATION_TIMEOUT = 5000;
const GO_BACK_TIMEOUT = 3000;

test.describe('Tree Listing Page Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/tree');
    await page.waitForTimeout(PAGE_LOAD_TIMEOUT);
  });

  test('loads tree listing page correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/KernelCI/);
    await expect(page).toHaveURL(/\/tree/);

    await expect(page.locator(TREE_LISTING_SELECTORS.table)).toBeVisible();

    await expect(
      page.locator(TREE_LISTING_SELECTORS.treeColumnHeader),
    ).toBeVisible();
    await expect(
      page.locator(TREE_LISTING_SELECTORS.branchColumnHeader),
    ).toBeVisible();
  });

  test('change time interval', async ({ page }) => {
    await expect(page.locator(COMMON_SELECTORS.tableRow).first()).toBeVisible();

    const intervalInput = page
      .locator(TREE_LISTING_SELECTORS.intervalInput)
      .first();
    await expect(intervalInput).toBeVisible();

    await intervalInput.fill('14');

    await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);

    await expect(intervalInput).toHaveValue('14');
  });

  test('change table size', async ({ page }) => {
    await expect(page.locator(TREE_LISTING_SELECTORS.table)).toBeVisible();

    const tableSizeSelector = page.locator('[role="combobox"]').nth(1);
    await expect(tableSizeSelector).toBeVisible();

    await tableSizeSelector.click();

    await expect(
      page.locator(TREE_LISTING_SELECTORS.itemsPerPageDropdown),
    ).toBeVisible();

    await page.locator(TREE_LISTING_SELECTORS.itemsPerPageOption('20')).click();

    await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);

    await expect(tableSizeSelector).toContainText('20');
  });

  test('search for trees', async ({ page }) => {
    const searchInput = page.locator(TREE_LISTING_SELECTORS.searchInput).nth(0);
    await expect(searchInput).toBeVisible();
    await searchInput.fill('main');

    await page.waitForTimeout(SEARCH_UPDATE_TIMEOUT);

    const tableRows = page.locator(COMMON_SELECTORS.tableRow);
    const count = await tableRows.count();
    expect(count).toBeGreaterThan(1);
  });

  test('navigate to tree details and back via breadcrumb', async ({ page }) => {
    await expect(page.locator(TREE_LISTING_SELECTORS.table)).toBeVisible();

    const firstTreeLink = page.locator('td a').first();
    await expect(firstTreeLink).toBeVisible();

    await firstTreeLink.click();

    await page.waitForTimeout(NAVIGATION_TIMEOUT);

    const url = page.url();
    expect(url).toMatch(/\/tree\/[^/]+\/[^/]+\/[^/]+$/);

    const breadcrumbLink = page.locator(
      TREE_LISTING_SELECTORS.breadcrumbTreesLink,
    );
    await expect(breadcrumbLink).toBeVisible({ timeout: 15000 });
    await breadcrumbLink.click();
    await page.waitForTimeout(GO_BACK_TIMEOUT);

    await expect(page).toHaveURL(/\/tree$/);
  });

  test('pagination navigation', async ({ page }) => {
    await expect(page.locator(TREE_LISTING_SELECTORS.table)).toBeVisible();

    const nextPageButton = page
      .locator(TREE_LISTING_SELECTORS.nextPageButton)
      .first();
    const hasNextPage =
      (await nextPageButton.count()) > 0 &&
      !(await nextPageButton.isDisabled());

    if (hasNextPage) {
      const originalPageUrl = page.url();
      await nextPageButton.click();

      await page.waitForTimeout(SEARCH_UPDATE_TIMEOUT);

      const newPageUrl = page.url();
      expect(newPageUrl).not.toBe(originalPageUrl);
    }
  });

  test('change origin', async ({ page }) => {
    const testOrigin = 'linaro';

    await expect(page.locator(TREE_LISTING_SELECTORS.table)).toBeVisible();

    await expect(page.locator('text="Origin"')).toBeVisible();

    const originDropdown = page.locator(COMMON_SELECTORS.originDropdown);
    await expect(originDropdown).toBeVisible({ timeout: 15000 });

    await originDropdown.click();

    await expect(
      page.locator(COMMON_SELECTORS.originOption(testOrigin)),
    ).toBeVisible();

    await page.locator(COMMON_SELECTORS.originOption(testOrigin)).click();

    await page.waitForTimeout(SEARCH_UPDATE_TIMEOUT);

    await expect(originDropdown).toContainText(testOrigin);
  });
});
