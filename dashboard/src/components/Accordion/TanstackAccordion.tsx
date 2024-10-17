// Os headers depende do tipo build/teste
// O corpo deve ser apenas uma tabela com os valores

import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';
import { useCallback, useState } from 'react';

import { ArrowUpDown } from 'lucide-react';

import { FormattedMessage } from 'react-intl';

import { MdChevronRight } from 'react-icons/md';

import { useNavigate } from '@tanstack/react-router';

import { TIndividualTest } from '@/types/general';

import { Button } from '@/components/ui/button';

import BaseTable from '@/components/Table/BaseTable';
import {
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@/components/ui/table';

import { TooltipDateTime } from '../TooltipDateTime';

const ChevronRightAnimate = (): JSX.Element => {
  return (
    <MdChevronRight className="transition group-data-[state='open']:rotate-90" />
  );
};

// o corpo vai ser uma tabela normal sem os headers

interface ITanstackAccordion {
  data: TIndividualTest[];
}

const columns: ColumnDef<TIndividualTest>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          <FormattedMessage
            key="testDetails.path"
            id="testDetails.path"
            defaultMessage="Path"
          ></FormattedMessage>
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          <FormattedMessage
            key="testDetails.status"
            id="testDetails.status"
            defaultMessage="Status"
          ></FormattedMessage>
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
  },
  {
    accessorKey: 'start_time',
    header: ({ column }): JSX.Element => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          <FormattedMessage
            key="global.date"
            id="global.date"
            defaultMessage="Date"
          ></FormattedMessage>
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }): JSX.Element => (
      <TableCell>
        <TooltipDateTime
          dateTime={row.getValue('start_time')}
          lineBreak={true}
          showLabelTime={true}
          showLabelTZ={true}
        />
      </TableCell>
    ),
  },
  {
    accessorKey: 'duration',
    header: ({ column }): JSX.Element => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          <FormattedMessage
            key="testDetails.duration"
            id="testDetails.duration"
            defaultMessage="Duration"
          ></FormattedMessage>
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }): string =>
      row.getValue('duration') ? row.getValue('duration') : '-',
  },
  {
    id: 'chevron',
    cell: (): JSX.Element => <ChevronRightAnimate />,
  },
];

export function IndividualTestsTable({
  data,
}: ITanstackAccordion): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const navigate = useNavigate({ from: '/tree/$treeId' });

  const onClickRow = useCallback(
    (testId: string) => {
      navigate({
        to: '/tree/$treeId/test/$testId',
        params: {
          testId: testId,
        },
        search: s => s,
      });
    },
    [navigate],
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    manualPagination: true,
    state: {
      sorting,
      columnFilters,
    },
  });

  return (
    <BaseTable
      headers={[]}
      headerComponents={table.getHeaderGroups()[0].headers.map(header => {
        return (
          <TableHead key={header.id}>
            {header.isPlaceholder
              ? null
              : flexRender(header.column.columnDef.header, header.getContext())}
          </TableHead>
        );
      })}
    >
      <TableBody>
        {table.getRowModel().rows?.length ? (
          table.getRowModel().rows.map(row => (
            <TableRow
              key={row.id}
              data-state={row.getIsSelected() && 'selected'}
              onClick={() => {
                onClickRow(data[row.index].id);
              }}
            >
              {row.getVisibleCells().map(cell => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))
        ) : (
          <TableRow>
            <TableCell colSpan={columns.length} className="h-24 text-center">
              No results.
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </BaseTable>
  );
}
