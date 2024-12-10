import { z } from 'zod';

import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import {
  defaultValidadorValues,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';

const defaultValues = {
  tableFilter: {
    buildsTable: defaultValidadorValues.buildsTableFilter,
    bootsTable: defaultValidadorValues.testsTableFilter,
    testsTable: defaultValidadorValues.testsTableFilter,
  },
};

const buildDetailsSearchSchema = z.object({
  tableFilter: zTableFilterInfoValidator,
});

export const Route = createFileRoute('/build/$buildId')({
  validateSearch: buildDetailsSearchSchema,
  search: { middlewares: [stripSearchParams(defaultValues)] },
});
