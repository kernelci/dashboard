import { createFileRoute, stripSearchParams } from '@tanstack/react-router';

import { z } from 'zod';

import {
  defaultValidadorValues,
  zPossibleTabValidator,
  zTableFilterInfoDefault,
  zTableFilterInfoValidator,
} from '@/types/tree/TreeDetails';

import { zTreeCommits } from '@/types/hardware/hardwareDetails';
import {
  DEFAULT_HARDWARE_DIFF_FILTER,
  DEFAULT_ORIGIN,
  type SearchSchema,
  zDiffFilter,
} from '@/types/general';

const defaultValues = {
  currentPageTab: defaultValidadorValues.tab,
  treeIndexes: null,
  treeCommits: {},
  tableFilter: zTableFilterInfoDefault,
  diffFilter: DEFAULT_HARDWARE_DIFF_FILTER,
  hardwareSearch: '',
};
const hardwareDetailsSearchSchema = z
  .object({
    origin: z.string().optional().catch(undefined),
    currentPageTab: zPossibleTabValidator,
    treeIndexes: z
      .array(z.union([z.string(), z.number()]))
      .transform(values => values.map(String))
      .nullable()
      .default(null),
    treeCommits: zTreeCommits,
    tableFilter: zTableFilterInfoValidator,
    diffFilter: zDiffFilter
      .removeCatch()
      .removeDefault()
      .default(DEFAULT_HARDWARE_DIFF_FILTER)
      .catch(DEFAULT_HARDWARE_DIFF_FILTER),
    hardwareSearch: z.string().catch(''),
  } satisfies SearchSchema)
  // Old `?o=` is the test origin, with checkout and build origin open.
  // Root injects maestro, so only another value is mapped and those defaults are dropped.
  .transform(({ origin, ...search }) => {
    if (!origin || origin === DEFAULT_ORIGIN) {
      return search;
    }
    const {
      checkoutOrigins: _,
      buildOrigin: __,
      ...diffFilter
    } = search.diffFilter;
    return {
      ...search,
      diffFilter: {
        ...diffFilter,
        testOrigin: diffFilter.testOrigin ?? { [origin]: true },
      },
    };
  });

export const Route = createFileRoute('/_main/hardware/$hardwareId')({
  validateSearch: hardwareDetailsSearchSchema,
  search: {
    middlewares: [
      stripSearchParams(defaultValues),
      // Drop `o` after mapping it, or clearing the filter leaves it and the next load restores it.
      // @ts-expect-error origin is required on the root schema, so it is not an optional details param
      stripSearchParams(['origin']),
    ],
  },
});
