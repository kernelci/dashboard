import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

import { LogViewer } from '@/pages/LogViewer';

const logViewerSchema = z.object({
  url: z.string(),
  type: z.enum(['build', 'test']).optional().catch(undefined),
  itemId: z.string().optional(),
});

export const Route = createFileRoute('/log-viewer')({
  validateSearch: logViewerSchema,
  component: LogViewer,
});
