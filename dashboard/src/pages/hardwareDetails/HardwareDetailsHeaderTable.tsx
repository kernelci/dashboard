import type {
  ColumnDef,
  RowSelectionState,
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

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { FormattedMessage } from 'react-intl';

import { useNavigate } from '@tanstack/react-router';

import BaseTable, { TableHead } from '@/components/Table/BaseTable';
import { TableHeader } from '@/components/Table/TableHeader';
import { TableBody, TableCell, TableRow } from '@/components/ui/table';
import type {
  CommitHistory,
  PreparedTrees,
} from '@/types/hardware/hardwareDetails';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/Tooltip';
import { sanitizeTableValue } from '@/components/Table/tableUtils';
import { PaginationInfo } from '@/components/Table/PaginationInfo';
import { IndeterminateCheckbox } from '@/components/Checkbox/IndeterminateCheckbox';
import { useDebounce } from '@/hooks/useDebounce';
import { GroupedTestStatus } from '@/components/Status/Status';

import { usePaginationState } from '@/hooks/usePaginationState';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { LoadingCircle } from '@/components/ui/loading-circle';
import CopyButton from '@/components/Button/CopyButton';

const DEBOUNCE_INTERVAL = 2000;

interface IHardwareHeader {
  treeItems: PreparedTrees[];
  selectedIndexes?: number[];
  updateTreeFilters: (selectedIndexes: number[]) => void;
}

const CommitSelector = ({
  headCommitHash,
  headCommitName,
  selectableCommits,
  isCommitsLoading,
  treeIndex,
  rowLength,
  isMainPageLoading,
}: {
  headCommitName?: string;
  headCommitHash?: string;
  selectableCommits: CommitHistory[];
  isCommitsLoading: boolean;
  isMainPageLoading: boolean;
  treeIndex: string;
  rowLength: number;
}): JSX.Element => {
  const navigate = useNavigate({ from: '/hardware/$hardwareId/' });

  const selectedCommitHash = useRef(headCommitHash);

  const navigateToThePast = useCallback(
    (commitHash: string) => {
      if (treeIndex === null) return;
      selectedCommitHash.current = commitHash;

      navigate({
        search: current => {
          const parsedTreeIndex =
            current.treeIndexes?.length ?? 0 > 0
              ? current.treeIndexes
              : Array.from(Array(rowLength).keys());
          return {
            ...current,
            treeCommits: { ...current.treeCommits, [treeIndex]: commitHash },
            treeIndexes: parsedTreeIndex,
          };
        },
      });
    },
    [navigate, rowLength, treeIndex],
  );

  const sortedSelectableCommits = useMemo(() => {
    return selectableCommits.sort(
      (a, b) =>
        new Date(b.start_time).getTime() - new Date(a.start_time).getTime(),
    );
  }, [selectableCommits]);

  if (selectableCommits.length < 1 || isCommitsLoading) {
    return (
      <Tooltip>
        <TooltipTrigger>
          <div className="flex items-center gap-4">
            {sanitizeTableValue(headCommitName, false)}
            {isCommitsLoading && <LoadingCircle />}
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <>{headCommitHash}</>
        </TooltipContent>
      </Tooltip>
    );
  }
  return (
    <div className="flex items-center gap-4">
      <Select onValueChange={navigateToThePast} disabled={isMainPageLoading}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder={headCommitHash} />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
            {sortedSelectableCommits.map(commit => (
              <SelectItem
                key={commit.git_commit_hash}
                value={commit.git_commit_hash}
              >
                {commit.git_commit_hash} - {commit.start_time}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectContent>
      </Select>
      {isMainPageLoading ? (
        <LoadingCircle />
      ) : (
        <CopyButton value={selectedCommitHash.current} />
      )}
    </div>
  );
};

const columns: ColumnDef<PreparedTrees>[] = [
  {
    id: 'select',
    header: ({ table }) => (
      <IndeterminateCheckbox
        {...{
          checked: table.getIsAllRowsSelected(),
          indeterminate: table.getIsSomeRowsSelected(),
          onChange: table.getToggleAllRowsSelectedHandler(),
          disabled: table.getIsAllRowsSelected(),
        }}
      />
    ),
    cell: ({ row, table }) => (
      <IndeterminateCheckbox
        {...{
          checked: row.getIsSelected(),
          disabled:
            !row.getCanSelect() ||
            (Object.keys(table.getState().rowSelection).length === 1 &&
              row.getIsSelected()),
          onChange: row.getToggleSelectedHandler(),
        }}
      />
    ),
  },
  {
    accessorKey: 'treeName',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.tree" />
    ),
    cell: ({ row }): JSX.Element => (
      <Tooltip>
        <TooltipTrigger>{row.getValue('treeName')}</TooltipTrigger>
        <TooltipContent>{row.original.gitRepositoryUrl}</TooltipContent>
      </Tooltip>
    ),
  },
  {
    accessorKey: 'gitRepositoryBranch',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.branch" />
    ),
  },
  {
    accessorKey: 'headGitCommitName',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.commitTag" />
    ),
    cell: ({ row, table }): JSX.Element => (
      <CommitSelector
        headCommitName={row.original.headGitCommitName}
        headCommitHash={row.original.headGitCommitHash}
        selectableCommits={row.original.selectableCommits}
        isCommitsLoading={row.original.isCommitHistoryDataLoading}
        treeIndex={row.original.index}
        rowLength={table.getCoreRowModel().rows.length}
        isMainPageLoading={row.original.isMainPageLoading}
      />
    ),
  },
  {
    accessorKey: 'selectedCommitStatusSummaryBuilds',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.build" />
    ),
    cell: ({ row }): JSX.Element => {
      const statusSummary = row.original.selectedCommitStatusSummary?.builds;
      return (
        <GroupedTestStatus
          fail={statusSummary?.invalid}
          pass={statusSummary?.valid}
          nullStatus={statusSummary?.null}
        />
      );
    },
  },
  {
    accessorKey: 'selectedCommitStatusSummaryBoots',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.bootStatus" />
    ),
    cell: ({ row }): JSX.Element => {
      const statusSummary = row.original.selectedCommitStatusSummary?.boots;
      return (
        <GroupedTestStatus
          fail={statusSummary?.FAIL}
          pass={statusSummary?.PASS}
          done={statusSummary?.DONE}
          error={statusSummary?.ERROR}
          miss={statusSummary?.MISS}
          skip={statusSummary?.SKIP}
        />
      );
    },
  },
  {
    accessorKey: 'selectedCommitStatusSummaryTests',
    header: ({ column }): JSX.Element => (
      <TableHeader column={column} intlKey="globalTable.test" />
    ),
    cell: ({ row }): JSX.Element => {
      const statusSummary = row.original.selectedCommitStatusSummary?.tests;
      return (
        <GroupedTestStatus
          fail={statusSummary?.FAIL}
          pass={statusSummary?.PASS}
          done={statusSummary?.DONE}
          error={statusSummary?.ERROR}
          miss={statusSummary?.MISS}
          skip={statusSummary?.SKIP}
        />
      );
    },
  },
];

