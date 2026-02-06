import type { Page } from '@playwright/test';
import { expect } from '@playwright/test';

const DRAWER_TIMEOUT = 10000;

/**
 * Open the filter drawer and wait for it to be visible
 */
export async function openFilterDrawer(
  page: Page,
  filterButtonSelector: string,
  drawerContentSelector: string,
  options?: {
    timeout?: number;
  },
): Promise<void> {
  const timeout = options?.timeout ?? DRAWER_TIMEOUT;

  const filterButton = page.locator(filterButtonSelector);
  await filterButton.waitFor({ state: 'visible', timeout });
  await filterButton.click();

  const drawerContent = page.locator(drawerContentSelector);
  await expect(drawerContent).toBeVisible({ timeout });
}

/**
 * Close the filter drawer by clicking the cancel button
 */
export async function closeFilterDrawer(
  page: Page,
  cancelButtonSelector: string,
  drawerContentSelector: string,
): Promise<void> {
  const cancelButton = page.locator(cancelButtonSelector);
  await expect(cancelButton).toBeVisible();
  await cancelButton.click();

  const drawerContent = page.locator(drawerContentSelector);
  await expect(drawerContent).not.toBeVisible();
}

/**
 * Open filter drawer, optionally perform actions, then close it
 */
export async function withFilterDrawer(
  page: Page,
  filterButtonSelector: string,
  cancelButtonSelector: string,
  drawerContentSelector: string,
  action?: (page: Page) => Promise<void>,
): Promise<void> {
  await openFilterDrawer(page, filterButtonSelector, drawerContentSelector);

  if (action) {
    await action(page);
  }

  await closeFilterDrawer(page, cancelButtonSelector, drawerContentSelector);
}
