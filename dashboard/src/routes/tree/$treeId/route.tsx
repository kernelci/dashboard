import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  DEFAULT_DIFF_FILTER,
  DEFAULT_ORIGIN,
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

const defaultValues = {
  diffFilter: DEFAULT_DIFF_FILTER,
  testPath: '',
  origin: DEFAULT_ORIGIN,
  treeInfo: DEFAULT_TREE_INFO,
  currentPageTab: defaultValidadorValues.tab,
  tableFilter: zTableFilterInfoDefault,
};

const treeDetailsSearchSchema = z.object({
  diffFilter: zDiffFilter,
  testPath: z.string().catch(''),
  origin: zOrigin,
  treeInfo: zTreeInformation,
  currentPageTab: zPossibleTabValidator,
  tableFilter: zTableFilterInfoValidator,
});

export const Route = createFileRoute('/tree/$treeId')({
  validateSearch: treeDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
