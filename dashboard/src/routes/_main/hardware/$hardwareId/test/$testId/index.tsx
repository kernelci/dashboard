import { createFileRoute, redirect } from '@tanstack/react-router';

import { RedirectFrom } from '@/types/general';

export const Route = createFileRoute(
  '/_main/hardware/$hardwareId/test/$testId/',
)({
  loaderDeps: ({ search }) => ({ search }),
  loader: async ({ params, deps }) => {
    throw redirect({
      to: '/test/$testId',
      params: { testId: params.testId },
      search: deps.search,
      state: { id: params.hardwareId, from: RedirectFrom.Hardware },
    });
  },
});
