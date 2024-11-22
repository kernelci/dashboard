import type { ColumnDef } from '@tanstack/react-table';

import { useCallback, type ReactElement } from 'react';

import { MdCheck, MdClose } from 'react-icons/md';

import { useNavigate, useParams, useSearch } from '@tanstack/react-router';

import { BuildsTable } from '@/components/BuildsTable/BuildsTable';
import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { ItemType } from '@/components/ListingItem/ListingItem';
import { TableHeader } from '@/components/Table/TableHeader';
import { TooltipDateTime } from '@/components/TooltipDateTime';
import type {
  AccordionItemBuilds,
  BuildsTableFilter,
} from '@/types/tree/TreeDetails';

export interface TTreeDetailsBuildsTable {
  buildItems: AccordionItemBuilds[];
}

type BuildStatus = Record<AccordionItemBuilds['status'], ReactElement>;

const buildStatusMap: BuildStatus = {
  valid: <MdCheck className="text-green" />,
  invalid: <MdClose className="text-red" />,
  null: <span>-</span>,
};

const columns: ColumnDef<AccordionItemBuilds>[] = [
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
      return buildStatusMap[row.getValue('status') as keyof BuildStatus];
    },
    filterFn: 'equals',
  },
];

export function TreeDetailsBuildsTable({
  buildItems,
}: TTreeDetailsBuildsTable): JSX.Element {
  const { treeId } = useParams({ from: '/tree/$treeId/' });
  const { tableFilter } = useSearch({ from: '/tree/$treeId/' });
  const navigate = useNavigate({ from: '/tree/$treeId/' });

  const navigateToBuildDetails = useCallback(
    (buildId: string) => {
      navigate({
        to: `/tree/${treeId}/build/${buildId}`,
        params: { treeId },
        search: prev => prev,
      });
    },
    [navigate, treeId],
  );

  const onClickFilter = useCallback(
    (newFilter: BuildsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              buildsTable: newFilter,
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
      onClickShowBuild={navigateToBuildDetails}
      filter={tableFilter.buildsTable}
      buildItems={buildItems}
      columns={columns}
      onClickFilter={onClickFilter}
    />
  );
}
