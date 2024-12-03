import { createFileRoute, redirect } from '@tanstack/react-router';

import { RedirectFrom } from '@/types/general';

export const Route = createFileRoute('/hardware/$hardwareId/test/$testId/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: async ({ params, deps }) => {
    throw redirect({
      to: '/test/$testId',
      search: deps.search,
      state: { id: params.hardwareId, from: RedirectFrom.Hardware },
    });
  },
});
