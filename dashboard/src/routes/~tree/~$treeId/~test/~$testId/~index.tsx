import { createFileRoute } from '@tanstack/react-router';

import TestDetails from '@/pages/TestDetails/TestDetails';

export const Route = createFileRoute('/tree/$treeId/test/$testId/')({
  component: () => <TestDetails />,
});
