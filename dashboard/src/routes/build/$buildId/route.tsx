import { z } from 'zod';

import { createFileRoute } from '@tanstack/react-router';

import { zTableFilterInfoValidator } from '@/types/tree/TreeDetails';

const buildDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfoValidator,
});

export const Route = createFileRoute('/build/$buildId')({
  validateSearch: buildDetailsSearchSchema,
});
