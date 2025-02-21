import type { ColumnDef } from '@tanstack/react-table';

import { useCallback, type JSX } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import type { ITestsTable } from '@/components/TestsTable/TestsTable';
import { TestsTable } from '@/components/TestsTable/TestsTable';
import { TableHeader } from '@/components/Table/TableHeader';
import type { TIndividualTest } from '@/types/general';
import { TooltipDateTime } from '@/components/TooltipDateTime';

import {
  DETAILS_COLUMN_ID,
  MoreDetailsIcon,
  MoreDetailsTableHeader,
} from '@/components/Table/DetailsColumn';

const innerColumns: ColumnDef<TIndividualTest>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.path" />
    ),
    cell: ({ row }): JSX.Element => {
      return (
        <Tooltip>
          <TooltipTrigger>
            <div className="max-w-80 overflow-clip text-nowrap text-ellipsis">
              {row.getValue('path')}
            </div>
          </TooltipTrigger>
          <TooltipContent>{row.getValue('path')}</TooltipContent>
        </Tooltip>
      );
    },
  },
  {
    accessorKey: 'treeBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.treeBranch" />
    ),
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.status" />
    ),
  },
  {
    accessorKey: 'start_time',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.date" />
    ),
    cell: ({ row }): JSX.Element => (
      <div className="text-nowrap">
        <TooltipDateTime
          dateTime={row.getValue('start_time')}
          showLabelTime={true}
        />
      </div>
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
  },
];

interface IHardwareDetailsTestTable
  extends Omit<ITestsTable, 'columns' | 'innerColumns ' | 'getRowLink'> {
  hardwareId: string;
}

const HardwareDetailsTestTable = ({
  tableKey,
  filter,
  onClickFilter,
  testHistory,
  hardwareId,
  updatePathFilter,
  currentPathFilter,
}: IHardwareDetailsTestTable): JSX.Element => {
  const getRowLink = useCallback(
    (bootId: string): LinkProps => ({
      to: '/hardware/$hardwareId/test/$testId',
      params: {
        testId: bootId,
        hardwareId: hardwareId,
      },
      search: s => s,
    }),
    [hardwareId],
  );

  return (
    <TestsTable
      tableKey={tableKey}
      filter={filter}
      onClickFilter={onClickFilter}
      testHistory={testHistory}
      innerColumns={innerColumns}
      getRowLink={getRowLink}
      updatePathFilter={updatePathFilter}
      currentPathFilter={currentPathFilter}
    />
  );
};

export default HardwareDetailsTestTable;
