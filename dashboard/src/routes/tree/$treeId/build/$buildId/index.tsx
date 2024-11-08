import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zTableFilterInfo } from '@/types/tree/TreeDetails';
import TreeBuildDetails from '@/pages/TreeBuildDetails';

const buildDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfo,
});

export const Route = createFileRoute('/tree/$treeId/build/$buildId/')({
  component: () => <TreeBuildDetails />,
  validateSearch: buildDetailsSearchSchema,
});
