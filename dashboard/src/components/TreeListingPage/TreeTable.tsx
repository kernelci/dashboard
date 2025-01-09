import type {
  ColumnDef,
  ColumnFiltersState,
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
import { Link, useSearch } from '@tanstack/react-router';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import type { TreeTableBody } from '@/types/tree/Tree';
import { zOrigin } from '@/types/general';

import { formattedBreakLineValue } from '@/locales/messages';

import {
  possibleBuildsTableFilter,
  possibleTestsTableFilter,
  zPossibleTabValidator,
} from '@/types/tree/TreeDetails';

import { usePaginationState } from '@/hooks/usePaginationState';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableRow,
} from '@/components/ui/table';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import { sanitizeTableValue } from '@/components/Table/tableUtils';

import { BuildStatus, GroupedTestStatus } from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import {
  CommitTagTooltip,
  gitCommitValueSelector,
} from '@/components/Tooltip/CommitTagTooltip';
import CopyButton from '@/components/Button/CopyButton';

import type { ListingTableColumnMeta } from '@/types/table';

import { InputTime } from './InputTime';

const MemoizedInputTime = memo(InputTime);

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
    meta: {
      tabTarget: 'global.builds',
    },
  },
  {
    accessorKey: 'branch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.branch" />
    ),
    meta: {
      tabTarget: 'global.builds',
    },
  },
  {
    id: 'commitTag',
    accessorKey: 'commitTag',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.commitTag" />
    ),
    cell: ({ row }): JSX.Element => (
      <CommitTagTooltip
        commitHash={row.original.commitHash}
        commitName={row.original.commitName}
        commitTags={row.original.commitTag}
      />
    ),
    meta: {
      tabTarget: 'global.builds',
    },
  },
  {
    accessorKey: 'date',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.date" />
    ),
    cell: ({ row }): JSX.Element => (
      <TooltipDateTime dateTime={row.getValue('date')} lineBreak={true} />
    ),
    meta: {
      tabTarget: 'global.builds',
    },
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
    meta: {
      tabTarget: 'global.builds',
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
    meta: {
      tabTarget: 'global.boots',
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
    meta: {
      tabTarget: 'global.tests',
    },
  },
];

interface ITreeTable {
  treeTableRows: TreeTableBody[];
}

export function TreeTable({ treeTableRows }: ITreeTable): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } = usePaginationState('treeListing');

  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);

  const getLinkProps = useCallback(
    (row: Row<TreeTableBody>, tabTarget?: string): LinkProps => {
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
          currentPageTab: zPossibleTabValidator.parse(tabTarget),
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

  const table = useReactTable({
    data: treeTableRows,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: paginationUpdater,
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
  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <TableRow key={row.id}>
          {row.getVisibleCells().map(cell => {
            const tabTarget = (
              cell.column.columnDef.meta as ListingTableColumnMeta
            ).tabTarget;
            // The CopyButton is defined outside of the cell column because I couldn't find
            // a way to include it within the cell definition while also using it outside of
            // a Link component. I attempted to modify CommitTagTooltip to wrap the tooltip
            // inside a Link component, but this would require the column cell to be a function
            // that receives LinkProps and returns the CommitTagTooltip component. However,
            // I couldn't figure out how to achieve this using TanStack Table, as
            // `cell.getValue()` would return an array instead of the expected function.
            return cell.column.columnDef.id === 'commitTag' ? (
              <TableCell key={cell.id}>
                <Link
                  className="inline-block"
                  {...getLinkProps(row, tabTarget)}
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </Link>
                <CopyButton
                  value={
                    gitCommitValueSelector({
                      commitHash: cell.row.original.commitHash,
                      commitName: cell.row.original.commitName,
                      commitTags: cell.row.original.commitTag,
                    }).content
                  }
                />
              </TableCell>
            ) : (
              <TableCellWithLink
                key={cell.id}
                linkClassName="w-full inline-block h-full"
                linkProps={getLinkProps(row, tabTarget)}
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
