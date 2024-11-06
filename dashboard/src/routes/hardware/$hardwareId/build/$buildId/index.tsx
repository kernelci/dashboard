import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zTableFilterInfo } from '@/types/tree/TreeDetails';

const buildDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfo,
});

import HardwareBuildDetails from '@/pages/HardwareBuildDetails';

export const Route = createFileRoute('/hardware/$hardwareId/build/$buildId/')({
  component: () => <HardwareBuildDetails />,
  validateSearch: buildDetailsSearchSchema,
});
