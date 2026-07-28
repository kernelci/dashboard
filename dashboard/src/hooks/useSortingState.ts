import { useCallback, useMemo } from 'react';

import type { OnChangeFn, SortingState } from '@tanstack/react-table';
import { useNavigate, useSearch } from '@tanstack/react-router';

import { TABLE_SORT_UNSORTED, type TableSortSearch } from '@/types/general';
import { EMPTY_OBJECT } from '@/utils/constants/general';

const EMPTY_SORTING: SortingState = [];

const sortingEquals = (a: SortingState, b: SortingState): boolean => {
  if (a.length !== b.length) {
    return false;
  }
  return a.every(
    (sort, index) => sort.id === b[index]?.id && sort.desc === b[index]?.desc,
  );
};

export const sortingToSearchValue = (sorting: SortingState): string => {
  if (sorting.length === 0) {
    return TABLE_SORT_UNSORTED;
  }
  const sort = sorting[0];
  return sort.desc ? `-${sort.id}` : sort.id;
};

export const searchValueToSorting = (
  value: string | undefined,
  defaultSorting: SortingState,
): SortingState => {
  if (value === undefined) {
    return defaultSorting;
  }
  if (value === TABLE_SORT_UNSORTED) {
    return [];
  }
  if (value.startsWith('-')) {
    return [{ id: value.slice(1), desc: true }];
  }
  return [{ id: value, desc: false }];
};

const toUrlValue = (
  sorting: SortingState,
  defaultSorting: SortingState,
): string | undefined => {
  if (sortingEquals(sorting, defaultSorting)) {
    return undefined;
  }
  return sortingToSearchValue(sorting);
};

export const getTableSortValue = (
  tableSort: TableSortSearch,
  sortKey?: string,
): string | undefined => {
  if (tableSort === undefined) {
    return undefined;
  }
  if (sortKey === undefined) {
    return typeof tableSort === 'string' ? tableSort : undefined;
  }
  if (typeof tableSort === 'object') {
    return tableSort[sortKey];
  }
  return undefined;
};

export const updateTableSortParam = (
  prev: TableSortSearch,
  sortKey: string | undefined,
  value: string | undefined,
): TableSortSearch => {
  if (sortKey === undefined) {
    return value;
  }

  const next: Record<string, string> =
    typeof prev === 'object' && prev !== null ? { ...prev } : {};
  if (value === undefined) {
    delete next[sortKey];
  } else {
    next[sortKey] = value;
  }
  return Object.keys(next).length === 0 ? undefined : next;
};

type UseSortingStateOptions = {
  defaultSorting?: SortingState;
  /** Set only when multiple tables on the same page need distinct sort params. */
  sortKey?: string;
};

export const useSortingState = (
  options: UseSortingStateOptions = EMPTY_OBJECT,
): {
  sorting: SortingState;
  handleSortingChange: OnChangeFn<SortingState>;
} => {
  const { defaultSorting = EMPTY_SORTING, sortKey } = options;
  const { tableSort } = useSearch({ strict: false });
  const navigate = useNavigate();

  const sortValue = getTableSortValue(tableSort, sortKey);

  const sorting = useMemo(
    () => searchValueToSorting(sortValue, defaultSorting),
    [defaultSorting, sortValue],
  );

  const handleSortingChange: OnChangeFn<SortingState> = useCallback(
    updater => {
      navigate({
        to: '.',
        search: prev => {
          const current = searchValueToSorting(
            getTableSortValue(prev.tableSort, sortKey),
            defaultSorting,
          );
          const nextSorting =
            typeof updater === 'function' ? updater(current) : updater;

          return {
            ...prev,
            tableSort: updateTableSortParam(
              prev.tableSort,
              sortKey,
              toUrlValue(nextSorting, defaultSorting),
            ),
          };
        },
        state: s => s,
        replace: true,
      });
    },
    [defaultSorting, navigate, sortKey],
  );

  return { sorting, handleSortingChange };
};
