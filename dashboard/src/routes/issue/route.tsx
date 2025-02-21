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
};

export const issueListingSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_TIME_SEARCH),
  issueSearch: z.string().catch(''),
  listingSize: zListingSize,
} satisfies SearchSchema);

export const Route = createFileRoute('/issue')({
  validateSearch: issueListingSearchSchema,
  search: { middlewares: [stripSearchParams(issueListingDefaultValues)] },
});
