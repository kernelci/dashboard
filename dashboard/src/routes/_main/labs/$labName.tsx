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
  treeIndexes: null,
};

const labDetailsSearchSchema = z.object({
  currentPageTab: zPossibleTabValidator,
  treeIndexes: z
    .array(z.union([z.string(), z.number()]))
    .transform(values => values.map(String))
    .nullable()
    .default(null),
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/labs/$labName')({
  validateSearch: labDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
  component: LabDetails,
});
