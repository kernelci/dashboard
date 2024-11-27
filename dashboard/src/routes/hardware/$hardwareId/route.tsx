import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import {
  zPossibleTabValidator,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';

import { zTreeCommits } from '@/types/hardware/hardwareDetails';
import { zDiffFilter } from '@/types/general';

const hardwareDetailsSearchSchema = z.object({
  currentPageTab: zPossibleTabValidator,
  treeIndexes: z.array(z.number().int()).optional(),
  treeCommits: zTreeCommits,
  tableFilter: zTableFilterInfoValidator,
  limitTimestampInSeconds: z.number(),
  diffFilter: zDiffFilter,
});

export const Route = createFileRoute('/hardware/$hardwareId')({
  validateSearch: hardwareDetailsSearchSchema,
});
