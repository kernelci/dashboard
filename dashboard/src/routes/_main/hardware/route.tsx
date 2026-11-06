import { createFileRoute, stripSearchParams } from '@tanstack/react-router';
import { z } from 'zod';

import {
  DEFAULT_REGISTRY_FILTER,
  zRegistryFilter,
} from '@/pages/Hardware/registryFilters';
import {
  DEFAULT_HARDWARE_DIFF_FILTER,
  makeZIntervalInDays,
  zDiffFilter,
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
  diffFilter: DEFAULT_HARDWARE_DIFF_FILTER,
  registryFilter: DEFAULT_REGISTRY_FILTER,
};

const zHardwareSchema = z.object({
  intervalInDays: makeZIntervalInDays(defaultValues.intervalInDays),
  hardwareSearch: z.string().catch(''),
  listingSize: zListingSize,
  registryFilter: zRegistryFilter,
  treeName: z.optional(z.string()),
  gitRepositoryUrl: z.optional(z.string()),
  gitBranch: z.optional(z.string()),
  gitCommitHash: z.optional(z.string()),
  diffFilter: zDiffFilter.default(DEFAULT_HARDWARE_DIFF_FILTER),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/hardware')({
  validateSearch: zHardwareSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
