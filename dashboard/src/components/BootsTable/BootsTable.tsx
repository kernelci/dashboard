import type { ColumnDef, SortingState } from '@tanstack/react-table';
import {
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from '@tanstack/react-table';

import { useCallback, useEffect, useMemo, useState, type JSX } from 'react';
import type { LinkProps } from '@tanstack/react-router';

import { FormattedMessage, useIntl } from 'react-intl';

import type {
  TestByCommitHash,
  PossibleTableFilters,
  TTestByCommitHashResponse,
} from '@/types/tree/TreeDetails';
import { possibleTableFilters } from '@/types/tree/TreeDetails';

import { getStatusGroup } from '@/utils/status';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import type { TestHistory } from '@/types/general';

import { PaginationInfo } from '@/components/Table/PaginationInfo';
import { useTestIssues } from '@/api/testDetails';
import { useLogData } from '@/hooks/useLogData';
import WrapperTableWithLogSheet from '@/pages/TreeDetails/Tabs/WrapperTableWithLogSheet';
import { usePaginationState } from '@/hooks/usePaginationState';
import { useLayoutTable } from '@/hooks/useLayoutTable';

import type { TableKeys } from '@/utils/constants/tables';

import { TableRowMemoized } from '@/components/Table/TableComponents';
import { TableFrame } from '@/components/Table/TableFrame';

import { buildHardwareArray, buildTreeBranch } from '@/utils/table';

import {
  DETAILS_COLUMN_ID,
  MoreDetailsIcon,
  MoreDetailsTableHeader,
} from '@/components/Table/DetailsColumn';
import { TableHeader } from '@/components/Table/TableHeader';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import TooltipHardware from '@/components/Table/TooltipHardware';
import { EMPTY_VALUE } from '@/lib/string';
import { UNKNOWN_STRING } from '@/utils/constants/backend';
import { TableTopFilters } from '@/components/Table/TableTopFilters';
import type { TStatusFilters } from '@/components/Table/TableStatusFilter';

const defaultColumns: ColumnDef<TestByCommitHash>[] = [
  {
    accessorKey: 'path',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.path" />
    ),
    meta: {
      headerIntlKey: 'global.path',
      isRowHeader: true,
      minWidth: 160,
      maxWidth: 400,
    },
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
    meta: {
      headerIntlKey: 'global.status',
      minWidth: 100,
      maxWidth: 160,
    },
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
    meta: {
      headerIntlKey: 'buildDetails.startTime',
      minWidth: 140,
      maxWidth: 220,
    },
  },
  {
    accessorKey: 'duration',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.duration" />
    ),
    cell: ({ row }): string =>
      row.getValue('duration') ? row.getValue('duration') : '-',
    meta: {
      headerIntlKey: 'global.duration',
      minWidth: 100,
      maxWidth: 160,
    },
  },
  {
    id: 'lab',
    accessorKey: 'lab',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.lab" />
    ),
    cell: ({ row }): string => {
      return row.getValue('lab') || UNKNOWN_STRING;
    },
    meta: {
      headerIntlKey: 'global.lab',
      minWidth: 100,
      maxWidth: 200,
    },
  },
  {
    accessorKey: 'hardware',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.hardware" />
    ),
    cell: ({ row }): JSX.Element | string => {
      return <TooltipHardware hardwares={row.original.hardware} />;
    },
    meta: {
      headerIntlKey: 'global.hardware',
      minWidth: 120,
      maxWidth: 280,
    },
  },
  {
    id: DETAILS_COLUMN_ID,
    header: (): JSX.Element => <MoreDetailsTableHeader />,
    cell: (): JSX.Element => <MoreDetailsIcon />,
    enableResizing: false,
    meta: {
      minWidth: 64,
      maxWidth: 96,
    },
  },
];

interface IBootsTable {
  tableKey: TableKeys;
  testHistory?: TestHistory[];
  filter: PossibleTableFilters;
  columns?: ColumnDef<TestByCommitHash>[];
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  onClickFilter: (newFilter: PossibleTableFilters) => void;
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
  const [globalFilter, setGlobalFilter] = useState<string | undefined>(
    currentPathFilter,
  );

  const intl = useIntl();

