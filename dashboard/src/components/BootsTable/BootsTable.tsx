import type { ColumnDef, SortingState } from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { useCallback, useEffect, useMemo, useState } from 'react';
import type { LinkProps } from '@tanstack/react-router';

import { FormattedMessage, useIntl } from 'react-intl';

import type {
  TestByCommitHash,
  TestsTableFilter,
  TTestByCommitHashResponse,
} from '@/types/tree/TreeDetails';
import { possibleTestsTableFilter } from '@/types/tree/TreeDetails';

import { getStatusGroup } from '@/utils/status';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import type { TestHistory } from '@/types/general';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import TableStatusFilter from '@/components/Table/TableStatusFilter';

import { PaginationInfo } from '@/components/Table/PaginationInfo';
import DebounceInput from '@/components/DebounceInput/DebounceInput';
import { useTestDetails, useTestIssues } from '@/api/testDetails';
import WrapperTableWithLogSheet from '@/pages/TreeDetails/Tabs/WrapperTableWithLogSheet';
import { usePaginationState } from '@/hooks/usePaginationState';

import type { TableKeys } from '@/utils/constants/tables';

import { TableRowMemoized } from '@/components/Table/TableComponents';

import { buildHardwareArray, buildTreeBranch } from '@/utils/table';

import {
  DETAILS_COLUMN_ID,
  MoreDetailsIcon,
  MoreDetailsTableHeader,
} from '@/components/Table/DetailsColumn';
import { TableHeader } from '@/components/Table/TableHeader';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import TooltipHardware from '@/components/Table/TooltipHardware';

const defaultColumns: ColumnDef<TestByCommitHash>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.path" />
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
    accessorKey: 'hardware',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.hardware" />
    ),
    cell: ({ row }): JSX.Element | string => {
      return <TooltipHardware hardwares={row.original.hardware} />;
    },
  },
  {
    id: DETAILS_COLUMN_ID,
    header: (): JSX.Element => <MoreDetailsTableHeader />,
    cell: (): JSX.Element => <MoreDetailsIcon />,
  },
];

interface IBootsTable {
  tableKey: TableKeys;
  testHistory?: TestHistory[];
  filter: TestsTableFilter;
  columns?: ColumnDef<TestByCommitHash>[];
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  onClickFilter: (newFilter: TestsTableFilter) => void;
  updatePathFilter?: (pathFilter: string) => void;
  currentPathFilter?: string;
}

// TODO: would be useful if the navigation happened within the table, so the parent component would only be required to pass the navigation url instead of the whole function for the update and the currentPath diffFilter (boots/tests Table)
export function BootsTable({
  tableKey,
  testHistory,
  filter,
  columns = defaultColumns,
  getRowLink,
  onClickFilter,
  updatePathFilter,
  currentPathFilter,
}: IBootsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const { pagination, paginationUpdater } = usePaginationState(tableKey);

  const intl = useIntl();

  const rawData = useMemo(
    (): TTestByCommitHashResponse => ({
      tests: testHistory
        ? testHistory.map((e): TestByCommitHash => {
            return {
              duration: e.duration?.toString() ?? '',
              id: e.id,
              path: e.path,
              startTime: e.start_time,
              status: e.status,
              hardware: buildHardwareArray(
                e.environment_compatible,
                e.environment_misc,
              ),
              treeBranch: buildTreeBranch(e.tree_name, e.git_repository_branch),
            };
          })
        : [],
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
    onPaginationChange: paginationUpdater,
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
        <TableRowMemoized<TestByCommitHash>
          key={idx}
          index={idx}
          row={row}
          openLogSheet={openLogSheet}
          currentLog={currentLog}
          getRowLink={getRowLink}
        />
      ))
    ) : (
      <TableRow key="no-results">
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [modelRows, getRowLink, openLogSheet, currentLog, columns.length]);

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

  const currentLinkProps = useMemo(() => {
    return getRowLink(dataTest?.id ?? '');
  }, [dataTest?.id, getRowLink]);

  const {
    data: issues,
    status,
    error,
  } = useTestIssues(
    currentLog !== undefined ? sortedItems[currentLog]?.id : '',
  );

  return (
    <WrapperTableWithLogSheet
      currentLog={currentLog}
      logExcerpt={dataTest?.log_excerpt}
      logUrl={dataTest?.log_url}
      navigationLogsActions={navigationLogsActions}
      onOpenChange={onOpenChange}
      currentLinkProps={currentLinkProps}
      issues={issues}
      status={status}
      error={error}
    >
      <TableStatusFilter filters={filters} onClickTest={onClickFilter} />
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.boots" />
    </WrapperTableWithLogSheet>
  );
}
