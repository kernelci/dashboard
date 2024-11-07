import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zOrigin } from '@/types/tree/Tree';
import { makeZIntervalInDays } from '@/types/general';
import { DEFAULT_TIME_SEARCH } from '@/pages/treeConstants';

export const RootSearchSchema = z.object({
  origin: zOrigin,
  intervalInDays: makeZIntervalInDays(DEFAULT_TIME_SEARCH),
});

export const Route = createFileRoute('/tree')({
  validateSearch: RootSearchSchema,
});
