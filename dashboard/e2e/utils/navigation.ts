import type { Page, Locator } from '@playwright/test';
import { expect } from '@playwright/test';

const NAVIGATE_TIMEOUT = 30000;
const BREADCRUMB_TIMEOUT = 20000;

/**
 * Navigate to a page and wait for it to be fully loaded
 */
export async function navigateAndWait(
  page: Page,
  url: string,
  options?: {
    timeout?: number;
    waitForLoadState?: boolean;
  },
): Promise<void> {
  const timeout = options?.timeout ?? NAVIGATE_TIMEOUT;
  const waitForLoadState = options?.waitForLoadState ?? true;

  await page.goto(url, { timeout });

  if (waitForLoadState) {
    await page.waitForLoadState('domcontentloaded');
  }
}

/**
 * Click a breadcrumb link and navigate back to tree listing
 */
export async function navigateBackViaBreadcrumb(
  page: Page,
  breadcrumbSelector: string,
  options?: {
    expectedUrl?: RegExp;
    timeout?: number;
  },
): Promise<void> {
  const timeout = options?.timeout ?? BREADCRUMB_TIMEOUT;
  const expectedUrl = options?.expectedUrl ?? /\/tree/;

  const breadcrumbLink = page.locator(breadcrumbSelector);
  await expect(breadcrumbLink).toBeVisible();
  await breadcrumbLink.click();

  await page.waitForURL(expectedUrl, { timeout });
  await expect(page).toHaveURL(expectedUrl);
}

/**
 * Click an element, wait for navigation, and verify URL pattern
 */
export async function clickAndVerifyNavigation(
  element: Locator,
  urlPattern: RegExp,
  options?: {
    timeout?: number;
    waitAfterClick?: number;
  },
): Promise<void> {
  const timeout = options?.timeout ?? NAVIGATE_TIMEOUT;
  const waitAfterClick = options?.waitAfterClick ?? 0;

  await element.click();

  if (waitAfterClick > 0) {
    await element.page().waitForTimeout(waitAfterClick);
  }

  await element.page().waitForURL(urlPattern, { timeout });

  const url = element.page().url();
  expect(url).toMatch(urlPattern);
}
