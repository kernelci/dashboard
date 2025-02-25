import { z } from 'zod';

import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  defaultValidadorValues,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';
import {
  DEFAULT_DIFF_FILTER,
  DEFAULT_ORIGIN,
  type SearchSchema,
} from '@/types/general';
import { DEFAULT_LOG_OPEN, zLogOpen } from '@/types/commonDetails';

import { DEFAULT_TIME_SEARCH } from '@/utils/constants/general';

export const buildDetailsDefaultValues = {
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

export const buildDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfoValidator,
  logOpen: zLogOpen,
} satisfies SearchSchema);

export const Route = createFileRoute('/build/$buildId')({
  validateSearch: buildDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(buildDetailsDefaultValues)] },
});
