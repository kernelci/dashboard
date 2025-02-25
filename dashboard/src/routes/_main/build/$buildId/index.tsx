import { createFileRoute } from '@tanstack/react-router';

import BuildDetailsPage from '@/pages/BuildDetails';

export const Route = createFileRoute('/_main/build/$buildId/')({
  component: () => <BuildDetailsPage />,
});
