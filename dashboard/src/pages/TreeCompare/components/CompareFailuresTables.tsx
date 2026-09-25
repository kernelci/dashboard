import type { ChangeEvent, JSX, ReactNode } from 'react';
import { useCallback, useMemo, useRef, useState } from 'react';

import { useVirtualizer } from '@tanstack/react-virtual';
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';
import { FormattedMessage } from 'react-intl';

import type {
  CompareBootFailureRow,
  CompareBuildFailureRow,
  CompareFailureRow,
} from '@/types/tree/TreeCompare';

import type { MessagesKey } from '@/locales/messages';

import { PathWithPrefixEllipsis } from '@/components/TestsTable/DefaultTestsColumns';
import {
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import { cn } from '@/lib/utils';
import { compareRowNav } from '@/utils/treeCompareDiff';
import type { LogType } from '@/hooks/useLogData';

import { CompareChangeBadge, isFailureHighlight } from './CompareChangeDisplay';
import {
  CompareDetailSheet,
  compareRowToDetailItem,
} from './CompareDetailSheet';
import {
  CompareSideCells,
  CompareTableSearch,
  rowMatchesSearch,
} from './compareTableShared';

const ESTIMATED_ROW_HEIGHT = 56;
const VIRTUALIZER_OVERSCAN = 10;
const VIRTUAL_TABLE_MAX_HEIGHT = 480;

/** Fixed widths keep columns stable while virtualized rows swap in/out. */
const BUILDS_COLGROUP = (
  <colgroup>
    <col className="w-[48%]" />
    <col className="w-[14%]" />
    <col className="w-[4%]" />
    <col className="w-[14%]" />
    <col className="w-[20%]" />
  </colgroup>
);

const BOOTS_COLGROUP = (
  <colgroup>
    <col className="w-[26%]" />
    <col className="w-[24%]" />
    <col className="w-[14%]" />
    <col className="w-[10%]" />
    <col className="w-[4%]" />
    <col className="w-[10%]" />
    <col className="w-[8%]" />
  </colgroup>
);

type SortDirection = 'asc' | 'desc';
type SortState<Key extends string> = {
  key: Key;
  direction: SortDirection;
} | null;

type BuildSortKey = 'config' | 'sideA' | 'sideB' | 'change';
type BootSortKey =
  | 'path'
  | 'config'
  | 'hardware'
  | 'sideA'
  | 'sideB'
  | 'change';

function cycleSort<Key extends string>(
  current: SortState<Key>,
  key: Key,
): SortState<Key> {
  if (current?.key !== key) {
    return { key, direction: 'asc' };
  }
  if (current.direction === 'asc') {
    return { key, direction: 'desc' };
  }
  return null;
}

function compareSortValues(a: unknown, b: unknown): number {
  if (typeof a === 'number' && typeof b === 'number') {
    return a - b;
  }
  return String(a ?? '').localeCompare(String(b ?? ''), undefined, {
    numeric: true,
    sensitivity: 'base',
  });
}

function sortRows<T, Key extends string>(
  rows: T[],
  sort: SortState<Key>,
  getters: Record<Key, (row: T) => unknown>,
): T[] {
  if (!sort) {
    return rows;
  }
  const getValue = getters[sort.key];
  const direction = sort.direction === 'asc' ? 1 : -1;
  return [...rows].sort(
    (left, right) =>
      direction * compareSortValues(getValue(left), getValue(right)),
  );
}

function useCompareSheet(
  visibleRows: CompareFailureRow[],
  logType: LogType,
): {
  selectedId: string | null;
  openRow: (id: string) => void;
  sheet: JSX.Element;
} {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const nav = compareRowNav(visibleRows, selectedId);

  const openRow = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  const closeSheet = useCallback((open: boolean) => {
    if (!open) {
      setSelectedId(null);
    }
  }, []);

  const goToPrevious = useCallback(() => {
    if (nav.previousId) {
      setSelectedId(nav.previousId);
    }
  }, [nav.previousId]);

  const goToNext = useCallback(() => {
    if (nav.nextId) {
      setSelectedId(nav.nextId);
    }
  }, [nav.nextId]);

  return {
    selectedId,
    openRow,
    sheet: (
      <CompareDetailSheet
        open={nav.row !== null}
        item={nav.row ? compareRowToDetailItem(nav.row) : null}
        logType={logType}
        onOpenChange={closeSheet}
        onPrevious={goToPrevious}
        onNext={goToNext}
        hasPrevious={nav.hasPrevious}
        hasNext={nav.hasNext}
      />
    ),
  };
}

function SortableHead<Key extends string>({
  intlKey,
  sortKey,
  sort,
  onSort,
  className,
}: {
  intlKey: MessagesKey;
  sortKey: Key;
  sort: SortState<Key>;
  onSort: (key: Key) => void;
  className?: string;
}): JSX.Element {
  const isActive = sort?.key === sortKey;
  const ArrowIcon = !isActive
    ? ArrowUpDown
    : sort.direction === 'asc'
      ? ArrowUp
      : ArrowDown;

  return (
    <TableHead className={cn('bg-light-gray font-semibold', className)}>
      <button
        type="button"
        className="hover:text-dim-black inline-flex items-center gap-1"
        onClick={() => onSort(sortKey)}
      >
        <FormattedMessage id={intlKey} />
        <ArrowIcon
          className={cn('h-3.5 w-3.5', !isActive && 'text-dim-gray')}
        />
      </button>
    </TableHead>
  );
}

function VirtualizedCompareTable({
  rowCount,
  getRowId,
  headerRow,
  renderRow,
  colGroup,
  colCount,
}: {
  rowCount: number;
  getRowId: (index: number) => string;
  headerRow: ReactNode;
  renderRow: (index: number) => ReactNode;
  colGroup: ReactNode;
  colCount: number;
}): JSX.Element {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: rowCount,
    estimateSize: () => ESTIMATED_ROW_HEIGHT,
    getScrollElement: () => parentRef.current,
    overscan: VIRTUALIZER_OVERSCAN,
    getItemKey: index => getRowId(index),
  });
  const virtualItems = virtualizer.getVirtualItems();

  const paddingTop = virtualItems.length > 0 ? virtualItems[0].start : 0;
  const paddingBottom =
    virtualItems.length > 0
      ? virtualizer.getTotalSize() - virtualItems[virtualItems.length - 1].end
      : 0;

  // Raw <table>: ui/Table wraps in its own overflow+border box and breaks rounded + sticky.
  // Spacers live in tbody so sticky thead can pin to the scroll container.
  return (
    <div
      ref={parentRef}
      className="overflow-auto rounded-lg border border-gray-200 bg-white"
      style={{ height: VIRTUAL_TABLE_MAX_HEIGHT }}
    >
      <table className="w-full table-fixed border-separate border-spacing-0 text-sm">
        {colGroup}
        <TableHeader className="sticky top-0 z-10 [&_tr]:border-b [&_tr]:border-gray-200">
          {headerRow}
        </TableHeader>
        <TableBody>
          {paddingTop > 0 && (
            <tr aria-hidden>
              <td
                colSpan={colCount}
                style={{ height: paddingTop, padding: 0, border: 'none' }}
              />
            </tr>
          )}
          {virtualItems.map(item => renderRow(item.index))}
          {paddingBottom > 0 && (
            <tr aria-hidden>
              <td
                colSpan={colCount}
                style={{ height: paddingBottom, padding: 0, border: 'none' }}
              />
            </tr>
          )}
        </TableBody>
      </table>
    </div>
  );
}

