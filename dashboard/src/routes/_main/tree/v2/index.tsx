import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import TreeListingNew from '@/pages/TreeListing/TreesV2';

export const TreeSearchSchema = z.object({
  treeSearch: z.string().catch(''),
});

export const Route = createFileRoute('/_main/tree/v2/')({
  component: () => (
    <TreeListingNew
      urlFromMap={{ search: '/_main/tree/v2', navigate: '/tree/v2' }}
    />
  ),
});
