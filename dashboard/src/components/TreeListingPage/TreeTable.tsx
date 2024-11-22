import type {
  ColumnDef,
  ColumnFiltersState,
  PaginationState,
  Row,
  SortingState,
} from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { memo, useCallback, useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useSearch } from '@tanstack/react-router';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import type { TreeTableBody } from '@/types/tree/Tree';
import { zOrigin } from '@/types/general';

import { formattedBreakLineValue } from '@/locales/messages';

import {
  possibleBuildsTableFilter,
  possibleTestsTableFilter,
  zPossibleTabValidator,
} from '@/types/tree/TreeDetails';

import BaseTable, { TableHead } from '../Table/BaseTable';
import { TableBody, TableCell, TableCellWithLink, TableRow } from '../ui/table';

import { Tooltip, TooltipContent, TooltipTrigger } from '../Tooltip';

import { sanitizeTableValue } from '../Table/tableUtils';

import { BuildStatus, GroupedTestStatus } from '../Status/Status';
import { TableHeader } from '../Table/TableHeader';
import { PaginationInfo } from '../Table/PaginationInfo';

import { InputTime } from './InputTime';

const columns: ColumnDef<TreeTableBody>[] = [
  {
    accessorKey: 'tree_name',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.tree" />
    ),
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
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.branch" />
    ),
  },
  {
    accessorKey: 'commitName',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.commitTag" />
    ),
    cell: ({ row }) =>
      sanitizeTableValue(
        row.getValue('commitName')
          ? row.getValue('commitName')
          : row.original.commitHash,
      ),
  },
  {
    accessorKey: 'date',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.date" />
    ),
    cell: ({ row }): JSX.Element => (
      <TooltipDateTime dateTime={row.getValue('date')} lineBreak={true} />
    ),
  },
  {
    accessorKey: 'buildStatus.valid',
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.build"
        tooltipId="build.statusTooltip"
      />
    ),
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
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.bootStatus"
        tooltipId="boots.statusTooltip"
      />
    ),
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
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="globalTable.test"
        tooltipId="test.statusTooltip"
      />
    ),
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
  'global.builds',
  'global.builds',
  'global.builds',
  'global.builds',
  'global.builds',
  'global.boots',
  'global.tests',
] as const;

interface ITreeTable {
  treeTableRows: TreeTableBody[];
}

export function TreeTable({ treeTableRows }: ITreeTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });

  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);

  const getLinkProps = useCallback(
    (row: Row<TreeTableBody>, target: string): LinkProps => {
      return {
        to: '/tree/$treeId',
        params: { treeId: row.original.id },

        search: previousSearch => ({
          tableFilter: {
            bootsTable: possibleTestsTableFilter[0],
            buildsTable: possibleBuildsTableFilter[2],
            testsTable: possibleTestsTableFilter[0],
          },
          origin: origin,
          currentPageTab: zPossibleTabValidator.parse(target),
          diffFilter: {},
          treeInfo: {
            gitUrl: row.original.url,
            gitBranch: row.original.branch,
            treeName: row.original.tree_name ?? undefined,
            commitName: row.original.commitName,
            headCommitHash: row.original.id,
          },
          intervalInDays: previousSearch.intervalInDays,
        }),
      };
    },
    [origin],
  );

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

  const groupHeaders = table.getHeaderGroups()[0].headers;
  const tableHeaders = useMemo((): JSX.Element[] => {
    return groupHeaders.map(header => {
      return (
        <TableHead key={header.id}>
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
  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <TableRow key={row.id}>
          {row.getVisibleCells().map((cell, cellIndex) => {
            return (
              <TableCellWithLink
                key={cell.id}
                linkClassName="w-full inline-block h-full"
                linkProps={getLinkProps(row, columnLinkTargets[cellIndex])}
              >
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </TableCellWithLink>
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
    );
  }, [getLinkProps, modelRows]);

  const MemoizedInputTime = memo(InputTime);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex items-center justify-between gap-4">
        <span className="text-left text-sm text-dimGray">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={formattedBreakLineValue}
          />
        </span>
        <div className="flex items-center justify-between gap-10">
          <MemoizedInputTime />
          <PaginationInfo table={table} intlLabel="global.trees" />
        </div>
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableBody}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.trees" />
    </div>
  );
}
