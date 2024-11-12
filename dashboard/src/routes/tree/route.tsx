import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { makeZIntervalInDays } from '@/types/general';
import { DEFAULT_TIME_SEARCH } from '@/pages/treeConstants';

export const RootSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_TIME_SEARCH),
});

export const Route = createFileRoute('/tree')({
  validateSearch: RootSearchSchema,
});
