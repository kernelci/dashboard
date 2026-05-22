import type {
  ColumnDef,
  ExpandedState,
  SortingState,
} from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { Fragment, useCallback, useMemo, useState, type JSX } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import type { PossibleTableFilters } from '@/types/tree/TreeDetails';
import { possibleTableFilters } from '@/types/tree/TreeDetails';

import type { TestHistory, TIndividualTest, TPathTests } from '@/types/general';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import {
  DumbBaseTable,
  DumbTableHeader,
  TableHead,
} from '@/components/Table/BaseTable';

import type { TableKeys } from '@/utils/constants/tables';

import { TableTopFilters } from '@/components/Table/TableTopFilters';

import type { TStatusFilters } from '@/components/Table/TableStatusFilter';

import { IndividualTestsTable } from './IndividualTestsTable';
import { defaultColumns, defaultInnerColumns } from './DefaultTestsColumns';
import { buildTestsTree } from './buildTestsTree';
import {
  pruneTree,
  computeGlobalCounts,
  matchByStatus,
  matchByPathSubstring,
  matchTestByPathSubstring,
} from './filterTestsTree';
import { collapseSingleChildChains } from './collapseTestsTree';

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

// TODO: would be useful if the navigation happened within the table, so the parent component would only be required to pass the navigation url instead of the whole function for the update and the currentPath diffFilter (boots/tests Table)
export function TestsTable({
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
  const pathFilter = currentPathFilter?.trim();

  const intl = useIntl();

  const rawTree = useMemo(() => buildTestsTree(testHistory), [testHistory]);

  const pathFilteredTree = useMemo(() => {
    if (!pathFilter) {
      return rawTree;
    }
    return pruneTree(rawTree, {
      matchTest: matchTestByPathSubstring(pathFilter),
      matchNodePath: matchByPathSubstring(pathFilter),
    });
  }, [rawTree, pathFilter]);

  const globalStatusGroup = useMemo(
    () => computeGlobalCounts(pathFilteredTree),
    [pathFilteredTree],
  );

  const data = useMemo(() => {
    const filtered =
      filter === 'all'
        ? pathFilteredTree
        : pruneTree(pathFilteredTree, { matchTest: matchByStatus(filter) });
    return collapseSingleChildChains(filtered);
  }, [pathFilteredTree, filter]);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getSubRows: row => row.sub_groups,
    getRowCanExpand: row =>
      (row.original.sub_groups !== undefined &&
        row.original.sub_groups.length > 0) ||
      row.original.individual_tests.length > 0,
    getExpandedRowModel: getExpandedRowModel(),
    onExpandedChange: setExpanded,
    getRowId: row =>
      row.path_prefix ? `${row.path_prefix}.${row.path_group}` : row.path_group,
    state: {
      sorting,
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
    [filterCount, intl, filter],
  );

  const onSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const trimmedPathFilter = e.target.value.trim();
      if (updatePathFilter) {
        updatePathFilter(trimmedPathFilter);
      }
    },
    [updatePathFilter],
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
          {headerComponent}
        </TableHead>
      );
    });
  }, [groupHeaders, sorting]);

  const modelRows = table.getRowModel().rows;
  const tableRows = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows.length ? (
      modelRows.map(row => {
        const hasIndividualTests = row.original.individual_tests.length > 0;

        return (
          <Fragment key={row.id}>
            <TableRow
              className="group hover:bg-light-blue cursor-pointer"
              onClick={() => {
                if (row.getCanExpand()) {
                  row.toggleExpanded();
                }
              }}
              data-state={row.getIsExpanded() ? 'open' : 'closed'}
              data-depth={row.depth}
            >
              {row.getVisibleCells().map(cell => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
            {row.getIsExpanded() && hasIndividualTests && (
              <TableRow>
                <TableCell colSpan={6} className="p-0">
                  <IndividualTestsTable
                    getRowLink={getRowLink}
                    data={row.original.individual_tests}
                    columns={innerColumns}
                  />
                </TableCell>
              </TableRow>
            )}
          </Fragment>
        );
      })
    ) : (
      <TableRow>
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [columns.length, getRowLink, innerColumns, modelRows]);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <TableTopFilters
        key="testsTableSearch"
        filters={filters}
        onClickFilter={onClickFilter}
        onSearchChange={onSearchChange}
        currentPathFilter={currentPathFilter}
      />
      <div className="h-[600px] overflow-auto">
        <DumbBaseTable containerClassName="overflow-visible h-full bg-white">
          <DumbTableHeader className="sticky top-0 z-10">
            {tableHeaders}
          </DumbTableHeader>
          <TableBody>{tableRows}</TableBody>
        </DumbBaseTable>
      </div>
    </div>
  );
}
