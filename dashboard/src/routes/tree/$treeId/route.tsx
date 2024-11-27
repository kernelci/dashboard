import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zOrigin } from '@/types/general';

import {
  zDiffFilter,
  zPossibleTabValidator,
  zTableFilterInfoValidator,
  zTreeInformation,
} from '@/types/tree/TreeDetails';

const treeDetailsSearchSchema = z.object({
  diffFilter: zDiffFilter,
  testPath: z.string().optional().catch(''),
  origin: zOrigin,
  treeInfo: zTreeInformation,
  currentPageTab: zPossibleTabValidator,
  tableFilter: zTableFilterInfoValidator,
});

export const Route = createFileRoute('/tree/$treeId')({
  validateSearch: treeDetailsSearchSchema,
});
