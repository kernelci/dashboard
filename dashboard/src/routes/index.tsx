import { createFileRoute, redirect } from '@tanstack/react-router';
import { z } from 'zod';

import { DEFAULT_TIME_SEARCH } from '@/pages/treeConstants';
import { makeZIntervalInDays } from '@/types/general';

export const HomeSearchSchema = z.object({
  treeSearch: z.string().optional().catch(undefined),
  intervalInDays: makeZIntervalInDays(DEFAULT_TIME_SEARCH),
});

export const Route = createFileRoute('/')({
  validateSearch: HomeSearchSchema,
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps }) => {
    throw redirect({ to: '/tree', search: deps.search });
  },
});
