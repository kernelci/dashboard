import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  compareDefaultValues,
  compareSearchSchema,
} from '@/types/tree/TreeCompare';

export const Route = createFileRoute(
  '/_main/tree/$treeName/$branch/compare',
)({
  validateSearch: compareSearchSchema,
  search: { middlewares: [stripSearchParams(compareDefaultValues)] },
});
