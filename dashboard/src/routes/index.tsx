import { createFileRoute, redirect } from '@tanstack/react-router';
import { z } from 'zod';

export const HomeSearchSchema = z.object({
  treeSearch: z.string().optional().catch(undefined),
});

export const Route = createFileRoute('/')({
  validateSearch: HomeSearchSchema,
  loader: ctx => {
    return redirect({ to: '/tree', search: ctx.location.search });
  },
});
