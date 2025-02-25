import {
  createFileRoute,
  redirect,
  stripSearchParams,
} from '@tanstack/react-router';

import {
  issueDetailsDefaultValues,
  issueDetailsSearchSchema,
} from '@/routes/_main/issue/$issueId/route';

export const Route = createFileRoute('/_main/(alternatives)/i/$issueId')({
  loaderDeps: ({ search }) => ({ search }),
  loader: ({ deps, params }) => {
    throw redirect({
      to: '/issue/$issueId',
      search: deps.search,
      params,
    });
  },
  validateSearch: issueDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(issueDetailsDefaultValues)] },
});
