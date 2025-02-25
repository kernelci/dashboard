import {
  createFileRoute,
  redirect,
  stripSearchParams,
} from '@tanstack/react-router';

import {
  issueListingDefaultValues,
  issueListingSearchSchema,
} from '@/routes/_main/issue/route';

export const Route = createFileRoute('/_main/(alternatives)/i')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/issue',
      search: deps.search,
      params,
    });
  },
  validateSearch: issueListingSearchSchema,
  search: { middlewares: [stripSearchParams(issueListingDefaultValues)] },
});
