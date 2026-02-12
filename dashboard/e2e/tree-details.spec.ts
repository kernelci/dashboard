import { test, expect } from '@playwright/test';

import { TREE_DETAILS_SELECTORS, TREE_LISTING_SELECTORS } from './selectors';
import {
  navigateAndWait,
  navigateBackViaBreadcrumb,
  clickAndVerifyNavigation,
  withFilterDrawer,
} from './utils';

const EXPAND_ROW_TIMEOUT = 3000;
const GRAPH_RENDER_TIMEOUT = 2000;
const CLEAR_FILTER_TIMEOUT = 1000;

test.describe('Tree Details Page Tests', () => {
  const TREE_URL =
    'tree/android/android-mainline/7c5912a7c78d669e825093b8cbb57e6afaa88d11';

  test.beforeEach(async ({ page }) => {
    const timeout = 60000;
    page.setDefaultTimeout(timeout);
  });

  test('adds filters via filter drawer and applies them', async ({ page }) => {
    await navigateAndWait(page, TREE_URL);

    // Open filter drawer
    const filterButton = page.locator(TREE_DETAILS_SELECTORS.filters.button);
    await expect(filterButton).toBeVisible({ timeout: 30000 });
    await filterButton.click();

    // Wait for drawer to be visible
    const drawerContent = page.locator(
      TREE_DETAILS_SELECTORS.filters.drawerContent,
    );
    await expect(drawerContent).toBeVisible();

    // Select FAIL filter in Build Status (first FAIL label in the page)
    const failCheckbox = page.locator('label:has-text("FAIL")').first();
    await expect(failCheckbox).toBeVisible();
    await failCheckbox.click();

    // Apply filter by clicking Filter button
    const applyFilterButton = page.locator(
      TREE_DETAILS_SELECTORS.filters.filterButton,
    );
    await expect(applyFilterButton).toBeVisible();
    await applyFilterButton.click();

    // Wait for drawer to close
    await expect(drawerContent).not.toBeVisible();

    // Verify URL contains filter parameter
    await expect(page).toHaveURL(/df.*FAIL/);

    // Verify filter was applied by checking if build table shows filtered results
    await page.waitForLoadState('domcontentloaded');

    // Open filter drawer again to clear filters
    await filterButton.click();
    await expect(drawerContent).toBeVisible();

    // Clear all filters if available
    const clearAllButton = page.locator(
      TREE_DETAILS_SELECTORS.filters.clearAllFilters,
    );
    const hasClearAllButton = (await clearAllButton.count()) > 0;

    if (hasClearAllButton) {
      await clearAllButton.click();
      await page.waitForTimeout(CLEAR_FILTER_TIMEOUT);
    }

    // Close drawer
    const cancelButton = page.locator(
      TREE_DETAILS_SELECTORS.filters.cancelButton,
    );
    await cancelButton.click();
    await expect(drawerContent).not.toBeVisible();
  });

  test('clicks on details button on build table and goes back via breadcrumb', async ({
    page,
  }) => {
    await navigateAndWait(page, TREE_URL);

    const detailsButton = page
      .locator(TREE_DETAILS_SELECTORS.buildTable.detailsButton)
      .first();
    await expect(detailsButton).toBeVisible({ timeout: 30000 });

    await clickAndVerifyNavigation(detailsButton, /\/build\//);

    await navigateBackViaBreadcrumb(
      page,
      TREE_DETAILS_SELECTORS.breadcrumbTreesLink,
    );
  });

  test('clicks on an issue details button on issue card and goes back via breadcrumb', async ({
    page,
  }) => {
    await navigateAndWait(page, TREE_URL);

    const issuesCardButton = page.locator(
      TREE_DETAILS_SELECTORS.issuesCard.button,
    );
    const hasIssues = (await issuesCardButton.count()) > 0;

    if (hasIssues) {
      await expect(issuesCardButton).toBeVisible();

      await clickAndVerifyNavigation(issuesCardButton, /\/issues\//);

      await navigateBackViaBreadcrumb(
        page,
        TREE_DETAILS_SELECTORS.breadcrumbTreesLink,
      );
    }
  });

  test('selects other tabs', async ({ page }) => {
    await navigateAndWait(page, TREE_URL);

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
    await navigateAndWait(page, TREE_URL);

    const testsTab = page.locator(TREE_DETAILS_SELECTORS.tabs.tests);
    await expect(testsTab).toBeVisible();
    await testsTab.click();

    await page.waitForLoadState('domcontentloaded');

    const testItems = page.locator(TREE_DETAILS_SELECTORS.testsTable.testItem);
    const hasTestItems = (await testItems.count()) > 0;

    if (hasTestItems) {
      const firstTestItem = testItems.first();
      await firstTestItem.click();

      await page.waitForTimeout(EXPAND_ROW_TIMEOUT);

      const expandedRows = page.locator(
        TREE_DETAILS_SELECTORS.testsTable.expandedRows,
      );
      const hasExpandedRows = (await expandedRows.count()) > 0;

      if (hasExpandedRows) {
        const detailsButton = page
          .locator(TREE_DETAILS_SELECTORS.testsTable.detailsButton)
          .first();
        await expect(detailsButton).toBeVisible({ timeout: 10000 });

        await clickAndVerifyNavigation(detailsButton, /\/test\//);

        await navigateBackViaBreadcrumb(
          page,
          TREE_DETAILS_SELECTORS.breadcrumbTreesLink,
        );
      }
    }
  });

  test('full workflow: navigate to tree details and back via breadcrumb', async ({
    page,
  }) => {
    await navigateAndWait(page, '/tree');

    await expect(page).toHaveURL(/\/tree$/);

    const firstTreeLink = page
      .locator(TREE_LISTING_SELECTORS.firstTreeCell)
      .first();
    await expect(firstTreeLink).toBeVisible();

    await clickAndVerifyNavigation(
      firstTreeLink,
      /\/tree\/[^/]+\/[^/]+\/[^/]+$/,
    );

    await navigateBackViaBreadcrumb(
      page,
      TREE_DETAILS_SELECTORS.breadcrumbTreesLink,
    );
  });

  test('build table status filters work correctly', async ({ page }) => {
    await navigateAndWait(page, TREE_URL);

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
    await navigateAndWait(page, TREE_URL);

    const searchInput = page.locator(
      TREE_DETAILS_SELECTORS.buildTable.searchInput,
    );
    await expect(searchInput).toBeVisible({ timeout: 30000 });

    await searchInput.fill('defconfig');

    await expect(searchInput).toHaveValue('defconfig');
  });

  test('navigates back one commit via commit graph', async ({ page }) => {
    await navigateAndWait(page, TREE_URL);

    const currentUrl = page.url();

    // Wait for a visible commit graph (there may be multiple, get the last visible one)
    const commitGraphContainer = page
      .locator(TREE_DETAILS_SELECTORS.commitGraph.container)
      .last();
    await expect(commitGraphContainer).toBeVisible({ timeout: 30000 });

    // Wait a bit for the graph to fully render
    await page.waitForTimeout(GRAPH_RENDER_TIMEOUT);

    // Look for clickable marks in the visible graph
    const marks = commitGraphContainer.locator('[class*="MuiMarkElement"]');
    const markCount = await marks.count();

    // Ensure we actually have marks to click
    expect(markCount).toBeGreaterThan(0);

    // Click on the first mark (data point in the commit history)
    await marks.first().click({ force: true });

    // Wait for navigation to complete
    await page.waitForTimeout(GRAPH_RENDER_TIMEOUT);

    const newUrl = page.url();

    // Verify URL changed (navigated to a different commit)
    expect(newUrl).not.toBe(currentUrl);
    expect(newUrl).toMatch(/\/tree\//);
  });

  test('adds filter via summary card and verifies URL change', async ({
    page,
  }) => {
    await navigateAndWait(page, TREE_URL);

    // Wait for summary cards to load
    await page.waitForLoadState('domcontentloaded');

    // Find and click on an arch filter link (e.g., arm64)
    const arm64Link = page.locator('a:has-text("arm64")').first();
    const hasArm64Link = (await arm64Link.count()) > 0;

    if (hasArm64Link) {
      await expect(arm64Link).toBeVisible({ timeout: 30000 });

      // Get current URL before clicking
      const urlBefore = page.url();

      // Click the link
      await arm64Link.click();

      // Wait for navigation
      await page.waitForLoadState('domcontentloaded');

      // Verify URL changed and contains filter parameter
      const urlAfter = page.url();
      expect(urlAfter).not.toBe(urlBefore);
      expect(urlAfter).toMatch(/df.*arm64/);
    }
  });

  test('clears all filters', async ({ page }) => {
    await navigateAndWait(page, TREE_URL);

    await withFilterDrawer(
      page,
      TREE_DETAILS_SELECTORS.filters.button,
      TREE_DETAILS_SELECTORS.filters.cancelButton,
      TREE_DETAILS_SELECTORS.filters.drawerContent,
      async () => {
        // Check if "Clear all" button exists and click it
        const clearAllButton = page.locator(
          TREE_DETAILS_SELECTORS.filters.clearAllFilters,
        );
        const hasClearAllButton = (await clearAllButton.count()) > 0;

        if (hasClearAllButton) {
          await clearAllButton.click();
          await page.waitForTimeout(CLEAR_FILTER_TIMEOUT);
        }
      },
    );
  });
});
