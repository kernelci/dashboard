import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  treeDetailsDefaultValues,
  treeDetailsSearchSchema,
} from '@/routes/_main/tree/$treeId/route';

export const Route = createFileRoute('/_main/tree/$treeName/$branch/$hash')({
  validateSearch: treeDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(treeDetailsDefaultValues)] },
});
