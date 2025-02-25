import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_main/(alternatives)/i/$issueId/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/issue/$issueId',
      search: deps.search,
      params,
    });
  },
});
