import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import BuildDetails from '@/pages/BuildDetails/BuildDetails';

import { zTableFilterInfo } from '@/types/tree/TreeDetails';

const buildDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfo,
});

export const Route = createFileRoute('/tree/$treeId/build/$buildId/')({
  component: BuildDetails,
  validateSearch: buildDetailsSearchSchema,
});