  const rawData = useMemo(
    (): TTestByCommitHashResponse => ({
      tests: testHistory
        ? testHistory.map((e): TestByCommitHash => {
            if (!e.path) {
              e.path = EMPTY_VALUE;
            }

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
              lab: e.lab,
            };
          })
        : [],
    }),
    [testHistory],
  );

  const testsData = useMemo(() => rawData.tests, [rawData]);

  const {
    table,
    containerRef,
    columnWidths,
    tableWidth,
    columnsMenu,
    tableHeaders,
  } = useLayoutTable({
    data: testsData,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: paginationUpdater,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      pagination,
      globalFilter,
    },
  });

  const filterCount: Record<PossibleTableFilters, number> = useMemo(() => {
    const count: Record<PossibleTableFilters, number> = {
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
    (possibleFilter: PossibleTableFilters): boolean => {
      return possibleFilter === filter;
    },
    [filter],
  );

  const filters: TStatusFilters[] = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleTableFilters[0]] },
        ),
        value: possibleTableFilters[0],
        isSelected: checkIfFilterIsSelected(possibleTableFilters[0]),
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleTableFilters[1]] },
        ),
        value: possibleTableFilters[1],
        isSelected: checkIfFilterIsSelected(possibleTableFilters[1]),
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleTableFilters[2]] },
        ),
        value: possibleTableFilters[2],
        isSelected: checkIfFilterIsSelected(possibleTableFilters[2]),
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleTableFilters[3]] },
        ),
        value: possibleTableFilters[3],
        isSelected: checkIfFilterIsSelected(possibleTableFilters[3]),
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
      setGlobalFilter(e.target.value);
      if (updatePathFilter) {
        updatePathFilter(e.target.value);
      }
    },
    [updatePathFilter],
  );

  const modelRows = table.getRowModel().rows;

  const sortedItems = useMemo(
    (): TestByCommitHash[] => modelRows.map(row => row.original),
    [modelRows],
  );

  const [currentLogId, setLog] = useState<string | undefined>(undefined);

  const currentLog = useMemo(() => {
    const index = sortedItems.findIndex(item => item.id === currentLogId);
    return index === -1 ? undefined : index;
  }, [sortedItems, currentLogId]);

  const activeLogId = currentLog !== undefined ? currentLogId ?? '' : '';

  const onOpenChange = useCallback(() => setLog(undefined), [setLog]);
  const openLogSheet = useCallback(
    (index: number) => setLog(sortedItems[index]?.id),
    [setLog, sortedItems],
  );

  useEffect(() => {
    if (
      currentLogId !== undefined &&
      !sortedItems.some(item => item.id === currentLogId)
    ) {
      setLog(undefined);
    }
  }, [currentLogId, sortedItems]);

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
          columnWidths={columnWidths}
        />
      ))
    ) : (
      <TableRow key="no-results">
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [
    modelRows,
    getRowLink,
    openLogSheet,
    currentLog,
    columns.length,
    columnWidths,
  ]);

  const handlePreviousItem = useCallback(() => {
    if (currentLog !== undefined && currentLog > 0) {
      setLog(sortedItems[currentLog - 1]?.id);
    }
  }, [setLog, currentLog, sortedItems]);

  const handleNextItem = useCallback(() => {
    if (currentLog !== undefined && currentLog < sortedItems.length - 1) {
      setLog(sortedItems[currentLog + 1]?.id);
    }
  }, [setLog, currentLog, sortedItems]);

  const { data: logData, isLoading } = useLogData(activeLogId, 'test');

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
    return getRowLink(logData?.id ?? '');
  }, [logData?.id, getRowLink]);

  const { data: issues, status, error } = useTestIssues(activeLogId);

  return (
    <WrapperTableWithLogSheet
      currentLog={currentLog}
      logData={logData}
      navigationLogsActions={navigationLogsActions}
      onOpenChange={onOpenChange}
      currentLinkProps={currentLinkProps}
      issues={issues}
      status={status}
      error={error}
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <TableTopFilters
          key="bootsTableSearch"
          filters={filters}
          onClickFilter={onClickFilter}
          onSearchChange={onSearchChange}
          currentPathFilter={currentPathFilter}
        />
        {columnsMenu}
      </div>
      <TableFrame
        containerRef={containerRef}
        tableWidth={tableWidth}
        headerComponents={tableHeaders}
      >
        <TableBody>{tableRows}</TableBody>
      </TableFrame>
      <PaginationInfo table={table} intlLabel="global.boots" />
    </WrapperTableWithLogSheet>
  );
}
