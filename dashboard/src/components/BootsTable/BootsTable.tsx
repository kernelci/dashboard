import type {
  Cell,
  ColumnDef,
  PaginationState,
  Row,
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

import { memo, useCallback, useEffect, useMemo, useState } from 'react';
import type { LinkProps } from '@tanstack/react-router';

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
import { useTestDetails } from '@/api/testDetails';
import WrapperTable from '@/pages/TreeDetails/Tabs/WrapperTable';
import { cn } from '@/lib/utils';

const columns: ColumnDef<TestByCommitHash>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'global.path',
        intlDefaultMessage: 'Path',
      }),
  },
  {
    accessorKey: 'status',
    filterFn: (row, columnId, filterValue) =>
      getStatusGroup(row.getValue(columnId)) === filterValue,
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'global.status',
        intlDefaultMessage: 'Status',
        tooltipId: 'boots.statusTooltip',
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
        intlKey: 'global.duration',
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
  testHistory: TestHistory[];
  filter: TestsTableFilter;
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  onClickFilter: (newFilter: TestsTableFilter) => void;
  updatePathFilter?: (pathFilter: string) => void;
  currentPathFilter?: string;
}

const TableCellComponent = ({
  cell,
  rowId,
  rowIndex,
  openLogSheet,
  getRowLink,
}: {
  cell: Cell<TestByCommitHash, unknown>;
  rowId: TestHistory['id'];
  rowIndex: number;
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  openLogSheet: (index: number) => void;
}): JSX.Element => {
  const handleClick = useCallback(
    () => openLogSheet(rowIndex),
    [rowIndex, openLogSheet],
  );

  const parsedHandleClick =
    cell.column.id === 'status' ? handleClick : undefined;
  const parsedLinkProps: LinkProps =
    cell.column.id === 'status' ? { search: s => s } : getRowLink(rowId);

  return (
    <TableCellWithLink
      onClick={parsedHandleClick}
      key={cell.id}
      linkProps={parsedLinkProps}
    >
      {flexRender(cell.column.columnDef.cell, cell.getContext())}
    </TableCellWithLink>
  );
};

const TableRowComponent = ({
  row,
  index,
  currentLog,
  getRowLink,
  openLogSheet,
}: {
  row: Row<TestByCommitHash>;
  index: number;
  currentLog?: number;
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  openLogSheet: (index: number) => void;
}): JSX.Element => {
  const className = index === currentLog ? 'bg-lightBlue' : undefined;

  return (
    <TableRow
      className={cn('cursor-pointer hover:bg-lightBlue', className)}
      key={row.id}
    >
      {row.getVisibleCells().map((cell, cellIdx) => (
        <TableCellMemoized
          key={cellIdx}
          cell={cell}
          rowId={row.original.id}
          rowIndex={index}
          getRowLink={getRowLink}
          openLogSheet={openLogSheet}
        />
      ))}
    </TableRow>
  );
};

const TableCellMemoized = memo(TableCellComponent);
const TableRowMemoized = memo(TableRowComponent);

