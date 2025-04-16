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

import { useCallback, useMemo, useState, type JSX } from 'react';

import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { Link, useNavigate, useSearch } from '@tanstack/react-router';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import type { TreeTableBody } from '@/types/tree/Tree';
import { DEFAULT_ORIGIN, RedirectFrom } from '@/types/general';
import type { TFilter } from '@/types/general';

import { formattedBreakLineValue } from '@/locales/messages';

import {
  possibleTableFilters,
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

import { GroupedTestStatusWithLink } from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import {
  CommitTagTooltip,
  gitCommitValueSelector,
} from '@/components/Tooltip/CommitTagTooltip';
import CopyButton from '@/components/Button/CopyButton';

import type { ListingTableColumnMeta } from '@/types/table';

import { statusCountToRequiredStatusCount } from '@/utils/status';

import { MemoizedInputTime } from '@/components/InputTime';
import { shouldShowRelativeDate } from '@/lib/date';
import { valueOrEmpty } from '@/lib/string';
import { PinnedTrees } from '@/utils/constants/tables';
import { makeTreeIdentifierKey } from '@/utils/trees';

const getLinkProps = (
  row: Row<TreeTableBody>,
  origin: string,
  tabTarget?: string,
  diffFilter?: TFilter,
): LinkProps => {
  return {
    to: '/tree/$treeId',
    params: { treeId: row.original.git_commit_hash },
    search: previousSearch => ({
      tableFilter: {
        bootsTable: possibleTableFilters[0],
        buildsTable: possibleTableFilters[0],
        testsTable: possibleTableFilters[0],
      },
      origin: origin,
      currentPageTab: zPossibleTabValidator.parse(tabTarget),
      diffFilter: diffFilter ?? {},
      treeInfo: {
        gitUrl: row.original.git_repository_url,
        gitBranch: row.original.git_repository_branch,
        treeName: row.original.tree_name ?? undefined,
        commitName: row.original.git_commit_name,
        headCommitHash: row.original.git_commit_hash,
      },
      intervalInDays: previousSearch.intervalInDays,
    }),
    state: s => ({
      ...s,
      id: row.original.git_commit_hash,
      from: RedirectFrom.Tree,
      treeStatusCount: {
        builds: statusCountToRequiredStatusCount({
          PASS: row.original.build_status?.PASS,
          FAIL: row.original.build_status?.FAIL,
          NULL: row.original.build_status?.NULL,
          DONE: row.original.build_status?.DONE,
          ERROR: row.original.build_status?.ERROR,
          MISS: row.original.build_status?.MISS,
          SKIP: row.original.build_status?.SKIP,
        }),
        tests: statusCountToRequiredStatusCount({
          PASS: row.original.test_status?.pass,
          FAIL: row.original.test_status?.fail,
          NULL: row.original.test_status?.null,
          DONE: row.original.test_status?.done,
          ERROR: row.original.test_status?.error,
          MISS: row.original.test_status?.miss,
          SKIP: row.original.test_status?.skip,
        }),
        boots: statusCountToRequiredStatusCount({
          PASS: row.original.boot_status?.pass,
          FAIL: row.original.boot_status?.fail,
          NULL: row.original.boot_status?.null,
          DONE: row.original.boot_status?.done,
          ERROR: row.original.boot_status?.error,
          MISS: row.original.boot_status?.miss,
          SKIP: row.original.boot_status?.skip,
        }),
      },
    }),
  };
};

const getColumns = (origin: string): ColumnDef<TreeTableBody>[] => {
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
              {sanitizeTableValue(row.getValue('tree_name') ?? '', false)}
            </TooltipTrigger>
            <TooltipContent>
              <a
                href={row.original.git_repository_url}
                target="_blank"
                rel="noreferrer"
              >
                {sanitizeTableValue(row.original.git_repository_url, false)}
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
      accessorKey: 'git_repository_branch',
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="globalTable.branch" />
      ),
      cell: ({ row }) => valueOrEmpty(row.getValue('git_repository_branch')),
      meta: {
        tabTarget: 'global.builds',
      },
    },
    {
      id: 'git_commit_tags',
      accessorKey: 'git_commit_tags',
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="globalTable.commitTag" />
      ),
      cell: ({ row }): JSX.Element => (
        <CommitTagTooltip
          commitName={row.original.git_commit_name}
          commitHash={row.original.git_commit_hash}
          commitTags={row.original.git_commit_tags}
        />
      ),
      meta: {
        tabTarget: 'global.builds',
      },
    },
    {
      accessorKey: 'start_time',
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="global.date" />
      ),
      cell: ({ row }): JSX.Element => (
        <TooltipDateTime
          dateTime={row.getValue('start_time')}
          lineBreak={true}
          showRelative={shouldShowRelativeDate(row.getValue('start_time'))}
        />
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
        return row.original.build_status ? (
          <GroupedTestStatusWithLink
            pass={row.original.build_status.PASS}
            skip={row.original.build_status.SKIP}
            fail={row.original.build_status.FAIL}
            miss={row.original.build_status.MISS}
            done={row.original.build_status.DONE}
            error={row.original.build_status.ERROR}
            nullStatus={row.original.build_status.NULL}
            passLinkProps={getLinkProps(row, origin, tabTarget, {
              buildStatus: { PASS: true },
            })}
            failLinkProps={getLinkProps(row, origin, tabTarget, {
              buildStatus: { FAIL: true },
            })}
            inconclusiveLinkProps={getLinkProps(row, origin, tabTarget, {
              buildStatus: {
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
        return row.original.boot_status ? (
          <GroupedTestStatusWithLink
            pass={row.original.boot_status.pass}
            skip={row.original.boot_status.skip}
            fail={row.original.boot_status.fail}
            miss={row.original.boot_status.miss}
            done={row.original.boot_status.done}
            error={row.original.boot_status.error}
            nullStatus={row.original.boot_status.null}
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
        return row.original.test_status ? (
          <GroupedTestStatusWithLink
            pass={row.original.test_status.pass}
            skip={row.original.test_status.skip}
            fail={row.original.test_status.fail}
            miss={row.original.test_status.miss}
            done={row.original.test_status.done}
            error={row.original.test_status.error}
            nullStatus={row.original.test_status.null}
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
  const origin = unsafeOrigin ?? DEFAULT_ORIGIN;
  const navigate = useNavigate({ from: '/tree' });

  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } = usePaginationState(
    'treeListing',
    listingSize,
  );

  const orderedData = useMemo(() => {
    return treeTableRows.sort((a, b) => {
      const aKey = makeTreeIdentifierKey({
        treeName: valueOrEmpty(a.tree_name),
        gitRepositoryBranch: valueOrEmpty(a.git_repository_branch),
        separator: '/',
      });
      const bKey = makeTreeIdentifierKey({
        treeName: valueOrEmpty(b.tree_name),
        gitRepositoryBranch: valueOrEmpty(b.git_repository_branch),
        separator: '/',
      });

      const aIsPinned = PinnedTrees.some(regex => regex.test(aKey));
      const bIsPinned = PinnedTrees.some(regex => regex.test(bKey));

      if (aIsPinned && !bIsPinned) {
        return -1;
      }
      if (!aIsPinned && bIsPinned) {
        return 1;
      }

      return aKey.localeCompare(bKey);
    });
  }, [treeTableRows]);

  const columns = useMemo(() => getColumns(origin), [origin]);

  const table = useReactTable({
    data: orderedData,
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
            return cell.column.columnDef.id === 'git_commit_tags' ? (
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
                      commitHash: cell.row.original.git_commit_hash,
                      commitName: cell.row.original.git_commit_name,
                      commitTags: cell.row.original.git_commit_tags,
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
          <MemoizedInputTime navigateFrom="/tree" />
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
