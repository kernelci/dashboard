import { createFileRoute, redirect } from '@tanstack/react-router';
import { z } from 'zod';

import {
  DEFAULT_TREE_INTERVAL_IN_DAYS,
  DEFAULT_TREE_SEARCH,
} from '@/pages/treeConstants';
import { makeZIntervalInDays } from '@/types/general';

export const HomeSearchSchema = z.object({
  treeSearch: z.string().catch(DEFAULT_TREE_SEARCH),
  intervalInDays: makeZIntervalInDays(DEFAULT_TREE_INTERVAL_IN_DAYS),
});

export const Route = createFileRoute('/')({
  validateSearch: HomeSearchSchema,
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps }) => {
    throw redirect({ to: '/tree', search: deps.search });
  },
});
