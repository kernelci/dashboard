import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/(alternatives)/t/$treeId/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/tree/$treeId',
      search: deps.search,
      params,
    });
  },
});
