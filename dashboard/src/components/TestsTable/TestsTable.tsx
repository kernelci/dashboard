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

import { Fragment, useCallback, useEffect, useMemo, useState, type JSX } from 'react';

import { FormattedMessage, useIntl } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';

import type { PossibleTableFilters } from '@/types/tree/TreeDetails';
import { possibleTableFilters } from '@/types/tree/TreeDetails';

import type { TestHistory, TIndividualTest, TPathTests } from '@/types/general';

import { StatusTable } from '@/utils/constants/database';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import { PaginationInfo } from '@/components/Table/PaginationInfo';

import { usePaginationState } from '@/hooks/usePaginationState';

import type { TableKeys } from '@/utils/constants/tables';
import { buildHardwareArray, buildTreeBranch } from '@/utils/table';

import { EMPTY_VALUE } from '@/lib/string';

import { TableTopFilters } from '@/components/Table/TableTopFilters';

import type { TStatusFilters } from '@/components/Table/TableStatusFilter';

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
  const [globalFilter, setGlobalFilter] = useState<string | undefined>(
    currentPathFilter,
  );
  const { pagination, paginationUpdater } = usePaginationState(tableKey);

  const intl = useIntl();

  const rawData = useMemo((): TPathTests[] => {
    type GroupNode = {
      done_tests: number;
      fail_tests: number;
      miss_tests: number;
      pass_tests: number;
      null_tests: number;
      skip_tests: number;
      error_tests: number;
      total_tests: number;
      individual_tests: TIndividualTest[];
      children: Map<string, GroupNode>;
    };

    const rootGroups = new Map<string, GroupNode>();

    const createEmptyNode = (): GroupNode => ({
      done_tests: 0,
      fail_tests: 0,
      miss_tests: 0,
      pass_tests: 0,
      null_tests: 0,
      skip_tests: 0,
      error_tests: 0,
      total_tests: 0,
      individual_tests: [],
      children: new Map(),
    });

    const countStatus = (node: GroupNode, status?: string): void => {
      node.total_tests++;
      switch (status?.toUpperCase()) {
        case StatusTable.DONE:
          node.done_tests++;
          break;
        case StatusTable.ERROR:
          node.error_tests++;
          break;
        case StatusTable.FAIL:
          node.fail_tests++;
          break;
        case StatusTable.MISS:
          node.miss_tests++;
          break;
        case StatusTable.PASS:
          node.pass_tests++;
          break;
        case StatusTable.SKIP:
          node.skip_tests++;
          break;
        default:
          node.null_tests++;
      }
    };

    if (testHistory !== undefined) {
      testHistory.forEach(e => {
        const path = e.path || EMPTY_VALUE;
        const segments = path === EMPTY_VALUE ? [EMPTY_VALUE] : path.split('.');

        let currentLevel = rootGroups;
        let currentPathPrefix = '';

        for (let i = 0; i < segments.length; i++) {
          const segment = segments[i];
          const isLastSegment = i === segments.length - 1;

          if (!currentLevel.has(segment)) {
            currentLevel.set(segment, createEmptyNode());
          }

          const node = currentLevel.get(segment)!;

          if (isLastSegment) {
            countStatus(node, e.status);
            node.individual_tests.push({
              id: e.id,
              duration: e.duration?.toString() ?? '',
              path: e.path,
              start_time: e.start_time,
              status: e.status,
              hardware: buildHardwareArray(
                e.environment_compatible,
                e.environment_misc,
              ),
              treeBranch: buildTreeBranch(
                e.tree_name,
                e.git_repository_branch,
              ),
              lab: e.lab,
            });
          } else {
            currentPathPrefix =
              currentPathPrefix === ''
                ? segment
                : `${currentPathPrefix}.${segment}`;
            currentLevel = node.children;
          }
        }
      });
    }

    const buildTree = (
      groups: Map<string, GroupNode>,
      parentPath: string,
    ): TPathTests[] => {
      const result: TPathTests[] = [];

      groups.forEach((node, segment) => {
        const fullPath =
          parentPath === '' ? segment : `${parentPath}.${segment}`;

        const subGroups =
          node.children.size > 0 ? buildTree(node.children, fullPath) : [];

        const hasDirectTests = node.individual_tests.length > 0;

        result.push({
          done_tests: node.done_tests,
          fail_tests: node.fail_tests,
          miss_tests: node.miss_tests,
          pass_tests: node.pass_tests,
          null_tests: node.null_tests,
          skip_tests: node.skip_tests,
          error_tests: node.error_tests,
          total_tests: node.total_tests,
          path_group: segment,
          path_prefix: parentPath,
          individual_tests: node.individual_tests,
          sub_groups: subGroups.length > 0 ? subGroups : undefined,
          is_leaf_group: hasDirectTests || subGroups.length === 0,
        });
      });

      return result;
    };

    return buildTree(rootGroups, '');
  }, [testHistory]);

  const [globalStatusGroup, pathFilteredData, searchExpandedState] = useMemo(
    ():
      | [TPathTestsStatus, TPathTests[], ExpandedState | undefined]
      | [TPathTestsStatus, TPathTests[], undefined] => {
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

    const filterNode = (node: TPathTests, searchPath: string): TPathTests | null => {
      const nodeFullPath = node.path_prefix
        ? `${node.path_prefix}.${node.path_group}`
        : node.path_group;
      const nodeMatches = nodeFullPath.includes(searchPath);

      const filteredSubGroups = node.sub_groups
        ?.map(sub => filterNode(sub, searchPath))
        .filter((sub): sub is TPathTests => sub !== null);

      const filteredIndividualTests = node.individual_tests.filter(t =>
        t.path?.includes(searchPath),
      );

      const hasMatchingChildren =
        (filteredSubGroups && filteredSubGroups.length > 0) ||
        filteredIndividualTests.length > 0;

      if (nodeMatches || hasMatchingChildren) {
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

        const countItems = (
          tests: TIndividualTest[],
          groups: TPathTests[],
        ): void => {
          tests.forEach(t => {
            countStatus(localGroup, t.status);
            countStatus(globalGroup, t.status);
          });
          groups.forEach(g => {
            localGroup.done_tests += g.done_tests;
            localGroup.fail_tests += g.fail_tests;
            localGroup.miss_tests += g.miss_tests;
            localGroup.pass_tests += g.pass_tests;
            localGroup.null_tests += g.null_tests;
            localGroup.skip_tests += g.skip_tests;
            localGroup.error_tests += g.error_tests;
            localGroup.total_tests += g.total_tests;
            globalGroup.done_tests += g.done_tests;
            globalGroup.fail_tests += g.fail_tests;
            globalGroup.miss_tests += g.miss_tests;
            globalGroup.pass_tests += g.pass_tests;
            globalGroup.null_tests += g.null_tests;
            globalGroup.skip_tests += g.skip_tests;
            globalGroup.error_tests += g.error_tests;
            globalGroup.total_tests += g.total_tests;
          });
        };

        countItems(filteredIndividualTests, filteredSubGroups ?? []);

        return {
          ...node,
          ...localGroup,
          sub_groups: filteredSubGroups?.length ? filteredSubGroups : undefined,
          individual_tests: filteredIndividualTests,
          is_leaf_group:
            filteredIndividualTests.length > 0 ||
            !filteredSubGroups?.length,
        };
      }

      return null;
    };

    const collectExpandedState = (
      nodes: TPathTests[],
      expandedAcc: Record<string, boolean>,
    ): void => {
      nodes.forEach(node => {
        const rowId = node.path_prefix
          ? `${node.path_prefix}.${node.path_group}`
          : node.path_group;
        if (node.sub_groups?.length || node.individual_tests.length) {
          expandedAcc[rowId] = true;
        }
        if (node.sub_groups) {
          collectExpandedState(node.sub_groups, expandedAcc);
        }
      });
    };

    if (isValidPath) {
      const filteredData = rawData
        .map(node => filterNode(node, path))
        .filter((node): node is TPathTests => node !== null);

      const autoExpanded: Record<string, boolean> = {};
      collectExpandedState(filteredData, autoExpanded);

      return [globalGroup, filteredData, autoExpanded as ExpandedState];
    }

    rawData.forEach(node => {
      const countNode = (n: TPathTests): void => {
        n.individual_tests.forEach(t => countStatus(globalGroup, t.status));
        n.sub_groups?.forEach(countNode);
      };
      countNode(node);
    });

    return [globalGroup, rawData, undefined];
  }, [globalFilter, rawData]);

  const data = useMemo((): TPathTests[] => {
    const filterByStatus = (
      nodes: TPathTests[],
      statusFilter: 'success' | 'failed' | 'inconclusive' | 'all',
    ): TPathTests[] => {
      const results: TPathTests[] = [];

      nodes.forEach(node => {
        const filteredSubGroups = node.sub_groups
          ? filterByStatus(node.sub_groups, statusFilter)
          : undefined;

        const filteredIndividualTests = node.individual_tests.filter(t => {
          const uppercaseStatus = t.status?.toUpperCase();
          switch (statusFilter) {
            case 'success':
              return uppercaseStatus === StatusTable.PASS;
            case 'failed':
              return uppercaseStatus === StatusTable.FAIL;
            case 'inconclusive':
              return (
                uppercaseStatus !== StatusTable.PASS &&
                uppercaseStatus !== StatusTable.FAIL
              );
            default:
              return true;
          }
        });

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

        filteredIndividualTests.forEach(t => {
          countStatus(localGroup, t.status);
        });
        filteredSubGroups?.forEach(g => {
          localGroup.done_tests += g.done_tests;
          localGroup.fail_tests += g.fail_tests;
          localGroup.miss_tests += g.miss_tests;
          localGroup.pass_tests += g.pass_tests;
          localGroup.null_tests += g.null_tests;
          localGroup.skip_tests += g.skip_tests;
          localGroup.error_tests += g.error_tests;
          localGroup.total_tests += g.total_tests;
        });

        const hasContent =
          filteredIndividualTests.length > 0 ||
          (filteredSubGroups && filteredSubGroups.length > 0);

        if (hasContent) {
          results.push({
            ...node,
            ...localGroup,
            sub_groups: filteredSubGroups?.length ? filteredSubGroups : undefined,
            individual_tests: filteredIndividualTests,
            is_leaf_group:
              filteredIndividualTests.length > 0 || !filteredSubGroups?.length,
          });
        }
      });

      return results;
    };

    return filterByStatus(pathFilteredData, filter);
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
    getSubRows: row => row.sub_groups,
    getRowCanExpand: row =>
      (row.original.sub_groups !== undefined &&
        row.original.sub_groups.length > 0) ||
      row.original.individual_tests.length > 0,
    getExpandedRowModel: getExpandedRowModel(),
    onExpandedChange: setExpanded,
    onGlobalFilterChange: setGlobalFilter,
    getRowId: row =>
      row.path_prefix ? `${row.path_prefix}.${row.path_group}` : row.path_group,
    state: {
      sorting,
      pagination,
      expanded,
      globalFilter,
    },
  });

  useEffect(() => {
    if (searchExpandedState !== undefined) {
      setExpanded(searchExpandedState);
    }
  }, [searchExpandedState]);

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
      setGlobalFilter(String(e.target.value));
      if (updatePathFilter) {
        updatePathFilter(e.target.value);
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
    return modelRows?.length ? (
      modelRows.map(row => {
        const hasIndividualTests = row.original.individual_tests.length > 0;
        const hasSubGroups =
          row.original.sub_groups !== undefined &&
          row.original.sub_groups.length > 0;
        const isLeafGroup = !hasSubGroups;

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
            {row.getIsExpanded() && isLeafGroup && hasIndividualTests && (
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
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.tests" />
    </div>
  );
}
