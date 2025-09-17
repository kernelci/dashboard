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

import { Fragment, useCallback, useMemo, useState, type JSX } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import type { PossibleTableFilters } from '@/types/tree/TreeDetails';
import { possibleTableFilters } from '@/types/tree/TreeDetails';

import type { TestHistory, TIndividualTest, TPathTests } from '@/types/general';

import { StatusTable } from '@/utils/constants/database';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import TableStatusFilter from '@/components/Table/TableStatusFilter';

import { PaginationInfo } from '@/components/Table/PaginationInfo';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

import { usePaginationState } from '@/hooks/usePaginationState';

import type { TableKeys } from '@/utils/constants/tables';
import { buildHardwareArray, buildTreeBranch } from '@/utils/table';

import { EMPTY_VALUE } from '@/lib/string';

import { IndividualTestsTable } from './IndividualTestsTable';
import { defaultColumns, defaultInnerColumns } from './DefaultTestsColumns';

export interface ITestsTable {
  tableKey: TableKeys;
  testHistory?: TestHistory[];
  onClickFilter: (filter: PossibleTableFilters) => void;
  filter: PossibleTableFilters;
  columns?: ColumnDef<TPathTests>[];
  innerColumns?: ColumnDef<TIndividualTest>[];
  getRowLink: (testId: TestHistory['id']) => LinkProps;
  updatePathFilter?: (pathFilter: string) => void;
  currentPathFilter?: string;
}

type TPathTestsStatus = Pick<
  TPathTests,
  | 'done_tests'
  | 'error_tests'
  | 'fail_tests'
  | 'miss_tests'
  | 'pass_tests'
  | 'skip_tests'
  | 'null_tests'
  | 'total_tests'
>;

const countStatus = (group: TPathTestsStatus, status?: string): void => {
  group.total_tests++;
  switch (status?.toUpperCase()) {
    case StatusTable.DONE:
      group.done_tests++;
      break;
    case StatusTable.ERROR:
      group.error_tests++;
      break;
    case StatusTable.FAIL:
      group.fail_tests++;
      break;
    case StatusTable.MISS:
      group.miss_tests++;
      break;
    case StatusTable.PASS:
      group.pass_tests++;
      break;
    case StatusTable.SKIP:
      group.skip_tests++;
      break;
    default:
      group.null_tests++;
  }
};

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
  const [globalFilter, setGlobalFilter] = useState<string | undefined>();
  const { pagination, paginationUpdater } = usePaginationState(tableKey);

  const intl = useIntl();

  const rawData = useMemo((): TPathTests[] => {
    type Groups = {
      [K: string]: TPathTests;
    };
    const groups: Groups = {};
    if (testHistory !== undefined) {
      testHistory.forEach(e => {
        if (!e.path) {
          e.path = EMPTY_VALUE;
        }
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
        groups[group].individual_tests.push({
          id: e.id,
          duration: e.duration?.toString() ?? '',
          path: e.path,
          start_time: e.start_time,
          status: e.status,
          hardware: buildHardwareArray(
            e.environment_compatible,
            e.environment_misc,
          ),
          treeBranch: buildTreeBranch(e.tree_name, e.git_repository_branch),
        });
      });
    }
    return Object.values(groups);
  }, [testHistory]);

  const [globalStatusGroup, pathFilteredData] = useMemo((): [
    TPathTestsStatus,
    TPathTests[],
  ] => {
    const path = globalFilter;
    const isValidPath = path !== undefined && path !== '';
    const globalGroup: TPathTestsStatus = {
      done_tests: 0,
      fail_tests: 0,
      miss_tests: 0,
      pass_tests: 0,
      null_tests: 0,
      skip_tests: 0,
      error_tests: 0,
      total_tests: 0,
    };

    const filteredData = rawData.reduce<TPathTests[]>((acc, test) => {
      const localGroup: TPathTestsStatus = {
        done_tests: 0,
        fail_tests: 0,
        miss_tests: 0,
        pass_tests: 0,
        null_tests: 0,
        skip_tests: 0,
        error_tests: 0,
        total_tests: 0,
      };
      const individualTest = test.individual_tests.filter(t => {
        let dataIncludesPath = true;
        if (isValidPath) {
          dataIncludesPath = t.path?.includes(path) ?? false;
        }
        if (dataIncludesPath) {
          countStatus(localGroup, t.status);
          countStatus(globalGroup, t.status);
        }
        return dataIncludesPath;
      });

      if (individualTest.length > 0) {
        acc.push({
          path_group: test.path_group,
          individual_tests: individualTest,
          ...localGroup,
        });
      }

      return acc;
    }, []);

    return [globalGroup, filteredData];
  }, [globalFilter, rawData]);

  const data = useMemo((): TPathTests[] => {
    switch (filter) {
      case 'all':
        return pathFilteredData;
      case 'success':
        return pathFilteredData
          ?.filter(tests => tests.pass_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status?.toUpperCase() === StatusTable.PASS,
            ),
          }));
      case 'failed':
        return pathFilteredData
          ?.filter(tests => tests.fail_tests > 0)
          .map(test => ({
            ...test,
            individual_tests: test.individual_tests.filter(
              t => t.status?.toUpperCase() === StatusTable.FAIL,
            ),
          }));
      case 'inconclusive':
        return pathFilteredData
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
  }, [filter, pathFilteredData]);

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
    onGlobalFilterChange: setGlobalFilter,
    getRowId: row => row.path_group,
    state: {
      sorting,
      pagination,
      expanded,
    },
  });

  const filterCount: Record<PossibleTableFilters, number> = useMemo(
    () => ({
      all: globalStatusGroup.total_tests,
      success: globalStatusGroup.pass_tests,
      failed: globalStatusGroup.fail_tests,
      inconclusive:
        globalStatusGroup.total_tests -
        globalStatusGroup.pass_tests -
        globalStatusGroup.fail_tests,
    }),
    [globalStatusGroup],
  );

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
    [filterCount, intl, filter],
  );

  const onSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.value !== undefined && updatePathFilter) {
        updatePathFilter(e.target.value);
      }
      if (updatePathFilter === undefined) {
        setGlobalFilter(String(e.target.value));
      }
    },
    [setGlobalFilter, updatePathFilter],
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
            className="group hover:bg-light-blue cursor-pointer"
            onClick={() => {
              if (row.getCanExpand()) {
                row.toggleExpanded();
              }
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
