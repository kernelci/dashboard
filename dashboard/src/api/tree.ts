import type { UseQueryResult } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';

import { useSearch } from '@tanstack/react-router';

import type { TreeLatestResponse, TreeListingItem } from '@/types/tree/Tree';
import { DEFAULT_ORIGIN } from '@/types/general';

import type { TreeListingRoutesMap } from '@/utils/constants/treeListing';

import { RequestData } from './commonRequest';

const fetchTreeLatest = async (
  treeName: string,
  branch: string,
  origin?: string,
  gitCommitHash?: string,
): Promise<TreeLatestResponse> => {
  const data = await RequestData.get<TreeLatestResponse>(
    `/api/tree/${treeName}/${branch}`,
    {
      params: {
        origin: origin || DEFAULT_ORIGIN,
        commit_hash: gitCommitHash,
      },
    },
  );
  return data;
};

export const useTreeLatest = (
  treeName: string,
  branch: string,
  origin?: string,
  gitCommitHash?: string,
): UseQueryResult<TreeLatestResponse> => {
  return useQuery({
    queryKey: ['treeLatest', treeName, branch, origin, gitCommitHash],
    queryFn: () => fetchTreeLatest(treeName, branch, origin, gitCommitHash),
    refetchOnWindowFocus: false,
  });
};

const fetchTreeListing = async (
  origin: string,
  intervalInDays: number,
): Promise<TreeListingItem[]> => {
  const params = {
    origin: origin,
    interval_in_days: intervalInDays,
  };

  const data = await RequestData.get<TreeListingItem[]>('/api/tree/', {
    params,
  });
  return data;
};

export const useTreeListing = ({
  searchFrom,
}: {
  searchFrom: TreeListingRoutesMap['search'];
}): UseQueryResult<TreeListingItem[]> => {
  const { origin, intervalInDays } = useSearch({ from: searchFrom });
  const queryKey = ['treeTable', origin, intervalInDays];

  return useQuery({
    queryKey,
    queryFn: () => fetchTreeListing(origin, intervalInDays),
    refetchOnWindowFocus: false,
  });
};
