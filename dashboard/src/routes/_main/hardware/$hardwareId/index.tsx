import { z } from 'zod';

import { createFileRoute } from '@tanstack/react-router';

import HardwareDetails from '@/pages/hardwareDetails/HardwareDetails';

const searchSchema = z.object({
  startTimestampInSeconds: z.number(),
  endTimestampInSeconds: z.number(),
});

export const Route = createFileRoute('/_main/hardware/$hardwareId/')({
  validateSearch: searchSchema,
  component: HardwareDetails,
});
