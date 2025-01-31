import type {
  ColumnDef,
  ExpandedState,
  SortingState,
} from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { Fragment, useCallback, useMemo, useState } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import type { TestsTableFilter } from '@/types/tree/TreeDetails';
import { possibleTestsTableFilter } from '@/types/tree/TreeDetails';

import type { TestHistory, TIndividualTest, TPathTests } from '@/types/general';

import { StatusTable } from '@/utils/constants/database';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import TableStatusFilter from '@/components/Table/TableStatusFilter';

import { PaginationInfo } from '@/components/Table/PaginationInfo';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

import { usePaginationState } from '@/hooks/usePaginationState';

import type { TableKeys } from '@/utils/constants/tables';
import { buildHardwareArray } from '@/utils/table';

import { IndividualTestsTable } from './IndividualTestsTable';
import { defaultColumns, defaultInnerColumns } from './DefaultTestsColumns';

export interface ITestsTable {
  tableKey: TableKeys;
  testHistory?: TestHistory[];
  onClickFilter: (filter: TestsTableFilter) => void;
  filter: TestsTableFilter;
  columns?: ColumnDef<TPathTests>[];
  innerColumns?: ColumnDef<TIndividualTest>[];
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  updatePathFilter?: (pathFilter: string) => void;
  currentPathFilter?: string;
}

// TODO: would be useful if the navigation happened within the table, so the parent component would only be required to pass the navigation url instead of the whole function for the update and the currentPath diffFilter (boots/tests Table)
export function TestsTable({
  tableKey,
  testHistory,
  onClickFilter,
  filter,
  columns = defaultColumns,
  innerColumns = defaultInnerColumns,
  getRowLink,
  updatePathFilter,
  currentPathFilter,
}: ITestsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const { pagination, paginationUpdater } = usePaginationState(tableKey);

  const intl = useIntl();

  const rawData = useMemo((): TPathTests[] => {
    type Groups = {
      [K: string]: TPathTests;
    };
    const groups: Groups = {};
    if (testHistory !== undefined) {
      testHistory.forEach(e => {
        const parts = e.path.split('.', 1);
        const group = parts.length > 0 ? parts[0] : '-';
        if (!(group in groups)) {
          groups[group] = {
            done_tests: 0,
            fail_tests: 0,
            miss_tests: 0,
            pass_tests: 0,
            null_tests: 0,
            skip_tests: 0,
            error_tests: 0,
            total_tests: 0,
            path_group: group,
            individual_tests: [],
          };
        }
        groups[group].total_tests++;
        groups[group].individual_tests.push({
          id: e.id,
          duration: e.duration?.toString() ?? '',
          path: e.path,
          start_time: e.start_time,
          status: e.status,
          hardware: buildHardwareArray(e.environment_compatible, e.misc),
        });
        switch (e.status) {
          case 'DONE':
            groups[group].done_tests++;
            break;
          case 'ERROR':
            groups[group].error_tests++;
            break;
          case 'FAIL':
            groups[group].fail_tests++;
            break;
          case 'MISS':
            groups[group].miss_tests++;
            break;
          case 'PASS':
            groups[group].pass_tests++;
            break;
          case 'SKIP':
            groups[group].skip_tests++;
            break;
          default:
            groups[group].null_tests++;
        }
      });
    }
    return Object.values(groups);
  }, [testHistory]);

  const data = useMemo((): TPathTests[] => {
    switch (filter) {
      case 'all':
        return rawData;
      case 'success':
        return rawData
          ?.filter(tests => tests.pass_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status?.toUpperCase() === StatusTable.PASS,
            ),
          }));
      case 'failed':
        return rawData
          ?.filter(tests => tests.fail_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(t => {
              const result = t.status?.toUpperCase() === StatusTable.FAIL;

              return result;
            }),
          }));
      case 'inconclusive':
        return rawData
          ?.filter(
            tests =>
              tests.done_tests > 0 ||
              tests.error_tests > 0 ||
              tests.miss_tests > 0 ||
              tests.skip_tests > 0 ||
              tests.null_tests > 0,
          )
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(t => {
              const uppercaseTestStatus = t.status?.toUpperCase();
              const result =
                uppercaseTestStatus !== StatusTable.PASS &&
                uppercaseTestStatus !== StatusTable.FAIL;
              return result;
            }),
          }));
    }
  }, [filter, rawData]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: paginationUpdater,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getRowCanExpand: _ => true,
    getExpandedRowModel: getExpandedRowModel(),
    onExpandedChange: setExpanded,
    state: {
      sorting,
      pagination,
      expanded,
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

      const filteredData = globalFilter
        ? rawData.filter(row => row.path_group.includes(globalFilter))
        : rawData;

      filteredData.forEach(tests => {
        count.all += tests.total_tests;
        count.success += tests.pass_tests;
        count.failed += tests.fail_tests;
        count.inconclusive +=
          tests.total_tests - tests.pass_tests - tests.fail_tests;
      });

      return count;
    }, [rawData, globalFilter]);

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleTestsTableFilter[0]] },
        ),
        value: possibleTestsTableFilter[0],
        isSelected: filter === possibleTestsTableFilter[0],
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleTestsTableFilter[1]] },
        ),
        value: possibleTestsTableFilter[1],
        isSelected: filter === possibleTestsTableFilter[1],
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleTestsTableFilter[2]] },
        ),
        value: possibleTestsTableFilter[2],
        isSelected: filter === possibleTestsTableFilter[2],
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleTestsTableFilter[3]] },
        ),
        value: possibleTestsTableFilter[3],
        isSelected: filter === possibleTestsTableFilter[3],
      },
    ],
    [filterCount, intl, filter],
  );

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
          {header.id === 'path_group' ? (
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
  const tableRows = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <Fragment key={row.id}>
          <TableRow
            className="group cursor-pointer hover:bg-lightBlue"
            onClick={() => {
              if (row.getCanExpand()) row.toggleExpanded();
            }}
            data-state={row.getIsExpanded() ? 'open' : 'closed'}
          >
            {row.getVisibleCells().map(cell => (
              <TableCell key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </TableCell>
            ))}
          </TableRow>
          {row.getIsExpanded() && (
            <TableRow>
              <TableCell colSpan={6} className="p-0">
                <IndividualTestsTable
                  getRowLink={getRowLink}
                  data={data[row.index].individual_tests}
                  columns={innerColumns}
                />
              </TableCell>
            </TableRow>
          )}
        </Fragment>
      ))
    ) : (
      <TableRow>
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [columns.length, data, getRowLink, innerColumns, modelRows]);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <TableStatusFilter filters={filters} onClickTest={onClickFilter} />
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.tests" />
    </div>
  );
}
