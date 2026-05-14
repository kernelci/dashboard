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

const defaultValues = {
  intervalInDays: REDUCED_TIME_SEARCH,
  hardwareSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
};

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(REDUCED_TIME_SEARCH),
  hardwareSearch: z.string().catch(''),
  listingSize: zListingSize,
  treeName: z.optional(z.string()),
  gitRepositoryUrl: z.optional(z.string()),
  gitBranch: z.optional(z.string()),
  gitCommitHash: z.optional(z.string()),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/hardware')({
  validateSearch: zHardwareSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
