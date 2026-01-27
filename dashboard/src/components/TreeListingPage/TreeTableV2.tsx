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

import type { TreeV2 } from '@/types/tree/Tree';
import { RedirectFrom } from '@/types/general';
import type { TFilter } from '@/types/general';

import { formattedBreakLineValue } from '@/locales/messages';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import { usePaginationState } from '@/hooks/usePaginationState';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import { ConditionalTableCell } from '@/components/Table/ConditionalTableCell';

import { BaseGroupedStatusWithLink } from '@/components/Status/Status';
import { TableHeader } from '@/components/Table/TableHeader';
import {
  ItemsPerPageSelector,
  ListingCount,
  PaginationButtons,
  PaginationInfo,
} from '@/components/Table/PaginationInfo';

import type { ListingTableColumnMeta } from '@/types/table';

import { MemoizedInputTime } from '@/components/InputTime';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import type { TreeListingRoutesMap } from '@/utils/constants/treeListing';

import { commonTreeTableColumns, sortTreesWithPinnedFirst } from './TreeTable';

const getLinkProps = (
  row: Row<TreeV2>,
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
    }),
  };
};

const getColumns = (origin: string): ColumnDef<TreeV2>[] => {
  return [
    ...(commonTreeTableColumns as ColumnDef<TreeV2>[]),
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
        return (
          <BaseGroupedStatusWithLink
            groupedStatus={{
              successCount: row.original.build_status.PASS,
              failedCount: row.original.build_status.FAIL,
              inconclusiveCount: row.original.build_status.INCONCLUSIVE,
            }}
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
        return (
          <BaseGroupedStatusWithLink
            groupedStatus={{
              successCount: row.original.boot_status.PASS,
              failedCount: row.original.boot_status.FAIL,
              inconclusiveCount: row.original.boot_status.INCONCLUSIVE,
            }}
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
        return (
          <BaseGroupedStatusWithLink
            groupedStatus={{
              successCount: row.original.test_status.PASS,
              failedCount: row.original.test_status.FAIL,
              inconclusiveCount: row.original.test_status.INCONCLUSIVE,
            }}
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
        );
      },
      meta: {
        tabTarget: 'global.tests',
      },
    },
  ];
};

export function TreeTableV2({
  treeTableRows,
  status,
  queryData,
  error,
  isLoading,
  urlFromMap,
}: {
  treeTableRows: TreeV2[];
  status?: UseQueryResult['status'];
  queryData?: unknown;
  error?: Error | null;
  isLoading?: boolean;
  showStatusUnavailable?: boolean;
  urlFromMap: TreeListingRoutesMap['v2'];
}): JSX.Element {
  const { origin, listingSize } = useSearch({
    from: urlFromMap.search,
  });
  const navigate = useNavigate({ from: urlFromMap.navigate });

  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } = usePaginationState(
    'treeListing',
    listingSize,
  );

  const orderedData = useMemo(() => {
    return sortTreesWithPinnedFirst(treeTableRows);
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
          <MemoizedInputTime navigateFrom="/tree" />
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
