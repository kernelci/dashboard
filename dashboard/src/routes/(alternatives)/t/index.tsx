import { createFileRoute, redirect } from '@tanstack/react-router';

import { z } from 'zod';

export const TreeSearchSchema = z.object({
  treeSearch: z.string().catch(''),
});

export const Route = createFileRoute('/(alternatives)/t/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps }) => {
    throw redirect({
      to: '/tree',
      search: deps.search,
    });
  },
});
