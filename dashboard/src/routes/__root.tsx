import { createRootRoute, Outlet } from '@tanstack/react-router';
import type { JSX } from 'react';

const RouteComponent = (): JSX.Element => {
  return <Outlet />;
};

export const Route = createRootRoute({
  component: RouteComponent,
});
