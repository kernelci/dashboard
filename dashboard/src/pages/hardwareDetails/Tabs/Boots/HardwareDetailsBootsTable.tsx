import type { ColumnDef } from '@tanstack/react-table';

import type { LinkProps } from '@tanstack/react-router';

import type { JSX } from 'react';

import {
  DETAILS_COLUMN_ID,
  MoreDetailsIcon,
  MoreDetailsTableHeader,
} from '@/components/Table/DetailsColumn';
import { TableHeader } from '@/components/Table/TableHeader';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { getStatusGroup } from '@/utils/status';

import type {
  TestByCommitHash,
  PossibleTableFilters,
} from '@/types/tree/TreeDetails';
import type { TestHistory } from '@/types/general';

import type { TableKeys } from '@/utils/constants/tables';

import { BootsTable } from '@/components/BootsTable/BootsTable';
import { UNKNOWN_STRING } from '@/utils/constants/backend';

export const columns: ColumnDef<TestByCommitHash>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.path" />
    ),
  },
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.treeBranch" />
    ),
  },
  {
    accessorKey: 'status',
    filterFn: (row, columnId, filterValue) =>
      getStatusGroup(row.getValue(columnId)) === filterValue,
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="global.status"
        tooltipId="boots.statusTooltip"
      />
    ),
  },
  {
    id: 'lab',
    accessorKey: 'lab',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.lab" />
    ),
    cell: ({ row }): string => {
      return row.getValue('lab') || UNKNOWN_STRING;
    },
  },
  {
    accessorKey: 'startTime',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="buildDetails.startTime" />
    ),
    cell: ({ row }): JSX.Element => (
      <TooltipDateTime
        dateTime={row.getValue('startTime')}
        lineBreak={true}
        showLabelTime={true}
        showLabelTZ={true}
      />
    ),
  },
  {
    accessorKey: 'duration',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.duration" />
    ),
    cell: ({ row }): string =>
      row.getValue('duration') ? row.getValue('duration') : '-',
  },
  {
    id: DETAILS_COLUMN_ID,
    header: (): JSX.Element => <MoreDetailsTableHeader />,
    cell: (): JSX.Element => <MoreDetailsIcon />,
    meta: {
      dataTestId: 'details-button',
    },
  },
];

interface IHardwareBootsTable {
  tableKey: TableKeys;
  testHistory?: TestHistory[];
  filter: PossibleTableFilters;
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  onClickFilter: (newFilter: PossibleTableFilters) => void;
  updatePathFilter?: (pathFilter: string) => void;
  currentPathFilter?: string;
}

export const HardwareDetailsBootsTable = ({
  tableKey,
  testHistory,
  filter,
  getRowLink,
  onClickFilter,
  updatePathFilter,
  currentPathFilter,
}: IHardwareBootsTable): JSX.Element => {
  return (
    <BootsTable
      tableKey={tableKey}
      getRowLink={getRowLink}
      filter={filter}
      testHistory={testHistory}
      columns={columns}
      onClickFilter={onClickFilter}
      updatePathFilter={updatePathFilter}
      currentPathFilter={currentPathFilter}
    />
  );
};
