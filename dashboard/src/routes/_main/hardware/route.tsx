import { createFileRoute, stripSearchParams } from '@tanstack/react-router';
import { z } from 'zod';

import {
  DEFAULT_ORIGIN,
  makeZIntervalInDays,
  zDiffFilter,
  zListingSize,
  type SearchSchema,
  type TFilter,
} from '@/types/general';
import {
  DEFAULT_LISTING_ITEMS,
  REDUCED_TIME_SEARCH,
} from '@/utils/constants/general';

const DEFAULT_HARDWARE_LISTING_DIFF_FILTER: TFilter = {
  checkoutOrigins: { [DEFAULT_ORIGIN]: true },
  buildOrigin: { [DEFAULT_ORIGIN]: true },
};

const defaultValues = {
  intervalInDays: REDUCED_TIME_SEARCH,
  hardwareSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
  diffFilter: DEFAULT_HARDWARE_LISTING_DIFF_FILTER,
};

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(defaultValues.intervalInDays),
  hardwareSearch: z.string().catch(''),
  listingSize: zListingSize,
  treeName: z.optional(z.string()),
  gitRepositoryUrl: z.optional(z.string()),
  gitBranch: z.optional(z.string()),
  gitCommitHash: z.optional(z.string()),
  diffFilter: zDiffFilter.default(DEFAULT_HARDWARE_LISTING_DIFF_FILTER),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/hardware')({
  validateSearch: zHardwareSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
