import { createFileRoute, stripSearchParams } from '@tanstack/react-router';
import { z } from 'zod';

import { makeZIntervalInDays, type SearchSchema } from '@/types/general';
import { DEFAULT_HARDWARE_INTERVAL_IN_DAYS } from '@/utils/constants/hardware';

const defaultValues = {
  intervalInDays: DEFAULT_HARDWARE_INTERVAL_IN_DAYS,
  hardwareSearch: '',
};

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_HARDWARE_INTERVAL_IN_DAYS),
  hardwareSearch: z.string().catch(''),
} satisfies SearchSchema);

export const Route = createFileRoute('/hardware')({
  validateSearch: zHardwareSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
