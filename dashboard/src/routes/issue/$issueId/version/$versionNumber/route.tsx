import { z } from 'zod';

import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  defaultValidadorValues,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';
import { DEFAULT_DIFF_FILTER, DEFAULT_ORIGIN } from '@/types/general';
import { DEFAULT_TIME_SEARCH } from '@/pages/treeConstants';

const defaultValues = {
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

const issueDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfoValidator,
});

export const Route = createFileRoute('/issue/$issueId/version/$versionNumber')({
  validateSearch: issueDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
