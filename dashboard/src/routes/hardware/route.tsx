import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

import { makeZIntervalInDays } from '@/types/general';
import { DEFAULT_HARDWARE_INTERVAL_IN_DAYS } from '@/utils/constants/hardware';
import { zTableFilterInfoValidator } from '@/types/tree/TreeDetails';

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_HARDWARE_INTERVAL_IN_DAYS),
  hardwareSearch: z.string().optional().catch(undefined),
  tableFilter: zTableFilterInfoValidator,
});

export const Route = createFileRoute('/hardware')({
  validateSearch: zHardwareSchema,
});
