import { createFileRoute, redirect } from '@tanstack/react-router';

import { RedirectFrom } from '@/types/general';

export const Route = createFileRoute(
  '/_main/hardware/$hardwareId/build/$buildId/',
)({
  loaderDeps: ({ search }) => ({ search }),
  loader: async ({ params, deps }) => {
    throw redirect({
      to: '/build/$buildId',
      params: { buildId: params.buildId },
      search: deps.search,
      state: { id: params.hardwareId, from: RedirectFrom.Hardware },
    });
  },
});
