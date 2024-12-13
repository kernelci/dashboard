import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  DEFAULT_DIFF_FILTER,
  DEFAULT_ORIGIN,
  DEFAULT_TAB,
  zDiffFilter,
  zOrigin,
  zPossibleTabValidator,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/general';

import { DEFAULT_TREE_INFO, zTreeInformation } from '@/types/tree/TreeDetails';

const defaultValues = {
  diffFilter: DEFAULT_DIFF_FILTER,
  origin: DEFAULT_ORIGIN,
  treeInfo: DEFAULT_TREE_INFO,
  currentPageTab: DEFAULT_TAB,
  tableFilter: zTableFilterInfoDefault,
};

const treeDetailsSearchSchema = z.object({
  diffFilter: zDiffFilter,
  origin: zOrigin,
  treeInfo: zTreeInformation,
  currentPageTab: zPossibleTabValidator,
  tableFilter: zTableFilterInfoValidator,
});

export const Route = createFileRoute('/tree/$treeId')({
  validateSearch: treeDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
