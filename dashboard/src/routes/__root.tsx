import { createRootRoute, Outlet } from '@tanstack/react-router';

import { z } from 'zod';

// Uncomment for TanStack Router  devtools
// eslint-disable-next-line import/no-extraneous-dependencies
// import { TanStackRouterDevtools } from '@tanstack/router-devtools';

import SideMenu from '@/components/SideMenu/SideMenu';
import TopBar from '@/components/TopBar/TopBar';

import { zOrigin } from '@/types/general';

const RouteSchema = z.object({
  origin: zOrigin,
});

export const Route = createRootRoute({
  validateSearch: RouteSchema,
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
      {/*     <TanStackRouterDevtools /> */}
    </>
  ),
});
