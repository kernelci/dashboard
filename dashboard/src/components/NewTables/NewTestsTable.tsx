import {
  ColumnDef,
  ColumnFiltersState,
  ExpandedState,
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  PaginationState,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';

import { Fragment, useCallback, useMemo, useState } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { MdChevronRight } from 'react-icons/md';

import { FormattedMessage, useIntl } from 'react-intl';

import {
  possibleTestsTableFilter,
  TestHistory,
  TestsTableFilter,
} from '@/types/tree/TreeDetails';

import { TPathTests } from '@/types/general';

import { StatusTable } from '@/utils/constants/database';

import BaseTable, { TableHead } from '../Table/BaseTable';
import { TableBody, TableCell, TableRow } from '../ui/table';

import TableStatusFilter from '../Table/TableStatusFilter';

import { GroupedTestStatus } from '../Status/Status';

import { NewTableHeader } from './NewTableHeader';
import { IndividualTestsTable } from './IndividualTestsTable';
import { PaginationInfo } from './PaginationInfo';

export interface ITestsTable {
  testHistory: TestHistory[];
}

const columns: ColumnDef<TPathTests>[] = [
  {
    accessorKey: 'path_group',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'testDetails.path',
        intlDefaultMessage: 'Path',
      }),
  },
  {
    accessorKey: 'pass_tests',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
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
    cell: (): JSX.Element => <MdChevronRight />,
  },
];

export function NewTestsTable({ testHistory }: ITestsTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const { tableFilter } = useSearch({
    from: '/tree/$treeId/',
  });

  const navigate = useNavigate({ from: '/tree/$treeId' });
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

  const onClickFilter = useCallback(
    (filter: TestsTableFilter): void => {
      navigate({
        search: previousParams => {
          return {
            ...previousParams,
            tableFilter: {
              bootsTable: previousParams.tableFilter.bootsTable,
              buildsTable: previousParams.tableFilter.buildsTable,
              testsTable: filter,
            },
          };
        },
      });
    },
    [navigate],
  );

  const filters = useMemo(
    () => [
      {
        label: intl.formatMessage({ id: 'global.all' }),
        value: possibleTestsTableFilter[0],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[0],
      },
      {
        label: intl.formatMessage({ id: 'global.success' }),
        value: possibleTestsTableFilter[1],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[1],
      },
      {
        label: intl.formatMessage({ id: 'global.failed' }),
        value: possibleTestsTableFilter[2],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[2],
      },
      {
        label: intl.formatMessage({ id: 'global.inconclusive' }),
        value: possibleTestsTableFilter[3],
        isSelected: tableFilter.testsTable === possibleTestsTableFilter[3],
      },
    ],
    [intl, tableFilter.testsTable],
  );

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
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
      columnFilters,
      pagination,
      expanded,
    },
  });

  return (
    <div className="flex flex-col gap-6 pb-4">
      <TableStatusFilter
        filters={filters}
        onClickTest={(filter: TestsTableFilter) => onClickFilter(filter)}
      />
      <PaginationInfo
        table={table}
        pagination={pagination}
        data={data}
        label="tests"
      />
      <BaseTable
        headers={[]}
        headerComponents={table.getHeaderGroups()[0].headers.map(header => {
          return (
            <TableHead key={header.id} className="border-b px-0 font-bold">
              {header.isPlaceholder
                ? null
                : flexRender(
                    header.column.columnDef.header,
                    header.getContext(),
                  )}
            </TableHead>
          );
        })}
      >
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map(row => (
              <Fragment key={row.id}>
                <TableRow
                  className="cursor-pointer hover:bg-lightBlue"
                  onClick={() => {
                    if (row.getCanExpand()) row.toggleExpanded();
                  }}
                >
                  {row.getVisibleCells().map(cell => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
                {row.getIsExpanded() && (
                  <TableRow>
                    <TableCell colSpan={6} className="p-0">
                      <div className="group max-h-[400px] w-full overflow-scroll border-b border-darkGray bg-lightGray p-8">
                        <IndividualTestsTable
                          data={data[row.index].individual_tests}
                        />
                      </div>
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
          )}
        </TableBody>
      </BaseTable>
      <PaginationInfo
        table={table}
        pagination={pagination}
        data={data}
        label="tests"
      />
    </div>
  );
}
