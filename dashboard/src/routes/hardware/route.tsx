import { createFileRoute, stripSearchParams } from '@tanstack/react-router';
import { z } from 'zod';

import { makeZIntervalInDays } from '@/types/general';
import {
  DEFAULT_HARDWARE_INTERVAL_IN_DAYS,
  DEFAULT_HARDWARE_SEARCH,
} from '@/utils/constants/hardware';

const defaultValues = {
  intervalInDays: DEFAULT_HARDWARE_INTERVAL_IN_DAYS,
  hardwareSearch: DEFAULT_HARDWARE_SEARCH,
};

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_HARDWARE_INTERVAL_IN_DAYS),
  hardwareSearch: z.string().catch(DEFAULT_HARDWARE_SEARCH),
});

export const Route = createFileRoute('/hardware')({
  validateSearch: zHardwareSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
