import { createFileRoute } from '@tanstack/react-router';

import { TreeLatest } from '@/pages/TreeLatest';

export const Route = createFileRoute(
  '/_main/(alternatives)/c/$treeName/$branch/',
)({
  component: () => (
    <TreeLatest urlFrom="/_main/(alternatives)/c/$treeName/$branch/" />
  ),
});
