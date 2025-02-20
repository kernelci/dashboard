import {
  createFileRoute,
  redirect,
  stripSearchParams,
} from '@tanstack/react-router';

import {
  testDetailsDefaultValues,
  testDetailsSearchSchema,
} from '@/routes/test/$testId/route';

export const Route = createFileRoute('/(alternatives)/t/$testId')({
  validateSearch: testDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(testDetailsDefaultValues)] },
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/test/$testId',
      search: deps.search,
      params,
    });
  },
});
