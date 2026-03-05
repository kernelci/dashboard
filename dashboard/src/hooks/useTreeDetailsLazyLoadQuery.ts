import type { UseQueryResult } from '@tanstack/react-query';

import type { UseTreeDetailsWithoutVariant } from '@/api/treeDetails';
import { useTreeDetails } from '@/api/treeDetails';
import type {
  TreeDetailsBuilds,
  TreeDetailsBoots,
  TreeDetailsTests,
  TreeDetailsSummary,
  PossibleTabs,
} from '@/types/tree/TreeDetails';
import type { QuerySelectorStatus } from '@/components/QuerySwitcher/QuerySwitcher';
import { useIssueExtraDetails } from '@/api/issueExtras';
import type { IssueExtraDetailsResponse } from '@/types/issueExtras';

type TabQueryResult<T> = {
  data?: T;
  isLoading: boolean;
  status: QuerySelectorStatus;
  error: UseQueryResult['error'];
};

export type TreeDetailsLazyLoaded = {
  summary: {
    data?: TreeDetailsSummary;
    isLoading: boolean;
    status: QuerySelectorStatus;
    error: UseQueryResult['error'];
    isPlaceholderData: boolean;
  };
  builds: TabQueryResult<TreeDetailsBuilds>;
  boots: TabQueryResult<TreeDetailsBoots>;
  tests: TabQueryResult<TreeDetailsTests>;
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

export type UseTreeDetailsLazyLoadQueryArgs = UseTreeDetailsWithoutVariant & {
  currentPageTab: PossibleTabs;
};

export const useTreeDetailsLazyLoadQuery = ({
  currentPageTab,
  ...useTreeDetailsArgs
}: UseTreeDetailsLazyLoadQueryArgs): TreeDetailsLazyLoaded => {
  const summaryResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'summary',
  });

  const hasSummary = !!summaryResult.data;

  const buildsResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'builds',
    enabled: hasSummary && currentPageTab === 'global.builds',
  });

  const bootsResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'boots',
    enabled: hasSummary && currentPageTab === 'global.boots',
  });

  const testsResult = useTreeDetails({
    ...useTreeDetailsArgs,
    variant: 'tests',
    enabled: hasSummary && currentPageTab === 'global.tests',
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
    builds: {
      data: buildsResult.data,
      isLoading: buildsResult.isLoading,
      status: buildsResult.status,
      error: buildsResult.error,
    },
    boots: {
      data: bootsResult.data,
      isLoading: bootsResult.isLoading,
      status: bootsResult.status,
      error: bootsResult.error,
    },
    tests: {
      data: testsResult.data,
      isLoading: testsResult.isLoading,
      status: testsResult.status,
      error: testsResult.error,
    },
    issuesExtras: {
      data: issuesExtrasResult.data,
      isLoading: issuesExtrasResult.isLoading,
      status: issuesExtrasResult.status,
      error: issuesExtrasResult.error,
    },
    common: {
      isAllReady:
        !!summaryResult &&
        !!buildsResult &&
        !!bootsResult &&
        !!testsResult &&
        !!issuesExtrasResult,
      isAnyLoading:
        summaryResult.isLoading ||
        buildsResult.isLoading ||
        bootsResult.isLoading ||
        testsResult.isLoading ||
        issuesExtrasResult.isLoading,
    },
  };
};
