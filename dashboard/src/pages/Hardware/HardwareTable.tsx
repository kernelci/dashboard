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

import { useNavigate, useSearch, type LinkProps } from '@tanstack/react-router';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import type { MessagesKey } from '@/locales/messages';

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

import type {
  HardwareItem,
  HardwareRevisionSelection,
  HardwareSelectorBranch,
  HardwareSelectorTree,
} from '@/types/hardware';

import { sumStatus } from '@/utils/status';

import { usePaginationState } from '@/hooks/usePaginationState';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type { ListingTableColumnMeta } from '@/types/table';

import { RedirectFrom, type TFilter } from '@/types/general';

import { EMPTY_VALUE } from '@/lib/string';
import { Badge } from '@/components/ui/badge';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

import { buildHardwareDetailsSearch } from './hardwareTableUtils';
import { HardwareRevisionSelectors } from './HardwareRevisionSelectors';
import type { HardwareRevisionSelectorValue } from './hardwareSelection';

// TODO Extract and reuse the table
interface IHardwareTable {
  treeTableRows: HardwareItem[];
  startTimestampInSeconds: number;
  endTimestampInSeconds: number;
  status?: UseQueryResult['status'];
  queryData?: unknown;
  error?: Error | null;
  isLoading?: boolean;
  navigateFrom: HardwareListingRoutes;
  emptyMessageId?: MessagesKey;
  selectors?: HardwareSelectorTree[];
  selectedTree?: HardwareSelectorTree | null;
  selectedBranch?: HardwareSelectorBranch | null;
  selection?: HardwareRevisionSelection | null;
  onTreeChange?: (nextSelection: HardwareRevisionSelectorValue) => void;
}

type HardwareListingRoutes = '/hardware';

const getLinkProps = (
  row: Row<HardwareItem>,
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  navigateFrom: HardwareListingRoutes,
  tabTarget?: string,
  newDiffFilter?: TFilter,
): LinkProps => {
  const currentPageTab = zPossibleTabValidator.parse(tabTarget);

  return {
    from: navigateFrom,
    to: '/hardware/$hardwareId',
    params: { hardwareId: row.original.platform },
    search: previousSearch =>
      buildHardwareDetailsSearch({
        previousSearch,
        currentPageTab,
        startTimestampInSeconds,
        endTimestampInSeconds,
        newDiffFilter,
      }),
    state: s => ({
      ...s,
      id: row.original.platform,
      from: RedirectFrom.Hardware,
      hardwareStatusCount: {
        builds: row.original.build_status_summary,
        tests: row.original.test_status_summary,
        boots: row.original.boot_status_summary,
      },
    }),
  };
};

const getColumns = (
  startTimestampInSeconds: number,
  endTimestampInSeconds: number,
  navigateFrom: HardwareListingRoutes,
): ColumnDef<HardwareItem>[] => {
  return [
    {
      accessorKey: 'platform',
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="global.platform" />
      ),
      meta: {
        tabTarget: 'global.builds',
      },
    },
    {
      accessorKey: 'hardware',
      accessorFn: ({ hardware }): number => {
        return hardware ? hardware.length : 0;
      },
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="global.compatibles" />
      ),
      cell: ({ row }): JSX.Element => {
        const hardwares = row.original.hardware;
        if (hardwares === undefined || hardwares === null) {
          return <>{EMPTY_VALUE}</>;
        }

        return (
          <div className="flex max-w-xl flex-wrap gap-2">
            {hardwares.map(hardware => {
              return (
                <Badge
                  key={hardware}
                  variant="outline"
                  className="text-sm font-normal text-nowrap"
                >
                  {hardware}
                </Badge>
              );
            })}
          </div>
        );
      },
      meta: {
        tabTarget: 'global.builds',
      },
    },
    {
      accessorKey: 'build_status_summary',
      accessorFn: ({ build_status_summary: buildCount }): number =>
        buildCount ? sumStatus(buildCount) : 0,
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
        return row.original.build_status_summary ? (
          <BaseGroupedStatusWithLink
            groupedStatus={{
              successCount: row.original.build_status_summary.PASS,
              failedCount: row.original.build_status_summary.FAIL,
              inconclusiveCount: row.original.build_status_summary.INCONCLUSIVE,
            }}
            passLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                buildStatus: { PASS: true },
              },
            )}
            failLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                buildStatus: { FAIL: true },
              },
            )}
            inconclusiveLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                buildStatus: {
                  MISS: true,
                  ERROR: true,
                  SKIP: true,
                  DONE: true,
                  NULL: true,
                },
              },
            )}
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
      accessorKey: 'boot_status_summary',
      accessorFn: ({ boot_status_summary: bootStatusCount }): number =>
        bootStatusCount ? sumStatus(bootStatusCount) : 0,
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
        return row.original.boot_status_summary ? (
          <BaseGroupedStatusWithLink
            groupedStatus={{
              successCount: row.original.boot_status_summary.PASS,
              failedCount: row.original.boot_status_summary.FAIL,
              inconclusiveCount: row.original.boot_status_summary.INCONCLUSIVE,
            }}
            passLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                bootStatus: { PASS: true },
              },
            )}
            failLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                bootStatus: { FAIL: true },
              },
            )}
            inconclusiveLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                bootStatus: {
                  MISS: true,
                  ERROR: true,
                  SKIP: true,
                  DONE: true,
                  NULL: true,
                },
              },
            )}
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
      accessorKey: 'test_status_summary',
      accessorFn: ({ test_status_summary: testStatusCount }): number =>
        testStatusCount ? sumStatus(testStatusCount) : 0,
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
        return row.original.test_status_summary ? (
          <BaseGroupedStatusWithLink
            groupedStatus={{
              successCount: row.original.test_status_summary.PASS,
              failedCount: row.original.test_status_summary.FAIL,
              inconclusiveCount: row.original.test_status_summary.INCONCLUSIVE,
            }}
            passLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                testStatus: { PASS: true },
              },
            )}
            failLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                testStatus: { FAIL: true },
              },
            )}
            inconclusiveLinkProps={getLinkProps(
              row,
              startTimestampInSeconds,
              endTimestampInSeconds,
              navigateFrom,
              tabTarget,
              {
                testStatus: {
                  MISS: true,
                  ERROR: true,
                  SKIP: true,
                  DONE: true,
                  NULL: true,
                },
              },
            )}
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