const BUILD_SORT_GETTERS: Record<
  BuildSortKey,
  (row: CompareBuildFailureRow) => unknown
> = {
  config: row => row.config,
  sideA: row => row.sideA,
  sideB: row => row.sideB,
  change: row => row.change,
};

export function CompareBuildsFailuresTable({
  rows,
}: {
  rows: CompareBuildFailureRow[];
}): JSX.Element {
  const [sort, setSort] = useState<SortState<BuildSortKey>>(null);
  const [search, setSearch] = useState('');

  const onSearchChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setSearch(event.target.value);
  }, []);

  const visibleRows = useMemo(() => {
    const filtered = rows.filter(row =>
      rowMatchesSearch(
        [row.config, row.arch, row.compiler, row.sideA, row.sideB, row.change],
        search,
      ),
    );
    return sortRows(filtered, sort, BUILD_SORT_GETTERS);
  }, [rows, search, sort]);

  const { selectedId, openRow, sheet } = useCompareSheet(visibleRows, 'build');

  return (
    <div>
      <CompareTableSearch onSearchChange={onSearchChange} />
      <VirtualizedCompareTable
        rowCount={visibleRows.length}
        getRowId={index => visibleRows[index]?.id ?? String(index)}
        colGroup={BUILDS_COLGROUP}
        colCount={5}
        headerRow={
          <TableRow className="bg-light-gray hover:bg-light-gray">
            <SortableHead
              intlKey="treeCompare.failures.configArch"
              sortKey="config"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
            <SortableHead
              className="text-center"
              intlKey="treeCompare.sideA"
              sortKey="sideA"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
            <TableHead className="bg-light-gray w-8" />
            <SortableHead
              className="text-center"
              intlKey="treeCompare.sideB"
              sortKey="sideB"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
            <SortableHead
              className="text-center"
              intlKey="treeCompare.failures.change"
              sortKey="change"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
          </TableRow>
        }
        renderRow={index => {
          const row = visibleRows[index];
          if (!row) {
            return null;
          }
          return (
            <TableRow
              key={row.id}
              onClick={() => openRow(row.id)}
              className={cn(
                'hover:bg-light-blue cursor-pointer',
                isFailureHighlight(row.change) && 'bg-red-50',
                selectedId === row.id && 'bg-sky-200 hover:bg-sky-200',
              )}
            >
              <TableCell className="max-w-0">
                <div
                  className="text-dim-black truncate font-medium"
                  title={row.config}
                >
                  {row.config}
                </div>
                <div
                  className="text-dim-gray truncate text-xs"
                  title={`${row.arch} · ${row.compiler}`}
                >
                  {row.arch} · {row.compiler}
                </div>
              </TableCell>
              <CompareSideCells sideA={row.sideA} sideB={row.sideB} />
              <TableCell>
                <div className="flex justify-center">
                  <CompareChangeBadge change={row.change} />
                </div>
              </TableCell>
            </TableRow>
          );
        }}
      />
      {sheet}
    </div>
  );
}

