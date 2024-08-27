import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zOrigin } from '@/types/tree/Tree';

import {
  zPossibleValidator,
  zDiffFilter,
  zTreeInformation,
  zTableFilterInfo,
} from '@/types/tree/TreeDetails';

import TreeDetails from '@/pages/TreeDetails/TreeDetails';

const treeDetailsSearchSchema = z.object({
  currentTreeDetailsTab: zPossibleValidator,
  tableFilter: zTableFilterInfo,
  diffFilter: zDiffFilter,
  testPath: z.string().optional().catch(''),
  origin: zOrigin,
  treeInfo: zTreeInformation,
});

export const Route = createFileRoute('/tree/$treeId/')({
  validateSearch: treeDetailsSearchSchema,
  component: TreeDetails,
});
