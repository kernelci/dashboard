import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_main/(alternatives)/b/$buildId/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/build/$buildId',
      search: deps.search,
      params,
    });
  },
});
