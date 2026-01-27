import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import Trees from '@/pages/TreeListing/Trees';

export const TreeSearchSchema = z.object({
  treeSearch: z.string().catch(''),
});

export const Route = createFileRoute('/_main/tree/v1/')({
  component: () => (
    <Trees urlFromMap={{ search: '/_main/tree/v1', navigate: '/tree/v1' }} />
  ),
});
