import { z } from 'zod';

import {
  createRootRoute,
  Outlet,
  stripSearchParams,
} from '@tanstack/react-router';

// Uncomment for TanStack Router  devtools
// eslint-disable-next-line import/no-extraneous-dependencies
// import { TanStackRouterDevtools } from '@tanstack/router-devtools';

import SideMenu from '@/components/SideMenu/SideMenu';
import TopBar from '@/components/TopBar/TopBar';

import { DEFAULT_ORIGIN, type SearchSchema, zOrigin } from '@/types/general';

const defaultValues = {
  origin: DEFAULT_ORIGIN,
};

const RouteSchema = z.object({
  origin: zOrigin,
} satisfies SearchSchema);

export const Route = createRootRoute({
  validateSearch: RouteSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
  component: () => (
    <>
      <div className="h-full w-full">
        <div className="flex w-full flex-row justify-between">
          <SideMenu />
          <TopBar />
          <div className="bg-light-gray w-full px-16 pt-24">
            <Outlet />
          </div>
        </div>
      </div>
      {/*     <TanStackRouterDevtools /> */}
    </>
  ),
});
