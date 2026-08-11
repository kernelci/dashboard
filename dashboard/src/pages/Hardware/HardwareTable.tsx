import type {
  ColumnDef,
  ColumnFiltersState,
  ExpandedState,
  Row,
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

import { Fragment, useCallback, useMemo, useState, type JSX } from 'react';
import type { UseQueryResult } from '@tanstack/react-query';

import { FormattedMessage } from 'react-intl';

import { useNavigate, useSearch, type LinkProps } from '@tanstack/react-router';

import { MdChevronRight, MdDeveloperBoard } from 'react-icons/md';

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

import { REDUCED_TIME_SEARCH } from '@/utils/constants/general';

import { usePaginationState } from '@/hooks/usePaginationState';

import { zPossibleTabValidator } from '@/types/tree/TreeDetails';

import type { ListingTableColumnMeta } from '@/types/table';

import { RedirectFrom, type TFilter } from '@/types/general';

import { EMPTY_VALUE } from '@/lib/string';
import { Badge } from '@/components/ui/badge';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import { LoadingCircle } from '@/components/ui/loading-circle';

import { FilterLabel } from '@/components/FilterLabel/FilterLabel';
import { HardwareRegistryListingDetails } from '@/components/HardwareRegistry/HardwareRegistry';
import {
  getMockHardwareRegistryListingInfo,
  type HardwareRegistryInfo,
} from '@/lib/hardwareRegistryMock';

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
  selectorsLoading?: boolean;
  onTreeChange?: (nextSelection: HardwareRevisionSelectorValue) => void;
  onClearSelection?: () => void;
}

type HardwareListingRoutes = '/hardware';
type HardwareListingRow = HardwareItem & {
  registry?: HardwareRegistryInfo;
};

const getLinkProps = (
  row: Row<HardwareListingRow>,
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
): ColumnDef<HardwareListingRow>[] => {
  return [
    {
      id: 'registry_expander',
      header: () => null,
      enableSorting: false,
      cell: ({ row }): JSX.Element | null =>
        row.getCanExpand() ? (
          <button
            type="button"
            aria-label={
              row.getIsExpanded() ? 'Collapse details' : 'Expand details'
            }
            aria-expanded={row.getIsExpanded()}
            onClick={row.getToggleExpandedHandler()}
          >
            <MdChevronRight
              className={`size-5 transition-transform ${
                row.getIsExpanded() ? 'rotate-90' : ''
              }`}
            />
          </button>
        ) : null,
    },
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
      id: 'processor',
      accessorFn: row => row.registry?.processor?.id ?? '',
      header: ({ column }): JSX.Element => (
        <TableHeader column={column} intlKey="global.processor" />
      ),
      cell: ({ row }): JSX.Element => {
        const processorId = row.original.registry?.processor?.id;
        if (!processorId) {
          return <>{EMPTY_VALUE}</>;
        }

        return (
          <span className="flex items-center gap-2">
            <MdDeveloperBoard className="text-blue size-5 shrink-0" />
            {processorId}
          </span>
        );
      },
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
  selectorsLoading = false,
  onTreeChange = (): void => {},
  onClearSelection = (): void => {},
}: IHardwareTable): JSX.Element {
  const { listingSize, intervalInDays } = useSearch({ strict: false });
  const navigate = useNavigate({ from: navigateFrom });

  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [expanded, setExpanded] = useState<ExpandedState>({});
  const { pagination, paginationUpdater } = usePaginationState(
    'hardwareListing',
    listingSize,
  );

  const data = useMemo(() => {
    return treeTableRows.map((row, index) => ({
      ...row,
      registry: getMockHardwareRegistryListingInfo(row.platform, index),
    }));
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
    onExpandedChange: setExpanded,
    getCoreRowModel: getCoreRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    getRowCanExpand: row => row.original.registry !== undefined,
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: paginationUpdater,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
      pagination,
      expanded,
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
        <Fragment key={row.id}>
          <TableRow>
            {row.getVisibleCells().map(cell => {
              if (cell.column.id === 'registry_expander') {
                return (
                  <TableCell key={cell.id} className="w-10">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                );
              }

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
          {row.getIsExpanded() && row.original.registry && (
            <TableRow>
              <TableCell colSpan={columns.length} className="p-0">
                <HardwareRegistryListingDetails info={row.original.registry} />
              </TableCell>
            </TableRow>
          )}
        </Fragment>
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
        {selectorsLoading ? (
          <LoadingCircle />
        ) : (
          selectors &&
          selectors.length > 0 && (
            <HardwareRevisionSelectors
              selectors={selectors}
              selectedTree={selectedTree}
              selectedBranch={selectedBranch}
              selection={selection}
              onTreeChange={onTreeChange}
              onClearSelection={onClearSelection}
            />
          )
        )}
        <div className="ml-auto flex flex-wrap items-center justify-end gap-4">
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
      <div className="flex flex-wrap items-start justify-between gap-4">
        {!selection && (
          <FilterLabel days={intervalInDays ?? REDUCED_TIME_SEARCH} />
        )}
        <div className="ml-auto">
          <PaginationInfo
            table={table}
            intlLabel="global.hardware"
            onPaginationChange={navigateWithPageSize}
          />
        </div>
      </div>
    </div>
  );
}
