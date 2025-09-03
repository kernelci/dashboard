import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  defaultValidadorValues,
  zPossibleTabValidator,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';

import { zTreeCommits } from '@/types/hardware/hardwareDetails';
import {
  DEFAULT_DIFF_FILTER,
  DEFAULT_ORIGIN,
  type SearchSchema,
  zDiffFilter,
  zOrigin,
} from '@/types/general';

const defaultValues = {
  origin: DEFAULT_ORIGIN,
  currentPageTab: defaultValidadorValues.tab,
  treeIndexes: null,
  treeCommits: {},
  tableFilter: zTableFilterInfoDefault,
  diffFilter: DEFAULT_DIFF_FILTER,
};
const hardwareDetailsSearchSchema = z.object({
  origin: zOrigin,
  currentPageTab: zPossibleTabValidator,
  treeIndexes: z.array(z.number().int()).nullable().default(null),
  treeCommits: zTreeCommits,
  tableFilter: zTableFilterInfoValidator,
  diffFilter: zDiffFilter,
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/hardware/$hardwareId')({
  validateSearch: hardwareDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
