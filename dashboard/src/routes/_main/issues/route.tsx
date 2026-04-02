import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import { zDiffFilter, zListingSize, type SearchSchema } from '@/types/general';
import { DEFAULT_LISTING_ITEMS } from '@/utils/constants/general';
import { CULPRIT_CODE, HAS_INCIDENT_OPTION } from '@/utils/constants/issues';

const DEFAULT_ISSUE_LISTING_DIFFFILTER = {
  issueCulprits: {
    [CULPRIT_CODE]: true,
  },
  issueOptions: {
    [HAS_INCIDENT_OPTION]: true,
  },
};

export const issueListingDefaultValues = {
  issueSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
  diffFilter: DEFAULT_ISSUE_LISTING_DIFFFILTER,
};

export const issueListingSearchSchema = z.object({
  startTimestampInSeconds: z.number().int().positive().optional(),
  endTimestampInSeconds: z.number().int().positive().optional(),
  issueSearch: z.string().catch(''),
  listingSize: zListingSize,
  diffFilter: zDiffFilter.default(DEFAULT_ISSUE_LISTING_DIFFFILTER),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/issues')({
  validateSearch: issueListingSearchSchema,
  search: { middlewares: [stripSearchParams(issueListingDefaultValues)] },
});
