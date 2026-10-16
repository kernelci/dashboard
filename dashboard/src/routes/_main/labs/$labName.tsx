import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import LabDetails from '@/pages/Labs/LabDetails';

import {
  defaultValidadorValues,
  zPossibleTabValidator,
} from '@/types/tree/TreeDetails';
import type { SearchSchema } from '@/types/general';

const defaultValues = {
  currentPageTab: defaultValidadorValues.tab,
  labDetailsPreview: undefined,
};

const labDetailsSearchSchema = z.object({
  currentPageTab: zPossibleTabValidator,
  labDetailsPreview: z.literal('empty').optional().catch(undefined),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/labs/$labName')({
  validateSearch: labDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
  component: LabDetails,
});
