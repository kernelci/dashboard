import { createFileRoute } from '@tanstack/react-router';

import TreeComparePage from '@/pages/TreeCompare/TreeComparePage';

export const Route = createFileRoute(
  '/_main/tree/$treeName/$branch/compare/',
)({
  component: TreeComparePage,
});
