import type {
  ColumnDef,
  PaginationState,
  SortingState,
} from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { useCallback, useMemo, useState } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { MdChevronRight } from 'react-icons/md';

import { FormattedMessage, useIntl } from 'react-intl';

import type {
  TestByCommitHash,
  TestsTableFilter,
  TTestByCommitHashResponse,
} from '@/types/tree/TreeDetails';
import { possibleTestsTableFilter } from '@/types/tree/TreeDetails';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { getStatusGroup } from '@/utils/status';

import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableRow,
} from '@/components/ui/table';

import type { TestHistory } from '@/types/general';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import TableStatusFilter from '@/components/Table/TableStatusFilter';

import { TableHeader } from '@/components/Table/TableHeader';

import { PaginationInfo } from '@/components/Table/PaginationInfo';
import DebounceInput from '@/components/DebounceInput/DebounceInput';

const columns: ColumnDef<TestByCommitHash>[] = [
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
        tooltipId: 'bootsTab.statusTooltip',
      }),
  },
  {
    accessorKey: 'startTime',
    header: ({ column }): JSX.Element =>
      TableHeader({
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
    cell: (): JSX.Element => <MdChevronRight />,
  },
];

interface IBootsTable {
  treeId: string;
  testHistory: TestHistory[];
}

export function BootsTable({ treeId, testHistory }: IBootsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
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

  const filterCount: Record<(typeof possibleTestsTableFilter)[number], number> =
    useMemo(() => {
      const count = {
        all: 0,
        success: 0,
        failed: 0,
        inconclusive: 0,
      };
      count.all = rawData.tests.length;
      rawData.tests.forEach(test => count[getStatusGroup(test.status)]++);

      return count;
    }, [rawData.tests]);

  const onClickFilter = useCallback(
    (filter: TestsTableFilter): void => {
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
    },
    [navigate],
  );

  const checkIfFilterIsSelected = useCallback(
    (filter: TestsTableFilter): boolean => {
      return bootsSelectedFilter === filter;
    },
    [bootsSelectedFilter],
  );

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleTestsTableFilter[0]] },
        ),
        value: possibleTestsTableFilter[0],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[0]),
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleTestsTableFilter[1]] },
        ),
        value: possibleTestsTableFilter[1],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[1]),
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleTestsTableFilter[2]] },
        ),
        value: possibleTestsTableFilter[2],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[2]),
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleTestsTableFilter[3]] },
        ),
        value: possibleTestsTableFilter[3],
        isSelected: checkIfFilterIsSelected(possibleTestsTableFilter[3]),
      },
    ],
    [intl, filterCount, checkIfFilterIsSelected],
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      pagination,
    },
  });

  const onSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) =>
      table.setGlobalFilter(String(e.target.value)),
    [table],
  );

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id}>
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
  const tableRows = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <TableRow key={row.id}>
          {row.getVisibleCells().map(cell => (
            <TableCellWithLink
              key={cell.id}
              linkProps={{
                to: '/tree/$treeId/test/$testId',
                params: {
                  treeId,
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
      <TableRow key="no-results">
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [modelRows, treeId]);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex justify-between">
        <TableStatusFilter filters={filters} onClickTest={onClickFilter} />
        <DebounceInput
          debouncedSideEffect={onSearchChange}
          className="w-50"
          type="text"
          placeholder={intl.formatMessage({ id: 'global.search' })}
        />
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} data={data} intlLabel="treeDetails.boots" />
    </div>
  );
}
