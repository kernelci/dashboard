import { createFileRoute, redirect } from '@tanstack/react-router';

import { z } from 'zod';

import { RedirectFrom, zTableFilterInfoValidator } from '@/types/general';

const buildDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfoValidator,
});

export const Route = createFileRoute('/tree/$treeId/build/$buildId/')({
  validateSearch: buildDetailsSearchSchema,
  loaderDeps: ({ search }) => ({ search }),
  loader: async ({ params, deps }) => {
    throw redirect({
      to: '/build/$buildId',
      params: { buildId: params.buildId },
      search: deps.search,
      state: { id: params.treeId, from: RedirectFrom.Tree },
    });
  },
});