const BOOT_SORT_GETTERS: Record<
  BootSortKey,
  (row: CompareBootFailureRow) => unknown
> = {
  path: row => row.path,
  config: row => row.config,
  hardware: row => row.hardware,
  sideA: row => row.sideA,
  sideB: row => row.sideB,
  change: row => row.change,
};

export function CompareBootsFailuresTable({
  rows,
}: {
  rows: CompareBootFailureRow[];
}): JSX.Element {
  const [sort, setSort] = useState<SortState<BootSortKey>>(null);
  const [search, setSearch] = useState('');

  const onSearchChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setSearch(event.target.value);
  }, []);

  const visibleRows = useMemo(() => {
    const filtered = rows.filter(row =>
      rowMatchesSearch(
        [
          row.path,
          row.config,
          row.arch,
          row.hardware,
          row.sideA,
          row.sideB,
          row.change,
        ],
        search,
      ),
    );
    return sortRows(filtered, sort, BOOT_SORT_GETTERS);
  }, [rows, search, sort]);

  const { selectedId, openRow, sheet } = useCompareSheet(visibleRows, 'test');

  return (
    <div>
      <CompareTableSearch onSearchChange={onSearchChange} />
      <VirtualizedCompareTable
        rowCount={visibleRows.length}
        getRowId={index => visibleRows[index]?.id ?? String(index)}
        colGroup={BOOTS_COLGROUP}
        colCount={7}
        headerRow={
          <TableRow className="bg-light-gray hover:bg-light-gray">
            <SortableHead
              intlKey="treeCompare.failures.pathArch"
              sortKey="path"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
            <SortableHead
              intlKey="global.config"
              sortKey="config"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
            <SortableHead
              intlKey="global.hardware"
              sortKey="hardware"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
            <SortableHead
              className="text-center"
              intlKey="treeCompare.sideA"
              sortKey="sideA"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
            <TableHead className="bg-light-gray w-8" />
            <SortableHead
              className="text-center"
              intlKey="treeCompare.sideB"
              sortKey="sideB"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
            <SortableHead
              className="text-center"
              intlKey="treeCompare.failures.change"
              sortKey="change"
              sort={sort}
              onSort={key => setSort(current => cycleSort(current, key))}
            />
          </TableRow>
        }
        renderRow={index => {
          const row = visibleRows[index];
          if (!row) {
            return null;
          }
          return (
            <TableRow
              key={row.id}
              onClick={() => openRow(row.id)}
              className={cn(
                'hover:bg-light-blue cursor-pointer',
                isFailureHighlight(row.change) && 'bg-red-50',
                selectedId === row.id && 'bg-sky-200 hover:bg-sky-200',
              )}
            >
              <TableCell className="max-w-0">
                <div className="text-dim-black font-medium" title={row.path}>
                  <PathWithPrefixEllipsis value={row.path} />
                </div>
                <div
                  className="text-dim-gray truncate text-xs"
                  title={row.arch}
                >
                  {row.arch}
                </div>
              </TableCell>
              <TableCell className="max-w-0">
                <div
                  className="text-dim-black truncate text-sm"
                  title={row.config}
                >
                  {row.config}
                </div>
              </TableCell>
              <TableCell className="max-w-0">
                <div
                  className="text-dim-black truncate text-sm"
                  title={row.hardware}
                >
                  {row.hardware}
                </div>
              </TableCell>
              <CompareSideCells sideA={row.sideA} sideB={row.sideB} />
              <TableCell>
                <div className="flex justify-center">
                  <CompareChangeBadge change={row.change} />
                </div>
              </TableCell>
            </TableRow>
          );
        }}
      />
      {sheet}
    </div>
  );
}
