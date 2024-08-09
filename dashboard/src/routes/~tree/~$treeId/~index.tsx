import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import {
  zPossibleValidator,
  zTableFilterValidator,
  zDiffFilter,
} from '@/types/tree/TreeDetails';

import TreeDetails from '@/pages/TreeDetails/TreeDetails';

const treeDetailsSearchSchema = z.object({
  currentTreeDetailsTab: zPossibleValidator,
  tableFilter: zTableFilterValidator,
  diffFilter: zDiffFilter,
});

export const Route = createFileRoute('/tree/$treeId/')({
  validateSearch: treeDetailsSearchSchema,
  component: TreeDetails,
});