const getInitialRowSelection = (
  selectedIndexes: number[],
  treeItemsLength: number,
): Record<string, boolean> => {
  if (selectedIndexes.length === 0) {
    return Object.fromEntries(
      Array.from({ length: treeItemsLength }, (_, i) => [i.toString(), true]),
    );
  }
  return Object.fromEntries(
    Array.from(selectedIndexes, treeIndex => [treeIndex.toString(), true]),
  );
};

const indexesFromRowSelection = (
  rowSelection: RowSelectionState,
  maxTreeItems: number,
): number[] => {
  const rowSelectionValues = Object.values(rowSelection);
  if (
    rowSelectionValues.length === maxTreeItems ||
    rowSelectionValues.length === 0
  ) {
    return [];
  }
  return Object.keys(rowSelection).map(rowId => parseInt(rowId));
};

export function HardwareHeader({
  treeItems,
  selectedIndexes = [],
  updateTreeFilters,
}: IHardwareHeader): JSX.Element {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'treeName', desc: false },
  ]);
  const { pagination, paginationUpdater } = usePaginationState(
    'hardwareDetailsTrees',
  );

  // The initial assignment is useful to catch the initial indexes from URL
  const [rowSelection, setRowSelection] = useState(() =>
    getInitialRowSelection(selectedIndexes, treeItems.length),
  );

  const rowSelectionDebounced = useDebounce(rowSelection, DEBOUNCE_INTERVAL);

  useEffect(() => {
    const updatedSelection = indexesFromRowSelection(
      rowSelectionDebounced,
      treeItems.length,
    );
    updateTreeFilters(updatedSelection);
  }, [rowSelectionDebounced, treeItems.length, updateTreeFilters]);

  // This useEffect update the current row selection when the selectedIndexes change.
  // Useful when the user select a tree by filter modal.
  useEffect(() => {
    setRowSelection(() =>
      getInitialRowSelection(selectedIndexes, treeItems.length),
    );
  }, [selectedIndexes, treeItems.length]);

  const table = useReactTable({
    data: treeItems,
    columns,
    getCoreRowModel: getCoreRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onPaginationChange: paginationUpdater,
    getFilteredRowModel: getFilteredRowModel(),
    getRowId: originalRow => originalRow.index,
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      pagination,
      rowSelection,
    },
  });

  const groupHeaders = table.getHeaderGroups()[0]?.headers;
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
                rowSelection, // needed for the selection icon too
              })}
        </TableHead>
      );
    });
  }, [groupHeaders, sorting, rowSelection]);

  const modelRows = table.getRowModel().rows;
  const tableRows = useMemo((): JSX.Element[] | JSX.Element => {
    return modelRows?.length ? (
      modelRows.map(row => (
        <TableRow key={row.id}>
          {row.getVisibleCells().map(cell => (
            <TableCell key={cell.id}>
              {flexRender(cell.column.columnDef.cell, cell.getContext())}
            </TableCell>
          ))}
        </TableRow>
      ))
    ) : (
      <TableRow key="no-results">
        <TableCell colSpan={columns.length} className="h-24 text-center">
          <FormattedMessage id="global.noResults" />
        </TableCell>
      </TableRow>
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modelRows, rowSelection]);

  return (
    <div className="flex flex-col gap-6 pb-4">
      <BaseTable headerComponents={tableHeaders}>
        <TableBody>{tableRows}</TableBody>
      </BaseTable>
      <PaginationInfo table={table} intlLabel="global.trees" />
    </div>
  );
}
