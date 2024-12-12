import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import Trees from '@/pages/Trees';
import { DEFAULT_TREE_SEARCH } from '@/pages/treeConstants';

export const TreeSearchSchema = z.object({
  treeSearch: z.string().catch(DEFAULT_TREE_SEARCH),
});

export const Route = createFileRoute('/tree/')({
  component: Trees,
});
