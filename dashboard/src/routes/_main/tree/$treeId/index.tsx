import { createFileRoute } from '@tanstack/react-router';

import TreeDetails from '@/pages/TreeDetails/TreeDetails';

export const Route = createFileRoute('/_main/tree/$treeId/')({
  component: TreeDetails,
});
