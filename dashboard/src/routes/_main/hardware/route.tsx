import { createFileRoute, stripSearchParams } from '@tanstack/react-router';
import { z } from 'zod';

import {
  makeZIntervalInDays,
  zListingSize,
  type SearchSchema,
} from '@/types/general';
import {
  DEFAULT_LISTING_ITEMS,
  REDUCED_TIME_SEARCH,
} from '@/utils/constants/general';
import { DEFAULT_HARDWARE_LISTING_FILTERS } from '@/utils/constants/hardwareListing';

const defaultValues = {
  intervalInDays: REDUCED_TIME_SEARCH,
  hardwareSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
  ...DEFAULT_HARDWARE_LISTING_FILTERS,
};

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(REDUCED_TIME_SEARCH),
  hardwareSearch: z.string().catch(''),
  listingSize: zListingSize,
  // An empty filter means every value, which is why only the two origins that KCI
  // defaults to are pre-set here
  checkoutOrigin: z
    .string()
    .catch(DEFAULT_HARDWARE_LISTING_FILTERS.checkoutOrigin),
  buildOrigin: z.string().catch(DEFAULT_HARDWARE_LISTING_FILTERS.buildOrigin),
  testOrigin: z.string().catch(DEFAULT_HARDWARE_LISTING_FILTERS.testOrigin),
  buildLab: z.string().catch(DEFAULT_HARDWARE_LISTING_FILTERS.buildLab),
  testLab: z.string().catch(DEFAULT_HARDWARE_LISTING_FILTERS.testLab),
  treeName: z.optional(z.string()),
  gitRepositoryUrl: z.optional(z.string()),
  gitBranch: z.optional(z.string()),
  gitCommitHash: z.optional(z.string()),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/hardware')({
  validateSearch: zHardwareSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
