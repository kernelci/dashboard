import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_main/(alternatives)/i/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/issues',
      search: deps.search,
      params,
    });
  },
});
