import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

import { makeZIntervalInDays } from '@/types/general';
import { DEFAULT_HARDWARE_INTERVAL_IN_DAYS } from '@/utils/constants/hardware';

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_HARDWARE_INTERVAL_IN_DAYS),
  hardwareSearch: z.string().optional().catch(undefined),
});

export const Route = createFileRoute('/hardware')({
  validateSearch: zHardwareSchema,
});
