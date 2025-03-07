import { createFileRoute, Outlet } from '@tanstack/react-router';

// Uncomment for TanStack Router  devtools

// import { TanStackRouterDevtools } from '@tanstack/router-devtools';

import { useIntl } from 'react-intl';

import type { JSX } from 'react';

import SideMenu from '@/components/SideMenu/SideMenu';
import TopBar from '@/components/TopBar/TopBar';

const RouteComponent = (): JSX.Element => {
  const { formatMessage } = useIntl();

  return (
    <>
      <title>{formatMessage({ id: 'title.default' })}</title>
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
  );
};

export const Route = createFileRoute('/_main')({
  component: RouteComponent,
});
