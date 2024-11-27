import type { ColumnDef } from '@tanstack/react-table';

import { useCallback } from 'react';

import type { LinkProps } from '@tanstack/react-router';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import type { ITestsTable } from '@/components/TestsTable/TestsTable';
import { TestsTable } from '@/components/TestsTable/TestsTable';
import { TableHeader } from '@/components/Table/TableHeader';
import type { TIndividualTest } from '@/types/general';
import { TooltipDateTime } from '@/components/TooltipDateTime';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';

//TODO: move 18n to global.
const innerColumns: ColumnDef<TIndividualTest>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.path',
        intlDefaultMessage: 'Path',
      }),
    cell: ({ row }): JSX.Element => {
      return (
        <Tooltip>
          <TooltipTrigger>
            <div className="max-w-80 overflow-clip text-ellipsis text-nowrap">
              {row.getValue('path')}
            </div>
          </TooltipTrigger>
          <TooltipContent>{row.getValue('path')}</TooltipContent>
        </Tooltip>
      );
    },
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.status',
        intlDefaultMessage: 'Status',
      }),
  },
  {
    accessorKey: 'start_time',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'global.date',
        intlDefaultMessage: 'Date',
      }),
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
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.duration',
        intlDefaultMessage: 'Duration',
      }),
    cell: ({ row }): string =>
      row.getValue('duration') ? row.getValue('duration') : '-',
  },
  {
    id: 'chevron',
    cell: (): JSX.Element => <ChevronRightAnimate />,
  },
];

interface IHardwareDetailsTestTable
  extends Omit<ITestsTable, 'columns' | 'innerColumns ' | 'getRowLink'> {
  hardwareId: string;
}

const HardwareDetailsTestTable = ({
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
