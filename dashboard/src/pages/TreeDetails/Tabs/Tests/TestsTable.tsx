import type {
  ColumnDef,
  ExpandedState,
  PaginationState,
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

import type { TableFilter, TestsTableFilter } from '@/types/tree/TreeDetails';
import { possibleTestsTableFilter } from '@/types/tree/TreeDetails';

import type { TestHistory, TPathTests } from '@/types/general';

import { StatusTable } from '@/utils/constants/database';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import { GroupedTestStatus } from '@/components/Status/Status';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import TableStatusFilter from '@/components/Table/TableStatusFilter';

import { TableHeader } from '@/components/Table/TableHeader';

import { PaginationInfo } from '@/components/Table/PaginationInfo';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';

import DebounceInput from '@/components/DebounceInput/DebounceInput';

import { IndividualTestsTable } from './IndividualTestsTable';

export interface ITestsTable {
  testHistory: TestHistory[];
  onClickFilter: (filter: TestsTableFilter) => void;
  tableFilter: TableFilter;
}

const columns: ColumnDef<TPathTests>[] = [
  {
    accessorKey: 'path_group',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.path',
        intlDefaultMessage: 'Path',
      }),
  },
  {
    accessorKey: 'pass_tests',
    header: ({ column }): JSX.Element =>
      TableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.status',
        intlDefaultMessage: 'Status',
        tooltipId: 'bootsTab.statusTooltip',
      }),
    cell: ({ row }): JSX.Element => {
      return (
        <GroupedTestStatus
          pass={row.original.pass_tests}
          done={row.original.done_tests}
          miss={row.original.miss_tests}
          fail={row.original.fail_tests}
          skip={row.original.skip_tests}
          error={row.original.error_tests}
        />
      );
    },
  },
  {
    id: 'chevron',
    cell: (): JSX.Element => <ChevronRightAnimate />,
  },
];

export function TestsTable({
  testHistory,
  onClickFilter,
  tableFilter,
}: ITestsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const intl = useIntl();

  const rawData = useMemo((): TPathTests[] => {
    type Groups = {
      [K: string]: TPathTests;
    };
    const groups: Groups = {};
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
        start_time: e.startTime,
        status: e.status,
        hardware: e.hardware,
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
          if (!e.status) groups[group].null_tests++;
      }
    });
    return Object.values(groups);
  }, [testHistory]);

  const data = useMemo((): TPathTests[] => {
    switch (tableFilter.testsTable) {
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
  }, [tableFilter.testsTable, rawData]);

  const filterCount: Record<(typeof possibleTestsTableFilter)[number], number> =
    useMemo(() => {
      const count = {
        all: 0,
        success: 0,
        failed: 0,
        inconclusive: 0,
      };

      rawData.forEach(tests => {
        count.all += tests.total_tests;
        count.success += tests.pass_tests;
        count.failed += tests.fail_tests;
        count.inconclusive +=
          tests.total_tests - tests.pass_tests - tests.fail_tests;
      });

      return count;
    }, [rawData]);

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage(
          { id: 'global.allCount' },
          { count: filterCount[possibleTestsTableFilter[0]] },
        ),
        value: possibleTestsTableFilter[0],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[0],
      },
      {
        label: intl.formatMessage(
          { id: 'global.successCount' },
          { count: filterCount[possibleTestsTableFilter[1]] },
        ),
        value: possibleTestsTableFilter[1],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[1],
      },
      {
        label: intl.formatMessage(
          { id: 'global.failedCount' },
          { count: filterCount[possibleTestsTableFilter[2]] },
        ),
        value: possibleTestsTableFilter[2],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[2],
      },
      {
        label: intl.formatMessage(
          { id: 'global.inconclusiveCount' },
          { count: filterCount[possibleTestsTableFilter[3]] },
        ),
        value: possibleTestsTableFilter[3],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[3],
      },
    ],
    [filterCount, intl, tableFilter.testsTable],
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: setPagination,
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

  const onSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) =>
      table.setGlobalFilter(String(e.target.value)),
    [table],
  );

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id} className="border-b px-2 font-bold">
          {header.isPlaceholder
            ? null
            : flexRender(header.column.columnDef.header, header.getContext())}
        </TableHead>
      );
    });
    // TODO: remove exhaustive-deps and change memo (all tables)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupHeaders, sorting]);

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
                <IndividualTestsTable data={data[row.index].individual_tests} />
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
  }, [data, modelRows]);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex justify-between">
        <TableStatusFilter filters={filters} onClickTest={onClickFilter} />
        <DebounceInput
          debouncedSideEffect={onSearchChange}
          className="w-50"
          type="text"
          placeholder={intl.formatMessage({ id: 'global.search' })}
        />
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} data={data} intlLabel="treeDetails.tests" />
    </div>
  );
}
