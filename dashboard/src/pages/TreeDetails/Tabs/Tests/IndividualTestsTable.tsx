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

import { useNavigate } from '@tanstack/react-router';

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

import { ChevronRightAnimate } from '@/components/Table/Chevron';

import { TableHeader } from '@/components/Table/TableHeader';

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
    id: 'chevron',
    cell: (): JSX.Element => <ChevronRightAnimate />,
  },
];

export function IndividualTestsTable({
  data,
}: {
  data: TIndividualTest[];
}): JSX.Element {
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
          <TableHead
            key={header.id}
            className="border-b px-2 font-bold text-black"
          >
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
              className="cursor-pointer hover:bg-lightBlue"
              onClick={() => {
                onClickRow(data[row.index].id);
              }}
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
        ) : (
          <TableRow>
            <TableCell colSpan={columns.length} className="h-24 text-center">
              <FormattedMessage id="global.noResults" />
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </BaseTable>
  );
}
