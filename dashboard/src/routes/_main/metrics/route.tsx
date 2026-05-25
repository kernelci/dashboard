import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import { makeZIntervalInDays, type SearchSchema } from '@/types/general';

const DEFAULT_METRICS_INTERVAL = 7;

const defaultValues = {
  intervalInDays: DEFAULT_METRICS_INTERVAL,
};

const metricsSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_METRICS_INTERVAL),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/metrics')({
  validateSearch: metricsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
