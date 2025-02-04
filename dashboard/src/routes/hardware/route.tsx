import { createFileRoute, stripSearchParams } from '@tanstack/react-router';
import { z } from 'zod';

import {
  makeZIntervalInDays,
  zListingSize,
  type SearchSchema,
} from '@/types/general';
import { DEFAULT_HARDWARE_INTERVAL_IN_DAYS } from '@/utils/constants/hardware';
import { DEFAULT_LISTING_ITEMS } from '@/utils/constants/general';

const defaultValues = {
  intervalInDays: DEFAULT_HARDWARE_INTERVAL_IN_DAYS,
  hardwareSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
};

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_HARDWARE_INTERVAL_IN_DAYS),
  hardwareSearch: z.string().catch(''),
  listingSize: zListingSize,
} satisfies SearchSchema);

export const Route = createFileRoute('/hardware')({
  validateSearch: zHardwareSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
