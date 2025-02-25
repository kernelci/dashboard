import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import Trees from '@/pages/Trees';

export const TreeSearchSchema = z.object({
  treeSearch: z.string().catch(''),
});

export const Route = createFileRoute('/_main/tree/')({
  component: Trees,
});
