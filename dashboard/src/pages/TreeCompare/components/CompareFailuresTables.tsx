import type { ChangeEvent, JSX, ReactNode } from 'react';
import { useCallback, useMemo, useRef, useState } from 'react';

import { useVirtualizer } from '@tanstack/react-virtual';
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';
import { FormattedMessage, useIntl } from 'react-intl';

import type {
  CompareBootFailureRow,
  CompareBuildFailureRow,
  CompareTestFailureRow,
} from '@/types/tree/TreeCompare';

import type { MessagesKey } from '@/locales/messages';

import DebounceInput from '@/components/DebounceInput/DebounceInput';
import {
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import { cn } from '@/lib/utils';

import {
  CompareChangeBadge,
  CompareStatusChip,
  isFailureHighlight,
} from './CompareChangeDisplay';

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

const PATH_COLGROUP = (
  <colgroup>
    <col className="w-[34%]" />
    <col className="w-[18%]" />
    <col className="w-[14%]" />
    <col className="w-[4%]" />
    <col className="w-[14%]" />
    <col className="w-[16%]" />
  </colgroup>
);

type SortDirection = 'asc' | 'desc';
type SortState<Key extends string> = {
  key: Key;
  direction: SortDirection;
} | null;

type BuildSortKey = 'config' | 'sideA' | 'sideB' | 'change';
type PathSortKey = 'path' | 'hardware' | 'sideA' | 'sideB' | 'change';

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

function rowMatchesSearch(values: unknown[], query: string): boolean {
  if (!query) {
    return true;
  }
  const needle = query.toLowerCase();
  return values.some(value =>
    String(value ?? '')
      .toLowerCase()
      .includes(needle),
  );
}

function CompareTableSearch({
  onSearchChange,
}: {
  onSearchChange: (event: ChangeEvent<HTMLInputElement>) => void;
}): JSX.Element {
  const { formatMessage } = useIntl();

  // mt keeps the input clear of the sticky tabs header, which overlaps its top border.
  return (
    <div className="mt-2 mb-4 flex flex-col items-center gap-4 sm:flex-row sm:justify-end">
      <DebounceInput
        debouncedSideEffect={onSearchChange}
        className="w-9/10 sm:w-50"
        type="text"
        placeholder={formatMessage({ id: 'global.search' })}
      />
    </div>
  );
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

function SideCells({
  sideA,
  sideB,
}: {
  sideA: CompareBuildFailureRow['sideA'];
  sideB: CompareBuildFailureRow['sideB'];
}): JSX.Element {
  return (
    <>
      <TableCell>
        <div className="flex justify-center">
          <CompareStatusChip status={sideA} />
        </div>
      </TableCell>
      <TableCell className="text-dim-gray text-center">→</TableCell>
      <TableCell>
        <div className="flex justify-center">
          <CompareStatusChip status={sideB} />
        </div>
      </TableCell>
    </>
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
  selectedId,
  onRowClick,
}: {
  rows: CompareBuildFailureRow[];
  selectedId?: string | null;
  onRowClick: (id: string) => void;
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
              onClick={() => onRowClick(row.id)}
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
              <SideCells sideA={row.sideA} sideB={row.sideB} />
              <TableCell>
                <div className="flex justify-center">
                  <CompareChangeBadge change={row.change} />
                </div>
              </TableCell>
            </TableRow>
          );
        }}
      />
    </div>
  );
}

const PATH_SORT_GETTERS: Record<
  PathSortKey,
  (row: CompareBootFailureRow | CompareTestFailureRow) => unknown
> = {
  path: row => row.path,
  hardware: row => row.hardware,
  sideA: row => row.sideA,
  sideB: row => row.sideB,
  change: row => row.change,
};

function PathHardwareTable({
  rows,
  selectedId,
  onRowClick,
}: {
  rows: Array<CompareBootFailureRow | CompareTestFailureRow>;
  selectedId?: string | null;
  onRowClick: (id: string) => void;
}): JSX.Element {
  const [sort, setSort] = useState<SortState<PathSortKey>>(null);
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
    return sortRows(filtered, sort, PATH_SORT_GETTERS);
  }, [rows, search, sort]);

  return (
    <div>
      <CompareTableSearch onSearchChange={onSearchChange} />
      <VirtualizedCompareTable
        rowCount={visibleRows.length}
        getRowId={index => visibleRows[index]?.id ?? String(index)}
        colGroup={PATH_COLGROUP}
        colCount={6}
        headerRow={
          <TableRow className="bg-light-gray hover:bg-light-gray">
            <SortableHead
              intlKey="treeCompare.failures.pathArch"
              sortKey="path"
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
              onClick={() => onRowClick(row.id)}
              className={cn(
                'hover:bg-light-blue cursor-pointer',
                isFailureHighlight(row.change) && 'bg-red-50',
                selectedId === row.id && 'bg-sky-200 hover:bg-sky-200',
              )}
            >
              <TableCell className="max-w-0">
                <div
                  className="text-dim-black truncate font-medium"
                  title={row.path}
                >
                  {row.path}
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
                  title={row.hardware}
                >
                  {row.hardware}
                </div>
              </TableCell>
              <SideCells sideA={row.sideA} sideB={row.sideB} />
              <TableCell>
                <div className="flex justify-center">
                  <CompareChangeBadge change={row.change} />
                </div>
              </TableCell>
            </TableRow>
          );
        }}
      />
    </div>
  );
}

export function CompareBootsFailuresTable({
  rows,
  selectedId,
  onRowClick,
}: {
  rows: CompareBootFailureRow[];
  selectedId?: string | null;
  onRowClick: (id: string) => void;
}): JSX.Element {
  return (
    <PathHardwareTable
      rows={rows}
      selectedId={selectedId}
      onRowClick={onRowClick}
    />
  );
}

export function CompareTestsFailuresTable({
  rows,
  selectedId,
  onRowClick,
}: {
  rows: CompareTestFailureRow[];
  selectedId?: string | null;
  onRowClick: (id: string) => void;
}): JSX.Element {
  return (
    <PathHardwareTable
      rows={rows}
      selectedId={selectedId}
      onRowClick={onRowClick}
    />
  );
}
