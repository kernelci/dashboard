import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zOrigin } from '@/types/tree/Tree';

import {
  zPossibleValidator,
  zTableFilterInfo,
  zDiffFilter,
  zTreeInformation,
} from '@/types/tree/TreeDetails';

const treeDetailsSearchSchema = z.object({
  currentTreeDetailsTab: zPossibleValidator,
  tableFilter: zTableFilterInfo,
  diffFilter: zDiffFilter,
  testPath: z.string().optional().catch(''),
  origin: zOrigin,
  treeInfo: zTreeInformation,
});

export const Route = createFileRoute('/tree/$treeId')({
  validateSearch: treeDetailsSearchSchema,
});