export function HardwareTable({
  treeTableRows,
  startTimestampInSeconds,
  endTimestampInSeconds,
  status,
  queryData,
  error,
  isLoading,
  navigateFrom,
  emptyMessageId = 'hardwareListing.notFound',
  selectors,
  selectedTree = null,
  selectedBranch = null,
  selection = null,
  onTreeChange = (): void => {},
}: IHardwareTable): JSX.Element {
  const { listingSize } = useSearch({ strict: false });
  const navigate = useNavigate({ from: navigateFrom });

  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const { pagination, paginationUpdater } = usePaginationState(
    'hardwareListing',
    listingSize,
  );

  const data = useMemo(() => {
    return treeTableRows;
  }, [treeTableRows]);

  const columns = useMemo(
    () =>
      getColumns(startTimestampInSeconds, endTimestampInSeconds, navigateFrom),
    [startTimestampInSeconds, endTimestampInSeconds, navigateFrom],
  );

  const table = useReactTable({
    data,
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
                linkProps={getLinkProps(
                  row,
                  startTimestampInSeconds,
                  endTimestampInSeconds,
                  navigateFrom,
                  tabTarget,
                )}
                linkClassName="w-full inline-block h-full"
              />
            );
          })}
        </TableRow>
      ))
    ) : (
      <TableRow>
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id={emptyMessageId} />
        </TableCell>
      </TableRow>
    );
  }, [
    emptyMessageId,
    modelRows,
    navigateFrom,
    columns.length,
    startTimestampInSeconds,
    endTimestampInSeconds,
  ]);

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
      <div className="flex flex-wrap items-end justify-between gap-4">
        {selectors && (
          <HardwareRevisionSelectors
            selectors={selectors}
            selectedTree={selectedTree}
            selectedBranch={selectedBranch}
            selection={selection}
            onTreeChange={onTreeChange}
          />
        )}
        <div className="flex flex-wrap items-center justify-end gap-4">
          <div className="flex justify-end gap-y-2 max-[700px]:flex-wrap">
            <ItemsPerPageSelector
              table={table}
              onPaginationChange={navigateWithPageSize}
              className="pl-4"
            />
          </div>
          <div className="flex justify-end gap-y-2 max-[700px]:flex-wrap">
            <ListingCount table={table} intlLabel="global.hardware" />
            <PaginationButtons table={table} className="pl-4" />
          </div>
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
            emptyLabel="hardwareListing.notFound"
          />
        }
      >
        <BaseTable headerComponents={tableHeaders}>
          <TableBody>{tableBody}</TableBody>
        </BaseTable>
      </QuerySwitcher>
      <PaginationInfo
        table={table}
        intlLabel="global.hardware"
        onPaginationChange={navigateWithPageSize}
      />
    </div>
  );
}
