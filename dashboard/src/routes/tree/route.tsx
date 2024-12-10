import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import { makeZIntervalInDays } from '@/types/general';
import { DEFAULT_TIME_SEARCH } from '@/pages/treeConstants';

const defaultValues = {
  intervalInDays: DEFAULT_TIME_SEARCH,
  treeSearch: '',
};

export const RootSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_TIME_SEARCH),
  treeSearch: z.string().catch(''),
});

export const Route = createFileRoute('/tree')({
  validateSearch: RootSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
