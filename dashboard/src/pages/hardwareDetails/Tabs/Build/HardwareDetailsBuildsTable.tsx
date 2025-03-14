import type { ColumnDef } from '@tanstack/react-table';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo, type JSX } from 'react';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import { TableHeader } from '@/components/Table/TableHeader';

import {
  zTableFilterInfoDefault,
  type AccordionItemBuilds,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';
import { defaultBuildColumns } from '@/components/BuildsTable/DefaultBuildsColumns';
import { sanitizeBuilds } from '@/utils/utils';
import type { BuildsTabBuild } from '@/types/general';

export interface THardwareDetailsBuildsTable {
  buildsData?: BuildsTabBuild[];
  hardwareId: string;
}

const hardwareDetailsBuildColumns: ColumnDef<AccordionItemBuilds>[] = [
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.treeBranch" />
    ),
  },
  ...defaultBuildColumns,
];

export function HardwareDetailsBuildsTable({
  buildsData,
  hardwareId,
}: THardwareDetailsBuildsTable): JSX.Element {
  const { tableFilter } = useSearch({ from: '/_main/hardware/$hardwareId' });

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const buildItems = useMemo(() => sanitizeBuilds(buildsData), [buildsData]);

  const getRowLink = useCallback(
    (buildId: string): LinkProps => ({
      to: '/hardware/$hardwareId/build/$buildId',
      params: {
        buildId: buildId,
        hardwareId: hardwareId,
      },
      search: s => ({
        origin: s.origin,
      }),
    }),
    [hardwareId],
  );

  const onClickFilter = useCallback(
    (filter: PossibleTableFilters) => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              ...(previousParams.tableFilter ?? zTableFilterInfoDefault),
              buildsTable: filter,
            },
          };
        },
        state: s => s,
      });
    },
    [navigate],
  );

  return (
    <BuildsTable
      tableKey="hardwareDetailsBuilds"
      filter={tableFilter.buildsTable}
      buildItems={buildItems}
      columns={hardwareDetailsBuildColumns}
      onClickFilter={onClickFilter}
      getRowLink={getRowLink}
    />
  );
}
