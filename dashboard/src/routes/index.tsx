import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';

import { zOrigin, zSection } from '@/types/tree/Tree';

import Trees from '../pages/Trees';

export const HomeSearchSchema = z.object({
  origin: zOrigin,
  section: zSection,
});

export const Route = createFileRoute('/')({
  validateSearch: HomeSearchSchema,
  component: Trees,
});
