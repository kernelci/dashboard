import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  makeZIntervalInDays,
  zListingSize,
  type SearchSchema,
} from '@/types/general';
import {
  DEFAULT_LISTING_INTERVAL_IN_DAYS,
  DEFAULT_LISTING_ITEMS,
} from '@/utils/constants/general';

const defaultValues = {
  intervalInDays: DEFAULT_LISTING_INTERVAL_IN_DAYS,
  treeSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
};

export const RootSearchSchema = z.object({
  intervalInDays: makeZIntervalInDays(DEFAULT_LISTING_INTERVAL_IN_DAYS),
  treeSearch: z.string().catch(''),
  listingSize: zListingSize,
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/tree')({
  validateSearch: RootSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
