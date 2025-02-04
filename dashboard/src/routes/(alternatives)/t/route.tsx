import {
  createFileRoute,
  redirect,
  stripSearchParams,
} from '@tanstack/react-router';

import { z } from 'zod';

import { makeZIntervalInDays, type SearchSchema } from '@/types/general';
import { DEFAULT_TIME_SEARCH } from '@/utils/constants/general';

const defaultValues = {
  intervalInDays: DEFAULT_TIME_SEARCH,
  treeSearch: '',
};

export const RootSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_TIME_SEARCH),
  treeSearch: z.string().catch(''),
} satisfies SearchSchema);

export const Route = createFileRoute('/(alternatives)/t')({
  validateSearch: RootSearchSchema,
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps }) => {
    throw redirect({
      to: '/tree',
      search: deps.search,
    });
  },
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
