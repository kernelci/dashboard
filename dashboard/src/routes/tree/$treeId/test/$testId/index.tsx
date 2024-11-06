import { createFileRoute } from '@tanstack/react-router';

import TreeTestDetails from '@/pages/TreeTestDetails/TreeTestDetails';

export const Route = createFileRoute('/tree/$treeId/test/$testId/')({
  component: () => <TreeTestDetails />,
});
