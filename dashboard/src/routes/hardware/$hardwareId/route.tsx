import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  DEFAULT_TREE_COMMITS,
  DEFAULT_TREE_INDEXES,
  zTreeCommits,
  zTreeIndexes,
} from '@/types/hardware/hardwareDetails';

import {
  DEFAULT_DIFF_FILTER,
  DEFAULT_TAB,
  zDiffFilter,
  zPossibleTabValidator,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/general';

const defaultValues = {
  currentPageTab: DEFAULT_TAB,
  treeIndexes: DEFAULT_TREE_INDEXES,
  treeCommits: DEFAULT_TREE_COMMITS,
  tableFilter: zTableFilterInfoDefault,
  diffFilter: DEFAULT_DIFF_FILTER,
};
const hardwareDetailsSearchSchema = z.object({
  currentPageTab: zPossibleTabValidator,
  treeIndexes: zTreeIndexes,
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
