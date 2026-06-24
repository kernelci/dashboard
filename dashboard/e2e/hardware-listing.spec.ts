import { test, expect, type Locator, type Page } from '@playwright/test';

import { HARDWARE_LISTING_SELECTORS } from './e2e-selectors';

const SELECTOR_LOAD_TIMEOUT = 15000;
const SELECTION_URL_PARAMS = ['t=', 'gu=', 'gb=', 'ch='] as const;

const getOpenComboboxPopover = (page: Page): Locator =>
  page.locator('[role="dialog"][data-state="open"]');

const openComboboxOptions = async (page: Page): Promise<void> => {
  const popover = getOpenComboboxPopover(page);
  await expect(popover).toBeVisible();
  await expect(popover.getByRole('option').first()).toBeVisible();
};

const selectComboboxOption = async (
  page: Page,
  selector: string,
  optionIndex = 0,
): Promise<string> => {
  const combobox = page.locator(selector);
  await expect(combobox).toBeVisible({ timeout: SELECTOR_LOAD_TIMEOUT });
  await expect(combobox).toBeEnabled();
  await combobox.click();
  await openComboboxOptions(page);

  const option = getOpenComboboxPopover(page)
    .getByRole('option')
    .nth(optionIndex);
  const label = (await option.textContent())?.trim() ?? '';
  await option.click();

  return label;
};

const expectSelectionInUrl = async (page: Page): Promise<void> => {
  for (const param of SELECTION_URL_PARAMS) {
    await expect(page).toHaveURL(new RegExp(`[?&]${param}`));
  }
};

const expectNoSelectionInUrl = (page: Page): void => {
  const url = page.url();
  for (const param of SELECTION_URL_PARAMS) {
    expect(url).not.toMatch(new RegExp(`[?&]${param}`));
  }
};

test.describe('Hardware Listing Page Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/hardware');
    await expect(
      page.locator(HARDWARE_LISTING_SELECTORS.treeSelector),
    ).toBeVisible({ timeout: SELECTOR_LOAD_TIMEOUT });
  });

  test('loads hardware listing page correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/KernelCI/);
    await expect(page).toHaveURL(/\/hardware/);
    await expect(page.locator(HARDWARE_LISTING_SELECTORS.table)).toBeVisible();
  });

  test('selecting a tree auto-fills branch and revision', async ({ page }) => {
    const treeLabel = await selectComboboxOption(
      page,
      HARDWARE_LISTING_SELECTORS.treeSelector,
    );

    await expectSelectionInUrl(page);

    const treeSelector = page.locator(HARDWARE_LISTING_SELECTORS.treeSelector);
    const branchSelector = page.locator(
      HARDWARE_LISTING_SELECTORS.branchSelector,
    );
    const revisionSelector = page.locator(
      HARDWARE_LISTING_SELECTORS.revisionSelector,
    );

    await expect(treeSelector).toContainText(treeLabel);
    await expect(branchSelector).not.toContainText('Select branch');
    await expect(revisionSelector).not.toContainText('Select revision');
    await expect(branchSelector).toBeEnabled();
    await expect(revisionSelector).toBeEnabled();
  });

  test('selecting a branch auto-fills revision', async ({ page }) => {
    await selectComboboxOption(page, HARDWARE_LISTING_SELECTORS.treeSelector);
    await expectSelectionInUrl(page);

    const branchBefore = new URL(page.url()).searchParams.get('gb');
    const revisionBefore = new URL(page.url()).searchParams.get('ch');

    const branchSelector = page.locator(
      HARDWARE_LISTING_SELECTORS.branchSelector,
    );
    await branchSelector.click();
    await openComboboxOptions(page);

    const options = getOpenComboboxPopover(page).getByRole('option');
    const optionCount = await options.count();
    test.skip(
      optionCount < 2,
      'Need at least two branches to verify branch auto-select',
    );

    await options.nth(1).click();

    await expect(page).toHaveURL(/[?&]ch=/);
    await expect(
      page.locator(HARDWARE_LISTING_SELECTORS.revisionSelector),
    ).not.toContainText('Select revision');

    const branchAfter = new URL(page.url()).searchParams.get('gb');
    const revisionAfter = new URL(page.url()).searchParams.get('ch');
    expect(branchAfter).toBeTruthy();
    expect(branchAfter).not.toBe(branchBefore);
    expect(revisionAfter).toBeTruthy();
    expect(revisionAfter).not.toBe(revisionBefore);
  });

  test('clear selection removes selector params from URL', async ({ page }) => {
    await selectComboboxOption(page, HARDWARE_LISTING_SELECTORS.treeSelector);
    await expectSelectionInUrl(page);

    const clearButton = page.locator(HARDWARE_LISTING_SELECTORS.clearSelection);
    test.skip(
      !(await clearButton.isVisible()),
      'Clear selection button is not available in this deployment',
    );

    await clearButton.click();

    expectNoSelectionInUrl(page);
    await expect(
      page.locator(HARDWARE_LISTING_SELECTORS.treeSelector),
    ).toContainText('Select tree');
    await expect(clearButton).toBeHidden();
  });
});
