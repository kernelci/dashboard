import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

import { zOrigin } from '@/types/tree/Tree';

import Trees from '../pages/Trees';

export const HomeSearchSchema = z.object({
  origin: zOrigin,
});

export const Route = createFileRoute('/')({
  validateSearch: HomeSearchSchema,
  component: Trees,
});
