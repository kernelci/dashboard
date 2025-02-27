import { z } from 'zod';

import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';
import { type SearchSchema } from '@/types/general';

export const issueDetailsDefaultValues = {
  tableFilter: zTableFilterInfoDefault,
  issueVersion: undefined,
};

export const issueDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfoValidator,
  issueVersion: z.number().optional(),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/issue/$issueId')({
  validateSearch: issueDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(issueDetailsDefaultValues)] },
});
