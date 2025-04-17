import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import type { SearchSchema } from '@/types/general';

export const treeLatestDefaultValues = {
  gitCommitHash: undefined,
};

export const TreeLatestSchema = z.object({
  gitCommitHash: z.optional(z.string()).catch(undefined),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/tree/$treeName/$branch')({
  validateSearch: TreeLatestSchema,
  search: { middlewares: [stripSearchParams(treeLatestDefaultValues)] },
});
