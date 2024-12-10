import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  defaultValidadorValues,
  zPossibleTabValidator,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';

import { zTreeCommits } from '@/types/hardware/hardwareDetails';
import { DEFAULT_DIFF_FILTER, zDiffFilter } from '@/types/general';

const defaultValues = {
  currentPageTab: defaultValidadorValues.tab,
  treeIndexes: [],
  treeCommits: {},
  tableFilter: zTableFilterInfoDefault,
  diffFilter: DEFAULT_DIFF_FILTER,
};
const hardwareDetailsSearchSchema = z.object({
  currentPageTab: zPossibleTabValidator,
  treeIndexes: z.array(z.number().int()).default([]),
  treeCommits: zTreeCommits,
  tableFilter: zTableFilterInfoValidator,
  startTimestampInSeconds: z.number(),
  endTimestampInSeconds: z.number(),
  diffFilter: zDiffFilter,
});

export const Route = createFileRoute('/hardware/$hardwareId')({
  validateSearch: hardwareDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
