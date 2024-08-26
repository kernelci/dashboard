import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import { zOrigin } from '@/types/tree/Tree';

import {
  zPossibleValidator,
  zBuildsTableFilterValidator,
  zDiffFilter,
  zTreeInformation,
  zTestsTableFilterValidator,
  possibleBuildsTableFilter,
  possibleTestsTableFilter,
} from '@/types/tree/TreeDetails';

import TreeDetails from '@/pages/TreeDetails/TreeDetails';

const treeDetailsSearchSchema = z
  .object({
    currentTreeDetailsTab: zPossibleValidator,
    tableFilter: z.enum([
      ...possibleBuildsTableFilter,
      ...possibleTestsTableFilter,
    ]),
    diffFilter: zDiffFilter,
    testPath: z.string().optional().catch(''),
    origin: zOrigin,
    treeInfo: zTreeInformation,
  })
  .superRefine((data, context) => {
    if (data.currentTreeDetailsTab === 'treeDetails.builds') {
      const validation = zBuildsTableFilterValidator.safeParse(
        data.tableFilter,
      );
      if (!validation.success) {
        context.addIssue({
          code: z.ZodIssueCode.custom,
          message: `Invalid table filter for builds table: ${data.tableFilter}`,
          path: ['tableFilter'],
        });
      }
    } else {
      const validation = zTestsTableFilterValidator.safeParse(data.tableFilter);
      if (!validation.success) {
        context.addIssue({
          code: z.ZodIssueCode.custom,
          message: `Invalid table filter for tests table: ${data.tableFilter}`,
          path: ['tableFilter'],
        });
      }
    }
  });

export const Route = createFileRoute('/tree/$treeId/')({
  validateSearch: treeDetailsSearchSchema,
  component: TreeDetails,
});
