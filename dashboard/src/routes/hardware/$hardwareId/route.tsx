import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import {
  zPossibleValidator,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';

import { zDiffFilter } from '@/types/hardware/hardwareDetails';

const hardwareDetailsSearchSchema = z.object({
  currentPageTab: zPossibleValidator,
  treeIndexes: z.array(z.number().int()).optional(),
  tableFilter: zTableFilterInfoValidator,
  startTimestampInSeconds: z.number(),
  endTimestampInSeconds: z.number(),
  diffFilter: zDiffFilter,
});

export const Route = createFileRoute('/hardware/$hardwareId')({
  validateSearch: hardwareDetailsSearchSchema,
});
