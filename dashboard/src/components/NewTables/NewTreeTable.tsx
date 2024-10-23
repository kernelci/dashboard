import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  PaginationState,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';

import { useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import { useSearch } from '@tanstack/react-router';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { TreeTableBody, zOrigin } from '@/types/tree/Tree';

import { formattedBreakLineValue } from '@/locales/messages';

import {
  possibleBuildsTableFilter,
  possibleTestsTableFilter,
  zPossibleValidator,
} from '@/types/tree/TreeDetails';

import BaseTable, { TableHead } from '../Table/BaseTable';
import { TableBody, TableCell, TableCellWithLink, TableRow } from '../ui/table';

import { Tooltip, TooltipContent, TooltipTrigger } from '../Tooltip';

import { sanitizeTableValue } from '../Table/tableUtils';

import { BuildStatus, GroupedTestStatus } from '../Status/Status';

import { NewTableHeader } from './NewTableHeader';
import { PaginationInfo } from './PaginationInfo';

const columns: ColumnDef<TreeTableBody>[] = [
  {
    accessorKey: 'tree_name',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.tree',
        intlDefaultMessage: 'Tree',
      }),
    cell: ({ row }): JSX.Element => {
      return (
        <Tooltip>
          <TooltipTrigger>
            <div>
              {sanitizeTableValue(row.getValue('tree_name') ?? '', false)}
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <a href={row.original.url} target="_blank" rel="noreferrer">
              {sanitizeTableValue(row.original.url, false)}
            </a>
          </TooltipContent>
        </Tooltip>
      );
    },
  },
  {
    accessorKey: 'branch',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.branch',
        intlDefaultMessage: 'Branch',
      }),
  },
  {
    accessorKey: 'commitName',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.commitTag',
        intlDefaultMessage: 'Commit/Tag',
      }),
    cell: ({ row }) =>
      sanitizeTableValue(
        row.getValue('commitName')
          ? row.getValue('commitName')
          : row.original.commitHash,
      ),
  },
  {
    accessorKey: 'date',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'global.date',
        intlDefaultMessage: 'Date',
      }),
    cell: ({ row }): JSX.Element => (
      <TooltipDateTime dateTime={row.getValue('date')} lineBreak={true} />
    ),
  },
  {
    accessorKey: 'buildStatus.valid',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.build',
        intlDefaultMessage: 'Build Status',
        tooltipId: 'buildTab.statusTooltip',
      }),
    cell: ({ row }): JSX.Element => {
      return row.original.buildStatus ? (
        <BuildStatus
          valid={row.original.buildStatus.valid}
          invalid={row.original.buildStatus.invalid}
          unknown={row.original.buildStatus.null}
        />
      ) : (
        <FormattedMessage id="global.loading" defaultMessage="Loading..." />
      );
    },
  },
  {
    accessorKey: 'bootStatus.pass',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.bootStatus',
        intlDefaultMessage: 'Boot Status',
        tooltipId: 'bootsTab.statusTooltip',
      }),
    cell: ({ row }): JSX.Element => {
      return row.original.bootStatus ? (
        <GroupedTestStatus
          pass={row.original.bootStatus.pass}
          skip={row.original.bootStatus.skip}
          fail={row.original.bootStatus.fail}
          miss={row.original.bootStatus.miss}
          done={row.original.bootStatus.done}
          error={row.original.bootStatus.error}
        />
      ) : (
        <FormattedMessage id="global.loading" defaultMessage="Loading..." />
      );
    },
  },
  {
    accessorKey: 'testStatus.pass',
    header: ({ column }): JSX.Element =>
      NewTableHeader({
        column: column,
        sortable: true,
        intlKey: 'treeTable.test',
        intlDefaultMessage: 'Test Status',
        tooltipId: 'testsTab.statusTooltip',
      }),
    cell: ({ row }): JSX.Element => {
      return row.original.testStatus ? (
        <GroupedTestStatus
          pass={row.original.testStatus.pass}
          skip={row.original.testStatus.skip}
          fail={row.original.testStatus.fail}
          miss={row.original.testStatus.miss}
          done={row.original.testStatus.done}
          error={row.original.testStatus.error}
        />
      ) : (
        <FormattedMessage id="global.loading" defaultMessage="Loading..." />
      );
    },
  },
];

const columnLinkTargets = [
  'treeDetails.builds',
  'treeDetails.builds',
  'treeDetails.builds',
  'treeDetails.builds',
  'treeDetails.builds',
  'treeDetails.boots',
  'treeDetails.tests',
] as const;

interface INewTreeTable {
  treeTableRows: TreeTableBody[];
}

export function NewTreeTable({ treeTableRows }: INewTreeTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);

  // type ILinkProps = LinkProps & { style: React.CSSProperties };

  // const linkProps = useMemo(
  //   () =>
  //     (row, target: string): ILinkProps => ({
  //       to: '/tree/$treeId',
  //       params: { treeId: row.id },
  //       style: {
  //         width: '100%',
  //         display: 'inline-block',
  //         height: '100%',
  //       },
  //       search: {
  //         tableFilter: {
  //           bootsTable: possibleTestsTableFilter[0],
  //           buildsTable: possibleBuildsTableFilter[2],
  //           testsTable: possibleTestsTableFilter[0],
  //         },
  //         origin: origin,
  //         currentTreeDetailsTab: zPossibleValidator.parse(target),
  //         diffFilter: {},
  //         treeInfo: {
  //           gitUrl: row.url,
  //           gitBranch: row.branch,
  //           treeName: row.tree_name ?? undefined,
  //           commitName: row.commitName,
  //           headCommitHash: row.id,
  //         },
  //       },
  //     }),
  //   [origin],
  // );

  const data = useMemo(() => {
    return treeTableRows;
  }, [treeTableRows]);

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
    state: {
      sorting,
      columnFilters,
      pagination,
    },
  });

  return (
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex items-center justify-between gap-4">
        <span className="text-left text-sm text-dimGray">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={formattedBreakLineValue}
          />
        </span>
        <PaginationInfo
          table={table}
          pagination={pagination}
          data={data}
          label="trees"
        />
      </div>
      <BaseTable
        headers={[]}
        headerComponents={table.getHeaderGroups()[0].headers.map(header => {
          return (
            <TableHead key={header.id}>
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
              // linkprops
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell, cellId) => {
                  return (
                    // <TableCell key={cell.id}>
                    <TableCellWithLink
                      key={cell.id}
                      linkClassName="w-full inline-block h-full"
                      linkProps={{
                        to: '/tree/$treeId',
                        params: { treeId: row.original.id },
                        search: {
                          tableFilter: {
                            bootsTable: possibleTestsTableFilter[0],
                            buildsTable: possibleBuildsTableFilter[2],
                            testsTable: possibleTestsTableFilter[0],
                          },
                          origin: origin,
                          currentTreeDetailsTab: zPossibleValidator.parse(
                            columnLinkTargets[cellId],
                          ),
                          diffFilter: {},
                          treeInfo: {
                            gitUrl: row.original.url,
                            gitBranch: row.original.branch,
                            treeName: row.original.tree_name ?? undefined,
                            commitName: row.original.commitName,
                            headCommitHash: row.original.id,
                          },
                        },
                      }}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCellWithLink>
                    // </TableCell>
                  );
                })}
              </TableRow>
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
        label="trees"
      />
    </div>
  );
}
