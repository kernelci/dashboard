import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import { makeZIntervalInDays } from '@/types/general';
import {
  DEFAULT_TREE_INTERVAL_IN_DAYS,
  DEFAULT_TREE_SEARCH,
} from '@/pages/treeConstants';

const defaultValues = {
  intervalInDays: DEFAULT_TREE_INTERVAL_IN_DAYS,
  treeSearch: DEFAULT_TREE_SEARCH,
};

export const RootSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_TREE_INTERVAL_IN_DAYS),
  treeSearch: z.string().catch(DEFAULT_TREE_SEARCH),
});

export const Route = createFileRoute('/tree')({
  validateSearch: RootSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
