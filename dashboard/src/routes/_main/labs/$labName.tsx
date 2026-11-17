import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import LabDetails from '@/pages/Labs/LabDetails';

import {
  DEFAULT_DIFF_FILTER,
  type SearchSchema,
  zDiffFilter,
} from '@/types/general';
import {
  defaultValidadorValues,
  zPossibleTabValidator,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';

const defaultValues = {
  currentPageTab: defaultValidadorValues.tab,
  treeIndexes: null,
  tableFilter: zTableFilterInfoDefault,
  diffFilter: DEFAULT_DIFF_FILTER,
};

const labDetailsSearchSchema = z.object({
  currentPageTab: zPossibleTabValidator,
  treeIndexes: z
    .array(z.union([z.string(), z.number()]))
    .transform(values => values.map(String))
    .nullable()
    .default(null),
  tableFilter: zTableFilterInfoValidator,
  diffFilter: zDiffFilter,
} satisfies SearchSchema);

export const Route = createFileRoute('/_main/labs/$labName')({
  validateSearch: labDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
  component: LabDetails,
});
