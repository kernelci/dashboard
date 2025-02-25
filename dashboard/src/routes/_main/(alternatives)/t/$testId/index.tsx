import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_main/(alternatives)/t/$testId/')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/test/$testId',
      search: deps.search,
      params,
    });
  },
});
