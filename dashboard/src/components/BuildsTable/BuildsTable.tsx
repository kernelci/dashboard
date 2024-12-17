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

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import TableStatusFilter from '@/components/Table/TableStatusFilter';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import type {
  AccordionItemBuilds,
  BuildsTableFilter,
} from '@/types/tree/TreeDetails';
import { possibleBuildsTableFilter } from '@/types/tree/TreeDetails';

import { useBuildStatusCount } from '@/api/treeDetails';
import WrapperTableWithLogSheet from '@/pages/TreeDetails/Tabs/WrapperTableWithLogSheet';

import { usePaginationState } from '@/hooks/usePaginationState';

import type { TableKeys } from '@/utils/constants/tables';

import { TableRowMemoized } from '@/components/Table/TableComponents';

import { defaultBuildColumns } from './DefaultBuildsColumns';

export interface IBuildsTable {
  tableKey: TableKeys;
  buildItems: AccordionItemBuilds[];
  columns?: ColumnDef<AccordionItemBuilds>[];
  filter: BuildsTableFilter;
  onClickFilter: (filter: BuildsTableFilter) => void;
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

  const table = useReactTable({
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

  const filterCount = useMemo(() => {
    const rowsOriginal = table
      .getPrePaginationRowModel()
      .rows.map(row => row.original);

    const dataFilter = globalFilter ? rowsOriginal : rawData;

    const count = possibleBuildsTableFilter.reduce(
      (acc, currentFilter) => {
        if (dataFilter)
          acc[currentFilter] = dataFilter?.reduce(
            (total, row) => (row.status === currentFilter ? total + 1 : total),
            0,
          );
        return acc;
      },
      {} as Record<(typeof possibleBuildsTableFilter)[number], number>,
    );
    count.all = dataFilter ? dataFilter.length : 0;

    return count;
  }, [rawData, globalFilter, table]);

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleBuildsTableFilter[2]] },
        ),
        value: possibleBuildsTableFilter[2],
        isSelected: filter === possibleBuildsTableFilter[2],
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleBuildsTableFilter[1]] },
        ),
        value: possibleBuildsTableFilter[1],
        isSelected: filter === possibleBuildsTableFilter[1],
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleBuildsTableFilter[0]] },
        ),
        value: possibleBuildsTableFilter[0],
        isSelected: filter === possibleBuildsTableFilter[0],
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleBuildsTableFilter[3]] },
        ),
        value: possibleBuildsTableFilter[3],
        isSelected: filter === possibleBuildsTableFilter[3],
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

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id} className="border-b px-0 font-bold">
          {header.isPlaceholder
            ? null
            : // the header must change the icon when sorting changes,
              // but just the column dependency won't trigger the rerender
              // so we pass an unused sorting prop here to force the useMemo dependency
              flexRender(header.column.columnDef.header, {
                ...header.getContext(),
                sorting,
              })}
        </TableHead>
      );
    });
  }, [groupHeaders, sorting]);

  const modelRows = table.getRowModel().rows;

  const sortedItems = useMemo(
    (): AccordionItemBuilds[] => modelRows.map(row => row.original),
    [modelRows],
  );

  const [currentLog, setLog] = useState<number | undefined>(undefined);

  const onOpenChange = useCallback(() => setLog(undefined), [setLog]);
  const openLogSheet = useCallback((index: number) => setLog(index), [setLog]);

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
  }, [modelRows, columns.length, openLogSheet, currentLog, getRowLink]);

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

  const { data: dataBuildCount, isLoading } = useBuildStatusCount(
    { buildId: sortedItems.length > 0 ? sortedItems[currentLog ?? 0]?.id : '' },
    { enabled: sortedItems.length > 0 && !!sortedItems[currentLog ?? 0]?.id },
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
    return getRowLink(sortedItems[currentLog ?? 0]?.id ?? '');
  }, [currentLog, getRowLink, sortedItems]);

  return (
    <WrapperTableWithLogSheet
      currentLog={currentLog}
      logExcerpt={dataBuildCount?.log_excerpt}
      logUrl={
        sortedItems.length > 0 ? sortedItems[currentLog ?? 0]?.buildLogs : ''
      }
      navigationLogsActions={navigationLogsActions}
      onOpenChange={onOpenChange}
      currentLinkProps={currentLinkProps}
    >
      <div className="flex justify-between">
        <TableStatusFilter filters={filters} onClickBuild={onClickFilter} />
        <DebounceInput
          debouncedSideEffect={onSearchChange}
          className="w-50"
          type="text"
          placeholder={intl.formatMessage({ id: 'global.search' })}
        />
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableBody}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.builds" />
    </WrapperTableWithLogSheet>
  );
}
