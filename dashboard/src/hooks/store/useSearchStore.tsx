import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import type { LinkProps } from '@tanstack/react-router';

interface SearchStore {
  previousSearch?: LinkProps['search'];
  updatePreviousSearch: (previousSearch: SearchStore['previousSearch']) => void;
}

export const useSearchStore = create<SearchStore>()(
  persist(
    set => ({
      previousSearch: undefined,
      updatePreviousSearch: (previousSearch): void =>
        set(() => ({ previousSearch: previousSearch })),
    }),
    {
      name: 'previousSearchParams',
    },
  ),
);
