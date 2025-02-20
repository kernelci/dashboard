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
};

export const buildDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfoValidator,
} satisfies SearchSchema);

export const Route = createFileRoute('/build/$buildId')({
  validateSearch: buildDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(buildDetailsDefaultValues)] },
});
