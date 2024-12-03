import { createFileRoute } from '@tanstack/react-router';

import TestDetailsPage from '@/pages/TestDetails/TestDetails';

export const Route = createFileRoute('/test/$testId/')({
  component: () => <TestDetailsPage />,
});
