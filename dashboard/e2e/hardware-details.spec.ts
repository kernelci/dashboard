import { expect, test } from '@playwright/test';

test('clear removes every selected tree on qemu-arm64', async ({ page }) => {
  await page.goto('/hardware/qemu-arm64');
  await page.getByRole('button', { name: 'Filters' }).click();

  const selected = page
    .getByRole('dialog')
    .getByRole('button', { name: /^Remove / });
  await expect(selected.nth(1)).toBeVisible();

  await page.getByRole('button', { name: 'Clear', exact: true }).click();

  await expect(selected).toHaveCount(0);
});
