import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zPossibleValidator, zTableFilterInfo } from '@/types/tree/TreeDetails';

const hardwareDetailsSearchSchema = z.object({
  currentPageTab: zPossibleValidator,
  tableFilter: zTableFilterInfo.catch({
    bootsTable: 'all',
    buildsTable: 'all',
    testsTable: 'all',
  }),
});

export const Route = createFileRoute('/hardware/$hardwareId')({
  validateSearch: hardwareDetailsSearchSchema,
});
