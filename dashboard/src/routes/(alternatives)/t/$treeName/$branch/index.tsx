import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/(alternatives)/t/$treeName/$branch/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/tree/$treeName/$branch',
      search: deps.search,
      params,
    });
  },
});
