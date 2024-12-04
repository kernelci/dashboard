import { useState } from 'react';

import type { Updater, PaginationState } from '@tanstack/react-table';

import type { TableKeys } from '@/utils/constants/tables';

import { useFeatureFlag } from './useFeatureFlag';

const DEFAULT_PAGINATION_STATE = { pageIndex: 0, pageSize: 10 } as const;

export const usePaginationState = (
  selectedTable: TableKeys,
): {
  pagination: PaginationState;
  paginationUpdater: (updater: Updater<PaginationState>) => void;
} => {
  const { showDev } = useFeatureFlag();
  const [pagination, setPagination] = useState<PaginationState>(() => {
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
