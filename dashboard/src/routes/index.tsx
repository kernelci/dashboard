import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

import Trees from '@/pages/Trees';

export const HomeSearchSchema = z.object({
  treeSearch: z.string().optional().catch(undefined),
});

export const Route = createFileRoute('/')({
  validateSearch: HomeSearchSchema,
  component: Trees,
});
