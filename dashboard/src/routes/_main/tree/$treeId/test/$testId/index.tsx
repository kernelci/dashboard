import { createFileRoute, redirect } from '@tanstack/react-router';

import { RedirectFrom } from '@/types/general';

export const Route = createFileRoute('/_main/tree/$treeId/test/$testId/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: async ({ params, deps, location }) => {
    throw redirect({
      to: '/test/$testId',
      params: { testId: params.testId },
      search: deps.search,
      state: { ...location.state, id: params.treeId, from: RedirectFrom.Tree },
    });
  },
});
