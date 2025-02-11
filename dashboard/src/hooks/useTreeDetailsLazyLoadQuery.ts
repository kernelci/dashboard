import type { UseQueryResult } from '@tanstack/react-query';

import type { UseTreeDetailsWithoutVariant } from '@/api/treeDetails';
import { useTreeDetails } from '@/api/treeDetails';
import type {
  TreeDetailsFullData,
  TreeDetailsSummary,
} from '@/types/tree/TreeDetails';
import type { QuerySelectorStatus } from '@/components/QuerySwitcher/QuerySwitcher';
import { useIssueExtraDetails } from '@/api/issueExtras';
import type { IssueExtraDetailsResponse } from '@/types/issueExtras';

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
  issuesExtras: {
    data?: IssueExtraDetailsResponse;
    isLoading: boolean;
    status: QuerySelectorStatus;
    error: UseQueryResult['error'];
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

  const issuesExtrasResult = useIssueExtraDetails({
    buildIssues: summaryResult.data?.summary.builds.issues,
    bootIssues: summaryResult.data?.summary.boots.issues,
    testIssues: summaryResult.data?.summary.tests.issues,
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
    issuesExtras: {
      data: issuesExtrasResult.data,
      isLoading: issuesExtrasResult.isLoading,
      status: issuesExtrasResult.status,
      error: issuesExtrasResult.error,
    },
    common: {
      isAllReady: !!summaryResult && !!fullResult && !!issuesExtrasResult,
      isAnyLoading:
        summaryResult.isLoading ||
        fullResult.isLoading ||
        issuesExtrasResult.isLoading,
    },
  };
};
