import type { UseQueryResult } from '@tanstack/react-query';

import type { UseTreeDetailsWithoutVariant } from '@/api/treeDetails';
import { useTreeDetails } from '@/api/treeDetails';
import type {
  TreeDetailsFullData,
  TreeDetailsSummary,
} from '@/types/tree/TreeDetails';
import type { QuerySelectorStatus } from '@/components/QuerySwitcher/QuerySwitcher';

export type TreeDetailsLazyLoaded = {
  summary: {
    data?: TreeDetailsSummary;
    isLoading: boolean;
    status: QuerySelectorStatus;
    error: UseQueryResult['error'];
    isPlaceholderData: boolean;
  };
  full: {
    data?: TreeDetailsFullData;
    isLoading: boolean;
    status: QuerySelectorStatus;
  };
  common: {
    isAllReady: boolean;
    isAnyLoading: boolean;
  };
};

export const useTreeDetailsLazyLoadQuery = (
  useTreeDetailsArgs: UseTreeDetailsWithoutVariant,
): TreeDetailsLazyLoaded => {
  const summaryResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'summary',
  });

  const fullResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'full',
    enabled: !!summaryResult.data,
  });

  return {
    summary: {
      data: summaryResult.data,
      isLoading: summaryResult.isLoading,
      status: summaryResult.status,
      isPlaceholderData: summaryResult.isPlaceholderData,
      error: summaryResult.error,
    },
    full: {
      data: fullResult.data,
      isLoading: fullResult.isLoading,
      status: fullResult.status,
    },
    common: {
      isAllReady: !!summaryResult && !!fullResult,
      isAnyLoading: summaryResult.isLoading || fullResult.isLoading,
    },
  };
};
