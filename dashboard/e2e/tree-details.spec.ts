import { test, expect } from '@playwright/test';

import { TREE_DETAILS_SELECTORS, TREE_LISTING_SELECTORS } from './selectors';

test.describe('Tree Details Page Tests', () => {
  test.beforeEach(async ({ page }) => {
    const timeout = 60000;
    page.setDefaultTimeout(timeout);
  });

  test('opens and closes filter drawer', async ({ page }) => {
    await page.goto(
      '/tree/mainline/master/c072629f05d7bca1148ab17690d7922a31423984',
      { timeout: 30000 },
    );
    await page.waitForLoadState('domcontentloaded');

    const filterButton = page.locator(TREE_DETAILS_SELECTORS.filters.button);
    await filterButton.waitFor({ state: 'visible', timeout: 10000 });
    await filterButton.click();

    const cancelButton = page.locator(
      TREE_DETAILS_SELECTORS.filters.cancelButton,
    );
    await expect(cancelButton).toBeVisible();
    await cancelButton.click();

    await expect(cancelButton).not.toBeVisible();
  });

  test('clicks on details button on build table and goes back via breadcrumb', async ({
    page,
  }) => {
    await page.goto(
      '/tree/mainline/master/c072629f05d7bca1148ab17690d7922a31423984',
      { timeout: 30000 },
    );
    await page.waitForLoadState('domcontentloaded');

    const detailsButton = page
      .locator(TREE_DETAILS_SELECTORS.buildTable.detailsButton)
      .first();
    await expect(detailsButton).toBeVisible({ timeout: 30000 });

    await detailsButton.click();

    await page.waitForURL(/\/build\//, { timeout: 30000 });

    const url = page.url();
    expect(url).toMatch(/\/build\//);

    const breadcrumbLink = page.locator(
      TREE_DETAILS_SELECTORS.breadcrumbTreesLink,
    );
    await expect(breadcrumbLink).toBeVisible();
    await breadcrumbLink.click();

    await page.waitForURL(/\/tree/, { timeout: 20000 });
    await expect(page).toHaveURL(/\/tree/);
  });

  test('clicks on an issue details button on issue card and goes back via breadcrumb', async ({
    page,
  }) => {
    await page.goto(
      '/tree/mainline/master/c072629f05d7bca1148ab17690d7922a31423984',
      { timeout: 30000 },
    );
    await page.waitForLoadState('domcontentloaded');

    const issuesCardButton = page.locator(
      TREE_DETAILS_SELECTORS.issuesCard.button,
    );
    const hasIssues = (await issuesCardButton.count()) > 0;

    if (hasIssues) {
      await expect(issuesCardButton).toBeVisible();

      await issuesCardButton.click();

      await page.waitForURL(/\/issues\//, { timeout: 20000 });

      const url = page.url();
      expect(url).toMatch(/\/issues\//);

      const breadcrumbLink = page.locator(
        TREE_DETAILS_SELECTORS.breadcrumbTreesLink,
      );
      await expect(breadcrumbLink).toBeVisible();
      await breadcrumbLink.click();

      await page.waitForURL(/\/tree/, { timeout: 20000 });
      await expect(page).toHaveURL(/\/tree/);
    }
  });

  test('selects other tabs', async ({ page }) => {
    await page.goto(
      '/tree/mainline/master/c072629f05d7bca1148ab17690d7922a31423984',
      { timeout: 30000 },
    );
    await page.waitForLoadState('domcontentloaded');

    const bootsTab = page.locator(TREE_DETAILS_SELECTORS.tabs.boots);
    await expect(bootsTab).toBeVisible();

    await bootsTab.click();
    await expect(bootsTab).toHaveAttribute('data-state', 'active');

    const testsTab = page.locator(TREE_DETAILS_SELECTORS.tabs.tests);
    await expect(testsTab).toBeVisible();

    await testsTab.click();
    await expect(testsTab).toHaveAttribute('data-state', 'active');

    const buildsTab = page.locator(TREE_DETAILS_SELECTORS.tabs.builds);
    await buildsTab.click();
    await expect(buildsTab).toHaveAttribute('data-state', 'active');
  });

  test('clicks on a test item and clicks on detail button for test item', async ({
    page,
  }) => {
    await page.goto(
      '/tree/mainline/master/c072629f05d7bca1148ab17690d7922a31423984',
      { timeout: 30000 },
    );
    await page.waitForLoadState('domcontentloaded');

    const testsTab = page.locator(TREE_DETAILS_SELECTORS.tabs.tests);
    await expect(testsTab).toBeVisible();
    await testsTab.click();

    await page.waitForLoadState('domcontentloaded');

    const testItems = page.locator(TREE_DETAILS_SELECTORS.testsTable.testItem);
    const hasTestItems = (await testItems.count()) > 0;

    if (hasTestItems) {
      const firstTestItem = testItems.first();
      await firstTestItem.click();

      await page.waitForTimeout(3000);

      const expandedRows = page.locator('tr:has(td[colspan])');
      const hasExpandedRows = (await expandedRows.count()) > 0;

      if (hasExpandedRows) {
        const detailsButton = page
          .locator(TREE_DETAILS_SELECTORS.testsTable.detailsButton)
          .first();
        await expect(detailsButton).toBeVisible({ timeout: 10000 });

        await detailsButton.click();

        await page.waitForURL(/\/test\//, { timeout: 30000 });

        const url = page.url();
        expect(url).toMatch(/\/test\//);

        const breadcrumbLink = page.locator(
          TREE_DETAILS_SELECTORS.breadcrumbTreesLink,
        );
        await expect(breadcrumbLink).toBeVisible();
        await breadcrumbLink.click();

        await page.waitForURL(/\/tree/, { timeout: 20000 });
        await expect(page).toHaveURL(/\/tree/);
      }
    }
  });

  test('full workflow: navigate to tree details and back via breadcrumb', async ({
    page,
  }) => {
    await page.goto('/tree', { timeout: 30000 });
    await page.waitForLoadState('domcontentloaded');

    await expect(page).toHaveURL(/\/tree$/);

    const firstTreeLink = page
      .locator(TREE_LISTING_SELECTORS.firstTreeCell)
      .first();
    await expect(firstTreeLink).toBeVisible();

    await firstTreeLink.click();

    await page.waitForURL(/\/tree\/[^/]+\/[^/]+\/[^/]+$/, { timeout: 30000 });

    const url = page.url();
    expect(url).toMatch(/\/tree\/[^/]+\/[^/]+\/[^/]+$/);

    const breadcrumbLink = page.locator(
      TREE_DETAILS_SELECTORS.breadcrumbTreesLink,
    );
    await expect(breadcrumbLink).toBeVisible();
    await breadcrumbLink.click();

    await page.waitForURL(/\/tree/, { timeout: 20000 });
    await expect(page).toHaveURL(/\/tree/);
  });

  test('build table status filters work correctly', async ({ page }) => {
    await page.goto(
      '/tree/mainline/master/c072629f05d7bca1148ab17690d7922a31423984',
      { timeout: 30000 },
    );
    await page.waitForLoadState('domcontentloaded');

    const allFilter = page.locator(
      TREE_DETAILS_SELECTORS.buildTable.statusFilters.all,
    );
    await expect(allFilter).toBeVisible({ timeout: 30000 });

    const successFilter = page.locator(
      TREE_DETAILS_SELECTORS.buildTable.statusFilters.success,
    );
    await expect(successFilter).toBeVisible();

    await successFilter.click();

    await allFilter.click();
  });

  test('search input is visible and functional', async ({ page }) => {
    await page.goto(
      '/tree/mainline/master/c072629f05d7bca1148ab17690d7922a31423984',
      { timeout: 30000 },
    );
    await page.waitForLoadState('domcontentloaded');

    const searchInput = page.locator(
      TREE_DETAILS_SELECTORS.buildTable.searchInput,
    );
    await expect(searchInput).toBeVisible({ timeout: 30000 });

    await searchInput.fill('defconfig');

    await expect(searchInput).toHaveValue('defconfig');
  });
});
