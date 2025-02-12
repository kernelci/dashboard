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
import { Link, useNavigate, useSearch } from '@tanstack/react-router';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import type { TreeTableBody } from '@/types/tree/Tree';
import { RedirectFrom, zOrigin } from '@/types/general';
import type { TFilter, TOrigins, BuildStatus } from '@/types/general';

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

import {
  BuildStatusWithLink,
  GroupedTestStatusWithLink,
} from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import {
  CommitTagTooltip,
  gitCommitValueSelector,
} from '@/components/Tooltip/CommitTagTooltip';
import CopyButton from '@/components/Button/CopyButton';

import type { ListingTableColumnMeta } from '@/types/table';

import { statusCountToRequiredStatusCount } from '@/utils/status';

import { InputTime } from './InputTime';

const MemoizedInputTime = memo(InputTime);

const getLinkProps = (
  row: Row<TreeTableBody>,
  origin: TOrigins,
  tabTarget?: string,
  diffFilter?: TFilter,
): LinkProps => {
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
      diffFilter: diffFilter ?? {},
      treeInfo: {
        gitUrl: row.original.url,
        gitBranch: row.original.branch,
        treeName: row.original.tree_name ?? undefined,
        commitName: row.original.commitName,
        headCommitHash: row.original.id,
      },
      intervalInDays: previousSearch.intervalInDays,
    }),
    state: s => ({
      ...s,
      id: row.original.id,
      from: RedirectFrom.Tree,
      treeStatusCount: {
        builds: {
          valid: row.original.buildStatus?.valid ?? 0,
          invalid: row.original.buildStatus?.invalid ?? 0,
          null: row.original.buildStatus?.null ?? 0,
        } satisfies BuildStatus,
        tests: statusCountToRequiredStatusCount({
          DONE: row.original.testStatus?.done,
          PASS: row.original.testStatus?.pass,
          FAIL: row.original.testStatus?.fail,
          ERROR: row.original.testStatus?.error,
          MISS: row.original.testStatus?.miss,
          SKIP: row.original.testStatus?.skip,
          NULL: row.original.testStatus?.null,
        }),
        boots: statusCountToRequiredStatusCount({
          DONE: row.original.bootStatus?.done,
          PASS: row.original.bootStatus?.pass,
          FAIL: row.original.bootStatus?.fail,
          ERROR: row.original.bootStatus?.error,
          MISS: row.original.bootStatus?.miss,
          SKIP: row.original.bootStatus?.skip,
          NULL: row.original.bootStatus?.null,
        }),
      },
    }),
  };
};

const getColumns = (origin: TOrigins): ColumnDef<TreeTableBody>[] => {
  return [
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
      cell: ({ column, row }): JSX.Element => {
        const tabTarget = (column.columnDef.meta as ListingTableColumnMeta)
          .tabTarget;
        return row.original.buildStatus ? (
          <BuildStatusWithLink
            valid={row.original.buildStatus.valid}
            invalid={row.original.buildStatus.invalid}
            unknown={row.original.buildStatus.null}
            validLinkProps={getLinkProps(row, origin, tabTarget, {
              buildStatus: { Success: true },
            })}
            invalidLinkProps={getLinkProps(row, origin, tabTarget, {
              buildStatus: { Failed: true },
            })}
            unknownLinkProps={getLinkProps(row, origin, tabTarget, {
              buildStatus: { Inconclusive: true },
            })}
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
      cell: ({ column, row }): JSX.Element => {
        const tabTarget = (column.columnDef.meta as ListingTableColumnMeta)
          .tabTarget;
        return row.original.bootStatus ? (
          <GroupedTestStatusWithLink
            pass={row.original.bootStatus.pass}
            skip={row.original.bootStatus.skip}
            fail={row.original.bootStatus.fail}
            miss={row.original.bootStatus.miss}
            done={row.original.bootStatus.done}
            error={row.original.bootStatus.error}
            nullStatus={row.original.bootStatus.null}
            passLinkProps={getLinkProps(row, origin, tabTarget, {
              bootStatus: { PASS: true },
            })}
            failLinkProps={getLinkProps(row, origin, tabTarget, {
              bootStatus: { FAIL: true },
            })}
            inconclusiveLinkProps={getLinkProps(row, origin, tabTarget, {
              bootStatus: {
                MISS: true,
                ERROR: true,
                SKIP: true,
                DONE: true,
                NULL: true,
              },
            })}
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
      cell: ({ column, row }): JSX.Element => {
        const tabTarget = (column.columnDef.meta as ListingTableColumnMeta)
          .tabTarget;
        return row.original.testStatus ? (
          <GroupedTestStatusWithLink
            pass={row.original.testStatus.pass}
            skip={row.original.testStatus.skip}
            fail={row.original.testStatus.fail}
            miss={row.original.testStatus.miss}
            done={row.original.testStatus.done}
            error={row.original.testStatus.error}
            nullStatus={row.original.testStatus.null}
            passLinkProps={getLinkProps(row, origin, tabTarget, {
              testStatus: { PASS: true },
            })}
            failLinkProps={getLinkProps(row, origin, tabTarget, {
              testStatus: { FAIL: true },
            })}
            inconclusiveLinkProps={getLinkProps(row, origin, tabTarget, {
              testStatus: {
                MISS: true,
                ERROR: true,
                SKIP: true,
                DONE: true,
                NULL: true,
              },
            })}
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
};

interface ITreeTable {
  treeTableRows: TreeTableBody[];
}

export function TreeTable({ treeTableRows }: ITreeTable): JSX.Element {
  const { origin: unsafeOrigin, listingSize } = useSearch({ strict: false });
  const navigate = useNavigate({ from: '/tree' });

  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } = usePaginationState(
    'treeListing',
    listingSize,
  );

  const origin = zOrigin.parse(unsafeOrigin);

  const columns = useMemo(() => getColumns(origin), [origin]);

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
                  {...getLinkProps(row, origin, tabTarget)}
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
                linkProps={getLinkProps(row, origin, tabTarget)}
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
  }, [modelRows, columns.length, origin]);

  const navigateWithPageSize = useCallback(
    (pageSize: number) => {
      navigate({
        search: prev => ({ ...prev, listingSize: pageSize }),
        state: s => s,
      });
    },
    [navigate],
  );

  return (
    <div className="flex flex-col gap-6 pb-4">
      <div className="flex items-center justify-between gap-4">
        <span className="text-dim-gray text-left text-sm">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={formattedBreakLineValue}
          />
        </span>
        <div className="flex items-center justify-between gap-10">
          <MemoizedInputTime />
          <PaginationInfo
            table={table}
            intlLabel="global.trees"
            onPaginationChange={navigateWithPageSize}
          />
        </div>
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableBody}</TableBody>
      </BaseTable>
      <PaginationInfo
        table={table}
        intlLabel="global.trees"
        onPaginationChange={navigateWithPageSize}
      />
    </div>
  );
}
