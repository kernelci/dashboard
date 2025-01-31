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
  issueVersion: undefined,
};

const issueDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfoValidator,
  issueVersion: z.number().optional(),
} satisfies SearchSchema);

export const Route = createFileRoute('/issue/$issueId')({
  validateSearch: issueDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
