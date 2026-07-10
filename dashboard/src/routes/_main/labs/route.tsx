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
  labsSearch: '',
  listingSize: DEFAULT_LISTING_ITEMS,
};

const zLabsSchema = z.object({
  intervalInDays: makeZIntervalInDays(REDUCED_TIME_SEARCH),
  labsSearch: z.string().catch(''),
  listingSize: zListingSize,
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/labs')({
  validateSearch: zLabsSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
