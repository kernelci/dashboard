import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import Trees from '@/pages/Trees';

export const TreeSearchSchema = z.object({
  treeSearch: z.string().optional().catch(undefined),
});

export const Route = createFileRoute('/tree/')({
  component: Trees,
});
