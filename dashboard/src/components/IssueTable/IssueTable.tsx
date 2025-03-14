import type { JSX } from 'react/jsx-runtime';

import {
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import type { Row, SortingState, ColumnDef, Cell } from '@tanstack/react-table';

import type { LinkProps } from '@tanstack/react-router';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { useCallback, useMemo, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import type {
  IssueListingResponse,
  IssueListingTableItem,
} from '@/types/issueListing';
import { TableHeader } from '@/components/Table/TableHeader';
import { usePaginationState } from '@/hooks/usePaginationState';
import { formattedBreakLineValue } from '@/locales/messages';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableRow,
} from '@/components/ui/table';
import BaseTable, { TableHead } from '@/components/Table/BaseTable';

import { MemoizedInputTime } from '@/components/InputTime';

import { IssueCulprit } from '@/components/Issue/IssueCulprit';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/Tooltip';
import { valueOrEmpty } from '@/lib/string';

import { TooltipDateTime } from '@/components/TooltipDateTime';
import { shouldShowRelativeDate } from '@/lib/date';
import { RedirectFrom } from '@/types/general';

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
    search: s => ({
      origin: s.origin,
    }),
  };
};

const columns: ColumnDef<IssueListingTableItem>[] = [
  {
    id: 'comment',
    accessorKey: 'comment',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="issueDetails.comment" />
    ),
    cell: ({ row }): JSX.Element | string =>
      row.getValue('comment') ? (
        <Tooltip>
          <TooltipTrigger className="max-w-[200px] truncate md:max-w-[225px] xl:max-w-[315px] 2xl:max-w-[570px]">
            {row.getValue('comment')}
          </TooltipTrigger>
          <TooltipContent>{row.original.id}</TooltipContent>
        </Tooltip>
      ) : (
        row.original.id
      ),
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
  },
];

interface IIssueTable {
  issueListing?: IssueListingResponse;
}

export const IssueTable = ({ issueListing }: IIssueTable): JSX.Element => {
  const { listingSize } = useSearch({ from: '/_main/issues' });
  const navigate = useNavigate({ from: '/issues' });

  const [sorting, setSorting] = useState<SortingState>([
    {
      id: 'first_seen',
      desc: true,
    },
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

  const table = useReactTable({
    data: issueTableRows,
    columns,
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
            return (
              <TableCellWithLink
                key={cell.id}
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
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
  }, [modelRows]);

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
          <MemoizedInputTime navigateFrom="/issues" />
          <PaginationInfo
            table={table}
            intlLabel="global.issues"
            onPaginationChange={navigateWithPageSize}
          />
        </div>
      </div>
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableBody}</TableBody>
      </BaseTable>
      <PaginationInfo
        table={table}
        intlLabel="global.issues"
        onPaginationChange={navigateWithPageSize}
      />
    </div>
  );
};
