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
import type { TFilter } from '@/types/general';

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
): Promise<TTreeCommitHistoryResponse> => {
  const filtersFormatted = mapFiltersKeysToBackendCompatible(filters);

  const params = {
    origin,
    git_url: gitUrl,
    git_branch: gitBranch,
    start_time_stamp_in_seconds: startTimestampInSeconds,
    end_time_stamp_in_seconds: endTimestampInSeconds,
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
      ),
  });
};
