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
import type { UseQueryResult } from '@tanstack/react-query';

import { FormattedMessage } from 'react-intl';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import type { TreeTableBody, TreeV2 } from '@/types/tree/Tree';
import { RedirectFrom } from '@/types/general';
import type { TFilter } from '@/types/general';

import { formattedBreakLineValue } from '@/locales/messages';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import { usePaginationState } from '@/hooks/usePaginationState';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import { ConditionalTableCell } from '@/components/Table/ConditionalTableCell';

import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';

import { sanitizeTableValue } from '@/components/Table/tableUtils';

import { GroupedTestStatusWithLink } from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import {
  ItemsPerPageSelector,
  ListingCount,
  PaginationButtons,
  PaginationInfo,
} from '@/components/Table/PaginationInfo';
import { CommitTagTooltip } from '@/components/Tooltip/CommitTagTooltip';

import type { ListingTableColumnMeta } from '@/types/table';

import { statusCountToRequiredStatusCount } from '@/utils/status';

import { MemoizedInputTime } from '@/components/InputTime';
import { shouldShowRelativeDate } from '@/lib/date';
import { valueOrEmpty } from '@/lib/string';
import { PinnedTrees } from '@/utils/constants/tables';
import { makeTreeIdentifierKey } from '@/utils/trees';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import type { TreeListingRoutesMap } from '@/utils/constants/treeListing';

const getLinkProps = (
  row: Row<TreeTableBody>,
  origin: string,
  tabTarget?: string,
  diffFilter?: TFilter,
): LinkProps => {
  const tree_name = row.original.tree_name;
  const branch = row.original.git_repository_branch;
  const hash = row.original.git_commit_hash;
  const repositoryUrl = row.original.git_repository_url;
  const commitName = row.original.git_commit_name;

  const canGoDirect = tree_name && branch && hash;

  const urlDirection: LinkProps = canGoDirect
    ? {
        to: '/tree/$treeName/$branch/$hash',
        params: {
          treeName: tree_name,
          branch: branch,
          hash: hash,
        },
        search: previousSearch => ({
          origin: origin,
          currentPageTab: zPossibleTabValidator.parse(tabTarget),
          diffFilter: diffFilter ?? {},
          intervalInDays: previousSearch.intervalInDays,
        }),
      }
    : {
        to: '/tree/$treeId',
        params: { treeId: hash },
        search: previousSearch => ({
          origin: origin,
          currentPageTab: zPossibleTabValidator.parse(tabTarget),
          diffFilter: diffFilter ?? {},
          treeInfo: {
            ...(repositoryUrl && { gitUrl: repositoryUrl }),
            ...(branch && { gitBranch: branch }),
            ...(tree_name && { treeName: tree_name }),
            ...(commitName && { commitName: commitName }),
            headCommitHash: hash,
          },
          intervalInDays: previousSearch.intervalInDays,
        }),
      };

  const stateParams = canGoDirect
    ? {
        treeName: tree_name,
        branch: branch,
        id: hash,
      }
    : { id: hash };

  return {
    ...urlDirection,
    state: s => ({
      ...s,
      ...stateParams,
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

export const commonTreeTableColumns: ColumnDef<TreeTableBody | TreeV2>[] = [
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
];

const getColumns = (
  origin: string,
  showStatusUnavailable?: boolean,
): ColumnDef<TreeTableBody>[] => {
  return [
    ...(commonTreeTableColumns as ColumnDef<TreeTableBody>[]),
    {
      accessorKey: 'build_status.PASS',
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
        ) : showStatusUnavailable ? (
          <span>-</span>
        ) : (
          <FormattedMessage id="global.loading" defaultMessage="Loading..." />
        );
      },
      meta: {
        tabTarget: 'global.builds',
      },
    },
    {
      accessorKey: 'boot_status.pass',
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
        ) : showStatusUnavailable ? (
          <span>-</span>
        ) : (
          <FormattedMessage id="global.loading" defaultMessage="Loading..." />
        );
      },
      meta: {
        tabTarget: 'global.boots',
      },
    },
    {
      accessorKey: 'test_status.pass',
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
        ) : showStatusUnavailable ? (
          <span>-</span>
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

export const sortTreesWithPinnedFirst = <T extends TreeTableBody | TreeV2>(
  treeTableRows: T[],
): T[] => {
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
};

export function TreeTable({
  treeTableRows,
  status,
  queryData,
  error,
  isLoading,
  showStatusUnavailable,
  urlFromMap,
}: {
  treeTableRows: TreeTableBody[];
  status?: UseQueryResult['status'];
  queryData?: unknown;
  error?: Error | null;
  isLoading?: boolean;
  showStatusUnavailable?: boolean;
  urlFromMap: TreeListingRoutesMap['v1'];
}): JSX.Element {
  const { origin, listingSize } = useSearch({ from: urlFromMap.search });
  const navigate = useNavigate({ from: urlFromMap.navigate });

  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } = usePaginationState(
    'treeListing',
    listingSize,
  );

  const orderedData = useMemo(
    () => sortTreesWithPinnedFirst(treeTableRows),
    [treeTableRows],
  );

  const columns = useMemo(
    () => getColumns(origin, showStatusUnavailable),
    [origin, showStatusUnavailable],
  );

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
            return (
              <ConditionalTableCell
                key={cell.id}
                cell={cell}
                linkProps={getLinkProps(row, origin, tabTarget)}
                linkClassName="w-full inline-block h-full"
              />
            );
          })}
        </TableRow>
      ))
    ) : (
      <TableRow>
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="treeListing.notFound" />
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
      <div className="flex flex-wrap items-center justify-end gap-4">
        <span className="text-dim-gray flex-1 justify-start text-left text-sm">
          <FormattedMessage
            id="global.projectUnderDevelopment"
            values={formattedBreakLineValue}
          />
        </span>
        <div className="flex justify-end gap-y-2 max-[700px]:flex-wrap">
          <MemoizedInputTime navigateFrom={urlFromMap.navigate} />
          <ItemsPerPageSelector
            table={table}
            onPaginationChange={navigateWithPageSize}
            className="pl-4"
          />
        </div>
        <div className="flex justify-end gap-y-2 max-[700px]:flex-wrap">
          <ListingCount table={table} intlLabel="global.trees" />
          <PaginationButtons table={table} className="pl-4" />
        </div>
      </div>
      {showStatusUnavailable && (
        <div className="rounded-md border border-red-500 bg-red-50 p-4 text-red-800">
          <p className="text-sm">
            <FormattedMessage id="treeListing.statusUnavailable" />
          </p>
        </div>
      )}
      <QuerySwitcher
        status={status}
        data={queryData}
        error={error}
        customError={
          <MemoizedSectionError
            isLoading={isLoading}
            errorMessage={error?.message}
            emptyLabel="treeListing.notFound"
          />
        }
      >
        <BaseTable headerComponents={tableHeaders}>
          <TableBody>{tableBody}</TableBody>
        </BaseTable>
      </QuerySwitcher>
      <PaginationInfo
        table={table}
        intlLabel="global.trees"
        onPaginationChange={navigateWithPageSize}
      />
    </div>
  );
}
