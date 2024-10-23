import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  PaginationState,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';

import { useCallback, useMemo, useState } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { MdChevronRight } from 'react-icons/md';

import { FormattedMessage, useIntl } from 'react-intl';

import {
  possibleTestsTableFilter,
  TestByCommitHash,
  TestHistory,
  TestsTableFilter,
  TTestByCommitHashResponse,
} from '@/types/tree/TreeDetails';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { getStatusGroup } from '@/utils/status';

import BaseTable, { TableHead } from '../Table/BaseTable';
import { TableBody, TableCell, TableRow } from '../ui/table';

import TableStatusFilter from '../Table/TableStatusFilter';

import { NewTableHeader } from './NewTableHeader';
import { PaginationInfo } from './PaginationInfo';

const columns: ColumnDef<TestByCommitHash>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.path',
        intlDefaultMessage: 'Path',
      }),
  },
  {
    accessorKey: 'status',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.status',
        intlDefaultMessage: 'Status',
        tooltipId: 'bootsTab.statusTooltip',
      }),
  },
  {
    accessorKey: 'startTime',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'buildDetails.startTime',
        intlDefaultMessage: 'Start time',
      }),
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
    header: ({ column }): JSX.Element =>
      NewTableHeader({
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
    cell: (): JSX.Element => <MdChevronRight />,
  },
];

interface IBootsTable {
  treeId: string;
  testHistory: TestHistory[];
}

export function NewBootsTable({
  treeId,
  testHistory,
}: IBootsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const { tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });
  const [bootsSelectedFilter, setBootsSelectedFilter] =
    useState<TestsTableFilter>(tableFilter.bootsTable);

  const navigate = useNavigate({ from: '/tree/$treeId' });
  const intl = useIntl();

  const rawData = useMemo(
    (): TTestByCommitHashResponse => ({
      tests: testHistory.map(
        (e): TestByCommitHash => ({
          duration: e.duration?.toString() ?? '',
          id: e.id,
          path: e.path,
          startTime: e.startTime,
          status: e.status,
        }),
      ),
    }),
    [testHistory],
  );

  const data = useMemo((): TestByCommitHash[] => {
    const filterToApply = tableFilter.bootsTable;
    if (filterToApply === 'all') {
      return rawData?.tests;
    }
    return rawData?.tests.filter(test => {
      return getStatusGroup(test.status) === filterToApply;
    });
  }, [rawData?.tests, tableFilter]);

  const onClickRow = useCallback(
    (id: string) => {
      navigate({
        to: '/tree/$treeId/test/$testId',
        params: {
          treeId,
          testId: id,
        },
        search: s => s,
      });
    },
    [navigate, treeId],
  );

  const onClickFilter = (filter: TestsTableFilter): void => {
    setBootsSelectedFilter(filter);
    navigate({
      search: previousParams => {
        return {
          ...previousParams,
          tableFilter: {
            ...previousParams.tableFilter,
            bootsTable: filter,
          },
        };
      },
    });
  };

  const checkIfFilterIsSelected = useCallback(
    (filter: TestsTableFilter): boolean => {
      return bootsSelectedFilter === filter;
    },
    [bootsSelectedFilter],
  );

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage({ id: 'global.all' }),
        value: possibleTestsTableFilter[0],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[0]),
      },
      {
        label: intl.formatMessage({ id: 'global.success' }),
        value: possibleTestsTableFilter[1],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[1]),
      },
      {
        label: intl.formatMessage({ id: 'global.failed' }),
        value: possibleTestsTableFilter[2],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[2]),
      },
      {
        label: intl.formatMessage({ id: 'global.inconclusive' }),
        value: possibleTestsTableFilter[3],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[3]),
      },
    ],
    [intl, checkIfFilterIsSelected],
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
      pagination,
    },
  });

  return (
    <div className="flex flex-col gap-6 pb-4">
      <TableStatusFilter
        filters={filters}
        onClickTest={(filter: TestsTableFilter) => onClickFilter(filter)}
      />
      <PaginationInfo
        table={table}
        pagination={pagination}
        data={data}
        label="boots"
      />
      <BaseTable
        headers={[]}
        headerComponents={table.getHeaderGroups()[0].headers.map(header => {
          return (
            <TableHead key={header.id}>
              {header.isPlaceholder
                ? null
                : flexRender(
                    header.column.columnDef.header,
                    header.getContext(),
                  )}
            </TableHead>
          );
        })}
      >
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map(row => (
              <TableRow
                key={row.id}
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
                <FormattedMessage id="global.noResults" />
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </BaseTable>
      <PaginationInfo
        table={table}
        pagination={pagination}
        data={data}
        label="boots"
      />
    </div>
  );
}
