import { useSearch } from '@tanstack/react-router';

import { useEffect, useState } from 'react';

import type { UseQueryResult } from '@tanstack/react-query';

import type { UseTreeDetailsWithoutVariant } from '@/api/treeDetails';
import { useTreeDetails } from '@/api/treeDetails';
import type {
  PossibleTabs,
  TreeDetailsBoots,
  TreeDetailsBuilds,
  TreeDetailsSummary,
  TreeDetailsTests,
} from '@/types/tree/TreeDetails';
import type { QuerySelectorStatus } from '@/components/QuerySwitcher/QuerySwitcher';

const canWeFetchAll = (
  isSummaryRead: boolean,
  currentPageTab: PossibleTabs,
  statusTable: Record<PossibleTabs, boolean>,
): boolean => {
  if (!isSummaryRead) {
    return false;
  }

  return statusTable[currentPageTab] ?? false;
};

export type TreeDetailsLazyLoaded = {
  summary: {
    data?: TreeDetailsSummary;
    isLoading: boolean;
    status: QuerySelectorStatus;
    error: UseQueryResult['error'];
    isPlaceholderData: boolean;
  };
  builds: {
    data?: TreeDetailsBuilds;
    isLoading: boolean;
    status: QuerySelectorStatus;
  };
  boots: {
    data?: TreeDetailsBoots;
    isLoading: boolean;
    status: QuerySelectorStatus;
  };
  tests: {
    data?: TreeDetailsTests;
    isLoading: boolean;
    status: QuerySelectorStatus;
  };
};

export const useTreeDetailsLazyLoadQuery = (
  useTreeDetailsArgs: UseTreeDetailsWithoutVariant,
): TreeDetailsLazyLoaded => {
  const [fetchAll, setFetchAll] = useState(false);

  const summaryResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'summary',
  });

  const { currentPageTab } = useSearch({
    from: '/tree/$treeId/',
  });

  const buildsResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'builds',
    enabled:
      (!!summaryResult.data && currentPageTab === 'global.builds') || fetchAll,
  });

  const bootsResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'boots',
    enabled:
      (!!summaryResult.data && currentPageTab === 'global.boots') || fetchAll,
  });

  const testsResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'tests',
    enabled:
      (!!summaryResult.data && currentPageTab === 'global.tests') || fetchAll,
  });

  useEffect(() => {
    if (
      canWeFetchAll(!!summaryResult.data, currentPageTab, {
        'global.builds': !!buildsResult.data,
        'global.boots': !!bootsResult.data,
        'global.tests': !!testsResult.data,
      })
    ) {
      setFetchAll(true);
    }
  }, [
    bootsResult.data,
    bootsResult.isLoading,
    buildsResult.data,
    buildsResult.isLoading,
    currentPageTab,
    fetchAll,
    setFetchAll,
    summaryResult.data,
    summaryResult.isLoading,
    testsResult.data,
    testsResult.isLoading,
  ]);

  return {
    summary: {
      data: summaryResult.data,
      isLoading: summaryResult.isLoading,
      status: summaryResult.status,
      isPlaceholderData: summaryResult.isPlaceholderData,
      error: summaryResult.error,
    },
    builds: {
      data: buildsResult.data,
      isLoading: buildsResult.isLoading,
      status: buildsResult.status,
    },
    boots: {
      data: bootsResult.data,
      isLoading: bootsResult.isLoading,
      status: bootsResult.status,
    },
    tests: {
      data: testsResult.data,
      isLoading: testsResult.isLoading,
      status: testsResult.status,
    },
  };
};
