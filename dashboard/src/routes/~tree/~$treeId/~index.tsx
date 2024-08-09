import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import {
  possibleTabValidator,
  tableFilterValidator,
  zDiffFilter,
} from '@/types/tree/TreeDetails';

import TreeDetails from './TreeDetails';

const treeDetailsSearchSchema = z.object({
  currentTreeDetailsTab: possibleTabValidator,
  tableFilter: tableFilterValidator,
  diffFilter: zDiffFilter,
});

export const Route = createFileRoute('/tree/$treeId/')({
  validateSearch: treeDetailsSearchSchema,
  component: TreeDetails,
});
