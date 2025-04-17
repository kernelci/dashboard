import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  treeLatestDefaultValues,
  TreeLatestSchema,
} from '@/routes/_main/tree/$treeName/$branch/route';

export const Route = createFileRoute(
  '/_main/(alternatives)/c/$treeName/$branch',
)({
  validateSearch: TreeLatestSchema,
  search: { middlewares: [stripSearchParams(treeLatestDefaultValues)] },
});
