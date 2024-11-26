import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import type {
  TTreeCommitHistoryResponse,
  TTreeDetailsFilter,
} from '@/types/tree/TreeDetails';

import { getTargetFilter } from '@/utils/filters';
import { mapFiltersKeysToBackendCompatible } from '@/utils/utils';

import http from './api';

const fetchCommitHistory = async (
  commitHash: string,
  origin: string,
  gitUrl: string,
  gitBranch: string,
  filters: TTreeDetailsFilter,
): Promise<TTreeCommitHistoryResponse> => {
  const filtersFormatted = mapFiltersKeysToBackendCompatible(filters);

  const params = {
    origin,
    git_url: gitUrl,
    git_branch: gitBranch,
    ...filtersFormatted,
  };

  const res = await http.get<TTreeCommitHistoryResponse>(
    `/api/tree/${commitHash}/commits`,
    {
      params,
    },
  );
  return res.data;
};

export const useCommitHistory = (
  {
    commitHash,
    origin,
    gitUrl,
    gitBranch,
    filter,
  }: {
    commitHash: string;
    origin: string;
    gitUrl: string;
    gitBranch: string;
    filter: TTreeDetailsFilter;
  },
  { enabled = true },
): UseQueryResult<TTreeCommitHistoryResponse> => {
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
    ],
    enabled,
    queryFn: () =>
      fetchCommitHistory(commitHash, origin, gitUrl, gitBranch, filters),
  });
};
