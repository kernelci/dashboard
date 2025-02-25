import { z } from 'zod';

import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  defaultValidadorValues,
  zTableFilterInfoDefault,
} from '@/types/tree/TreeDetails';
import {
  DEFAULT_DIFF_FILTER,
  DEFAULT_ORIGIN,
  type SearchSchema,
} from '@/types/general';
import { DEFAULT_TIME_SEARCH } from '@/utils/constants/general';
import { DEFAULT_LOG_OPEN, zLogOpen } from '@/types/commonDetails';

export const testDetailsDefaultValues = {
  origin: DEFAULT_ORIGIN,
  tableFilter: zTableFilterInfoDefault,
  diffFilter: DEFAULT_DIFF_FILTER,
  currentPageTab: defaultValidadorValues.tab,
  intervalInDays: DEFAULT_TIME_SEARCH,
  treeSearch: '',
  hardwareSearch: '',
  treeIndexes: [],
  treeCommits: {},
  logOpen: DEFAULT_LOG_OPEN,
};

export const testDetailsSearchSchema = z.object({
  logOpen: zLogOpen,
} satisfies SearchSchema);

export const Route = createFileRoute('/test/$testId')({
  validateSearch: testDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(testDetailsDefaultValues)] },
});
