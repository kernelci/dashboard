import {
  createFileRoute,
  redirect,
  stripSearchParams,
} from '@tanstack/react-router';

import {
  buildDetailsDefaultValues,
  buildDetailsSearchSchema,
} from '@/routes/build/$buildId/route';

export const Route = createFileRoute('/(alternatives)/b/$buildId')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/build/$buildId',
      search: deps.search,
      params,
    });
  },
  validateSearch: buildDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(buildDetailsDefaultValues)] },
});
