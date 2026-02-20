import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { treeDetailsDirectRouteName } from '@/types/tree/TreeDetails';
import type {
  TreeDetailsRouteFrom,
  TTreeCommitHistoryResponse,
  TTreeDetailsFilter,
} from '@/types/tree/TreeDetails';

import { mapFiltersKeysToBackendCompatible } from '@/utils/utils';

import { getTargetFilter } from '@/types/general';
import type { TFilter, TreeEntityTypes } from '@/types/general';

import { RequestData } from './commonRequest';

const fetchCommitHistory = async (
  commitHash: string,
  origin: string,
  gitUrl: string,
  gitBranch: string,
  filters: TTreeDetailsFilter,
  startTimestampInSeconds: number | undefined,
  endTimestampInSeconds: number | undefined,
  treeName?: string,
  treeUrlFrom?: TreeDetailsRouteFrom,
  types?: TreeEntityTypes[],
  buildsRelatedToFilteredTestsOnly?: boolean,
): Promise<TTreeCommitHistoryResponse> => {
  const filtersFormatted = mapFiltersKeysToBackendCompatible(filters);

  const params = {
    origin,
    git_url: gitUrl,
    git_branch: gitBranch,
    start_timestamp_in_seconds: startTimestampInSeconds,
    end_timestamp_in_seconds: endTimestampInSeconds,
    types: types?.join(','),
    builds_related_to_filtered_tests_only: buildsRelatedToFilteredTestsOnly,
    ...filtersFormatted,
  };

  const baseUrl =
    treeUrlFrom === treeDetailsDirectRouteName
      ? `/api/tree/${treeName}/${gitBranch}/${commitHash}`
      : `/api/tree/${commitHash}`;

  const data = await RequestData.get<TTreeCommitHistoryResponse>(
    `${baseUrl}/commits`,
    {
      params,
    },
  );

  return data;
};

export const useCommitHistory = ({
  commitHash,
  origin,
  gitUrl,
  gitBranch,
  filter,
  endTimestampInSeconds,
  startTimestampInSeconds,
  treeName,
  treeUrlFrom,
  types,
  buildsRelatedToFilteredTestsOnly,
}: {
  commitHash: string;
  origin: string;
  gitUrl: string;
  gitBranch: string;
  filter: TTreeDetailsFilter | TFilter;
  startTimestampInSeconds?: number;
  endTimestampInSeconds?: number;
  treeName?: string;
  treeUrlFrom?: TreeDetailsRouteFrom;
  types?: TreeEntityTypes[];
  buildsRelatedToFilteredTestsOnly?: boolean;
}): UseQueryResult<TTreeCommitHistoryResponse> => {
  const testFilter = getTargetFilter(filter, 'test');
  const treeDetailsFilter = getTargetFilter(filter, 'treeDetails');

  const filters = {
    ...treeDetailsFilter,
    ...testFilter,
  };

  return useQuery({
    queryKey: [
      'treeCommitHistory',
      commitHash,
      origin,
      gitUrl,
      gitBranch,
      filters,
      startTimestampInSeconds,
      endTimestampInSeconds,
      treeName,
      treeUrlFrom,
      types,
      buildsRelatedToFilteredTestsOnly,
    ],
    queryFn: () =>
      fetchCommitHistory(
        commitHash,
        origin,
        gitUrl,
        gitBranch,
        filters,
        startTimestampInSeconds,
        endTimestampInSeconds,
        treeName,
        treeUrlFrom,
        types,
        buildsRelatedToFilteredTestsOnly,
      ),
  });
};
