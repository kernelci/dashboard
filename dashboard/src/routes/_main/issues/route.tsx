import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  makeZIntervalInDays,
  zListingSize,
  type SearchSchema,
} from '@/types/general';
import {
  DEFAULT_LISTING_ITEMS,
  DEFAULT_TIME_SEARCH,
} from '@/utils/constants/general';

export const issueListingDefaultValues = {
  intervalInDays: DEFAULT_TIME_SEARCH,
  issueSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
  culpritCode: true,
  culpritTool: false,
  culpritHarness: false,
};

export const issueListingSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_TIME_SEARCH),
  issueSearch: z.string().catch(''),
  listingSize: zListingSize,
  culpritCode: z.boolean().catch(true),
  culpritTool: z.boolean().catch(false),
  culpritHarness: z.boolean().catch(false),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/issues')({
  validateSearch: issueListingSearchSchema,
  search: { middlewares: [stripSearchParams(issueListingDefaultValues)] },
});
