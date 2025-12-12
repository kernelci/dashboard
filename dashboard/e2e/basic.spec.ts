import { test, expect } from '@playwright/test';

test('homepage has KernelCI in title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/KernelCI/);
});

test('trees page loads', async ({ page }) => {
  await page.goto('/tree');
  await expect(page).toHaveURL(/\/tree/);
});
