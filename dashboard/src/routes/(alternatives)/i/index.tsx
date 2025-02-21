import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/(alternatives)/i/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/issue',
      search: deps.search,
      params,
    });
  },
});
