import { createFileRoute, redirect } from '@tanstack/react-router';

import { RedirectFrom } from '@/types/general';

export const Route = createFileRoute('/_main/tree/$treeId/build/$buildId/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: async ({ params, deps, location }) => {
    throw redirect({
      to: '/build/$buildId',
      params: { buildId: params.buildId },
      search: deps.search,
      state: { ...location.state, id: params.treeId, from: RedirectFrom.Tree },
    });
  },
});
