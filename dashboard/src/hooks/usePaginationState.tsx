import { useState } from 'react';

import type { Updater, PaginationState } from '@tanstack/react-table';

import type { TableKeys } from '@/utils/constants/tables';

import { ItemsPerPageValues } from '@/utils/constants/general';

import { useFeatureFlag } from './useFeatureFlag';

const DEFAULT_PAGINATION_STATE = { pageIndex: 0, pageSize: 10 } as const;

const DEFAULT_LISTING_SIZE = 10;

const findClosestGreaterNumber = (sortedList: number[], x: number): number => {
  for (let i = 0; i < sortedList.length; i++) {
    if (sortedList[i] >= x) return sortedList[i];
  }

  return sortedList.slice(-1)[0] ?? DEFAULT_LISTING_SIZE;
};

export const usePaginationState = (
  selectedTable: TableKeys,
  defaultValue?: number,
): {
  pagination: PaginationState;
  paginationUpdater: (updater: Updater<PaginationState>) => void;
} => {
  const { showDev } = useFeatureFlag();
  const [pagination, setPagination] = useState<PaginationState>(() => {
    if (defaultValue) {
      const pageSize = findClosestGreaterNumber(
        ItemsPerPageValues,
        defaultValue,
      );
      return { pageIndex: DEFAULT_PAGINATION_STATE.pageIndex, pageSize };
    }

    const storageData = window.localStorage.getItem(selectedTable);
    if (storageData && showDev) {
      try {
        return { pageIndex: 0, pageSize: JSON.parse(storageData) };
      } catch {
        return DEFAULT_PAGINATION_STATE;
      }
    }
    return DEFAULT_PAGINATION_STATE;
  });

  const paginationUpdater = (updater: Updater<PaginationState>): void => {
    setPagination(prev => {
      const newState = typeof updater === 'function' ? updater(prev) : updater;
      try {
        const serializedState = JSON.stringify(newState.pageSize);
        window.localStorage.setItem(selectedTable, serializedState);
      } catch {
        // If there's an error in serializing the newState, this value won't be saved
      }

      return newState;
    });
  };

  const return_value = showDev
    ? { pagination, paginationUpdater }
    : { pagination, paginationUpdater: setPagination };
  return return_value;
};
