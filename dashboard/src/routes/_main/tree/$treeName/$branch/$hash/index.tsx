import { createFileRoute } from '@tanstack/react-router';

import { TreeLatest } from '@/pages/TreeLatest';

export const Route = createFileRoute('/_main/tree/$treeName/$branch/$hash/')({
  component: () => {
    return <TreeLatest urlFrom="/_main/tree/$treeName/$branch/$hash/" />;
  },
});
