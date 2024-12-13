import type { ColumnDef } from '@tanstack/react-table';

import { MdCheck, MdClose } from 'react-icons/md';

import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback } from 'react';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { ItemType } from '@/components/ListingItem/ListingItem';
import { TableHeader } from '@/components/Table/TableHeader';
import { TooltipDateTime } from '@/components/TooltipDateTime';

import type {
  AccordionItemBuilds,
  BuildsTableFilter,
} from '@/types/tree/TreeDetails';

export interface THardwareDetailsBuildsTable {
  buildItems: AccordionItemBuilds[];
  hardwareId: string;
}

const buildStatusMap = {
  valid: <MdCheck className="text-green" />,
  invalid: <MdClose className="text-red" />,
  null: <span>-</span>,
};

const columns: ColumnDef<AccordionItemBuilds>[] = [
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="hardwareDetails.treeBranch" />
    ),
  },
  {
    accessorKey: 'config',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.config" />
    ),
  },
  {
    accessorKey: 'architecture',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.arch" />
    ),
  },
  {
    accessorKey: 'compiler',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.compiler" />
    ),
  },
  {
    accessorKey: 'date',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.date" />
    ),
    cell: ({ row }): JSX.Element => (
      <TooltipDateTime
        dateTime={row.getValue('date')}
        lineBreak={true}
        showLabelTime={true}
        showLabelTZ={true}
      />
    ),
  },
  {
    accessorKey: 'buildErrors',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.buildErrors" />
    ),
    cell: ({ row }): JSX.Element => (
      <ColoredCircle
        className="max-w-6"
        quantity={row.getValue('buildErrors')}
        backgroundClassName={
          (row.getValue('buildErrors') as number) > 0
            ? ItemType.Error
            : ItemType.None
        }
      />
    ),
  },
  {
    accessorKey: 'buildTime',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.buildTime" />
    ),
    cell: ({ row }): JSX.Element => {
      return row.getValue('buildTime');
    },
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="global.status"
        tooltipId="build.statusTooltip"
      />
    ),
    cell: ({ row }): JSX.Element => {
      return buildStatusMap[
        row.getValue('status') as keyof typeof buildStatusMap
      ];
    },
    filterFn: 'equals',
  },
];

export function HardwareDetailsBuildsTable({
  buildItems,
  hardwareId,
}: THardwareDetailsBuildsTable): JSX.Element {
  const { tableFilter } = useSearch({ from: '/hardware/$hardwareId' });

  const navigate = useNavigate({ from: '/hardware/$hardwareId/' });

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
              buildsTable: filter,
              bootsTable: previousParams.tableFilter?.bootsTable ?? 'all',
              testsTable: previousParams.tableFilter?.testsTable ?? 'all',
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
      columns={columns}
      onClickFilter={onClickFilter}
      onClickShowBuild={navigateToBuildDetails}
    />
  );
}
