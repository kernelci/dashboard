import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

import { LogViewer } from '@/pages/LogViewer';

const logViewerSchema = z.object({
  url: z.string(),
});

export const Route = createFileRoute('/log-viewer')({
  validateSearch: logViewerSchema,
  component: LogViewer,
});
