import { z } from 'zod';

import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  DEFAULT_DIFF_FILTER,
  DEFAULT_ORIGIN,
  type SearchSchema,
  zDiffFilter,
  zOrigin,
} from '@/types/general';

import {
  DEFAULT_TREE_INFO,
  defaultValidadorValues,
  zPossibleTabValidator,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
  zTreeInformation,
} from '@/types/tree/TreeDetails';

export const treeDetailsDefaultValues = {
  diffFilter: DEFAULT_DIFF_FILTER,
  origin: DEFAULT_ORIGIN,
  treeInfo: DEFAULT_TREE_INFO,
  currentPageTab: defaultValidadorValues.tab,
  tableFilter: zTableFilterInfoDefault,
};

export const treeDetailsSearchSchema = z.object({
  diffFilter: zDiffFilter,
  origin: zOrigin,
  treeInfo: zTreeInformation,
  currentPageTab: zPossibleTabValidator,
  tableFilter: zTableFilterInfoValidator,
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/tree/$treeId')({
  validateSearch: treeDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(treeDetailsDefaultValues)] },
});
