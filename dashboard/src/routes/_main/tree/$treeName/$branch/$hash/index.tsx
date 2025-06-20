import { createFileRoute } from '@tanstack/react-router';

import TreeDetails from '@/pages/TreeDetails/TreeDetails';

export const Route = createFileRoute('/_main/tree/$treeName/$branch/$hash/')({
  component: () => (
    <TreeDetails urlFrom="/_main/tree/$treeName/$branch/$hash" />
  ),
});
