import { createFileRoute } from '@tanstack/react-router';

import BuildDetails from '@/pages/BuildDetails/BuildDetails';

export const Route = createFileRoute('/tree/$treeId/build/$buildId/')({
  component: BuildDetails,
});
