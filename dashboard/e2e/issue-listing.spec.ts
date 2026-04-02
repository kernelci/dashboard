import { test, expect } from '@playwright/test';

import { ISSUE_LISTING_SELECTORS, COMMON_SELECTORS } from './e2e-selectors';

const PAGE_LOAD_TIMEOUT = 5000;
const DEFAULT_ACTION_TIMEOUT = 1000;
const SECONDS_IN_DAY = 86400;
const MILLISECONDS_IN_SECOND = 1000;
const THREE_DAYS = 3;
const TWO_DAYS = 2;
const ONE_DAY = 1;
const MIN_DATE_STR = '2024-01-01';
const BEFORE_MIN_DATE_STR = '2023-12-31';

const daysToMilliseconds = (days: number): number =>
  days * SECONDS_IN_DAY * MILLISECONDS_IN_SECOND;

test.describe('Issue Listing Page Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/issues');
    await page.waitForTimeout(PAGE_LOAD_TIMEOUT);
  });

  test('loads issue listing page correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/KernelCI/);
    await expect(page).toHaveURL(/\/issues/);

    await expect(page.locator(ISSUE_LISTING_SELECTORS.table)).toBeVisible();
    await expect(
      page.locator(ISSUE_LISTING_SELECTORS.commentColumnHeader),
    ).toBeVisible();
    await expect(
      page.locator(ISSUE_LISTING_SELECTORS.originColumnHeader),
    ).toBeVisible();
  });

  test('date range inputs are visible with default values', async ({
    page,
  }) => {
    const startInput = page.locator(ISSUE_LISTING_SELECTORS.startDateInput);
    const endInput = page.locator(ISSUE_LISTING_SELECTORS.endDateInput);

    await expect(startInput).toBeVisible();
    await expect(endInput).toBeVisible();

    const startValue = await startInput.inputValue();
    const endValue = await endInput.inputValue();

    expect(startValue).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(endValue).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(new Date(startValue).getTime()).toBeLessThan(
      new Date(endValue).getTime(),
    );
  });

  test('changing start date updates URL search params', async ({ page }) => {
    const startInput = page.locator(ISSUE_LISTING_SELECTORS.startDateInput);
    await expect(startInput).toBeVisible();

    const endValue = await page
      .locator(ISSUE_LISTING_SELECTORS.endDateInput)
      .inputValue();

    const newStart = new Date(
      new Date(endValue).getTime() - daysToMilliseconds(THREE_DAYS),
    )
      .toISOString()
      .slice(0, TEN_DAYS);

    await startInput.fill(newStart);
    await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);

    await expect(page).toHaveURL(/st=/);
  });

  test('changing end date updates URL search params', async ({ page }) => {
    const endInput = page.locator(ISSUE_LISTING_SELECTORS.endDateInput);
    await expect(endInput).toBeVisible();

    const startValue = await page
      .locator(ISSUE_LISTING_SELECTORS.startDateInput)
      .inputValue();

    const newEnd = new Date(
      new Date(startValue).getTime() + daysToMilliseconds(TEN_DAYS),
    )
      .toISOString()
      .slice(0, TEN_DAYS);

    await endInput.fill(newEnd);
    await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);

    await expect(page).toHaveURL(/et=/);
  });

  test('start date before minimum (2023-12-31) does not update URL', async ({
    page,
  }) => {
    const startInput = page.locator(ISSUE_LISTING_SELECTORS.startDateInput);
    await expect(startInput).toBeVisible();

    const urlBefore = page.url();
    await startInput.fill(BEFORE_MIN_DATE_STR);
    await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);

    expect(page.url()).toBe(urlBefore);
  });

  test('start date at minimum (2024-01-01) updates URL', async ({ page }) => {
    const startInput = page.locator(ISSUE_LISTING_SELECTORS.startDateInput);
    await expect(startInput).toBeVisible();

    await startInput.fill(MIN_DATE_STR);
    await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);

    await expect(page).toHaveURL(/st=/);
  });

  test('end date before start date does not update URL', async ({ page }) => {
    const startInput = page.locator(ISSUE_LISTING_SELECTORS.startDateInput);
    const endInput = page.locator(ISSUE_LISTING_SELECTORS.endDateInput);

    await expect(endInput).toBeVisible();

    const startValue = await startInput.inputValue();
    const invalidEnd = new Date(
      new Date(startValue).getTime() - daysToMilliseconds(TWO_DAYS),
    )
      .toISOString()
      .slice(0, TEN_DAYS);

    const urlBefore = page.url();
    await endInput.fill(invalidEnd);
    await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);

    expect(page.url()).toBe(urlBefore);
  });

  test('change table size', async ({ page }) => {
    await expect(page.locator(ISSUE_LISTING_SELECTORS.table)).toBeVisible();

    const tableSizeSelector = page.locator('[role="combobox"]').first();
    await expect(tableSizeSelector).toBeVisible();

    await tableSizeSelector.click();

    await expect(
      page.locator(ISSUE_LISTING_SELECTORS.itemsPerPageDropdown),
    ).toBeVisible();

    await page
      .locator(ISSUE_LISTING_SELECTORS.itemsPerPageOption('25'))
      .click();

    await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);

    await expect(tableSizeSelector).toContainText('25');
  });

  test('pagination navigation', async ({ page }) => {
    await expect(page.locator(ISSUE_LISTING_SELECTORS.table)).toBeVisible();

    const nextPageButton = page
      .locator(ISSUE_LISTING_SELECTORS.nextPageButton)
      .first();

    const hasNextPage =
      (await nextPageButton.count()) > 0 &&
      !(await nextPageButton.isDisabled());

    if (hasNextPage) {
      const urlBefore = page.url();
      await nextPageButton.click();
      await page.waitForTimeout(DEFAULT_ACTION_TIMEOUT);
      expect(page.url()).not.toBe(urlBefore);
    }
  });

  test('table rows are visible', async ({ page }) => {
    await expect(page.locator(ISSUE_LISTING_SELECTORS.table)).toBeVisible();

    const rows = page.locator(COMMON_SELECTORS.tableRow);
    const count = await rows.count();
    expect(count).toBeGreaterThan(1);
  });
});
