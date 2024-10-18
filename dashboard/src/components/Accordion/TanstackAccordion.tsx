// Os headers depende do tipo build/teste
// O corpo deve ser apenas uma tabela com os valores

import {
  Column,
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';
import { useCallback, useMemo, useState } from 'react';

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

import { MessagesKey } from '@/locales/messages';

import { TooltipDateTime } from '../TooltipDateTime';

const ChevronRightAnimate = (): JSX.Element => {
  return (
    <MdChevronRight className="transition group-data-[state='open']:rotate-90" />
  );
};

interface INewTable {
  data: TIndividualTest[];
  columnDefinition: ColumnDef<TIndividualTest>[];
}

interface INewTableColumnHeader {
  column: Column<TIndividualTest>;
  sortable: boolean;
  intlKey: MessagesKey;
  intlDefaultMessage: string;
}

function NewTableColumnHeader({
  column,
  sortable,
  intlKey,
  intlDefaultMessage,
}: INewTableColumnHeader): JSX.Element {
  return (
    <Button
      variant="ghost"
      className="w-full justify-start px-2"
      onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
    >
      <FormattedMessage
        key={intlKey}
        id={intlKey}
        defaultMessage={intlDefaultMessage}
      ></FormattedMessage>
      {sortable && <ArrowUpDown className="ml-2 h-4 w-4" />}
    </Button>
  );
}

export const individualTestColumns: ColumnDef<TIndividualTest>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element =>
      NewTableColumnHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.path',
        intlDefaultMessage: 'Path',
      }),
    // if there is no cell, it will default to simple text
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element =>
      NewTableColumnHeader({
        column: column,
        sortable: false,
        intlKey: 'testDetails.status',
        intlDefaultMessage: 'Status',
      }),
  },
  {
    accessorKey: 'start_time',
    header: ({ column }): JSX.Element =>
      NewTableColumnHeader({
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
      NewTableColumnHeader({
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

export function NewTable({ data, columnDefinition }: INewTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const navigate = useNavigate({ from: '/tree/$treeId' });

  const columns = useMemo(() => {
    return columnDefinition;
  }, [columnDefinition]);

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
