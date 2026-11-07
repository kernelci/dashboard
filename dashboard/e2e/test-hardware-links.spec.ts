import { expect, test } from '@playwright/test';

const hardware = 'ti,dra718-evm';
const compatible = 'ti,dra718';
const testId = 'hardware-link-test';

for (const origin of ['ti', 'maestro']) {
  for (const target of [hardware, compatible]) {
    test(`${origin} test links to ${target} with its test origin`, async ({
      page,
      context,
    }) => {
      await context.route(
        url => url.pathname.startsWith('/api/'),
        route => route.fulfill({ status: 404, json: {} }),
      );
      await context.route(`**/api/test/${testId}`, route =>
        route.fulfill({
          json: {
            id: testId,
            build_id: 'hardware-link-build',
            path: 'boot',
            status: 'PASS',
            field_timestamp: '2026-07-16T16:56:40Z',
            start_time: '2026-07-16T16:46:39Z',
            // Checkout and test origins need not match.
            origin: origin === 'ti' ? 'maestro' : 'other-checkout-origin',
            test_origin: origin,
            environment_misc: { platform: hardware },
            environment_compatible: [compatible],
          },
        }),
      );
      await context.route(`**/api/test/${testId}/issues`, route =>
        route.fulfill({ json: [] }),
      );

      const link = page.getByRole('link', { name: target, exact: true });
      const href = `/hardware/${encodeURIComponent(target)}?df%7Cto%7C${origin}=true`;
      await page.goto(`/test/${testId}`);
      await expect(link).toHaveAttribute('href', href);

      // Unrelated navigation context must not override the result's origin.
      await page.goto(
        `/test/${testId}?o=stale-origin&df%7Cto%7Cstale-origin=true`,
      );
      await expect(link).toHaveAttribute('href', href);
      await expect(link).toHaveAttribute('target', '_blank');

      const summaryPath = `/api/hardware/${target}/summary`;
      const summaryRequest = context.waitForEvent('request', {
        predicate: request =>
          decodeURIComponent(new URL(request.url()).pathname) === summaryPath,
      });
      const popup = page.waitForEvent('popup');
      await link.click();
      const hardwarePage = await popup;
      expect((await summaryRequest).postDataJSON().filter).toEqual({
        'filter_boot.origin': [origin],
        'filter_test.origin': [origin],
      });
      await expect(hardwarePage).toHaveURL(
        url => decodeURIComponent(url.pathname) === `/hardware/${target}`,
      );
      expect(
        new URL(hardwarePage.url()).searchParams.get(`df|to|${origin}`),
      ).toBe('true');

      // A copied URL must work without the source tab's history state.
      const sharedPage = await context.newPage();
      const sharedRequest = sharedPage.waitForRequest(
        request =>
          decodeURIComponent(new URL(request.url()).pathname) === summaryPath,
      );
      await sharedPage.goto(hardwarePage.url());
      expect((await sharedRequest).postDataJSON().filter).toEqual({
        'filter_boot.origin': [origin],
        'filter_test.origin': [origin],
      });

      const reloadRequest = sharedPage.waitForRequest(
        request =>
          decodeURIComponent(new URL(request.url()).pathname) === summaryPath,
      );
      await sharedPage.reload();
      expect((await reloadRequest).postDataJSON().filter).toEqual({
        'filter_boot.origin': [origin],
        'filter_test.origin': [origin],
      });
    });
  }
}
