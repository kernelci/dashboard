import {
  createRootRoute,
  Outlet,
  stripSearchParams,
} from '@tanstack/react-router';
import type { JSX } from 'react';

import { z } from 'zod';

import {
  DEFAULT_ORIGIN,
  type SearchSchema,
  zOrigin,
  zTableSortValidator,
} from '@/types/general';

const defaultValues = {
  origin: DEFAULT_ORIGIN,
  tableSort: undefined,
};

const RouteSchema = z.object({
  origin: zOrigin,
  tableSort: zTableSortValidator,
} satisfies SearchSchema);

const RouteComponent = (): JSX.Element => {
  return <Outlet />;
};

export const Route = createRootRoute({
  validateSearch: RouteSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
  component: RouteComponent,
});
