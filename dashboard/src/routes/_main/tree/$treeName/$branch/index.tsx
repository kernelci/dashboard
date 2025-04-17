import { createFileRoute } from '@tanstack/react-router';

import { TreeLatest } from '@/pages/TreeLatest/TreeLatest';

export const Route = createFileRoute('/_main/tree/$treeName/$branch/')({
  component: TreeLatest,
});
