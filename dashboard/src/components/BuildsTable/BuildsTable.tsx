import type { ColumnDef, SortingState } from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { useCallback, useEffect, useMemo, useState, type JSX } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import TableStatusFilter from '@/components/Table/TableStatusFilter';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import {
  possibleTableFilters,
  type AccordionItemBuilds,
  type PossibleTableFilters,
} from '@/types/tree/TreeDetails';

import WrapperTableWithLogSheet from '@/pages/TreeDetails/Tabs/WrapperTableWithLogSheet';

import { usePaginationState } from '@/hooks/usePaginationState';

import type { TableKeys } from '@/utils/constants/tables';

import { TableRowMemoized } from '@/components/Table/TableComponents';

import { useBuildIssues } from '@/api/buildDetails';
import { useLogData } from '@/hooks/useLogData';

import { getBuildStatusGroup } from '@/utils/status';

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

  const filters = useMemo(
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
      if (typeof previousLog === 'number' && previousLog > 0) {
        return previousLog - 1;
      }

      return previousLog;
    });
  }, [setLog]);

  const handleNextItem = useCallback(() => {
    setLog(previousLog => {
      if (
        typeof previousLog === 'number' &&
        previousLog < sortedItems.length - 1
      ) {
        return previousLog + 1;
      }

      return previousLog;
    });
  }, [setLog, sortedItems.length]);

  const { data: logData, isLoading } = useLogData(
    sortedItems.length > 0 ? sortedItems[currentLog ?? 0]?.id : '',
    'build',
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

  const {
    data: issues,
    status,
    error,
  } = useBuildIssues(
    currentLog !== undefined ? sortedItems[currentLog]?.id : '',
  );

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
      <div className="flex items-center justify-between">
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
