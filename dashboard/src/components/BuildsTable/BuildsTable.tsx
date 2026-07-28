import type { ColumnDef, SortingState } from '@tanstack/react-table';
import {
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from '@tanstack/react-table';

import { useCallback, useEffect, useMemo, useState, type JSX } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import { PaginationInfo } from '@/components/Table/PaginationInfo';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import {
  possibleTableFilters,
  type AccordionItemBuilds,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import WrapperTableWithLogSheet from '@/pages/TreeDetails/Tabs/WrapperTableWithLogSheet';

import { usePaginationState } from '@/hooks/usePaginationState';
import { useLayoutTable } from '@/hooks/useLayoutTable';

import type { TableKeys } from '@/utils/constants/tables';

import { TableRowMemoized } from '@/components/Table/TableComponents';
import { TableFrame } from '@/components/Table/TableFrame';

import { useBuildIssues } from '@/api/buildDetails';
import { useLogData } from '@/hooks/useLogData';

import { getBuildStatusGroup } from '@/utils/status';

import { TableTopFilters } from '@/components/Table/TableTopFilters';

import type { TStatusFilters } from '@/components/Table/TableStatusFilter';

import { defaultBuildColumns } from './DefaultBuildsColumns';

export interface IBuildsTable {
  tableKey: TableKeys;
  buildItems: AccordionItemBuilds[];
  columns?: ColumnDef<AccordionItemBuilds>[];
  filter: PossibleTableFilters;
  onClickFilter: (filter: PossibleTableFilters) => void;
  getRowLink: (buildId: string) => LinkProps;
}

export function BuildsTable({
  tableKey,
  buildItems,
  columns = defaultBuildColumns,
  filter,
  onClickFilter,
  getRowLink,
}: IBuildsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const { pagination, paginationUpdater } = usePaginationState(tableKey);

  const intl = useIntl();

  const rawData = useMemo((): AccordionItemBuilds[] => {
    return buildItems?.map(row => ({
      ...row,
      config: row.config ?? '-',
      architecture: row.architecture ?? '-',
      compiler: row.compiler ?? '-',
      buildTime: row.buildTime ? (
        <span>
          {typeof row.buildTime === 'number'
            ? Math.floor(row.buildTime) + ' '
            : row.buildTime}
          <FormattedMessage id="global.seconds" />
        </span>
      ) : (
        '-'
      ),
      date: row.date,
    }));
  }, [buildItems]);

  const {
    table,
    containerRef,
    columnWidths,
    tableWidth,
    columnsMenu,
    tableHeaders,
  } = useLayoutTable({
    data: rawData,
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

  const filterCount: Record<PossibleTableFilters, number> = useMemo(() => {
    const rowsOriginal = table
      .getPrePaginationRowModel()
      .rows.map(row => row.original);

    const dataFilter = globalFilter ? rowsOriginal : rawData;

    const count: Record<PossibleTableFilters, number> = {
      all: 0,
      success: 0,
      failed: 0,
      inconclusive: 0,
    };

    count.all = dataFilter ? dataFilter.length : 0;
    dataFilter.forEach(build => count[getBuildStatusGroup(build.status)]++);

    return count;
  }, [rawData, globalFilter, table]);

  const filters: TStatusFilters[] = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleTableFilters[0]] },
        ),
        value: possibleTableFilters[0],
        isSelected: filter === possibleTableFilters[0],
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleTableFilters[1]] },
        ),
        value: possibleTableFilters[1],
        isSelected: filter === possibleTableFilters[1],
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleTableFilters[2]] },
        ),
        value: possibleTableFilters[2],
        isSelected: filter === possibleTableFilters[2],
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleTableFilters[3]] },
        ),
        value: possibleTableFilters[3],
        isSelected: filter === possibleTableFilters[3],
      },
    ],
    [intl, filterCount, filter],
  );

  useEffect(() => {
    table
      .getColumn('status')
      ?.setFilterValue(filter !== 'all' ? filter : undefined);
  }, [filter, table]);

  const onSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) =>
      table.setGlobalFilter(String(e.target.value)),
    [table],
  );

  const modelRows = table.getRowModel().rows;

  const sortedItems = useMemo(
    (): AccordionItemBuilds[] => modelRows.map(row => row.original),
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

  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    {
      return modelRows?.length ? (
        modelRows.map((row, index) => {
          return (
            <TableRowMemoized<AccordionItemBuilds>
              key={index}
              index={index}
              row={row}
              openLogSheet={openLogSheet}
              currentLog={currentLog}
              getRowLink={getRowLink}
              columnWidths={columnWidths}
            />
          );
        })
      ) : (
        <TableRow>
          <TableCell colSpan={columns.length} className="h-24 text-center">
            <FormattedMessage id="global.noResults" />
          </TableCell>
        </TableRow>
      );
    }
  }, [
    modelRows,
    columns.length,
    openLogSheet,
    currentLog,
    getRowLink,
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

  const { data: logData, isLoading } = useLogData(activeLogId, 'build');

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
    return getRowLink(sortedItems[currentLog ?? 0]?.id ?? '');
  }, [currentLog, getRowLink, sortedItems]);

  const { data: issues, status, error } = useBuildIssues(activeLogId);

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
          key="buildsTableSearch"
          filters={filters}
          onClickFilter={onClickFilter}
          onSearchChange={onSearchChange}
        />
        {columnsMenu}
      </div>
      <TableFrame
        containerRef={containerRef}
        tableWidth={tableWidth}
        headerComponents={tableHeaders}
      >
        <TableBody>{tableBody}</TableBody>
      </TableFrame>
      <PaginationInfo table={table} intlLabel="global.builds" />
    </WrapperTableWithLogSheet>
  );
}
