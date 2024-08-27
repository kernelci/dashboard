import { createFileRoute } from '@tanstack/react-router';

import TreeDetails from '@/pages/TreeDetails/TreeDetails';

export const Route = createFileRoute('/tree/$treeId/')({
  component: TreeDetails,
});