// TODO: would be useful if the navigation happened within the table, so the parent component would only be required to pass the navigation url instead of the whole function for the update and the currentPath diffFilter (boots/tests Table)
export function BootsTable({
  testHistory,
  filter,
  getRowLink,
  onClickFilter,
  updatePathFilter,
  currentPathFilter,
}: IBootsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

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

  const testsData = useMemo(() => rawData.tests, [rawData]);

  const table = useReactTable({
    data: testsData,
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

  const { globalFilter } = table.getState();

  const filterCount: Record<(typeof possibleTestsTableFilter)[number], number> =
    useMemo(() => {
      const count = {
        all: 0,
        success: 0,
        failed: 0,
        inconclusive: 0,
      };

      const rowsOriginal = table
        .getPrePaginationRowModel()
        .rows.map(row => row.original);

      const dataFilter = globalFilter ? rowsOriginal : testsData;

      count.all = dataFilter.length;
      dataFilter.forEach(test => count[getStatusGroup(test.status)]++);

      return count;
    }, [testsData, globalFilter, table]);

  const checkIfFilterIsSelected = useCallback(
    (possibleFilter: TestsTableFilter): boolean => {
      return possibleFilter === filter;
    },
    [filter],
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

  useEffect(() => {
    table
      .getColumn('status')
      ?.setFilterValue(filter !== 'all' ? filter : undefined);
  }, [filter, table]);

  const onSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.value !== undefined && updatePathFilter) {
        updatePathFilter(e.target.value);
      }
      if (updatePathFilter === undefined) {
        table.setGlobalFilter(String(e.target.value));
      }
    },
    [table, updatePathFilter],
  );

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      const headerComponent = header.isPlaceholder
        ? null
        : // the header must change the icon when sorting changes,
          // but just the column dependency won't trigger the rerender
          // so we pass an unused sorting prop here to force the useMemo dependency
          flexRender(header.column.columnDef.header, {
            ...header.getContext(),
            sorting,
          });
      return (
        <TableHead key={header.id} className="border-b px-2 font-bold">
          {header.id === 'path' ? (
            <div className="flex items-center">
              {headerComponent}
              <DebounceInput
                key={currentPathFilter}
                debouncedSideEffect={onSearchChange}
                startingValue={currentPathFilter}
                className="w-50 font-normal"
                type="text"
                placeholder={intl.formatMessage({ id: 'global.search' })}
              />
            </div>
          ) : (
            headerComponent
          )}
        </TableHead>
      );
    });
  }, [currentPathFilter, groupHeaders, intl, onSearchChange, sorting]);

  const modelRows = table.getRowModel().rows;

  const sortedItems = useMemo(
    (): TestByCommitHash[] => modelRows.map(row => row.original),
    [modelRows],
  );

  const [currentLog, setLog] = useState<number | undefined>(undefined);

  const onOpenChange = useCallback(() => setLog(undefined), [setLog]);
  const openLogSheet = useCallback((index: number) => setLog(index), [setLog]);

  const tableRows = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map((row, idx) => (
        <TableRowMemoized
          getRowLink={getRowLink}
          openLogSheet={openLogSheet}
          currentLog={currentLog}
          key={idx}
          index={idx}
          row={row}
        />
      ))
    ) : (
      <TableRow key="no-results">
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [modelRows, getRowLink, openLogSheet, currentLog]);

  const handlePreviousItem = useCallback(() => {
    setLog(previousLog => {
      if (typeof previousLog === 'number' && previousLog > 0)
        return previousLog - 1;

      return previousLog;
    });
  }, [setLog]);

  const handleNextItem = useCallback(() => {
    setLog(previousLog => {
      if (
        typeof previousLog === 'number' &&
        previousLog < sortedItems.length - 1
      )
        return previousLog + 1;

      return previousLog;
    });
  }, [setLog, sortedItems.length]);

  const { data: dataTest, isLoading } = useTestDetails(
    sortedItems.length > 0 ? sortedItems[currentLog ?? 0].id : '',
  );

  const navigationLogsActions = useMemo(
    () => ({
      nextItem: handleNextItem,
      hasNext:
        typeof currentLog === 'number' && currentLog < sortedItems.length - 1,
      previousItem: handlePreviousItem,
      hasPrevious: !!currentLog,
      isLoading,
    }),
    [
      currentLog,
      isLoading,
      sortedItems.length,
      handleNextItem,
      handlePreviousItem,
    ],
  );

  return (
    <WrapperTable
      currentLog={currentLog}
      logExcerpt={dataTest?.log_excerpt}
      logUrl={dataTest?.log_url}
      navigationLogsActions={navigationLogsActions}
      onOpenChange={onOpenChange}
    >
      <TableStatusFilter filters={filters} onClickTest={onClickFilter} />
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.boots" />
    </WrapperTable>
  );
}
