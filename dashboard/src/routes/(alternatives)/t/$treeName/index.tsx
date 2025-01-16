import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/(alternatives)/t/$treeName/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/tree/$treeName',
      search: deps.search,
      params,
    });
  },
});
