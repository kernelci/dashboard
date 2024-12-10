import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  defaultValidadorValues,
  zPossibleTabValidator,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';

import { zTreeCommits } from '@/types/hardware/hardwareDetails';
import { DEFAULT_DIFF_FILTER, zDiffFilter } from '@/types/general';

const defaultValues = {
  currentPageTab: defaultValidadorValues.tab,
  treeIndexes: [],
  tableFilter: {
    buildsTable: defaultValidadorValues.buildsTableFilter,
    bootsTable: defaultValidadorValues.testsTableFilter,
    testsTable: defaultValidadorValues.testsTableFilter,
  },
  diffFilter: DEFAULT_DIFF_FILTER,
};
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
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
