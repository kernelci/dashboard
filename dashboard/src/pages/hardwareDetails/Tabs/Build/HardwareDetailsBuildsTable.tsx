import type { ColumnDef } from '@tanstack/react-table';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import { TableHeader } from '@/components/Table/TableHeader';

import {
  zTableFilterInfoDefault,
  type AccordionItemBuilds,
  type BuildsTableFilter,
} from '@/types/tree/TreeDetails';
import { defaultBuildColumns } from '@/components/BuildsTable/DefaultBuildsColumns';

export interface THardwareDetailsBuildsTable {
  buildItems: AccordionItemBuilds[];
  hardwareId: string;
}

const hardwareDetailsBuildColumns: ColumnDef<AccordionItemBuilds>[] = [
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="hardwareDetails.treeBranch" />
    ),
  },
  ...defaultBuildColumns,
];

export function HardwareDetailsBuildsTable({
  buildItems,
  hardwareId,
}: THardwareDetailsBuildsTable): JSX.Element {
  const { tableFilter } = useSearch({ from: '/hardware/$hardwareId' });

  const navigate = useNavigate({ from: '/hardware/$hardwareId' });

  const navigateToBuildDetails = useCallback(
    (buildId: string) => {
      navigate({
        to: `/hardware/${hardwareId}/build/${buildId}`,
        params: { hardwareId },
        search: prev => prev,
      });
    },
    [navigate, hardwareId],
  );

  const onClickFilter = useCallback(
    (filter: BuildsTableFilter) => {
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
      onClickShowBuild={navigateToBuildDetails}
    />
  );
}
