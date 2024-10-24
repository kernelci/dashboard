import { createRootRoute, Outlet } from '@tanstack/react-router';

// Uncomment for TanStack Router  devtools
// eslint-disable-next-line import/no-extraneous-dependencies
// import { TanStackRouterDevtools } from '@tanstack/router-devtools';

import { z } from 'zod';

import SideMenu from '@/components/SideMenu/SideMenu';
import TopBar from '@/components/TopBar/TopBar';
import { zOrigin } from '@/types/tree/Tree';
import { DEFAULT_TIME_SEARCH } from '@/pages/treeConstants';

export const RootSearchSchema = z.object({
  origin: zOrigin,
  intervalInDays: z.optional(z.number().min(1).catch(DEFAULT_TIME_SEARCH)),
});

export const Route = createRootRoute({
  validateSearch: RootSearchSchema,
  component: () => (
    <>
      <div className="h-full w-full">
        <div className="flex w-full flex-row justify-between">
          <SideMenu />
          <TopBar />
          <div className="w-full bg-lightGray px-16 pt-24">
            <Outlet />
          </div>
        </div>
      </div>
      {/* <TanStackRouterDevtools /> */}
    </>
  ),
});
