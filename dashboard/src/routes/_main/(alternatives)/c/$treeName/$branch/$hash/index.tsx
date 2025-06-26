import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute(
  '/_main/(alternatives)/c/$treeName/$branch/$hash/',
)({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/tree/$treeName/$branch/$hash',
      search: deps.search,
      params,
    });
  },
});
