import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zPossibleValidator } from '@/types/tree/TreeDetails';

const hardwareDetailsSearchSchema = z.object({
  currentPageTab: zPossibleValidator,
});

export const Route = createFileRoute('/hardware/$hardwareId')({
  validateSearch: hardwareDetailsSearchSchema,
});
