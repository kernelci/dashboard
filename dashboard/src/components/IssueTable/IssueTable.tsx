import type { JSX } from 'react/jsx-runtime';

import {
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from '@tanstack/react-table';

import type { Row, SortingState, ColumnDef, Cell } from '@tanstack/react-table';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo, useState } from 'react';
import type { UseQueryResult } from '@tanstack/react-query';

import { FormattedMessage } from 'react-intl';

import type {
  IssueListingResponse,
  IssueListingTableItem,
} from '@/types/issueListing';
import { TableHeader } from '@/components/Table/TableHeader';
import { usePaginationState } from '@/hooks/usePaginationState';
import { columnWidthStyle, useLayoutTable } from '@/hooks/useLayoutTable';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableRow,
} from '@/components/ui/table';
import { TableFrame } from '@/components/Table/TableFrame';

import { IssueCulprit } from '@/components/Issue/IssueCulprit';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';
import { valueOrEmpty } from '@/lib/string';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { shouldShowRelativeDate } from '@/lib/date';
import { RedirectFrom } from '@/types/general';

import QuerySwitcher from '@/components/QuerySwitcher/QuerySwitcher';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';

const getLinkProps = (
  row: Row<IssueListingTableItem>,
  cell: Cell<IssueListingTableItem, unknown>,
): LinkProps => {
  if (
    cell.column.id === 'treeBranch' &&
    row.original.git_commit_hash !== undefined
  ) {
    return {
      from: '/issues',
      to: '/tree/$treeId',
      params: { treeId: row.original.git_commit_hash },
      state: s => s,
      search: previousSearch => ({
        ...previousSearch,
        origin: row.original.origin,
        treeInfo: {
          gitBranch: row.original.git_repository_branch,
          gitUrl: row.original.git_repository_url,
          headCommitHash: row.original.git_commit_hash,
          CommitName: row.original.git_commit_name,
          treeName: row.original.tree_name,
        },
      }),
    };
  }

  return {
    from: '/issues',
    to: '/issue/$issueId',
    params: { issueId: row.original.id },
    state: s => ({
      ...s,
      id: row.original.id,
      from: RedirectFrom.Issues,
    }),
    search: _ => ({
      origin: row.original.origin,
      issueVersion: row.original.version,
    }),
  };
};

const columns: ColumnDef<IssueListingTableItem>[] = [
  {
    id: 'comment',
    accessorKey: 'comment',
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="issueDetails.comment"
        tooltipId="issueDetails.issueListingInfo"
      />
    ),
    cell: ({ row }): JSX.Element | string =>
      row.getValue('comment') ? (
        <Tooltip>
          <TooltipTrigger className="max-w-full truncate">
            {row.getValue('comment')}
          </TooltipTrigger>
          <TooltipContent>{row.original.id}</TooltipContent>
        </Tooltip>
      ) : (
        row.original.id
      ),
    meta: {
      headerIntlKey: 'issueDetails.comment',
      isRowHeader: true,
      minWidth: 160,
      maxWidth: 480,
    },
  },
  {
    accessorKey: 'origin',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="global.origin" />
    ),
    meta: {
      headerIntlKey: 'global.origin',
      minWidth: 80,
      maxWidth: 160,
    },
  },
  {
    id: 'culprit',
    accessorFn: (original, _): boolean[] => {
      return [
        original.culprit_code ?? false,
        original.culprit_harness ?? false,
        original.culprit_tool ?? false,
      ];
    },
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="issueDetails.culpritTitle"
        tooltipId="issueListing.culpritInfo"
      />
    ),
    cell: ({ row }): JSX.Element => (
      <IssueCulprit
        culprit_code={row.original.culprit_code}
        culprit_harness={row.original.culprit_harness}
        culprit_tool={row.original.culprit_tool}
      />
    ),
    meta: {
      headerIntlKey: 'issueDetails.culpritTitle',
      minWidth: 100,
      maxWidth: 200,
    },
  },
  {
    accessorKey: 'first_seen',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="issue.firstSeen" />
    ),
    cell: ({ row }): JSX.Element => (
      <TooltipDateTime
        dateTime={row.getValue('first_seen')}
        lineBreak={true}
        showRelative={shouldShowRelativeDate(row.getValue('first_seen'))}
      />
    ),
    meta: {
      headerIntlKey: 'issue.firstSeen',
      minWidth: 100,
      maxWidth: 180,
    },
  },
  {
    id: 'treeBranch',
    accessorFn: (original, _): string => {
      if (!original.tree_name && !original.git_repository_branch) {
        return '-';
      }
      return [
        valueOrEmpty(original.tree_name),
        valueOrEmpty(original.git_repository_branch),
      ].join(' / ');
    },
    header: ({ column }): JSX.Element => (
      <TableHeader
        column={column}
        intlKey="global.treeBranch"
        tooltipId="issueListing.treeBranchTooltip"
      />
    ),
    meta: {
      headerIntlKey: 'global.treeBranch',
      minWidth: 120,
      maxWidth: 280,
    },
  },
];

interface IIssueTable {
  issueListing?: IssueListingResponse;
  status?: UseQueryResult['status'];
  queryData?: unknown;
  error?: Error | null;
  isLoading?: boolean;
}

export const IssueTable = ({
  issueListing,
  status,
  queryData,
  error,
  isLoading,
}: IIssueTable): JSX.Element => {
  const { listingSize } = useSearch({ from: '/_main/issues' });
  const navigate = useNavigate({ from: '/issues' });

  const [sorting, setSorting] = useState<SortingState>([
    { id: 'first_seen', desc: true },
  ]);

  const { pagination, paginationUpdater } = usePaginationState(
    'issueListing',
    listingSize,
  );

  const issueTableRows = useMemo((): IssueListingTableItem[] => {
    if (!issueListing) {
      return [];
    }

    return issueListing.issues.map(issue => ({
      ...issue,
      ...issueListing.extras[issue.id],
    }));
  }, [issueListing]);

  const {
    table,
    containerRef,
    columnWidths,
    tableWidth,
    columnsMenu,
    tableHeaders,
  } = useLayoutTable({
    data: issueTableRows,
    columns,
    initialColumnVisibility: { culprit: false },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: paginationUpdater,
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting,
      pagination,
    },
  });

  const modelRows = table.getRowModel().rows;
  const tableBody = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <TableRow key={row.id}>
          {row.getVisibleCells().map(cell => {
            return (
              <TableCellWithLink
                key={cell.id}
                className="overflow-hidden"
                style={columnWidthStyle(columnWidths[cell.column.id])}
                linkClassName="w-full inline-block h-full"
                linkProps={getLinkProps(row, cell)}
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
          <FormattedMessage id="issueListing.notFound" />
        </TableCell>
      </TableRow>
    );
  }, [modelRows, columnWidths]);

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
    <>
      <div className="mb-4 flex justify-end">{columnsMenu}</div>
      <QuerySwitcher
        status={status}
        data={queryData}
        error={error}
        customError={
          <MemoizedSectionError
            isLoading={isLoading}
            errorMessage={error?.message}
            emptyLabel="issueListing.notFound"
          />
        }
      >
        <TableFrame
          containerRef={containerRef}
          tableWidth={tableWidth}
          headerComponents={tableHeaders}
        >
          <TableBody>{tableBody}</TableBody>
        </TableFrame>
      </QuerySwitcher>
      <PaginationInfo
        table={table}
        intlLabel="global.issues"
        onPaginationChange={navigateWithPageSize}
      />
    </>
  );
};
