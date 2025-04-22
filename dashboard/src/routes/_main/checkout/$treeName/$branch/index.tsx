import { createFileRoute } from '@tanstack/react-router';

import { TreeLatest } from '@/pages/TreeLatest';

export const Route = createFileRoute('/_main/checkout/$treeName/$branch/')({
  component: () => <TreeLatest urlFrom="/_main/checkout/$treeName/$branch/" />,
});
