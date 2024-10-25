import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';
import { useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import { TIndividualTest } from '@/types/general';

import BaseTable from '@/components/Table/BaseTable';
import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableHead,
  TableRow,
} from '@/components/ui/table';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';

import { TableHeader } from '@/components/Table/TableHeader';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { sanitizeTableValue } from '@/components/Table/tableUtils';

const columns: ColumnDef<TIndividualTest>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.path',
        intlDefaultMessage: 'Path',
      }),
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
      <TooltipDateTime
        dateTime={row.getValue('start_time')}
        lineBreak={true}
        showLabelTime={true}
        showLabelTZ={true}
      />
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
    id: 'hardware',
    accessorKey: 'hardware',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeDetails.hardware',
        intlDefaultMessage: 'Hardware',
      }),
    cell: ({ row }): JSX.Element => (
      <TooltipHardware hardwares={row.getValue('hardware')} />
    ),
  },
  {
    id: 'chevron',
    cell: (): JSX.Element => <ChevronRightAnimate />,
  },
];

const TooltipHardware = ({
  hardwares,
}: {
  hardwares: string[] | undefined;
}): JSX.Element => {
  const hardwaresTooltip = useMemo(() => {
    return hardwares
      ? hardwares.map(hardware => (
          <div key={hardware} className="text-center">
            <span>{hardware}</span>
            <br />
          </div>
        ))
      : '-';
  }, [hardwares]);

  return (
    <Tooltip>
      <TooltipTrigger>
        {sanitizeTableValue(hardwares?.[0], false)}
      </TooltipTrigger>
      <TooltipContent>{hardwaresTooltip}</TooltipContent>
    </Tooltip>
  );
};

export function IndividualTestsTable({
  data,
}: {
  data: TIndividualTest[];
}): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    manualPagination: true,
    state: {
      sorting,
    },
  });

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead
          key={header.id}
          className="border-b px-2 font-bold text-black"
        >
          {header.isPlaceholder
            ? null
            : flexRender(header.column.columnDef.header, header.getContext())}
        </TableHead>
      );
    });
    // TODO: remove exhaustive-deps and change memo  (all tables)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupHeaders, sorting]);

  const modelRows = table.getRowModel().rows;
  const tableRows = useMemo((): JSX.Element[] => {
    return modelRows?.length
      ? modelRows.map(row => (
          <TableRow
            key={row.id}
            data-state={row.getIsSelected() && 'selected'}
            className="cursor-pointer hover:bg-lightBlue"
          >
            {row.getVisibleCells().map(cell => (
              <TableCellWithLink
                key={cell.id}
                linkProps={{
                  to: '/tree/$treeId/test/$testId',
                  params: {
                    testId: row.original.id,
                  },
                  search: s => s,
                }}
              >
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </TableCellWithLink>
            ))}
          </TableRow>
        ))
      : [
          <TableRow key="no-results">
            <TableCell colSpan={columns.length} className="h-24 text-center">
              <FormattedMessage id="global.noResults" />
            </TableCell>
          </TableRow>,
        ];
  }, [modelRows]);

  return (
    <BaseTable headerComponents={tableHeaders}>
      <TableBody>{...tableRows}</TableBody>
    </BaseTable>
  );
}
