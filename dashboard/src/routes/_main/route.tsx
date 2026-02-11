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
        <div className="flex w-full flex-row">
          <SideMenu />
          <main className="flex min-h-screen min-w-0 flex-1 flex-col">
            <TopBar />
            <div className="bg-light-gray h-full w-full px-8 pt-24 md:px-16">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
      {/*     <TanStackRouterDevtools /> */}
    </>
  );
};

// the treeListing controls the search, but it doesn't control the topbar
// we should give the topbar the control of the search as well since they are in the same place (pagewise)
// the listings should check the search by the url since that's where we are storing state
// with the topbar having control over the search, we can change responsivity all at once in there

// steps:
// X remove searchbar from treeListing
// X add searchbar to topbar
// X validate behavior (validate as in check and make sure it is correct)
// add simple responsivity to topbar
// validate behavior
// propagate changes to hardware and issue listing

export const Route = createFileRoute('/_main')({
  component: RouteComponent,
});
