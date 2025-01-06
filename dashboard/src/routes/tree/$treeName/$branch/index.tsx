import { createFileRoute } from '@tanstack/react-router';

import { TreeLatest } from '@/pages/TreeLatest';

export const Route = createFileRoute('/tree/$treeName/$branch/')({
  component: TreeLatest,
});
