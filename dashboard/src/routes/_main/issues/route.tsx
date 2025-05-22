import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  makeZIntervalInDays,
  zDiffFilter,
  zListingSize,
  type SearchSchema,
} from '@/types/general';
import {
  DEFAULT_LISTING_ITEMS,
  REDUCED_TIME_SEARCH,
} from '@/utils/constants/general';

const DEFAULT_ISSUE_LISTING_DIFFFILTER = {
  issueCulprits: {
    code: true,
  },
};

export const issueListingDefaultValues = {
  intervalInDays: REDUCED_TIME_SEARCH,
  issueSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
  diffFilter: DEFAULT_ISSUE_LISTING_DIFFFILTER,
};

export const issueListingSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(REDUCED_TIME_SEARCH),
  issueSearch: z.string().catch(''),
  listingSize: zListingSize,
  diffFilter: zDiffFilter.default(DEFAULT_ISSUE_LISTING_DIFFFILTER),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/issues')({
  validateSearch: issueListingSearchSchema,
  search: { middlewares: [stripSearchParams(issueListingDefaultValues)] },
});
