import { z } from 'zod';

import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  DEFAULT_DIFF_FILTER,
  DEFAULT_ORIGIN,
  DEFAULT_TAB,
  zTableFilterInfoDefault,
} from '@/types/general';

import {
  DEFAULT_TREE_INTERVAL_IN_DAYS,
  DEFAULT_TREE_SEARCH,
} from '@/pages/treeConstants';
import {
  DEFAULT_TREE_COMMITS,
  DEFAULT_TREE_INDEXES,
} from '@/types/hardware/hardwareDetails';
import { DEFAULT_HARDWARE_SEARCH } from '@/utils/constants/hardware';

const defaultValues = {
  origin: DEFAULT_ORIGIN,
  tableFilter: zTableFilterInfoDefault,
  diffFilter: DEFAULT_DIFF_FILTER,
  currentPageTab: DEFAULT_TAB,
  intervalInDays: DEFAULT_TREE_INTERVAL_IN_DAYS,
  treeSearch: DEFAULT_TREE_SEARCH,
  hardwareSearch: DEFAULT_HARDWARE_SEARCH,
  treeIndexes: DEFAULT_TREE_INDEXES,
  treeCommits: DEFAULT_TREE_COMMITS,
};

const testDetailsSearchSchema = z.object({});

export const Route = createFileRoute('/test/$testId')({
  validateSearch: testDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
